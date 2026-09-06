#!/usr/bin/env python3
"""Round 5 · Lane A2 — the named defects of the 97-row audit, as regression cases.

Founder rule, binding: the 97 rows are an **evaluation set, not a tuning set**. So each test here
pins the *shape* of the defect and its counterexamples, never the literal string — a rule that
recognises «3.10° m/s» and nothing else would pass this file and have fixed nothing. Every rule is
therefore also tested against the readings it must NOT touch: temperatures, angles, độ cồn.

Generalisation is measured separately, on a holdout this lane did not look at while writing the
rules; see `docs/research/MATH-ACCURACY-AUDIT-2026-09-06.md` §7.7.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'corpus'))

from mathfix import sci_notation as SN       # noqa: E402


class TestDefect1DestroyedExponent(unittest.TestCase):
    """`3×10⁸ m/s` → `3×10° m/s` — a physical constant served as nonsense, TRUSTED, today."""

    # Every string below is a real OCR line from poc-out/graph/ocr-body, not an invention.
    SERVED_WRONG = [
        'Trong đó, c là tốc độ ánh sáng trong chân không (c = 3.10° m/s);',
        'c là tốc độ ánh sáng trong chân không (c = 3.10° m/s); v là tốc độ ánh sáng trong môi trường.',
        '- Bar: 1 Bar = 10° Pa.',
        '1 kJ = 10°J',
        '1 MW = 10° W',
        '1 GW = 10° W',
        "Khoảng 2.10' W",
        'x 10° Q',
        "một cột thuy ngân cao 76 cm: 1 atm = 1,013.10' Pa.",
    ]

    def test_every_destroyed_exponent_is_detected(self):
        for t in self.SERVED_WRONG:
            with self.subTest(t):
                self.assertTrue(SN.withholds(t), t)

    def test_the_finding_names_its_rule_and_its_span(self):
        f = SN.find_destroyed_exponents('(c = 3.10° m/s)')[0]
        self.assertEqual(f.rule_id, 'destroyed-exponent-v1')
        self.assertEqual('(c = 3.10° m/s)'[f.start:f.end].strip(), '10°')

    def test_nothing_is_repaired(self):
        """Detection only. The exponent's value is not in the text — recovering it needs a
        recogniser on the printed region, and inventing it would be exactly the forbidden guess."""
        self.assertFalse(hasattr(SN, 'repair'))
        f = SN.find_destroyed_exponents('1 kJ = 10°J')[0]
        self.assertNotIn('proposed_value', f.__dataclass_fields__)


class TestDefect1MustNotOverWithhold(unittest.TestCase):
    """Over-withholding is the larger pool in the 97 rows (19 of 30). A guard that eats every «°»
    would trade one false trust for a hundred false withholds."""

    LEAVE_ALONE = [
        'Ethylene là chất khí ở điều kiện thường (hoá lỏng ở - 104 °C và hóa rắn ở -169 °C),',
        '• Độ cồn là số mililít ethylic alcohol nguyên chất có trong 100 mL dung dịch ở 20 °C.',
        'Bước 4: Đun lá trong cồn 90° đến khi sôi (Hình 24.2d).',
        '2. Chiếu tia sáng tới dưới góc tới 30° vào gương phẳng đặt thẳng đứng, vẽ hình biểu',
        'cho góc giữa dây và mặt đất bằng vĩ độ nơi em sống (Ví dụ, Hà Nội là 21°, Thành phố',
        'Ví dụ: cồn y tế 70° có nghĩa là trong 100 mL cồn 70° có chứa 70 mL',
        'Mai ơi! Từ băng giấy dài 3 m, làm thế nào lấy được đoạn băng giấy dài 2 m?',
        'Diện tích hình chữ nhật là 1 360 m2.',
    ]

    def test_a_temperature_an_angle_or_an_alcohol_strength_is_not_a_destroyed_exponent(self):
        for t in self.LEAVE_ALONE:
            with self.subTest(t):
                self.assertFalse(SN.withholds(t), t)

    def test_the_rule_needs_the_literal_ten(self):
        """«45°» is an angle whatever follows it; only a power of TEN loses an exponent this way."""
        self.assertFalse(SN.withholds('45° 2'))
        self.assertTrue(SN.withholds('10°2'))


class TestSiPrefixValidator(unittest.TestCase):
    """The page states the prefix relation, so SI fixes the exponent — as a CHECK on a future
    recogniser's reading, never as a way to invent one."""

    def test_the_printed_prefixes_entail_the_exponent(self):
        self.assertEqual(SN.si_expected_exponent('1 kJ = 10°J'), 3)
        self.assertEqual(SN.si_expected_exponent('1 MW = 10° W'), 6)
        self.assertEqual(SN.si_expected_exponent('1 GW = 10° W'), 9)

    def test_it_abstains_when_the_page_does_not_state_the_relation(self):
        self.assertIsNone(SN.si_expected_exponent('(c = 3.10° m/s)'))
        self.assertIsNone(SN.si_expected_exponent('- Bar: 1 Bar = 10° Pa.'))

    def test_it_abstains_when_the_two_units_are_not_the_same_kind(self):
        self.assertIsNone(SN.si_expected_exponent('1 kJ = 10° W'))

    def test_a_detection_carries_the_expectation_when_there_is_one(self):
        self.assertEqual(SN.find_destroyed_exponents('1 MJ = 10°J')[0].expected_exponent, 6)
        self.assertIsNone(SN.find_destroyed_exponents('(c = 3.10° m/s)')[0].expected_exponent)


class TestDefect2FlattenedFraction(unittest.TestCase):
    """`b) 3/10 + 5/21` → `b) 10 +`, on the real page. Corpus-gated: the corpus never enters git."""

    BOOK, PAGE = '05-sgk-toan-5-tap-mot', 22

    def setUp(self):
        try:
            import pymupdf                                    # noqa: F401
            import numpy                                      # noqa: F401
        except Exception:
            self.skipTest('PyMuPDF/numpy not installed (the raster path is CLI-only)')
        from mathfix import runner
        if not os.path.exists(runner.pdf_path(self.BOOK)):
            self.skipTest('corpus not on this machine (it never enters git)')
        from mathfix import detect as D
        from mathfix.inkmask import InkMask
        from mathfix.tokens import load_tokens
        mask = InkMask.from_pdf(runner.pdf_path(self.BOOK), self.PAGE)
        self.regions = D.find_fraction_regions(mask, load_tokens(self.BOOK, self.PAGE))

    def _in_row(self):
        """The «luyện tập 1 Tính» row, where item b) is printed «3/10 + 5/21»."""
        return [r for r in self.regions if 0.775 < r.bar.y0 < 0.786]

    def test_both_printed_fractions_of_item_b_are_FOUND(self):
        """The whole point of raster-first detection: the region exists even though the OCR lost
        the numerator «3» entirely, so it can be withheld with its crop instead of missed."""
        band = self._in_row()
        self.assertEqual(len(band), 8, 'the row prints eight fractions across four items')
        b_items = [r for r in band if 0.29 < r.bar.x0 < 0.46]
        self.assertEqual(len(b_items), 2, 'item b) prints two fractions')

    def test_neither_is_extracted_because_the_digits_are_not_on_the_page_output(self):
        for r in self._in_row():
            if 0.29 < r.bar.x0 < 0.46:
                self.assertFalse(r.extractable)
                self.assertIn(r.reason, ('numerator_token_missing', 'denominator_token_missing',
                                         'denominator_ambiguous', 'numerator_ambiguous',
                                         'token_shared'))

    def test_no_repair_is_proposed_for_the_block(self):
        """A wrong restored formula is worse than a withheld one: one unreadable item poisons it."""
        from mathfix import extract as E
        from mathfix.inkmask import InkMask
        from mathfix.tokens import load_tokens
        from mathfix import runner
        mask = InkMask.from_pdf(runner.pdf_path(self.BOOK), self.PAGE)
        toks = load_tokens(self.BOOK, self.PAGE)
        cand = E.math_line_candidate(toks, self._in_row(), mask)
        self.assertEqual(cand.proposed_value, '')
        self.assertTrue(cand.reason.startswith('region_unextractable'), cand.reason)


class TestDefect2DroppedOperator(unittest.TestCase):
    """`d) 20/18 − 2/5` was restored as `d) 20/18 2/5` — the one wrong restore this lane produced.

    By area the printed «−» is 3.75 % of the block's glyph ink, under any ceiling one would dare
    set; it is caught by SHAPE, as the widest unbroken run of ink no OCR token accounts for. This
    test pins the refusal AND the reason, so a later change that keeps the refusal by accident (a
    tighter area ceiling, say) still fails. Corpus-gated: the corpus never enters git.
    """

    BOOK, PAGE, BLOCK = '05-sgk-toan-5-tap-mot', 22, ':020'

    def setUp(self):
        try:
            import pymupdf                                    # noqa: F401
            import numpy                                      # noqa: F401
        except Exception:
            self.skipTest('PyMuPDF/numpy not installed')
        from mathfix import runner
        self.runner = runner
        if not os.path.exists(runner.pdf_path(self.BOOK)):
            self.skipTest('corpus not on this machine')
        sdm = (f'{runner.ROOT}/poc-out/round4/legacy/batch-1-rerun-tc2-p2/tcroot/poc-out/'
               f'trusted-corpus/tc-v2/tc2-p2/sdm/{self.BOOK}/p{self.PAGE:03d}.sdm.json')
        if not os.path.exists(sdm):
            self.skipTest('the round-4 legacy rerun is not on this machine')
        import json
        with open(sdm) as fh:
            page = json.load(fh)
        self.report = runner.page_report(self.BOOK, self.PAGE, sdm=page)

    def _block(self):
        for b in self.report['blocks']:
            if b['block_id'].endswith(self.BLOCK):
                return b
        self.fail(f'block {self.BLOCK} not found on the page')

    def test_the_block_is_not_restored(self):
        b = self._block()
        self.assertEqual(b['proposed_value'], 'd) 20/18 2/5',
                         'the candidate is still built — the refusal must come from validation')
        self.assertEqual(b['verdict'], 'WITHHOLD')
        self.assertEqual(b['disposition'], 'WITHHELD')

    def test_it_is_the_run_length_and_not_the_area_that_refuses_it(self):
        ev = [v for v in self._block()['validations'] if v['validator_id'] == 'ink-accounted-v1'][0]
        self.assertEqual(ev['verdict'], 'FAIL')
        self.assertLess(ev['evidence']['unaccounted_share'], ev['evidence']['ceiling'],
                        'by area alone this block would have been restored without its operator')
        self.assertGreater(ev['evidence']['widest_unaccounted_run'], ev['evidence']['run_ceiling'])


if __name__ == '__main__':
    unittest.main()
