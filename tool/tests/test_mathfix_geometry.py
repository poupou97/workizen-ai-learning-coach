#!/usr/bin/env python3
"""Round 5 · Lane A2 — the raster and token primitives the math repairer stands on.

Why these are pinned by synthetic rasters rather than by real pages: the Founder's order is
«do not reconstruct expressions speculatively from OCR prose», so the fraction bar has to be
read off the PAGE. That makes the raster a load-bearing input, and a load-bearing input needs
tests that run everywhere — CI has no PDF, no PyMuPDF and no numpy. `InkMask.from_ascii`
therefore builds the same structure the PDF loader builds, and every geometric rule below is
pinned on a picture a human can read in the test file itself.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'corpus'))

from mathfix import inkmask as IM          # noqa: E402
from mathfix import bars as BARS           # noqa: E402
from mathfix.tokens import Token           # noqa: E402


# A 40×20 «page»: a fraction (1 over 5) with its bar, a minus sign to the right of it,
# and a full-width rule along the bottom (a table rule / box border).
PAGE = """\
........................................
........................................
.........##.............................
........###.............................
.........##.............................
.........##.............................
.........##.............................
........................................
......########..........#######.........
........................................
.........##.............................
........####............................
.......##..##...........................
...........##...........................
.........###............................
........................................
........................................
........................................
######################################..
........................................
"""


class TestInkMask(unittest.TestCase):
    def test_from_ascii_reads_the_picture(self):
        m = IM.InkMask.from_ascii(PAGE)
        self.assertEqual((m.width, m.height), (40, 20))
        self.assertTrue(m.ink(9, 2))
        self.assertFalse(m.ink(0, 0))

    def test_any_ink_is_a_half_open_box(self):
        m = IM.InkMask.from_ascii(PAGE)
        self.assertTrue(m.any_ink(6, 8, 14, 9))        # the fraction bar row
        self.assertFalse(m.any_ink(0, 0, 40, 2))       # the blank top

    def test_column_coverage_is_the_share_of_columns_carrying_ink(self):
        m = IM.InkMask.from_ascii(PAGE)
        # columns 6..13 in rows 2..7 hold only the numerator «1» (3 of the 8 columns)
        self.assertAlmostEqual(m.column_coverage(6, 2, 14, 8), 3 / 8, places=6)
        self.assertEqual(m.column_coverage(0, 0, 40, 2), 0.0)

    def test_row_runs_finds_contiguous_ink(self):
        m = IM.InkMask.from_ascii(PAGE)
        self.assertEqual(m.row_runs(8, 0, 40), [(6, 8), (24, 7)])
        self.assertEqual(m.row_runs(0, 0, 40), [])


class TestFindBars(unittest.TestCase):
    def test_finds_the_fraction_bar_and_the_minus_sign(self):
        m = IM.InkMask.from_ascii(PAGE)
        found = BARS.find_bars(m, min_len_frac=0.15, max_len_frac=0.30, max_thick_frac=0.15)
        got = sorted((b.px0, b.px1, b.py0, b.py1) for b in found)
        self.assertEqual(got, [(6, 14, 8, 9), (24, 31, 8, 9)])

    def test_min_length_drops_the_horizontal_strokes_inside_a_glyph(self):
        # The «5» of the denominator has a 2-px horizontal stroke of its own. A vinculum is never
        # that short relative to the page, which is the whole job of MIN_LEN.
        m = IM.InkMask.from_ascii(PAGE)
        loose = BARS.find_bars(m, min_len_frac=0.05, max_len_frac=0.30, max_thick_frac=0.15)
        self.assertIn((11, 13, 12, 13), [(b.px0, b.px1, b.py0, b.py1) for b in loose])
        tight = BARS.find_bars(m, min_len_frac=0.15, max_len_frac=0.30, max_thick_frac=0.15)
        self.assertNotIn((11, 13, 12, 13), [(b.px0, b.px1, b.py0, b.py1) for b in tight])

    def test_rejects_a_full_width_rule_as_too_long(self):
        m = IM.InkMask.from_ascii(PAGE)
        found = BARS.find_bars(m, min_len_frac=0.15, max_len_frac=0.30, max_thick_frac=0.15)
        self.assertFalse([b for b in found if b.py0 == 18],
                         'the bottom rule spans 95 % of the page — a table rule, never a vinculum')

    def test_rejects_a_thick_block_as_too_thick(self):
        m = IM.InkMask.from_ascii('..........\n..#####...\n..#####...\n..#####...\n..........\n')
        self.assertEqual(BARS.find_bars(m, 0.2, 0.9, max_thick_frac=0.20), [])

    def test_a_bar_is_one_object_across_the_rows_it_spans(self):
        m = IM.InkMask.from_ascii('..........\n..######..\n..######..\n..........\n')
        found = BARS.find_bars(m, 0.2, 0.9, max_thick_frac=0.60)
        self.assertEqual(len(found), 1)
        self.assertEqual((found[0].py0, found[0].py1), (1, 3))

    def test_normalised_geometry_is_derived_from_the_mask_size(self):
        m = IM.InkMask.from_ascii(PAGE)
        b = [x for x in BARS.find_bars(m, 0.15, 0.30, 0.15) if x.px0 == 6][0]
        self.assertAlmostEqual(b.x0, 6 / 40, places=6)
        self.assertAlmostEqual(b.x1, 14 / 40, places=6)
        self.assertAlmostEqual(b.y0, 8 / 20, places=6)
        self.assertAlmostEqual(b.length, 8 / 40, places=6)


class TestNeutralLayer(unittest.TestCase):
    """A press prints a rule in neutral ink; an illustration's edge is coloured.

    On an unbiased 12-page sample of ordinary Toán pages, 4 of 7 detected regions were parts of
    PICTURES — a grass band, a speech-bubble tail, the brim of a hat. Reading bars off the neutral
    layer removed two of them and cost nothing on the 45 real fractions of the dense pages.
    """

    ART = """\
..........
..######..
..........
..######..
..........
"""

    def test_from_ascii_treats_every_pixel_as_neutral(self):
        m = IM.InkMask.from_ascii(self.ART)
        self.assertIs(m.neutral_rows, m.rows)

    def test_find_bars_reads_the_neutral_layer(self):
        m = IM.InkMask.from_ascii(self.ART)
        # the second rule is «coloured»: dark, but not neutral
        m.neutral_rows = [m.rows[0], m.rows[1], m.rows[2], bytes(m.width), m.rows[4]]
        found = BARS.find_bars(m, 0.2, 0.9, 0.30)
        self.assertEqual([(b.px0, b.py0) for b in found], [(2, 1)])

    def test_ink_queries_still_see_the_coloured_pixels(self):
        """A printed DIGIT may be coloured — Toán 5 tập một p22 sets «× 5» in red and «× 2» in
        blue — so the ink-accounting scan must keep seeing it, or a dropped coloured digit would
        pass unnoticed."""
        m = IM.InkMask.from_ascii(self.ART)
        m.neutral_rows = [m.rows[0], m.rows[1], m.rows[2], bytes(m.width), m.rows[4]]
        self.assertTrue(m.any_ink(2, 3, 8, 4))
        self.assertEqual(m.row_runs(3, 0, 10), [(2, 6)])
        self.assertEqual(m.row_runs(3, 0, 10, neutral=True), [])


class TestToken(unittest.TestCase):
    def test_derived_edges(self):
        t = Token(text='31', x=0.75, y=0.13, w=0.03, h=0.017, conf=1.0, index=3)
        self.assertAlmostEqual(t.x1, 0.78, places=6)
        self.assertAlmostEqual(t.y1, 0.147, places=6)
        self.assertAlmostEqual(t.cx, 0.765, places=6)

    def test_digit_run_classification(self):
        self.assertTrue(Token('31', 0, 0, 1, 1, 1.0, 0).is_digit_run)
        self.assertTrue(Token(' 7 ', 0, 0, 1, 1, 1.0, 0).is_digit_run)
        self.assertFalse(Token('3,1', 0, 0, 1, 1, 1.0, 0).is_digit_run)
        self.assertFalse(Token('a) 7 +', 0, 0, 1, 1, 1.0, 0).is_digit_run)
        self.assertFalse(Token('', 0, 0, 1, 1, 1.0, 0).is_digit_run)


if __name__ == '__main__':
    unittest.main()
