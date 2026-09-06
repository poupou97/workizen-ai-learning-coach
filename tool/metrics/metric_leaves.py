#!/usr/bin/env python3
"""Round 7 · WS-M — leaf-record iterators, and the guard that makes `len()` unusable on a container.

THE INCIDENT THIS FILE EXISTS FOR
---------------------------------
`toanExercises` in `assets/pack/lesson-index-g*.json` is a **dict keyed by lesson number
whose values are lists of expressions**:

    len(d['toanExercises'])                          # 10  <- lesson KEYS
    sum(len(v) for v in d['toanExercises'].values()) # 41  <- expressions

Round 6 called `len()`, reported «10 toanExercises», and then filed the settled figure
`41 -> 0` as NOT CAPTURED. Round 3 made the same mistake. The number was the right type
and the wrong quantity, so it passed every check that was not a re-derivation.

THE RULE THIS FILE ENFORCES
---------------------------
A count is taken over **leaf records**, never over a container. `count_leaves()` raises on
a mapping; `count_container_keys()` exists but must be named explicitly, and its unit is
`key`, never `item`. Any metric that wants a number goes through an iterator here, so the
shape question is answered once, in one place, by the schema — not re-guessed per caller.

No SGK text leaves this module: the iterators yield identity and provenance fields only.
"""
import json
import os

# --------------------------------------------------------------------------- shapes
# The pack schema's activity-bearing keys, and the SHAPE of each. `by_lesson` means
# dict[lessonNoAsString] -> list[leaf]; `list` means list[leaf]. This table is the single
# place the shape is recorded, and it is checked against real packs by
# `check_pack_shapes()` so a schema change cannot silently invalidate a metric.
#
# Kept byte-compatible with tool/corpus/legacy/packs.py FAMILIES (same seven keys, same
# shapes). Divergence between the two is itself a defect and is asserted in the tests.
ACTIVITY_SHAPES = {
    'toanExercises':   'by_lesson',
    'tvReadings':      'list',
    'tvWritings':      'list',
    'suSources':       'list',
    'khoaExperiments': 'list',
    'diaMaps':         'list',
    'sourceAssets':    'list',
}

# Six of the seven. `sourceAssets` is excluded: a source asset is a cropped picture with
# provenance, not something a learner is asked to do, and every grade pack carries the SAME
# rows (see DISTINCT_SOURCE_ASSET_COUNT). This is the family set used by
# tool/corpus/readiness_matrix.py ACT_KEYS and tool/research/lane_c PACK_KEYS.
LEARNER_ACTIVITY_FAMILIES = tuple(k for k in ACTIVITY_SHAPES if k != 'sourceAssets')

GRADES = tuple(range(1, 13))


class ContainerShapeError(TypeError):
    """Raised when a count is attempted over a container instead of over leaf records."""


class ArtefactMissing(FileNotFoundError):
    """Raised when the artefact a metric is defined over is not on this machine.

    Packs and `poc-out/` are gitignored (SGK derivative works). A missing artefact is
    UNAVAILABLE — never zero, and never a pass.
    """


# --------------------------------------------------------------------------- guards
def count_leaves(records):
    """Count leaf records. REFUSES a mapping — that is the whole point of this function.

    >>> count_leaves([{'a': 1}, {'a': 2}])
    2
    >>> count_leaves({'60': [{}, {}], '61': [{}]})
    Traceback (most recent call last):
    ContainerShapeError: ...
    """
    if isinstance(records, dict):
        raise ContainerShapeError(
            'count_leaves() was handed a mapping. len() on a keyed container counts KEYS, '
            'not items — this is the round-6 `toanExercises` defect (10 keys reported for '
            '41 expressions). Flatten with flatten_by_lesson() and count the leaves, or say '
            'count_container_keys() and carry the unit `key`.')
    return sum(1 for _ in records)


def count_container_keys(container):
    """Count the KEYS of a keyed container. Unit is `key`, and it is not an item count."""
    if not isinstance(container, dict):
        raise ContainerShapeError(
            'count_container_keys() was handed a non-mapping; it has no keys to count.')
    return len(container)


def flatten_by_lesson(container):
    """dict[lessonNo] -> list[leaf]  ==>  iterator of (lessonNoAsInt, leaf).

    The one correct way to read a `by_lesson` family. Iterating the dict directly yields
    its keys, which is how tool/research/lane_c/subject_family_census.py came to record
    lesson numbers as `_non_dict_entries` (WS-M finding 2).
    """
    if not isinstance(container, dict):
        raise ContainerShapeError(
            f'flatten_by_lesson() expects a by_lesson mapping, got {type(container).__name__}.')
    for lesson_no, items in container.items():
        for leaf in (items or []):
            yield int(lesson_no), leaf


# --------------------------------------------------------------------------- artefacts
def repo_root(start=None):
    here = os.path.abspath(start or os.path.dirname(os.path.abspath(__file__)))
    while here != os.path.dirname(here):
        if os.path.isdir(os.path.join(here, 'tool')) and os.path.isdir(os.path.join(here, 'lib')):
            return here
        here = os.path.dirname(here)
    return os.getcwd()


def pack_path(grade, root=None):
    return os.path.join(root or repo_root(), 'assets', 'pack', f'lesson-index-g{grade}.json')


def load_pack(grade, root=None):
    path = pack_path(grade, root)
    if not os.path.exists(path):
        raise ArtefactMissing(path)
    with open(path, encoding='utf-8') as fh:
        return json.load(fh)


def load_packs(root=None, grades=GRADES):
    """Every grade pack, or ArtefactMissing naming the first one absent.

    All twelve or none: a metric computed over a partial pack set is a different metric,
    and silently counting eight packs as twelve is the same class of error as counting keys
    as items.
    """
    return [(g, load_pack(g, root)) for g in grades]


def exercise_case_map_path(root=None):
    return os.path.join(root or repo_root(), 'poc-out', 'units', 'exercise-case-map.json')


def load_exercise_case_map(root=None):
    """The UPSTREAM leaf source for toanExercises, gitignored under poc-out/."""
    path = exercise_case_map_path(root)
    if not os.path.exists(path):
        raise ArtefactMissing(path)
    with open(path, encoding='utf-8') as fh:
        blob = json.load(fh)
    return blob if isinstance(blob, list) else blob.get('items', [])


# --------------------------------------------------------------------------- leaf iterators
def iter_activity_leaves(packs, families=None):
    """(grade, family, lessonNo, book, leaf) for every activity leaf record in the packs.

    Shape-aware by construction: a `by_lesson` family is flattened, a `list` family is not.
    """
    fams = families or tuple(ACTIVITY_SHAPES)
    for grade, pack in packs:
        for fam in fams:
            blob = pack.get(fam)
            if not blob:
                continue
            if ACTIVITY_SHAPES[fam] == 'by_lesson':
                for lesson_no, leaf in flatten_by_lesson(blob):
                    yield grade, fam, lesson_no, (leaf or {}).get('book'), leaf
            else:
                if isinstance(blob, dict):
                    raise ContainerShapeError(
                        f'{fam} is declared shape `list` but the pack holds a mapping — the '
                        f'schema and the artefact disagree; refusing to count.')
                for leaf in blob:
                    leaf = leaf or {}
                    yield (grade, fam, leaf.get('lesson'),
                           leaf.get('book') or leaf.get('sourceDocumentId'), leaf)


def iter_lesson_rows(packs):
    """(sourceDocumentId, lessonNo, pageStart, title) for every TOC lesson ROW in the packs.

    This is the leaf population under 3,679 / 3,650 / 3,381 / 3,240 — four published
    denominators that are the SAME rows read with four different grouping keys.
    """
    for _grade, pack in packs:
        for books in (pack.get('subjects') or {}).values():
            for book in books:
                for lesson in (book.get('lessons') or []):
                    yield (book.get('sourceDocumentId'), lesson.get('no'),
                           lesson.get('pageStart'), lesson.get('title'))


def iter_book_rows(packs):
    """(grade, sourceDocumentId) for every shelf book row in the packs."""
    for grade, pack in packs:
        for book in (pack.get('books') or []):
            yield grade, (book or {}).get('sourceDocumentId')


def iter_upstream_toan_exercises(root=None):
    """(book, lessonNo, status, method, skillCaseId) per upstream Toán exercise leaf record.

    `expr` is deliberately NOT yielded: it is verbatim-shaped SGK content and a metric never
    needs it. All 41 rows carry status INFERRED (geometry rebuild), which is why the builder
    fails closed and ships none of them (Founder §3).
    """
    for row in load_exercise_case_map(root):
        if row.get('lesson') is None or 'sgk-toan-' not in (row.get('book') or ''):
            continue
        yield (row.get('book'), row.get('lesson'), (row.get('status') or '').strip().upper(),
               row.get('method'), row.get('skillCaseId'))


# --------------------------------------------------------------------------- schema check
def check_pack_shapes(packs):
    """Every declared shape actually holds in every pack. Returns a list of disagreements."""
    bad = []
    for grade, pack in packs:
        for fam, shape in ACTIVITY_SHAPES.items():
            if fam not in pack:
                continue
            got = 'by_lesson' if isinstance(pack[fam], dict) else (
                'list' if isinstance(pack[fam], list) else type(pack[fam]).__name__)
            if got != shape:
                bad.append(f'g{grade}.{fam}: declared {shape}, artefact is {got}')
    return bad
