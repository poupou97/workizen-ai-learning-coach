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
        self.assertEqual(pa['attachmentRule'], 'capped-toc-v1')
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
        self.assertEqual(pp.main(['verify', p]), 0)

    def test_missing_manifest_fails(self):
        p = self._write(default_pack())
        self.assertEqual(pp.verify_file(p), ['missing buildProvenance'])
        self.assertEqual(pp.main(['verify', p]), 1)

    def test_tampered_content_fails_hash(self):
        pack = pp.stamp(default_pack(), 6, pp.read_flags({}), BUILDER)
        pack['khoaExperiments'][0]['title'] = 'edited after build'
        p = self._write(pack)
        self.assertTrue(any('contentHash mismatch' in x for x in pp.verify_file(p)))
        self.assertEqual(pp.main(['verify', p]), 1)

    def test_experimental_pack_fails_default_check(self):
        pack = default_pack()
        pack['tvReadings'].append(dict(book='b', lesson=1, page=1, passage='p', questions=[], source='pattern-router-v2-layout'))
        pack = pp.stamp(pack, 6, pp.read_flags({'PATTERN_ROUTER': '1', 'UNITS_SOURCE': 'layout'}), BUILDER)
        p = self._write(pack)
        problems = pp.verify_file(p)
        self.assertTrue(any('experimental' in x for x in problems))
        self.assertTrue(any('pattern-router' in x for x in problems))
        self.assertTrue(any('PATTERN_ROUTER=1' in x for x in problems))
        self.assertEqual(pp.main(['verify', p]), 1)
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
        self.assertEqual(pp.main([]), 2)
        self.assertEqual(pp.main(['verify']), 2)


if __name__ == '__main__':
    unittest.main()
