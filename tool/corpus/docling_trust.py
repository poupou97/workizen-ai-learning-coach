#!/usr/bin/env python3
"""CỔNG TIN CẬY cho ĐỀ XUẤT của Docling (B2, chế độ bóng).

Kiến trúc: `SOURCE → đề xuất tri giác → CỔNG TIN CẬY → bằng chứng nguồn →
vùng đáng tin → pack → sản phẩm`. Docling nói CHỖ NÀO; sách nói ĐÓ LÀ HÌNH GÌ.
Model KHÔNG có quyền tự xác lập sự thật SGK.

⛔ KHÔNG tái dùng nguyên cổng của D. Đo được trên bộ 34 trang: đem hai cổng
của D áp thẳng lên hộp Docling thì chặn 6/9 hộp có hại nhưng chặn NHẦM 30/93
hộp lành — vì hộp Docling ĐÚNG thì đương nhiên chứa chữ (ô bảng, nhãn sơ đồ,
lời bài hát). Biểu diễn khác đòi phép kiểm khác.

⭐ CHỮ NẰM TRONG VÙNG KHÔNG PHẢI LÀ LẪN CHỮ. Ô bảng, nhãn trục, nhãn sơ đồ,
lời bài hát, chữ trong infographic đều là chữ CỦA hình.

── VÌ SAO CỔNG NÀY DỰA VÀO CHÚ THÍCH ───────────────────────────────────

Chấm 95 hộp ảnh trên 34 trang (5 hộp đã chấm bằng mắt là CÓ HẠI):

    tín hiệu                     bắt được hại   giữ nhầm lành
    chú thích in kề bên              5/5             84/90
    hộp chứa phần tử Docling khác    1/5              0/90
    tỉ lệ chữ phủ trong hộp          0/5   (không tách được: hộp lành lên tới 0,92)

Chỉ BẰNG CHỨNG IN TRONG SÁCH tách được. Nên cổng này AN TOÀN mà YẾU: nó chỉ
tin ~7% đề xuất, vì phần lớn hình SGK không có chú thích đánh số. Đó là con số
phải báo, không phải con số để giấu.

Ba trạng thái, không ép nhị phân:

    TRUSTED    có chú thích in kề bên, không mâu thuẫn
    CONFLICT   ôm chú thích của NHIỀU hình, hoặc chứa phần tử cấu trúc khác
    WITHHELD   không đủ bằng chứng — giữ lại, dùng nội dung D an toàn sẵn có
"""
CAPTION_GAP = 0.06        # chú thích in ngay trên hoặc ngay dưới vùng
INSIDE_FRAC = 0.70


def _overlap(a0, a1, b0, b1):
    return min(a1, b1) - max(a0, b0)


def adjacent_captions(bbox, anchors, gap=CAPTION_GAP):
    """Chú thích in NGAY KỀ vùng (trên hoặc dưới) và chồng ngang với nó."""
    x, y, w, h = bbox
    out = []
    for a in anchors:
        below = a['y'] - (y + h)
        above = y - (a['y'] + a['h'])
        d = below if -0.01 <= below <= gap else (above if -0.01 <= above <= gap else None)
        if d is None:
            continue
        if _overlap(x, x + w, a['x'], a['x'] + a['w']) <= 0:
            continue
        out.append((d, a))
    return [a for _, a in sorted(out, key=lambda z: z[0])]


def contained_captions(bbox, anchors):
    """Chú thích nằm HẲN TRONG vùng — dấu hiệu vùng ôm cả hình của người khác."""
    x, y, w, h = bbox
    out = []
    for a in anchors:
        cy = a['y'] + a['h'] / 2
        if y <= cy <= y + h and _overlap(x, x + w, a['x'], a['x'] + a['w']) > 0:
            out.append(a)
    return out


SELF_IOU = 0.8            # trùng chừng này thì đó là CHÍNH đề xuất đang xét


def _iou(a, b):
    ix = _overlap(a[0], a[2], b[0], b[2])
    iy = _overlap(a[1], a[3], b[1], b[3])
    if ix <= 0 or iy <= 0:
        return 0.0
    inter = ix * iy
    ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / max(ua, 1e-9)


def contains_item(bbox, items, frac=INSIDE_FRAC):
    """Phần tử cấu trúc KHÁC của Docling nằm trong vùng ⇒ đây là một mảng
    trang, không phải một hình.

    ⚠ Phải loại CHÍNH NÓ ra. Không loại thì mọi hộp bảng đều «chứa» item bảng
    của chính mình và bị gán CONFLICT — đo được: 7/7 bảng bị chặn oan.
    """
    x, y, w, h = bbox
    me = (x, y, x + w, y + h)
    n = 0
    for it in items:
        b = it['box']
        if _iou(me, b) >= SELF_IOU:
            continue
        ix = _overlap(x, x + w, b[0], b[2])
        iy = _overlap(y, y + h, b[1], b[3])
        if ix <= 0 or iy <= 0:
            continue
        area = max((b[2] - b[0]) * (b[3] - b[1]), 1e-9)
        if ix * iy >= frac * area:
            n += 1
    return n


def judge(bbox, *, anchors, items=(), kind='picture'):
    """`(trạng thái, lý do, chú thích)` cho MỘT đề xuất."""
    if bbox[2] <= 0 or bbox[3] <= 0:
        return 'WITHHELD', 'hộp rỗng', None
    inside = contained_captions(bbox, anchors)
    if len(inside) > 1:
        return 'CONFLICT', f'ôm {len(inside)} chú thích của nhiều hình', None
    if contains_item(bbox, items):
        return 'CONFLICT', 'chứa phần tử cấu trúc khác ⇒ mảng trang', None
    adj = adjacent_captions(bbox, anchors)
    if adj:
        return 'TRUSTED', f'sách in chú thích kề bên: {adj[0]["kind"]} {adj[0]["num"]}', adj[0]
    if inside:
        return 'TRUSTED', f'sách in chú thích trong vùng: {inside[0]["num"]}', inside[0]
    return 'WITHHELD', 'không có bằng chứng in trong sách', None
