#!/usr/bin/env python3
"""WAL-192 gate script — automated SGK<->SGV answer-key linkage verification
for Tin học, scoped to grades 6/9/11/12, single-select only.

Not wired into build_lesson_index.py yet — this is the fail-closed gate that
decides whether WAL-192 proceeds to implementation. See docs/research/
LEARNABLE-COVERAGE-SCALE-STRATEGY.md §"Tin học — full-chain validation".

Why not just match by each document's own internal lesson counter: spot-check
found SGK's and SGV's independently-derived `lesson` fields (from
tool/ingest/extract_units_generic.py / poc-out/units-k12/) drift out of sync
with each other on a real, previously-verified case (the same real lesson was
internal-lesson=4 in SGK's units-k12 output but internal-lesson=3 in SGV's) —
a single missed header detection anywhere in one document permanently offsets
every later lesson count in that document. Not safe as a cross-document key.

What this script does instead: derives each document's lesson page-ranges
independently from its own PRINTED "Bài N" number (not a re-derived counter):
  - SGK: from its own table-of-contents page, "Bài N. Title <printed-page>"
    lines give (number, title, start printed page); converted to PDF pages
    via each page's own OCR'd footer page number.
  - SGV: directly from in-body "BÀI N. TITLE" headers (confirmed reliable,
    unlike SGK where large-typography lesson titles don't OCR as clean text).
Both are keyed by the same real printed number N, so no drift risk.

Within SGK lesson N's page range, this collects ALL numbered MCQ-shaped items
(a line "K. <question>" followed by >=2 lines "A. .../B. ..."). The SGK's own
front-matter documents a FIXED section order for every lesson (Mục tiêu →
Khởi động → Nội dung → Hoạt động → Kiến thức mới → Hộp kiến thức → Câu hỏi →
Luyện tập → Vận dụng) — so the first contiguous run of K items (numbering
restarts at 1 for the next section) is the Câu hỏi block. A match is HIGH
CONFIDENCE only when: SGV has a "Câu hỏi (hoạt động củng cố kiến thức)"
answer run of length K, SGK's first-encountered run also has exactly K items,
and none of SGV's K answers are multi-select. Anything else is UNKNOWN —
fail closed, never guessed.
"""
import glob
import json
import re

GRADES = [6, 9, 11, 12]

TOC_TITLE = re.compile(r'^Bài\s+(\d+[a-z]?)\.\s+(.+)$')
BAI_HEADER = re.compile(r'^BÀI\s+(\d+[a-z]?)\.\s+\S')
Q_RE = re.compile(r'^(\d+)\.\s+\S')
OPT_RE = re.compile(r'^[A-D]\.\s+\S')
SVG_HEADER_RE = re.compile(
    r'(Câu hỏi \(hoạt động củng cố kiến thức\)|Hoạt động luyện tập|'
    r'Hoạt động vận dụng|Hoạt động củng cố kiến thức|Hoạt động \d+[:\.]?)',
    re.IGNORECASE)
SGV_ANSWER_RE = re.compile(r'^(\d+)\.\s*Đáp án:\s*(.+)$')
DIGITS_ONLY = re.compile(r'^\d+$')


def load_pages(book):
    pages = {}
    for f in sorted(glob.glob(f'poc-out/graph/ocr-body/{book}/p*.json')):
        j = json.load(open(f))
        pdf = int(re.search(r'p(\d+)\.json', f).group(1))
        lines = [l['text'] for l in j['lines']]
        printed = None
        for t in lines:
            if DIGITS_ONLY.match(t.strip()):
                printed = int(t.strip())
        pages[pdf] = dict(lines=lines, printed=printed)
    return pages


def printed_to_pdf(pages):
    m = {}
    for pdf in sorted(pages):
        p = pages[pdf]['printed']
        if p is not None and p not in m:
            m[p] = pdf
    return m


def toc_entries_on_page(lines):
    """TOC prints title and its page number on separate consecutive lines
    (confirmed on real OCR — not a single 'title ... N' line)."""
    entries = []
    for i, t in enumerate(lines):
        m = TOC_TITLE.match(t.strip())
        if not m:
            continue
        for j in range(i + 1, min(i + 3, len(lines))):
            nt = lines[j].strip()
            if DIGITS_ONLY.match(nt):
                entries.append((m.group(1), m.group(2), int(nt)))
                break
    return entries


def sgk_lesson_ranges(pages):
    best_pdf, best_hits = None, []
    for pdf, pg in pages.items():
        hits = toc_entries_on_page(pg['lines'])
        if len(hits) > len(best_hits):
            best_pdf, best_hits = pdf, hits
    if not best_hits:
        return []
    entries = sorted(best_hits, key=lambda e: e[2])
    p2pdf = printed_to_pdf(pages)
    ranges = []
    for i, (num, title, startp) in enumerate(entries):
        start_pdf = p2pdf.get(startp)
        if start_pdf is None:
            continue
        end_pdf = max(pages.keys())
        if i + 1 < len(entries):
            nxt_pdf = p2pdf.get(entries[i + 1][2])
            if nxt_pdf:
                end_pdf = nxt_pdf - 1
        ranges.append(dict(number=num, title=title, start_pdf=start_pdf, end_pdf=end_pdf))
    return ranges


def sgv_lesson_ranges(pages):
    hits = []
    for pdf in sorted(pages):
        for t in pages[pdf]['lines']:
            m = BAI_HEADER.match(t.strip())
            if m:
                hits.append((m.group(1), pdf))
                break
    ranges = []
    for i, (num, pdf) in enumerate(hits):
        end_pdf = hits[i + 1][1] - 1 if i + 1 < len(hits) else max(pages.keys())
        ranges.append(dict(number=num, start_pdf=pdf, end_pdf=end_pdf))
    return ranges


def sgk_mcq_runs(pages, start_pdf, end_pdf):
    """Numbered-MCQ-shaped items in page order, split into runs (numbering
    restarting at 1 starts a new run — each run ~= one SGK section)."""
    items = []
    cur = None
    for pdf in range(start_pdf, end_pdf + 1):
        if pdf not in pages:
            continue
        for t in pages[pdf]['lines']:
            ts = t.strip()
            qm = Q_RE.match(ts)
            if qm:
                if cur and len(cur['options']) >= 2:
                    items.append(cur)
                elif cur:
                    cur = None
                cur = dict(qnum=int(qm.group(1)), text=ts, options=[])
                continue
            om = OPT_RE.match(ts)
            if om and cur:
                cur['options'].append(ts)
    if cur and len(cur['options']) >= 2:
        items.append(cur)
    runs = []
    for it in items:
        if it['qnum'] == 1 or not runs:
            runs.append([it])
        else:
            runs[-1].append(it)
    return runs


def sgv_answer_runs(pages, start_pdf, end_pdf):
    """(header_class, [(qnum, answer_text, is_multi), ...]) runs in page order."""
    runs = []
    cur_header = None
    cur_run = None
    for pdf in range(start_pdf, end_pdf + 1):
        if pdf not in pages:
            continue
        for t in pages[pdf]['lines']:
            ts = t.strip()
            hm = SVG_HEADER_RE.search(ts)
            if hm:
                if cur_run:
                    runs.append((cur_header, cur_run))
                cur_header = hm.group(1)
                cur_run = []
                continue
            am = SGV_ANSWER_RE.match(ts)
            if am and cur_run is not None:
                ans = am.group(2).strip().rstrip('.')
                is_multi = bool(re.search(r'[A-D]\s*,\s*[A-D]', ans))
                cur_run.append((int(am.group(1)), ans, is_multi))
    if cur_run:
        runs.append((cur_header, cur_run))
    return runs


def is_closed_header(h):
    hl = (h or '').lower()
    return 'câu hỏi' in hl or 'củng cố' in hl


def find_book(prefix):
    """Grades 11-12 split SGK into 'định hướng' (track) editions; SGV stays
    unified. Prefer the 'ứng dụng' (applied) track — the more common one —
    when a plain match isn't found."""
    exact = glob.glob(f'poc-out/graph/ocr-body/{prefix}')
    if exact:
        return prefix
    candidates = sorted(glob.glob(f'poc-out/graph/ocr-body/{prefix}-*'))
    applied = [c for c in candidates if 'ung-dung' in c]
    chosen = applied[0] if applied else (candidates[0] if candidates else None)
    return chosen.split('/')[-1] if chosen else None


def verify_grade(g):
    book_sgk = find_book(f'{g:02d}-sgk-tin-hoc-{g}')
    book_sgv = find_book(f'{g:02d}-sgv-tin-hoc-{g}')
    if not book_sgk or not book_sgv:
        return None
    sgk_pages = load_pages(book_sgk)
    sgv_pages = load_pages(book_sgv)
    sgk_ranges = {r['number']: r for r in sgk_lesson_ranges(sgk_pages)}
    sgv_ranges = {r['number']: r for r in sgv_lesson_ranges(sgv_pages)}

    results = []
    for num, sgv_r in sgv_ranges.items():
        answer_runs = sgv_answer_runs(sgv_pages, sgv_r['start_pdf'], sgv_r['end_pdf'])
        closed_runs = [(h, run) for h, run in answer_runs if is_closed_header(h)]
        if not closed_runs:
            continue
        header, run = closed_runs[0]
        k = len(run)
        has_multi = any(m for _, _, m in run)
        sgk_r = sgk_ranges.get(num)
        status = 'UNKNOWN'
        detail = ''
        if sgk_r is None:
            detail = 'no matching SGK lesson number in TOC'
        elif has_multi:
            status = 'EXCLUDED_MULTI_SELECT'
            detail = f'{sum(1 for _,_,m in run if m)}/{k} answers multi-select'
        else:
            mcq_runs = sgk_mcq_runs(sgk_pages, sgk_r['start_pdf'], sgk_r['end_pdf'])
            first_run = mcq_runs[0] if mcq_runs else []
            if len(first_run) == k:
                status = 'HIGH_CONFIDENCE_MATCH'
                detail = f'SGK first run={len(first_run)} items == SGV answers={k}'
            else:
                detail = f'SGK first run={len(first_run)} items != SGV answers={k} (SGK total runs={len(mcq_runs)}, sizes={[len(r) for r in mcq_runs]})'
        results.append(dict(lesson=num, sgv_header=header, answer_count=k,
                             status=status, detail=detail))
    return results


def main():
    grand_total = 0
    grand_match = 0
    for g in GRADES:
        results = verify_grade(g)
        print(f'\n=== Grade {g} ===')
        if results is None:
            print('  (book not found)')
            continue
        if not results:
            print('  no "Câu hỏi (hoạt động củng cố kiến thức)" answer runs found')
            continue
        for r in results:
            grand_total += 1
            if r['status'] == 'HIGH_CONFIDENCE_MATCH':
                grand_match += 1
            print(f"  lesson {r['lesson']:>3}  answers={r['answer_count']}  "
                  f"{r['status']:<24}  {r['detail']}")
    print(f'\n=== TOTAL: {grand_match}/{grand_total} lessons HIGH_CONFIDENCE_MATCH '
          f'(rest UNKNOWN/EXCLUDED — fail closed) ===')


if __name__ == '__main__':
    main()
