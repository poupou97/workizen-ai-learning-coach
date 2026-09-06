#!/usr/bin/env python3
"""Round 5 · Lane A4 — the **signal × case matrix** and the router's **human review rate**.

    python3 tool/corpus/verify/run_matrix.py [--policy recall]

For each POC case × each signal: DETECTED? · PROPOSED the right correction? · VERIFIED it? · what the
false-correction risk is. Then the router's escalation rate on all three evaluation sets, because a router
that escalates everything is useless and the only way to know is to count.

Reads the artefacts the other runners wrote (`llm-decisions.jsonl`, `xcorpus-report.json`) rather than
re-running them, so the matrix is assembled from the same numbers the per-signal tables report.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from verify import (crosscorpus as xc, enumerator as EN, evalsets as es, external as EX,  # noqa: E402
                    furniture as FU, index as ix, paths, router as R)

SDM_ROOT = f'{paths.ROOT}/poc-out/round5/pipeline/tc2-p3/sdm'

SIGNALS = ['deterministic (A.enumerator)', 'specialised parser (C.numeric / A2)',
           'Vietnamese lexical (A.vi_lexicon / A1)', 'page furniture (B.page_furniture)',
           'cross-corpus (D.cross_corpus)', 'LLM semantic (G.llm_semantic)',
           'external authoritative (H.external)']


def load_json(p, default=None):
    if not os.path.exists(p):
        return default
    with open(p, encoding='utf-8') as fh:
        return json.load(fh)


def llm_rows():
    p = f'{paths.OUT}/llm-decisions.jsonl'
    if not os.path.exists(p):
        return []
    with open(p, encoding='utf-8') as fh:
        return [json.loads(x) for x in fh if x.strip()]


def cell(detected, proposed, correct, verified, risk, note=''):
    return dict(detected=detected, proposed=proposed, proposed_right=correct, verified=verified,
                false_correction_risk=risk, note=note)


def build_matrix(xreport, policy, llm):
    cases = es.poc_cases()
    xpol = ((xreport or {}).get('policies') or {}).get(policy, {})
    xcases = {c['case']: c for c in xpol.get('poc_cases', [])}
    out = {}
    for c in cases:
        cid = c['id']
        row = {}

        # ---- deterministic: the enumerator shape rule
        got = EN.analyse(c['observed'])
        row[SIGNALS[0]] = cell(
            bool(got), bool(got), bool(got and got[1] == c['span_correct']),
            bool(got and got[1] == c['span_correct']),
            'none — it only ever fires on a token that is neither a numeral nor a number',
            f'{got[0]} → {got[1]}' if got else 'no leading enumerator to judge')

        # ---- specialised parser (A2 owns the repairer; recorded here as its detection surface)
        stem = bool(R.STEM.search(c['observed']))
        row[SIGNALS[1]] = cell(
            stem, False, False, False,
            'low — deterministic digit/unit checks; A2 measured CHEM firing 173× with ≥40 non-chemical '
            'matches, so the guard needs the fix, not the parser',
            'Lane A2 owns the repairer; A4 routes to it' if stem else 'not a STEM expression')

        # ---- Vietnamese lexical (A1's signal; A4 reports its published numbers, does not re-run it)
        row[SIGNALS[2]] = cell(
            None, None, None, None,
            'measured 0.000 by A1 on dev and held-out',
            'A1: precision 1.000 / false-correction 0.000 but detection recall 0.040 (6/152) — the gap '
            'this lane exists to close')

        # ---- page furniture
        cleaned, removed = FU.strip_known(c['observed'])
        row[SIGNALS[3]] = cell(
            bool(removed), bool(removed), bool(removed),
            bool(removed),
            'deletion only — it cannot invent a wrong word; the residual risk is deleting real text, '
            'bounded by the stray-single-letter guard',
            f'removed {[p for p, _, _ in removed]}' if removed else 'no watermark fragment')

        # ---- cross-corpus
        xc_row = xcases.get(cid)
        if xc_row:
            row[SIGNALS[4]] = cell(
                xc_row['detected'], xc_row['proposed'], xc_row['correct_proposal'],
                False,      # never self-validated: layer D may not validate a layer-D candidate
                'measured: clean-text 0.92–2.90 proposals per 1,000 tokens; injected FCR 0.063–0.092',
                xc_row['reason'][:140])
        else:
            row[SIGNALS[4]] = cell(None, None, None, None, 'not measured for this case', '')

        # ---- LLM
        mine = [d for d in llm if d['id'] == f'poc-{cid}-observed']
        on = [d for d in mine if any(w.lower() in c['span_observed'].lower() for w in d['span'].split())
              or c['span_observed'].lower() in d['span'].lower()]
        right = [d for d in on if d['verdict'] == 'CORRECT']
        row[SIGNALS[5]] = cell(
            bool(on) if mine or cid != 'F' else None, bool([d for d in on if d.get('proposed')]),
            bool(right), False,
            'HIGH as a proposer: on 60 already-correct rows it proposed 13 changes and every one was '
            'wrong (FCR 1.000, 26.7 % of rows flagged). Acceptable as a DETECTOR: recall 0.717',
            '; '.join(f"{d['span']}→{d['proposed']}" for d in on[:2]) or 'no finding')

        # ---- external
        ext_kind = {'A': 'stem_constant', 'B': 'proper_noun_person', 'C': 'common_word_meaning',
                    'D': 'proper_noun_state', 'E': 'dictionary_word', 'F': 'reading_order'}[cid]
        ok, why = EX.appropriate(ext_kind)
        row[SIGNALS[6]] = cell(
            None, None, None, None,
            'no auto-apply is possible by construction; the risk is spending the budget where the '
            'question is source-bound',
            ('APPROPRIATE — ' + why) if ok else ('NOT APPROPRIATE — ' + why))
        out[cid] = dict(case=c, signals=row)
    return out


def sdm_rows(limit=1200):
    """Real pipeline blocks, with the roles, guards and agreement the router is actually keyed on.

    The synthetic holdout rows carry none of that, so the router reads every one of them as ordinary
    display prose and escalates none — a 0.0000 rate there measures the *inputs*, not the router. This set
    is the honest denominator for a human-review rate."""
    import glob
    out = []
    for f in sorted(glob.glob(f'{SDM_ROOT}/*/*.json'))[:400]:
        with open(f, encoding='utf-8') as fh:
            page = json.load(fh)
        for b in page.get('blocks') or ():
            if not b.get('text'):
                continue
            out.append(('S-sdm', b['id'], b['text'], (b.get('role') or {}).get('value'),
                        dict(guards=b.get('guards') or [], agreement=b.get('agreement') or {},
                             ocr_conf=b.get('ocr_conf'))))
            if len(out) >= limit:
                return out
    return out


def router_rates(policy='recall'):
    """The escalation rate, on every set the lane measures."""
    rows = []
    for r in es.lanec_bai8():
        rows.append(('L-lanec', r['short'], r['text'], r['role'],
                     dict(guards=r['guards'], agreement=r['agreement'], ocr_conf=r['ocr_conf'])))
    ho, _ = es.held_out_books()
    clean = es.holdout_lines(ho, per_book=40)
    for r in clean:
        rows.append(('H-clean', r['id'], r['text'], None, dict(ocr_conf=r.get('conf'))))
    for r in es.inject(clean):
        rows.append(('H-inj', r['id'], r['corrupted'], None, dict(ocr_conf=r.get('conf'))))
    for c in es.poc_cases():
        rows.append(('R-poc', c['id'], c['observed'], c.get('role', 'body'), {}))
    rows.extend(sdm_rows())

    agg = {}
    detail = []
    for setname, bid, text, role, block in rows:
        rt = R.route(bid, text, role=role, block=block)
        a = agg.setdefault(setname, Counter())
        a['rows'] += 1
        a[f'ctype:{rt.content_type}'] += 1
        a[f'tc:{rt.teaching_consequence}'] += 1
        a['human'] += int(rt.human)
        a['llm'] += int('G.llm_semantic' in rt.path)
        a['external'] += int('H.external' in rt.path)
        a['xcorpus'] += int('D.cross_corpus' in rt.path)
        a['cost'] += rt.cost
        if rt.human:
            detail.append(rt.to_json())
    out = {}
    for k, a in sorted(agg.items()):
        n = a['rows']
        out[k] = dict(rows=n,
                      human_review_rate=round(a['human'] / n, 4),
                      llm_consult_rate=round(a['llm'] / n, 4),
                      external_consult_rate=round(a['external'] / n, 4),
                      cross_corpus_rate=round(a['xcorpus'] / n, 4),
                      mean_cost=round(a['cost'] / n, 1),
                      content_types={x.split(':', 1)[1]: v for x, v in a.items() if x.startswith('ctype:')},
                      teaching={x.split(':', 1)[1]: v for x, v in a.items() if x.startswith('tc:')})
    return out, detail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--policy', default='recall')
    a = ap.parse_args()

    xreport = load_json(f'{paths.OUT}/xcorpus-report.json')
    llm = llm_rows()
    matrix = build_matrix(xreport, a.policy, llm)
    rates, escalated = router_rates(a.policy)

    report = dict(policy=a.policy, matrix=matrix, router=rates,
                  escalated_examples=escalated[:20])
    with open(f'{paths.OUT}/matrix-report.json', 'w', encoding='utf-8') as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)

    print('=== SIGNAL × CASE MATRIX ===')
    for cid, row in matrix.items():
        c = row['case']
        print(f"\n{cid} · {c['kind']} · observed «{c['span_observed']}» → printed «{c['span_correct']}»")
        for sig in SIGNALS:
            v = row['signals'][sig]
            def m(x):
                return {True: 'YES', False: 'no ', None: ' - '}[x]
            print(f"   {sig:38s} detect={m(v['detected'])} propose={m(v['proposed'])} "
                  f"right={m(v['proposed_right'])} verify={m(v['verified'])}  {v['note'][:78]}")

    print('\n=== ROUTER ===')
    for k, v in rates.items():
        print(f"  {k:10s} rows={v['rows']:4d} HUMAN REVIEW RATE={v['human_review_rate']:.4f} "
              f"llm={v['llm_consult_rate']:.3f} external={v['external_consult_rate']:.3f} "
              f"xcorpus={v['cross_corpus_rate']:.3f} mean_cost={v['mean_cost']}")
        print(f"             content={v['content_types']} teaching={v['teaching']}")


if __name__ == '__main__':
    main()
