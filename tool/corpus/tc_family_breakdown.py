#!/usr/bin/env python3
"""TC-v1 — TLSR / false-trust / CTE broken down by gold-page LAYOUT FEATURE, for the
single candidates and the cascades. Answers Founder questions 15–16 ("which layouts stay
untrusted, can they be failed closed") with measurements, and feeds the corpus-level
extrapolation (census share of each feature × measured FTR).

Usage: <bake-off venv python> tool/corpus/tc_family_breakdown.py [--ver tc-v1] [--md out.md]
"""
import argparse
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tc_sdm  # noqa: E402
import tc_score  # noqa: E402
import tc_cascade  # noqa: E402

FEATS = ['plain', 'two_col', 'side_by_side', 'sidebar', 'colored_box', 'table', 'formula', 'diagram', 'figure', 'speech_bubble', 'question_block', 'continuation', 'color_heavy', 'sgv', 'front/back matter']
PIPELINES = [('docling-ocrmac', None), ('marker', None), ('docling>xycut+mathguard', ('docling-ocrmac', ['current-xycut'], True)), ('marker>docling+mathguard', ('marker', ['docling-ocrmac'], True)), ('current-xycut', None), ('current-naive', None)]


def page_feats(g):
    f = set(g.get('features', []))
    out = set()
    for k in FEATS:
        if k == 'plain' and 'plain' in f: out.add(k)
        elif k == 'sgv' and g.get('docType') == 'SGV': out.add(k)
        elif k == 'front/back matter' and (g.get('lesson', {}).get('number') is None): out.add(k)
        elif k in f or (k == 'two_col' and 'two_col_region' in f) or (k == 'figure' and ('figure' in f or 'caption' in f)): out.add(k)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--ver', default='tc-v1'); ap.add_argument('--md', default=None); a = ap.parse_args()
    golds = tc_sdm.all_gold()
    table = {}
    for name, spec in PIPELINES:
        acc = defaultdict(lambda: dict(pages=0, L=0, T=0, W=0, ok=0, cte=0))
        for g in golds:
            if spec is None:
                S = tc_sdm.load_sdm(name, g['book'], g['page'], a.ver)
                if S is None or S.get('error'): continue
            else:
                prim, vers, guard = spec
                P = tc_sdm.load_sdm(prim, g['book'], g['page'], a.ver); Vs = [tc_sdm.load_sdm(v, g['book'], g['page'], a.ver) for v in vers]
                if P is None or P.get('error') or any(v is None or v.get('error') for v in Vs): continue
                S = tc_cascade.verify(P, Vs); S['candidate'] = name
                if guard: S = tc_cascade.math_guard(S)
            r = tc_score.score(g, S)
            if 'tlsr' not in r: continue
            for k in page_feats(g) | {'ALL'}:
                d = acc[k]; d['pages'] += 1; d['L'] += r['learning_blocks']; d['T'] += r['trusted_blocks']; d['W'] += r['false_trusted']; d['ok'] += round(r['tlsr'] * r['learning_blocks']); d['cte'] += sum(v for kk, v in r['cte'].items() if kk != 'lesson_attach_wrong')
        table[name] = {k: dict(v, tlsr=round(v['ok'] / max(1, v['L']), 3), ftr=round(v['W'] / max(1, v['T']), 3), coverage=round(v['T'] / max(1, v['L']), 3)) for k, v in acc.items()}
    L = ['# TC-v1 — trust by layout feature (gold pages carrying the feature; MEASURED)', '']
    for name, tab in table.items():
        L += [f'## {name}', '', '| feature | pages | learning blocks | trusted (coverage) | TLSR | false trusted | FTR | CTE events (all output) |', '|---|---|---|---|---|---|---|---|']
        for k in ['ALL'] + FEATS:
            if k not in tab: continue
            v = tab[k]
            L.append(f"| {k} | {v['pages']} | {v['L']} | {v['T']} ({v['coverage']:.2f}) | {v['tlsr']:.3f} | {v['W']} | {v['ftr']:.3f} | {v['cte']} |")
        L.append('')
    md = '\n'.join(L)
    if a.md:
        open(a.md, 'w').write(md + '\n')
        json.dump(table, open(a.md.replace('.md', '.json'), 'w'), ensure_ascii=False, indent=1)
    print(md)


if __name__ == '__main__':
    main()
