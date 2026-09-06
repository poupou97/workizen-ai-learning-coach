#!/usr/bin/env python3
"""Round 6 · WS-A — tests for the conservation ledger and its HARD FAILURE.

The invariant under test:

    INPUT SOURCE REGIONS = SERVED + WITHHELD + EXCLUDED_WITH_REASON + defined non-learning regions

Round 5's silent loss survived because nothing failed when a region disappeared: the served share was
computed over a base that had already shrunk, and the over-withhold rate reviewed only regions that
WERE withheld. These tests pin the three properties that make the ledger a check rather than a report:
it partitions the WHOLE input population, an unnamed region is UNACCOUNTED rather than quietly dropped,
and `audit` exits non-zero when a single region is UNACCOUNTED.

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
import dispositions as D  # noqa: E402
import ledger  # noqa: E402

BOOK, PIPE, LES, PAGE = '04-sgk-toan-4-tap-hai', 'test-pipe', 61, 81


def _put(path, obj):
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(obj, fh, ensure_ascii=False)


class ClassifierTests(unittest.TestCase):
    """What the single `empty` bucket was hiding — one class per physically different thing."""

    def test_a_printed_arithmetic_line_is_not_no_letters(self):
        self.assertEqual(D.classify_unread('40 613 + 47 519', ['40 613 + 47 519']),
                         'numeric_expression_inline')

    def test_a_stacked_expression_flattened_from_many_lines_is_its_own_class(self):
        cls = D.classify_unread('7 8 2 8 7 - 2 8 5 8',
                                ['7', '2', '7- 2', '5', '=', '8', '8', '8', '8'])
        self.assertEqual(cls, 'numeric_expression_stacked')

    def test_a_map_figure_is_a_numeric_label_not_an_expression(self):
        self.assertEqual(D.classify_unread('1408', ['1408']), 'numeric_label')

    def test_an_operator_torn_off_its_expression_is_a_symbol_fragment(self):
        self.assertEqual(D.classify_unread('- -', ['--']), 'symbol_fragment')

    def test_a_region_with_no_text_but_ocr_lines_under_it_is_unreadable_not_empty(self):
        """A Docling FORMULA region whose block text is empty while nine OCR lines sit under it has
        not lost nothing — it has lost everything, and `empty_block` says the opposite."""
        self.assertEqual(D.classify_unread('', ['9', '3', 'a)', '11', '11']), 'unreadable_region')

    def test_only_a_truly_empty_region_is_an_acceptable_exclusion(self):
        self.assertEqual(D.classify_unread('', []), 'no_content')
        self.assertEqual(D.disposition_for_unaccounted_role('empty', '', [])[0], D.EXCLUDED)
        for cls_text, lines in (('1408', ['1408']), ('', ['9']), ('1 + 1', ['1 + 1']), ('-', ['-'])):
            self.assertEqual(D.disposition_for_unaccounted_role('empty', cls_text, lines)[0], D.UNACCOUNTED)

    def test_the_reason_code_no_longer_misstates_what_was_lost(self):
        """Round 5 §8.2: «`empty_block` on a block reading `7 8 2 8 7 - 2 8 5 8` misstates what was lost.»"""
        _, reason = D.disposition_for_unaccounted_role('empty', '7 8 2 8 7 - 2 8 5 8', ['7', '2', '5'])
        self.assertEqual(reason, 'unread:numeric_expression_stacked')
        self.assertEqual(D.unread_guard('no_content'), 'empty_block')

    def test_a_defined_non_learning_role_is_excluded_with_a_named_reason(self):
        for role in ('page_number', 'running_head', 'figure', 'figure_text'):
            disp, reason = D.disposition_for_unaccounted_role(role, 'x', ['x'])
            self.assertEqual(disp, D.EXCLUDED)
            self.assertTrue(reason.startswith('non_learning:'), reason)

    def test_a_learning_role_that_reached_neither_list_is_never_silently_excluded(self):
        disp, reason = D.disposition_for_unaccounted_role('body', 'Tính.', ['Tính.'])
        self.assertEqual(disp, D.UNACCOUNTED)
        self.assertEqual(reason, 'dropped_with_role:body')


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='ws-a-ledger-')
        self.root = os.path.join(self.tmp, 'tcroot', 'poc-out', 'trusted-corpus', 'tc-v2', PIPE)
        os.makedirs(os.path.join(self.root, 'sdm', BOOK))
        os.makedirs(os.path.join(self.root, 'lessons', BOOK))
        _put(os.path.join(self.tmp, 'batch-spec.json'),
             {'batch': 'test', 'lessons': [{'book': BOOK, 'lesson': LES}]})

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _blk(self, idx, role, text, lines=None):
        b = {'id': f'{BOOK}:p{PAGE:03d}:{PIPE}:{idx:03d}', 'order': idx, 'role': {'value': role}, 'text': text}
        if lines is not None:
            b['geometry'] = {'lines': [{'text': t} for t in lines]}
        return b

    def _write(self, sdm_blocks, served, withheld, excluded=None, lesson=LES):
        _put(os.path.join(self.root, 'sdm', BOOK, f'p{PAGE:03d}.sdm.json'),
             {'book': BOOK, 'page': PAGE, 'blocks': sdm_blocks})
        doc = {'book': BOOK, 'lesson': lesson, 'boundary': {'pages': [PAGE]},
               'blocks': [{'id': i} for i in served],
               'withheld': [{'id': i, 'reasons': ['agree_text']} for i in withheld],
               'stats': {'trusted': len(served), 'withheld': len(withheld)}}
        if excluded is not None:
            doc['excluded'] = excluded
        _put(os.path.join(self.root, 'lessons', BOOK, f'bai-{lesson:02d}.tsl.json'), doc)
        return ledger.ledger_lesson(self.tmp, PIPE, BOOK, lesson)

    def _id(self, i):
        return f'{BOOK}:p{PAGE:03d}:{PIPE}:{i:03d}'

    def test_the_ledger_partitions_the_whole_input_population(self):
        r = self._write([self._blk(0, 'body', 'a'), self._blk(1, 'body', 'b'),
                         self._blk(2, 'page_number', '81'), self._blk(3, 'empty', '1 + 1', ['1 + 1'])],
                        [self._id(0)], [self._id(1)])
        self.assertEqual(r['inputSourceRegions'], 4)
        self.assertEqual((r['served'], r['withheld'], r['excludedWithReason'], r['unaccounted']), (1, 1, 1, 1))
        self.assertEqual(r['served'] + r['withheld'] + r['excludedWithReason'] + r['unaccounted'],
                         r['inputSourceRegions'])

    def test_a_silently_lost_region_makes_the_ledger_fail_to_conserve(self):
        r = self._write([self._blk(0, 'body', 'a'), self._blk(1, 'empty', '40 613 + 47 519', ['40 613 + 47 519'])],
                        [self._id(0)], [])
        self.assertFalse(r['conserves'])
        self.assertEqual(r['unaccounted'], 1)
        self.assertEqual(r['byReason']['unread:numeric_expression_inline'], 1)

    def test_the_silent_loss_lands_in_the_DENOMINATOR_not_the_numerator(self):
        """Served count unchanged, learning base grown — exactly round 5's correction."""
        r = self._write([self._blk(0, 'body', 'a'), self._blk(1, 'empty', '1 + 1', ['1 + 1']),
                         self._blk(2, 'empty', '2 + 2', ['2 + 2']), self._blk(3, 'empty', '3 + 3', ['3 + 3'])],
                        [self._id(0)], [])
        self.assertEqual(r['servedShareAsReported'], 1.0)
        self.assertEqual(r['servedShareOfLearningRegions'], 0.25)

    def test_a_defined_non_learning_region_does_NOT_dilute_the_served_share(self):
        """`EXCLUDED_WITH_REASON` is not a synonym for WITHHELD: converting every excluded region into a
        withheld one would trade a silent loss for a mass over-withhold."""
        r = self._write([self._blk(0, 'body', 'a'), self._blk(1, 'page_number', '81'),
                         self._blk(2, 'figure_text', 'nhãn hình')],
                        [self._id(0)], [])
        self.assertTrue(r['conserves'])
        self.assertEqual(r['servedShareAsReported'], 1.0)
        self.assertEqual(r['servedShareOfLearningRegions'], 1.0)
        self.assertEqual(r['servedShareOfAllInputRegions'], round(1 / 3, 4))

    def test_an_excluded_list_carried_by_the_TSL_itself_is_used_and_reported_as_such(self):
        r = self._write([self._blk(0, 'body', 'a'), self._blk(1, 'figure_text', 'nhãn')],
                        [self._id(0)], [], excluded=[{'id': self._id(1), 'reason': 'non_learning:figure_text'}])
        self.assertEqual(r['excludedSource'], 'tsl.excluded')
        self.assertTrue(r['conserves'])

    def test_a_block_a_neighbouring_lesson_accounts_for_is_excluded_not_lost(self):
        """Two lessons share a page at a mid-page header; the neighbour's ledger carries the block."""
        _put(os.path.join(self.root, 'lessons', BOOK, 'bai-62.tsl.json'),
             {'book': BOOK, 'lesson': 62, 'boundary': {'pages': [PAGE]},
              'blocks': [{'id': self._id(1)}], 'withheld': [], 'stats': {'trusted': 1, 'withheld': 0}})
        r = self._write([self._blk(0, 'body', 'a'), self._blk(1, 'body', 'b')], [self._id(0)], [])
        self.assertTrue(r['conserves'])
        self.assertEqual(r['byReason']['other_lesson:62'], 1)

    def test_audit_exits_non_zero_on_an_unaccounted_region(self):
        """A HARD FAILURE, not a warning — the whole point of R13."""
        self._write([self._blk(0, 'body', 'a'), self._blk(1, 'empty', '1 + 1', ['1 + 1'])], [self._id(0)], [])
        self.assertEqual(ledger.main(['audit', '--batch-dir', self.tmp, '--pipeline', PIPE]), 1)
        self.assertEqual(ledger.main(['audit', '--batch-dir', self.tmp, '--pipeline', PIPE, '--historical']), 0)

    def test_audit_exits_zero_when_conservation_holds(self):
        self._write([self._blk(0, 'body', 'a'), self._blk(1, 'page_number', '81')], [self._id(0)], [])
        self.assertEqual(ledger.main(['audit', '--batch-dir', self.tmp, '--pipeline', PIPE]), 0)

    def test_a_page_outside_the_lesson_boundary_is_another_lesson_s_ledger(self):
        _put(os.path.join(self.root, 'sdm', BOOK, 'p999.sdm.json'),
             {'book': BOOK, 'page': 999, 'blocks': [{'id': 'x', 'role': {'value': 'empty'}, 'text': '9+9'}]})
        r = self._write([self._blk(0, 'body', 'a')], [self._id(0)], [])
        self.assertEqual(r['inputSourceRegions'], 1)

    def test_a_downstream_demotion_moves_a_region_without_breaking_conservation(self):
        """WS-C's repair projection honours a fail-closed ledger ruling and withdraws a served block.
        A demotion moves a region SERVED → WITHHELD; the population must not change, and the count is
        reported apart from this workstream's own reclassification so the two are never folded."""
        r = self._write([self._blk(0, 'body', 'a'), self._blk(1, 'body', 'b'), self._blk(2, 'body', 'c')],
                        [self._id(0), self._id(1)], [self._id(2)])
        self.assertEqual((r['served'], r['withheld'], r['demotedDownstream']), (2, 1, 0))
        r2 = ledger.ledger_lesson(self.tmp, PIPE, BOOK, LES, demotions=[self._id(1)])
        self.assertEqual((r2['served'], r2['withheld'], r2['demotedDownstream']), (1, 2, 1))
        self.assertEqual(r2['inputSourceRegions'], r['inputSourceRegions'])
        self.assertTrue(r2['conserves'])
        self.assertEqual(r2['byReason']['withheld:demoted_downstream'], 1)

    def test_a_demotion_joins_across_generations_on_page_and_block_index(self):
        """WS-C runs on its own pipeline generation, so its block ids carry a different pipeline
        segment. The join uses (book, page, native index) — never the whole id, never text."""
        r = self._write([self._blk(0, 'body', 'a'), self._blk(1, 'body', 'b')], [self._id(0), self._id(1)], [])
        other_generation = f'{BOOK}:p{PAGE:03d}:some-other-pipeline:001'
        r2 = ledger.ledger_lesson(self.tmp, PIPE, BOOK, LES, demotions=[other_generation])
        self.assertEqual(r2['demotedDownstream'], 1)
        self.assertEqual((r2['served'], r2['withheld']), (1, 1))
        self.assertTrue(r2['conserves'])

    def test_the_ledger_never_carries_block_text(self):
        """Corpus discipline: counts, ids and reason codes leave `poc-out/`; printed text does not."""
        r = self._write([self._blk(0, 'body', 'BÍ MẬT'), self._blk(1, 'empty', 'SECRET 1 + 1', ['SECRET 1 + 1'])],
                        [self._id(0)], [])
        self.assertNotIn('SECRET', json.dumps(r, ensure_ascii=False))
        self.assertNotIn('BÍ MẬT', json.dumps(r, ensure_ascii=False))


if __name__ == '__main__':
    unittest.main()
