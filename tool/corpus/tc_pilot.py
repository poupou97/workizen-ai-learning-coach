#!/usr/bin/env python3
"""TC-v1 — BOUNDED PILOT: run the candidate winner (Docling+ocrmac) and the current
XY-cut on non-gold pages of a few books, then measure throughput and the cascade gate
pass rate at corpus scale (no gold here — this is the coverage side of the funnel).

Steps
  --make   write poc-out/trusted-corpus/<ver>/pilot/pages.json (books × page range)
  --analyse read bakeoff/raw/{docling-ocrmac,current-xycut,current-naive} for those pages,
           apply the docling>xycut agreement gate (tc_cascade.verify) and report:
           seconds/page (median, p90), pages with output, blocks total, trusted share,
           XY-cut page-trust share, and the old-vs-new text agreement.
Run the batches themselves with tc_bakeoff_run.py --batch (see chainPilot.sh in logs/).
"""
import argparse
import json
import os
import statistics
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tc_sdm  # noqa: E402
import tc_cascade  # noqa: E402

ROOT = tc_sdm.ROOT
BOOKS = [('07-sgk-khoa-hoc-tu-nhien-7', 10, 59), ('05-sgk-toan-5-tap-mot', 10, 59), ('09-sgk-ngu-van-9-tap-mot', 10, 59)]
import re  # noqa: E402
# same directive vocabulary the WAL-206 layout extractor uses to label learner questions
DIRECTIVE = re.compile(r'^\s*(\d{1,2}[.)]\s*)?(Em hãy|Hãy|Nêu|Cho biết|Giải thích|Vì sao|Tại sao|Quan sát|So sánh|Kể|Chọn|Tính|Viết|Đọc|Thảo luận|Trình bày|Mô tả|Xác định|Dự đoán|Kể tên|Liệt kê|Nhận xét|Phân loại|Sắp xếp|Điền|Nối|Tìm)\b', re.IGNORECASE)


def make(ver):
    d = f'{ROOT}/poc-out/trusted-corpus/{ver}/pilot'; os.makedirs(d, exist_ok=True)
    pages = [dict(book=b, page=p) for b, p0, p1 in BOOKS for p in range(p0, p1 + 1)]
    json.dump(pages, open(f'{d}/pages.json', 'w'))
    print(len(pages), 'pilot pages →', f'{d}/pages.json')


def analyse(ver):
    d = f'{ROOT}/poc-out/trusted-corpus/{ver}/pilot'
    pages = json.load(open(f'{d}/pages.json'))
    secs, rows = [], []
    per_book = Counter(); per_book_trusted = Counter(); per_book_blocks = Counter(); xy_trusted_pages = Counter(); pages_ran = Counter()
    gate = Counter()
    for p in pages:
        D = tc_sdm.load_sdm('docling-ocrmac', p['book'], p['page'], ver); X = tc_sdm.load_sdm('current-xycut', p['book'], p['page'], ver)
        if D is None or D.get('error') or X is None or X.get('error'):
            continue
        pages_ran[p['book']] += 1
        if D.get('seconds'):
            secs.append(D['seconds'])
        S = tc_cascade.verify(D, [X])
        blocks = [b for b in S['blocks'] if b['text'] and len(b['text']) >= 12]
        t = sum(1 for b in blocks if b['trusted'])
        per_book[p['book']] += 1; per_book_blocks[p['book']] += len(blocks); per_book_trusted[p['book']] += t
        gate.update(S['meta']['stats'])
        if X.get('meta', {}).get('page_trusted'):
            xy_trusted_pages[p['book']] += 1
        S2 = tc_cascade.math_guard(S)
        directive_new = sum(1 for b in S2['blocks'] if b['trusted'] and b['text'] and DIRECTIVE.search(b['text'][:120]))
        directive_old = sum(1 for b in X['blocks'] if b.get('trusted') and X.get('meta', {}).get('page_trusted') and b['text'] and DIRECTIVE.search(b['text'][:120]))
        rows.append(dict(book=p['book'], page=p['page'], seconds=D.get('seconds'), blocks=len(blocks), trusted=t, trusted_mathguard=sum(1 for b in S2['blocks'] if b['trusted'] and b['text'] and len(b['text']) >= 12),
                         directive_new=directive_new, directive_old=directive_old, xycut_page_trusted=X.get('meta', {}).get('page_trusted'),
                         xycut_blocks=len([b for b in X['blocks'] if b['text']]), xycut_trusted_blocks=sum(1 for b in X['blocks'] if b.get('trusted'))))
    out = dict(pages=len(rows), sec_median=statistics.median(secs) if secs else None, sec_p90=(sorted(secs)[int(0.9 * len(secs))] if secs else None), sec_mean=(sum(secs) / len(secs)) if secs else None,
               blocks=sum(per_book_blocks.values()), trusted=sum(per_book_trusted.values()), trusted_share=round(sum(per_book_trusted.values()) / max(1, sum(per_book_blocks.values())), 3),
               gate=dict(gate), per_book={b: dict(pages=per_book[b], blocks=per_book_blocks[b], trusted=per_book_trusted[b], trusted_share=round(per_book_trusted[b] / max(1, per_book_blocks[b]), 3), xycut_trusted_pages=xy_trusted_pages[b]) for b in per_book},
               trusted_mathguard=sum(r['trusted_mathguard'] for r in rows), directive_units_new=sum(r['directive_new'] for r in rows), directive_units_old=sum(r['directive_old'] for r in rows),
               xycut_trusted_pages=sum(xy_trusted_pages.values()), xycut_trusted_blocks=sum(r['xycut_trusted_blocks'] for r in rows), xycut_blocks=sum(r['xycut_blocks'] for r in rows), rows=rows)
    json.dump(out, open(f'{d}/pilot-result.json', 'w'), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != 'rows'}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--ver', default='tc-v1'); ap.add_argument('--make', action='store_true'); ap.add_argument('--analyse', action='store_true')
    a = ap.parse_args()
    if a.make: make(a.ver)
    if a.analyse: analyse(a.ver)
