#!/usr/bin/env python3
"""MÔN HỌC — khớp theo RANH GIỚI ĐOẠN, không khớp chuỗi con.

Lỗi đã xảy ra thật và đã tới tay Founder: `'khoa-hoc'` chứa `'hoa-hoc'`, nên
«Tin học định hướng KHOA HỌC máy tính» bị gán nhãn «Hoá học», và tôi báo
«53,5% vùng code ở Hoá học» trong khi sự thật là 0,2%.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
from subject import subject  # noqa: E402


class PhanLoaiMon(unittest.TestCase):
    def test_KHOA_HOC_KHONG_bi_nham_thanh_HOA_HOC(self):
        """⭐ Chính lỗi đã báo sai cho Founder."""
        self.assertEqual(
            subject('11-sgk-tin-hoc-11-dinh-huong-khoa-hoc-may-tinh'), 'Tin học')
        self.assertEqual(
            subject('12-sgk-chuyen-de-hoc-tap-tin-hoc-1'), 'Tin học')

    def test_hoa_hoc_that_van_nhan_dung(self):
        self.assertEqual(subject('12-sgk-hoa-hoc-12'), 'Hoá học')
        self.assertEqual(subject('10-sgk-chuyen-de-hoc-tap-hoa-hoc-10'), 'Hoá học')

    def test_khoa_hoc_tu_nhien_rieng_voi_khoa_hoc(self):
        self.assertEqual(subject('06-sgk-khoa-hoc-tu-nhien-6'), 'KHTN')
        self.assertEqual(subject('05-sgk-khoa-hoc-5'), 'Khoa học')

    def test_cac_mon_thuong(self):
        for book, want in (('10-sgk-toan-10-tap-hai', 'Toán'),
                           ('11-sgk-vat-li-11', 'Vật lí'),
                           ('10-sgk-sinh-hoc-10', 'Sinh học'),
                           ('08-sgk-cong-nghe-8', 'Công nghệ'),
                           ('12-sgk-am-nhac-12', 'Âm nhạc'),
                           ('04-sgk-lich-su-va-dia-li-4', 'Lịch sử')):
            self.assertEqual(subject(book), want, book)

    def test_khong_nhan_ra_thi_tra_MON_KHAC_chu_khong_doan(self):
        self.assertEqual(subject('09-sgk-mot-cuon-la'), 'môn khác')
        self.assertEqual(subject(''), 'môn khác')
        self.assertEqual(subject(None), 'môn khác')

    def test_KHONG_khop_chuoi_con_giua_doan(self):
        """«toantinh» không phải «toan». Khớp chuỗi con thì nhận nhầm."""
        self.assertEqual(subject('09-sgk-toantinh-abc'), 'môn khác')
