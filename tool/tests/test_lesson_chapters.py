#!/usr/bin/env python3
"""ĐỊNH DANH BÀI — `(sách, số bài)` đã bị bác bỏ bằng dữ liệu.

Đo trên corpus: 593 bản ghi va chạm trên 154 khoá ở 45 sách; `volume` cứu được 0;
105/154 khoá có tiêu đề GIỐNG HỆT nhau. GDTC có «Bài 1» cho mỗi môn thể thao.

Mục tiêu là ĐỊNH DANH ĐÚNG, không phải TỈ LỆ KHỚP CAO. Sai bài nguy hiểm hơn
thiếu bài, nên mọi ca không đủ bằng chứng đều phải WITHHOLD.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import lesson_chapters as lc  # noqa: E402


def L(no, page):
    return {'no': no, 'pageStart': page}


OPENERS = [(11, 'ĐỘI HÌNH ĐỘI NGŨ'), (28, 'BÀI TẬP THỂ DỤC'),
           (41, 'TƯ THẾ VÀ KĨ NĂNG VẬN ĐỘNG CƠ BẢN')]


class FoldTests(unittest.TestCase):
    def test_D_with_stroke_folds_to_D(self):
        # `Đ` (U+0110) KHÔNG phân rã theo NFD. Bỏ sót nó làm phép đo trượt IM
        # LẶNG: lần đo đầu báo 31,9% thay vì 57,7% đúng vì lỗi này.
        self.assertIn('CHU DE', lc.fold('Chủ đề'))
        self.assertIn('CHU DE', lc.fold('CHỦ ĐỀ'))
        self.assertIn('CHU DE', lc.fold('CHÚ DE'))   # OCR đọc sai dấu

    def test_marker_matches_the_real_ocr_spellings(self):
        for s in ('CHỦ ĐỀ', 'CHÚ DE', 'CHỦ ĐE', 'CHỦ ĐẾ', 'PHẦN', 'CHƯƠNG'):
            self.assertTrue(lc.MARKER.search(lc.fold(s)), s)

    def test_marker_does_not_fire_on_ordinary_words(self):
        for s in ('CHUNG TA', 'PHA MAU', 'CHUYEN DE HOC TAP'):
            self.assertIsNone(lc.MARKER.search(lc.fold(s)), s)


class ChapterAtTests(unittest.TestCase):
    def test_page_takes_the_nearest_opener_before_it(self):
        self.assertEqual(lc.chapter_at(OPENERS, 20), 'ĐỘI HÌNH ĐỘI NGŨ')
        self.assertEqual(lc.chapter_at(OPENERS, 41), 'TƯ THẾ VÀ KĨ NĂNG VẬN ĐỘNG CƠ BẢN')

    def test_a_page_before_every_chapter_gets_none_not_a_guess(self):
        self.assertIsNone(lc.chapter_at(OPENERS, 3))

    def test_one_page_of_slack_between_opener_and_lesson(self):
        # Trang mở chương và trang mở bài lệch nhau một trang là có thật.
        self.assertEqual(lc.chapter_at(OPENERS, 10), 'ĐỘI HÌNH ĐỘI NGŨ')


class ResolveTests(unittest.TestCase):
    def test_same_number_in_different_chapters_are_different_lessons(self):
        r, w, _ = lc.resolve_group([L(1, 10), L(1, 27), L(1, 40)], OPENERS, 1)
        self.assertEqual(len(r), 3)
        self.assertEqual({c for c, _ in r},
                         {'ĐỘI HÌNH ĐỘI NGŨ', 'BÀI TẬP THỂ DỤC',
                          'TƯ THẾ VÀ KĨ NĂNG VẬN ĐỘNG CƠ BẢN'})
        self.assertEqual(w, [])

    def test_same_chapter_same_page_is_one_lesson_read_twice(self):
        # Mục lục đọc trùng một dòng ⇒ gộp, không phải hai bài.
        r, w, _ = lc.resolve_group([L(1, 10), L(1, 10)], OPENERS, 1)
        self.assertEqual(len(r), 1)
        self.assertEqual(w, [])

    def test_same_chapter_different_pages_is_WITHHELD(self):
        # Vẫn là hai bài khác nhau mà chương không phân biệt được ⇒ giữ lại cả
        # nhóm. Chọn bừa một cái là cho trẻ mở nhầm bài.
        r, w, why = lc.resolve_group([L(1, 12), L(1, 20)], OPENERS, 1)
        self.assertEqual(r, [])
        self.assertEqual(len(w), 2)
        self.assertEqual(why, 'CHAPTER_NOT_DISCRIMINATING')

    def test_missing_chapter_for_any_record_withholds_the_whole_group(self):
        # Một bản ghi không có chương thì cả nhóm chưa tách được.
        r, w, why = lc.resolve_group([L(1, 3), L(1, 27)], OPENERS, 1)
        self.assertEqual(r, [])
        self.assertEqual(len(w), 2)
        self.assertEqual(why, 'NO_CHAPTER')

    def test_missing_page_start_withholds(self):
        r, w, why = lc.resolve_group([L(1, None), L(1, 27)], OPENERS, 1)
        self.assertEqual(w and why, 'NO_CHAPTER')

    def test_no_offset_withholds_rather_than_guessing(self):
        r, w, why = lc.resolve_group([L(1, 10), L(1, 27)], OPENERS, None)
        self.assertEqual(r, [])
        self.assertEqual(why, 'NO_CHAPTER')

    def test_a_book_with_no_chapter_markers_withholds_everything(self):
        r, w, why = lc.resolve_group([L(1, 10), L(1, 27)], [], 1)
        self.assertEqual(r, [])
        self.assertEqual(len(w), 2)


class OpenerTests(unittest.TestCase):
    def test_chapter_name_is_the_books_own_words(self):
        import json
        import tempfile
        d = tempfile.mkdtemp()
        os.makedirs(f'{d}/sach', exist_ok=True)
        def page(n, lines):
            json.dump({'lines': [dict(text=t, x=0.1, y=0.05 + i * 0.03, w=0.5, h=0.02)
                                 for i, t in enumerate(lines)]},
                      open(f'{d}/sach/p{n:03d}.json', 'w', encoding='utf-8'),
                      ensure_ascii=False)
        page(1, ['CHỦ ĐỀ', 'ĐỘI HÌNH ĐỘI NGŨ', '1', 'BÀI 1'])
        page(2, ['một đoạn văn bình thường không có dấu chương nào'])
        o = lc.chapter_openers('sach', ocr_dir=d)
        self.assertEqual(o, [(1, 'ĐỘI HÌNH ĐỘI NGŨ')],
                         'tên chương phải là chữ của sách, và trang thường không được tính')
