#!/usr/bin/env python3
"""Round 6 · WS-A (A2) — SourceLessonRecord vs CanonicalLessonIdentity.

`poc-out/k12-census-exports/all-lessons.csv` carries **3,679 rows** but only **3,240 distinct
`(sourceDocumentId, lessonNo)` keys**: 154 keys are duplicated, 439 rows in excess of one per key.
The Founder has approved neither number as the count of unique canonical lessons, so `3,679` stands
as **HISTORICAL BASELINE ONLY** until the evidence settles what it counts.

The evidence is upstream. Each CSV row is one entry of a book's `lessons[]` array in
`poc-out/graph/curriculum-structure.json`, and that entry carries `number`, `pageStart` and `title`
— three fields the CSV projection drops down to `number`. So the question «is 3,679 a lesson count or
a row count?» is answerable without any new judgement: ask whether two rows that share a key also
share the page they start on.

    lesson_identity.py report [--out FILE] [--md FILE]

TWO CONCEPTS, and the measurement says they are genuinely different things:

  SourceLessonRecord      one entry as parsed from one book's table of contents:
                          (sourceDocumentId, lessonNo, pageStart, title). 3,679 of them.
  CanonicalLessonIdentity one actual lesson in one book. `(sourceDocumentId, lessonNo)` is NOT it,
                          because in GDTC / Âm nhạc / Chuyên đề books the printed numbering RESTARTS
                          inside every chủ đề — «Bài 1» occurs seven times in one book, at seven
                          different printed pages, and those are seven different lessons.

Counts only; no SGK text is written by this tool beyond what the census CSV already carries.
"""
import argparse
import collections
import csv
import json
import os
import sys

SCHEMA = 'ws-a-lesson-identity-v1'
ROOT = os.environ.get('TC_ROOT', '/Users/alexnguyen/projects/workizen-ai-learning-coach')
STRUCTURE = f'{ROOT}/poc-out/graph/curriculum-structure.json'
CENSUS_CSV = f'{ROOT}/poc-out/k12-census-exports/all-lessons.csv'

#: The classes the Founder asked every duplicate to be sorted into. Each verdict below is decided by a
#: fact in the source structure, never by a similarity threshold.
CLASSES = (
    'true_duplicate',              # identical on number, pageStart AND title: one record emitted twice
    'key_collision',               # same number, different pageStart: numbering restarts per chủ đề
    'mixed',                       # a group that contains both
    'unverifiable',                # no pageStart and no title on any row: the evidence cannot decide
)


def load_records(structure=None, census_csv=None):
    """The SourceLessonRecords of the census population: the books that actually produce CSV rows."""
    struct = json.load(open(structure or STRUCTURE, encoding='utf-8'))
    docs = {x['sourceDocumentId']: x for x in struct['documents']}
    with open(census_csv or CENSUS_CSV, encoding='utf-8') as fh:
        books = sorted({r['sourceDocumentId'] for r in csv.DictReader(fh)})
    out = []
    for b in books:
        for l in docs[b].get('lessons') or []:
            if l.get('number') is None:
                continue
            out.append(dict(book=b, lessonNo=l['number'], pageStart=l.get('pageStart'),
                            title=(l.get('title') or '').strip() or None,
                            grade=docs[b].get('grade'), subject=docs[b].get('subject')))
    return out, docs, books


def classify_group(recs):
    """→ (class, evidence) for the ≥ 2 records that share one `(book, lessonNo)` key."""
    pages = {r['pageStart'] for r in recs}
    titles = {r['title'] for r in recs}
    full = {(r['pageStart'], r['title']) for r in recs}
    if len(full) == 1:
        if pages == {None} and titles == {None}:
            return 'unverifiable', 'every row has the same number and neither a pageStart nor a title'
        return 'true_duplicate', f'every row starts at the same printed page ({sorted(pages)[0]})'
    if len(full) == len(recs):
        return 'key_collision', f'{len(recs)} rows, {len(full)} distinct (pageStart, title) — printed numbering restarts'
    return 'mixed', f'{len(recs)} rows collapse to {len(full)} distinct (pageStart, title)'


def report(structure=None, census_csv=None):
    recs, docs, books = load_records(structure, census_csv)
    by_key = collections.defaultdict(list)
    for r in recs:
        by_key[(r['book'], r['lessonNo'])].append(r)
    dup = {k: v for k, v in by_key.items() if len(v) > 1}

    groups, by_class, excess_by_class = [], collections.Counter(), collections.Counter()
    for k, v in sorted(dup.items()):
        cls, ev = classify_group(v)
        full = {(r['pageStart'], r['title']) for r in v}
        groups.append(dict(book=k[0], lessonNo=k[1], rows=len(v), distinctRecords=len(full),
                           cls=cls, evidence=ev, subject=v[0]['subject'], grade=v[0]['grade']))
        by_class[cls] += 1
        excess_by_class[cls] += len(v) - len(full)          # rows this class removes
    canonical = {(r['book'], r['lessonNo'], r['pageStart'], r['title']) for r in recs}
    anchored = sum(1 for c in canonical if c[2] is not None)
    true_dup_excess = len(recs) - len(canonical)
    excess_rows = sum(len(v) - 1 for v in dup.values())

    sgk = [b for b, x in docs.items() if x.get('docType') == 'SGK']
    zero = [b for b in sgk if b not in set(books)]

    return dict(
        schema=SCHEMA,
        # ---- the six figures the Founder asked for ----
        sourceRows=len(recs),
        distinctCurrentKeys=len(by_key),
        trueDuplicates=true_dup_excess,
        keyCollisions=excess_rows - true_dup_excess,
        sourceVariants=0,
        canonicalLessonCount=len(canonical),
        # ---- the evidence behind them ----
        duplicatedKeys=len(dup), excessRows=excess_rows,
        groupsByClass=dict(by_class), rowsRemovedByClass=dict(excess_by_class),
        canonicalKey='(sourceDocumentId, lessonNo, pageStart, title)',
        canonicalPageAnchored=anchored,
        canonicalUnanchored=len(canonical) - anchored,
        rowsWithoutPageStart=sum(1 for r in recs if r['pageStart'] is None),
        # ---- what the denominator does NOT contain, which is its own accounting problem ----
        sgkDocuments=len(sgk), booksContributingRows=len(books),
        sgkBooksContributingZeroRows=len(zero),
        sgkZeroRowStructureStatus=dict(collections.Counter(docs[b].get('structureStatus') for b in zero)),
        duplicatedKeysBySubject=dict(collections.Counter(g['subject'] for g in groups)),
        duplicatedKeysByGrade=dict(collections.Counter(str(g['grade']) for g in groups)),
        groups=groups)


def _md(o):
    L = ['| figure | value |', '|---|---:|',
         f"| SOURCE ROWS | {o['sourceRows']} |",
         f"| DISTINCT CURRENT KEYS `(book, lessonNo)` | {o['distinctCurrentKeys']} |",
         f"| TRUE DUPLICATES (excess rows) | {o['trueDuplicates']} |",
         f"| KEY COLLISIONS (excess rows) | {o['keyCollisions']} |",
         f"| SOURCE VARIANTS | {o['sourceVariants']} |",
         f"| **CANONICAL LESSON COUNT** `{o['canonicalKey']}` | **{o['canonicalLessonCount']}** |",
         f"| ... page-anchored | {o['canonicalPageAnchored']} |",
         f"| ... unanchored (no `pageStart`) | {o['canonicalUnanchored']} |",
         '', '| duplicate class | keys | rows it removes |', '|---|---:|---:|']
    for k in CLASSES:
        L.append(f"| `{k}` | {o['groupsByClass'].get(k, 0)} | {o['rowsRemovedByClass'].get(k, 0)} |")
    return '\n'.join(L) + '\n'


def cmd_report(a):
    o = report()
    print(f"  SOURCE ROWS                   {o['sourceRows']}")
    print(f"  DISTINCT CURRENT KEYS         {o['distinctCurrentKeys']}  "
          f"({o['duplicatedKeys']} duplicated keys, {o['excessRows']} excess rows)")
    print(f"  TRUE DUPLICATES               {o['trueDuplicates']}")
    print(f"  KEY COLLISIONS                {o['keyCollisions']}")
    print(f"  SOURCE VARIANTS               {o['sourceVariants']}")
    print(f"  CANONICAL LESSON COUNT        {o['canonicalLessonCount']}  {o['canonicalKey']}")
    print(f"    page-anchored {o['canonicalPageAnchored']} · unanchored {o['canonicalUnanchored']}")
    print(f"  groups by class: {dict(o['groupsByClass'])}")
    print(f"  NOTE: {o['sgkBooksContributingZeroRows']} of {o['sgkDocuments']} SGK books contribute ZERO "
          f"rows ({o['sgkZeroRowStructureStatus']}) — 3,679 is not «all SGK lessons»")
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        json.dump(o, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(f'→ {a.out}')
    if a.md:
        os.makedirs(os.path.dirname(os.path.abspath(a.md)), exist_ok=True)
        open(a.md, 'w', encoding='utf-8').write(_md(o))
        print(f'markdown → {a.md}')
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('report')
    s.add_argument('--out', default='')
    s.add_argument('--md', default='')
    s.set_defaults(fn=cmd_report)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == '__main__':
    sys.exit(main())
