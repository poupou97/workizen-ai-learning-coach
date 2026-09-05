#!/usr/bin/env python3
"""Round 5 · the DETECT -> REPAIR -> VALIDATE -> RESTORE engine.

The engine owns the *policy*; the plugins own the *knowledge*. Policy, in full:

1. A block arrives with its **original observations** (one per source) and the pipeline's current
   disposition (TRUSTED or WITHHELD, with reasons). Nothing here ever writes to an observation.
2. Each registered repairer for each detected failure class proposes `RepairCandidate`s. A candidate is
   `REPAIRED_CANDIDATE` and is **never served**, whatever produced it (rule, heuristic or LLM).
3. Each registered validator rules on each candidate. The rule is **unanimity among non-abstainers**:
   a single `rejected` kills the candidate, and a candidate with no `validated` verdict stays a candidate.
   `insufficient` is never a soft yes.
4. Final disposition, fail-closed:
   - block WITHHELD, a candidate reached `VALIDATED_REPAIR`, and every withhold reason on the block is
     covered by a validated repair  -> **restorable**: `VALIDATED_REPAIR`, and the caller may serve it as
     TRUSTED by recording the restore (`Outcome.restore_entry`). A reason nobody repaired keeps it withheld.
   - block TRUSTED and a failure was DETECTED but no repair validated -> **WITHHELD** (accuracy first: a
     detected error that cannot be repaired is not served).
   - block TRUSTED, a failure detected AND repaired+validated -> `VALIDATED_REPAIR` (restorable).
   - nothing detected -> the pipeline's own disposition, unchanged and unrecorded.
5. Everything above is written to the ledger as immutable rows.

No threshold in this module is a production trust threshold: the engine decides *whether a repair is
confirmed*, never *whether the corpus is good enough to teach from*. That gate does not exist yet and this
lane does not create one.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from . import model, registry
from .ledger import Ledger


@dataclass
class RepairContext:
    """Everything a repairer/validator may look at. Deliberately plain data - a plugin cannot reach back
    into the pipeline through it."""
    block_id: str
    observations: Sequence[model.Observation]
    disposition: str = model.Disposition.TRUSTED
    withhold_reasons: Sequence[str] = ()
    role: str | None = None
    page: Mapping[str, Any] = field(default_factory=dict)        # book, page, printed_page, features, bbox
    document: Any = None                                          # a DocumentContext-like object (signal D)
    lexicon: Any = None                                           # a VietnameseLexicon-like object (signal A)
    extra: Mapping[str, Any] = field(default_factory=dict)

    def observation(self, source):
        for o in self.observations:
            if o.source == source:
                return o
        return None

    def primary(self):
        return self.observations[0] if self.observations else None


@dataclass
class Outcome:
    block_id: str
    disposition: str
    final_value: Any
    reasons: tuple
    entries: tuple
    candidates: tuple = ()
    validations: tuple = ()
    restorable: bool = False
    detected: tuple = ()

    @property
    def repaired(self):
        return self.disposition == model.Disposition.VALIDATED_REPAIR


class RepairEngine:
    def __init__(self, ledger=None, failure_classes=None):
        self.ledger = ledger if ledger is not None else Ledger()
        self.failure_classes = list(failure_classes) if failure_classes else None

    def _classes(self):
        return self.failure_classes if self.failure_classes is not None else registry.failure_classes()

    def run_block(self, ctx):
        base_value = ctx.primary().value if ctx.primary() else None
        candidates, validations, detected = [], [], []
        best = None            # (candidate, validation) that reached VALIDATED_REPAIR
        for fc in self._classes():
            for fn in registry.repairers_for(fc):
                for cand in (fn(ctx) or ()):
                    if not isinstance(cand, model.RepairCandidate):
                        raise TypeError(f'{getattr(fn, "repairer_id", fn)} returned {type(cand).__name__}, '
                                        f'expected RepairCandidate')
                    detected.append(dict(failure_class=cand.failure_class, rule_id=cand.rule_id,
                                         detail=dict(cand.detected)))
                    candidates.append(cand)
                    self.ledger.append(model.LedgerEntry(
                        block_id=ctx.block_id, failure_class=cand.failure_class,
                        disposition=model.Disposition.REPAIRED_CANDIDATE,
                        observations=ctx.observations, candidate=cand, stage='detect',
                        final_value=cand.proposed_value,
                        reasons=('detected:' + cand.rule_id,)))
                    verdicts = [v(cand, ctx) for v in registry.validators_for(cand.failure_class)]
                    verdicts = [v for v in verdicts if v is not None]
                    validations.extend(verdicts)
                    ok = self._decide(verdicts)
                    entry = self.ledger.append(model.LedgerEntry(
                        block_id=ctx.block_id, failure_class=cand.failure_class,
                        disposition=(model.Disposition.VALIDATED_REPAIR if ok else model.Disposition.REPAIRED_CANDIDATE),
                        observations=ctx.observations, candidate=cand, stage='validate',
                        validation=(verdicts[0] if len(verdicts) == 1 else _merge(verdicts)),
                        final_value=cand.proposed_value,
                        reasons=tuple(f'{v.validator_id}:{v.verdict}' for v in verdicts) or ('no-validator:insufficient',)))
                    if ok and best is None:
                        best = (cand, entry)
        if not candidates:
            return Outcome(ctx.block_id, ctx.disposition, base_value, tuple(ctx.withhold_reasons), (), (), (), False, ())

        covered = {c.failure_class for c, _ in ([best] if best else [])}
        # a validated repair covers the withhold reasons its rule declares it covers
        covered_reasons = set()
        if best:
            covered_reasons = set(best[0].provenance.get('covers_reasons') or ()) | {best[0].failure_class}
        residual = [r for r in ctx.withhold_reasons if r not in covered_reasons]

        if best and not residual:
            final, disp, restorable = best[0].proposed_value, model.Disposition.VALIDATED_REPAIR, True
            reasons = ('repaired:' + best[0].rule_id,)
        elif best and residual:
            final, disp, restorable = best[0].proposed_value, model.Disposition.WITHHELD, False
            reasons = tuple(['repaired:' + best[0].rule_id, 'residual_withhold'] + residual)
        else:
            # A failure was DETECTED and nothing was confirmed. On a served block that is SUSPECT (and it
            # is not served any more); on an already-withheld block it stays WITHHELD. CONFLICT is recorded
            # when the evidence actively contradicts itself rather than merely being insufficient.
            contradicted = any(c.contradicting() for c in candidates)
            disp = (model.Disposition.CONFLICT if contradicted
                    else (model.Disposition.SUSPECT if ctx.disposition == model.Disposition.TRUSTED
                          else model.Disposition.WITHHELD))
            final, restorable = base_value, False
            reasons = tuple(list(ctx.withhold_reasons) + ['detected_unrepaired:' + candidates[0].failure_class])
        entry = self.ledger.append(model.LedgerEntry(
            block_id=ctx.block_id, failure_class=(best[0].failure_class if best else candidates[0].failure_class),
            disposition=disp, observations=ctx.observations, stage='dispose',
            candidate=(best[0] if best else None), validation=(_merge(validations) if validations else None),
            final_value=final, reasons=reasons,
            prior_entry_id=(best[1].entry_id if best else None)))
        return Outcome(ctx.block_id, disp, final, reasons, (entry,), tuple(candidates), tuple(validations),
                       restorable, tuple(detected))

    def restore(self, outcome):
        """Record that a VALIDATED_REPAIR is served. Separate from `run_block` on purpose: repairing and
        serving are two acts, and the ledger shows both."""
        if not outcome.restorable:
            raise ValueError('only a restorable VALIDATED_REPAIR may be restored')
        prior = outcome.entries[-1]
        return self.ledger.supersede(prior, disposition=model.Disposition.TRUSTED, stage='restore',
                                     reasons=tuple(list(outcome.reasons) + ['restored']))

    @staticmethod
    def _decide(verdicts):
        """Unanimity among non-abstainers; no validator at all -> not validated."""
        if not verdicts:
            return False
        if any(v.verdict == model.Verdict.REJECTED for v in verdicts):
            return False
        return any(v.validated for v in verdicts)


def _merge(verdicts):
    if not verdicts:
        return None
    if any(v.verdict == model.Verdict.REJECTED for v in verdicts):
        verdict = model.Verdict.REJECTED
    elif any(v.validated for v in verdicts):
        verdict = model.Verdict.VALIDATED
    else:
        verdict = model.Verdict.INSUFFICIENT
    return model.ValidationResult('engine.merge', verdict,
                                  evidence=[e for v in verdicts for e in v.evidence],
                                  detail=dict(validators={v.validator_id: v.verdict for v in verdicts}))


# ------------------------------------------------------------------ per-signal contribution
class SignalContribution:
    """Per-signal contribution accounting (Founder §3: <measure each signal's contribution>).

    For each signal layer it counts: how often it was consulted, supported, objected, abstained; how often
    it was the **only** supporting layer of a validated repair (`decisive`); and, when truth is known, how
    often a repair it supported was right or wrong. `ablate` answers the question the Founder actually
    asked - what would we lose if this signal did not exist - by re-deciding every candidate with that
    layer's signals removed.
    """

    def __init__(self):
        self.rows = []

    def observe(self, candidate, validated, correct=None, tokens_changed=0, tokens_right=0,
                false_corrections=0):
        """`false_corrections` is the token-level count the Founder called the number that matters most:
        tokens this candidate changed that were ALREADY correct. It is attributed to every signal that
        supported the candidate, so a signal cannot hide behind an aggregate."""
        self.rows.append(dict(candidate=candidate, validated=bool(validated), correct=correct,
                              tokens_changed=int(tokens_changed), tokens_right=int(tokens_right),
                              false_corrections=int(false_corrections)))

    def by_signal(self):
        """The same accounting one level finer - per `signal_id` rather than per layer - so «which of the
        three layer-A sub-signals actually did the work» is answerable."""
        from collections import defaultdict
        agg = defaultdict(lambda: dict(consulted=0, supports=0, objects=0, abstains=0,
                                       validated_with=0, right=0, wrong=0,
                                       tokens_changed=0, tokens_right=0, false_corrections=0))
        for r in self.rows:
            for s in r['candidate'].supporting_signals:
                a = agg[s.signal_id]
                a['consulted'] += 1
                a['supports'] += s.supports
                a['objects'] += s.objects
                a['abstains'] += (s.verdict == model.SignalVerdict.ABSTAINS)
                if r['validated'] and s.supports:
                    a['validated_with'] += 1
                    a['right'] += (r['correct'] is True)
                    a['wrong'] += (r['correct'] is False)
                    a['tokens_changed'] += r.get('tokens_changed', 0)
                    a['tokens_right'] += r.get('tokens_right', 0)
                    a['false_corrections'] += r.get('false_corrections', 0)
        for a in agg.values():
            a['false_correction_rate'] = (round(a['false_corrections'] / a['tokens_changed'], 4)
                                          if a['tokens_changed'] else None)
        return {k: dict(v) for k, v in sorted(agg.items())}

    def table(self, validator_rule=None):
        from collections import defaultdict
        agg = defaultdict(lambda: dict(consulted=0, supports=0, objects=0, abstains=0, decisive=0,
                                       validated_with=0, right=0, wrong=0, ablate_lost=0, ablate_kept=0))
        for r in self.rows:
            cand = r['candidate']
            layers = cand.signals_by_layer()
            for layer, sigs in layers.items():
                a = agg[layer]
                a['consulted'] += 1
                a['supports'] += any(s.supports for s in sigs)
                a['objects'] += any(s.objects for s in sigs)
                a['abstains'] += all(s.verdict == model.SignalVerdict.ABSTAINS for s in sigs)
                if r['validated'] and any(s.supports for s in sigs):
                    a['validated_with'] += 1
                    if r['correct'] is True:
                        a['right'] += 1
                    elif r['correct'] is False:
                        a['wrong'] += 1
                    if cand.independent_support(exclude_layers=(layer,)) == []:
                        a['decisive'] += 1
                if validator_rule is not None and r['validated']:
                    if validator_rule(cand, layer):
                        a['ablate_kept'] += 1
                    else:
                        a['ablate_lost'] += 1        # this layer was NECESSARY: without it the repair fails
        return {k: dict(v) for k, v in sorted(agg.items())}
