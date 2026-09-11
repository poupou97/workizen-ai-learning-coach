#!/usr/bin/env python3
"""CENSUS DANH TÍNH HÌNH & BẢNG — một đường sinh duy nhất, tái hiện được.

    python3 tool/corpus/figure_identity_census.py [--kind hinh|bang|all] [--csv OUT]

⛔ VÌ SAO CÓ TỆP NÀY. WAL-232 ghi «5.041 hình của chính bài · 1.854 tham chiếu
chéo · khớp 1.017 = 20,2%» — nhưng **cách đo không được ghi lại đủ để chạy
lại**. Hệ quả: sau khi sửa đường dựng, KHÔNG AI biết con số ấy đã nhúc nhích
hay chưa. Một chỉ số cấp Founder mà chỉ tồn tại dưới dạng phần trăm cuối cùng
là một chỉ số đã chết.

Nên ở đây MỌI định nghĩa đều viết ra, và mọi tổng đều kiểm chứng lại được từ
dòng lá.

═══ ĐỊNH NGHĨA (viết ra để tranh luận được) ═══

NGUỒN
    · `assets/pack/lesson-index-g*.json`  — thứ TRẺ NHẬN ĐƯỢC
    · `poc-out/graph/ocr-body/<sách>/pNNN.json` — chữ IN của từng trang

ĐƠN VỊ ĐẾM
    MỘT CẶP `(bài, danh tính)`. Danh tính = «Hình 5.2» / «Bảng 21.3» chuẩn hoá
    thành `5.2`. ⚠ ĐƠN VỊ LÀ THỰC THỂ DUY NHẤT, KHÔNG PHẢI LƯỢT NHẮC: sách
    nhắc «Hình 5.2» ba lần trong một bài vẫn là MỘT hình.

MẪU SỐ  `NAMED_OWN`
    Danh tính mà bài GỌI TÊN trong chữ của chính nó, VÀ chú thích của nó được
    IN TRÊN CHÍNH DẢI TRANG của bài ấy.

LOẠI TRỪ  `NAMED_CROSS`
    Bài có gọi tên, nhưng chú thích in ở TRANG NGOÀI dải bài — tức bài đang
    nhắc tới hình của bài khác. Không tính vào mẫu số: bài này không có nghĩa
    vụ giao hình của bài khác.

    ⚠ ĐÂY LÀ CHỖ PHÉP ĐO CŨ VÀ MỚI KHÁC NHAU. Bản này quyết định «của chính
    bài» bằng BẰNG CHỨNG VỊ TRÍ (chú thích in ở đâu). Nếu đo bằng cách đoán
    theo tiền tố chương thì ra con số khác hẳn — đã thử: 127 so với 1.854.

    `NAMED_NO_CAPTION` = gọi tên mà KHÔNG tìm thấy chú thích in ở đâu cả
    (trong bài lẫn ngoài bài). Tách riêng, không gộp vào chéo.

PHÂN LOẠI
    `kind` lấy từ CHÍNH TỪ IN: hình · bảng · sơ đồ · biểu đồ. Không suy từ
    hình dạng vùng.

KHỚP DANH TÍNH  `IDENTITY_MATCHED`
    Trong dòng đọc của bài có một khối `img` mà CHÚ THÍCH của nó mang đúng
    danh tính ấy. `TEXT MENTION != FIGURE IDENTITY` — khớp qua chú thích, tuyệt
    đối không so số lượng.

ĐỘ TIN CẬY KHÁC NHAU THEO CÁCH ĐÁNH SỐ — phải tách, không gộp:

    HAI CẤP «Hình 12.7»  danh tính DUY NHẤT trong cuốn ⇒ phép đo VỮNG
    MỘT CẤP «Hình 2»     mỗi bài đánh số lại từ đầu ⇒ KHÔNG duy nhất trong
                         cuốn. Khớp trong phạm vi MỘT bài vẫn đúng, nhưng
                         phân loại «tham chiếu chéo» thì MƠ HỒ: một bài gọi
                         «Hình 3» mà trang của nó không dò ra chú thích sẽ bị
                         xếp nhầm thành chéo. Nên con số một cấp là CHẶN TRÊN
                         lạc quan nhẹ.

⚠ KHỚP DANH TÍNH **KHÔNG** CÓ NGHĨA LÀ DÙNG ĐƯỢC. Một cái bảng có thể tới
đúng tên mà quan hệ hàng–cột đã vỡ. Đừng đóng nợ cấu trúc bảng vì danh tính
đã khá lên.

ĐẦU RA
    Dòng lá mỗi `(bài, danh tính)` kèm trạng thái, để mọi tổng kiểm lại được.
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
from subject import subject  # noqa: E402

OCR = os.path.join(ROOT, 'poc-out/graph/ocr-body')
PACK = os.path.join(ROOT, 'assets/pack')

KINDS = {'hình': 'hinh', 'bảng': 'bang', 'sơ đồ': 'sodo', 'biểu đồ': 'bieudo'}

#: Danh tính ĐƯỢC GỌI TÊN trong chữ — hai cấp «Hình 5.2» hoặc một cấp «Hình 2».
NAMED = re.compile(
    r'\b(Hình|Bảng|Sơ\s*đồ|Biểu\s*đồ)\s*(\d{1,2}(?:\s*[.,]\s*\d{1,2})?)\b', re.I)
#: Chú thích IN — phải ĐỨNG ĐẦU DÒNG. Một câu «…xem Hình 5.2» không phải chú thích.
CAPTION = re.compile(
    r'^\s*(Hình|Bảng|Sơ\s*đồ|Biểu\s*đồ)\s*(\d{1,2}(?:\s*[.,]\s*\d{1,2})?)\b', re.I)


def norm_kind(w):
    return KINDS.get(re.sub(r'\s+', ' ', w.strip().lower()), 'khac')


def norm_num(n):
    return re.sub(r'\s*[.,]\s*', '.', n.strip())


def caption_home():
    """`(sách, kind, số) → {trang có chú thích ấy IN ĐẦU DÒNG}`.

    Đây là bằng chứng «hình này nằm ở đâu trong sách», độc lập với pack.
    """
    home = collections.defaultdict(set)
    for p in sorted(glob.glob(os.path.join(OCR, '*/p*.json'))):
        bk = p.split('/')[-2]
        pg = int(os.path.basename(p)[1:4])
        try:
            lines = json.load(open(p, encoding='utf-8'))['lines']
        except (OSError, ValueError, KeyError):
            continue
        for l in lines:
            m = CAPTION.match((l.get('text') or '').strip())
            if m:
                home[(bk, norm_kind(m.group(1)), norm_num(m.group(2)))].add(pg)
    return home


def rows(home, kinds):
    out = []
    for p in sorted(glob.glob(os.path.join(PACK, 'lesson-index-g*.json'))):
        grade = int(re.search(r'g(\d+)', p).group(1))
        for r in json.load(open(p, encoding='utf-8')).get('lessonReadings') or []:
            C = [e for e in (r.get('content') or []) if isinstance(e, dict)]
            txt = ' '.join(e.get('v') or '' for e in C
                           if e.get('t') in ('text', 'heading'))
            # danh tính GỌI TÊN — thực thể duy nhất, không đếm lượt nhắc
            named = {(norm_kind(a), norm_num(b)) for a, b in NAMED.findall(txt)}
            # danh tính GIAO ĐƯỢC — từ chú thích của khối ảnh trong dòng đọc
            got = set()
            for e in C:
                if e.get('t') == 'img' and e.get('caption'):
                    for a, b in NAMED.findall(e['caption']):
                        got.add((norm_kind(a), norm_num(b)))
            span = set(range(r['pagePdfStart'], r['pagePdfEnd'] + 1))
            for k, n in sorted(named):
                if kinds and k not in kinds:
                    continue
                pages = home.get((r['book'], k, n)) or set()
                if not pages:
                    status = 'NAMED_NO_CAPTION'
                elif pages & span:
                    status = 'MATCHED' if (k, n) in got else 'OWN_MISSING'
                else:
                    status = 'NAMED_CROSS'
                out.append(dict(grade=grade, book=r['book'], lesson=r['lesson'],
                                subject=subject(r['book']), kind=k, num=n,
                                status=status,
                                caption_pages=','.join(map(str, sorted(pages)))[:40],
                                span=f"{r['pagePdfStart']}-{r['pagePdfEnd']}"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--kind', default='all', choices=('hinh', 'bang', 'all'))
    ap.add_argument('--csv', default=None, help='ghi dòng lá ra đây để kiểm chéo')
    a = ap.parse_args()
    kinds = None if a.kind == 'all' else {a.kind}
    home = caption_home()
    rs = rows(home, kinds)
    for r in rs:
        r['scheme'] = 'hai_cap' if '.' in r['num'] else 'mot_cap'
    c = collections.Counter(r['status'] for r in rs)
    own = c['MATCHED'] + c['OWN_MISSING']
    print(f'══ CENSUS DANH TÍNH — kind={a.kind} · {len(rs)} cặp (bài, danh tính)\n')
    print(f'  NAMED_OWN  (mẫu số)        {own:6d}')
    print(f'  ├ IDENTITY_MATCHED         {c["MATCHED"]:6d}  {c["MATCHED"]/max(own,1):6.1%}')
    print(f'  └ OWN_MISSING              {c["OWN_MISSING"]:6d}  {c["OWN_MISSING"]/max(own,1):6.1%}')
    print(f'  NAMED_CROSS (loại trừ)     {c["NAMED_CROSS"]:6d}')
    print(f'  NAMED_NO_CAPTION (loại)    {c["NAMED_NO_CAPTION"]:6d}')
    print('\n  TÁCH THEO CÁCH ĐÁNH SỐ (độ tin cậy khác nhau):')
    for sch, lab in (('hai_cap', 'HAI CẤP «Hình 12.7» — danh tính duy nhất, VỮNG'),
                     ('mot_cap', 'MỘT CẤP «Hình 2»   — chặn trên lạc quan nhẹ')):
        v = collections.Counter(r['status'] for r in rs if r['scheme'] == sch)
        o = v['MATCHED'] + v['OWN_MISSING']
        print(f'    {lab}')
        print(f'      own {o:6d} · khớp {v["MATCHED"]:6d} = {v["MATCHED"]/max(o,1):6.1%}'
              f' · chéo {v["NAMED_CROSS"]:4d} · không có chú thích {v["NAMED_NO_CAPTION"]:4d}')

    by = collections.defaultdict(collections.Counter)
    for r in rs:
        by[(r['kind'], r['subject'])][r['status']] += 1
    print(f'\n  {"kind":7s} {"môn":12s} {"khớp":>6s} {"/ own":>7s} {"":>8s}')
    agg = collections.defaultdict(collections.Counter)
    for (k, s), v in by.items():
        agg[k][s] = 0
    for (k, s), v in sorted(by.items(), key=lambda kv: -(kv[1]['MATCHED'] + kv[1]['OWN_MISSING'])):
        o = v['MATCHED'] + v['OWN_MISSING']
        if o < 30:
            continue
        print(f'  {k:7s} {s:12s} {v["MATCHED"]:6d} {o:7d} {v["MATCHED"]/max(o,1):8.1%}')
    if a.csv:
        with open(a.csv, 'w', newline='', encoding='utf-8') as fh:
            w = csv.DictWriter(fh, fieldnames=list(rs[0]))
            w.writeheader()
            w.writerows(rs)
        print(f'\n  dòng lá → {a.csv}  ({len(rs)} dòng)')
    print('\n⚠ KHỚP DANH TÍNH != DÙNG ĐƯỢC. Bảng có thể tới đúng tên mà quan hệ '
          'hàng–cột đã vỡ.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
