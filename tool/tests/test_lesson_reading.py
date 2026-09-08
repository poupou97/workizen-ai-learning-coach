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


# Giãn dòng THẬT trong sách ≈ 1,2–1,5 lần chiều cao dòng (đo trên OCR: h≈0,019,
# bước y≈0,017–0,025). Fixture giãn quá rộng sẽ làm mọi dòng thành khối riêng và
# test đo một thứ không tồn tại trong sách.
LH = 0.02
STEP = 0.025


def one_column(n=10):
    return [line(f'câu số {i} trong một đoạn văn dài', y=0.1 + i * STEP) for i in range(n)]


def two_columns(n=12):
    # Hai cột THẬT: mỗi cột rộng ~0,36 và KHÔNG chồng lên nhau theo x. Fixture
    # cột rộng 0,6 sẽ chồng nhau — đó là một cột bị tách đôi, không phải hai cột.
    left = [line(f'cột trái dòng {i} của một đoạn dài', x=0.08, y=0.15 + i * STEP, w=0.36)
            for i in range(n)]
    right = [line(f'cột phải dòng {i} của một đoạn dài', x=0.55, y=0.15 + i * STEP, w=0.36)
             for i in range(n)]
    return left + right


def table():
    """Bảng: nhiều ô NGẮN trải hai bên — KHÔNG được coi là hai cột văn bản."""
    return [line(f'ô {r}{c}', x=0.1 + c * 0.4, y=0.2 + r * 0.1, w=0.12)
            for r in range(6) for c in range(2)]


class ReadingOrderTests(unittest.TestCase):
    def test_two_text_flows_are_detected(self):
        # Vẫn đo được bố cục (census dùng), nhưng KHÔNG còn dùng để từ chối bài.
        self.assertTrue(lr.is_two_column(two_columns()))

    def test_blocks_separate_a_narrow_side_note_from_the_body(self):
        body = [line('thân bài dòng dài ở bên trái', x=0.12, y=0.1 + i * STEP, w=0.49)
                for i in range(5)]
        note = [line('khung phụ hẹp bên phải', x=0.66, y=0.11 + i * STEP, w=0.22)
                for i in range(5)]
        bs = lr.blocks(body + note)
        self.assertGreaterEqual(len(bs), 2, 'thân bài và khung phụ phải là hai khối')
        for b in bs:
            xs = {round(l['x'], 2) for l in b}
            self.assertLessEqual(len(xs), 2, 'một khối không được trộn hai cột')

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

    def test_two_columns_are_read_in_order_not_interleaved(self):
        # Ghép theo y đan hai cột ⇒ trẻ đọc một câu ghép từ hai câu khác nhau.
        # Máy thật đã cho ra đúng lỗi ấy. Nay đọc HẾT cột trái rồi mới sang phải.
        self.pages = {5: two_columns()}
        d, why = lr.lesson_reading('x', 5, 5)
        self.assertIsNone(why)
        t = d['pages'][0]['text']
        last_left = t.index('cột trái dòng 11')
        first_right = t.index('cột phải dòng 0')
        self.assertLess(last_left, first_right,
                        'cột trái phải xong hẳn TRƯỚC khi sang cột phải')

    def test_a_side_note_does_not_split_a_body_sentence(self):
        # Ca thật trên Nokia (Công nghệ 6 Bài 1): khung niên biểu rộng 0,22 —
        # HẸP hơn mọi ngưỡng «dòng dài» — chen vào giữa câu thân bài.
        body = [line('Nhà ở là công trình được xây dựng với mục đích',
                     x=0.124, y=0.093 + i * 0.019, w=0.49) for i in range(6)]
        note = [line('Khoảng tám nghìn năm trước con người',
                     x=0.659, y=0.112 + i * 0.017, w=0.222) for i in range(6)]
        self.pages = {5: body + note}
        d, _ = lr.lesson_reading('x', 5, 5)
        t = d['pages'][0]['text']
        self.assertLess(t.rindex('mục đích'), t.index('Khoảng tám nghìn'),
                        'thân bài phải xong trước khi tới khung phụ')

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


class ContentStreamTests(unittest.TestCase):
    """Dòng nội dung là ĐƯỜNG ĐỌC THỨ HAI — nó có thể hỏng lại theo đúng kiểu mà
    chuỗi chữ phẳng đã được sửa. Máy thật đã bắt đúng chuyện đó một lần."""

    def setUp(self):
        self.pages = {}
        self._real = lr.page_lines
        lr.page_lines = lambda book, pp: self.pages.get(pp)
        self.addCleanup(lambda: setattr(lr, 'page_lines', self._real))

    def test_paragraph_order_matches_the_flat_text(self):
        # Hai đường đọc phải kể CÙNG một câu chuyện. Nếu lệch thì đường nào đúng?
        # Đây là bất biến giữ cho dòng nội dung không trôi khỏi chuỗi chữ đã sửa
        # ở #141 — một đường đọc thứ hai có thể hỏng lại theo đúng kiểu cũ.
        self.pages = {5: one_column(), 6: two_columns()}
        d, _ = lr.lesson_reading('x', 5, 6)
        for p in d['pages']:
            self.assertEqual(' '.join(q['text'] for q in p['paragraphs']), p['text'])


class UnitStartSearchTests(unittest.TestCase):
    """Tìm trang mở THẬT của đơn vị — hai họ lớn nhất của census dải trang.

    Census 270 ca: nguyên nhân chính KHÔNG phải offset (offset còn không ổn định
    trong cùng một cuốn). Hai họ lớn nhất là «mục lục ghi PHẦN CON của bài» (51)
    và «lệch đúng một trang» (40); cả hai giải bằng cùng một luật.
    """

    def setUp(self):
        self.pages = {}
        self._real = lr.page_lines
        lr.page_lines = lambda book, pp: self.pages.get(pp)
        self.addCleanup(lambda: setattr(lr, 'page_lines', self._real))

    def _titled(self, title):
        return [line(title, y=0.06, w=0.5)] + one_column()

    def test_sub_section_starting_INSIDE_the_range_is_found(self):
        # Ca thật TV5: dải bài mở ở trang khác, mục «Luyện từ và câu» ở trong.
        self.pages = {5: one_column(), 6: one_column(),
                      7: self._titled('LUYỆN TỪ VÀ CÂU LIÊN KẾT CÂU')}
        d, why = lr.lesson_reading('x', 5, 7, title='Luyện từ và câu: Liên kết câu')
        self.assertIsNone(why)
        self.assertEqual(d['pagePdfStart'], 7)

    def test_off_by_one_before_the_range_is_found(self):
        self.pages = {4: self._titled('TÁCH CHẤT KHỎI HỖN HỢP'),
                      5: one_column(), 6: one_column()}
        d, why = lr.lesson_reading('x', 5, 6, title='Tách chất khỏi hỗn hợp')
        self.assertIsNone(why)
        self.assertEqual(d['pagePdfStart'], 4)

    def test_TWO_matching_pages_means_WITHHOLD(self):
        # Nhiều chỗ khớp ⇒ không biết chỗ nào là mở đầu. Chọn cái đầu là ĐOÁN,
        # và đoán sai thì trẻ đọc nhầm chỗ.
        self.pages = {5: one_column(),
                      6: self._titled('ÔN TẬP CHƯƠNG MỘT'),
                      7: self._titled('ÔN TẬP CHƯƠNG MỘT')}
        d, why = lr.lesson_reading('x', 5, 7, title='Ôn tập chương một')
        self.assertIsNone(d)
        self.assertEqual(why, 'LESSON_START_UNCONFIRMED')

    def test_no_matching_page_anywhere_means_WITHHOLD(self):
        self.pages = {5: one_column(), 6: one_column()}
        d, why = lr.lesson_reading('x', 5, 6, title='Một bài không có trên trang')
        self.assertIsNone(d)
        self.assertEqual(why, 'LESSON_START_UNCONFIRMED')

    def test_search_never_runs_past_the_slack_window(self):
        # Trang khớp nằm xa hơn ±2 ⇒ KHÔNG nhận: nó thuộc bài khác.
        self.pages = {1: self._titled('TÁCH CHẤT KHỎI HỖN HỢP'),
                      5: one_column(), 6: one_column()}
        d, why = lr.lesson_reading('x', 5, 6, title='Tách chất khỏi hỗn hợp')
        self.assertIsNone(d)
        self.assertEqual(why, 'LESSON_START_UNCONFIRMED')

    def test_the_shifted_start_never_passes_the_end_of_the_range(self):
        # Dịch tới sau trang cuối nghĩa là đã sang bài khác.
        self.pages = {5: one_column(), 6: one_column(),
                      7: self._titled('TÁCH CHẤT KHỎI HỖN HỢP')}
        d, why = lr.lesson_reading('x', 5, 6, title='Tách chất khỏi hỗn hợp')
        self.assertIsNone(d, 'trang khớp nằm NGOÀI dải ⇒ không nhận')

    def test_a_found_start_is_re_verified_on_the_full_reading(self):
        # Phép dò chỉ nhìn 10 dòng đầu; dòng đọc đầy đủ mới là thứ trẻ thấy.
        # Trang khớp ⇒ nhận, và nội dung trả về PHẢI mở đúng bằng tên ấy.
        self.pages = {5: one_column(), 6: self._titled('TÁCH CHẤT KHỎI HỖN HỢP')}
        d, why = lr.lesson_reading('x', 5, 6, title='Tách chất khỏi hỗn hợp')
        self.assertIsNone(why)
        self.assertTrue(d['pages'][0]['text'].startswith('TÁCH CHẤT'))

    def test_TWO_matches_in_the_slack_window_also_WITHHOLD(self):
        # Ngoài dải cũng vậy: hai chỗ khớp thì không chỗ nào chứng minh được nó
        # là mở đầu. Luật «duy nhất» phải áp cho cả vùng nới, không chỉ trong dải.
        self.pages = {3: self._titled('TÁCH CHẤT KHỎI HỖN HỢP'),
                      4: self._titled('TÁCH CHẤT KHỎI HỖN HỢP'),
                      5: one_column(), 6: one_column()}
        d, why = lr.lesson_reading('x', 5, 6, title='Tách chất khỏi hỗn hợp')
        self.assertIsNone(d)
        self.assertEqual(why, 'LESSON_START_UNCONFIRMED')
