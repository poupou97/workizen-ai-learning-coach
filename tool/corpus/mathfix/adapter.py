#!/usr/bin/env python3
"""The seam between this lane and Lane A1's repair framework.

Lane A2 registers plugins against `tool/corpus/repair/` (Lane A1's, `a1/round5-repair-framework`).
This branch targets `integration/round5-2026-09-06`, which does not carry that package yet, and a
lane that cannot run until another lane merges is a lane that cannot be reviewed. So:

  · if `repair` imports, `MODEL` and `REGISTRY` **are** A1's — same types, same registry, no copy;
  · if it does not, they are the stand-in below: the same names with the same semantics, enough to
    run and to test the repairer end to end.

`FRAMEWORK` says which one is in use, and `tool/tests/test_mathfix_plugin.py` asserts that when the
real package is importable it is the one that got used — so the stand-in can never quietly become
the thing this lane is actually tested against.

The stand-in is deliberately minimal. It is not a second framework and nothing outside `mathfix`
should import it.
"""
import os
import sys
from dataclasses import dataclass, field

_CORPUS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _CORPUS not in sys.path:
    sys.path.insert(0, _CORPUS)

try:                                                   # Lane A1's framework, when it is on the branch
    from repair import model as MODEL                  # noqa: F401
    from repair import registry as REGISTRY            # noqa: F401
    FRAMEWORK = 'repair-v1'
except Exception:                                      # pragma: no cover - exercised on the other branch
    MODEL = REGISTRY = None
    FRAMEWORK = 'mathfix-standin'


# ---------------------------------------------------------------- the stand-in
if MODEL is None:
    class _Disposition:
        ORIGINAL_OBSERVATION = 'ORIGINAL_OBSERVATION'
        REPAIRED_CANDIDATE = 'REPAIRED_CANDIDATE'
        VALIDATED_REPAIR = 'VALIDATED_REPAIR'
        TRUSTED = 'TRUSTED'
        WITHHELD = 'WITHHELD'
        LEGACY = 'LEGACY'
        SUPERSEDED = 'SUPERSEDED'
        ALL = (ORIGINAL_OBSERVATION, REPAIRED_CANDIDATE, VALIDATED_REPAIR, TRUSTED, WITHHELD,
               LEGACY, SUPERSEDED)
        SERVABLE = frozenset({TRUSTED})

    class _Verdict:
        VALIDATED = 'validated'
        REJECTED = 'rejected'
        INSUFFICIENT = 'insufficient'
        ALL = (VALIDATED, REJECTED, INSUFFICIENT)

    class _SignalVerdict:
        SUPPORTS = 'supports'
        OBJECTS = 'objects'
        ABSTAINS = 'abstains'
        ALL = (SUPPORTS, OBJECTS, ABSTAINS)

    @dataclass(frozen=True)
    class _Observation:
        block_id: str
        source: str
        value: object
        provenance: dict = field(default_factory=dict)
        observation_id: str = ''

        def __post_init__(self):
            if not self.observation_id:
                object.__setattr__(self, 'observation_id', f'{self.block_id}#{self.source}')

        @property
        def disposition(self):
            return _Disposition.ORIGINAL_OBSERVATION

    @dataclass(frozen=True)
    class _Signal:
        signal_id: str
        verdict: str
        strength: float = 0.0
        detail: dict = field(default_factory=dict)

        @property
        def layer(self):
            return self.signal_id.split('.', 1)[0]

        @property
        def supports(self):
            return self.verdict == _SignalVerdict.SUPPORTS

        @property
        def objects(self):
            return self.verdict == _SignalVerdict.OBJECTS

    @dataclass(frozen=True)
    class _RepairCandidate:
        block_id: str
        failure_class: str
        original_observations: tuple
        proposed_value: object
        rule_id: str
        supporting_signals: tuple = ()
        confidence: float = 0.0
        provenance: dict = field(default_factory=dict)
        detected: dict = field(default_factory=dict)
        candidate_id: str = ''

        def __post_init__(self):
            object.__setattr__(self, 'original_observations', tuple(self.original_observations))
            object.__setattr__(self, 'supporting_signals', tuple(self.supporting_signals))
            if not self.original_observations:
                raise ValueError('a RepairCandidate must cite at least one original observation')
            if not self.candidate_id:
                object.__setattr__(self, 'candidate_id', f'{self.block_id}#{self.rule_id}')

        @property
        def disposition(self):
            return _Disposition.REPAIRED_CANDIDATE

        def independent_support(self, exclude_layers=()):
            skip = set(exclude_layers)
            return sorted({s.layer for s in self.supporting_signals
                           if s.supports and s.layer not in skip})

        def objections(self):
            return [s for s in self.supporting_signals if s.objects]

    @dataclass(frozen=True)
    class _ValidationResult:
        validator_id: str
        verdict: str
        evidence: tuple = ()
        detail: dict = field(default_factory=dict)

        def __post_init__(self):
            if self.verdict not in _Verdict.ALL:
                raise ValueError(f'validation verdict must be one of {_Verdict.ALL}')
            object.__setattr__(self, 'evidence', tuple(self.evidence))

        @property
        def validated(self):
            return self.verdict == _Verdict.VALIDATED

    class _Model:
        Disposition = _Disposition
        Verdict = _Verdict
        SignalVerdict = _SignalVerdict
        Observation = _Observation
        Signal = _Signal
        RepairCandidate = _RepairCandidate
        ValidationResult = _ValidationResult

    class _Registry:
        def __init__(self):
            self._r, self._v, self._s = {}, {}, {}

        def _add(self, table, fc, pid, fn):
            if any(p == pid for p, _ in table.get(fc, ())):
                raise ValueError(f'{pid!r} already registered for failure class {fc!r}')
            table.setdefault(fc, []).append((pid, fn))
            return fn

        def repairer(self, failure_class, repairer_id, order=100):
            def deco(fn):
                fn.repairer_id, fn.failure_class = repairer_id, failure_class
                return self._add(self._r, failure_class, repairer_id, fn)
            return deco

        def validator(self, failure_class, validator_id, order=100):
            def deco(fn):
                fn.validator_id, fn.failure_class = validator_id, failure_class
                return self._add(self._v, failure_class, validator_id, fn)
            return deco

        def signal(self, signal_id):
            def deco(fn):
                fn.signal_id = signal_id
                self._s[signal_id] = fn
                return fn
            return deco

        def repairers_for(self, fc):
            return [fn for _, fn in self._r.get(fc, ())]

        def validators_for(self, fc):
            return [fn for _, fn in self._v.get(fc, ())]

        def signals(self):
            return dict(self._s)

        def failure_classes(self):
            return sorted(set(self._r) | set(self._v))

        def describe(self):
            return dict(failure_classes={fc: dict(repairers=[p for p, _ in self._r.get(fc, ())],
                                                  validators=[p for p, _ in self._v.get(fc, ())])
                                         for fc in self.failure_classes()},
                        signals=sorted(self._s))

    MODEL = _Model
    REGISTRY = _Registry()
