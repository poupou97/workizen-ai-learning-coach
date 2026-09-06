#!/usr/bin/env python3
"""Round 5 · Lane A4 — run **A1's engine** with A4's signals installed, and score it A1's way.

    python3 tool/corpus/verify/run_engine.py [--policy strict]

Every other runner in this lane measures a signal on its own. This one measures what the *framework* does
once A4's signals are registered in it — which is the only number that says whether registering them was
worth anything. Ground truth is Lane C's human print read of LS&ĐL 5 Bài 8 (51 blocks, 11 with a slip).

Scored with **`ledger.false_correction_report(truth)`** — A1's own P0 metric, with per-signal attribution,
so a false correction can be traced to the signals that supported it. A4 does not compute its own version
of a number A1 already computes.

Fail-closed by construction, and worth stating before the numbers: a candidate reaches `VALIDATED_REPAIR`
only with support from a layer other than its generator's, so **a cross-corpus proposal alone can never
become a repair**. On this set that means the engine repairs almost nothing — and that is the framework
working, not the signal failing.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from repair import engine, ledger as ledger_mod, model  # noqa: E402
from verify import crosscorpus as xc, evalsets as es, index as ix, paths, router as R, trust  # noqa: E402


def build_verifier(policy_name, rows):
    idx_path = f'{paths.OUT}/xcorpus-index-heldout.json'
    if not os.path.exists(idx_path):
        raise SystemExit(f'missing {idx_path} — run tool/corpus/verify/run_xcorpus.py first')
    idx = ix.CrossCorpusIndex.load(idx_path)
    pol = dict(strict=xc.STRICT, default=xc.DEFAULT, recall=xc.RECALL)[policy_name]
    v = xc.CrossCorpusVerifier(idx, None, pol)
    keys = set()
    for r in rows:
        keys |= v.context_keys(r['text'])
    ho, extra = es.held_out_books()
    scan = ix.ContextScan(keys, max_occ=6).run(paths.OCR_BODY, exclude_books=list(ho) + list(extra))
    return xc.install(xc.CrossCorpusVerifier(idx, scan, pol))


def printed_text(row):
    """What the print says, reconstructed from Lane C's slip list. `None` when the print was not read or
    the pipeline text already matches it."""
    if row['verdict'] != 'slip' or not row['slips']:
        return row['text'] if row['verdict'] in ('verbatim', 'verbatim_glyph') else None
    out = row['text']
    for s in row['slips']:
        if s['pipeline'] in out:
            out = out.replace(s['pipeline'], s['printed'])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--policy', default='strict', choices=('strict', 'default', 'recall'))
    a = ap.parse_args()

    import verify
    verify.load_plugins(which=('crosscorpus',))
    rows = es.lanec_bai8()
    build_verifier(a.policy, rows)

    truth_map = {r['block_id']: printed_text(r) for r in rows}
    led = ledger_mod.Ledger(f'{paths.OUT}/engine-ledger-{a.policy}.jsonl',
                            run=dict(lane='a4', policy=a.policy, set='lanec-bai8'))
    eng = engine.RepairEngine(led)

    counts = Counter()
    decisions = []
    for r in rows:
        obs = [model.Observation(block_id=r['block_id'], source='docling-ocrmac', value=r['text'],
                                 provenance=dict(book=r['book'], page=r['page']))]
        if r.get('text_docling'):
            obs.append(model.Observation(block_id=r['block_id'], source='current-xycut',
                                         value=r['text_docling']))
        ctx = engine.RepairContext(
            block_id=r['block_id'], observations=tuple(obs),
            disposition=(model.Disposition.WITHHELD if r['trust'] == 'WITHHELD'
                         else model.Disposition.TRUSTED),
            withhold_reasons=tuple(r['reasons']), role=r['role'],
            page=dict(book=r['book'], page=r['page'], printed_page=r['printed_page'],
                      heading_path=r['heading_path'], lesson='Bài 8'))
        out = eng.run_block(ctx)

        anomalies = xc.anomalies_of(r['block_id'], r['text'], xc._STATE['verifier'],
                                    where=dict(book=r['book'], page=r['page']))
        td = trust.TrustDecision.from_outcome(out, ctx, anomalies=anomalies)
        rt = R.route(r['block_id'], r['text'], role=r['role'],
                     block=dict(guards=r['guards'], agreement=r['agreement'], ocr_conf=r['ocr_conf']))
        esc, why = R.escalate_after(rt, td.disposition)

        counts[f'pipeline:{r["trust"]}'] += 1
        counts[f'engine:{out.disposition}'] += 1
        counts[f'trust:{td.disposition}'] += 1
        counts['restorable'] += int(out.restorable)
        counts['escalated'] += int(esc)
        counts['candidates'] += len(out.candidates)
        counts['anomalies'] += len(anomalies)
        decisions.append(dict(block=r['short'], print_verdict=r['verdict'],
                              pipeline=r['trust'], engine=out.disposition, trust=td.disposition,
                              restorable=out.restorable, escalated=esc, escalation_reason=why,
                              candidates=[c.rule_id for c in out.candidates],
                              anomalies=[x.reason[:80] for x in anomalies],
                              explain=td.explain()))

    # ---- demotion precision: the cost side of the ledger.
    # A1's engine turns «TRUSTED block, failure detected, nothing validated» into SUSPECT. That is a
    # withhold, not a correction, so `false_correction_report` cannot see it — and on a lane whose whole
    # job is raising detection recall it is exactly the cost that must be reported. A demotion is RIGHT
    # when the print says the block really has a slip, and WRONG when the print says verbatim.
    dem = [d for d in decisions if d['pipeline'] == 'TRUSTED' and d['engine'] != 'TRUSTED']
    right = [d for d in dem if d['print_verdict'] == 'slip']
    wrong = [d for d in dem if d['print_verdict'] in ('verbatim', 'verbatim_glyph')]
    slips_trusted = [d for d in decisions if d['pipeline'] == 'TRUSTED' and d['print_verdict'] == 'slip']
    demotion = dict(demotions=len(dem), right=len(right), wrong=len(wrong),
                    demotion_precision=(round(len(right) / len(dem), 4) if dem else None),
                    false_demotion_rate=(round(len(wrong) / len(dem), 4) if dem else None),
                    slip_blocks_served_before=len(slips_trusted),
                    slip_blocks_caught=len(right),
                    wrong_served_prevented=len(right),
                    correct_served_lost=len(wrong),
                    detection_recall_on_served_slip_blocks=(round(len(right) / len(slips_trusted), 4)
                                                            if slips_trusted else None),
                    right_blocks=[d['block'] for d in right], wrong_blocks=[d['block'] for d in wrong])

    fc = led.false_correction_report(lambda bid: truth_map.get(bid))
    report = dict(policy=a.policy, n=len(rows), counts=dict(counts), demotion=demotion,
                  false_correction_report=fc, decisions=decisions)
    with open(f'{paths.OUT}/engine-report-{a.policy}.json', 'w', encoding='utf-8') as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    led.close()

    print(f'=== A1 ENGINE + A4 SIGNALS · Lane C Bài 8 · policy {a.policy} · n={len(rows)} ===')
    for k in sorted(counts):
        print(f'  {k:34s} {counts[k]}')
    print('\n--- A1 false_correction_report (the P0 metric, per-signal attribution) ---')
    print(f"  totals            : {fc['totals']}")
    print(f"  changed           : {fc['changed']}")
    print(f"  FALSE CORRECTION  : {fc['false_correction_rate']}")
    print(f"  correction prec.  : {fc['correction_precision']}")
    print(f"  by signal         : {fc['by_signal']}")
    print('\n--- demotion (the cost `false_correction_report` structurally cannot see) ---')
    for k, v in demotion.items():
        print(f'  {k:44s} {v}')
    moved = [d for d in decisions if d['engine'] != ('WITHHELD' if d['pipeline'] == 'WITHHELD'
                                                     else 'TRUSTED')]
    print(f'\n--- blocks whose disposition MOVED: {len(moved)} ---')
    for d in moved[:12]:
        print(f"  {d['block']:22s} {d['pipeline']:8s} → engine {d['engine']:20s} trust {d['trust']:20s} "
              f"{'ESCALATE' if d['escalated'] else ''} {d['candidates']}")


if __name__ == '__main__':
    main()
