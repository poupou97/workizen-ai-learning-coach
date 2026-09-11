#!/usr/bin/env python3
"""Chữ VẼ TRONG bản đồ bị bỏ; chữ IN quanh bản đồ thì không.

Mọi ca ở đây lấy từ trang thật, đo ngày 2026-09-11 — không dựng số liệu.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'corpus'))

import map_ownership as mo  # noqa: E402

#: Hộp «Hình 2. Bản đồ phân bố dân cư Việt Nam năm 2024» — LS&ĐL 5 tr.24.
MAP = [0.102, 0.067, 0.814, 0.828]


def para(x0, y0, x1, y1, text=''):
    return dict(box=[x0, y0, x1, y1], text=text)


class TenGoiCuaSach(unittest.TestCase):
    def test_sach_goi_la_ban_do(self):
        self.assertTrue(mo.is_map_caption('Hình 2. Bản đồ phân bố dân cư Việt Nam'))
        self.assertTrue(mo.is_map_caption('Hình 1. Lược đồ chiến dịch'))
        self.assertTrue(mo.is_map_caption('Hình 2.3. Bản đồ khí hậu Việt Nam'))
        self.assertTrue(mo.is_map_caption('Lược đồ Việt Nam'))

    def test_nhac_toi_khong_phai_la_danh_tinh(self):
        """LS&ĐL 4 tr.10: vật là SƠ ĐỒ, trong nó là ba bước SỬ DỤNG in ra chữ.

        Nhận nhầm ở đây là xoá «Đọc tên bản đồ, lược đồ để biết…», «Xem chú
        giải…», «Tìm đối tượng lịch sử hoặc địa lí dựa vào kí hiệu.»
        """
        self.assertFalse(
            mo.is_map_caption('Hình 3. Sơ đồ các bước sử dụng bản đồ, lược đồ'))
        self.assertFalse(mo.is_map_caption('Hình 5. Sơ đồ tư duy về bản đồ'))
        self.assertFalse(mo.is_map_caption('Hình 25.4. Chọn địa điểm trên bản đồ'))

    def test_khong_co_chu_thich_thi_khong_phai_ban_do(self):
        self.assertFalse(mo.is_map_caption(None))
        self.assertFalse(mo.is_map_caption(''))

    def test_vung_bang_khong_bao_gio_la_ban_do(self):
        figs = [dict(kind='table', bbox=MAP, caption='Bảng 2. Bản đồ hành chính')]
        self.assertEqual(mo.map_regions(figs), [])

    def test_chi_lay_vung_ban_do(self):
        figs = [dict(kind='picture', bbox=MAP, caption='Hình 2. Bản đồ phân bố dân cư'),
                dict(kind='picture', bbox=[0, 0, 0.2, 0.2], caption='Hình 3. Sơ đồ')]
        self.assertEqual(mo.map_regions(figs), [MAP])


class SoHuuTheoHinhHoc(unittest.TestCase):
    def test_nhan_trong_ban_do_bi_bo(self):
        """«LAI CHÂU», «PINÓM PÊNII» — địa danh vẽ trong tấm ảnh đang hiện."""
        self.assertTrue(mo.owned_by_map(para(0.2, 0.3, 0.28, 0.32, 'LAI CHÂU'), [MAP]))

    def test_van_xuoi_ngoai_vung_giu_nguyen(self):
        self.assertFalse(
            mo.owned_by_map(para(0.08, 0.90, 0.92, 0.95, 'Dân cư nước ta phân bố'), [MAP]))

    def test_chi_chom_vao_thi_giu(self):
        """Nửa trong nửa ngoài ⇒ không đủ bằng chứng sở hữu ⇒ GIỮ."""
        self.assertFalse(
            mo.owned_by_map(para(0.60, 0.80, 0.99, 0.90, 'văn xuôi tràn mép'), [MAP]))

    def test_khong_co_hop_thi_giu(self):
        self.assertFalse(mo.owned_by_map(dict(text='LAI CHÂU'), [MAP]))

    def test_khong_co_ban_do_thi_giu(self):
        self.assertFalse(mo.owned_by_map(para(0.2, 0.3, 0.28, 0.32, 'LAI CHÂU'), []))


class DanhTinhKhongBaoGioBiChan(unittest.TestCase):
    def test_chu_thich_lot_vao_hop_van_song(self):
        """Toán 8 tr.97: «Hình 9.40» in ở y0,728 lọt vào hộp y0,623–0,740."""
        self.assertFalse(
            mo.owned_by_map(para(0.773, 0.72, 0.847, 0.74, 'Hình 9.40'), [MAP]))

    def test_cau_hoi_tro_vao_hinh_van_song(self):
        self.assertFalse(mo.owned_by_map(
            para(0.2, 0.3, 0.6, 0.34, 'Quan sát Hình 8.4 và cho biết cách chia'), [MAP]))

    def test_chu_thich_ban_do_cua_chinh_no_van_song(self):
        self.assertFalse(mo.owned_by_map(
            para(0.2, 0.80, 0.8, 0.83, 'Hình 2. Bản đồ phân bố dân cư Việt Nam'), [MAP]))


if __name__ == '__main__':
    unittest.main()
