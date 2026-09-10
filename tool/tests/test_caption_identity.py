#!/usr/bin/env python3
"""DANH TÍNH CHÚ THÍCH — bằng chứng của chính dòng, không phải kích thước khối.

Mục tiêu KHÔNG phải «lấy được nhiều chú thích hơn». Mục tiêu là:

    VẬT THỂ NGUỒN  ↔  CHÚ THÍCH IN  ↔  HÌNH TỚI TAY TRẺ

đủ bằng chứng để nói ba thứ ấy là CÙNG MỘT vật. `SAI TÊN > THIẾU TÊN`.

Mọi ca dưới đây LẤY TỪ CORPUS THẬT, qua mẫu đóng băng 80 ca (seed 20260911)
đã dán nhãn tay. Không có ca nào bịa.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'tool', 'corpus'))

import figure_funnel as ff  # noqa: E402


def anchors(text, block_lines):
    l = {'x': 0.3, 'y': 0.9, 'w': 0.4, 'h': 0.02, 'text': text}
    return ff.caption_anchors([l], extended=True, block_lines={id(l): block_lines})


class ChuThichCoTen(unittest.TestCase):
    """Có DẤU NGĂN + CÓ TÊN + ĐÚNG MỘT danh tính ⇒ nhận, bất kể khối dài."""

    THAT = [
        # ⭐ NHÂN CHỨNG CHÍNH: bài tập in của Lịch sử 5 Bài 4 đòi đúng tấm bản
        # đồ này. Trước bản vá nó bị loại vì `blocks()` gom nó với hai nhãn
        # toạ độ bản đồ («100», «108°») thành khối 3 dòng.
        ('Hình 2. Bản đồ phân bố dân cư Việt Nam năm 2024', 3),
        ('Hình 1. Lược đồ cuộc kháng chiến chống Tổng năm 981', 4),
        ('Hình 6. Du lịch trên sông Hồng', 6),          # tên mở đầu bằng từ 2 chữ
        ('Hình 2. Kĩ thuật đánh cầu cao trái tay', 7),
        ('Hình 20. Sơ đồ bài tập Mô phỏng đội hình di chuyển', 4),
        ('BẢNG 2. TRỊ GIÁ XUẤT, NHẬP KHẨU HÀNG HOÁ VÀ DỊCH VỤ', 14),
        ('Biểu đồ 1. Mức độ đóng góp của khu vực FDI vào GDP', 8),
        ('Hình 4: Sơ đồ đường đi của thức ăn.', 37),    # dấu ngăn hai chấm
        ('Hình 12a.3. Bảng tổng hợp mục chi', 4),       # số hiệu có chữ cái
    ]

    def test_nhan_du_khoi_dai(self):
        for t, n in self.THAT:
            with self.subTest(t=t):
                a = anchors(t, n)
                self.assertTrue(a, f'bỏ sót chú thích thật: «{t}»')


class KhongPhaiChuThich(unittest.TestCase):
    """Câu văn · danh sách · phép nhân — loại hết. Đây là nửa quan trọng hơn."""

    KHONG = [
        ('Hình 1 gắn liên với hoạt động của', 6),        # CÂU, không có dấu ngăn
        ('Hình 8 và cho biết bạn An đã gặp', 5),         # CÂU
        ('Hình 1 là một tháp Chăm tiêu biểu của Vương quốc', 3),
        ('Hình 7.4a (SGK) tương ứng với bộ phận nào ở Hình 7.4b', 32),
        ('Hình 9a.1 và Hình 9a.2 còn cung cấp cho HS cái nhìn', 23),
        ('Hình 1: Sơ đồ các hành tinh; Hình 2: Sơ đồ Trái Đất', 34),
        ('hình 1b ít nhất, sau đó đến hình 1c, còn nến ở hình 1a', 33),
        # ⚠ «bảng 10 x 10» là một PHÉP NHÂN, không phải chú thích bảng.
        ('bảng 10 x 10, cột 10 x 1 và các khối lập phương đơn vị', 17),
        ('Hình 9a.9.', 14),                              # kết một câu, không có tên
        ('Hình 11', 30),                                 # đánh số TRƠ trong khối dài
        ('Hình 2 (b, d)', 30),
        ('Hình 2a, 3', 17),
    ]

    def test_loai_het(self):
        for t, n in self.KHONG:
            with self.subTest(t=t):
                self.assertFalse(anchors(t, n), f'nhận nhầm: «{t}»')


class KhongDuocLamHongCaiDangChay(unittest.TestCase):
    """Hai cấp «Hình 14.2» và khối ngắn vẫn phải chạy y như cũ."""

    def test_hai_cap_van_nhan(self):
        for t in ('Hình 14.2', 'Hình 14.1 Thí nghiệm về dòng điện cảm ứng',
                  'Bảng 21.3. Một số đặc điểm của phản ứng'):
            with self.subTest(t=t):
                self.assertTrue(anchors(t, 24), f'mất chú thích hai cấp: «{t}»')

    def test_danh_so_TRO_trong_khoi_NGAN_van_nhan(self):
        """Toán đặt tên hình bằng số trơ «Hình 10.16» — không được mất."""
        self.assertTrue(anchors('Hình 10.16', 1))
        self.assertTrue(anchors('Hình 1', 2))

    def test_danh_so_TRO_trong_khoi_DAI_van_bi_loai(self):
        """Cố ý KHÔNG nới chỗ này — không có tên thì không có bằng chứng."""
        self.assertFalse(anchors('Hình 1', 3))


class HaiDanhTinhThiKhongGanDuoc(unittest.TestCase):
    """Một dòng mang HAI danh tính thì không gán an toàn cho MỘT hình.

    Loại nó là fail-closed ĐÚNG, không phải mất mát. Áp cho CẢ nhánh hai cấp:
    đo được 57/10.059 (0,57%) chú thích đang nhận rơi vào họ này, phần lớn là
    câu văn — «Hình 2.13b trình bày các hình chiếu vuông góc của hình trụ được
    mô tả ở Hình 2.13a.»
    """

    def test_hai_danh_tinh_bi_loai_ke_ca_hai_cap(self):
        self.assertFalse(anchors(
            'Hình 2.13b trình bày các hình chiếu vuông góc của hình trụ '
            'được mô tả ở Hình 2.13a.', 1))

    def test_mot_danh_tinh_van_nhan(self):
        self.assertTrue(anchors('Hình 2.13. Hình chiếu vuông góc của hình trụ', 9))


if __name__ == '__main__':
    unittest.main()
