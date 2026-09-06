#!/usr/bin/env python3
"""Round 5 · the adapter from the TC-v2 pipeline to the repair framework.

`tc2_sdm` is the pipeline; `repair/` is the framework. This module is the only place that knows both, so a
plugin never imports the pipeline and the pipeline never imports a plugin. It turns one SDM page into
`RepairContext`s carrying:

* the **original observations** - the primary (Docling+Apple Vision) reading and the verifier (XY-cut on the
  same Apple Vision lines) reading of the same block, each with its own provenance;
* the pipeline's current disposition and its withhold reasons;
* a `DocumentContext` - the rest of this book, for layer D (cross-page / in-document consistency);
* the lexicon - for layer A.

**A finding this adapter makes visible.** The two "independent" stacks are not independent in text: the
XY-cut verifier reads `poc-out/graph/ocr-body`, whose `extraction_method` is `apple-vision-accurate-vi`,
and the Docling primary runs `ocrmac` - Apple Vision again - at `recognition='accurate'`, `lang=['vi-VT']`.
They differ in render scale and in layout grouping, not in the recogniser. Round 4's falsified A26
(«two stacks agreeing means verbatim») is therefore not a surprising empirical result but a structural one:
the agreement gate was always a *layout* agreement gate wearing a text agreement's clothes.
"""
from __future__ import annotations

import glob
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))          # tool/corpus

import tc2_sdm            # noqa: E402
import tc2_paths          # noqa: E402
import tc_score           # noqa: E402
import tc_sdm             # noqa: E402

from . import model                                # noqa: E402
from .engine import RepairContext                  # noqa: E402
from .vi import lexicon as vi_lexicon              # noqa: E402
from .vi import lexicon_build                      # noqa: E402

ROOT = tc2_paths.ROOT
PRIMARY = 'docling-ocrmac'
VERIFIER = 'current-xycut'

#: what each stack's text actually comes from - recorded on every observation so a reader of the ledger can
#: see for themselves that the two sources share a recogniser.
SOURCE_STACKS = {
    PRIMARY: dict(layout='docling-2.126', ocr='apple-vision (ocrmac)', recognition='accurate',
                  lang='vi-VT,en-US', images_scale=2.0),
    VERIFIER: dict(layout='wal-206 xy-cut', ocr='apple-vision (poc-out/graph/ocr-body)',
                   recognition='accurate', lang='vi', extraction_method='apple-vision-accurate-vi'),
}


class DocumentContext:
    """The rest of the book around a block: layer D's evidence. Page-level counts of word forms and
    bigrams, with the page under repair excluded, plus the book's TOC titles."""

    def __init__(self, book, page, page_tokens, page_bigrams, toc_titles=None, lesson_pages=None):
        self.book = book
        self.page = page
        self._page_tokens = page_tokens        # page_no -> set(token)
        self._page_bigrams = page_bigrams      # page_no -> set((a, b))
        self.toc_titles = toc_titles or {}
        self.lesson_pages = set(lesson_pages or ())

    def token_pages(self, token, within_lesson=False):
        t = (token or '').lower()
        pages = self.lesson_pages if within_lesson and self.lesson_pages else self._page_tokens.keys()
        return sum(1 for p in pages if p != self.page and t in self._page_tokens.get(p, ()))

    def bigram_pages(self, a, b, within_lesson=False):
        key = ((a or '').lower(), (b or '').lower())
        pages = self.lesson_pages if within_lesson and self.lesson_pages else self._page_bigrams.keys()
        return sum(1 for p in pages if p != self.page and key in self._page_bigrams.get(p, ()))

    @classmethod
    def for_book(cls, book, page, cache={}):
        if book not in cache:
            pt, pb = {}, {}
            for _, pno, text in lexicon_build.iter_pages(books=[book]):
                toks = lexicon_build.tokens(text)
                pt[pno] = set(toks)
                pb[pno] = set(zip(toks, toks[1:]))
            cache[book] = (pt, pb)
        pt, pb = cache[book]
        return cls(book, page, pt, pb)


def observations_for_page(book, page, pipeline, sdm):
    """(block_id -> [Observation, ...]) for one SDM page: the primary's own text, and the verifier stream
    slice the agreement gate aligned it to. Both are ORIGINAL OBSERVATIONS and neither is ever rewritten."""
    rawD, srcD = tc2_sdm.load_raw(PRIMARY, book, page, pipeline)
    rawX, srcX = tc2_sdm.load_raw(VERIFIER, book, page, pipeline)
    if rawD is None or rawX is None:
        return {}
    blocks, _pics, _tables = tc2_sdm.adapt_docling_v2(rawD['result'])
    X, xmeta = tc_sdm.adapt_current_xycut(rawX['result'])
    agree = tc2_sdm.agreement(blocks, dict(book=book, page=page, candidate=VERIFIER, blocks=X, meta=xmeta))
    out = {}
    for b, a in zip(blocks, agree):
        bid = f'{book}:p{page:03d}:{pipeline}:{b["order"]:03d}'
        prov = dict(book=book, page=page, bbox=b['bbox'], pipeline=pipeline, raw=srcD, stack=SOURCE_STACKS[PRIMARY])
        obs = [model.Observation(bid, PRIMARY, b['text'], prov)]
        vraw = a.get('vraw')
        if vraw:
            obs.append(model.Observation(bid, VERIFIER, ' '.join(vraw),
                                         dict(book=book, page=page, pipeline=pipeline, raw=srcX,
                                              verifier_id=a.get('verifier_id'), text_sim=a.get('text_sim'),
                                              stack=SOURCE_STACKS[VERIFIER])))
        out[bid] = obs
    return out


def page_agreed_forms(sdm):
    """{skeleton: {tone-placement-normalised form: [surface forms]}} over the TRUSTED blocks of the page -
    i.e. the words this page prints in places where the two stacks agreed. Layer D's page-scope evidence."""
    import re
    import tc_score
    tok = re.compile(r'[0-9A-Za-zÀ-ỹĂăÂâĐđÊêÔôƠơƯư]+')
    letter = re.compile(r'[A-Za-zÀ-ỹĂăÂâĐđÊêÔôƠơƯư]')
    out = {}
    for ob in sdm['blocks']:
        if ob['trust']['status'] != 'TRUSTED' or not (ob.get('text') or '').strip():
            continue
        for t in tok.findall(ob['text']):
            if len(t) < 2 or not letter.search(t):
                continue
            skel = re.sub(r'[^a-z0-9]', '', tc_score.strip_all(t).lower())
            out.setdefault(skel, {}).setdefault(tc_score.norm_tone_placement(t).lower(), []).append(t)
    return out


def verifier_page_tokens(book, page, pipeline):
    """The verifier's whole page as a flat, tone-placement-normalised token stream - the evidence
    `column-linearisation-v1` reads."""
    import re
    import tc_score
    rawX, _ = tc2_sdm.load_raw(VERIFIER, book, page, pipeline)
    if rawX is None:
        return []
    X, _m = tc_sdm.adapt_current_xycut(rawX['result'])
    tok = re.compile(r'[0-9A-Za-zÀ-ỹĂăÂâĐđÊêÔôƠơƯư]+')
    return [tc_score.norm_tone_placement(t).lower() for b in X for t in tok.findall(b.get('text') or '')]


def contexts_for_page(sdm, lexicon=None, document=None, pipeline=None, learning_only=True):
    """One RepairContext per text block of an SDM page."""
    book, page = sdm['book'], sdm['page']
    pipeline = pipeline or sdm.get('pipeline') or tc2_sdm.PIPELINE_ID
    obs_by_id = observations_for_page(book, page, pipeline, sdm)
    document = document if document is not None else DocumentContext.for_book(book, page)
    page_forms = page_agreed_forms(sdm)
    vstream = verifier_page_tokens(book, page, pipeline)
    out = []
    for ob in sdm['blocks']:
        if learning_only and not ob.get('learning'):
            continue
        if not (ob.get('text') or '').strip():
            continue
        obs = obs_by_id.get(ob['id'])
        if not obs:
            obs = [model.Observation(ob['id'], PRIMARY, ob['text'],
                                     dict(book=book, page=page, bbox=ob['bbox'], pipeline=pipeline))]
        out.append(RepairContext(
            block_id=ob['id'],
            observations=tuple(obs),
            disposition=(model.Disposition.TRUSTED if ob['trust']['status'] == 'TRUSTED'
                         else model.Disposition.WITHHELD),
            withhold_reasons=tuple(ob['trust']['reasons']),
            role=ob['role']['value'],
            page=dict(book=book, page=page, printed_page=sdm.get('printed_page'), features=sdm.get('features') or {},
                      bbox=ob['bbox'], ocr_conf=ob.get('ocr_conf'), colour=ob.get('colour'),
                      heading_path=ob.get('heading_path') or [], order=ob.get('order')),
            document=document,
            lexicon=lexicon,
            extra=dict(sdm_block=ob, page_forms=page_forms, verifier_page_tokens=vstream),
        ))
    return out


def load_sdm(pipeline, book, page, out_root=None):
    if out_root:
        tc2_paths.set_out_root(out_root)
    p = tc2_sdm.sdm_path(pipeline, book, page, gold=True)
    if not os.path.exists(p):
        p = tc2_sdm.sdm_path(pipeline, book, page, gold=False)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None
