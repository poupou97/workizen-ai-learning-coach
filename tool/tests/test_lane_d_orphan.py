#!/usr/bin/env python3
"""Round 5 · Lane D — tests for tool/corpus/legacy/orphan.py (Founder evaluation-set defect 8:
withholding is not always safe).

The case that matters most is the one the first implementation MISSED: on Toán 4 tập một Bài 37
p130 the served options carry `order` 11, 12, 13 and the withheld fourth option carries `order` 17,
so an `order`-based grouping walks straight past a mutilated multiple-choice. The grouping is now
on the page-level index in the block id, and this file pins that.

Run:  python3 -m unittest discover -s tool/tests -v
"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _lane_d_sandbox  # noqa: E402,F401  — MUST precede anything that reaches legacy/common.py

sys.path.insert(0, os.path.join(HERE, '..', 'corpus', 'legacy'))
import orphan  # noqa: E402

BOOK = '04-sgk-toan-4-tap-mot'


def served(idx, role, text, page=130, order=None, bbox=(0.1, 0.1, 0.5, 0.02)):
    return {'id': f'{BOOK}:p{page:03d}:tc2-p2:{idx:03d}', 'page': page,
            'order': idx if order is None else order,
            'role': {'value': role, 'confidence': 0.9}, 'text': text, 'bbox': list(bbox)}


def withheld(idx, role, reasons, page=130, order=None, text_len=12, bbox=(0.1, 0.1, 0.5, 0.02)):
    return {'id': f'{BOOK}:p{page:03d}:tc2-p2:{idx:03d}', 'page': page,
            'order': idx if order is None else order, 'role': role, 'reasons': list(reasons),
            'status': 'CONFLICT', 'text_len': text_len, 'text': None, 'bbox': list(bbox)}


def tsl(blocks, wh=(), figures=(), lesson=37):
    return {'book': BOOK, 'lesson': lesson, 'pipeline': 'tc2-p2',
            'blocks': list(blocks), 'withheld': list(wh), 'figures': list(figures),
            'stats': {'trusted': len(blocks), 'withheld': len(wh)}}


class PageIndexTests(unittest.TestCase):
    def test_the_page_index_comes_from_the_block_id_suffix(self):
        self.assertEqual(orphan.page_index('04-sgk-toan-4-tap-mot:p130:tc2-p2:014'), 14)
        self.assertIsNone(orphan.page_index('weird-id-without-a-number'))


class SplitOptionGroupTests(unittest.TestCase):
    """The exact defect the Founder named."""

    def test_option_D_withheld_while_A_B_C_are_served_is_detected(self):
        t = tsl([served(11, 'option', 'A. 1 số chẵn'),
                 served(12, 'option', 'B. 2 số chẵn'),
                 served(13, 'option', 'C. 3 số chẵn')],
                [withheld(14, 'option', ['agree_order'], order=17)])
        found = orphan.scan_tsl(t)
        kinds = [f['kind'] for f in found]
        self.assertIn('SPLIT_OPTION_GROUP', kinds)
        f = next(x for x in found if x['kind'] == 'SPLIT_OPTION_GROUP')
        self.assertEqual((f['served'], f['withheld']), (3, 1))
        self.assertEqual(f['withheldReasons'], ['agree_order'])

    def test_the_per_list_order_field_would_have_missed_it(self):
        """A guard on the bug, not only on the fix: `order` 13 -> 17 is a gap of four."""
        t = tsl([served(11, 'option', 'A.', order=11), served(12, 'option', 'B.', order=12),
                 served(13, 'option', 'C.', order=13)],
                [withheld(14, 'option', ['agree_order'], order=17)])
        seq = orphan.entries(t)
        by_id = {e['id'][-3:]: e for e in seq}
        self.assertEqual(by_id['013']['order'] + 1, by_id['014']['order'],
                         'the id-suffix index is contiguous where the list order is not')
        self.assertNotEqual(by_id['013']['listOrder'] + 1, by_id['014']['listOrder'])

    def test_an_intact_option_group_is_not_flagged(self):
        t = tsl([served(11, 'option', 'A.'), served(12, 'option', 'B.'),
                 served(13, 'option', 'C.'), served(14, 'option', 'D.')])
        self.assertEqual([f['kind'] for f in orphan.scan_tsl(t)], [])

    def test_a_fully_withheld_option_group_is_reported_as_safe_not_teaching_critical(self):
        t = tsl([served(10, 'body', 'Trong các ô đó có:')],
                [withheld(11, 'option', ['agree_text']), withheld(12, 'option', ['agree_text'])])
        found = orphan.scan_tsl(t)
        self.assertEqual([f['kind'] for f in found], ['OPTION_GROUP_FULLY_WITHHELD'])
        self.assertNotIn('OPTION_GROUP_FULLY_WITHHELD', orphan.TEACHING_CRITICAL_KINDS,
                         'losing a whole question costs coverage; showing three of four answers is a wrong question')


class QuestionOptionTests(unittest.TestCase):
    def test_a_served_question_whose_options_are_all_withheld(self):
        t = tsl([served(10, 'question', 'Chọn câu trả lời đúng.')],
                [withheld(11, 'option', ['agree_text']), withheld(12, 'option', ['agree_text'])])
        self.assertIn('QUESTION_WITHOUT_OPTIONS', [f['kind'] for f in orphan.scan_tsl(t)])

    def test_served_options_whose_question_is_withheld(self):
        t = tsl([served(11, 'option', 'A.'), served(12, 'option', 'B.')],
                [withheld(10, 'question', ['agree_tones'])])
        self.assertIn('OPTIONS_WITHOUT_QUESTION', [f['kind'] for f in orphan.scan_tsl(t)])


class EnumeratedRunTests(unittest.TestCase):
    def test_a_gap_inside_an_enumerated_run_is_detected(self):
        t = tsl([served(1, 'body', 'a) 3/5 + 1/5'), served(2, 'body', 'b) 2/7 + 3/7'),
                 served(4, 'body', 'd) 1/9 + 5/9')],
                [withheld(3, 'body', ['math_guard'])])
        self.assertIn('SPLIT_ENUMERATED_RUN', [f['kind'] for f in orphan.scan_tsl(t)])

    def test_an_unbroken_enumerated_run_is_not_flagged(self):
        t = tsl([served(1, 'body', 'a) x'), served(2, 'body', 'b) y'), served(3, 'body', 'c) z')])
        self.assertEqual([f['kind'] for f in orphan.scan_tsl(t)], [])


class CaptionFigureTests(unittest.TestCase):
    def test_a_figure_with_one_served_and_one_withheld_caption_is_split(self):
        fig = {'page': 130, 'bbox': [0.1, 0.3, 0.5, 0.2]}
        t = tsl([served(5, 'caption', 'Hình 5.1', bbox=(0.12, 0.52, 0.2, 0.02))],
                [withheld(6, 'caption', ['agree_order'], bbox=(0.34, 0.52, 0.2, 0.02))],
                figures=[fig])
        self.assertIn('SPLIT_CAPTION_SET', [f['kind'] for f in orphan.scan_tsl(t)])


class DoctrineTests(unittest.TestCase):
    def test_every_split_kind_is_classified_teaching_critical(self):
        for k in ('SPLIT_OPTION_GROUP', 'QUESTION_WITHOUT_OPTIONS', 'OPTIONS_WITHOUT_QUESTION',
                  'SPLIT_ENUMERATED_RUN', 'SPLIT_CAPTION_SET', 'SPLIT_TABLE'):
            self.assertIn(k, orphan.TEACHING_CRITICAL_KINDS)

    def test_a_withheld_region_never_needs_its_text_to_be_grouped(self):
        """D4: the TSL does not carry withheld text, and the detector must not need it."""
        t = tsl([served(11, 'option', 'A.'), served(12, 'option', 'B.')],
                [withheld(13, 'option', ['agree_order'], text_len=0)])
        found = orphan.scan_tsl(t)
        self.assertIn('SPLIT_OPTION_GROUP', [f['kind'] for f in found])
        self.assertNotIn('text', json.dumps(found[0]['withheldIds']))


if __name__ == '__main__':
    unittest.main()
