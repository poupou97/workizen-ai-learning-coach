#!/usr/bin/env python3
"""Round 7 · WS-T — tests for the trust-calibration machinery.

The machinery's whole value is that it CANNOT do the thing it is about. So the tests check the
refusals harder than they check the arithmetic:

  1. the policy algebra keeps `trusted ⊆ served`, so activation can never serve a new block;
  2. the freeze ledger makes the ORDER provable — a population cannot be frozen before a policy,
     an admitted set cannot be frozen before an approval, and a payload edited after freezing
     stops verifying;
  3. no artefact this workstream produces names a lesson or book identity in an admission
     context, and the check that says so is itself tested against a payload that does;
  4. `apply.py` is inert: every path refuses without an approval artefact naming the frozen
     policy by hash;
  5. the blind audit worklist does not leak the gate to the annotator;
  6. `measure.py` reads its bound from the frozen policy and decides on the UPPER confidence
     bound, so a point estimate of zero at small n does not pass.
"""

import json
import os
import random
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tool', 'corpus'))

from thresholds import apply as A            # noqa: E402
from thresholds import audit_sheet as SH     # noqa: E402
from thresholds import candidates as C       # noqa: E402
from thresholds import freeze as F           # noqa: E402
from thresholds import gate as G             # noqa: E402
from thresholds import measure as M          # noqa: E402
from thresholds import policy as P           # noqa: E402

FROZEN = os.path.join(ROOT, 'tool', 'corpus', 'thresholds', 'frozen')
DOCS = os.path.join(ROOT, 'docs', 'research')


def load(path):
    with open(path, encoding='utf-8') as fh:
        return json.load(fh)


def row(**kw):
    base = dict(matched=True, guards=[], text_sim=100.0, ocr_conf=1.0, role_confidence=0.9,
                role_value='heading', tone_disagreements=0, order_ok=True, subject='KHTN',
                refers_figure=False, truth_wrong_any=False, truth_teaching_critical=False)
    base.update(kw)
    base['_served'] = G.decide(base, G.PIPELINE_GATE)[0]
    return base


class PolicyAlgebra(unittest.TestCase):
    def test_trusted_is_always_a_subset_of_served(self):
        """The invariant activation rests on: no candidate can serve a block the pipeline
        withholds, so round 6's byte-identical served set survives activation."""
        rng = random.Random(7)
        rows = [row(guards=rng.choice([[], ['agree_tones'], ['math_guard'], ['teacher_text']]),
                    role_value=rng.choice(['heading', 'body', 'question', 'caption']),
                    role_confidence=rng.choice([0.6, 0.7, 0.85, 0.97]),
                    text_sim=rng.choice([88.0, 100.0]),
                    subject=rng.choice(['KHTN', 'Toán', 'Ngữ văn']))
                for _ in range(400)]
        for name, pol in C.CANDIDATES.items():
            if P.unavailable_clauses(pol):
                continue
            for r in rows:
                if P.admits(r, pol)[0]:
                    self.assertTrue(r['_served'], f'{name} admitted a withheld block')

    def test_empty_clause_set_admits_nothing(self):
        self.assertFalse(P.admits(row(), C.CANDIDATES['C0 · NULL'])[0])

    def test_served_only_and_no_repair_are_mandatory(self):
        p = P.normalise(dict(clauses=['two_stack_exact']))
        self.assertEqual(p['clauses'][0], 'served_only')
        self.assertIn('no_repair', p['clauses'])

    def test_a_validated_repair_is_never_trusted(self):
        r = row(disposition='VALIDATED_REPAIR')
        self.assertFalse(P.admits(r, C.CANDIDATES['C2 · PROSE'])[0])
        self.assertIn('no_repair', P.admits(r, C.CANDIDATES['C2 · PROSE'])[1])

    def test_a_policy_may_only_intersect_with_served(self):
        with self.assertRaises(ValueError):
            P.normalise(dict(base='everything', clauses=['two_stack_exact']))

    def test_unavailable_clause_invalidates_the_measurement(self):
        m = P.evaluate([row()], C.CANDIDATES['C4 · C1 + THE MACHINERY THAT DOES NOT EXIST'])
        self.assertIn('MEASUREMENT_INVALID', m)
        self.assertIn('digit_sequence_verified', m['unavailable_clauses'])


class BoundArithmetic(unittest.TestCase):
    def test_lesson_promise_and_block_rate_are_inverses(self):
        for promise in (0.8, 0.9, 0.95, 0.99):
            r = P.block_rate_for_lesson_promise(promise, 30)
            self.assertAlmostEqual(P.lesson_clean_probability(r, 30), promise, places=9)

    def test_audit_cost_grows_as_the_bound_tightens(self):
        sizes = [P.min_n_for_upper_bound(b) for b in (0.05, 0.02, 0.01, 0.005)]
        self.assertEqual(sizes, sorted(sizes), 'a tighter bound must cost more, not less')

    def test_zero_observed_is_not_zero_rate(self):
        """The reason every bound in this workstream is an upper bound."""
        self.assertGreater(P.wilson_upper(0, 50), 0.05)

    def test_every_bound_carries_its_audit_cost(self):
        for bid, b in C.BOUNDS.items():
            self.assertIn('min_audited_trusted_blocks_if_zero_observed', b, bid)
            self.assertIn('prediction_from_pre_existing_evidence', b, bid)


class IdentitySuppression(unittest.TestCase):
    def test_leak_detector_catches_an_identity_in_an_admission_context(self):
        bad = dict(admitted_lessons=['05-sgk-lich-su-va-dia-li-5 Bài 8'])
        self.assertTrue(P.identity_leaks(bad))

    def test_leak_detector_ignores_an_identity_outside_an_admission_context(self):
        ok = dict(excluded_books=['05-sgk-lich-su-va-dia-li-5'])
        self.assertFalse(P.identity_leaks(ok))

    def test_no_frozen_artefact_leaks_an_identity(self):
        for name in os.listdir(FROZEN):
            if not name.endswith('.json'):
                continue
            payload = load(os.path.join(FROZEN, name))
            self.assertFalse(P.identity_leaks(payload), name)

    def test_the_calibration_documents_name_no_lesson_and_no_book(self):
        """Expected trade-offs are rates, not «this lesson would be admitted»."""
        for name in os.listdir(DOCS):
            if not name.startswith('TRUST-CALIBRATION-'):
                continue
            with open(os.path.join(DOCS, name), encoding='utf-8') as fh:
                text = fh.read()
            self.assertIsNone(P.BOOK_ID_RE.search(text), f'{name} names a book')
            self.assertIsNone(P.LESSON_REF_RE.search(text), f'{name} names a lesson')


class FreezeLedger(unittest.TestCase):
    def test_the_committed_ledger_verifies(self):
        ok, problems = F.verify()
        self.assertTrue(ok, problems)

    def test_the_policy_was_frozen_before_the_population(self):
        """The order proof. Not «we did it in this order» — the population entry embeds the
        policy hash, so it could not have been written first."""
        entries = F.read_ledger()
        kinds = [e['kind'] for e in entries]
        self.assertEqual(kinds[0], 'policy')
        pol = entries[0]['sha256']
        pops = [e for e in entries if e['kind'] == 'population']
        self.assertTrue(pops, 'no population frozen')
        for p in pops:
            self.assertEqual(p['binds_policy'], pol)
            self.assertGreater(p['seq'], entries[0]['seq'])

    def test_no_admitted_set_exists(self):
        self.assertNotIn('admitted', {e['kind'] for e in F.read_ledger()})
        self.assertNotIn('approval', {e['kind'] for e in F.read_ledger()})

    def test_an_edited_payload_stops_verifying(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, 'x'))
            pp = os.path.join(d, 'x', 'p.json')
            json.dump(dict(a=1), open(pp, 'w'))
            led = os.path.join(d, 'LEDGER.jsonl')
            F.freeze('policy', dict(a=1), pp, ledger_path=led, root=d)
            self.assertTrue(F.verify(led, root=d)[0])
            json.dump(dict(a=2), open(pp, 'w'))
            ok, problems = F.verify(led, root=d)
            self.assertFalse(ok)
            self.assertTrue(any('hash' in p for p in problems))

    def test_a_population_cannot_be_frozen_before_a_policy(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            led = os.path.join(d, 'LEDGER.jsonl')
            pp = os.path.join(d, 'p.json')
            json.dump(dict(a=1), open(pp, 'w'))
            with self.assertRaises(PermissionError):
                F.freeze('population', dict(a=1), pp, ledger_path=led, root=d)

    def test_an_admitted_set_cannot_be_frozen_before_an_approval(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            led = os.path.join(d, 'LEDGER.jsonl')
            pp = os.path.join(d, 'p.json')
            json.dump(dict(a=1), open(pp, 'w'))
            F.freeze('policy', dict(a=1), pp, ledger_path=led, root=d)
            with self.assertRaises(PermissionError):
                F.freeze('admitted', dict(a=1), pp, ledger_path=led, root=d)

    def test_freezing_refuses_a_payload_that_names_what_it_admits(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            led = os.path.join(d, 'LEDGER.jsonl')
            pp = os.path.join(d, 'p.json')
            payload = dict(admitted=['05-sgk-khoa-hoc-5 Bài 3'])
            json.dump(payload, open(pp, 'w'))
            with self.assertRaises(PermissionError):
                F.freeze('policy', payload, pp, ledger_path=led, root=d)


class FrozenArtefacts(unittest.TestCase):
    def setUp(self):
        self.policy = load(os.path.join(FROZEN, 'TRUST-POLICY-CANDIDATES-v1.json'))

    def test_the_frozen_policy_carries_every_candidate_and_bound(self):
        self.assertEqual({c['name'] for c in self.policy['candidates']}, set(C.CANDIDATES))
        self.assertEqual(set(self.policy['bounds']), set(C.BOUNDS))

    def test_the_frozen_policy_states_the_invariant(self):
        self.assertIn('TRUST = SERVED', self.policy['invariant'])

    def test_the_recommendation_predicts_its_own_outcome(self):
        """A calibration predicts before it measures; a selection reports after."""
        self.assertEqual(self.policy['recommendation']['expected_outcome'], 'TRUTHFUL ZERO')

    def test_the_populations_carry_identities_and_no_signals(self):
        for name in ('BLIND-POPULATION-v1.json', 'BLIND-POPULATION-TEACHING-v1.json'):
            pop = load(os.path.join(FROZEN, name))
            self.assertTrue(pop['lessons'])
            for l in pop['lessons']:
                for forbidden in ('guards', 'text_sim', 'role_confidence', 'truth_wrong_any',
                                  'trusted', 'admitted', 'text'):
                    self.assertNotIn(forbidden, l, f'{name} carries a signal or a verdict')

    def test_the_evaluation_order_is_frozen_and_total(self):
        for name in ('BLIND-POPULATION-v1.json', 'BLIND-POPULATION-TEACHING-v1.json'):
            pop = load(os.path.join(FROZEN, name))
            self.assertEqual(sorted(l['evaluation_order'] for l in pop['lessons']),
                             list(range(1, len(pop['lessons']) + 1)))

    def test_no_production_thresholds_file_exists(self):
        """Round 5's guard, carried forward. Round 7 must not create one either."""
        for p in (os.path.join(ROOT, 'THRESHOLDS.json'),
                  os.path.join(FROZEN, 'THRESHOLDS.json')):
            self.assertFalse(os.path.exists(p), f'{p} would be a production trust gate')


class ApplyIsInert(unittest.TestCase):
    def test_cli_refuses_without_an_approval(self):
        r = subprocess.run([sys.executable, os.path.join(ROOT, 'tool', 'corpus', 'thresholds',
                                                         'apply.py'),
                            '--candidate', 'C2 · PROSE', '--evidence', os.devnull],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, A.REFUSED)
        self.assertIn('REFUSED', r.stdout)

    def test_refuses_an_approval_naming_a_different_policy(self):
        import tempfile
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as fh:
            json.dump(dict(policy_sha256='0' * 64, population_sha256='0' * 64,
                           decision='ACTIVATE', candidate='C2 · PROSE',
                           approved_by='x', approved_at_utc='now'), fh)
            path = fh.name
        try:
            with self.assertRaises(A.Refused):
                A.check_approval(path, 'C2 · PROSE')
        finally:
            os.unlink(path)

    def test_refuses_a_candidate_whose_machinery_does_not_exist(self):
        pop = dict(lessons=[dict(sourceDocumentId='b', lessonNo=1)])
        with self.assertRaises(A.Refused):
            A.apply_policy([], 'C4 · C1 + THE MACHINERY THAT DOES NOT EXIST', pop)

    def test_refuses_rows_outside_the_frozen_population(self):
        pop = dict(lessons=[dict(sourceDocumentId='in', lessonNo=1)])
        r = row(sourceDocumentId='out', lessonNo=9)
        with self.assertRaises(A.Refused):
            A.apply_policy([r], 'C2 · PROSE', pop)

    def test_refuses_a_row_that_already_carries_a_verdict(self):
        pop = dict(lessons=[dict(sourceDocumentId='in', lessonNo=1)])
        r = row(sourceDocumentId='in', lessonNo=1, truth_wrong_any=True)
        with self.assertRaises(A.Refused):
            A.apply_policy([r], 'C2 · PROSE', pop)

    def test_a_clean_application_admits_a_subset_of_served(self):
        pop = dict(lessons=[dict(sourceDocumentId='in', lessonNo=1)])
        rows = [row(sourceDocumentId='in', lessonNo=1, truth_wrong_any=None,
                    truth_teaching_critical=None),
                row(sourceDocumentId='in', lessonNo=1, guards=['math_guard'],
                    truth_wrong_any=None, truth_teaching_critical=None)]
        adm = A.apply_policy(rows, 'C2 · PROSE', pop)
        self.assertEqual(len(adm), 1)
        self.assertTrue(all(r['_served'] for r in adm))


class BlindWorklist(unittest.TestCase):
    def setUp(self):
        self.rows = [dict(row_id=f'r{i}', sourceDocumentId='b', lessonNo=i % 5,
                          page_pdf=i, text=f'text {i}', _served=True, guards=[],
                          role_confidence=0.9) for i in range(40)]
        self.worklist, self.key = SH.build(self.rows, {f'r{i}' for i in range(0, 40, 2)}, 11)

    def test_the_worklist_does_not_reveal_the_gate(self):
        for w in self.worklist:
            for k in ('admitted', 'trusted', '_served', 'guards', 'role_confidence'):
                self.assertNotIn(k, w)

    def test_every_row_gets_the_protocol_verdict_fields_unfilled(self):
        for w in self.worklist:
            for v in SH.VERDICTS:
                self.assertIsNone(w[v])

    def test_the_sealed_key_covers_every_row_and_holds_the_answer(self):
        self.assertEqual(set(self.key['key']), {w['row_id'] for w in self.worklist})
        self.assertEqual(sum(1 for v in self.key['key'].values() if v['admitted']), 20)

    def test_the_shuffle_interleaves_admitted_and_withheld(self):
        first = [self.key['key'][w['row_id']]['admitted'] for w in self.worklist[:10]]
        self.assertIn(True, first)
        self.assertIn(False, first)


class Measurement(unittest.TestCase):
    def setUp(self):
        self.bound, self.hash = M.resolve_bound('BOUND-2')

    def test_the_bound_comes_from_the_frozen_policy(self):
        self.assertEqual(self.bound['id'], 'BOUND-2')
        self.assertEqual(self.hash, F.read_ledger()[0]['sha256'])

    def test_an_unknown_bound_is_refused(self):
        with self.assertRaises(SystemExit):
            M.resolve_bound('BOUND-WHATEVER-MAKES-THIS-PASS')

    def test_a_clean_but_small_audit_does_not_pass(self):
        ann, key = M._synthetic(100)
        m = M.measure(ann, key, self.bound)
        self.assertEqual(m['verdict'], 'TRUTHFUL ZERO')
        self.assertEqual(m['teaching_critical']['rate'], 0.0)

    def test_a_clean_audit_of_the_required_size_passes(self):
        ann, key = M._synthetic(3000)
        m = M.measure(ann, key, self.bound)
        self.assertEqual(m['verdict'], 'PASS')

    def test_teaching_critical_errors_fail_the_bound(self):
        ann, key = M._synthetic(3000, tc_every=50)
        m = M.measure(ann, key, self.bound)
        self.assertEqual(m['verdict'], 'TRUTHFUL ZERO')
        self.assertEqual(m['trusted'], 0)

    def test_an_unsure_row_is_not_a_clean_row(self):
        ann, key = M._synthetic(3000)
        ann[0]['teaching_critical_fidelity'] = 'UNSURE'
        m = M.measure(ann, key, self.bound)
        self.assertEqual(m['verdict'], 'TRUTHFUL ZERO')
        self.assertTrue(any('UNSURE' in w for w in m['why']))

    def test_over_withholding_is_measured_on_the_refused_side(self):
        ann, key = M._synthetic(200)
        m = M.measure(ann, key, self.bound)
        self.assertEqual(m['over_withheld']['n'], 100)

    def test_lesson_incidence_is_measured_not_extrapolated(self):
        ann, key = M._synthetic(200, tc_every=20)
        m = M.measure(ann, key, self.bound)
        self.assertGreater(m['lesson_incidence']['lessons_with_admitted_blocks'], 0)
        self.assertGreater(m['lesson_incidence']['lessons_with_teaching_critical'], 0)


class CanonicalHashing(unittest.TestCase):
    def test_key_order_does_not_change_the_hash(self):
        a = dict(x=1, y=[1, 2], z=dict(b=2, a=1))
        b = dict(z=dict(a=1, b=2), y=[1, 2], x=1)
        self.assertEqual(F.sha256(a), F.sha256(b))

    def test_a_changed_value_changes_the_hash(self):
        self.assertNotEqual(F.sha256(dict(a=1)), F.sha256(dict(a=2)))

    def test_unicode_normalisation_is_applied(self):
        self.assertEqual(F.sha256(dict(a='Toán')), F.sha256(dict(a='Toán')))


GOLD = os.path.join(ROOT, 'poc-out', 'round5', 'lane-a3', 'evidence-gold-tc2-p2.jsonl')


@unittest.skipUnless(os.path.exists(GOLD), 'gitignored evidence rows not present')
class DerivationReproduces(unittest.TestCase):
    """The derivation is only worth anything if it reproduces the published baseline it claims
    to re-decide. Skipped on a clean clone, where `poc-out/` does not exist."""

    @classmethod
    def setUpClass(cls):
        with open(GOLD, encoding='utf-8') as fh:
            cls.rows = [json.loads(l) for l in fh]
        for r in cls.rows:
            r['_served'] = G.decide(r, G.PIPELINE_GATE)[0]

    def test_reproduces_the_published_round5_baseline(self):
        m = G.evaluate(self.rows, G.PIPELINE_GATE)
        self.assertEqual((m['n'], m['served'], m['coverage'], m['served_wrong'], m['ftr']),
                         (643, 354, 0.5505, 26, 0.0734))

    def test_teaching_critical_is_not_a_subset_of_false_trust(self):
        srv = [r for r in self.rows if r['_served']]
        tc_only = sum(1 for r in srv if r.get('truth_teaching_critical')
                      and not r.get('truth_wrong_any'))
        self.assertEqual(tc_only, 5, 'a bound on false trust alone would miss these')

    def test_the_prose_candidate_dominates_the_navigation_candidate(self):
        """More content AND a lower teaching-critical rate — the falsification of the intuition
        that a tighter role-confidence floor buys safety."""
        c1 = P.evaluate(self.rows, C.CANDIDATES['C1 · NAVIGATION-ONLY'])
        c2 = P.evaluate(self.rows, C.CANDIDATES['C2 · PROSE'])
        self.assertGreater(c2['n_trusted'], c1['n_trusted'])
        self.assertLess(c2['tc_rate'], c1['tc_rate'])

    def test_frozen_expected_tradeoffs_still_match_the_evidence(self):
        frozen = load(os.path.join(FROZEN, 'TRUST-POLICY-CANDIDATES-v1.json'))[
            'expected_tradeoffs_no_identities']
        for name, pol in C.CANDIDATES.items():
            if P.unavailable_clauses(pol):
                continue
            self.assertEqual(P.evaluate(self.rows, pol)['n_trusted'],
                             frozen[name]['n_trusted'], name)


if __name__ == '__main__':
    unittest.main()
