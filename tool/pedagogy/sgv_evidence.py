#!/usr/bin/env python3
"""BẰNG CHỨNG SƯ PHẠM TỪ SGV — chỉ trên cặp SGK↔SGV đã CHỨNG MINH.

⛔ XUẤT HIỆN KHÔNG PHẢI LÀ SỞ HỮU. SGV có chữ «Đáp án» ở đâu đó KHÔNG có
nghĩa đáp án ấy thuộc bài đang xét; «MỤC TIÊU» in trên trang KHÔNG có nghĩa
mục tiêu ấy là của bài nếu sở hữu chưa chứng minh.

Nên module này CHỈ đọc trong DẢI TRANG của một cặp `CONFIDENT` (xem
`sgk_sgv_pairing`): từ trang tiêu đề bài tới trang tiêu đề bài kế tiếp trong
cùng cuốn SGV. Ngoài dải ⇒ không lấy.

⚠ HAI TRỤC TIN CẬY, KHÔNG PHẢI MỘT. Bản trước gắn `SOURCE_EXPLICIT` cho
13.634/13.634 finding — một rổ duy nhất thì không phải phân xử, chỉ là khẳng
định. Ở đây tách:

  A · SỰ THẬT NGUỒN   sách có NÓI THẲNG điều này không?
      SOURCE_EXPLICIT     có nhãn mục in ra («Đáp án và đánh giá», «MỤC TIÊU»)
      SOURCE_DEMONSTRATED sách THỂ HIỆN mà không gắn nhãn
      UNKNOWN             không đủ căn cứ

  B · SỰ THẬT SỞ HỮU  điều này thuộc đúng chỗ SAM định dùng không?
      LESSON_OWNED   nằm trong dải trang của bài đã ghép CONFIDENT
      TASK_LINKED    ngoài ra còn dẫn SỐ CÂU mà bài SGK cũng in ra
      (không có mức nào khác — thiếu thì không dùng)

⚠ HƯỚNG DẪN CHO GIÁO VIÊN KHÔNG PHẢI GỢI Ý CHO TRẺ. SGV viết cho người lớn
đứng lớp («GV tổ chức cho HS…»). Nên trường gợi ý ở đây luôn mang cờ
`audience=TEACHER`. Biến nó thành lời SAM nói với trẻ là việc CHƯA được phép.
"""
import argparse
import collections
import csv
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import sgk_sgv_pairing as P  # noqa: E402

PAIRS = os.path.join(ROOT, 'poc-out/pedagogy/sgk-sgv-pairs.csv')

#: Nhãn mục IN RA ⇒ trục A = SOURCE_EXPLICIT. Dò trên chữ đã bỏ dấu.
EXPLICIT = {
    'OBJECTIVE':  r'(muc tieu|yeu cau can dat|muc dich, yeu cau|muc dich yeu cau)',
    'ANSWER':     r'(dap an|goi y tra loi|goi y dap an|huong dan tra loi)',
    'ASSESSMENT': r'(danh gia|huong dan danh gia|kiem tra, danh gia)',
    'ACTIVITY':   r'(hoat dong|tien trinh|to chuc hoat dong|cac hoat dong day hoc)',
    'HINT':       r'(luu y|goi y|huong dan hs|gv goi y)',
    'MISCONCEPT': r'(sai lam|nham lan|hs thuong nham|de nham|luu y hs thuong)',
}
#: Dấu THỂ HIỆN mà không gắn nhãn ⇒ trục A = SOURCE_DEMONSTRATED.
DEMONSTRATED = {
    'ANSWER':     r'(^|\s)(cau\s*\d{1,2}\s*[.:)]|^\d{1,2}\s*[.)]\s)',
    'ASSESSMENT': r'\((b|h|vd|vd\s*\d)\)',
    'ACTIVITY':   r'(gv (cho|to chuc|huong dan|yeu cau) hs|hs (quan sat|thao luan|thuc hien))',
    'MISCONCEPT': r'(hs co the (nham|sai|lung tung)|chua phan biet duoc)',
}
#: Số câu mà SGV dẫn.
QNUM = re.compile(r'c[âa]u\s*(\d{1,2})', re.IGNORECASE)
#: Câu hỏi mà SGV IN RA NGUYÊN VĂN («Câu 1. Nêu tính chất của nước…»).
#: ⚠ Khớp SỐ không dùng được: SGK đánh số «N.» ở 97,0% bài nhưng chỉ 3,1% bài
#: dùng «Câu N», mà «N.» còn là số MỤC chứ không riêng câu hỏi. Nên sở hữu
#: mức VIỆC phải xét bằng CHỮ của chính câu hỏi, không bằng con số.
QTEXT = re.compile(r'c[âa]u\s*\d{1,2}\s*[.:)]\s*([^?]{10,140}\?)', re.IGNORECASE)
#: Câu hỏi của SGV phải trùng chừng này với chữ bài SGK mới coi là cùng một việc.
TASK_MIN = 0.5


def _fold(s):
    return P._fold(s)


def spans(csv_path=PAIRS):
    """Dải trang của từng cặp CONFIDENT — tới tiêu đề bài kế tiếp cùng cuốn."""
    rows = [r for r in csv.DictReader(open(csv_path, encoding='utf-8'))]
    byb = collections.defaultdict(list)
    for r in rows:
        byb[r['sgv']].append(r)
    out = []
    for sgv, rs in byb.items():
        rs.sort(key=lambda r: int(r['sgvPage']))
        for i, r in enumerate(rs):
            if r['status'] != 'CONFIDENT':
                continue
            start = int(r['sgvPage'])
            end = int(rs[i + 1]['sgvPage']) if i + 1 < len(rs) else start + 12
            out.append(dict(sgv=sgv, sgk=r['sgk'], lesson=int(r['lesson']),
                            start=start, end=max(end, start + 1)))
    return out


def page_text(sgv, a, b):
    out = []
    for p in P._pages(sgv):
        pg = int(os.path.basename(p)[1:-5])
        if a <= pg < b:
            out.append(' '.join(l.get('text', '') for l in P._page_lines(p)))
    return ' '.join(out)


def sgk_qnums(sgk_book, lesson, cache={}):
    """Số câu mà CHÍNH BÀI SGK in ra — để kiểm sở hữu mức TASK."""
    if not cache:
        for p in sorted(glob.glob(os.path.join(ROOT, 'assets/pack',
                                               'lesson-index-g*.json'))):
            for r in json.load(open(p, encoding='utf-8')).get('lessonReadings') or []:
                txt = ' '.join(e.get('v') or '' for e in (r.get('content') or [])
                               if isinstance(e, dict) and e.get('t') in ('text', 'heading'))
                cache[(r['book'], r['lesson'])] = {int(m) for m in QNUM.findall(txt)}
    return cache.get((sgk_book, lesson), set())


def sgk_words(sgk_book, lesson, cache={}):
    if not cache:
        for p in sorted(glob.glob(os.path.join(ROOT, 'assets/pack',
                                               'lesson-index-g*.json'))):
            for r in json.load(open(p, encoding='utf-8')).get('lessonReadings') or []:
                txt = ' '.join(e.get('v') or '' for e in (r.get('content') or [])
                               if isinstance(e, dict) and e.get('t') in ('text', 'heading'))
                cache[(r['book'], r['lesson'])] = P.toks(txt)
    return cache.get((sgk_book, lesson), set())


def task_linked(folded_span, span):
    """SGV có in NGUYÊN VĂN một câu hỏi mà chính bài SGK cũng in không?

    Đây là sở hữu mức VIỆC. «Đáp án thuộc bài» KHÔNG có nghĩa «đáp án thuộc
    việc trẻ đang làm» — muốn SAM đối chiếu câu trả lời thì phải chỉ ra được
    ĐÚNG câu hỏi ấy trong sách học sinh.
    """
    W = sgk_words(span['sgk'], span['lesson'])
    if not W:
        return False
    for q in QTEXT.findall(folded_span):
        qt = P.toks(q)
        if qt and len(qt & W) / len(qt) >= TASK_MIN:
            return True
    return False


def evidence(span):
    """Một bản ghi cho từng LOẠI bằng chứng tìm được trong dải bài."""
    t = _fold(page_text(span['sgv'], span['start'], span['end']))
    if not t:
        return []
    rows = []
    for field in ('OBJECTIVE', 'ANSWER', 'MISCONCEPT', 'HINT',
                  'ASSESSMENT', 'ACTIVITY'):
        exp = bool(re.search(EXPLICIT[field], t))
        dem = bool(re.search(DEMONSTRATED[field], t)) if field in DEMONSTRATED else False
        if exp:
            axis_a = 'SOURCE_EXPLICIT'
        elif dem:
            axis_a = 'SOURCE_DEMONSTRATED'
        else:
            axis_a = 'UNKNOWN'
        axis_b = 'LESSON_OWNED'
        if field == 'ANSWER' and axis_a != 'UNKNOWN':
            if task_linked(t, span):
                axis_b = 'TASK_LINKED'
        rows.append(dict(sgv=span['sgv'], sgk=span['sgk'], lesson=span['lesson'],
                         pages=f"{span['start']}-{span['end'] - 1}", field=field,
                         sourceTruth=axis_a, ownership=axis_b,
                         audience=('TEACHER' if field in ('HINT', 'ACTIVITY')
                                   else 'SOURCE')))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='poc-out/pedagogy/sgv-evidence.csv')
    a = ap.parse_args()
    sp = spans()
    print(f'{len(sp)} dải bài CONFIDENT', file=sys.stderr)
    rows = []
    for i, s in enumerate(sp):
        if i % 100 == 0:
            print(f'  {i}/{len(sp)}…', file=sys.stderr, flush=True)
        rows += evidence(s)
    out = os.path.join(ROOT, a.out)
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    n = len(sp)
    print(f'\nBẰNG CHỨNG SƯ PHẠM — mẫu số {n} bài đã ghép CONFIDENT\n')
    print(f"{'loại':12s} {'EXPLICIT':>9s} {'DEMONSTR':>9s} {'UNKNOWN':>8s}   {'có ≥1':>7s}")
    for field in ('OBJECTIVE', 'ANSWER', 'MISCONCEPT', 'HINT', 'ASSESSMENT', 'ACTIVITY'):
        c = collections.Counter(r['sourceTruth'] for r in rows if r['field'] == field)
        have = c['SOURCE_EXPLICIT'] + c['SOURCE_DEMONSTRATED']
        print(f"{field:12s} {c['SOURCE_EXPLICIT']:9d} {c['SOURCE_DEMONSTRATED']:9d} "
              f"{c['UNKNOWN']:8d}   {have / n:6.1%}")
    tl = sum(1 for r in rows if r['ownership'] == 'TASK_LINKED')
    print(f"\nĐÁP ÁN dẫn được tới SỐ CÂU mà bài SGK cũng in: {tl}/{n} ({tl / n:.1%})")
    print(f'leaf → {a.out}')


if __name__ == '__main__':
    main()
