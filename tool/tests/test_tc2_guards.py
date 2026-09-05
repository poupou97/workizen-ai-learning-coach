#!/usr/bin/env python3
"""Round 4 · Lane A-pipeline — tests for the deterministic number / unit / chemistry guards of tool/corpus/tc2_sdm.py
(failure class 2: formula / number / unit fidelity; docs/research/PIPELINE-ROUND4-FAILURE-CLASS-FIXES.md §2).

Synthetic strings only (no SGK text, Founder D4). Every guard withholds — none of them rewrites or guesses a value.

Run:  python3 -m unittest discover -s tool/tests -v"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import tc2_sdm  # noqa: E402


class NumberAgreementTests(unittest.TestCase):
    def test_same_digits_agree(self):
        self.assertFalse(tc2_sdm.numbers_disagree('Dung dịch 10% và 1 360 m', 'dung dich 10 va 1 360 m'))

    def test_letter_o_for_zero_is_a_disagreement(self):
        # KHTN 7 p21 shape: primary «A (1, O)» (letter O), verifier «A (1, 0)»
        self.assertTrue(tc2_sdm.numbers_disagree('A (1, O); D (1, 1)', 'a 1 0 d 1 1'))

    def test_footnote_mark_read_as_symbol_is_a_disagreement(self):
        # Ngữ văn 9 p67 shape: primary «Kiều(<)», verifier «Kiều(2)»
        self.assertTrue(tc2_sdm.numbers_disagree('Trích Truyện Kiều(<), TÁC GIẢ', 'trich truyen kieu 2 tac gia'))

    def test_a_run_cut_at_the_window_edge_is_tolerated(self):
        self.assertFalse(tc2_sdm.numbers_disagree('Bước 2. Đổ 500 mL nước', '2 do 500 ml nuoc 3'))
        self.assertFalse(tc2_sdm.numbers_disagree('Đổ 500 mL nước', '1 do 500 ml nuoc'))

    def test_an_edge_run_of_the_window_is_a_neighbours_number(self):
        self.assertFalse(tc2_sdm.numbers_disagree('Không có số nào ở đây', 'khong co so nao o day 12'))
        self.assertFalse(tc2_sdm.numbers_disagree('Không có số nào ở đây', '3 khong co so nao o day'))

    def test_an_interior_run_the_primary_dropped_is_a_disagreement(self):
        # Ngữ văn 9 p67 shape: the primary lost a footnote mark entirely
        self.assertTrue(tc2_sdm.numbers_disagree('Kim - Kiều gặp gỡ")', 'kim kieu gap go 1 nguyen du'))

    def test_decimal_comma_and_dot_normalise_the_same(self):
        self.assertFalse(tc2_sdm.numbers_disagree('khối lượng riêng 0,9 g/mL', 'khoi luong rieng 0 9 g ml'))
        self.assertTrue(tc2_sdm.numbers_disagree('khối lượng riêng 0,9 g/mL', 'khoi luong rieng 9 g ml'))


class UnitAndChemistryGuardTests(unittest.TestCase):
    def test_flattened_unit_exponent_is_caught(self):
        for t in ('diện tích 1 360 m2', 'thể tích 25 cm3', 'đơn vị dm2 và km2'):
            self.assertTrue(tc2_sdm.UNIT_EXP.search(t), t)

    def test_plain_units_and_words_are_not_caught(self):
        for t in ('dài 1 360 m', 'cách 3 km', 'sam3 là một từ', 'trang 12', 'm 2 bạn', 'cm 23'):
            self.assertFalse(tc2_sdm.UNIT_EXP.search(t), t)

    def test_chemical_formulas_and_flattened_subscripts_are_caught(self):
        for t in ('khí CO2 và H2O', 'dung dịch AgNO, 1%', 'dung dịch NH, 5%', 'phân tử H,O', 'muối NaCl2', 'Fe3O4'):
            self.assertTrue(tc2_sdm.CHEM.search(t), t)

    def test_ordinary_capitalised_words_are_not_caught(self):
        for t in ('Hà Nội, 2010', 'GV, HS thảo luận', 'Bài 12', 'TP. Hồ Chí Minh', 'NXB Giáo dục, 2021', 'Câu 1.'):
            self.assertFalse(tc2_sdm.CHEM.search(t), t)


if __name__ == '__main__':
    unittest.main()
