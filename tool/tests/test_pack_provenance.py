#!/usr/bin/env python3
"""WAL-210 — tests for tool/ui/pack_provenance.py (audit gate G5).

Run:  python3 -m unittest discover -s tool/tests -v
  or: python3 -m pytest tool/tests
No corpus needed — every pack here is synthetic."""
import copy
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'ui'))
import pack_provenance as pp  # noqa: E402

BUILDER = os.path.join(HERE, '..', 'ui', 'build_lesson_index.py')


def _main(argv):
    """Run the CLI silently — its FAIL/OK lines are the thing under test, not log noise."""
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()):
        return pp.main(argv)


def default_pack():
    return dict(grade=6, version='lesson-index-v2',
                subjects={'KHTN': [dict(sourceDocumentId='06-sgk-khoa-hoc-tu-nhien-6', volume=None,
                                        lessons=[dict(no=1, title='A', pageStart=6), dict(no=2, title='B', pageStart=11)])]},
                toanExercises={}, tvReadings=[dict(book='06-sgk-khoa-hoc-tu-nhien-6', lesson=1, page=6, passage='x' * 130,
                                                   questions=[dict(prompt='Vì sao?', page=6)])],
                tvWritings=[], suSources=[], khoaExperiments=[dict(subject='KHTN', book='06-sgk-khoa-hoc-tu-nhien-6', page=7, pagePdf=8, lesson=1,
                                                                   lessonTitle='A', title='T', chuanBi='c', tienHanh=['b1 b2 b3'], duDoan=None, quanSat=None)],
                diaMaps=[], sourceAssets=[], books=[])


class HashTests(unittest.TestCase):
    def test_hash_is_stable_across_key_order_and_ignores_provenance(self):
        a = default_pack()
        b = json.loads(json.dumps(dict(reversed(list(a.items()))), ensure_ascii=False))
        self.assertEqual(pp.content_hash(a), pp.content_hash(b))
        c = dict(a, buildProvenance={'anything': 1})
        self.assertEqual(pp.content_hash(a), pp.content_hash(c))
        self.assertEqual(len(pp.content_hash(a)), 64)

    def test_hash_changes_when_content_changes(self):
        a = default_pack(); b = copy.deepcopy(a)
        b['khoaExperiments'][0]['lesson'] = 2
        self.assertNotEqual(pp.content_hash(a), pp.content_hash(b))

    def test_canonical_json_is_sorted_compact_and_keeps_unicode(self):
        s = pp.canonical_json({'b': 'Tiếng Việt', 'a': [1, 2]})
        self.assertEqual(s, '{"a":[1,2],"b":"Tiếng Việt"}')


class ExperimentalTests(unittest.TestCase):
    def test_default_pack_is_not_experimental(self):
        self.assertFalse(pp.is_experimental(default_pack(), pp.read_flags({})))
        self.assertEqual(pp.router_sources(default_pack()), [])

    def test_router_source_makes_it_experimental(self):
        p = default_pack()
        p['tvReadings'].append(dict(book='b', lesson=1, page=1, passage='p', questions=[], source='pattern-router-v2-layout'))
        self.assertTrue(pp.is_experimental(p, pp.read_flags({})))
        self.assertEqual(pp.router_sources(p), [('tvReadings', 1, 'pattern-router-v2-layout')])
        p2 = default_pack(); p2['tvWritings'].append(dict(book='b', lesson=1, page=1, prompt='Viết…', source='pattern-router-v1'))
        self.assertTrue(pp.is_experimental(p2, pp.read_flags({})))

    def test_flag_makes_it_experimental_even_without_router_entries(self):
        self.assertTrue(pp.is_experimental(default_pack(), pp.read_flags({'PATTERN_ROUTER': '1'})))

    def test_read_flags_normalises(self):
        self.assertEqual(pp.read_flags({}), {'PATTERN_ROUTER': '0', 'UNITS_SOURCE': '', 'ROUTE_EXPLAIN': '0'})
        self.assertEqual(pp.read_flags({'PATTERN_ROUTER': '1', 'UNITS_SOURCE': 'layout', 'ROUTE_EXPLAIN': '1'}),
                         {'PATTERN_ROUTER': '1', 'UNITS_SOURCE': 'layout', 'ROUTE_EXPLAIN': '1'})
        self.assertEqual(pp.read_flags({'PATTERN_ROUTER': 'yes'})['PATTERN_ROUTER'], '0')


class StampTests(unittest.TestCase):
    def test_shape_and_determinism_except_built_at(self):
        t1 = datetime(2026, 9, 5, 10, 20, 30, tzinfo=timezone.utc)
        t2 = datetime(2026, 9, 5, 11, 0, 0, tzinfo=timezone.utc)
        a = pp.stamp(default_pack(), 6, pp.read_flags({}), BUILDER, built_at=t1)
        b = pp.stamp(default_pack(), 6, pp.read_flags({}), BUILDER, built_at=t2)
        pa, pb = a['buildProvenance'], b['buildProvenance']
        self.assertEqual(set(pa), {'schema', 'builderVersion', 'gitSha', 'builtAt', 'grade', 'flags', 'experimental', 'attachmentRule', 'contentHash', 'packVersion'})
        self.assertEqual(pa['schema'], 1)
        self.assertEqual(pa['grade'], 6)
        self.assertEqual(pa['attachmentRule'], 'capped-toc-v2')
        self.assertFalse(pa['experimental'])
        self.assertTrue(pa['builderVersion'].startswith('build_lesson_index.py@'))
        self.assertEqual(pa['builtAt'], '2026-09-05T10:20:30Z')
        self.assertEqual(pa['packVersion'], f'g6-20260905T1020Z-{pa["gitSha"][:8]}')
        self.assertEqual(set(pa['flags']), {'PATTERN_ROUTER', 'UNITS_SOURCE', 'ROUTE_EXPLAIN'})
        # deterministic except builtAt / packVersion
        for k in pa:
            if k not in ('builtAt', 'packVersion'):
                self.assertEqual(pa[k], pb[k], k)
        self.assertNotEqual(pa['builtAt'], pb['builtAt'])
        # hash is over the pack WITHOUT the manifest
        self.assertEqual(pa['contentHash'], pp.content_hash(default_pack()))

    def test_restamp_replaces_previous_manifest(self):
        a = pp.stamp(default_pack(), 6, pp.read_flags({}), BUILDER)
        a['buildProvenance']['contentHash'] = 'bogus'
        b = pp.stamp(a, 6, pp.read_flags({}), BUILDER)
        self.assertEqual(b['buildProvenance']['contentHash'], pp.content_hash(default_pack()))


class VerifyTests(unittest.TestCase):
    def _write(self, pack, name='lesson-index-g6.json'):
        d = tempfile.mkdtemp()
        p = os.path.join(d, name)
        json.dump(pack, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
        return p

    def test_good_default_pack_verifies(self):
        p = self._write(pp.stamp(default_pack(), 6, pp.read_flags({}), BUILDER))
        self.assertEqual(pp.verify_file(p), [])
        self.assertEqual(_main(['verify', p]), 0)

    def test_missing_manifest_fails(self):
        p = self._write(default_pack())
        self.assertEqual(pp.verify_file(p), ['missing buildProvenance'])
        self.assertEqual(_main(['verify', p]), 1)

    def test_tampered_content_fails_hash(self):
        pack = pp.stamp(default_pack(), 6, pp.read_flags({}), BUILDER)
        pack['khoaExperiments'][0]['title'] = 'edited after build'
        p = self._write(pack)
        self.assertTrue(any('contentHash mismatch' in x for x in pp.verify_file(p)))
        self.assertEqual(_main(['verify', p]), 1)

    def test_experimental_pack_fails_default_check(self):
        pack = default_pack()
        pack['tvReadings'].append(dict(book='b', lesson=1, page=1, passage='p', questions=[], source='pattern-router-v2-layout'))
        pack = pp.stamp(pack, 6, pp.read_flags({'PATTERN_ROUTER': '1', 'UNITS_SOURCE': 'layout'}), BUILDER)
        p = self._write(pack)
        problems = pp.verify_file(p)
        self.assertTrue(any('experimental' in x for x in problems))
        self.assertTrue(any('pattern-router' in x for x in problems))
        self.assertTrue(any('PATTERN_ROUTER=1' in x for x in problems))
        self.assertEqual(_main(['verify', p]), 1)
        # the same file passes when default-build assertions are not required (hash still checked)
        self.assertEqual(pp.verify_file(p, require_default=False), [])

    def test_router_entry_with_false_experimental_flag_is_caught(self):
        pack = pp.stamp(default_pack(), 6, pp.read_flags({}), BUILDER)
        pack['tvWritings'].append(dict(book='b', lesson=1, page=1, prompt='Viết', source='pattern-router-v1'))
        pack = pp.stamp(pack, 6, pp.read_flags({}), BUILDER)   # honest manifest: experimental=true
        self.assertTrue(pack['buildProvenance']['experimental'])
        pack['buildProvenance']['experimental'] = False        # lie in the manifest
        p = self._write(pack)
        problems = pp.verify_file(p)
        self.assertTrue(any('router sources exist' in x for x in problems))

    def test_grade_must_match_filename_and_pack(self):
        pack = pp.stamp(default_pack(), 6, pp.read_flags({}), BUILDER)
        p = self._write(pack, name='lesson-index-g7.json')
        self.assertTrue(any('!= expected 7' in x for x in pp.verify_file(p)))

    def test_usage_exit_code(self):
        self.assertEqual(_main([]), 2)
        self.assertEqual(_main(['verify']), 2)


if __name__ == '__main__':
    unittest.main()


# ---------------------------------------------------------------------------
# WAL-223 S3 + S4 — ABSENCE CANNOT SATISFY A POSITIVE OBLIGATION.
#
# S4: `router_sources()` returning [] means "no experiment source found". Over a
#     pack with nothing in it that is not evidence, yet it certified the pack a
#     DEFAULT build. S3: the CI step skipped when packs were absent and exited 0.
#
# Every test below is written so that REMOVING the fix turns it red — the point
# is the gate, not the coverage number.
class AbsenceIsNotSuccessTests(unittest.TestCase):
    def _empty(self):
        p = default_pack()
        for fam in pp.ACTIVITY_FAMILIES:
            p[fam] = {} if isinstance(p.get(fam), dict) else []
        return p

    def _stamped(self, pack, grade=6):
        # verify_pack() short-circuits on a missing manifest, so an unstamped
        # pack never reaches the default-build assertions at all. Two of these
        # tests passed vacuously until they were stamped — the same shape of
        # mistake this whole ticket is about.
        return pp.stamp(pack, grade, pp.read_flags({}), BUILDER)

    def test_empty_pack_is_not_certified_a_default_build(self):
        problems = pp.verify_pack(self._stamped(self._empty()), require_default=True)
        self.assertIn(pp.VACUOUS, problems,
                      'a pack carrying no activity at all was certified OK')

    def test_the_old_evidence_really_was_vacuous(self):
        # Documents WHY the fix is needed: the check the old code relied on
        # returns "nothing wrong" over an empty pack.
        self.assertEqual(pp.router_sources(self._empty()), [])
        self.assertEqual(pp.activity_population(self._empty()), 0)

    def test_a_real_pack_still_passes(self):
        # The fix must not buy honesty with a false red.
        self.assertGreater(pp.activity_population(default_pack()), 0)
        self.assertEqual(pp.verify_pack(self._stamped(default_pack()), require_default=True), [])

    def test_population_counts_entries_not_lessons(self):
        # ⚠ `toanExercises` is a DICT keyed by lesson: len() counts LESSONS.
        # Getting this wrong has broken twice, so it is pinned.
        p = default_pack()
        p['toanExercises'] = {'1': [{'e': 1}, {'e': 2}, {'e': 3}], '2': [{'e': 4}]}
        base = pp.activity_population(default_pack()) - 0
        self.assertEqual(pp.activity_population(p), base + 4,
                         'counted lessons (2) instead of exercises (4)')

    def test_every_family_counts_not_only_the_router_ones(self):
        # The first cut of this fix listed only the three families the router
        # touches and reported 11 of 12 real packs as empty — a false RED.
        for fam in ('suSources', 'khoaExperiments', 'diaMaps'):
            self.assertIn(fam, pp.ACTIVITY_FAMILIES, f'{fam} missing from the denominator')

    def test_unknown_top_level_key_is_loud(self):
        p = default_pack()
        p['brandNewFamily'] = [{'source': 'x'}]
        problems = pp.verify_pack(self._stamped(p), require_default=True)
        self.assertTrue(any('brandNewFamily' in x for x in problems),
                        'a key the gate cannot classify was silently ignored')

    def test_router_detection_scans_every_family(self):
        # A detector that only looks where the last experiment put things finds
        # only the last experiment.
        p = default_pack()
        p['khoaExperiments'] = [dict(source='pattern-router-v9')]
        self.assertTrue(pp.router_sources(p), 'router source outside tvReadings went unseen')

    # ---- S3: "no packs" is a recorded state, never a silent pass ----
    def test_bare_verify_is_still_a_usage_error(self):
        self.assertEqual(_main(['verify']), 2)

    def test_zero_packs_must_be_declared(self):
        # CI legitimately has no packs, but it has to SAY so.
        self.assertEqual(_main(['verify', '--allow-empty']), 0)

    def test_zero_packs_cannot_claim_verification(self):
        self.assertEqual(_main(['verify', '--require-verified']), 1,
                         'claimed verification with nothing verified')

    def test_ledger_records_that_nothing_ran(self):
        with tempfile.TemporaryDirectory() as d:
            led = os.path.join(d, 'sub', 'ledger.json')
            self.assertEqual(_main(['verify', '--allow-empty', '--ledger', led]), 0)
            rec = json.load(open(led, encoding='utf-8'))
        # The whole point: "never ran" is readable, and is not a verification.
        self.assertIs(rec['ran'], False)
        self.assertEqual(rec['packsGiven'], 0)
        self.assertIs(rec['claimsDefaultBuildVerified'], False)

    def test_ledger_records_a_real_verification(self):
        with tempfile.TemporaryDirectory() as d:
            pk = os.path.join(d, 'lesson-index-g6.json')
            pack = pp.stamp(default_pack(), 6, pp.read_flags({}), BUILDER)
            json.dump(pack, open(pk, 'w', encoding='utf-8'), ensure_ascii=False)
            led = os.path.join(d, 'ledger.json')
            self.assertEqual(_main(['verify', '--ledger', led, pk]), 0)
            rec = json.load(open(led, encoding='utf-8'))
        self.assertIs(rec['ran'], True)
        self.assertIs(rec['claimsDefaultBuildVerified'], True)
        self.assertEqual(rec['verified'], [pk])

    def test_empty_pack_does_not_claim_verification_in_the_ledger(self):
        with tempfile.TemporaryDirectory() as d:
            pk = os.path.join(d, 'lesson-index-g6.json')
            pack = pp.stamp(self._empty(), 6, pp.read_flags({}), BUILDER)
            json.dump(pack, open(pk, 'w', encoding='utf-8'), ensure_ascii=False)
            led = os.path.join(d, 'ledger.json')
            self.assertEqual(_main(['verify', '--ledger', led, pk]), 1)
            rec = json.load(open(led, encoding='utf-8'))
        self.assertEqual(rec['unverifiable'], [pk])
        self.assertEqual(rec['verified'], [])
        self.assertIs(rec['claimsDefaultBuildVerified'], False)
