#!/usr/bin/env python3
"""GHÉP SGK ↔ SGV — khớp số bài KHÔNG phải là ghép đã chứng minh.

Mọi ca ở đây lấy từ nguồn thật, đo 2026-09-11.
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pedagogy'))

import sgk_sgv_pairing as P  # noqa: E402


class TrungTieuDe(unittest.TestCase):
    def test_bo_dau_van_trung(self):
        """OCR rụng dấu suốt: «Cầu trúc lặp» vs «CẤU TRÚC LẶP»."""
        self.assertGreaterEqual(P.title_match('CẤU TRÚC LẶP', 'Cầu trúc lặp'), 0.9)

    def test_khac_bai_thi_khong_trung(self):
        self.assertLess(
            P.title_match('ĐO CHIỀU DÀI', 'Hệ thống phân loại sinh vật'),
            P.TITLE_MIN)

    def test_tieu_de_bi_cat_van_nhan_duoc(self):
        """SGV in «NHÓM NGHỀ QUẢN TRỊ», SGK in đầy đủ hơn — vẫn phải khớp."""
        self.assertGreaterEqual(
            P.title_match('NHÓM NGHỀ QUẢN TRỊ',
                          'Nhóm nghề quản trị trong ngành Công nghệ thông tin'),
            P.TITLE_MIN)

    def test_rong_thi_khong_trung(self):
        self.assertEqual(P.title_match('', 'Đo chiều dài'), 0.0)


class BaChotDocLap(unittest.TestCase):
    """CONFIDENT đòi CẢ BA: số bài · tiêu đề · mở thân bài."""

    def _rows(self, heads, les):
        P_heads = P.body_headers
        P.body_headers = lambda _b: heads
        try:
            return P.pair_lessons('sgv-x', 'sgk-x', {'sgk-x': les})
        finally:
            P.body_headers = P_heads

    def test_du_ba_chot_thi_confident(self):
        r = self._rows([dict(page=44, lesson=9, text='HIỆU ỨNG CHUYỂN TRANG',
                             opener=True)], {9: 'Hiệu ứng chuyển trang'})
        self.assertEqual(r[0]['status'], 'CONFIDENT')

    def test_bang_phan_bo_tiet_KHONG_confident(self):
        """⭐ CA GHÉP SAI ĐÃ ĐO: `09-sgv-toan-9` tr93.

        Trang in «Bài 11. Tỉ số lượng giác của góc nhọn 4 tiết · Bài 12… 3
        tiết» trong phần giới thiệu sách. Số bài ĐÚNG, tiêu đề TRÙNG KHÍT —
        chỉ thiếu chốt mở thân bài. Nhận nhầm ở đây là gán cả bằng chứng sư
        phạm của một bài cho bảng phân bổ tiết.
        """
        r = self._rows([dict(page=93, lesson=11,
                             text='Tỉ số lượng giác của góc nhọn', opener=False)],
                       {11: 'Tỉ số lượng giác của góc nhọn'})
        self.assertEqual(r[0]['status'], 'AMBIGUOUS')

    def test_dung_so_bai_sai_tieu_de_KHONG_confident(self):
        r = self._rows([dict(page=10, lesson=5, text='MỘT NỘI DUNG KHÁC HẲN',
                             opener=True)], {5: 'Đo chiều dài'})
        self.assertEqual(r[0]['status'], 'AMBIGUOUS')

    def test_so_bai_khong_co_trong_SGK_thi_UNKNOWN(self):
        r = self._rows([dict(page=10, lesson=99, text='KHÔNG LIÊN QUAN',
                             opener=True)], {5: 'Đo chiều dài'})
        self.assertEqual(r[0]['status'], 'UNKNOWN')

    def test_hai_muc_cung_doi_mot_bai_thi_AMBIGUOUS(self):
        """Số bài lặp lại — không được chọn bừa một mục."""
        r = self._rows([dict(page=31, lesson=5, text='ĐO CHIỀU DÀI', opener=True),
                        dict(page=99, lesson=5, text='ĐO CHIỀU DÀI', opener=True)],
                       {5: 'Đo chiều dài'})
        self.assertEqual({x['status'] for x in r}, {'AMBIGUOUS'})


class DocTrangThat(unittest.TestCase):
    """Chạy THẲNG qua `body_headers` — hai đột biến từng sống sót vì không
    test nào đi qua hàm này: bỏ `_fold` ở chốt mở, và bỏ lọc trang mục lục."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.old = P.OCR
        P.OCR = self.tmp
        os.makedirs(os.path.join(self.tmp, 'x-sgv-y'))

    def tearDown(self):
        P.OCR = self.old
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _page(self, n, lines):
        with open(os.path.join(self.tmp, 'x-sgv-y', f'p{n:03d}.json'), 'w',
                  encoding='utf-8') as f:
            json.dump({'lines': [{'text': t} for t in lines]}, f)

    def test_chot_mo_chiu_duoc_OCR_rung_dau(self):
        """Tin học 4 tr44 thật: OCR viết «MỤC ĐICH» — vẫn phải nhận."""
        self._page(44, ['BÀI 9. HIỆU ỨNG CHUYỂN TRANG', 'A. MỤC ĐICH, YÊU CẦU',
                        '1. Kiến thức'])
        h = P.body_headers('x-sgv-y')
        self.assertEqual(len(h), 1)
        self.assertTrue(h[0]['opener'])

    def test_trang_muc_luc_bi_loai(self):
        """Mục lục liệt kê mọi bài ⇒ khớp với tất cả ⇒ mỏ neo giả."""
        self._page(6, ['Bài 16. Hỗn hợp các chất 91', 'Bài 17. Tách chất 100',
                       'Bài 18. Tế bào 106', 'Bài 19. Cấu tạo 108',
                       'Bài 20. Sự lớn lên 112'])
        self.assertEqual(P.body_headers('x-sgv-y'), [])

    def test_bang_phan_bo_tiet_khong_co_chot_mo(self):
        """Dòng lấy đúng theo `09-sgv-toan-9` tr93 — ca ghép sai đã đo."""
        self._page(93, ['Bài 11. Tỉ số lượng giác của góc nhọn', '4 tiết',
                        'Bài 12. Một số hệ thức giữa cạnh, góc trong tam giác '
                        'vuông và ứng dụng 3 tiết',
                        'Luyện tập chung', '2 tiết', 'Bài tập cuối chương IV',
                        '2 tiết', '3. Những điểm đổi mới chủ yếu so với SGK',
                        '3.1. Về nội dung',
                        # ⚠ Chữ «MỤC TIÊU» CÓ trên trang, nhưng ở một mục khác
                        # hẳn. Bản dò-cả-trang nhận nhầm đúng vì dòng này.
                        'Điểm mới nổi bật của SGK này là bám sát',
                        'MỤC TIÊU của Chương trình GDPT 2018 về năng lực'])
        h = P.body_headers('x-sgv-y')
        self.assertEqual(len(h), 1)
        self.assertFalse(h[0]['opener'])


class KhongLayMucLucLamMoNeo(unittest.TestCase):
    def test_nguong_muc_luc_con_hieu_luc(self):
        self.assertGreaterEqual(P.TOC_MIN, 3)

    def test_chot_mo_than_bai_bo_dau(self):
        """OCR viết «MỤC ĐICH» — rụng dấu không làm nó thôi là mục mở bài."""
        self.assertTrue(P.OPENER.search(P._fold('A. MỤC ĐICH, YÊU CẦU')))
        self.assertTrue(P.OPENER.search(P._fold('1 MỤC TIÊU')))
        self.assertTrue(P.OPENER.search(P._fold('I. YÊU CẦU CẦN ĐẠT')))

    def test_bang_phan_bo_khong_phai_chot_mo(self):
        self.assertFalse(P.OPENER.search(P._fold('4 tiết Bài 12. Một số hệ thức')))


if __name__ == '__main__':
    unittest.main()
