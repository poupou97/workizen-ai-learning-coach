#!/usr/bin/env python3
"""WAL-127 — aggregate findings: coverage theo family, chuỗi intent theo bài,
kho misconception, phân bố skill EN. Số đếm thuần — không suy diễn."""
import json, os, collections

def fam(s):
    s=s.lower()
    if 'toán' in s: return 'TOAN'
    if 'tiếng việt' in s or 'ngữ văn' in s: return 'TV-VAN'
    if 'khoa' in s or 'hoá' in s: return 'KHOA'
    if 'lịch sử' in s: return 'SU'
    if 'tiếng anh' in s: return 'NN'
    return 'KHAC'

docs = {}
for fn in os.listdir('poc-out/pedagogy/findings'):
    fs = json.load(open(f'poc-out/pedagogy/findings/{fn}'))
    if fs: docs[fn[:-5]] = fs

# 1) coverage field × family
cov = collections.defaultdict(collections.Counter)
for did, fs in docs.items():
    f0 = fam(fs[0]['subject'])
    for f in fs: cov[f0][f['field']] += 1

# 2) chuỗi intent theo bài (VN) — thứ tự xuất hiện trong một lesson
seqs = collections.Counter()
for did, fs in docs.items():
    if fam(fs[0]['subject'])=='NN': continue
    by_lesson = collections.defaultdict(list)
    for f in fs:
        if f['field']=='intent' and f.get('lesson') is not None:
            by_lesson[f['lesson']].append((f['page'], f['intent']))
    for les, xs in by_lesson.items():
        seq = []
        for _, it in sorted(xs):
            if not seq or seq[-1] != it: seq.append(it)
        if len(seq) >= 2: seqs['→'.join(seq)] += 1

# 3) misconception harvest
mis = [dict(doc=did, page=f['page'], lesson=f.get('lesson'), headline=f['headline'])
       for did, fs in docs.items() for f in fs if f['field']=='misconceptionCandidate']

# 4) EN skill + block structure
en_skill = collections.Counter()
en_blocks = 0
for did, fs in docs.items():
    if fam(fs[0]['subject'])!='NN': continue
    for f in fs:
        if f['field']=='skillActivity': en_skill[f['skill']] += 1
        if f['field']=='goal': en_blocks += 1

out = dict(coverage={k: dict(v) for k, v in cov.items()},
           intentSequencesTop=dict(seqs.most_common(15)),
           misconceptions=mis, enSkill=dict(en_skill), enGoalBlocks=en_blocks)
json.dump(out, open('poc-out/pedagogy/aggregates.json','w'), ensure_ascii=False, indent=1)

print('== COVERAGE (field: count) theo family ==')
for f0, c in sorted(cov.items()):
    top = ' '.join(f'{k}:{v}' for k, v in c.most_common(9))
    print(f'{f0:7} {top}')
print('\n== TOP INTENT SEQUENCES (theo bài, VN) ==')
for s, n in seqs.most_common(12): print(f'  {n:3} × {s}')
print(f'\n== MISCONCEPTIONS: {len(mis)} candidate có (doc,page,lesson) ==')
for m in mis[:8]: print(f"  {m['doc'][:22]} p{m['page']}: {m['headline'][:90]}")
print(f'\n== EN: {en_blocks} Goal-block; skill {dict(en_skill)} ==')
