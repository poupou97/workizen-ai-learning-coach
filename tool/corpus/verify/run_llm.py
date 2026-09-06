#!/usr/bin/env python3
"""Round 5 · Lane A4 — measure the LLM verifier as a **detector** and as a **proposer**, separately.

    python3 tool/corpus/verify/run_llm.py [--model haiku] [--holdout 60] [--workers 6] [--offline]

Bounded by design: the POC five, Lane C's 51 human-verified Bài 8 blocks, and a slice of the injection
holdout in both its corrupted and its uncorrupted form. Answers are cached on disk by prompt hash, so a
re-run costs nothing and `--offline` re-scores without spawning a single subprocess.

The uncorrupted holdout rows are the P0 measurement: there the correct output is «no finding» for every
row, so any proposal is a false correction and any flag is a false alarm — the number that decides whether
this signal can be allowed near a corpus at all.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from verify import evalsets as es, index as ix, llm as L, paths  # noqa: E402


def rows_to_check(n_holdout):
    poc = es.poc_cases()
    lanec = es.lanec_bai8()
    ho, _ = es.held_out_books()
    clean = es.holdout_lines(ho, per_book=max(2, n_holdout // len(ho)))[:n_holdout]
    corrupt = es.inject(clean)[:n_holdout]
    out = []
    for c in poc:
        out.append(dict(set='R-poc', id=f"poc-{c['id']}-observed", text=c['observed'],
                        context=dict(subject=c['subject'], lesson=c['lesson'],
                                     heading=' > '.join(c['heading_path']), role='body'),
                        truth_spans={c['span_observed']: c['span_correct']}, case=c['id']))
        out.append(dict(set='R-poc-correct', id=f"poc-{c['id']}-correct", text=c['correct'],
                        context=dict(subject=c['subject'], lesson=c['lesson'],
                                     heading=' > '.join(c['heading_path']), role='body'),
                        truth_spans={}, case=c['id']))
    for r in lanec:
        out.append(dict(set='L-lanec', id=r['short'], text=r['text'],
                        context=dict(subject='Lịch sử và Địa lí 5', lesson='Bài 8',
                                     heading=' > '.join(r['heading_path']), role=r['role']),
                        truth_spans={s['pipeline']: s['printed'] for s in r['slips']},
                        verdict=r['verdict']))
    for r in corrupt:
        out.append(dict(set='H-inj', id=r['id'], text=r['corrupted'],
                        context=dict(subject=r['book'], lesson=None, heading=None, role=None),
                        truth_spans={r['injected_token']: r['truth_token']}))
    for r in clean:
        out.append(dict(set='H-clean', id=r['id'], text=r['text'],
                        context=dict(subject=r['book'], lesson=None, heading=None, role=None),
                        truth_spans={}))
    return out


def _covers(span, truth_key):
    """Does a flagged span point at this slip?

    Two matchers, because two different kinds of span arrive. Vietnamese word slips are compared **by
    token** after normalisation, so «Sưu tẩm» flagged as a phrase still counts as pointing at `tẩm`. A
    STEM span like `3×10°` has no word tokens at all — the superscript is not a letter — so it is compared
    **by raw substring**. Without the second matcher the Founder's own worked example scores as a miss
    while the model in fact found it, which would be a measurement bug reported as a model result.
    """
    if truth_key.lower() in span.lower() or span.lower() in truth_key.lower():
        return True
    st = {ix.norm_token(w) for w in ix.TOKEN.findall(span)}
    return bool(st) and ix.norm_token(truth_key) in st


def _proposal_ok(span, proposed, truth_spans):
    """Did this proposal turn the slip into what the print actually says?"""
    for bad, good in truth_spans.items():
        if not _covers(span, bad):
            continue
        if good.lower() in proposed.lower() or proposed.lower() in good.lower():
            return True
        toks = [ix.norm_token(w) for w in ix.TOKEN.findall(proposed)]
        if ix.norm_token(good) in toks:
            return True
    return False


def score(rows, results):
    """Detector and proposer, in two tables that never borrow from each other."""
    agg = {}
    detail = []
    for row, (anomalies, proposals, meta) in zip(rows, results):
        s = agg.setdefault(row['set'], Counter())
        s['rows'] += 1
        if meta.get('error'):
            s['unparsable'] += 1
        s['dropped_hallucinated_spans'] += len(meta.get('dropped_spans') or ())
        truth = dict(row['truth_spans'])
        s['slips'] += len(truth)

        # ---- detector: did any flagged span cover a real slip?
        hit = {k for k in truth if any(_covers(a.span, k) for a in anomalies)}
        s['detected'] += len(hit)
        s['flags'] += len(anomalies)
        s['flag_tokens'] += len({ix.norm_token(w) for a in anomalies for w in ix.TOKEN.findall(a.span)})
        s['false_alarms'] += sum(1 for a in anomalies if not any(_covers(a.span, k) for k in truth))
        if anomalies and not truth:
            s['rows_falsely_flagged'] += 1
        if truth and hit:
            s['rows_detected'] += 1
        if truth:
            s['rows_with_slips'] += 1

        # ---- proposer: of the corrections it actually made, how many were right?
        for p in proposals:
            s['proposals'] += 1
            ok = _proposal_ok(p['span'], p['proposed'], truth)
            s['correct_corrections' if ok else 'false_corrections'] += 1
            detail.append(dict(set=row['set'], id=row['id'], span=p['span'], proposed=p['proposed'],
                               kind=p['kind'], severity=p['severity'], confidence=p['confidence'],
                               reason=p['reason'], verdict='CORRECT' if ok else 'FALSE',
                               truth=row['truth_spans'],
                               contradicting=len(p['contradicting']), supporting=len(p['supporting'])))
        for a in anomalies:
            if not any(p['span'] == a.span for p in proposals):
                detail.append(dict(set=row['set'], id=row['id'], span=a.span, proposed=None,
                                   severity=a.severity, confidence=a.confidence, reason=a.reason,
                                   verdict=('ANOMALY_ON_SLIP'
                                            if any(_covers(a.span, k) for k in truth)
                                            else 'ANOMALY_ELSEWHERE'),
                                   truth=row['truth_spans'],
                                   contradicting=len(a.contradicting()), supporting=len(a.supporting())))
    return agg, detail


def rates(c):
    def d(a, b):
        return round(a / b, 4) if b else None
    prop = c['proposals']
    return dict(
        rows=c['rows'], slips=c['slips'], unparsable=c['unparsable'],
        hallucinated_spans_dropped=c['dropped_hallucinated_spans'],
        detector=dict(flags=c['flags'], flagged_tokens=c['flag_tokens'],
                      detection_recall=d(c['detected'], c['slips']),
                      row_detection_recall=d(c['rows_detected'], c['rows_with_slips']),
                      false_alarms=c['false_alarms'],
                      false_alarms_per_row=d(c['false_alarms'], c['rows']),
                      rows_falsely_flagged=c['rows_falsely_flagged'],
                      row_false_alarm_rate=d(c['rows_falsely_flagged'], c['rows'])),
        proposer=dict(proposals=prop,
                      correct=c['correct_corrections'], false=c['false_corrections'],
                      correction_precision=d(c['correct_corrections'], prop),
                      correction_recall=d(c['correct_corrections'], c['slips']),
                      false_correction_rate=d(c['false_corrections'], prop)),
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', default=L.DEFAULT_MODEL)
    ap.add_argument('--holdout', type=int, default=60)
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--offline', action='store_true')
    a = ap.parse_args()

    rows = rows_to_check(a.holdout)
    v = L.LLMVerifier(model_name=a.model, offline=a.offline)
    print(f'{len(rows)} rows · model {a.model} · cache {v.cache_dir}', flush=True)

    def one(r):
        return v.verify(r['id'], r['text'], r['context'])

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        results = list(ex.map(one, rows))
    print('harness:', v.stats, flush=True)

    agg, detail = score(rows, results)
    report = dict(model=a.model, prompt_version=L.PROMPT_VERSION, harness=v.stats,
                  sets={k: rates(c) for k, c in sorted(agg.items())})
    os.makedirs(paths.OUT, exist_ok=True)
    with open(f'{paths.OUT}/llm-report.json', 'w', encoding='utf-8') as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    with open(f'{paths.OUT}/llm-decisions.jsonl', 'w', encoding='utf-8') as fh:
        for row in detail:
            fh.write(json.dumps(row, ensure_ascii=False) + '\n')

    print('\n=== LLM AS VERIFIER (G.llm_semantic) ===')
    for k, m in report['sets'].items():
        dd, pp = m['detector'], m['proposer']
        print(f"\n{k}: rows={m['rows']} slips={m['slips']} unparsable={m['unparsable']} "
              f"hallucinated_spans={m['hallucinated_spans_dropped']}")
        print(f"  DETECTOR  flags={dd['flags']} recall={dd['detection_recall']} "
              f"false_alarms={dd['false_alarms']} "
              f"rows_falsely_flagged={dd['rows_falsely_flagged']} ({dd['row_false_alarm_rate']})")
        print(f"  PROPOSER  proposals={pp['proposals']} precision={pp['correction_precision']} "
              f"recall={pp['correction_recall']} FCR={pp['false_correction_rate']}")
    # the five, one line each
    print('\n--- the POC five, LLM ---')
    poc = [d for d in detail if d['set'] == 'R-poc']
    for c in es.poc_cases():
        mine = [d for d in poc if d['id'] == f"poc-{c['id']}-observed"]
        on = [d for d in mine if any(w.lower() in c['span_observed'].lower()
                                     for w in d['span'].split())] or mine
        shown = ' · '.join('{!r}→{!r} [{}]'.format(d['span'], d['proposed'], d['verdict'])
                           for d in on[:3]) or 'no finding'
        print(f"  {c['id']} {c['kind']:22s} flags={len(mine)} {shown}")
        wrong = [d for d in detail if d['id'] == f"poc-{c['id']}-correct"]
        if wrong:
            print(f"       ⚠ on the CORRECT text it flagged: "
                  f"{[(d['span'], d['proposed']) for d in wrong[:3]]}")


if __name__ == '__main__':
    main()
