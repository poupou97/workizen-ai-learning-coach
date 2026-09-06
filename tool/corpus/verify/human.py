#!/usr/bin/env python3
"""Round 5 · Lane A4 — the **human correction workflow**: schema, validation, versioning. No production UI.

Founder: *«Learner/Parent/Teacher/Internal Reviewer → Report/Suggest → ProposedCorrection → validation →
Accepted/Rejected → new corpus version»*, recording `{sourceBlockId, original, proposed, reason, reporter
type, source evidence, timestamp, validation result, reviewer/evidence, corpus version}`, and
**«users never overwrite canonical truth»**.

The workflow, in one line each:

    REPORTED → (triage) → VALIDATING → ACCEPTED | REJECTED | NEEDS_SOURCE
    ACCEPTED → a RepairCandidate in A1's engine → a validated repair → a NEW corpus version
    at no point does a report reach the corpus by itself

## Why a human report is a *source*, not an override

The Founder's own rule: **no naive trust ladder**. Lane C produced the evidence — on LS&ĐL 5 Bài 8 a human
print read decided **against** a machine correction («Đăng Khoa» must not become «Đặng Khoa») and *for*
the machine on the river name in the same block. A human was right twice for two opposite reasons, which
is only expressible if the human's reading is evidence with provenance rather than a verdict.

So a `CorrectionRecord` carries exactly what an LLM answer or a search result carries — original
observation, proposal, reason, evidence, who, when, confidence — and goes through the same validation. The
one thing a human uniquely *can* supply is `source_evidence='print'`: a reading of the printed page, which
is the only signal that answers the question the Trusted Corpus actually asks. That is recorded as an
evidence kind, not as a rank.

## Reporter types and what each is trusted to supply

| reporter | what it can establish | what it cannot |
|---|---|---|
| `learner` | «this looks wrong» — a detection, at scale, free | what the print says |
| `parent` | the same, plus the physical book in the room | a corpus-wide rule |
| `teacher` | subject judgement; whether a claim is teachable | a substitute for the page |
| `internal_reviewer` | a page read at a stated resolution, with a recorded protocol | independence from us |
| `founder` | a decision about *policy*; the only source of a gate | the facts |

A `learner` report is therefore full-value **detection** and zero-value **proposal** — the same split the
LLM turned out to have, for the same reason: detecting that something is off is easy and being right about
the fix is not.
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # tool/corpus

from repair import model  # noqa: E402

from . import paths  # noqa: E402
from .trust import EvidenceRef  # noqa: E402

HUMAN_VERSION = 'human-correction-v1'
SIGNAL_ID = 'E.human'

REPORTERS = ('learner', 'parent', 'teacher', 'internal_reviewer', 'founder')
STATUSES = ('REPORTED', 'VALIDATING', 'ACCEPTED', 'REJECTED', 'NEEDS_SOURCE', 'SUPERSEDED')
SOURCE_EVIDENCE = ('print', 'photo', 'other_edition', 'reasoning', 'none')

#: What a reporter type may *establish* on its own. A report from a learner is a detection and never a
#: proposal, however confident it is; only a reading of the page can establish the page.
CAN_ESTABLISH = {
    'learner': ('detection',),
    'parent': ('detection', 'print_if_photographed'),
    'teacher': ('detection', 'teachability', 'print_if_photographed'),
    'internal_reviewer': ('detection', 'print_if_read_at_stated_resolution'),
    'founder': ('policy',),
}


@dataclass(frozen=True)
class CorrectionRecord:
    """One report, with every field the Founder listed and nothing that would let it skip validation."""
    record_id: str
    source_block_id: str                  # byte-identical to the SDM/TSL block id (A1 verified 0 mismatches)
    original: Any
    proposed: Any
    reason: str
    reporter_type: str
    source_evidence: str = 'none'         # print · photo · other_edition · reasoning · none
    evidence: Sequence[EvidenceRef] = ()
    corpus_version: str | None = None     # the version the report was made AGAINST
    reported_at: str = ''
    status: str = 'REPORTED'
    validation: Mapping[str, Any] = field(default_factory=dict)   # verdict · validator · independent layers
    reviewer: str | None = None
    reviewed_at: str | None = None
    resulting_corpus_version: str | None = None
    prior_record_id: str | None = None
    note: str = ''

    def __post_init__(self):
        if self.reporter_type not in REPORTERS:
            raise ValueError(f'reporter_type must be one of {REPORTERS}, got {self.reporter_type!r}')
        if self.status not in STATUSES:
            raise ValueError(f'status must be one of {STATUSES}, got {self.status!r}')
        if self.source_evidence not in SOURCE_EVIDENCE:
            raise ValueError(f'source_evidence must be one of {SOURCE_EVIDENCE}')
        object.__setattr__(self, 'evidence', tuple(self.evidence))
        object.__setattr__(self, 'validation', model._freeze(dict(self.validation)))
        if not self.reported_at:
            object.__setattr__(self, 'reported_at',
                               datetime.now(timezone.utc).isoformat(timespec='seconds'))

    # ---- what this record is allowed to do
    @property
    def establishes_print(self):
        """Only a reading of the printed page establishes what the page says — and only from a reporter
        whose protocol says how it was read."""
        if self.source_evidence not in ('print', 'photo'):
            return False
        return self.reporter_type in ('parent', 'teacher', 'internal_reviewer')

    @property
    def is_detection_only(self):
        return not self.establishes_print

    def as_signal(self):
        """Layer `E`. A record that establishes the print supports its proposal; one that does not is a
        **detection**, recorded as an objection to the observed text and never as support for a fix."""
        if self.establishes_print:
            return model.Signal(SIGNAL_ID, model.SignalVerdict.SUPPORTS, 0.85,
                                dict(record_id=self.record_id, reporter=self.reporter_type,
                                     source_evidence=self.source_evidence, reason=self.reason,
                                     evidence=[e.to_json() for e in self.evidence]))
        return model.Signal(SIGNAL_ID, model.SignalVerdict.OBJECTS, 0.4,
                            dict(record_id=self.record_id, reporter=self.reporter_type,
                                 reason=self.reason,
                                 note='a report without a page reading is a DETECTION, not a correction'))

    def to_json(self):
        return dict(schema=HUMAN_VERSION, record_id=self.record_id,
                    source_block_id=self.source_block_id, original=self.original,
                    proposed=self.proposed, reason=self.reason, reporter_type=self.reporter_type,
                    source_evidence=self.source_evidence,
                    evidence=[e.to_json() for e in self.evidence],
                    corpus_version=self.corpus_version, reported_at=self.reported_at,
                    status=self.status, validation=dict(self.validation), reviewer=self.reviewer,
                    reviewed_at=self.reviewed_at,
                    resulting_corpus_version=self.resulting_corpus_version,
                    prior_record_id=self.prior_record_id, note=self.note,
                    establishes_print=self.establishes_print)


def triage(record, independent_layers=()):
    """The validation step, as a pure function so it can be tested and argued with.

    → (new status, reason). **Nothing here writes to a corpus.** An `ACCEPTED` record becomes a
    `RepairCandidate` for A1's engine and takes exactly the same path as a machine-generated one.
    """
    if record.status not in ('REPORTED', 'VALIDATING'):
        return record.status, 'already decided'
    if record.reporter_type == 'founder':
        return 'REJECTED', ('a Founder decision is a policy act, not a corpus correction; record it as a '
                            'decision, not as a report')
    if record.original == record.proposed:
        return 'REJECTED', 'the proposal is identical to the observation'
    if record.is_detection_only:
        return 'NEEDS_SOURCE', (f'a {record.reporter_type} report with source_evidence='
                                f'{record.source_evidence!r} is a DETECTION; the printed page must still '
                                f'be read before anything changes')
    if not independent_layers:
        return 'VALIDATING', ('a page reading is one signal; it needs an independent one before it '
                              'becomes a correction (humans are wrong too)')
    return 'ACCEPTED', f'page reading corroborated by independent layer(s) {sorted(independent_layers)}'


def to_candidate(record, observations, failure_class='human_reported'):
    """An ACCEPTED record, as a `RepairCandidate` for A1's engine — a proposal like any other."""
    if record.status != 'ACCEPTED':
        raise ValueError('only an ACCEPTED record may become a candidate')
    return model.RepairCandidate(
        block_id=record.source_block_id, failure_class=failure_class,
        original_observations=observations, proposed_value=record.proposed,
        rule_id=f'human.{record.reporter_type}-v1', supporting_signals=(record.as_signal(),),
        confidence=0.7,
        provenance=dict(record_id=record.record_id, reporter=record.reporter_type,
                        source_evidence=record.source_evidence,
                        corpus_version=record.corpus_version, schema=HUMAN_VERSION),
        detected=dict(kind='human report', reason=record.reason))


class CorrectionQueue:
    """Append-only JSONL. A record is never edited: a decision is a NEW row naming the one it supersedes,
    exactly as A1's ledger works, so «what did we think on 6 September» stays answerable."""

    def __init__(self, path=None):
        self.path = path or f'{paths.OUT}/correction-queue.jsonl'
        self.records = []

    def add(self, record):
        self.records.append(record)
        os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)
        with open(self.path, 'a', encoding='utf-8') as fh:
            fh.write(json.dumps(record.to_json(), ensure_ascii=False) + '\n')
        return record

    def decide(self, record, status, reason, reviewer=None, corpus_version=None):
        import dataclasses
        new = dataclasses.replace(
            record, status=status, reviewer=reviewer,
            reviewed_at=datetime.now(timezone.utc).isoformat(timespec='seconds'),
            validation=dict(dict(record.validation), verdict=status, reason=reason),
            resulting_corpus_version=corpus_version, prior_record_id=record.record_id,
            record_id=f'{record.record_id}+{status.lower()}')
        return self.add(new)

    def open_records(self):
        latest = {}
        for r in self.records:
            latest[r.prior_record_id or r.record_id] = r
        return [r for r in latest.values() if r.status in ('REPORTED', 'VALIDATING', 'NEEDS_SOURCE')]


# --------------------------------------------------------------------------- UX research note
UX_NOTE = """\
«Báo nội dung sai» / «Đề xuất sửa» — UX research note (NOT a production design)

WHERE. On the block, not on the page. A child reading a lesson can point at one sentence; a form that asks
«which page?» is a form nobody fills in. The affordance is a long-press on a block → «Chỗ này có vẻ sai».

WHAT WE ASK FOR, IN ORDER OF HOW MUCH IT COSTS THE REPORTER.
  1. one tap: «sai» (a DETECTION — the whole value of a learner report, and free)
  2. optional: which words look wrong (a span, by tapping)
  3. optional: what it should say
  4. optional, and the only one that can actually settle it: a photo of the printed page
Steps 3 and 4 must never be required. Requiring a proposal from someone who only noticed something is how
a reporting channel turns into a source of confident wrong answers — the same failure the LLM measurement
found at 21.7 % of clean rows.

WHAT WE PROMISE, AND WHAT WE MUST NOT.
  say:        «Cảm ơn. SAM sẽ kiểm tra lại với sách in.»
  never say:  «Đã sửa.»  — because it has not been, and it will not be by this report alone.
A child must not learn that their tap rewrites the book. The honest message is that a person will check
the printed page, and the app should be able to show the report's state later («đang kiểm tra» /
«đã đối chiếu sách in»).

WHAT THE CHILD SEES AFTERWARDS. If the report is accepted, the block changes and carries the same source
explanation every other block carries — «đối chiếu với sách in», never «do bạn sửa». Attribution to a
reporter would make the corpus a place where being loud changes the text.

WHAT A TEACHER OR PARENT SEES. The same flow, plus «tôi có sách in ở đây» — which is the single question
that moves a record from NEEDS_SOURCE to VALIDATING, and therefore the only extra field worth the space.

FAILURE MODES THIS DESIGN IS TRYING TO AVOID.
  · a report queue nobody reads (so: the queue is a lane deliverable with a review rate, not a mailbox)
  · a child taught that the book is wrong when the app is wrong (so: never blame the book in the message)
  · brigading — many reports treated as evidence (so: reports are DEDUPLICATED, never counted as votes;
    frequency is not truth here either)
"""
