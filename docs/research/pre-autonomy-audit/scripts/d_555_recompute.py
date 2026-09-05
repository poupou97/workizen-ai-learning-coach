#!/usr/bin/env python3
"""Pre-autonomy audit — S4: recompute TC-18 Q3/Q17 'lessons with no UNHANDLED feature' (the ~555 / 3,381)
with the census's own range rule (tc_census_report.py: pageStart -> next pageStart-1, last -> end of book;
NOTE the census uses the PRINTED pageStart as if it were the PDF page index — no offset — so ranges are
shifted by the book's front-matter offset; reported as the census reported it, with that caveat).
Also computes the same flags for the 113 baseline lessons. Writes data/sourceable-555.json"""
import json, collections
ROOT = '/Users/alexnguyen/projects/workizen-ai-learning-coach'
OUT = f'{ROOT}/poc-out/audit/pre-autonomy/data'
docs = {d['sourceDocumentId']: d for d in json.load(open(f'{ROOT}/poc-out/graph/curriculum-structure.json'))['documents']}
FEATS = ['two_col', 'three_col', 'side_by_side', 'table', 'formula', 'sidebar', 'figure', 'diagram', 'colored_box', 'color_heavy', 'overlap', 'low_conf', 'continuation', 'sparse']
HARD = {'two_col', 'three_col', 'side_by_side', 'table', 'formula', 'sidebar', 'diagram', 'colored_box', 'color_heavy', 'overlap', 'low_conf'}
UNHANDLED = {'formula', 'diagram', 'color_heavy', 'table', 'three_col'}   # TC-18 Q3 wording
pages = collections.defaultdict(dict)
for line in open(f'{ROOT}/poc-out/trusted-corpus/tc-v1/census/pages.jsonl'):
    r = json.loads(line); pages[r['book']][r['page']] = {f for f in FEATS if r.get(f)}
baseline = {tuple(x) for x in json.load(open(f'{ROOT}/poc-out/p0-experiment/baseline-learnable.json'))}
tot = collections.Counter(); per_subj = collections.defaultdict(collections.Counter); per_grade = collections.defaultdict(collections.Counter); base = collections.Counter(); base_rows = []
for bid, m in docs.items():
    if m.get('docType') != 'SGK':
        continue
    ls = sorted([l for l in m.get('lessons', []) if l.get('pageStart')], key=lambda l: l['pageStart'])
    pb = pages.get(bid, {}); last = max(pb) if pb else 0
    for i, l in enumerate(ls):
        p0 = l['pageStart']; p1 = (ls[i + 1]['pageStart'] - 1) if i + 1 < len(ls) else last
        if p1 < p0:
            p1 = p0
        fs = set(); n = 0
        for p in range(p0, p1 + 1):
            if p in pb:
                fs |= pb[p]; n += 1
        hard = fs & HARD; unh = fs & UNHANDLED
        for c in (tot, per_subj[m['subject']], per_grade[m['grade']]):
            c['ranged'] += 1; c['plain'] += (not hard); c['no_unhandled'] += (not unh); c['no_unhandled_no_sbs'] += (not unh and 'side_by_side' not in fs)
        k = (bid, l.get('number'))
        if k in baseline:
            base['ranged'] += 1; base['plain'] += (not hard); base['no_unhandled'] += (not unh); base['pages'] += n
            base['pages_side_by_side'] += sum(1 for p in range(p0, p1 + 1) if 'side_by_side' in pb.get(p, set()))
            base['pages_any_hard'] += sum(1 for p in range(p0, p1 + 1) if pb.get(p, set()) & HARD)
            base_rows.append(dict(book=bid, lesson=l.get('number'), pages=n, hard=sorted(hard), unhandled=sorted(unh)))
out = dict(script='d_555_recompute.py', note='census range rule (printed pageStart used as pdf index, no offset) — same as tc_census_report.py; UNHANDLED = formula/diagram/color_heavy/table/three_col per TC-18 Q3',
           total=dict(tot), per_subject={k: dict(v) for k, v in sorted(per_subj.items())}, per_grade={str(k): dict(v) for k, v in sorted(per_grade.items())},
           baseline_113=dict(base), baseline_rows=base_rows)
json.dump(out, open(f'{OUT}/sourceable-555.json', 'w'), ensure_ascii=False, indent=1)
print('TOTAL', dict(tot)); print('BASELINE113', dict(base))
for k, v in sorted(per_subj.items(), key=lambda kv: -kv[1]['ranged']):
    print(f"{k:<14} ranged {v['ranged']:>4}  plain {v['plain']:>3}  no_unhandled {v['no_unhandled']:>4}  no_unhandled&no_sbs {v['no_unhandled_no_sbs']:>4}")
