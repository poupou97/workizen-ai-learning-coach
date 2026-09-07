#!/usr/bin/env python3
"""Một THỨ không được thành một NGƯỜI trong «Danh nhân».

Chạy:  python3 -m unittest discover -s tool/tests -v

Bốn ca đo được trên corpus thật, hai trong số đó ĐANG tới tay trẻ (nằm trong
21 người của pack):

  «Tượng Hoàng đế Sác-lơ-ma-nhơ (742–814)»  chú thích ảnh — một BỨC TƯỢNG
  «Xuân Phái Bùi Xuân Phái (1920–1988)»     OCR dính caption vào thân bài
  «nhà văn Đan Mạch»                        QUỐC TỊCH đi sau vai
  «ở Thăng Long (1527–1592)»                ĐỊA DANH trước khoảng năm"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'stories'))
import mine_stories as ms  # noqa: E402


class CleanNameTests(unittest.TestCase):
    def test_statue_of_a_person_is_not_the_person(self):
        self.assertEqual(ms.clean_name('Tượng Hoàng đế Sác-lơ-ma-nhơ'),
                         'Hoàng đế Sác-lơ-ma-nhơ')

    def test_other_depiction_nouns(self):
        for pre in ('Chân dung', 'Bức tranh', 'Ảnh', 'Hình'):
            self.assertEqual(ms.clean_name(f'{pre} Nguyễn Trãi'), 'Nguyễn Trãi')

    def test_ocr_doubled_name_collapses(self):
        # nguồn thật: «hoạ sĩ Bùi Xuân Phái Bùi Xuân Phái (1920 - 1988)»
        self.assertEqual(ms.clean_name('Bùi Xuân Phái Bùi Xuân Phái'),
                         'Bùi Xuân Phái')

    def test_offset_doubled_capture_collapses(self):
        # bản bắt lệch của cùng câu ấy: prefix == suffix ⇒ bỏ prefix
        self.assertEqual(ms.clean_name('Xuân Phái Bùi Xuân Phái'),
                         'Bùi Xuân Phái')

    def test_a_normal_name_is_untouched(self):
        for n in ('Thạch Lam', 'Lê Thánh Tông', 'Han Cri-xti-an An-đéc-xen',
                  'Ludwig van Beethoven'):
            self.assertEqual(ms.clean_name(n), n)

    def test_a_name_that_merely_repeats_a_word_is_untouched(self):
        # «Trần Trần» không phải kiểu lặp cả cụm — đừng cắt bừa
        self.assertEqual(ms.clean_name('Nguyễn Văn Nguyễn'),
                         'Nguyễn Văn Nguyễn')


class EntityTypeTests(unittest.TestCase):
    def test_countries_are_rejected(self):
        for c in ('Đan Mạch', 'Việt Nam', 'Pháp', 'Nhật Bản', 'Hy Lạp'):
            self.assertTrue(ms.COUNTRYISH.match(c), c)

    def test_real_people_are_not_mistaken_for_countries(self):
        for n in ('Thạch Lam', 'Nguyễn Trãi', 'Lê Văn Hưu', 'Tô Hoài'):
            self.assertFalse(ms.COUNTRYISH.match(n), n)

    def test_locative_before_a_name_marks_a_place(self):
        for pre in ('trong thời gian ở ', 'tại ', 'kinh đô ', 'thành phố '):
            self.assertTrue(ms.LOCATIVE.search(pre), pre)

    def test_ordinary_text_before_a_name_is_not_locative(self):
        for pre in ('nhà văn ', 'Theo ', 'của hoạ sĩ ', 'tác giả '):
            self.assertFalse(ms.LOCATIVE.search(pre), pre)
