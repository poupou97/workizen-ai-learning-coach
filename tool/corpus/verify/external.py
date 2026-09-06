#!/usr/bin/env python3
"""Round 5 · Lane A4 — signal **`H.external`**: bounded authoritative verification. **Research only.**

Founder: *«external authoritative verification khi phù hợp … evidence phải có URL/source identity ·
retrieval timestamp · extracted claim · authority classification · relation to the candidate.
SEARCH RESULT ≠ SOURCE TRUTH. Không auto-rewrite trong production.»*

## What this module is, and what it deliberately is not

It is an **evidence store with a schema you cannot skip**, plus the routing rule that decides when
reaching outside is even appropriate. It is **not** a search client and it does not call the internet on
its own: evidence rows are recorded by a human or an agent doing a bounded lookup, and the row is refused
unless it carries every field the Founder listed (`EvidenceRef` raises on a missing URL or timestamp).

There is no code path from an external row to a corpus value. The strongest thing an external row can do
is contribute a layer-`H` `Signal` toward A1's independent-support requirement, and A1's engine still
needs a validator to say `validated`. `apply()` does not exist in this module. On purpose.

## When external verification is appropriate — and when it is a trap

The router asks this module `appropriate(...)` before anything else, because reaching outside is only
defensible for a **stable, public, checkable fact**:

| appropriate | not appropriate |
|---|---|
| a physical or chemical constant (`3×10⁸ m/s`) | ordinary Vietnamese prose |
| a historical proper noun with a canonical spelling (`Lý Thái Tổ`) | which of two valid orthographies this book uses (`hoà`/`hòa`) |
| an official state or institution name (`Cộng hoà xã hội chủ nghĩa Việt Nam`) | anything whose truth is *what this printed page says* |
| a dictionary word's existence | reading order, layout, role, attachment |

The last row of the right-hand column is the important one. **The truth we need is what the printed page
says**, and no external source knows that. External verification can tell us that `3×10°  m/s` is not a
physical constant; it cannot tell us that page 41 prints «Bạch Đằng». So `H.external` is a signal about
*plausibility in the world*, never about *fidelity to the source* — and fidelity is what a Trusted Corpus
is for. That distinction is why this signal is last in priority and why cross-corpus outranks it.
"""
from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # tool/corpus

from repair import model, registry  # noqa: E402

from . import paths  # noqa: E402
from .trust import AnomalySignal, EvidenceRef  # noqa: E402

SIGNAL_ID = 'H.external'
VALIDATOR_ID = 'external.evidence-v1'
FC_TONE = 'vi_tone_disagreement'
STORE_VERSION = 'external-v1'

#: Authority classification is a *statement about the kind of source*, never a score. The router and the
#: reports use it to say what was consulted; nothing multiplies by it.
AUTHORITY = ('official', 'reference', 'secondary', 'unknown')

#: The only content classes for which reaching outside is defensible at all.
VERIFIABLE_KINDS = ('stem_constant', 'unit', 'proper_noun_person', 'proper_noun_place',
                    'proper_noun_state', 'chemical_formula', 'dictionary_word')

#: Content classes where an external source cannot help, because the question is «what does THIS page
#: print», not «what is true in the world».
SOURCE_BOUND_KINDS = ('orthography_variant', 'reading_order', 'role', 'attachment', 'layout',
                      'common_word_meaning')


def appropriate(kind, severity='unknown'):
    """Is external verification defensible for this content class? → (bool, reason)."""
    if kind in SOURCE_BOUND_KINDS:
        return False, ('the question is what the printed page says; no external source knows that '
                       f'({kind})')
    if kind in VERIFIABLE_KINDS:
        return True, f'{kind} is a stable, public, checkable fact'
    return False, f'unclassified content ({kind}); external verification is not the default'


# --------------------------------------------------------------------------- the store
@dataclass(frozen=True)
class ExternalClaim:
    """One bounded lookup, recorded so it can be audited long after the page has changed.

    `evidence` is a tuple of `EvidenceRef(kind='external_page', …)`, and those *refuse to be constructed*
    without a URL and a retrieval timestamp — the requirement is enforced by the type, not by a reviewer
    remembering it.
    """
    block_id: str
    span: str
    kind: str
    question: str
    evidence: Sequence[EvidenceRef] = ()
    proposed: str | None = None
    researcher: str = 'lane-a4'
    recorded_at: str = ''
    note: str = ''

    def __post_init__(self):
        object.__setattr__(self, 'evidence', tuple(self.evidence))
        if not self.recorded_at:
            object.__setattr__(self, 'recorded_at',
                               datetime.now(timezone.utc).isoformat(timespec='seconds'))
        ok, why = appropriate(self.kind)
        if not ok:
            raise ValueError(f'external verification is not appropriate here: {why}')
        for e in self.evidence:
            if e.kind != 'external_page':
                raise ValueError('an ExternalClaim holds external_page evidence only')

    def supporting(self):
        return tuple(e for e in self.evidence if e.relation == 'supports')

    def contradicting(self):
        return tuple(e for e in self.evidence if e.contradicts)

    def independent_sources(self):
        """Distinct hosts. Two pages of one site are one source, and a claim resting on a single host is
        recorded as resting on a single host."""
        hosts = set()
        for e in self.evidence:
            m = re.match(r'https?://([^/]+)', e.source or '')
            if m:
                hosts.add(m.group(1).lower().removeprefix('www.'))
        return sorted(hosts)

    def authorities(self):
        return sorted({e.authority for e in self.evidence})

    def to_json(self):
        return dict(store_version=STORE_VERSION, block_id=self.block_id, span=self.span, kind=self.kind,
                    question=self.question, proposed=self.proposed, researcher=self.researcher,
                    recorded_at=self.recorded_at, note=self.note,
                    independent_sources=self.independent_sources(), authorities=self.authorities(),
                    supporting_evidence=[e.to_json() for e in self.supporting()],
                    contradicting_evidence=[e.to_json() for e in self.contradicting()])

    def as_anomaly(self, observed_text=None):
        return AnomalySignal(
            block_id=self.block_id, detector_id=f'{SIGNAL_ID}/{STORE_VERSION}',
            reason=self.question, span=self.span, observed=observed_text,
            confidence=self._confidence(), severity='teaching_critical',
            context_supplied=dict(kind=self.kind, researcher=self.researcher),
            evidence=self.evidence)

    def _confidence(self):
        """Evidence quality, not vote counting: independent hosts, an official/reference authority, and
        nothing contradicting. Capped well below 1 — an external page is never proof about a printed
        page."""
        if self.contradicting():
            return 0.2
        base = 0.2 + 0.2 * min(len(self.independent_sources()), 2)
        if {'official', 'reference'} & set(self.authorities()):
            base += 0.15
        return round(min(base, 0.75), 3)


class ExternalStore:
    """Append-only JSONL of `ExternalClaim`s. Same discipline as A1's ledger: nothing is edited, a later
    lookup supersedes an earlier one by being a later row."""

    def __init__(self, path=None):
        self.path = path or paths.EXTERNAL_STORE
        self.claims = []
        if os.path.exists(self.path):
            with open(self.path, encoding='utf-8') as fh:
                self.raw = [json.loads(x) for x in fh if x.strip()]
        else:
            self.raw = []

    def add(self, claim):
        self.claims.append(claim)
        os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)
        with open(self.path, 'a', encoding='utf-8') as fh:
            fh.write(json.dumps(claim.to_json(), ensure_ascii=False) + '\n')
        return claim

    def for_block(self, block_id):
        return [c for c in self.claims if c.block_id == block_id]

    def find(self, span):
        return [c for c in self.claims if c.span == span]


# --------------------------------------------------------------------------- plugins (A1's registry)
_STATE = dict(store=None)


def install(store):
    _STATE['store'] = store
    return store


@registry.signal(SIGNAL_ID)
def external_signal(value, ctx):
    """Layer `H` as A1's registry sees it. Supports a proposal an authoritative lookup independently
    reached; **objects** when the lookup found the observed text confirmed; abstains otherwise — which is
    the answer almost every time, and abstention is recorded rather than dropped."""
    store = _STATE['store']
    if store is None:
        return model.Signal(SIGNAL_ID, model.SignalVerdict.ABSTAINS, 0.0, dict(reason='no store installed'))
    claims = store.for_block(ctx.block_id)
    if not claims:
        return model.Signal(SIGNAL_ID, model.SignalVerdict.ABSTAINS, 0.0,
                            dict(reason='no external lookup was recorded for this block'))
    observed = ctx.primary().value if ctx.primary() else ''
    for c in claims:
        if c.proposed and isinstance(value, str) and c.proposed in value and c.proposed not in str(observed):
            return model.Signal(SIGNAL_ID, model.SignalVerdict.SUPPORTS, c._confidence(),
                                dict(claim=c.to_json()))
        if c.proposed and isinstance(observed, str) and c.proposed in observed:
            return model.Signal(SIGNAL_ID, model.SignalVerdict.OBJECTS, c._confidence(),
                                dict(reason='the authoritative form is what the text already says',
                                     claim=c.to_json()))
    return model.Signal(SIGNAL_ID, model.SignalVerdict.ABSTAINS, 0.0,
                        dict(reason='the recorded lookups do not bear on this proposal'))


@registry.token_signal_provider('external.token-v1')
def external_token_signal(observed, proposed, ctx):
    store = _STATE['store']
    if store is None or not isinstance(proposed, str):
        return None
    for c in store.for_block(ctx.block_id):
        if not c.proposed or observed.lower() not in c.span.lower():
            continue
        if c.proposed.lower() == proposed.lower() or proposed.lower() in c.proposed.lower():
            return model.Signal(SIGNAL_ID, model.SignalVerdict.SUPPORTS, c._confidence(),
                                dict(claim=c.to_json()))
        return model.Signal(SIGNAL_ID, model.SignalVerdict.OBJECTS, c._confidence(),
                            dict(reason='the authority names a different form', claim=c.to_json()))
    return None


@registry.validator(FC_TONE, validator_id=VALIDATOR_ID)
def external_validator(candidate, ctx):
    """External evidence **never validates alone** and never validates a source-bound question.

    It also never validates a candidate it generated: a claim in the store contributes layer `H`, and a
    candidate whose only support is `H` is `insufficient`. The strongest verdict this validator ever
    returns is `validated`, and only when an independent non-`H` layer already supports the same value —
    i.e. external evidence can *confirm*, it can never *decide*.
    """
    store = _STATE['store']
    if store is None:
        return None
    if candidate.contradicting():
        return model.ValidationResult(VALIDATOR_ID, model.Verdict.REJECTED,
                                      detail=dict(reason='a signal objects to this candidate'))
    claims = [c for c in store.for_block(candidate.block_id)
              if c.proposed and isinstance(candidate.proposed_value, str)
              and c.proposed in candidate.proposed_value]
    if not claims:
        return None
    layers = candidate.independent_support(exclude_layers=('H',))
    if not layers:
        return model.ValidationResult(
            VALIDATOR_ID, model.Verdict.INSUFFICIENT,
            detail=dict(reason='only external support; a search result is not source truth'))
    c = claims[0]
    if c.contradicting():
        return model.ValidationResult(VALIDATOR_ID, model.Verdict.REJECTED,
                                      detail=dict(reason='the external lookup found contradicting evidence'),
                                      evidence=[e.to_json() for e in c.contradicting()])
    return model.ValidationResult(VALIDATOR_ID, model.Verdict.VALIDATED,
                                  detail=dict(independent_layers=layers,
                                              independent_sources=c.independent_sources(),
                                              authorities=c.authorities()),
                                  evidence=[e.to_json() for e in c.supporting()])
