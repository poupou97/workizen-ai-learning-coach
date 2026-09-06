#!/usr/bin/env python3
"""Third signal **layer A** - Vietnamese lexical / orthographic evidence.

Three sub-signals, all under layer A because they are *not independent of each other* (they are all
Vietnamese-orthography knowledge) and the framework's «confirmed by an independent signal» rule counts
layers, not signal ids:

* `A.vi_syllable` - **deterministic phonotactics**, no data at all: a Vietnamese syllable carries at most one
  tone mark and its onset is one of the 28 initial spellings. This is the only sub-signal whose evidence
  cannot itself be an OCR artefact, and it is the one that catches the «thủỷ» class - which matters, because
  the corpus table below is *fooled* by that class (Apple Vision produces «thủỷ» so consistently that it is
  attested on 743 pages of 160 books, more than the correct «thủy»). Measured, and reported.
* `A.vi_lexicon` - is this form a word at all, in the sense of being attested on enough distinct pages of
  enough distinct books, with the book under repair subtracted.
* `A.vi_collocation` - the discriminating one: does this form occur *next to these neighbours* elsewhere in
  the corpus. «tiến hành» 4,010 pages vs «tiền hành» 177; «có thể» 24,255 vs «cô thể» 14.

Every sub-signal may return `objects`, and an objection is fatal in the engine's policy. None of them
decides anything on its own.
"""
from __future__ import annotations

from .. import model, registry
from ..vi import syllable

MIN_UNI_PAGES = 8       # a candidate form must be attested on this many pages OUTSIDE its own book …
MIN_UNI_BOOKS = 4       # … in this many distinct books, before layer A will even consider proposing it
CTX_MIN = 3             # a bigram side counts as "attested" from this many pages
CTX_RATIO = 4.0         # margin one side must show before it is decisive


@registry.signal('A.vi_syllable')
def syllable_signal(token, ctx=None):
    """Deterministic legality of ONE token. `objects` when the token cannot be Vietnamese."""
    ok, reasons = syllable.legality(token)
    if ok:
        return model.Signal('A.vi_syllable', model.SignalVerdict.SUPPORTS, 0.3,
                            dict(token=token, legal=True))
    return model.Signal('A.vi_syllable', model.SignalVerdict.OBJECTS, 1.0,
                        dict(token=token, legal=False, reasons=reasons))


@registry.signal('A.vi_lexicon')
def lexicon_signal(token, lex, book=None):
    """Is this form attested outside its own book? `abstains` when the lexicon is absent."""
    if lex is None:
        return model.Signal('A.vi_lexicon', model.SignalVerdict.ABSTAINS, 0.0, dict(token=token))
    s = lex.unigram(token, exclude_book=book)
    clean = lex.clean_unigram(token)
    ok = s.pages >= MIN_UNI_PAGES and s.books >= MIN_UNI_BOOKS
    return model.Signal('A.vi_lexicon',
                        model.SignalVerdict.SUPPORTS if ok else model.SignalVerdict.OBJECTS,
                        min(1.0, s.books / 100.0),
                        dict(token=token, pages=s.pages, books=s.books, in_book=s.in_book,
                             clean_files=clean.books, min_pages=MIN_UNI_PAGES, min_books=MIN_UNI_BOOKS))


@registry.signal('A.vi_sweep')
def sweep_signal(text, lex, book, exempt_ascii=True):
    """A whole-block sweep: is every Vietnamese word in this text a legal syllable that the corpus has
    actually seen? It **objects** when it is not.

    This is what stops a *correct* repair from restoring a block that is wrong somewhere the repairer never
    looked - measured on the dev split, three of thirteen restores were exactly that. Exemptions, stated:
    an ASCII-only token (a foreign word - «Provider», «ISP») and a capitalised token that is not sentence
    initial (a proper name - «Klong») are not judged, because the corpus is a poor lexicon for both."""
    import re as _re
    if lex is None:
        return model.Signal('A.vi_sweep', model.SignalVerdict.ABSTAINS, 0.0, dict())
    tok = _re.compile(r'[0-9A-Za-zÀ-ỹĂăÂâĐđÊêÔôƠơƯư]+')
    letter = _re.compile(r'[A-Za-zÀ-ỹĂăÂâĐđÊêÔôƠơƯư]')
    ascii_only = _re.compile(r'^[A-Za-z]+$')
    bad = []
    words = [(m.group(0), m.start()) for m in tok.finditer(text or '')]
    for i, (t, at) in enumerate(words):
        if len(t) < 2 or not letter.search(t):
            continue
        if exempt_ascii and ascii_only.match(t):
            continue
        if i > 0 and t[:1].isupper() and not t.isupper():
            continue                       # a capitalised word mid-text: proper name, not judged
        if not syllable.legality(t)[0]:
            bad.append(dict(token=t, why='illegal'))
            continue
        su = lex.unigram(t, exclude_book=book)
        if su.pages < MIN_UNI_PAGES or su.books < MIN_UNI_BOOKS:
            bad.append(dict(token=t, why='unattested', pages=su.pages, books=su.books))
    if bad:
        return model.Signal('A.vi_sweep', model.SignalVerdict.OBJECTS, 1.0,
                            dict(unvouched=bad[:6], n=len(bad)))
    return model.Signal('A.vi_sweep', model.SignalVerdict.SUPPORTS, 0.5,
                        dict(words=len(words), note='every Vietnamese word in the block is a legal, '
                                                    'corpus-attested form'))


def _sides(candidates, left, right, lex, book):
    """{candidate: {'left': pages, 'right': pages}} - bigram page support with the book subtracted."""
    out = {}
    for c in candidates:
        d = {}
        if left:
            d['left'] = lex.bigram(left, c, exclude_book=book).pages
        if right:
            d['right'] = lex.bigram(c, right, exclude_book=book).pages
        out[c] = d
    return out


def decide(candidates, left, right, lex, book, ratio=CTX_RATIO, minimum=CTX_MIN):
    """The collocation arbitration, used by layer A and (with different numbers) by layer D.

    A side is **decisive** for `c` when its support is at least `minimum` and at least `ratio` times the best
    of the others; a side **objects** to `c` when another candidate's support on that side is decisive
    against it. The winner is the unique candidate with at least one decisive side and no objecting side -
    otherwise there is no winner, and the caller abstains. Returns `(winner, table, per_candidate_verdict)`.
    """
    table = _sides(candidates, left, right, lex, book)
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
        verdict[c] = dict(decisive=decisive, objecting=objecting, **table[c])
    winners = [c for c in candidates if verdict[c]['decisive'] and not verdict[c]['objecting']]
    return (winners[0] if len(winners) == 1 else None), table, verdict


@registry.signal('A.vi_collocation')
def collocation_signal(token, verdict_row, winner):
    """`supports` the winner of `decide`, `objects` to a candidate a side ruled against."""
    if verdict_row is None:
        return model.Signal('A.vi_collocation', model.SignalVerdict.ABSTAINS, 0.0, dict(token=token))
    if verdict_row['objecting']:
        return model.Signal('A.vi_collocation', model.SignalVerdict.OBJECTS, 1.0,
                            dict(token=token, **{k: v for k, v in verdict_row.items() if k != 'objecting'}))
    if token == winner and verdict_row['decisive']:
        strength = min(1.0, max(verdict_row.get('left', 0), verdict_row.get('right', 0)) / 100.0)
        return model.Signal('A.vi_collocation', model.SignalVerdict.SUPPORTS, strength,
                            dict(token=token, **verdict_row))
    return model.Signal('A.vi_collocation', model.SignalVerdict.ABSTAINS, 0.0,
                        dict(token=token, **verdict_row))
