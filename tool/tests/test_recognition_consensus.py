#!/usr/bin/env python3
"""Round 6 · Workstream B — the crop geometry and the consensus rule.

These are the two places where a recogniser can quietly become a fabricator, so they are the two
places tested hardest:

  boxes      the rectangle must be derived from the printed vinculum, never from the OCR — a box
             that reaches the neighbouring fraction imports its digits, and a reading assembled
             from two fractions is the round-3 failure with better provenance.
  consensus  a reading is accepted only when independent observations agree, and abstention is
             never a pass. Every refusal below is a refusal this experiment actually needed on a
             real page.

No corpus, no raster, no Vision, no network.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'corpus'))

from recognition import boxes as B            # noqa: E402
from recognition import consensus as C        # noqa: E402


def lines(*texts, y=None):
    """Vision returns lines; only text and vertical order matter to `consensus`."""
    ys = y if y is not None else [i * 0.3 for i in range(len(texts))]
    return [dict(text=t, conf=1.0, x=0.1, y=yy, w=0.2, h=0.2) for t, yy in zip(texts, ys)]


class TestBoxes(unittest.TestCase):
    BAR = (0.37751, 0.7806, 0.02925, 0.001302)     # `3/10` on Toán 5 tập một p22, measured
    MH = 0.01599                                   # that page's own median OCR line height

    def test_three_boxes_in_a_fixed_order(self):
        got = B.fraction_boxes(self.BAR, self.MH)
        self.assertEqual([b.kind for b in got], ['numerator', 'denominator', 'region'])

    def test_the_numerator_box_sits_above_the_bar_and_never_touches_it(self):
        n, d, r = B.fraction_boxes(self.BAR, self.MH)
        self.assertLess(n.y1, self.BAR[1])
        self.assertGreater(d.y0, self.BAR[1] + self.BAR[3])
        self.assertLess(r.y0, n.y0 + 1e-9)
        self.assertGreater(r.y1, d.y1 - 1e-9)

    def test_the_box_does_not_reach_the_neighbouring_fraction(self):
        """On the `1 Tính` row of Toán 5 tập một p22 six fractions sit within 0.10 of page width.
        The next bar starts at 0.43327; the crop must end before it."""
        n, _, _ = B.fraction_boxes(self.BAR, self.MH)
        self.assertLess(n.x1, 0.43327)

    def test_a_page_with_no_ocr_at_all_still_gets_a_box(self):
        n, d, r = B.fraction_boxes(self.BAR, None)
        self.assertFalse(r.is_degenerate)
        self.assertLess(n.y1, d.y0)

    def test_native_pixels_report_the_information_actually_available(self):
        """The corpus pages are 100 ppi scans. `crop_pixels` at scale 20 is interpolation; the
        honest number beside it is how many SOURCE pixels the box holds."""
        _, _, r = B.fraction_boxes(self.BAR, self.MH)
        page_pt = (787.68, 1105.92)
        big = B.crop_pixels(r, page_pt, 20.0)
        native = B.native_pixels(r, page_pt)
        self.assertGreater(big[0], native[0] * 10)
        self.assertGreater(native[1], 8)


class TestHalfReading(unittest.TestCase):
    def test_two_agreeing_scales_are_read(self):
        r = C.read_half({6.0: lines('3'), 20.0: lines('3')})
        self.assertEqual((r.verdict, r.value), (C.READ, '3'))
        self.assertEqual(r.agreeing_scales, (6.0, 20.0))

    def test_one_scale_alone_is_not_evidence(self):
        r = C.read_half({6.0: lines('3'), 20.0: lines()})
        self.assertEqual(r.verdict, C.INSUFFICIENT)
        self.assertIsNone(C.read_fraction('k', {6.0: lines('3')}, {6.0: lines('10')},
                                          {6.0: lines('3', '10')}).value)

    def test_two_scales_that_disagree_fail_closed(self):
        r = C.read_half({6.0: lines('3'), 20.0: lines('8'), 14.0: lines('3')})
        self.assertEqual(r.verdict, C.CONFLICT)
        self.assertIsNone(r.value)

    def test_nothing_legible_is_UNREAD_and_not_a_pass(self):
        self.assertEqual(C.read_half({6.0: lines(), 20.0: lines()}).verdict, C.UNREAD)
        self.assertEqual(C.read_half({6.0: lines('m/s'), 20.0: lines('kg')}).verdict, C.UNREAD)

    def test_two_digit_runs_in_one_half_are_ambiguous_and_never_joined(self):
        """Scale 6 on the real page returned `1` and `0` for a printed `10`. Joining them is
        reconstruction from fragments — the thing this whole lane exists to refuse. Another scale
        may read it whole; this one abstains."""
        r = C.read_half({6.0: lines('1', '0')})
        self.assertEqual(r.verdict, C.AMBIGUOUS)
        self.assertIsNone(r.value)


class TestFractionReading(unittest.TestCase):
    def test_the_named_defect(self):
        """`b) 3/10 + 5/21` served as `b) 10 +`. The numerator `3` is absent from the whole-page
        OCR entirely; two crop scales read it and the region crop shows it stacked over `10`."""
        fr = C.read_fraction('toan5:p022:r028',
                             {6.0: lines('3'), 20.0: lines('3')},
                             {6.0: lines('10'), 20.0: lines('10')},
                             {20.0: lines('3', '10')})
        self.assertEqual((fr.verdict, fr.value), (C.READ, '3/10'))
        self.assertEqual(fr.region_agreement_scale, 20.0)

    def test_halves_read_but_never_seen_stacked_are_refused(self):
        fr = C.read_fraction('k', {6.0: lines('3'), 20.0: lines('3')},
                             {6.0: lines('10'), 20.0: lines('10')},
                             {20.0: lines('3', '10', '5')})
        self.assertEqual(fr.verdict, 'REGION_UNCONFIRMED')
        self.assertIsNone(fr.value)

    def test_the_wrong_way_up_is_refused(self):
        fr = C.read_fraction('k', {6.0: lines('3'), 20.0: lines('3')},
                             {6.0: lines('10'), 20.0: lines('10')},
                             {20.0: lines('10', '3')})
        self.assertEqual(fr.verdict, 'REGION_UNCONFIRMED')

    def test_a_refusal_names_which_half_failed(self):
        fr = C.read_fraction('k', {6.0: lines('3'), 20.0: lines('8')},
                             {6.0: lines('10'), 20.0: lines('10')}, {20.0: lines('3', '10')})
        self.assertTrue(fr.reason.startswith('numerator:'), fr.reason)


if __name__ == '__main__':
    unittest.main()
