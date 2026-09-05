#!/usr/bin/env python3
"""WAL-210 — tests for tool/corpus/ft_audit_score.py (statistics + derivation on synthetic rows).

Run:  python3 -m unittest discover -s tool/tests -v"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
import ft_audit_score as fs  # noqa: E402


class WilsonTests(unittest.TestCase):
    def test_wilson_matches_closed_form_for_zero_failures(self):
        p, lo, hi = fs.wilson(0, 100)
        self.assertEqual(p, 0.0); self.assertEqual(lo, 0.0)
        self.assertAlmostEqual(hi, fs.Z ** 2 / (100 + fs.Z ** 2), places=9)

    def test_wilson_known_value(self):
        p, lo, hi = fs.wilson(50, 439)                     # TC-v2 all-gold FTR
        self.assertAlmostEqual(p, 0.1139, places=4)
        self.assertAlmostEqual(lo, 0.0875, places=3); self.assertAlmostEqual(hi, 0.1470, places=3)

    def test_sample_size_for_one_percent_claim(self):
        self.assertEqual(fs.n_for_upper(0, 0.01, 'wilson'), 381)     # n > 99·z² = 380.3
        self.assertEqual(fs.n_for_upper(0, 0.01, 'exact'), 299)      # ln 0.05 / ln 0.99 = 298.1
        self.assertLess(fs.wilson(0, 381)[2], 0.01); self.assertGreaterEqual(fs.wilson(0, 380)[2], 0.01)
        self.assertLess(fs.clopper_pearson_upper(0, 299), 0.01); self.assertGreaterEqual(fs.clopper_pearson_upper(0, 298), 0.01)
        tbl = fs.sample_size_table()
        self.assertEqual([r['k'] for r in tbl], [0, 1, 2, 3, 4, 5])
        self.assertTrue(all(tbl[i]['wilson'] < tbl[i + 1]['wilson'] for i in range(5)))

    def test_empty_denominator(self):
        self.assertEqual(fs.wilson(0, 0), (None, None, None))


def row(fam='khoaExperiments', act='a1', served=True, **ann):
    r = dict(family=fam, book='b', activityId=act, servedAsTrusted=served, display_fidelity='', teaching_critical_fidelity='', role_fidelity='', lesson_attachment='', false_trust='')
    r.update(ann)
    return r


class RateTests(unittest.TestCase):
    def test_rate_counts_only_ok_and_wrong(self):
        rows = [row(display_fidelity='OK'), row(display_fidelity='WRONG'), row(display_fidelity='UNSURE'), row(display_fidelity='NA'), row()]
        x = fs._rate(rows, 'display_fidelity')
        self.assertEqual((x['wrong'], x['ok'], x['judged'], x['unsure'], x['na'], x['unjudged'], x['sampled']), (1, 1, 2, 1, 1, 1, 5))
        self.assertAlmostEqual(x['rate'], 0.5)

    def test_derived_false_trust(self):
        att = {'a1': 'OK', 'a2': 'WRONG'}
        self.assertEqual(fs.derived_false_trust(row(display_fidelity='OK', teaching_critical_fidelity='NA', role_fidelity='OK'), att), 'OK')
        self.assertEqual(fs.derived_false_trust(row(display_fidelity='OK', role_fidelity='WRONG'), att), 'WRONG')
        self.assertEqual(fs.derived_false_trust(row(act='a2', display_fidelity='OK'), att), 'WRONG')      # attachment via the activity
        self.assertEqual(fs.derived_false_trust(row(display_fidelity='OK', role_fidelity='UNSURE'), att), 'UNSURE')
        self.assertEqual(fs.derived_false_trust(row(), {}), '')                                            # nothing judged

    def test_score_rows_separates_families_activities_and_withheld(self):
        rows = [row(act='a1', display_fidelity='OK', role_fidelity='OK', lesson_attachment='OK', false_trust='OK'),
                row(act='a1', display_fidelity='WRONG', role_fidelity='OK', false_trust='WRONG'),
                row(fam='tvReadings', act='t1', display_fidelity='OK', role_fidelity='WRONG', lesson_attachment='WRONG', false_trust='OK'),
                row(fam='tslBai17', act='b17', served=False, notes='safe rejection, figure label')]
        res = fs.score_rows(rows)
        self.assertEqual(res['ALL']['blocks'], 3); self.assertEqual(res['ALL']['activities'], 2)
        self.assertEqual(res['ALL']['display_only_fidelity']['wrong'], 1)
        self.assertEqual(res['ALL']['lesson_attachment']['judged'], 2)                 # per activity, not per block
        self.assertEqual(res['ALL']['lesson_attachment']['wrong'], 1)
        self.assertEqual(res['ALL']['false_trust_derived']['wrong'], 2)                # a1 second row + t1 (role + attachment)
        self.assertEqual(res['ALL']['false_trust_reviewer']['wrong'], 1)               # reviewer disagreed on t1 — both reported
        self.assertEqual(res['khoaExperiments']['blocks'], 2); self.assertEqual(res['tvReadings']['blocks'], 1)
        self.assertEqual(res['_withheld_reviewed'], dict(rows=1, with_notes=1))
        md = fs.render_md(res, 'meta', 'title')
        self.assertIn('| 0 | 381 | 299 |', md)


if __name__ == '__main__':
    unittest.main()
