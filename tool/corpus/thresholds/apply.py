#!/usr/bin/env python3
"""STEP C — apply a frozen policy to the frozen blind population. **INERT BY DESIGN.**

Round 7 stops before this runs. The module exists so that step C can execute the moment the
Founder approves, and so that the shape of «what would happen» is reviewable now — but every
path through it terminates in a refusal unless an approval artefact exists that names the frozen
policy BY HASH.

    # what it does today, and will keep doing until an approval exists
    $ python3 tool/corpus/thresholds/apply.py --candidate 'C2 · PROSE' --evidence <rows>
    REFUSED: no approval artefact. Round 7 stops at step B.

    # after approval — two commands, in this order, both of them auditable
    $ python3 tool/corpus/thresholds/apply.py --record-approval approval.json
    $ python3 tool/corpus/thresholds/apply.py --candidate 'C2 · PROSE' \
          --evidence <rows for the frozen population> --approval approval.json --out <dir>

An approval artefact must carry `policy_sha256` matching the frozen policy payload,
`population_sha256` matching a frozen population, the candidate name, `decision: "ACTIVATE"`,
and who approved it and when. A hash mismatch is a refusal, not a warning: if the policy has
been edited since approval, the thing approved is not the thing that would run.

Four further refusals, each of which exists because it is the way this could go wrong quietly:

1. **A candidate naming a clause with no implementation is refused.** `C4` names structural
   sibling completeness and independent digit verification; neither exists. Applying it would
   silently admit on the clauses that DO run.
2. **Evidence rows outside the frozen population are refused.** Otherwise the blind population
   could be quietly widened to whatever produced a better number.
3. **A row already carrying a verdict is refused.** Truth must not exist before admission.
4. **`trusted ⊆ served` is asserted on the output**, not assumed.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from thresholds import candidates as C      # noqa: E402
from thresholds import freeze as F          # noqa: E402
from thresholds import policy as P          # noqa: E402

REFUSED = 3
VERDICT_FIELDS = ('truth_wrong_any', 'truth_teaching_critical', 'verdict_false_trust',
                  'verdict_display_fidelity', 'verdict_teaching_critical_fidelity')


class Refused(Exception):
    pass


def _frozen(kind, name=None):
    entries = [e for e in F.read_ledger() if e['kind'] == kind]
    if name:
        entries = [e for e in entries
                   if os.path.basename(e['payload_path']).startswith(name)]
    if not entries:
        raise Refused(f'no frozen {kind} in the ledger')
    e = entries[-1]
    payload = json.load(open(os.path.join(F.ROOT, e['payload_path']), encoding='utf-8'))
    if F.sha256(payload) != e['sha256']:
        raise Refused(f'{kind} payload no longer hashes to its ledger entry — it was edited '
                      f'after freezing')
    return e, payload


def check_approval(approval_path, candidate):
    if not approval_path or not os.path.exists(approval_path):
        raise Refused('no approval artefact. Round 7 stops at step B; steps C-G happen only '
                      'after the Founder approves a frozen policy.')
    ap = json.load(open(approval_path, encoding='utf-8'))
    pe, _ = _frozen('policy')
    if ap.get('policy_sha256') != pe['sha256']:
        raise Refused(f"approval names policy {ap.get('policy_sha256')} but the frozen policy is "
                      f"{pe['sha256']} — the thing approved is not the thing that would run")
    pops = [e['sha256'] for e in F.read_ledger() if e['kind'] == 'population']
    if ap.get('population_sha256') not in pops:
        raise Refused('approval names no frozen population')
    if ap.get('decision') != 'ACTIVATE':
        raise Refused(f"approval decision is {ap.get('decision')!r}, not 'ACTIVATE'")
    if ap.get('candidate') != candidate:
        raise Refused(f"approval is for {ap.get('candidate')!r}, not {candidate!r}")
    for k in ('approved_by', 'approved_at_utc'):
        if not ap.get(k):
            raise Refused(f'approval is missing {k}')
    return ap


def population_keys(population):
    return {(l['sourceDocumentId'], l['lessonNo']) for l in population['lessons']}


def apply_policy(rows, candidate, population):
    pol = C.CANDIDATES[candidate]
    missing = P.unavailable_clauses(pol)
    if missing:
        raise Refused(f'candidate {candidate!r} names clause(s) with no implementation: '
                      f'{missing}. Applying it would admit on the clauses that do run.')
    keys = population_keys(population)
    for r in rows:
        if (r.get('sourceDocumentId'), r.get('lessonNo')) not in keys:
            raise Refused('evidence contains a row outside the frozen blind population')
        for f in VERDICT_FIELDS:
            if r.get(f) is not None:
                raise Refused(f'evidence row already carries a verdict ({f}) — truth must not '
                              f'exist before admission')
    admitted = [r for r in rows if P.admits(r, pol)[0]]
    served = [r for r in rows if r.get('_served')]
    ids = {id(r) for r in served}
    assert all(id(r) in ids for r in admitted), 'INVARIANT VIOLATED: trusted ⊄ served'
    return admitted


def main():
    ap = argparse.ArgumentParser(description='STEP C — apply a frozen policy (inert until '
                                             'a Founder approval artefact exists)')
    ap.add_argument('--candidate', default=None)
    ap.add_argument('--evidence', default=None)
    ap.add_argument('--approval', default=None)
    ap.add_argument('--population', default='BLIND-POPULATION')
    ap.add_argument('--out', default=None)
    ap.add_argument('--record-approval', default=None)
    a = ap.parse_args()
    try:
        if a.record_approval:
            payload = json.load(open(a.record_approval, encoding='utf-8'))
            check_approval(a.record_approval, payload.get('candidate'))
            e = F.freeze('approval', payload, a.record_approval,
                         note='Founder approval of a frozen candidate policy')
            print(f"FROZEN approval sha256={e['sha256']}")
            return 0
        if not (a.candidate and a.evidence):
            raise Refused('nothing to do without --candidate and --evidence')
        check_approval(a.approval, a.candidate)
        _, population = _frozen('population', a.population)
        rows = [json.loads(l) for l in open(a.evidence, encoding='utf-8')]
        admitted = apply_policy(rows, a.candidate, population)
        out = a.out or 'poc-out/round7/ws-t/admitted'
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, 'admitted.jsonl'), 'w', encoding='utf-8') as fh:
            for r in admitted:
                fh.write(json.dumps(r, ensure_ascii=False) + '\n')
        print(f'admitted {len(admitted)} of {len(rows)} rows -> {out}/admitted.jsonl')
        return 0
    except Refused as exc:
        print(f'REFUSED: {exc}')
        return REFUSED


if __name__ == '__main__':
    raise SystemExit(main())
