#!/usr/bin/env python3
"""Phase F — the narrow-slice gate's bar, tested corpus-free.

The gate's headline result is a ZERO: no candidate unit reaches `QUALIFIES_GATE_CLOSED`. A zero is
worth exactly nothing unless two opposite things are both proved:

  REACHABILITY — the verdict CAN be printed. A gate that cannot pass anything reports zero over
                 every population and measures nothing. `test_a_perfect_unit_qualifies` builds the
                 unit the bar describes and asserts the gate prints QUALIFIES_GATE_CLOSED.
  NON-VACUITY  — every stage can independently REFUSE. One test per stage breaks exactly one
                 property of that same perfect unit and asserts the verdict names that stage.

Plus the two structural claims the corpus measurement rests on, pinned so they cannot drift:

  * a unit whose only child-actionable member is a gold `question` is refused by EVERY frozen trust
    candidate, and by C2 through `role_not_interactive` — the clause, not a threshold, is what
    stops it. This is why the corpus zero is not a tuning problem.
  * a member the evidence layer does not model (gold roles `instruction`, `table`, `figure_label`,
    `diagram`, `answer_slot` are outside `tc_sdm.LEARNING_ROLES`) makes its unit UNVERIFIABLE
    rather than passing quietly.

No SGK string appears here. Every text below is `x`-filler written for this test (D4).

Run:  python3 -m unittest discover -s tool/tests -v
"""
import importlib.util
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(HERE, '..', 'corpus')
sys.path.insert(0, CORPUS)
sys.path.insert(0, os.path.join(CORPUS, 'thresholds'))

_spec = importlib.util.spec_from_file_location(
    'phase_f_slice_gate', os.path.join(CORPUS, 'audit', 'phase_f_slice_gate.py'))
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)

CANDIDATES = {c['name']: c for c in json.load(open(gate.FROZEN))['candidates'] if c['clauses']}
GOLD = dict(book='xx-test-book', page=1, printed_page=1, subject='TEST', grade=0,
            lesson={'number': 1}, gold_set='synthetic')


def member(gid, role, order, text='xxxx xxxx xxxx'):
    return dict(id=gid, order=order, role=role, bbox=[0.1, 0.1, 0.5, 0.05], text=text,
                anchor=text)


def row(gid, gold_role, coarse, value, conf=0.95, **kw):
    r = dict(gold_id=gid, gold_role=gold_role, matched=True, block_id='b%s' % gid,
             role_coarse=coarse, role_value=value, role_confidence=conf, role_method='typography',
             cer=0.0, edits=0.0, text_sim=100.0, tone_disagreements=0, order_ok=True,
             refers_figure=False, pipeline_trusted=True, pipeline_status='TRUSTED', guards=[],
             truth_wrong=[], truth_wrong_any=False, truth_digits_wrong=False,
             truth_as_question=False, truth_teaching_critical=False, subject='TEST')
    r.update(kw)
    return r


def perfect_unit():
    """A heading + an ACTIVITY the pipeline serves as BODY. Under `tc_sdm.GOLD_ROLE_MAP` an
    `activity` maps to BODY, so this unit satisfies G3 (a child acts on it) without carrying a
    block C2's `role_not_interactive` refuses. It is the shape the bar is reachable through."""
    members = [member('g1', 'heading', 1), member('g2', 'activity', 2)]
    rows = {'g1': row('g1', 'heading', 'HEADING', 'heading'),
            'g2': row('g2', 'activity', 'BODY', 'body', conf=0.75)}
    return dict(scope='SECTION', anchor='g1', members=members), rows


def judge(unit, rows):
    return gate.judge(unit, rows, GOLD, CANDIDATES)


class Reachability(unittest.TestCase):
    """A gate that can never pass measures nothing. This is the test that gives the zero meaning."""

    def test_a_perfect_unit_qualifies(self):
        v = judge(*perfect_unit())
        self.assertEqual(v['verdict'], 'QUALIFIES_GATE_CLOSED')
        self.assertTrue(all(v['stage'].values()), v['stage'])

    def test_the_verdict_is_never_trusted_or_certified(self):
        v = judge(*perfect_unit())
        self.assertNotIn('TRUST', v['verdict'].upper().replace('GATE_CLOSED', ''))
        self.assertNotIn('CERTIF', v['verdict'].upper())


class EachStageCanRefuse(unittest.TestCase):
    """Non-vacuity: break exactly one property, and the named stage must be the one that fails."""

    def _broken(self, gid, **patch):
        unit, rows = perfect_unit()
        rows[gid] = dict(rows[gid], **patch)
        return judge(unit, rows)

    def test_S1_an_unmatched_member_fails_source(self):
        self.assertEqual(self._broken('g2', matched=False)['verdict'], 'FAIL@S1_SOURCE')

    def test_S1_a_member_with_no_evidence_row_is_unverifiable(self):
        unit, rows = perfect_unit()
        rows.pop('g2')
        v = judge(unit, rows)
        self.assertEqual(v['members_without_row'], ['g2'])
        self.assertFalse(v['stage']['S1_SOURCE'])

    def test_S2_two_members_matching_one_block_fails_structure(self):
        v = self._broken('g2', block_id='bg1')
        self.assertEqual(v['verdict'], 'FAIL@S2_STRUCTURE')
        self.assertEqual(v['s2_many_to_one'], ['bg1'])

    def test_S2_a_member_depending_on_a_figure_fails_structure(self):
        self.assertEqual(self._broken('g2', refers_figure=True)['verdict'], 'FAIL@S2_STRUCTURE')

    def test_S3_one_edit_fails_recognition(self):
        self.assertEqual(self._broken('g2', cer=0.01, edits=1)['verdict'], 'FAIL@S3_RECOGNITION')

    def test_S3_a_member_without_gold_text_is_UNMEASURABLE_never_a_pass(self):
        unit, rows = perfect_unit()
        unit['members'][1] = dict(unit['members'][1], text='')
        v = judge(unit, rows)
        self.assertEqual(v['verdict'], 'UNMEASURABLE')
        self.assertTrue(v['s3_unmeasurable'])

    def test_S4_a_wrong_coarse_role_fails_role(self):
        self.assertEqual(self._broken('g2', role_coarse='CAPTION')['verdict'], 'FAIL@S4_ROLE')

    def test_S4_a_non_question_served_as_a_question_fails_role(self):
        v = self._broken('g2', truth_as_question=True, role_coarse='QUESTION',
                         role_value='question')
        self.assertEqual(v['verdict'], 'FAIL@S4_ROLE')

    def test_S5_a_withheld_member_fails_validation(self):
        v = self._broken('g2', pipeline_trusted=False, pipeline_status='WITHHELD')
        self.assertEqual(v['verdict'], 'FAIL@S5_VALIDATION')

    def test_S5_a_guard_reason_fails_validation(self):
        self.assertEqual(self._broken('g2', guards=['agree_tones'])['verdict'],
                         'FAIL@S5_VALIDATION')

    def test_S5_a_teaching_critical_member_fails_validation(self):
        v = self._broken('g2', truth_teaching_critical=True, truth_digits_wrong=True)
        self.assertEqual(v['verdict'], 'FAIL@S5_VALIDATION')

    def test_S6a_a_two_stack_disagreement_fails_the_policy_stage(self):
        v = self._broken('g2', text_sim=98.0)
        self.assertEqual(v['verdict'], 'FAIL@S6a_POLICY')
        self.assertIn('two_stack_exact', v['candidates']['C2 · PROSE']['refusals'])


class G3NotALearningSlice(unittest.TestCase):
    def test_a_unit_a_child_does_not_act_on_can_never_qualify(self):
        members = [member('g1', 'heading', 1), member('g2', 'body', 2)]
        rows = {'g1': row('g1', 'heading', 'HEADING', 'heading'),
                'g2': row('g2', 'body', 'BODY', 'body')}
        v = judge(dict(scope='SECTION', anchor='g1', members=members), rows)
        self.assertEqual(v['verdict'], 'NOT_A_LEARNING_SLICE')
        self.assertEqual(v['acts_on'], [])
        # ...even though every stage of the bar is satisfied. G3 is a scope rule, not a bar.
        self.assertTrue(all(v['stage'].values()), v['stage'])


class TheClauseNotTheThreshold(unittest.TestCase):
    """Why the corpus zero cannot be tuned away: a question is refused by a CLAUSE."""

    def _heading_plus_question(self, conf=0.95):
        members = [member('g1', 'heading', 1), member('g2', 'question', 2)]
        rows = {'g1': row('g1', 'heading', 'HEADING', 'heading'),
                'g2': row('g2', 'question', 'QUESTION', 'question', conf=conf)}
        return dict(scope='SECTION', anchor='g1', members=members), rows

    def test_a_perfect_question_section_is_refused_by_every_frozen_candidate(self):
        v = judge(*self._heading_plus_question())
        self.assertEqual(v['verdict'], 'FAIL@S6a_POLICY')
        for name, c in v['candidates'].items():
            self.assertFalse(c['all_admitted'], f'{name} admitted a question section')

    def test_C2_refuses_it_through_role_not_interactive(self):
        v = judge(*self._heading_plus_question())
        self.assertEqual(v['candidates']['C2 · PROSE']['refusals'], {'role_not_interactive': 1})

    def test_the_question_surface_refuses_the_heading_too(self):
        """C3 admits ONLY a question, so a COMPLETE section can never clear it: its heading is
        refused for not being a question. Serving the question without its heading is the
        mutilated structure round 5 defect 8 forbids."""
        v = judge(*self._heading_plus_question(conf=0.99))
        self.assertEqual(v['candidates']['C3 · QUESTION SURFACE']['refusals'],
                         {'role_is_question_high_confidence': 1})

    def test_raising_role_confidence_does_not_rescue_it_under_C2(self):
        for conf in (0.70, 0.85, 0.90, 0.99):
            v = judge(*self._heading_plus_question(conf=conf))
            self.assertEqual(v['verdict'], 'FAIL@S6a_POLICY', f'confidence {conf}')


class RoleMapPinned(unittest.TestCase):
    """The two constants the corpus reading depends on. If either moves, this test says so."""

    def test_the_roles_the_evidence_layer_does_not_model(self):
        import tc_sdm
        for role in ('instruction', 'table', 'figure_label', 'diagram', 'answer_slot'):
            self.assertNotIn(role, tc_sdm.LEARNING_ROLES,
                             f'{role} is now a learning role; the S1 census must be re-derived')

    def test_an_activity_maps_to_BODY_and_a_question_to_QUESTION(self):
        import tc_sdm
        self.assertEqual(tc_sdm.GOLD_ROLE_MAP['activity'], 'BODY')
        self.assertEqual(tc_sdm.GOLD_ROLE_MAP['question'], 'QUESTION')


if __name__ == '__main__':
    unittest.main()
