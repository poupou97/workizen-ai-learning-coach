"""WAL-77 (GĐ4) — cross-grade graph từ objectives sourceStated.

Vocabulary CÓ BẰNG CHỨNG (đo phân bố động từ mở đầu 569 objectives):
- INTRODUCES : «Nhận biết/Hiểu/Biết/Làm quen» (~101 obj)
- REINFORCES : «Củng cố/Ôn tập» (13+)
- APPLIES    : động từ hành động (Giải/Thực hiện/Tính/Vận dụng/Đọc/Viết/…)
- unclassified: không match — giữ trung thực, không đoán.
Cạnh xuyên lớp: BUILDS_ON (concept lớp 4 → lớp 5) mang origin
**sourceSequence** — «chương trình xếp trước», KHÔNG BAO GIỜ tự nâng thành
sourceStated/prerequisite (luật CurriculumEdge.citable, áp ở scale).
REQUIRES chỉ nhúng khi sourceStated (hiện: 1 cạnh WAL-18).
"""
import json, re
from collections import defaultdict

INTRO = re.compile(r'^(Nhận biết|Hiểu|Biết|Làm quen)')
REINF = re.compile(r'^(Củng cố|Ôn tập|Ôn lại)')
APPLY = re.compile(r'^(Giải|Thực hiện|Tính|Vận dụng|Đọc|Viết|Tìm|Vẽ|Xác định'
                   r'|So sánh|Sắp|Chuyển|Sử dụng|Làm tròn|Làm|Đo|Ước lượng)')

def kind_of(text):
    if INTRO.match(text): return 'INTRODUCES'
    if REINF.match(text): return 'REINFORCES'
    if APPLY.match(text): return 'APPLIES'
    return 'unclassified'

nodes = defaultdict(lambda: {'grades': defaultdict(list)})
stats = defaultdict(int)
for book, grade in [('04-sgv-toan-4', 4), ('05-sgv-toan-5', 5)]:
    for o in json.load(open(f'poc-out/units/{book}.objectives.json')):
        if o['conceptId'] == 'unmapped': continue
        k = kind_of(o['text'])
        stats[k] += 1
        nodes[o['conceptId']]['grades'][grade].append(
            {'lesson': o['lesson'], 'kind': k, 'objectiveId': o['id'],
             'origin': 'sourceStated'})

edges = []
for c, n in sorted(nodes.items()):
    gs = sorted(n['grades'])
    for a, b in zip(gs, gs[1:]):
        edges.append({
            'from': f'{c}@g{a}', 'to': f'{c}@g{b}', 'kind': 'BUILDS_ON',
            'origin': 'sourceSequence',  # thứ tự chương trình — KHÔNG citable-as-dependency
            'evidence': f'{c}: lớp {a} bài {sorted(set(x["lesson"] for x in n["grades"][a]))}'
                        f' → lớp {b} bài {sorted(set(x["lesson"] for x in n["grades"][b]))}',
        })
# REQUIRES sourceStated duy nhất (WAL-18 — SGK5-T2 B53 tr.54)
edges.append({
    'from': 'the-tich-hinh-hop-chu-nhat@g5', 'to': 'the-tich-hinh-lap-phuong@g5',
    'kind': 'REQUIRES', 'origin': 'sourceStated',
    'evidence': 'SGK5-T2 B53 tr.54: «Mình đã biết cách tính thể tích của HHCN…»',
})

out = {'nodes': {c: {str(g): v for g, v in n['grades'].items()}
                 for c, n in sorted(nodes.items())},
       'edges': edges}
json.dump(out, open('poc-out/graph/crossgrade-graph.json', 'w'),
          ensure_ascii=False, indent=1)
from collections import Counter
eo = Counter((e['kind'], e['origin']) for e in edges)
print(f'nodes (concept): {len(nodes)} · objective-kind: {dict(stats)}')
print('edges:', dict(eo), '| llmInferred: 0 (chưa dùng LLM)')
cross = [e for e in edges if e['kind'] == 'BUILDS_ON']
print('cross-grade BUILDS_ON:', [e['from'].split('@')[0] for e in cross])
