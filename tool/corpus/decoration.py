#!/usr/bin/env python3
"""ĐỒ TRANG TRÍ CỦA TRANG — không phải hình học tập, không được đưa cho trẻ.

Mẫu ngẫu nhiên 120 hình soi bằng mắt (WAL-238) cho `FIGURE_CROP_VALID` = 70,8%.
Trong 35 ca hỏng, **17 ca là đồ trang trí của trang và CẢ 17 ĐỀU TỪ ĐƯỜNG D**:
dải sóng kèm số trang, dải màu mép trang, băng đầu bài, một tấm bìa sau sách.
Docling không sinh ca nào thuộc họ này.

Đây là họ hỏng RIÊNG — không phải cắt cụt, không phải lẫn chữ văn xuôi, mà
KHÔNG PHẢI HÌNH HỌC TẬP. Luật cũ của D («mảng mực đủ lớn») không phân biệt được
một dải trang trí với một bức ảnh.

── HAI BẰNG CHỨNG, PHẢI CÓ CẢ HAI ──────────────────────────────────────

1. LẶP LẠI TRONG CÙNG MỘT CUỐN. Đồ trang trí in lại trên hàng chục trang; một
   hình học tập thì không.
2. TỈ LỆ CỰC ĐOAN, CẢ HAI CHIỀU. Dải ngang đầu/cuối trang rất dẹt; dải dọc mép
   trang rất cao. Hình học tập nằm quanh tỉ lệ 1.

⭐ VÌ SAO PHẢI CÓ CẢ HAI, KHÔNG ĐƯỢC LẤY MỘT:

· Chỉ LẶP LẠI thì gỡ nhầm hình thật: sơ đồ sân tập trong sách GDTC lặp 8 trang
  vì bài nào cũng dùng lại sân ấy (ca #067 trong mẫu 120 — đã soi, HỢP LỆ).
· Chỉ TỈ LỆ DẸT thì gỡ nhầm KÝ ÂM: khuông nhạc rất dẹt. Đo được: luật hai vế
  gỡ 0/362 hình trong sách Âm nhạc.

⚠ «LẶP LẠI KHÔNG TỰ ĐỘNG LÀ TRANG TRÍ» — lời Founder, và số đo xác nhận.

── ĐO ĐƯỢC ─────────────────────────────────────────────────────────────

Trên 120 ca đã gán nhãn độc lập: bắt 10, cả 10 là trang trí, MẤT HÌNH THẬT 0.
Soi thêm 47 ca bị gỡ (24 ngẫu nhiên · 11 họ dải dọc · 12 đối kháng ở hai môn bị
gỡ nhiều nhất): 47/47 là trang trí, 0 ca mất hình thật.

Toàn corpus: gỡ 1.136/17.779 = 6,4%. Không đụng một hình Docling nào.

Cố ý KHÔNG đuổi theo 100%: 7/17 ca trang trí đã biết vẫn lọt (bìa sau, mảnh
nhoè, băng đầu bài lặp ít). Founder: «gỡ nhầm một hình thật tệ hơn để sót vài
đồ trang trí» ⇒ nghi ngờ thì GIỮ.
"""
import collections
import io

REP_MIN = 6          # lặp trên ít nhất ngần này TRANG PHÂN BIỆT của cùng cuốn
ASPECT_MIN = 3.0     # dẹt hoặc cao gấp ngần này
HASH_N = 12


def image_hash(jpeg, n=HASH_N):
    """Vân tay thô của ảnh — đủ để nhận ra CÙNG MỘT dải trang trí in lại."""
    from PIL import Image
    im = Image.open(io.BytesIO(jpeg)).convert('L').resize((n, n), Image.BILINEAR)
    px = list(im.getdata())
    avg = sum(px) / len(px)
    return int(''.join('1' if p > avg else '0' for p in px), 2)


def repeat_index(items):
    """`{(sách, vân tay): số TRANG PHÂN BIỆT}`.

    Đếm theo TRANG chứ không theo số bản ghi: một trang có hai bản của cùng một
    dải không chứng minh nó lặp qua nhiều trang.
    """
    pages = collections.defaultdict(set)
    for it in items:
        pages[(it['book'], it['hash'])].add(it['page'])
    return {k: len(v) for k, v in pages.items()}


def aspect(w, h):
    """Tỉ lệ dài/ngắn cho KÍCH THƯỚC ĐIỂM ẢNH (640×67…).

    ⚠ Chặn dưới ở 1 điểm ảnh — nên KHÔNG dùng được cho hộp bao chuẩn hoá 0–1:
    ở đó mọi cạnh đều < 1 và hàm này trả về 1,0 với mọi hộp. Đã dính thật:
    luật băng mục im lặng không bao giờ kích hoạt. Hộp chuẩn hoá dùng
    `aspect_norm`.
    """
    w, h = max(w or 0, 1), max(h or 0, 1)
    return max(w / h, h / w)


def aspect_norm(w, h):
    """Tỉ lệ dài/ngắn cho HỘP BAO CHUẨN HOÁ (0–1 theo bề trang)."""
    w, h = max(w or 0.0, 1e-6), max(h or 0.0, 1e-6)
    return max(w / h, h / w)


def is_page_furniture(item, reps, rep_min=REP_MIN, aspect_min=ASPECT_MIN):
    """Có ĐỦ CẢ HAI bằng chứng thì mới gọi là đồ trang trí của trang.

    Chỉ áp cho đường D. Vùng Docling đi qua cổng tin cậy riêng và trong toàn bộ
    số đo không sinh ca nào thuộc họ này — áp thêm luật này lên chúng là thêm
    rủi ro gỡ nhầm mà không có bằng chứng nào đòi.
    """
    if item.get('source') == 'docling':
        return False
    if reps.get((item['book'], item['hash']), 0) < rep_min:
        return False
    return aspect(item.get('w'), item.get('h')) >= aspect_min


# ────────────────────────────────────────────────────────────────────────
# HỌ THỨ HAI: BĂNG MỤC VÀ DẢI TRANG — không lặp đủ để luật trên bắt được
# ────────────────────────────────────────────────────────────────────────
#
# Census theo BÀI (n=40) xếp `NOT_A_LEARNING_VISUAL` đứng đầu: 10/40 bài
# (25%). Nhưng đó là một họ KHÁC họ trên: băng đầu mục («HÁT», «NHẠC CỤ»,
# «ĐỌC NHẠC»), dải nền có số trang, huy hiệu chương, mảnh nhãn vỡ. Chúng
# KHÔNG lặp đủ 6 trang theo vân tay ảnh, vì nét vẽ băng đổi chút một.
#
# ⛔ HAI LUẬT HIỂN NHIÊN ĐÃ BỊ CHÍNH SỐ LIỆU BÁC BỎ, ghi lại để không ai
# thử lại:
#
# 1. «ÍT MỰC ⇒ TRANG TRÍ» — SAI. Các ca HỢP LỆ ít mực nhất đều là HÌNH HỌC
#    của Toán: một điểm và một đường «Hình 3.31» mực 0,030; tam giác 0,061;
#    đường tròn trên lưới 0,109. Ngưỡng mực sẽ xoá đúng hình hình học.
#
# 2. «TỈ LỆ DẸT ⇒ TRANG TRÍ» — SAI, và đây là ca đối kháng đắt nhất: lấy 12
#    hình sách ÂM NHẠC có tỉ lệ ≥3 mà lặp ít, soi tận mắt thì ĐÚNG MỘT NỬA
#    là băng mục, MỘT NỬA là KHUÔNG NHẠC THẬT (kể cả khuông kép của piano).
#    Cùng cuốn, cùng dải tỉ lệ. Hình dạng không tách được chúng.
#
# ⭐ THỨ TÁCH ĐƯỢC LÀ VAI TRÒ TRONG SÁCH, KHÔNG PHẢI DÁNG VẺ:
#
#   · băng mục CHỨA NHÃN MỤC CỦA CHÍNH CUỐN SÁCH, in lại trên nhiều trang
#     («HÁT» 10 trang, «ĐỌC NHẠC» 6, «NHẠC CỤ» 5) — trong khi khuông nhạc
#     chỉ chứa lời hát và ký hiệu nhịp, lặp 0–1;
#   · dải trang CHỨA CHÍNH SỐ TRANG in ở mép — hình học tập thì không.
#
# Đo trên 36 ca đã soi tận mắt (24 ngẫu nhiên + 12 đối kháng ký âm):
# bắt đúng 7/16, GỠ NHẦM 0. Cố ý không đuổi theo phủ hết — Founder:
# «gỡ nhầm một hình thật tệ hơn để sót vài đồ trang trí».

HEAD_REP_MIN = 5      # nhãn mục in lại trên ít nhất ngần này trang của cuốn
HEAD_LINES_MAX = 3    # vùng chỉ có vài dòng chữ ⇒ nó LÀ cái nhãn, không chứa nhãn
EDGE = 0.09           # số trang nằm sát mép trên/dưới


def heading_reps(lines_by_page):
    """`{CHỮ IN HOA: số trang của cuốn có in dòng ấy}` — nhãn mục của sách.

    Chỉ đếm dòng NGẮN và KHÔNG phải số: «HÁT», «LUYỆN TẬP», «VẬN DỤNG».
    Số bị loại vì số trang lặp khắp nơi mà không phải nhãn mục.
    """
    import collections as _c
    seen = _c.defaultdict(set)
    for page, lines in lines_by_page.items():
        for l in lines or ():
            t = (l.get('text') or '').strip()
            if 3 <= len(t) <= 24 and not t.replace('.', '').replace(',', '').isdigit():
                seen[t.upper()].add(page)
    return {k: len(v) for k, v in seen.items()}


def _inside(bbox, l):
    x, y, w, h = bbox
    cx = l['x'] + (l.get('w') or 0) / 2
    cy = l['y'] + (l.get('h') or 0) / 2
    return x <= cx <= x + w and y <= cy <= y + h


def is_section_furniture(bbox, lines, reps, aspect_min=ASPECT_MIN,
                         head_min=HEAD_REP_MIN, max_lines=HEAD_LINES_MAX):
    """Băng mục / dải trang — nhận bằng VAI TRÒ, không bằng dáng vẻ.

    Ba vế, phải có đủ:
      1. tỉ lệ cực đoan (đây là họ dải ngang/dọc, không phải hình vuông vắn);
      2. chỉ vài dòng chữ bên trong ⇒ vùng ẤY LÀ cái nhãn, không phải hình
         có nhãn;
      3. và một trong hai bằng chứng nguồn: chứa NHÃN MỤC lặp nhiều trang,
         hoặc chứa CHÍNH SỐ TRANG in ở mép.
    """
    if bbox is None or aspect_norm(bbox[2], bbox[3]) < aspect_min:
        return False
    inside = [l for l in (lines or ()) if (l.get('text') or '').strip() and _inside(bbox, l)]
    if not inside or len(inside) > max_lines:
        return False
    for l in inside:
        t = (l.get('text') or '').strip()
        if reps.get(t.upper(), 0) >= head_min:
            return True
        if t.isdigit() and (l['y'] < EDGE or l['y'] > 1 - EDGE):
            return True
    return False
