#!/usr/bin/env python3
"""PACK CANONICAL KHÔNG ĐƯỢC THIẾU NĂNG LỰC ĐÃ PROMOTE.

2026-09-11: `FORMULA_SOURCE` là cờ BẬT thủ công. Một lượt dựng lớp 5 quên cờ
ấy làm **28 bài Toán 5 TĂNG khối chữ** — mảnh OCR công thức («+», «a)»,
«:(x7)», «- (2+ →)») chảy ngược vào dòng đọc trẻ đọc. Số hình y hệt, số bài y
hệt, mọi bất biến pack đều ĐẠT, không một lỗi nào.

Mọi cổng sẵn có đều đo PACK; không cổng nào đo CẤU HÌNH sinh ra pack.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'corpus'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ui'))

import staging  # noqa: E402
import build_lesson_figures as blf  # noqa: E402


class CoTatPhaiNoiRo(unittest.TestCase):
    """Quên cờ = ĐẦY ĐỦ. Muốn thiếu thì phải nói rõ."""

    def test_mac_dinh_khong_thieu_gi(self):
        # ⭐ ĐÂY LÀ BẤT BIẾN BỊ PHÁ. Trước bản sửa, môi trường trống nghĩa là
        # FormulaSource TẮT, và pack canonical ra thiếu mà không ai biết.
        self.assertNotIn('FormulaSource', blf.promoted_off({}))

    def test_tat_ro_thi_bao_ten(self):
        self.assertEqual(blf.promoted_off({'FORMULA_SOURCE': '0'}),
                         ['FormulaSource'])

    def test_che_do_dem_cung_la_thieu(self):
        """`FORMULA_SHADOW=1` chỉ ĐẾM, không đổi dòng đọc ⇒ pack vẫn thiếu."""
        self.assertEqual(blf.promoted_off({'FORMULA_SHADOW': '1'}),
                         ['FormulaSource'])

    def test_bat_ro_van_day_du(self):
        self.assertNotIn('FormulaSource', blf.promoted_off({'FORMULA_SOURCE': '1'}))


class DungCanonicalThiDungHan(unittest.TestCase):
    def setUp(self):
        self._old = os.environ.get('PACK_OUT_DIR')
        os.environ.pop('PACK_OUT_DIR', None)      # ⇒ đích là canonical

    def tearDown(self):
        os.environ.pop('PACK_OUT_DIR', None)
        if self._old is not None:
            os.environ['PACK_OUT_DIR'] = self._old

    def test_day_du_thi_chay_tiep(self):
        self.assertFalse(staging.is_staging())
        staging.require_promoted([])              # không ném

    def test_thieu_thi_SystemExit(self):
        self.assertFalse(staging.is_staging())
        with self.assertRaises(SystemExit) as cm:
            staging.require_promoted(['FormulaSource'])
        self.assertIn('FormulaSource', str(cm.exception))

    def test_khu_dung_thu_van_duoc_tat(self):
        """Tắt để đối chiếu chính là việc của khu dựng thử."""
        os.environ['PACK_OUT_DIR'] = '/tmp/wal-staging-test'
        self.assertTrue(staging.is_staging())
        staging.require_promoted(['FormulaSource'])   # không ném


if __name__ == '__main__':
    unittest.main()
