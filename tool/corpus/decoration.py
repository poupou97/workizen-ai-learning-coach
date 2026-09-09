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
    w, h = max(w or 0, 1), max(h or 0, 1)
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
