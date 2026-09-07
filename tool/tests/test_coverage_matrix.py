#!/usr/bin/env python3
"""Census toàn corpus — các tính chất KHÔNG được phép trôi.

Census sai nguy hiểm hơn census không có: nó biến một con số bịa thành cơ sở
để quyết định làm gì tiếp. Bốn tính chất dưới đây là chỗ nó dễ nói dối nhất.
"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import coverage_matrix as cm  # noqa: E402


def _attach(tmp, book, lessons, pages=40):
    d = os.path.join(tmp, 'attach')
    os.makedirs(d, exist_ok=True)
    json.dump({'book': book, 'grade': 6, 'lessons': lessons,
               'pages': [{'page': i + 1} for i in range(pages)]},
              open(os.path.join(d, f'{book}.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    return tmp


class MatrixTests(unittest.TestCase):
    def test_denominator_is_the_canonical_toc_not_what_the_pipeline_produced(self):
        # Đo pipeline bằng mẫu số của chính pipeline là tự chấm điểm mình.
        rows = cm.canonical_lessons()
        self.assertGreater(len(rows), 3000)
        books = {r['book'] for r in rows}
        self.assertGreater(len(books), 200)
        self.assertEqual({r['grade'] for r in rows}, set(range(1, 13)),
                         'mẫu số phải phủ đủ lớp 1–12')

    def test_duplicate_toc_records_are_kept_not_silently_merged(self):
        # 439 bản ghi va chạm dưới (book, no). Gộp im lặng = giấu 310 bài THẬT.
        rows = cm.canonical_lessons()
        keys = [(r['book'], r['no']) for r in rows]
        self.assertGreater(len(rows), len(set(keys)),
                           'va chạm (book,no) phải còn nhìn thấy được trong mẫu số')

    def test_a_lesson_attach_never_reached_is_not_counted_readable(self):
        # Không có dải trang ⇒ không thể biết trẻ sẽ đọc gì ⇒ KHÔNG phải Level 1.
        with tempfile.TemporaryDirectory() as tmp:
            _attach(tmp, 'sach-khong-co-that', [])
            rows = cm.build(tmp, [])
            hit = [r for r in rows if not r['page_pdf']]
            self.assertTrue(hit)
            self.assertFalse(any(r['L1'] for r in hit))
            self.assertTrue(all(cm.NO_RANGE in r['blockers'] for r in hit))

    def test_levels_are_nested_never_inverted(self):
        # L3 mà không L2, hay L2 mà không L1, là một bài «dạy được nhưng không đọc được».
        with tempfile.TemporaryDirectory() as tmp:
            _attach(tmp, 'x', [])
            for r in cm.build(tmp, []):
                if r['L3']:
                    self.assertTrue(r['L2'], r)
                if r['L2']:
                    self.assertTrue(r['L1'], r)

    def test_title_read_from_the_page_is_recorded_as_such(self):
        # Tiêu đề lấy từ TRANG SÁCH và tiêu đề lấy từ MỤC LỤC không được lẫn:
        # cái sau là dữ liệu đã có, cái trước là điều ta vừa khôi phục được.
        with tempfile.TemporaryDirectory() as tmp:
            _attach(tmp, 'x', [])
            rows = cm.build(tmp, [])
            self.assertTrue({r['title_from'] for r in rows} <= {'index', 'page', None})
            for r in rows:
                if r['title_from'] == 'index':
                    self.assertTrue(r['title'], 'nói lấy từ index thì index phải có chữ')
