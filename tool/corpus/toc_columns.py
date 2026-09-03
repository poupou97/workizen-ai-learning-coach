#!/usr/bin/env python3
"""Đọc mục lục HAI CỘT cho đúng — thử nghiệm, chưa nối vào pipeline.

Vì sao: `parse_structure.py` v2 có phát hiện cột, nhưng hai chỗ đóng cứng làm nó
gộp nhầm hai cột thành một ở nhiều cuốn:

  1. `detect_columns(gap=0.25)` — hai cột cách nhau 0.1 (thân trái x≈0.4 →
     thân phải x≈0.5) thì bị gộp làm MỘT.
  2. cột số trang lấy theo `x > 0.80` — đúng với mục lục MỘT cột, nhưng ở mục
     lục hai cột thì số trang của cột TRÁI nằm giữa trang (x≈0.5), nên bị coi
     là chữ thân bài.

Hậu quả đo được ở `05-sgk-khoa-hoc-5`: «Bài 1» nhận trang 64 của «Bài 17» ở cột
phải ⇒ hai dãy đơn điệu chồng nhau, 56% đầu cuốn sách không bài nào phủ (C-008).

Cách ở đây: KHÔNG đoán trước vị trí. Tìm các cụm x của DÒNG TOÀN CHỮ SỐ — mỗi
cụm là một cột số trang, và mỗi cột số trang định ra một DẢI: chữ bên trái nó
(tới cột số trang trước đó) thuộc về dải ấy. Đọc từng dải trên→dưới.

Chạy: python3 tool/corpus/toc_columns.py poc-out/graph/ocr/05/05-sgk-khoa-hoc-5/p005.json
"""
import json
import re
import sys
import unicodedata

# ⭐ GIỮ LẠI TỪ KHOÁ đã khớp. Gộp «Chủ đề 1» vào cùng rổ với «Bài 1» là lý do
# còn 6 số trùng ở Khoa học 5: chủ đề và bài đánh số ĐỘC LẬP nhau. Corpus đã có
# sẵn chiều `unitKind` cho đúng việc này.
UNIT = re.compile(
    r'(B[àa]i|Chuy[êe]n đ[êề]|Chủ đ[êề]|Tu[âầ]n|Unit)\s*(\d+)\s*[.．:]?\s*(.*)',
    re.I)

_KIND = {'bai': 'bai', 'chude': 'chuDe', 'chuyende': 'chuyenDe',
         'tuan': 'tuan', 'unit': 'unit'}


def unit_kind(word):
    # Bỏ dấu bằng NFD rồi loại dấu kết hợp; `đ` KHÔNG phải `d` có dấu nên phải
    # thay riêng — thiếu dòng này thì «Chủ đề» rơi nhầm vào rổ «Bài».
    k = unicodedata.normalize('NFD', word.lower())
    k = ''.join(c for c in k if not unicodedata.combining(c))
    k = ''.join(c for c in k.replace('đ', 'd') if c.isalpha())
    for pref, kind in _KIND.items():
        if k.startswith(pref[:4]):
            return kind
    return 'bai'


def cluster(values, gap):
    """Gom giá trị thành cụm khi khoảng cách vượt `gap`."""
    if not values:
        return []
    vals = sorted(values)
    out, cur = [], [vals[0]]
    for a, b in zip(vals, vals[1:]):
        if b - a > gap:
            out.append(cur)
            cur = [b]
        else:
            cur.append(b)
    out.append(cur)
    return out


def page_number_columns(lines, gap=0.08):
    """Cột SỐ TRANG = cụm x của các dòng chỉ gồm chữ số (1–3 chữ số)."""
    xs = [l['x'] for l in lines
          if l['text'].strip().isdigit() and len(l['text'].strip()) <= 3]
    return [sum(c) / len(c) for c in cluster(xs, gap) if len(c) >= 2]


def parse(path, y_tol=0.013):
    lines = json.load(open(path))['lines']
    pcols = page_number_columns(lines)
    if not pcols:
        # Mục lục KHÔNG in số trang (có thật: nhiều SGV, sách Âm nhạc/Mĩ thuật).
        # Vẫn đọc được số bài + tên bài theo thứ tự đọc — trả về ít thông tin
        # hơn, nhưng KHÔNG được trả về rỗng: rỗng là mất bài, tệ hơn thiếu trang.
        pcols = [1.0]

    # Mỗi cột số trang định ra một dải: (trái của cột trước, cột này].
    bands, left = [], 0.0
    for px in pcols:
        bands.append((left, px))
        left = px
    entries = []
    for lo, hi in bands:
        body = sorted([l for l in lines if lo <= l['x'] < hi - 0.01],
                      key=lambda l: l['y'])
        for l in body:
            m = UNIT.match(l['text'].strip())
            if not m:
                continue
            # số trang của dòng này: dòng toàn số, cùng hàng y, ở ĐÚNG cột của dải
            same = [q for q in lines
                    if abs(q['y'] - l['y']) < y_tol
                    and q['text'].strip().isdigit()
                    and abs(q['x'] - hi) < 0.06]
            entries.append({'unitKind': unit_kind(m.group(1)),
                            'number': int(m.group(2)),
                            'title': (m.group(3) or '').strip() or None,
                            'pageStart': int(same[0]['text']) if same else None})
    return entries, pcols


# ---------------------------------------------------------------------------
# HỌ MỤC LỤC THỨ HAI: BẢNG có dòng tiêu đề cột
#
# Tiếng Việt 3/4/5 KHÔNG viết «Bài 1. …» mà kẻ bảng:
#     Tuần | Bài | Nội dung              | Trang
#          |     | NHỮNG TRẢI NGHIỆM…    |   9
#       1  |  1  | Đọc: Ngày gặp lại     |  10
#          |     | Nói và nghe: Mùa hè…  |  11
# Số bài là CHỮ SỐ TRẦN nằm trong cột riêng; chữ «Bài» chỉ xuất hiện MỘT lần ở
# dòng tiêu đề. Regex đòi từ khoá sẽ ra 0 mục — đúng 33 cuốn tụt hạng khi đo.
#
# Đây cũng là chỗ lộ ra PHÂN CẤP THẬT mà Founder yêu cầu giữ:
# Sách → Tuần → Bài. Số bài LẶP LẠI qua từng tuần, nên số bài một mình không
# bao giờ đủ làm định danh (khớp WAL-170).
_HEADERS = {'tuan': 'tuan', 'bai': 'bai', 'noidung': 'noiDung', 'trang': 'trang'}


def _slug(t):
    k = unicodedata.normalize('NFD', t.strip().lower())
    k = ''.join(c for c in k if not unicodedata.combining(c))
    return ''.join(c for c in k.replace('đ', 'd') if c.isalpha())


def header_row(lines, y_tol=0.02):
    """Tìm dòng tiêu đề cột. Trả về {tên cột: x}, rỗng nếu không phải bảng."""
    cands = [l for l in lines if _slug(l['text']) in _HEADERS]
    if len(cands) < 3:
        return {}
    # nhóm theo y — tiêu đề cột nằm cùng một hàng
    cands.sort(key=lambda l: l['y'])
    best = {}
    for anchor in cands:
        row = {_HEADERS[_slug(l['text'])]: l['x'] for l in cands
               if abs(l['y'] - anchor['y']) < y_tol}
        if len(row) > len(best):
            best = row
    return best if {'bai', 'trang'} <= set(best) else {}


def parse_table(path, y_tol=0.02):
    """Đọc mục lục dạng BẢNG. Giữ cả `Tuần` làm phân cấp trên bài."""
    lines = json.load(open(path))['lines']
    hdr = header_row(lines)
    if not hdr:
        return []
    x_bai, x_trang = hdr['bai'], hdr['trang']
    x_tuan = hdr.get('tuan')
    x_noi = hdr.get('noiDung', (x_bai + x_trang) / 2)
    body = sorted(lines, key=lambda l: l['y'])

    def digits_near(x, tol=0.06):
        return [l for l in body if l['text'].strip().isdigit()
                and len(l['text'].strip()) <= 3 and abs(l['x'] - x) < tol]

    out, week = [], None
    for l in body:
        if x_tuan is not None and l in digits_near(x_tuan, 0.05):
            week = int(l['text'])
            continue
        if l not in digits_near(x_bai, 0.05):
            continue
        n = int(l['text'])
        # Tiêu đề cột «Nội dung» được canh GIỮA cột, còn chữ thì canh TRÁI —
        # lấy theo x của tiêu đề sẽ trượt hết. Nhận mọi dòng chữ nằm giữa cột
        # số bài và cột số trang.
        # ⭐ Một «Bài» Tiếng Việt là KHỐI NHIỀU HOẠT ĐỘNG (Đọc / Nói và nghe /
        # Viết) — cột nội dung liệt kê từng hoạt động, không phải một tên bài.
        # Lấy dòng TRÊN CÙNG của khối làm tên; các dòng còn lại là hoạt động
        # bên trong, cần mô hình riêng (ghi ở Living Research).
        block = [q for q in body
                 if abs(q['y'] - l['y']) < y_tol * 1.5
                 and x_bai + 0.02 < q['x'] < x_trang - 0.02
                 and not q['text'].strip().isdigit()]
        block.sort(key=lambda q: q['y'])
        title = block[0]['text'].strip() if block else None
        page = next((int(q['text']) for q in digits_near(x_trang)
                     if abs(q['y'] - l['y']) < y_tol), None)
        out.append({'unitKind': 'bai', 'number': n, 'title': title,
                    'pageStart': page, 'week': week})
    return out


def lesson_unit_kind(entries):
    """Đơn vị BÀI của một cuốn là loại nào?

    Sách phổ thông không dùng chung một quy ước: Khoa học 5 có cả «Chủ đề» (mục
    lớn) lẫn «Bài» (đơn vị học) ⇒ bài là `bai`. Nhưng Âm nhạc 3 KHÔNG có «Bài»
    nào — «Chủ đề N» chính là đơn vị học. Lọc cứng lấy `bai` sẽ xoá sạch mục lục
    của những cuốn ấy (đo được: 0/8 bài còn lại ở `03-sgk-am-nhac-3`).

    Luật: có `bai` thì `bai` là bài (các loại khác thành mục lớn); không có thì
    lấy loại xuất hiện nhiều nhất.
    """
    kinds = [e['unitKind'] for e in entries]
    if not kinds:
        return 'bai'
    if 'bai' in kinds:
        return 'bai'
    return max(set(kinds), key=kinds.count)


def lessons_of(entries):
    kind = lesson_unit_kind(entries)
    return [e for e in entries if e['unitKind'] == kind]


def parse_any(path):
    """Bảng trước, danh sách sau. Hai HỌ mục lục, một đường vào."""
    t = parse_table(path)
    if t:
        return t, ['bảng']
    return parse(path)


def main():
    path = sys.argv[1]
    entries, pcols = parse_any(path)
    print('bố cục: ' + (', '.join(pcols) if pcols and isinstance(pcols[0], str)
                        else f'cột số trang {[round(p, 2) for p in pcols]}'))
    print(f'{len(entries)} mục:')
    for e in entries:
        print(f"  {e['unitKind']:9s} {e['number']:3d} · trang "
              f"{str(e['pageStart']):>4} · {(e['title'] or '')[:40]}")
    lessons = lessons_of(entries)
    paged = [e for e in lessons if e['pageStart']]
    mono = all(paged[i]['pageStart'] <= paged[i + 1]['pageStart']
               for i in range(len(paged) - 1))
    nums = [e['number'] for e in lessons]
    print(f"\nBÀI: {len(lessons)} · đơn điệu theo thứ tự đọc: "
          f"{'CÓ' if mono else 'KHÔNG'} · số trùng: {len(nums) - len(set(nums))} · "
          f"có trang: {len(paged)}/{len(lessons)}")


if __name__ == '__main__':
    main()
