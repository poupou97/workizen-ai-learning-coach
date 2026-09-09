#!/usr/bin/env python3
"""BẢNG HIỆN HAI LẦN — bỏ bản chữ trùng, GIỮ văn xuôi quanh bảng.

Máy thật bắt được: trẻ thấy «STT 1 2 3 4 5 6», «1986 1998 1998 2010» rồi mới
thấy ảnh bảng đúng. 277/290 bài có ảnh bảng đáng tin dính lỗi này.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import table_ownership as to  # noqa: E402

TABLE = (0.10, 0.20, 0.80, 0.30)          # x, y, w, h


def para(x0, y0, x1, y1):
    return dict(box=[x0, y0, x1, y1], text='ô bảng')


class QuyenSoHuu(unittest.TestCase):
    def test_khoi_NAM_GON_trong_bang_thi_bang_so_huu(self):
        self.assertTrue(to.owned_by_table(para(0.2, 0.22, 0.5, 0.26), [TABLE]))

    def test_khoi_NGOAI_bang_la_van_xuoi_GIU_NGUYEN(self):
        """⭐ Founder: «Preserve surrounding prose.»"""
        self.assertFalse(to.owned_by_table(para(0.1, 0.55, 0.9, 0.62), [TABLE]))

    def test_khoi_CHI_CHAM_MEP_bang_thi_KHONG_bi_coi_la_cua_bang(self):
        """Đoạn văn bắt đầu trong bảng rồi chạy dài xuống dưới ⇒ phần lớn nó
        KHÔNG nằm trong ảnh bảng, nên xoá đi là mất chữ của sách.

        ⚠ Bảng trải y 0,20–0,50. Đoạn này 0,45–0,75: chỉ 1/6 nằm trong."""
        self.assertFalse(to.owned_by_table(para(0.05, 0.45, 0.95, 0.75), [TABLE]))

    def test_KHONG_CO_HOP_thi_GIU(self):
        """Không có bằng chứng sở hữu ⇒ không được xoá chữ của sách."""
        self.assertFalse(to.owned_by_table(dict(text='x'), [TABLE]))

    def test_khong_co_bang_nao_thi_giu_het(self):
        self.assertFalse(to.owned_by_table(para(0.2, 0.22, 0.5, 0.26), []))


class ChiApChoBangDangTin(unittest.TestCase):
    def test_chi_lay_vung_BANG_cua_Docling(self):
        figs = [dict(bbox=[0, 0, 1, 1], kind='table', source='docling'),
                dict(bbox=[0, 0, 1, 1], kind='picture', source='docling'),
                dict(bbox=[0, 0, 1, 1], source='D')]
        self.assertEqual(to.table_regions(figs), [[0, 0, 1, 1]])

    def test_hinh_thuong_KHONG_duoc_xoa_chu(self):
        """Một khối chữ nằm trong hộp ẢNH THƯỜNG chưa chắc được ảnh hiện ra
        đầy đủ — chỉ vùng bảng đáng tin mới hứa giữ nguyên văn."""
        figs = [dict(bbox=list(TABLE), kind='picture', source='docling')]
        self.assertEqual(to.table_regions(figs), [])


class PhepDoDienTich(unittest.TestCase):
    def test_mau_so_la_KHOI_CHU_khong_phai_vung(self):
        # Khối bé nằm trọn trong bảng to ⇒ 1.0, dù nó chỉ chiếm 1% diện tích bảng.
        self.assertAlmostEqual(
            to._inside_frac([0.2, 0.22, 0.22, 0.23], TABLE), 1.0, places=5)

    def test_khong_giao_nhau_thi_bang_khong(self):
        self.assertEqual(to._inside_frac([0.0, 0.0, 0.05, 0.05], TABLE), 0.0)


if __name__ == '__main__':
    unittest.main()
