#!/usr/bin/env python3
"""Round 5 · Lane A2 — the repairer as a plugin of Lane A1's registry.

Two things are pinned here that prose cannot pin:
 · when A1's `repair` package is importable, THIS is what the plugin registers against — the local
   stand-in can never quietly become the thing the lane is tested on;
 · the repairer proposes and the validator disposes, and the validator re-derives its answer from
   the PAGE, so a hand-built candidate cannot validate itself.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'corpus'))

from mathfix import adapter                   # noqa: E402
from mathfix import plugin as P               # noqa: E402
from mathfix.inkmask import InkMask           # noqa: E402
from mathfix.tokens import Token              # noqa: E402

MODEL = adapter.MODEL

# The same «1 over 5» picture, with room for a lead token to its left.
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


class Ctx:
    """The shape of A1's `RepairContext`, with only the fields this plugin reads."""

    def __init__(self, block_id, bbox, page_ctx, reasons=(), disposition='WITHHELD'):
        self.block_id = block_id
        self.observations = [MODEL.Observation(block_id=block_id, source='sdm', value='1 a) 7 + 5')]
        self.disposition = disposition
        self.withhold_reasons = tuple(reasons)
        self.role = 'body'
        self.page = dict(book='test', page=1, bbox=bbox)
        self.extra = dict(mathfix_page=page_ctx)

    def primary(self):
        return self.observations[0]


def page_context(tokens):
    from mathfix import detect as D
    m = InkMask.from_ascii(FRACTION)
    return P.PageContext(m, tokens, D.find_fraction_regions(m, tokens, bar_params=BAR_PARAMS))


def whole_page():
    return (0.0, 0.0, 1.0, 1.0)


NUM = Token('1', x=8 / 20, y=1 / 14, w=2 / 20, h=4 / 14, conf=1.0, index=0)
DEN = Token('5', x=7 / 20, y=8 / 14, w=4 / 20, h=5 / 14, conf=1.0, index=1)
LEAD = Token('a) 7 +', x=1 / 20, y=6 / 14, w=3 / 20, h=2 / 14, conf=1.0, index=2)


class TestRegistration(unittest.TestCase):
    def test_the_real_framework_is_used_when_it_is_on_the_branch(self):
        try:
            import repair                                        # noqa: F401
        except Exception:
            self.skipTest("Lane A1's repair framework is not on this branch — the stand-in is in use")
        self.assertEqual(adapter.FRAMEWORK, 'repair-v1')
        self.assertIs(adapter.MODEL, repair.model)
        self.assertIs(adapter.REGISTRY, repair.registry)

    def test_registering_declares_one_repairer_and_one_validator_for_the_class(self):
        reg = P.register(registry=_fresh_registry())
        self.assertEqual([f.repairer_id for f in reg.repairers_for(P.FAILURE_CLASS)],
                         ['mathfix.math-line-v1'])
        self.assertEqual([f.validator_id for f in reg.validators_for(P.FAILURE_CLASS)],
                         ['mathfix.deterministic-v1'])

    def test_the_failure_class_is_the_one_the_plan_names(self):
        self.assertEqual(P.FAILURE_CLASS, 'formula_flattened')


def _fresh_registry():
    """A registry object of whichever framework is in use, with nothing registered on it."""
    if adapter.FRAMEWORK == 'repair-v1':
        import repair
        snap = repair.registry.snapshot()
        repair.registry.reset()
        unittest.addModuleCleanup(repair.registry.restore, snap)
        return repair.registry
    return adapter.REGISTRY.__class__()


class TestProposal(unittest.TestCase):
    def test_a_readable_expression_yields_one_candidate_citing_its_observations(self):
        ctx = Ctx('b1', whole_page(), page_context([NUM, DEN, LEAD]), reasons=('math_guard',))
        cands = list(P.propose(ctx))
        self.assertEqual(len(cands), 1)
        c = cands[0]
        self.assertEqual(c.proposed_value, 'a) 7 + 1/5')
        self.assertEqual(c.failure_class, 'formula_flattened')
        self.assertEqual(c.disposition, MODEL.Disposition.REPAIRED_CANDIDATE)
        self.assertEqual(sorted({o.source for o in c.original_observations}),
                         ['apple-vision-ocr-line', 'page-raster-300dpi'])

    def test_a_repairer_with_nothing_to_say_says_nothing(self):
        ctx = Ctx('b2', whole_page(), page_context([NUM]), reasons=('math_guard',))
        self.assertEqual(list(P.propose(ctx)), [])       # the denominator token was lost

    def test_no_page_evidence_means_no_candidate_rather_than_a_guess(self):
        ctx = Ctx('b3', whole_page(), page_context([NUM, DEN, LEAD]))
        ctx.extra = {}
        self.assertEqual(list(P.propose(ctx)), [])

    def test_the_candidate_carries_the_reasons_it_claims_to_cover(self):
        ctx = Ctx('b4', whole_page(), page_context([NUM, DEN, LEAD]), reasons=('math_guard',))
        c = list(P.propose(ctx))[0]
        self.assertEqual(tuple(c.provenance['covers_reasons']), P.COVERS_REASONS)
        self.assertNotIn('agree_order', c.provenance['covers_reasons'])
        self.assertNotIn('low_ocr_conf', c.provenance['covers_reasons'])

    def test_the_signals_carry_the_founder_s_layer_letters_and_abstentions(self):
        ctx = Ctx('b5', whole_page(), page_context([NUM, DEN, LEAD]), reasons=('math_guard',))
        c = list(P.propose(ctx))[0]
        self.assertEqual(sorted({s.layer for s in c.supporting_signals}), ['B', 'C'])
        abstained = [s for s in c.supporting_signals if s.verdict == MODEL.SignalVerdict.ABSTAINS]
        self.assertTrue(abstained, 'the page states no equality, so arith-selfcheck must abstain')
        self.assertEqual(abstained[0].strength, 0.0)


class TestValidator(unittest.TestCase):
    def test_a_reproducible_expression_validates(self):
        ctx = Ctx('c1', whole_page(), page_context([NUM, DEN, LEAD]), reasons=('math_guard',))
        c = list(P.propose(ctx))[0]
        self.assertEqual(P.validate_candidate(c, ctx).verdict, MODEL.Verdict.VALIDATED)

    def test_a_candidate_the_page_does_not_reproduce_is_rejected(self):
        """The validator re-reads the page; it never takes the candidate's word for anything."""
        ctx = Ctx('c2', whole_page(), page_context([NUM, DEN, LEAD]), reasons=('math_guard',))
        real = list(P.propose(ctx))[0]
        forged = MODEL.RepairCandidate(
            block_id='c2', failure_class=P.FAILURE_CLASS,
            original_observations=real.original_observations,
            proposed_value='a) 7 + 1/50', rule_id='math-line-v1')
        r = P.validate_candidate(forged, ctx)
        self.assertEqual(r.verdict, MODEL.Verdict.REJECTED)
        self.assertEqual(r.evidence[0]['check'], 'reproducibility')

    def test_without_page_evidence_the_verdict_is_insufficient_not_validated(self):
        ctx = Ctx('c3', whole_page(), page_context([NUM, DEN, LEAD]), reasons=('math_guard',))
        c = list(P.propose(ctx))[0]
        ctx.extra = {}
        self.assertEqual(P.validate_candidate(c, ctx).verdict, MODEL.Verdict.INSUFFICIENT)


class TestEngineIntegration(unittest.TestCase):
    """End to end through A1's own engine, when it is on the branch."""

    def setUp(self):
        try:
            import repair                                        # noqa: F401
        except Exception:
            self.skipTest("Lane A1's repair framework is not on this branch")
        self.repair = repair
        self.snap = repair.registry.snapshot()
        repair.registry.reset()
        P.register(registry=repair.registry)
        self.addCleanup(repair.registry.restore, self.snap)

    def _ctx(self, reasons):
        engine = self.repair.engine
        return engine.RepairContext(
            block_id='e1',
            observations=[self.repair.model.Observation('e1', 'sdm', '1 a) 7 + 5')],
            disposition=self.repair.model.Disposition.WITHHELD,
            withhold_reasons=reasons,
            page=dict(book='test', page=1, bbox=whole_page()),
            extra=dict(mathfix_page=page_context([NUM, DEN, LEAD])))

    def test_a_block_withheld_only_for_a_covered_reason_becomes_restorable(self):
        out = self.repair.engine.RepairEngine().run_block(self._ctx(('math_guard',)))
        self.assertTrue(out.restorable, out.reasons)
        self.assertEqual(out.disposition, self.repair.model.Disposition.VALIDATED_REPAIR)
        self.assertEqual(out.final_value, 'a) 7 + 1/5')

    def test_a_reason_this_lane_does_not_cover_keeps_the_block_withheld(self):
        out = self.repair.engine.RepairEngine().run_block(self._ctx(('math_guard', 'figure_text')))
        self.assertFalse(out.restorable)
        self.assertEqual(out.disposition, self.repair.model.Disposition.WITHHELD)
        self.assertIn('figure_text', out.reasons)


if __name__ == '__main__':
    unittest.main()
