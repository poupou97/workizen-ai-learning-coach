#!/usr/bin/env python3
"""TC-v1 — census report: feature matrix, overlaps, layout families, lesson impact.

Reads poc-out/trusted-corpus/<ver>/census/pages.jsonl (tc_layout_census.py)
and curriculum-structure.json; writes summary.json + summary.md next to it.

Rules: features overlap — every table reports "pages carrying feature X"
with the denominator, never a sum across features. A page's LAYOUT FAMILY
is the sorted set of its features (sparse pages form their own family).
Lesson impact uses SGK lessons with a page range (pageStart → next
lesson's pageStart − 1, last lesson → end of book).
"""
import argparse
import json
import os
from collections import Counter, defaultdict

ROOT = os.environ.get('TC_ROOT', '/Users/alexnguyen/projects/workizen-ai-learning-coach')
FEATS = ['sparse', 'two_col', 'three_col', 'side_by_side', 'table', 'formula', 'sidebar', 'figure', 'diagram', 'colored_box', 'color_heavy', 'continuation', 'overlap', 'low_conf', 'mixed', 'native_text']


def feats_of(r):
    f = set()
    for k in FEATS:
        if k == 'two_col':
            if r.get('columns') == 2: f.add(k)
        elif k == 'three_col':
            if r.get('columns', 0) >= 3: f.add(k)
        elif r.get(k):
            f.add(k)
    return f


def family_of(fs):
    if 'sparse' in fs:
        return 'SPARSE/IMAGE-ONLY'
    core = []
    if 'three_col' in fs: core.append('3col')
    elif 'two_col' in fs: core.append('2col')
    else: core.append('1col')
    for k, tag in (('side_by_side', 'sbs'), ('table', 'table'), ('formula', 'formula'), ('sidebar', 'sidebar'), ('diagram', 'diagram'), ('figure', 'figure'), ('colored_box', 'box'), ('color_heavy', 'visual')):
        if k in fs and not (k == 'figure' and 'diagram' in fs):
            core.append(tag)
    return '+'.join(core)


def pct(a, b):
    return f'{100.0 * a / b:.1f}%' if b else 'n/a'


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--ver', default='tc-v1'); a = ap.parse_args()
    d = f'{ROOT}/poc-out/trusted-corpus/{a.ver}/census'
    rows = [json.loads(l) for l in open(f'{d}/pages.jsonl')]
    docs = {x['sourceDocumentId']: x for x in json.load(open(f'{ROOT}/poc-out/graph/curriculum-structure.json'))['documents']}
    for r in rows:
        r['_f'] = feats_of(r); r['_fam'] = family_of(r['_f'])
        m = docs.get(r['book'], {})
        r['_grade'] = m.get('grade'); r['_subject'] = m.get('subject'); r['_doc'] = m.get('docType')
    N = len(rows)
    nonsparse = [r for r in rows if 'sparse' not in r['_f']]
    out = dict(pages=N, documents=len(set(r['book'] for r in rows)), nonsparse=len(nonsparse),
               errors=sum(1 for r in rows if r.get('error') or r.get('render_error')))
    feat_counts = {k: sum(1 for r in rows if k in r['_f']) for k in FEATS}
    out['feature_pages'] = feat_counts
    out['columns'] = dict(Counter(str(r.get('columns')) for r in rows))
    # overlaps: pairwise co-occurrence among non-sparse pages
    pair = {}
    keys = ['two_col', 'side_by_side', 'table', 'formula', 'sidebar', 'figure', 'diagram', 'colored_box', 'color_heavy']
    for i, k1 in enumerate(keys):
        for k2 in keys[i + 1:]:
            pair[f'{k1}&{k2}'] = sum(1 for r in nonsparse if k1 in r['_f'] and k2 in r['_f'])
    out['overlaps'] = pair
    out['features_per_page'] = dict(Counter(min(6, len(r['_f'] - {'continuation', 'mixed', 'native_text', 'overlap', 'low_conf'})) for r in nonsparse))
    fam = Counter(r['_fam'] for r in rows)
    out['families'] = fam.most_common()
    cum, acc = [], 0
    for f, c in fam.most_common():
        acc += c; cum.append((f, c, round(100.0 * acc / N, 1)))
    out['families_cumulative'] = cum
    # breakdowns
    def breakdown(keyf):
        g = defaultdict(lambda: Counter())
        for r in rows:
            k = keyf(r); g[k]['pages'] += 1
            for f in r['_f']: g[k][f] += 1
        return {str(k): dict(v) for k, v in sorted(g.items(), key=lambda kv: str(kv[0]))}
    out['by_grade'] = breakdown(lambda r: r['_grade'])
    out['by_subject'] = breakdown(lambda r: r['_subject'])
    out['by_doctype'] = breakdown(lambda r: r['_doc'])
    out['by_book'] = breakdown(lambda r: r['book'])
    # lesson impact (SGK lessons with page ranges)
    pages_by_book = defaultdict(dict)
    for r in rows:
        pages_by_book[r['book']][r['page']] = r
    lesson_total = lesson_ranged = 0
    lesson_feat = Counter(); lesson_clean = 0; lesson_fam = Counter()
    for bid, m in docs.items():
        if m.get('docType') != 'SGK':
            continue
        ls = sorted([l for l in m.get('lessons', []) if l.get('pageStart')], key=lambda l: l['pageStart'])
        lesson_total += len(m.get('lessons', []))
        pb = pages_by_book.get(bid, {})
        last = max(pb) if pb else 0
        for i, l in enumerate(ls):
            p0 = l['pageStart']; p1 = (ls[i + 1]['pageStart'] - 1) if i + 1 < len(ls) else last
            if p1 < p0: p1 = p0
            lesson_ranged += 1
            fs = set()
            for p in range(p0, p1 + 1):
                if p in pb: fs |= pb[p]['_f']
            for f in fs: lesson_feat[f] += 1
            hard = fs & {'two_col', 'three_col', 'side_by_side', 'table', 'formula', 'sidebar', 'diagram', 'colored_box', 'color_heavy', 'overlap', 'low_conf'}
            if not hard: lesson_clean += 1
            lesson_fam[','.join(sorted(hard)) or 'plain'] += 1
    out['lessons'] = dict(sgk_total=lesson_total, with_page_range=lesson_ranged, containing_feature=dict(lesson_feat), plain_only=lesson_clean, hard_feature_sets=lesson_fam.most_common(25))
    json.dump(out, open(f'{d}/summary.json', 'w'), ensure_ascii=False, indent=1)
    # markdown
    L = [f'# TC-v1 K-12 layout census — {N:,} pages / {out["documents"]} documents (MEASURED)', '',
         f'Non-sparse pages: {len(nonsparse):,} ({pct(len(nonsparse), N)}). Render/parse errors: {out["errors"]}.', '',
         '## Pages carrying each feature (overlapping — do NOT sum)', '', '| feature | pages | % of all pages | % of non-sparse |', '|---|---|---|---|']
    for k in FEATS:
        L.append(f'| {k} | {feat_counts[k]:,} | {pct(feat_counts[k], N)} | {pct(feat_counts[k], len(nonsparse)) if k != "sparse" else "—"} |')
    L += ['', '## Column count (non-sparse pages)', '', '| columns | pages |', '|---|---|'] + [f'| {k} | {v:,} |' for k, v in sorted(out['columns'].items())]
    L += ['', '## Pairwise overlaps (non-sparse pages carrying BOTH features)', '', '| pair | pages |', '|---|---|'] + [f'| {k} | {v:,} |' for k, v in sorted(pair.items(), key=lambda kv: -kv[1])[:20]]
    L += ['', '## Number of hard features per non-sparse page', '', '| features | pages |', '|---|---|'] + [f'| {k} | {v:,} |' for k, v in sorted(out['features_per_page'].items())]
    L += ['', '## Layout families (signature = set of features; cumulative share of ALL pages)', '', '| family | pages | cumulative % |', '|---|---|---|'] + [f'| {f} | {c:,} | {cp} |' for f, c, cp in cum[:40]]
    L.append(f'\nDistinct families: {len(fam)}; families covering 80 % of pages: {next((i + 1 for i, (_, _, cp) in enumerate(cum) if cp >= 80), len(cum))}; 90 %: {next((i + 1 for i, (_, _, cp) in enumerate(cum) if cp >= 90), len(cum))}; 95 %: {next((i + 1 for i, (_, _, cp) in enumerate(cum) if cp >= 95), len(cum))}.')
    for title, key in (('grade', 'by_grade'), ('subject', 'by_subject'), ('docType', 'by_doctype')):
        L += ['', f'## By {title} (pages carrying feature; overlapping)', '', '| ' + title + ' | pages | sparse | 2col | 3col | side-by-side | table | formula | sidebar | figure | diagram | colored_box | color_heavy |', '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
        for k, v in out[key].items():
            L.append(f'| {k} | {v["pages"]:,} | ' + ' | '.join(pct(v.get(f, 0), v['pages']) for f in ('sparse', 'two_col', 'three_col', 'side_by_side', 'table', 'formula', 'sidebar', 'figure', 'diagram', 'colored_box', 'color_heavy')) + ' |')
    lz = out['lessons']
    L += ['', '## SGK lesson impact (lessons with a page range; a lesson "contains" a feature if ≥ 1 page in its range carries it)', '',
          f'SGK lessons: {lz["sgk_total"]:,}; with page range: {lz["with_page_range"]:,}; range with NO hard feature on any page: {lz["plain_only"]:,} ({pct(lz["plain_only"], lz["with_page_range"])}).', '',
          '| feature | lessons containing ≥1 such page | % of ranged lessons |', '|---|---|---|']
    for f, c in sorted(lz['containing_feature'].items(), key=lambda kv: -kv[1]):
        L.append(f'| {f} | {c:,} | {pct(c, lz["with_page_range"])} |')
    L += ['', '| hard-feature set of the lesson range | lessons |', '|---|---|'] + [f'| {k} | {v:,} |' for k, v in lz['hard_feature_sets']]
    open(f'{d}/summary.md', 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L[:60]))


if __name__ == '__main__':
    main()
