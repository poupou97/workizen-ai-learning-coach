#!/usr/bin/env python3
"""WAL-210 — LESSON ATTACHMENT with a capped, header-repaired TOC range (audit gate G2)
and a LESSON-IDENTITY gate (audit gate G3). Rule id: ``capped-toc-v1``.

Why: `build_lesson_index.lesson_for` attached an activity to "the last lesson whose
pageStart ≤ page" with NO upper bound. When a TOC is truncated (KHTN 8 stops at Bài 22
of 47) every later page fell into the last lesson — the audit measured KHTN 8 "Bài 22"
holding experiments from Bài 24 and Bài 28. When a canonical lesson has no pageStart
(Khoa học 4 Bài 2/3, Khoa học 5 Bài 4 …) its pages were silently swallowed by the
previous lesson (Khoa học 4 "Bài 1" p11 is Bài 2; Khoa học 5 "Bài 3" p20 is Bài 4).
And two TV5 activities were keyed to lesson numbers that do not exist in the canonical
lesson list at all.

capped-toc-v1 (printed-page space, deterministic, fail closed):
  1. STARTS — a canonical lesson's start is its TOC pageStart. When the TC-v2
     header-based attachment for the book is on disk
     (poc-out/trusted-corpus/tc-v2/tc2-p1/attach/<book>.json — a deterministic
     OCR-line header detector, measured 43/54 gold pages vs TOC 37/54), a canonical
     lesson WITHOUT a TOC start takes its header-detected start (confidence ≥ 0.8)
     — "TOC repair". A lesson whose TOC start and header start disagree by > 1 page
     is CONFLICTED: its pages are withheld (`start_conflict`). Header-detected
     starts of NON-canonical lesson numbers (KHTN 8 Bài 23–47) never create a
     lesson, but they do END the previous lesson's range (terminators).
  2. CAP — the same rule as tool/ui/pattern_router.toc_ranges: a range ends at the
     next start, but never later than start + cap, cap = max(8, round(2.5 × median
     gap between consecutive starts)). Pages past the end belong to NO lesson
     (`beyond_cap` / `beyond_header_end`).
  3. UNRANGED-SUCCESSOR GUARD — if a canonical lesson that still has no start sits
     between lesson L and the next started lesson, every page of L after L's own
     start page is ambiguous (it may belong to the unranged lesson) and is withheld
     (`successor_unranged`). A page-level "continuation of L" from the header data
     does not lift this: the detector that missed the successor's header cannot
     vouch for it.
  4. HEADER CROSS-CHECK — a page-level header record disagreeing with the range
     lesson T withholds the page (`header_disagrees`) when that record is POSITIVE
     evidence: its lesson H is non-canonical, or H's header-detected start lies at
     or after T's start. When H's start lies BEFORE T's start, the chain is merely a
     stale continuation across a header the detector missed — the TOC wins
     (`attached_header_stale`, counted). A record saying the page has no lesson
     (front/back matter, theme opener) withholds it (`header_no_lesson`).
  5. IDENTITY — an activity may only carry a lesson number that exists in the
     book's canonical lesson list (curriculum-structure.json); anything else is
     dropped (`not_canonical`). For families whose lesson key comes from an
     upstream extractor (TV5 units, Toán exercise map, source-asset registry) this
     is the only drop; the TOC range is a cross-check that is COUNTED
     (`range_mismatch`, `unranged_lesson`) but not a drop — the in-body header the
     extractor read is the stronger signal, and TV5's TOC is systematically 2
     pages off (every reading sits 2 printed pages before its lesson's pageStart).

Every decision returns a reason code so the builder can count and log it.
Set HEADER_REPAIR = False to fall back to withhold-only (no moves, no repair).
"""
import json
import os
import statistics
from collections import Counter

RULE = 'capped-toc-v2'   # round 4: + systematic TOC offset (header-verified starts); v1 rules otherwise unchanged
CAP_MULT = 2.5
CAP_MIN = 8
HEADER_REPAIR = True          # use header-detected starts to repair the TOC (rule 1)
HEADER_MIN_CONF = 0.8         # header starts at/above this confidence are accepted unconditionally
# tc2_attach gives 0.6 to a header whose number jumps +2…+4 without TOC confirmation — which is exactly
# what happens when the previous header was missed AND the lesson has no TOC entry (LS&ĐL 5 Bài 4).
# Such a header is accepted only when its page is bracketed by the known starts of the neighbouring
# lesson numbers (deterministic plausibility check); below this it is never used.
HEADER_MIN_CONF_BRACKETED = 0.6
# Round 4: the pipeline is versioned (tc2-p1, tc2-p2, …) but this path was pinned to tc2-p1, so a pack
# built after a new pipeline run would silently read the OLD page verdicts — including the old
# 'the back cover belongs to the last lesson'. `WAL_TC2_ATTACH_DIR` points it at the run in hand.
TC2_ATTACH_DIR = os.environ.get('WAL_TC2_ATTACH_DIR') or 'poc-out/trusted-corpus/tc-v2/tc2-p1/attach'

# reason codes — attached
ATTACHED = 'attached'
ATTACHED_REPAIRED = 'attached_header_repaired_start'   # lesson start came from a header, not the TOC
ATTACHED_HEADER_STALE = 'attached_header_stale'        # page-level header chain was stale; TOC kept
# reason codes — withheld / dropped
NO_TOC_RANGES = 'no_toc_ranges'
PAGE_UNKNOWN = 'page_unknown'
BEFORE_FIRST = 'before_first_lesson'
BEYOND_CAP = 'beyond_cap'
BEYOND_HEADER_END = 'beyond_header_end'
SUCCESSOR_UNRANGED = 'successor_unranged'
START_CONFLICT = 'start_conflict'
HEADER_DISAGREES = 'header_disagrees'
HEADER_NO_LESSON = 'header_no_lesson'
NOT_CANONICAL = 'not_canonical'
# reason codes — upstream-keyed cross-check (counted, kept)
RANGE_OK = 'range_ok'
RANGE_MISMATCH = 'range_mismatch'
UNRANGED_LESSON = 'unranged_lesson'

ATTACH_REASONS = {ATTACHED, ATTACHED_REPAIRED, ATTACHED_HEADER_STALE}
WITHHOLD_REASONS = {NO_TOC_RANGES, PAGE_UNKNOWN, BEFORE_FIRST, BEYOND_CAP, BEYOND_HEADER_END, SUCCESSOR_UNRANGED, START_CONFLICT, HEADER_DISAGREES, HEADER_NO_LESSON, NOT_CANONICAL}


def cap_for(starts):
    """cap = max(8, round(2.5 × median gap between consecutive lesson starts))."""
    lens = [b - a for a, b in zip(starts, starts[1:])]
    return max(CAP_MIN, round(CAP_MULT * statistics.median(lens))) if lens else CAP_MIN


def accepted_header_starts(toc_start, header_lessons):
    """number → printed start for header-detected lessons: confidence ≥ 0.8 unconditionally; 0.6–0.8 only
    when the page lies strictly between the known starts of the nearest lower and higher lesson numbers."""
    hdr, pending = {}, []
    for h in header_lessons or []:
        n, p = h.get('number'), h.get('page_printed')
        if n is None or p is None or h.get('source') not in ('header', 'both'):
            continue
        c = h.get('confidence') or 0
        if c >= HEADER_MIN_CONF:
            hdr[n] = p
        elif c >= HEADER_MIN_CONF_BRACKETED:
            pending.append((n, p))
    known = dict(toc_start)
    for n, p in hdr.items():
        known.setdefault(n, p)
    for n, p in sorted(pending):
        if n in known:
            continue
        below = [q for m, q in known.items() if m < n]
        above = [q for m, q in known.items() if m > n]
        if below and above and max(below) < p < min(above):
            hdr[n] = p; known[n] = p
    return hdr


def systematic_toc_offset(toc_start, header_lessons, min_headers=5, min_share=0.6):
    """Round 4 (audit: TV5 pageStart is 2 printed pages AFTER the page that carries the lesson badge — the pipeline
    measured −2 on 17–19 of ~25 headers in TV5 tập một/hai, TV2, TV4). When ≥ min_headers accepted headers (confidence
    ≥ HEADER_MIN_CONF, source header/both) have a TOC start and ≥ min_share of them share one non-zero
    (header − TOC) difference, that difference is the book's TOC offset; 0 otherwise."""
    diffs = []
    for h in header_lessons or []:
        n, p = h.get('number'), h.get('page_printed')
        if n is None or p is None or h.get('source') not in ('header', 'both') or (h.get('confidence') or 0) < HEADER_MIN_CONF:
            continue
        if n in toc_start:
            diffs.append(p - toc_start[n])
    if len(diffs) < min_headers:
        return 0
    best, cnt = Counter(diffs).most_common(1)[0]
    return best if best != 0 and cnt / len(diffs) >= min_share else 0


def capped_ranges(lessons, header_lessons=None):
    """lessons: iterable of {number, pageStart, title} (printed pages).
    header_lessons (optional): iterable of {number, page_printed, source, confidence} from the
    TC-v2 attach file. Returns (ranges, cap, info) with ranges = [{number, title, lo, hi, hi_source,
    start_source, conflicted, ambiguous_after, unranged_successors}] sorted by lo, hi exclusive.
    Round 4: a systematic (header − TOC) offset shifts every TOC start before anything else is decided
    (`info['toc_offset']`), so a book whose TOC is printed 2 pages late no longer conflicts on every lesson."""
    canon = {l['number']: l for l in lessons if l.get('number') is not None}
    toc_raw = {n: l['pageStart'] for n, l in canon.items() if l.get('pageStart') is not None}
    toc_offset = systematic_toc_offset(toc_raw, header_lessons) if HEADER_REPAIR else 0
    toc_start = {n: s + toc_offset for n, s in toc_raw.items()}
    hdr_start = accepted_header_starts(toc_start, header_lessons) if HEADER_REPAIR else {}
    starts = {}; start_source = {}; conflicted = set()
    for n in canon:
        if n in toc_start:
            starts[n] = toc_start[n]; start_source[n] = 'toc'
            if n in hdr_start and abs(hdr_start[n] - toc_start[n]) > 1:
                conflicted.add(n)
        elif n in hdr_start:
            starts[n] = hdr_start[n]; start_source[n] = 'header'
    terminators = sorted(p for n, p in hdr_start.items() if n not in canon)
    ordered = sorted(starts.items(), key=lambda kv: (kv[1], kv[0]))
    cap = cap_for([p for _, p in ordered])
    unranged = sorted(n for n in canon if n not in starts)
    out = []
    for i, (n, lo) in enumerate(ordered):
        nxt_no, nxt_start = (ordered[i + 1] if i + 1 < len(ordered) else (None, None))
        hi, hi_source = lo + cap, 'cap'
        if nxt_start is not None and nxt_start < hi:
            hi, hi_source = nxt_start, 'next_start'
        term = next((t for t in terminators if lo < t < hi), None)
        if term is not None:
            hi, hi_source = term, 'header_terminator'
        succ = [m for m in unranged if n < m and (nxt_no is None or m < nxt_no)]
        out.append(dict(number=n, title=canon[n].get('title'), lo=lo, hi=hi, hi_source=hi_source, start_source=start_source[n],
                        conflicted=(n in conflicted), ambiguous_after=lo if succ else None, unranged_successors=succ))
    info = dict(cap=cap, canonical=len(canon), toc_ranged=len(toc_start), repaired=sum(1 for n in starts if start_source[n] == 'header'),
                conflicted=sorted(conflicted), terminators=len(terminators), unranged=unranged, toc_offset=toc_offset)
    return out, cap, info


class BookAttach:
    """Attachment + identity for ONE book.
    header_pages: pdf page → {lesson, method, kind} (page-level TC-v2 attachment);
    header_lessons: [{number, page_printed, source, confidence}] (header-detected starts)."""

    def __init__(self, book, lessons, header_pages=None, header_lessons=None):
        self.book = book
        self.canonical = {l['number'] for l in lessons if l.get('number') is not None}
        self.ranges, self.cap, self.info = capped_ranges(lessons, header_lessons)
        self.header_pages = header_pages or {}
        toc_start = {l['number']: l['pageStart'] + self.info.get('toc_offset', 0) for l in lessons if l.get('number') is not None and l.get('pageStart') is not None}
        self.header_start = accepted_header_starts(toc_start, header_lessons)
        self.has_header_data = bool(header_pages) or bool(header_lessons)

    def is_canonical(self, number):
        return number is not None and number in self.canonical

    def range_of(self, number):
        return next((r for r in self.ranges if r['number'] == number), None)

    def _toc_hit(self, printed):
        return next((r for r in self.ranges if r['lo'] <= printed < r['hi']), None)

    def header_for(self, pdf_page):
        return self.header_pages.get(pdf_page) if pdf_page is not None else None

    def attach(self, printed, pdf_page=None):
        """→ dict(lesson, title, reason, toc_lesson, header_lesson, header_method, start_source).
        lesson is None when withheld; reason is always set."""
        res = dict(lesson=None, title=None, reason=None, toc_lesson=None, header_lesson=None, header_method=None, start_source=None)
        if not self.ranges:
            res['reason'] = NO_TOC_RANGES; return res
        if printed is None:
            res['reason'] = PAGE_UNKNOWN; return res
        hit = self._toc_hit(printed)
        hdr = self.header_for(pdf_page)
        if hdr is not None:
            res['header_lesson'] = hdr.get('lesson'); res['header_method'] = hdr.get('method')
        if hit is None:
            if printed < self.ranges[0]['lo']:
                res['reason'] = BEFORE_FIRST; return res
            prev = max((r for r in self.ranges if r['lo'] <= printed), key=lambda r: r['lo'])
            res['reason'] = BEYOND_HEADER_END if prev['hi_source'] == 'header_terminator' else BEYOND_CAP; return res
        res['toc_lesson'] = hit['number']; res['start_source'] = hit['start_source']
        if hit['conflicted']:
            res['reason'] = START_CONFLICT; return res
        ambiguous = hit['ambiguous_after'] is not None and printed > hit['ambiguous_after']
        stale = False
        if hdr is not None:
            h = hdr.get('lesson')
            if h is None:
                res['reason'] = HEADER_NO_LESSON; return res
            if h != hit['number']:
                h_start = self.header_start.get(h)
                positive = (not self.is_canonical(h)) or h_start is None or h_start >= hit['lo']
                if positive:
                    res['reason'] = HEADER_DISAGREES; return res
                stale = True
        if ambiguous:
            res['reason'] = SUCCESSOR_UNRANGED; return res
        reason = ATTACHED_HEADER_STALE if stale else (ATTACHED_REPAIRED if hit['start_source'] == 'header' else ATTACHED)
        res.update(lesson=hit['number'], title=hit['title'], reason=reason)
        return res

    def check_upstream(self, lesson, printed=None):
        """Identity gate + counted range cross-check for an upstream-keyed activity → (keep, reason)."""
        if not self.is_canonical(lesson):
            return False, NOT_CANONICAL
        r = self.range_of(lesson)
        if r is None:
            return True, UNRANGED_LESSON
        if printed is None:
            return True, PAGE_UNKNOWN
        return True, (RANGE_OK if r['lo'] <= printed < r['hi'] else RANGE_MISMATCH)


# ---------------------------------------------------------------- loading helpers
def load_header_data(book, attach_dir=TC2_ATTACH_DIR):
    """(pages_map, lessons_list) from the TC-v2 header attachment file, or ({}, []) when absent."""
    p = os.path.join(attach_dir, f'{book}.json')
    if not os.path.exists(p):
        return {}, []
    try:
        a = json.load(open(p, encoding='utf-8'))
    except (OSError, ValueError):
        return {}, []
    pages = {r['page']: dict(lesson=r.get('lesson'), method=r.get('method'), kind=r.get('kind')) for r in a.get('pages', []) if r.get('page') is not None}
    # The attach file's page_printed is unreliable on secondary books (the big lesson-number banner is
    # read as the footer digit: Vật lí 10 "Bài 3 → printed 3"); derive printed from the pdf page and
    # the book's measured printed offset instead, falling back to page_printed only when either is absent.
    off = (a.get('counts') or {}).get('printed_offset')
    lessons = []
    for l in a.get('lessons', []):
        pp = l.get('page_pdf')
        printed = (pp - off) if (pp is not None and off is not None) else l.get('page_printed')
        lessons.append(dict(number=l.get('number'), page_printed=printed, page_pdf=pp, source=l.get('source'), confidence=l.get('confidence')))
    return pages, lessons


class AttachRegistry:
    """Lazy per-book BookAttach over curriculum-structure documents + a reason-coded log."""

    def __init__(self, docs, attach_dir=TC2_ATTACH_DIR, use_headers=True):
        self._docs = {d['sourceDocumentId']: d for d in docs}
        self._books = {}
        self.attach_dir = attach_dir
        self.use_headers = use_headers
        self.counts = Counter()      # (family, reason) → n
        self.dropped = []            # detailed rows for withheld/dropped activities
        self.flagged = []            # upstream cross-check rows that were kept but flagged
        self.moved = []              # attached to a lesson the old uncapped rule would not have chosen

    def book(self, book_id):
        if book_id not in self._books:
            d = self._docs.get(book_id, {})
            hp, hl = load_header_data(book_id, self.attach_dir) if self.use_headers else ({}, [])
            self._books[book_id] = BookAttach(book_id, d.get('lessons', []), hp, hl)
        return self._books[book_id]

    @staticmethod
    def _legacy_lesson(book, printed):
        """The old uncapped rule (last TOC pageStart ≤ page), for the move log only."""
        hit = None
        for r in sorted(book.ranges, key=lambda r: r['lo']):
            if r['start_source'] == 'toc' and r['lo'] <= printed:
                hit = r['number']
        return hit

    def attach(self, family, book_id, printed, pdf_page=None, note=None):
        b = self.book(book_id)
        res = b.attach(printed, pdf_page)
        self.counts[(family, res['reason'])] += 1
        row = dict(family=family, book=book_id, page=printed, pagePdf=pdf_page, reason=res['reason'], tocLesson=res['toc_lesson'],
                   headerLesson=res['header_lesson'], headerMethod=res['header_method'], startSource=res['start_source'], note=note)
        if res['lesson'] is None:
            self.dropped.append(row)
        elif printed is not None and res['lesson'] != self._legacy_lesson(b, printed):
            self.moved.append(dict(row, lesson=res['lesson'], legacyLesson=self._legacy_lesson(b, printed)))
        return res

    def check_upstream(self, family, book_id, lesson, printed=None, note=None):
        b = self.book(book_id)
        keep, reason = b.check_upstream(lesson, printed)
        self.counts[(family, reason)] += 1
        row = dict(family=family, book=book_id, page=printed, lesson=lesson, reason=reason, note=note)
        if not keep:
            self.dropped.append(row)
        elif reason in (RANGE_MISMATCH, UNRANGED_LESSON):
            self.flagged.append(row)
        return keep

    def attach_items(self, family, items, page_key='page', pdf_key='pagePdf', note_key=None):
        """Attach a list of page-keyed activity dicts (e.g. diaMaps): each kept item gets `lesson` and
        `lessonTitle`; items the rule withholds are dropped (fail closed) and logged. Returns the kept list."""
        kept = []
        for it in items:
            res = self.attach(family, it.get('book'), it.get(page_key), it.get(pdf_key), note=it.get(note_key) if note_key else None)
            if res['lesson'] is None:
                continue
            kept.append(dict(it, lesson=res['lesson'], lessonTitle=res['title'] or None))
        return kept

    def summary(self):
        by_family = {}
        for (fam, reason), n in sorted(self.counts.items()):
            by_family.setdefault(fam, {})[reason] = n
        return dict(rule=RULE, capMult=CAP_MULT, capMin=CAP_MIN, headerRepair=HEADER_REPAIR, counts=by_family,
                    dropped=len(self.dropped), flagged=len(self.flagged), moved=len(self.moved),
                    books={b: dict(x.info, headerData=x.has_header_data) for b, x in sorted(self._books.items())})
