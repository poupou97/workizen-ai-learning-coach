#!/usr/bin/env python3
"""PHASE B — per-row measurement of the served plane, so a before/after is ATTRIBUTABLE.

Founder order 47 §PHASE C forbids "tests green therefore solved". A total that moves from 12
to 7 says nothing about *which* rows moved, and an aggregate cannot separate a rule that
removes the rows it was derived from (in-sample) from a rule that generalises. This harness
rebuilds every gold page with the code as it stands in the checkout it is run from and writes
ONE ROW PER GOLD LEARNING BLOCK. Two runs — one on `origin/main`, one on the branch — are
then diffed row by row, so every delta is attributed to a named block.

It ships no rule and patches nothing: the arm is decided by which checkout you run it from.

D4: `--out` carries ids, roles, booleans and counts. Served and printed strings go only to
`--detail`, which must live outside the repository.

ABSENCE CANNOT SATISFY A POSITIVE OBLIGATION, and TEST POPULATIONS MUST CONTAIN THE FAILING
CASE. The run aborts, non-zero and UNVERIFIED, unless every one of the twelve rows Phase A
traced is present and matched in the rebuilt population. A veto measured over a population
that lost its failing rows prints a flawless zero.
"""
import argparse
import collections
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.dirname(HERE)
sys.path.insert(0, CORPUS)
sys.path.insert(0, os.path.join(CORPUS, 'thresholds'))

import tc_sdm      # noqa: E402
import tc2_sdm     # noqa: E402
import evidence    # noqa: E402

#: The twelve rows Phase A traced (`docs/research/PHASE-A-ROOT-CAUSE-AUDIT.md` §3), by
#: (book, page, gold block id). The population is not adequate for this measurement unless it
#: holds all twelve — matched, on the served plane or off it.
PHASE_A_ROWS = (
    ('04-sgk-khoa-hoc-4', 9, 'b10'),                 # 1  recognition
    ('07-sgk-khoa-hoc-tu-nhien-7', 21, 'b14'),       # 2  recognition
    ('07-sgk-toan-7-tap-hai', 41, 'b03'),            # 3  role   (P1 derivation row)
    ('09-sgk-khoa-hoc-tu-nhien-9', 46, 'b01'),       # 4  segmentation
    ('09-sgk-ngu-van-9-tap-mot', 67, 'b05'),         # 5  recognition
    ('09-sgk-ngu-van-9-tap-mot', 83, 'b04'),         # 6  recognition
    ('09-sgk-toan-9-tap-mot', 29, 'b01'),            # 7  role   (P2 derivation row)
    ('09-sgk-toan-9-tap-mot', 29, 'b13'),            # 8  matcher artefact
    ('10-sgk-vat-li-10', 30, 'b03'),                 # 9  role   (P2 derivation row)
    ('10-sgk-vat-li-10', 30, 'b19'),                 # 10 role   (P3 derivation row)
    ('10-sgk-vat-li-10', 89, 'b06'),                 # 11 role   (no veto touches it)
    ('10-sgv-tin-hoc-10', 39, 'b09'),                # 12 tokeniser artefact
)

KEEP = ('book', 'page', 'gold_id', 'gold_role', 'held_out', 'matched', 'block_id',
        'pipeline_trusted', 'pipeline_status', 'role_value', 'role_coarse',
        'role_confidence', 'role_method', 'truth_wrong', 'truth_wrong_any',
        'truth_digits_wrong', 'truth_as_question', 'truth_teaching_critical', 'cer', 'edits')


def load_overlay(path):
    """Adjudication overlay: {(book, page, gold_id): role}. The committed gold is NEVER written."""
    if not path:
        return {}
    doc = json.load(open(path))
    return {(o['book'], o['page'], o['gold_id']): o['to'] for o in doc['overlay']}


def rebuild(pages, gold_dir, pipeline='tc2-p2', overlay=None):
    rows, detail = [], []
    overlay = overlay or {}
    applied = 0
    for book, page in pages:
        sdm = tc2_sdm.build_page(book, page, pipeline=pipeline)
        gold = json.load(open(f'{gold_dir}/{book}-p{page:03d}.json'))
        for g in gold['blocks']:
            if (book, page, g['id']) in overlay:
                g['role'] = overlay[(book, page, g['id'])]
                applied += 1
        for r in evidence.gold_page_rows(gold, sdm):
            rows.append({k: r.get(k) for k in KEEP})
            detail.append(dict(book=r['book'], page=r['page'], gold_id=r['gold_id'],
                               gold_text=(next((g.get('text') or g.get('anchor')
                                                for g in gold['blocks'] if g['id'] == r['gold_id']), None)),
                               role_value=r.get('role_value'), block_id=r.get('block_id')))
    if overlay and applied != len(overlay):
        raise SystemExit(f'UNVERIFIED: the adjudication overlay names {len(overlay)} rows but only '
                         f'{applied} were found in the rebuilt population. An overlay that silently '
                         f'applies to nothing would leave the numbers unchanged and look like agreement.')
    return rows, detail


def summarise(rows):
    served = [r for r in rows if r['pipeline_trusted']]
    T = collections.Counter()
    T['learning'] = len(rows)
    T['served'] = len(served)
    T['false_trust'] = sum(1 for r in served if r['truth_wrong_any'])
    T['teaching_critical'] = sum(1 for r in served if r['truth_teaching_critical'])
    T['digits'] = sum(1 for r in served if r['truth_digits_wrong'])
    T['as_question'] = sum(1 for r in served if r['truth_as_question'])
    T['correct_questions'] = sum(1 for r in served
                                 if r['role_coarse'] == 'QUESTION' and r['gold_role'] == 'question')
    T['role_wrong'] = sum(1 for r in served
                          if tc_sdm.GOLD_ROLE_MAP.get(r['gold_role'], 'UNKNOWN') != r['role_coarse'])
    return T


def main():
    ap = argparse.ArgumentParser(description='Phase B per-row served-plane measurement')
    ap.add_argument('--sdm', help='sdm-gold directory naming the pages to rebuild')
    ap.add_argument('--pages-from-gold', action='store_true',
                    help='the plane is every page in --gold-dir (used for the Bài 17 gold set, which '
                         'has no SDM run of its own)')
    ap.add_argument('--require', choices=('phase-a', 'none'), default='phase-a',
                    help='population adequacy: "phase-a" demands all twelve traced rows be present and '
                         'matched. "none" is only for a DIFFERENT plane and then --min-rows is mandatory')
    ap.add_argument('--min-rows', type=int, help='minimum learning rows the plane must hold')
    ap.add_argument('--gold-dir', default=os.path.join(CORPUS, 'tc_gold'))
    ap.add_argument('--out', required=True, help='per-row JSONL (ids/roles/booleans only)')
    ap.add_argument('--detail', help='D4 readings; must live outside the repository')
    ap.add_argument('--adjudication', help='role-adjudication overlay (see ROLE-ADJUDICATION-v1.json)')
    ap.add_argument('--label', default='arm')
    ns = ap.parse_args()

    if ns.require == 'none' and ns.min_rows is None:
        raise SystemExit('UNVERIFIED: --require none removes the failing-case guarantee, so the plane '
                         'must declare its own size with --min-rows. Absence cannot satisfy a positive '
                         'obligation.')
    pages = []
    if ns.pages_from_gold:
        for f in sorted(glob.glob(os.path.join(ns.gold_dir, '*-p[0-9][0-9][0-9].json'))):
            g = json.load(open(f))
            pages.append((g['book'], g['page']))
    else:
        if not ns.sdm:
            raise SystemExit('UNVERIFIED: give --sdm or --pages-from-gold; there is nothing to measure')
        for f in sorted(glob.glob(os.path.join(ns.sdm, '*', 'p*.sdm.json'))):
            d = json.load(open(f))
            if os.path.exists(f"{ns.gold_dir}/{d['book']}-p{d['page']:03d}.json"):
                pages.append((d['book'], d['page']))
    if not pages:
        raise SystemExit('UNVERIFIED: no gold page in this plane; there is nothing to measure')

    rows, detail = rebuild(pages, ns.gold_dir, overlay=load_overlay(ns.adjudication))
    if ns.min_rows is not None and len(rows) < ns.min_rows:
        raise SystemExit(f'UNVERIFIED: the plane holds {len(rows)} learning rows, fewer than the '
                         f'{ns.min_rows} it declares adequate.')
    if ns.require == 'phase-a':
        present = {(r['book'], r['page'], r['gold_id']) for r in rows if r['matched']}
        missing = [k for k in PHASE_A_ROWS if k not in present]
        if missing:
            raise SystemExit('UNVERIFIED: the rebuilt population does not contain the failing cases '
                             f'({len(missing)} of {len(PHASE_A_ROWS)} Phase A rows absent or unmatched): '
                             + ', '.join(f'{b} p{p:03d} {g}' for b, p, g in missing))

    with open(ns.out, 'w') as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n')
    if ns.detail:
        repo = os.path.dirname(os.path.dirname(CORPUS))
        # `startswith` on a path string is the wrong containment test — it makes `<repo>-work`
        # look like a directory inside `<repo>`. Compare resolved path components instead.
        if os.path.commonpath([os.path.realpath(ns.detail), os.path.realpath(repo)]) == os.path.realpath(repo):
            raise SystemExit('REFUSED: --detail carries D4 readings and must live outside the repository')
        with open(ns.detail, 'w') as fh:
            json.dump(detail, fh, ensure_ascii=False, indent=1)

    T = summarise(rows)
    print(f"[{ns.label}] pages={len(pages)} learning={T['learning']} served={T['served']} "
          f"false_trust={T['false_trust']} teaching_critical={T['teaching_critical']} "
          f"(digits={T['digits']} as_question={T['as_question']}) "
          f"correct_questions={T['correct_questions']} role_wrong={T['role_wrong']}")
    if ns.require == 'phase-a':
        print(f"[{ns.label}] population adequacy: all {len(PHASE_A_ROWS)} Phase A rows present and matched")
    else:
        print(f"[{ns.label}] population adequacy: NOT the Phase A plane — the failing-case guarantee is "
              f"NOT in force here; {len(rows)} rows (>= {ns.min_rows} declared)")


if __name__ == '__main__':
    main()
