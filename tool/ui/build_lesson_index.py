#!/usr/bin/env python3
"""WAL-136 — lesson index cho UI từ DỮ LIỆU THẬT (curriculum-structure +
exercise-case-map). Output: assets/pack/lesson-index-g<N>.json — đi cùng
chính sách pack (gitignored, localResearchOnly; build local vào APK dev)."""
import json, os, sys, collections

GRADE = int(sys.argv[1]) if len(sys.argv) > 1 else 5

docs = json.load(open('poc-out/graph/curriculum-structure.json'))['documents']

subjects = collections.defaultdict(list)
for d in docs:
    if d['docType'] != 'SGK' or d['grade'] != GRADE:
        continue
    lessons = [dict(no=les['number'], title=les.get('title'),
                    pageStart=les.get('pageStart'))
               for les in d.get('lessons', []) if les.get('number') is not None]
    if lessons:
        subjects[d['subject']].append(dict(
            sourceDocumentId=d['sourceDocumentId'],
            volume=d.get('volume'),
            lessons=sorted(lessons, key=lambda x: x['no'])))

ex_by_lesson = collections.defaultdict(list)
try:
    ec = json.load(open('poc-out/units/exercise-case-map.json'))
    items = ec if isinstance(ec, list) else ec.get('items', [])
    for e in items:
        if f'0{GRADE}-sgk-toan-{GRADE}' in e.get('book', '') and e.get('lesson') is not None:
            ex_by_lesson[e['lesson']].append(dict(
                expr=e['expr'], skillCaseId=e.get('skillCaseId'),
                page=e.get('printed'), book=e.get('book')))
except FileNotFoundError:
    pass

for v in subjects.values():
    v.sort(key=lambda b: (b['volume'] or '9', b['sourceDocumentId']))
out = dict(grade=GRADE, version='lesson-index-v1',
           subjects={k: v for k, v in sorted(subjects.items())},
           toanExercises={str(k): v for k, v in sorted(ex_by_lesson.items())})
os.makedirs('assets/pack', exist_ok=True)
path = f'assets/pack/lesson-index-g{GRADE}.json'
json.dump(out, open(path, 'w'), ensure_ascii=False)
n_les = sum(len(l['lessons']) for v in subjects.values() for l in v)
print(f'{path}: {len(subjects)} môn, {n_les} bài, exercises Toán: '
      f'{sum(len(v) for v in ex_by_lesson.values())} (bài: {sorted(ex_by_lesson)[:10]})')
for b in subjects.get('Toán', [])[:1]:
    for l in b['lessons'][:8]:
        print('  Toán:', l['no'], (l['title'] or 'KHÔNG TÊN')[:50])
print('môn:', list(subjects.keys()))
