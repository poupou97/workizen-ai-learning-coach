#!/usr/bin/env python3
"""Round 7 · WS-M — the METRIC DEFINITION REGISTRY.

    NO IMPORTANT DERIVED METRIC IS ACCEPTED UNLESS IT CAN BE RE-DERIVED FROM LEAF RECORDS.

Every entry records, without exception:

    semantic quantity · unit · leaf population · grouping key · denominator ·
    aggregation function · exclusions · source artefact/version · re-derivation command

and carries a runnable `derive` that a reviewer can execute:

    python3 tool/metrics/cli.py verify

A metric is NOT accepted because its type is correct, its range looks plausible, CI is
green, or a neighbouring metric agrees. It is accepted when it re-derives.

DEPRECATED entries stay in the file. A number that was published and is wrong is deleted
from nothing: it is marked, explained, and left where a reader who meets it can find out
what happened to it.
"""
import collections
import dataclasses
import typing

import leaves as L

MEASURED_ON = '2026-09-06'

# ---------------------------------------------------------------- record types
ABSOLUTE = 'NONE — absolute count, not a share'


@dataclasses.dataclass(frozen=True)
class Metric:
    id: str
    semantic_quantity: str
    unit: str
    leaf_population: str
    grouping_key: str
    denominator: str
    aggregation: str
    exclusions: str
    source_artefact: str
    rederivation_command: str
    derive: typing.Callable
    recorded_value: typing.Optional[int] = None
    measured_on: str = MEASURED_ON
    note: str = ''


@dataclasses.dataclass(frozen=True)
class Deprecated:
    id: str
    published_value: typing.Optional[int]
    published_as: str
    what_it_actually_is: str
    verdict: str            # DEPRECATED | SUPERSEDED | RENAMED
    reason: str
    replacement: str
    reconstruction: str = ''
    reconstruct: typing.Optional[typing.Callable] = None


# ---------------------------------------------------------------- context
class Ctx:
    """Lazily loaded artefacts. An artefact that is absent yields UNAVAILABLE, never 0."""

    def __init__(self, root=None):
        self.root = root or L.repo_root()
        self._packs = None
        self._upstream = None

    @property
    def packs(self):
        if self._packs is None:
            self._packs = L.load_packs(self.root)
        return self._packs

    @property
    def upstream_toan(self):
        if self._upstream is None:
            self._upstream = list(L.iter_upstream_toan_exercises(self.root))
        return self._upstream


# ---------------------------------------------------------------- derivations
def _toan_leaves(c):
    return L.count_leaves([x for x in L.iter_activity_leaves(c.packs, ('toanExercises',))])


def _toan_container_keys(c):
    return sum(L.count_container_keys(p.get('toanExercises') or {}) for _g, p in c.packs)


def _lesson_container_keys(c):
    total = 0
    for _g, pack in c.packs:
        for fam, shape in L.ACTIVITY_SHAPES.items():
            if shape == 'by_lesson':
                total += L.count_container_keys(pack.get(fam) or {})
    return total


def _activity_leaves(c):
    return L.count_leaves(list(L.iter_activity_leaves(c.packs)))


def _learner_activity_leaves(c):
    return L.count_leaves(list(L.iter_activity_leaves(c.packs, L.LEARNER_ACTIVITY_FAMILIES)))


def _source_asset_rows(c):
    return L.count_leaves([x for x in L.iter_activity_leaves(c.packs, ('sourceAssets',))])


def _distinct_source_assets(c):
    return len({(leaf.get('asset'), leaf.get('sourceDocumentId'))
                for *_h, leaf in L.iter_activity_leaves(c.packs, ('sourceAssets',))})


def _activity_family_count(_c):
    return len(L.ACTIVITY_SHAPES)


def _activity_family_nonempty(c):
    fams = collections.Counter(fam for _g, fam, *_r in L.iter_activity_leaves(c.packs))
    return sum(1 for f in L.ACTIVITY_SHAPES if fams[f] > 0)


def _upstream_toan_leaves(c):
    return L.count_leaves(c.upstream_toan)


def _upstream_toan_keys(c):
    return len({(book, lesson) for book, lesson, *_r in c.upstream_toan})


def _upstream_toan_non_verbatim(c):
    verbatim = ('', 'VERBATIM', 'PRINTED', 'ORIGINAL')
    return sum(1 for _b, _l, status, *_r in c.upstream_toan if status not in verbatim)


def _lesson_rows(c):
    return L.count_leaves(list(L.iter_lesson_rows(c.packs)))


def _canonical_lesson_identities(c):
    return len(set(L.iter_lesson_rows(c.packs)))


def _ranged_lesson_rows(c):
    return sum(1 for _d, _n, page_start, _t in L.iter_lesson_rows(c.packs) if page_start is not None)


def _lesson_pair_keys(c):
    return len({(doc, no) for doc, no, _p, _t in L.iter_lesson_rows(c.packs)})


def _true_duplicate_excess_rows(c):
    counts = collections.Counter(L.iter_lesson_rows(c.packs))
    return sum(v - 1 for v in counts.values() if v > 1)


def _pack_book_rows(c):
    return L.count_leaves(list(L.iter_book_rows(c.packs)))


def _distinct_pack_books(c):
    return len({doc for _g, doc in L.iter_book_rows(c.packs)})


# ---------------------------------------------------------------- the registry
PACK_ARTEFACT = ('assets/pack/lesson-index-g{1..12}.json (gitignored SGK derivative); version '
                 'field `lesson-index-v2`, build identity in buildProvenance.contentHash / '
                 'builderVersion / builtAt')
UPSTREAM_ARTEFACT = ('poc-out/units/exercise-case-map.json (gitignored SGK derivative); the '
                     'upstream record set build_lesson_index.py reads to emit toanExercises')

METRICS = [
    # ---------------------------------------------------------------- the incident
    Metric(
        id='TOAN_EXERCISE_LEAF_COUNT',
        semantic_quantity='Toán exercise expressions SHIPPED in the packs',
        unit='expression (leaf record)',
        leaf_population='every element of every list under pack.toanExercises[lessonNo]',
        grouping_key='none — leaf rows are counted, not grouped',
        denominator=ABSOLUTE,
        aggregation='count of leaf records',
        exclusions=('upstream records the builder failed closed on (non-VERBATIM status, '
                    'Founder §3) never enter the pack and are therefore not counted here'),
        source_artefact=PACK_ARTEFACT,
        rederivation_command="python3 tool/metrics/cli.py verify --only TOAN_EXERCISE_LEAF_COUNT",
        derive=_toan_leaves,
        recorded_value=0,
        note=('THE TRUTHFUL ZERO. `len(pack["toanExercises"])` is NOT this metric: it counts '
              'lesson keys. Round 6 reported that container count (10) as an expression count '
              'against a true 41, then filed the settled figure 41 -> 0 as NOT CAPTURED.'),
    ),
    Metric(
        id='LESSON_KEY_COUNT',
        semantic_quantity=('KEYS of the by-lesson activity containers in the packs — the '
                           'quantity `len()` returns, named so it can never again be mistaken '
                           'for an item count'),
        unit='container key (NOT an item; NOT a lesson identity)',
        leaf_population=('the key set of pack.toanExercises — the only family whose declared '
                         'shape is by_lesson'),
        grouping_key='lesson number as a string, WITHIN one grade pack',
        denominator=ABSOLUTE,
        aggregation='count of mapping keys, summed over the 12 packs',
        exclusions=('books — the key is the lesson NUMBER only, so two books in one grade that '
                    'both print «Bài 6» would collapse into one key. No collision exists in the '
                    'measured data (10 keys = 10 distinct (book, lesson) pairs upstream), which '
                    'is exactly the kind of accidental agreement that hides a grouping-key bug'),
        source_artefact=PACK_ARTEFACT,
        rederivation_command="python3 tool/metrics/cli.py verify --only LESSON_KEY_COUNT",
        derive=_lesson_container_keys,
        recorded_value=0,
        note=('NEVER PUBLISH THIS AS AN ACTIVITY COUNT. It is defined here so that the number '
              'has a name and a unit of its own; a report that means expressions must cite '
              'TOAN_EXERCISE_LEAF_COUNT.'),
    ),
    Metric(
        id='TOAN_EXERCISE_UPSTREAM_LEAF_COUNT',
        semantic_quantity='Toán exercise records available UPSTREAM, before the builder fails closed',
        unit='exercise record (leaf)',
        leaf_population='rows of exercise-case-map.json with a lesson and a Toán book',
        grouping_key='none — leaf rows',
        denominator=ABSOLUTE,
        aggregation='count of leaf records',
        exclusions='rows with lesson=None; non-Toán books (none present in the measured artefact)',
        source_artefact=UPSTREAM_ARTEFACT,
        rederivation_command="python3 tool/metrics/cli.py verify --only TOAN_EXERCISE_UPSTREAM_LEAF_COUNT",
        derive=_upstream_toan_leaves,
        recorded_value=41,
        note='The «41» of «41 -> 0». PROVEN by direct count of the upstream leaf records.',
    ),
    Metric(
        id='TOAN_EXERCISE_UPSTREAM_NON_VERBATIM_COUNT',
        semantic_quantity='upstream Toán records the builder refuses to emit (Founder §3 fail-closed)',
        unit='exercise record (leaf)',
        leaf_population='rows of exercise-case-map.json with a lesson and a Toán book',
        grouping_key='none — leaf rows',
        denominator=('TOAN_EXERCISE_UPSTREAM_LEAF_COUNT = 41; the share is 41/41 = 1.000 and must '
                     'be written with that denominator'),
        aggregation="count where status not in ('', VERBATIM, PRINTED, ORIGINAL)",
        exclusions='none',
        source_artefact=UPSTREAM_ARTEFACT,
        rederivation_command="python3 tool/metrics/cli.py verify --only TOAN_EXERCISE_UPSTREAM_NON_VERBATIM_COUNT",
        derive=_upstream_toan_non_verbatim,
        recorded_value=41,
        note=('All 41 carry status INFERRED, method geometric-fraction-rebuild-v1. This is why '
              'TOAN_EXERCISE_LEAF_COUNT is 0 and not 41: the zero is a decision, not a loss.'),
    ),
    Metric(
        id='TOAN_EXERCISE_UPSTREAM_LESSON_KEY_COUNT',
        semantic_quantity='distinct lessons the 41 upstream records belong to',
        unit='lesson (book, lessonNo)',
        leaf_population='rows of exercise-case-map.json with a lesson and a Toán book',
        grouping_key='(book, lessonNo) — the BOOK is part of the key, unlike the pack container',
        denominator=ABSOLUTE,
        aggregation='count of distinct groups',
        exclusions='none',
        source_artefact=UPSTREAM_ARTEFACT,
        rederivation_command="python3 tool/metrics/cli.py verify --only TOAN_EXERCISE_UPSTREAM_LESSON_KEY_COUNT",
        derive=_upstream_toan_keys,
        recorded_value=10,
        note=('The «10 lessons whose exercise list is now empty» of the round-5 scoreboard. It '
              'equals the pack container-key count by accident, not by construction: three '
              'books contribute, and no two share a lesson number.'),
    ),

    # ---------------------------------------------------------------- activities
    Metric(
        id='ACTIVITY_LEAF_COUNT',
        semantic_quantity='activity leaf rows shipped in the packs, all seven families',
        unit='activity row (leaf record)',
        leaf_population=('every element of every activity family: the 6 list families flat, '
                         'plus toanExercises flattened out of its by-lesson container'),
        grouping_key='none — leaf rows are counted, not grouped or de-duplicated',
        denominator=ABSOLUTE,
        aggregation='count of leaf records over 12 packs x 7 families',
        exclusions=('`subjects` and `books` (catalogue, not activities). Rows are NOT '
                    'de-duplicated: the 36 sourceAssets rows are 3 distinct assets repeated in '
                    'all 12 grade packs — see DISTINCT_SOURCE_ASSET_COUNT'),
        source_artefact=PACK_ARTEFACT,
        rederivation_command="python3 tool/metrics/cli.py verify --only ACTIVITY_LEAF_COUNT",
        derive=_activity_leaves,
        recorded_value=207,
        note=('This is the metric the published lineage 248 -> 207 belongs to; 248 was its value '
              'before the §3 fail-closed change removed the 41 INFERRED expressions. '
              'Independently reproduced by tool/corpus/legacy/packs.py pack_metrics() '
              "['activitiesTotal'], which is shape-aware and agrees exactly."),
    ),
    Metric(
        id='LEARNER_ACTIVITY_LEAF_COUNT',
        semantic_quantity='activity leaf rows that ask a learner to DO something (six families)',
        unit='activity row (leaf record)',
        leaf_population='the same leaf rows, minus the sourceAssets family',
        grouping_key='none — leaf rows',
        denominator=ABSOLUTE,
        aggregation='count of leaf records over 12 packs x 6 families',
        exclusions=('sourceAssets — a cropped picture with provenance is a source object, not a '
                    'task. This is the family set of tool/corpus/readiness_matrix.py ACT_KEYS '
                    'and tool/research/lane_c PACK_KEYS'),
        source_artefact=PACK_ARTEFACT,
        rederivation_command="python3 tool/metrics/cli.py verify --only LEARNER_ACTIVITY_LEAF_COUNT",
        derive=_learner_activity_leaves,
        recorded_value=171,
        note=('The repository already held TWO family sets for the word «activity» — seven in '
              'packs.py, six in readiness_matrix.py — differing by 36 rows. Both are recorded '
              'here rather than one being chosen silently.'),
    ),
    Metric(
        id='SOURCE_ASSET_ROW_COUNT',
        semantic_quantity='sourceAssets rows across the 12 packs',
        unit='row',
        leaf_population='pack.sourceAssets elements',
        grouping_key='none — leaf rows',
        denominator=ABSOLUTE,
        aggregation='count of leaf records',
        exclusions='none',
        source_artefact=PACK_ARTEFACT,
        rederivation_command="python3 tool/metrics/cli.py verify --only SOURCE_ASSET_ROW_COUNT",
        derive=_source_asset_rows,
        recorded_value=36,
    ),
    Metric(
        id='DISTINCT_SOURCE_ASSET_COUNT',
        semantic_quantity='DISTINCT source assets that exist in the corpus',
        unit='asset',
        leaf_population='pack.sourceAssets elements',
        grouping_key='(asset, sourceDocumentId)',
        denominator=ABSOLUTE,
        aggregation='count of distinct groups',
        exclusions='none',
        source_artefact=PACK_ARTEFACT,
        rederivation_command="python3 tool/metrics/cli.py verify --only DISTINCT_SOURCE_ASSET_COUNT",
        derive=_distinct_source_assets,
        recorded_value=3,
        note=('36 rows, 3 assets: every grade pack carries the SAME three grade-5 crops. Only in '
              'grade 5 do they pass the app-side grade filter (`sourceAssetsFor`), so a count of '
              '36 overstates by 33 what any learner can reach. VISIBLE != SERVED, in a metric.'),
    ),
    Metric(
        id='ACTIVITY_FAMILY_COUNT',
        semantic_quantity='activity families the pack schema declares',
        unit='family',
        leaf_population='the keys of ACTIVITY_SHAPES / packs.py FAMILIES',
        grouping_key='family name',
        denominator=ABSOLUTE,
        aggregation='count of declared families',
        exclusions=('`samUnits` — it appears in tool/corpus/ft_audit_sample.py FAMILIES (8) but '
                    'is not a pack key; `subjects`/`books` are catalogue, not activities'),
        source_artefact='tool/metrics/leaves.py ACTIVITY_SHAPES, asserted equal to packs.py FAMILIES',
        rederivation_command="python3 tool/metrics/cli.py verify --only ACTIVITY_FAMILY_COUNT",
        derive=_activity_family_count,
        recorded_value=7,
        note='Three different family sets exist in the repo: 7 (packs.py), 6 (readiness_matrix.py, '
             'lane_c), 8 (ft_audit_sample.py, includes the non-pack samUnits). 7 is the schema.',
    ),
    Metric(
        id='ACTIVITY_FAMILY_NONEMPTY_COUNT',
        semantic_quantity='activity families that currently hold at least one leaf row',
        unit='family',
        leaf_population='activity leaf rows',
        grouping_key='family name',
        denominator='ACTIVITY_FAMILY_COUNT = 7',
        aggregation='count of families with count > 0',
        exclusions='none',
        source_artefact=PACK_ARTEFACT,
        rederivation_command="python3 tool/metrics/cli.py verify --only ACTIVITY_FAMILY_NONEMPTY_COUNT",
        derive=_activity_family_nonempty,
        recorded_value=6,
        note='6 of 7 — toanExercises is the empty one, and it is empty on purpose.',
    ),

    # ---------------------------------------------------------------- lesson denominators
    Metric(
        id='SOURCE_LESSON_ROW_COUNT',
        semantic_quantity='SourceLessonRecords — one row per TOC entry as parsed from one book',
        unit='TOC row',
        leaf_population='pack.subjects[*][*].lessons[*] across the 12 packs',
        grouping_key='none — rows are counted',
        denominator=ABSOLUTE,
        aggregation='count of leaf rows',
        exclusions=('63 of 301 SGK documents contribute zero rows (structureStatus NO_TOC); this '
                    'is «lessons in the 238 books with a parseable TOC», not «all SGK lessons»'),
        source_artefact=PACK_ARTEFACT,
        rederivation_command="python3 tool/metrics/cli.py verify --only SOURCE_LESSON_ROW_COUNT",
        derive=_lesson_rows,
        recorded_value=3679,
        note=('HISTORICAL BASELINE ONLY per the standing rule. Re-derived here from the packs, an '
              'artefact independent of WS-A\'s all-lessons.csv, and agreeing exactly.'),
    ),
    Metric(
        id='CANONICAL_LESSON_IDENTITY_COUNT',
        semantic_quantity='CanonicalLessonIdentity — one actual lesson in one book',
        unit='lesson',
        leaf_population='the same TOC rows',
        grouping_key='(sourceDocumentId, lessonNo, pageStart, title)',
        denominator=ABSOLUTE,
        aggregation='count of distinct groups',
        exclusions=('291 identities have no pageStart and rest on title alone; where title is '
                    'also null the evidence cannot decide (WS-A `unverifiable` class)'),
        source_artefact=PACK_ARTEFACT,
        rederivation_command="python3 tool/metrics/cli.py verify --only CANONICAL_LESSON_IDENTITY_COUNT",
        derive=_canonical_lesson_identities,
        recorded_value=3650,
        note=('A MEASUREMENT, not a Founder-approved denominator. 3,679 and 3,650 are the SAME '
              'leaf rows under two grouping keys — not two artefacts disagreeing.'),
    ),
    Metric(
        id='RANGED_LESSON_ROW_COUNT',
        semantic_quantity='TOC rows that carry a printed pageStart, i.e. are source-addressable',
        unit='TOC row',
        leaf_population='the same TOC rows',
        grouping_key='none — rows',
        denominator='SOURCE_LESSON_ROW_COUNT = 3,679 (3,381 / 3,679 = 0.919)',
        aggregation='count where pageStart is not None',
        exclusions='none',
        source_artefact=PACK_ARTEFACT,
        rederivation_command="python3 tool/metrics/cli.py verify --only RANGED_LESSON_ROW_COUNT",
        derive=_ranged_lesson_rows,
        recorded_value=3381,
    ),
    Metric(
        id='LESSON_PAIR_KEY_COUNT',
        semantic_quantity='distinct (sourceDocumentId, lessonNo) pairs — the BROWSABLE figure',
        unit='key pair (NOT a lesson)',
        leaf_population='the same TOC rows',
        grouping_key='(sourceDocumentId, lessonNo)',
        denominator=ABSOLUTE,
        aggregation='count of distinct groups',
        exclusions='none',
        source_artefact=PACK_ARTEFACT,
        rederivation_command="python3 tool/metrics/cli.py verify --only LESSON_PAIR_KEY_COUNT",
        derive=_lesson_pair_keys,
        recorded_value=3240,
        note=('WS-A proved this key OVER-COLLAPSES by 410 real lessons: printed numbering restarts '
              'inside each chủ đề, so «Bài 1» occurs seven times in 01-sgk-giao-duc-the-chat-1. '
              'Kept in the registry BECAUSE it was published as a lesson count and is not one.'),
    ),
    Metric(
        id='TRUE_DUPLICATE_EXCESS_ROWS',
        semantic_quantity='rows that repeat a full identity tuple — the whole gap 3,679 - 3,650',
        unit='row',
        leaf_population='the same TOC rows',
        grouping_key='(sourceDocumentId, lessonNo, pageStart, title)',
        denominator=ABSOLUTE,
        aggregation='sum over groups of (size - 1)',
        exclusions='none',
        source_artefact=PACK_ARTEFACT,
        rederivation_command="python3 tool/metrics/cli.py verify --only TRUE_DUPLICATE_EXCESS_ROWS",
        derive=_true_duplicate_excess_rows,
        recorded_value=29,
        note='3,679 - 29 = 3,650, exactly. The two denominators are reconciled by arithmetic.',
    ),
    Metric(
        id='PACK_BOOK_ROW_COUNT',
        semantic_quantity='shelf book rows across the 12 packs',
        unit='book row',
        leaf_population='pack.books[*]',
        grouping_key='none — rows',
        denominator=ABSOLUTE,
        aggregation='count of leaf rows',
        exclusions='SGK documents with no parseable TOC contribute no shelf row',
        source_artefact=PACK_ARTEFACT,
        rederivation_command="python3 tool/metrics/cli.py verify --only PACK_BOOK_ROW_COUNT",
        derive=_pack_book_rows,
        recorded_value=238,
        note=('COLLISION WARNING. «238» also names a completely different population: the 238 '
              'TC-v2 repaired-ranged LESSONS in six Science books (METRIC-DENOMINATORS.md), which '
              'is the denominator of round 6\'s Learning View census. Same numeral, two '
              'populations, one a book count and one a lesson count. Always write the unit.'),
    ),
    Metric(
        id='PACK_DISTINCT_BOOK_COUNT',
        semantic_quantity='distinct SGK documents on the shelves',
        unit='book',
        leaf_population='pack.books[*]',
        grouping_key='sourceDocumentId',
        denominator=ABSOLUTE,
        aggregation='count of distinct groups',
        exclusions='none',
        source_artefact=PACK_ARTEFACT,
        rederivation_command="python3 tool/metrics/cli.py verify --only PACK_DISTINCT_BOOK_COUNT",
        derive=_distinct_pack_books,
        recorded_value=238,
        note=('Equal to PACK_BOOK_ROW_COUNT: no SGK document appears on two grade shelves. The '
              'equality is measured, not assumed — sourceAssets shows what happens when a row set '
              'IS replicated across packs.'),
    ),
]

METRICS_BY_ID = {m.id: m for m in METRICS}


# ---------------------------------------------------------------- deprecations
def _reconstruct_248(c):
    """The pre-fail-closed pack total: today's leaf rows plus the 41 records that were dropped."""
    return _activity_leaves(c) + _upstream_toan_leaves(c)


def _reconstruct_217(c):
    """207 leaf rows + 10 container KEYS. Reconstructed only to prove it is a unit error."""
    return _activity_leaves(c) + _upstream_toan_keys(c)


def _reconstruct_161(c):
    leaves = list(L.iter_activity_leaves(c.packs, ('tvReadings', 'tvWritings')))
    return L.count_leaves(leaves) + _upstream_toan_leaves(c)


DEPRECATED = [
    Deprecated(
        id='TOTAL_ACTIVITIES',
        published_value=None,
        published_as='«total activities» over the twelve pack files',
        what_it_actually_is='nothing — the phrase is not defined anywhere in the repository',
        verdict='DEPRECATED',
        reason=('Three different totals — 248, 217, 161 — were all published under this one '
                'phrase. A phrase that admits three answers is not a metric. It must not enter '
                'round-7 reporting in any form.'),
        replacement=('ACTIVITY_LEAF_COUNT (7 families, 207) or LEARNER_ACTIVITY_LEAF_COUNT '
                     '(6 families, 171) — chosen explicitly and written with its family set.'),
    ),
    Deprecated(
        id='ACTIVITY_TOTAL_248',
        published_value=248,
        published_as='«pack activities», round-5 Lane D scoreboard, BEFORE column',
        what_it_actually_is=('a correct earlier VALUE of ACTIVITY_LEAF_COUNT: the same seven '
                             'families, the same leaf-row aggregation, on the pack build before '
                             'the Founder §3 fail-closed change. 248 = 207 + 41'),
        verdict='SUPERSEDED',
        reason=('Not wrong. Superseded by an artefact change, and it stays valid as the historical '
                'value of a named metric on a named build.'),
        replacement='ACTIVITY_LEAF_COUNT = 207 on the 2026-09-06 build',
        reconstruction='ACTIVITY_LEAF_COUNT + TOAN_EXERCISE_UPSTREAM_LEAF_COUNT = 207 + 41',
        reconstruct=_reconstruct_248,
    ),
    Deprecated(
        id='ACTIVITY_TOTAL_217',
        published_value=217,
        published_as='an «activities» total over the same twelve pack files',
        what_it_actually_is=('207 activity LEAF ROWS plus 10 toanExercises CONTAINER KEYS. It is a '
                             'sum of two different units, so it counts no population at all'),
        verdict='DEPRECATED',
        reason=('THE UNIT ERROR ITSELF. Adding keys to rows produces a number of the right type '
                'and no quantity. 217 answers no question anyone can state. It is exactly the '
                'defect this workstream exists for, preserved as its own worked example.'),
        replacement='ACTIVITY_LEAF_COUNT = 207 (was 248 pre-fail-closed)',
        reconstruction='ACTIVITY_LEAF_COUNT + TOAN_EXERCISE_UPSTREAM_LESSON_KEY_COUNT = 207 + 10',
        reconstruct=_reconstruct_217,
    ),
    Deprecated(
        id='ACTIVITY_TOTAL_161',
        published_value=161,
        published_as='an «activities» total over the same twelve pack files',
        what_it_actually_is=('tvReadings + tvWritings leaf rows + the 41 upstream Toán expressions '
                             '= 66 + 54 + 41. A leaf-row count over 3 of the 7 families, i.e. the '
                             'Tiếng Việt and Toán subset only'),
        verdict='DEPRECATED',
        reason=('The aggregation is sound; the family set is arbitrary and was never declared. It '
                'silently drops suSources, khoaExperiments, diaMaps and sourceAssets — 87 of the '
                'rows it purports to total — while being published under a whole-corpus name.'),
        replacement=('LEARNER_ACTIVITY_LEAF_COUNT = 171 for the six learner-facing families. If a '
                     'Toán+Tiếng-Việt subtotal is genuinely wanted it must be named as such and '
                     'declare its three families; no consumer in the repository asks for one.'),
        reconstruction=('tvReadings + tvWritings leaf rows + TOAN_EXERCISE_UPSTREAM_LEAF_COUNT '
                        '= 66 + 54 + 41'),
        reconstruct=_reconstruct_161,
    ),
]

DEPRECATED_BY_ID = {d.id: d for d in DEPRECATED}
