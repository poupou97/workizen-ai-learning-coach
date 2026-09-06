#!/usr/bin/env python3
"""Round 5 · Lane A4 — `TrustDecision`, and the three dispositions A1's set does not have.

**Audit first, reuse if an equivalent representation already exists** (Founder). It does, mostly. Lane A1's
`repair/model.py` already carries observations, signals, correction candidates *with supporting AND
contradicting signals* (`RepairCandidate.objections()`), validation results, provenance and an append-only
ledger. So `TrustDecision` here is a **read projection over A1's ledger**, not a second model.

Mapping the Founder's disposition set onto what exists:

| Founder | A1 `Disposition` | status |
|---|---|---|
| RAW | `ORIGINAL_OBSERVATION` | **exists** — alias only |
| CORRECTION_PROPOSED | `REPAIRED_CANDIDATE` | **exists** — alias only |
| WITHHELD / VALIDATED_REPAIR / TRUSTED | same names | **exists** |
| **SUSPECT** | — | **missing.** A1's engine only learns of a failure through a *repairer*, i.e. through something that yields a `RepairCandidate`. A detector that says «this is wrong and I do not know what it should be» has no way to speak. That is most of what an LLM verifier and a cross-corpus check actually produce. → `AnomalySignal` + `SUSPECT`. |
| **HUMAN_VERIFIED** | — | **missing.** Needed by the correction workflow, and distinct from TRUSTED: a human is a *source*, not an oracle. |
| **CONFLICT** | — | **missing.** Two credible signals proposing *different* corrections collapse in A1's engine into «not validated», which throws away the most informative case there is. |

Trust is evidence-based, never a ladder. There is no rule here that says LLM < internet < human. A
`TrustDecision` records *what each signal said and how independent it was*, and a disposition is only ever
derived from that record — fail-closed, so an unknown is never a soft yes.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

from repair import model as rmodel

TRUST_VERSION = 'trust-v1'


# --------------------------------------------------------------------------- dispositions
class Disposition(rmodel.Disposition):
    """A1's seven, plus the three the Founder's set needs and A1's does not have.

    Subclassing rather than redefining is deliberate: `verify.trust.Disposition.TRUSTED is
    repair.model.Disposition.TRUSTED`, so a ledger row written by A1, A2 or D compares equal without
    anyone importing this module.
    """

    RAW = rmodel.Disposition.ORIGINAL_OBSERVATION            # alias, not a new state
    CORRECTION_PROPOSED = rmodel.Disposition.REPAIRED_CANDIDATE   # alias, not a new state

    SUSPECT = 'SUSPECT'                 # an anomaly was detected; no correction is proposed. NOT servable.
    HUMAN_VERIFIED = 'HUMAN_VERIFIED'   # a validated human correction. A source, not an oracle.
    CONFLICT = 'CONFLICT'               # two credible signals disagree about the correction. NOT servable.

    ALL = rmodel.Disposition.ALL + (SUSPECT, HUMAN_VERIFIED, CONFLICT)

    #: what a projection layer may serialise for a child. `SUSPECT` and `CONFLICT` are deliberately out:
    #: a detected-but-unexplained anomaly is exactly the case where serving is worst.
    SERVABLE = frozenset({rmodel.Disposition.TRUSTED, HUMAN_VERIFIED})

    @classmethod
    def check(cls, value):
        if value not in cls.ALL:
            raise ValueError(f'unknown disposition {value!r}; allowed: {cls.ALL}')
        return value


# --------------------------------------------------------------------------- evidence
@dataclass(frozen=True)
class EvidenceRef:
    """One piece of evidence, with everything the Founder requires of an *external* one, so that internal
    and external evidence are the same shape and can be compared honestly.

    `authority` is a classification, never a score: `corpus` (our own SGK/SGV), `official` (a ministry or
    publisher), `reference` (dictionary/encyclopaedia of record), `secondary`, `unknown`. It says *what
    kind of thing spoke*, not how right it is.
    """
    kind: str                       # 'corpus_occurrence' | 'external_page' | 'llm_statement' | 'human_report' | 'deterministic'
    source: str                     # book+page for corpus, URL for external, model@version for an LLM
    claim: str                      # the extracted claim, in words
    relation: str = 'supports'      # supports | contradicts | context
    authority: str = 'unknown'
    retrieved_at: str | None = None  # REQUIRED for external evidence (see `external.py`)
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
    proposal is also the only way to measure a signal as a **detector** and as a **proposer** apart — which
    the lane brief requires, and which turns out to be the difference between the LLM's best and worst
    numbers.

    A block carrying an unexplained `AnomalySignal` becomes `SUSPECT`: not served, not repaired, queued.
    """
    block_id: str
    detector_id: str                 # 'G.llm_semantic/haiku@2026-09', 'D.cross_corpus/xcorpus-v1'
    reason: str
    span: str = ''                   # the exact substring the detector objects to, when it can point
    observed: Any = None
    confidence: float = 0.0
    context_supplied: Mapping[str, Any] = field(default_factory=dict)   # what the detector was shown
    evidence: Sequence[EvidenceRef] = ()
    severity: str = 'unknown'        # 'teaching_critical' | 'display' | 'unknown' — feeds the router

    def __post_init__(self):
        object.__setattr__(self, 'context_supplied', rmodel._freeze(dict(self.context_supplied)))
        object.__setattr__(self, 'evidence', tuple(self.evidence))
        object.__setattr__(self, 'confidence', float(self.confidence))

    def as_signal(self, signal_id=None):
        """Project onto A1's `Signal` so a repairer may attach it to a candidate as *contradicting*
        evidence — an anomaly is, by construction, an objection to the observed value."""
        return rmodel.Signal(signal_id or self.detector_id.split('/')[0],
                             rmodel.SignalVerdict.OBJECTS, self.confidence,
                             dict(reason=self.reason, span=self.span, severity=self.severity,
                                  evidence=[e.to_json() for e in self.evidence]))

    def to_json(self):
        return dict(block_id=self.block_id, detector_id=self.detector_id, reason=self.reason,
                    span=self.span, observed=self.observed, confidence=round(self.confidence, 4),
                    severity=self.severity, context_supplied=dict(self.context_supplied),
                    evidence=[e.to_json() for e in self.evidence])


# --------------------------------------------------------------------------- decision
@dataclass(frozen=True)
class TrustDecision:
    """The whole evidence record for one block, and the disposition derived from it.

    Built from an A1 `engine.Outcome` (plus the anomalies and human records A1's engine cannot carry), or
    replayed from ledger rows. It never *decides* anything an engine did not: `disposition` is a pure
    function of the record, and `explain()` prints the derivation so a Founder can check it by eye.
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
        return tuple(e for e in self.evidence if e.relation == 'supports')

    def contradicting(self):
        """The Founder asked for this by name and it is the half everyone forgets to store."""
        return tuple(e for e in self.evidence if e.contradicts)

    def validated_candidates(self):
        ok = {v.validator_id for v in self.validations if v.validated}
        rej = {v.validator_id for v in self.validations if v.verdict == rmodel.Verdict.REJECTED}
        return tuple(c for c in self.candidates
                     if ok and not rej and not c.objections()) if ok else ()

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
        """(disposition, reasons). Fail-closed, and ordered so that *disagreement beats confidence*."""
        reasons = []
        vc = self.validated_candidates()
        proposed = {json.dumps(c.proposed_value, ensure_ascii=False, default=str) for c in vc}

        acc = self.accepted_human()
        if acc:
            # a human correction that itself passed validation. Still a source: it is recorded with
            # provenance, it can be superseded, and it is not automatically better than the corpus.
            reasons.append(f'human_accepted:{len(acc)}')
            if len(proposed) > 1:
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
            return Disposition.CORRECTION_PROPOSED, tuple(f'proposed:{c.rule_id}' for c in self.candidates)

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
        return self.disposition in Disposition.SERVABLE

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
