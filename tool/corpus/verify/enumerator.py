#!/usr/bin/env python3
"""Round 5 · Lane A4 — signal **`A.enumerator`** + **`D.section_sequence`**: `I1` is not a number.

Founder defect (KHTN 9, Bài 5, pdf p27):

    printed  II – Định luật khúc xạ ánh sáng
    served   I1 - Định luật khúc xạ ánh sáng Ô C. SỐNG

Two independent defects in one heading. `furniture.py` removes the watermark tail. This module handles the
other half, and it is the cheapest signal in the whole lane:

* **Layer A — lexical.** `I1` is not a Roman numeral, not an Arabic number, and not any enumerator a
  Vietnamese textbook prints. It is a *shape* error, decidable with no corpus, no second OCR stack and no
  model. At 3× zoom the printed glyphs are two identical vertical strokes and the scanner emitted a digit
  for the second — so **agreement is useless here** (both stacks read the same strokes), which is this
  round's own thesis stated as a test case.
* **Layer D — sequence.** The book numbers its sections `I`, `II`, `III`. That sequence is observable in
  the *same book*, so the corpus carries the evidence for its own repair — the Founder's «cross-corpus
  before internet», in its cheapest possible form. `I1` breaks a sequence; `II` continues it.

The two layers are independent by construction (one reads the token, the other reads the book), so a
candidate from A can be validated by D without any lane bending A1's independent-support rule.
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # tool/corpus

import tc_score  # noqa: E402
from repair import model, registry  # noqa: E402

from . import index as ix, paths  # noqa: E402
from .trust import AnomalySignal, EvidenceRef  # noqa: E402

SIGNAL_A = 'A.enumerator'
SIGNAL_D = 'D.section_sequence'
FC_ENUM = 'enumerator_malformed'
RULE = 'enum.roman-glyph-v1'
VALIDATOR_ID = 'enum.sequence-v1'
ENUM_VERSION = 'enum-v1'

ROMAN = 'IVXLCDM'
#: Glyph confusions a scanner makes on Roman numerals in a serif display face. `1`/`l`/`|` for `I` is the
#: Founder's case; the rest are the same substitution class and cost nothing to include.
GLYPH = {'1': 'I', 'l': 'I', '|': 'I', '!': 'I', 'i': 'I', 'V': 'V', 'v': 'V', 'X': 'X', 'x': 'X',
         '0': 'O', 'O': 'I'}

#: A heading's leading enumerator: the token before a dash/dot separator at the very start of the block.
LEAD = re.compile(r'^\s*([A-Za-z0-9|!]{1,6})\s*[-–—.·:)]\s')


def roman_value(s):
    vals = dict(I=1, V=5, X=10, L=50, C=100, D=500, M=1000)
    if not s or any(c not in vals for c in s):
        return None
    total, prev = 0, 0
    for c in reversed(s):
        v = vals[c]
        total += -v if v < prev else v
        prev = max(prev, v)
    return total


def is_wellformed(tok):
    """A token that is a plain Arabic number, a plain Roman numeral, or a single letter is fine."""
    if tok.isdigit():
        return True
    up = tok.upper()
    if all(c in ROMAN for c in up) and roman_value(up) is not None:
        return True
    return len(tok) == 1 and tok.isalpha()


def repair_glyphs(tok):
    """→ the Roman numeral this token was probably meant to be, or None.

    Only fires on a token that **mixes** Roman letters with the digits/letters that look like them —
    `I1`, `1I`, `Il`, `1V`. A pure number is left alone: `11` is eleven, not `II`, and guessing there
    would be exactly the «AI confidently wrong in a different way» failure this lane exists to prevent.
    """
    if is_wellformed(tok):
        return None
    if not (1 <= len(tok) <= 6):
        return None
    has_roman = any(c in ROMAN for c in tok.upper())
    has_lookalike = any(c in '1l|!' for c in tok)
    if not (has_roman and has_lookalike):
        return None
    out = ''.join(GLYPH.get(c, c.upper()) for c in tok)
    if not all(c in ROMAN for c in out) or roman_value(out) is None:
        return None
    return out


# --------------------------------------------------------------------------- layer D: the book's sequence
class SectionSequence:
    """Which section enumerators a book actually prints, learned from the book itself."""

    def __init__(self, book, romans=None, arabics=None, pages=0):
        self.book = book
        self.romans = romans or Counter()
        self.arabics = arabics or Counter()
        self.pages = pages

    @classmethod
    def learn(cls, book, ocr_root=None):
        ocr_root = ocr_root or paths.OCR_BODY
        bdir = os.path.join(ocr_root, book)
        romans, arabics = Counter(), Counter()
        names = sorted(n for n in os.listdir(bdir) if n.endswith('.json'))
        for name in names:
            with open(os.path.join(bdir, name), encoding='utf-8') as fh:
                page = json.load(fh)
            for line in page.get('lines') or ():
                m = LEAD.match(tc_score.nfc(line.get('text') or ''))
                if not m:
                    continue
                tok = m.group(1)
                up = tok.upper()
                if all(c in ROMAN for c in up) and roman_value(up) is not None:
                    romans[up] += 1
                elif tok.isdigit():
                    arabics[tok] += 1
        return cls(book, romans, arabics, len(names))

    def attests(self, numeral):
        return self.romans.get(numeral.upper(), 0)

    def evidence_for(self, numeral):
        return [EvidenceRef(
            kind='corpus_occurrence', source=f'{self.book} (whole book)',
            claim=f'this book prints «{n}» as a section enumerator {c}×',
            relation=('supports' if n.upper() == numeral.upper() else 'context'),
            authority='corpus', detail=dict(numeral=n, count=c))
            for n, c in self.romans.most_common(6)]

    def to_json(self):
        return dict(book=self.book, pages=self.pages, romans=dict(self.romans),
                    arabics=dict(self.arabics.most_common(12)))


# --------------------------------------------------------------------------- plugins
_STATE = dict(sequences={})


def install(seq):
    _STATE['sequences'][seq.book] = seq
    return seq


def _seq_for(ctx):
    return _STATE['sequences'].get((ctx.page or {}).get('book'))


def analyse(text):
    """→ (observed enumerator, proposed enumerator) or None. Pure function, no corpus needed."""
    m = LEAD.match(tc_score.nfc(text or ''))
    if not m:
        return None
    tok = m.group(1)
    fixed = repair_glyphs(tok)
    return (tok, fixed) if fixed and fixed != tok else None


@registry.signal(SIGNAL_A)
def enumerator_signal(value, ctx):
    obs = ctx.primary().value if ctx.primary() else ''
    if not isinstance(obs, str):
        return model.Signal(SIGNAL_A, model.SignalVerdict.ABSTAINS, 0.0, dict(reason='not text'))
    got = analyse(obs)
    if not got:
        return model.Signal(SIGNAL_A, model.SignalVerdict.ABSTAINS, 0.0,
                            dict(reason='the leading enumerator is well formed or absent'))
    tok, fixed = got
    if isinstance(value, str) and value.lstrip().startswith(fixed):
        return model.Signal(SIGNAL_A, model.SignalVerdict.SUPPORTS, 0.8,
                            dict(observed=tok, proposed=fixed,
                                 reason=f'«{tok}» is neither a Roman numeral nor a number'))
    return model.Signal(SIGNAL_A, model.SignalVerdict.OBJECTS, 0.6,
                        dict(observed=tok, expected=fixed,
                             reason='the enumerator is malformed and this proposal does not fix it'))


@registry.signal(SIGNAL_D)
def sequence_signal(value, ctx):
    seq = _seq_for(ctx)
    got = analyse(ctx.primary().value if ctx.primary() else '')
    if seq is None or not got:
        return model.Signal(SIGNAL_D, model.SignalVerdict.ABSTAINS, 0.0,
                            dict(reason='no section sequence learned for this book'))
    tok, fixed = got
    n = seq.attests(fixed)
    if n and isinstance(value, str) and value.lstrip().startswith(fixed):
        return model.Signal(SIGNAL_D, model.SignalVerdict.SUPPORTS, min(0.9, 0.4 + n / 40),
                            dict(numeral=fixed, attested=n, book=seq.book,
                                 sequence=dict(seq.romans.most_common(6))))
    return model.Signal(SIGNAL_D, model.SignalVerdict.ABSTAINS, 0.0,
                        dict(reason=f'the book does not print «{fixed}» as a section enumerator',
                             sequence=dict(seq.romans.most_common(6))))


@registry.repairer(FC_ENUM, repairer_id=RULE)
def propose_enumerator(ctx):
    """Layer A proposes; layer D is attached as independent corroboration when the book attests it."""
    if not ctx.primary():
        return
    obs = ctx.primary().value
    if not isinstance(obs, str):
        return
    got = analyse(obs)
    if not got:
        return
    tok, fixed = got
    proposed = obs.replace(tok, fixed, 1)
    sigs = [model.Signal(SIGNAL_A, model.SignalVerdict.SUPPORTS, 0.8,
                         dict(observed=tok, proposed=fixed,
                              reason=f'«{tok}» is neither a Roman numeral nor a number; '
                                     f'the glyphs 1/l/| are read for I'))]
    seq = _seq_for(ctx)
    ev = []
    if seq is not None:
        n = seq.attests(fixed)
        ev = seq.evidence_for(fixed)
        sigs.append(model.Signal(SIGNAL_D, model.SignalVerdict.SUPPORTS if n else model.SignalVerdict.ABSTAINS,
                                 min(0.9, 0.4 + n / 40) if n else 0.0,
                                 dict(numeral=fixed, attested=n, book=seq.book,
                                      sequence=dict(seq.romans.most_common(6)),
                                      evidence=[e.to_json() for e in ev])))
    yield model.RepairCandidate(
        block_id=ctx.block_id, failure_class=FC_ENUM, original_observations=ctx.observations,
        proposed_value=proposed, rule_id=RULE, supporting_signals=tuple(sigs), confidence=0.7,
        provenance=dict(covers_reasons=('agree_text', 'chem_guard'), version=ENUM_VERSION),
        detected=dict(kind='malformed section enumerator', observed=tok, proposed=fixed))


@registry.validator(FC_ENUM, validator_id=VALIDATOR_ID)
def validate_enumerator(candidate, ctx):
    """Needs the book's own sequence — layer A may not validate itself."""
    if candidate.contradicting():
        return model.ValidationResult(VALIDATOR_ID, model.Verdict.REJECTED,
                                      detail=dict(reason='a signal objects to this candidate'))
    layers = candidate.independent_support(exclude_layers=('A',))
    if not layers:
        return model.ValidationResult(
            VALIDATOR_ID, model.Verdict.INSUFFICIENT,
            detail=dict(reason='the shape rule cannot confirm itself; the book must attest the numeral'))
    return model.ValidationResult(VALIDATOR_ID, model.Verdict.VALIDATED,
                                  detail=dict(independent_layers=layers),
                                  evidence=[dict(kind='section_sequence', layers=layers)])


def anomalies_of(block_id, text, where=None):
    got = analyse(text)
    if not got:
        return []
    tok, fixed = got
    return [AnomalySignal(block_id=block_id, detector_id=f'{SIGNAL_A}/{ENUM_VERSION}',
                          reason=f'«{tok}» is not a well-formed enumerator', span=tok, observed=text,
                          confidence=0.8, severity='display',
                          context_supplied=dict(where=dict(where or {})))]
