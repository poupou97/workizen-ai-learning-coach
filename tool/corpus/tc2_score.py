#!/usr/bin/env python3
"""TC-v2 — score the SDM-v2 pipeline on the gold set: TC-v1 metrics (unchanged scorer) + the Role Layer
per fine role (the Founder's six: QUESTION · ANSWER · ACTIVITY · INSTRUCTION · OBJECTIVE · SIDEBAR, plus
the rest) + lesson attachment (TOC range vs header-based).

Sets: dev = the 38 TC-v1 gold pages (guards/lexicon were calibrated on them) · heldout = the 16 TC-v2 pages
(written before any tc-v2 gate was scored on them) · science = every gold page from the six slice books or
their SGV counterparts · all.

Role scoring: the gold block ↔ pipeline block matching is tc_score.match (anchor prefix, then bbox). A
pipeline role is a true positive when the gold role maps to it (GOLD→canonical, PIPE→canonical). On an SGV
page a gold `question` is a quoted teacher prompt: the pipeline is expected to say TEACHER_PROMPT, and a
QUESTION there is counted as a false question. Precision = TP / pipeline blocks of that role among matched
blocks; recall = TP / gold blocks of that role among matched blocks (as TC-07 did); unmatched pipeline
blocks are reported separately. `q_trusted_precision` = precision of TRUSTED QUESTION blocks (what a
Short-Answer surface would consume).

Usage: <venv python> tool/corpus/tc2_score.py --pipeline tc2-p1 [--json out] [--md out]
"""
import argparse
import glob
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tc_sdm  # noqa: E402
import tc_score  # noqa: E402
import tc2_sdm  # noqa: E402
import tc2_attach  # noqa: E402
import tc2_paths  # noqa: E402

ROOT = tc_sdm.ROOT
SLICE = set(tc2_sdm.__dict__.get('SLICE_BOOKS', [])) or {'04-sgk-khoa-hoc-4', '05-sgk-khoa-hoc-5', '06-sgk-khoa-hoc-tu-nhien-6', '07-sgk-khoa-hoc-tu-nhien-7', '08-sgk-khoa-hoc-tu-nhien-8', '09-sgk-khoa-hoc-tu-nhien-9'}
SCIENCE = SLICE | {b.replace('-sgk-', '-sgv-') for b in SLICE}
SIX = ['QUESTION', 'ANSWER', 'ACTIVITY', 'INSTRUCTION', 'OBJECTIVE', 'SIDEBAR']
OTHER = ['HEADING', 'BODY', 'CAPTION', 'OPTION', 'ANSWER_SLOT', 'TABLE', 'FORMULA', 'FOOTNOTE', 'FIGURE_TEXT', 'PAGENUM', 'TEACHER_PROMPT']

GOLD_CANON = {'question': 'QUESTION', 'answer': 'ANSWER', 'activity': 'ACTIVITY', 'instruction': 'INSTRUCTION', 'objective': 'OBJECTIVE', 'sidebar': 'SIDEBAR',
              'heading': 'HEADING', 'running_head': 'HEADING', 'body': 'BODY', 'rule': 'BODY', 'attribution': 'BODY', 'speech_bubble': 'BODY',
              'caption': 'CAPTION', 'option': 'OPTION', 'answer_slot': 'ANSWER_SLOT', 'table': 'TABLE', 'formula': 'FORMULA', 'footnote': 'FOOTNOTE',
              'figure_label': 'FIGURE_TEXT', 'diagram': 'FIGURE_TEXT', 'page_number': 'PAGENUM'}
PIPE_CANON = {'question': 'QUESTION', 'answer': 'ANSWER', 'model_answer': 'ANSWER', 'activity': 'ACTIVITY', 'instruction': 'INSTRUCTION', 'objective': 'OBJECTIVE', 'sidebar': 'SIDEBAR',
              'heading': 'HEADING', 'stage_label': 'HEADING', 'running_head': 'HEADING', 'body': 'BODY', 'teacher_text': 'BODY', 'rule': 'BODY', 'teacher_prompt': 'TEACHER_PROMPT',
              'caption': 'CAPTION', 'option': 'OPTION', 'answer_slot': 'ANSWER_SLOT', 'table': 'TABLE', 'formula': 'FORMULA', 'footnote': 'FOOTNOTE',
              'figure_text': 'FIGURE_TEXT', 'figure': 'FIGURE_TEXT', 'page_number': 'PAGENUM', 'empty': 'EMPTY'}


def gold_canon(g, sgv):
    c = GOLD_CANON.get(g['role'], 'BODY')
    if sgv and c == 'QUESTION':
        return 'TEACHER_PROMPT'
    return c


def score_page(gold, sdm, attach_rec):
    v1 = tc2_sdm.to_v1_sdm(sdm)
    r = tc_score.score(gold, v1)
    sgv = '-sgv-' in gold['book']
    m = tc_score.match(gold, v1)
    tp = Counter(); pred = Counter(); goldc = Counter(); q_trusted = Counter(); confusion = Counter(); false_q = []
    matched_ids = set()
    for g in gold['blocks']:
        gc = gold_canon(g, sgv)
        c = m.get(g['id'])
        if not c:
            continue
        matched_ids.add(c['id'])
        pc = PIPE_CANON.get(c.get('fine_role'), 'BODY')
        goldc[gc] += 1; pred[pc] += 1
        if pc == gc:
            tp[pc] += 1
        else:
            confusion[(gc, pc)] += 1
        if pc == 'QUESTION':
            trusted = c.get('trusted') is True
            fig = 'figure_dependent' in (c.get('reasons') or [])
            if trusted:
                q_trusted['pred'] += 1; q_trusted['tp'] += (gc == 'QUESTION')
            if gc != 'QUESTION':
                false_q.append((g['id'], g['role'], c['text'][:70], 'TRUSTED' if trusted else 'withheld'))
    unmatched = Counter(PIPE_CANON.get(b.get('fine_role'), 'BODY') for b in v1['blocks'] if b['id'] not in matched_ids and b['text'] and len(b['text']) >= 12)
    r['roles6'] = dict(tp=dict(tp), pred=dict(pred), gold=dict(goldc), confusion={f'{a}->{b}': n for (a, b), n in confusion.items()}, q_trusted=dict(q_trusted), false_questions=false_q[:8], unmatched_pipeline=dict(unmatched))
    # attachment: header-based vs gold
    gl = gold.get('lesson', {}).get('number')
    if attach_rec is not None:
        hl, method = attach_rec.get('lesson'), attach_rec.get('method')
        r['attach_header'] = dict(lesson=hl, method=method, kind=attach_rec.get('kind'), ok=(hl == gl))
    else:
        r['attach_header'] = dict(lesson=None, method='no-attach-data', ok=None)
    r['attach_toc_ok'] = (r['lesson_toc'] == gl)
    r['gold_set'] = gold.get('gold_set', 'tc-v1'); r['held_out'] = bool(gold.get('held_out'))
    r['trust_reasons'] = dict(Counter(x for b in v1['blocks'] for x in (b.get('reasons') or []) if b['text']))
    r['blocks_trusted_all'] = sum(1 for b in v1['blocks'] if b.get('trusted') is True and b['text'])
    r['blocks_withheld_all'] = sum(1 for b in v1['blocks'] if b.get('trusted') is False and b['text'])
    return r


def aggregate(rows, name):
    rs = [r for r in rows if not r.get('error') and 'tlsr' in r]
    if not rs:
        return dict(name=name, pages=0)
    L = sum(r['learning_blocks'] for r in rs); T = sum(r['trusted_blocks'] for r in rs); W = sum(r['false_trusted'] for r in rs)

    def mean(k):
        v = [r[k] for r in rs if r.get(k) is not None]
        return round(sum(v) / len(v), 3) if v else None
    cte = Counter()
    for r in rs:
        cte.update({k: v for k, v in r['cte'].items()})
    tp = Counter(); pred = Counter(); goldc = Counter(); qt = Counter(); conf = Counter(); unm = Counter()
    for r in rs:
        s = r['roles6']; tp.update(s['tp']); pred.update(s['pred']); goldc.update(s['gold']); qt.update(s['q_trusted']); conf.update(s['confusion']); unm.update(s['unmatched_pipeline'])
    roles = {}
    for k in SIX + OTHER:
        roles[k] = dict(p=round(tp[k] / pred[k], 3) if pred[k] else None, r=round(tp[k] / goldc[k], 3) if goldc[k] else None, tp=tp[k], pred=pred[k], gold=goldc[k])
    reasons = Counter()
    for r in rs:
        reasons.update(r['trust_reasons'])
    att_h = [r['attach_header']['ok'] for r in rs if r['attach_header']['ok'] is not None]
    return dict(name=name, pages=len(rs), learning_blocks=L, trusted=T, coverage=round(T / max(1, L), 3), tlsr=round(sum(r['tlsr'] * r['learning_blocks'] for r in rs) / max(1, L), 3),
                false_trusted=W, ftr=round(W / max(1, T), 4), safe_rejected=sum(r['safe_rejected'] for r in rs), wrong_kinds=dict(Counter(k for r in rs for _, ks in r['wrong_examples'] for k in ks)),
                found=mean('found'), order=mean('order'), meaning_inversions=sum(r['order_meaning_inversions'] for r in rs), text_acc=mean('text_acc'), cer_notone=mean('cer_notone'), cer_nodiacritic=mean('cer_nodiacritic'),
                fidelity=mean('fidelity'), splices=sum(r['splices'] for r in rs), caption_assoc=mean('caption_assoc'), table_role=mean('table_role'), formula_role=mean('formula_role'), digits_ok=mean('digits_ok'), provenance=mean('provenance_bbox'),
                cte=dict(cte), cte_total=sum(v for k, v in cte.items() if k != 'lesson_attach_wrong'), cte_pages=sum(1 for r in rs if sum(v for k, v in r['cte'].items() if k != 'lesson_attach_wrong')),
                roles=roles, question_trusted_precision=(round(qt['tp'] / qt['pred'], 3) if qt['pred'] else None), question_trusted_n=qt['pred'], confusion=dict(conf.most_common(25)), unmatched_pipeline=dict(unm),
                attach_toc_ok=sum(1 for r in rs if r['attach_toc_ok']), attach_header_ok=sum(1 for x in att_h if x), attach_header_n=len(att_h), trust_reasons=dict(reasons),
                blocks_trusted_all=sum(r['blocks_trusted_all'] for r in rs), blocks_withheld_all=sum(r['blocks_withheld_all'] for r in rs))


def fmt(x):
    return '—' if x is None else (f'{x:.3f}' if isinstance(x, float) else str(x))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--pipeline', default='tc2-p1'); ap.add_argument('--json', default=None); ap.add_argument('--md', default=None)
    ap.add_argument('--out', default=None, help='pipeline output root (default poc-out/trusted-corpus/tc-v2/<pipeline>; env TC2_OUT_ROOT)')
    ap.add_argument('--gold-dir', default=None, help='score a different gold directory (e.g. tool/corpus/tc_gold_bai17); pages are read from sdm/ when sdm-gold/ lacks them')
    a = ap.parse_args()
    if a.out:
        tc2_paths.set_out_root(a.out)
    golds = tc_sdm.all_gold() if not a.gold_dir else [json.load(open(f)) for f in sorted(glob.glob(f'{a.gold_dir}/*.json'))]
    attach_cache = {}
    rows = []
    for g in golds:
        p = tc2_sdm.sdm_path(a.pipeline, g['book'], g['page'], gold=True)
        if not os.path.exists(p):
            p = tc2_sdm.sdm_path(a.pipeline, g['book'], g['page'], gold=False)
        if not os.path.exists(p):
            rows.append(dict(book=g['book'], page=g['page'], error='no sdm-gold')); continue
        sdm = json.load(open(p))
        if g['book'] not in attach_cache:
            att = tc2_attach.load_attach(g['book'], a.pipeline)
            attach_cache[g['book']] = {r['page']: r for r in att['pages']} if att else {}
        rows.append(score_page(g, sdm, attach_cache[g['book']].get(g['page'])))
    sets = dict(all=rows, dev=[r for r in rows if not r.get('held_out')], heldout=[r for r in rows if r.get('held_out')],
                science=[r for r in rows if r.get('book') in SCIENCE], science_sgk=[r for r in rows if r.get('book') in SLICE], sgv=[r for r in rows if '-sgv-' in (r.get('book') or '')])
    agg = {k: aggregate(v, k) for k, v in sets.items()}
    out = dict(pipeline=a.pipeline, pages=len(golds), rows=rows, aggregate=agg)
    if a.json:
        json.dump(out, open(a.json, 'w'), ensure_ascii=False, indent=1)
    L = [f'# TC-v2 pipeline {a.pipeline} on the gold set (MEASURED)', '',
         '| set | pages | learning blk | trusted (cov) | TLSR | false trusted | FTR | safe rej | found | order | inv | text acc | CER no-tone | fidelity | splices | CTE | CTE pages | attach TOC ok | attach header ok |',
         '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for k, v in agg.items():
        if not v.get('pages'):
            continue
        L.append(f"| {k} | {v['pages']} | {v['learning_blocks']} | {v['trusted']} ({v['coverage']:.3f}) | {v['tlsr']:.3f} | {v['false_trusted']} | {v['ftr']:.4f} | {v['safe_rejected']} | {fmt(v['found'])} | {fmt(v['order'])} | {v['meaning_inversions']} | {fmt(v['text_acc'])} | {fmt(v['cer_notone'])} | {fmt(v['fidelity'])} | {v['splices']} | {v['cte_total']} | {v['cte_pages']} | {v['attach_toc_ok']}/{v['pages']} | {v['attach_header_ok']}/{v['attach_header_n']} |")
    L += ['', '## Role Layer — precision / recall per role (matched blocks; "(n)" = gold blocks of that role)', '']
    for k, v in agg.items():
        if not v.get('pages'):
            continue
        L.append(f'### {k} ({v["pages"]} pages) — trusted-QUESTION precision {fmt(v["question_trusted_precision"])} (n={v["question_trusted_n"]})')
        L.append('| role | precision | recall | tp | predicted | gold |'); L.append('|---|---|---|---|---|---|')
        for role in SIX + OTHER:
            rr = v['roles'][role]
            if rr['pred'] == 0 and rr['gold'] == 0:
                continue
            L.append(f"| {'**' + role + '**' if role in SIX else role} | {fmt(rr['p'])} | {fmt(rr['r'])} | {rr['tp']} | {rr['pred']} | {rr['gold']} |")
        L.append(''); L.append(f"confusion (gold→pipeline): {v['confusion']}"); L.append(f"unmatched pipeline blocks by role: {v['unmatched_pipeline']}"); L.append(f"trust reasons (blocks): {v['trust_reasons']}"); L.append(f"CTE by class: {v['cte']}"); L.append('')
    L += ['## Per page', '', '| page | set | found | order | text | fidelity | splices | TLSR | FTR | trusted/withheld | CTE | lesson TOC | lesson header | false Qs |', '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        if r.get('error'):
            L.append(f"| {r['book']} p{r['page']:03d} | | ERROR {r['error']} | | | | | | | | | | | |"); continue
        ah = r['attach_header']
        L.append(f"| {r['book']} p{r['page']:03d} | {'held-out' if r['held_out'] else 'dev'} | {fmt(r['found'])} | {fmt(r['order'])} | {fmt(r['text_acc'])} | {fmt(r['fidelity'])} | {r['splices']} | {fmt(r['tlsr'])} | {fmt(r['ftr'])} | {r['trusted_blocks']}/{r['safe_rejected']} | {r['cte_total']} | {r['lesson_attach']} | {ah['lesson']} {ah['method']} {'OK' if ah['ok'] else ('WRONG' if ah['ok'] is False else '?')} | {len(r['roles6']['false_questions'])} |")
    md = '\n'.join(L) + '\n'
    if a.md:
        open(a.md, 'w').write(md)
    print('\n'.join(L[:8]))
    for k in ('dev', 'heldout', 'science'):
        v = agg[k]
        if v.get('pages'):
            print(k, 'question P/R', v['roles']['QUESTION'], 'trusted-Q precision', v['question_trusted_precision'], 'attach header', v['attach_header_ok'], '/', v['attach_header_n'], 'toc', v['attach_toc_ok'])


if __name__ == '__main__':
    main()
