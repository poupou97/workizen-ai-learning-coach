#!/usr/bin/env python3
"""B3 — CỔNG TIN CẬY CHẠY TRÊN KHU TẠM, SINH VÙNG ĐÁNG TIN CHO CORPUS.

    python3 tool/corpus/docling_gate.py            # đọc poc-out/docling/*.jsonl

Bước RẺ, chạy lại được: đọc đề xuất thô đã lưu, áp cổng bằng chứng in, tách
`REGION_TRUST` khỏi `IDENTITY_LINK`, ghi ra `trusted.jsonl` + bản kiểm đếm.

KHÔNG bước nào ở đây ghi vào `assets/pack`. Đưa vào pack là việc của
`build_lesson_figures.py`, và chỉ nhận vùng đạt CẢ HAI phép đo.
"""
import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
OUT = os.path.join(ROOT, 'poc-out', 'docling')

from lesson_reading import page_lines                      # noqa: E402
import figure_funnel as ff                                 # noqa: E402
import docling_trust as dt                                 # noqa: E402
import docling_identity as di                              # noqa: E402

PICT, TABL = 'picture', 'table'


def proposals(out_dir=OUT):
    """Mỗi trang một bản ghi, gộp từ mọi shard. Trang trùng lấy bản đầu."""
    seen = {}
    if not os.path.isdir(out_dir):
        return seen
    for fn in sorted(os.listdir(out_dir)):
        if not (fn.startswith('proposals-w') and fn.endswith('.jsonl')):
            continue
        with open(os.path.join(out_dir, fn), encoding='utf-8') as fh:
            for line in fh:
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                seen.setdefault((d['book'], d['page']), d)
    return seen


def judge_page(rec, lines):
    """Đề xuất của MỘT trang → danh sách bản ghi đã chấm cả hai phép đo."""
    items = rec.get('items') or []
    bl = ff.block_line_counts(lines)
    anchors = ff.caption_anchors(lines, extended=True, block_lines=bl)
    subs = di.sublabels(lines, block_lines=bl)

    staged = []
    for it in items:
        lab = it.get('label')
        if lab not in (PICT, TABL):
            continue
        b = it['box']
        bbox = (b[0], b[1], b[2] - b[0], b[3] - b[1])
        kind = 'table' if lab == TABL else 'picture'
        st, why, cap = dt.judge(bbox, anchors=anchors, items=items, kind=kind)
        staged.append([bbox, kind, st, why, cap])

    # ⭐ MỘT CHÚ THÍCH ĐANG ĐƯỢC MẤY VÙNG VIỆN DẪN — đây chính là dấu hiệu cụm
    # hình con. Phải đếm SAU khi chấm cả trang, không đếm được khi xét lẻ.
    cited = collections.Counter(id(c) for _, _, s, _, c in staged
                                if s == 'TRUSTED' and c is not None)

    out = []
    for bbox, kind, st, why, cap in staged:
        shared = cited.get(id(cap), 0) if cap is not None else 0
        if st == 'TRUSTED':
            ist, ident, iwhy = di.link(bbox, caption=cap, shared=shared, subs=subs)
        else:
            ist, ident, iwhy = di.WITHHELD, None, 'vùng chưa đáng tin'
        out.append(dict(book=rec['book'], page=rec['page'], kind=kind,
                        box=[round(v, 4) for v in bbox],
                        region_trust=st, region_why=why,
                        identity=ist, identity_why=iwhy, ident=ident,
                        shared=shared,
                        readable=di.readable(st, ist, shared=shared)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(OUT, 'trusted.jsonl'))
    a = ap.parse_args()

    props = proposals()
    cnt = collections.Counter()
    band = lambda g: '1-3' if g <= 3 else ('4-8' if g <= 8 else '9-12')   # noqa: E731
    reg = json.load(open(os.path.join(ROOT, 'poc-out', 'registry',
                                      'source-registry.json'), encoding='utf-8'))
    docs = reg['documents'] if isinstance(reg, dict) else reg
    GRADE = {d['sourceDocumentId']: d.get('grade') or 0 for d in docs}

    n_pages = 0
    with open(a.out, 'w', encoding='utf-8') as fh:
        for (book, pp), rec in sorted(props.items()):
            n_pages += 1
            if rec.get('error'):
                cnt['TRANG_LOI'] += 1
                continue
            lines = page_lines(book, pp)
            if lines is None:
                cnt['TRANG_KHONG_OCR'] += 1
                continue
            g = GRADE.get(book, 0)
            for r in judge_page(rec, lines):
                cnt['DE_XUAT'] += 1
                cnt[f'REGION_{r["region_trust"]}'] += 1
                if r['region_trust'] == 'TRUSTED':
                    cnt[f'IDENTITY_{r["identity"]}'] += 1
                    cnt[f'BAND_{band(g)}'] += 1
                    if r['kind'] == 'table':
                        cnt['TABLE_TRUSTED'] += 1
                if r['readable']:
                    cnt['VAO_DONG_DOC'] += 1
                r['grade'] = g
                fh.write(json.dumps(r, ensure_ascii=False) + '\n')
    cnt['TRANG'] = n_pages
    print(json.dumps(dict(sorted(cnt.items())), ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
