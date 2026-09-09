#!/usr/bin/env python3
"""MÔN HỌC suy từ MÃ SÁCH — khớp theo RANH GIỚI ĐOẠN, không khớp chuỗi con.

⚠ LỖI ĐÃ XẢY RA THẬT, hai lần trong một ngày, và một lần đã tới tay Founder.

Bản cũ dùng `if 'hoa-hoc' in book`. Chuỗi `'khoa-hoc'` CHỨA `'hoa-hoc'`, nên
`11-sgk-tin-hoc-11-dinh-huong-khoa-hoc-may-tinh` bị gán nhãn **Hoá học**. Hệ
quả: tôi báo với Founder «53,5% vùng code nằm ở Hoá học nên gần chắc là trang
bản quyền». Sự thật: Tin học 91,8%, Hoá học 0,2%, và trang bản quyền chỉ 0,9%.
Một giả thuyết sai được xây trọn vẹn trên một phép so chuỗi.

Nên ở đây mã sách được TÁCH THÀNH ĐOẠN rồi mới đối chiếu. `khoa-hoc` và
`hoa-hoc` là hai dãy đoạn khác nhau; không có cách nào nhầm lẫn.

⛔ KHÔNG thêm luật riêng cho từng cuốn. Nhận không ra thì trả «môn khác» —
`UNKNOWN != đoán bừa`.
"""

#: Thứ tự KHÔNG còn quan trọng vì đã khớp theo đoạn, nhưng vẫn để dãy dài
#: trước dãy ngắn cho người đọc thấy rõ quan hệ bao hàm.
SUBJECTS = (
    (('khoa', 'hoc', 'tu', 'nhien'), 'KHTN'),
    (('dinh', 'huong', 'khoa', 'hoc', 'may', 'tinh'), 'Tin học'),
    (('tin', 'hoc'), 'Tin học'),
    (('hoa', 'hoc'), 'Hoá học'),
    (('vat', 'li'), 'Vật lí'),
    (('sinh', 'hoc'), 'Sinh học'),
    (('cong', 'nghe'), 'Công nghệ'),
    (('toan',), 'Toán'),
    (('ngu', 'van'), 'Ngữ văn'),
    (('lich', 'su'), 'Lịch sử'),
    (('dia', 'li'), 'Địa lí'),
    (('am', 'nhac'), 'Âm nhạc'),
    (('mi', 'thuat'), 'Mĩ thuật'),
    (('tieng', 'anh'), 'Tiếng Anh'),
    (('tieng', 'viet'), 'Tiếng Việt'),
    (('giao', 'duc', 'the', 'chat'), 'GDTC'),
    (('khoa', 'hoc'), 'Khoa học'),
)


def _segments(book):
    return tuple(s for s in (book or '').split('-') if s)


def _has_run(segs, run):
    """Dãy đoạn `run` có xuất hiện LIỀN NHAU trong `segs` không."""
    n = len(run)
    return any(segs[i:i + n] == run for i in range(len(segs) - n + 1))


def subject(book):
    """Tên môn, hoặc «môn khác» khi không có bằng chứng trong mã sách."""
    segs = _segments(book)
    for run, name in SUBJECTS:
        if _has_run(segs, run):
            return name
    return 'môn khác'
