#!/usr/bin/env python3
"""Round 5 · Lane A2 — the canonical structured representation.

Founder, STEM P0: *«STOP treating flattened OCR text as the canonical representation.»* So what is
pinned here is that the AST is the object, LaTeX is derived from it one way only, and a printed
expression that is not a whole expression cannot be built at all.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'corpus'))

from mathfix import nodes as A                # noqa: E402
from mathfix import build as B              # noqa: E402
from mathfix import expression as X         # noqa: E402


def frac(a, b):
    return A.Frac(A.Num(a), A.Num(b))


class TestTheFounderSExample(unittest.TestCase):
    """«3/10 + 5/21 must not exist only as a string; the AST understands ADD(FRACTION(3,10), …)»."""

    def setUp(self):
        self.node = A.BinOp(A.ADD, frac('3', '10'), frac('5', '21'))

    def test_the_ast_is_the_shape_the_order_names(self):
        j = self.node.to_json()
        self.assertEqual(j['kind'], 'ADD')
        self.assertEqual(j['left'], dict(kind='FRACTION',
                                         num=dict(kind='NUM', literal='3'),
                                         den=dict(kind='NUM', literal='10')))

    def test_latex_is_derived_from_the_ast(self):
        self.assertEqual(self.node.to_latex(), r'\frac{3}{10} + \frac{5}{21}')

    def test_the_text_projection_is_a_courtesy_not_a_source(self):
        self.assertEqual(self.node.to_text(), '3/10 + 5/21')

    def test_the_value_is_exact_rational_arithmetic(self):
        self.assertEqual(self.node.value(), __import__('fractions').Fraction(113, 210))

    def test_a_tree_survives_a_round_trip_through_its_own_json(self):
        self.assertEqual(A.from_json(self.node.to_json()), self.node)

    def test_there_is_no_way_back_from_latex(self):
        """If a string could become structure, a hand-edited or model-generated LaTeX would
        launder itself into truth. `from_json` exists; `from_latex` must not."""
        self.assertFalse(hasattr(A, 'from_latex'))
        self.assertFalse(hasattr(A, 'parse'))


class TestPhysicsNodes(unittest.TestCase):
    """§6: `m/s` and `m/s²` must be different objects, and `10°` must be unbuildable."""

    def test_speed_and_acceleration_are_different_structures(self):
        speed = A.Unit('m', den=A.Unit('s'))
        accel = A.Unit('m', den=A.Unit('s', exp=2))
        self.assertNotEqual(speed, accel)
        self.assertEqual(speed.to_text(), 'm/s')
        self.assertEqual(accel.to_text(), 'm/s²')
        self.assertEqual(accel.to_latex(), 'm/s^{2}')

    def test_the_speed_of_light_is_a_quantity_with_a_power_of_ten(self):
        c = A.Quantity(A.BinOp(A.MUL, A.Num('3'), A.Power(A.Num('10'), A.Num('8'))),
                       A.Unit('m', den=A.Unit('s')))
        self.assertEqual(c.to_text(), '3 × 10^8 m/s')
        self.assertEqual(c.to_latex(), r'3 \times {10}^{8}\ \mathrm{m/s}')
        self.assertEqual(c.value(), 300000000)

    def test_a_destroyed_exponent_has_no_representation(self):
        """§6 asks for «structurally impossible transformations» to be detectable. `3×10° m/s` is
        not flagged here — it is unbuildable: there is no degree node, and `Num('°')` has no value.
        """
        self.assertFalse(any(n == 'DEG' or n == 'DEGREE' for n in dir(A)))
        self.assertIsNone(A.Num('°').value())
        self.assertIsNone(A.Power(A.Num('10'), A.Num('°')).value())

    def test_a_unit_round_trips(self):
        u = A.Unit('m', den=A.Unit('s', exp=2))
        self.assertEqual(A.from_json(u.to_json()), u)


class TestBuildFromAtoms(unittest.TestCase):
    def atoms(self, spec):
        """spec: [(x, kind, payload)] written in printed order."""
        return [B.Atom(x, k, p) for x, k, p in spec]

    def test_a_whole_printed_item_parses(self):
        node = B.build_row(self.atoms([
            (0.10, 'enum', 'a)'), (0.12, 'num', '7'), (0.14, 'op', A.ADD),
            (0.16, 'node', frac('1', '5'))]))
        self.assertEqual(node.to_text(), 'a) 7 + 1/5')
        self.assertEqual(node.to_latex(), r'\text{a)}\ 7 + \frac{1}{5}')

    def test_precedence_is_school_precedence(self):
        node = B.build_row(self.atoms([
            (0.1, 'num', '1'), (0.2, 'op', A.ADD), (0.3, 'num', '2'),
            (0.4, 'op', A.MUL), (0.5, 'num', '3')]))
        self.assertEqual(node.to_json()['kind'], 'ADD')
        self.assertEqual(node.value(), 7)

    def test_a_dangling_operator_cannot_be_built(self):
        """«b) 10 +» — the round-4 defect. R2 request (b), met structurally: the shipped MATH regex
        cannot express this, because it requires a digit AFTER the operator."""
        with self.assertRaises(B.Unparseable) as e:
            B.build_row(self.atoms([(0.1, 'enum', 'b)'), (0.2, 'num', '10'), (0.3, 'op', A.ADD)]))
        self.assertIn('ends on an operator', str(e.exception))

    def test_two_operands_with_no_operator_cannot_be_built(self):
        """«d) 20/18 2/5» — the operator the OCR dropped. Refused by the grammar, not by a pixel
        count, so it is refused even where the raster check cannot see it."""
        with self.assertRaises(B.Unparseable):
            B.build_row(self.atoms([(0.1, 'node', frac('20', '18')), (0.2, 'node', frac('2', '5'))]))

    def test_one_destroyed_item_poisons_the_whole_row(self):
        with self.assertRaises(B.Unparseable):
            B.build_row(self.atoms([
                (0.1, 'enum', 'a)'), (0.2, 'num', '1'), (0.3, 'op', A.ADD), (0.4, 'num', '2'),
                (0.5, 'enum', 'b)'), (0.6, 'num', '10'), (0.7, 'op', A.ADD)]))

    def test_a_row_of_sound_items_builds(self):
        row = B.build_row(self.atoms([
            (0.1, 'enum', 'a)'), (0.2, 'num', '1'), (0.3, 'op', A.ADD), (0.4, 'num', '2'),
            (0.5, 'enum', 'b)'), (0.6, 'num', '3'), (0.7, 'op', A.SUB), (0.8, 'num', '4')]))
        self.assertEqual(row.to_text(), 'a) 1 + 2    b) 3 − 4')


class TestAtomsOfToken(unittest.TestCase):
    def kinds(self, text):
        return [(a.kind, a.payload) for a in B.atoms_of_token(text, 0.0, 1.0)]

    def test_an_enumerator_is_a_label_not_an_operand(self):
        self.assertEqual(self.kinds('a) 7 +'), [('enum', 'a)'), ('num', '7'), ('op', A.ADD)])

    def test_ascii_hyphen_is_an_operator(self):
        """The shipped `MATH` regex omits ASCII '-' from its operator class; a printed minus that
        the OCR renders as a hyphen must not become invisible."""
        self.assertEqual(self.kinds('3 - 4'), [('num', '3'), ('op', A.SUB), ('num', '4')])

    def test_a_vietnamese_decimal_keeps_its_comma(self):
        self.assertEqual(self.kinds('0,7'), [('num', '0,7')])
        self.assertEqual(A.Num('0,7').value(), __import__('fractions').Fraction(7, 10))

    def test_an_unknown_mark_aborts_rather_than_being_skipped(self):
        with self.assertRaises(B.Unparseable):
            B.atoms_of_token('7 ⊕ 2', 0.0, 1.0)

    def test_prose_cannot_leak_into_an_expression(self):
        with self.assertRaises(B.Unparseable):
            B.atoms_of_token('Hai mẫu số 5 và 2', 0.0, 1.0)


class TestMathExpressionObject(unittest.TestCase):
    def make(self, ast=None):
        return X.MathExpression(source_block_id='b:1', book='05-sgk-toan-5-tap-mot', page_pdf=22,
                                page_printed=21, bbox=(0.1, 0.2, 0.3, 0.05), crop='crops/x.png',
                                ast=ast, original_text='b) 10 +', rule_id='math-line-v1')

    def test_latex_and_text_are_projections_with_no_setter(self):
        e = self.make(A.BinOp(A.ADD, frac('3', '10'), frac('5', '21')))
        self.assertEqual(e.latex, r'\frac{3}{10} + \frac{5}{21}')
        with self.assertRaises(AttributeError):
            e.latex = r'\frac{9}{9}'

    def test_the_original_observation_is_kept_beside_the_proposal(self):
        e = self.make(A.BinOp(A.ADD, frac('3', '10'), frac('5', '21')))
        self.assertEqual(e.original_text, 'b) 10 +')
        self.assertNotEqual(e.text, e.original_text)

    def test_a_new_expression_is_never_servable(self):
        e = self.make(frac('1', '5'))
        self.assertEqual(e.disposition, X.REPAIRED_CANDIDATE)
        self.assertFalse(e.servable)

    def test_one_rejection_withholds(self):
        e = self.make(frac('1', '5'))
        e.record([dict(validator_id='a', verdict='PASS'), dict(validator_id='b', verdict='FAIL')])
        self.assertEqual(e.disposition, X.WITHHELD)
        self.assertEqual(e.reasons, ('b',))

    def test_no_confirmation_withholds(self):
        e = self.make(frac('1', '5'))
        e.record([dict(validator_id='a', verdict='NOT_APPLICABLE')])
        self.assertEqual(e.disposition, X.WITHHELD)
        self.assertEqual(e.reasons, ('no_validator_confirmed',))

    def test_a_confirmation_reaches_validated_repair_and_no_further(self):
        e = self.make(frac('1', '5'))
        e.record([dict(validator_id='a', verdict='PASS')])
        self.assertEqual(e.disposition, X.VALIDATED_REPAIR)
        self.assertFalse(e.servable, 'TRUSTED is a separate Founder act this lane cannot perform')

    def test_a_withheld_region_is_named_and_keeps_its_crop(self):
        """Today 14 of 15 Docling formula regions are filed as «empty — no letters». A refused
        region must say a formula was refused HERE, and keep the picture of it."""
        w = X.withheld('b:2', 'x', 22, bbox=(0.1, 0.2, 0.3, 0.05), crop='crops/y.png',
                       reasons=('numerator_token_missing',), original_text='b) 10 +')
        self.assertEqual(w.disposition, X.WITHHELD)
        self.assertIsNone(w.ast)
        self.assertIsNone(w.latex)
        self.assertEqual(w.crop, 'crops/y.png')
        self.assertEqual(w.bbox, (0.1, 0.2, 0.3, 0.05))
        self.assertEqual(w.reasons, ('numerator_token_missing',))

    def test_the_json_carries_the_whole_trace(self):
        e = self.make(frac('1', '5'))
        j = e.to_json()
        for k in ('sourceBlockId', 'book', 'pagePdf', 'pagePrinted', 'bbox', 'crop', 'ast',
                  'latex', 'textProjection', 'originalText', 'observations', 'sourceGeometry',
                  'ruleId', 'recognition', 'validations', 'provenance', 'disposition', 'reasons'):
            self.assertIn(k, j)


class TestSourceGeometryContract(unittest.TestCase):
    """§2: geometry must survive OCR → SDM → TSL. One reader, so A1's field and the fallback
    cannot drift."""

    def test_lane_a1_s_field_is_used_when_the_block_carries_it(self):
        blk = dict(bbox=[0, 0, 1, 1], lines=[dict(text='3', bbox=[0.1, 0.2, 0.01, 0.02], index=4)])
        g = X.geometry_from_sdm_block(blk)
        self.assertEqual(len(g), 1)
        self.assertEqual((g[0].text, g[0].index, g[0].bbox), ('3', 4, (0.1, 0.2, 0.01, 0.02)))

    def test_the_fallback_reads_the_ocr_tokens_under_the_block(self):
        from mathfix.tokens import Token
        blk = dict(bbox=[0.0, 0.0, 0.5, 0.5])
        toks = [Token('3', 0.1, 0.1, 0.02, 0.02, 1.0, 0), Token('9', 0.9, 0.9, 0.02, 0.02, 1.0, 1)]
        g = X.geometry_from_sdm_block(blk, toks)
        self.assertEqual([t.text for t in g], ['3'])

    def test_no_geometry_anywhere_is_an_empty_tuple_not_a_guess(self):
        self.assertEqual(X.geometry_from_sdm_block(dict(bbox=None)), ())


if __name__ == '__main__':
    unittest.main()
