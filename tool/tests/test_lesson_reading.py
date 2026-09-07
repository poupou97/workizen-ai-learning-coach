#!/usr/bin/env python3
"""Nội dung đọc của bài — chỗ dễ đưa cho trẻ một trang chữ lộn nhất."""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import lesson_reading as lr  # noqa: E402


def line(text, x=0.1, y=0.5, w=0.6, h=0.02):
    return {'text': text, 'x': x, 'y': y, 'w': w, 'h': h, 'conf': 1}


def one_column(n=10):
    return [line(f'câu số {i} trong một đoạn văn dài', y=0.1 + i * 0.07) for i in range(n)]


def two_columns():
    left = [line(f'cột trái dòng {i} của một đoạn dài', x=0.08, y=0.15 + i * 0.09) for i in range(6)]
    right = [line(f'cột phải dòng {i} của một đoạn dài', x=0.55, y=0.15 + i * 0.09) for i in range(6)]
    return left + right


def table():
    """Bảng: nhiều ô NGẮN trải hai bên — KHÔNG được coi là hai cột văn bản."""
    return [line(f'ô {r}{c}', x=0.1 + c * 0.4, y=0.2 + r * 0.1, w=0.12)
            for r in range(6) for c in range(2)]


class ReadingOrderTests(unittest.TestCase):
    def test_two_text_flows_are_detected(self):
        self.assertTrue(lr.is_two_column(two_columns()))

    def test_a_table_is_not_mistaken_for_two_columns(self):
        # Xé một bảng ra làm hai cột làm nó nát hơn là để nguyên.
        self.assertFalse(lr.is_two_column(table()))

    def test_a_plain_page_is_single_flow(self):
        self.assertFalse(lr.is_two_column(one_column()))


class ExtractTests(unittest.TestCase):
    def setUp(self):
        self.pages = {}
        self._real = lr.page_lines
        lr.page_lines = lambda book, pp: self.pages.get(pp, None)
        self.addCleanup(lambda: setattr(lr, 'page_lines', self._real))

    def test_single_flow_lesson_is_served_verbatim(self):
        self.pages = {5: one_column(), 6: one_column()}
        d, why = lr.lesson_reading('x', 5, 6)
        self.assertIsNone(why)
        self.assertEqual([p['pagePdf'] for p in d['pages']], [5, 6])
        self.assertIn('câu số 0 trong một đoạn văn dài', d['pages'][0]['text'])

    def test_a_two_column_page_stops_the_whole_lesson(self):
        # Ghép theo y sẽ đan hai cột ⇒ trẻ đọc một câu ghép từ hai câu khác nhau.
        # Thà bài chưa mở được còn hơn bài mở ra chữ lộn.
        self.pages = {5: one_column(), 6: two_columns()}
        d, why = lr.lesson_reading('x', 5, 6)
        self.assertIsNone(d)
        self.assertEqual(why, 'READING_ORDER')

    def test_a_missing_ocr_page_stops_the_lesson(self):
        # Thiếu một trang giữa bài = đưa cho trẻ một bài thủng, không nói gì.
        self.pages = {5: one_column()}
        d, why = lr.lesson_reading('x', 5, 6)
        self.assertIsNone(d)
        self.assertEqual(why, 'OCR_MISSING')

    def test_no_range_is_refused(self):
        self.assertEqual(lr.lesson_reading('x', None, None)[1], 'SOURCE_RANGE')
        self.assertEqual(lr.lesson_reading('x', 9, 5)[1], 'SOURCE_RANGE')

    def test_page_number_and_running_header_are_dropped(self):
        hdr = 'KHOA HỌC TỰ NHIÊN 6'
        self.pages = {5: [line('61', x=0.9, y=0.97, w=0.03),
                          line(hdr, x=0.1, y=0.02, w=0.3)] + one_column(),
                      6: [line('62', x=0.9, y=0.97, w=0.03),
                          line(hdr, x=0.1, y=0.02, w=0.3)] + one_column()}
        d, _ = lr.lesson_reading('x', 5, 6)
        t = ' '.join(p['text'] for p in d['pages'])
        self.assertNotIn('61', t)
        self.assertNotIn(hdr, t, 'tiêu đề chạy lặp qua 2 trang ⇒ thuộc cuốn sách')
        self.assertIn('câu số 3 trong một đoạn văn dài', t, 'chữ của bài phải còn nguyên')

    def test_a_lesson_title_at_the_margin_is_NOT_dropped(self):
        # «TÁCH CHẤT KHỎI HỖN HỢP» nằm ở y≈0,058, sát dải mép, và chỉ có MỘT lần.
        # Cắt theo độ dài / theo vị trí sẽ xoá đúng thứ trẻ cần thấy đầu tiên.
        title = 'TÁCH CHẤT KHỎI HỖN HỢP'
        self.pages = {5: [line(title, x=0.25, y=0.058, w=0.51)] + one_column(),
                      6: one_column()}
        d, _ = lr.lesson_reading('x', 5, 6)
        self.assertIn(title, d['pages'][0]['text'])

    def test_an_empty_lesson_is_not_served_as_readable(self):
        self.pages = {5: [line('', y=0.5)]}
        self.assertEqual(lr.lesson_reading('x', 5, 5)[1], 'CONTENT_THIN')


class LessonStartTests(unittest.TestCase):
    def setUp(self):
        self.pages = {}
        self._real = lr.page_lines
        lr.page_lines = lambda book, pp: self.pages.get(pp)
        self.addCleanup(lambda: setattr(lr, 'page_lines', self._real))

    def test_content_that_starts_mid_lesson_is_refused(self):
        # Trẻ mở bài ra và đã ở giữa bài, mất phần mở đầu. 101 bài thật rơi vào đây.
        self.pages = {5: one_column()}
        d, why = lr.lesson_reading('x', 5, 5, title='Tách chất khỏi hỗn hợp')
        self.assertIsNone(d)
        self.assertEqual(why, 'LESSON_START_UNCONFIRMED')

    def test_content_that_opens_with_the_lesson_is_served(self):
        self.pages = {5: [line('TÁCH CHẤT KHỎI HỖN HỢP', y=0.06, w=0.5)] + one_column()}
        d, why = lr.lesson_reading('x', 5, 5, title='Tách chất khỏi hỗn hợp')
        self.assertIsNone(why)
        self.assertIn('TÁCH CHẤT', d['pages'][0]['text'])

    def test_a_short_title_is_matched_as_a_whole_phrase(self):
        # «Ôn tập» không có từ nào dài hơn 3 ký tự — luật theo token sẽ bỏ sót.
        self.assertIs(lr.starts_at_lesson('ÔN TẬP giữa kì', 'Ôn tập'), True)
        self.assertIs(lr.starts_at_lesson('Bài học về cây', 'Ôn tập'), False)

    def test_no_title_means_cannot_check_not_silently_pass(self):
        self.assertIsNone(lr.starts_at_lesson('bất kì', ''))
