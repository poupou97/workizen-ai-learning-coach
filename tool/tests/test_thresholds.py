#!/usr/bin/env python3
"""Round 5 · Lane A3 — tests for the trust-gate SIMULATOR.

The simulator's whole value is that its numbers are the same numbers the pipeline already
publishes, re-decided under a different gate. So the tests check three things:

  1. the gate algebra is what it claims (fail-closed by default; waiving a guard can only
     add served blocks, never remove one);
  2. the evidence extractor's per-block truth reproduces `tc_score.score`'s page aggregates
     — on a synthetic page here, and by an assertion inside the extractor on every real page;
  3. the repository does not contain a production `THRESHOLDS.json`, and the example file
     says loudly that it is not one.
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tool', 'corpus'))

from thresholds import gate as G          # noqa: E402
from thresholds import sweep as S         # noqa: E402
from thresholds import evidence as E      # noqa: E402


def row(**kw):
    base = dict(plane='gold', matched=True, guards=[], text_sim=100.0, ocr_conf=1.0,
                role_confidence=0.9, role_value='body', tone_disagreements=0, order_ok=True,
                pipeline_trusted=True, truth_wrong_any=False, truth_teaching_critical=False)
    base.update(kw)
    return base


class GateAlgebra(unittest.TestCase):
    def test_open_gate_serves_everything_matched(self):
        rows = [row(), row(guards=['agree_text']), row(guards=['math_guard'])]
        m = G.evaluate(rows, dict(deny_guards=[]))
        self.assertEqual(m['served'], 3)
        self.assertEqual(m['coverage'], 1.0)

    def test_pipeline_gate_denies_every_known_guard(self):
        rows = [row(guards=[g], pipeline_trusted=False) for g in G.ALL_GUARDS] + [row()]
        m = G.evaluate(rows, G.PIPELINE_GATE)
        self.assertEqual(m['served'], 1)
        self.assertEqual(m['withheld'], len(G.ALL_GUARDS))

    def test_unmatched_block_can_never_be_served(self):
        m = G.evaluate([row(matched=False)], dict(deny_guards=[], on_missing_signal='allow'))
        self.assertEqual(m['served'], 0)
        self.assertIn('unmatched', m['withhold_reasons'])

    def test_missing_signal_is_fail_closed_by_default(self):
        r = row(text_sim=None)
        self.assertFalse(G.decide(r, dict(min_text_sim=95.0))[0])
        self.assertTrue(G.decide(r, dict(min_text_sim=95.0, on_missing_signal='allow'))[0])

    def test_absent_floor_is_not_a_floor_of_zero(self):
        # a gate that sets no floor must not accidentally reject a block whose signal is missing
        self.assertTrue(G.decide(row(text_sim=None, ocr_conf=None, role_confidence=None),
                                 dict(deny_guards=[]))[0])

    def test_waiving_a_guard_only_adds_served_blocks(self):
        rows = [row(guards=['agree_tones'], pipeline_trusted=False),
                row(guards=['agree_tones', 'math_guard'], pipeline_trusted=False),
                row()]
        strict = G.evaluate(rows, G.PIPELINE_GATE)
        waived = G.evaluate(rows, dict(deny_guards=[g for g in G.ALL_GUARDS if g != 'agree_tones']))
        self.assertEqual(strict['served'], 1)
        self.assertEqual(waived['served'], 2)          # the math_guard block is still withheld
        self.assertGreaterEqual(waived['served'], strict['served'])

    def test_restore_is_measured_against_the_pipeline_decision(self):
        rows = [row(guards=['agree_tones'], pipeline_trusted=False, truth_wrong_any=False),
                row(guards=['agree_tones'], pipeline_trusted=False, truth_wrong_any=True)]
        m = G.evaluate(rows, dict(deny_guards=[]))
        self.assertEqual(m['restored'], 2)
        self.assertEqual(m['restored_clean'], 1)
        self.assertEqual(m['restored_wrong'], 1)
        self.assertEqual(m['restore_precision'], 0.5)

    def test_newly_withheld_separates_what_it_costs_from_what_it_buys(self):
        rows = [row(truth_wrong_any=True), row(truth_wrong_any=False)]
        m = G.evaluate(rows, dict(deny_guards=[], min_role_confidence=0.99))
        self.assertEqual(m['newly_withheld'], 2)
        self.assertEqual(m['newly_withheld_wrong'], 1)
        self.assertEqual(m['newly_withheld_clean'], 1)

    def test_roles_whitelist_and_blacklist(self):
        rows = [row(role_value='question'), row(role_value='body')]
        self.assertEqual(G.evaluate(rows, dict(deny_guards=[], allow_roles=['question']))['served'], 1)
        self.assertEqual(G.evaluate(rows, dict(deny_guards=[], deny_roles=['body']))['served'], 1)

    def test_deny_where_predicates(self):
        rows = [row(subject='Toán'), row(subject='TV')]
        g = dict(deny_guards=[], deny_where=[dict(field='subject', op='eq', value='Toán')])
        self.assertEqual(G.evaluate(rows, g)['served'], 1)
        with self.assertRaises(ValueError):
            G.decide(rows[0], dict(deny_guards=[], deny_where=[dict(field='subject', op='nope', value=1)]))

    def test_ftr_and_wilson(self):
        rows = [row(truth_wrong_any=True)] + [row() for _ in range(9)]
        m = G.evaluate(rows, dict(deny_guards=[]))
        self.assertEqual(m['ftr'], 0.1)
        lo, hi = m['ftr_ci95']
        self.assertLess(lo, 0.1)
        self.assertGreater(hi, 0.1)
        self.assertEqual(G.wilson(0, 0), (None, None))

    def test_teaching_critical_is_reported_separately_from_false_trust(self):
        rows = [row(truth_wrong_any=True, truth_teaching_critical=True),
                row(truth_wrong_any=True, truth_teaching_critical=False)]
        m = G.evaluate(rows, dict(deny_guards=[]))
        self.assertEqual(m['served_wrong'], 2)
        self.assertEqual(m['served_teaching_critical'], 1)


class Sweeps(unittest.TestCase):
    def test_guard_cost_attributes_only_sole_reasons(self):
        rows = [row(guards=['agree_tones'], pipeline_trusted=False),
                row(guards=['agree_tones', 'math_guard'], pipeline_trusted=False,
                    truth_wrong_any=True)]
        gc = S.guard_cost(rows)
        self.assertEqual(gc['agree_tones']['fires'], 2)
        self.assertEqual(gc['agree_tones']['sole_reason'], 1)     # the second block also has math_guard
        self.assertEqual(gc['agree_tones']['sole_clean'], 1)
        self.assertEqual(gc['math_guard']['sole_reason'], 0)

    def test_sweep_guards_is_cumulative_and_monotone(self):
        rows = [row(guards=['agree_tones'], pipeline_trusted=False),
                row(guards=['math_guard'], pipeline_trusted=False)]
        pts = S.sweep_guards(rows, G.PIPELINE_GATE, ['agree_tones', 'math_guard'])
        self.assertEqual([p['served'] for p in pts], [0, 1, 2])
        self.assertEqual(pts[-1]['waived'], ['agree_tones', 'math_guard'])

    def test_sweep_axis_records_the_value(self):
        rows = [row(role_confidence=0.6), row(role_confidence=0.95)]
        pts = S.sweep_axis(rows, dict(deny_guards=[]), 'min_role_confidence', [None, 0.9])
        self.assertEqual([p['served'] for p in pts], [2, 1])
        self.assertEqual([p['value'] for p in pts], [None, 0.9])

    def test_frontier_drops_dominated_points(self):
        pts = [dict(coverage=0.5, served_wrong=10, name='a'),
               dict(coverage=0.6, served_wrong=10, name='b'),     # dominates a
               dict(coverage=0.7, served_wrong=20, name='c')]
        names = [p['name'] for p in S.frontier(pts)]
        self.assertEqual(names, ['b', 'c'])

    def test_svg_is_wellformed_and_needs_no_dependency(self):
        pts = [dict(coverage=0.5, ftr=0.07), dict(coverage=0.8, ftr=0.10)]
        svg = S.svg_curve([('x', pts, '#123456')])
        self.assertTrue(svg.startswith('<svg'))
        self.assertTrue(svg.rstrip().endswith('</svg>'))
        self.assertIn('#123456', svg)

    def test_svg_survives_empty_input(self):
        self.assertTrue(S.svg_curve([('x', [], '#000')]).startswith('<svg'))


# ------------------------------------------------------------------ evidence
GOLD_PAGE = dict(
    book='99-sgk-test', page=1, printed_page=1, grade=5, subject='Test', docType='SGK',
    lesson=dict(number=None), gold_set='unit-test',
    blocks=[
        dict(id='b01', order=0, role='heading', anchor='Bai mot hoc ve so hoc',
             text='Bai mot hoc ve so hoc', bbox=[0.1, 0.1, 0.5, 0.05], column=1, contiguous=True),
        dict(id='b02', order=1, role='body', anchor='Mot con ga co hai cai chan',
             text='Mot con ga co hai cai chan', bbox=[0.1, 0.2, 0.5, 0.05], column=1, contiguous=True),
        dict(id='b03', order=2, role='body', anchor='Ba con vit co sau cai chan',
             text='Ba con vit co sau cai chan', bbox=[0.1, 0.3, 0.5, 0.05], column=1, contiguous=True),
    ])


def sdm_block(i, text, role, coarse, guards, bbox):
    return dict(id=f'99-sgk-test:p001:tc2-p2:{i:03d}', order=i, native_order=i,
                native_label=None, text=text, text_docling=text, enumerator_restored=False,
                bbox=bbox, column=1, ocr_conf=1.0, colour=dict(share=0.0),
                extraction='unit-test',
                agreement=dict(text_sim=100.0, verifier_id=None, verifier_role=None,
                               order_ok=True, tone_disagreements=[]),
                role=dict(value=role, coarse=coarse, method='unit-test', confidence=0.9,
                          evidence=[], verifier_hint=None, conflict=False),
                guards=list(guards),
                trust=dict(status='TRUSTED' if not guards else 'WITHHELD', reasons=list(guards)),
                learning=True, refers_figure=False, heading_path=[], lesson=None, cells=None)


SDM_PAGE = dict(
    book='99-sgk-test', page=1, printed_page=1, docType='SGK', pipeline='tc2-p2',
    sdm_version='unit-test', role_signal=None, source={}, page_size=[1, 1],
    features=dict(color_heavy=False, diagram=False),
    blocks=[
        sdm_block(0, 'Bai mot hoc ve so hoc', 'heading', 'HEADING', [], [0.1, 0.1, 0.5, 0.05]),
        sdm_block(1, 'Mot con ga co ba cai chan roi', 'body', 'BODY', [], [0.1, 0.2, 0.5, 0.05]),
        sdm_block(2, 'Ba con vit co sau cai chan', 'body', 'BODY', ['agree_tones'], [0.1, 0.3, 0.5, 0.05]),
    ],
    figures=[], tables=[], stats={})


class Evidence(unittest.TestCase):
    def setUp(self):
        import tc_score
        # `lesson_from_toc` would otherwise read the corpus curriculum file; an empty cache
        # makes it answer "no TOC for this book", which is what a synthetic page needs.
        self._docs = tc_score.lesson_from_toc._docs
        tc_score.lesson_from_toc._docs = {}

    def tearDown(self):
        import tc_score
        tc_score.lesson_from_toc._docs = self._docs

    def test_rows_reproduce_the_scorer(self):
        import copy
        rows = E.gold_page_rows(copy.deepcopy(GOLD_PAGE), copy.deepcopy(SDM_PAGE))
        self.assertEqual(len(rows), 3)                      # 3 gold learning blocks with anchors
        by = {r['gold_id']: r for r in rows}
        self.assertTrue(by['b01']['pipeline_trusted'])
        self.assertFalse(by['b01']['truth_wrong_any'])
        self.assertTrue(by['b02']['pipeline_trusted'])
        self.assertTrue(by['b02']['truth_wrong_any'])        # "hai" served as "ba ... roi"
        self.assertIn('cer', by['b02']['truth_wrong'])
        self.assertFalse(by['b03']['pipeline_trusted'])      # agree_tones withheld it
        self.assertEqual(by['b03']['guards'], ['agree_tones'])
        # the extractor's own assertions already compared these to tc_score.score page by page
        m = G.evaluate(rows, G.PIPELINE_GATE)
        self.assertEqual((m['served'], m['served_wrong'], m['withheld']), (2, 1, 1))

    def test_waiving_the_guard_restores_the_clean_block(self):
        import copy
        rows = E.gold_page_rows(copy.deepcopy(GOLD_PAGE), copy.deepcopy(SDM_PAGE))
        m = G.evaluate(rows, dict(deny_guards=[g for g in G.ALL_GUARDS if g != 'agree_tones']))
        self.assertEqual(m['restored'], 1)
        self.assertEqual(m['restore_precision'], 1.0)
        self.assertEqual(m['coverage'], 1.0)

    def test_a_drifting_extractor_raises_instead_of_reporting(self):
        """If the extractor's per-block truth ever stops agreeing with `tc_score.score`, the
        numbers in the report would silently diverge from the published scoreboard. The
        extractor asserts instead. Here the scorer is made to disagree on purpose."""
        import copy
        import tc_score
        import unittest.mock as mock
        real = tc_score.score

        def lying_score(gold, sdm):
            r = real(gold, sdm)
            r['trusted_blocks'] += 1
            return r
        with mock.patch.object(tc_score, 'score', lying_score):
            with self.assertRaises(AssertionError):
                E.gold_page_rows(copy.deepcopy(GOLD_PAGE), copy.deepcopy(SDM_PAGE))

    def test_audit_rows_carry_the_annotator_verdicts(self):
        import tempfile
        rec = dict(sampleId='s-1', family='samUnits', book='b', kind='exercise',
                   servedAsTrusted=True, precheck=dict(ocrSim=88.0, hasMath=True, multiLine=True),
                   source=dict(status=None, reasons=[]),
                   display_fidelity='WRONG', teaching_critical_fidelity='OK', reading_order='NA',
                   role_fidelity='OK', lesson_attachment='OK', false_trust='OK', text='x')
        with tempfile.NamedTemporaryFile('w', suffix='.jsonl', delete=False) as fh:
            fh.write(json.dumps(rec) + '\n')
            p = fh.name
        try:
            rows = E.audit_rows(p, 'unit-test')
        finally:
            os.unlink(p)
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]['truth_wrong_any'])          # display WRONG → derived wrong
        self.assertFalse(rows[0]['truth_teaching_critical'])
        self.assertEqual(rows[0]['verdict_display_fidelity'], 'WRONG')
        self.assertEqual(rows[0]['text_sim'], 88.0)


class NoProductionThreshold(unittest.TestCase):
    """Round 5 forbids Lane A3 from setting a production gate. These tests are the enforcement."""

    def test_repository_has_no_root_thresholds_json(self):
        self.assertFalse(os.path.exists(os.path.join(ROOT, 'THRESHOLDS.json')),
                         'THRESHOLDS.json is a Founder-only record (G1); Lane A3 must not create it')

    def test_example_file_exists_and_declares_itself_an_example(self):
        p = os.path.join(ROOT, 'THRESHOLDS.example.json')
        with open(p) as fh:
            doc = json.load(fh)
        self.assertIn('_THIS_IS_NOT_A_PRODUCTION_FILE', doc)
        self.assertIn('EXAMPLES ONLY', doc['_THIS_IS_NOT_A_PRODUCTION_FILE'])
        self.assertGreaterEqual(len(doc['scenarios']), 3)
        for s in doc['scenarios'] + doc['audit_plane_scenarios']:
            self.assertIn('illustrates', s, f'{s["name"]} must say what question it illustrates')
            self.assertTrue(s['name'].lower().endswith('illustration')
                            or 'illustration' in s['name'].lower(),
                            f'{s["name"]} must be named as an illustration, not as a setting')

    def test_every_example_scenario_is_evaluable(self):
        with open(os.path.join(ROOT, 'THRESHOLDS.example.json')) as fh:
            doc = json.load(fh)
        rows = [row(), row(guards=['agree_tones'], pipeline_trusted=False),
                row(role_value='question', subject='Toán', layout_family='two_col',
                    has_math=True, multi_line=True)]
        for s in doc['scenarios'] + doc['audit_plane_scenarios']:
            m = G.evaluate(rows, s['gate'])
            self.assertIsNotNone(m['coverage'], s['name'])


if __name__ == '__main__':
    unittest.main()
