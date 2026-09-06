#!/usr/bin/env python3
"""STEP E — measure the blind audit against the PREDECLARED bound. Round 7 does not run it.

    python3 tool/corpus/thresholds/measure.py \
        --annotated <worklist with verdicts filled> --key <SEALED-KEY.json> \
        --bound BOUND-2 --out <json>
    python3 tool/corpus/thresholds/measure.py --dry-run     # proves the machinery, admits nothing

THE BOUND COMES FROM THE LEDGER, NOT FROM THE COMMAND LINE
-----------------------------------------------------------
`--bound` names one of the bounds inside the FROZEN policy payload and nothing else. There is no
flag that sets a threshold value, because a bound that can be passed at measurement time is a
bound that can be chosen after seeing the result. `resolve_bound` reads the frozen payload,
re-hashes it against the ledger, and refuses if it has been edited.

WHAT IS MEASURED, AND WHY IT IS FOUR NUMBERS AND NOT ONE
---------------------------------------------------------
* **false trust** among admitted rows — the annotator's `false_trust` verdict.
* **teaching-critical error** among admitted rows — a SEPARATE number, never folded into the
  first. On the gold plane these two sets overlap without either containing the other: 7 blocks
  are both, 19 only false trust, 5 only teaching-critical. A bound on false trust alone would
  have missed those 5 entirely.
* **over-withholding** among non-admitted rows — because refusing is not free. Round 5's 97-row
  audit found 19 of 30 withheld rows were refused wrongly, and its defect 8 showed that
  withholding one member of a structure makes the served remainder wrong.
* **lesson incidence** — P(a lesson contains at least one teaching-critical error among its
  admitted blocks). This is the number the bound is actually about, and it is measured rather
  than extrapolated from the block rate, because errors cluster.

Every rate is reported with its Wilson 95 % interval and the DECISION USES THE UPPER BOUND. A
point estimate of zero at small n is not evidence of zero.
"""
import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from thresholds import freeze as F        # noqa: E402
from thresholds import policy as P        # noqa: E402


def resolve_bound(bound_id):
    entries = [e for e in F.read_ledger() if e['kind'] == 'policy']
    if not entries:
        raise SystemExit('no frozen policy in the ledger — there is no predeclared bound to '
                         'measure against, and this tool will not invent one')
    e = entries[-1]
    with open(os.path.join(F.ROOT, e['payload_path']), encoding='utf-8') as fh:
        payload = json.load(fh)
    if F.sha256(payload) != e['sha256']:
        raise SystemExit('the frozen policy no longer hashes to its ledger entry')
    if bound_id not in payload['bounds']:
        raise SystemExit(f'{bound_id} is not a bound in the frozen policy '
                         f'({sorted(payload["bounds"])})')
    return payload['bounds'][bound_id], e['sha256']


def _rate(k, n):
    if not n:
        return dict(k=k, n=n, rate=None, upper95=None)
    return dict(k=k, n=n, rate=round(k / n, 4), upper95=round(P.wilson_upper(k, n), 4))


def measure(annotated, key, bound):
    K = key['key']
    adm = [r for r in annotated if K.get(r['row_id'], {}).get('admitted')]
    wh = [r for r in annotated if not K.get(r['row_id'], {}).get('admitted')]
    ft = sum(1 for r in adm if r.get('false_trust') == 'WRONG')
    tc = sum(1 for r in adm if r.get('teaching_critical_fidelity') == 'WRONG')
    harm = sum(1 for r in adm if r.get('false_trust') == 'WRONG'
               or r.get('teaching_critical_fidelity') == 'WRONG')
    unsure = sum(1 for r in adm if 'UNSURE' in
                 (r.get('false_trust'), r.get('teaching_critical_fidelity')))
    over = sum(1 for r in wh if r.get('display_fidelity') == 'OK'
               and r.get('teaching_critical_fidelity') in ('OK', 'NA'))
    lessons = collections.defaultdict(lambda: dict(n=0, tc=0))
    for r in adm:
        k = K[r['row_id']]
        g = lessons[(k['sourceDocumentId'], k['lessonNo'])]
        g['n'] += 1
        g['tc'] += (r.get('teaching_critical_fidelity') == 'WRONG')
    n_les = len(lessons)
    les_tc = sum(1 for g in lessons.values() if g['tc'])

    ft_m, tc_m = _rate(ft, len(adm)), _rate(tc, len(adm))
    reasons = []
    if not adm:
        reasons.append('nothing was admitted')
    for name, m, cap in (('teaching-critical', tc_m, bound.get('tc_rate_upper95_max')),
                         ('false trust', ft_m, bound.get('ft_rate_upper95_max'))):
        if cap is None:
            continue
        if m['upper95'] is None or m['upper95'] > cap:
            reasons.append(f'{name} upper95 {m["upper95"]} > predeclared {cap}')
    need = bound.get('min_audited_trusted_blocks_if_zero_observed')
    if need and len(adm) < need:
        reasons.append(f'only {len(adm)} admitted blocks audited; the bound needs >= {need} '
                       f'to be decidable at zero observed errors')
    if unsure:
        reasons.append(f'{unsure} admitted row(s) judged UNSURE — an undecided row is not a '
                       f'clean row')
    return dict(
        schema='trust-calibration-measurement-v1',
        bound=bound,
        n_annotated=len(annotated), n_admitted=len(adm), n_not_admitted=len(wh),
        false_trust=ft_m, teaching_critical=tc_m,
        harm_union=_rate(harm, len(adm)),
        unsure_admitted=unsure,
        over_withheld=_rate(over, len(wh)),
        lesson_incidence=dict(lessons_with_admitted_blocks=n_les,
                              lessons_with_teaching_critical=les_tc,
                              **{k: v for k, v in _rate(les_tc, n_les).items()
                                 if k in ('rate', 'upper95')}),
        verdict='PASS' if not reasons else 'TRUTHFUL ZERO',
        trusted='as measured' if not reasons else 0,
        why=reasons or ['every predeclared condition met on the blind population'],
        reminder='PASS means the bound held on this population. It is not permission to scale, '
                 'and it is not a claim about any lesson that was not audited.',
    )


def _synthetic(n=200, tc_every=None):
    """Rows for the dry run. Fabricated on purpose: the dry run must prove the MACHINERY, and it
    may not touch real content, because touching real content is step D."""
    ann, key = [], {}
    for i in range(n):
        rid = f'dry{i:04d}'
        bad = tc_every and i % tc_every == 0
        ann.append(dict(row_id=rid, display_fidelity='OK',
                        teaching_critical_fidelity='WRONG' if bad else 'OK',
                        false_trust='WRONG' if bad else 'OK', reading_order='NA',
                        role_fidelity='OK', lesson_attachment='OK'))
        key[rid] = dict(admitted=i % 2 == 0, served=True,
                        sourceDocumentId='SYNTHETIC', lessonNo=i // 10)
    return ann, dict(schema='blind-audit-sealed-key-v1', seed=0, n=n, key=key)


def main():
    ap = argparse.ArgumentParser(description='STEP E — measure against the predeclared bound')
    ap.add_argument('--annotated')
    ap.add_argument('--key')
    ap.add_argument('--bound', default='BOUND-2')
    ap.add_argument('--out')
    ap.add_argument('--dry-run', action='store_true',
                    help='prove the machinery on fabricated rows. Admits nothing, reads no real '
                         'content, and does not use the frozen bound to admit anything.')
    a = ap.parse_args()
    bound, pol_hash = resolve_bound(a.bound)
    if a.dry_run:
        print(f'DRY RUN · bound {bound["id"]} read from frozen policy {pol_hash[:16]}… '
              f'· fabricated rows only · nothing admitted, no real content read\n')
        cases = (('clean, but too small to decide', 600, dict(tc_every=None)),
                 ('clean, audited to the required size', 3000, dict(tc_every=None)),
                 ('1 in 50 teaching-critical', 3000, dict(tc_every=50)),
                 ('1 in 8 teaching-critical', 3000, dict(tc_every=8)))
        for label, n, kw in cases:
            ann, key = _synthetic(n, **kw)
            m = measure(ann, key, bound)
            print(f"  {label:36s} admitted={m['n_admitted']:5d} "
                  f"tc={m['teaching_critical']['rate']} (<= {m['teaching_critical']['upper95']}) "
                  f"-> {m['verdict']}")
            if m['verdict'] != 'PASS':
                print(f"      because: {m['why'][0]}")
        return 0
    if not (a.annotated and a.key):
        raise SystemExit('--annotated and --key are required (or use --dry-run)')
    ann = [json.loads(l) for l in open(a.annotated, encoding='utf-8')]
    key = json.load(open(a.key, encoding='utf-8'))
    m = measure(ann, key, bound)
    m['policy_sha256'] = pol_hash
    if a.out:
        os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
        json.dump(m, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps(m, ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
