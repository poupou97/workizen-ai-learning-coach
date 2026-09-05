#!/usr/bin/env python3
"""Round 5 · Lane A2 — extraction and the deterministic validators.

«A wrong restored formula is worse than a withheld one» is the governing rule, so most of what is
pinned here is REFUSAL: the dropped digit, the invented character, the arithmetic that does not
come out, the block that is half prose, the block whose tokens sit on two baselines.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'corpus'))

from mathfix import detect as D              # noqa: E402
from mathfix import extract as E             # noqa: E402
from mathfix import validate as V            # noqa: E402
from mathfix.inkmask import InkMask          # noqa: E402
from mathfix.tokens import Token             # noqa: E402

# «1 over 5» drawn at 20 × 14, the same picture the detector tests use.
FRACTION = """\
....................
.........#..........
........##..........
.........#..........
.........#..........
....................
....###########.....
....................
........####........
.......#............
.......####.........
..........#.........
.......###..........
....................
"""
PARAMS = dict(min_len_frac=0.30, max_len_frac=0.90, max_thick_frac=0.20)


def num(text='1'):
    return Token(text, x=8 / 20, y=1 / 14, w=2 / 20, h=4 / 14, conf=1.0, index=0)


def den(text='5'):
    return Token(text, x=7 / 20, y=8 / 14, w=4 / 20, h=5 / 14, conf=1.0, index=1)


def region(mask, tokens):
    rs = D.find_fraction_regions(mask, tokens, bar_params=PARAMS)
    return rs[0]


class TestFractionCandidate(unittest.TestCase):
    def setUp(self):
        self.m = InkMask.from_ascii(FRACTION)

    def test_a_validated_region_proposes_n_over_d(self):
        c = E.fraction_candidate(region(self.m, [num(), den()]))
        self.assertEqual(c.proposed_value, '1/5')
        self.assertEqual(c.rule_id, 'stacked-fraction-v1')
        self.assertEqual([o['kind'] for o in c.original_observations],
                         ['ocr_line', 'ocr_line', 'raster_bar'])

    def test_an_unextractable_region_proposes_nothing_and_says_why(self):
        c = E.fraction_candidate(region(self.m, [num()]))
        self.assertEqual(c.proposed_value, '')
        self.assertEqual(c.reason, 'denominator_token_missing')

    def test_the_source_observations_are_never_rewritten(self):
        toks = [num(), den()]
        c = E.fraction_candidate(region(self.m, toks))
        self.assertEqual(c.original_observations[0]['text'], '1')
        self.assertEqual(toks[0].text, '1')
        self.assertNotEqual(c.proposed_value, toks[0].text)


class TestDigitProvenance(unittest.TestCase):
    def test_a_value_built_from_the_observations_passes(self):
        c = E.fraction_candidate(region(InkMask.from_ascii(FRACTION), [num('3'), den('10')]))
        self.assertEqual(c.proposed_value, '3/10')
        self.assertEqual(V.digit_provenance_v1(c).verdict, 'PASS')

    def test_an_invented_digit_fails(self):
        c = E.fraction_candidate(region(InkMask.from_ascii(FRACTION), [num('3'), den('10')]))
        c.proposed_value = '3/100'
        r = V.digit_provenance_v1(c)
        self.assertEqual(r.verdict, 'FAIL')
        self.assertEqual(r.evidence['invented'], '0')

    def test_a_reused_digit_fails_even_though_every_character_was_observed(self):
        """«19/33 − 3/5 assembled from two printed items» is the round-3 defect; a substring check
        would have let it through, so provenance counts characters."""
        c = E.fraction_candidate(region(InkMask.from_ascii(FRACTION), [num('3'), den('5')]))
        c.proposed_value = '3/55'
        self.assertEqual(V.digit_provenance_v1(c).verdict, 'FAIL')


class TestArithSelfCheck(unittest.TestCase):
    def check(self, value):
        return V.arith_selfcheck_v1(E.Candidate('x', value, [], []))

    def test_a_true_printed_equality_passes(self):
        self.assertEqual(self.check('7/10 = 0,7').verdict, 'PASS')

    def test_a_false_one_fails(self):
        self.assertEqual(self.check('7/10 = 0,8').verdict, 'FAIL')

    def test_precedence_is_honoured(self):
        self.assertEqual(self.check('1 + 2 × 3 = 7').verdict, 'PASS')

    def test_an_expression_with_no_equality_is_not_applicable(self):
        r = self.check('a) 7 + 1/5')
        self.assertEqual(r.verdict, 'NOT_APPLICABLE')

    def test_an_unparseable_side_is_not_applicable_rather_than_a_pass(self):
        self.assertEqual(self.check('S = a × b').verdict, 'NOT_APPLICABLE')

    def test_the_enumerator_does_not_join_the_arithmetic(self):
        self.assertEqual(self.check('b) 70/100 = 0,70').verdict, 'PASS')


class TestInkAccounted(unittest.TestCase):
    """The dropped-digit check: ink inside the region that no observation covers."""

    # «14 over 5», where the OCR box covers only the «4».
    DROPPED = """\
....................
.......#.##.........
.......#.#.#........
.......#.#.#........
.......#.##.........
....................
....###########.....
....................
........####........
.......#............
.......####.........
..........#.........
.......###..........
....................
"""

    def test_ink_the_observations_do_not_cover_is_reported(self):
        m = InkMask.from_ascii(self.DROPPED)
        # the OCR read only the «4»: a box over columns 9..12, missing the «1» at column 7
        n = Token('4', x=9 / 20, y=1 / 14, w=3 / 20, h=4 / 14, conf=1.0, index=0)
        r = region(m, [n, den()])
        c = E.fraction_candidate(r)
        self.assertEqual(c.proposed_value, '4/5')
        res = V.ink_accounted_v1(c, m, r.bbox, text_height=4 / 14, bar_len=r.bar.length)
        self.assertEqual(res.verdict, 'FAIL')
        self.assertGreater(res.evidence['unaccounted_share'], V.MAX_INK_UNACCOUNTED)

    def test_a_complete_reading_accounts_for_all_the_ink(self):
        m = InkMask.from_ascii(FRACTION)
        r = region(m, [num(), den()])
        c = E.fraction_candidate(r)
        res = V.ink_accounted_v1(c, m, r.bbox, text_height=4 / 14, bar_len=r.bar.length)
        self.assertEqual(res.verdict, 'PASS', res.evidence)


class TestVinculumRaster(unittest.TestCase):
    def test_a_bar_longer_than_both_halves_passes(self):
        m = InkMask.from_ascii(FRACTION)
        r = region(m, [num(), den()])
        self.assertEqual(V.vinculum_raster(r, m).verdict, 'PASS')

    def test_a_bar_no_longer_than_its_halves_fails(self):
        """Printed typography: a vinculum is drawn at least as wide as the half it separates.

        Ink that spills past both ends of the bar is not that bar's numerator — it is the rest of
        the line, and reading it as a numerator is the "assembled from two printed items" defect.
        """
        art = """\
....................
....##.##.##.##.....
....##.##.##.##.....
....................
.....#########......
....................
....##.##.##.##.....
....##.##.##.##.....
....................
"""
        m = InkMask.from_ascii(art)
        rs = D.find_fraction_regions(m, [], bar_params=dict(min_len_frac=0.30, max_len_frac=0.90,
                                                            max_thick_frac=0.30))
        self.assertTrue(rs, 'the middle rule has detached ink above and below')
        r = V.vinculum_raster(rs[0], m)
        self.assertEqual(r.verdict, 'FAIL')
        self.assertLess(r.evidence['overhang'], V.MIN_BAR_OVERHANG)


class TestMathLine(unittest.TestCase):
    def test_a_whole_arithmetic_line_is_assembled_in_printed_order(self):
        m = InkMask.from_ascii(FRACTION)
        lead = Token('a) 7 +', x=1 / 20, y=6 / 14, w=3 / 20, h=2 / 14, conf=1.0, index=2)
        toks = [num(), den(), lead]
        rs = D.find_fraction_regions(m, toks, bar_params=PARAMS)
        c = E.math_line_candidate(toks, rs, m)
        self.assertEqual(c.proposed_value, 'a) 7 + 1/5')

    def test_one_unreadable_item_poisons_the_whole_block(self):
        m = InkMask.from_ascii(FRACTION)
        lead = Token('c) 3 -', x=1 / 20, y=6 / 14, w=3 / 20, h=2 / 14, conf=1.0, index=2)
        toks = [num('11'), lead]                      # the denominator token was lost
        rs = D.find_fraction_regions(m, toks, bar_params=PARAMS)
        c = E.math_line_candidate(toks, rs, m)
        self.assertEqual(c.proposed_value, '')
        self.assertEqual(c.reason, 'region_unextractable:denominator_token_missing')

    def test_a_block_carrying_prose_is_not_this_lane_s_to_repair(self):
        m = InkMask.from_ascii(FRACTION)
        prose = Token('Hai mẫu số 5 và 2 không chia hết', x=0.0, y=6 / 14, w=0.9, h=2 / 14,
                      conf=1.0, index=2)
        toks = [num(), den(), prose]
        rs = D.find_fraction_regions(m, toks, bar_params=PARAMS)
        self.assertEqual(E.math_line_candidate(toks, rs, m).reason, 'prose_token_in_block')

    def test_a_block_whose_tokens_sit_on_two_baselines_fails_closed(self):
        m = InkMask.from_ascii(FRACTION)
        a = Token('a) 7 +', x=1 / 20, y=6 / 14, w=3 / 20, h=2 / 14, conf=1.0, index=2)
        b = Token('b) 2 -', x=1 / 20, y=12 / 14, w=3 / 20, h=2 / 14, conf=1.0, index=3)
        toks = [num(), den(), a, b]
        rs = D.find_fraction_regions(m, toks, bar_params=PARAMS)
        self.assertEqual(E.math_line_candidate(toks, rs, m).reason, 'multiple_baselines')

    def test_a_block_with_no_fraction_is_left_alone(self):
        m = InkMask.from_ascii(FRACTION)
        self.assertEqual(E.math_line_candidate([], [], m).reason, 'no_fraction_region')


class TestOverallVerdict(unittest.TestCase):
    def test_restore_needs_a_pass_and_no_fail(self):
        m = InkMask.from_ascii(FRACTION)
        r = region(m, [num(), den()])
        c = E.fraction_candidate(r)
        verdict, results = V.validate(c, m, r.bbox, 4 / 14, r.bar.length)
        self.assertEqual(verdict, 'RESTORE')
        self.assertIn('arith-selfcheck-v1', [x.validator_id for x in results])

    def test_a_single_fail_withholds_the_whole_candidate(self):
        m = InkMask.from_ascii(FRACTION)
        r = region(m, [num(), den()])
        c = E.fraction_candidate(r)
        c.proposed_value = '1/50'                   # an invented «0»
        verdict, _ = V.validate(c, m, r.bbox, 4 / 14, r.bar.length)
        self.assertEqual(verdict, 'WITHHOLD')

    def test_not_applicable_everywhere_is_not_a_restore(self):
        """«Nothing contradicted it» is not evidence."""
        na = V.ValidationResult('NOT_APPLICABLE', {}, 'x')
        self.assertEqual(V.overall_verdict([na, na]), 'WITHHOLD')
        self.assertEqual(V.overall_verdict([]), 'WITHHOLD')

    def test_one_fail_outweighs_any_number_of_passes(self):
        ok = V.ValidationResult('PASS', {}, 'a')
        bad = V.ValidationResult('FAIL', {}, 'b')
        self.assertEqual(V.overall_verdict([ok, ok, ok, bad]), 'WITHHOLD')
        self.assertEqual(V.overall_verdict([ok, ok, ok]), 'RESTORE')

    def test_a_candidate_with_no_value_is_never_restored(self):
        m = InkMask.from_ascii(FRACTION)
        r = region(m, [num()])
        verdict, results = V.validate(E.fraction_candidate(r), m, r.bbox, 4 / 14, r.bar.length)
        self.assertEqual((verdict, results), ('WITHHOLD', []))


if __name__ == '__main__':
    unittest.main()
