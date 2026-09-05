#!/usr/bin/env python3
"""LANE C — per-subject-family census: what dominates outside Science?

For each family (science · history_geo · math · language · informatics ·
english · primary_1_3 · other) this script MEASURES, from data already on
disk (no reprocess):
  1. curriculum: canonical / ranged lessons, TOC health of the books;
  2. activity directives: the 27-pattern labels of fable-taxonomy.json
     (old-extractor units — a pipeline property, TC-15; ranks shapes only);
  3. layout hard features on SGK pages (TC-v1 census pages.jsonl);
  4. lexical SHAPE markers over units-k12 SGK units (HYPOTHESIS: which
     SemanticData shape the family's activities point at — timeline, source,
     map, table, steps, comparison, math…);
  5. the only trust numbers outside Science: the TC-v2 gold rows on
     non-Science pages (gold-scores.json, n is tiny);
  6. SGV availability: books with an SGV units file; SGK lessons with SGV
     markers (sgk-lessons-with-sgv.json);
  7. pack wiring: lessons with any Surface entry in assets/pack.

Read-only. Writes poc-out/round3/lane-c/subject-family-census.{json,md}.
"""
import argparse
import glob
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import FAMILY_ORDER, dump, family_of, load_census_pages, load_curriculum, load_pack_index, pct, root, shape_hits, write_md  # noqa: E402

FEATURES = ['formula', 'table', 'diagram', 'sidebar', 'side_by_side', 'color_heavy', 'figure', 'colored_box', 'two_col', 'continuation']
PACK_KEYS = ['toanExercises', 'tvReadings', 'tvWritings', 'suSources', 'khoaExperiments', 'diaMaps']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default=root())
    a = ap.parse_args()
    R = a.root
    docs = load_curriculum(R)
    sgk = {k: d for k, d in docs.items() if d.get('docType') == 'SGK'}
    fam_of_book = {k: family_of(d) for k, d in sgk.items()}

    # 1. curriculum
    cur = defaultdict(lambda: Counter())
    for k, d in sgk.items():
        f = fam_of_book[k]
        cur[f]['books'] += 1
        cur[f]['canonical'] += d.get('lessonCount') or 0
        cur[f]['ranged'] += sum(1 for l in d.get('lessons') or [] if l.get('pageStart') is not None)
        cur[f]['toc_' + str(d.get('structureStatus'))] += 1
        cur[f]['lessons_missing_page'] += d.get('lessonsMissingPage') or 0

    # 2. patterns (fable-taxonomy labels, keyed book|lesson)
    tax = json.load(open(os.path.join(R, 'poc-out/k12-census-exports/fable-taxonomy.json')))
    pat = defaultdict(Counter)
    prim = defaultdict(Counter)
    labelled = Counter()
    for key, labels in tax['labels'].items():
        book = key.split('|')[0]
        f = fam_of_book.get(book)
        if f is None:
            continue
        labelled[f] += 1
        for l in labels:
            pat[f][l] += 1
        prim[f][tax['primary'].get(key, '—')] += 1

    # 3. layout features on SGK pages
    pages = load_census_pages(R, books=set(sgk))
    lay = defaultdict(Counter)
    for row in pages:
        f = fam_of_book[row['book']]
        lay[f]['pages'] += 1
        for feat in FEATURES:
            if row.get(feat):
                lay[f][feat] += 1
        if not any(row.get(x) for x in ('formula', 'table', 'diagram', 'color_heavy', 'three_col')):
            lay[f]['no_unhandled_feature'] += 1

    # 4. lexical shape markers over units-k12 SGK units with a lesson
    shp = defaultdict(Counter)
    for fp in glob.glob(os.path.join(R, 'poc-out/units-k12/*-sgk-*.json')):
        j = json.load(open(fp))
        book = j['sourceDocumentId']
        f = fam_of_book.get(book)
        if f is None:
            continue
        for u in j['units']:
            if u.get('lesson') is None or u.get('role') == 'SECTION_TEXT':
                continue
            shp[f]['units'] += 1
            for h in shape_hits(u.get('text') or ''):
                shp[f][h] += 1

    # 5. gold rows outside Science (tc-v2 scorer)
    gs = json.load(open(os.path.join(R, 'poc-out/trusted-corpus/tc-v2/tc2-p1/metrics/gold-scores.json')))
    gold = defaultdict(list)
    for row in gs['rows']:
        book = row['book']
        d = docs.get(book) or {}
        f = 'sgv' if d.get('docType') == 'SGV' or '-sgv-' in book else family_of(d) if d else 'other'
        gold[f].append({
            'page': f'{book} p{row["page"]:03d}', 'tlsr': row.get('tlsr'), 'ftr': row.get('ftr'),
            'trusted': row.get('trusted_blocks'), 'false_trusted': row.get('false_trusted'),
            'question_p': row.get('question_p'), 'question_gold': row.get('question_gold'),
            'order': row.get('order'), 'text_acc': row.get('text_acc'), 'lesson_attach': row.get('lesson_attach'),
            'meaning_inversions': row.get('order_meaning_inversions'),
        })

    # 6. SGV availability
    sgv_files = {os.path.basename(p)[:-5] for p in glob.glob(os.path.join(R, 'poc-out/units-k12/*-sgv-*.json'))}
    with_sgv = json.load(open(os.path.join(R, 'poc-out/k12-census-exports/sgk-lessons-with-sgv.json')))
    sgv = defaultdict(Counter)
    for k, d in sgk.items():
        f = fam_of_book[k]
        stem = k.replace('-sgk-', '-sgv-')
        # tập một / tập hai SGK often share one SGV
        base = stem.split('-tap-')[0]
        if stem in sgv_files or any(s.startswith(base) for s in sgv_files):
            sgv[f]['books_with_sgv_units'] += 1
    for key, markers in with_sgv.items():
        book = key.split('|')[0]
        f = fam_of_book.get(book)
        if f is None:
            continue
        sgv[f]['lessons_with_sgv_markers'] += 1
        if markers.get('answer') or markers.get('expected'):
            sgv[f]['lessons_with_answer_or_expected_marker'] += 1
        if markers.get('objective'):
            sgv[f]['lessons_with_objective_marker'] += 1

    # 7. pack wiring
    wired = defaultdict(Counter)
    wired_lessons = defaultdict(set)
    for g in range(1, 13):
        p = load_pack_index(g, R)
        if not p:
            continue
        for key in PACK_KEYS:
            for e in p.get(key) or []:
                if not isinstance(e, dict):  # some packs carry bare ids (e.g. toanExercises)
                    wired['_non_dict_entries'][key] += 1
                    continue
                book = e.get('book') or e.get('sourceDocumentId')
                f = fam_of_book.get(book)
                if f is None:
                    continue
                wired[f][key] += 1
                wired_lessons[f].add((book, e.get('lesson') or e.get('lessonNo')))
    for f in wired_lessons:
        wired[f]['lessons_with_any_entry'] = len(wired_lessons[f])

    out = {}
    for f in FAMILY_ORDER:
        c = cur[f]
        L = lay[f]
        s = shp[f]
        out[f] = {
            'curriculum': dict(c),
            'patterns_top10(unique lessons; old-extractor labels — DOC-CLAIM/pipeline property)': pat[f].most_common(10),
            'primary_pattern_top6': prim[f].most_common(6),
            'lessons_labelled': labelled[f],
            'layout_pages': L['pages'],
            'layout_feature_pct': {k: pct(L[k], L['pages']) for k in FEATURES + ['no_unhandled_feature']},
            'shape_markers_units': s['units'],
            'shape_markers_pct(HYPOTHESIS)': {k: pct(s[k], s['units']) for k in sorted(s) if k != 'units'},
            'gold_pages_tc2': gold.get(f, []),
            'sgv': dict(sgv[f]),
            'pack_wiring': dict(wired[f]),
        }
    out['_sgv_gold_pages'] = gold.get('sgv', [])
    dump(out, 'subject-family-census.json', R)

    md = ['# Subject-family census (MEASURED unless marked)', '',
          'Denominators: canonical lessons = `lessonCount` per SGK book (sums to 3,679 corpus-wide); ranged = lessons with a TOC `pageStart`; pages = SGK pages in the TC-v1 census; units = units-k12 SGK units with a lesson (old extractor). Pattern labels are the WAL-203 registry labels on old-extractor units — they rank shapes, they do not size them (TC-15).', '',
          '| family | books | canonical | ranged | TOC OK / PARTIAL / NO_TOC | missing pageStart | labelled lessons | top patterns (unique lessons) |', '|---|---|---|---|---|---|---|---|']
    for f in FAMILY_ORDER:
        c = cur[f]
        top = ', '.join(f'{p} {n}' for p, n in pat[f].most_common(6))
        md.append(f'| {f} | {c["books"]} | {c["canonical"]} | {c["ranged"]} | {c["toc_OK"]} / {c["toc_PARTIAL"]} / {c["toc_NO_TOC"]} | {c["lessons_missing_page"]} | {labelled[f]} | {top} |')
    md += ['', '## Layout hard features on SGK pages (% of the family\'s pages; overlapping)', '', '| family | pages | formula | table | diagram | sidebar | side-by-side | colour-heavy | figure | coloured box | no unhandled feature |', '|---|---|---|---|---|---|---|---|---|---|---|']
    for f in FAMILY_ORDER:
        L = lay[f]
        md.append('| ' + ' | '.join([f, str(L['pages'])] + [str(pct(L[k], L['pages'])) for k in ['formula', 'table', 'diagram', 'sidebar', 'side_by_side', 'color_heavy', 'figure', 'colored_box', 'no_unhandled_feature']]) + ' |')
    keys = ['timeline_year', 'source_text', 'map_spatial', 'figure_ref', 'table_ref', 'process_steps', 'compare', 'cause_why', 'definition', 'math_ops', 'write', 'read_aloud', 'mcq_options', 'blank', 'oral']
    md += ['', '## Lexical shape markers in activity units (% of units; HYPOTHESIS — a marker says the unit points at a shape, not that the shape is extractable)', '', '| family | units | ' + ' | '.join(keys) + ' |', '|---|---|' + '---|' * len(keys)]
    for f in FAMILY_ORDER:
        s = shp[f]
        md.append('| ' + ' | '.join([f, str(s['units'])] + [str(pct(s[k], s['units'])) for k in keys]) + ' |')
    md += ['', '## TC-v2 gold pages outside the Science slice (the only measured trust numbers there; n is tiny)', '', '| family | page | trusted | false-trusted | TLSR | FTR | question P (gold n) | order | text acc | meaning inversions | lesson attach |', '|---|---|---|---|---|---|---|---|---|---|---|']
    for f in FAMILY_ORDER + ['sgv']:
        for g in (gold.get(f) or []):
            if f == 'science':
                continue
            md.append(f'| {f} | {g["page"]} | {g["trusted"]} | {g["false_trusted"]} | {g["tlsr"]} | {g["ftr"]} | {g["question_p"]} ({g["question_gold"]}) | {g["order"]} | {g["text_acc"]} | {g["meaning_inversions"]} | {g["lesson_attach"]} |')
    md += ['', '## SGV availability and pack wiring', '', '| family | SGK books with an SGV units file | SGK lessons with SGV markers | …with answer/expected marker | …with objective marker | pack entries | lessons with any pack entry |', '|---|---|---|---|---|---|---|']
    for f in FAMILY_ORDER:
        s = sgv[f]
        w = wired[f]
        entries = ', '.join(f'{k} {w[k]}' for k in PACK_KEYS if w[k])
        md.append(f'| {f} | {s["books_with_sgv_units"]} / {cur[f]["books"]} | {s["lessons_with_sgv_markers"]} | {s["lessons_with_answer_or_expected_marker"]} | {s["lessons_with_objective_marker"]} | {entries or "—"} | {w["lessons_with_any_entry"]} |')
    md.append('')
    p = write_md('\n'.join(md), 'subject-family-census.md', R)
    print(open(p).read())


if __name__ == '__main__':
    main()
