#!/usr/bin/env python3
"""Round 6 · Workstream B — the FAILURE CENSUS detectors.

Every case below is a real string from the corpus, or a real string this detector must never
fire on. The census decides what gets built, so a detector that over-fires does not merely add
noise: it invents a failure class and buys work that no defect needed. Round 5 killed three rules
that way, and the counter-examples here are the ones that would have killed them earlier.

No corpus, no raster, no network. These run on the CI box.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'corpus'))

from recognition import census as C          # noqa: E402


def classes(text, book='09-sgk-khoa-hoc-tu-nhien-9', page=27):
    return {f.cls for f in C.line_findings(book, page, text)}


class TestRomanNumeral(unittest.TestCase):
    """`II` read as `I1` — the Founder's named defect, and the sequence it breaks."""

    def test_the_named_defect(self):
        self.assertIn(C.ROMAN_NUMERAL, classes('I1 - Định luật khúc xạ ánh sáng'))

    def test_the_other_named_defect(self):
        self.assertIn(C.ROMAN_NUMERAL, classes('I1 - Khái niệm năng lượng nhiệt'))

    def test_lowercase_l_is_the_same_failure(self):
        """`Il - Glucose và saccharose` — found in the corpus scan. The second stroke came back
        as a lowercase L rather than as a digit; it is the same lost glyph."""
        self.assertIn(C.ROMAN_NUMERAL, classes('Il - Glucose và saccharose'))

    def test_a_correct_roman_heading_is_not_a_finding(self):
        for good in ('II - Định luật khúc xạ ánh sáng', 'I. Mở đầu', 'III – Vận dụng',
                     'IV. Luyện tập'):
            self.assertNotIn(C.ROMAN_NUMERAL, classes(good), good)

    def test_prose_beginning_with_a_capital_i_is_not_a_finding(self):
        self.assertNotIn(C.ROMAN_NUMERAL, classes('In hình vẽ ra giấy rồi cắt theo nét đứt.'))


class TestSuperscript(unittest.TestCase):
    """`3×10⁸ m/s` served as `3×10° m/s` — born in recognition, served TRUSTED."""

    def test_speed_of_light(self):
        self.assertIn(C.SUPERSCRIPT,
                      classes('Trong đó, c là tốc độ ánh sáng trong chân không (c = 3.10° m/s);'))

    def test_the_si_prefixed_forms(self):
        for s in ('1 kJ = 10°J', '1 MJ = 10°J', '1 MW = 10° W', '1 GW = 10° W', '1 Bar = 10° Pa.'):
            self.assertIn(C.SUPERSCRIPT, classes(s), s)

    def test_a_temperature_or_an_angle_is_never_a_finding(self):
        for s in ('Nhiệt độ 10 °C', 'góc 30°', 'cồn 90°', 'vĩ độ 21°', 'diện tích 1 360 m2'):
            self.assertNotIn(C.SUPERSCRIPT, classes(s), s)


class TestSymbolConfusion(unittest.TestCase):
    """Ω read as `S2`. The line the Founder named is both a guard false positive and a
    destroyed symbol at once, and the census must count the second thing."""

    def test_the_named_defect(self):
        self.assertIn(C.SYMBOL_CONFUSION, classes('1 MS = 1 000 000 S2'))

    def test_unit_prose(self):
        self.assertIn(C.SYMBOL_CONFUSION, classes('được tính bằng ôm (S2).'))

    def test_a_bare_capital_and_digit_without_a_unit_context_is_not_a_finding(self):
        self.assertNotIn(C.SYMBOL_CONFUSION, classes('Bảng S2 dưới đây mô tả các loài.'))


class TestSubscript(unittest.TestCase):
    """A subscript flattened onto the baseline. Counted as a LOST LEVEL, not as chemistry:
    `tc2_sdm.CHEM` fires on the same shape and round 5 measured >=40 of its 173 matches as
    non-chemical, so calling this class «chemistry» would repeat that error in the census."""

    def test_an_element_with_an_index(self):
        self.assertIn(C.SUBSCRIPT, classes('Khí O2 chiếm khoảng 21 % thể tích không khí.'))

    def test_a_physics_index(self):
        self.assertIn(C.SUBSCRIPT, classes('I1 - Định luật khúc xạ ánh sáng'))

    def test_a_lowercase_word_with_a_digit_is_not_a_finding(self):
        self.assertNotIn(C.SUBSCRIPT, classes('bài 2 trang 15'))


class TestSegmentation(unittest.TestCase):
    """`b) 10 +.` where the page prints `b) 3/10 +` — the enumerator, the DENOMINATOR and the
    operator fused into one token while the numerator was never read at all."""

    def test_the_named_defect(self):
        self.assertIn(C.SEGMENTATION, classes('b) 10 +.'))

    def test_a_normal_enumerated_item_is_not_a_finding(self):
        for s in ('b) 3/10 + 5/21', 'a) Tính rồi so sánh giá trị của hai biểu thức.', 'c) 16 + 21'):
            self.assertNotIn(C.SEGMENTATION, classes(s), s)


class TestDiacritics(unittest.TestCase):
    """The unigram test is kept as a FALSIFIED baseline; the bigram test is the survivor.

    Measured over 2 398 513 OCR lines the unigram form returns 26 703 «candidates» whose top rows
    are `qua`/`quá`, `cung`/`cũng`, `nay`/`này` — ordinary Vietnamese words, every one. The test
    below pins that behaviour so nobody re-adopts the rule by accident.
    """

    def test_strip(self):
        self.assertEqual(C._strip_diacritics('Cộng hoà'), 'Cong hoa')
        self.assertEqual(C._strip_diacritics('Đường'), 'Duong')

    def test_unigram_cannot_tell_a_homograph_from_a_lost_tone(self):
        lines = {'b': ['qua sông'] * 20 + ['quá trình'] * 200}
        rows = C.diacritic_candidates(C.diacritic_index(lines)).get('b', [])
        self.assertTrue(any(r[0] == 'qua' for r in rows),
                        'the unigram rule fires on a real word — this is the falsification')

    def test_bigram_finds_the_collocation_the_book_contradicts_itself_on(self):
        lines = {'b': ['nước cộng hoà xã hội'] * 60 + ['nước cong hoa xã hội'] * 2}
        rows = C.diacritic_bigram_candidates(C.diacritic_bigram_index(lines)).get('b', [])
        self.assertIn('cong hoa', [r[0] for r in rows])

    def test_bigram_is_silent_when_both_spellings_are_common(self):
        lines = {'b': ['qua sông'] * 100 + ['quá trình'] * 100}
        rows = C.diacritic_bigram_candidates(C.diacritic_bigram_index(lines)).get('b', [])
        self.assertEqual([r for r in rows if r[0] == 'qua song'], [])


if __name__ == '__main__':
    unittest.main()
