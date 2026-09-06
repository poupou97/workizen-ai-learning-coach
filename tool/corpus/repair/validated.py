#!/usr/bin/env python3
"""Round 6 · Workstream C — `ValidatedRepair`: the value that crosses from the repair laboratory
into the product-shaped pipeline.

Round 5 ended with a verified structural fact: **no file outside `tool/corpus/repair/` and
`tool/tests/` imported the `repair` package at all.** The repair path was validated and invisible.
This module is the first half of the connection; `tsl_projection.py` is the second.

    OriginalObservation -> RepairCandidate -> Deterministic Validator -> ValidatedRepair
      -> Trust/Disposition -> Trusted Structured Content -> LessonDocument -> Learning View

**CONNECT != TRUST.** Connecting the path does not set a production trust threshold - that is a
Founder gate. So `ValidatedRepair` makes «not trusted» a *type* invariant rather than a policy:

  * its `disposition` may only ever be `VALIDATED_REPAIR`. There is no field, flag, argument or
    method on this type that produces `TRUSTED`. A repair becomes trusted only by a separate,
    Founder-gated act that this module cannot express.
  * `from_entry()` refuses any ledger row that is not a validated one, and refuses a `restore`
    row - a laboratory restore (`run_gold.py --out .../tc2-p3`) is **capped** here, loudly, with
    the reason recorded on the record itself.

**No fourth provenance universe.** This type is a *bridge*, not a new vocabulary:

  * the observation / candidate / validation are round-5's own frozen `model` types, carried whole;
  * the source grounding **is** Lane E1's `semantic.graph.SourceGrounding` - imported, not re-declared,
    so the JSON a reader sees is E1's `to_json()` byte for byte;
  * the disposition strings are `repair.model.Disposition`;
  * the JSON it writes into a TSL is read by `tsl_to_lesson_document.py` and lands on the app's
    existing `SourceRef` / `ContentTrust` types.

**No constructor from a presentation form** (A2's rule for `MathExpression`, applied here). There is
`from_json`, which reads exactly what `to_json` wrote and requires the whole trace; there is no
`from_text`, no `from_summary`, and no way to build a record from a rendered string. A record that
cannot show its observation, its candidate, its validator and its grounding does not exist.

**Serialisation is a provenance-laundering channel** (Lane E2's finding: a round trip once *upgraded*
a grounding from `inheritedFromEntity` to `cellStated`). `assert_repair_not_strengthened()` asserts
across every round trip that neither the disposition nor the grounding came back stronger, and it
delegates the grounding half to E1's own `assert_not_strengthened` rather than re-implementing it.
"""
from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from . import model
from . import supersession as _sup
from .model import Disposition, Observation, RepairCandidate, ValidationResult, Verdict

# Lane E1's grounding, imported rather than re-declared (`tool/` on the path; `repair` lives in
# `tool/corpus/`). A hard import is deliberate: a "compatible" local fallback would be exactly the
# fourth provenance universe this workstream was told not to build.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from semantic import graph as _graph                                        # noqa: E402

SourceGrounding = _graph.SourceGrounding
SemanticError = _graph.SemanticError
ProvenanceLaundering = _graph.ProvenanceLaundering

INTEGRATION_VERSION = 'repair-integration-v1'

#: How strong a disposition is. Used only to prove a round trip never *raises* it. `TRUSTED` is in the
#: table because it is the thing that must never be reached, not because anything here can reach it.
DISPOSITION_STRENGTH = {
    Disposition.WITHHELD: 0,
    Disposition.CONFLICT: 0,
    Disposition.SUSPECT: 1,
    Disposition.LEGACY: 1,
    Disposition.SUPERSEDED: 1,
    Disposition.ORIGINAL_OBSERVATION: 2,
    Disposition.REPAIRED_CANDIDATE: 3,
    Disposition.VALIDATED_REPAIR: 4,
    Disposition.HUMAN_VERIFIED: 5,
    Disposition.TRUSTED: 6,
}

_VERSION_SUFFIX = re.compile(r'(?:^|[-_.])(v\d+(?:\.\d+)*)$')

#: `RepairEngine._merge` names its combined result `engine.merge`. That is the ENGINE's bookkeeping, not
#: a validator anybody wrote, and a record whose «validator + version» reads `engine.merge/unversioned`
#: has lost exactly the field a reader needs to re-decide the repair. The real validators are in
#: `detail['validators']`; `resolve_validator` puts them back.
MERGED_VALIDATOR = 'engine.merge'


class RepairIntegrityError(ValueError):
    """Raised instead of building a record that cannot show its own trace. Fail-closed by construction."""


class TrustEscalation(RepairIntegrityError):
    """Raised when something tried to make a `ValidatedRepair` trusted. There is no legitimate path."""


def version_of(plugin_id, default='unversioned'):
    """`linearisation.subsequence-v1` -> `v1`. A validator that does not version itself says so, in
    the record, rather than being given a version it never claimed."""
    m = _VERSION_SUFFIX.search(plugin_id or '')
    return m.group(1) if m else default


def resolve_validator(validation):
    """(validator_id, validator_version, all_validators) for a validation result.

    Unwraps `engine.merge` back to the validators that actually ruled. When more than one validated,
    the id becomes `a+b` - deliberately not "the first one", because a record must not credit a repair
    to a validator that was only half of the reason it passed.
    """
    vid = validation.validator_id
    all_v = dict(validation.detail.get('validators') or {})
    if vid != MERGED_VALIDATOR or not all_v:
        return vid, version_of(vid), (all_v or {vid: validation.verdict})
    passed = sorted(k for k, v in all_v.items() if v == Verdict.VALIDATED)
    if not passed:
        return vid, version_of(vid), all_v
    real = '+'.join(passed)
    return real, (version_of(passed[0]) if len(passed) == 1 else 'multi'), all_v


def _require(d, *keys):
    missing = [k for k in keys if d.get(k) in (None, '', [], {})]
    if missing:
        raise RepairIntegrityError(
            f'a ValidatedRepair cannot be built without {missing} - a record that cannot show its '
            f'observation, candidate, validator and grounding is not a record')


@dataclass(frozen=True)
class ValidatedRepair:
    """One repair a deterministic validator confirmed, with everything a reader needs to re-decide it.

    The ten things the round-6 plan requires it to retain, and where each lives:

    | required                | field                                                     |
    |-------------------------|-----------------------------------------------------------|
    | original observation    | `original_observations` (round-5 `model.Observation`)     |
    | candidate               | `candidate` (round-5 `model.RepairCandidate`)             |
    | source grounding        | `source_grounding` (Lane E1 `SourceGrounding`)            |
    | failure class           | `failure_class`                                           |
    | repair method           | `repair_method` (the rule id) + `supporting_layers`       |
    | validator + version     | `validator_id` + `validator_version`                      |
    | validation result       | `validation` (round-5 `model.ValidationResult`)           |
    | repair version          | `repair_version` (framework/rule) + `framework_version`   |
    | provenance              | `provenance` + `source_version` (replay: corpus/pipeline) |
    | disposition             | `disposition` - VALIDATED_REPAIR, and only that           |
    """
    block_id: str
    failure_class: str
    original_observations: Sequence[Observation]
    candidate: RepairCandidate
    validation: ValidationResult
    source_grounding: Any                       # semantic.graph.SourceGrounding
    repair_method: str
    validator_id: str
    validator_version: str
    repair_version: str
    source_version: Mapping[str, Any] = field(default_factory=dict)
    provenance: Mapping[str, Any] = field(default_factory=dict)
    structured_value: Any = None                # e.g. MathExpression.to_json() - structure, not a rendering
    ledger_entry_id: str | None = None
    framework_version: str = model.FRAMEWORK_VERSION
    integration_version: str = INTEGRATION_VERSION
    caps: Sequence[str] = ()                    # what this record was NOT allowed to be, and why
    #: WAL-213. The relation by which this repair's observation REPLACED a destroyed one, when the
    #: repair came from a recogniser rather than from a rule over the text that was already there.
    #: `None` for every round-5/6 repair, which is why it is optional and last: an existing record
    #: reads back unchanged, and a record that HAS one can never lose it (see `to_json`).
    supersession: Any = None                    # repair.supersession.Supersession

    #: not a field. A `ValidatedRepair` is a validated repair; it is not a trusted one.
    disposition = Disposition.VALIDATED_REPAIR

    def __post_init__(self):
        if not self.original_observations:
            raise RepairIntegrityError('a ValidatedRepair must cite at least one original observation')
        if not isinstance(self.candidate, RepairCandidate):
            raise RepairIntegrityError('candidate must be the round-5 RepairCandidate, not a copy of one')
        if not isinstance(self.validation, ValidationResult) or not self.validation.validated:
            raise RepairIntegrityError('a ValidatedRepair needs a ValidationResult whose verdict is '
                                       f'{Verdict.VALIDATED!r}')
        if not isinstance(self.source_grounding, SourceGrounding):
            raise RepairIntegrityError('source_grounding must be Lane E1 SourceGrounding - reuse the type, '
                                       'do not invent a fourth provenance universe')
        _require(dict(block_id=self.block_id, failure_class=self.failure_class,
                      repair_method=self.repair_method, validator_id=self.validator_id,
                      repair_version=self.repair_version),
                 'block_id', 'failure_class', 'repair_method', 'validator_id', 'repair_version')
        object.__setattr__(self, 'original_observations', tuple(self.original_observations))
        object.__setattr__(self, 'source_version', model._freeze(dict(self.source_version)))
        object.__setattr__(self, 'provenance', model._freeze(dict(self.provenance)))
        object.__setattr__(self, 'caps', tuple(self.caps))
        if self.supersession is not None:
            if not isinstance(self.supersession, _sup.Supersession):
                raise RepairIntegrityError(
                    'supersession must be repair.supersession.Supersession — reuse the type, do not '
                    'invent a fourth provenance universe')
            if self.supersession.block_id != self.block_id:
                raise RepairIntegrityError(
                    f'supersession is for block {self.supersession.block_id!r}, this repair is for '
                    f'{self.block_id!r}')
            if self.supersession.servable:
                raise TrustEscalation('a supersession attached to a repair claimed to be servable')
            _sup.assert_not_trusted(self.supersession)

    # ------------------------------------------------------------------ read-only projections
    @property
    def proposed_value(self):
        """What the repairer PROPOSED. Named a proposal on purpose: there is no `value` and no
        `served_value` on this type, because nothing here is servable."""
        return self.candidate.proposed_value

    @property
    def observed_value(self):
        return self.original_observations[0].value

    @property
    def changed(self):
        return self.proposed_value != self.observed_value

    @property
    def servable(self):
        """Always False, like `MathExpression.servable`. Serving is a Founder act elsewhere."""
        return False

    @property
    def supporting_layers(self):
        return self.candidate.independent_support()

    @property
    def repair_id(self):
        return f'{self.block_id}#{self.repair_method}#{self.candidate.candidate_id.rsplit("#", 1)[-1]}'

    # ------------------------------------------------------------------ construction
    @staticmethod
    def from_entry(entry, *, grounding=None, source_version=None, structured_value=None, caps=(),
                   validation=None, supersession=None):
        """Build from an append-only ledger row. The ONLY construction path from the engine.

        Refuses anything that is not a confirmed repair, and refuses a `restore` row outright: a
        laboratory restore is the pipeline serving a repair, and this type exists to say that has not
        been gated. A caller that has capped such a row passes the reason in `caps`.
        """
        if entry.stage == 'restore' or entry.disposition == Disposition.TRUSTED:
            raise TrustEscalation(
                f'ledger row {entry.entry_id} is a RESTORE ({entry.disposition}/{entry.stage}). A '
                f'ValidatedRepair is never trusted; cap the row and record the cap instead.')
        if entry.disposition != Disposition.VALIDATED_REPAIR:
            raise RepairIntegrityError(f'ledger row {entry.entry_id} has disposition '
                                       f'{entry.disposition!r}, not {Disposition.VALIDATED_REPAIR!r}')
        cand = entry.candidate
        if cand is None:
            raise RepairIntegrityError(f'ledger row {entry.entry_id} has no candidate')
        val = validation or entry.validation
        if val is None or not val.validated:
            raise RepairIntegrityError(f'ledger row {entry.entry_id} carries no validated verdict')
        g = grounding or grounding_for(cand)
        sv = dict(source_version or {})
        vid, vver, all_v = resolve_validator(val)
        prov = dict(cand.provenance)
        prov['validators'] = all_v
        prov['engineVerdict'] = val.verdict
        return ValidatedRepair(
            block_id=entry.block_id, failure_class=entry.failure_class,
            original_observations=cand.original_observations, candidate=cand, validation=val,
            source_grounding=g, repair_method=cand.rule_id,
            validator_id=vid, validator_version=vver,
            repair_version=f'{entry.framework_version}/{cand.rule_id}',
            source_version=sv, provenance=prov,
            structured_value=structured_value, ledger_entry_id=entry.entry_id,
            framework_version=entry.framework_version, caps=tuple(caps),
            supersession=supersession)

    @staticmethod
    def from_json(d):
        """Structure -> structure. Reads exactly what `to_json` wrote and requires the whole trace.

        There is deliberately no `from_text` / `from_latex` / `from_summary`: a rendering must never be
        able to become a record (A2's rule for `MathExpression`, kept here).
        """
        if not isinstance(d, Mapping):
            raise RepairIntegrityError('from_json takes the object to_json wrote, not a string')
        if d.get('disposition') != Disposition.VALIDATED_REPAIR:
            raise TrustEscalation(f'refusing to read a repair record whose disposition is '
                                  f'{d.get("disposition")!r}; only {Disposition.VALIDATED_REPAIR} exists here')
        _require(d, 'blockId', 'failureClass', 'originalObservations', 'candidate', 'validation',
                 'sourceGrounding', 'repairMethod', 'validatorId', 'repairVersion')
        obs = tuple(Observation(block_id=o['block_id'], source=o['source'], value=o['value'],
                                provenance=o.get('provenance') or {}, observation_id=o.get('observation_id') or '')
                    for o in d['originalObservations'])
        c = d['candidate']
        cand = RepairCandidate(
            block_id=c['block_id'], failure_class=c['failure_class'], original_observations=obs,
            proposed_value=c['proposed_value'], rule_id=c['rule_id'],
            supporting_signals=tuple(model.Signal(s['signal_id'], s['verdict'], s.get('strength', 0.0),
                                                  s.get('detail') or {})
                                     for s in c.get('supporting_signals') or ()),
            confidence=c.get('confidence', 0.0), provenance=c.get('provenance') or {},
            detected=c.get('detected') or {}, candidate_id=c.get('candidate_id') or '')
        v = d['validation']
        val = ValidationResult(v['validator_id'], v['verdict'], evidence=tuple(v.get('evidence') or ()),
                               detail=v.get('detail') or {})
        return ValidatedRepair(
            block_id=d['blockId'], failure_class=d['failureClass'], original_observations=obs,
            candidate=cand, validation=val,
            source_grounding=SourceGrounding.from_json(d['sourceGrounding']),
            repair_method=d['repairMethod'], validator_id=d['validatorId'],
            validator_version=d.get('validatorVersion') or version_of(d['validatorId']),
            repair_version=d['repairVersion'], source_version=d.get('sourceVersion') or {},
            provenance=d.get('provenance') or {}, structured_value=d.get('structuredValue'),
            ledger_entry_id=d.get('ledgerEntryId'),
            framework_version=d.get('frameworkVersion') or model.FRAMEWORK_VERSION,
            integration_version=d.get('integrationVersion') or INTEGRATION_VERSION,
            caps=tuple(d.get('caps') or ()),
            supersession=(_sup.Supersession.from_json(d['supersession'])
                          if d.get('supersession') else None))

    # ------------------------------------------------------------------ serialisation
    def to_json(self):
        return dict(
            repairId=self.repair_id,
            blockId=self.block_id,
            disposition=self.disposition,
            failureClass=self.failure_class,
            repairMethod=self.repair_method,
            repairVersion=self.repair_version,
            frameworkVersion=self.framework_version,
            integrationVersion=self.integration_version,
            validatorId=self.validator_id,
            validatorVersion=self.validator_version,
            validation=self.validation.to_json(),
            candidate=self.candidate.to_json(),
            originalObservations=[o.to_json() for o in self.original_observations],
            sourceGrounding=self.source_grounding.to_json(),
            supportingLayers=list(self.supporting_layers),
            contradictingSignals=[s.to_json() for s in self.candidate.contradicting()],
            changed=self.changed,
            sourceVersion=dict(self.source_version),
            provenance=dict(self.provenance),
            structuredValue=self.structured_value,
            ledgerEntryId=self.ledger_entry_id,
            servable=self.servable,
            caps=list(self.caps),
            supersession=self.supersession.to_json() if self.supersession else None,
        )

    def to_block_json(self):
        """The SMALL projection a TSL region / LessonDocument block carries inline. Deliberately no
        `proposedValue`: the proposal lives in `repairs[]` (corpus-internal, INTERNAL/RESEARCH ONLY),
        never on the block a renderer walks. A renderer can count and label it; it cannot read it."""
        return dict(
            repairId=self.repair_id,
            disposition=self.disposition,
            failureClass=self.failure_class,
            method=self.repair_method,
            repairVersion=self.repair_version,
            validatorId=self.validator_id,
            validatorVersion=self.validator_version,
            verdict=self.validation.verdict,
            supportingLayers=list(self.supporting_layers),
            changed=self.changed,
            servable=self.servable,
            structuredKind=(self.structured_value or {}).get('kind') if isinstance(self.structured_value, Mapping) else None,
            caps=list(self.caps),
            # WAL-213: the SMALL supersession projection — a count, an engine and a coverage class.
            # Never a value on either side: the destroyed reading and the replacement both stay
            # corpus-side, so a renderer can COUNT the contradiction and cannot READ it.
            supersedes=self.supersession.to_block_json() if self.supersession else None,
        )


def grounding_for(candidate, trust='trustedStructuredLesson'):
    """A `SourceGrounding` from a candidate's own provenance. Fails closed (E1 raises) when the
    candidate carries no locator beyond a block id - a repair we cannot point at on the page is not a
    repair we may carry forward."""
    prov = dict(candidate.provenance or {})
    obs_prov = dict(candidate.original_observations[0].provenance or {})
    def pick(*keys, default=None):
        for k in keys:
            for src in (prov, obs_prov):
                if src.get(k) is not None:
                    return src[k]
        return default
    book = pick('book') or (candidate.block_id or '').split(':')[0]
    return SourceGrounding(
        book=book, block_id=candidate.block_id,
        page_pdf=pick('page', 'page_pdf'), page_printed=pick('page_printed'),
        bbox=pick('bbox'), extraction=pick('extraction'), pipeline=pick('pipeline'),
        ocr_conf=pick('ocr_conf'), agreement_score=pick('text_sim', 'agreement_score'),
        trust=trust)


def assert_repair_not_strengthened(before, after):
    """A repair record must never come back from a round trip stronger than it went in.

    Lane E2 found a save/load round trip *upgrading* a grounding. The same door exists here and is
    wider: a record that came back `TRUSTED` would be a repair that became servable by being written
    to disk. Delegates the grounding/trust half to E1's `assert_not_strengthened` (one implementation,
    not two) and adds the disposition axis.
    """
    b = DISPOSITION_STRENGTH.get(before.get('disposition'), -1)
    a = DISPOSITION_STRENGTH.get(after.get('disposition'), -1)
    if a > b:
        raise ProvenanceLaundering(f'disposition strengthened {before.get("disposition")!r} -> '
                                   f'{after.get("disposition")!r} across a round trip')
    if after.get('servable') and not before.get('servable'):
        raise ProvenanceLaundering('servable became true across a round trip')
    if len(after.get('caps') or ()) < len(before.get('caps') or ()):
        raise ProvenanceLaundering('a cap was dropped across a round trip - the reason a repair was '
                                   'held back must survive serialisation')
    # WAL-213: a repair that carried a supersession must still carry it, and the supersession
    # itself must not have been laundered. A record whose contradiction disappeared across a save
    # and load looks MORE complete than the one that went in, which is the worst kind of lie.
    sb, sa = before.get('supersession'), after.get('supersession')
    if sb and not sa:
        raise ProvenanceLaundering('a supersession was dropped across a round trip — the observation '
                                   'this repair replaced must survive serialisation')
    if sb and sa:
        _sup.assert_supersession_not_strengthened(sb, sa)
    # E1's own guard, on the grounding pair. Its shape is {support, status, grounding[], ...}.
    _graph.assert_not_strengthened(
        dict(grounding=[before.get('sourceGrounding') or {}]),
        dict(grounding=[after.get('sourceGrounding') or {}]))
    return True
