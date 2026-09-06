#!/usr/bin/env python3
"""Round 5 · Lane A4 — signal **`B.page_furniture`**: subtract what the *page* prints, not what the
*lesson* says.

Founder defect (KHTN 9, Bài 5, pdf p27, role `heading`):

    printed  II – Định luật khúc xạ ánh sáng
    served   I1 - Định luật khúc xạ ánh sáng Ô C. SỐNG

`Ô C. SỐNG` is not text. It is a fragment of the faint diagonal series watermark
«KẾT NỐI TRI THỨC / VỚI CUỘC SỐNG» that every page of that publisher's books carries, caught because the
heading's bounding box overlaps its right edge. No lexicon, no second OCR stack and no agreement gate can
see that, because **both stacks read the same faint strokes** — the round's own thesis.

But the corpus can see it, and cheaply: a watermark is *page furniture*, and page furniture is by
definition **the text that repeats across the pages of a book**. So this module learns, per book, which
short text fragments recur on many pages, and offers them as things to subtract. One rule learned from the
corpus removes a whole failure class rather than one row — which is the only kind of fix worth having at
62,729 pages.

Two deliberate restraints:

* **It proposes a deletion, never a rewrite.** The candidate is «this block minus this fragment»; the
  words that remain are the observed words, untouched. That keeps it outside the false-correction risk
  this lane exists to bound: subtracting furniture cannot invent a wrong word.
* **It refuses to subtract anything that is also ordinary lesson text.** A fragment is furniture only if
  it recurs on a large fraction of the book's pages *and* is short; «Bài» recurs on every page and is
  never furniture, so a minimum length and a maximum in-line share both apply.
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # tool/corpus

import tc_score  # noqa: E402
from repair import model, registry  # noqa: E402

from . import index as ix, paths  # noqa: E402
from .trust import AnomalySignal, EvidenceRef  # noqa: E402

SIGNAL_ID = 'B.page_furniture'
FC_FURNITURE = 'page_furniture_bleed'
RULE = 'furniture.repeat-subtract-v1'
FURNITURE_VERSION = 'furniture-v1'


class PageFurniture:
    """Learned per book: fragments that recur on many pages, and where they sit.

    `min_page_share` is the fraction of the book's pages a fragment must appear on. A running head appears
    on ~100 %; a series watermark appears on ~100 % *but is read differently each time*, so the learner
    also keys on the diacritic-stripped form, which is what makes «Ô C. SỐNG», «C SỐNG» and «Ô C S ỐNG»
    collapse to one thing.
    """

    def __init__(self, book, fragments=None, pages=0, meta=None):
        self.book = book
        self.fragments = fragments or {}       # key -> dict(count, pages, surfaces, x, y, edge)
        self.pages = pages
        self.meta = meta or {}

    # ---- learn
    @classmethod
    def learn(cls, book, ocr_root=None, min_pages=6, max_words=6, min_chars=3, sim=0.6,
              min_variants=4, max_variant_pages=2):
        """Two learners, because page furniture arrives in two shapes and only one of them repeats
        literally.

        **Exact.** A running head or a section scaffold (`a) Mục tiêu`, `b) Nội dung`) is printed in solid
        ink and read the same way every time, so identical strings on many pages find it.

        **Fuzzy.** A faint diagonal series watermark is read *differently on every page it survives at
        all*. Measured on KHTN 9, «KẾT NỐI TRI THỨC / VỚI CUỘC SỐNG» arrives as `I TRI THƯC`, `Ố1 TRI
        THỨC`, `RI THỨC`, `KẾT NƠI TRỊ THỨC`, `ỚI CUỘC SỐNG`, `C SỐNG`, `CUỘC SỘ` — **every variant
        appearing once or twice**. Exact repetition finds nothing, which is why the first version of this
        learner honestly returned zero fragments for the very book it was written for. So short lines are
        clustered by character similarity over their diacritic-stripped upper-case form, blocked by shared
        4-grams so the clustering is near-linear rather than quadratic, and a *cluster* that reaches
        `min_pages` is furniture even though no single string in it does.
        """
        import difflib
        ocr_root = ocr_root or paths.OCR_BODY
        bdir = os.path.join(ocr_root, book)
        names = sorted(n for n in os.listdir(bdir) if n.endswith('.json'))
        seen = defaultdict(lambda: dict(count=0, pages=set(), surfaces=Counter(), xs=[], ys=[]))
        for name in names:
            with open(os.path.join(bdir, name), encoding='utf-8') as fh:
                page = json.load(fh)
            for line in page.get('lines') or ():
                raw = tc_score.nfc(line.get('text') or '')
                words = ix.TOKEN.findall(raw)
                if not words or len(words) > max_words or len(raw.strip()) < min_chars:
                    continue
                key = tc_score.norm_key(raw)
                if not key or key.isdigit():
                    continue
                e = seen[key]
                e['count'] += 1
                e['pages'].add(name)
                e['surfaces'][raw.strip()] += 1
                e['xs'].append(line.get('x', 0) + line.get('w', 0) / 2)
                e['ys'].append(line.get('y', 0) + line.get('h', 0) / 2)

        keys = list(seen)
        flat = {k: re.sub(r'[^a-z0-9]', '', k) for k in keys}
        clusters, frags = {}, {}

        def record(root, members, kind):
            pages, count, surfaces, xs, ys = set(), 0, Counter(), [], []
            for k in members:
                e = seen[k]
                pages |= e['pages']
                count += e['count']
                surfaces.update(e['surfaces'])
                xs += e['xs']
                ys += e['ys']
            if len(pages) < min_pages:
                return
            rec = dict(count=count, pages=len(pages), page_share=round(len(pages) / len(names), 3),
                       surfaces=surfaces.most_common(8), variants=len(members), kind=kind,
                       x=round(sum(xs) / len(xs), 3), y=round(sum(ys) / len(ys), 3))
            clusters[root] = rec
            for k in members:
                frags[k] = rec

        # ---- shape (a): SOLID INK. The same string on many pages. No clustering needed, no chaining risk.
        for k in keys:
            record(k, [k], 'exact')

        # ---- shape (b): FAINT INK. Many *individually rare* variants that are near-duplicates of each
        # other. Restricting the clustering to rare keys is what stops it chaining: the first version
        # clustered everything transitively and produced one 2,260-variant «cluster» covering 230/230
        # pages that contained real lesson text («MỤC TIÊU», «Tiến hành:») — a learner that would have
        # deleted the lesson. Common scaffold text repeats *exactly* and is already caught above, so it
        # has no business in the fuzzy pass.
        rare = [k for k in keys if len(seen[k]['pages']) <= max_variant_pages and len(flat[k]) >= 5]
        buckets = defaultdict(list)
        for k in rare:
            s = flat[k]
            for g in {s[i:i + 4] for i in range(len(s) - 3)}:
                buckets[g].append(k)
        neighbours = defaultdict(set)
        for g, members in buckets.items():
            if len(members) > 400:           # a 4-gram this common says nothing about identity
                continue
            for i, a in enumerate(members):
                for b in members[i + 1:]:
                    if b in neighbours[a]:
                        continue
                    if difflib.SequenceMatcher(None, flat[a], flat[b]).ratio() >= sim:
                        neighbours[a].add(b)
                        neighbours[b].add(a)
        # greedy, NON-transitive: each cluster is one representative plus its own direct neighbours, so a
        # chain a~b~c with a≁c never collapses into one thing.
        taken = set()
        for k in sorted(neighbours, key=lambda k: (-len(neighbours[k]), k)):
            if k in taken:
                continue
            members = [k] + sorted(n for n in neighbours[k] if n not in taken)
            if len(members) < min_variants:
                continue
            taken.update(members)
            record(f'fuzzy:{k}', members, 'fuzzy-cluster')

        return cls(book, frags, len(names),
                   meta=dict(version=FURNITURE_VERSION, min_pages=min_pages, similarity=sim,
                             min_variants=min_variants, max_variant_pages=max_variant_pages,
                             clusters=len(clusters), keys=len(frags),
                             cluster_index={r: v for r, v in clusters.items()}))

    # ---- use
    def is_furniture(self, phrase):
        return tc_score.norm_key(phrase) in self.fragments

    def find_in(self, text, min_words=1, max_words=5):
        """Every furniture fragment present in `text`, as (start, end, phrase, record).

        Only *trailing or leading* fragments are reported: a watermark bleeds in at the edge of a bounding
        box, and a fragment that sits in the middle of a sentence is far more likely to be the lesson
        actually saying those words.
        """
        raw = tc_score.nfc(text or '')
        spans = [(m.start(), m.end(), m.group()) for m in ix.TOKEN.finditer(raw)]
        if not spans:
            return []
        out = []
        n = len(spans)
        for w in range(min(max_words, n), min_words - 1, -1):
            for start in (0, n - w):                       # leading or trailing only
                if start < 0 or start + w > n:
                    continue
                phrase = raw[spans[start][0]:spans[start + w - 1][1]]
                rec = self.fragments.get(tc_score.norm_key(phrase))
                if rec and not any(a <= start and start + w <= b for a, b, _, _ in out):
                    out.append((start, start + w, phrase, rec))
        return out

    def strip(self, text):
        """→ (text without its leading/trailing furniture, [(phrase, record)]). Words are only ever
        REMOVED; nothing is rewritten."""
        raw = tc_score.nfc(text or '')
        found = self.find_in(raw)
        if not found:
            return raw, []
        spans = [(m.start(), m.end()) for m in ix.TOKEN.finditer(raw)]
        keep_a, keep_b = 0, len(spans)
        removed = []
        for a, b, phrase, rec in sorted(found):
            if a == keep_a and b <= keep_b:
                keep_a = b
                removed.append((phrase, rec))
            elif b == keep_b and a >= keep_a:
                keep_b = a
                removed.append((phrase, rec))
        if keep_a >= keep_b:
            return raw, []                                  # the whole block is furniture: not our call
        cleaned = raw[spans[keep_a][0]:spans[keep_b - 1][1]]
        return cleaned.strip(' ,.;:-–—'), removed

    def to_json(self):
        return dict(book=self.book, pages=self.pages, meta=self.meta,
                    fragments={k: v for k, v in sorted(self.fragments.items(),
                                                       key=lambda kv: -kv[1]['pages'])})


# --------------------------------------------------------------------------- plugin (A1's registry)
_STATE = dict(by_book={})


def install(furniture):
    _STATE['by_book'][furniture.book] = furniture
    return furniture


def for_ctx(ctx):
    book = (ctx.page or {}).get('book')
    return _STATE['by_book'].get(book)


@registry.signal(SIGNAL_ID)
def furniture_signal(value, ctx):
    f = for_ctx(ctx)
    if f is None or not ctx.primary():
        return model.Signal(SIGNAL_ID, model.SignalVerdict.ABSTAINS, 0.0,
                            dict(reason='no furniture model for this book'))
    observed = ctx.primary().value
    if not isinstance(observed, str):
        return model.Signal(SIGNAL_ID, model.SignalVerdict.ABSTAINS, 0.0, dict(reason='not text'))
    cleaned, removed = f.strip(observed)
    if removed and cleaned == value:
        return model.Signal(SIGNAL_ID, model.SignalVerdict.SUPPORTS, 0.7,
                            dict(removed=[(p, r['pages'], r['page_share']) for p, r in removed]))
    if removed:
        return model.Signal(SIGNAL_ID, model.SignalVerdict.ABSTAINS, 0.0,
                            dict(reason='furniture found but the proposal is a different string',
                                 removed=[p for p, _ in removed]))
    return model.Signal(SIGNAL_ID, model.SignalVerdict.ABSTAINS, 0.0,
                        dict(reason='no page furniture in this block'))


@registry.repairer(FC_FURNITURE, repairer_id=RULE)
def propose_furniture(ctx):
    """DELETION-only repair: the block minus a fragment the book prints on `pages` of its pages.

    Evidence is the page list itself — «this exact fragment is on 231 of 236 pages of this book, always
    at x≈0.61 y≈0.55» is a stronger and far cheaper argument than anything a language model could make
    about it, and it is checkable by opening any two pages.
    """
    f = for_ctx(ctx)
    if f is None or not ctx.primary():
        return
    observed = ctx.primary().value
    if not isinstance(observed, str):
        return
    cleaned, removed = f.strip(observed)
    if not removed or cleaned == observed or not cleaned:
        return
    ev = [EvidenceRef(kind='corpus_occurrence', source=f'{f.book} ({r["pages"]}/{f.pages} pages)',
                      claim=f'«{p}» is printed on {r["page_share"] * 100:.0f}% of this book\'s pages '
                            f'at x≈{r["x"]} y≈{r["y"]}',
                      relation='supports', authority='corpus',
                      detail=dict(surfaces=r['surfaces'], pages=r['pages']))
          for p, r in removed]
    sig = model.Signal(SIGNAL_ID, model.SignalVerdict.SUPPORTS, 0.8,
                       dict(removed=[p for p, _ in removed],
                            evidence=[e.to_json() for e in ev],
                            note='deletion only; no word is rewritten'))
    yield model.RepairCandidate(
        block_id=ctx.block_id, failure_class=FC_FURNITURE, original_observations=ctx.observations,
        proposed_value=cleaned, rule_id=RULE, supporting_signals=(sig,), confidence=0.7,
        provenance=dict(covers_reasons=('agree_text', 'chem_guard'), signal=SIGNAL_ID,
                        furniture_version=FURNITURE_VERSION, deletion_only=True),
        detected=dict(kind='page furniture bled into a block',
                      removed=[dict(phrase=p, pages=r['pages'], page_share=r['page_share'],
                                    x=r['x'], y=r['y']) for p, r in removed]))


# --------------------------------------------------------------------------- known series branding
#: The three Vietnamese SGK series slogans, printed as a faint diagonal watermark on every page of every
#: book in the series. **A list of three strings, not a learner** — and that is a result, not a shortcut.
#:
#: Learning furniture from repetition was tried first and is reported as a measured negative
#: (`ACCURACY-RECOVERY-RESULT.md` §4): the exact learner finds solid-ink furniture (running heads,
#: «MỤC TIÊU», «EM ĐÃ HỌC») reliably, but a faint watermark is read differently on **every** page it
#: survives on, so no string repeats; and clustering the rare variants by character similarity pulls in
#: real lesson text — on KHTN 9 the cluster containing `C SỐNG` also contained «đời sống.» and «VÀ ĐỜI
#: SỐNG». A learner that would delete «đời sống» from a biology lesson is not a learner worth having.
#:
#: Three strings, on the other hand, are auditable by eye, need no threshold, and cover the whole corpus:
#: every SGK page in Vietnam carries one of them. The list is *validated against the corpus* rather than
#: asserted — `validate_registry()` counts the books each slogan is found in.
SERIES_SLOGANS = (
    'KẾT NỐI TRI THỨC VỚI CUỘC SỐNG',
    'CHÂN TRỜI SÁNG TẠO',
    'CÁNH DIỀU',
)
KNOWN_VERSION = 'known-furniture-v1'


def _flat(s):
    return re.sub(r'[^a-z0-9]', '', tc_score.norm_key(s))


_SLOGAN_FLAT = tuple((s, _flat(s)) for s in SERIES_SLOGANS)


def slogan_match(fragment, min_ratio=0.85, min_chars=5):
    """Is this fragment a piece of a series watermark? → (slogan, ratio) or None.

    Compared against every window of the slogan of a similar length, because the OCR catches an arbitrary
    *middle* of the diagonal string: «Ô C S ỐNG» is a piece of «…CUỘC SỐNG», «I TRI THƯC» a piece of
    «…TRI THỨC». Whole-string similarity would score both near zero.
    """
    import difflib
    f = _flat(fragment)
    if len(f) < min_chars:
        return None
    best = None
    for slogan, s in _SLOGAN_FLAT:
        for w in range(max(min_chars, len(f) - 3), min(len(s), len(f) + 4) + 1):
            for i in range(0, len(s) - w + 1):
                r = difflib.SequenceMatcher(None, f, s[i:i + w]).ratio()
                if r >= min_ratio and (best is None or r > best[1]):
                    best = (slogan, round(r, 3))
    if best is None:
        return None
    # ---- the conjunctive guard, and it is not optional.
    # Similarity alone strips real prose: «Em có thể vận dụng vào cuộc sống» matches «…VỚI CUỘC SỐNG» at
    # 0.91, and deleting «vào cuộc sống» from a lesson is exactly the false correction this lane exists to
    # prevent. What separates the two is *how the ink was read*: OCR crossing a faint diagonal watermark
    # shatters it into stray single glyphs («Ô C S ỐNG», «I TRI»), or — when the stroke survives whole —
    # reproduces the slogan almost exactly. Ordinary prose does neither.
    #
    # The tell that survives every test is **stray single letters**. A near-exact match is NOT enough on
    # its own: «cuộc sống» is an exact substring of «…VỚI CUỘC SỐNG» and is also two of the commonest
    # words in Vietnamese, so a similarity-only rule deletes it out of «Kể tên các nguồn năng lượng trong
    # cuộc sống». A digit is not a tell either («Bài 5» is a lesson number). So: at least one one-letter
    # word. That is fail-closed — a watermark line the OCR read cleanly and completely is left alone here,
    # because a *whole block* of series branding is a role/attachment question, not an edge bleed.
    toks = ix.TOKEN.findall(tc_score.nfc(fragment))
    if not any(len(t) == 1 and t.isalpha() for t in toks):
        return None
    return best


def strip_known(text, max_words=5, min_ratio=0.85):
    """→ (text minus its leading/trailing watermark fragment, [(phrase, slogan, ratio)]).

    Leading/trailing only, and **deletion only**: a watermark bleeds in at the edge of a bounding box, and
    removing it can never invent a wrong word — which is what keeps this signal outside the
    false-correction risk the rest of this lane spends its budget bounding.
    """
    raw = tc_score.nfc(text or '')
    spans = [(m.start(), m.end()) for m in ix.TOKEN.finditer(raw)]
    if len(spans) < 2:
        return raw, []
    a, b, removed = 0, len(spans), []
    changed = True
    while changed and b - a > 1:
        changed = False
        for w in range(min(max_words, b - a - 1), 0, -1):
            for lead in (True, False):
                s, e = (a, a + w) if lead else (b - w, b)
                phrase = raw[spans[s][0]:spans[e - 1][1]]
                hit = slogan_match(phrase, min_ratio)
                if hit:
                    removed.append((phrase, hit[0], hit[1]))
                    a, b = (e, b) if lead else (a, s)
                    changed = True
                    break
            if changed:
                break
    if not removed:
        return raw, []
    return raw[spans[a][0]:spans[b - 1][1]].strip(' ,.;:-–—'), removed


def validate_registry(books, ocr_root=None, per_book=60):
    """Corpus evidence for the registry: how many of these books print a fuzzy match of each slogan, and
    what the OCR actually made of it. Evidence that the three strings are real, measured rather than
    asserted."""
    ocr_root = ocr_root or paths.OCR_BODY
    found = {s: dict(books=set(), samples=Counter()) for s in SERIES_SLOGANS}
    for book in books:
        bdir = os.path.join(ocr_root, book)
        names = sorted(n for n in os.listdir(bdir) if n.endswith('.json'))[:per_book]
        for name in names:
            with open(os.path.join(bdir, name), encoding='utf-8') as fh:
                page = json.load(fh)
            for line in page.get('lines') or ():
                raw = tc_score.nfc(line.get('text') or '').strip()
                if not raw or len(ix.TOKEN.findall(raw)) > 5:
                    continue
                hit = slogan_match(raw)
                if hit:
                    found[hit[0]]['books'].add(book)
                    found[hit[0]]['samples'][raw] += 1
    return {s: dict(books=len(v['books']), of=len(books), samples=v['samples'].most_common(8))
            for s, v in found.items()}


@registry.repairer(FC_FURNITURE, repairer_id='furniture.known-series-v1')
def propose_known(ctx):
    """DELETION-only repair against the publisher registry. Independent of any learned model, so it works
    on a book the pipeline has never seen — which is the whole point of a registry over a learner."""
    if not ctx.primary():
        return
    observed = ctx.primary().value
    if not isinstance(observed, str):
        return
    cleaned, removed = strip_known(observed)
    if not removed or not cleaned or cleaned == observed:
        return
    ev = [EvidenceRef(kind='deterministic', source=f'series-watermark/{KNOWN_VERSION}',
                      claim=f'«{p}» matches the series watermark «{slogan}» at ratio {r}',
                      relation='supports', authority='official',
                      detail=dict(slogan=slogan, ratio=r))
          for p, slogan, r in removed]
    sig = model.Signal(SIGNAL_ID, model.SignalVerdict.SUPPORTS, 0.75,
                       dict(removed=[p for p, _, _ in removed],
                            evidence=[e.to_json() for e in ev], note='deletion only'))
    yield model.RepairCandidate(
        block_id=ctx.block_id, failure_class=FC_FURNITURE, original_observations=ctx.observations,
        proposed_value=cleaned, rule_id='furniture.known-series-v1', supporting_signals=(sig,),
        confidence=0.7,
        provenance=dict(covers_reasons=('agree_text', 'chem_guard'), signal=SIGNAL_ID,
                        deletion_only=True, version=KNOWN_VERSION),
        detected=dict(kind='series watermark bled into a block',
                      removed=[dict(phrase=p, slogan=s, ratio=r) for p, s, r in removed]))


def anomalies_of(block_id, text, furniture, where=None):
    out = []
    cleaned, removed = furniture.strip(text)
    for p, r in removed:
        out.append(AnomalySignal(
            block_id=block_id, detector_id=f'{SIGNAL_ID}/{FURNITURE_VERSION}',
            reason=f'«{p}» is page furniture: it is printed on {r["pages"]} of {furniture.pages} pages',
            span=p, observed=text, confidence=0.7, severity='display',
            context_supplied=dict(book=furniture.book, where=dict(where or {}))))
    return out
