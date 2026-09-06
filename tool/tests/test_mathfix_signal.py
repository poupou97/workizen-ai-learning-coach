#!/usr/bin/env python3
"""Round 5 · Lane A2 — the layer-C numeric provider A1 left this lane a slot for.

The property under test is one sentence: **support only from the page, object from the strings,
never relax A1's fail-closed default without evidence.** A provider that answered SUPPORTS from two
strings would hand a text lane a licence to move digits, which is the exact thing layer C exists to
prevent.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'corpus'))

from mathfix import adapter                       # noqa: E402
from mathfix import plugin as P                   # noqa: E402
from mathfix import signal_numeric as SN          # noqa: E402
from mathfix.inkmask import InkMask               # noqa: E402
from mathfix.tokens import Token                  # noqa: E402

MODEL = adapter.MODEL
SV = MODEL.SignalVerdict

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
BAR_PARAMS = dict(min_len_frac=0.30, max_len_frac=0.90, max_thick_frac=0.20)
NUM = Token('1', x=8 / 20, y=1 / 14, w=2 / 20, h=4 / 14, conf=1.0, index=0)
DEN = Token('5', x=7 / 20, y=8 / 14, w=4 / 20, h=5 / 14, conf=1.0, index=1)
LEAD = Token('a) 7 +', x=1 / 20, y=6 / 14, w=3 / 20, h=2 / 14, conf=1.0, index=2)


class Ctx:
    def __init__(self, page=None, bbox=(0.0, 0.0, 1.0, 1.0)):
        self.page = dict(book='test', page=1, bbox=bbox)
        self.extra = dict(mathfix_page=page) if page else {}


def page_context(tokens):
    from mathfix import detect as D
    m = InkMask.from_ascii(FRACTION)
    return P.PageContext(m, tokens, D.find_fraction_regions(m, tokens, bar_params=BAR_PARAMS))


class TestWithoutPageEvidence(unittest.TestCase):
    """Strings alone can only ever object or abstain here."""

    def sig(self, observed, proposed):
        return SN.provider(observed, proposed, Ctx(), model=MODEL)

    def test_an_invented_digit_objects(self):
        s = self.sig('b) 10 +', 'b) 3/10 + 5/21')
        self.assertEqual(s.verdict, SV.OBJECTS)
        self.assertIn('3', s.detail['invented'])

    def test_an_operator_that_changed_identity_objects(self):
        """«16/21 × 3/5» read as «16/21 - 3/5»: every digit stayed put. A rule that only counted
        digits would wave this past — which is how the false correction happened."""
        s = self.sig('16 21 × 3 5', '16/21 - 3/5')
        self.assertEqual(s.verdict, SV.OBJECTS)
        self.assertEqual(s.detail['reason'], 'an operator changed identity or vanished')

    def test_an_operator_that_vanished_objects(self):
        s = self.sig('20 18 − 2 5', '20/18 2/5')
        self.assertEqual(s.verdict, SV.OBJECTS)

    def test_it_never_supports_from_strings_alone(self):
        for observed, proposed in (('3 10 + 5 21', '3/10 + 5/21'), ('x', 'x'), ('1 5', '1/5')):
            s = self.sig(observed, proposed)
            self.assertTrue(s is None or s.verdict != SV.SUPPORTS, (observed, proposed))

    def test_nothing_to_add_falls_through_to_a1_s_default(self):
        self.assertIsNone(self.sig('3 10 + 5 21', '3/10 + 5/21'))


class TestWithPageEvidence(unittest.TestCase):
    def test_a_validated_expression_supports(self):
        ctx = Ctx(page_context([NUM, DEN, LEAD]))
        s = SN.provider('1 a) 7 + 5', 'a) 7 + 1/5', ctx, model=MODEL)
        self.assertEqual(s.verdict, SV.SUPPORTS)
        self.assertEqual(s.detail['provider'], 'mathfix.numeric-v1')
        self.assertIn('ink-accounted-v1', s.detail['checks'])

    def test_a_value_the_page_does_not_reproduce_objects(self):
        ctx = Ctx(page_context([NUM, DEN, LEAD]))
        s = SN.provider('1 a) 7 + 5', 'a) 7 + 1/50', ctx, model=MODEL)
        self.assertEqual(s.verdict, SV.OBJECTS)
        self.assertEqual(s.detail['reason'], 'the page does not reproduce this value')

    def test_a_block_with_no_printed_fraction_is_not_this_lane_s_to_judge(self):
        ctx = Ctx(page_context([NUM, DEN, LEAD]), bbox=(0.9, 0.9, 0.05, 0.05))
        self.assertIsNone(SN.provider('a', 'b', ctx, model=MODEL))


class TestRegistration(unittest.TestCase):
    def test_it_installs_into_lane_a1_s_numeric_slot(self):
        try:
            from repair.signals import numeric
        except Exception:
            self.skipTest("Lane A1's repair framework is not on this branch")
        prev = numeric._provider
        self.addCleanup(setattr, numeric, '_provider', prev)
        numeric._provider = None
        self.assertTrue(SN.register())
        self.assertIs(numeric._provider, SN.provider)

    def test_registering_is_a_no_op_when_the_framework_is_absent(self):
        class NoModule:
            pass
        self.assertTrue(SN.register(numeric_module=type('M', (), {
            'register_provider': staticmethod(lambda fn: fn)})()))


if __name__ == '__main__':
    unittest.main()
