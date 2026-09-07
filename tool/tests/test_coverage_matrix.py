#!/usr/bin/env python3
"""Census toàn corpus — các tính chất KHÔNG được phép trôi.

Census sai nguy hiểm hơn census không có: nó biến một con số bịa thành cơ sở
để quyết định làm gì tiếp.

⚠ Test ở đây DỰNG LẤY mục lục của mình. Mục lục thật (`assets/pack/lesson-index-
g<N>.json`) được dựng tại máy và KHÔNG nằm trong git: một test đọc thẳng nó sẽ
xanh ở máy dev và đỏ trên CI — hoặc tệ hơn, XANH RỖNG vì không có dữ liệu nào
để khẳng định gì. Cả hai kiểu đều đã xảy ra ở lần chạy CI đầu của tệp này.
"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import coverage_matrix as cm  # noqa: E402

BOOK = '06-sgk-vi-du-6'


def _index(dirpath, grade=6, lessons=None):
    """Một mục lục tối thiểu đúng hình dạng thật: subjects → sách → lessons."""
    lessons = lessons if lessons is not None else [
        {'no': 1, 'title': 'Bài có tên', 'pageStart': 5},
        {'no': 2, 'title': None, 'pageStart': 9},          # mục lục thiếu tên
        {'no': 3, 'title': 'Trùng số', 'pageStart': 20},   # va chạm: cùng no…
        {'no': 3, 'title': 'Trùng số', 'pageStart': 40},   # …khác trang ⇒ BÀI KHÁC
    ]
    json.dump({'grade': grade, 'version': 'lesson-index-v2',
               'subjects': {'Ví dụ': [{'sourceDocumentId': BOOK, 'volume': None,
                                       'lessons': lessons}]}},
              open(os.path.join(dirpath, f'lesson-index-g{grade}.json'), 'w',
                   encoding='utf-8'), ensure_ascii=False)
    return dirpath


def _attach(dirpath, lessons, pages=60, book=BOOK):
    d = os.path.join(dirpath, 'attach')
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, f'{book}.json'), 'w', encoding='utf-8') as fh:
        json.dump({'book': book, 'grade': 6, 'lessons': lessons,
                   'pages': [{'page': i + 1} for i in range(pages)]}, fh, ensure_ascii=False)
    return dirpath


class MatrixTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = self.tmp.name
        self.addCleanup(self.tmp.cleanup)

    def test_denominator_is_the_canonical_toc_not_what_the_pipeline_produced(self):
        # Đo pipeline bằng mẫu số của chính pipeline là tự chấm điểm mình.
        rows = cm.canonical_lessons(_index(self.d))
        self.assertEqual(len(rows), 4, 'mẫu số = mọi bài trong mục lục, kể cả bài trùng số')
        self.assertEqual({r['book'] for r in rows}, {BOOK})

    def test_duplicate_toc_records_are_kept_not_silently_merged(self):
        # Trên corpus thật: 439 bản ghi va chạm dưới (book,no), trong đó 310 là
        # BÀI THẬT SỰ KHÁC NHAU. Gộp im lặng = giấu chúng đi để coverage đẹp hơn.
        rows = cm.canonical_lessons(_index(self.d))
        self.assertEqual(len([r for r in rows if r['no'] == 3]), 2)
        self.assertEqual({r['page_start'] for r in rows if r['no'] == 3}, {20, 40})

    def test_a_lesson_attach_never_reached_is_not_counted_readable(self):
        # Không có dải trang ⇒ không biết trẻ sẽ đọc gì ⇒ KHÔNG phải Level 1.
        _index(self.d); _attach(self.d, [])
        rows = cm.build(self.d, [], index_dir=self.d)
        self.assertEqual(len(rows), 4, 'test phải có dữ liệu để khẳng định, không xanh rỗng')
        self.assertFalse(any(r['L1'] for r in rows))
        self.assertTrue(all(cm.NO_RANGE in r['blockers'] for r in rows))

    def test_a_lesson_with_a_range_but_no_ocr_is_not_readable(self):
        # Dải trang trỏ vào sách không có OCR: gán được dải KHÔNG phải đọc được.
        _index(self.d)
        _attach(self.d, [{'number': 1, 'title': 'Bài có tên', 'page_pdf': 6,
                          'source': 'both', 'confidence': 0.95}])
        rows = cm.build(self.d, [], index_dir=self.d)
        r1 = [r for r in rows if r['no'] == 1][0]
        self.assertEqual(r1['chars'], 0)
        self.assertIn(cm.THIN, r1['blockers'])
        self.assertFalse(r1['L1'])

    def test_ambiguous_identity_blocks_level_1(self):
        # Hai bài dùng chung (book,no,pageStart) ⇒ không nói được trẻ mở cái nào.
        _index(self.d, lessons=[{'no': 7, 'title': 'A', 'pageStart': 5},
                                {'no': 7, 'title': 'B', 'pageStart': 5}])
        _attach(self.d, [])
        rows = cm.build(self.d, [], index_dir=self.d)
        self.assertTrue(all(cm.AMBIG in r['blockers'] for r in rows))
        self.assertFalse(any(r['L1'] for r in rows))

    def test_levels_are_nested_never_inverted(self):
        # L3 mà không L2 là một bài «dạy được nhưng không đọc được».
        _index(self.d); _attach(self.d, [])
        rows = cm.build(self.d, [], index_dir=self.d)
        self.assertTrue(rows)
        for r in rows:
            if r['L3']:
                self.assertTrue(r['L2'], r)
            if r['L2']:
                self.assertTrue(r['L1'], r)

    def test_title_read_from_the_page_fills_a_gap_the_toc_left(self):
        # 1.340 bài không có tên trong mục lục; attach đọc lại được 681 tên từ
        # CHÍNH TRANG SÁCH. Hai nguồn ấy không được lẫn vào nhau.
        _index(self.d)
        _attach(self.d, [{'number': 2, 'title': 'TÊN ĐỌC TỪ TRANG', 'page_pdf': 10,
                          'source': 'both', 'confidence': 0.95}])
        rows = cm.build(self.d, [], index_dir=self.d)
        r2 = [r for r in rows if r['no'] == 2][0]
        self.assertEqual(r2['title_resolved'], 'TÊN ĐỌC TỪ TRANG')
        self.assertEqual(r2['title_from'], 'page')
        r1 = [r for r in rows if r['no'] == 1][0]
        self.assertEqual(r1['title_from'], 'index')
        self.assertNotIn(cm.NO_TITLE, r2['blockers'])
