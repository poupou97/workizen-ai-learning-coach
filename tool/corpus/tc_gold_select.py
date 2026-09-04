#!/usr/bin/env python3
"""TC-v1 — propose HARD gold-set candidate pages from the census (stratified).

Why: the gold set must be deliberately hard and diverse (Founder order F):
columns / side-by-side, sidebar, activity box, question blocks, table,
formula, figure+caption, diagram, text wrapping around image, cross-page
lesson, broken layout, elementary visual page — across Toán, Tiếng
Việt/Ngữ văn, Khoa học/KHTN, Lịch sử/Địa lí, Tin học, others, SGK and SGV.

Selection is deterministic (sorted, fixed seed) and only PROPOSES pages;
the annotator confirms by looking at the render (tc_render.py --grid).
Pages are required to sit inside a lesson's page range (so lesson
association can be scored) unless the stratum is 'sgv' or 'no_toc'.

Usage: python3 tool/corpus/tc_gold_select.py [--ver tc-v1] [--per 3]
Output: poc-out/trusted-corpus/<ver>/gold/candidates.json (+ printed table)
"""
import argparse
import json
import os
import random
from collections import defaultdict

ROOT = os.environ.get('TC_ROOT', '/Users/alexnguyen/projects/workizen-ai-learning-coach')

EXISTING = {('07-sgk-khoa-hoc-tu-nhien-7', 20), ('05-sgk-toan-5-tap-mot', 21), ('09-sgk-ngu-van-9-tap-mot', 67), ('09-sgk-tin-hoc-9', 20),
            ('04-sgk-khoa-hoc-4', 30), ('05-sgk-lich-su-va-dia-li-5', 41), ('10-sgk-dia-li-10', 40), ('10-sgk-vat-li-10', 30), ('05-sgk-tieng-viet-5-tap-hai', 8)}

FAMILY = {
    'Toán': 'math', 'Tiếng Việt': 'literacy', 'Ngữ văn': 'literacy', 'Khoa học': 'science', 'KHTN': 'science', 'Vật lí': 'science', 'Hoá học': 'science', 'Sinh học': 'science',
    'LS&ĐL': 'social', 'Lịch sử': 'social', 'Địa lí': 'social', 'Tin học': 'informatics', 'Công nghệ': 'informatics', 'TN&XH': 'science', 'Đạo đức': 'other', 'GDCD': 'other', 'GDKT&PL': 'other',
    'Tiếng Anh': 'language', 'HĐTN': 'other', 'HĐTN-HN': 'other', 'Âm nhạc': 'arts', 'Mĩ thuật': 'arts', 'GDTC': 'other', 'Chuyên đề': 'other',
}

STRATA = [
    ('two_col', lambda r: r.get('columns') == 2 and r['n_lines'] >= 20),
    ('three_col', lambda r: r.get('columns') == 3 and r['n_lines'] >= 20),
    ('side_by_side', lambda r: r.get('side_by_side') and r.get('columns') == 1 and r['n_lines'] >= 20),
    ('sidebar', lambda r: r.get('sidebar') and r['n_lines'] >= 20),
    ('table', lambda r: r.get('table') and r['n_lines'] >= 15),
    ('formula', lambda r: r.get('formula') and r['n_lines'] >= 15),
    ('diagram', lambda r: r.get('diagram') and r['n_lines'] >= 15),
    ('colored_box', lambda r: r.get('colored_box') and r['n_lines'] >= 15),
    ('color_heavy', lambda r: r.get('color_heavy') and r['n_lines'] >= 8),
    ('continuation', lambda r: r.get('continuation') and r['n_lines'] >= 20),
    ('broken', lambda r: (r.get('overlap') or r.get('low_conf')) and r['n_lines'] >= 10),
    ('plain', lambda r: r.get('columns') == 1 and not r.get('figure') and not r.get('sidebar') and not r.get('side_by_side') and r['n_lines'] >= 25),
]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--ver', default='tc-v1'); ap.add_argument('--per', type=int, default=3); a = ap.parse_args()
    rows = [json.loads(l) for l in open(f'{ROOT}/poc-out/trusted-corpus/{a.ver}/census/pages.jsonl')]
    docs = {x['sourceDocumentId']: x for x in json.load(open(f'{ROOT}/poc-out/graph/curriculum-structure.json'))['documents']}
    # lesson ranges for SGK
    ranges = {}
    for bid, m in docs.items():
        ls = sorted([l for l in m.get('lessons', []) if l.get('pageStart')], key=lambda l: l['pageStart'])
        for i, l in enumerate(ls):
            p1 = (ls[i + 1]['pageStart'] - 1) if i + 1 < len(ls) else 10 ** 6
            for p in range(l['pageStart'], min(p1, l['pageStart'] + 60) + 1):
                ranges[(bid, p)] = dict(number=l['number'], title=l['title'], pageStart=l['pageStart'], pageEnd=None if p1 == 10 ** 6 else p1)
    rnd = random.Random(20260904)
    out = []
    for name, pred in STRATA:
        pool = defaultdict(list)
        for r in rows:
            m = docs.get(r['book'], {})
            if not pred(r):
                continue
            fam = FAMILY.get(m.get('subject'), 'other')
            if m.get('docType') == 'SGV':
                fam = 'sgv'
            elif (r['book'], r['page']) not in ranges:
                continue
            pool[fam].append(r)
        for fam, lst in sorted(pool.items()):
            lst.sort(key=lambda r: (r['book'], r['page']))
            picks = rnd.sample(lst, min(a.per, len(lst)))
            for r in picks:
                lr = ranges.get((r['book'], r['page']))
                out.append(dict(stratum=name, family=fam, book=r['book'], page=r['page'], grade=docs[r['book']]['grade'], subject=docs[r['book']]['subject'],
                                docType=docs[r['book']]['docType'], n_lines=r['n_lines'], columns=r.get('columns'), sbs=r.get('sbs_rows'),
                                feats=[k for k in ('table', 'formula', 'sidebar', 'figure', 'diagram', 'colored_box', 'color_heavy', 'continuation', 'overlap', 'low_conf') if r.get(k)],
                                lesson=lr, existing=(r['book'], r['page']) in EXISTING))
    d = f'{ROOT}/poc-out/trusted-corpus/{a.ver}/gold'; os.makedirs(d, exist_ok=True)
    json.dump(out, open(f'{d}/candidates.json', 'w'), ensure_ascii=False, indent=1)
    for o in out:
        print(f"{o['stratum']:<13} {o['family']:<11} {o['book']:<40} p{o['page']:03d} g{o['grade']:<2} lines={o['n_lines']:<3} cols={o['columns']} sbs={o['sbs']} {','.join(o['feats'])} lesson={(o['lesson'] or {}).get('number')}")
    print(len(out), 'candidates')


if __name__ == '__main__':
    main()
