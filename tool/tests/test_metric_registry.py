#!/usr/bin/env python3
"""Round 7 · WS-M — the container-shape regression, and the registry's own guards.

THE INCIDENT, AS A TEST
-----------------------
`toanExercises` is a dict keyed by lesson number whose values are lists of expressions.

    len(d['toanExercises'])                          -> 10   lesson KEYS   (wrong quantity)
    sum(len(v) for v in d['toanExercises'].values()) -> 41   expressions   (right quantity)

Round 6 called `len()`, published «10 toanExercises», and then filed the settled figure
`41 -> 0` as NOT CAPTURED. Round 3 had made the same mistake. **A number that is the right
type and the wrong quantity passes every check that is not a re-derivation.**

So this file does not test that 41 is 41. It tests the two things that generalise:

  1. the `len()`-on-a-container route is BLOCKED — `count_leaves()` raises, rather than
     returning a plausible integer;
  2. the leaf-count route re-derives the right number on a fixture built so that the
     container count, the leaf count and every neighbouring family count are all
     DIFFERENT — so an implementation that confuses any two of them fails.

The fixture is synthetic. No SGK text, no packs, no poc-out. The checks against the real
artefacts live in `python3 tool/metrics/cli.py verify` and skip here when the gitignored
artefacts are absent, because a missing artefact is UNAVAILABLE and never a pass.

Run:  python3 -m unittest discover -s tool/tests -v
"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'metrics'))

import metric_container_lint as container_lint  # noqa: E402
import metric_leaves as L                       # noqa: E402
import metric_registry as R                     # noqa: E402


# --------------------------------------------------------------------------- fixture
# Deliberately adversarial: EVERY count that could be confused with another is a distinct
# number, so no accidental agreement can make a wrong implementation look right.
#
#   toanExercises   3 lesson keys  ·  7 expression leaves
#   tvReadings      5 leaves       tvWritings   2 leaves
#   suSources       1 leaf         khoaExperiments 4 leaves
#   diaMaps         6 leaves       sourceAssets 8 rows / 2 distinct
#
#   leaves, 7 families = 7+5+2+1+4+6+8 = 33
#   leaves, 6 families (no sourceAssets) = 25
#   keys + non-toan leaves (the 217-shaped unit error) = 3 + 26 = 29
def _pack(grade=5):
    return {
        'grade': grade, 'version': 'lesson-index-v2',
        'subjects': {'Toán': [{'sourceDocumentId': 'b1', 'volume': None, 'lessons': [
            {'no': 1, 'title': 'A', 'pageStart': 5},
            {'no': 2, 'title': 'B', 'pageStart': 9},
            {'no': 2, 'title': 'B', 'pageStart': 9},      # a true duplicate row
            {'no': 3, 'title': 'C', 'pageStart': None},
        ]}]},
        'toanExercises': {
            '10': [{'book': 'b1', 'expr': 'e1'}, {'book': 'b1', 'expr': 'e2'},
                   {'book': 'b1', 'expr': 'e3'}, {'book': 'b1', 'expr': 'e4'}],
            '11': [{'book': 'b1', 'expr': 'e5'}, {'book': 'b1', 'expr': 'e6'}],
            '12': [{'book': 'b1', 'expr': 'e7'}],
        },
        'tvReadings': [{'book': 'b1', 'lesson': i} for i in range(5)],
        'tvWritings': [{'book': 'b1', 'lesson': i} for i in range(2)],
        'suSources': [{'book': 'b1', 'lesson': 1}],
        'khoaExperiments': [{'book': 'b1', 'lesson': i} for i in range(4)],
        'diaMaps': [{'book': 'b1', 'lesson': 1} for _ in range(6)],
        'sourceAssets': [{'asset': f'a{i % 2}.png', 'sourceDocumentId': 'b1', 'lesson': 1}
                         for i in range(8)],
        'books': [{'sourceDocumentId': 'b1', 'subject': 'Toán', 'lessonCount': 4}],
        'buildProvenance': {'schema': 1},
    }


def _tmp_root():
    root = tempfile.mkdtemp(prefix='ws-m-metrics-')
    for d in ('tool', 'lib', os.path.join('assets', 'pack'), os.path.join('poc-out', 'units')):
        os.makedirs(os.path.join(root, d), exist_ok=True)
    for g in L.GRADES:
        with open(os.path.join(root, 'assets', 'pack', f'lesson-index-g{g}.json'), 'w') as fh:
            json.dump(_pack(g), fh)
    return root


# --------------------------------------------------------------------------- the regression
class TestContainerShapeRegression(unittest.TestCase):
    """The round-6 incident, in both directions: the wrong route must FAIL, the right one PASS."""

    def setUp(self):
        self.pack = _pack()
        self.container = self.pack['toanExercises']

    def test_len_on_the_container_is_the_wrong_quantity_and_looks_fine(self):
        """The premise of the whole workstream: the wrong number is a plausible integer."""
        self.assertEqual(len(self.container), 3)          # lesson KEYS
        self.assertIsInstance(len(self.container), int)   # right type
        self.assertNotEqual(len(self.container), 7)       # wrong quantity

    def test_count_leaves_REFUSES_a_container(self):
        """A metric may not be taken by len() over a keyed container. This is the guard."""
        with self.assertRaises(L.ContainerShapeError):
            L.count_leaves(self.container)

    def test_count_leaves_refuses_any_mapping_not_just_this_one(self):
        """General, not toanExercises-specific: any mapping handed to a leaf count raises."""
        for mapping in ({}, {'a': []}, {'x': [1, 2], 'y': [3]}, dict(enumerate([[1], [2]]))):
            with self.assertRaises(L.ContainerShapeError):
                L.count_leaves(mapping)

    def test_the_leaf_rederivation_passes(self):
        leaves = list(L.flatten_by_lesson(self.container))
        self.assertEqual(L.count_leaves(leaves), 7)
        self.assertEqual(sum(len(v) for v in self.container.values()), 7)

    def test_container_keys_must_be_asked_for_by_name(self):
        self.assertEqual(L.count_container_keys(self.container), 3)
        with self.assertRaises(L.ContainerShapeError):
            L.count_container_keys([1, 2, 3])

    def test_every_confusable_count_is_a_different_number(self):
        """No accidental agreement may rescue a wrong implementation on this fixture."""
        packs = [(5, self.pack)]
        counts = {
            'toan_leaves': L.count_leaves(list(L.iter_activity_leaves(packs, ('toanExercises',)))),
            'toan_keys': L.count_container_keys(self.container),
            'all_leaves': L.count_leaves(list(L.iter_activity_leaves(packs))),
            'six_family_leaves': L.count_leaves(
                list(L.iter_activity_leaves(packs, L.LEARNER_ACTIVITY_FAMILIES))),
            'lesson_rows': L.count_leaves(list(L.iter_lesson_rows(packs))),
        }
        self.assertEqual(counts, {'toan_leaves': 7, 'toan_keys': 3, 'all_leaves': 33,
                                  'six_family_leaves': 25, 'lesson_rows': 4})
        self.assertEqual(len(set(counts.values())), len(counts), counts)

    def test_a_list_family_declared_as_a_list_but_shipped_as_a_dict_is_refused(self):
        """The next container-shaped metric: a family that CHANGES shape must not be counted."""
        broken = _pack()
        broken['tvReadings'] = {'1': [{'book': 'b1'}], '2': [{'book': 'b1'}]}
        with self.assertRaises(L.ContainerShapeError):
            list(L.iter_activity_leaves([(5, broken)]))
        self.assertTrue(L.check_pack_shapes([(5, broken)]),
                        'check_pack_shapes must report the schema/artefact disagreement')

    def test_declared_shapes_hold_on_a_well_formed_pack(self):
        self.assertEqual(L.check_pack_shapes([(5, _pack())]), [])


class TestShapeTableMatchesTheRepository(unittest.TestCase):
    """WS-M's shape table and the pack tool's FAMILIES table must not drift apart."""

    def test_families_agree_with_legacy_packs_py(self):
        sys.path.insert(0, HERE)
        import _lane_d_sandbox  # noqa: F401  — must precede legacy/common.py
        sys.path.insert(0, os.path.join(HERE, '..', 'ui'))
        sys.path.insert(0, os.path.join(HERE, '..', 'corpus', 'legacy'))
        import packs  # noqa: E402
        self.assertEqual(set(L.ACTIVITY_SHAPES), set(packs.FAMILIES))
        for fam, spec in packs.FAMILIES.items():
            self.assertEqual(L.ACTIVITY_SHAPES[fam], spec['shape'], fam)


# --------------------------------------------------------------------------- the lint
BAD_LEN = "n = len(pack['toanExercises'])\n"
BAD_GET_LEN = "n = len(pack.get('toanExercises') or {})\n"
BAD_ITER = "for e in pack['toanExercises']:\n    use(e)\n"
BAD_ITER_GET = "for e in pack.get('toanExercises') or []:\n    use(e)\n"
BAD_ITER_VAR = ("KEYS = ['toanExercises', 'tvReadings']\n"
                "for key in KEYS:\n"
                "    for e in pack.get(key) or []:\n"
                "        use(e)\n")
BAD_PARTIAL_FLATTEN = ("for key in ('toanExercises', 'tvReadings'):\n"
                       "    xs = pack.get(key) or []\n"
                       "    if isinstance(xs, dict):\n"
                       "        xs = list(xs.values())\n"
                       "    for e in xs:\n"
                       "        use(e)\n")
GOOD_ITEMS = "for lesson, items in pack['toanExercises'].items():\n    for e in items:\n        use(e)\n"
GOOD_FLATTEN = ("for key in ('toanExercises',):\n"
                "    xs = pack.get(key) or []\n"
                "    if isinstance(xs, dict):\n"
                "        xs = [e for v in xs.values() for e in v]\n"
                "    for e in xs:\n"
                "        use(e)\n")
GOOD_LIST_FAMILY = "n = len(pack['tvReadings'])\nfor e in pack['tvWritings']:\n    use(e)\n"


class TestContainerLint(unittest.TestCase):
    """The lint catches the shapes that produced the incident — and stays quiet otherwise."""

    def _rules(self, src):
        return sorted(f.rule for f in container_lint.lint_source(src, 'x.py'))

    def test_flags_len_on_a_container(self):
        self.assertEqual(self._rules(BAD_LEN), ['A-len-on-container'])
        self.assertEqual(self._rules(BAD_GET_LEN), ['A-len-on-container'])

    def test_flags_iterating_a_container(self):
        self.assertEqual(self._rules(BAD_ITER), ['B-iterate-container'])
        self.assertEqual(self._rules(BAD_ITER_GET), ['B-iterate-container'])

    def test_flags_a_family_name_held_in_a_loop_variable(self):
        """A literal-only lint would miss both live occurrences in the repository."""
        self.assertEqual(self._rules(BAD_ITER_VAR), ['B-iterate-container'])

    def test_flags_a_flatten_that_stops_one_level_short(self):
        """`list(d.values())` yields LISTS; treating them as leaves silently counts zero."""
        self.assertEqual(self._rules(BAD_PARTIAL_FLATTEN), ['B-iterate-container'])

    def test_silent_on_correct_usage(self):
        self.assertEqual(self._rules(GOOD_ITEMS), [])
        self.assertEqual(self._rules(GOOD_FLATTEN), [])

    def test_silent_on_list_shaped_families(self):
        """len() over a list family is right, and the lint must not cry wolf about it."""
        self.assertEqual(self._rules(GOOD_LIST_FAMILY), [])

    def test_no_UNTRIAGED_finding_in_the_repository(self):
        """A NEW occurrence of the defect family fails CI. Known ones carry a written verdict."""
        root = os.path.abspath(os.path.join(HERE, '..', '..'))
        findings = container_lint.lint_paths(root)
        new = [str(f) for f in findings if f.key not in container_lint.KNOWN_FINDINGS]
        self.assertEqual(new, [], 'new container-shape finding(s); triage and baseline them')
        for f in findings:
            self.assertTrue(container_lint.KNOWN_FINDINGS[f.key].strip())

    def test_the_baseline_does_not_rot(self):
        """A baselined finding that has disappeared must be MOVED to REPAIRED_FINDINGS.

        This test fired on its first real encounter: the coordinator fixed both live
        findings on the integration branch while WS-M was working, and the baseline was
        left asserting defects that no longer existed. A baseline that outlives its
        defects is a second-order version of the very error this workstream exists for —
        a record that is the right shape and no longer describes anything.
        """
        root = os.path.abspath(os.path.join(HERE, '..', '..'))
        live = {f.key for f in container_lint.lint_paths(root)}
        self.assertEqual(sorted(set(container_lint.KNOWN_FINDINGS) - live), [])

    def test_repaired_findings_stay_repaired(self):
        """A repaired defect that reappears at the same site fails, loudly and by name."""
        root = os.path.abspath(os.path.join(HERE, '..', '..'))
        live = {f.key for f in container_lint.lint_paths(root)}
        returned = sorted(set(container_lint.REPAIRED_FINDINGS) & live)
        self.assertEqual(returned, [], 'a repaired container-shape defect has returned')

    def test_a_repair_records_what_it_means_for_numbers_published_earlier(self):
        """A REPAIR IS ALSO A CHANGE TO WHAT OLD NUMBERS MEAN.

        Output produced by broken code cannot be regenerated by the fixed code. Nothing
        published is rewritten, but the gap must be findable at the code, or a reader who
        re-runs a script and gets different numbers than the report in their hand is left
        to infer a contradiction that nobody recorded.
        """
        for key, r in container_lint.REPAIRED_FINDINGS.items():
            for field in container_lint.REPAIRED_FIELDS:
                self.assertTrue(r.get(field, '').strip(), f'{key} is missing {field}')
            self.assertIn('docs/', r['correction_recorded_in'],
                          f'{key} must name where the correction is recorded')

    def test_a_finding_is_never_both_live_and_repaired_in_the_record(self):
        self.assertEqual(set(container_lint.KNOWN_FINDINGS)
                         & set(container_lint.REPAIRED_FINDINGS), set())


# --------------------------------------------------------------------------- the registry
class TestRegistryContract(unittest.TestCase):
    """Every metric in the registry carries the nine fields the rule demands."""

    FIELDS = ('semantic_quantity', 'unit', 'leaf_population', 'grouping_key', 'denominator',
              'aggregation', 'exclusions', 'source_artefact', 'rederivation_command')

    def test_ids_are_unique(self):
        ids = [m.id for m in R.METRICS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_metric_is_fully_specified(self):
        for m in R.METRICS:
            for field in self.FIELDS:
                value = getattr(m, field)
                self.assertTrue(isinstance(value, str) and value.strip(),
                                f'{m.id}.{field} is empty — the rule admits no blank field')
            self.assertTrue(callable(m.derive), m.id)
            self.assertIn(m.id, m.rederivation_command,
                          f'{m.id} re-derivation command must name the metric it re-derives')

    def test_every_metric_has_a_recorded_value(self):
        """An unrecorded metric cannot be verified, so it cannot be relied on."""
        for m in R.METRICS:
            self.assertIsInstance(m.recorded_value, int, f'{m.id} has no recorded value')

    def test_total_activities_is_deprecated_and_stays_deprecated(self):
        d = R.DEPRECATED_BY_ID['TOTAL_ACTIVITIES']
        self.assertEqual(d.verdict, 'DEPRECATED')
        self.assertNotIn('TOTAL_ACTIVITIES', R.METRICS_BY_ID)

    def test_the_three_published_totals_are_all_accounted_for(self):
        for value in (248, 217, 161):
            self.assertTrue(any(d.published_value == value for d in R.DEPRECATED),
                            f'{value} was published and has no verdict in the registry')

    def test_deprecations_are_explained_not_merely_listed(self):
        for d in R.DEPRECATED:
            self.assertIn(d.verdict, ('DEPRECATED', 'SUPERSEDED', 'RENAMED'), d.id)
            for field in ('published_as', 'what_it_actually_is', 'reason', 'replacement'):
                self.assertTrue(getattr(d, field).strip(), f'{d.id}.{field}')


class TestRegistryRederivesOnAFixture(unittest.TestCase):
    """The engine itself is exercised without touching a real, gitignored artefact."""

    def setUp(self):
        self.root = _tmp_root()
        self.ctx = R.Ctx(self.root)

    def test_derivations_run_and_agree_with_the_fixture(self):
        got = {m.id: m.derive(self.ctx) for m in R.METRICS
               if 'UPSTREAM' not in m.id}
        self.assertEqual(got['TOAN_EXERCISE_LEAF_COUNT'], 12 * 7)
        self.assertEqual(got['LESSON_KEY_COUNT'], 12 * 3)
        self.assertEqual(got['ACTIVITY_LEAF_COUNT'], 12 * 33)
        self.assertEqual(got['LEARNER_ACTIVITY_LEAF_COUNT'], 12 * 25)
        self.assertEqual(got['SOURCE_ASSET_ROW_COUNT'], 12 * 8)
        self.assertEqual(got['DISTINCT_SOURCE_ASSET_COUNT'], 2)
        self.assertEqual(got['ACTIVITY_FAMILY_COUNT'], 7)
        self.assertEqual(got['ACTIVITY_FAMILY_NONEMPTY_COUNT'], 7)
        self.assertEqual(got['SOURCE_LESSON_ROW_COUNT'], 12 * 4)
        self.assertEqual(got['CANONICAL_LESSON_IDENTITY_COUNT'], 3)   # 12 packs share b1's rows
        self.assertEqual(got['RANGED_LESSON_ROW_COUNT'], 12 * 3)
        self.assertEqual(got['LESSON_PAIR_KEY_COUNT'], 3)
        self.assertEqual(got['TRUE_DUPLICATE_EXCESS_ROWS'], 12 * 4 - 3)

    def test_a_missing_artefact_is_UNAVAILABLE_and_never_zero(self):
        os.remove(os.path.join(self.root, 'assets', 'pack', 'lesson-index-g7.json'))
        with self.assertRaises(L.ArtefactMissing):
            R.Ctx(self.root).packs
        with self.assertRaises(L.ArtefactMissing):
            list(L.iter_upstream_toan_exercises(self.root))

    def test_the_217_shaped_unit_error_reconstructs_and_is_still_meaningless(self):
        """Rows + keys is arithmetically reproducible and semantically empty."""
        with open(os.path.join(self.root, 'poc-out', 'units', 'exercise-case-map.json'), 'w') as fh:
            json.dump([{'book': 'x-sgk-toan-5', 'lesson': 10, 'status': 'INFERRED'},
                       {'book': 'x-sgk-toan-5', 'lesson': 10, 'status': 'INFERRED'},
                       {'book': 'x-sgk-toan-5', 'lesson': 11, 'status': 'INFERRED'}], fh)
        ctx = R.Ctx(self.root)
        rows = R.DEPRECATED_BY_ID['ACTIVITY_TOTAL_248'].reconstruct(ctx)
        mixed = R.DEPRECATED_BY_ID['ACTIVITY_TOTAL_217'].reconstruct(ctx)
        self.assertEqual(rows, 12 * 33 + 3)     # leaves + leaves — a quantity
        self.assertEqual(mixed, 12 * 33 + 2)    # leaves + KEYS   — not a quantity
        self.assertNotEqual(rows, mixed)


class TestRealArtefacts(unittest.TestCase):
    """The recorded values, against the real gitignored artefacts when they are present.

    SKIPPED, never passed, when they are not: `assets/pack/` and `poc-out/` are SGK
    derivative works and do not travel with the repository. The full check is
    `python3 tool/metrics/cli.py verify`, which exits non-zero on UNAVAILABLE.
    """

    def setUp(self):
        self.root = os.path.abspath(os.path.join(HERE, '..', '..'))
        if not os.path.exists(L.pack_path(1, self.root)):
            self.skipTest('assets/pack/ not on this machine (gitignored SGK derivative)')
        self.ctx = R.Ctx(self.root)

    def test_recorded_values_rederive(self):
        for m in R.METRICS:
            if 'UPSTREAM' in m.id and not os.path.exists(L.exercise_case_map_path(self.root)):
                continue
            with self.subTest(metric=m.id):
                self.assertEqual(m.derive(self.ctx), m.recorded_value)

    def test_pack_shapes_hold(self):
        self.assertEqual(L.check_pack_shapes(self.ctx.packs), [])

    def test_the_toan_exercise_zero_is_a_decision_not_a_loss(self):
        """0 shipped, 41 upstream, 41 refused. The zero must never read as «nothing existed»."""
        if not os.path.exists(L.exercise_case_map_path(self.root)):
            self.skipTest('poc-out/ not on this machine (gitignored SGK derivative)')
        ctx = self.ctx
        shipped = R.METRICS_BY_ID['TOAN_EXERCISE_LEAF_COUNT'].derive(ctx)
        upstream = R.METRICS_BY_ID['TOAN_EXERCISE_UPSTREAM_LEAF_COUNT'].derive(ctx)
        refused = R.METRICS_BY_ID['TOAN_EXERCISE_UPSTREAM_NON_VERBATIM_COUNT'].derive(ctx)
        self.assertEqual(shipped, 0)
        self.assertEqual(upstream, refused)
        self.assertEqual(upstream - refused, shipped)

    def test_the_four_lesson_denominators_are_one_population(self):
        """3,679 / 3,650 / 3,381 / 3,240 are the same rows under four grouping keys."""
        ctx = self.ctx
        rows = R.METRICS_BY_ID['SOURCE_LESSON_ROW_COUNT'].derive(ctx)
        canonical = R.METRICS_BY_ID['CANONICAL_LESSON_IDENTITY_COUNT'].derive(ctx)
        excess = R.METRICS_BY_ID['TRUE_DUPLICATE_EXCESS_ROWS'].derive(ctx)
        pairs = R.METRICS_BY_ID['LESSON_PAIR_KEY_COUNT'].derive(ctx)
        ranged = R.METRICS_BY_ID['RANGED_LESSON_ROW_COUNT'].derive(ctx)
        self.assertEqual(rows - excess, canonical)
        self.assertLessEqual(pairs, canonical)
        self.assertLessEqual(ranged, rows)

    def test_the_published_248_reconstructs_exactly(self):
        if not os.path.exists(L.exercise_case_map_path(self.root)):
            self.skipTest('poc-out/ not on this machine (gitignored SGK derivative)')
        d = R.DEPRECATED_BY_ID['ACTIVITY_TOTAL_248']
        self.assertEqual(d.reconstruct(self.ctx), 248)

    def test_the_published_217_and_161_reconstruct_exactly(self):
        """Both reproduce — which is the point: reproducibility is not meaning."""
        if not os.path.exists(L.exercise_case_map_path(self.root)):
            self.skipTest('poc-out/ not on this machine (gitignored SGK derivative)')
        self.assertEqual(R.DEPRECATED_BY_ID['ACTIVITY_TOTAL_217'].reconstruct(self.ctx), 217)
        self.assertEqual(R.DEPRECATED_BY_ID['ACTIVITY_TOTAL_161'].reconstruct(self.ctx), 161)


# --------------------------------------------------------------------------- ledger population
class TestLedgerPopulationIsNamed(unittest.TestCase):
    """A TOTAL WITHOUT ITS POPULATION IS NOT A METRIC.

    Round 6 published two different accounting totals over the same batch dirs — §7's
    «29 lesson ledgers · 1 878 input regions» and §9's withheld counts — and
    `ledger.py audit` had no way to say which it was computing. It always read
    `batch-spec.json`, so the documented command reproduced §9's population and not §7's.
    Both sets of numbers are right; only the re-derivation path was ambiguous.

    These tests pin the selector, and pin `spec` as the default so nothing that already
    ran changes its answer.
    """

    BOOK, PIPE, PAGE = 'b-sgk-x', 'test-pipe', 81

    def setUp(self):
        sys.path.insert(0, os.path.join(HERE, '..', 'corpus', 'accounting'))
        import ledger                                          # noqa: E402
        self.ledger = ledger
        self.tmp = tempfile.mkdtemp(prefix='ws-m-ledger-')
        root = os.path.join(self.tmp, 'tcroot', 'poc-out', 'trusted-corpus', 'tc-v2', self.PIPE)
        os.makedirs(os.path.join(root, 'sdm', self.BOOK))
        os.makedirs(os.path.join(root, 'lessons', self.BOOK))
        # Lesson 1 is in the spec; lesson 2 is a neighbour the pipeline also produced.
        with open(os.path.join(self.tmp, 'batch-spec.json'), 'w') as fh:
            json.dump({'batch': 't', 'lessons': [{'book': self.BOOK, 'lesson': 1}]}, fh)
        for lesson, page in ((1, self.PAGE), (2, self.PAGE + 1)):
            bid = f'{self.BOOK}:p{page:03d}:{self.PIPE}:000'
            with open(os.path.join(root, 'sdm', self.BOOK, f'p{page:03d}.sdm.json'), 'w') as fh:
                json.dump({'book': self.BOOK, 'page': page,
                           'blocks': [{'id': bid, 'order': 0, 'role': {'value': 'body'},
                                       'text': 'x'}]}, fh)
            with open(os.path.join(root, 'lessons', self.BOOK, f'bai-{lesson:02d}.tsl.json'), 'w') as fh:
                json.dump({'book': self.BOOK, 'lesson': lesson, 'boundary': {'pages': [page]},
                           'blocks': [{'id': bid}], 'withheld': [], 'excluded': []}, fh)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_the_two_populations_are_different_and_both_reachable(self):
        spec = self.ledger.batch_lessons(self.tmp, self.PIPE, self.ledger.SPEC)
        every = self.ledger.batch_lessons(self.tmp, self.PIPE, self.ledger.ALL_TSL)
        self.assertEqual(spec, [(self.BOOK, 1)])
        self.assertEqual(every, [(self.BOOK, 1), (self.BOOK, 2)])
        self.assertNotEqual(spec, every)

    def test_the_default_is_still_the_spec_so_no_existing_run_changes_answer(self):
        self.assertEqual(self.ledger.batch_lessons(self.tmp, self.PIPE),
                         self.ledger.batch_lessons(self.tmp, self.PIPE, self.ledger.SPEC))

    def test_the_output_records_which_population_produced_it(self):
        for population, lessons, regions in ((self.ledger.SPEC, 1, 1), (self.ledger.ALL_TSL, 2, 2)):
            out = self.ledger.ledger_batch(self.tmp, self.PIPE, (), population)
            self.assertEqual(out['population'], population)
            self.assertEqual(out['lessons'], lessons)
            self.assertEqual(out['inputSourceRegions'], regions)

    def test_an_unnamed_population_is_refused_rather_than_guessed(self):
        with self.assertRaises(ValueError):
            self.ledger.batch_lessons(self.tmp, self.PIPE, 'whatever-looks-right')


if __name__ == '__main__':
    unittest.main()
