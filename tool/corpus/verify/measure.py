#!/usr/bin/env python3
"""Round 5 · Lane A4 — the metrics, with **FALSE CORRECTION RATE as P0**.

The failure mode this lane exists to avoid is turning *«OCR got it wrong»* into *«AI confidently got it
wrong differently»*. So every table below reports, for the same rows and the same policy:

| metric | definition |
|---|---|
| **anomaly detection recall** | slips the signal flagged (proposal **or** anomaly) ÷ slips present |
| **correction precision** | proposals that restore the printed token ÷ proposals made |
| **correction recall** | proposals that restore the printed token ÷ slips present |
| **FALSE CORRECTION RATE** | proposals that do **not** restore the printed token ÷ proposals made |
| **clean false-correction rate** | proposals made on text that was already right ÷ tokens examined |
| **human review rate** | rows the router sends to a human ÷ rows |

Detection and proposal are counted **separately**, because a signal can be an excellent detector and a
poor proposer — that turns out to be the whole story for the LLM, and half the story for cross-corpus on
proper nouns.

`clean false-correction rate` is the one that cannot be gamed. On the uncorrupted holdout the correct
output for every token is «propose nothing», so any proposal is a false correction, and the rate is a
straight count with no adjudication. (Its one caveat is recorded honestly: the corpus lines are OCR
output, not print, so a proposal there *could* be a genuine repair of a genuine OCR error. A sample is
adjudicated by hand and reported, and the raw rate is stated as an **upper bound**.)
"""
from __future__ import annotations

import json
import os
from collections import Counter

from . import crosscorpus as xc, index as ix, paths


# --------------------------------------------------------------------------- truth maps
def truth_for_injection(row):
    """{token index: printed token} for one injected row — exactly one entry."""
    return {row['truth_i']: row['truth_token']}


def truth_for_lanec(row):
    """{token index: printed token} for a Lane C row, plus the slips this comparison structurally cannot
    see. `hóa`/`hoá` is the clear case: they are two valid orthographies of one word, the index unifies
    them on purpose, and «correcting» one to the other is a display-fidelity act, not a meaning repair."""
    toks = ix.tokens_of(row['text'])
    tmap, unseeable = {}, []
    for slip in row['slips']:
        bad, good = ix.norm_token(slip['pipeline']), ix.norm_token(slip['printed'])
        if bad == good:
            unseeable.append(dict(slip=slip, reason='tone-placement orthography (hoà/hòa); not a tone error'))
            continue
        hits = [i for i, t in enumerate(toks) if t == bad]
        if slip.get('context'):
            ctx = [ix.norm_token(w) for w in slip['context'].replace('—', ' ').split()]
            narrowed = [i for i in hits
                        if any((i and toks[i - 1] == c) or (i + 1 < len(toks) and toks[i + 1] == c)
                               for c in ctx)]
            hits = narrowed or hits
        if not hits:
            unseeable.append(dict(slip=slip, reason='token not present in the pipeline text as recorded'))
            continue
        for i in hits:
            tmap[i] = good
    return tmap, unseeable


# --------------------------------------------------------------------------- token-level scoring
def score_rows(verifier, rows, text_key, truth_fn, label):
    """Score one set. Returns the counters and every individual decision, so a Founder can read the rows
    behind any number."""
    c = Counter()
    decisions = []
    unseeable_all = []
    for row in rows:
        text = row[text_key]
        tmap = truth_fn(row)
        if isinstance(tmap, tuple):
            tmap, unseeable = tmap
            unseeable_all.extend(dict(row=row.get('short') or row.get('id'), **u) for u in unseeable)
        c['rows'] += 1
        c['tokens'] += len(ix.tokens_of(text))
        c['slips'] += len(tmap)
        findings = verifier.analyse(text, where=row)
        c['findings'] += len(findings)
        hit_positions = {f.i for f in findings}
        for i in tmap:
            if i in hit_positions:
                c['detected'] += 1
        for f in findings:
            proper = 'pn' if f.is_proper else 'cw'
            if f.proposes:
                c['proposals'] += 1
                c[f'proposals_{proper}'] += 1
                want = tmap.get(f.i)
                if want is None:
                    c['false_corrections'] += 1
                    c[f'false_corrections_{proper}'] += 1
                    kind = 'FALSE_on_correct_token'
                elif f.proposed == want:
                    c['correct_corrections'] += 1
                    c[f'correct_corrections_{proper}'] += 1
                    kind = 'CORRECT'
                else:
                    c['false_corrections'] += 1
                    c[f'false_corrections_{proper}'] += 1
                    kind = 'FALSE_wrong_target'
            else:
                c['anomalies'] += 1
                c[f'anomalies_{proper}'] += 1
                kind = 'ANOMALY_ON_SLIP' if f.i in tmap else 'ANOMALY_on_correct_token'
                c[kind] += 1
            decisions.append(dict(set=label, row=row.get('short') or row.get('id'), kind=kind,
                                  **f.to_json()))
    return c, decisions, unseeable_all


def rates(c):
    def d(a, b):
        return round(a / b, 4) if b else None
    return dict(
        rows=c['rows'], tokens=c['tokens'], slips=c['slips'],
        findings=c['findings'], proposals=c['proposals'], anomalies=c['anomalies'],
        detection_recall=d(c['detected'], c['slips']),
        correction_precision=d(c['correct_corrections'], c['proposals']),
        correction_recall=d(c['correct_corrections'], c['slips']),
        false_correction_rate=d(c['false_corrections'], c['proposals']),
        false_corrections=c['false_corrections'], correct_corrections=c['correct_corrections'],
        proposals_per_1k_tokens=d(1000 * c['proposals'], c['tokens']),
        proper_noun=dict(proposals=c['proposals_pn'], correct=c['correct_corrections_pn'],
                         false=c['false_corrections_pn'],
                         false_correction_rate=d(c['false_corrections_pn'], c['proposals_pn'])),
        common_word=dict(proposals=c['proposals_cw'], correct=c['correct_corrections_cw'],
                         false=c['false_corrections_cw'],
                         false_correction_rate=d(c['false_corrections_cw'], c['proposals_cw'])),
    )


# --------------------------------------------------------------------------- the POC five
def score_poc(verifier, cases):
    out = []
    for case in cases:
        toks_bad = ix.tokens_of(case['observed'])
        toks_ok = ix.tokens_of(case['correct'])
        # the differing position(s)
        tmap = {i: toks_ok[i] for i in range(min(len(toks_bad), len(toks_ok)))
                if toks_bad[i] != toks_ok[i]}
        fs = verifier.analyse(case['observed'], where=case)
        on_target = [f for f in fs if f.i in tmap]
        elsewhere = [f for f in fs if f.i not in tmap]
        prop = [f for f in on_target if f.proposes]
        right = [f for f in prop if f.proposed == tmap[f.i]]
        # what does the signal do to the CORRECT text? any proposal there is a false correction
        fs_ok = verifier.analyse(case['correct'], where=case)
        out.append(dict(
            case=case['id'], kind=case['kind'], observed_span=case['span_observed'],
            correct_span=case['span_correct'],
            differing_tokens=len(tmap) or None,
            detected=bool(on_target), proposed=bool(prop),
            proposed_value=(prop[0].proposed if prop else None),
            correct_proposal=bool(right),
            rule=(prop[0].rule if prop else (on_target[0].rule if on_target else None)),
            reason=(on_target[0].reason if on_target else 'no finding at the corrupted position'),
            evidence=dict(observed_ctx=(on_target[0].observed_ctx_count if on_target else None),
                          alt_ctx=(on_target[0].alt_ctx_count if on_target else None),
                          alt_books=(on_target[0].alt_ctx_books if on_target else None),
                          proper_ratio=(on_target[0].proper_ratio if on_target else None),
                          supporting=len(on_target[0].supporting) if on_target else 0,
                          contradicting=len(on_target[0].contradicting) if on_target else 0),
            false_corrections_elsewhere=[f.to_json() for f in elsewhere if f.proposes],
            false_corrections_on_correct_text=[f.to_json() for f in fs_ok if f.proposes],
        ))
    return out


# --------------------------------------------------------------------------- driver
POLICIES = dict(strict=xc.STRICT, default=xc.DEFAULT, recall=xc.RECALL)


def run_all(idx, scan, d, out_dir=None):
    out_dir = out_dir or paths.OUT
    os.makedirs(out_dir, exist_ok=True)
    report = dict(index=idx.meta, holdout_books=d['holdout_books'], policies={})
    all_decisions = []
    for name, pol in POLICIES.items():
        v = xc.CrossCorpusVerifier(idx, scan, pol)
        poc = score_poc(v, d['poc'])
        c_inj, dec_inj, _ = score_rows(v, d['corrupt'], 'corrupted', truth_for_injection, f'H-inj/{name}')
        c_clean, dec_clean, _ = score_rows(v, d['clean'], 'text', lambda r: {}, f'H-clean/{name}')
        c_lc, dec_lc, unseeable = score_rows(v, d['lanec'], 'text', truth_for_lanec, f'L-lanec/{name}')
        all_decisions += dec_inj + dec_clean + dec_lc
        report['policies'][name] = dict(
            policy=pol.label(),
            poc_cases=poc,
            holdout_injected=rates(c_inj),
            holdout_clean=rates(c_clean),
            lanec_bai8=rates(c_lc),
            lanec_structurally_unseeable=unseeable,
        )
    with open(f'{out_dir}/xcorpus-report.json', 'w', encoding='utf-8') as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    with open(f'{out_dir}/xcorpus-decisions.jsonl', 'w', encoding='utf-8') as fh:
        for row in all_decisions:
            fh.write(json.dumps(row, ensure_ascii=False) + '\n')
    _print(report)
    return report


def _print(report):
    print('\n=== CROSS-CORPUS SIGNAL (D.cross_corpus) ===')
    for name, r in report['policies'].items():
        print(f"\n--- policy {name}: {r['policy']}")
        for setname in ('holdout_injected', 'holdout_clean', 'lanec_bai8'):
            m = r[setname]
            print(f"  {setname:20s} rows={m['rows']:4d} tok={m['tokens']:6d} slips={m['slips']:3d} "
                  f"prop={m['proposals']:3d} anom={m['anomalies']:3d} "
                  f"det_recall={m['detection_recall']} corr_prec={m['correction_precision']} "
                  f"corr_recall={m['correction_recall']} FCR={m['false_correction_rate']} "
                  f"prop/1k={m['proposals_per_1k_tokens']}")
            print(f"  {'':20s} proper-noun {m['proper_noun']} · common {m['common_word']}")
        print('  POC five:')
        for c in r['poc_cases']:
            print(f"    {c['case']} {c['kind']:22s} detect={c['detected']!s:5s} propose={c['proposed']!s:5s} "
                  f"right={c['correct_proposal']!s:5s} → {c['proposed_value']!r} · {c['reason'][:70]}")
            if c['false_corrections_on_correct_text']:
                print(f"       ⚠ proposes a change to the CORRECT text: "
                      f"{[f['observed'] + '→' + f['proposed'] for f in c['false_corrections_on_correct_text']]}")
