#!/usr/bin/env python3
"""Round 5 · Lane D — SILENT LOSS: content that is neither served nor withheld.

Lane A2 (PR #84) reported that 14 of 15 Docling formula-labelled blocks on the Toán pages die at
`tc2_sdm.py:276-277` as role `empty` with reason `empty_block` and evidence "no letters" — a ROLE
decision, not a math one, and one of them carries `'7 8 2 8 7 - 2 8 5 8'`. Checked on Lane D's own
batches the effect is larger, and it lands on Lane D's denominators rather than on Lane A2's:

    a block whose role is `empty` never reaches the Trusted Structured Lesson AT ALL.
    It is not in `blocks` (served) and it is not in `withheld` (refused).

So it is invisible to every rate Lane D reports. `learning blocks = trusted + withheld` excludes it,
which means the **served share is computed over a denominator that has already dropped this content**,
and the **over-withhold rate cannot see it** because it only reviews regions that were withheld.

Withholding is a decision a child's lesson can be audited for. This is not withholding — it is a
disappearance, and it carries no reason code into the TSL. A pipeline that refuses to guess must
still be able to say what it refused.

    silent_loss.py scan --batch-dir DIR --pipeline ID [--out FILE] [--md FILE]

Counts only; the block text stays in gitignored poc-out (D4). What the repo carries is how much was
lost, how much of it carried digits, and on which lessons.

ROUND 6 (WS-A, R13): this file is FROZEN as the historical measurement. Its behaviour is unchanged so
round 5's published numbers stay reproducible from round 5's artefacts — verified: batch 2
232/135/27 → 0.6322/0.5888, batch 1 (holdout) 196/124/55 → 0.6125/0.5227. Its successor is
`tool/corpus/accounting/ledger.py`, which partitions the WHOLE input population rather than scanning
for one role, and FAILS (non-zero exit) instead of reporting. The two agree exactly on these batches,
which is why the ledger can be trusted to have replaced it rather than merely reworded it. Round 6
also shows this tool's correction is a LOWER BOUND: it puts every lost region into the learning
denominator, and 50 of the 82 turned out to be defined non-learning regions.
"""
import argparse
import collections
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402

SCHEMA = 'lane-d-silent-loss-v1'
DIGIT = re.compile(r'\d')
# An expression-shaped run: two digit groups with an arithmetic operator between them. Deliberately
# loose — the point is «this had arithmetic in it», not «this is a valid expression».
EXPRESSION = re.compile(r'\d[\d\s]*\s*[+\-−×÷:x*/]\s*[\d\s]*\d')
SILENT_ROLES = ('empty',)
SILENT_REASONS = ('empty_block',)


def _role(b):
    r = b.get('role')
    return r.get('value') if isinstance(r, dict) else r


def scan_lesson(batch_dir, pipeline, book, lesson):
    tslp = (f'{batch_dir}/tcroot/poc-out/trusted-corpus/tc-v2/{pipeline}/lessons/'
            f'{book}/bai-{int(lesson):02d}.tsl.json')
    tsl = common.load_json(tslp)
    if not tsl:
        return None
    pages = set((tsl.get('boundary') or {}).get('pages') or [])
    in_tsl = {b['id'] for b in tsl.get('blocks', [])} | {w['id'] for w in tsl.get('withheld', [])}
    st = tsl.get('stats') or {}

    silent, with_digits, with_expr, leaked = [], [], [], 0
    for f in sorted(glob.glob(f'{batch_dir}/tcroot/poc-out/trusted-corpus/tc-v2/{pipeline}/sdm/{book}/*.json')):
        d = common.load_json(f) or {}
        if d.get('page') not in pages:
            continue
        for b in d.get('blocks', []):
            reasons = b.get('reasons') or b.get('withhold_reasons') or []
            if _role(b) not in SILENT_ROLES and not (set(reasons) & set(SILENT_REASONS)):
                continue
            txt = b.get('text') or ''
            silent.append(b)
            if DIGIT.search(txt):
                with_digits.append(b)
            if EXPRESSION.search(txt):
                with_expr.append(b)
            if b['id'] in in_tsl:
                leaked += 1
    trusted, withheld = int(st.get('trusted') or 0), int(st.get('withheld') or 0)
    return dict(
        book=book, lesson=int(lesson),
        trusted=trusted, withheld=withheld,
        learningBlocksAsReported=trusted + withheld,
        silentlyLost=len(silent),
        silentlyLostCarryingDigits=len(with_digits),
        silentlyLostCarryingAnExpression=len(with_expr),
        silentlyLostThatDoReachTheTsl=leaked,
        # The share a lesson actually serves, once the silent losses are put back in the denominator.
        servedShareAsReported=(round(trusted / (trusted + withheld), 4) if (trusted + withheld) else None),
        servedShareWithSilentLoss=(round(trusted / (trusted + withheld + len(silent)), 4)
                                   if (trusted + withheld + len(silent)) else None),
        exampleIds=[b['id'] for b in with_expr][:6])


def cmd_scan(a):
    spec = common.load_json(f'{a.batch_dir}/batch-spec.json', {})
    rows = []
    for L in spec.get('lessons', []):
        r = scan_lesson(a.batch_dir, a.pipeline, L['book'], L['lesson'])
        if r:
            rows.append(r)
    tot_t = sum(r['trusted'] for r in rows)
    tot_w = sum(r['withheld'] for r in rows)
    tot_s = sum(r['silentlyLost'] for r in rows)
    tot_d = sum(r['silentlyLostCarryingDigits'] for r in rows)
    tot_e = sum(r['silentlyLostCarryingAnExpression'] for r in rows)
    leaked = sum(r['silentlyLostThatDoReachTheTsl'] for r in rows)
    out = dict(
        schema=SCHEMA, batchDir=os.path.abspath(a.batch_dir), pipeline=a.pipeline,
        finding='a block whose role is `empty` reaches neither `blocks` nor `withheld` of the TSL, so it is '
                'invisible to every served/withheld rate — including the over-withhold rate, which reviews '
                'only regions that WERE withheld (Lane A2, PR #84, tc2_sdm.py:276-277)',
        lessons=len(rows),
        trusted=tot_t, withheld=tot_w,
        learningBlocksAsReported=tot_t + tot_w,
        silentlyLost=tot_s,
        silentlyLostCarryingDigits=tot_d,
        silentlyLostCarryingAnExpression=tot_e,
        silentlyLostThatDoReachTheTsl=leaked,
        servedShareAsReported=(round(tot_t / (tot_t + tot_w), 4) if (tot_t + tot_w) else None),
        servedShareWithSilentLoss=(round(tot_t / (tot_t + tot_w + tot_s), 4) if (tot_t + tot_w + tot_s) else None),
        silentLossShareOfAllExtractedBlocks=(round(tot_s / (tot_t + tot_w + tot_s), 4)
                                             if (tot_t + tot_w + tot_s) else None),
        perLesson=rows)
    if a.out:
        common.dump_json(out, a.out)
        print(f'→ {a.out}')
    for r in rows:
        print(f"  {r['book']} Bài {r['lesson']}: trusted {r['trusted']} withheld {r['withheld']} "
              f"· SILENTLY LOST {r['silentlyLost']} (digits {r['silentlyLostCarryingDigits']}, "
              f"expressions {r['silentlyLostCarryingAnExpression']}) "
              f"· served share {r['servedShareAsReported']} → {r['servedShareWithSilentLoss']}")
    print(f"  TOTAL trusted {tot_t} · withheld {tot_w} · SILENTLY LOST {tot_s} "
          f"({tot_d} with digits, {tot_e} with an expression)")
    print(f"  served share as reported {out['servedShareAsReported']} → with the silent loss in the "
          f"denominator {out['servedShareWithSilentLoss']}")
    if leaked:
        print(f'  note: {leaked} of them DO reach the TSL — the role is not always terminal')
    if a.md:
        L = ['| lesson | trusted | withheld | **silently lost** | of those, digits | expressions | served share as reported | served share incl. silent loss |',
             '|---|---|---|---|---|---|---|---|']
        for r in rows:
            L.append(f"| {common.book_label(r['book'])} Bài {r['lesson']} | {r['trusted']} | {r['withheld']} | "
                     f"**{r['silentlyLost']}** | {r['silentlyLostCarryingDigits']} | "
                     f"{r['silentlyLostCarryingAnExpression']} | {r['servedShareAsReported']} | "
                     f"{r['servedShareWithSilentLoss']} |")
        L.append(f"| **all** | **{tot_t}** | **{tot_w}** | **{tot_s}** | **{tot_d}** | **{tot_e}** | "
                 f"**{out['servedShareAsReported']}** | **{out['servedShareWithSilentLoss']}** |")
        os.makedirs(os.path.dirname(os.path.abspath(a.md)), exist_ok=True)
        open(a.md, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
        print(f'markdown → {a.md}')
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('scan')
    s.add_argument('--batch-dir', required=True)
    s.add_argument('--pipeline', required=True)
    s.add_argument('--out', default='')
    s.add_argument('--md', default='')
    s.set_defaults(fn=cmd_scan)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == '__main__':
    sys.exit(main())
