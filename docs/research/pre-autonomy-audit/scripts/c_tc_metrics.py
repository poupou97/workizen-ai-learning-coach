#!/usr/bin/env python3
"""Pre-autonomy audit — S3: re-read TC-v1 / TC-v2 metric JSON and the 238 TSL documents;
verify the numbers quoted in docs (FTR 0.32 / 0.12 / 0.10-0.12, roles, TSL 238 = 2 FULL + 236 PARTIAL, SGV 0 trusted).
Writes data/tc-metrics.json."""
import json, glob, collections
ROOT = '/Users/alexnguyen/projects/workizen-ai-learning-coach'
OUT = f'{ROOT}/poc-out/audit/pre-autonomy/data'
TC1 = f'{ROOT}/poc-out/trusted-corpus/tc-v1/bakeoff'
TC2 = f'{ROOT}/poc-out/trusted-corpus/tc-v2/tc2-p1'
res = {}
KEEP = ('pages', 'learning_blocks', 'trusted', 'coverage', 'tlsr', 'false_trusted', 'ftr', 'safe_rejected', 'order', 'text_acc', 'fidelity', 'splices')
s = json.load(open(f'{TC1}/scores.json'))['aggregate']
res['tc_v1_single'] = {k: {kk: v.get(kk) for kk in KEEP} for k, v in s.items()}
res['tc_v1_single_keys'] = {k: sorted(v.keys()) for k, v in s.items()}
c = json.load(open(f'{TC1}/cascade.json'))['aggregate']
res['tc_v1_cascades'] = {k: {kk: v.get(kk) for kk in KEEP} for k, v in c.items()}
g = json.load(open(f'{TC2}/metrics/gold-scores.json'))['aggregate']
res['tc_v2_gold_raw_keys'] = {k: sorted(v.keys()) for k, v in g.items()}
res['tc_v2_gold'] = {}
for k, v in g.items():
    r = {kk: v.get(kk) for kk in KEEP}
    for extra in ('roles6', 'roles', 'role_pr', 'trusted_question_precision', 'trusted_question_n', 'attach_toc_ok', 'attach_header_ok', 'cte', 'cte_by_class', 'false_questions'):
        if extra in v:
            r[extra] = v[extra]
    res['tc_v2_gold'][k] = r
sl = json.load(open(f'{TC2}/metrics/slice-report.json'))
res['tc_v2_slice_keys'] = sorted(sl.keys())
res['tc_v2_slice'] = {k: sl[k] for k in sl if not isinstance(sl[k], list)}
sg = json.load(open(f'{TC2}/metrics/sgv-report.json'))
res['tc_v2_sgv_keys'] = sorted(sg.keys())
res['tc_v2_sgv'] = {k: sg[k] for k in sg if not isinstance(sg[k], list)}
# TSL documents re-counted
tsl = glob.glob(f'{TC2}/lessons/*/*.tsl.json')
srcb = collections.Counter(); roles = collections.Counter(); wh = collections.Counter(); per_book = collections.defaultdict(collections.Counter)
n_native = n_with = q_lessons = 0; ak_true = 0; header_src = collections.Counter(); withheld_text_nonnull = 0; withheld_per_lesson = []
for f in tsl:
    d = json.load(open(f)); srcb[d['sourceability']] += 1; per_book[d['book']][d['sourceability']] += 1
    n_native += len(d['blocks']); n_with += len(d['withheld']); header_src[d['boundary']['source']] += 1
    withheld_per_lesson.append(len(d['withheld']))
    for b in d['blocks']:
        roles[b['role']['value']] += 1
    for w in d['withheld']:
        for r in w['reasons']:
            wh[r] += 1
        if w.get('text') is not None:
            withheld_text_nonnull += 1
    if any(b['role']['value'] == 'question' for b in d['blocks']):
        q_lessons += 1
    ak_true += bool(d.get('answer_keys_included'))
withheld_per_lesson.sort()
res['tsl_recount'] = dict(documents=len(tsl), sourceability=dict(srcb), native_blocks=n_native, withheld_regions=n_with,
                          withheld_per_lesson_median=withheld_per_lesson[len(withheld_per_lesson) // 2] if withheld_per_lesson else None,
                          roles_trusted=dict(roles.most_common()), withheld_by_reason=dict(wh.most_common()),
                          lessons_with_trusted_question=q_lessons, answer_keys_included_true=ak_true, boundary_source=dict(header_src),
                          withheld_blocks_carrying_text=withheld_text_nonnull, per_book={b: dict(v) for b, v in sorted(per_book.items())})
# SDM slice pages re-count (SGK only)
sdm = glob.glob(f'{TC2}/sdm/*sgk*/*.sdm.json'); st = collections.Counter(); pages = 0; reasons = collections.Counter()
for f in sdm:
    d = json.load(open(f)); pages += 1
    for b in d['blocks']:
        if b.get('learning'):
            st[b['trust']['status']] += 1
            if b['trust']['status'] != 'TRUSTED':
                for r in b['trust'].get('reasons', []):
                    reasons[r] += 1
res['sdm_sgk_recount'] = dict(pages=pages, learning_blocks=sum(st.values()), by_status=dict(st), trusted_share=round(st['TRUSTED'] / max(1, sum(st.values())), 3), withheld_reasons=dict(reasons.most_common()))
sdm_sgv = glob.glob(f'{TC2}/sdm/*sgv*/*.sdm.json'); st2 = collections.Counter(); p2 = 0; learner_roles = collections.Counter()
for f in sdm_sgv:
    d = json.load(open(f)); p2 += 1
    for b in d['blocks']:
        if b.get('learning'):
            st2[b['trust']['status']] += 1
            if b['trust']['status'] == 'TRUSTED':
                learner_roles[b['role']['value']] += 1
res['sdm_sgv_recount'] = dict(pages=p2, learning_blocks=sum(st2.values()), by_status=dict(st2), trusted_roles=dict(learner_roles.most_common()))
json.dump(res, open(f'{OUT}/tc-metrics.json', 'w'), ensure_ascii=False, indent=1)
print('TC1 single', json.dumps(res['tc_v1_single'], ensure_ascii=False))
print('TC1 cascades', json.dumps(res['tc_v1_cascades'], ensure_ascii=False))
print('TC1 keys', res['tc_v1_single_keys'].get('current-xycut'))
print('TSL', json.dumps(res['tsl_recount'], ensure_ascii=False))
print('SDM SGK', json.dumps(res['sdm_sgk_recount'], ensure_ascii=False))
print('SDM SGV', json.dumps(res['sdm_sgv_recount'], ensure_ascii=False))
print('GOLD keys', res['tc_v2_gold_raw_keys']['science'])
for k, v in res['tc_v2_gold'].items():
    print('GOLD', k, {kk: v.get(kk) for kk in ('pages', 'trusted', 'false_trusted', 'ftr', 'tlsr', 'trusted_question_precision', 'trusted_question_n')})
print('SLICE keys', res['tc_v2_slice_keys']); print(json.dumps(res['tc_v2_slice'], ensure_ascii=False)[:2500])
print('SGV keys', res['tc_v2_sgv_keys']); print(json.dumps(res['tc_v2_sgv'], ensure_ascii=False)[:2000])
