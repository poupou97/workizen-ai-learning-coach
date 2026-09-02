"""WAL-78 (GĐ5) — TeachingMethod catalogue + exposure từ RULE đã map.

RULE «Muốn…, ta…» / «Khi X thì Y» là sách NÓI THẲNG CÁCH LÀM — mỗi RULE
mapped = một method-được-dạy có trang nguồn (sourceStated). Exposure =
(book, grade, lesson, trang) — chính là dữ liệu nuôi LearningStage.
methodsIntroduced thật thay fixture tay.

Phát hiện tự động: concept có ≥2 method ở GRADE KHÁC NHAU = ca «quy đồng
lớp 4 vs lớp 5» tổng quát hoá — nguồn của caseTransitionGap.
Bất biến giữ: KHÔNG entry nào thiếu trang nguồn; không suy method từ
tri thức toán tổng quát — chỉ từ RULE sách in.
"""
import json
from collections import defaultdict

rules = json.load(open('poc-out/units/rule-concept-map.json'))
units_by_id = {}
for b in ('04-sgk-toan-4-tap-mot', '04-sgk-toan-4-tap-hai',
          '05-sgk-toan-5-tap-mot', '05-sgk-toan-5-tap-hai',
          '05-sgk-tieng-viet-5-tap-mot', '05-sgk-tieng-viet-5-tap-hai'):
    for u in json.load(open(f'poc-out/units/{b}.json'))['units']:
        units_by_id[u['id']] = u

cat, skipped = [], 0
for i, r in enumerate(rules):
    if r['conceptId'] == 'unmapped':
        continue
    u = units_by_id.get(r['unitId'])
    if not u or not u.get('pagePrinted'):
        skipped += 1  # thiếu trang nguồn ⇒ KHÔNG vào catalogue (bất biến)
        continue
    grade = 4 if r['book'].startswith('04') else 5
    cat.append({
        'methodId': f"m:{r['conceptId']}:g{grade}:b{r['lesson']}",
        'conceptId': r['conceptId'],
        'grade': grade,
        'book': r['book'],
        'lesson': r['lesson'],
        'pagePrinted': u['pagePrinted'],
        'textHead': u['text'][:120],
        'origin': 'sourceStated',   # RULE là lời sách nói thẳng cách làm
        'extraction': 'rule-method-v1',
    })

json.dump(cat, open('poc-out/units/method-catalogue.json', 'w'),
          ensure_ascii=False, indent=1)

by_concept = defaultdict(set)
for m in cat:
    by_concept[m['conceptId']].add((m['grade'], m['lesson']))
multi = {c: sorted(v) for c, v in by_concept.items()
         if len({g for g, _ in v}) > 1 or len(v) > 1}
print(f'methods: {len(cat)} (bỏ {skipped} thiếu-trang) · concepts: {len(by_concept)}')
print('concept ĐA-METHOD (nguồn caseTransitionGap):')
for c, v in sorted(multi.items()):
    print(f'  {c}: {v}')
