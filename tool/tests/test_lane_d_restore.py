#!/usr/bin/env python3
"""Round 5 · Lane D — tests for RESTORE PRECISION (tool/corpus/legacy/restore.py) and the
round-5 scoreboard extensions (multi-root batches, the restore block, figure_relation).

The Founder's rule is "do not raise coverage with imprecise restores", so the tests are about
the ways a restore metric can flatter itself: inheriting the old judgement instead of making a
new one, counting UNSURE as correct, printing a blank where no restore stage ran, and summing
a guard-loosening restore with a repair restore.

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
import _lane_d_sandbox  # noqa: E402,F401  — MUST precede anything that reaches legacy/common.py

sys.path.insert(0, os.path.join(HERE, '..', 'corpus', 'legacy'))
import restore  # noqa: E402
import scoreboard  # noqa: E402

PIPE = 'test-pipe'


class BaseVerdictTests(unittest.TestCase):
    """The earlier audit's judgement of the REFUSAL — read off its note, never guessed."""

    def test_over_withheld_note_reads_as_OVER(self):
        self.assertEqual(restore._base_verdict('CONFLICT (agree_order) — OVER-withheld: a plain rule box'), 'OVER')

    def test_safe_rejection_note_reads_as_SAFE(self):
        self.assertEqual(restore._base_verdict('WITHHELD (agree_text) — safe rejection: fractions flattened'), 'SAFE')
        self.assertEqual(restore._base_verdict('WITHHELD (figure_dependent) — correct by design'), 'SAFE')

    def test_the_round5_keyword_prefix_is_read_and_wins(self):
        """Round 5 asks the annotator for a leading keyword; round 4 wrote the verdict inline.
        Both conventions are in the corpus, and a prefix must beat a stray word in the prose."""
        self.assertEqual(restore._base_verdict('OVER: clean section title refused on agree_order'), 'OVER')
        self.assertEqual(restore._base_verdict('SAFE: figure-dependent question, unreadable alone'), 'SAFE')
        self.assertEqual(restore._base_verdict('UNSURE: the crop is cut off'), 'UNSURE')
        self.assertEqual(restore._base_verdict('OVER: a safe, clean paragraph'), 'OVER',
                         'the prefix is the field the annotator filled; a stray «safe» must not win')

    def test_an_unclassifiable_note_is_UNSURE_not_SAFE(self):
        self.assertEqual(restore._base_verdict('WITHHELD (agree_text)'), 'UNSURE')
        self.assertEqual(restore._base_verdict(''), 'UNSURE')


class RestoreRowsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='lane-d-restore-')
        self.delta = os.path.join(self.tmp, 'delta.json')
        self.annot = os.path.join(self.tmp, 'annotated.jsonl')
        self.out = os.path.join(self.tmp, 'rows.json')
        self.rerun = os.path.join(self.tmp, 'rerun')

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _fixture(self, rows, notes):
        json.dump({'withheld': {'rows': rows}}, open(self.delta, 'w', encoding='utf-8'))
        with open(self.annot, 'w', encoding='utf-8') as f:
            for sid, note in notes.items():
                f.write(json.dumps({'sampleId': sid, 'notes': note, 'servedAsTrusted': False}) + '\n')
        d = os.path.join(self.rerun, 'tcroot', 'poc-out', 'trusted-corpus', 'tc-v2', PIPE, 'lessons', 'b')
        os.makedirs(d, exist_ok=True)
        json.dump({'blocks': [{'id': 'blk1', 'text': 'Một câu văn.', 'bbox': [0, 0, 1, 0.1],
                               'role': {'value': 'body'}}]},
                  open(os.path.join(d, 'bai-01.tsl.json'), 'w', encoding='utf-8'))
        return type('A', (), dict(delta=self.delta, annotated=self.annot, rerun_dir=self.rerun,
                                  pipeline=PIPE, out=self.out))()

    def test_restored_and_falsely_withheld_recovered_are_counted_separately(self):
        rows = [
            {'sampleId': 's1', 'book': 'b', 'lesson': 1, 'pagePdf': 9, 'base_reasons': ['page_feature:color_heavy'],
             'outcome': 'now_served', 'new_block': {'id': 'blk1'}},
            {'sampleId': 's2', 'book': 'b', 'lesson': 1, 'pagePdf': 9, 'base_reasons': ['agree_text'],
             'outcome': 'now_served', 'new_block': {'id': 'blk1'}},
            {'sampleId': 's3', 'book': 'b', 'lesson': 1, 'pagePdf': 9, 'base_reasons': ['agree_text'],
             'outcome': 'now_withheld'},
        ]
        a = self._fixture(rows, {'s1': 'OVER-withheld: a clean stanza',
                                 's2': 'safe rejection: the fractions are flattened',
                                 's3': 'OVER-withheld: a plain question'})
        restore.cmd_rows(a)
        d = json.load(open(self.out, encoding='utf-8'))
        self.assertEqual(d['restored'], 2)
        self.assertEqual(d['falselyWithheldTotal'], 2, 'both s1 and s3 were judged over-withheld')
        self.assertEqual(d['falselyWithheldRecovered'], 1, 'only s1 came back')
        self.assertEqual(d['wronglyRestoredCandidates'], 1,
                         's2 was a SAFE refusal and is served again — the dangerous direction')

    def test_a_string_new_block_resolves_to_its_text_and_role(self):
        """rerun.recovered() writes `new_block` as the block ID STRING. Accepting only a dict made every
        restored row resolve to None, and the audit sheets rendered «(no text recorded)» for all of them —
        a blank sheet from which a precision would have been invented. Caught by the blind annotator."""
        rows = [{'sampleId': 's1', 'book': 'b', 'lesson': 1, 'pagePdf': 9, 'base_reasons': ['agree_order'],
                 'outcome': 'now_served', 'new_block': 'blk1'}]
        a = self._fixture(rows, {'s1': 'OVER: a clean instruction'})
        restore.cmd_rows(a)
        d = json.load(open(self.out, encoding='utf-8'))
        r = d['rows'][0]
        self.assertEqual(r['newBlockId'], 'blk1')
        self.assertEqual(r['newText'], 'Một câu văn.')
        self.assertEqual(r['newRole'], 'body')
        self.assertTrue(r['newBlockResolved'])
        self.assertEqual(d['restoredWithUnresolvedBlock'], [])

    def test_an_unresolvable_block_is_reported_not_silently_blank(self):
        rows = [{'sampleId': 's1', 'book': 'b', 'lesson': 1, 'pagePdf': 9, 'base_reasons': ['agree_order'],
                 'outcome': 'now_served', 'new_block': 'no-such-block'}]
        a = self._fixture(rows, {'s1': 'OVER: a clean instruction'})
        restore.cmd_rows(a)
        d = json.load(open(self.out, encoding='utf-8'))
        self.assertFalse(d['rows'][0]['newBlockResolved'])
        self.assertEqual(d['restoredWithUnresolvedBlock'], ['s1'])

    def test_the_mechanism_is_recorded_so_a_guard_restore_is_never_read_as_a_repair(self):
        a = self._fixture([], {})
        restore.cmd_rows(a)
        d = json.load(open(self.out, encoding='utf-8'))
        self.assertIn('NOT a repair', d['restoreMechanism'])


class RestorePrecisionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='lane-d-prec-')

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run(self, judgements, base_verdicts=('OVER', 'OVER', 'SAFE')):
        rows_f = os.path.join(self.tmp, 'rows.json')
        ans_f = os.path.join(self.tmp, 'ans.json')
        out_f = os.path.join(self.tmp, 'prec.json')
        json.dump({'restoreMechanism': 'guard change — NOT a repair', 'falselyWithheldTotal': 3,
                   'rows': [dict(id=f's{i}', book='b', lesson=1, pagePdf=9, baseReasons=['agree_text'],
                                 baseRefusalVerdict=v, newRole='body', restored=True)
                            for i, v in enumerate(base_verdicts)]},
                  open(rows_f, 'w', encoding='utf-8'))
        json.dump({'protocol': 'test', 'annotator': 't', 'judgements': judgements},
                  open(ans_f, 'w', encoding='utf-8'))
        restore.cmd_precision(type('A', (), dict(rows=rows_f, answers=ans_f, out=out_f, md=''))())
        return json.load(open(out_f, encoding='utf-8'))

    def test_precision_is_correct_over_correct_plus_wrong(self):
        d = self._run([{'id': 's0', 'verdict': 'CORRECT'}, {'id': 's1', 'verdict': 'WRONG'},
                       {'id': 's2', 'verdict': 'CORRECT'}])
        self.assertAlmostEqual(d['restorePrecisionValue'], 2 / 3)

    def test_UNSURE_is_excluded_from_the_precision_and_counted_beside(self):
        """Counting UNSURE as correct is the cheapest way to inflate a restore precision."""
        d = self._run([{'id': 's0', 'verdict': 'CORRECT'}, {'id': 's1', 'verdict': 'UNSURE'},
                       {'id': 's2', 'verdict': 'WRONG'}])
        self.assertAlmostEqual(d['restorePrecisionValue'], 0.5, msg='1 correct of 2 judgeable, not 2 of 3')
        self.assertEqual(d['counts']['UNSURE'], 1)

    def test_the_fresh_verdict_overrides_the_earlier_judgement_of_the_refusal(self):
        """A region the earlier audit called over-withheld can still come back WRONG — and must."""
        d = self._run([{'id': 's0', 'verdict': 'WRONG', 'why': 'spliced'},
                       {'id': 's1', 'verdict': 'CORRECT'}, {'id': 's2', 'verdict': 'CORRECT'}],
                      base_verdicts=('OVER', 'OVER', 'OVER'))
        self.assertAlmostEqual(d['restorePrecisionValue'], 2 / 3)
        self.assertEqual(d['falselyWithheldRecoveredAndCorrect'], 2,
                         'recovered-and-correct counts only the ones the fresh judgement kept')

    def test_a_restored_SAFE_refusal_is_named_in_the_output(self):
        d = self._run([{'id': 's0', 'verdict': 'CORRECT'}, {'id': 's1', 'verdict': 'CORRECT'},
                       {'id': 's2', 'verdict': 'CORRECT'}])
        self.assertEqual(d['restoredThatTheEarlierAuditCalledSafeRefusals'], ['s2'])

    def test_no_judgements_means_no_precision_not_a_perfect_one(self):
        d = self._run([])
        self.assertIsNone(d['restorePrecisionValue'])
        self.assertEqual(d['counts'].get('not-judged'), 3)


class ScoreboardRoundFiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='lane-d-sb5-')

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_multiple_legacy_roots_are_read_and_labelled_by_round(self):
        r4 = os.path.join(self.tmp, 'round4', 'legacy')
        r5 = os.path.join(self.tmp, 'round5', 'legacy')
        for root, name in ((r4, 'batch-1'), (r5, 'batch-2')):
            d = os.path.join(root, name)
            os.makedirs(d)
            json.dump({'batch': name, 'lessons': []}, open(os.path.join(d, 'batch-spec.json'), 'w'))
            json.dump({'started': '2026-09-0' + ('5' if name == 'batch-1' else '6')},
                      open(os.path.join(d, 'run-manifest.json'), 'w'))
        both = f'{r4},{r5}'
        ds = scoreboard.batch_dirs(both)
        self.assertEqual(len(ds), 2)
        self.assertEqual([scoreboard.batch_label(x, scoreboard.legacy_roots(both)) for x in ds],
                         ['round4/legacy/batch-1', 'round5/legacy/batch-2'])

    def test_a_single_root_keeps_the_bare_batch_name(self):
        r5 = os.path.join(self.tmp, 'round5', 'legacy')
        d = os.path.join(r5, 'batch-2')
        os.makedirs(d)
        self.assertEqual(scoreboard.batch_label(d, scoreboard.legacy_roots(r5)), 'batch-2')

    def test_no_restore_stage_reports_a_reason_not_a_zero(self):
        """A blank cell reads as zero; zero restores and no-restore-stage are different facts."""
        d = os.path.join(self.tmp, 'batch-x')
        os.makedirs(d)
        rec = scoreboard.restore_record(d)
        self.assertFalse(rec['ran'])
        # The test pins the PROPERTY — a reason is given — not the exact prose, which is copy.
        self.assertTrue(rec['why'].strip(), 'a false `ran` must be accompanied by a reason')
        self.assertIn('REPAIRED', rec['why'], 'the reason must name the stage that did not run')
        md = '\n'.join(scoreboard.render_restore({'dir': 'batch-x', 'restore': rec}))
        self.assertIn('empty, not zero', md)

    def test_the_restore_block_reports_precision_when_it_exists(self):
        d = os.path.join(self.tmp, 'batch-y', 'restore')
        os.makedirs(d)
        json.dump({'restoreMechanism': 'guard change — NOT a repair', 'reviewedWithheldRegions': 30,
                   'restored': 6, 'falselyWithheldTotal': 12, 'falselyWithheldRecovered': 4,
                   'falselyWithheldRecoveryRate': '4 / 12 = 0.333', 'wronglyRestoredCandidates': 2},
                  open(os.path.join(d, 'restore-rows.json'), 'w'))
        json.dump({'restorePrecision': '5 / 6 = 0.833', 'restorePrecisionValue': 5 / 6,
                   'counts': {'CORRECT': 5, 'WRONG': 1}, 'falselyWithheldRecoveredAndCorrect': 4},
                  open(os.path.join(d, 'restore-precision.json'), 'w'))
        rec = scoreboard.restore_record(os.path.dirname(d))
        self.assertTrue(rec['ran'])
        md = '\n'.join(scoreboard.render_restore({'dir': 'batch-y', 'restore': rec}))
        self.assertIn('RESTORE PRECISION', md)
        self.assertIn('5 / 6 = 0.833', md)
        self.assertIn('NOT a repair', md)

    def test_figure_relation_detached_rate_is_reported_within_class(self):
        d = os.path.join(self.tmp, 'batch-z', 'audit')
        os.makedirs(d)
        with open(os.path.join(d, 'annotated-kind-caption-20260907.jsonl'), 'w', encoding='utf-8') as f:
            for v in ('OK', 'OK', 'DETACHED', 'DETACHED', 'NA'):
                f.write(json.dumps({'sampleId': v, 'figure_relation': v}) + '\n')
        c = scoreboard.caption_relation(os.path.dirname(d))
        self.assertEqual(c['detached'], 2)
        self.assertEqual(c['judged'], 4, 'NA is not in the denominator')
        self.assertAlmostEqual(c['detached_rate'], 0.5)
        md = '\n'.join(scoreboard.render_caption_relation({'dir': 'batch-z', 'caption_relation': c}))
        self.assertIn('within the caption class', md)


if __name__ == '__main__':
    unittest.main()
