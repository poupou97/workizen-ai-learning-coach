#!/usr/bin/env python3
"""Pre-autonomy audit — S5: WAL-206 XY-cut page-level gate census on poc-out/layout (six Science books + 6 gold books)
and units-layout drop reasons. Also units-k12 (naive) role counts for the six books. Writes data/layout-gate.json"""
import json, glob, os, collections
ROOT = '/Users/alexnguyen/projects/workizen-ai-learning-coach'
OUT = f'{ROOT}/poc-out/audit/pre-autonomy/data'
res = {}
for bdir in sorted(glob.glob(f'{ROOT}/poc-out/layout/*/')):
    b = os.path.basename(bdir.rstrip('/'))
    if ' ' in b: res[b] = dict(note='stray directory name (zsh word-split artefact), skipped'); continue
    pages = trusted_pages = 0; blocks = collections.Counter(); roles_trusted = collections.Counter(); tablelike = 0; marginal = 0
    for f in glob.glob(bdir + 'p*.json'):
        d = json.load(open(f)); pages += 1; L = d['layout']; trusted_pages += bool(L.get('trusted')); tablelike += bool(L.get('tableLike')); marginal += bool(L.get('marginalCuts'))
        for bl in d['blocks']:
            blocks['trusted' if bl.get('trusted') else 'untrusted'] += 1
            if bl.get('trusted'): roles_trusted[bl.get('role')] += 1
    row = dict(pages=pages, trusted_pages=trusted_pages, trusted_page_share=round(trusted_pages / pages, 3) if pages else None, tableLike_pages=tablelike, pages_with_marginal_cuts=marginal, blocks=dict(blocks), trusted_block_share=round(blocks['trusted'] / max(1, sum(blocks.values())), 3), trusted_roles=dict(roles_trusted))
    ul = f'{ROOT}/poc-out/units-layout/{b}.json'
    if os.path.exists(ul):
        u = json.load(open(ul)); row['units_layout'] = dict(collections.Counter(x['role'] for x in u['units'])); row['units_layout_dropped'] = u['dropped']
    uk = f'{ROOT}/poc-out/units-k12/{b}.json'
    if os.path.exists(uk):
        u = json.load(open(uk)); row['units_k12'] = dict(collections.Counter(x['role'] for x in u['units'])); row['units_k12_extractor'] = u.get('extractor')
    res[b] = row
json.dump(res, open(f'{OUT}/layout-gate.json', 'w'), ensure_ascii=False, indent=1)
for b, r in res.items():
    if 'pages' in r: print(f"{b:<32} pages {r['pages']:>3} trusted_pages {r['trusted_pages']:>3} ({r['trusted_page_share']}) blocks {r['blocks']} trusted_block_share {r['trusted_block_share']} units-layout {r.get('units_layout')} dropped {r.get('units_layout_dropped')}")
    else: print(b, r)
