#!/usr/bin/env python3
"""ĐO ẢNH TRÙNG CÙNG-NGUỒN trong pack — cùng trang, cùng chú thích in, hai bản.

    python3 tool/corpus/pack_duplicates.py [thư-mục-pack]

Nợ sản phẩm đo được hôm 2026-09-09: 937 cặp trên 856 trang. Trẻ mở bài ra thấy
CÙNG MỘT hình hai lần, một bản do D cắt (có thể hỏng), một bản do Docling.

Sinh ra vì B3 gộp thêm theo HÌNH HỌC: hai bản của một hình mà hộp lệch nhau
(IoU ≤ 0,5) thì không bị coi là trùng, nên cả hai cùng vào pack.

⚠ MỘT ĐƯỜNG SINH SỐ DUY NHẤT cho cả «trước» và «sau». Đo trước bằng tay rồi đo
sau bằng script khác là cách chắc chắn nhất để hai con số không so được với nhau.
"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def _norm(t):
    return ' '.join((t or '').split()).strip().lower()


def count(pack_dir):
    """`(số cặp trùng, số trang dính, số hình D, số hình Docling)`."""
    dup = 0
    pages = set()
    n_d = n_dl = 0
    seen = set()
    for g in range(1, 13):
        p = os.path.join(pack_dir, f'lesson-index-g{g}.json')
        if not os.path.exists(p):
            continue
        with open(p, encoding='utf-8') as fh:
            idx = json.load(fh)
        for r in idx.get('lessonReadings') or []:
            by = collections.defaultdict(list)
            for e in r.get('content') or []:
                if not (isinstance(e, dict) and e.get('t') == 'img'):
                    continue
                if e['id'] in seen:
                    continue
                seen.add(e['id'])
                src = 'dl' if ':dl' in e['id'] else 'd'
                n_dl += src == 'dl'
                n_d += src == 'd'
                by[(r['book'], e['page'], _norm(e.get('caption')))].append(src)
            for (bk, pg, cap), v in by.items():
                if cap and 'd' in v and 'dl' in v:
                    dup += min(v.count('d'), v.count('dl'))
                    pages.add((bk, pg))
    return dup, len(pages), n_d, n_dl


def main():
    d = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'assets', 'pack')
    dup, pg, n_d, n_dl = count(d)
    print(f'{d}')
    print(f'  hình D                 : {n_d}')
    print(f'  hình Docling           : {n_dl}')
    print(f'  CẶP TRÙNG CÙNG-NGUỒN   : {dup}  trên {pg} trang')
    return 0


if __name__ == '__main__':
    sys.exit(main())
