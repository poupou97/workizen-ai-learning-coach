#!/usr/bin/env python3
"""Lệnh 60 §6 — QUOTE phải nối được tới NGƯỜI, để chân dung có đường tới sản phẩm.

Chạy:  python3 -m unittest discover -s tool/tests -v

Chuỗi sản phẩm cần: QUOTE đã duyệt → NGƯỜI đã duyệt → CHÂN DUNG đã duyệt →
Quote Card. Nó đứt ở mắt đầu: mục QUOTE mang `person` là chuỗi tên, không bao
giờ mang `personId`, nên `PersonPortraits.forPerson()` luôn nhận null.

⚠ Trên corpus hôm nay mắt xích này nối được **0** mục: 0/13 tên trong trích dẫn
khớp 74 người canonical — hai tập RỜI NHAU. Nghĩa là nếu chỉ chạy trên dữ liệu
thật thì cơ chế này KHÔNG BAO GIỜ được kiểm: mẫu số bằng 0, và một khẳng định
trên mẫu số 0 thì không chứng minh điều gì (đúng bài học WAL-223).

Nên test này tự dựng mẫu số khác 0."""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'stories'))
from verify_stories import link_person_refs, slug  # noqa: E402


def item(typ, **kw):
    return dict(type=typ, source=dict(sourceDocumentId='d', pagePdf=1), **kw)


class LinkTests(unittest.TestCase):
    def setUp(self):
        self.canon = {slug('Thạch Lam'): {'canonicalName': 'Thạch Lam'}}

    def test_quote_naming_a_known_person_gets_that_personId(self):
        items = [item('QUOTE', person='Thạch Lam', quote='…')]
        self.assertEqual(link_person_refs(items, self.canon), 1)
        self.assertEqual(items[0]['personId'], slug('Thạch Lam'))

    def test_link_survives_whitespace_and_case(self):
        items = [item('QUOTE', person='  thạch lam ', quote='…')]
        self.assertEqual(link_person_refs(items, self.canon), 1)

    def test_unknown_person_is_left_NULL_not_invented(self):
        # ⭐⭐ Một cái tên đứng cạnh câu trích là lời DẪN NGUỒN, không phải hồ sơ
        # nhân vật đã xác minh. Tạo người từ đó là bịa ra thực thể.
        items = [item('QUOTE', person='Hồ Chí Minh', quote='…')]
        self.assertEqual(link_person_refs(items, self.canon), 0)
        self.assertIsNone(items[0].get('personId'))
        self.assertNotIn(slug('Hồ Chí Minh'), self.canon,
                         'sổ canonical bị thêm người từ một dòng trích dẫn')

    def test_person_items_are_left_alone(self):
        # PERSON đã có personId từ entity resolution — không đè lên.
        items = [item('PERSON', person='Thạch Lam', personId='p:khac')]
        self.assertEqual(link_person_refs(items, self.canon), 0)
        self.assertEqual(items[0]['personId'], 'p:khac')

    def test_item_without_a_person_name_is_untouched(self):
        items = [item('EVENT', year=1945)]
        self.assertEqual(link_person_refs(items, self.canon), 0)
        self.assertIsNone(items[0].get('personId'))

    def test_other_types_link_too_not_just_quotes(self):
        # INVENTION_DISCOVERY cũng mang `person`; chuỗi chân dung áp dụng chung.
        items = [item('INVENTION_DISCOVERY', person='Thạch Lam')]
        self.assertEqual(link_person_refs(items, self.canon), 1)
