#!/usr/bin/env python3
"""BẰNG CHỨNG SƯ PHẠM — xuất hiện KHÔNG phải là sở hữu."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pedagogy'))

import sgv_evidence as E  # noqa: E402


class HaiTrucTinCay(unittest.TestCase):
    def test_nhan_muc_in_ra_la_EXPLICIT(self):
        import re
        self.assertTrue(re.search(E.EXPLICIT['ANSWER'], E._fold('2. Đáp án và đánh giá')))
        self.assertTrue(re.search(E.EXPLICIT['MISCONCEPT'], E._fold('HS dễ nhầm lẫn giữa')))

    def test_the_hien_khong_nhan_la_DEMONSTRATED(self):
        import re
        self.assertFalse(re.search(E.EXPLICIT['ANSWER'], E._fold('Câu 1. Nước có tính chất')))
        self.assertTrue(re.search(E.DEMONSTRATED['ANSWER'], E._fold('Câu 1. Nước có tính chất')))

    def test_muc_danh_gia_B_H_VD(self):
        import re
        self.assertTrue(re.search(E.DEMONSTRATED['ASSESSMENT'], E._fold('Câu 1 (B). Nước có')))


class SoHuuMucVIEC(unittest.TestCase):
    """«Đáp án thuộc bài» KHÔNG phải «đáp án thuộc việc trẻ đang làm»."""

    def _span(self, W):
        E.sgk_words.__defaults__[0].clear()
        E.sgk_words.__defaults__[0][('sgk-x', 1)] = W
        return dict(sgk='sgk-x', lesson=1)

    def test_cau_hoi_SGV_in_ra_trung_bai_SGK(self):
        import sgk_sgv_pairing as P
        W = P.toks('Nêu tính chất của nước đã được học trong bài')
        t = E._fold('Câu 1. Nêu tính chất của nước đã được học trong bài?')
        self.assertTrue(E.task_linked(t, self._span(W)))

    def test_cau_hoi_khac_han_thi_KHONG_gan_duoc(self):
        import sgk_sgv_pairing as P
        W = P.toks('Hệ thống phân loại sinh vật gồm những bậc nào')
        t = E._fold('Câu 1. Nêu tính chất của nước đã được học trong bài?')
        self.assertFalse(E.task_linked(t, self._span(W)))

    def test_bai_SGK_khong_co_chu_thi_KHONG_gan_duoc(self):
        t = E._fold('Câu 1. Nêu tính chất của nước?')
        self.assertFalse(E.task_linked(t, self._span(set())))

    def test_khong_khop_bang_CON_SO(self):
        """SGK dùng «N.» ở 97,0% bài nhưng «Câu N» chỉ 3,1% — và «N.» còn là
        số MỤC. Khớp số là sở hữu giả, nên luật phải xét CHỮ."""
        import sgk_sgv_pairing as P
        W = P.toks('1. Quy mô dân số 2. Gia tăng dân số')
        t = E._fold('Câu 1. Nêu tính chất của nước đã được học trong bài?')
        self.assertFalse(E.task_linked(t, self._span(W)))


class HuongDanGiaoVienKhongPhaiGoiYChoTre(unittest.TestCase):
    def test_goi_y_luon_mang_co_TEACHER(self):
        sp = dict(sgv='x', sgk='y', lesson=1, start=1, end=2)
        E.page_text = lambda *a, **k: 'MỤC TIÊU. Lưu ý: GV cho HS quan sát. Hoạt động 1.'
        rows = E.evidence(sp)
        aud = {r['field']: r['audience'] for r in rows}
        self.assertEqual(aud['HINT'], 'TEACHER')
        self.assertEqual(aud['ACTIVITY'], 'TEACHER')
        self.assertEqual(aud['OBJECTIVE'], 'SOURCE')


if __name__ == '__main__':
    unittest.main()
