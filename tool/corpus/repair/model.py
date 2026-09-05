#!/usr/bin/env python3
"""Round 5 · the data-accuracy repair framework — the value types.

Founder order (§2-§4): every value carries an explicit **disposition**, a source observation is
**never overwritten**, and every repair is traceable
`source -> observation -> failure -> repair rule -> supporting signals -> validation -> final disposition`.

Nothing in this module knows about OCR, Vietnamese, maths or the pipeline: it is the contract that
Lane A1 (text), Lane A2 (`tool/corpus/mathfix/`) and Lane D (the legacy ledger consumer) share.

The types are **frozen dataclasses**: a repairer cannot mutate the observation it was handed, which is
how "never overwrite the source observation" is enforced in code rather than asserted in prose.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

FRAMEWORK_VERSION = 'repair-v1'


# ---------------------------------------------------------------- dispositions
class Disposition:
    """The seven dispositions of the Founder's data-versioning order (§14). Strings, not an Enum, so a
    ledger line stays readable and a consumer in another lane can compare without importing this module."""

    ORIGINAL_OBSERVATION = 'ORIGINAL_OBSERVATION'   # what a source actually produced; immutable, forever
    REPAIRED_CANDIDATE = 'REPAIRED_CANDIDATE'       # a proposal. NEVER served. NEVER trusted.
    VALIDATED_REPAIR = 'VALIDATED_REPAIR'           # a candidate an independent validator confirmed
    TRUSTED = 'TRUSTED'                             # eligible to be served (a separate, Founder-gated act)
    WITHHELD = 'WITHHELD'                           # detected wrong, or not confirmed: not served
    LEGACY = 'LEGACY'                               # produced by a superseded pipeline, kept for comparison
    SUPERSEDED = 'SUPERSEDED'                       # replaced by a later disposition; kept, never deleted

    # Founder addendum (ACCURACY RECOVERY ARCHITECTURE), added because the existing set had no equivalent:
    SUSPECT = 'SUSPECT'                             # a failure was DETECTED and no repair was confirmed
    HUMAN_VERIFIED = 'HUMAN_VERIFIED'               # a person ruled on it - evidence with provenance, not an override
    CONFLICT = 'CONFLICT'                           # signals contradict each other and neither side is decisive

    ALL = (ORIGINAL_OBSERVATION, REPAIRED_CANDIDATE, VALIDATED_REPAIR, TRUSTED, WITHHELD, LEGACY, SUPERSEDED,
           SUSPECT, HUMAN_VERIFIED, CONFLICT)

    #: The Founder's addendum names, mapped onto what this model already expressed. «Map rather than
    #: duplicate»: RAW and CORRECTION_PROPOSED are the same states under different names, so they are
    #: aliases, not new members - a ledger reader written against either vocabulary works.
    ALIASES = {'RAW': ORIGINAL_OBSERVATION, 'CORRECTION_PROPOSED': REPAIRED_CANDIDATE}

    @classmethod
    def canonical(cls, value):
        return cls.ALIASES.get(value, value)

    #: a disposition a projection layer (pack / bridge / app) may serialise for a child to read.
    SERVABLE = frozenset({TRUSTED})

    @classmethod
    def check(cls, value):
        value = cls.canonical(value)
        if value not in cls.ALL:
            raise ValueError(f'unknown disposition {value!r}; allowed: {cls.ALL} '
                             f'(aliases: {sorted(cls.ALIASES)})')
        return value


# ---------------------------------------------------------------- verdicts
class Verdict:
    VALIDATED = 'validated'
    REJECTED = 'rejected'
    INSUFFICIENT = 'insufficient'
    ALL = (VALIDATED, REJECTED, INSUFFICIENT)


class SignalVerdict:
    SUPPORTS = 'supports'     # this signal is evidence FOR the proposed value
    OBJECTS = 'objects'       # this signal is evidence AGAINST it
    ABSTAINS = 'abstains'     # this signal has nothing to say here (counted, never treated as support)
    ALL = (SUPPORTS, OBJECTS, ABSTAINS)


class _FrozenDict(dict):
    """A dict that refuses to be written to. Cheap, JSON-serialisable, and enough to make
    `candidate.provenance['book'] = 'x'` a loud failure instead of a silent overwrite."""

    def _ro(self, *a, **k):
        raise TypeError('repair framework: this mapping is immutable (never overwrite an observation)')

    __setitem__ = __delitem__ = clear = pop = popitem = setdefault = update = _ro

    def __hash__(self):
        return hash(tuple(sorted((k, repr(v)) for k, v in self.items())))


def _freeze(x):
    """Deep-freeze a mapping/sequence so a frozen dataclass really is immutable to its holder."""
    if isinstance(x, Mapping):
        return _FrozenDict((k, _freeze(v)) for k, v in x.items())
    if isinstance(x, (list, tuple)):
        return tuple(_freeze(v) for v in x)
    return x


def _digest(*parts):
    h = hashlib.sha256()
    for p in parts:
        h.update(json.dumps(p, ensure_ascii=False, sort_keys=True, default=str).encode())
    return h.hexdigest()[:16]


# ---------------------------------------------------------------- observation
@dataclass(frozen=True)
class Observation:
    """What ONE source actually produced. The root of every trace. Immutable by construction.

    `source` is the producing stack/parser/run (`docling-ocrmac`, `current-xycut`, `human-annotator`,
    `legacy-pack@v1`). `value` is whatever that source said - text, a number, a bbox, a role.
    """
    block_id: str
    source: str
    value: Any
    provenance: Mapping[str, Any] = field(default_factory=dict)
    observation_id: str = ''

    def __post_init__(self):
        object.__setattr__(self, 'provenance', _freeze(dict(self.provenance)))
        if not self.observation_id:
            object.__setattr__(self, 'observation_id', f'{self.block_id}#{self.source}#{_digest(self.value)}')

    @property
    def disposition(self):
        return Disposition.ORIGINAL_OBSERVATION

    def to_json(self):
        return dict(observation_id=self.observation_id, block_id=self.block_id, source=self.source,
                    value=self.value, provenance=dict(self.provenance), disposition=self.disposition)


# ---------------------------------------------------------------- signal
@dataclass(frozen=True)
class Signal:
    """One third-signal reading. `signal_id` is the layer letter of the Founder's priority order plus the
    implementation name: `A.vi_lexicon`, `B.layout`, `C.numeric`, `D.consistency`, `E.human`, `F.third_stack`.

    `strength` is that signal's own 0..1 evidence weight; it is NEVER a probability of correctness and no
    threshold on it is a production trust threshold. `abstains` is recorded, not dropped: per-signal
    contribution can only be measured if we know when a signal had nothing to say.
    """
    signal_id: str
    verdict: str
    strength: float = 0.0
    detail: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.verdict not in SignalVerdict.ALL:
            raise ValueError(f'signal verdict must be one of {SignalVerdict.ALL}, got {self.verdict!r}')
        object.__setattr__(self, 'detail', _freeze(dict(self.detail)))
        object.__setattr__(self, 'strength', float(self.strength))

    @property
    def layer(self):
        """'A'..'F' - the Founder's signal-priority letter."""
        return self.signal_id.split('.', 1)[0]

    @property
    def supports(self):
        return self.verdict == SignalVerdict.SUPPORTS

    @property
    def objects(self):
        return self.verdict == SignalVerdict.OBJECTS

    def to_json(self):
        return dict(signal_id=self.signal_id, layer=self.layer, verdict=self.verdict,
                    strength=round(self.strength, 4), detail=dict(self.detail))


# ---------------------------------------------------------------- candidate
@dataclass(frozen=True)
class RepairCandidate:
    """A PROPOSAL. Its disposition is REPAIRED_CANDIDATE and it stays that way until a validator says
    otherwise - an LLM-generated candidate is exactly as untrusted as a rule-generated one (§4)."""
    block_id: str
    failure_class: str
    original_observations: Sequence[Observation]
    proposed_value: Any
    rule_id: str
    supporting_signals: Sequence[Signal] = ()
    confidence: float = 0.0
    provenance: Mapping[str, Any] = field(default_factory=dict)
    detected: Mapping[str, Any] = field(default_factory=dict)   # what the detector saw (the "failure" step of the trace)
    candidate_id: str = ''

    def __post_init__(self):
        object.__setattr__(self, 'original_observations', tuple(self.original_observations))
        object.__setattr__(self, 'supporting_signals', tuple(self.supporting_signals))
        object.__setattr__(self, 'provenance', _freeze(dict(self.provenance)))
        object.__setattr__(self, 'detected', _freeze(dict(self.detected)))
        object.__setattr__(self, 'confidence', float(self.confidence))
        if not self.original_observations:
            raise ValueError('a RepairCandidate must cite at least one original observation')
        if not self.candidate_id:
            object.__setattr__(self, 'candidate_id',
                               f'{self.block_id}#{self.rule_id}#'
                               f'{_digest(self.proposed_value, [o.observation_id for o in self.original_observations])}')

    @property
    def disposition(self):
        return Disposition.REPAIRED_CANDIDATE

    def signals_by_layer(self):
        out = {}
        for s in self.supporting_signals:
            out.setdefault(s.layer, []).append(s)
        return out

    def independent_support(self, exclude_layers=()):
        """Layers (A..F) that SUPPORT this candidate, excluding the ones named. The Founder's rule -
        <a trusted repair must be confirmed by an independent signal or source> - is a statement about
        this set, and a validator is expected to use it rather than to invent its own arithmetic."""
        skip = set(exclude_layers)
        return sorted({s.layer for s in self.supporting_signals if s.supports and s.layer not in skip})

    def objections(self):
        return self.contradicting()

    def supporting(self):
        """Signals that are evidence FOR the proposal."""
        return [s for s in self.supporting_signals if s.supports]

    def contradicting(self):
        """Signals that are evidence AGAINST it. The model holds contradicting evidence as a first-class
        citizen (Founder addendum): a candidate is not a bag of reasons to say yes, and a reader of the
        ledger sees the case against as plainly as the case for."""
        return [s for s in self.supporting_signals if s.objects]

    def abstaining(self):
        return [s for s in self.supporting_signals if s.verdict == SignalVerdict.ABSTAINS]

    def to_json(self):
        return dict(candidate_id=self.candidate_id, block_id=self.block_id, failure_class=self.failure_class,
                    disposition=self.disposition, rule_id=self.rule_id, proposed_value=self.proposed_value,
                    confidence=round(self.confidence, 4), detected=dict(self.detected),
                    original_observations=[o.to_json() for o in self.original_observations],
                    supporting_signals=[s.to_json() for s in self.supporting_signals],
                    supporting_evidence=[s.to_json() for s in self.supporting()],
                    contradictory_evidence=[s.to_json() for s in self.contradicting()],
                    provenance=dict(self.provenance))


# ---------------------------------------------------------------- validation
@dataclass(frozen=True)
class ValidationResult:
    """A validator's answer. `insufficient` is a first-class outcome and is NOT a soft yes: the engine
    treats `insufficient` exactly like `rejected` for the purpose of serving anything (fail closed)."""
    validator_id: str
    verdict: str
    evidence: Sequence[Mapping[str, Any]] = ()
    detail: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.verdict not in Verdict.ALL:
            raise ValueError(f'validation verdict must be one of {Verdict.ALL}, got {self.verdict!r}')
        object.__setattr__(self, 'evidence', tuple(_freeze(dict(e)) for e in self.evidence))
        object.__setattr__(self, 'detail', _freeze(dict(self.detail)))

    @property
    def validated(self):
        return self.verdict == Verdict.VALIDATED

    def to_json(self):
        return dict(validator_id=self.validator_id, verdict=self.verdict,
                    evidence=[dict(e) for e in self.evidence], detail=dict(self.detail))


# ---------------------------------------------------------------- ledger entry
@dataclass(frozen=True)
class LedgerEntry:
    """One immutable, append-only row of the repair ledger: the full trace for one block, one failure.

    `prior_entry_id` chains a later disposition to the one it supersedes - a value is never edited in
    place, it is superseded by a new row that names its predecessor.
    """
    block_id: str
    failure_class: str
    disposition: str
    observations: Sequence[Observation]
    candidate: RepairCandidate | None = None
    validation: ValidationResult | None = None
    final_value: Any = None
    reasons: Sequence[str] = ()
    stage: str = 'dispose'          # detect | validate | dispose | restore - which step of the trace this row is
    prior_entry_id: str | None = None
    framework_version: str = FRAMEWORK_VERSION
    entry_id: str = ''
    ts: str = ''

    STAGES = ('detect', 'validate', 'dispose', 'restore')

    def __post_init__(self):
        Disposition.check(self.disposition)
        if self.stage not in self.STAGES:
            raise ValueError(f'stage must be one of {self.STAGES}, got {self.stage!r}')
        object.__setattr__(self, 'observations', tuple(self.observations))
        object.__setattr__(self, 'reasons', tuple(self.reasons))
        if not self.entry_id:
            object.__setattr__(self, 'entry_id', _digest(self.block_id, self.failure_class, self.disposition,
                                                         self.stage,
                                                         [o.observation_id for o in self.observations],
                                                         self.candidate.candidate_id if self.candidate else None,
                                                         list(self.reasons), self.prior_entry_id))

    def to_json(self):
        return dict(entry_id=self.entry_id, ts=self.ts, framework_version=self.framework_version,
                    block_id=self.block_id, failure_class=self.failure_class, disposition=self.disposition,
                    stage=self.stage, reasons=list(self.reasons), prior_entry_id=self.prior_entry_id,
                    observations=[o.to_json() for o in self.observations],
                    candidate=self.candidate.to_json() if self.candidate else None,
                    validation=self.validation.to_json() if self.validation else None,
                    final_value=self.final_value)


def replace(obj, **kw):
    return dataclasses.replace(obj, **kw)
