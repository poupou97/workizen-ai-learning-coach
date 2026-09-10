#!/usr/bin/env python3
"""WAL-239 — `stem_exposure` phải CHẠY ĐƯỢC, và chạy đúng ngưỡng đã công bố.

Hồi quy cho một lỗi thật: `INSIDE` bị xoá nhầm ở d099f5f cùng lúc gỡ bộ phân
loại môn cục bộ nằm ngay bên cạnh, nên module ném `NameError` ngay vùng đầu
tiên có chữ. Không test nào bắt được vì không test nào GỌI nó.

⛔ Ngưỡng 0,60 là giá trị KHÔI PHỤC theo chứng cứ git (3e1c367, eca4d50) — nó
là ngưỡng đã sinh ra mọi số phơi nhiễm đã báo cáo. Đổi nó là định nghĩa lại
một phép đo đã công bố, không phải tinh chỉnh.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'tool', 'corpus'))

import stem_exposure as se  # noqa: E402


class NguongPhoiNhiem(unittest.TestCase):

    def test_inside_dung_gia_tri_lich_su(self):
        self.assertEqual(se.INSIDE, 0.60)

    def test_mau_so_la_chinh_doan_van_khong_phai_vung(self):
        """`_frac` hỏi «đoạn này có thuộc về vùng không» ⇒ chia cho ĐOẠN.

        Đây đúng cái bẫy mẫu số đã dính ba lần trong một ngày, nên chốt bằng
        một hình có hai đáp số khác hẳn nhau: đoạn nhỏ nằm trọn trong vùng lớn
        ⇒ 100% theo mẫu số ĐOẠN, mà chỉ 25% nếu lỡ chia cho VÙNG.
        """
        doan = [0.0, 0.0, 0.1, 0.1]          # 0,01 đơn vị diện tích
        vung = [0.0, 0.0, 0.2, 0.2]          # 0,04 — gấp bốn
        self.assertAlmostEqual(se._frac(doan, vung), 1.0)
        self.assertAlmostEqual(se._frac(vung, doan), 0.25)

    def test_khong_chong_thi_bang_khong(self):
        self.assertEqual(se._frac([0.5, 0.5, 0.1, 0.1], [0.0, 0.0, 0.2, 0.2]), 0.0)

    def test_wh_doi_GOC_sang_xywh(self):
        """`page_paragraphs` trả GÓC `[x0,y0,x1,y1]`; vùng Docling là `[x,y,w,h]`.

        Hai quy ước cùng tồn tại trong repo và đã một lần làm đọc kích thước
        vùng công thức thành 29,9% trang thay vì 0,91%.
        """
        got = se.wh([0.2, 0.3, 0.5, 0.9])
        for a, b in zip(got, [0.2, 0.3, 0.3, 0.6]):
            self.assertAlmostEqual(a, b)

    def test_quyet_dinh_thuoc_ve_dung_o_hai_ben_nguong(self):
        """Chạy đúng phép so mà `main()` dùng — bắt được `NameError` nếu tái phát."""
        vung = [0.0, 0.0, 1.0, 1.0]
        trong = se.wh([0.0, 0.0, 0.5, 0.5])          # trọn trong vùng ⇒ 100%
        ngoai = se.wh([0.8, 0.8, 1.6, 1.6])          # thò ra ngoài ⇒ 25%
        self.assertGreaterEqual(se._frac(trong, vung), se.INSIDE)
        self.assertLess(se._frac(ngoai, vung), se.INSIDE)


if __name__ == '__main__':
    unittest.main()
