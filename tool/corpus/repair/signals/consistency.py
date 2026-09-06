#!/usr/bin/env python3
"""Third signal **layer D** - cross-page / in-document / heading-TOC consistency.

A textbook says the same word many times. When one page prints «phẫu lọc» and four other blocks of the same
lesson print «phễu lọc», the document itself has already answered the question - and it answered it with
*different ink on a different page*, which is exactly the independence layer A cannot give (layer A
deliberately subtracts the book under repair; layer D is the book under repair). The two together are the
«independent signal» the Founder's validation rule asks for.

* `D.in_document` - page support for a form, and for the form in its neighbourhood, elsewhere in this book,
  excluding the page under repair.
* `D.toc_title` - a lesson-title block must agree with the TOC entry for that lesson. The TOC is a different
  page, usually a different type size, and is therefore an independent reading of the same words.
"""
from __future__ import annotations

import unicodedata

from .. import model, registry

DOC_MIN = 1             # in-document evidence is rare and specific: one other page already counts
DOC_RATIO = 3.0


def _nfc(s):
    return unicodedata.normalize('NFC', s or '')


def doc_sides(candidates, left, right, document, within_lesson=False):
    out = {}
    for c in candidates:
        d = {}
        if left:
            d['left'] = document.bigram_pages(left, c, within_lesson=within_lesson)
        if right:
            d['right'] = document.bigram_pages(c, right, within_lesson=within_lesson)
        d['pages'] = document.token_pages(c, within_lesson=within_lesson)
        out[c] = d
    return out


def decide(candidates, left, right, document, ratio=DOC_RATIO, minimum=DOC_MIN):
    """Same shape as layer A's `decide`, over this book instead of the corpus.

    **Only the bigram sides decide.** The first version of this let the unigram side (`pages` - how often the
    form occurs anywhere in the book) be decisive, and on the dev split that turned layer D into a popularity
    prior: «tim»→«tìm» «won» with zero bigram support on either side because «tìm» appears on 93 pages of
    that Tiếng Việt volume. A common word is not evidence about *this* word. `pages` is kept, reported, and
    used only as a *precondition* (a proposal whose form never occurs elsewhere in the book gets no support
    from this layer) and as objection evidence."""
    table = doc_sides(candidates, left, right, document)
    verdict = {}
    for c in candidates:
        decisive = objecting = False
        for side in ('left', 'right'):
            mine = table[c].get(side)
            if mine is None:
                continue
            others = [table[o].get(side, 0) for o in candidates if o != c]
            best_other = max(others) if others else 0
            if mine >= minimum and mine >= ratio * max(best_other, 1e-9):
                decisive = True
            if best_other >= minimum and best_other >= ratio * max(mine, 1e-9):
                objecting = True
        if table[c].get('pages', 0) <= 0:
            decisive = False
        verdict[c] = dict(decisive=decisive, objecting=objecting, **table[c])
    winners = [c for c in candidates if verdict[c]['decisive'] and not verdict[c]['objecting']]
    return (winners[0] if len(winners) == 1 else None), table, verdict


@registry.signal('D.in_document')
def in_document_signal(token, verdict_row, winner):
    if verdict_row is None:
        return model.Signal('D.in_document', model.SignalVerdict.ABSTAINS, 0.0, dict(token=token))
    if verdict_row['objecting']:
        return model.Signal('D.in_document', model.SignalVerdict.OBJECTS, 0.8,
                            dict(token=token, **{k: v for k, v in verdict_row.items() if k != 'objecting'}))
    if token == winner and verdict_row['decisive']:
        return model.Signal('D.in_document', model.SignalVerdict.SUPPORTS,
                            min(1.0, verdict_row.get('pages', 0) / 10.0 + 0.4),
                            dict(token=token, **verdict_row))
    return model.Signal('D.in_document', model.SignalVerdict.ABSTAINS, 0.0, dict(token=token, **verdict_row))


@registry.signal('D.in_block')
def in_block_signal(token, observed, count, competing):
    """The tightest consistency scope there is: the **same block** already prints this word, in a place
    where both stacks agree, and it prints it differently from the reading under repair.

    This is the «vặn khoa lại» case - the block writes «khóa» twice, correctly, and then «khoa» once. It
    requires at least two agreed occurrences of the proposal and exactly one form competing with it, so a
    genuine homograph pair inside one block («bàn»/«bán») cannot drive it."""
    if count < 2 or competing != 1:
        return model.Signal('D.in_block', model.SignalVerdict.ABSTAINS, 0.0,
                            dict(token=token, agreed_occurrences=count, competing_forms=competing))
    return model.Signal('D.in_block', model.SignalVerdict.SUPPORTS, 1.0,
                        dict(token=token, observed=observed, agreed_occurrences=count,
                             note='the same block prints this word this way, and both stacks agree there'))


@registry.signal('D.in_page')
def in_page_signal(token, observed, count, observed_count, competing):
    """The same PAGE already prints this word - in a block the pipeline trusts, i.e. one where both stacks
    agreed - and never prints the reading under repair.

    This is the «phẫu lọc» case: two blocks lower down the same page print «phễu» and are trusted, while the
    instruction block prints «phẫu» once. Different ink, different block, same page; it is evidence the
    corpus table cannot give (the word is domain-specific and rare) and the block itself cannot give
    (the correct spelling is not inside it)."""
    if count < 1 or observed_count > 0 or competing > 1:
        return model.Signal('D.in_page', model.SignalVerdict.ABSTAINS, 0.0,
                            dict(token=token, trusted_occurrences=count,
                                 observed_trusted_occurrences=observed_count, competing_forms=competing))
    return model.Signal('D.in_page', model.SignalVerdict.SUPPORTS, min(1.0, 0.5 + 0.25 * count),
                        dict(token=token, observed=observed, trusted_occurrences=count,
                             note='this page prints the word this way in a block both stacks agreed on, '
                                  'and never prints the observed reading'))


@registry.signal('D.toc_title')
def toc_title_signal(observed_text, proposed_text, toc_title):
    """A lesson title read from the page banner, against the same title read from the TOC page."""
    if not toc_title:
        return model.Signal('D.toc_title', model.SignalVerdict.ABSTAINS, 0.0, dict())
    t = _nfc(toc_title).strip().lower()
    if _nfc(proposed_text).strip().lower() == t and _nfc(observed_text).strip().lower() != t:
        return model.Signal('D.toc_title', model.SignalVerdict.SUPPORTS, 1.0, dict(toc_title=toc_title))
    if _nfc(observed_text).strip().lower() == t and _nfc(proposed_text).strip().lower() != t:
        return model.Signal('D.toc_title', model.SignalVerdict.OBJECTS, 1.0, dict(toc_title=toc_title))
    return model.Signal('D.toc_title', model.SignalVerdict.ABSTAINS, 0.0, dict(toc_title=toc_title))
