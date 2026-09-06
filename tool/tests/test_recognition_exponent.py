#!/usr/bin/env python3
"""Round 6 · Workstream B — recovering a destroyed power-of-ten exponent.

Every rule below was written because a hand-check found a wrong reading, and every counter-example
is a real line from the corpus. The four false recognitions the first version produced are all
pinned here, so re-introducing any of them fails a test rather than a review.

No corpus, no PDF, no Vision. The raster cases are ASCII pictures, the same pattern round 5's
mathfix suite uses so the CI box needs neither numpy nor PyMuPDF.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'corpus'))

from mathfix import sci_notation as SN            # noqa: E402
from mathfix.inkmask import InkMask               # noqa: E402
from mathfix.tokens import Token                  # noqa: E402
from recognition import exponent as X             # noqa: E402


class TestExponentInOneLine(unittest.TestCase):
    def test_a_plain_reading(self):
        self.assertEqual(X._exponent_in('= 105 P'), '5')
        self.assertEqual(X._exponent_in('10 8 CFU/g'), '8')

    def test_a_two_digit_exponent(self):
        """`10^22 sao` on Toán 10 chuyên đề p15. The crop returns the exponent glued to the ten,
        which is fine here and only here: the region is one the page pass already read as `10°`,
        so a bare `1022` in it is a broken power of ten and not the number one thousand and
        twenty-two. The digit guards on either side keep it from matching inside a longer run."""
        self.assertEqual(X._exponent_in('1022 sa'), '22')
        self.assertEqual(X._exponent_in('10 22 sa'), '22')
        self.assertIsNone(X._exponent_in('310225'))

    def test_a_bracket_or_a_letter_before_the_ten_is_not_a_power_of_ten(self):
        """`(2 + x)^100` on Toán 10 chuyên đề p50 was RECOVERED as 10^0 by the first version."""
        self.assertIsNone(X._exponent_in('x) 100'))
        self.assertIsNone(X._exponent_in('1) 100'))
        self.assertIsNone(X._exponent_in('g 101'))

    def test_ten_to_the_zero_is_refused(self):
        self.assertIsNone(X._exponent_in('= 100 P'))

    def test_a_degree_sign_that_survived_is_not_a_reading(self):
        self.assertIsNone(X._exponent_in('= 10° P'))
        self.assertTrue(X.STILL_BROKEN.search('= 10° P'))


class TestConsensus(unittest.TestCase):
    def test_two_scales_agreeing(self):
        v, val, sc = X.read({8.0: ['= 105 P'], 20.0: ['= 105 p']})
        self.assertEqual((v, val), ('RECOVERED', '5'))
        self.assertEqual(sc, (8.0, 20.0))

    def test_one_scale_alone_is_not_evidence(self):
        v, val, _ = X.read({8.0: ['= 105 P'], 20.0: ['= 10° P']})
        self.assertEqual(v, 'INSUFFICIENT_AGREEMENT')

    def test_disagreeing_scales_fail_closed(self):
        v, val, _ = X.read({8.0: ['= 105 P'], 20.0: ['= 106 P'], 14.0: ['= 105 P']})
        self.assertEqual((v, val), ('CONFLICT', None))

    def test_the_defect_reproducing_at_every_scale_is_STILL_BROKEN_not_a_reading(self):
        v, _, _ = X.read({8.0: ['3.10° m'], 20.0: ['3.10° m']})
        self.assertEqual(v, 'STILL_BROKEN')

    def test_a_match_may_not_span_two_lines(self):
        """Toán 6 tập hai p31 prints `-35/10 ; -1/10`; the crop returned three separate lines and
        the first version joined them and read `10 10` as ten to the tenth."""
        v, val, _ = X.read({8.0: ['-35 -1', '10', '10'], 20.0: ['-35 -1', '10']})
        self.assertNotEqual(val, '10')
        self.assertEqual(v, 'UNREAD')


class TestSiValidator(unittest.TestCase):
    """The page's own printed prefix relation, and only where the page prints one."""

    def test_the_page_fixes_the_exponent(self):
        self.assertEqual(SN.si_expected_exponent('1 kJ = 10°J'), 3)
        self.assertEqual(X.validate('3', '1 kJ = 10°J'), ('PASS', 3))
        self.assertEqual(X.validate('5', '1 kJ = 10°J'), ('FAIL', 3))

    def test_abstention_is_reported_and_is_never_a_pass(self):
        self.assertEqual(X.validate('5', '- Bar: 1 Bar = 10° Pa.'), ('NOT_APPLICABLE', None))


# `10`, then the superscript slot. In SIGNED a short detached bar sits in that slot — the printed
# minus of `10^-5`; in UNSIGNED the slot holds only the exponent digit. The two pictures differ by
# exactly the mark the guard exists to see.
SIGNED = """\
............................
............................
................####........
............................
..#...###.......#####.......
.###.#...#......#...........
..#..#...#......#####.......
..#..#...#..........#.......
..#..#...#......#...#.......
.###..###........###........
............................
............................
"""
UNSIGNED = """\
............................
............................
............................
............................
..#...###.......#####.......
.###.#...#......#...........
..#..#...#......#####.......
..#..#...#..........#.......
..#..#...#......#...#.......
.###..###........###........
............................
............................
"""


class TestSuperscriptSign(unittest.TestCase):
    """Identity, not coverage. The magnitude of `10^-5` is right and the sign is a printed mark
    nobody read; only the pixels where the sign should be can say so."""

    @staticmethod
    def _upscale(art, k=3):
        """Draw the picture k times larger in both directions.

        The guard's tolerances are ratios of the line height — a minus is at most 0.18 of it
        thick — so a picture whose strokes are one cell wide has a stroke thickness of 0.08 of
        its own height and every stroke reads as a thin bar. Real pages are 88 raster rows per
        line; the test has to be drawn at a comparable proportion or it tests nothing.
        """
        rows = [ln for ln in art.splitlines() if ln]
        return '\n'.join(''.join(c * k for c in ln) for ln in rows for _ in range(k)) + '\n'

    def _probe(self, art):
        """The production window, not a convenient one. It begins past the `10` on purpose:
        measured on the real pages, a window over the whole match finds the printed
        multiplication mark to the LEFT of the ten and refuses correct readings — 9 of 18
        instead of 2 of 18."""
        mask = InkMask.from_ascii(self._upscale(art))
        tok = Token(text='10 -5', x=0.0, y=0.0, w=1.0, h=1.0, conf=1.0, index=0)
        return X.superscript_sign(mask, tok, SN.ExponentFinding(start=0, end=4, matched='10 '))

    def test_row_runs_are_start_and_length(self):
        """The bug that made the first version of this guard fire on 0 of 18 real readings."""
        mask = InkMask.from_ascii('..####....\n')
        self.assertEqual(mask.row_runs(0, 0, 10, min_len=1), [(2, 4)])

    def test_a_detached_bar_in_the_superscript_slot_refuses_the_reading(self):
        self.assertIs(self._probe(SIGNED), True)

    def test_the_same_exponent_without_a_sign_passes(self):
        """A guard that refused every exponent would be safe and useless — round 5's own words."""
        self.assertIs(self._probe(UNSIGNED), False)

    def test_an_empty_slot_abstains_rather_than_passing(self):
        mask = InkMask.from_ascii('..........\n..........\n..........\n')
        tok = Token(text='10 5', x=0.0, y=0.0, w=1.0, h=1.0, conf=1.0, index=0)
        self.assertIsNone(X.superscript_sign(mask, tok, SN.ExponentFinding(0, 3, '10 ')))


if __name__ == '__main__':
    unittest.main()
