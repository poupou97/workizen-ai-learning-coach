#!/usr/bin/env python3
"""ĐO họ «vùng nuốt vật thể khác» trên TOÀN BỘ ứng cử thay chỗ.

    python3 tool/corpus/containment_census.py

Founder Gate: «Do NOT immediately invent a rule. Instrument … Measure this over
the full corpus.» Nên bước này CHỈ ĐẾM, chưa chặn gì.

Đo ngoài luồng dựng: chỉ cần hộp hình D, dòng chú thích in, và vùng đáng tin
của đúng những trang có ứng cử — không phải dựng lại cả pack.
"""
import collections
import json
import os
import sys
import warnings

warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import containment as ct          # noqa: E402
import figure_funnel as ff        # noqa: E402
from lesson_figures import lesson_figures  # noqa: E402

OCR = os.path.join(ROOT, 'poc-out/graph/ocr-body')
PAIRS = os.path.join(ROOT, 'poc-out/docling/selector-pairs-uniq.json')
TRUSTED = os.path.join(ROOT, 'poc-out/docling/trusted.jsonl')


def pdf_path(book):
    for p in (f'{ROOT}/poc-out/pdf/{book[:2]}/{book}.pdf',
              f'{ROOT}/poc-out/pdf/{book}.pdf'):
        if os.path.exists(p):
            return p
    return None


def lines_of(book, page):
    try:
        with open(f'{OCR}/{book}/p{page:03d}.json', encoding='utf-8') as fh:
            return json.load(fh)['lines']
    except (OSError, ValueError, KeyError):
        return []


def main():
    pairs = json.load(open(PAIRS, encoding='utf-8'))
    trusted = collections.defaultdict(list)
    with open(TRUSTED, encoding='utf-8') as fh:
        for line in fh:
            r = json.loads(line)
            if r.get('readable'):
                trusted[(r['book'], r['page'])].append(r)

    by_page = collections.defaultdict(list)
    for r in pairs:
        by_page[(r['book'], r['page'])].append(r)

    st = collections.Counter()
    hits = []
    pages = sorted(by_page)
    for i, (book, page) in enumerate(pages):
        if i % 200 == 0:
            print(f'  {i}/{len(pages)} trang…', flush=True)
        lines = lines_of(book, page)
        bl = ff.block_line_counts(lines) if lines else {}
        anchors = ff.caption_anchors(lines, extended=True, block_lines=bl) if lines else []
        pdf = pdf_path(book)
        try:
            figs = lesson_figures(pdf, book, [page], {page: lines}) if pdf else []
        except Exception:                      # một trang hỏng không giết cả lượt
            figs = []
        for r in by_page[(book, page)]:
            st['CANDIDATE_SUPERSEDES'] += 1
            lab, why = ct.swallowed(
                r['dl_bbox'], r.get('caption'), r['d_bbox'],
                anchors=anchors, d_figs=figs, trusted=trusted[(book, page)],
                have_lines=bool(lines))
            st[lab or 'CLEAN'] += 1
            if lab:
                hits.append(dict(book=book, page=page, label=lab, why=why,
                                 caption=r.get('caption'),
                                 d_bbox=r['d_bbox'], dl_bbox=r['dl_bbox']))
    print()
    for k in ('CANDIDATE_SUPERSEDES', 'CLEAN', 'CONTAINS_SEPARATE_CAPTION',
              'CONTAINS_OTHER_NAMED_VISUAL', 'CONTAINS_OTHER_TRUSTED_REGION',
              'AMBIGUOUS_CONTAINMENT'):
        n = st.get(k, 0)
        pct = f'{n / max(st["CANDIDATE_SUPERSEDES"], 1):6.1%}'
        print(f'  {k:32s} {n:5d}  {pct}')
    out = os.path.join(ROOT, 'poc-out/docling/containment-hits.json')
    json.dump(hits, open(out, 'w'), ensure_ascii=False, indent=1)
    print(f'\n{len(hits)} ca → {out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
