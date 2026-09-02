"""WAL-79 (GĐ6) — Q-matrix cho batch: GIỮ BẤT ĐỊNH, báo cáo chắc/không riêng.

Ba tầng tin cậy, KHÔNG ép đầy-đủ-biết:
- mapped-case  : có SkillCase từ dựng-hình-học (exercise-case-map, INFERRED)
- concept-only : bài trong lesson có concept (qua RULE/objective mapped)
                 nhưng ca CHƯA CÔ LẬP — requirements ghi 'unresolved',
                 đúng doctrine attributionUnresolved (WAL-54).
- unmapped     : chưa có gì đáng tin — nói thẳng.
Mapping version nướng vào từng entry ('qmap-v1') — đổi luật map sau này
KHÔNG diễn giải lại lịch sử (replay audit §G).
"""
import json
from collections import Counter, defaultdict

VERSION = 'qmap-v1'
BOOKS = ['04-sgk-toan-4-tap-mot', '04-sgk-toan-4-tap-hai',
         '05-sgk-toan-5-tap-mot', '05-sgk-toan-5-tap-hai']

case_by_key = {}
for r in json.load(open('poc-out/units/exercise-case-map.json')):
    case_by_key[(r['book'], r['lesson'], r['expr'])] = r

# lesson → concepts (nguồn: RULE map + objectives, đều đã có provenance)
lesson_concepts = defaultdict(set)
for r in json.load(open('poc-out/units/rule-concept-map.json')):
    if r['conceptId'] != 'unmapped':
        lesson_concepts[(r['book'], r['lesson'])].add(r['conceptId'])
for b_sgv, b_sgk4, b_sgk5 in [('04-sgv-toan-4', None, None)]:
    pass
for sgv, grade in [('04-sgv-toan-4', 4), ('05-sgv-toan-5', 5)]:
    for o in json.load(open(f'poc-out/units/{sgv}.objectives.json')):
        if o['conceptId'] != 'unmapped':
            for b in BOOKS:
                if b.startswith(f'{grade:02d}'):
                    lesson_concepts[(b, o['lesson'])].add(o['conceptId'])

out = []
for b in BOOKS:
    for u in json.load(open(f'poc-out/units/{b}.json'))['units']:
        if u['role'] != 'EXERCISE':
            continue
        entry = {'exerciseUnitId': u['id'], 'book': b, 'lesson': u['lesson'],
                 'pagePrinted': u['pagePrinted'], 'version': VERSION}
        concepts = sorted(lesson_concepts.get((b, u['lesson']), []))
        matched = None
        for (bb, ll, expr), r in case_by_key.items():
            if bb == b and ll == u['lesson'] and expr in u['text']:
                matched = r
                break
        if matched:
            entry['tier'] = 'mapped-case'
            entry['requirements'] = [{'conceptId': matched['conceptId'],
                                      'skillCaseId': matched['skillCaseId'],
                                      'origin': 'systemDerived'}]
        elif concepts:
            entry['tier'] = 'concept-only'
            entry['requirements'] = [{'conceptId': c,
                                      'skillCaseId': 'unresolved',
                                      'origin': 'systemDerived'}
                                     for c in concepts]
        else:
            entry['tier'] = 'unmapped'
            entry['requirements'] = []
        out.append(entry)

json.dump(out, open('poc-out/units/qmatrix.json', 'w'),
          ensure_ascii=False, indent=1)
c = Counter(e['tier'] for e in out)
n = len(out)
print(f'exercises: {n} · ' + ' · '.join(
    f'{k}: {v} ({v/n:.0%})' for k, v in c.most_common()))
