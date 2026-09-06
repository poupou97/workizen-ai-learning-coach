#!/usr/bin/env python3
"""Round 5 · Lane A2 — is the printed operator the operator the OCR named?

This check exists because a hand-check found a FALSE CORRECTION the rest of the lane could not see:
Toán 4 tập hai p118 prints `c) 16/21 × 3/5`, Apple Vision returned a token whose text was `'-'`,
and every check passed — the ink was accounted for, no character was invented, the grammar parsed,
both vinculums were real — so the candidate came out `16/21 - 3/5`. Multiplication served as
subtraction, with a clean audit trail.

Completeness ≠ identity. These tests pin the identity check.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'corpus'))

from mathfix import glyphs as G              # noqa: E402
from mathfix import nodes as A               # noqa: E402
from mathfix import validate as V            # noqa: E402
from mathfix.build import Atom               # noqa: E402
from mathfix.extract import Candidate        # noqa: E402
from mathfix.inkmask import InkMask          # noqa: E402

MINUS = """\
..........
..........
..######..
..........
..........
"""
PLUS = """\
....#.....
....#.....
..######..
....#.....
....#.....
"""
TIMES = """\
..#....#..
...#..#...
....##....
...#..#...
..#....#..
"""
EQUALS = """\
..........
..######..
..........
..######..
..........
"""
COLON = """\
....##....
....##....
..........
....##....
....##....
"""


def scale(art, k=4):
    """Draw the picture k× bigger. A real operator at 300 dpi is hundreds of ink pixels; the
    classifier abstains below `MIN_INK_PX`, so a 6-pixel ASCII minus would (correctly) abstain."""
    out = []
    for line in art.splitlines():
        row = ''.join(c * k for c in line)
        out.extend([row] * k)
    return '\n'.join(out) + '\n'


def shape(art, k=4):
    m = InkMask.from_ascii(scale(art, k))
    return G.classify(m, (0.0, 0.0, 1.0, 1.0), text_height=0.0)


class TestShapeClassification(unittest.TestCase):
    def test_a_minus_is_one_bar(self):
        self.assertEqual(shape(MINUS), 'one_bar')

    def test_a_plus_is_a_crossed_bar(self):
        self.assertEqual(shape(PLUS), 'crossed_bar')

    def test_an_equals_is_two_bars(self):
        self.assertEqual(shape(EQUALS), 'two_bars')

    def test_a_times_has_no_dominant_bar(self):
        self.assertEqual(shape(TIMES), 'no_bar')

    def test_a_colon_has_no_dominant_bar(self):
        self.assertEqual(shape(COLON), 'no_bar')

    def test_an_empty_box_abstains_rather_than_guessing(self):
        self.assertIsNone(shape('..........\n..........\n'))

    def test_a_speck_abstains(self):
        self.assertIsNone(shape('..........\n....#.....\n..........\n', k=1))


class TestMatching(unittest.TestCase):
    def test_each_shape_admits_only_its_own_operators(self):
        self.assertTrue(G.matches('one_bar', A.SUB))
        self.assertFalse(G.matches('one_bar', A.ADD))
        self.assertFalse(G.matches('one_bar', A.MUL))
        self.assertTrue(G.matches('crossed_bar', A.ADD))
        self.assertTrue(G.matches('two_bars', A.EQ))
        self.assertTrue(G.matches('no_bar', A.MUL))
        self.assertTrue(G.matches('no_bar', A.DIV))

    def test_an_unjudgeable_shape_admits_nothing(self):
        for op in (A.ADD, A.SUB, A.MUL, A.DIV, A.EQ):
            self.assertFalse(G.matches(None, op))


class TestOperatorRasterValidator(unittest.TestCase):
    def candidate(self, op, box=(0.0, 0.0, 1.0, 1.0)):
        c = Candidate('math-line-v1', 'x', [], [])
        c.operators = (Atom(0.0, 'op', op, box),)
        return c

    def test_a_printed_times_read_as_a_minus_is_refused(self):
        """The p118 defect, in miniature."""
        m = InkMask.from_ascii(scale(TIMES))
        r = V.operator_raster_v1(self.candidate(A.SUB), m, text_height=0.0)
        self.assertEqual(r.verdict, 'FAIL')
        self.assertEqual(r.evidence['mismatched'][0]['printed_shape'], 'no_bar')
        self.assertEqual(r.evidence['mismatched'][0]['op'], A.SUB)

    def test_a_printed_minus_read_as_a_minus_passes(self):
        m = InkMask.from_ascii(scale(MINUS))
        r = V.operator_raster_v1(self.candidate(A.SUB), m, text_height=0.0)
        self.assertEqual(r.verdict, 'PASS')
        self.assertEqual(r.evidence['checked'], [dict(op=A.SUB, shape='one_bar')])

    def test_a_printed_plus_read_as_a_minus_is_refused(self):
        m = InkMask.from_ascii(scale(PLUS))
        self.assertEqual(V.operator_raster_v1(self.candidate(A.SUB), m, 0.0).verdict, 'FAIL')

    def test_a_candidate_with_no_operator_mark_is_not_applicable(self):
        c = Candidate('math-line-v1', 'x', [], [])
        self.assertEqual(V.operator_raster_v1(c, InkMask.from_ascii(scale(MINUS)), 0.0).verdict,
                         'NOT_APPLICABLE')

    def test_an_abstention_is_not_a_pass(self):
        m = InkMask.from_ascii('..........\n..........\n')
        r = V.operator_raster_v1(self.candidate(A.SUB), m, 0.0)
        self.assertEqual(r.verdict, 'NOT_APPLICABLE')
        self.assertEqual(r.evidence['abstained'], 1)


class TestP118Regression(unittest.TestCase):
    """The real page. Corpus-gated: the corpus never enters git."""

    BOOK, PAGE = '04-sgk-toan-4-tap-hai', 118

    def setUp(self):
        try:
            import pymupdf                                    # noqa: F401
            import numpy                                      # noqa: F401
        except Exception:
            self.skipTest('PyMuPDF/numpy not installed')
        from mathfix import runner
        if not os.path.exists(runner.pdf_path(self.BOOK)):
            self.skipTest('corpus not on this machine')
        sdm = (f'{runner.ROOT}/poc-out/round4/legacy/batch-1-rerun-tc2-p2/tcroot/poc-out/'
               f'trusted-corpus/tc-v2/tc2-p2/sdm/{self.BOOK}/p{self.PAGE:03d}.sdm.json')
        if not os.path.exists(sdm):
            self.skipTest('the round-4 legacy rerun is not on this machine')
        import json
        with open(sdm) as fh:
            page = json.load(fh)
        self.blocks = {b['block_id'][-3:]: b for b in
                       runner.page_report(self.BOOK, self.PAGE, sdm=page)['blocks']}

    def test_the_printed_times_is_refused(self):
        b = self.blocks['012']
        self.assertEqual(b['proposed_value'], '16/21 - 3/5',
                         'the OCR really does return «-» for the printed «×»')
        self.assertEqual(b['verdict'], 'WITHHOLD')
        ev = [v for v in b['validations'] if v['validator_id'] == 'operator-raster-v1'][0]
        self.assertEqual(ev['verdict'], 'FAIL')

    def test_the_printed_minus_beside_it_is_still_restored(self):
        """A guard that refused every operator would be safe and useless: `b) 8/11 − 19/33` is on
        the same printed row, is correct, and must survive."""
        b = self.blocks['011']
        self.assertEqual(b['proposed_value'], 'b) 8/11 - 19/33')
        self.assertEqual(b['verdict'], 'RESTORE')
        ev = [v for v in b['validations'] if v['validator_id'] == 'operator-raster-v1'][0]
        self.assertEqual(ev['verdict'], 'PASS')


if __name__ == '__main__':
    unittest.main()
