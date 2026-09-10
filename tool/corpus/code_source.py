#!/usr/bin/env python3
"""WAL-239 — MÃ NGUỒN GIỮ NGUYÊN DÒNG, dựng từ hình học trang.

⛔ RANH GIỚI, Founder chốt:

    HÌNH HỌC ĐƯỢC PHÉP DỰNG LẠI CẤU TRÚC.
    HÌNH HỌC KHÔNG ĐƯỢC PHÉP BỊA RA NỘI DUNG.

⭐ VÌ SAO PHẢI SỞ HỮU THEO **DÒNG**, KHÔNG PHẢI THEO ĐOẠN

Công thức sở hữu theo ĐOẠN được (`formula_source.owned_by_formula`) vì một
đoạn công thức đứng riêng. Mã nguồn thì KHÔNG: `blocks()` gom dòng theo cột,
mà thụt lề của mã tạo ra bước nhảy x, nên một chương trình bị XÉ ra nhiều khối
rồi mỗi mảnh bị HÀN vào văn xuôi quanh nó. Census toàn corpus trên 334 vùng có
dấu vết chương trình in:

    bị xé thành nhiều khối        201   60,2%
    hàn với chữ NGOÀI vùng        294   88,0%   (tới 14 khối cho một chương trình)

Đoạn nào cũng chỉ có 0,9%–39,7% diện tích nằm trong vùng mã, nên MỌI ngưỡng
sở hữu theo đoạn đều trượt. Đơn vị đúng là DÒNG OCR: dòng có tâm nằm trong
vùng thì thuộc vùng ấy.

⚠ ĐÂY CŨNG LÀ CHỖ MỘT PHÉP ĐO ĐÃ ĐÁNH LỪA TÔI. Bản audit hôm 2026-09-09 kết
luận «mất nội dung, chỉ còn số dòng» cho 8/16 ca. Sai. Truy lại từng chặng:
21/21 dòng mã của bốn ca họ B ĐỀU tới pack. Cái mất là ở PHÉP ĐO —
`stem_exposure` chỉ đếm đoạn phủ ≥60% vào vùng, mà cột số dòng thì hẹp nên phủ
100%, còn dòng mã thật thì đã bị hàn vào văn xuôi rộng cả trang nên rớt ngưỡng.
Cột số dòng sống sót trong PHÉP ĐO, không phải trong SẢN PHẨM.

⛔ PHẠM VI HẸP CÓ CHỦ Ý. Chỉ đụng vùng nhãn `code` CÓ dấu vết chương trình in
(`code_poc.PY_MARK`). 541/875 vùng còn lại phần lớn là lời giải Toán — giữ
nguyên đường cũ, không đổi gì. Founder: «fixing code MUST NOT globally preserve
arbitrary OCR newlines in normal prose.»
"""
import collections
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from code_poc import PY_MARK, reconstruct  # noqa: E402

#: Một bậc thụt lề in ra bằng chừng này dấu cách. Chỉ là cách VIẾT LẠI bậc đã
#: đo được, không phải suy ra số dấu cách của bản gốc.
INDENT = '    '

#: Ít hơn chừng này dòng thì không có CẤU TRÚC nào để giữ — trả về None và để
#: nguyên đường cũ. Fail closed.
MIN_ROWS = 2

_INDEX = None


def _wh(box):
    """GÓC `[x0,y0,x1,y1]` → `[x,y,w,h]`.

    ⚠ HAI QUY ƯỚC HỘP CÙNG TỒN TẠI trong repo: đề xuất Docling dùng GÓC,
    `trusted.jsonl` dùng `[x,y,w,h]`. Đọc nhầm một lần đã làm kích thước vùng
    công thức thành 29,9% trang thay vì 0,91%.
    """
    return [box[0], box[1], box[2] - box[0], box[3] - box[1]]


def regions_index(path=None):
    """`(sách, trang) → [vùng mã]`, CHỈ vùng có dấu vết chương trình in."""
    global _INDEX
    if _INDEX is not None and path is None:
        return _INDEX
    out = collections.defaultdict(list)
    pat = path or os.path.join(ROOT, 'poc-out/docling/proposals-w*.jsonl')
    for p in sorted(glob.glob(pat)):
        with open(p, encoding='utf-8') as fh:
            for ln in fh:
                try:
                    r = json.loads(ln)
                except ValueError:
                    continue
                for it in r.get('items') or []:
                    if it.get('label') != 'code':
                        continue
                    t = ' '.join((it.get('text') or '').split())
                    if not PY_MARK.search(t):
                        continue
                    out[(r['book'], r['page'])].append(_wh(it['box']))
    if path is None:
        _INDEX = out
    return out


def _centre_in(line, box):
    cx = line['x'] + (line.get('w') or 0) / 2
    cy = line['y'] + (line.get('h') or 0) / 2
    return (box[0] <= cx <= box[0] + box[2]) and (box[1] <= cy <= box[1] + box[3])


def owned_lines(lines, regions):
    """Chia dòng OCR: dòng nào thuộc vùng mã nào, dòng nào không thuộc vùng nào.

    Trả `(ngoài, [(vùng, các dòng trong vùng), …])`. Một dòng chỉ thuộc ĐÚNG
    MỘT vùng — vùng đầu tiên ôm tâm nó — nên không có chuyện chữ hiện hai lần.
    """
    taken, groups = set(), []
    for box in regions or ():
        got = [l for l in lines
               if id(l) not in taken and (l.get('text') or '').strip()
               and _centre_in(l, box)]
        for l in got:
            taken.add(id(l))
        groups.append((box, got))
    outside = [l for l in lines if id(l) not in taken]
    return outside, groups


def _gutter_merged(rows):
    """Số dòng bị OCR gộp VÀO CHÍNH dòng mã ⇒ x mất nghĩa, thụt lề KHÔNG đo được.

    Khác hẳn ca `code_poc._gutter` xử lý được: ở đó số dòng là một mẩu chữ
    RIÊNG nên bỏ ra là xong. Ở đây «1 def reverseorder (T,k):» là một dòng OCR
    duy nhất, mọi dòng đều bắt đầu ở mốc x của cột số, nên mọi bậc thụt lề đo
    ra đều bằng nhau và bằng 0. Nhận ra thì KHÔNG dựng thụt lề nữa —
    `UNKNOWN != VALID`, và đoán thụt lề Python là đổi chương trình.
    """
    if len(rows) < 3:
        return False
    return all(re.match(r'^\d{1,3}\s+\S', (r.get('text') or '').strip()) for r in rows)



#: Khe giữa hai mẩu chữ CÙNG MỘT DÒNG rộng gấp chừng này bề ngang một ký tự
#: của chính dòng ấy thì không còn là khoảng cách giữa hai từ nữa.
KHE_TU = 4.0


def _rows(lines, tol=0.004):
    """Gom mẩu chữ thành DÒNG IN theo y — cùng phép gom `reconstruct` dùng."""
    ls = sorted([l for l in lines if (l.get('text') or '').strip()],
                key=lambda l: (round(l['y'], 4), l['x']))
    if not ls:
        return []
    rows, cur = [], [ls[0]]
    for l in ls[1:]:
        if abs(l['y'] - cur[-1]['y']) <= tol:
            cur.append(l)
        else:
            rows.append(cur); cur = [l]
    rows.append(cur)
    return rows


def two_column(lines):
    """Khung có nuốt CỘT THỨ HAI không — trang mã kèm cột chú giải bên phải.

    ⚠ LỖI NÀY DO CHÍNH BẢN VÁ SINH RA, không có ở đường cũ. Trước kia dòng mã
    nằm lẫn trong đoạn văn nên chẳng ai ghép chúng lại; giờ `reconstruct` gom
    theo y, nên chú giải bên phải bị HÀN vào câu lệnh:

        «if k ›= len (T): Bước 2. Thực hiện thao tác»

    Với Python đó là một chương trình KHÁC. Docling không cứu được — chính nó
    khoanh khung `code` trải hết bề ngang trang (x 0,145–0,897) ở ca này.

    Nhận bằng SỰ LẶP LẠI, không bằng một con số bề rộng: một dòng mã có thể
    căn lề thưa một lần, nhưng CỘT thì để lại khe ở NHIỀU dòng tại CÙNG một
    chỗ. Đòi hai dòng trở lên có khe rộng chồng nhau theo x.
    """
    gaps = []
    for r in _rows(lines):
        r = sorted(r, key=lambda l: l['x'])
        # ⚠ BỎ CỘT SỐ DÒNG RA TRƯỚC. Chính nó cũng để lại một khe rộng lặp ở
        # cùng một chỗ trên mọi dòng — đo được: chốt này bắt nhầm 50,9% số
        # vùng, gần như toàn bộ là sách in kèm số dòng.
        if len(r) > 1 and re.fullmatch(r'\d{1,3}', (r[0].get('text') or '').strip()):
            r = r[1:]
        if len(r) < 2:
            continue
        ch = [(l.get('w') or 0) / max(len((l.get('text') or '').strip()), 1) for l in r]
        ch = sorted(c for c in ch if c > 0)
        if not ch:
            continue
        avg = ch[len(ch) // 2]
        for a, b in zip(r, r[1:]):
            khe = b['x'] - (a['x'] + (a.get('w') or 0))
            if khe > KHE_TU * avg:
                gaps.append((a['x'] + (a.get('w') or 0), b['x']))
    for i, g in enumerate(gaps):
        for h in gaps[i + 1:]:
            if min(g[1], h[1]) - max(g[0], h[0]) > 0:
                return True
    return False

def code_text(lines_in, box):
    """Chuỗi mã GIỮ NGUYÊN DÒNG, hoặc `None` khi không có gì để giữ.

    Trả `(text, ghi_chú)`. Nội dung KHÔNG bị đụng vào: chỉ ranh giới dòng, thứ
    tự dòng và bậc thụt lề là dựng từ hình học.
    """
    if two_column(lines_in):
        # Fail closed: thà giữ đường cũ còn hơn giao một chương trình đã bị
        # chú giải hàn vào giữa câu lệnh.
        return None, 'HAI_COT'
    rows, why = reconstruct(lines_in, box)
    if len(rows) < MIN_ROWS:
        return None, 'QUA_IT_DONG'
    if _gutter_merged(rows):
        # Fail closed: giữ DÒNG và NỘI DUNG, bỏ thụt lề vì không đo được.
        return '\n'.join(r['text'] for r in rows), 'THUT_LE_KHONG_DO_DUOC'
    # SỐ DÒNG IN của sách được in lại đúng như sách, canh phải theo số rộng
    # nhất — sách canh cột, và trẻ cần đọc được «dòng 3» khi bài tập nhắc tới.
    w = max((len(r.get('num') or '') for r in rows), default=0)
    return '\n'.join(((r['num'] or '').rjust(w) + ' ' if w else '')
                     + INDENT * r['indent'] + r['text'] for r in rows), why


def code_paragraph(lines_in, box, seq, drop=frozenset()):
    """Một ĐOẠN cho dòng đọc, mang cả chương trình, đúng chỗ nó đứng trong bài."""
    keep = [l for l in lines_in
            if (l.get('text') or '').strip() and (l.get('text') or '').strip() not in drop]
    if not keep:
        return None
    text, why = code_text(keep, box)
    if text is None:
        return None
    xs = [l['x'] for l in keep]
    ys = [l['y'] for l in keep]
    return dict(y=round(min(ys), 4), seq=seq, kind='code', note=why,
                box=[round(min(xs), 4), round(min(ys), 4),
                     round(max(l['x'] + (l.get('w') or 0) for l in keep), 4),
                     round(max(l['y'] + (l.get('h') or 0) for l in keep), 4)],
                text=text)
