#!/usr/bin/env python3
"""Round 5 · Lane D — tests for tool/corpus/legacy/packs.py and pack_delta_audit.py.

What is worth testing here is the *order* the Founder ordered (§13): snapshot before
rebuild, the old baseline stays reproducible, and a delta that tells a re-attachment
apart from a deletion plus an addition. All fixtures are synthetic packs in a tmpdir —
no poc-out, no real packs, no SGK.

Run:  python3 -m unittest discover -s tool/tests -v
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _lane_d_sandbox  # noqa: E402,F401  — MUST precede any import that pulls in legacy/common.py

sys.path.insert(0, os.path.join(HERE, '..', 'ui'))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus', 'legacy'))
import packs  # noqa: E402
import pack_delta_audit  # noqa: E402
import pack_provenance  # noqa: E402


def a_pack(grade=6, readings=(), exercises=(), assets=()):
    """A minimal but structurally real pack; `readings` = (lesson, page, passage) triples."""
    p = {
        'grade': grade, 'version': 'lesson-index-v2',
        'subjects': {'KHTN': [{'sourceDocumentId': 'b1', 'volume': None,
                               'lessons': [{'no': 1, 'title': 'A', 'pageStart': 5},
                                           {'no': 2, 'title': 'B', 'pageStart': 9}]}]},
        'toanExercises': {str(l): [{'expr': e, 'skillCaseId': 'sc', 'page': pg, 'book': 'b1'}]
                          for (l, pg, e) in exercises},
        'tvReadings': [{'book': 'b1', 'lesson': l, 'page': pg, 'passage': t,
                        'questions': [{'prompt': '1. ?', 'page': pg}]} for (l, pg, t) in readings],
        'tvWritings': [], 'suSources': [], 'khoaExperiments': [], 'diaMaps': [],
        'sourceAssets': [{'asset': a, 'lesson': 1, 'sourceDocumentId': 'b1'} for a in assets],
        'books': [{'sourceDocumentId': 'b1', 'subject': 'KHTN', 'grade': grade}],
    }
    return pack_provenance.stamp(p, grade, pack_provenance.read_flags({}), __file__)


class DeltaTests(unittest.TestCase):
    """The delta must name what happened, not merely that something did."""

    def _delta(self, before, after):
        rows = packs.delta_pack(before, after)
        return {r['verdict'] for r in rows}, rows

    def test_identical_packs_are_all_unchanged(self):
        b = a_pack(readings=[(1, 5, 'x'), (2, 9, 'y')])
        verdicts, rows = self._delta(b, json.loads(json.dumps(b)))
        self.assertEqual(verdicts, {'unchanged'})
        self.assertEqual(len(rows), 2)

    def test_reattachment_is_a_MOVE_not_a_delete_plus_an_add(self):
        """The point of the identity: the same printed region handed to another lesson."""
        b = a_pack(readings=[(1, 5, 'x')])
        a = a_pack(readings=[(2, 5, 'x')])
        _v, rows = self._delta(b, a)
        self.assertEqual([r['verdict'] for r in rows], ['moved-lesson'])
        self.assertEqual((rows[0]['lessonBefore'], rows[0]['lessonAfter']), (1, 2))

    def test_changed_text_at_the_same_place_is_content_changed(self):
        """tvReadings keys on the passage, so a changed passage is a new activity;
        a changed *question set* under the same passage is a content change."""
        b = a_pack(readings=[(1, 5, 'x')])
        a = json.loads(json.dumps(b))
        a['tvReadings'][0]['questions'] = [{'prompt': '2. ?', 'page': 5}]
        _v, rows = self._delta(b, a)
        self.assertEqual([r['verdict'] for r in rows], ['content-changed'])

    def test_appeared_and_disappeared_are_distinguished(self):
        b = a_pack(readings=[(1, 5, 'x')])
        a = a_pack(readings=[(1, 7, 'z')])
        v, _rows = self._delta(b, a)
        self.assertEqual(v, {'appeared', 'disappeared'})

    def test_delta_compares_hashes_not_text(self):
        """D4: no verbatim SGK may leave the pack — the delta rows carry digests only."""
        b = a_pack(readings=[(1, 5, 'SECRET PASSAGE')])
        rows = packs.delta_pack(b, a_pack(readings=[(2, 5, 'SECRET PASSAGE')]))
        blob = json.dumps(rows, ensure_ascii=False)
        self.assertNotIn('SECRET PASSAGE', blob)


class MetricsTests(unittest.TestCase):
    def test_metrics_count_activities_per_family_and_openable_lessons(self):
        m = packs.pack_metrics(a_pack(readings=[(1, 5, 'x'), (2, 9, 'y')],
                                      exercises=[(1, 5, '1+1')], assets=['a.png']))
        self.assertEqual(m['activityFamilies']['tvReadings'], 2)
        self.assertEqual(m['activityFamilies']['toanExercises'], 1)
        self.assertEqual(m['activitiesTotal'], 4)
        self.assertEqual(m['openableLessons'], 2)      # lessons 1 and 2 of book b1
        self.assertEqual(m['catalogueLessons'], 2)

    def test_metrics_carry_no_pack_text(self):
        m = packs.pack_metrics(a_pack(readings=[(1, 5, 'SECRET PASSAGE')]))
        self.assertNotIn('SECRET PASSAGE', json.dumps(m, ensure_ascii=False))


class OrderOfOperationsTests(unittest.TestCase):
    """§13 in code: a rebuild can never be the first thing that happens to a pack."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='lane-d-packs-')
        self.pack_dir = os.path.join(self.tmp, 'pack')
        os.makedirs(self.pack_dir)
        for g in (6,):
            with open(os.path.join(self.pack_dir, f'lesson-index-g{g}.json'), 'w', encoding='utf-8') as f:
                json.dump(a_pack(grade=g, readings=[(1, 5, 'x')]), f, ensure_ascii=False)
        self.snap = os.path.join(self.tmp, 'before')

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _args(self, **kw):
        return type('A', (), kw)()

    def test_snapshot_writes_manifest_metrics_sums_and_readme(self):
        rc = packs.cmd_snapshot(self._args(dir=self.snap, pack_dir=self.pack_dir, note='t'))
        self.assertEqual(rc, 0)
        for f in ('MANIFEST.json', 'BASELINE-METRICS.json', 'PIPELINE-VERSION.json', 'SHA256SUMS', 'README.md'):
            self.assertTrue(os.path.exists(os.path.join(self.snap, f)), f)
        man = json.load(open(os.path.join(self.snap, 'MANIFEST.json'), encoding='utf-8'))
        self.assertTrue(man['packs']['6']['present'])
        self.assertEqual(len(man['packs']['6']['sha256']), 64)
        self.assertIn('attachmentRule', man['pipelineVersion'])

    def test_snapshot_refuses_to_overwrite_an_existing_snapshot(self):
        packs.cmd_snapshot(self._args(dir=self.snap, pack_dir=self.pack_dir, note=''))
        rc = packs.cmd_snapshot(self._args(dir=self.snap, pack_dir=self.pack_dir, note=''))
        self.assertEqual(rc, 2, 'a snapshot is the old baseline — it is never overwritten')

    def test_rebuild_refuses_without_a_snapshot(self):
        rc = packs.cmd_rebuild(self._args(snapshot=os.path.join(self.tmp, 'nope'), grades='6',
                                          pack_dir=self.pack_dir, out='', attach_log_dir=self.tmp))
        self.assertEqual(rc, 2)

    def test_rebuild_refuses_when_the_snapshot_does_not_describe_the_packs_on_disk(self):
        packs.cmd_snapshot(self._args(dir=self.snap, pack_dir=self.pack_dir, note=''))
        p = os.path.join(self.pack_dir, 'lesson-index-g6.json')
        d = json.load(open(p, encoding='utf-8'))
        d['tvReadings'][0]['lesson'] = 2
        json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
        rc = packs.cmd_rebuild(self._args(snapshot=self.snap, grades='6', pack_dir=self.pack_dir,
                                          out='', attach_log_dir=self.tmp))
        self.assertEqual(rc, 3, 'snapshotting pack A and rebuilding over pack B preserves the wrong baseline')

    def test_restore_puts_the_old_baseline_back_byte_for_byte(self):
        p = os.path.join(self.pack_dir, 'lesson-index-g6.json')
        original = open(p, 'rb').read()
        packs.cmd_snapshot(self._args(dir=self.snap, pack_dir=self.pack_dir, note=''))
        open(p, 'wb').write(b'{"grade":6}')
        packs.cmd_restore(self._args(snapshot=self.snap, pack_dir=self.pack_dir))
        self.assertEqual(open(p, 'rb').read(), original)

    def test_restore_refuses_a_corrupted_snapshot(self):
        packs.cmd_snapshot(self._args(dir=self.snap, pack_dir=self.pack_dir, note=''))
        open(os.path.join(self.snap, 'packs', 'lesson-index-g6.json'), 'ab').write(b' ')
        rc = packs.cmd_restore(self._args(snapshot=self.snap, pack_dir=self.pack_dir))
        self.assertEqual(rc, 3)


class DeltaAuditTests(unittest.TestCase):
    """The flag-level restore precision: restored-correct / all restored."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='lane-d-delta-audit-')

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _logs(self, old_rows, new_rows):
        old = os.path.join(self.tmp, 'old'); new = os.path.join(self.tmp, 'new')
        for d, rows, rule in ((old, old_rows, 'capped-toc-v1'), (new, new_rows, 'capped-toc-v2')):
            os.makedirs(d, exist_ok=True)
            json.dump({'grade': 5, 'summary': {'rule': rule, 'books': {}, 'flagged': len(rows), 'dropped': 0},
                       'dropped': [], 'flagged': rows},
                      open(os.path.join(d, 'lesson-index-g5.attach-log.json'), 'w', encoding='utf-8'))
        return old, new

    def test_a_row_that_stops_being_flagged_is_a_restore(self):
        row = dict(family='tvReadings', book='b', page=8, lesson=1, reason='range_mismatch', note='b:p009:0001')
        old, new = self._logs([row], [])
        out = os.path.join(self.tmp, 'rows.json')
        pack_delta_audit.cmd_rows(type('A', (), dict(old=old, new=new, out=out))())
        d = json.load(open(out, encoding='utf-8'))
        self.assertEqual(d['totals'], {'restored': 1})
        self.assertEqual(d['rows'][0]['pagePdf'], 9, 'the pdf page is read off the unit id, not guessed')

    def test_a_row_that_starts_being_flagged_is_newly_flagged(self):
        row = dict(family='tvWritings', book='b', page=52, lesson=10, reason='range_mismatch', note='b:p053:0164')
        old, new = self._logs([], [row])
        out = os.path.join(self.tmp, 'rows.json')
        pack_delta_audit.cmd_rows(type('A', (), dict(old=old, new=new, out=out))())
        self.assertEqual(json.load(open(out, encoding='utf-8'))['totals'], {'newly-flagged': 1})

    def test_restore_precision_counts_only_restores_and_needs_the_printed_page_to_agree(self):
        sample = os.path.join(self.tmp, 's.json'); answers = os.path.join(self.tmp, 'a.json')
        json.dump({'rows': [
            dict(id='r1', grade=5, family='f', book='b', lesson=7, page=30, note='', pagePdf=31,
                 reasonBefore='range_mismatch', reasonAfter='range_ok', direction='restored'),
            dict(id='r2', grade=5, family='f', book='b', lesson=9, page=40, note='', pagePdf=41,
                 reasonBefore='range_mismatch', reasonAfter='range_ok', direction='restored'),
            dict(id='r3', grade=5, family='f', book='b', lesson=3, page=12, note='', pagePdf=13,
                 reasonBefore='range_ok', reasonAfter='range_mismatch', direction='newly-flagged'),
        ]}, open(sample, 'w', encoding='utf-8'))
        json.dump({'protocol': 'test', 'readings': [
            {'id': 'r1', 'printedLesson': 7, 'unreadable': False},     # restore agrees with the page
            {'id': 'r2', 'printedLesson': 8, 'unreadable': False},     # restore contradicts the page
            {'id': 'r3', 'printedLesson': 4, 'unreadable': False},     # new flag agrees with the page
        ]}, open(answers, 'w', encoding='utf-8'))
        out = os.path.join(self.tmp, 'v.json')
        pack_delta_audit.cmd_verdicts(type('A', (), dict(sample=sample, answers=answers, out=out, md=''))())
        d = json.load(open(out, encoding='utf-8'))
        self.assertEqual(d['counts']['restored-correct'], 1)
        self.assertEqual(d['counts']['restored-wrong'], 1)
        self.assertEqual(d['counts']['flagged-correct'], 1)
        self.assertAlmostEqual(d['restorePrecisionValue'], 0.5)
        self.assertAlmostEqual(d['newFlagPrecisionValue'], 1.0,
                               msg='a newly-flagged row is CORRECT when the page really is another lesson')

    def test_a_page_with_no_lesson_badge_is_unjudgeable_not_a_disagreement(self):
        """A page in the middle of a lesson prints no badge. Scoring that as "the page is a
        different lesson" would manufacture precision the method never measured."""
        sample = os.path.join(self.tmp, 's.json'); answers = os.path.join(self.tmp, 'a.json')
        json.dump({'rows': [
            dict(id='r1', grade=5, family='f', book='b', lesson=7, page=30, note='', pagePdf=31,
                 reasonBefore='range_mismatch', reasonAfter='range_ok', direction='restored'),
            dict(id='r2', grade=5, family='f', book='b', lesson=9, page=40, note='', pagePdf=41,
                 reasonBefore='range_mismatch', reasonAfter='range_ok', direction='restored'),
        ]}, open(sample, 'w', encoding='utf-8'))
        json.dump({'protocol': 'test', 'readings': [
            {'id': 'r1', 'printedLesson': 7, 'unreadable': False},
            {'id': 'r2', 'printedLesson': None, 'unreadable': False},   # mid-lesson page, no badge
        ]}, open(answers, 'w', encoding='utf-8'))
        out = os.path.join(self.tmp, 'v.json')
        pack_delta_audit.cmd_verdicts(type('A', (), dict(sample=sample, answers=answers, out=out, md=''))())
        d = json.load(open(out, encoding='utf-8'))
        self.assertEqual(d['counts']['no-badge-unjudgeable'], 1)
        self.assertEqual(d['counts'].get('restored-wrong', 0), 0)
        self.assertAlmostEqual(d['restorePrecisionValue'], 1.0)          # 1/1 judgeable
        self.assertIn('1 / 2', d['restorePrecisionWorstCase'])           # the harsh reading, reported beside
        self.assertEqual(d['unjudgeableByDirection'], {'restored': 1})


if __name__ == '__main__':
    unittest.main()
