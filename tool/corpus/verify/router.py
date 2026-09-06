#!/usr/bin/env python3
"""Round 5 · Lane A4 — the **router**: which verification path a block gets, and who is asked.

Founder: *«KHÔNG phải block nào cũng chạy đủ mọi lớp — cần router chọn đường xác minh theo content type ·
risk · disagreement · confidence · teaching consequence.»*

A router that escalates everything is useless, and a router that escalates nothing is a rubber stamp. So
this module makes the choice explicit and **measurable**: `route()` returns the ordered list of signals to
consult, the reason each was chosen or skipped, and whether a human is needed — and `run_router.py`
reports the resulting **human review rate** on the same evaluation sets as every other number in the lane.

## The five inputs, and what each actually changes

| input | where it comes from | what it decides |
|---|---|---|
| **content type** | role + text shape (`stem`, `enumerator`, `proper_noun`, `prose`, `table`, `option`) | which specialist signals can even apply, and whether external verification is defensible at all |
| **teaching consequence** | role + content type | whether an unresolved anomaly may be served, withheld, or must reach a human |
| **disagreement** | the SDM's own `agreement.text_sim`, `tone_disagreements`, `guards` | whether the two stacks already flagged this; round 4 proved agreement is *not* sufficient, so this raises priority but never clears a block |
| **confidence** | `ocr_conf`, and the token's position in its line | how far down the expensive path to go |
| **structural membership** | `groups` (OPTION ⊂ QUESTION, caption ⊂ figure) | whether a decision about this block is really a decision about its whole group — the 97-row audit's defect 8 |

## Two measured facts shape the default path

* **The LLM is a good detector and a bad proposer.** Measured on the injection holdout: detection recall
  **0.717** (cross-corpus 0.498–0.642) but, on text that was *already correct*, it proposed a change on
  **21.7 %** of rows and **every one of those was wrong**. So the router calls it to *detect*, and its
  proposals are never a repair path on their own — they are escalation evidence.
* **Edge tokens are riskier than interior ones.** Measured over 486,304 tokens of 12 held-out books, the
  unattested-token rate is **0.00268 first / 0.00324 last / 0.00085 interior** — the ends of a line carry
  **3–4×** the interior risk. Cheap, general, and it costs one integer per token.
"""
from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # tool/corpus

from . import external as EX, index as ix  # noqa: E402

ROUTER_VERSION = 'router-v1'

#: cost class per signal — used only to order the path and to report what a policy would spend.
COST = {'A.enumerator': 1, 'A.vi_lexicon': 1, 'B.page_furniture': 1, 'B.layout': 2, 'C.numeric': 1,
        'D.cross_corpus': 3, 'D.section_sequence': 2, 'G.llm_semantic': 20, 'H.external': 50,
        'E.human': 500}

TEACHING_CRITICAL_ROLES = frozenset({'question', 'option', 'answer', 'definition', 'objective',
                                     'stage_label', 'formula', 'table', 'heading'})

STEM = re.compile(r'[0-9]\s*[×x·]\s*10|[=<>≤≥]|\b\d+\s*(m/s|km/h|kg|cm|mm|km|ml|°C|Ω|MΩ|J|W|V|A|mol)\b'
                  r'|[⁰¹²³⁴⁵⁶⁷⁸⁹]|\b[A-Z][a-z]?\d+\b')
ENUMERATED = re.compile(r'^\s*[A-Za-z0-9|!]{1,6}\s*[-–—.·:)]\s')


@dataclass(frozen=True)
class Route:
    block_id: str
    content_type: str
    teaching_consequence: str          # teaching_critical | display | unknown
    disagreement: str                  # none | tone | text | order | guard
    confidence: float | None
    path: Sequence[str] = ()
    skipped: Mapping[str, str] = field(default_factory=dict)
    human: bool = False
    human_reason: str = ''
    group: str | None = None
    notes: Sequence[str] = ()

    @property
    def cost(self):
        return sum(COST.get(s, 1) for s in self.path) + (COST['E.human'] if self.human else 0)

    def to_json(self):
        return dict(router_version=ROUTER_VERSION, block_id=self.block_id,
                    content_type=self.content_type, teaching_consequence=self.teaching_consequence,
                    disagreement=self.disagreement, confidence=self.confidence, path=list(self.path),
                    skipped=dict(self.skipped), human=self.human, human_reason=self.human_reason,
                    group=self.group, cost=self.cost, notes=list(self.notes))


def content_type(text, role=None):
    """What kind of thing is this, for routing purposes. Deliberately coarse — a finer taxonomy would be
    a role spec, which is Lane A3's deliverable, not a router's."""
    t = text or ''
    if STEM.search(t):
        return 'stem_expression'
    if ENUMERATED.match(t):
        return 'enumerated_heading'
    if role in ('table',) or t.count('|') >= 3:
        return 'table'
    if role in ('option',):
        return 'option'
    words = ix.TOKEN.findall(t)
    if words:
        caps = sum(1 for i, w in enumerate(words) if i and w[:1].isupper())
        if len(words) <= 12 and caps >= 2:
            return 'proper_noun_phrase'
    if role in ('heading', 'chapter', 'lesson_title'):
        return 'heading'
    return 'prose'


def teaching_consequence(ctype, role=None, guards=()):
    if ctype in ('stem_expression', 'option', 'table'):
        return 'teaching_critical'
    if role in TEACHING_CRITICAL_ROLES:
        return 'teaching_critical'
    if 'agree_numbers' in (guards or ()):
        return 'teaching_critical'
    return 'display'


def disagreement_of(block):
    """What the two stacks already said. Round 4 falsified «agreement ⇒ verbatim», so this raises the
    priority of a block and **never** clears one: a block with no disagreement still gets the cheap
    signals, which is how «both stacks made the same error» is reachable at all."""
    ag = (block or {}).get('agreement') or {}
    guards = (block or {}).get('guards') or []
    if ag.get('tone_disagreements'):
        return 'tone'
    for g, name in (('agree_text', 'text'), ('agree_order', 'order'), ('agree_numbers', 'numbers')):
        if g in guards:
            return name
    if guards:
        return 'guard'
    return 'none'


def route(block_id, text, role=None, block=None, group=None, has_index=True, has_llm=True,
          has_external=True, budget='normal'):
    """→ `Route`. Pure and cheap: no corpus access, no model call. Deciding *whether* to spend must not
    itself cost anything."""
    block = block or {}
    ctype = content_type(text, role)
    tc = teaching_consequence(ctype, role, block.get('guards'))
    dis = disagreement_of(block)
    conf = block.get('ocr_conf')
    path, skipped, notes = [], {}, []

    # ---- always: the free deterministic layers. They cost one regex each and they are the only signals
    # with a measured false-correction rate of zero.
    path.append('A.enumerator')
    path.append('B.page_furniture')
    if ctype == 'stem_expression':
        path.append('C.numeric')
        notes.append('STEM: the numeric/unit validator owns this class (Lane A2)')
    else:
        skipped['C.numeric'] = 'no numeric or unit expression in this block'

    # ---- cross-corpus: whenever the text has any word with a diacritic variant, which is most Vietnamese
    # text. Cheap enough to be the default and it is the signal that outranks internet lookup.
    if has_index and ctype not in ('table',):
        path.append('D.cross_corpus')
        if ctype == 'enumerated_heading':
            path.append('D.section_sequence')
    else:
        skipped['D.cross_corpus'] = ('no index installed' if not has_index
                                     else 'table cells are routed by structure, not by phrase context')

    # ---- LLM: only where a cheap signal cannot reach, and only ever as a DETECTOR.
    llm_warranted = (tc == 'teaching_critical' or dis in ('tone', 'text', 'numbers')
                     or (conf is not None and conf < 0.8) or ctype == 'stem_expression')
    if has_llm and llm_warranted and budget != 'cheap':
        path.append('G.llm_semantic')
        notes.append('LLM consulted as a DETECTOR only: measured clean-text false-correction rate 1.000 '
                     'on 13 proposals over 60 correct rows')
    else:
        skipped['G.llm_semantic'] = ('budget=cheap' if budget == 'cheap' else
                                     'no disagreement, adequate confidence, not teaching-critical')

    # ---- external: only for a stable public fact, never for a source-bound question.
    ext_kind = {'stem_expression': 'stem_constant', 'proper_noun_phrase': 'proper_noun_person',
                'heading': 'orthography_variant', 'prose': 'common_word_meaning',
                'enumerated_heading': 'reading_order', 'option': 'reading_order',
                'table': 'layout'}.get(ctype, 'other')
    ok, why = EX.appropriate(ext_kind)
    if has_external and ok and tc == 'teaching_critical' and budget == 'full':
        path.append('H.external')
    else:
        skipped['H.external'] = why if not ok else ('budget' if budget != 'full' else
                                                    'not teaching-critical')

    # ---- human: the escalation rule, stated once.
    human, hreason = False, ''
    if group and tc == 'teaching_critical' and dis != 'none':
        human, hreason = True, (f'teaching-critical member of structural group «{group}»: withholding one '
                                f'member serves a mutilated structure (97-row audit, defect 8)')
    elif tc == 'teaching_critical' and dis in ('tone', 'text', 'numbers'):
        human, hreason = True, f'teaching-critical block with a {dis} disagreement between the two stacks'
    elif ctype == 'proper_noun_phrase' and dis != 'none':
        human, hreason = True, ('a proper noun with a disagreement: frequency evidence is worth least '
                                'exactly here (Lane C measured a false correction on a person\'s name)')
    return Route(block_id, ctype, tc, dis, conf, tuple(path), skipped, human, hreason, group,
                 tuple(notes))


def escalate_after(route_, outcome_disposition, anomalies=(), candidates=()):
    """Second escalation decision, made *after* the signals have run. The first one is about what a block
    looks like; this one is about what the evidence turned out to be.

    A `CONFLICT` always reaches a human — that is the whole reason the disposition exists. A
    teaching-critical `SUSPECT` reaches a human because «detected, unexplained, and the child would be
    taught it» is the one combination nothing automatic should settle.
    """
    if outcome_disposition == 'CONFLICT':
        return True, 'signals contradict each other; no automatic rule may pick a winner'
    if outcome_disposition == 'SUSPECT' and route_.teaching_consequence == 'teaching_critical':
        return True, 'teaching-critical block with a detected but unexplained anomaly'
    if route_.human:
        return True, route_.human_reason
    return False, ''
