#!/usr/bin/env python3
"""LANE C (round 5, §11) — a MEASUREMENT, not a repairer: could a deterministic, non-LLM,
in-corpus signal have produced the right Vietnamese tone repair on LS&ĐL 5 Bài 8?

Round 4 falsified «two stacks agreeing ⇒ verbatim» (A26) and round 5's strategy is
DETECT → REPAIR candidate → VALIDATE → RESTORE or WITHHOLD. Lane A1 owns the repairer; Lane C owns
one hard case and the ground truth for it (a human read of the printed page,
`docs/research/lane-c/data/lsdl5-bai8-verbatim-ledger.json`). This probe asks the falsifiable question:

    given ONLY the pipeline's own TRUSTED text, does a context-scoped tone-majority signal
    generate the repair the print actually shows — and how often does it generate a WRONG one?

Signal under test (deterministic, no lexicon file, no model):
  key(token) = (tone-stripped previous token, tone-stripped token)          ← context-scoped, so
                                                                             «Bạch Đằng» and «Đăng Khoa»
                                                                             are different keys
  evidence   = surface forms of that key across the TRUSTED blocks of the scope (lesson or book)
  candidate  = the strict-majority form M when M ≠ the observed form F, count(M) ≥ `--min-support`,
               and F is never observed for that key anywhere in the scope

Tone-stripping removes ONLY the five tone marks (´ ` ̉ ̃ ̣); vowel quality (ă â ê ô ơ ư) and «đ» are
kept, so «HÂN» and «HÁN» are NOT the same key — a limitation this probe reports rather than hides.

Nothing is written back into any pipeline artefact: a candidate is a REPAIRED CANDIDATE with its
supporting evidence, and only VALIDATION (here: the human read) may promote it.

    python3 tool/research/lane_c/tone_repair_probe.py [--scope lesson|book] [--min-support 2] [--out DIR]
"""
import argparse
import json
import os
import re
import unicodedata
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
MAIN = '/Users/alexnguyen/projects/workizen-ai-learning-coach'
BOOK = '05-sgk-lich-su-va-dia-li-5'
LESSON = 8
R5 = f'{MAIN}/poc-out/round5/lane-c/tc2-lsdl5/v1/root/poc-out/trusted-corpus/tc-v2/tc2-r5'
LEDGER = f'{REPO}/docs/research/lane-c/data/lsdl5-bai8-verbatim-ledger.json'

TONES = {'́', '̀', '̉', '̃', '̣'}   # ´ ` ̉ ̃ ̣ — the five Vietnamese tones
WORD = re.compile(r"[^\W\d_]+", re.UNICODE)


def strip_tone(word):
    """Remove ONLY tone marks; keep ă â ê ô ơ ư đ. «đằng» and «đăng» collapse; «HÂN» and «HÁN» do not."""
    d = unicodedata.normalize('NFD', word)
    return unicodedata.normalize('NFC', ''.join(c for c in d if c not in TONES)).lower()


def tokens(text):
    return WORD.findall(text or '')


def keyed(text):
    """[(key, surface)] — key is (tone-stripped previous token or '^', tone-stripped token)."""
    ts = tokens(text)
    out = []
    for i, t in enumerate(ts):
        prev = strip_tone(ts[i - 1]) if i else '^'
        out.append(((prev, strip_tone(t)), t))
    return out


def load(path):
    with open(path, encoding='utf-8') as fh:
        return json.load(fh)


def short(block_id):
    parts = (block_id or '').split(':')
    return ':'.join(parts[1:]) if len(parts) >= 4 else (block_id or '')


def tsl_paths(scope):
    d = f'{R5}/lessons/{BOOK}'
    if scope == 'book':
        return [f'{d}/{n}' for n in sorted(os.listdir(d)) if n.endswith('.tsl.json')]
    return [f'{d}/bai-{LESSON:02d}.tsl.json']


def evidence(scope):
    """key → Counter(lower-cased surface form) over the TRUSTED blocks of the scope — what the pipeline
    itself already believes, with no help from the human read."""
    ev = defaultdict(Counter)
    for p in tsl_paths(scope):
        for b in load(p)['blocks']:
            for k, surface in keyed(b.get('text')):
                ev[k][surface.lower()] += 1
    return ev


def recase(proposed, observed):
    """Give the proposal the casing of the token it replaces («kì» beside «KĨ» → «KÌ»)."""
    if observed.isupper():
        return proposed.upper()
    if observed[:1].isupper():
        return proposed[:1].upper() + proposed[1:]
    return proposed


# Two rule variants, both deterministic and both reported — R2 is not «the» rule, it is the sensitivity
# of the answer to one design choice (does an attested-but-wrong form veto a repair?).
RULES = ('strict-unattested', 'dominant-majority')


def candidates(text, ev, min_support, rule, dominance):
    """Repair candidates for one block. Nothing is applied; each carries its supporting counts."""
    out = []
    for i, (k, surface) in enumerate(keyed(text)):
        counts = ev.get(k)
        if not counts:
            continue
        f = surface.lower()
        best, n = counts.most_common(1)[0]
        if best == f or n < min_support:
            continue
        seen = counts.get(f, 0)
        if rule == 'strict-unattested':
            # a repair only where the observed form is attested NOWHERE and the evidence is unanimous
            if seen or len(counts) > 1:
                continue
        else:
            # a repair where the majority form dominates the observed one by `dominance`×
            if n < dominance * max(1, seen):
                continue
        out.append(dict(index=i, observed=surface, proposed=recase(best, surface),
                        support=n, observedSupport=seen, variants=dict(counts)))
    return out


def run(scope, min_support, rule, dominance):
    ledger = load(LEDGER)
    ev = evidence(scope)
    tsl = load(f'{R5}/lessons/{BOOK}/bai-{LESSON:02d}.tsl.json')
    texts = {}
    for b in tsl['blocks']:
        texts[short(b['id'])] = ('TRUSTED', b.get('text') or '')
    for b in tsl['withheld']:
        texts[short(b['id'])] = ('WITHHELD', '')      # the TSL withholds text — read it from the SDM instead
    sdm_dir = f'{R5}/sdm/{BOOK}'
    for name in sorted(os.listdir(sdm_dir)):
        page = load(f'{sdm_dir}/{name}')
        for b in page['blocks']:
            sid = short(b['id'])
            if sid in texts and texts[sid][0] == 'WITHHELD':
                texts[sid] = ('WITHHELD', b.get('text') or '')

    rows, tally = [], Counter()
    for entry in ledger['blocks']:
        bid = entry['block']
        status, text = texts.get(bid, ('?', ''))
        if not text:
            continue
        cands = candidates(text, ev, min_support, rule, dominance)
        printed = {s['pipeline']: s['printed'] for s in (entry.get('slips') or [])}
        matched, wrong = [], []
        for c in cands:
            want = printed.get(c['observed'])
            (matched if want is not None and want.lower() == c['proposed'].lower() else wrong).append(c)
        missed = [k for k in printed if not any(c['observed'] == k for c in cands)]
        tally['slips'] += len(printed)
        tally['candidates'] += len(cands)
        tally['correct'] += len(matched)
        tally['false_corrections'] += len(wrong)
        tally['missed'] += len(missed)
        if cands or printed:
            rows.append(dict(block=bid, status=status, verdict=entry['verdict'],
                             slips=[f'{k}→{v}' for k, v in printed.items()],
                             candidates=[f"{c['observed']}→{c['proposed']} (support {c['support']})" for c in cands],
                             correct=[f"{c['observed']}→{c['proposed']}" for c in matched],
                             falseCorrections=[f"{c['observed']}→{c['proposed']}" for c in wrong],
                             missed=missed))
    precision = tally['correct'] / tally['candidates'] if tally['candidates'] else None
    recall = tally['correct'] / tally['slips'] if tally['slips'] else None
    fcr = tally['false_corrections'] / tally['candidates'] if tally['candidates'] else None
    return dict(scope=scope, rule=rule, minSupport=min_support, dominance=dominance,
                evidenceKeys=len(ev), tally=dict(tally),
                precision=precision, recall=recall, falseCorrectionRate=fcr, rows=rows)


def render(reps):
    L = ['# Tone-repair probe on LS&ĐL 5 Bài 8 (Lane C, round 5)', '',
         'Question: using only the pipeline\'s own TRUSTED text, does a context-scoped tone-majority signal '
         'generate the repair the PRINT shows — and how often does it generate a wrong one? Ground truth is the '
         'human verbatim ledger. Nothing is applied to any artefact; every hit is a REPAIRED CANDIDATE.', '',
         '| rule | scope | min support | evidence keys | slips in the lesson | candidates | correct | false corrections | missed | precision | recall | false-correction rate |',
         '|---|---|---|---|---|---|---|---|---|---|---|---|']
    for r in reps:
        t = r['tally']
        fmt = lambda v: '—' if v is None else f'{v:.3f}'
        L.append(f"| {r['rule']} | {r['scope']} | {r['minSupport']} | {r['evidenceKeys']} | {t.get('slips', 0)} | {t.get('candidates', 0)} | "
                 f"{t.get('correct', 0)} | {t.get('false_corrections', 0)} | {t.get('missed', 0)} | "
                 f"{fmt(r['precision'])} | {fmt(r['recall'])} | {fmt(r['falseCorrectionRate'])} |")
    for r in reps:
        L += ['', f"## rule = {r['rule']} · scope = {r['scope']} · block by block", '',
              '| block | pipeline status | print verdict | slips the print shows | candidates the signal generated | correct | false corrections | missed |',
              '|---|---|---|---|---|---|---|---|']
        for row in r['rows']:
            L.append('| ' + ' | '.join([row['block'], row['status'], row['verdict'],
                                        '; '.join(row['slips']) or '—', '; '.join(row['candidates']) or '—',
                                        '; '.join(row['correct']) or '—', '; '.join(row['falseCorrections']) or '—',
                                        '; '.join(row['missed']) or '—']) + ' |')
    return '\n'.join(L) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scope', default='both', choices=('lesson', 'book', 'both'))
    ap.add_argument('--min-support', type=int, default=2)
    ap.add_argument('--dominance', type=int, default=2, help='dominant-majority: how many times the majority form must beat the observed one')
    ap.add_argument('--out', default=f'{MAIN}/poc-out/round5/lane-c/tc2-lsdl5/v1/report')
    ap.add_argument('--copy-md', default=None)
    a = ap.parse_args()
    scopes = ['lesson', 'book'] if a.scope == 'both' else [a.scope]
    reps = [run(s, a.min_support, rule, a.dominance) for rule in RULES for s in scopes]
    os.makedirs(a.out, exist_ok=True)
    with open(f'{a.out}/tone-repair-probe.json', 'w', encoding='utf-8') as fh:
        json.dump(reps, fh, ensure_ascii=False, indent=2)
    md = render(reps)
    with open(f'{a.out}/tone-repair-probe.md', 'w', encoding='utf-8') as fh:
        fh.write(md)
    if a.copy_md:
        with open(a.copy_md, 'w', encoding='utf-8') as fh:
            fh.write(md)
    print(f'{a.out}/tone-repair-probe.md')
    for r in reps:
        t = r['tally']
        print(f"  {r['rule']}/{r['scope']}: candidates {t.get('candidates', 0)} correct {t.get('correct', 0)} "
              f"false {t.get('false_corrections', 0)} missed {t.get('missed', 0)} of {t.get('slips', 0)} slips")


if __name__ == '__main__':
    main()
