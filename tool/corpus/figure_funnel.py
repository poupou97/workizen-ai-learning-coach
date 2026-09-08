#!/usr/bin/env python3
"""PHỄU DÒ HÌNH — hình của sách chết ở CHẶNG NÀO.

Sách tự in «Hình N.M» ⇒ trang ấy CHẮC CHẮN có hình. Đó là giám sát yếu, lấy
từ chính nguồn, không cần gán nhãn tay hàng nghìn trang. Nhưng:

    CHÚ THÍCH CHỨNG MINH HÌNH TỒN TẠI, KHÔNG CHO BIẾT BIÊN CỦA HÌNH.

Nên ở đây chỉ dùng chú thích làm MỎ NEO để soi vùng lân cận, và phân loại chỗ
chết theo chặng:

    NOT_VISIBLE          không có mực nào trong vùng lân cận
    COMPONENT_NONE       có mực mà không thành phần liên thông nào sống sót
    FRAGMENTED           nhiều mảnh, không mảnh nào đủ lớn, nhưng HỢP của chúng
                         thì đủ — thiếu bước GOM VÙNG
    REGION_TOO_SMALL     mảnh có, hợp cũng nhỏ — hình thật sự bé
    DECORATIVE           đúng một vùng, rơi vào dải «trang trí»
    ACCEPTED             có vùng đạt ngưỡng nội dung

⚠ KHÔNG chỉnh ngưỡng ở đây. Đây là dụng cụ ĐO.
"""
import re

CAPTION_NUM = re.compile(r'^\s*(hình|bảng|sơ\s*đồ|biểu\s*đồ)\s*(\d{1,2})\s*[.,]\s*(\d{1,2})',
                         re.IGNORECASE)
# ⭐ SÁCH CÒN ĐÁNH SỐ MỘT CẤP: «Hình 2», «Hình 10», «Bảng 3» (đánh số theo bài,
# không theo chương). Census trên 72 đề xuất bị giữ: 3 ca là chú thích ĐÁNH SỐ
# thật mà mẫu hai-cấp bỏ lọt (LS&ĐL 7 «Hình 2. Cột kinh Phật…», Lịch sử 10
# «Hình 10», «Hình 11»). Vẫn là BẰNG CHỨNG ĐÁNH SỐ IN TRONG SÁCH — nới mẫu
# nhận, KHÔNG hạ chuẩn bằng chứng.
CAPTION_NUM_ANY = re.compile(
    r'^\s*(hình|bảng|sơ\s*đồ|biểu\s*đồ)\s*(\d{1,2})(?:\s*[.,]\s*(\d{1,2}))?(?![\d])',
    re.IGNORECASE)
# ⭐ CHÚ THÍCH CÓ DẤU NGUỒN: dòng ngắn kết bằng chỉ số nguồn «⁽⁴⁾» — OCR ra
# «Thêu(4)», «Nhuộm3)», «In lưới?)». Đây là CẤU TRÚC IN của sách (nối ảnh với
# danh sách nguồn cuối trang), không phải chữ tình cờ nằm dưới ảnh.
# Census: 13 ca ở Mĩ thuật 10 (hai cuốn khác nhau).
#
# ⚠ PHẢI MỞ ĐẦU BẰNG CHỮ CÁI — CHÚ THÍCH LÀ MỘT CÁI TÊN, KHÔNG PHẢI MỘT HÌNH DẠNG.
# Bản đầu chỉ bắt hình dạng «…số)» nên nhận cả Ô ĐẦU CỘT của bảng số liệu:
# «[160; 165)». Đã tạo ra một TRUSTED SAI thật ở Toán 11 trang 67 — vùng được
# tin là con mascot trang trí trong hộp ghi chú, còn «bằng chứng» là một ô
# khoảng giá trị của bảng bên dưới. Sách KHÔNG hề nói bức ấy tên là gì.
# Riêng luật này loại 13 dòng không phải chú thích trên 63 trang đã đo (khoảng
# giá trị, một trích dẫn nguồn trong ngoặc, một mẩu mã «,maxsplit=2)») mà vẫn
# giữ đủ 15 chú thích thật.
CAPTION_FOOTNOTE = re.compile(r'^(?![\d\W])\S.{1,59}[\(\?\"“”]?\s*\d\s*\)\s*$')
BAND_UP = 0.35        # soi tối đa ngần này chiều cao trang phía trên chú thích
BAND_PAD = 0.02


def caption_anchors(lines, *, extended=False, block_lines=None):
    """Dòng chú thích IN TRONG SÁCH, kèm hình học của chính dòng ấy.

    `extended=False` giữ đúng hành vi cũ (chỉ số hai cấp «Hình 5.1») — dùng cho
    mọi phép đo đã công bố, để số cũ không đổi nghĩa.

    `extended=True` nhận thêm HAI HỌ BẰNG CHỨNG IN, không hạ chuẩn:
      · đánh số MỘT CẤP («Hình 2», «Bảng 3»);
      · chú thích kết bằng CHỈ SỐ NGUỒN («Thêu⁽⁴⁾»).

    ⚠ Cả hai chỉ nhận khi dòng nằm trong KHỐI NGẮN (≤2 dòng). Một câu thân bài
    mở đầu bằng «Hình 5.1 là đồ thị…» là THAM CHIẾU, không phải chú thích —
    census cho thấy khác biệt nằm ở chỗ nó nằm trong đoạn văn nhiều dòng.
    `block_lines` = `{id(dòng): số dòng của khối}`.
    """
    out = []
    for l in lines:
        t = (l.get('text') or '').strip()
        m = CAPTION_NUM.match(t)
        fam = 'NUMBERED'
        if not m and extended:
            short = (block_lines or {}).get(id(l), 1) <= 2
            if short:
                m = CAPTION_NUM_ANY.match(t)
                if not m and CAPTION_FOOTNOTE.match(t):
                    out.append(dict(kind='hình', num=None, family='FOOTNOTE',
                                    x=l['x'], y=l['y'], w=l.get('w') or 0,
                                    h=l.get('h') or 0, text=t))
                    continue
        if not m:
            continue
        num = f'{m.group(2)}.{m.group(3)}' if m.lastindex and m.group(3) else m.group(2)
        out.append(dict(kind=m.group(1).lower().replace(' ', ''), num=num, family=fam,
                        x=l['x'], y=l['y'], w=l.get('w') or 0, h=l.get('h') or 0,
                        text=t))
    return out


def block_line_counts(lines):
    """`{id(dòng): số dòng của khối chứa nó}` — để biết dòng có đứng riêng không."""
    from lesson_reading import blocks, is_furniture
    out = {}
    for b in blocks(lines):
        k = [l for l in b if not is_furniture(l) and (l.get('text') or '').strip()]
        for l in k:
            out[id(l)] = len(k)
    return out


def neighborhood(anchor, anchors, page_h=1.0, prose=()):
    """Dải NGHI CÓ HÌNH: từ ngay trên chú thích ngược lên, dừng ở thứ gần nhất
    phía trên — chú thích khác (hình của người ta) hoặc KHỐI THÂN BÀI.

    ⭐ Chặn trên bằng KHỐI THÂN BÀI là điều kiện then chốt. Không có nó, dải
    cao tới `BAND_UP` và hợp các mảnh mực trong dải trườn qua cả đoạn văn phía
    trên: đo được 18/108 vùng gom chồng hơn 30% diện tích lên khối thân bài —
    tức là đưa cho trẻ ẢNH CHỤP đoạn chữ mà nó vừa đọc.

    Hình không kéo dài lên trên đoạn văn đứng trước nó. Ranh giới ấy là cấu
    trúc của chính trang, không phải một con số.

    `prose` = các hộp `(x0, y0, x1, y1)` của khối chữ thân bài.
    """
    top = max(0.0, anchor['y'] - BAND_UP)
    ax0, ax1 = anchor['x'], anchor['x'] + anchor['w']
    for a in anchors:
        if a is anchor:
            continue
        ay = a['y'] + a['h']
        if ay <= anchor['y'] and ay > top:
            top = ay
    for px0, py0, px1, py1 in prose:
        if py1 > anchor['y']:
            continue                      # khối nằm dưới chú thích
        if min(ax1, px1) - max(ax0, px0) <= 0:
            continue                      # không cùng cột với chú thích
        if py1 > top:
            top = py1
    return (top, max(top, anchor['y'] - 0.001))


def prose_boxes(lines, min_lines=3):
    """Hộp của các khối THÂN BÀI (từ `min_lines` dòng trở lên)."""
    from lesson_reading import blocks, is_furniture
    out = []
    for b in blocks(lines):
        k = [l for l in b if not is_furniture(l) and (l.get('text') or '').strip()]
        if len(k) < min_lines:
            continue
        out.append((min(l['x'] for l in k), min(l['y'] for l in k),
                    max(l['x'] + (l.get('w') or 0) for l in k),
                    max(l['y'] + (l.get('h') or 0) for l in k)))
    return out


def unproven_text_boxes(lines, regions):
    """Hộp của MỌI khối chữ CHƯA CHỨNG MINH ĐƯỢC là chữ của hình.

    ⭐ ĐÂY LÀ PHƯƠNG ÁN D — GIỮ LẠI KHI KHÔNG CHỨNG MINH ĐƯỢC QUYỀN SỞ HỮU.

    Bộ kiểm gán tay (#160, 77 khối) cho thấy: với hình học dòng OCR + thành phần
    mực, KHÔNG luật nào vừa nhận đủ chữ-của-hình vừa không nuốt văn xuôi. Tín
    hiệu SẠCH duy nhất là «khối nằm trong hộp của một thành phần mực đã dò» —
    chính xác 100% nhưng chỉ phủ 11%.

    Nên ranh giới nới hình dừng ở MỌI khối chữ, trừ:
      · khối chứng minh được là chữ của hình (nằm trong mực đã dò);
      · dòng chú thích (nó là mỏ neo, không phải rào).

    Trước đây chỉ chặn ở khối ≥3 dòng, nên khung phụ 2 dòng lọt qua và hợp
    trườn ngang qua câu chữ trẻ đang đọc — đúng ca đã nhìn tận mắt ở Toán 11
    trang 87 (mascot + hai dòng thân bài + hình tứ diện trong một tấm).

    «Thiếu hình» sửa được ở vòng sau; «hình nuốt mất câu» thì trẻ đọc phải ngay.
    """
    from lesson_reading import blocks, is_furniture
    caps = {a['text'] for a in caption_anchors(lines)}
    out = []
    for b in blocks(lines):
        k = [l for l in b if not is_furniture(l) and (l.get('text') or '').strip()]
        if not k:
            continue
        if any((l.get('text') or '').strip() in caps for l in k):
            continue
        x0 = min(l['x'] for l in k)
        y0 = min(l['y'] for l in k)
        x1 = max(l['x'] + (l.get('w') or 0) for l in k)
        y1 = max(l['y'] + (l.get('h') or 0) for l in k)
        area = max((x1 - x0) * (y1 - y0), 1e-9)
        proven = False
        for r in regions:
            rx, ry, rw, rh = r['bbox']
            ix = min(x1, rx + rw) - max(x0, rx)
            iy = min(y1, ry + rh) - max(y0, ry)
            if ix > 0 and iy > 0 and ix * iy >= 0.6 * area:
                proven = True
                break
        if not proven:
            out.append((x0, y0, x1, y1))
    return out


def in_band(bbox, band, x_span=None):
    y0, y1 = band
    bx, by, bw, bh = bbox
    if by + bh < y0 - BAND_PAD or by > y1 + BAND_PAD:
        return False
    if x_span is not None:
        ix = min(bx + bw, x_span[1]) - max(bx, x_span[0])
        if ix <= 0:
            return False
    return True


def union_area(boxes):
    if not boxes:
        return 0.0
    x0 = min(b[0] for b in boxes)
    y0 = min(b[1] for b in boxes)
    x1 = max(b[0] + b[2] for b in boxes)
    y1 = max(b[1] + b[3] for b in boxes)
    return (x1 - x0) * (y1 - y0)


def classify_failure(*, ink_px, raw, kept, content_min):
    """Chặng chết cho MỘT mỏ neo. `raw`/`kept` là list bbox."""
    if ink_px == 0:
        return 'NOT_VISIBLE'
    if not raw:
        return 'COMPONENT_NONE'
    if any(b[2] * b[3] >= content_min for b in kept):
        return 'ACCEPTED'
    if not kept:
        return 'COMPONENT_NONE'
    if len(kept) >= 2 and union_area(kept) >= content_min:
        return 'FRAGMENTED'
    if len(kept) == 1:
        return 'DECORATIVE'
    return 'REGION_TOO_SMALL'
