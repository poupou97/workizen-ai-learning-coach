#!/usr/bin/env python3
"""Round 5 · Lane A4 — `TrustDecision`, `AnomalySignal`, `EvidenceRef`.

**Audit first, reuse if an equivalent representation already exists** (Founder). It does — more of it than
when this lane started. Lane A1's `repair/model.py` carries observations, signals, correction candidates
with `supporting()` **and** `contradicting()`, validation results, an append-only ledger, and — since A1's
second delivery — the three dispositions the Founder's addendum named that A1's original seven lacked:

    Disposition.SUSPECT · Disposition.HUMAN_VERIFIED · Disposition.CONFLICT
    Disposition.ALIASES = {'RAW': ORIGINAL_OBSERVATION, 'CORRECTION_PROPOSED': REPAIRED_CANDIDATE}

So this module **does not define a disposition of its own**. `verify.trust.Disposition is
repair.model.Disposition`; a ledger row written by A1, A2, C or D compares equal without anyone importing
this file. What is left for A4 to add is exactly three things A1's model still has no slot for:

| type | why A1's model cannot express it |
|---|---|
| `AnomalySignal` | A1 learns of a failure only through a **repairer**, i.e. through something that yields a `RepairCandidate`. A detector that says *«this is wrong and I do not know what it should be»* has no way to speak — and that is the majority output of an LLM verifier and of a cross-corpus check on a proper noun. |
| `EvidenceRef` | `ValidationResult.evidence` is free-form dicts. External evidence has **required** fields (URL/source identity · retrieval timestamp · extracted claim · authority classification · relation), and «required» has to be enforced somewhere or it will be skipped. |
| `TrustDecision` | A **read projection** joining observations + anomalies + candidates + validations + human records into one record with a derived disposition, so the whole case for and against a block can be printed for a Founder. It decides nothing an engine did not. |

**No naive trust ladder.** Nothing here ranks LLM < internet < human. A human record is a source with
provenance like any other, an accepted human correction can still be superseded, and two credible signals
that disagree produce `CONFLICT` rather than a winner.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

from repair import model as rmodel
from repair.model import Disposition  # noqa: F401  — A1's, not a copy. Re-exported for convenience.

TRUST_VERSION = 'trust-v2'

#: What a projection layer may serialise for a child. A1 says `{TRUSTED}`; A4 does **not** widen it.
#: `HUMAN_VERIFIED` is deliberately *not* servable here: a human is a source, not an oracle (Lane C's
#: proper-noun case shows a human read deciding *against* a machine correction, not for it), and in any
#: case no production trust gate exists yet — round 4 measured Source Trust 0/97 for exactly that reason.
SERVABLE = rmodel.Disposition.SERVABLE

#: The Founder's two alias names, resolved through A1's own `ALIASES` map rather than redefined. They are
#: *names for states that already exist*, so binding them here costs nothing and monkey-patching A1's class
#: would cost correctness.
RAW = rmodel.Disposition.canonical('RAW')
CORRECTION_PROPOSED = rmodel.Disposition.canonical('CORRECTION_PROPOSED')


# --------------------------------------------------------------------------- evidence
@dataclass(frozen=True)
class EvidenceRef:
    """One piece of evidence, in the shape the Founder requires of an **external** one — so internal and
    external evidence are the same shape and can be weighed against each other honestly.

    `authority` is a classification, never a score: `corpus` (our own SGK/SGV), `official` (a ministry or
    publisher), `reference` (a dictionary or encyclopaedia of record), `secondary`, `unknown`. It says
    *what kind of thing spoke*, not how right it is.
    """
    kind: str                       # corpus_occurrence | external_page | llm_statement | human_report | deterministic
    source: str                     # book+page for corpus, URL for external, model@version for an LLM
    claim: str                      # the extracted claim, in words
    relation: str = 'supports'      # supports | contradicts | context
    authority: str = 'unknown'
    retrieved_at: str | None = None  # REQUIRED for external evidence
    detail: Mapping[str, Any] = field(default_factory=dict)

    RELATIONS = ('supports', 'contradicts', 'context')
    AUTHORITY = ('corpus', 'official', 'reference', 'secondary', 'unknown')

    def __post_init__(self):
        if self.relation not in self.RELATIONS:
            raise ValueError(f'relation must be one of {self.RELATIONS}, got {self.relation!r}')
        if self.authority not in self.AUTHORITY:
            raise ValueError(f'authority must be one of {self.AUTHORITY}, got {self.authority!r}')
        if self.kind == 'external_page' and not self.retrieved_at:
            raise ValueError('external evidence must carry a retrieval timestamp (Founder: URL/source '
                             'identity · retrieval timestamp · extracted claim · authority classification)')
        if self.kind == 'external_page' and not str(self.source).startswith(('http://', 'https://')):
            raise ValueError('external evidence must identify its source by URL')
        object.__setattr__(self, 'detail', rmodel._freeze(dict(self.detail)))

    @property
    def contradicts(self):
        return self.relation == 'contradicts'

    def to_json(self):
        return dict(kind=self.kind, source=self.source, claim=self.claim, relation=self.relation,
                    authority=self.authority, retrieved_at=self.retrieved_at, detail=dict(self.detail))


# --------------------------------------------------------------------------- anomaly
@dataclass(frozen=True)
class AnomalySignal:
    """«Something is wrong here» **without** a proposed correction.

    This is the shape A1's framework has no slot for, and it is the majority output of every semantic
    verifier: an LLM reading `c = 3×10° m/s` in a Physics context is far more reliable at saying *this is
    not a physical constant* than at saying *it must be 3×10⁸*. Recording detection separately from
    proposal is the only way to measure a signal as a **detector** and as a **proposer** apart — which
    turns out to be the whole story for the LLM and half the story for cross-corpus on proper nouns.

    Every field the Founder listed for an LLM verifier is here: original observation · reason · context
    supplied · model/version (`detector_id`) · confidence · supporting **and contradicting** evidence.
    A block carrying an unexplained `AnomalySignal` is `SUSPECT`: not served, not repaired, queued.
    """
    block_id: str
    detector_id: str                 # 'G.llm_semantic/haiku@2026-09-06', 'D.cross_corpus/xcorpus-v1'
    reason: str
    span: str = ''                   # the exact substring the detector objects to, when it can point
    observed: Any = None
    confidence: float = 0.0
    context_supplied: Mapping[str, Any] = field(default_factory=dict)   # what the detector was shown
    evidence: Sequence[EvidenceRef] = ()
    severity: str = 'unknown'        # teaching_critical | display | unknown — feeds the router

    SEVERITIES = ('teaching_critical', 'display', 'unknown')

    def __post_init__(self):
        object.__setattr__(self, 'context_supplied', rmodel._freeze(dict(self.context_supplied)))
        object.__setattr__(self, 'evidence', tuple(self.evidence))
        object.__setattr__(self, 'confidence', float(self.confidence))
        if self.severity not in self.SEVERITIES:
            raise ValueError(f'severity must be one of {self.SEVERITIES}, got {self.severity!r}')

    @property
    def layer(self):
        return self.detector_id.split('.', 1)[0]

    def supporting(self):
        return tuple(e for e in self.evidence if e.relation == 'supports')

    def contradicting(self):
        return tuple(e for e in self.evidence if e.contradicts)

    def as_signal(self, signal_id=None):
        """Project onto A1's `Signal` so a repairer or a `token_signal_provider` may attach it — an
        anomaly is, by construction, an **objection** to the observed value, and A1's registry treats an
        `objects` signal from a provider as a veto."""
        return rmodel.Signal(signal_id or self.detector_id.split('/')[0],
                             rmodel.SignalVerdict.OBJECTS, self.confidence,
                             dict(reason=self.reason, span=self.span, severity=self.severity,
                                  detector=self.detector_id,
                                  context_supplied=dict(self.context_supplied),
                                  supporting=[e.to_json() for e in self.supporting()],
                                  contradicting=[e.to_json() for e in self.contradicting()]))

    def to_json(self):
        return dict(block_id=self.block_id, detector_id=self.detector_id, reason=self.reason,
                    span=self.span, observed=self.observed, confidence=round(self.confidence, 4),
                    severity=self.severity, context_supplied=dict(self.context_supplied),
                    supporting_evidence=[e.to_json() for e in self.supporting()],
                    contradicting_evidence=[e.to_json() for e in self.contradicting()])


# --------------------------------------------------------------------------- decision
@dataclass(frozen=True)
class TrustDecision:
    """The whole evidence record for one block, and the disposition derived from it.

    Built from an A1 `engine.Outcome` (plus the anomalies and human records A1's engine cannot carry), or
    replayed from ledger rows. `disposition` is a pure function of the record and `explain()` prints the
    derivation, so a Founder can check any verdict by eye rather than by trusting the code.
    """
    block_id: str
    observations: Sequence[rmodel.Observation] = ()
    anomalies: Sequence[AnomalySignal] = ()
    candidates: Sequence[rmodel.RepairCandidate] = ()
    validations: Sequence[rmodel.ValidationResult] = ()
    evidence: Sequence[EvidenceRef] = ()
    human: Sequence[Any] = ()                 # `human.CorrectionRecord`s, kept opaque to avoid a cycle
    pipeline_disposition: str = Disposition.TRUSTED
    withhold_reasons: Sequence[str] = ()
    provenance: Mapping[str, Any] = field(default_factory=dict)
    corpus_version: str | None = None
    decided_at: str = ''

    def __post_init__(self):
        for f in ('observations', 'anomalies', 'candidates', 'validations', 'evidence', 'human',
                  'withhold_reasons'):
            object.__setattr__(self, f, tuple(getattr(self, f)))
        object.__setattr__(self, 'provenance', rmodel._freeze(dict(self.provenance)))
        if not self.decided_at:
            object.__setattr__(self, 'decided_at', datetime.now(timezone.utc).isoformat(timespec='seconds'))

    # ---- evidence views
    def supporting(self):
        out = [e for e in self.evidence if e.relation == 'supports']
        for a in self.anomalies:
            out.extend(a.supporting())
        return tuple(out)

    def contradicting(self):
        """The Founder asked for this by name and it is the half everyone forgets to store."""
        out = [e for e in self.evidence if e.contradicts]
        for a in self.anomalies:
            out.extend(a.contradicting())
        return tuple(out)

    def validated_candidates(self):
        rej = any(v.verdict == rmodel.Verdict.REJECTED for v in self.validations)
        ok = any(v.validated for v in self.validations)
        if rej or not ok:
            return ()
        return tuple(c for c in self.candidates if not c.contradicting())

    def independent_layers(self):
        """Distinct signal layers that SUPPORT any candidate. Independence, not count, is what makes
        evidence strong — two readings of the same OCR stack are one signal, not two."""
        out = set()
        for c in self.candidates:
            out.update(c.independent_support())
        return sorted(out)

    def accepted_human(self):
        return tuple(h for h in self.human if getattr(h, 'status', None) == 'ACCEPTED')

    # ---- the derivation
    def derive(self):
        """(disposition, reasons). Fail-closed, and ordered so that **disagreement beats confidence**."""
        reasons = []
        vc = self.validated_candidates()
        proposed = {json.dumps(c.proposed_value, ensure_ascii=False, default=str) for c in vc}

        acc = self.accepted_human()
        if acc:
            reasons.append(f'human_accepted:{len(acc)}')
            if len(proposed) > 1 or any(json.dumps(getattr(h, 'proposed', None), ensure_ascii=False,
                                                   default=str) not in proposed for h in acc if proposed):
                return Disposition.CONFLICT, tuple(reasons + ['human_vs_machine_disagree'])
            return Disposition.HUMAN_VERIFIED, tuple(reasons)

        if len(proposed) > 1:
            return Disposition.CONFLICT, ('candidates_disagree:' + str(len(proposed)),)

        if vc:
            residual = [r for r in self.withhold_reasons
                        if not any(r in (tuple(c.provenance.get('covers_reasons') or ()) + (c.failure_class,))
                                   for c in vc)]
            if residual:
                return Disposition.WITHHELD, tuple(['validated_repair_but_residual'] + residual)
            return Disposition.VALIDATED_REPAIR, tuple(f'repaired:{c.rule_id}' for c in vc)

        if self.candidates:
            if any(c.contradicting() for c in self.candidates):
                return Disposition.CONFLICT, tuple(f'contradicted:{c.rule_id}' for c in self.candidates)
            return CORRECTION_PROPOSED, tuple(f'proposed:{c.rule_id}' for c in self.candidates)

        if self.anomalies:
            # detected, unexplained. NOT withheld-by-guard and NOT trusted: a third state, on purpose.
            return Disposition.SUSPECT, tuple(f'anomaly:{a.detector_id}' for a in self.anomalies)

        if self.pipeline_disposition == Disposition.WITHHELD:
            return Disposition.WITHHELD, tuple(self.withhold_reasons)
        return self.pipeline_disposition, ()

    @property
    def disposition(self):
        return self.derive()[0]

    @property
    def servable(self):
        return self.disposition in SERVABLE

    def explain(self):
        d, why = self.derive()
        return (f'{self.block_id}: {d} ({", ".join(why) or "unchanged"}) · '
                f'{len(self.observations)} observation(s) · {len(self.anomalies)} anomaly · '
                f'{len(self.candidates)} candidate · layers {self.independent_layers() or "-"} · '
                f'{len(self.supporting())} supporting / {len(self.contradicting())} contradicting evidence')

    def to_json(self):
        d, why = self.derive()
        return dict(trust_version=TRUST_VERSION, block_id=self.block_id, disposition=d, reasons=list(why),
                    servable=self.servable, decided_at=self.decided_at, corpus_version=self.corpus_version,
                    pipeline_disposition=self.pipeline_disposition,
                    withhold_reasons=list(self.withhold_reasons),
                    observations=[o.to_json() for o in self.observations],
                    anomalies=[a.to_json() for a in self.anomalies],
                    candidates=[c.to_json() for c in self.candidates],
                    validations=[v.to_json() for v in self.validations],
                    supporting_evidence=[e.to_json() for e in self.supporting()],
                    contradicting_evidence=[e.to_json() for e in self.contradicting()],
                    human=[h.to_json() for h in self.human if hasattr(h, 'to_json')],
                    independent_layers=self.independent_layers(), provenance=dict(self.provenance))

    # ---- construction
    @classmethod
    def from_outcome(cls, outcome, ctx=None, anomalies=(), evidence=(), human=(), corpus_version=None):
        return cls(block_id=outcome.block_id,
                   observations=tuple(ctx.observations) if ctx else (),
                   anomalies=tuple(anomalies), candidates=tuple(outcome.candidates),
                   validations=tuple(outcome.validations), evidence=tuple(evidence), human=tuple(human),
                   pipeline_disposition=(ctx.disposition if ctx else Disposition.TRUSTED),
                   withhold_reasons=tuple(ctx.withhold_reasons) if ctx else (),
                   provenance=dict(ctx.page) if ctx else {}, corpus_version=corpus_version)
