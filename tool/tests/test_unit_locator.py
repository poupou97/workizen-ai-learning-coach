#!/usr/bin/env python3
"""TÌM DẢI TRANG khi mục lục không ghi trang.

«Mục lục không ghi trang» KHÔNG đồng nghĩa «sách không có bài ấy» — nhưng tìm nó
phải bằng bằng chứng, và phải chấp nhận rằng phần lớn sẽ không tìm được.
Đo được: 26/59 ca. Mỗi test dưới đây chốt một chỗ dễ nhận bừa.
"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import unit_locator as ul  # noqa: E402

BOOK = 'sach'


def line(text, y=0.10, x=0.15, w=0.5, h=0.02):
    return {'text': text, 'x': x, 'y': y, 'w': w, 'h': h}


class Fx(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        os.makedirs(f'{self.d}/{BOOK}', exist_ok=True)

    def page(self, n, lines):
        json.dump({'lines': lines},
                  open(f'{self.d}/{BOOK}/p{n:03d}.json', 'w', encoding='utf-8'),
                  ensure_ascii=False)

    def locate(self, title, number=12, titles=()):
        return ul.locate_start(BOOK, title, number, list(titles), ocr_dir=self.d)


class NameEvidenceTests(Fx):
    def test_one_page_opens_with_the_name(self):
        self.page(1, [line('Một trang khác')])
        self.page(5, [line('ĐỒ CHƠI CỦA CHÚNG EM', y=0.08)])
        self.assertEqual(self.locate('Đồ chơi của chúng em'), 5)

    def test_no_page_means_WITHHOLD(self):
        self.page(1, [line('Không liên quan gì')])
        self.assertIsNone(self.locate('Đồ chơi của chúng em'))

    def test_TWO_pages_with_the_name_and_no_number_means_WITHHOLD(self):
        # Không «chọn ứng viên tốt nhất»: hai trang cùng khớp thì ta không biết
        # trang nào là chỗ bắt đầu, và đoán sai thì trẻ mở nhầm bài.
        self.page(5, [line('ĐỒ CHƠI CỦA CHÚNG EM', y=0.08)])
        self.page(40, [line('ĐỒ CHƠI CỦA CHÚNG EM', y=0.08)])
        self.assertIsNone(self.locate('Đồ chơi của chúng em'))

    def test_a_name_in_the_LOWER_half_is_not_a_lesson_start(self):
        # Một bài mở ở ĐẦU trang, không ở giữa thân bài.
        self.page(5, [line('ĐỒ CHƠI CỦA CHÚNG EM', y=0.72)])
        self.assertIsNone(self.locate('Đồ chơi của chúng em'))

    def test_a_name_in_the_page_margin_is_a_running_header(self):
        self.page(5, [line('ĐỒ CHƠI CỦA CHÚNG EM', y=0.01)])
        self.assertIsNone(self.locate('Đồ chơi của chúng em'))

    def test_a_caption_carrying_the_phrase_is_not_a_start(self):
        self.page(5, [line('Hình 3. Đồ chơi của chúng em', y=0.08)])
        self.assertIsNone(self.locate('Đồ chơi của chúng em'))


class TocPageTests(Fx):
    def test_the_TOC_page_itself_is_not_a_lesson_start(self):
        # Trang mục lục CHỨA tên bài nhưng không phải chỗ bài bắt đầu.
        others = ['bài học về gia đình em', 'bài học về trường lớp thân yêu',
                  'bài học về quê hương đất nước']
        self.page(3, [line('MỤC LỤC', y=0.05)]
                  + [line(t, y=0.10 + i * 0.03) for i, t in enumerate(others)]
                  + [line('Đồ chơi của chúng em', y=0.22)])
        self.page(50, [line('ĐỒ CHƠI CỦA CHÚNG EM', y=0.08)])
        self.assertEqual(self.locate('Đồ chơi của chúng em', titles=others), 50)

    def test_without_the_TOC_rule_the_TOC_page_would_win(self):
        others = ['bài học về gia đình em', 'bài học về trường lớp thân yêu',
                  'bài học về quê hương đất nước']
        toc = [line(t, y=0.10 + i * 0.03) for i, t in enumerate(others)]
        self.assertTrue(ul.is_toc_page(toc, others))
        self.assertFalse(ul.is_toc_page([line('một trang thường')], others))


class NumberEvidenceTests(Fx):
    def test_the_number_SPLITS_a_tie_it_never_decides_alone(self):
        self.page(5, [line('ĐỒ CHƠI CỦA CHÚNG EM', y=0.08)])
        self.page(40, [line('ĐỒ CHƠI CỦA CHÚNG EM', y=0.08),
                       line('Bài 12', y=0.06)])
        self.assertEqual(self.locate('Đồ chơi của chúng em', number=12), 40)

    def test_number_alone_never_locates_anything(self):
        # «Bài 12» có ở mọi trang của bài 12 — một mình nó không chỉ ra chỗ mở.
        self.page(5, [line('Bài 12', y=0.06), line('Nội dung nào đó', y=0.2)])
        self.assertIsNone(self.locate('Một tên hoàn toàn khác', number=12))

    def test_TWO_pages_both_carrying_the_number_still_WITHHOLD(self):
        for p in (5, 40):
            self.page(p, [line('ĐỒ CHƠI CỦA CHÚNG EM', y=0.08),
                          line('Bài 12', y=0.06)])
        self.assertIsNone(self.locate('Đồ chơi của chúng em', number=12))

    def test_a_different_number_does_not_count(self):
        self.page(5, [line('ĐỒ CHƠI CỦA CHÚNG EM', y=0.08)])
        self.page(40, [line('ĐỒ CHƠI CỦA CHÚNG EM', y=0.08), line('Bài 13', y=0.06)])
        self.assertIsNone(self.locate('Đồ chơi của chúng em', number=12))


class EndTests(unittest.TestCase):
    def test_end_comes_from_the_next_confirmed_unit(self):
        self.assertEqual(ul.locate_end(10, [5, 20, 30], 99), 19)

    def test_end_is_the_last_page_when_nothing_follows(self):
        self.assertEqual(ul.locate_end(90, [5, 20], 99), 99)

    def test_a_one_page_unit_is_valid(self):
        self.assertEqual(ul.locate_end(21, [5, 20, 22], 99), 21)

    def test_an_end_before_the_start_is_refused(self):
        # Thà không có dải còn hơn một dải ngược — nó sẽ nuốt bài trước.
        self.assertIsNone(ul.locate_end(30, [5, 20, 25], 20))

    def test_the_end_never_swallows_the_next_unit(self):
        for nxt in (12, 40, 77):
            self.assertLess(ul.locate_end(10, [nxt], 99), nxt)
