#!/usr/bin/env python3
"""B3 — «KHÔNG promote corpus/pack MỘT PHẦN chỉ vì hết thời gian» là CODE.

Pack dựng dở đọc ra vẫn «hợp lệ»: đủ bài, đủ bìa, không lỗi nào — chỉ thiếu
hình mà không ai biết. Đúng kiểu hỏng đã làm lớp 3 tụt 232 → 44 bài trong khi
cả ba bất biến đều ĐẠT.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import docling_promote as dpr  # noqa: E402

GRADE = {'a': 3, 'b': 3, 'c': 4}
WANT = [('a', 1), ('a', 2), ('b', 1), ('c', 1)]


class DoPhu(unittest.TestCase):
    def test_du_ca_lop_thi_duoc_dung_lai(self):
        done = {'a': {1, 2}, 'b': {1}, 'c': {1}}
        cov = dpr.coverage(WANT, done, GRADE)
        self.assertEqual(cov[3], (3, 3, True))
        self.assertEqual(cov[4], (1, 1, True))

    def test_THIEU_MOT_TRANG_thi_ca_lop_bi_giu_lai(self):
        done = {'a': {1, 2}, 'b': set(), 'c': {1}}
        cov = dpr.coverage(WANT, done, GRADE)
        self.assertEqual(cov[3], (2, 3, False))   # lớp 3 KHÔNG được dựng
        self.assertEqual(cov[4], (1, 1, True))    # lớp 4 vẫn đủ

    def test_thieu_HAN_MOT_CUON_cung_la_chua_du(self):
        done = {'a': {1, 2}}
        self.assertFalse(dpr.coverage(WANT, done, GRADE)[3][2])

    def test_trang_thua_khong_lam_lop_thanh_du(self):
        """Chạy nhầm trang ngoài danh sách không bù được trang còn thiếu — và
        cũng KHÔNG được cộng vào số đã xong, nếu không báo cáo tiến độ sẽ nói
        dối về chỗ đang đứng."""
        done = {'a': {1, 2, 99}, 'b': set(), 'c': {1}}
        self.assertEqual(dpr.coverage(WANT, done, GRADE)[3], (2, 3, False))


if __name__ == '__main__':
    unittest.main()
