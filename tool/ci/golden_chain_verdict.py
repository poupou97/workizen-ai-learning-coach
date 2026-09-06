#!/usr/bin/env python3
"""WAL-218 — the CI job states its own coverage, and absence never reads as PASS.

`flutter test` prints «All tests passed!» whether or not the Golden #1 fixture is
on the machine. It is gitignored under Founder D4 (verbatim SGK text and page
crops are INTERNAL / RESEARCH ONLY), so on the runner it never is, and nine
Golden-chain assertions turn into skips. Measured on main (6fd728d) 2026-09-06:
fixture present 1108 passed / 33 skipped; fixture absent 1099 passed / 42 skipped.
Nine tests, and the suite's last line was identical in both runs.

This tool reads the ledger those nine tests write (`build/golden-chain/*.json`),
checks it against the declared obligations in `golden-chain-obligations.json`,
and prints a coverage block that a reader cannot mistake for verification.

⭐ THE GOVERNING RULE: ABSENCE CANNOT SATISFY A POSITIVE OBLIGATION.

  * a missing ledger is an ERROR, not an empty PASS (exit 2);
  * a declared obligation with no record is an ERROR — deleting a test does not
    improve coverage, it breaks the build (exit 2);
  * `--min-obligations N` refuses a shrunken registry, which is the exact shape
    of round 7's gate that printed `0/0 present · PASS` (exit 2);
  * `--require-verified` exits 1 unless every Golden obligation was exercised on
    the REAL fixture. Anything that wants to CLAIM Golden verification passes
    that flag, and without the fixture the claim goes red.

Synthetic mirrors are counted and printed on their own line, never added to the
Golden total: SYNTHETIC PASS != GOLDEN CHAIN VERIFIED. A synthetic fixture proves
the code path; only the real fixture proves the chain.

Exit codes: 0 ok · 1 a verification claim failed · 2 the ledger itself is broken.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REGISTRY = os.path.join(HERE, "golden-chain-obligations.json")


class LedgerError(Exception):
    """The ledger cannot support any statement at all — neither PASS nor FAIL."""


def _load_registry(path):
    with open(path, encoding="utf-8") as fh:
        reg = json.load(fh)
    obligations = reg.get("obligations")
    mirrors = reg.get("syntheticMirrors", [])
    if not isinstance(obligations, list):
        raise LedgerError(f"{path}: `obligations` must be a list")
    ids = [o["id"] for o in obligations]
    if len(set(ids)) != len(ids):
        raise LedgerError(f"{path}: duplicate obligation ids")
    return reg, obligations, mirrors


def _read_ledger(ledger_dir):
    if not os.path.isdir(ledger_dir):
        raise LedgerError(
            f"no ledger at {ledger_dir}. A run that produced no ledger has not "
            "verified anything — this is not an empty PASS. Run `flutter test` "
            "first (the whole suite: a partial run cannot speak for coverage)."
        )
    out = {}
    for name in sorted(os.listdir(ledger_dir)):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(ledger_dir, name), encoding="utf-8") as fh:
            rec = json.load(fh)
        rid = rec.get("id")
        if not rid:
            raise LedgerError(f"{name}: record without an id")
        out[rid] = rec
    return out


def _bar(title):
    return f"\n{title}\n" + "-" * len(title)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--registry", default=DEFAULT_REGISTRY)
    ap.add_argument("--ledger", default=None, help="default: registry.ledgerDir")
    ap.add_argument(
        "--min-obligations",
        type=int,
        default=0,
        help="refuse a registry that declares fewer than N Golden obligations. "
        "Pinned in .github/workflows/ci.yml so that dropping an obligation "
        "takes two files, not one.",
    )
    ap.add_argument(
        "--require-verified",
        action="store_true",
        help="this run CLAIMS the Golden chain is verified — exit 1 if it is not",
    )
    ap.add_argument("--out", default=None, help="write the verdict as JSON here")
    ap.add_argument(
        "--summary",
        default=os.environ.get("GITHUB_STEP_SUMMARY"),
        help="append a markdown summary here (default: $GITHUB_STEP_SUMMARY)",
    )
    a = ap.parse_args(argv)

    try:
        reg, obligations, mirrors = _load_registry(a.registry)
        ledger_dir = a.ledger or reg.get("ledgerDir", "build/golden-chain")
        ledger = _read_ledger(ledger_dir)
    except LedgerError as e:
        print(f"GOLDEN CHAIN: LEDGER ERROR — {e}", file=sys.stderr)
        return 2

    declared = len(obligations)
    problems = []

    if declared < a.min_obligations:
        problems.append(
            f"registry declares {declared} Golden obligations, floor is "
            f"{a.min_obligations}. A shrinking denominator is how `0/0 · PASS` "
            "happens; the floor exists so it cannot happen quietly."
        )

    exercised, unverified, missing = [], [], []
    for o in obligations:
        rec = ledger.get(o["id"])
        if rec is None:
            missing.append(o["id"])
        elif rec.get("exercised") is True:
            exercised.append(o["id"])
        else:
            unverified.append(o["id"])

    if missing:
        problems.append(
            "declared obligation(s) left NO record: "
            + ", ".join(missing)
            + ". Either the test was deleted, or it threw before recording, or "
            "only part of the suite ran. None of those is coverage."
        )

    mirror_ids = [m["id"] for m in mirrors]
    mirror_done = [i for i in mirror_ids if ledger.get(i, {}).get("exercised") is True]
    mirror_missing = [i for i in mirror_ids if i not in ledger]
    if mirror_missing:
        problems.append(
            "synthetic mirror(s) left no record: " + ", ".join(mirror_missing)
        )

    unknown = sorted(
        set(ledger) - {o["id"] for o in obligations} - set(mirror_ids)
    )
    if unknown:
        problems.append(
            "ledger carries ids that no registry row declares: " + ", ".join(unknown)
        )

    fixture = reg.get("fixture", "?")
    present = os.path.exists(fixture)
    verified = declared > 0 and len(exercised) == declared and not problems

    print(_bar("GOLDEN CHAIN COVERAGE (WAL-218)"))
    print(f"  real fixture            : {'PRESENT' if present else 'ABSENT'}  ({fixture})")
    print(f"  obligations declared    : {declared}")
    print(f"  exercised on REAL       : {len(exercised)}")
    print(f"  UNVERIFIED (no fixture) : {len(unverified)}")
    if missing:
        print(f"  NO RECORD (broken)      : {len(missing)}  {', '.join(missing)}")
    print(
        f"  synthetic mirrors       : {len(mirror_done)}/{len(mirror_ids)} exercised"
        "   [SYNTHETIC PASS != GOLDEN VERIFIED]"
    )
    if unverified:
        print("\n  not verified by this run:")
        for o in obligations:
            if o["id"] in unverified:
                print(f"    - {o['id']}  {o['claim']}")
    for p in problems:
        print(f"\n  !! {p}")

    if verified:
        verdict = "GOLDEN CHAIN VERIFIED"
        detail = f"all {declared} obligations exercised on the real fixture"
        rc = 0
    elif problems:
        verdict = "GOLDEN CHAIN LEDGER BROKEN"
        detail = "the ledger cannot support any statement about coverage"
        rc = 2
    else:
        verdict = "GOLDEN CHAIN UNVERIFIED"
        detail = (
            f"{len(exercised)}/{declared} exercised — this run does NOT verify the "
            "Golden chain. `flutter test` being green says nothing about it."
        )
        rc = 1 if a.require_verified else 0

    print(f"\nVERDICT: {verdict} — {detail}")
    if a.require_verified and not verified and rc == 1:
        print(
            "  this run CLAIMED Golden verification (--require-verified) and the "
            "claim is false. Absence cannot satisfy a positive obligation."
        )

    payload = {
        "verdict": verdict,
        "verified": verified,
        "declared": declared,
        "exercised": exercised,
        "unverified": unverified,
        "missing": missing,
        "syntheticMirrorsExercised": mirror_done,
        "fixture": fixture,
        "fixturePresent": present,
        "problems": problems,
        "requireVerified": a.require_verified,
    }
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
            fh.write("\n")

    if a.summary:
        try:
            with open(a.summary, "a", encoding="utf-8") as fh:
                fh.write(f"### {verdict}\n\n")
                fh.write(f"{detail}\n\n")
                fh.write("| | |\n|---|---|\n")
                fh.write(f"| real Golden fixture | {'PRESENT' if present else 'ABSENT (D4: never committed)'} |\n")
                fh.write(f"| Golden obligations exercised | {len(exercised)}/{declared} |\n")
                fh.write(f"| UNVERIFIED for want of the fixture | {len(unverified)} |\n")
                fh.write(f"| synthetic mirrors exercised | {len(mirror_done)}/{len(mirror_ids)} |\n\n")
                fh.write(
                    "> A green `flutter test` on this runner is **not** Golden-chain "
                    "verification, and a synthetic mirror is not either.\n"
                )
        except OSError:
            pass

    return rc


if __name__ == "__main__":
    sys.exit(main())
