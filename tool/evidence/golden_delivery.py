#!/usr/bin/env python3
"""ROUND 6 · WS-D — GOLDEN DELIVERY: assemble a learner-facing fixture, and GATE it.

    SOURCE → RECOGNITION → ACCOUNTED STRUCTURE → VALIDATED REPAIR → TRUST/DISPOSITION
      → TSL → LESSON DOCUMENT → LEARNING VIEW → REAL DEVICE

This driver owns the two links in the middle that Track B is responsible for — TSL →
LessonDocument → `assets/fixtures/real/` — and it REFUSES to place a document that
cannot prove its own lineage. It never edits a TSL, never repairs anything, never
invents a field: the repair happens upstream in `tool/corpus/repair/`, and if no
repair reached the TSL then this tool says so and (under `--require-repair`) declines.

    python3 tool/evidence/golden_delivery.py \\
        --tsl <path to the TSL to ship from> \\
        [--history-rules] [--verbatim-ledger docs/research/lane-c/data/…json] \\
        [--require-repair] [--place] [--stage <dir>] [--json <out>]

Without `--place` it stages into a scratch directory and reports — that is the default,
because putting a file into `assets/fixtures/real/` changes what a child sees.

WHY A DRIVER AND NOT THREE COMMANDS. Round 5 shipped a stale gitignored fixture that
read as a passing test. The failure was not that anyone ran the wrong command; it was
that «the file exists» and «the file is the current generation» were indistinguishable
from outside. Here they are one step: a fixture that reaches `assets/fixtures/real/`
has passed `fixture_lineage`, and the run prints the hash chain that says which
generation it is.

  TSL sha256  →  document sha256  →  fixture on disk
  and every version field the Founder requires, recorded INSIDE the document.

`assets/fixtures/real/` is gitignored (Founder D4: verbatim SGK text and page crops are
INTERNAL / RESEARCH ONLY, never distributed, never committed), so this run is also the
only durable record of what was placed. Keep its `--json` next to the device evidence.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import fixture_lineage as fl  # noqa: E402

BRIDGE = os.path.join(ROOT, 'tool', 'fixtures', 'make_lesson_fixture.py')
HISTORY_RULES = os.path.join(ROOT, 'tool', 'research', 'lane_c', 'history_rules.py')
REAL_DIR = os.path.join(ROOT, 'assets', 'fixtures', 'real')


def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(f'FAILED: {" ".join(cmd)}\n{p.stdout}\n{p.stderr}')
    return p.stdout.strip()


def only_document(d):
    got = [f for f in sorted(os.listdir(d))
           if f.startswith('lesson-') and f.endswith('.json')]
    if len(got) != 1:
        raise SystemExit(f'expected exactly one lesson document in {d}, found {got}')
    return os.path.join(d, got[0])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--tsl', required=True)
    ap.add_argument('--stage', default=os.path.join(ROOT, 'poc-out', 'round6', 'golden'))
    ap.add_argument('--history-rules', action='store_true',
                    help='apply the PROPOSED History rules post-pass (LS&ĐL only)')
    ap.add_argument('--verbatim-ledger',
                    help='history-rules@v2 verbatim gate; without it the rules run v1')
    ap.add_argument('--toc-title')
    ap.add_argument('--no-crops', action='store_true')
    ap.add_argument('--require-repair', action='store_true',
                    help='the delivery claim: refuse a document with no repair lineage')
    ap.add_argument('--place', action='store_true',
                    help='copy the gated document + crops into assets/fixtures/real/')
    ap.add_argument('--json', dest='json_out')
    a = ap.parse_args(argv)

    tsl = a.tsl if os.path.isabs(a.tsl) else os.path.join(ROOT, a.tsl)
    if not os.path.exists(tsl):
        raise SystemExit(f'no TSL at {a.tsl}')
    tsl_hash = fl.sha256_file(tsl)

    stage = os.path.abspath(a.stage)
    bridged = os.path.join(stage, 'bridged')
    shutil.rmtree(bridged, ignore_errors=True)
    os.makedirs(bridged, exist_ok=True)

    steps = [dict(step='TSL', path=os.path.relpath(tsl, ROOT), sha256=tsl_hash)]

    cmd = [sys.executable, BRIDGE, '--tsl', tsl, '--out', bridged]
    if a.no_crops:
        cmd.append('--no-crops')
    run(cmd)
    doc_path = only_document(bridged)
    steps.append(dict(step='LESSON DOCUMENT (bridge)',
                      path=os.path.relpath(doc_path, ROOT),
                      sha256=fl.sha256_file(doc_path),
                      generator='tool/corpus/tsl_to_lesson_document.py'))

    if a.history_rules:
        ruled = os.path.join(stage, 'history-rules')
        shutil.rmtree(ruled, ignore_errors=True)
        os.makedirs(ruled, exist_ok=True)
        cmd = [sys.executable, HISTORY_RULES, '--doc', doc_path, '--out', ruled, '--report']
        if a.verbatim_ledger:
            cmd += ['--verbatim-ledger', a.verbatim_ledger]
        if a.toc_title:
            cmd += ['--toc-title', a.toc_title]
        out = run(cmd)
        # the rules write beside the document but do not copy crops — carry them.
        crops = os.path.join(bridged, 'crops')
        if os.path.isdir(crops):
            shutil.copytree(crops, os.path.join(ruled, 'crops'), dirs_exist_ok=True)
        doc_path = only_document(ruled)
        steps.append(dict(step='HISTORY RULES (PROPOSED post-pass)',
                          path=os.path.relpath(doc_path, ROOT),
                          sha256=fl.sha256_file(doc_path),
                          generator='tool/research/lane_c/history_rules.py',
                          note=out.splitlines()[-1] if out else ''))

    lineage = fl.check(doc_path, root=ROOT, require_repair=a.require_repair,
                       expect_source_hash=tsl_hash)
    print(fl.render(lineage))
    print()
    for s in steps:
        print(f"  {s['step']:<34} {s['sha256'][:16]}…  {s['path']}")
        if s.get('note'):
            print(f"  {'':<34} {s['note']}")

    placed = None
    if a.place:
        if lineage['verdict'] == fl.FAIL:
            print('\n  REFUSED TO PLACE — the lineage gate failed. Nothing was copied.')
            return 1
        os.makedirs(os.path.join(REAL_DIR, 'crops'), exist_ok=True)
        placed = os.path.join(REAL_DIR, os.path.basename(doc_path))
        shutil.copy2(doc_path, placed)
        src_crops = os.path.join(os.path.dirname(doc_path), 'crops')
        n = 0
        if os.path.isdir(src_crops):
            for f in sorted(os.listdir(src_crops)):
                shutil.copy2(os.path.join(src_crops, f), os.path.join(REAL_DIR, 'crops', f))
                n += 1
        print(f"\n  PLACED {os.path.relpath(placed, ROOT)} (+{n} crops)")
        print('  assets/fixtures/real/ is gitignored — this file does NOT reach CI or a '
              'clean clone, and its crops are INTERNAL / RESEARCH ONLY (Founder D4).')
    else:
        print('\n  STAGED ONLY — pass --place to make this what a child sees.')

    result = dict(tslSha256=tsl_hash, chain=steps, lineage=lineage,
                  placed=os.path.relpath(placed, ROOT) if placed else None)
    if a.json_out:
        os.makedirs(os.path.dirname(os.path.abspath(a.json_out)), exist_ok=True)
        with open(a.json_out, 'w', encoding='utf-8') as fh:
            json.dump(result, fh, ensure_ascii=False, indent=2, sort_keys=True)
            fh.write('\n')
    return 1 if lineage['verdict'] == fl.FAIL else 0


if __name__ == '__main__':
    sys.exit(main())
