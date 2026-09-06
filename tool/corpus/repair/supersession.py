#!/usr/bin/env python3
"""WAL-213 · the SUPERSESSION CONTRACT — a recovered observation REPLACES a destroyed one.

Round 7 measured the defect this module exists to close:

    a recovered digit does not become a repaired block — `10 -> 10, delta 0`.

The re-crop recogniser recovered 17 of 47 unreadable fraction regions on Toán 4 Bài 61, 17 of 17
correct against the printed page, and **not one of them changed what the pipeline serves**, because
`study.block_projection` does `aug_tokens = list(tokens) + list(recovered)`. It **ADDS**. The
destroyed observation is still there, so a block can hold **two contradictory texts at once** and
nothing decides which one is the block's text. A validator asked about such a block is judging two
overlapping expressions.

WHAT THIS MODULE IS
    A **relation between observations**, not a mutation of one. `Supersession` names the
    observations that were destroyed, the observation that replaces them, the engine that produced
    it, the scales that agreed, and the region/stacking evidence that says the replacement covers
    the same printed ink. `ObservationSet.resolve()` then answers the one question the trust
    decision needs: **which observation is CURRENT for this region, and which are visible only to an
    auditor.**

WHAT IT IS NOT, AND CANNOT BECOME
  * **CONNECT != TRUST.** Nothing here is servable. `servable` is a property returning `False`, not
    a field, so no JSON can set it; `Disposition.TRUSTED` is unreachable from this module and
    `TrustEscalation` is raised at every door that could reach it.
  * **A source observation is never overwritten.** A superseded observation is carried whole,
    unmodified, in the record that supersedes it. `resolve()` returns NEW tuples; nothing in this
    file mutates an `Observation`, and round 5's frozen dataclasses make that structural.
  * **No constructor from a presentation form.** There is `from_json`, which reads exactly what
    `to_json` wrote and requires the whole trace. There is no `from_text`, no `from_line`, no
    `from_reading`. A rendering must never be able to become a relation.
  * **No fourth provenance universe.** `Observation`, `RepairCandidate`, `ValidationResult`,
    `Signal` and every `Disposition` string are round 5's own frozen `model` types, imported. The
    disposition `SUPERSEDED` already existed in the doctrine and was unused for this purpose; this
    module is what uses it.

THE THREE COVERAGE OUTCOMES, and why the middle one is the important one
    A destroyed observation is not always the same shape as the region that recovered it. Measured
    on Bài 61: of the 17 recovered regions, **4** are covered by a page-pass token that lies wholly
    inside the recogniser's crop, and **13** are covered by a token that carries OTHER PRINTED
    CONTENT as well — an item letter (`0)`), an operator, a neighbouring fraction's digit. Cutting
    such a token down to the part the crop covers would be *editing a source observation*, which is
    the one thing this framework forbids. So:

    FULL     the superseded observation's ink is inside the superseding region -> `SUPERSEDED`;
             it leaves the current view and stays in the audit view.
    PARTIAL  ink remains outside -> `CONFLICT`. **Fail closed**: neither side is current, the
             region is unresolved, and the block carrying it is not repairable. The contradiction
             is NAMED and REFUSED rather than concatenated.
    NONE     nothing was observed there at all. That is an ADDITION, not a supersession, and this
             module refuses to call it one (`Supersession` requires at least one superseded
             observation). `ABSENCE CANNOT SATISFY A POSITIVE OBLIGATION` in the other direction
             too: an empty superseded set is not a successful supersession.

SERIALISATION IS A PROVENANCE-LAUNDERING CHANNEL
    Lane E2 caught a save/load round trip *upgrading* a grounding; `validated.py` closed the same
    door for `ValidatedRepair`. `assert_supersession_not_strengthened()` closes it here, and the
    axis that matters is new: **a superseded observation that goes missing across a round trip is a
    contradiction that became invisible**, so the audit set may never shrink and a `CONFLICT` may
    never come back as a `SUPERSEDED`.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from . import model
from .model import Disposition, Observation, RepairCandidate, ValidationResult, Verdict

SUPERSESSION_VERSION = 'supersession-v1'

#: How much of a superseded observation's ink must lie inside the superseding region before the
#: replacement is allowed to stand alone. Not a trust threshold and not tunable per run: it is the
#: geometric statement «this crop covers that token», and anything below it means printed content
#: would be lost. Deliberately just under 1.0 for float/rounding noise in normalised bboxes.
FULL_COVERAGE = 0.98

#: Below this, an observation is not considered to be in the region at all (detector noise, a token
#: whose corner grazes the padded crop). Between the two the outcome is CONFLICT, never a silent
#: choice.
TOUCH_COVERAGE = 0.05

FULL = 'FULL'
PARTIAL = 'PARTIAL'
NONE = 'NONE'
COVERAGE_ALL = (FULL, PARTIAL, NONE)


class SupersessionError(ValueError):
    """Raised instead of building a relation that cannot show its own trace. Fail closed."""


class SupersessionConflict(SupersessionError):
    """Two supersessions disagree, or a chain closes on itself. Never resolved by picking one."""


class TrustEscalation(SupersessionError):
    """Something tried to make a supersession servable or trusted. There is no legitimate path."""


class PopulationInadequate(AssertionError):
    """The population a rule was validated on does not contain the case the rule is about.

    Round 7's structural finding: *the tests were not missing, the populations were.* A suite that
    proves a supersession rule on a fixture containing no supersession has proved nothing, and a
    gate that prints `0/0 present · PASS` is green because its subject is absent.
    """


def _digest(*parts):
    h = hashlib.sha256()
    for p in parts:
        h.update(json.dumps(p, ensure_ascii=False, sort_keys=True, default=str).encode())
    return h.hexdigest()[:16]


def _bbox4(b):
    """`(x0, y0, x1, y1)` from either a 4-tuple or an `(x, y, w, h)` token box, or None."""
    if b is None:
        return None
    v = [float(x) for x in b]
    if len(v) != 4:
        raise SupersessionError(f'a box needs four numbers, got {b!r}')
    return tuple(v)


def _area_fraction(inner, outer):
    """How much of `inner` lies inside `outer`, by area. Both `(x0, y0, x1, y1)`."""
    if inner is None or outer is None:
        return 0.0
    ix0, iy0, ix1, iy1 = inner
    ox0, oy0, ox1, oy1 = outer
    w, h = max(0.0, ix1 - ix0), max(0.0, iy1 - iy0)
    if w <= 0 or h <= 0:
        return 0.0
    dx = max(0.0, min(ix1, ox1) - max(ix0, ox0))
    dy = max(0.0, min(iy1, oy1) - max(iy0, oy0))
    return (dx * dy) / (w * h)


# ---------------------------------------------------------------- region evidence
@dataclass(frozen=True)
class RegionEvidence:
    """WHERE on the page the replacement was read, and WHAT independent readings agreed.

    A supersession without this is a claim that one string should replace another because a machine
    said so. With it, a reader can go back to the printed page and check. Construction fails closed
    when the evidence bag is empty: **an empty evidence bag must not construct**, for the same
    reason `0/0 present` must not print PASS.

    `agreeing_scales` is `{box kind -> the scales that returned the same string}`; `stacking_scale`
    is the scale at which the WHOLE-REGION crop showed those halves stacked in that order, which is
    the only observation that says the two halves belong to one printed fraction (round 5:
    completeness and honesty do not prove identity).
    """
    region_key: str
    boxes: Mapping[str, Any] = field(default_factory=dict)     # kind -> (x0, y0, x1, y1)
    agreeing_scales: Mapping[str, Any] = field(default_factory=dict)   # kind -> (scale, ...)
    stacking_scale: float | None = None
    detector: str = ''
    bar: Any = None                                            # (x0, y0, length, thickness)

    def __post_init__(self):
        if not self.region_key:
            raise SupersessionError('region evidence must name the region it came from')
        boxes = {k: _bbox4(v) for k, v in dict(self.boxes).items() if v is not None}
        scales = {k: tuple(float(s) for s in v) for k, v in dict(self.agreeing_scales).items() if v}
        if not boxes and not scales:
            raise SupersessionError(
                f'region evidence for {self.region_key!r} carries neither a box nor an agreeing '
                f'scale. ABSENCE CANNOT SATISFY A POSITIVE OBLIGATION: an empty evidence bag is '
                f'not evidence.')
        object.__setattr__(self, 'boxes', model._freeze(boxes))
        object.__setattr__(self, 'agreeing_scales', model._freeze(scales))
        object.__setattr__(self, 'bar', tuple(float(x) for x in self.bar) if self.bar else None)
        if self.stacking_scale is not None:
            object.__setattr__(self, 'stacking_scale', float(self.stacking_scale))

    @property
    def stacked(self):
        """Did the whole-region crop show the halves stacked? A fraction recovery with no stacking
        observation has two readings and no evidence they belong together."""
        return self.stacking_scale is not None

    @property
    def envelope(self):
        """The union box of every crop that was asked. This — not the block, not the line — is what
        a superseding observation is entitled to replace."""
        boxes = [b for b in self.boxes.values() if b]
        if not boxes:
            return None
        return (min(b[0] for b in boxes), min(b[1] for b in boxes),
                max(b[2] for b in boxes), max(b[3] for b in boxes))

    @property
    def min_agreeing(self):
        return min((len(v) for v in self.agreeing_scales.values()), default=0)

    def covers(self, bbox):
        """The share of `bbox` that lies inside the envelope. 0.0 when either is unknown."""
        return _area_fraction(_bbox4(bbox), self.envelope)

    def to_json(self):
        return dict(regionKey=self.region_key,
                    boxes={k: list(v) for k, v in self.boxes.items()},
                    agreeingScales={k: list(v) for k, v in self.agreeing_scales.items()},
                    stackingScale=self.stacking_scale, stacked=self.stacked,
                    detector=self.detector, bar=list(self.bar) if self.bar else None,
                    minAgreeing=self.min_agreeing)

    @staticmethod
    def from_json(d):
        if not isinstance(d, Mapping):
            raise SupersessionError('RegionEvidence.from_json takes the object to_json wrote')
        return RegionEvidence(region_key=d.get('regionKey') or '',
                              boxes=d.get('boxes') or {},
                              agreeing_scales=d.get('agreeingScales') or {},
                              stacking_scale=d.get('stackingScale'),
                              detector=d.get('detector') or '',
                              bar=d.get('bar'))


# ---------------------------------------------------------------- the relation
@dataclass(frozen=True)
class Supersession:
    """One recovered observation REPLACING one or more destroyed ones, with everything a reader
    needs to re-decide it.

    | required by WAL-213      | field                                                     |
    |--------------------------|-----------------------------------------------------------|
    | the original observation | `superseded` — round-5 `model.Observation`, carried whole  |
    | the superseding one      | `superseding` — same type, a different `source`            |
    | the engine               | `engine` (and `superseding.source`, which must match it)   |
    | the agreeing scales      | `region.agreeing_scales`                                   |
    | region / stacking        | `region` — boxes, bar, `stacking_scale`                    |
    | a disposition            | `disposition` — SUPERSEDED or CONFLICT, decided by COVERAGE|

    The disposition is **derived from the geometry, not passed in**: there is no argument by which a
    caller can declare a partial replacement clean.
    """
    block_id: str
    superseded: Sequence[Observation]
    superseding: Observation
    engine: str
    region: RegionEvidence
    candidate: RepairCandidate
    failure_class: str = ''
    reason: str = ''
    validation: ValidationResult | None = None
    supersession_version: str = SUPERSESSION_VERSION

    def __post_init__(self):
        sup = tuple(self.superseded)
        if not sup:
            raise SupersessionError(
                'a Supersession must cite at least one superseded observation. A recovery with '
                'nothing to replace is an ADDITION, and calling it a supersession is how an '
                'invented value acquires the authority of a replaced one.')
        if not all(isinstance(o, Observation) for o in sup):
            raise SupersessionError('superseded must be round-5 model.Observation values')
        if not isinstance(self.superseding, Observation):
            raise SupersessionError('superseding must be a round-5 model.Observation')
        if not isinstance(self.region, RegionEvidence):
            raise SupersessionError('region must be RegionEvidence — reuse the type, do not invent '
                                    'a fourth provenance universe')
        if not isinstance(self.candidate, RepairCandidate):
            raise SupersessionError('candidate must be the round-5 RepairCandidate, not a copy')
        if not self.engine:
            raise SupersessionError('a supersession must name the engine that produced the '
                                    'replacement; «some recogniser» is not provenance')
        if self.superseding.source != self.engine:
            raise SupersessionError(
                f'the superseding observation says it came from {self.superseding.source!r} but the '
                f'relation credits {self.engine!r}')
        ids = {o.observation_id for o in sup}
        if self.superseding.observation_id in ids:
            raise SupersessionError('an observation cannot supersede itself')
        for o in sup:
            if o.source == self.superseding.source:
                raise SupersessionError(
                    f'{self.superseding.source!r} cannot supersede its own observation '
                    f'{o.observation_id!r}: a replacement needs an INDEPENDENT producer, which is '
                    f'the whole reason the relation is worth recording.')
        blocks = {o.block_id for o in sup} | {self.superseding.block_id, self.block_id}
        if len(blocks) != 1:
            raise SupersessionError(f'a supersession is within one block; got {sorted(blocks)}')
        if self.validation is not None and not isinstance(self.validation, ValidationResult):
            raise SupersessionError('validation must be a round-5 model.ValidationResult')
        object.__setattr__(self, 'superseded', sup)
        object.__setattr__(self, 'failure_class',
                           self.failure_class or self.candidate.failure_class or '')

    # ------------------------------------------------------------------ derived, never passed in
    @property
    def coverage_fraction(self):
        """The share of the superseded ink this region covers. Uses each observation's own
        `provenance['bbox']`; an observation with no bbox contributes 0.0, because a replacement
        we cannot point at on the page has not been shown to cover anything."""
        vals = [self.region.covers(dict(o.provenance).get('bbox')) for o in self.superseded]
        return min(vals) if vals else 0.0

    @property
    def coverage(self):
        f = self.coverage_fraction
        if f >= FULL_COVERAGE:
            return FULL
        return PARTIAL if f > 0.0 else NONE

    @property
    def disposition(self):
        """What happens to the SUPERSEDED observations. `SUPERSEDED` only when the replacement
        covers them; otherwise `CONFLICT` — signals contradict and neither side is decisive."""
        return Disposition.SUPERSEDED if self.coverage == FULL else Disposition.CONFLICT

    @property
    def resolved(self):
        return self.disposition == Disposition.SUPERSEDED

    @property
    def servable(self):
        """Always False, like `ValidatedRepair.servable` and `MathExpression.servable`. Serving is
        a Founder act that no code in this package can perform."""
        return False

    @property
    def changed(self):
        """Does the replacement say something different from every observation it replaces?"""
        return all(o.value != self.superseding.value for o in self.superseded)

    @property
    def superseded_ids(self):
        return tuple(o.observation_id for o in self.superseded)

    @property
    def supersession_id(self):
        return f'{self.block_id}#{self.region.region_key}#{_digest(self.superseded_ids, self.superseding.observation_id)}'

    @property
    def residual_reason(self):
        """Why a PARTIAL supersession is refused, in words a reader can act on."""
        if self.coverage == FULL:
            return ''
        return (f'the replacement covers {self.coverage_fraction:.2f} of the observation it would '
                f'replace; the remainder is printed content that is not this region, and cutting a '
                f'source observation down to fit is overwriting it')

    # ------------------------------------------------------------------ serialisation
    def to_json(self):
        return dict(
            supersessionId=self.supersession_id,
            supersessionVersion=self.supersession_version,
            blockId=self.block_id,
            failureClass=self.failure_class,
            engine=self.engine,
            disposition=self.disposition,
            coverage=self.coverage,
            coverageFraction=round(self.coverage_fraction, 4),
            resolved=self.resolved,
            changed=self.changed,
            servable=self.servable,
            reason=self.reason,
            residualReason=self.residual_reason,
            region=self.region.to_json(),
            superseded=[o.to_json() for o in self.superseded],
            supersededDisposition=self.disposition,
            superseding=self.superseding.to_json(),
            candidate=self.candidate.to_json(),
            validation=self.validation.to_json() if self.validation else None,
        )

    def to_block_json(self):
        """The SMALL projection a TSL region / block carries. Carries NO value on either side: the
        superseded text and the replacement both stay corpus-side. A renderer can count the
        contradiction and name its engine; it cannot read either half of it."""
        return dict(
            supersessionId=self.supersession_id,
            disposition=self.disposition,
            supersededObservations=len(self.superseded),
            supersedingEngine=self.engine,
            coverage=self.coverage,
            agreeingScales=self.region.min_agreeing,
            stacked=self.region.stacked,
            resolved=self.resolved,
            changed=self.changed,
            servable=self.servable,
        )

    @staticmethod
    def from_json(d):
        """Structure -> structure. Reads exactly what `to_json` wrote and requires the whole trace.

        There is deliberately no `from_text` / `from_reading`: a rendering must never become a
        relation between observations.
        """
        if not isinstance(d, Mapping):
            raise SupersessionError('from_json takes the object to_json wrote, not a string')
        if d.get('servable'):
            raise TrustEscalation('refusing to read a supersession that claims to be servable')
        if d.get('disposition') == Disposition.TRUSTED:
            raise TrustEscalation('a supersession is never TRUSTED; that is a Founder gate and this '
                                  'type has no input for it')
        missing = [k for k in ('blockId', 'engine', 'region', 'superseded', 'superseding', 'candidate')
                   if not d.get(k)]
        if missing:
            raise SupersessionError(
                f'a supersession cannot be read without {missing} — a relation that cannot show the '
                f'observation it replaced, the one that replaced it, and where on the page, is not a '
                f'relation')
        sup = tuple(_obs_from_json(o) for o in d['superseded'])
        return Supersession(
            block_id=d['blockId'], superseded=sup, superseding=_obs_from_json(d['superseding']),
            engine=d['engine'], region=RegionEvidence.from_json(d['region']),
            candidate=_candidate_from_json(d['candidate'], sup),
            failure_class=d.get('failureClass') or '', reason=d.get('reason') or '',
            validation=_validation_from_json(d.get('validation')),
            supersession_version=d.get('supersessionVersion') or SUPERSESSION_VERSION)


def _obs_from_json(o):
    return Observation(block_id=o['block_id'], source=o['source'], value=o['value'],
                       provenance=o.get('provenance') or {},
                       observation_id=o.get('observation_id') or '')


def _candidate_from_json(c, fallback_obs=()):
    obs = tuple(_obs_from_json(o) for o in c.get('original_observations') or ()) or tuple(fallback_obs)
    return RepairCandidate(
        block_id=c['block_id'], failure_class=c['failure_class'], original_observations=obs,
        proposed_value=c['proposed_value'], rule_id=c['rule_id'],
        supporting_signals=tuple(model.Signal(s['signal_id'], s['verdict'], s.get('strength', 0.0),
                                              s.get('detail') or {})
                                 for s in c.get('supporting_signals') or ()),
        confidence=c.get('confidence', 0.0), provenance=c.get('provenance') or {},
        detected=c.get('detected') or {}, candidate_id=c.get('candidate_id') or '')


def _validation_from_json(v):
    if not v:
        return None
    return ValidationResult(v['validator_id'], v['verdict'], evidence=tuple(v.get('evidence') or ()),
                            detail=v.get('detail') or {})


# ---------------------------------------------------------------- resolution
@dataclass(frozen=True)
class Resolution:
    """The answer the trust decision needs: which observations are CURRENT, which are audit-only,
    and which region could not be decided at all.

    `usable` is the fail-closed switch. It is False whenever ANY region in the block is unresolved,
    because a block holding one undecided contradiction is a block whose text nobody can name.
    """
    block_id: str
    current: Sequence[Observation]
    superseded: Sequence[Observation]
    conflicted: Sequence[Observation]
    by_region: Mapping[str, Any]
    reasons: Sequence[str] = ()

    @property
    def usable(self):
        return not self.conflicted

    @property
    def audit_only(self):
        """Everything a validator must NOT read but an auditor must be able to."""
        return tuple(self.superseded) + tuple(self.conflicted)

    def current_for(self, region_key):
        """EXACTLY ONE current observation for a region, or a refusal. Never «the first one»."""
        entry = dict(self.by_region).get(region_key)
        if entry is None:
            raise SupersessionError(f'no region {region_key!r} in this resolution')
        cur = entry.get('current') or ()
        if len(cur) != 1:
            raise SupersessionConflict(
                f'region {region_key!r} has {len(cur)} current observations, not exactly one; a '
                f'trust decision may not choose between them')
        return cur[0]

    def to_json(self):
        return dict(blockId=self.block_id, usable=self.usable,
                    current=[o.to_json() for o in self.current],
                    superseded=[o.to_json() for o in self.superseded],
                    conflicted=[o.to_json() for o in self.conflicted],
                    byRegion={k: dict(regionKey=k, disposition=v['disposition'],
                                      coverage=v['coverage'],
                                      current=[o.observation_id for o in v.get('current') or ()],
                                      superseded=[o.observation_id for o in v.get('superseded') or ()])
                              for k, v in dict(self.by_region).items()},
                    reasons=list(self.reasons))


class ObservationSet:
    """The observations of ONE block, plus the supersession relations over them.

    Immutable in the way that matters: `with_supersession` returns a NEW set, and `resolve()`
    returns new tuples of the SAME `Observation` objects. No method here writes to an observation.
    """

    def __init__(self, block_id, observations=(), supersessions=()):
        self.block_id = block_id
        self._observations = tuple(observations)
        self._supersessions = tuple(supersessions)
        for o in self._observations:
            if o.block_id != block_id:
                raise SupersessionError(f'observation {o.observation_id!r} is not in block {block_id!r}')
        for s in self._supersessions:
            self._check(s)

    # ------------------------------------------------------------------ build
    def _check(self, s):
        if not isinstance(s, Supersession):
            raise SupersessionError('ObservationSet takes Supersession relations only')
        if s.block_id != self.block_id:
            raise SupersessionError(f'supersession {s.supersession_id!r} is not in block '
                                    f'{self.block_id!r}')
        known = {o.observation_id for o in self._observations}
        unknown = [o.observation_id for o in s.superseded if o.observation_id not in known]
        if unknown:
            raise SupersessionError(
                f'supersession {s.supersession_id!r} supersedes {unknown}, which this block never '
                f'observed. A relation to an observation nobody made is not auditable.')
        if s.superseding.observation_id in {o.observation_id for o in s.superseded}:
            raise SupersessionConflict('a supersession chain closed on itself')

    def with_supersession(self, s):
        self._check(s)
        return ObservationSet(self.block_id, self._observations + (s.superseding,),
                              self._supersessions + (s,))

    def with_observations(self, obs):
        return ObservationSet(self.block_id, self._observations + tuple(obs), self._supersessions)

    # ------------------------------------------------------------------ read
    @property
    def observations(self):
        return self._observations

    @property
    def supersessions(self):
        return self._supersessions

    def resolve(self):
        """Decide, per region, which observation is current.

        The rules, in order, and every one of them fail-closed:

        1. A superseded observation whose replacement covers it FULLY leaves the current view and
           enters the audit view with disposition `SUPERSEDED`.
        2. A superseded observation the replacement covers only PARTIALLY is `CONFLICT`. **Both**
           it and its replacement leave the current view: the block holds an undecided
           contradiction, and a validator must not be handed either half of it.
        3. Two supersessions naming the same observation are combined by COVERAGE, not by order.
           Two DIFFERENT replacements for the same observation whose regions overlap is a
           `SupersessionConflict`, never a last-one-wins.
        4. A chain (A superseded by B, B superseded by C) resolves to C. A cycle raises.
        """
        by_obs = {}
        for s in self._supersessions:
            for o in s.superseded:
                by_obs.setdefault(o.observation_id, []).append(s)
        self._assert_acyclic()

        superseded, conflicted, reasons = {}, {}, []
        blocked_regions = set()
        for oid, rels in sorted(by_obs.items()):
            obs = next(o for o in self._observations if o.observation_id == oid)
            self._assert_no_overlap(obs, rels)
            covered = _union_coverage(obs, rels)
            if covered >= FULL_COVERAGE:
                superseded[oid] = obs
            else:
                conflicted[oid] = obs
                for r in rels:
                    blocked_regions.add(r.region.region_key)
                reasons.append(
                    f'{oid}: replaced over {covered:.2f} of its ink by '
                    f'{sorted(r.region.region_key for r in rels)} — the remainder is printed '
                    f'content this region did not read, so neither reading is current')

        # rule 2: a replacement whose superseded partner is unresolved is not current either.
        blocked_new = {s.superseding.observation_id for s in self._supersessions
                       if s.region.region_key in blocked_regions}
        current, conflicted_new = [], []
        for o in self._observations:
            if o.observation_id in superseded or o.observation_id in conflicted:
                continue
            if o.observation_id in blocked_new:
                conflicted_new.append(o)
                continue
            current.append(o)

        by_region = {}
        for s in self._supersessions:
            key = s.region.region_key
            entry = by_region.setdefault(key, dict(disposition=s.disposition, coverage=s.coverage,
                                                   current=[], superseded=[]))
            entry['superseded'].extend(s.superseded)
            if key not in blocked_regions:
                entry['current'] = [s.superseding]
                entry['disposition'] = Disposition.SUPERSEDED
            else:
                entry['current'] = []
                entry['disposition'] = Disposition.CONFLICT
                entry['coverage'] = PARTIAL
        for k, v in by_region.items():
            v['current'] = tuple(v['current'])
            v['superseded'] = tuple(v['superseded'])

        return Resolution(block_id=self.block_id, current=tuple(current),
                          superseded=tuple(superseded.values()),
                          conflicted=tuple(conflicted.values()) + tuple(conflicted_new),
                          by_region=by_region, reasons=tuple(reasons))

    # ------------------------------------------------------------------ integrity
    def _assert_acyclic(self):
        edge = {}
        for s in self._supersessions:
            for o in s.superseded:
                edge.setdefault(o.observation_id, set()).add(s.superseding.observation_id)
        for start in edge:
            seen, stack = set(), [start]
            while stack:
                node = stack.pop()
                if node == start and seen:
                    raise SupersessionConflict(
                        f'supersession cycle through {start!r}: an observation cannot end up '
                        f'superseding itself')
                if node in seen:
                    continue
                seen.add(node)
                stack.extend(edge.get(node, ()))

    @staticmethod
    def _assert_no_overlap(obs, rels):
        """Two DIFFERENT replacements for the same observation must read disjoint regions."""
        for i, a in enumerate(rels):
            for b in rels[i + 1:]:
                if a.superseding.observation_id == b.superseding.observation_id:
                    continue
                if _area_fraction(a.region.envelope, b.region.envelope) > TOUCH_COVERAGE:
                    raise SupersessionConflict(
                        f'observation {obs.observation_id!r} is superseded by two overlapping '
                        f'regions ({a.region.region_key!r}, {b.region.region_key!r}); which reading '
                        f'is current is not something order may decide')

    def assert_conserved(self):
        """Nothing is lost and nothing is invented. Every observation this set holds ends up in
        exactly one of current / superseded / conflicted."""
        r = self.resolve()
        buckets = [o.observation_id for o in r.current] + [o.observation_id for o in r.superseded] \
            + [o.observation_id for o in r.conflicted]
        held = [o.observation_id for o in self._observations]
        if sorted(buckets) != sorted(held):
            raise SupersessionError(
                f'resolution is not conservative: held {len(held)} observations, resolution '
                f'accounts for {len(buckets)}')
        if len(set(buckets)) != len(buckets):
            raise SupersessionError('an observation appears in more than one bucket')
        return True

    def audit_trail(self):
        """Everything an auditor needs, including the readings a validator may not see."""
        r = self.resolve()
        return dict(blockId=self.block_id, supersessionVersion=SUPERSESSION_VERSION,
                    resolution=r.to_json(),
                    supersessions=[s.to_json() for s in self._supersessions])


def _union_coverage(obs, rels):
    """How much of `obs` several regions cover between them.

    Sums the per-region coverage. The regions are proved disjoint by `_assert_no_overlap` before
    this is called, so the sum is an upper bound that cannot double-count, and it is clamped to 1.0
    so a rounding artefact can never manufacture a FULL.
    """
    bbox = dict(obs.provenance).get('bbox')
    return min(1.0, sum(r.region.covers(bbox) for r in rels))


# ---------------------------------------------------------------- obligations
def assert_population_adequate(supersessions, *, minimum=1, require_resolved=True,
                               require_unresolved=True, require_changed=True, label='population'):
    """**ABSENCE CANNOT SATISFY A POSITIVE OBLIGATION.**

    A rule about supersession proved on a population containing no supersession has proved nothing.
    Round 7 found a gate printing `0/0 present · PASS` and four tests whose populations contained
    only their own precondition. This is the guard that goes red instead.

    The obligations, each of which a degenerate fixture fails:

    * at least `minimum` supersessions at all — an empty population is a FAILURE, not a pass;
    * at least one that RESOLVES (`FULL` coverage), or the resolvable path was never exercised;
    * at least one that does NOT (`PARTIAL`), or the fail-closed path was never exercised — and
      that path is the one this contract exists for;
    * at least one where the replacement says something DIFFERENT from what it replaced, or the
      population proves only that supersession is a no-op.
    """
    rels = list(supersessions)
    if len(rels) < minimum:
        raise PopulationInadequate(
            f'{label}: {len(rels)} supersessions, need at least {minimum}. A suite that never sees '
            f'a supersession cannot have validated one.')
    if require_resolved and not any(s.resolved for s in rels):
        raise PopulationInadequate(
            f'{label}: no supersession in this population RESOLVES (none has FULL coverage). The '
            f'replacement path was never exercised.')
    if require_unresolved and all(s.resolved for s in rels):
        raise PopulationInadequate(
            f'{label}: every supersession resolves. The fail-closed path — a replacement that would '
            f'destroy printed content — was never exercised, and that is the path this contract '
            f'exists for.')
    if require_changed and not any(s.changed for s in rels):
        raise PopulationInadequate(
            f'{label}: no supersession changes the value. A population where every replacement '
            f'agrees with what it replaced proves supersession is harmless, not that it works.')
    return True


def assert_no_supersession_needed(observations, supersessions, *, label='block'):
    """The «nothing to supersede» path, which may not be reached by having nothing.

    Round 7's `fixture_lineage` L5 printed `0/0 present · PASS` because a document with no crops
    satisfied a consistency check over crops. The same shape here would be «this block needs no
    supersession» returned for a block with no observations at all. So the existence obligation is
    checked first: a block that observed nothing has not been shown to need no supersession, it has
    been shown to have no evidence either way.
    """
    obs = list(observations)
    if not obs:
        raise PopulationInadequate(
            f'{label}: no observations at all. «No supersession needed» is a claim about a '
            f'population; it cannot be satisfied by the population being empty.')
    if list(supersessions):
        raise SupersessionError(f'{label}: supersessions are present, so this path does not apply')
    return True


DISPOSITION_STRENGTH = {
    Disposition.CONFLICT: 0,
    Disposition.WITHHELD: 0,
    Disposition.SUPERSEDED: 1,
    Disposition.LEGACY: 1,
    Disposition.SUSPECT: 1,
    Disposition.ORIGINAL_OBSERVATION: 2,
    Disposition.REPAIRED_CANDIDATE: 3,
    Disposition.VALIDATED_REPAIR: 4,
    Disposition.HUMAN_VERIFIED: 5,
    Disposition.TRUSTED: 6,
}


def assert_supersession_not_strengthened(before, after):
    """A round trip must never return a supersession stronger than it went in.

    Three axes, and the second and third are specific to this relation:

    1. the disposition may not rise (`CONFLICT` -> `SUPERSEDED` is a contradiction becoming a
       decision without new evidence; anything -> `TRUSTED` is serving by serialisation);
    2. **the audit set may not shrink.** A superseded observation that disappears across a save and
       load is a contradiction that became invisible, which is worse than one that was never
       recorded, because the record now looks complete;
    3. `resolved` and `servable` may not become true, and `coverage` may not improve — geometry does
       not change by being written to disk.
    """
    b = DISPOSITION_STRENGTH.get(before.get('disposition'), -1)
    a = DISPOSITION_STRENGTH.get(after.get('disposition'), -1)
    if a > b:
        raise TrustEscalation(f'supersession disposition strengthened {before.get("disposition")!r} '
                              f'-> {after.get("disposition")!r} across a round trip')
    if len(after.get('superseded') or ()) < len(before.get('superseded') or ()):
        raise TrustEscalation('a superseded observation was dropped across a round trip — the '
                              'contradiction must survive serialisation or the record lies by '
                              'looking complete')
    if after.get('resolved') and not before.get('resolved'):
        raise TrustEscalation('an unresolved supersession became resolved across a round trip')
    if after.get('servable') and not before.get('servable'):
        raise TrustEscalation('servable became true across a round trip')
    rank = {NONE: 0, PARTIAL: 1, FULL: 2}
    if rank.get(after.get('coverage'), -1) > rank.get(before.get('coverage'), -1):
        raise TrustEscalation(f'coverage improved {before.get("coverage")!r} -> '
                              f'{after.get("coverage")!r} across a round trip')
    return True


# ---------------------------------------------------------------- ledger bridge
def ledger_entries(supersession, *, stage='dispose'):
    """The append-only rows this relation writes: one for the superseded side, one for the
    proposal that replaced it. Uses round-5's `LedgerEntry` and `prior_entry_id` chaining rather
    than a new store, so a Lane-D reader that already parses the ledger sees supersession without
    learning a new vocabulary.
    """
    first = model.LedgerEntry(
        block_id=supersession.block_id, failure_class=supersession.failure_class,
        disposition=supersession.disposition, stage=stage,
        observations=supersession.superseded,
        reasons=tuple(r for r in (supersession.reason, supersession.residual_reason) if r))
    second = model.LedgerEntry(
        block_id=supersession.block_id, failure_class=supersession.failure_class,
        disposition=Disposition.REPAIRED_CANDIDATE, stage=stage,
        observations=(supersession.superseding,), candidate=supersession.candidate,
        validation=supersession.validation,
        reasons=(f'supersedes {",".join(supersession.superseded_ids)}',),
        prior_entry_id=first.entry_id)
    return (first, second)


def assert_not_trusted(supersession):
    """There is no path from this module to `TRUSTED`. Called by anything that projects outward."""
    if supersession.servable:
        raise TrustEscalation('a supersession reported itself servable')
    if supersession.disposition not in (Disposition.SUPERSEDED, Disposition.CONFLICT):
        raise TrustEscalation(f'a supersession reported disposition {supersession.disposition!r}')
    if supersession.validation is not None and supersession.validation.verdict not in Verdict.ALL:
        raise TrustEscalation('a supersession carries an unknown validation verdict')
    return True
