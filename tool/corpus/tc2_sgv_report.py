#!/usr/bin/env python3
"""TC-v2 — SGV SAMPLE report (≤ 100 pages): what the SDM-v2 pipeline does on teacher books, measured.

Per SGV book (sample pages only): blocks by role, answer-leak / teacher-text guard counts, blocks that
would have reached a learner without the guards (question-form or body-form blocks that the agreement
gate alone trusts), and the SGK↔SGV PAIRING measurement: an SGV block in an answer section carrying an
enumerator ("Câu N", "HĐ N", "Bài N", "N.") under lesson L is a pairing candidate; it is PAIRABLE when the
SGK Trusted Structured Lesson L (tc2_tsl) has a TRUSTED question/activity block with the same enumerator,
AMBIGUOUS when several SGK blocks share the enumerator, and UNPAIRED otherwise. Pairing fails closed.

Usage: python3 tool/corpus/tc2_sgv_report.py --pipeline tc2-p1 [--json out] [--md out]
"""
import argparse
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tc2_run  # noqa: E402
import tc2_attach  # noqa: E402

ROOT = tc2_run.ROOT
ENUM = re.compile(r'^\s*(?:(Câu|HĐ|Hoạt động|Bài)\s*(\d{1,2})|(\d{1,2})[.)])')


def enum_key(t):
    """Printed enumerator → pairing key. SGV keys are written "Câu 1" / "HĐ 2" / "Bài 3"; SGK questions are printed
    "1." (rarely "Câu 1."), so "Câu N" and a bare "N." normalise to the same key "#N"; HĐ N and Bài N stay distinct."""
    m = ENUM.match(t or '')
    if not m:
        return None
    if m.group(1):
        kind = m.group(1).replace('Hoạt động', 'HĐ')
        return f'#{m.group(2)}' if kind == 'Câu' else f'{kind} {m.group(2)}'
    return f'#{m.group(3)}'


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--pipeline', default='tc2-p1'); ap.add_argument('--json', default=None); ap.add_argument('--md', default=None)
    a = ap.parse_args()
    out = {}
    for sgv in tc2_run.SGV_BOOKS:
        sgk = sgv.replace('-sgv-', '-sgk-')
        att = tc2_attach.load_attach(sgv, a.pipeline) or tc2_attach.attach_book(sgv, a.pipeline)
        prec = {r['page']: r for r in att['pages']}
        # SGK trusted questions by (lesson, enum)
        sgk_q = defaultdict(list)
        for f in glob.glob(f'{tc2_run.outdir(a.pipeline)}/lessons/{sgk}/bai-*.tsl.json'):
            d = json.load(open(f))
            for b in d['blocks']:
                if b['role']['value'] in ('question', 'activity', 'instruction'):
                    k = enum_key(b['text'])
                    if k:
                        sgk_q[(d['lesson'], k)].append(b['id'])
        roles = Counter(); reasons = Counter(); pages = 0; leak_blocks = 0; teacher_blocks = 0; would_reach = 0; trusted_learning = 0
        cands = [];
        for f in sorted(glob.glob(f'{tc2_run.outdir(a.pipeline)}/sdm/{sgv}/p*.sdm.json')):
            s = json.load(open(f)); pages += 1
            pr = prec.get(s['page'], {})
            lesson = pr.get('lesson')
            for ob in s['blocks']:
                r = ob['role']['value']; roles[r] += 1
                if not ob['learning']:
                    continue
                rs = ob['trust']['reasons']
                for x in rs:
                    reasons[x] += 1
                if 'answer_leak' in rs:
                    leak_blocks += 1
                if 'teacher_text' in rs:
                    teacher_blocks += 1
                if ob['trust']['status'] == 'TRUSTED':
                    trusted_learning += 1
                # "would reach a learner" = blocks the agreement gate alone trusts (no agree_* / math / empty reasons) that are answers/teacher text
                if not any(x.startswith('agree') or x in ('math_guard', 'empty_block', 'furniture', 'figure_text', 'low_ocr_conf') for x in rs) and (r in ('answer', 'model_answer', 'teacher_text', 'teacher_prompt')):
                    would_reach += 1
                if r in ('answer', 'model_answer') or 'answer_leak' in rs:
                    k = enum_key(ob['text'])
                    if k and lesson is not None:
                        hits = sgk_q.get((lesson, k), [])
                        cands.append(dict(page=s['page'], lesson=lesson, enum=k, status='PAIRABLE' if len(hits) == 1 else ('AMBIGUOUS' if len(hits) > 1 else 'UNPAIRED'), sgk_blocks=hits[:3], sgv_block=ob['id']))
        pair = Counter(c['status'] for c in cands)
        out[sgv] = dict(sample_pages=pages, roles=dict(roles.most_common()), learning_trusted=trusted_learning, guard_reasons=dict(reasons.most_common()), answer_leak_blocks=leak_blocks, teacher_text_blocks=teacher_blocks,
                        would_reach_learner_without_sgv_guards=would_reach, pairing=dict(candidates=len(cands), **pair), pairing_examples=cands[:6],
                        attach=dict(canonical=att['counts']['canonical_lesson_count'], toc_ranged=att['counts']['toc_ranged'], header_detected=att['counts']['header_detected'], repaired_ranged=att['counts']['repaired_ranged']))
    if a.json:
        json.dump(out, open(a.json, 'w'), ensure_ascii=False, indent=1)
    L = ['# TC-v2 SGV sample (MEASURED on the sampled pages only)', '', '| SGV book | pages | trusted learning blk | answer_leak | teacher_text | would reach a learner w/o SGV guards | pairing cand. | PAIRABLE | AMBIGUOUS | UNPAIRED | SGV lessons canonical / TOC-ranged / header-detected / repaired |', '|---|---|---|---|---|---|---|---|---|---|---|']
    tot = Counter()
    for b, v in out.items():
        p = v['pairing']; at = v['attach']
        L.append(f"| {b} | {v['sample_pages']} | {v['learning_trusted']} | {v['answer_leak_blocks']} | {v['teacher_text_blocks']} | {v['would_reach_learner_without_sgv_guards']} | {p['candidates']} | {p.get('PAIRABLE', 0)} | {p.get('AMBIGUOUS', 0)} | {p.get('UNPAIRED', 0)} | {at['canonical']} / {at['toc_ranged']} / {at['header_detected']} / {at['repaired_ranged']} |")
        tot.update(dict(pages=v['sample_pages'], trusted=v['learning_trusted'], leak=v['answer_leak_blocks'], teacher=v['teacher_text_blocks'], reach=v['would_reach_learner_without_sgv_guards'], cand=p['candidates'], pairable=p.get('PAIRABLE', 0), amb=p.get('AMBIGUOUS', 0), unp=p.get('UNPAIRED', 0)))
    L.append(f"| **total** | {tot['pages']} | {tot['trusted']} | {tot['leak']} | {tot['teacher']} | {tot['reach']} | {tot['cand']} | {tot['pairable']} | {tot['amb']} | {tot['unp']} | |")
    L += ['', 'Reading: on SGV pages the SDM-v2 role layer marks prose as teacher_text and answer-section blocks as answer; both carry a withholding reason, so **no SGV block is TRUSTED for a learner surface** (learning_trusted counts headings/captions only). "Would reach a learner" counts the blocks that pass the agreement gate and would have been served as text without the SGV lexicon — the size of the leak the guards close on this sample. Pairing is by (lesson, printed enumerator) against TRUSTED SGK question/activity blocks and fails closed on ambiguity; it is an upper bound on what an `answer_of` relation could key today, not a shipped feature.', '']
    md = '\n'.join(L) + '\n'
    if a.md:
        open(a.md, 'w').write(md)
    print(md)


if __name__ == '__main__':
    main()
