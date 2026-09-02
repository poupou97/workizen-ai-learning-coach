#!/usr/bin/env python3
"""WAL-128 — dựng PedagogicalPattern INSTANCES từ findings thật (không bịa).

Mỗi pattern = (family, band) + chuỗi intent phổ biến nhất đo được + pacing
median nếu nguồn có + provenance trỏ về doc đại diện. Output:
poc-out/pedagogy/patterns-v0.json (data; code Dart chỉ giữ MODEL)."""
import json, os, collections, statistics

def fam(s):
    s=s.lower()
    if 'toán' in s: return 'TOAN'
    if 'tiếng việt' in s or 'ngữ văn' in s: return 'TV-VAN'
    if 'khoa' in s or 'hoá' in s: return 'KHOA'
    if 'lịch sử' in s: return 'SU'
    if 'tiếng anh' in s: return 'NN'
    return 'KHAC'
def band(g): return '1-2' if g<=2 else '3-5' if g<=5 else '6-9' if g<=9 else '10-12'

docs={}
for fn in os.listdir('poc-out/pedagogy/findings'):
    fs=json.load(open(f'poc-out/pedagogy/findings/{fn}'))
    if fs: docs[fn[:-5]]=fs

patterns=[]
for did,fs in docs.items():
    f0,g=fam(fs[0]['subject']),fs[0]['grade']
    key=(f0,band(g))
    # chuỗi intent theo bài
    by_lesson=collections.defaultdict(list)
    for f in fs:
        if f['field']=='intent' and f.get('lesson') is not None:
            by_lesson[f['lesson']].append((f['page'],f['intent']))
    seqs=collections.Counter()
    for les,xs in by_lesson.items():
        seq=[]
        for _,it in sorted(xs):
            if not seq or seq[-1]!=it: seq.append(it)
        if len(seq)>=2: seqs[tuple(seq)]+=1
    if not seqs: continue
    top,ntop=seqs.most_common(1)[0]
    # pacing median theo intent (THCS có timedComponent cùng trang intent ±1)
    mins=collections.defaultdict(list)
    timed={f['page']:f['minutes'] for f in fs if f['field']=='timedComponent'}
    for f in fs:
        if f['field']=='intent' and f['page'] in timed:
            mins[f['intent']].append(timed[f['page']])
    med={k:int(statistics.median(v)) for k,v in mins.items() if v}
    # trang đại diện của chuỗi top (bài đầu tiên khớp)
    page=None
    for les,xs in sorted(by_lesson.items()):
        seq=[]
        for _,it in sorted(xs):
            if not seq or seq[-1]!=it: seq.append(it)
        if tuple(seq)==top: page=sorted(xs)[0][0]; break
    patterns.append(dict(
        patternId=f'pat:{f0.lower()}:{band(g)}:{"-".join(s.lower() for s in top)}',
        subjectFamily=f0, gradeBand=band(g),
        steps=[dict(intent=s, minutesMedian=med.get(s)) for s in top],
        occurrences=ntop,
        source=dict(authority='SOURCE_EXPLICIT', extractionMethod='sgv-pedagogy-v1',
                    sourceDocumentId=did, page=page),
    ))
patterns.sort(key=lambda p:-p['occurrences'])
json.dump(patterns, open('poc-out/pedagogy/patterns-v0.json','w'), ensure_ascii=False, indent=1)
print(f'{len(patterns)} pattern instances:')
for p in patterns:
    steps='→'.join(s['intent']+(f"({s['minutesMedian']}p)" if s['minutesMedian'] else '') for s in p['steps'])
    print(f"  ×{p['occurrences']:3} {p['subjectFamily']:7}{p['gradeBand']:6} {steps}  [{p['source']['sourceDocumentId']} p{p['source']['page']}]")
