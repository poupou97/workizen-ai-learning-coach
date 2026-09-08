#!/usr/bin/env python3
"""NHÃN PHÂN BIỆT sách trùng tên — đọc từ bìa, xác minh chéo với định danh."""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'ui'))
import book_variant as bv  # noqa: E402


def _cover(d, book, lines):
    os.makedirs(f'{d}/{book}', exist_ok=True)
    json.dump({'lines': [dict(text=t, x=0.2, y=0.1 + i * 0.05, w=0.5, h=0.03)
                         for i, t in enumerate(lines)]},
              open(f'{d}/{book}/p001.json', 'w', encoding='utf-8'), ensure_ascii=False)


class VariantTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def test_cover_line_matching_the_identity_is_accepted(self):
        b = '11-sgk-mi-thuat-11-thiet-ke-thoi-trang'
        _cover(self.d, b, ['MĨ THUẬT', '11', 'THIẾT KẾ THỜI TRANG'])
        self.assertEqual(bv.variant_label(b, self.d), 'THIẾT KẾ THỜI TRANG')

    def test_a_cover_line_that_matches_only_PART_is_refused(self):
        # Khớp một nửa không chứng minh được dòng ấy là tên của CUỐN NÀY.
        b = '11-sgk-mi-thuat-11-thiet-ke-thoi-trang'
        _cover(self.d, b, ['MĨ THUẬT', 'THIẾT KẾ'])
        self.assertIsNone(bv.variant_label(b, self.d))

    def test_no_cover_evidence_means_no_label(self):
        # Thà để hai cuốn trùng nhãn còn hơn dán một cái tên không kiểm được.
        b = '11-sgk-mi-thuat-11-hoi-hoa'
        _cover(self.d, b, ['MĨ THUẬT', '11', 'Fon EE', 'KẾT NỐC'])
        self.assertIsNone(bv.variant_label(b, self.d))

    def test_diacritics_come_from_the_book_not_from_the_slug(self):
        # Định danh viết «hoi-hoa»; sách in «HỘI HOẠ». Máy KHÔNG được tự thêm dấu.
        b = '11-sgk-mi-thuat-11-hoi-hoa'
        _cover(self.d, b, ['MĨ THUẬT', 'HỘI HOẠ'])
        self.assertEqual(bv.variant_label(b, self.d), 'HỘI HOẠ')

    def test_only_books_that_collide_get_a_label(self):
        # Thêm chữ vào chỗ không cần chỉ làm giá sách ồn hơn.
        books = [
            {'sourceDocumentId': '11-sgk-mi-thuat-11-hoi-hoa',
             'title': 'Mĩ thuật 11', 'volumeLabel': None},
            {'sourceDocumentId': '11-sgk-mi-thuat-11-kien-truc',
             'title': 'Mĩ thuật 11', 'volumeLabel': None},
            {'sourceDocumentId': '11-sgk-vat-li-11', 'title': 'Vật lí 11',
             'volumeLabel': None},
        ]
        _cover(self.d, books[0]['sourceDocumentId'], ['HỘI HOẠ'])
        _cover(self.d, books[1]['sourceDocumentId'], ['KIẾN TRÚC'])
        _cover(self.d, books[2]['sourceDocumentId'], ['VẬT LÍ 11'])
        out = bv.label_variants(books, self.d)
        self.assertEqual(set(out), {books[0]['sourceDocumentId'],
                                    books[1]['sourceDocumentId']})

    def test_a_book_id_that_does_not_parse_gets_no_label(self):
        self.assertEqual(bv.distinguishing_words('linh-tinh'), set())
        self.assertIsNone(bv.variant_label('linh-tinh', self.d))
