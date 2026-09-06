#!/usr/bin/env python3
"""Freeze an artefact so the ORDER of this round's work is provable, not asserted.

The Founder's process is ordered A→G and «the order is the whole point». Step A freezes a
candidate policy; step B freezes a blind evaluation population; only after approval may
anything be applied. A policy chosen after seeing what it admits is not a policy, it is a
selection — and the difference between the two is invisible in the finished artefact unless
something records the order.

So: an append-only ledger of SHA-256 commitments, each one carrying the hash of the entry
before it.

    seq 1  kind=policy      sha256=<H1>  prev=null
    seq 2  kind=population  sha256=<H2>  prev=<H1>   binds_policy=<H1>
    seq 3  kind=admitted    sha256=<H3>  prev=<H2>   (POST-APPROVAL ONLY)

An admitted-set entry that claims to precede the policy is arithmetically impossible: it would
have to contain a hash that did not exist. `verify` recomputes every payload hash and the whole
chain, and additionally refuses a ledger in which an `admitted` entry appears before both a
`policy` and a `population` entry.

The ledger is committed to git, so the commit timestamps are a second, independent witness to
the same order.
"""
import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from thresholds.policy import canonical, identity_leaks   # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
FROZEN_DIR = os.path.join(HERE, 'frozen')
LEDGER = os.path.join(FROZEN_DIR, 'LEDGER.jsonl')

#: Kinds, in the only order they may legally appear.
ORDER = ['policy', 'population', 'approval', 'admitted', 'audit', 'measurement']
#: Kinds that may only be frozen after a Founder approval entry exists.
POST_APPROVAL = {'admitted', 'audit', 'measurement'}


def sha256(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def _git(*args):
    try:
        return subprocess.check_output(['git'] + list(args), cwd=HERE,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return None


def read_ledger(path=LEDGER):
    if not os.path.exists(path):
        return []
    return [json.loads(l) for l in open(path, encoding='utf-8') if l.strip()]


def freeze(kind, payload, payload_path, note=None, ledger_path=LEDGER):
    """Append one commitment. Returns the entry. Raises rather than write a bad one."""
    if kind not in ORDER:
        raise ValueError(f'unknown kind {kind!r}')
    entries = read_ledger(ledger_path)
    kinds = {e['kind'] for e in entries}
    if kind in POST_APPROVAL and 'approval' not in kinds:
        raise PermissionError(
            f"refusing to freeze a {kind!r} entry: no Founder approval is recorded in the "
            f"ledger. Steps C-G do not happen before approval.")
    if kind == 'population' and 'policy' not in kinds:
        raise PermissionError(
            'refusing to freeze a population before a policy. The population is frozen AFTER '
            'the policy so that the policy provably did not see it.')
    leaks = identity_leaks(payload)
    if leaks:
        raise PermissionError(
            f'refusing to freeze: payload names lesson/book identities in an admission '
            f'context at {leaks[:3]}')
    h = sha256(payload)
    entry = dict(
        seq=len(entries) + 1, kind=kind, sha256=h,
        prev=entries[-1]['sha256'] if entries else None,
        frozen_at_utc=datetime.datetime.now(datetime.timezone.utc)
                      .strftime('%Y-%m-%dT%H:%M:%SZ'),
        payload_path=os.path.relpath(payload_path, ROOT),
        git_commit=_git('rev-parse', 'HEAD'),
        git_branch=_git('rev-parse', '--abbrev-ref', 'HEAD'),
        note=note,
    )
    if kind == 'population':
        entry['binds_policy'] = [e['sha256'] for e in entries if e['kind'] == 'policy'][-1]
    os.makedirs(os.path.dirname(ledger_path), exist_ok=True)
    with open(ledger_path, 'a', encoding='utf-8') as fh:
        fh.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + '\n')
    return entry


def verify(ledger_path=LEDGER, root=None):
    """Recompute every payload hash and the whole chain. Returns (ok, problems)."""
    root = root or ROOT
    entries = read_ledger(ledger_path)
    problems = []
    prev = None
    seen = []
    for i, e in enumerate(entries):
        if e.get('seq') != i + 1:
            problems.append(f"seq {e.get('seq')} out of order at position {i + 1}")
        if e.get('prev') != prev:
            problems.append(f"seq {e.get('seq')}: prev {e.get('prev')} != {prev}")
        p = os.path.join(root, e['payload_path'])
        if not os.path.exists(p):
            problems.append(f"seq {e['seq']}: payload missing at {e['payload_path']}")
        else:
            got = sha256(json.load(open(p, encoding='utf-8')))
            if got != e['sha256']:
                problems.append(f"seq {e['seq']}: payload hash {got} != recorded {e['sha256']}")
        if e['kind'] in POST_APPROVAL and 'approval' not in seen:
            problems.append(f"seq {e['seq']}: {e['kind']} appears with no prior approval")
        if e['kind'] == 'population':
            if 'policy' not in seen:
                problems.append(f"seq {e['seq']}: population frozen before any policy")
            elif e.get('binds_policy') not in [x['sha256'] for x in entries[:i]
                                               if x['kind'] == 'policy']:
                problems.append(f"seq {e['seq']}: binds_policy names no earlier policy entry")
        seen.append(e['kind'])
        prev = e['sha256']
    return (not problems), problems


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def build_policy_payload(derivation_path, inputs):
    """Step A's payload: the candidates, the bounds, the recommendation, and the expected
    trade-offs EXPRESSED AS RATES. No lesson, book or page identity appears anywhere."""
    from thresholds import candidates as C
    from thresholds import policy as P
    der = json.load(open(derivation_path, encoding='utf-8'))
    trade = {}
    for name, m in der['candidates'].items():
        trade[name] = {k: m[k] for k in (
            'n_served', 'n_trusted', 'trusted_share_of_served', 'ft_k', 'ft_rate', 'ft_upper95',
            'tc_k', 'tc_rate', 'tc_upper95', 'harm_k', 'harm_rate', 'harm_split', 'by_role',
            'by_subject', 'page_incidence', 'refused_by', 'unavailable_clauses',
            'MEASUREMENT_INVALID', 'evaluated_on') if k in m}
    return dict(
        schema='trust-policy-freeze-v1',
        frozen_for='round 7 · WS-T · step A — candidate policy and bound, before any application',
        invariant='TRUST = SERVED ∩ admit(...). Activation cannot serve one new block.',
        blocks_per_lesson=C.BLOCKS_PER_LESSON,
        clauses={cid: {k: v for k, v in c.items() if k != 'predicate'}
                 for cid, c in P.CLAUSES.items()},
        candidates=[{k: v for k, v in c.items() if k != 'bound'} | {'bound_id': c['bound']['id']}
                    for c in C.CANDIDATES.values()],
        bounds=C.BOUNDS,
        recommendation=C.RECOMMENDATION,
        expected_tradeoffs_no_identities=trade,
        plane_disagreement=der['planes'],
        guard_free_observations=der['guard_free_observations'],
        derivation_inputs=inputs,
        declared_limitations=[
            'The gold plane is 54 DELIBERATELY HARD pages, not a sample (A3 §5.2). No rate in '
            'this payload transfers to the corpus, and none is offered as a corpus estimate.',
            'Teaching-critical is defined NARROWLY on the gold plane (corrupted digits, a '
            'non-question served as a question). The audit protocol also counts truncation, '
            'in-sentence contamination and term-level tone slips. The two are not comparable and '
            'are never summed.',
            'Every candidate was derived on evidence rows that ALREADY EXISTED before this round. '
            'The 181 rows marked held_out in that file were pooled into A3\'s published curve, so '
            'they are NOT a blind holdout and are not used as one here.',
            'The 97-row independent audit exists in this repository only as a published summary '
            'table, not as row-level data. Disjointness of the blind population from it can be '
            'argued from book coverage but CANNOT BE PROVEN. Recorded as a known weakness.',
            'Independence between blocks in a lesson is assumed by the bound arithmetic and is '
            'optimistic: errors cluster by page and by book.',
        ])


def main():
    ap = argparse.ArgumentParser(description='freeze / verify the trust-calibration ledger')
    ap.add_argument('cmd', choices=('verify', 'show', 'policy'))
    ap.add_argument('--ledger', default=LEDGER)
    ap.add_argument('--derivation', default=None)
    ap.add_argument('--input', action='append', default=[],
                    help='NAME=PATH of an evidence file the derivation consumed')
    a = ap.parse_args()
    if a.cmd == 'policy':
        if not a.derivation:
            return print('--derivation is required') or 2
        inputs = []
        for spec in a.input:
            name, _, path = spec.partition('=')
            inputs.append(dict(name=name, path=path, sha256=file_sha256(path),
                               gitignored=path.startswith('poc-out/')))
        payload = build_policy_payload(a.derivation, inputs)
        os.makedirs(FROZEN_DIR, exist_ok=True)
        out = os.path.join(FROZEN_DIR, 'TRUST-POLICY-CANDIDATES-v1.json')
        json.dump(payload, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        e = freeze('policy', payload, out,
                   note='candidate trust policies + bound options, derived from pre-existing '
                        'evidence only; nothing applied, nothing activated')
        print(f"FROZEN policy  sha256={e['sha256']}  at {e['frozen_at_utc']}  -> {out}")
        return 0
    if a.cmd == 'show':
        for e in read_ledger(a.ledger):
            print(f"{e['seq']:>3}  {e['kind']:<12} {e['sha256'][:16]}…  {e['frozen_at_utc']}  "
                  f"{e['payload_path']}")
        return 0
    ok, problems = verify(a.ledger)
    if ok:
        n = len(read_ledger(a.ledger))
        print(f'LEDGER OK — {n} commitment(s), chain intact, every payload hashes as recorded.')
        return 0
    print('LEDGER BROKEN:')
    for p in problems:
        print('  -', p)
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
