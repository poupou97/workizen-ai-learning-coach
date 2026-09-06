#!/usr/bin/env python3
"""Round 5 · Lane A4 — the CROSS-CORPUS index.

The Founder's order: *«cross-corpus verification is HIGHER PRIORITY than internet search»* — use our own
SGK/SGV corpus (same book, same lesson, SGK↔SGV, cross-grade terminology, repeated names / definitions /
constants / formulas) before ever reaching outside. This module is that corpus, made queryable.

Substrate: `poc-out/graph/ocr-body/<book>/pNNN.json` — **62,729 OCR pages across 531 books**, one JSON per
page with `lines[] = {text, conf, x, y, w, h}`. Read-only. Nothing here writes to the corpus, so this is
**not** a reprocess: it is an index built beside it.

Two passes, because the shapes have very different cost:

* **pass 1 — unigram (full scan, ~30 s, cached).** Every surface form with its corpus count and the number
  of distinct books it appears in. Keyed additionally by its *diacritic-stripped* form, so
  `norm_key('tổ') == norm_key('tô') == 'to'` gives the variant set `{tổ: 41k, tô: 9k, tồ: 3, …}` in O(1).
* **pass 2 — context (query-driven full scan, ~40 s per batch).** Bigram/trigram counts are only ever
  needed for the handful of *keys* a verification batch asks about, and a full bigram table over 14 M
  tokens does not fit in memory honestly. So the caller declares the keys it needs and one scan returns
  exact counts **plus real occurrences** (book · page · line · snippet) to use as evidence.

Why pass 2 is not optional: three of the five Founder POC cases are invisible to unigram frequency.
`hoa` (Cộng hoà → Cộng hoa), `bán` (bản sắc → bán sắc) and `tô` (Lý Thái Tổ → Lý Thái Tô) are all common,
perfectly valid Vietnamese words. Only the **context** — `cộng hoà` 4,000× vs `cộng hoa` 0× — separates
them. Frequency is a signal about a *phrase in its context*, never about a syllable alone.

**Frequency is not truth.** Everything here returns evidence (counts, books, occurrences); the decision to
call something an anomaly lives in `crosscorpus.py`, and the decision to repair lives in the engine.
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # tool/corpus

import tc_score  # noqa: E402  (the pipeline's own Vietnamese normalisation — reused, never re-derived)

INDEX_VERSION = 'xcorpus-v1'

#: Vietnamese word token. Same class as `tc2_sdm.TOKEN` so this index and the pipeline tokenise alike.
TOKEN = re.compile(r'[0-9A-Za-zÀ-ỹĂăÂâĐđÊêÔôƠơƯư]+')


def norm_token(tok):
    """Surface form as the index stores it: NFC, lower-case, tone placement modernised (`hoà`→`hòa`).

    Tone-placement normalisation matters: `hoà` and `hòa` are two *valid* orthographies of one word, and
    counting them apart would make the correct old-style spelling look like a rare anomaly."""
    return tc_score.norm_tone_placement(tc_score.nfc(tok).lower())


def key_of(tok):
    """The diacritic-stripped key two tone variants share. `tổ`/`tô`/`tồ` → `to`."""
    return tc_score.norm_key(tok)


def tokens_of(text):
    return [norm_token(t) for t in TOKEN.findall(tc_score.nfc(text or ''))]


def tokens_with_adjacency(text):
    """`[(form, adjacent_to_previous)]`.

    Two tokens are **adjacent** only when nothing but whitespace separates them. This matters more than it
    looks: measured on Lane C's Bài 8 blocks, treating a punctuation-separated pair as context produced
    false corrections directly — «đồi mồi,...), phải» was read as the bigram `mồi phải`, which the corpus
    of course never writes, so the correct «mồi» looked anomalous next to the very common «mới phải».
    A comma is a structural break, and evidence must not be read across one.
    """
    t = tc_score.nfc(text or '')
    out, prev_end = [], None
    for m in TOKEN.finditer(t):
        gap = t[prev_end:m.start()] if prev_end is not None else None
        out.append((norm_token(m.group()), gap is not None and (gap == '' or gap.isspace())))
        prev_end = m.end()
    return out


def page_tokens(page):
    """The whole page as `[(form, adjacent_to_previous)]`, joining consecutive lines.

    A block's text is built by joining OCR *lines*, so a bigram that straddles a line break is a bigram a
    block really contains — and if the index counted only within-line pairs, every such pair would look
    «unattested in 62,729 pages» and every one would be a false anomaly. The join is adjacency-aware: a
    line ending in a full stop is not adjacent to the next line's first word.
    """
    out = []
    tail_ok = False
    for line in page.get('lines') or ():
        toks = tokens_with_adjacency(line.get('text'))
        if not toks:
            continue
        raw = tc_score.nfc(line.get('text') or '')
        last = list(TOKEN.finditer(raw))[-1]
        first_gap_ok = not raw[:list(TOKEN.finditer(raw))[0].start()].strip()
        out.append((toks[0][0], tail_ok and first_gap_ok))
        out.extend(toks[1:])
        tail_ok = not raw[last.end():].strip()
    return out


def book_meta(book):
    """`06-sgk-khoa-hoc-tu-nhien-6` → (grade '06', kind 'sgk', subject 'khoa-hoc-tu-nhien').

    Used for *evidence independence*: a dominant form attested in 40 different books across 6 grades is
    much stronger evidence than the same form repeated 40× inside one book."""
    m = re.match(r'^(\d{2})-(sgk|sgv|sbt|[a-z]+)-(.+)$', book)
    if not m:
        return dict(grade=None, kind=None, subject=book)
    grade, kind, rest = m.groups()
    rest = re.sub(r'-tap-(mot|hai|ba)$', '', rest)
    rest = re.sub(r'-\d+$', '', rest)
    return dict(grade=grade, kind=kind, subject=rest)


# --------------------------------------------------------------------------- pass 1
class CrossCorpusIndex:
    """Unigram frequency over the whole OCR corpus, plus the diacritic-variant map and a **proper-noun
    prior**.

    `forms[form] = [count, n_books, eligible, capitalised]` and `by_key[key] = [form, …]`. Nothing else:
    an index that also held every occurrence would be 60 % of the corpus, and occurrences are what pass 2
    is for.

    The proper-noun prior exists because of Lane C's measured failure (`docs/research/lane-c/
    07-ROUND5-HISTORY.md` §4): a token-frequency repairer proposed the right river name **and** rewrote a
    person's name «Đăng Khoa» → «Đặng Khoa». A person's name may legitimately be rare and may legitimately
    differ by one tone from a common word, so *frequency evidence is worth less on a proper noun* and the
    bar must be higher. `eligible` counts appearances that are **not** line-initial in a **not-all-caps**
    line — the only positions where an initial capital carries information — and `capitalised` counts how
    many of those were capitalised. The ratio is a corpus-measured prior that also works inside ALL-CAPS
    headings, where the surface itself tells you nothing.
    """

    def __init__(self, forms=None, by_key=None, meta=None):
        self.forms = forms or {}
        self.by_key = by_key or {}
        self.meta = meta or {}

    # ---- build / persist
    @classmethod
    def build(cls, ocr_root, books=None, progress=None):
        forms = defaultdict(lambda: [0, 0, 0, 0])
        books_all = sorted(books or os.listdir(ocr_root))
        books_all = [b for b in books_all if os.path.isdir(os.path.join(ocr_root, b))]
        pages = 0
        for i, book in enumerate(books_all):
            seen_here = set()
            bdir = os.path.join(ocr_root, book)
            for name in sorted(os.listdir(bdir)):
                if not name.endswith('.json'):
                    continue
                pages += 1
                with open(os.path.join(bdir, name), encoding='utf-8') as fh:
                    page = json.load(fh)
                for line in page.get('lines') or ():
                    raw = tc_score.nfc(line.get('text') or '')
                    surface = TOKEN.findall(raw)
                    all_caps = bool(surface) and all(t.upper() == t for t in surface)
                    for j, tok in enumerate(surface):
                        form = norm_token(tok)
                        e = forms[form]
                        e[0] += 1
                        seen_here.add(form)
                        if j and not all_caps:            # line-initial capitals carry no information
                            e[2] += 1
                            if tok[:1].isupper():
                                e[3] += 1
            for tok in seen_here:
                forms[tok][1] += 1
            if progress and i % 50 == 0:
                progress(i, len(books_all), pages)
        by_key = defaultdict(list)
        for form in forms:
            by_key[key_of(form)].append(form)
        for k in by_key:
            by_key[k].sort(key=lambda f: -forms[f][0])
        return cls(dict(forms), {k: v for k, v in by_key.items()},
                   meta=dict(version=INDEX_VERSION, source=ocr_root, books=len(books_all), pages=pages,
                             distinct_forms=len(forms)))

    def save(self, path):
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as fh:
            json.dump(dict(meta=self.meta, forms=self.forms, by_key=self.by_key), fh, ensure_ascii=False)
        return path

    @classmethod
    def load(cls, path):
        with open(path, encoding='utf-8') as fh:
            d = json.load(fh)
        return cls(d['forms'], d['by_key'], d.get('meta'))

    # ---- query
    def count(self, form):
        e = self.forms.get(norm_token(form))
        return e[0] if e else 0

    def books(self, form):
        e = self.forms.get(norm_token(form))
        return e[1] if e else 0

    def variants(self, form_or_key, key=False):
        """Every surface form in the corpus sharing this diacritic-stripped key, commonest first.
        → [(form, count, n_books)]."""
        k = form_or_key if key else key_of(form_or_key)
        return [(f, self.forms[f][0], self.forms[f][1]) for f in self.by_key.get(k, ())]

    def proper_ratio(self, form):
        """0..1 — how often the corpus capitalises this word where a capital means something, or `None`
        when the corpus has too few informative positions to say. A **prior about the word**, never a
        verdict about this occurrence."""
        e = self.forms.get(norm_token(form))
        if not e or len(e) < 4 or e[2] < 5:
            return None
        return round(e[3] / e[2], 3)

    def key_proper_ratio(self, form):
        """The same prior pooled over every diacritic variant of the key — the form that matters when the
        *observed* variant is a rare OCR artefact with no statistics of its own."""
        elig = cap = 0
        for f in self.by_key.get(key_of(form), ()):
            e = self.forms[f]
            if len(e) >= 4:
                elig += e[2]
                cap += e[3]
        return round(cap / elig, 3) if elig >= 5 else None

    def dominant(self, form):
        v = self.variants(form)
        return v[0] if v else None


# --------------------------------------------------------------------------- pass 2
class ContextScan:
    """One read-only pass over the corpus answering a declared set of n-gram *key* questions.

    `keys` are tuples of diacritic-stripped keys — `('cong', 'hoa')`, `('cay', 'oi')`. For each requested
    key the scan returns every **surface** n-gram that matched, its count, the number of distinct books,
    and up to `max_occ` real occurrences with enough context to be shown to a human reviewer.

    Occurrences are what make this a *verification* signal rather than a frequency oracle: a candidate
    correction can be handed to a reviewer with «here are 12 places the corpus writes it the other way».
    """

    def __init__(self, keys, max_occ=6, ngram=2):
        self.ngram = ngram
        self.keys = {tuple(k) for k in keys}
        self.max_occ = max_occ
        self.counts = defaultdict(Counter)          # key -> Counter(surface tuple)
        self.books = defaultdict(lambda: defaultdict(set))
        self.occ = defaultdict(lambda: defaultdict(list))

    def run(self, ocr_root, books=None, exclude_books=()):
        exclude = set(exclude_books)
        blist = sorted(books or os.listdir(ocr_root))
        for book in blist:
            bdir = os.path.join(ocr_root, book)
            if book in exclude or not os.path.isdir(bdir):
                continue
            for name in sorted(os.listdir(bdir)):
                if not name.endswith('.json'):
                    continue
                with open(os.path.join(bdir, name), encoding='utf-8') as fh:
                    page = json.load(fh)
                stream = page_tokens(page)
                if len(stream) < self.ngram:
                    continue
                toks = [t for t, _ in stream]
                adj = [a for _, a in stream]
                ks = [key_of(t) for t in toks]
                lines = [ln.get('text') or '' for ln in (page.get('lines') or ())]
                for i in range(len(toks) - self.ngram + 1):
                    if not all(adj[i + j] for j in range(1, self.ngram)):
                        continue                    # punctuation or a paragraph break: not a context
                    kk = tuple(ks[i:i + self.ngram])
                    if kk not in self.keys:
                        continue
                    surf = tuple(toks[i:i + self.ngram])
                    self.counts[kk][surf] += 1
                    self.books[kk][surf].add(book)
                    lst = self.occ[kk][surf]
                    if len(lst) < self.max_occ:
                        phrase = ' '.join(surf)
                        hit = next((ln for ln in lines if phrase in norm_token(ln)), lines[0] if lines else '')
                        lst.append(dict(book=book, page=name[:-5], line=None,
                                        snippet=_snippet(hit, phrase)))
        return self

    def surfaces(self, key):
        """[(surface tuple, count, n_books)] commonest first, for one requested key."""
        c = self.counts.get(tuple(key), Counter())
        return [(s, n, len(self.books[tuple(key)][s])) for s, n in c.most_common()]

    def count(self, surface):
        surface = tuple(norm_token(t) for t in surface)
        return self.counts.get(tuple(key_of(t) for t in surface), Counter()).get(surface, 0)

    def occurrences(self, surface):
        surface = tuple(norm_token(t) for t in surface)
        return list(self.occ.get(tuple(key_of(t) for t in surface), {}).get(surface, ()))

    def to_json(self):
        return {'|'.join(k): dict(surfaces=[dict(surface=' '.join(s), count=n, books=b)
                                            for s, n, b in self.surfaces(k)],
                                  occurrences={' '.join(s): v for s, v in self.occ[k].items()})
                for k in sorted(self.counts)}


def _snippet(text, phrase, width=70):
    t = tc_score.nfc(text)
    low = norm_token(t)
    i = low.find(phrase)
    if i < 0:
        return t[:width * 2]
    a, b = max(0, i - width // 2), min(len(t), i + len(phrase) + width // 2)
    return ('…' if a else '') + t[a:b] + ('…' if b < len(t) else '')
