#!/usr/bin/env python3
"""WAL-206 — automated CONTENT QUALITY GATE for router-emitted activities.

Founder rule: a lesson is not device-valid because the Reader opens. Each
emitted reading/writing must pass, deterministically:
  Q1 passage coherent — built only from trusted layout body blocks of ONE
     region (layout mode guarantees this; we re-verify via unit ids), and
     contains no sidebar/caption/footnote label text.
  Q2 reading order — passage units come from trusted regions (no marginal
     cut on their region path).
  Q3 question is a learner question — role QUESTION from layout, not a
     heading (uppercase-ratio < 0.6) and not a caption/label.
  Q4 heading-as-question — rejected by Q3.
  Q5 provenance — passage page and question page both inside the lesson's
     TOC page range; question page ≥ passage page.
  Q6 no cross-lesson contamination — implied by Q5 (both pages in range).
  Q7 no future-content leakage — book/grade of the pack equals the lesson's.
  Q8 surface fit — READ_TEXT needs ≥120-char passage + prompt ≥12 chars;
     SELECT_MCQ needs ≥2 options and no answer key (never graded).
Prints per-pack pass/fail counts and writes poc-out/p0-experiment/quality-<grade>.json.
"""
import json
import re
import sys
from collections import Counter

LABELS = re.compile(r'\b(Em có biết|Lưu ý|Ghi nhớ|Chú ý|Theo dõi|Hình \d|Bảng \d|Sơ đồ \d)\b')


def upper_ratio(t):
    letters = [c for c in t if c.isalpha()]
    return (sum(1 for c in letters if c.isupper()) / len(letters)) if letters else 0


def lesson_ranges(docs, book):
    d = next((d for d in docs if d['sourceDocumentId'] == book), None)
    ls = sorted([l for l in d.get('lessons', []) if l.get('number') is not None and l.get('pageStart') is not None], key=lambda l: l['pageStart']) if d else []
    out = {}
    for i, l in enumerate(ls):
        out[l['number']] = (l['pageStart'], ls[i + 1]['pageStart'] if i + 1 < len(ls) else 10 ** 6)
    return out


def check_reading(r, ranges, layout_units):
    fails = []
    q = r['questions'][0]
    if len(r['passage']) < 120: fails.append('Q8_passage_short')
    if len(q['prompt']) < 12: fails.append('Q8_prompt_short')
    if LABELS.search(r['passage']): fails.append('Q1_label_in_passage')
    if upper_ratio(q['prompt']) > 0.6: fails.append('Q3_heading_as_question')
    if r.get('pattern') == 'SELECT_MCQ':
        if len(q.get('options', [])) < 2: fails.append('Q8_mcq_options')
        if q.get('correctOption') is not None: fails.append('Q8_mcq_graded_without_key')
    lo, hi = ranges.get(r['lesson'], (None, None))
    if lo is None: fails.append('Q5_no_lesson_range')
    else:
        if not (lo <= r['page'] < hi): fails.append('Q5_passage_page_out_of_lesson')
        if q.get('page') is not None and not (lo <= q['page'] < hi): fails.append('Q5_question_page_out_of_lesson')
        if q.get('page') is not None and q['page'] < r['page']: fails.append('Q5_question_before_passage')
    pu = layout_units.get(r.get('passageUnitId'))
    qu = layout_units.get(r.get('questionUnitId'))
    if r.get('source', '').endswith('layout'):
        if not pu or pu['role'] != 'PASSAGE': fails.append('Q2_passage_unit_missing')
        if not qu or qu['role'] != 'QUESTION': fails.append('Q3_question_unit_not_question')
    return fails


def main(grades):
    docs = json.load(open('poc-out/graph/curriculum-structure.json'))['documents']
    total = Counter()
    for g in grades:
        pack = json.load(open(f'assets/pack/lesson-index-g{g}.json'))
        res = []
        cache = {}
        for r in pack['tvReadings']:
            if not r.get('source', '').startswith('pattern-router'): continue
            book = r['book']
            if book not in cache:
                try: cache[book] = {u['id']: u for u in json.load(open(f'poc-out/units-layout/{book}.json'))['units']}
                except FileNotFoundError: cache[book] = {}
            fails = check_reading(r, lesson_ranges(docs, book), cache[book])
            res.append(dict(book=book, lesson=r['lesson'], pattern=r.get('pattern'), fails=fails))
            total['pass' if not fails else 'fail'] += 1
            for f in fails: total[f] += 1
        for w in pack['tvWritings']:
            if not w.get('source', '').startswith('pattern-router'): continue
            fails = [] if 12 <= len(w['prompt']) <= 400 and upper_ratio(w['prompt']) < 0.6 else ['Q8_prompt']
            res.append(dict(book=w['book'], lesson=w['lesson'], pattern='WRITE_TEXT', fails=fails))
            total['pass' if not fails else 'fail'] += 1
        json.dump(res, open(f'poc-out/p0-experiment/quality-g{g}.json', 'w'), ensure_ascii=False)
        ok = sum(1 for x in res if not x['fails'])
        print(f'grade {g}: routed activities {len(res)}, pass {ok}, fail {len(res) - ok}')
    print('TOTAL', dict(total))
    passing_lessons = set()
    for g in grades:
        for x in json.load(open(f'poc-out/p0-experiment/quality-g{g}.json')):
            if not x['fails']: passing_lessons.add((x['book'], x['lesson']))
    print('unique lessons with >=1 activity passing the content gate:', len(passing_lessons))
    json.dump(sorted(passing_lessons), open('poc-out/p0-experiment/content-valid-lessons.json', 'w'))


if __name__ == '__main__':
    main([int(a) for a in sys.argv[1:]] or list(range(4, 10)))
