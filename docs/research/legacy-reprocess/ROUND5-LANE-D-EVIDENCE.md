# Round 5 · Lane D — evidence manifest

Where every number in [`ROUND5-LANE-D-REPORT.md`](ROUND5-LANE-D-REPORT.md) and
[`../DATA-ACCURACY-SCOREBOARD-LANE-D.md`](../DATA-ACCURACY-SCOREBOARD-LANE-D.md) comes from.

Everything below lives under gitignored `poc-out/` (Founder D4: pack content, TSL text and page crops
are derived from copyrighted SGK and are never committed). The repo carries counts and hashes.

---

## ⚠️ Operational state of this Mac — read before deploying anything

**The packs in the main checkout (`assets/pack/`) are still the OLD ones.** They stamp
`capped-toc-v1`, fail `pack_provenance.py verify` 12/12, and **still contain all 41 INFERRED
geometry-rebuilt expressions**. Lane D built and measured the corrected packs inside its own worktree
and deliberately did not touch the main checkout — the fix reaches the shipped surface only when this
PR is merged and the packs are rebuilt there:

```bash
for g in $(seq 1 12); do python3 tool/ui/build_lesson_index.py $g; done
python3 tool/ui/pack_provenance.py verify assets/pack/lesson-index-g*.json   # must exit 0
flutter test test/features/subjects/lesson_index_test.dart                   # the INFERRED gate
```

Until then **no APK built on this Mac should be treated as carrying the round-5 corrections.**

---

## Pack rebuild

| what | where |
|---|---|
| snapshot before the round (stale provenance) | `poc-out/round5/legacy/packs-before-round5/` |
| snapshot before the §3 fail-closed change | `poc-out/round5/legacy/packs-before-inferred-fix/` |
| — each contains | `packs/`, `SHA256SUMS`, `MANIFEST.json`, `BASELINE-METRICS.json`, `PIPELINE-VERSION.json`, `README.md` |
| rebuild runs (commands, rc, timings, verify, metrics) | `poc-out/round5/legacy/after/REBUILD-RUN.json`, `.../after-inferred-fix/REBUILD-RUN-final.json` |
| content delta, provenance rebuild (zero) | `poc-out/round5/legacy/after/PACK-DELTA.{json,md}` |
| content delta, §3 fail-closed (−41) | `poc-out/round5/legacy/after-inferred-fix/PACK-DELTA.{json,md}` |
| attachment logs, per grade, with `droppedNonVerbatim` | `poc-out/round5/legacy/attach-log/lesson-index-g<N>.attach-log.json` |
| blind delta audit — sample, sheets, answers, verdicts | `poc-out/round5/legacy/after/DELTA-AUDIT-*.{json,md}`, `.../delta-sheets/` |
| defect-6 scan of the shipped packs | `poc-out/round5/legacy/regression/pack-scan-final.json` |

Reproduce the OLD baseline:
`python3 tool/corpus/legacy/packs.py restore poc-out/round5/legacy/packs-before-round5`

## Batches

| what | where |
|---|---|
| batch 2 spec (committed) | `tool/corpus/legacy/batches/batch-2.json` |
| batch 2 run — manifest, log, shadow root, TSL, LessonDocuments | `poc-out/round5/legacy/batch-2/` |
| batch 2 OLD vs NEW mechanical compare | `poc-out/round5/legacy/batch-2/compare/compare.{json,md}` |
| batch 2 audit — samples, sheets, judgments, annotated rows, scores | `poc-out/round5/legacy/batch-2/audit/` |
| batch 1 re-run on the current build (`tc2-p2r`) | `poc-out/round5/legacy/batch-1-round5/` |
| re-run delta vs `tc2-p1` (coverage · rescue · recovery) | `poc-out/round5/legacy/batch-1-round5/delta-from-p1/delta.{json,md}` |
| transferred verdicts (identical rows only — **not** a fresh annotation) | `poc-out/round5/legacy/batch-1-round5/audit/transferred-from-p1.jsonl` |

## Restore precision

| what | where |
|---|---|
| restored rows + falsely-withheld recovery | `poc-out/round5/legacy/batch-1-round5/restore/restore-rows.json` |
| blind sheets of what is served NOW | `poc-out/round5/legacy/batch-1-round5/restore/sheets/` |
| fresh blind verdicts | `poc-out/round5/legacy/batch-1-round5/restore/restore-answers.json` |
| RESTORE PRECISION | `poc-out/round5/legacy/batch-1-round5/restore/restore-precision.{json,md}` |

## Regression corpus and orphaned siblings

| what | where |
|---|---|
| three defects on the round-4 build (baseline) | `poc-out/round5/legacy/regression/round4-tc2-p2.json` |
| three defects on the current build | `poc-out/round5/legacy/regression/round5-tc2-p2r.{json,md}` |
| R1 class scan (book tails) | `poc-out/round5/legacy/regression/batch-2-tail-scan.json` |
| orphaned siblings — evaluation set | `poc-out/round5/legacy/batch-2/orphan/orphans.{json,md}` |
| orphaned siblings — independent holdout | `poc-out/round5/legacy/batch-1-round5/orphan/orphans.{json,md}` |

## Annotators

Four independent sessions, each judging **only from page renders**, each explicitly forbidden the
sample files, the compare output, the packs and the units:

| sample | rows | what it judged |
|---|---|---|
| pack delta (badge reading) | 31 | the printed lesson badge, without seeing the claimed lesson |
| batch 2 OLD | 43 | what the old product served |
| batch 2 NEW | 97 (67 trusted + 30 withheld) | what the new pipeline serves, and whether each refusal was safe |
| batch 2 caption quota | 20 | the caption class, incl. the new `figure_relation` field |
| restored regions | 6 | what is served now, after a guard change handed it back |

## Commands

```bash
# pack rebuild, with the guard rails
python3 tool/corpus/legacy/packs.py snapshot poc-out/round5/legacy/<new-dir>
python3 tool/corpus/legacy/packs.py rebuild  poc-out/round5/legacy/<new-dir>
python3 tool/corpus/legacy/packs.py delta    poc-out/round5/legacy/<new-dir> --md /tmp/delta.md
python3 tool/corpus/legacy/packs.py restore  poc-out/round5/legacy/<new-dir>

# a batch, end to end
LEGACY_OUT=$PWD/poc-out/round5/legacy python3 tool/corpus/legacy/run_batch.py \
    --batch tool/corpus/legacy/batches/batch-2.json
LEGACY_OUT=$PWD/poc-out/round5/legacy python3 tool/corpus/legacy/compare.py \
    --batch-dir $PWD/poc-out/round5/legacy/batch-2

# the named defects, on any build
python3 tool/corpus/legacy/regression.py check --batch-dir <dir> --pipeline <id>
python3 tool/corpus/legacy/regression.py tail-scan --batch-dir <dir> --pipeline <id>
python3 tool/corpus/legacy/regression.py pack-scan
python3 tool/corpus/legacy/orphan.py scan --batch-dir <dir> --pipeline <id>

# the scoreboard over both rounds
python3 tool/corpus/legacy/scoreboard.py \
    --registry $PWD/poc-out/round4/legacy/registry.json \
    --legacy-out "$PWD/poc-out/round4/legacy,$PWD/poc-out/round5/legacy"
```

## Tests

`python3 -m unittest discover -s tool/tests` → **289 OK** (60 new in this lane:
`test_lane_d_packs`, `test_lane_d_regression`, `test_lane_d_restore`, `test_lane_d_orphan`).
`flutter test` → **948 pass, 15 skipped**, including the three pack-gated FILE THẬT tests and the
new INFERRED gate.
