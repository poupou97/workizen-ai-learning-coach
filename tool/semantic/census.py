#!/usr/bin/env python3
"""Lane E1 · P0.3 — the 3,679-lesson semantic/visual census, with honest tiers.

WHAT THIS COUNTS, AND WHAT IT REFUSES TO COUNT

Six ladder levels, reported as SEPARATE counts and never summed into one score:

  REPRESENTABLE   a cue for the family appears in the lesson's text.
                  A HYPOTHESIS about the content. Not extractability.
  EXTRACTABLE     the family's minimum arity was actually BUILT from real blocks
                  (>=2 ordered steps, >=2 dated events, >=2 hasPart edges, ...).
  GROUNDABLE      every claim behind it carries a locator beyond the block id —
                  a page, a bbox or a character span.
  VALIDATABLE     a named deterministic validator exists that could pass or fail it.
  VISUALIZABLE    a renderer for the family exists in the app today.
  LEARNER_READY   the claim crossed a production trust gate.

A lesson can be REPRESENTABLE and not EXTRACTABLE — that is the normal case and it is
the number that matters. "An LLM emitted JSON for it" is not any of the six, and no LLM
was called anywhere in this lane.

TIERS
  A  source/semantic evidence strong    — a TSL exists; claims built from trusted blocks
  B  candidate / hypothesis             — only line-level units; cues only
  C  insufficient source                — no units and no TSL: nothing to read
  D  domain extension required          — the lesson's object needs a node the core lacks
  E  exception / unknown                — see 07-EXCEPTION-CLUSTERS

DENOMINATORS (D5, docs/research/METRIC-DENOMINATORS.md) — every rate names one:
  canonical 3,679 · units-backed (measured here) · TSL-backed (measured here)
Never write a slice over the canonical denominator.

    python3 tool/semantic/census.py
"""
import argparse
import collections
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import corpus_io as cio  # noqa: E402
import corpus_paths as cp  # noqa: E402
import extract as ex  # noqa: E402
import ontology as onto  # noqa: E402
import visualspec as vs  # noqa: E402

FAMILIES = list(onto.FAMILIES)
DUPES = {}

# What exists in the app TODAY, verified in 01-AUDIT-CLASSIFICATION.md.
VISUALIZABLE_TODAY = {
    'PROCESS': 'visual_view.dart:396 — real corpus data',
    'COMPARISON': 'visual_view.dart:540 — real corpus data',
    'TIMELINE': 'views/timeline_view.dart:22 — SYNTHETIC data only',
    'CONCEPT_MAP': 'visual_view.dart:609 — renderer exists, ZERO producers',
}
VALIDATABLE_TODAY = {
    'TIMELINE': 'timeline-order-v1 (lib/core/lesson_model/timeline_validator.dart:55)',
}

# Domain extensions, and the deterministic signal that a lesson needs one.
EXTENSION_SIGNALS = {
    'MATH_AST': onto.MATH_EXPR_RX,
    'CHEM_REACTION': onto.CHEM_RX,
    'PHYS_QUANTITY': onto.UNIT_SYMBOL_RX,
    'LIT_TEXT': onto.VERSE_RX,
}


def cue_families(texts):
    """{family: {'strong': n, 'weak': n, 'cues': [...]}} over a lesson's text."""
    out = {}
    blob = ' \n '.join(cio.norm(t) for t in texts if t)
    for fam in FAMILIES:
        hits = onto.cue_hits(blob, fam)
        if not hits:
            continue
        strong = sum(1 for _, _, _, weak in hits if not weak)
        out[fam] = {'strong': strong, 'weak': len(hits) - strong,
                    'cues': sorted({n for n, _, _, _ in hits})}
    return out


def extensions_needed(texts):
    blob = ' \n '.join(t for t in texts if t)
    return sorted(k for k, rx in EXTENSION_SIGNALS.items() if rx.search(blob))


def _tsl_index():
    """{(book, lesson): path} for every TSL build available, newest pipeline wins."""
    idx = {}
    roots = [cp.tsl_dir()]
    roots += sorted(glob.glob(os.path.join(cp.poc_out(), 'round*', 'lane-c', '*', '*',
                                           'root', 'poc-out', 'trusted-corpus', 'tc-v2',
                                           '*', 'lessons')))
    for root in roots:
        for path in sorted(glob.glob(os.path.join(root, '*', '*.tsl.json'))):
            book = os.path.basename(os.path.dirname(path))
            try:
                lesson = int(os.path.basename(path).split('.')[0].split('-')[1])
            except (IndexError, ValueError):
                continue
            idx.setdefault((book, lesson), []).append(path)
    return idx


def run(limit=None):
    canonical = cio.load_canonical_lessons()
    canon_keys = {(r['book'], r['lesson']): r for r in canonical}
    # ⚠️ REPORTED, NOT FIXED (workspace rule: report contradictions, do not resolve
    # doctrine). The canonical export has 3,679 ROWS but only 3,240 distinct
    # (book, lessonNo) identities: 154 keys are duplicated, 439 rows in total, mostly
    # title-less rows in GDTC / Âm nhạc / Mĩ thuật style books. A PER-LESSON census can
    # only address the 3,240. Both numbers are carried; neither replaces the other, and
    # D5's 3,679 stays the product-coverage denominator until the Founder decides.
    DUPES['rows'] = len(canonical)
    DUPES['distinctKeys'] = len(canon_keys)
    DUPES['duplicateRows'] = len(canonical) - len(canon_keys)

    # --- tier B source: role-tagged line units --------------------------------
    units = {}
    for book, subject, lesson, us in cio.iter_units_lessons():
        units[(book, lesson)] = [u['text'] for u in us]

    # --- tier A source: TSL ----------------------------------------------------
    tsl = _tsl_index()

    rows = []
    n = 0
    for key, meta in sorted(canon_keys.items()):
        n += 1
        if limit and n > limit:
            break
        book, lesson = key
        row = {'book': book, 'lesson': lesson, 'grade': meta['grade'],
               'subject': meta['subject'], 'tier': 'C',
               'representable': [], 'extractable': [], 'groundable': [],
               'extensions': [], 'primitives': {}, 'relations': {},
               'claims': 0, 'citable': 0, 'learnerReady': 0,
               'unitsBacked': False, 'tslBacked': False}

        texts = units.get(key)
        if texts:
            row['unitsBacked'] = True
            row['tier'] = 'B'
            cues = cue_families(texts)
            row['representable'] = sorted(f for f, v in cues.items() if v['strong'])
            row['representableWeakOnly'] = sorted(f for f, v in cues.items()
                                                  if not v['strong'])
            row['cues'] = {f: v['cues'] for f, v in cues.items()}
            row['extensions'] = extensions_needed(texts)

        paths = tsl.get(key)
        if paths:
            row['tslBacked'] = True
            row['tier'] = 'A'
            row['tslBuilds'] = len(paths)
            # census the BEST build available: a family that any build supports is
            # extractable in principle. The spread between builds is itself reported.
            per_build = {}
            for path in paths:
                les = cio.load_tsl(path)
                les['pipeline'] = path.split(os.sep)[
                    path.split(os.sep).index('tc-v2') + 1] if 'tc-v2' in path.split(os.sep) else '?'
                g = ex.extract(les, subject=meta['subject'], grade=meta['grade'])
                fams = sorted(vs.compile_all(g))
                per_build[les['pipeline']] = fams
                s = g.summary()
                if len(fams) >= len(row['extractable']):
                    row['extractable'] = fams
                    _, prims, rels = ex.families_present(g)
                    row['primitives'], row['relations'] = prims, rels
                    row['claims'] = s['claims']
                    row['citable'] = s['citable']
                    row['learnerReady'] = s['learnerVisible']
                    # GROUNDABLE: SourceGrounding refuses to exist without a locator
                    # beyond the block id, so every built claim is groundable by
                    # construction. Recorded as the locator mix, not as a boast.
                    row['groundable'] = sorted(fams)
                    row['locators'] = s['groundingsByLocator']
            row['perBuild'] = per_build
            if len(per_build) > 1 and len({tuple(v) for v in per_build.values()}) > 1:
                row['buildDisagreement'] = True
            if not texts:
                row['extensions'] = extensions_needed(
                    [b['text'] for b in cio.load_tsl(paths[0])['blocks']])

        # TIER is a PRIMARY label; the flags below stay separately readable, because a
        # lesson can be both "units-backed" and "needs a domain extension" and
        # collapsing that into one letter hides which.
        if not texts and not paths:
            row['tier'] = 'C'
        elif row['extensions'] and not row['extractable']:
            row['tier'] = 'D'
        row['needsExtension'] = bool(row['extensions'])
        rows.append(row)
    return canonical, rows


def aggregate(canonical, rows):
    N = len(rows)
    units_backed = sum(1 for r in rows if r['unitsBacked'])
    tsl_backed = sum(1 for r in rows if r['tslBacked'])

    # A family with no extractor cannot be EXTRACTABLE anywhere; saying "0 lessons"
    # without saying "because no rule exists" would read as a fact about the corpus.
    has_extractor = set(vs.COMPILERS)
    no_extractor = sorted(set(FAMILIES) - has_extractor)

    rep = collections.Counter()
    ext = collections.Counter()
    extn = collections.Counter()
    tiers = collections.Counter()
    multi_rep = multi_ext = 0
    none_rep = none_ext = 0
    subj_fam = collections.Counter()
    grade_fam = collections.Counter()
    disagree = 0

    for r in rows:
        tiers[r['tier']] += 1
        for f in r['representable']:
            rep[f] += 1
            subj_fam[(r['subject'], f)] += 1
            grade_fam[(r['grade'], f)] += 1
        for f in r['extractable']:
            ext[f] += 1
        for e in r['extensions']:
            extn[e] += 1
        if len(r['representable']) > 1:
            multi_rep += 1
        if len(r['extractable']) > 1:
            multi_ext += 1
        if not r['representable']:
            none_rep += 1
        if not r['extractable']:
            none_ext += 1
        if r.get('buildDisagreement'):
            disagree += 1

    return {
        'denominators': {
            'canonicalRows': DUPES.get('rows'),
            'canonicalDistinctLessonKeys': DUPES.get('distinctKeys'),
            'duplicateRows': DUPES.get('duplicateRows'),
            'censusedLessons': N,
            'unitsBacked': units_backed,
            'tslBacked': tsl_backed,
            'note': ('every per-lesson rate below is over censusedLessons '
                     '(= distinct (book,lessonNo) keys). A rate over unitsBacked or '
                     'tslBacked must never be written /3679.'),
        },
        'tiers': dict(tiers),
        'representableByFamily': dict(rep.most_common()),
        'extractableByFamily': dict(ext.most_common()),
        'extensionsNeeded': dict(extn.most_common()),
        'multiFamily': {'representable': multi_rep, 'extractable': multi_ext},
        'noFamily': {'representable': none_rep, 'extractable': none_ext},
        'buildDisagreement': disagree,
        'familiesWithNoExtractor': no_extractor,
        'tslBackedWithAnyExtractable': sum(
            1 for r in rows if r['tslBacked'] and r['extractable']),
        'tslBackedWithNoExtractable': sum(
            1 for r in rows if r['tslBacked'] and not r['extractable']),
        'unitsBackedNeedingExtension': sum(
            1 for r in rows if r['unitsBacked'] and r['needsExtension']),
        'extractablePerLesson': dict(collections.Counter(
            len(r['extractable']) for r in rows if r['tslBacked']).most_common()),
        'representablePerLesson': dict(collections.Counter(
            len(r['representable']) for r in rows if r['unitsBacked']).most_common()),
        'visualizableToday': VISUALIZABLE_TODAY,
        'validatableToday': VALIDATABLE_TODAY,
        'learnerReady': {
            'count': sum(r['learnerReady'] for r in rows),
            'reason': 'THRESHOLDS.json does not exist; no claim can be validated',
        },
        'subjectFamilyTop': {'%s|%s' % k: v for k, v in subj_fam.most_common(40)},
        'gradeFamily': {'%s|%s' % k: v for k, v in sorted(grade_fam.items())},
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=None)
    args = ap.parse_args(argv)
    canonical, rows = run(limit=args.limit)
    agg = aggregate(canonical, rows)
    out = cp.out_dir()
    with open(os.path.join(out, 'census-rows.json'), 'w', encoding='utf-8') as fh:
        json.dump(rows, fh, ensure_ascii=False)
    with open(os.path.join(out, 'census-summary.json'), 'w', encoding='utf-8') as fh:
        json.dump(agg, fh, ensure_ascii=False, indent=1)
    print(json.dumps(agg, ensure_ascii=False, indent=1)[:4000])
    print('\nrows -> %s' % os.path.join(out, 'census-rows.json'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
