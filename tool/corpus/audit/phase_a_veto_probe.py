#!/usr/bin/env python3
"""PHASE A — measure the proposed question-promotion veto WITHOUT shipping it.

This is a MEASUREMENT, not a change. Nothing here is imported by the pipeline; the three
candidate rules are applied by wrapping `tc2_sdm.assign_role` for the duration of one pass and
restored afterwards, so the pipeline on disk is untouched and no artefact this writes can reach
a learner. Phase B implements the rules properly, with tests and a population-adequacy guard,
and re-measures on the frozen blind populations.

The rules, each of which refuses a QUESTION promotion the block's own structure contradicts:

  P1  a block whose native label is `section_header` / `title` is not promoted to QUESTION.
      Today the heading rule at `tc2_sdm.assign_role` carries `not ends with "?"`, so an
      explicit structural label is discarded in favour of the question lexicon.
  P2  a block opening with a worked-example or remark lead-in is not promoted to QUESTION.
  P3  `SIDEBAR_LABEL` matches the labels as printed. Its vowel classes carry the plain and
      circumflex forms and omit the tone-marked ones, so it matches mainly where the OCR is
      wrong; with the label unmatched, the sidebar box context never opens and the question
      lexicon wins inside a side box.

WHY IT IS MEASURED REBUILD-AGAINST-REBUILD. The stored round-4 SDM pages and a fresh build of
the same pages differ by two served blocks, because `FORMULA` handling changed after round 4.
Comparing a patched build against the stored artefact would credit the veto with two blocks it
did not cause. Both columns are therefore fresh builds with the same code, and the only
difference between them is the patch.

THE RESULT IS IN-SAMPLE. The rules were derived from the very rows they remove. The number this
prints is a ceiling, not an expectation; the honest measurement is on `BLIND-CORE` /
`BLIND-TEACHING` and has not been made.

ABSENCE CANNOT SATISFY A POSITIVE OBLIGATION: with no gold pages, or a baseline that holds no
as-question error, the probe exits non-zero. A veto measured on a population with nothing to
veto would print a flawless zero.

Usage
  python3 tool/corpus/audit/phase_a_veto_probe.py --sdm <sdm-gold dir> [--gold-dir <dir>]
"""
import argparse
import collections
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.dirname(HERE)
sys.path.insert(0, CORPUS)

import tc_score   # noqa: E402
import tc_sdm     # noqa: E402
import tc2_sdm    # noqa: E402

LEAD_IN = re.compile(r'^\s*(Bài tập ví dụ|Ví dụ\s*\d*|Nhận xét)\b')
_ORIG_ROLE = tc2_sdm.assign_role
_ORIG_SIDEBAR = tc2_sdm.SIDEBAR_LABEL
#: the same alternatives, with the tone-marked vowels the printed labels actually use
_SIDEBAR_AS_PRINTED = re.compile(
    _ORIG_SIDEBAR.pattern
    .replace('Em có th[eê]', 'Em có th[eêểế]')
    .replace('EM CÓ TH[EÊ]', 'EM CÓ TH[EÊỂẾ]')
    .replace('Em có bi[eê][tít]', 'Em có bi[eêế][tít]')
    .replace('EM CÓ BI[EÊ][TÍ]T?', 'EM CÓ BI[EÊẾ][TÍ]T?'))


def _veto(components):
    def assign(b, ctx):
        r = _ORIG_ROLE(b, ctx)
        if r[0] != 'question':
            return r
        t = (b['text'] or '').strip()
        if 'P1' in components and b.get('native_label') in ('section_header', 'title') and len(t) <= 100:
            return ('heading', 'native', 0.85, ['section_header: question-promotion vetoed'])
        if 'P2' in components and LEAD_IN.match(t):
            return ('body', 'lexicon', 0.7, ['worked-example / remark lead-in: question-promotion vetoed'])
        return r
    return assign


def measure(pages, gold_dir, components=(), sidebar_as_printed=False):
    if components:
        tc2_sdm.assign_role = _veto(components)
    if sidebar_as_printed:
        tc2_sdm.SIDEBAR_LABEL = _SIDEBAR_AS_PRINTED
    T = collections.Counter()
    served = set()
    try:
        for book, page in pages:
            pg = tc2_sdm.build_page(book, page, pipeline='tc2-p2')
            gold = json.load(open(f'{gold_dir}/{book}-p{page:03d}.json'))
            v1 = tc2_sdm.to_v1_sdm(pg)
            r = tc_score.score(gold, v1)
            T['learning'] += r['learning_blocks']
            T['trusted'] += r['trusted_blocks']
            T['false_trusted'] += r['false_trusted']
            m = tc_score.match(gold, v1)
            by = {b['id']: b for b in pg['blocks']}
            for g in gold['blocks']:
                if g['role'] not in tc_sdm.LEARNING_ROLES or not g.get('anchor'):
                    continue
                c = m.get(g['id'])
                if not c or c['trusted'] is not True:
                    continue
                served.add((book, page, g['id']))
                if by[c['id']]['role']['coarse'] == 'QUESTION':
                    if g['role'] in tc_sdm.NOT_A_QUESTION:
                        T['as_question_error'] += 1
                    elif g['role'] == 'question':
                        T['question_correct'] += 1
    finally:
        tc2_sdm.assign_role = _ORIG_ROLE
        tc2_sdm.SIDEBAR_LABEL = _ORIG_SIDEBAR
    return T, served


def main():
    ap = argparse.ArgumentParser(description='Phase A veto probe (measurement only; ships nothing)')
    ap.add_argument('--sdm', required=True, help='sdm-gold directory naming the pages to rebuild')
    ap.add_argument('--gold-dir', default=os.path.join(CORPUS, 'tc_gold'))
    ns = ap.parse_args()
    pages = []
    for f in sorted(glob.glob(os.path.join(ns.sdm, '*', 'p*.sdm.json'))):
        d = json.load(open(f))
        if os.path.exists(f"{ns.gold_dir}/{d['book']}-p{d['page']:03d}.json"):
            pages.append((d['book'], d['page']))
    if not pages:
        raise SystemExit('UNVERIFIED: no gold page under --sdm; there is nothing to measure')
    base, base_served = measure(pages, ns.gold_dir)
    if not base['as_question_error']:
        raise SystemExit('UNVERIFIED: the baseline holds no as-question error. A veto measured on a '
                         'population with nothing to veto would print a flawless zero, and that is '
                         'not a result.')
    print(f"BASELINE   trusted={base['trusted']} false_trusted={base['false_trusted']} "
          f"as_question={base['as_question_error']} correct_questions={base['question_correct']}")
    for tag, comp, sb in (('P1 alone', ('P1',), False), ('P2 alone', ('P2',), False),
                          ('P3 alone', (), True), ('P1+P2+P3', ('P1', 'P2'), True)):
        t, s = measure(pages, ns.gold_dir, comp, sb)
        print(f"{tag:<10} trusted={t['trusted']} false_trusted={t['false_trusted']} "
              f"as_question={t['as_question_error']} correct_questions={t['question_correct']}  "
              f"| Δ as_question {t['as_question_error'] - base['as_question_error']:+d} "
              f"· Δ correct questions {t['question_correct'] - base['question_correct']:+d} "
              f"· withdrawn {len(base_served - s)} · newly served {len(s - base_served)}")
    print('IN-SAMPLE: the rules were derived from the rows they remove. Measure on the frozen '
          'blind populations before believing any of it.')


if __name__ == '__main__':
    main()
