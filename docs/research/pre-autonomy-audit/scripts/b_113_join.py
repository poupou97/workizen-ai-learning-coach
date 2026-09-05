#!/usr/bin/env python3
"""Pre-autonomy audit — S2: what the 113 proven lessons are built on, joined with TC-v2 block trust.
For every baseline lesson: which pack activity type(s) carry it and which extractor produced the text.
For the 37 khoaExperiments lessons in the six Science books that TC-v2 covered: match each experiment string
(title / Chuẩn bị / Tiến hành steps / Dự đoán / Quan sát) to the SDM-v2 blocks on the same PDF page and record
trust status + reasons; compare the pack's TOC-range lesson attribution with TC-v2 header-based attachment;
record the WAL-206 XY-cut page gate verdict on the same page. Writes data/113-join.json + data/113-join.md"""
import json, glob, os, re, collections, difflib
ROOT = '/Users/alexnguyen/projects/workizen-ai-learning-coach'
OUT = f'{ROOT}/poc-out/audit/pre-autonomy/data'
TC2 = f'{ROOT}/poc-out/trusted-corpus/tc-v2/tc2-p1'
SCIENCE = ['04-sgk-khoa-hoc-4', '05-sgk-khoa-hoc-5', '06-sgk-khoa-hoc-tu-nhien-6', '07-sgk-khoa-hoc-tu-nhien-7', '08-sgk-khoa-hoc-tu-nhien-8', '09-sgk-khoa-hoc-tu-nhien-9']
baseline = {tuple(x) for x in json.load(open(f'{ROOT}/poc-out/p0-experiment/baseline-learnable.json'))}
packs = {g: json.load(open(f'{ROOT}/assets/pack/lesson-index-g{g}.json')) for g in range(1, 13)}
EXTRACTOR = dict(EXPERIMENT='ocr-body naive line order (build_lesson_index.py Chuẩn bị/Tiến hành scan) = TC-v1 "current-naive", FTR 0.32 on hard pages',
                 READING='poc-out/units TV5 extractor (extract_units_tv, SECTION_TEXT >=400 chars + numbered EXERCISE) = naive line order',
                 WRITING='poc-out/units TV5 extractor (EXERCISE "Viết…") = naive line order',
                 SOURCE='ocr-body naive lines ("TƯ LIỆU" block + attribution) = naive line order',
                 TOAN_EXERCISE='poc-out/units/exercise-case-map.json (Toán 4-5 fraction expressions; page from footer)')
acts = collections.defaultdict(set); exps = []
for g, p in packs.items():
    for e in p['khoaExperiments']:
        k = (e['book'], e.get('lesson'))
        if k in baseline:
            acts[k].add('EXPERIMENT'); exps.append(e)
    for e in p['suSources']:
        k = (e['book'], e.get('lesson'))
        if k in baseline: acts[k].add('SOURCE')
    for key, tag in (('tvReadings', 'READING'), ('tvWritings', 'WRITING')):
        for e in p[key]:
            if str(e.get('source', '')).startswith('pattern-router'):
                continue
            k = (e['book'], e['lesson'])
            if k in baseline: acts[k].add(tag)
    for les, lst in p['toanExercises'].items():
        for e in lst:
            k = (e['book'], int(les))
            if k in baseline: acts[k].add('TOAN_EXERCISE')
by_type = collections.Counter()
for k in baseline:
    for t in acts.get(k, {'<none>'}): by_type[t] += 1
by_book = collections.Counter(k[0] for k in baseline)

def norm(t):
    return re.sub(r'\s+', ' ', (t or '').lower()).strip()
def sim(a, b):
    a, b = norm(a), norm(b)
    if not a or not b: return 0.0
    if a in b or b in a: return 1.0
    return difflib.SequenceMatcher(None, a, b).ratio()

attach_cache = {}
def attach_lesson(book, pdf):
    if book not in attach_cache:
        a = json.load(open(f'{TC2}/attach/{book}.json')); attach_cache[book] = {p['page']: p for p in a['pages']}
    return attach_cache[book].get(pdf)

rows = []; lesson_agg = collections.defaultdict(lambda: collections.Counter())
for e in exps:
    book, pdf, les = e['book'], e['pagePdf'], e['lesson']
    if book not in SCIENCE:
        rows.append(dict(book=book, lesson=les, pagePdf=pdf, covered_by_tc2=False)); continue
    sdm_path = f'{TC2}/sdm/{book}/p{pdf:03d}.sdm.json'
    if not os.path.exists(sdm_path):
        rows.append(dict(book=book, lesson=les, pagePdf=pdf, covered_by_tc2=False, note='no SDM page')); continue
    sdm = json.load(open(sdm_path)); blocks = [b for b in sdm['blocks'] if b.get('text')]
    strings = [('title', e.get('title')), ('chuanBi', e.get('chuanBi'))] + [('step', s) for s in e.get('tienHanh', [])] + [('duDoan', e.get('duDoan')), ('quanSat', e.get('quanSat'))]
    strings = [(k, s) for k, s in strings if s and len(norm(s)) >= 8]
    matches = []
    for kind, s in strings:
        best = max(blocks, key=lambda b: sim(s, b['text'])) if blocks else None
        r = sim(s, best['text']) if best else 0.0
        if best and r >= 0.5:
            matches.append(dict(kind=kind, ratio=round(r, 2), status=best['trust']['status'], reasons=best['trust'].get('reasons', []), role=best['role']['value'], block=best['id']))
        else:
            matches.append(dict(kind=kind, ratio=round(r, 2), status='UNMATCHED', reasons=[], role=None, block=None))
    st = collections.Counter(m['status'] for m in matches); reasons = collections.Counter(r for m in matches for r in m['reasons'])
    page_status = collections.Counter(b['trust']['status'] for b in sdm['blocks'] if b.get('learning'))
    at = attach_lesson(book, pdf)
    lay_path = f'{ROOT}/poc-out/layout/{book}/p{pdf:03d}.json'
    lay = json.load(open(lay_path))['layout'] if os.path.exists(lay_path) else None
    row = dict(book=book, lesson=les, pagePdf=pdf, covered_by_tc2=True, n_strings=len(strings), match_status=dict(st), match_reasons=dict(reasons),
               page_learning_blocks=dict(page_status), tc2_attach_lesson=at.get('lesson') if at else None, tc2_attach_method=at.get('method') if at else None,
               attach_agrees=(at.get('lesson') == les) if at else None, xycut_page_trusted=(lay or {}).get('trusted'), xycut_marginal_cuts=len((lay or {}).get('marginalCuts') or []),
               matches=matches)
    rows.append(row)
    L = lesson_agg[(book, les)]; L['experiments'] += 1; L['strings'] += len(strings)
    for k, v in st.items(): L[f'str_{k}'] += v
    L['exp_with_withheld_or_conflict'] += any(m['status'] in ('WITHHELD', 'CONFLICT') for m in matches)
    L['exp_attach_disagree'] += (at is not None and at.get('lesson') != les)
    L['exp_page_xycut_untrusted'] += (lay is not None and not lay.get('trusted'))
    L['page_has_withheld'] += (page_status.get('WITHHELD', 0) + page_status.get('CONFLICT', 0)) > 0

covered = [r for r in rows if r.get('covered_by_tc2')]
tot = collections.Counter()
for r in covered:
    for k, v in r['match_status'].items(): tot[k] += v
    for k, v in r['match_reasons'].items(): tot['reason:' + k] += v
    tot['experiments'] += 1; tot['attach_agree'] += bool(r['attach_agrees']); tot['attach_disagree'] += (r['attach_agrees'] is False)
    tot['xycut_page_trusted'] += bool(r['xycut_page_trusted']); tot['xycut_page_untrusted'] += (r['xycut_page_trusted'] is False)
lessons_cov = len(lesson_agg)
lessons_clean = sum(1 for L in lesson_agg.values() if L['exp_with_withheld_or_conflict'] == 0 and L['str_UNMATCHED'] == 0)
lessons_withheld = sum(1 for L in lesson_agg.values() if L['exp_with_withheld_or_conflict'] > 0)
lessons_attach_disagree = sum(1 for L in lesson_agg.values() if L['exp_attach_disagree'] > 0)
lessons_xycut_untrusted = sum(1 for L in lesson_agg.values() if L['exp_page_xycut_untrusted'] > 0)
lessons_unmatched = sum(1 for L in lesson_agg.values() if L['str_UNMATCHED'] > 0)

# figures / tables / formulas in TSL (support question 5)
fig = tab = 0; formula_role = 0
for f in glob.glob(f'{TC2}/lessons/*/*.tsl.json'):
    d = json.load(open(f)); fig += len(d.get('figures', [])); tab += sum(1 for b in d['blocks'] if b['role']['value'] == 'table'); formula_role += sum(1 for b in d['blocks'] if b['role']['value'] == 'formula')

out = dict(script='b_113_join.py', baseline=len(baseline), by_activity_type=dict(by_type), extractor_per_type=EXTRACTOR, by_book=dict(by_book),
           experiments_in_baseline=len(exps), experiments_covered_by_tc2=len(covered),
           string_match_totals=dict(tot), lessons=dict(covered=lessons_cov, all_strings_matched_and_trusted=lessons_clean, with_any_withheld_or_conflict_string=lessons_withheld,
           with_unmatched_string=lessons_unmatched, tc2_header_attach_disagrees=lessons_attach_disagree, on_xycut_untrusted_page=lessons_xycut_untrusted),
           per_lesson={f'{b}|{l}': dict(v) for (b, l), v in sorted(lesson_agg.items())}, rows=rows,
           tsl_objects=dict(figures=fig, table_blocks_trusted=tab, formula_blocks_trusted=formula_role))
json.dump(out, open(f'{OUT}/113-join.json', 'w'), ensure_ascii=False, indent=1)
md = ['# 113 proven lessons — extractor and TC-v2 trust join (MEASURED, scripts/b_113_join.py)', '',
      f'Baseline 113 by activity type (multi-label): {dict(by_type)}', '', 'Extractor per type:'] + [f'- {k}: {v}' for k, v in EXTRACTOR.items()] + ['',
      f'khoaExperiments entries carrying baseline lessons: {len(exps)}; covered by TC-v2 SDM (six Science books): {len(covered)}', '',
      f'String-level: {dict(tot)}', '',
      f'Lesson-level (TC-v2-covered): covered {lessons_cov}; all strings matched AND trusted {lessons_clean}; >=1 string WITHHELD/CONFLICT {lessons_withheld}; >=1 string unmatched {lessons_unmatched}; TC-v2 header attachment disagrees with pack lesson {lessons_attach_disagree}; experiment page fails WAL-206 XY-cut page gate {lessons_xycut_untrusted}', '',
      '| book | lesson | pdf page | strings | trusted | withheld | conflict | unmatched | reasons | tc2 lesson (method) | agrees | xycut page trusted |', '|---|---|---|---|---|---|---|---|---|---|---|---|']
for r in covered:
    s = r['match_status']
    md.append(f"| {r['book']} | {r['lesson']} | {r['pagePdf']} | {r['n_strings']} | {s.get('TRUSTED',0)} | {s.get('WITHHELD',0)} | {s.get('CONFLICT',0)} | {s.get('UNMATCHED',0)} | {r['match_reasons']} | {r['tc2_attach_lesson']} ({r['tc2_attach_method']}) | {r['attach_agrees']} | {r['xycut_page_trusted']} |")
open(f'{OUT}/113-join.md', 'w').write('\n'.join(md) + '\n')
print(json.dumps({k: out[k] for k in ('baseline', 'by_activity_type', 'by_book', 'experiments_in_baseline', 'experiments_covered_by_tc2', 'string_match_totals', 'lessons', 'tsl_objects')}, ensure_ascii=False, indent=1))
for k, v in out['per_lesson'].items():
    if v.get('exp_with_withheld_or_conflict') or v.get('exp_attach_disagree') or v.get('str_UNMATCHED'):
        print('LESSON', k, dict(v))
print('--- attach disagreements / withheld examples ---')
for r in covered:
    if r['attach_agrees'] is False:
        print('ATTACH', r['book'], 'pack lesson', r['lesson'], 'pdf', r['pagePdf'], '-> tc2', r['tc2_attach_lesson'], r['tc2_attach_method'])
    for m in r['matches']:
        if m['status'] in ('WITHHELD', 'CONFLICT'):
            print('WITHHELD', r['book'], r['lesson'], r['pagePdf'], m['kind'], m['status'], m['reasons'], m['role'], m['ratio'])
