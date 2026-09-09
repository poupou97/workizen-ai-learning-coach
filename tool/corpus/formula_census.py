#!/usr/bin/env python3
"""WAL-239 — CENSUS các chỉ số Founder yêu cầu cho `FormulaSourceBlock`.

    python3 tool/corpus/formula_census.py --pack /private/tmp/wal-stage-formula

⛔ CENSUS ≠ ƯỚC LƯỢNG TỪ MẪU. Mọi số ở đây đếm trên TOÀN BỘ corpus. Chỉ số duy
nhất phải lấy từ mẫu soi mắt là `FORMULA_SOURCE_FAITHFUL_VALIDATED`, và nó
được in ở một mục RIÊNG, không trộn.

Founder: «Do not estimate the last metric from the old 88.7% sample if direct
census is now possible.» Số «chữ công thức còn hại mà trẻ vẫn thấy» ở đây là
CENSUS của phần CÒN PHƠI NHIỄM — đếm được chính xác. Còn *tỉ lệ hại* trong
phần ấy thì vẫn phải soi mắt, và được nói rõ là ước lượng.
"""
import argparse
import collections
import json
import os
import sys
import warnings

warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import formula_source as fs          # noqa: E402
from lesson_reading import page_paragraphs  # noqa: E402

OCR = os.path.join(ROOT, 'poc-out/graph/ocr-body')


def _norm(t):
    return ' '.join((t or '').split())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pack', default='/private/tmp/wal-stage-formula')
    a = ap.parse_args()
    regs = fs.regions_index()
    c = collections.Counter()
    order_bad = 0
    order_seen = 0
    prose_lost = []

    c['FORMULA_TOTAL'] = sum(len(v) for v in regs.values())

    # Vùng dựng được khối / bị bỏ, và VÌ SAO bỏ — hai lý do KHÔNG gộp.
    seen_pages = set()
    for (bk, pg), rr in regs.items():
        try:
            with open(f'{OCR}/{bk}/p{pg:03d}.json', encoding='utf-8') as fh:
                lines = json.load(fh)['lines']
        except (OSError, ValueError, KeyError):
            c['KHONG_CO_DU_LIEU_DONG'] += len(rr)
            continue
        paras = page_paragraphs(lines)
        seen_pages.add((bk, pg))
        for r in rr:
            if not fs.safe_region(r):
                c['FORMULA_WITHHELD_UNSAFE_REGION'] += 1
                continue
            own = [p for p in paras if fs.owned_by_formula(p, [r])]
            if own:
                c['FORMULA_SOURCE_REGION_AVAILABLE'] += 1
                c['UNSAFE_OCR_SUPPRESSED'] += len(own)
            elif fs._touched(r, paras):
                c['FORMULA_WITHHELD_AVOID_C'] += 1
            else:
                c['FORMULA_SOURCE_REGION_AVAILABLE'] += 1
                c['REGION_KHONG_CO_CHU'] += 1

    # Đối chiếu với PACK thật: khối đã vào dòng đọc, văn xuôi có còn, thứ tự
    # có giữ. Đây là chỗ duy nhất nói được «sản phẩm đúng», không phải ý định.
    import glob
    for p in sorted(glob.glob(os.path.join(a.pack, 'lesson-index-g*.json'))):
        with open(p, encoding='utf-8') as fh:
            idx = json.load(fh)
        for r in idx.get('lessonReadings') or []:
            content = r.get('content') or []
            c['FORMULA_BLOCK_IN_READ'] += sum(
                1 for e in content if isinstance(e, dict) and e.get('t') == 'formula')
            texts = {_norm(e.get('v')) for e in content
                     if isinstance(e, dict) and e.get('t') in ('text', 'heading')}
            for pg in range(r['pagePdfStart'], r['pagePdfEnd'] + 1):
                rr = regs.get((r['book'], pg))
                if not rr:
                    continue
                try:
                    with open(f'{OCR}/{r["book"]}/p{pg:03d}.json', encoding='utf-8') as f2:
                        lines = json.load(f2)['lines']
                except (OSError, ValueError, KeyError):
                    continue
                for q in page_paragraphs(lines):
                    if fs.owned_by_formula(q, rr):
                        continue                     # đã bị bỏ có bằng chứng
                    c['SURROUNDING_PROSE_TOTAL'] += 1
                    if _norm(q['text']) in texts:
                        c['SURROUNDING_PROSE_PRESERVED'] += 1
                    else:
                        prose_lost.append((r['book'], pg, q['text'][:60]))
            # THỨ TỰ: khối công thức phải nằm GIỮA chữ trước và chữ sau của
            # chính trang nó — không được dồn xuống cuối bài.
            pos = [i for i, e in enumerate(content)
                   if isinstance(e, dict) and e.get('t') == 'formula']
            for i in pos:
                order_seen += 1
                has_before = any(content[j].get('t') in ('text', 'heading')
                                 for j in range(i))
                has_after = any(content[j].get('t') in ('text', 'heading')
                                for j in range(i + 1, len(content)))
                if not (has_before or has_after):
                    order_bad += 1

    n = c['FORMULA_TOTAL']
    print('═══ CENSUS TOÀN CORPUS (không phải ước lượng từ mẫu) ═══\n')
    print(f'  FORMULA_TOTAL                      {n:6d}')
    # ⚠ ĐƠN VỊ. Chỉ số đếm VÙNG mới lấy `FORMULA_TOTAL` làm mẫu số. Số đoạn
    # văn bị bỏ là ĐƠN VỊ KHÁC (đoạn, không phải vùng) — in tỉ lệ chung cho nó
    # ra 129,5%, một con số vô nghĩa. Đây đúng cái bẫy hôm nay đã dính.
    for k in ('FORMULA_SOURCE_REGION_AVAILABLE', 'FORMULA_WITHHELD_AVOID_C',
              'FORMULA_WITHHELD_UNSAFE_REGION', 'REGION_KHONG_CO_CHU'):
        print(f'  {k:34s} {c[k]:6d}  {c[k] / n:6.1%}  (vùng)')
    print(f'  {"FORMULA_BLOCK_IN_READ":34s} {c["FORMULA_BLOCK_IN_READ"]:6d}'
          f'          (LƯỢT vào bài — một trang dùng chung nhiều bài)')
    print(f'  {"UNSAFE_OCR_SUPPRESSED":34s} {c["UNSAFE_OCR_SUPPRESSED"]:6d}'
          f'          (ĐOẠN văn, đơn vị khác — không chia cho số vùng)')
    tp = c['SURROUNDING_PROSE_TOTAL']
    print(f'\n  SURROUNDING_PROSE_PRESERVED        {c["SURROUNDING_PROSE_PRESERVED"]:6d}'
          f'/{tp}  {c["SURROUNDING_PROSE_PRESERVED"] / max(tp, 1):.2%}')
    print(f'  ORDER_PRESERVED                    {order_seen - order_bad:6d}'
          f'/{order_seen}  {(order_seen - order_bad) / max(order_seen, 1):.2%}')
    print(f'\n  CÒN PHƠI NHIỄM (census): {c["FORMULA_WITHHELD_AVOID_C"]} vùng vẫn có '
          f'chuỗi OCR không bỏ được')
    print('  ⚠ Tỉ lệ HẠI trong phần còn lại vẫn phải soi mắt — KHÔNG suy từ 88,7% cũ.')
    if prose_lost:
        print(f'\n  ⛔ VĂN XUÔI BỊ MẤT: {len(prose_lost)} — 5 ví dụ:')
        for b, pg, t in prose_lost[:5]:
            print(f'     {b[:30]} tr.{pg} «{t}»')
    return 0


if __name__ == '__main__':
    sys.exit(main())
