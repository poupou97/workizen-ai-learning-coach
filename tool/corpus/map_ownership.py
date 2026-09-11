#!/usr/bin/env python3
"""BẢN ĐỒ HIỆN HAI LẦN — ảnh bản đồ đúng, và cạnh nó là chữ TRONG bản đồ bị bẹp.

Máy thật (Lịch sử & Địa lí 5, Bài 4): sau khi vòng danh tính chú thích giao
được «Hình 2. Bản đồ phân bố dân cư Việt Nam năm 2024», trẻ đọc tiếp được
«PINÓM PÊNII», «NHT TYHI HNH 8°», «LAI CHÂU», «CHÚ GIÁI MẶT ĐỌ DÂN SỐ…» —
địa danh, toạ độ, thước tỉ lệ và chú giải VẼ TRONG tấm bản đồ, đã hiện trong
ảnh rồi, còn rơi thêm một lần nữa thành văn xuôi.

⛔ KHÔNG XOÁ CHỮ CỦA SÁCH KHI CHƯA CÓ BẰNG CHỨNG SỞ HỮU.

Luật này CỐ Ý HẸP. Đo trước khi viết (2026-09-11, mẫu đóng băng hạt giống
20260911) đã BÁC BỎ bản rộng «mọi vùng hình có danh tính»: 39 797 đoạn bị
chặn, trong đó

  • 1 166 đoạn mang chuỗi danh tính trên 925 trang — tức luật rộng XOÁ ĐÚNG
    chú thích và câu hỏi in trỏ vào hình mà vòng trước vừa giành lại;
  • Hoá học 12 chuyên đề tr.25: hộp «Hình 5.4» phình ra 74% trang trong khi
    hình thật chỉ là dải đáy — bên trong nó là TOÀN BỘ quy trình in của bài
    («Chuẩn bị nguyên liệu», «Nung chảy», «Định hình», cả phương trình).

Hai đặc trưng hình học (tỉ lệ chữ phủ vùng, bề rộng khối) KHÔNG tách được
trường hợp đúng khỏi trường hợp sai: Sinh học 11 tr.168 (nuốt «Bước 1–4»,
HỎNG) phủ 15,1%, còn bản đồ LS5 tr.24 (ĐÚNG) phủ 21,0%. Dữ kiện phân biệt
thật — «chữ nằm trên tranh hay trên giấy trắng» — là dữ kiện ĐIỂM ẢNH, mà kho
không có ảnh trang. Nên phạm vi thu về đúng vật mà CHÍNH SÁCH GỌI TÊN là bản
đồ: 3 375 đoạn / 118 trang, chỉ Lịch sử và Địa lí.

⚠ NHẮC TỚI KHÔNG PHẢI LÀ DANH TÍNH. «Hình 3. Sơ đồ các bước sử dụng bản đồ,
lược đồ» có chữ «bản đồ» nhưng vật ấy là SƠ ĐỒ; bên trong nó là ba bước in
«Đọc tên bản đồ…», «Xem chú giải…», «Tìm đối tượng…». Nên từ chỉ loại phải
đọc ở NGAY SAU phần đánh số, không phải ở bất kỳ đâu trong chú thích.
"""
import re

from figure_funnel import IDENTITY

#: Cùng ngưỡng đã chứng minh ở `table_ownership`: nằm gọn ngần này diện tích
#: CỦA CHÍNH KHỐI CHỮ trong vùng ⇒ ảnh ấy đã hiện nó ra rồi.
INSIDE = 0.8

#: Phần ĐÁNH SỐ mở đầu chú thích («Hình 2.», «Hình 2.3.», «Bảng 1,2:»).
_NUMBERING = re.compile(
    r'^\s*(?:hình|bảng|sơ\s*đồ|biểu\s*đồ|bản\s*đồ|lược\s*đồ)'
    r'\s*\d{1,2}[a-z]?(?:\s*[.,]\s*\d{1,2}[a-z]?)*\s*[.:]?\s*', re.IGNORECASE)
#: Từ chỉ loại mà sách gán cho VẬT, đọc ngay sau phần đánh số.
_IS_MAP = re.compile(r'^\s*(?:bản\s*đồ|lược\s*đồ)\b', re.IGNORECASE)


def is_map_caption(caption):
    """Sách có GỌI vật này là bản đồ/lược đồ không — theo chữ in, không đoán."""
    return bool(_IS_MAP.match(_NUMBERING.sub('', caption or '', count=1)))


def _inside_frac(box, bbox):
    """Phần diện tích của KHỐI CHỮ nằm trong vùng — mẫu số là khối, không phải vùng."""
    x0, y0, x1, y1 = box
    bx, by, bw, bh = bbox
    ix = min(x1, bx + bw) - max(x0, bx)
    iy = min(y1, by + bh) - max(y0, by)
    if ix <= 0 or iy <= 0:
        return 0.0
    area = max((x1 - x0) * (y1 - y0), 1e-9)
    return (ix * iy) / area


def map_regions(figs):
    """Hộp của các vùng BẢN ĐỒ đã giao được ảnh trên trang này.

    Danh sách truyền vào là hình ĐÃ qua lọc trang trí và ĐÃ có ảnh — nên chữ
    bị bỏ đi chắc chắn còn hiện trong một tấm ảnh trẻ nhìn thấy.
    """
    return [f['bbox'] for f in figs
            if f.get('kind') != 'table' and is_map_caption(f.get('caption'))]


def owned_by_map(para, maps, inside=INSIDE):
    """Khối chữ này có nằm gọn trong một tấm bản đồ đang hiện không."""
    box = para.get('box')
    if not box:
        return False                      # không có bằng chứng ⇒ GIỮ
    # ⭐ CHÚ THÍCH VÀ CÂU HỎI TRỎ VÀO HÌNH KHÔNG BAO GIỜ BỊ CHẶN. Hộp hình của
    # Docling thường nuốt cả dòng chú thích in ngay dưới nó (Toán 8 tr.97
    # «Hình 9.40» ở y0,728 lọt vào hộp y0,623–0,740), và đề bài cũng gọi tên
    # hình («Quan sát Hình 8.4 và cho biết…»). Mất hai thứ ấy là mất đúng cái
    # vòng danh tính vừa giành lại.
    if IDENTITY.search(para.get('text') or ''):
        return False
    return any(_inside_frac(box, m) >= inside for m in maps)
