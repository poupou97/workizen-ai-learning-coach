#!/usr/bin/env python3
"""Freeze the BLIND evaluation population — round 7 · WS-T · step B.

    python3 tool/corpus/thresholds/population.py build \
        --structure poc-out/graph/curriculum-structure.json \
        --exclusions <json> --freeze

WHAT MAKES IT BLIND, AND WHY IT HAD TO BE BUILT THIS WAY
---------------------------------------------------------
The first thing this workstream looked for was an existing labelled population the candidate
policy had never seen. **There is not one.** Every annotated population in this repository was
consumed by the derivation:

  · the 54 gold pages — A3's published curve was computed over ALL 643 of their rows, including
    the 181 marked `held_out` (gold set `tc-v2`). Pooling them into the published baseline
    (354 served, coverage 0.5505, 26 wrong, FTR 0.0734 — reproduced here exactly) spent them.
    **They are not a blind holdout and this module refuses to treat them as one.**
  · the round-3 484-row audit and the legacy batch-1 audits — A3's audit plane.
  · the 97-row independent audit — a Founder-designated EVALUATION set whose OVER/SAFE labels
    round 5 §8.3 already used to ROUTE restores. Measured on, and acted on.

So blindness is obtained the only honest way left: the population is frozen as a list of LESSON
IDENTITIES for which **no signals and no verdicts exist yet**. Nothing has been decided about
these lessons by anyone. The pipeline runs on them, and the annotation is produced, only after
approval — which means the candidate policy could not have been fitted to them even in
principle, and the ledger's hash chain proves the policy hash existed first.

Publishing the identities does not break blindness. What must never exist before approval is an
artefact saying which of them a threshold ADMITS; `freeze.py` refuses to record one.

SAMPLING
--------
Primary sampling unit: a page-anchored SGK lesson. Cluster, not block — the bound is a promise
about a LESSON, so the unit that is drawn must be the unit the promise is about, and the
within-lesson clustering of errors must be observable rather than assumed away.

Stratification is PROPORTIONAL to the eligible universe on (grade band × subject family). It is
deliberately NOT stratified to suit the candidate policy: a population arranged so that a policy
admits plenty of it is a population chosen to produce a number. If the policy admits little of a
proportional sample, that is the finding.

The evaluation order is frozen with the population. A bound cheaper than the recommended one is
evaluated on a PREFIX of that order — never on a subset chosen later.
"""
import argparse
import collections
import hashlib
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from thresholds import candidates as C     # noqa: E402
from thresholds import freeze as F         # noqa: E402
from thresholds import policy as P         # noqa: E402

#: Pre-committed, and the same convention round 3's sampler used (`seed 20260905`). It is the
#: date, not a number anybody could have searched for a favourable draw with.
SEED = 20260906

#: Lessons to freeze. Sized from the RECOMMENDED bound: BOUND-2 needs >= 1,092 audited trusted
#: blocks with zero teaching-critical errors, and the gold plane suggests a lesson yields on the
#: order of ten admitted blocks. 120 lessons carries headroom; a cheaper bound uses a prefix.
N_LESSONS = 120

SUBJECT_FAMILY = {
    'Toán': 'math', 'Chuyên đề': 'math',
    'KHTN': 'science', 'Khoa học': 'science', 'Vật lí': 'science', 'Hoá học': 'science',
    'Sinh học': 'science', 'Công nghệ': 'science', 'Tin học': 'science',
    'TN&XH': 'science', 'Địa lí': 'science',
    'Ngữ văn': 'language', 'Tiếng Việt': 'language', 'Tiếng Anh': 'language',
    'Lịch sử': 'humanities', 'LS&ĐL': 'humanities', 'GDCD': 'humanities',
    'Đạo đức': 'humanities', 'GDKT&PL': 'humanities', 'GDQP-AN': 'humanities',
}


def grade_band(g):
    return 'primary' if g <= 5 else 'lower_secondary' if g <= 9 else 'upper_secondary'


def family(subject):
    return SUBJECT_FAMILY.get(subject, 'other')


def eligible_lessons(structure_path, exclusions):
    """Page-anchored SGK lessons in books that no truth-producing artefact has touched."""
    doc = json.load(open(structure_path, encoding='utf-8'))
    excluded = set()
    for v in exclusions.values():
        excluded |= set(v)
    out = []
    for d in doc['documents']:
        if d.get('docType') != 'SGK' or not d.get('lessonCount'):
            continue
        if d['sourceDocumentId'] in excluded:
            continue
        ls = [l for l in d['lessons'] if l.get('pageStart')]
        starts = sorted({l['pageStart'] for l in ls})
        nxt = {s: (starts[i + 1] if i + 1 < len(starts) else None)
               for i, s in enumerate(starts)}
        for l in ls:
            end = nxt[l['pageStart']]
            out.append(dict(
                sourceDocumentId=d['sourceDocumentId'], grade=d['grade'], subject=d['subject'],
                lessonNo=l['number'], pageStart=l['pageStart'],
                pageEndExclusive=end,
                unitKind=l.get('unitKind'),
                title_sha256=hashlib.sha256(
                    (l.get('title') or '').encode('utf-8')).hexdigest(),
                stratum=f'{grade_band(d["grade"])}/{family(d["subject"])}'))
    return out


def draw(universe, n=N_LESSONS, seed=SEED):
    """Proportional stratified draw, then a seeded shuffle that fixes the evaluation order."""
    rng = random.Random(seed)
    by = collections.defaultdict(list)
    for r in universe:
        by[r['stratum']].append(r)
    for k in by:
        by[k].sort(key=lambda r: (r['sourceDocumentId'], r['lessonNo']))
    total = len(universe)
    # largest-remainder allocation, so the strata sum to exactly n
    quota = {k: n * len(v) / total for k, v in by.items()}
    take = {k: int(q) for k, q in quota.items()}
    for k in sorted(by, key=lambda k: -(quota[k] - take[k]))[:n - sum(take.values())]:
        take[k] += 1
    picked = []
    for k in sorted(by):
        picked += rng.sample(by[k], min(take[k], len(by[k])))
    rng.shuffle(picked)
    for i, r in enumerate(picked):
        r['evaluation_order'] = i + 1
    return picked


#: The subject families the product exists to teach. `other` (Mĩ thuật, Âm nhạc, GDTC,
#: HĐTN-HN …) is not one of them.
TEACHING_FAMILIES = ('math', 'science', 'language', 'humanities')


def build(structure_path, exclusions, n=N_LESSONS, seed=SEED, families=None, name='BLIND-CORE'):
    universe = eligible_lessons(structure_path, exclusions)
    if families:
        universe = [r for r in universe if r['stratum'].split('/')[1] in set(families)]
    picked = draw(universe, n, seed)
    prefixes = {}
    for b in C.BOUNDS.values():
        need = b.get('min_audited_trusted_blocks_if_zero_observed') or 0
        # 10 admitted blocks per lesson is the PLANNING assumption, not a measurement: the gold
        # plane's candidate C2 admits 0.53 of served and served is 0.55 of blocks, on 54 hard
        # pages. It is recorded so the prefix can be recomputed when the real yield is known.
        prefixes[b['id']] = dict(min_audited_trusted_blocks=need,
                                 lessons_at_10_admitted_per_lesson=min(n, -(-need // 10) if need else 0))
    return dict(
        schema='blind-evaluation-population-v1',
        name=name,
        restricted_to_families=list(families) if families else None,
        frozen_for='round 7 · WS-T · step B — the population is frozen AFTER the policy and '
                   'carries no signals and no verdicts',
        seed=seed,
        sampling_unit='page-anchored SGK lesson (cluster sample)',
        stratification='proportional on grade band × subject family, NOT arranged to suit any '
                       'candidate policy',
        universe=dict(
            structure_file=os.path.basename(structure_path),
            sgk_books_with_lessons_total=238,
            lessons_total=3679,
            lessons_page_anchored_total=3381,
            note='3,679 and 3,381 are re-derived here independently and agree exactly with '
                 'ROUND6 §6. Both are HISTORICAL BASELINE figures; the canonical count 3,650 is '
                 'a MEASUREMENT awaiting a Founder ruling. Neither is used as a denominator for '
                 'any rate in this workstream.',
            eligible_books=len({r['sourceDocumentId'] for r in universe}),
            eligible_lessons=len(universe),
            eligible_by_stratum=dict(sorted(collections.Counter(
                r['stratum'] for r in universe).items())),
        ),
        exclusions=dict(
            reason='a book is excluded if any artefact in this repository has produced TRUTH '
                   'LABELS from it, or tuned anything against it. Corpus-wide OCR and layout '
                   'scans do NOT contaminate and are not grounds for exclusion.',
            books=exclusions,
            excluded_book_count=len({b for v in exclusions.values() for b in v}),
        ),
        known_weakness=(
            'The 97-row independent audit exists only as a published summary; its rows cannot be '
            'enumerated, so disjointness from it is ARGUED (its working set was the books already '
            'excluded above) and NOT PROVEN. This is the weakest link in the blindness claim and '
            'is recorded rather than smoothed over.'),
        size=len(picked),
        evaluation_order_is_frozen=True,
        prefix_for_bound=prefixes,
        lessons=picked,
    )


def main():
    ap = argparse.ArgumentParser(description='freeze the blind evaluation population')
    ap.add_argument('cmd', choices=('build',))
    ap.add_argument('--structure', required=True)
    ap.add_argument('--exclusions', required=True)
    ap.add_argument('--n', type=int, default=N_LESSONS)
    ap.add_argument('--seed', type=int, default=SEED)
    ap.add_argument('--freeze', action='store_true')
    ap.add_argument('--families', default=None,
                    help='comma-separated subject families to restrict to (e.g. the four the '
                         'product teaches). Omit for a proportional draw over everything.')
    ap.add_argument('--name', default='BLIND-CORE')
    ap.add_argument('--out-name', default='BLIND-POPULATION-v1.json')
    a = ap.parse_args()
    excl = json.load(open(a.exclusions, encoding='utf-8'))
    fam = a.families.split(',') if a.families else None
    payload = build(a.structure, excl, a.n, a.seed, fam, a.name)
    leaks = P.identity_leaks(payload)
    if leaks:
        raise SystemExit(f'identity leak in an admission context: {leaks[:3]}')
    out = os.path.join(F.FROZEN_DIR, a.out_name)
    os.makedirs(F.FROZEN_DIR, exist_ok=True)
    json.dump(payload, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"{payload['size']} lessons from {payload['universe']['eligible_lessons']} eligible "
          f"in {payload['universe']['eligible_books']} books")
    for k, v in sorted(collections.Counter(r['stratum'] for r in payload['lessons']).items()):
        print(f'  {k:32s} {v}')
    if a.freeze:
        e = F.freeze('population', payload, out,
                     note=f"blind evaluation population {a.name} — identities only, no signals, "
                          f'no verdicts, frozen after the policy')
        print(f"FROZEN population sha256={e['sha256']} binds_policy={e['binds_policy'][:16]}…")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
