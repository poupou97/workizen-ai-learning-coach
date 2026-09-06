#!/usr/bin/env python3
"""Round 5 · Lane D — tests for tool/corpus/legacy/silent_loss.py.

The metric exists because a block whose role is `empty` reaches neither `blocks` nor `withheld` of
the TSL, so it is invisible to every served/withheld rate Lane D publishes — including the
over-withhold rate, which by construction only reviews regions that WERE withheld. These tests pin
the two things that make the number trustworthy: it counts blocks that are in the SDM and in neither
TSL list, and it puts them back into the denominator rather than into the numerator.

Run:  python3 -m unittest discover -s tool/tests -v
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _lane_d_sandbox  # noqa: E402,F401  — MUST precede anything that reaches legacy/common.py

sys.path.insert(0, os.path.join(HERE, '..', 'corpus', 'legacy'))
import silent_loss  # noqa: E402

BOOK, PIPE, LES = '04-sgk-toan-4-tap-hai', 'test-pipe', 61


class SilentLossTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='lane-d-silent-')
        self.root = os.path.join(self.tmp, 'tcroot', 'poc-out', 'trusted-corpus', 'tc-v2', PIPE)
        os.makedirs(os.path.join(self.root, 'sdm', BOOK))
        os.makedirs(os.path.join(self.root, 'lessons', BOOK))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, sdm_blocks, trusted_ids, withheld_ids, page=81):
        json.dump({'book': BOOK, 'page': page, 'blocks': sdm_blocks},
                  open(os.path.join(self.root, 'sdm', BOOK, f'p{page:03d}.json'), 'w', encoding='utf-8'))
        json.dump({'book': BOOK, 'lesson': LES, 'boundary': {'pages': [page]},
                   'blocks': [{'id': i, 'page': page, 'role': {'value': 'body'}, 'text': 'x'} for i in trusted_ids],
                   'withheld': [{'id': i, 'page': page, 'role': 'body', 'reasons': ['agree_text']} for i in withheld_ids],
                   'figures': [],
                   'stats': {'trusted': len(trusted_ids), 'withheld': len(withheld_ids)}},
                  open(os.path.join(self.root, 'lessons', BOOK, f'bai-{LES:02d}.tsl.json'), 'w', encoding='utf-8'))
        return silent_loss.scan_lesson(os.path.join(self.tmp), PIPE, BOOK, LES)

    def _blk(self, idx, role, text, page=81):
        return {'id': f'{BOOK}:p{page:03d}:{PIPE}:{idx:03d}', 'role': {'value': role}, 'text': text}

    def test_an_empty_role_block_is_counted_as_silently_lost(self):
        r = self._write([self._blk(0, 'body', 'Tính.'), self._blk(1, 'empty', '7 8 2 8 7 - 2 8 5 8')],
                        [f'{BOOK}:p081:{PIPE}:000'], [])
        self.assertEqual(r['silentlyLost'], 1)
        self.assertEqual(r['silentlyLostCarryingDigits'], 1)
        self.assertEqual(r['silentlyLostCarryingAnExpression'], 1,
                         'two digit groups with an operator between them is an expression')

    def test_a_served_or_withheld_block_is_never_silently_lost(self):
        """The whole point is «in neither list». A block that IS in a list is accounted for."""
        r = self._write([self._blk(0, 'body', '1+1'), self._blk(1, 'body', '2+2')],
                        [f'{BOOK}:p081:{PIPE}:000'], [f'{BOOK}:p081:{PIPE}:001'])
        self.assertEqual(r['silentlyLost'], 0)

    def test_the_silent_loss_goes_into_the_DENOMINATOR_not_the_numerator(self):
        """Served share must fall, because the served count is unchanged and the base grew."""
        r = self._write([self._blk(0, 'body', 'a'), self._blk(1, 'empty', '1 + 1'),
                         self._blk(2, 'empty', '2 + 2'), self._blk(3, 'empty', '3 + 3')],
                        [f'{BOOK}:p081:{PIPE}:000'], [])
        self.assertEqual(r['trusted'], 1)
        self.assertEqual(r['servedShareAsReported'], 1.0)
        self.assertEqual(r['servedShareWithSilentLoss'], 0.25, '1 served of 1 + 0 + 3')

    def test_a_block_marked_only_by_the_reason_code_is_caught_too(self):
        b = self._blk(1, 'body', '5 - 3')
        b['reasons'] = ['empty_block']
        r = self._write([self._blk(0, 'body', 'a'), b], [f'{BOOK}:p081:{PIPE}:000'], [])
        self.assertEqual(r['silentlyLost'], 1)

    def test_a_page_outside_the_lesson_boundary_is_not_counted(self):
        """A silent loss on a page the lesson does not own is another lesson's problem."""
        json.dump({'book': BOOK, 'page': 99, 'blocks': [self._blk(0, 'empty', '9 + 9', page=99)]},
                  open(os.path.join(self.root, 'sdm', BOOK, 'p099.json'), 'w', encoding='utf-8'))
        r = self._write([self._blk(0, 'body', 'a')], [f'{BOOK}:p081:{PIPE}:000'], [])
        self.assertEqual(r['silentlyLost'], 0)

    def test_text_never_leaves_the_pack(self):
        """D4: the row carries counts and ids, never the block text."""
        r = self._write([self._blk(0, 'body', 'a'), self._blk(1, 'empty', 'SECRET 1 + 1')],
                        [f'{BOOK}:p081:{PIPE}:000'], [])
        self.assertNotIn('SECRET', json.dumps(r, ensure_ascii=False))

    def test_a_non_expression_digit_run_counts_as_digits_but_not_as_an_expression(self):
        r = self._write([self._blk(0, 'body', 'a'), self._blk(1, 'empty', '1408')],
                        [f'{BOOK}:p081:{PIPE}:000'], [])
        self.assertEqual(r['silentlyLostCarryingDigits'], 1)
        self.assertEqual(r['silentlyLostCarryingAnExpression'], 0)


if __name__ == '__main__':
    unittest.main()
