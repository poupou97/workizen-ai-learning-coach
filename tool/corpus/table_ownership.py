#!/usr/bin/env python3
"""BẢNG HIỆN HAI LẦN — ảnh bảng đúng, và ngay cạnh là bản chữ bảng bị bẹp.

Máy thật bắt được (Nokia, 2026-09-09, Hoá học 11 chuyên đề Bài 9): trẻ thấy
«STT 1 2 3 4 5 6», «Tên mỏ Bạch Hổ Hồng Ngọc Rạng Đông…», «1986 1998 1998 2010»
— bảng đọc thành văn xuôi — RỒI mới thấy ảnh bảng đúng ngay bên dưới.

Đo trên toàn corpus: **277/290 bài (95,5%)** có ảnh bảng đáng tin vẫn kèm dấu
vết bảng bẹp thành chữ.

⛔ KHÔNG XOÁ CHỮ CỦA SÁCH KHI CHƯA CÓ BẰNG CHỨNG SỞ HỮU. Founder: «Preserve
surrounding prose. Do NOT delete source text blindly.»

Bằng chứng sở hữu ở đây là HÌNH HỌC, không phải phỏng đoán: một khối chữ NẰM
GỌN TRONG vùng bảng đáng tin thì chính ảnh bảng ấy đã hiện nó ra rồi. Bỏ bản
chữ đi không mất gì — vì nó nằm trong ảnh. Khối chữ nằm ngoài vùng là văn xuôi
quanh bảng, GIỮ NGUYÊN.

Chỉ áp cho vùng BẢNG đã qua cổng tin cậy (654 vùng toàn corpus). Không áp cho
hình thường: một khối chữ nằm trong hộp ảnh chưa chắc được ảnh ấy hiện ra đầy
đủ, và ảnh thường không hứa hẹn giữ nguyên văn.
"""
INSIDE = 0.8          # nằm trong ngần này diện tích của chính nó ⇒ bảng sở hữu


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


def owned_by_table(para, tables, inside=INSIDE):
    """Khối chữ này có nằm gọn trong một vùng BẢNG đáng tin đang hiện không."""
    box = para.get('box')
    if not box:
        return False                      # không có bằng chứng ⇒ GIỮ
    return any(_inside_frac(box, t) >= inside for t in tables)


def table_regions(figs):
    """Hộp của các vùng BẢNG đáng tin trong danh sách hình của trang."""
    return [f['bbox'] for f in figs
            if (f.get('kind') == 'table' and f.get('source') == 'docling')]
