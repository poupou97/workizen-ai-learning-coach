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

## The REPAIRED stage (Lane A1 merged, `tc2-p3`)

| what | where |
|---|---|
| batch 2 re-run on the merged build | `poc-out/round5/legacy/batch-2-repaired/` |
| batch 1 re-run on the merged build (holdout) | `poc-out/round5/legacy/batch-1-round5-repaired/` |
| re-run delta `tc2-p2` → `tc2-p3` (rescue · collateral · recovery) | `.../batch-2-repaired/delta-from-p2/delta.{json,md}` |
| re-run delta `tc2-p1` → `tc2-p3` (the whole round, batch 1) | `.../batch-1-round5-repaired/delta-from-p1/delta.{json,md}` |
| restore precision, REPAIRED stage (0/1) | `.../batch-2-repaired/restore/restore-precision.{json,md}` |
| restore precision, batch 1 (3/6, verdicts transferred) | `.../batch-1-round5-repaired/restore/restore-precision.{json,md}` |
| orphaned siblings after the merge | `.../batch-2-repaired/orphan/orphans.{json,md}`, `.../batch-1-round5-repaired/orphan/…` |
| **silent loss** (neither served nor withheld) | `.../batch-2-repaired/silent-loss.{json,md}`, `.../batch-1-round5-repaired/silent-loss.{json,md}` |
| named defects on the merged build | `poc-out/round5/legacy/regression/round5-repaired-tc2-p3.{json,md}` |
| R1 class on a second book, after the fix | `poc-out/round5/legacy/regression/batch-2-repaired-tail-scan.json` |

## Provenance of the attach artefact

| what | where |
|---|---|
| reproducibility check, 38 books / 6,176 page verdicts | `poc-out/round5/legacy/provenance/attach-repro.{json,md}` |
| freshly regenerated attach used for the experiment | `poc-out/round5/legacy/provenance/attach-fresh/attach/` |
| packs rebuilt against the fresh attach | `poc-out/round5/legacy/provenance/REBUILD-FRESH-ATTACH.json` |
| resulting pack delta (**zero**) | `poc-out/round5/legacy/provenance/PACK-DELTA-FRESH-ATTACH.{json,md}` |
| attach log from that build (the diagnosis that did move) | `poc-out/round5/legacy/provenance/attach-log-fresh/` |
| snapshot taken before the experiment | `poc-out/round5/legacy/packs-before-a1/` |
| default rebuild after the A1 merge (content identical) | `poc-out/round5/legacy/after-a1/` |

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
| restored regions (pre-merge) | 6 | what is served now, after a guard change handed it back |
| restored region (REPAIRED stage) | 1 | the `chem_guard` release, judged WRONG on two counts |

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

# provenance: does the stored attach artefact reproduce from its own code?
python3 tool/corpus/legacy/attach_repro.py check --md /tmp/attach-repro.md

# content that is neither served nor withheld
python3 tool/corpus/legacy/silent_loss.py scan --batch-dir <dir> --pipeline <id> --md /tmp/silent.md

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

`python3 -m unittest discover -s tool/tests` → **348 OK, 7 skipped** (67 in this lane:
`test_lane_d_packs`, `test_lane_d_regression`, `test_lane_d_restore`, `test_lane_d_orphan`,
`test_lane_d_silent_loss`; the rest are Lane A1's, merged).
`flutter test` → **948 pass, 15 skipped**, including the three pack-gated FILE THẬT tests and the
new INFERRED gate.
