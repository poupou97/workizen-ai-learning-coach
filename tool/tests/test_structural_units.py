#!/usr/bin/env python3
"""ĐƠN VỊ CẤU TRÚC — corpus tự nói, không áp taxonomy trước.

Phép đo này quyết định KHÔNG cài đặt một mô hình đơn vị cấu trúc. Test giữ đúng
những chỗ nó dễ nói sai, vì một phép đo sai cũng dẫn tới một quyết định sai.
"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import structural_units as su  # noqa: E402


def _book(d, book, pages):
    """`pages` = {số trang: [dòng đầu trang]}"""
    os.makedirs(f'{d}/{book}', exist_ok=True)
    for pp, lines in pages.items():
        json.dump({'lines': [dict(text=t, x=0.1, y=0.05 + i * 0.03, w=0.5, h=0.02)
                             for i, t in enumerate(lines)]},
                  open(f'{d}/{book}/p{pp:03d}.json', 'w', encoding='utf-8'),
                  ensure_ascii=False)


class RunningHeaderTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def test_a_single_repeated_header_is_not_a_unit(self):
        # «TOÁN 5» ở chân MỌI trang — một số duy nhất, không thành dãy.
        _book(self.d, 'sach', {p: ['TOÁN 5', f'nội dung trang {p}'] for p in range(1, 12)})
        self.assertEqual(su.dominant_unit('sach', self.d), (None, 0))

    def test_a_header_repeated_ACROSS_pages_of_each_chapter_is_filtered(self):
        # Ca thật mà luật «mỗi số một trang» sinh ra để chặn: tiêu đề chạy mang
        # SỐ CHƯƠNG, lặp trên mọi trang của chương. Ba chương ⇒ ba số ⇒ đủ dài
        # để thành «dãy», nhưng mỗi số phủ nhiều trang nên nó KHÔNG đánh dấu
        # đơn vị nào — nó chỉ nói trang này thuộc chương nào.
        pages = {}
        for ch in (1, 2, 3):
            for k in range(5):
                pages[ch * 10 + k] = [f'CHỦ ĐỀ {ch}', 'nội dung']
        _book(self.d, 'sach', pages)
        self.assertEqual(su.dominant_unit('sach', self.d), (None, 0),
                         'mỗi số phủ 5 trang ⇒ tiêu đề chạy, không phải dấu đơn vị')

    def test_real_unit_markers_are_found(self):
        _book(self.d, 'sach', {1: ['BÀI 1 Mở đầu'], 5: ['BÀI 2 Tiếp theo'],
                               9: ['BÀI 3 Nữa'], 13: ['BÀI 4 Cuối']})
        w, n = su.dominant_unit('sach', self.d)
        self.assertEqual(w, 'BAI')
        self.assertEqual(n, 4)

    def test_diacritics_are_folded_including_D_with_stroke(self):
        # `Đ` không phân rã theo NFD — bỏ sót nó làm «CHỦ ĐỀ» trượt im lặng.
        _book(self.d, 'sach', {1: ['CHỦ ĐỀ 1'], 5: ['CHỦ ĐỀ 2'], 9: ['CHỦ ĐỀ 3']})
        self.assertEqual(su.dominant_unit('sach', self.d)[0], 'CHU DE')

    def test_too_few_units_is_not_a_pattern(self):
        _book(self.d, 'sach', {1: ['BÀI 1'], 5: ['BÀI 2']})
        self.assertEqual(su.dominant_unit('sach', self.d), (None, 0))

    def test_a_book_with_no_marker_returns_none_not_a_guess(self):
        # 159/238 sách thật rơi vào đây — đa số, và là phát hiện chính.
        _book(self.d, 'sach', {p: [f'một đoạn văn ở trang {p}'] for p in range(1, 9)})
        self.assertEqual(su.dominant_unit('sach', self.d), (None, 0))


class InterleavedTocTests(unittest.TestCase):
    def test_two_column_toc_read_as_one_sequence_is_detected(self):
        # HĐTN 1 thật: bài 1 ở trang 6 VÀ 7, bài 2 ở 9 và 14, bài 3 ở 15 và 22.
        lessons = [{'no': 1, 'pageStart': 6}, {'no': 1, 'pageStart': 7},
                   {'no': 2, 'pageStart': 9}, {'no': 2, 'pageStart': 14},
                   {'no': 3, 'pageStart': 15}, {'no': 3, 'pageStart': 22},
                   {'no': 4, 'pageStart': 17}, {'no': 4, 'pageStart': 32}]
        self.assertTrue(su.interleaved_toc(lessons))

    def test_a_normal_toc_is_not_flagged(self):
        self.assertFalse(su.interleaved_toc(
            [{'no': i, 'pageStart': i * 4} for i in range(1, 10)]))

    def test_duplicates_that_do_NOT_form_two_ordered_sequences(self):
        # Đủ 4 cặp trùng số, nhưng trang lộn xộn — đây là lỗi đọc mục lục,
        # KHÔNG phải bảng hai cột. Nhận nhầm thì ta "sửa" một thứ không tồn tại.
        self.assertFalse(su.interleaved_toc(
            [{'no': 1, 'pageStart': 30}, {'no': 1, 'pageStart': 31},
             {'no': 2, 'pageStart': 5}, {'no': 2, 'pageStart': 40},
             {'no': 3, 'pageStart': 60}, {'no': 3, 'pageStart': 12},
             {'no': 4, 'pageStart': 20}, {'no': 4, 'pageStart': 21}]))

    def test_a_few_duplicates_are_not_two_sequences(self):
        # Hai bài trùng số vì lỗi đọc mục lục KHÔNG phải mục lục hai cột.
        self.assertFalse(su.interleaved_toc(
            [{'no': 1, 'pageStart': 5}, {'no': 1, 'pageStart': 9},
             {'no': 2, 'pageStart': 12}]))

    def test_lessons_without_pages_do_not_create_a_false_pattern(self):
        self.assertFalse(su.interleaved_toc([{'no': i, 'pageStart': None}
                                             for i in range(1, 10)]))
