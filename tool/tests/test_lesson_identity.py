#!/usr/bin/env python3
"""Round 6 · WS-A (A2) — tests for SourceLessonRecord vs CanonicalLessonIdentity.

`all-lessons.csv` has 3,679 rows and 3,240 distinct `(sourceDocumentId, lessonNo)` keys, and the
Founder has approved neither as the count of unique canonical lessons. These tests pin the rule that
decides between them: two rows that share a key are the SAME lesson only when they also share the
printed page they start on. Anything else is a key collision — «Bài 1» printed seven times in one
GDTC book, once per chủ đề, is seven lessons and not one.

Run:  python3 -m unittest discover -s tool/tests -v
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus', 'accounting'))
import lesson_identity as LI  # noqa: E402


class ClassifyTests(unittest.TestCase):
    def _r(self, no, page, title=None):
        return dict(book='b', lessonNo=no, pageStart=page, title=title, grade=1, subject='GDTC')

    def test_same_number_same_page_same_title_is_a_true_duplicate(self):
        cls, _ = LI.classify_group([self._r(1, 10, 'Chạy'), self._r(1, 10, 'Chạy')])
        self.assertEqual(cls, 'true_duplicate')

    def test_same_number_different_pages_is_a_key_collision_not_a_duplicate(self):
        """The GDTC shape: printed numbering restarts inside every chủ đề."""
        cls, ev = LI.classify_group([self._r(1, 10), self._r(1, 27), self._r(1, 40)])
        self.assertEqual(cls, 'key_collision')
        self.assertIn('restarts', ev)

    def test_a_group_that_repeats_AND_collides_is_reported_as_mixed(self):
        cls, _ = LI.classify_group([self._r(1, 10), self._r(1, 10), self._r(1, 27)])
        self.assertEqual(cls, 'mixed')

    def test_no_page_and_no_title_is_unverifiable_never_silently_a_duplicate(self):
        cls, ev = LI.classify_group([self._r(1, None), self._r(1, None)])
        self.assertEqual(cls, 'unverifiable')
        self.assertIn('neither', ev)

    def test_two_titles_under_one_number_and_no_page_are_kept_apart(self):
        """Real corpus case, GDTC 8 Bài 1: «Bài thể dục nhịp điệu» and «Kĩ thuật đá bóng bằng mu
        ngoài» share a number and have no pageStart. Collapsing them would delete a lesson."""
        cls, _ = LI.classify_group([self._r(1, None, 'Bài thể dục nhịp điệu'),
                                    self._r(1, None, 'Kĩ thuật đá bóng bằng mu ngoài')])
        self.assertEqual(cls, 'key_collision')


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='ws-a-identity-')
        self.struct = os.path.join(self.tmp, 'structure.json')
        self.csv = os.path.join(self.tmp, 'all-lessons.csv')
        json.dump({'schemaVersion': 1, 'documents': [
            {'sourceDocumentId': 'x', 'grade': 1, 'subject': 'GDTC', 'docType': 'SGK',
             'structureStatus': 'OK', 'lessons': [
                 {'number': 1, 'title': None, 'pageStart': 10},
                 {'number': 1, 'title': None, 'pageStart': 10},     # true duplicate
                 {'number': 1, 'title': None, 'pageStart': 27},     # key collision
                 {'number': 2, 'title': 'Hai', 'pageStart': 14}]},
            {'sourceDocumentId': 'y', 'grade': 2, 'subject': 'Toán', 'docType': 'SGK',
             'structureStatus': 'NO_TOC', 'lessons': []}]},
            open(self.struct, 'w', encoding='utf-8'))
        with open(self.csv, 'w', encoding='utf-8') as fh:
            fh.write('sourceDocumentId,lessonNo\n' + 'x,1\nx,1\nx,1\nx,2\n')

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_the_six_figures_add_up(self):
        o = LI.report(self.struct, self.csv)
        self.assertEqual(o['sourceRows'], 4)
        self.assertEqual(o['distinctCurrentKeys'], 2)
        self.assertEqual(o['trueDuplicates'], 1)
        self.assertEqual(o['keyCollisions'], 1)
        self.assertEqual(o['canonicalLessonCount'], 3)
        self.assertEqual(o['sourceRows'] - o['trueDuplicates'], o['canonicalLessonCount'])
        self.assertEqual(o['trueDuplicates'] + o['keyCollisions'], o['excessRows'])

    def test_a_book_with_no_TOC_is_reported_rather_than_silently_absent(self):
        """The same failure family as R13: a whole book leaving the denominator with no record."""
        o = LI.report(self.struct, self.csv)
        self.assertEqual(o['sgkDocuments'], 2)
        self.assertEqual(o['booksContributingRows'], 1)
        self.assertEqual(o['sgkBooksContributingZeroRows'], 1)
        self.assertEqual(o['sgkZeroRowStructureStatus'], {'NO_TOC': 1})

    def test_the_canonical_count_is_never_the_current_key_count(self):
        o = LI.report(self.struct, self.csv)
        self.assertGreater(o['canonicalLessonCount'], o['distinctCurrentKeys'],
                           'collapsing on (book, lessonNo) deletes lessons that share a number')
        self.assertLess(o['canonicalLessonCount'], o['sourceRows'])


if __name__ == '__main__':
    unittest.main()
