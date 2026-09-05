#!/usr/bin/env python3
"""TC-v2 — HEADER-BASED LESSON ATTACHMENT + TOC REPAIR (deterministic: OCR-line geometry + lexicon).

Why (TC-19 #5, TC-02 §5): TOC-range attachment is wrong on 10/38 hard gold pages — partial TOCs
(KHTN 7 stops at Bài 18, KHTN 8 at Bài 22, Khoa học 4/5 lack pageStart for 4 / 8 lessons), non-lesson
pages (TOC, back matter, theme openers) attached to a lesson, two lessons on one page. Here every page
gets a lesson from the PRINTED lesson header when one exists, `continues` otherwise, and "no lesson"
for front/back matter and theme openers; the TOC is only a cross-check and a fallback.

Header forms (all measured on OCR lines, never on extractor output):
  secondary  "Bài 20" / "BÀI 34. TITLE" as one big line (h ≥ 1.25 × median) in the top 35 %
  elementary a small "Bài" line and/or a large standalone 1–2-digit number (h ≥ 1.4 × median, top 30 %)
             next to an UPPERCASE title line (KNTT Khoa học 4/5 banner)
Not a header: a page whose top lines say MỤC LỤC / LỜI NÓI ĐẦU / HƯỚNG DẪN SỬ DỤNG / BẢNG TRA CỨU… (front or
back matter), a page with ≥ 4 "Bài N" lines (a TOC), a "Bài N" inside a sentence ("xem Bài 3").

Sequence rule per book: headers must be plausible in order — n == current+1 (or the first header) is
accepted; a TOC pageStart within ±1 printed page confirms any n; a jump backwards or > +4 without TOC
confirmation is rejected as an OCR misread / cross-reference and logged. Pages without a header continue
the current lesson (method `continuation`); a theme opener (CHỦ ĐỀ / CHƯƠNG banner, no header) ends it.

Outputs poc-out/trusted-corpus/tc-v2/<pipeline>/attach/<book>.json:
  pages[]   {page, printed, kind, lesson, method header|continuation|none, confidence, header{number,title,y,form}, prev_lesson}
  lessons[] {number, title, page_pdf, page_printed, source header|toc|both}
  counts    canonical_lesson_count (curriculum-structure lessonCount) · toc_ranged · header_detected ·
            repaired_ranged (union) · beyond_canonical (header numbers > lessonCount) · rejected_headers
Usage: python3 tool/corpus/tc2_attach.py --pipeline tc2-p1 <book>…   |   --gold-books (every book that has a gold page)
"""
import argparse
import glob
import json
import os
import re
import statistics
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tc2_paths  # noqa: E402
ROOT = tc2_paths.ROOT
OCR = f'{ROOT}/poc-out/graph/ocr-body'
CURR = f'{ROOT}/poc-out/graph/curriculum-structure.json'

# Round 4 (Lane C request 2): the banner font makes OCR read «BÀI» as «BÃI» on 5 of the 28 LS&ĐL 5 lessons
# (Bài 3, 7, 11, 13, 23) — the class had no `Ã`, so those five lessons were never ranged and 17 of 123 pages
# stayed attached to their predecessor. One character class; the sequence rule below is unchanged.
LESSON_HDR = re.compile(r'^\s*(B[ÀÁẢÃẠ]I|B[àáảãạ]i)\s+(\d{1,2})\b\s*[.:]?\s*(.*)$')   # OCR tone slips on display fonts: "Bải 19", "Bái 3", "BÃI 7"
BAI_ALONE = re.compile(r'^\s*(B[ÀÁẢÃẠ]I|B[àáảãạ]i)\s*$')
DIGITS = re.compile(r'^\d{1,3}$')
THEME = re.compile(r'^\s*(CHỦ ĐỀ|Chủ đề|CHƯƠNG|Chương|PHẦN|Phần)\s+([IVX]+|\d+)\b')
FRONT = re.compile(r'^\s*(MỤC LỤC|Mục lục|LỜI NÓI ĐẦU|Lời nói đầu|HƯỚNG DẪN SỬ DỤNG|Hướng dẫn sử dụng|BẢNG TRA CỨU|Bảng tra cứu|GIẢI THÍCH THUẬT NGỮ|Giải thích thuật ngữ|PHỤ LỤC|Phụ lục|BẢNG THUẬT NGỮ|TÀI LIỆU THAM KHẢO|Tài liệu tham khảo)')
BACK = re.compile(r'^\s*(BẢNG TRA CỨU|Bảng tra cứu|GIẢI THÍCH THUẬT NGỮ|Giải thích thuật ngữ|PHỤ LỤC|Phụ lục|BẢNG THUẬT NGỮ|TÀI LIỆU THAM KHẢO|Tài liệu tham khảo)')
# Round 4 (failure class 4: lesson attachment / identity). The audit's 8 of 11 wrong attachments were the BACK COVER
# (publisher's book list, ISBN, barcode, price, website) attached to a book's last lesson: nothing above marked it as
# end matter. A cover is recognised by its furniture, never by position alone; two independent marks are required.
#
# Round 4 correctness review (F13): "two of any seven marks" was not discriminating — three of the seven are ORDINARY
# CONTENT («Giá:» is a price in a Toán word problem, «Website:» sits in an «Em có biết» box, «HUÂN CHƯƠNG» is Lịch sử
# prose), and a false positive did not merely mislabel one page: it ended the book. The marks are now split, and a
# cover needs at least one mark that only a cover carries. Measured over the 42 attached books: all 42 back covers
# carry ≥ 1 strong mark (the 7 SGV covers print «BỘ SÁCH GIÁO VIÊN», not «… GIÁO KHOA» — hence both spellings).
COVER_STRONG = (re.compile(r'\bISBN\b'),
                re.compile(r'\bBỘ SÁCH GIÁO (?:KHOA|VIÊN)\b'),
                re.compile(r'\bNHÀ XUẤT BẢN GIÁO DỤC\b'),
                re.compile(r'^\s*9\s?7\d{4}\s?\d{6}\s*$'))    # EAN-13 barcode digits
COVER_WEAK = (re.compile(r'\bWebsite\s*:', re.IGNORECASE),
              re.compile(r'^\s*Giá\s*:', re.IGNORECASE),
              re.compile(r'\bHUÂN CHƯƠNG\b|\bHUÀN CHƯƠNG\b'))
COVER_MARKS = COVER_STRONG + COVER_WEAK
COVER_MIN_MARKS = 2
COVER_MIN_STRONG = 1

# Round 5 (Founder 97-row audit, defect 6: «imprint / back matter → lesson heading» - end matter STILL leaking
# into a lesson after round 4's cover fix). Reproduced at scale: **26 of the 42 attached books** attach their
# IMPRINT page (the colophon: who published it, how many copies, the deposit date) to the book's last lesson,
# by `continuation`. The round-4 rule could not catch it and it is worth saying exactly why rather than
# widening a threshold: an imprint page IS in the tail and DOES carry a strong mark (ISBN), but it carries
# only ONE - the three weak marks («Website:», «Giá:», «HUÂN CHƯƠNG») are *back-cover* furniture, and an
# imprint page is not a back cover. `COVER_MIN_MARKS = 2` therefore refused it, correctly, for a cover.
#
# The fix is a mark family of its own, in the same shape as the cover rule (≥ 2 marks, no lesson banner,
# tail of the book) and with the same fail-closed direction. This vocabulary is publishing boilerplate that
# never appears in a lesson: «Chịu trách nhiệm xuất bản», «Số ĐKXB», «In xong và nộp lưu chiểu». Measured:
# every one of the 26 pages carries ≥ 3 of these, and no page currently attached to a lesson body carries 2.
IMPRINT_MARKS = (re.compile(r'Chịu trách nhiệm xuất bản', re.IGNORECASE),
                 re.compile(r'Chịu trách nhiệm nội dung', re.IGNORECASE),
                 re.compile(r'Biên tập viên|Biên tập nội dung', re.IGNORECASE),
                 re.compile(r'Trình bày bìa|Thiết kế sách|Chế bản', re.IGNORECASE),
                 re.compile(r'Số\s*Đ?KXB|Số\s*QĐXB', re.IGNORECASE),
                 re.compile(r'In xong và nộp lưu chiểu', re.IGNORECASE),
                 re.compile(r'Bản quyền thuộc', re.IGNORECASE),
                 re.compile(r'\bIn\b[^.\n]{0,30}\bcuốn\b', re.IGNORECASE))
IMPRINT_MIN_MARKS = 2


def upper_ratio(t):
    letters = [c for c in t if c.isalpha()]
    return (sum(1 for c in letters if c.isupper()) / len(letters)) if letters else 0.0


def _norm(s):
    import unicodedata
    s = unicodedata.normalize('NFD', (s or '').replace('đ', 'd').replace('Đ', 'D'))
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower()
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()


def printed_offset(book):
    """Mode of (pdf page − footer digit) over the book (same rule as tool/ui/pattern_router.printed_to_pdf_offset, absolute paths)."""
    diffs = Counter()
    for fp in glob.glob(f'{OCR}/{book}/p*.json'):
        pdf = int(re.search(r'p(\d+)\.json', fp).group(1))
        try:
            lines = json.load(open(fp))['lines']
        except (OSError, ValueError):
            continue
        for l in lines[-3:] + lines[:2]:
            t = l['text'].strip()
            if DIGITS.match(t) and (l['y'] > 0.88 or l['y'] < 0.08):
                d = pdf - int(t)
                if -3 <= d <= 15:
                    diffs[d] += 1
    if not diffs:
        return None
    (best, n), = diffs.most_common(1)
    return best if n >= 3 else None


def page_info(book, page, n_pages=None, lines=None):
    """`lines` (OCR lines of the page) may be injected instead of read from disk — used by the tests."""
    if lines is None:
        fp = f'{OCR}/{book}/p{page:03d}.json'
        lines = json.load(open(fp))['lines'] if os.path.exists(fp) else []
    lines = [l for l in lines if l.get('text', '').strip()]
    info = dict(page=page, lines=len(lines), printed=None, kind='page', header=None, theme=None, continuation=False, _tail=bool(n_pages and page >= 0.88 * n_pages))
    if not lines:
        info['kind'] = 'empty'; return info
    med = statistics.median(l['h'] for l in lines)
    for l in lines[-4:] + lines[:2]:
        t = l['text'].strip()
        if DIGITS.match(t) and (l['y'] > 0.88 or l['y'] < 0.08):
            info['printed'] = int(t)
    top = sorted(lines, key=lambda l: l['y'])[:8]
    big_top = [l for l in top if l['h'] >= 1.2 * med]
    strong = sum(1 for rx in COVER_STRONG if any(rx.search(l['text'].strip()) for l in lines))
    weak = sum(1 for rx in COVER_WEAK if any(rx.search(l['text'].strip()) for l in lines))
    if any(FRONT.match(l['text'].strip()) for l in top):
        is_back = any(BACK.match(l['text'].strip()) for l in big_top)
        # back matter only counts in the last 12 % of the book (a "Tài liệu tham khảo" line inside a lesson is not the end of the book)
        info['kind'] = 'back_matter' if (is_back and info.get('_tail')) else ('front_matter' if not is_back else 'page')
        if info['kind'] != 'page':
            return info
    hdr_lines = [l for l in lines if LESSON_HDR.match(l['text'].strip())]
    if len(hdr_lines) >= 4:
        trailing_num = sum(1 for l in hdr_lines if re.search(r'\s\d{1,3}\s*$', l['text'].strip()))
        if trailing_num >= 3 or any(re.match(r'^\s*(MỤC LỤC|Mục lục)', l['text'].strip()) for l in top):
            info['kind'] = 'toc'; return info
        info['ambiguous_bai'] = True   # Toán-style exercise numbering "Bài 1/2/3…" on one page — not lesson headers
        return info
    body_lines = sorted(lines, key=lambda l: l['y'])
    first_body = next((l for l in body_lines if l['y'] > 0.08 and len(l['text'].strip()) > 20), None)
    info['continuation'] = bool(first_body and first_body['text'].strip()[:1].islower())
    # secondary form
    cands = []
    for l in lines:
        t = l['text'].strip(); m = LESSON_HDR.match(t)
        big = l['h'] >= 1.25 * med or (l['h'] >= 1.1 * med and upper_ratio(t) >= 0.7 and len(t) >= 8)   # SGV "BÀI 34. TITLE" lines are bold but only ~1.2× the body height
        if m and big and l['y'] < 0.35 and len(t) <= 120:
            title = m.group(3).strip()
            if not title:
                nxt = [x for x in lines if x['y'] > l['y'] - 0.01 and x['y'] < l['y'] + 0.12 and x is not l and upper_ratio(x['text']) >= 0.7 and len(x['text'].strip()) >= 4 and x['h'] >= 1.2 * med]
                title = ' '.join(x['text'].strip() for x in sorted(nxt, key=lambda x: (x['y'], x['x']))[:2])
            cands.append(dict(number=int(m.group(2)), title=title[:120], y=round(l['y'], 3), form='secondary', h=round(l['h'] / med, 2)))
    titles = [l for l in lines if upper_ratio(l['text']) >= 0.7 and len(l['text'].strip()) >= 6 and l['h'] >= 1.3 * med and l['y'] < 0.35 and not THEME.match(l['text'].strip()) and not DIGITS.match(l['text'].strip())]
    if not cands:
        # KNTT KHTN 6 form: a SMALL "Bài N" line (≈ body height) printed beside a large uppercase title
        for l in lines:
            t = l['text'].strip(); m = LESSON_HDR.match(t)
            if m and not m.group(3).strip() and l['y'] < 0.3 and any(abs(x['y'] - l['y']) < 0.1 for x in titles):
                near_t = sorted([x for x in titles if abs(x['y'] - l['y']) < 0.1], key=lambda x: (x['y'], x['x']))
                cands.append(dict(number=int(m.group(2)), title=' '.join(x['text'].strip() for x in near_t[:2])[:120], y=round(l['y'], 3), form='small-bai+title', h=round(l['h'] / med, 2)))
                break
    if not cands and page > 3:
        # elementary form: big standalone digit (not the footer, not the cover's grade number) + uppercase title nearby, or a lone "Bài" line
        bigs = [l for l in lines if DIGITS.match(l['text'].strip()) and 1.4 * med <= l['h'] <= 3.5 * med and l['y'] < 0.3 and int(l['text'].strip()) <= 60]
        bai = [l for l in lines if BAI_ALONE.match(l['text'].strip()) and l['y'] < 0.35]
        for d in bigs:
            near_t = [t for t in titles if abs(t['y'] - d['y']) < 0.12]
            if near_t or bai:
                title = ' '.join(t['text'].strip() for t in sorted(near_t, key=lambda x: (x['y'], x['x']))[:2])
                cands.append(dict(number=int(d['text'].strip()), title=title[:120], y=round(d['y'], 3), form='elementary', h=round(d['h'] / med, 2)))
                break
        if not cands and bai:
            # the OCR dropped the stylised digit: a lone "Bài" beside an uppercase title → number resolved later (TOC title match, else current+1)
            near_t = [t for t in titles if abs(t['y'] - bai[0]['y']) < 0.12]
            if near_t:
                title = ' '.join(t['text'].strip() for t in sorted(near_t, key=lambda x: (x['y'], x['x']))[:2])
                cands.append(dict(number=None, title=title[:120], y=round(bai[0]['y'], 3), form='elementary-no-digit', h=round(bai[0]['h'] / med, 2)))
    if cands:
        info['header'] = sorted(cands, key=lambda c: c['y'])[0]
    # Round 4 correctness review (F13): the cover verdict runs LAST, so a page that is a TOC, front/back matter,
    # or that PRINTS ITS OWN LESSON BANNER is never called a cover. Measured over the 42 attached books: no page
    # currently classified a cover carries a detected lesson header, so this costs no back cover and it closes the
    # «a Lịch sử page naming a medal and the publisher ends the book» case.
    if info['header'] is None and strong >= COVER_MIN_STRONG and strong + weak >= COVER_MIN_MARKS and (info['_tail'] or page <= 3):
        info['kind'] = 'back_cover' if info['_tail'] else 'front_cover'
        info['cover_marks'] = strong + weak; info['cover_strong'] = strong
        return info
    # Round 5 (audit defect 6): the imprint / colophon page. Same shape as the cover rule - two independent
    # marks and no lesson banner - with the vocabulary an imprint page actually prints. In the tail it ends
    # the book (it is the last content page); in the first three pages it is front matter and ends nothing,
    # because a false positive there would delete the whole book.
    imprint = sum(1 for pat in IMPRINT_MARKS if any(pat.search(l['text']) for l in lines))
    if info['header'] is None and imprint >= IMPRINT_MIN_MARKS and (info['_tail'] or page <= 3):
        info['kind'] = 'imprint' if info['_tail'] else 'front_matter'
        info['imprint_marks'] = imprint
        return info
    th = [l for l in lines if THEME.match(l['text'].strip()) and l['h'] >= 1.4 * med and l['y'] < 0.4]
    if th:
        info['theme'] = th[0]['text'].strip()[:60]
        if not info['header'] and len(lines) < 40:
            info['kind'] = 'theme_opener'
    return info


def _systematic_toc_offset(pages, infos, toc, off, min_headers=5, min_share=0.6):
    """MODE of (printed page of a detected header − TOC pageStart) over plausible headers when ≥ min_headers carry a
    TOC start and ≥ min_share of them agree on one non-zero value; 0 otherwise. Plausible = the sequence rule alone
    (first header, or current + 1 … current + 4).

    (Round 4 correctness review, F12: the docstring said «Median». The code takes the mode — `Counter.most_common`
    — and the `min_share` gate below only makes sense for a mode: it asks what share of the headers agree on ONE
    value. The comment was wrong, not the code.)"""
    diffs = []
    current = None
    for p in pages:
        info = infos[p]
        h = info.get('header')
        if info['kind'] != 'page' or not h or h.get('number') is None:
            continue
        n = h['number']
        if current is not None and not (current < n <= current + 4):
            continue
        printed = info['printed'] if info['printed'] is not None else (p - off if off is not None else None)
        if printed is not None and toc.get(n, {}).get('pageStart') is not None:
            diffs.append(printed - toc[n]['pageStart'])
        current = n
    if len(diffs) < min_headers:
        return 0
    best, cnt = Counter(diffs).most_common(1)[0]
    return best if best != 0 and cnt / len(diffs) >= min_share else 0


def attach_book(book, pipeline='tc2-p1', write=True):
    docs = {d['sourceDocumentId']: d for d in json.load(open(CURR))['documents']}
    meta = docs.get(book, {})
    toc = {l['number']: l for l in meta.get('lessons', []) if l.get('number') is not None}
    off = printed_offset(book)
    pages = sorted(int(re.search(r'p(\d+)\.json', f).group(1)) for f in glob.glob(f'{OCR}/{book}/p*.json'))
    infos = {p: page_info(book, p, len(pages)) for p in pages}
    # Round 4: systematic TOC offset. Some books print the lesson badge N printed pages BEFORE the TOC's pageStart.
    # Measured per book from the headers themselves (first pass, sequence rule only): when ≥ 5 headers carry a TOC
    # start and ≥ 60 % share the same non-zero difference, every TOC start is shifted by it before it confirms a
    # header — the header is the printed truth, the TOC a cross-check. Measured on 42 books: it fires on 3 of them,
    # all −2 (TV5 tập hai, TV2 tập một, TV2 tập hai) and NOT on TV5 tập một or TV4 tập một, whose headers agree with
    # their TOC. The rule follows the evidence in the book at hand; it is not a per-series assumption.
    toc_offset = _systematic_toc_offset(pages, infos, toc, off)
    toc_start = {n: (l['pageStart'] + toc_offset) for n, l in toc.items() if l.get('pageStart') is not None}
    out_pages, headers, rejected = [], [], []
    current, conf, seen_first, ended, last_lesson = None, 0.0, False, False, None
    for p in pages:
        info = infos[p]; info.pop('_tail', None)
        # Round 4 correctness review (found while fixing F14): a footer digit that disagrees with the book's own
        # measured printed offset is a MISREAD, not this page's printed page — a number in the top/bottom band
        # (a year, a big result, the lesson badge) is read as the footer. Measured: on LS&ĐL 5 p024 the footer
        # read 104 on a 123-page book (p − off = 22), on Tin học 6 p022 it read 210 (21), on TV2 p045 303 (44),
        # on Toán 9 p052 132 (51). Such a number makes EVERY remaining TOC start «already due» and, with F14's
        # clamp, would jump the page four lessons forward. The offset is the mode over the whole book; the single
        # page's digit only wins when the two agree to within a page.
        printed = info['printed']
        if off is not None:
            derived = p - off
            if printed is None or abs(printed - derived) > 1:
                if printed is not None:
                    info['printed_misread'] = printed
                printed = derived
        # Round 4 correctness review (F13): ending the book is REVERSIBLE. `ended` used to delete every page after
        # the first back-cover verdict, so a single false positive silently removed the tail of a book with no way
        # back. A page that PRINTS a plausible lesson banner re-opens the book — the printed header is this module's
        # truth and the TOC only a cross-check, so the same evidence that opens a lesson anywhere else opens it here.
        # Real end matter carries no banner, so the class-4 gain is untouched.
        resumed = False
        if ended and info['kind'] == 'page':
            h0 = info.get('header') or {}
            n0 = h0.get('number')
            if n0 is not None and (last_lesson is None or last_lesson < n0 <= last_lesson + 4):
                ended, current, resumed = False, last_lesson, True
        rec = dict(page=p, printed=printed, kind=info['kind'], lesson=None, method='none', confidence=0.0, header=info['header'], theme=info['theme'], prev_lesson=current, continues=info['continuation'])
        if resumed:
            rec['resumed_after_end'] = True
        if info['kind'] in ('front_matter', 'toc', 'empty', 'front_cover'):
            out_pages.append(rec); continue
        if info['kind'] in ('back_matter', 'back_cover', 'imprint'):
            ended = True; current = None; out_pages.append(rec); continue
        if ended:
            rec['kind'] = 'back_matter'; out_pages.append(rec); continue
        h = info['header']
        if h and h.get('number') is None:
            # resolve a digit-less banner: TOC title match (diacritics-insensitive prefix), else current+1
            key = _norm(h.get('title') or '')
            hit = [n for n, l in toc.items() if l.get('title') and key and (_norm(l['title'])[:25] == key[:25] or key[:25] in _norm(l['title']) or _norm(l['title'])[:20] in key)]
            if len(hit) == 1:
                h['number'] = hit[0]; h['resolved_by'] = 'toc-title'
            elif current is not None:
                h['number'] = current + 1; h['resolved_by'] = 'current+1'
            else:
                h = None
        if h:
            n = h['number']
            toc_ok = n in toc_start and printed is not None and abs(toc_start[n] - printed) <= 1
            accept = False; c = 0.0
            if toc_ok:
                accept, c = True, 0.95
            elif current is None and not seen_first:
                accept, c = True, 0.8
            elif current is not None and n == current + 1:
                accept, c = True, 0.85
            elif current is not None and current + 1 < n <= current + 4:
                accept, c = True, 0.6
            if accept:
                current, conf, seen_first, last_lesson = n, c, True, n
                headers.append(dict(number=n, title=h['title'], page_pdf=p, page_printed=printed, source='both' if toc_ok else 'header', confidence=c, form=h['form']))
                rec.update(lesson=n, method='header', confidence=c)
            else:
                rejected.append(dict(page=p, header=h, current=current))
                if current is not None:
                    rec.update(lesson=current, method='continuation', confidence=round(conf * 0.9, 2))
            out_pages.append(rec); continue
        if info['kind'] == 'theme_opener':
            current = None; out_pages.append(rec); continue
        # Round 4: TOC-range fallback — no header on this page, but the (offset-corrected) TOC says a LATER lesson
        # starts here or started on a previous page that carried no detectable header (Tin học 6 p21, Toán 9 p29,
        # Toán 12 p20, Vật lí 11 p105, SGV Toán 4 p54 on the gold set): switch to that lesson at 0.6 confidence,
        # method `toc_range`, never backwards, never across a lesson the headers already passed.
        # Fail closed on both ends (round 4, measured): the fallback NEVER runs before the book's first header
        # — before it, `max(due)` is an unbounded jump into the middle of the book (it put KHTN 9's second TOC
        # page, and the eight lesson pages after it, into Bài 26) — and it never skips more than 4 lessons.
        # Round 4 correctness review (F14): the +4 bound is a CLAMP on which lessons the fallback may choose, not a
        # veto on the whole page. `max(due) <= current + 4` threw away a legitimate `current + 1` whenever a far
        # outlier (an OCR-misread TOC start) sat in the same set, and the page then silently kept the WRONG lesson.
        if printed is not None and toc_start and seen_first and current is not None:
            due = [n for n, s in toc_start.items() if s <= printed and n > current and n not in {hh['number'] for hh in headers}]
            near = [n for n in due if n <= current + 4]
            if near:
                n = max(near)
                current, conf, last_lesson = n, 0.6, n
                headers.append(dict(number=n, title=toc[n].get('title'), page_pdf=p, page_printed=printed, source='toc_range', confidence=0.6, form=None))
                rec.update(lesson=n, method='toc_range', confidence=0.6); out_pages.append(rec); continue
        if current is not None:
            rec.update(lesson=current, method='continuation', confidence=round(conf, 2))
        out_pages.append(rec)
    # lessons: headers ∪ TOC-only
    by_n = {h['number']: h for h in headers}
    for n, l in toc.items():
        if n not in by_n and l.get('pageStart') is not None and off is not None:
            by_n[n] = dict(number=n, title=l.get('title'), page_pdf=l['pageStart'] + off, page_printed=l['pageStart'], source='toc', confidence=0.6, form=None)
    lessons = [by_n[n] for n in sorted(by_n)]
    canonical = meta.get('lessonCount') or len(toc)
    toc_ranged = sum(1 for l in toc.values() if l.get('pageStart') is not None)
    counts = dict(canonical_lesson_count=canonical, toc_lessons=len(toc), toc_ranged=toc_ranged, header_detected=sum(1 for h in headers if h['source'] != 'toc_range'), toc_range_fallbacks=sum(1 for h in headers if h['source'] == 'toc_range'), toc_offset=toc_offset, header_confirmed_by_toc=sum(1 for h in headers if h['source'] == 'both'),
                  header_only=sum(1 for h in headers if h['source'] == 'header'), repaired_ranged=len(lessons), beyond_canonical=sum(1 for n in by_n if n > canonical), max_lesson_number=max(by_n) if by_n else None,
                  rejected_headers=len(rejected), pages=len(pages), pages_with_lesson=sum(1 for r in out_pages if r['lesson'] is not None), pages_no_lesson=sum(1 for r in out_pages if r['lesson'] is None),
                  page_kinds=dict(Counter(r['kind'] for r in out_pages)), printed_offset=off, structure_status=meta.get('structureStatus'))
    res = dict(book=book, pipeline=pipeline, docType=meta.get('docType'), grade=meta.get('grade'), subject=meta.get('subject'), counts=counts, lessons=lessons, rejected_headers=rejected, pages=out_pages)
    if write:
        d = f'{tc2_paths.out_root(pipeline)}/attach'; os.makedirs(d, exist_ok=True)
        json.dump(res, open(f'{d}/{book}.json', 'w'), ensure_ascii=False, indent=0)
    return res


def load_attach(book, pipeline='tc2-p1'):
    p = f'{tc2_paths.out_root(pipeline)}/attach/{book}.json'
    return json.load(open(p)) if os.path.exists(p) else None


def lesson_for_block(page_rec, bbox):
    """Two lessons on one page: blocks above a mid-page header belong to the previous lesson."""
    if page_rec is None:
        return None, 'none'
    h = page_rec.get('header')
    if h and page_rec.get('method') == 'header' and bbox and (bbox[1] + bbox[3] / 2) < h['y'] - 0.01 and page_rec.get('prev_lesson') is not None:
        return page_rec['prev_lesson'], 'continuation-before-header'
    return page_rec.get('lesson'), page_rec.get('method', 'none')


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--pipeline', default='tc2-p1'); ap.add_argument('books', nargs='*'); ap.add_argument('--gold-books', action='store_true')
    ap.add_argument('--out', default=None, help='pipeline output root (default poc-out/trusted-corpus/tc-v2/<pipeline>; env TC2_OUT_ROOT)')
    a = ap.parse_args()
    if a.out:
        tc2_paths.set_out_root(a.out)
    books = list(a.books)
    if a.gold_books:
        books += sorted({json.load(open(f))['book'] for f in glob.glob(f'{HERE}/tc_gold/*.json')})
    for b in sorted(set(books)):
        r = attach_book(b, a.pipeline)
        c = r['counts']
        print(f"{b}: canonical={c['canonical_lesson_count']} toc_ranged={c['toc_ranged']} headers={c['header_detected']} (toc-confirmed {c['header_confirmed_by_toc']}, header-only {c['header_only']}) repaired_ranged={c['repaired_ranged']} beyond_canonical={c['beyond_canonical']} max={c['max_lesson_number']} rejected={c['rejected_headers']} pages={c['pages']} with_lesson={c['pages_with_lesson']} kinds={c['page_kinds']}")


if __name__ == '__main__':
    main()
