#!/usr/bin/env python3
"""Round 4 · Lane D — tests for tool/corpus/legacy/ (registry, compare, audit, scoreboard).

Hermetic: no poc-out, no packs, no PDFs, no venv — every fixture is synthetic and lives in a tmpdir.
TC_ROOT / LEGACY_OUT are redirected before the modules are imported so nothing can touch real corpus data.

Run:  python3 -m unittest discover -s tool/tests -v
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
_SANDBOX = tempfile.mkdtemp(prefix='lane-d-tests-')
os.environ['TC_ROOT'] = _SANDBOX
os.environ['LEGACY_OUT'] = os.path.join(_SANDBOX, 'legacy')
sys.path.insert(0, os.path.join(HERE, '..', 'corpus'))
sys.path.insert(0, os.path.join(HERE, '..', 'corpus', 'legacy'))
import audit  # noqa: E402
import common  # noqa: E402
import compare  # noqa: E402
import registry  # noqa: E402
import rerun  # noqa: E402
import scoreboard  # noqa: E402


def tearDownModule():
    shutil.rmtree(_SANDBOX, ignore_errors=True)


class SandboxTests(unittest.TestCase):
    def test_modules_read_the_redirected_root_not_the_real_corpus(self):
        """Lane D must never write outside poc-out/round4/legacy/ — the roots come from the environment."""
        self.assertEqual(common.MAIN_ROOT, _SANDBOX)
        self.assertTrue(common.LEGACY_OUT.startswith(_SANDBOX))
        for path in (common.OCR, common.PDF, common.UNITS, common.CURRICULUM, common.SAM_UNITS_DB):
            self.assertTrue(path.startswith(_SANDBOX), path)


class CommonTests(unittest.TestCase):
    def test_wilson_known_values(self):
        self.assertEqual(common.wilson(0, 0), (None, None, None))
        p, lo, hi = common.wilson(39, 55)                       # batch-1 OLD display
        self.assertAlmostEqual(p, 0.7091, places=3)
        self.assertAlmostEqual(lo, 0.579, places=2); self.assertAlmostEqual(hi, 0.812, places=2)
        p, lo, hi = common.wilson(0, 26)                        # batch-1 NEW reading order
        self.assertEqual(p, 0.0); self.assertEqual(lo, 0.0); self.assertGreater(hi, 0.0)
        self.assertLess(hi, 0.2)

    def test_write_new_version_never_overwrites(self):
        d = tempfile.mkdtemp(dir=_SANDBOX)
        p1 = common.write_new_version({'n': 1}, f'{d}/x.json')
        p2 = common.write_new_version({'n': 2}, f'{d}/x.json')
        p3 = common.write_new_version({'n': 3}, f'{d}/x.json')
        self.assertEqual(os.path.basename(p1), 'x.json')
        self.assertEqual(os.path.basename(p2), 'x.v2.json')
        self.assertEqual(os.path.basename(p3), 'x.v3.json')
        self.assertEqual(common.load_json(p1)['n'], 1)          # the first run is still intact

    def test_hashes_are_order_independent_for_dicts_but_not_for_lists(self):
        self.assertEqual(common.sha256_json({'a': 1, 'b': 2}), common.sha256_json({'b': 2, 'a': 1}))
        self.assertNotEqual(common.sha256_json([1, 2]), common.sha256_json([2, 1]))
        self.assertEqual(common.sha256_text(''), common.sha256_text(None))

    def test_book_label_and_subject(self):
        self.assertEqual(common.book_label('04-sgk-toan-4-tap-hai'), 'Toán 4 tập hai')
        self.assertEqual(common.book_label('06-sgk-khoa-hoc-tu-nhien-6'), 'KHTN 6')
        self.assertEqual(common.subject_of('05-sgk-tieng-viet-5-tap-mot'), 'Tiếng Việt')
        self.assertEqual(common.subject_of('06-sgk-khoa-hoc-tu-nhien-6'), 'KHTN')
        self.assertEqual(common.subject_of('05-sgk-khoa-hoc-5'), 'Khoa học')


class RegistryTests(unittest.TestCase):
    def test_lesson_ranges_ends_one_before_the_next_start(self):
        doc = {'lessons': [{'number': 1, 'pageStart': 8}, {'number': 2, 'pageStart': 12}, {'number': 3, 'pageStart': None}]}
        r = registry.lesson_ranges(doc)
        self.assertEqual(r[1], (8, 11))
        self.assertEqual(r[2], (12, None))                       # last ranged lesson has no end
        self.assertEqual(r[3], (None, None))                     # unranged stays unranged, never guessed

    def test_risk_classes_are_derived_from_measured_features_only(self):
        r = registry.risk_classes('04-sgk-toan-4-tap-hai', 'Toán', {80: 'two_col'}, {80: {'formula': True, 'diagram': True}},
                                  [], toc_start=79, toc_end=82, unit_pages=[80], last_lesson=False, has_toan_exercises=True)
        self.assertIn('toan', r); self.assertIn('two_col', r); self.assertIn('order_suspect', r)
        self.assertIn('formula', r); self.assertIn('figure_caption', r); self.assertIn('geometry_rebuilt_expr', r)
        self.assertNotIn('attachment_suspect', r)

    def test_attachment_suspect_for_each_measured_mechanism(self):
        base = dict(pages_layout={}, features={}, units=[], toc_start=10, toc_end=12, unit_pages=[11], last_lesson=False, has_toan_exercises=False)
        def flags(book='06-sgk-khoa-hoc-tu-nhien-6', subject='KHTN', **kw):
            a = dict(base); a.update(kw)
            return registry.risk_classes(book, subject, a['pages_layout'], a['features'], a['units'], a['toc_start'], a['toc_end'], a['unit_pages'], a['last_lesson'], a['has_toan_exercises'])
        self.assertNotIn('attachment_suspect', flags())
        self.assertIn('attachment_suspect', flags(toc_start=None, toc_end=None))            # unranged in the TOC
        self.assertIn('attachment_suspect', flags(last_lesson=True))                        # back cover risk
        self.assertIn('attachment_suspect', flags(book='05-sgk-tieng-viet-5-tap-mot'))      # measured TV5 offset
        self.assertIn('attachment_suspect', flags(unit_pages=[11, 20]))                     # units past the TOC range

    def test_build_registry_on_synthetic_scope(self):
        curr = {'04-sgk-toan-4-tap-hai': dict(sourceDocumentId='04-sgk-toan-4-tap-hai', subject='Toán', grade=4, docType='SGK',
                                              lessons=[{'number': 61, 'title': 'Phép trừ phân số', 'pageStart': 80}, {'number': 62, 'title': 'x', 'pageStart': 84}])}
        reg = registry.build_registry(curr=curr, baseline=[('04-sgk-toan-4-tap-hai', 61)], sam_rows={('04-sgk-toan-4-tap-hai', 62): [dict(id='u1', role='EXERCISE', page=84, sha256='a')]},
                                      packs={}, layout={}, feature_census={}, units_loader=lambda b, units_dir=None: ([], 1), pdf_hash=False)
        self.assertEqual(reg['summary']['in_scope'], 2)                     # 113-baseline ∪ sam-units
        self.assertEqual(reg['summary']['in_113'], 1)
        self.assertEqual(reg['summary']['in_sam_units'], 1)
        self.assertEqual(reg['denominators']['in_scope']['value'], 2)
        self.assertEqual(reg['denominators']['canonical']['value'], 3679)   # historical denominators are never recomputed
        self.assertEqual(reg['denominators']['ranged']['value'], 3381)
        self.assertTrue(all(l['status'] == 'PENDING' for l in reg['lessons']))
        self.assertEqual(reg['lessons'][1]['old']['sam_units_rows'], 1)


class CompareTests(unittest.TestCase):
    def test_overlap_frac_is_the_share_of_a_inside_b(self):
        a = [0.0, 0.0, 0.2, 0.2]
        self.assertAlmostEqual(compare.overlap_frac(a, [0.0, 0.0, 0.4, 0.4]), 1.0)
        self.assertAlmostEqual(compare.overlap_frac(a, [0.1, 0.0, 0.4, 0.4]), 0.5)
        self.assertEqual(compare.overlap_frac(a, [0.5, 0.5, 0.1, 0.1]), 0.0)
        self.assertEqual(compare.overlap_frac(None, a), 0.0)
        self.assertEqual(compare.overlap_frac([0, 0, 0, 0], a), 0.0)

    def test_crosses_column_gap_detects_the_interleave_mechanism(self):
        lines = [dict(x=0.10, w=0.3), dict(x=0.55, w=0.3), dict(x=0.10, w=0.3), dict(x=0.55, w=0.3), dict(x=0.10, w=0.8)]
        self.assertTrue(compare.crosses_column_gap(lines, [0, 1, 2, 3]))     # L R L R → 3 flips
        self.assertFalse(compare.crosses_column_gap(lines, [0, 2, 4]))       # same column + a full-width line
        self.assertFalse(compare.crosses_column_gap(lines, [0, 1]))          # < 3 lines: no claim

    def _new(self, trusted, withheld, figures=(), lesson=61, page=81):
        return dict(tsl=dict(boundary=dict(pages=[page]), blocks=trusted, withheld=withheld),
                    attach_pages={page: dict(lesson=lesson, method='header', kind='page')}, figures={page: list(figures)}, sdm_pages={})

    def _blk(self, i, bbox, text, role='body'):
        return dict(id=i, page=81, bbox=bbox, text=text, role=dict(value=role, confidence=0.9), order=0)

    def test_align_block_statuses(self):
        ob = dict(id='o1', family='samUnits', kind='EXERCISE', page_pdf=81, bbox=[0.1, 0.1, 0.2, 0.1], text='Tính 1/2 - 1/6')
        same = self._new([self._blk('n1', [0.1, 0.1, 0.2, 0.1], 'Tính 1/2 - 1/6', 'question')], [])
        self.assertEqual(compare.align_block(ob, same, 61)['status'], 'now_trusted')
        changed = self._new([self._blk('n1', [0.1, 0.1, 0.2, 0.1], 'hoàn toàn khác hẳn nội dung này', 'question')], [])
        self.assertEqual(compare.align_block(ob, changed, 61)['status'], 'now_trusted_changed')
        held = self._new([], [dict(id='w1', page=81, bbox=[0.1, 0.1, 0.2, 0.1], reasons=['math_guard'], order=0)])
        r = compare.align_block(ob, held, 61)
        self.assertEqual(r['status'], 'now_withheld')
        self.assertEqual(r['withheld_reasons'], ['math_guard'])
        self.assertEqual(compare.align_block(ob, self._new([], []), 61)['status'], 'now_absent')
        mixed = self._new([self._blk('n1', [0.1, 0.1, 0.1, 0.1], 'Tính', 'question')], [dict(id='w1', page=81, bbox=[0.2, 0.1, 0.1, 0.1], reasons=['agree_text'], order=0)])
        self.assertEqual(compare.align_block(ob, mixed, 61)['status'], 'now_mixed')

    def test_align_block_flags_a_page_the_new_pipeline_gives_to_another_lesson(self):
        ob = dict(id='o1', family='samUnits', kind='EXERCISE', page_pdf=81, bbox=[0.1, 0.1, 0.2, 0.1], text='x')
        r = compare.align_block(ob, self._new([], [], lesson=62), 61)
        self.assertEqual(r['status'], 'now_other_lesson')
        self.assertTrue(r['attachment_differs'])

    def test_a_lesson_with_no_tsl_is_withheld_never_guessed(self):
        ob = dict(id='o1', family='samUnits', kind='EXERCISE', page_pdf=81, bbox=[0.1, 0.1, 0.2, 0.1], text='x')
        r = compare.align_block(ob, dict(tsl=None, attach_pages={}, figures={}, sdm_pages={}), 61)
        self.assertEqual(r['status'], 'now_absent')
        self.assertIn('nothing guessed', r['note'])

    def test_geometry_rebuilt_expression_counts_only_on_an_exact_string_hit(self):
        expr = dict(id='e1', family='toanExercises', kind='expr', page_pdf=81, bbox=None, text='19/33 - 3/5')
        hit = self._new([self._blk('n1', [0.1, 0.1, 0.2, 0.1], 'a) 19/33 - 3/5')], [])
        self.assertEqual(compare.align_block(expr, hit, 61)['status'], 'now_trusted')
        miss = self._new([self._blk('n1', [0.1, 0.1, 0.2, 0.1], 'a) 19 33 3 5')], [dict(id='w1', page=81, bbox=[0.5, 0.5, 0.1, 0.1], reasons=['math_guard'], order=0)])
        self.assertEqual(compare.align_block(expr, miss, 61)['status'], 'now_withheld')


def _row(sid, side='NEW', served=True, kind='body', book='04-sgk-toan-4-tap-hai', lesson=61, **kw):
    r = dict(sampleId=sid, side=side, family='legacyNew' if side == 'NEW' else 'samUnits', book=book, lesson=lesson, kind=kind,
             activityId=f'{side}:{book}:L{lesson}', servedAsTrusted=served, subject='Toán', precheck=dict(hasNumbers=True, hasMath=False),
             display_fidelity='OK', teaching_critical_fidelity='NA', reading_order='NA', role_fidelity='OK', lesson_attachment='OK', false_trust='OK',
             display_error_class='', teaching_critical_class='', notes='')
    r.update(kw)
    return r


class AuditTests(unittest.TestCase):
    def test_second_annotation_sample_is_blind_and_deterministic(self):
        rows = [_row(f's-{i:03d}', side='OLD', display_fidelity='WRONG', teaching_critical_fidelity='WRONG', notes='annotator #1 said so',
                     reviewer='annotator #1', layoutFamily='two_col' if i % 2 else 'single') for i in range(40)]
        a, man = audit.sample_second(rows, seed=20260906, n=12)
        b, _ = audit.sample_second(rows, seed=20260906, n=12)
        self.assertEqual([r['sampleId'] for r in a], [r['sampleId'] for r in b])          # deterministic
        c, _ = audit.sample_second(rows, seed=1, n=12)
        self.assertNotEqual([r['sampleId'] for r in a], [r['sampleId'] for r in c])       # a different seed is a different sample
        self.assertEqual(len(a), 12)
        for r in a:
            for f in audit.ANNOT_FIELDS:
                self.assertEqual(r[f], '', f'{f} leaked annotator #1 to annotator #2')     # blank slot, never the verdict
            for f in audit.EXTRA_FIELDS:
                self.assertNotIn(f, r, f'{f} leaked annotator #1 to annotator #2')         # notes / reviewer removed entirely
        self.assertIn('strata', man)

    def test_second_annotation_only_samples_rows_that_were_served(self):
        rows = [_row('s-1', served=True), _row('s-2', served=False)]
        a, _ = audit.sample_second(rows, seed=20260906, n=2)
        self.assertEqual([r['sampleId'] for r in a], ['s-1'])

    def test_kind_quota_sample_takes_only_the_asked_roles_and_marks_itself_within_class(self):
        d = tempfile.mkdtemp(dir=_SANDBOX)
        common.dump_json(dict(batch='b', pipeline='p', lessons=[dict(book='06-sgk-khoa-hoc-tu-nhien-6', lesson=11)]), f'{d}/batch-spec.json')
        blocks = [dict(id=f'x:{i}', page=37, order=i, bbox=[0.1, 0.1 * i, 0.2, 0.05], text=f't{i}',
                       role=dict(value='caption' if i < 5 else 'body', confidence=0.9)) for i in range(9)]
        common.dump_json(dict(boundary=dict(pages=[37]), blocks=blocks, withheld=[]),
                         f'{d}/tcroot/poc-out/trusted-corpus/tc-v2/p/lessons/06-sgk-khoa-hoc-tu-nhien-6/bai-11.tsl.json')
        rows = audit.sample_kind(d, 20260907, ['caption'], per_lesson=8)
        self.assertEqual(len(rows), 5)                                   # only the 5 caption blocks exist
        self.assertTrue(all(r['kind'] == 'caption' for r in rows))
        self.assertEqual(rows[0]['_kindSample']['kinds'], ['caption'])
        self.assertIn('never rates over the batch', rows[0]['_kindSample']['warning'])
        again = audit.sample_kind(d, 20260907, ['caption'], per_lesson=8)
        self.assertEqual([r['tslBlockId'] for r in rows], [r['tslBlockId'] for r in again])
        capped = audit.sample_kind(d, 20260907, ['caption'], per_lesson=2)
        self.assertEqual(len(capped), 2)

    def test_annotate_rejects_a_verdict_outside_the_vocabulary(self):
        rows = [_row('s-1')]
        with self.assertRaises(ValueError):
            audit.annotate(rows, {'s-1': dict(display_fidelity='PROBABLY')}, 'annotator #2')
        out, missing = audit.annotate(rows, {'s-1': dict(display_fidelity='wrong', notes='n')}, 'annotator #2')
        self.assertEqual(out[0]['display_fidelity'], 'WRONG')                              # normalised, not re-judged
        self.assertEqual(out[0]['reviewer'], 'annotator #2')
        self.assertEqual(missing, [])
        out, missing = audit.annotate(rows, {}, 'annotator #2')
        self.assertEqual(missing, ['s-1'])                                                 # an unjudged row is reported, never defaulted

    def test_kappa_matches_a_hand_computed_two_by_two(self):
        # 10 rows: 4 OK/OK, 1 OK/WRONG, 1 WRONG/OK, 4 WRONG/WRONG → po = 0.8, p1w = p2w = 0.5, pe = 0.5, κ = 0.6
        first, second = [], []
        pairs = [('OK', 'OK')] * 4 + [('OK', 'WRONG')] + [('WRONG', 'OK')] + [('WRONG', 'WRONG')] * 4
        for i, (v1, v2) in enumerate(pairs):
            first.append(_row(f'k-{i}', display_fidelity=v1))
            second.append(_row(f'k-{i}', display_fidelity=v2))
        k = audit.kappa(first, second)['display']
        self.assertEqual(k['n_both_judged'], 10)
        self.assertAlmostEqual(k['agreement'], 0.8, places=3)
        self.assertAlmostEqual(k['kappa'], 0.6, places=3)
        self.assertEqual(k['confusion'], {'OK/OK': 4, 'OK/WRONG': 1, 'WRONG/OK': 1, 'WRONG/WRONG': 4})

    def test_kappa_counts_na_disagreement_separately_and_never_as_agreement(self):
        first = [_row('k-0', reading_order='OK'), _row('k-1', reading_order='NA')]
        second = [_row('k-0', reading_order='NA'), _row('k-1', reading_order='NA')]
        k = audit.kappa(first, second)['reading_order']
        self.assertEqual(k['n_both_judged'], 0)
        self.assertEqual(k['na_or_unsure_mismatch'], 1)
        self.assertIsNone(k['kappa'])


class ScoreboardTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(dir=_SANDBOX)
        self.legacy = f'{self.root}/legacy'
        self.registry_path = f'{self.legacy}/registry.json'
        common.dump_json(dict(version='t', scope_definition='test',
                              denominators=dict(canonical=dict(value=3679, definition='c'), ranged=dict(value=3381, definition='r'), in_scope=dict(value=4, definition='s')),
                              summary=dict(in_113=4, in_sam_units=0, both=0, non_canonical=0, unranged=0, by_subject={}, risk={}, old_pack_activities=0, old_units=0),
                              lessons=[dict(book='b', lesson=n) for n in (1, 2, 3, 4)]), self.registry_path)

    def _batch(self, name='batch-1', lessons=(), docs=(), new_rows=(), old_rows=(), started='2026-09-05T09:00:00+00:00'):
        d = f'{self.legacy}/{name}'
        common.dump_json(dict(batch=name, pipeline='legacy-b1', lessons=list(lessons)), f'{d}/batch-spec.json')
        common.dump_json(dict(pipeline='legacy-b1', pages=1, steps=[], started=started), f'{d}/run-manifest.json')
        for doc in docs:
            common.dump_json(doc, f'{d}/lesson-documents/{scoreboard.doc_filename(doc["book"], doc["lesson"])}')
        os.makedirs(f'{d}/audit', exist_ok=True)
        for side, rows in (('new', new_rows), ('old', old_rows)):
            if rows:
                with open(f'{d}/audit/annotated-{side}-1.jsonl', 'w', encoding='utf-8') as f:
                    for r in rows:
                        f.write(json.dumps(r, ensure_ascii=False) + '\n')
        return d

    def _doc(self, lesson, trusted, withheld, book='b'):
        return dict(book=book, lesson=lesson, licence='internalResearchOnly',
                    provenance=dict(sourceability=('FULL' if not withheld else ('NONE' if not trusted else 'PARTIAL')), auditStatus='notAudited', sourceHash='h', pipelineVersion='legacy-b1/sdm-v2',
                                    pagePdfStart=1, pagePdfEnd=2, tslStats=dict(learning_blocks=trusted + withheld, trusted=trusted, withheld=withheld, withheld_by_reason={}, figures=0)))

    def test_states_full_partial_withheld_rejected_pending(self):
        self._batch(lessons=[dict(book='b', lesson=1, risk=[]), dict(book='b', lesson=2, risk=[]), dict(book='b', lesson=3, risk=[])],
                    docs=[self._doc(1, 9, 0), self._doc(2, 9, 3), self._doc(3, 0, 5)])
        sb = scoreboard.build(self.registry_path, self.legacy, f'{self.root}/no-thresholds.json')
        s = sb['scoreboard']
        self.assertEqual(s['total_in_scope'], 4)
        self.assertEqual(s['pending'], 1)                        # lesson 4 is in no batch
        self.assertEqual(s['reprocessed'], 3)
        self.assertEqual(s['full_sourceability'], 1)
        self.assertEqual(s['partial'], 1)
        self.assertEqual(s['withheld'], 1)                       # 0 trusted blocks → nothing servable
        self.assertEqual(s['rejected'], 0)

    def test_a_lesson_the_pipeline_produced_nothing_for_is_rejected_not_missing(self):
        self._batch(lessons=[dict(book='b', lesson=1, risk=[])], docs=[])
        sb = scoreboard.build(self.registry_path, self.legacy, f'{self.root}/none.json')
        self.assertEqual(sb['scoreboard']['rejected'], 1)
        self.assertEqual(sb['scoreboard']['reprocessed'], 0)
        self.assertIn('refused', sb['batches'][0]['lessons'][0]['reason'])

    def test_trusted_and_eligible_are_zero_without_a_founder_threshold_record(self):
        rows = [_row(f'n-{i}', book='b', lesson=1) for i in range(6)]
        self._batch(lessons=[dict(book='b', lesson=1, risk=[])], docs=[self._doc(1, 9, 0)], new_rows=rows)
        sb = scoreboard.build(self.registry_path, self.legacy, f'{self.root}/absent.json')
        self.assertEqual(sb['scoreboard']['independently_audited'], 1)
        self.assertEqual(sb['scoreboard']['full_sourceability'], 1)      # perfect sourceability and a clean audit …
        self.assertEqual(sb['scoreboard']['trusted'], 0)                 # … still is not trust
        self.assertEqual(sb['scoreboard']['eligible_for_teaching'], 0)
        self.assertIn('no Founder threshold record', sb['thresholds']['note'])
        self.assertIn('| trusted | **0** |', scoreboard.render_md(sb))

    def test_a_founder_threshold_record_is_the_only_thing_that_can_raise_trusted(self):
        rows = [_row(f'n-{i}', book='b', lesson=1) for i in range(6)]
        self._batch(lessons=[dict(book='b', lesson=1, risk=[])], docs=[self._doc(1, 9, 0)], new_rows=rows)
        th = f'{self.root}/thresholds.json'
        common.dump_json(dict(max_false_trust_rate=0.05, teachingAuthorised=False), th)
        sb = scoreboard.build(self.registry_path, self.legacy, th)
        self.assertEqual(sb['scoreboard']['trusted'], 1)
        self.assertEqual(sb['scoreboard']['eligible_for_teaching'], 0)   # trust ≠ permission to teach
        common.dump_json(dict(max_false_trust_rate=0.05, teachingAuthorised=True), th.replace('.json', '2.json'))
        sb2 = scoreboard.build(self.registry_path, self.legacy, th.replace('.json', '2.json'))
        self.assertEqual(sb2['scoreboard']['eligible_for_teaching'], 1)

    def test_a_lesson_that_fails_the_threshold_is_not_trusted(self):
        rows = [_row(f'n-{i}', book='b', lesson=1, false_trust='WRONG' if i < 3 else 'OK') for i in range(6)]
        self._batch(lessons=[dict(book='b', lesson=1, risk=[])], docs=[self._doc(1, 9, 0)], new_rows=rows)
        th = f'{self.root}/th2.json'
        common.dump_json(dict(max_false_trust_rate=0.05, teachingAuthorised=True), th)
        sb = scoreboard.build(self.registry_path, self.legacy, th)
        self.assertEqual(sb['scoreboard']['trusted'], 0)

    def test_class_rates_use_served_rows_only_and_exclude_na(self):
        rows = [_row('a', display_fidelity='WRONG'), _row('b', display_fidelity='OK'), _row('c', display_fidelity='NA'),
                _row('d', display_fidelity='WRONG', served=False)]                        # a withheld region is not a served claim
        r = scoreboard.class_rates(rows)
        self.assertEqual((r['display']['wrong'], r['display']['judged'], r['display']['na_or_unsure']), (1, 2, 1))
        self.assertEqual(r['_meta']['served'], 3)
        self.assertEqual(r['_meta']['withheld_rows'], 1)
        self.assertAlmostEqual(r['display']['rate'], 0.5)

    def test_the_two_tag_derived_classes_count_the_rows_the_annotator_tagged(self):
        rows = [_row('a', display_error_class='math_flattened', display_fidelity='WRONG'),
                _row('b', teaching_critical_class='fraction', display_fidelity='WRONG'),
                _row('c', display_error_class='tone_mark', display_fidelity='WRONG'),
                _row('d', kind='caption', display_error_class='figure_text', display_fidelity='WRONG'),
                _row('e', display_fidelity='OK')]
        r = scoreboard.class_rates(rows)
        self.assertEqual(r['formula_number_unit']['wrong'], 2)             # math_flattened + fraction, not tone_mark
        self.assertEqual(r['formula_number_unit']['judged'], 5)
        self.assertEqual(r['figure_caption']['wrong'], 1)
        self.assertEqual(r['figure_caption']['applicable'], 1)

    def test_old_and_new_rates_are_reported_side_by_side_and_never_summed(self):
        old = [_row(f'o-{i}', side='OLD', display_fidelity='WRONG') for i in range(4)]
        new = [_row(f'n-{i}', side='NEW', display_fidelity='OK') for i in range(4)]
        self._batch(lessons=[dict(book='b', lesson=1, risk=[])], docs=[self._doc(1, 4, 0)], new_rows=new, old_rows=old)
        sb = scoreboard.build(self.registry_path, self.legacy, f'{self.root}/none.json')
        b = sb['batches'][0]['old_vs_new']
        self.assertEqual(b['OLD']['display']['rate'], 1.0)
        self.assertEqual(b['NEW']['display']['rate'], 0.0)
        md = scoreboard.render_md(sb)
        self.assertIn('4 / 4 = 1.000', md); self.assertIn('0 / 4 = 0.000', md)
        self.assertIn('REPROCESSED ≠ TRUSTED', md)

    def test_the_newest_version_of_a_versioned_audit_file_is_the_one_scored(self):
        d = self._batch(lessons=[dict(book='b', lesson=1, risk=[])], docs=[self._doc(1, 4, 0)],
                        new_rows=[_row('n-0', display_fidelity='WRONG')])
        os.rename(f'{d}/audit/annotated-new-1.jsonl', f'{d}/audit/annotated-new-20260906.jsonl')
        with open(f'{d}/audit/annotated-new-20260906.v2.jsonl', 'w', encoding='utf-8') as f:
            f.write(json.dumps(_row('n-0', display_fidelity='OK'), ensure_ascii=False) + '\n')
        sb = scoreboard.build(self.registry_path, self.legacy, f'{self.root}/none.json')
        self.assertEqual(sb['batches'][0]['old_vs_new']['NEW']['display']['rate'], 0.0)

    def test_multiple_batches_accumulate_without_double_counting_a_lesson(self):
        self._batch('batch-1', lessons=[dict(book='b', lesson=1, risk=[])], docs=[self._doc(1, 4, 2)])
        self._batch('batch-2', lessons=[dict(book='b', lesson=1, risk=[]), dict(book='b', lesson=2, risk=[])],
                    docs=[self._doc(1, 6, 0), self._doc(2, 3, 1)], started='2026-09-05T10:00:00+00:00')
        sb = scoreboard.build(self.registry_path, self.legacy, f'{self.root}/none.json')
        self.assertEqual(sb['scoreboard']['reprocessed'], 2)              # lesson 1 counted once, in its latest batch
        self.assertEqual(sb['scoreboard']['full_sourceability'], 1)
        self.assertEqual(sb['scoreboard']['pending'], 2)

    def test_a_lessons_state_comes_from_the_latest_run_whatever_the_directory_is_called(self):
        """A re-run supersedes the run it re-ran even when its name sorts first."""
        self._batch('batch-1-zzz-first-run', lessons=[dict(book='b', lesson=1, risk=[])], docs=[self._doc(1, 4, 2)],
                    started='2026-09-05T09:00:00+00:00')
        self._batch('batch-1-aaa-rerun', lessons=[dict(book='b', lesson=1, risk=[])], docs=[self._doc(1, 6, 0)],
                    started='2026-09-05T14:00:00+00:00')
        sb = scoreboard.build(self.registry_path, self.legacy, f'{self.root}/none.json')
        self.assertEqual([b['dir'] for b in sb['batches']], ['batch-1-zzz-first-run', 'batch-1-aaa-rerun'])
        self.assertEqual(sb['scoreboard']['reprocessed'], 1)
        self.assertEqual(sb['scoreboard']['full_sourceability'], 1)       # the later run's FULL, not the earlier PARTIAL
        self.assertEqual(sb['scoreboard']['partial'], 0)


class RerunDeltaTests(unittest.TestCase):
    """A re-run measures whether an improved build rescues the SAME lesson — never a fresh claim smuggled in."""

    def _tsl(self, blocks, withheld=(), page=81):
        return dict(boundary=dict(pages=[page]), blocks=list(blocks), withheld=list(withheld))

    def _blk(self, i, bbox, text, role='body'):
        return dict(id=i, page=81, bbox=bbox, text=text, role=dict(value=role, confidence=0.9), order=0)

    def _row(self, sid='r1', bbox=(0.1, 0.1, 0.2, 0.1), text='Tính (theo mẫu).', page=81, **kw):
        r = _row(sid, kind='body', **kw)
        r.update(pagePdf=page, bbox=list(bbox), text=text, source=dict(kind='tsl', bbox=list(bbox)))
        return r

    def test_identical_text_in_the_same_region_is_the_only_transfer_licence(self):
        row = self._row()
        t = self._tsl([self._blk('n1', [0.1, 0.1, 0.2, 0.1], 'Tính (theo mẫu).')])
        self.assertEqual(rerun.locate(row, t)[0], 'still_trusted_identical')
        t2 = self._tsl([self._blk('n1', [0.1, 0.1, 0.2, 0.1], 'Tính (theo mấu) một cái gì đó khác.')])
        self.assertEqual(rerun.locate(row, t2)[0], 'still_trusted_changed')

    def test_a_withheld_or_unattached_or_missing_region_is_not_served_any_more(self):
        row = self._row()
        held = self._tsl([], [dict(id='w1', page=81, bbox=[0.1, 0.1, 0.2, 0.1], reasons=['agree_tones'], order=0)])
        self.assertEqual(rerun.locate(row, held)[0], 'now_withheld')
        self.assertEqual(rerun.locate(row, self._tsl([], [], page=99))[0], 'now_unattached')
        self.assertEqual(rerun.locate(row, None)[0], 'now_unattached')
        self.assertEqual(rerun.locate(row, self._tsl([]))[0], 'now_absent')

    def test_normalised_text_comparison_ignores_whitespace_but_not_tone_marks(self):
        row = self._row(text='Tính  (theo mẫu).')
        same = self._tsl([self._blk('n1', [0.1, 0.1, 0.2, 0.1], 'Tính (theo mẫu).')])
        self.assertEqual(rerun.locate(row, same)[0], 'still_trusted_identical')
        tone = self._tsl([self._blk('n1', [0.1, 0.1, 0.2, 0.1], 'Tính (theo mấu).')])
        self.assertEqual(rerun.locate(row, tone)[0], 'still_trusted_changed')

    def test_summary_counts_only_regions_no_longer_served_as_rescued(self):
        rows = [dict(sampleId='a', outcome='now_withheld', verdicts=dict(display='WRONG')),
                dict(sampleId='b', outcome='still_trusted_changed', verdicts=dict(display='WRONG')),
                dict(sampleId='c', outcome='still_trusted_identical', verdicts=dict(display='WRONG')),
                dict(sampleId='d', outcome='now_withheld', verdicts=dict(display='OK'))]
        s = rerun.summarise(rows)['display']
        self.assertEqual(s['WRONG']['n'], 3)
        self.assertEqual(s['WRONG']['no_longer_served_as_before'], 1)     # changed text is NOT a rescue
        self.assertEqual(s['OK']['no_longer_served_as_before'], 1)        # collateral is counted, not hidden

    def test_transfer_carries_verdicts_only_for_identical_rows_and_stamps_their_origin(self):
        annotated = [_row('a', display_fidelity='WRONG'), _row('b', display_fidelity='OK'), _row('c', display_fidelity='OK')]
        delta = [dict(sampleId='a', outcome='still_trusted_identical', new_block='n-a', coverage=0.99),
                 dict(sampleId='b', outcome='still_trusted_changed', new_block='n-b', coverage=0.9),
                 dict(sampleId='c', outcome='now_withheld', new_block='w-c', coverage=0.9)]
        t = rerun.transfer_annotations(annotated, delta, 'tc2-p2', 'legacy-b1')
        self.assertEqual([r['sampleId'] for r in t], ['a'])
        self.assertEqual(t[0]['display_fidelity'], 'WRONG')
        self.assertEqual(t[0]['packVersion'], 'tc2-p2')
        self.assertEqual(t[0]['tslBlockId'], 'n-a')
        self.assertEqual(t[0]['verdictTransferredFrom']['pipeline'], 'legacy-b1')
        self.assertIn('identical', t[0]['verdictTransferredFrom']['rule'])

    def test_withheld_regions_are_followed_too_so_over_withholding_can_be_measured(self):
        """A re-run that only counts rescued rows would score a build that withholds everything as perfect."""
        base = [_row('w-1', served=False, kind='body'), _row('w-2', served=False), _row('s-1', served=True)]
        for r in base:
            r.update(pagePdf=81, bbox=[0.1, 0.1, 0.2, 0.1], source=dict(kind='tsl', bbox=[0.1, 0.1, 0.2, 0.1]), text=None)
            r['withheldReasons'] = ['page_feature:color_heavy']
        base[1]['bbox'] = base[1]['source']['bbox'] = [0.5, 0.5, 0.2, 0.1]
        base[2]['text'] = 'x'
        d = tempfile.mkdtemp(dir=_SANDBOX)
        common.dump_json(dict(boundary=dict(pages=[81]),
                              blocks=[dict(id='n1', page=81, bbox=[0.1, 0.1, 0.2, 0.1], text='now served', role=dict(value='body'), order=0)],
                              withheld=[dict(id='w9', page=81, bbox=[0.5, 0.5, 0.2, 0.1], reasons=['agree_text'], order=0)]),
                         f'{d}/tcroot/poc-out/trusted-corpus/tc-v2/p/lessons/04-sgk-toan-4-tap-hai/bai-61.tsl.json')
        rec = rerun.recovered(base, d, 'p')
        self.assertEqual(rec['reviewed'], 2)                                # only the withheld rows, not the served one
        self.assertEqual(rec['now_served'], 1)
        self.assertEqual(rec['outcomes'], {'now_served': 1, 'now_withheld': 1})
        self.assertEqual(rec['by_base_reason']['page_feature:color_heavy'], {'reviewed': 2, 'now_served': 1})
        self.assertNotIn('still_trusted_identical', rec['outcomes'])         # a withheld row served no text to compare

    def test_coverage_reports_the_price_paid_in_withholding(self):
        d = tempfile.mkdtemp(dir=_SANDBOX)
        common.dump_json(dict(pipeline='tc2-p2'), f'{d}/run-manifest.json')
        common.dump_json(dict(book='b', lesson=1, provenance=dict(sourceability='PARTIAL', pagePdfStart=1, pagePdfEnd=2,
                                                                 tslStats=dict(learning_blocks=10, trusted=4, withheld=6, withheld_by_reason={'agree_tones': 6}))),
                         f'{d}/lesson-documents/lesson-b-b1.json')
        c = rerun.coverage(d)['b#1']
        self.assertEqual((c['trusted'], c['withheld']), (4, 6))
        self.assertAlmostEqual(c['served_share'], 0.4)
        self.assertEqual(rerun.pipeline_of(d), 'tc2-p2')


if __name__ == '__main__':
    unittest.main()
