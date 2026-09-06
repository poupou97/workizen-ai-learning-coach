# 05 · METRICS — BEFORE → AFTER

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

**Reading rules, binding on this file.**

1. **Denominators are never pooled.** Every number names its population.
2. **Nothing is averaged.** The Reality Scoreboard in particular is reported dimension by dimension.
3. **Three served shares exist and answer three different questions.** Conflating them is the
   mistake round 5 made in two opposite directions at once.
4. **Withheld counts before and after the accounting fix are not comparable without saying so** —
   the base grew because always-refused regions became visible.
5. Machine-readable companion: `metrics/round6-gate-results.json`, `metrics/golden-slices.json`.

---

## 1. GATE A — CONSERVATION · the round's headline number

**Population:** every SDM block on each lesson's own boundary pages. *(MEASURED, WS-A, PR #91.)*

| population | lessons | input regions | SERVED | WITHHELD | EXCLUDED | **UNACCOUNTED** |
|---|---:|---:|---:|---:|---:|---:|
| batch 2 (evaluation set), all lessons — before | 11 | 787 | 285 | 160 | 309 | **33** |
| batch 2 — after | 11 | 787 | **285** | 169 | 333 | **0** |
| batch 1 (**holdout**), all lessons — before | 14 | 814 | 234 | 144 | 374 | **62** |
| batch 1 — after | 14 | 814 | **234** | 170 | 410 | **0** |
| golden run, all lessons — before | 4 | 277 | 43 | 35 | 156 | **43** |
| golden run — after | 4 | 277 | **43** | 43 | 191 | **0** |
| **TOTAL** | **29** | **1,878** | — | — | — | **138 → 0** |

**And the served set is byte-identical before and after in every population** — 285 / 234 / 43.
**Zero blocks moved from served to withheld; zero moved the other way.** No threshold was touched.
*This was the claim most likely to fail.*

### Where the 82 lost regions went

**50 → `EXCLUDED_WITH_REASON` · 32 → `WITHHELD` with a truthful reason.**
**61 % of the "silent loss" was never learning content** — turning all of it into withheld regions
would have traded a silent loss for a mass over-withhold, on a metric round 5 already measured
getting worse (0.400 → 0.633).

### The two Golden slices, controlled before → after

**GOLDEN #1 · LS&ĐL 5 Bài 8** *(the delivery slice)*

| | input | SERVED | WITHHELD | EXCLUDED | **UNACCOUNTED** |
|---|---:|---:|---:|---:|---:|
| before (pre-fix, `1a75d24`) | 84 | 36 | 15 | 27 | **6** |
| after (WS-A fix) | 84 | **36** | 15 | 33 | **0** |
| **composed** (× WS-C demotion) | 84 | **34** | **17** | 33 | **0** |

**Zero new withholds from the accounting fix on the delivery slice.** All six lost regions were
figure text inside a map/table picture region — *the History/Geography loss profile is not the Toán
one, and the Toán root cause did not have to generalise for this slice to close.*

**GOLDEN #2 · Toán 4 tập hai Bài 61** *(round 5's worst case)*

| | input | SERVED | WITHHELD | EXCLUDED | **UNACCOUNTED** |
|---|---:|---:|---:|---:|---:|
| before | 148 | 4 | 15 | 97 | **32** |
| after | 148 | **4** | 22 | 122 | **0** |

25 were figure text; 7 are Docling FORMULA regions now withheld as
`unread:unreadable_region` / `formula_unvalidated` — **including the block round 5 named,
`7 8 2 8 7 - 2 8 5 8`.** `ledger.py audit` exits **1** before and **0** after.

### The demotion is a SECOND, separate movement — never folded in

| movement | what it did | effect on Golden #1 |
|---|---|---|
| **WS-A rule-order fix** | reclassified regions that were **never accounted for** | served **unchanged** 36 → 36; UNACCOUNTED 6 → 0 |
| **WS-C ledger-honouring demotion** | withdrew regions that **were** served | served **36 → 34**; withheld 15 → 17 |

**Conservation across the demotion, verified rather than assumed:** WS-C 34+17 = **51 learning
regions**; WS-A 36+15 = **51**; the two `(page, native index)` sets are **identical**; exactly **2**
regions moved SERVED → WITHHELD and **0** moved the other way; composed ledger `conserves: true`,
`unaccounted: 0`, `demotedDownstream: 2`.

---

## 2. THE THREE SERVED SHARES — and why the third is the honest one

*(Golden slices; MEASURED.)*

| rate | before | after (WS-A fix) | composed (× WS-C demotion) | the question it answers |
|---|---:|---:|---:|---|
| `servedShareAsReported` | 0.5714 | 0.5195 | 0.4935 | of the regions the pipeline **classified**, what share did it serve? |
| `servedShareOfLearningRegions` | 0.3704 | 0.5195 | 0.4935 | of the regions that **are learning content**, what share reached a child? |
| `servedShareOfAllInputRegions` | 0.1724 | **0.1724** | 0.1638 | of **everything extracted from the page**, what share reached a child? |

The third is **unchanged by the accounting fix, as it must be** — a reclassification touches neither
the numerator nor the whole population. **It moves only in the composed column, because a demotion
really does remove text from a child.** The first two converge once nothing is unaccounted — *which
is what conservation means.*

## 3. HISTORICAL CORRECTION TO ROUND 5 — round 5 was wrong in two directions

| | R5 reported | R5 corrected | **R6 accounted** |
|---|---:|---:|---:|
| batch 2 (evaluation set) | 0.632 | 0.589 | **0.617** |
| batch 1 (**holdout**) | 0.613 | 0.523 | **0.571** |
| Toán 4 tập hai Bài 61 | 0.211 | 0.078 | **0.154** |
| Toán 4 tập một Bài 37 | 0.489 | 0.371 | **0.434** |
| Toán 5 tập một Bài 6 | 0.480 | 0.353 | **0.364** |
| LS&ĐL 4 Bài 12 | 0.522 | 0.444 | **0.522** |
| LS&ĐL 5 Bài 8 (Golden #1) | 0.706 | 0.632 | **0.706** |

Golden #1's composed share **after WS-C's two demotions is 0.667 (34/51)** — a *separate* movement,
reported apart. **Round 5's published figures are unchanged and remain reproducible**;
`silent_loss.py` re-run unchanged reproduces its output byte for byte.

---

## 4. GATE B — RECOGNITION · six metrics, five populations, never summed

*(MEASURED, WS-B, PR #92. **DEV** = round 5's 16 tuned pages · **SDM** = all 113 Toán pages with an
SDM and a PDF (where round 5's «274 of 336» lives) · **HOLDOUT-1** = 24 random Toán pages, grades
2–12, seed 20260906 · **HOLDOUT-2** = 12 pages with ≥6 detected bar regions in untuned books ·
**HOLDOUT-3** = 14 pages whose own text contains «phân số», in untuned books. **All three holdout
rules were fixed before the draw.**)*

| | DEV | **SDM** | HOLDOUT-1 | HOLDOUT-2 | **HOLDOUT-3** | Bài 61 |
|---|---|---|---|---|---|---|
| pages | 16 | 113 | 24 | 12 | 14 | 3 |
| fraction regions | 204 | 784 | 68 | 127 | 212 | 85 |
| recovery population | 128 | 548 | 66 | 105 | 177 | 47 |
| **① DIGIT RECALL** | 0.500 | **0.403** | 0.061 | 0.038 | **0.181** | 0.532 |
| **③ STRUCTURAL EXACT MATCH** | 0.344 | 0.259 | 0.000 | 0.010 | 0.130 | 0.362 |
| **⑥ RECOVERABLE FRACTION RATE** | 44/128 | 142/548 | 0/66 | 1/105 | 23/177 | **17/47** |
| control regions | 76 | 236 | 2 | 22 | 35 | 38 |
| control disagreements | 1 | 1 | 0 | 0 | 2 | **0** |

**② SYMBOL RECALL — three classes, three different answers**

| class | population | read | correct | accepted after guards |
|---|---:|---:|---:|---|
| destroyed exponent `10⁸ → 10°` | 171 | 21 | 17 | **16, all correct** |
| Roman numeral `II → I1` | 106 | 8 | 7 | **3** (sequence validator), all correct |
| **ohm `Ω → S2`** | 22 | **0** | — | **0 — the lever does not work here** |

**⑤ FALSE RECOGNITION RATE — beside every recall figure, as the round required**

| set | readings | wrong | rate |
|---|---:|---:|---:|
| DEV p22 + Bài 61 p81–83 | 28 | **0** | **0.000** |
| **HOLDOUT-3** | 41 | **2** | **0.049** |
| SDM control | 236 | 1 disagreement | 0.004 *(hand-check: the **baseline** is wrong)* |
| destroyed exponent, raw | 21 | 4 | 0.190 |
| destroyed exponent, **guarded** | 16 | **0** | **0.000** |
| Roman, ungated | 8 | 1 | 0.125 |

**④ EXPRESSION EXACT MATCH (block level, 387 fraction-bearing SDM blocks): before 10 · after 10 ·
Δ = 0.** The round's honest negative.

**The 274/336, before → after:** blocks blocked by «the OCR did not read the digit» **281 → 234
(−16.7 %)**; blocks reaching RESTORE **10 → 10**. Response rates by class: DIGIT LOSS **76/312 =
0.244** · SEGMENTATION **46/196 = 0.235** · FRACTION STRUCTURE **20/40 = 0.500**.

**The ceiling, and where it could move:** of 548 unreadable regions the re-crop reads **142** and
refuses **406** — `UNREAD` 186 · **`INSUFFICIENT_AGREEMENT` 97 (the largest addressable group)** ·
`REGION_UNCONFIRMED` 79 · `CONFLICT` 42 · `AMBIGUOUS` 2.

**The scale-ladder trade, measured:** 8 scales give **+41 %** recoveries on DEV and **27/27 correct**
on Bài 61 at no control cost — but **HOLDOUT-3's false recognition rises 0.049 → 0.083** for **+17 %**
recall. **Four scales stays.** Cost of eight: 24 crops/region, ~0.9 s.

### The LINE census — candidate counts, with precision only where measured

*(2,398,513 OCR lines · 531 books · 62,729 pages.)*

| Class | Findings | Books | Precision |
|---|---:|---:|---|
| SUBSCRIPT | 6,168 | 388 | **5/16** hand-checked |
| SYMBOL CONFUSION (Ω) | **22** | 11 | not formally sampled; all 12 inspected are real |
| SUPERSCRIPT | 171 | 47 | ≥2 false positives among 21 inspected |
| ROMAN NUMERAL | 106 | 59 | ≥1 false positive among 8 inspected |
| SEGMENTATION | 24 | 10 | all 24 inspected are the same real shape |
| DIACRITIC (unigram) | 26,703 forms | 529 | **FALSIFIED — a denominator, not a count** |
| DIACRITIC (bigram) | 2,778 forms | 450 | a **candidate list**, OBSERVED, unchecked against the page |
| OPERATOR LOSS · MATH REGION · FORMULA · TABLE/STRUCTURE · OTHER | **NOT MEASURED** | — | listed rather than estimated |

Sub-form named: **`V` + digit — 687 candidates**, an unknown share being `√n` misread. *Shape cannot
separate them; the raster can.*

### REGION census — where round 5's «274» splits

| class | regions | share of the 548 unreadable |
|---|---:|---:|
| **DIGIT LOSS** | **312** | 0.569 |
| **SEGMENTATION** | **196** | 0.358 |
| FRACTION STRUCTURE | 40 | 0.073 |

---

## 5. GATE C — REPAIR · counted, and capped

*(MEASURED by WS-C; **the artefact figures re-verified first-hand by the archive builder**.)*

| | source TSL | projected TSL |
|---|---:|---:|
| served blocks | 36 | **34** |
| withheld regions | 15 | **17** |
| validated repairs recorded | — | **9** |
| …carried on a withheld region | — | **6** |
| …**trusted** | — | **0** |
| violations (a repair being served) | — | **0** |
| demotions (detected, unrepaired, still served) | — | **2** |
| served text changed | — | **none** (asserted) |

**Independently confirmed in the shipped fixture** *(PROVEN)*: 52 blocks · 17 withheld · 35
non-withheld (34 content + 1 `sourceRef`) · `semantic` **0** · `tutorSteps` **0** · **6 blocks carry
a repair, 6/6 `VALIDATED_REPAIR`, 6/6 `servable:false`, 6/6 on type `withheld`, 0 with a `text`
field, 0 with any forbidden value key.**

**False-demotion exposure, published beside the restores:** Golden #1 **2 blocks**. Round-5 prior for
the comparable act: **demotion precision 0.250** on 4 blocks.

---

## 6. GATE E — DEVICE · Workspace Option B, measured

*(MEASURED on the widget tree at the Nokia viewport 392.7 × 698.2 dp, runnable in CI; device
confirmation OBSERVED across 7 frames.)*

| pinned chrome | Đọc | Trực quan | Học với SAM |
|---|---|---|---|
| round 4/5 (`card`) | 225 dp | 225 dp | **411 dp = 58.9 %** |
| **round 6 (Option B)** | **281 dp** | **281 dp** | **281 dp** |
| B after «Để sau» | **225 dp** | 225 dp | 225 dp |
| view labels visible | 4 | 4 | 3 |

First lesson content on **Trực quan**: `card` **384.0 dp** → **B peeking 289.0 dp** → **B collapsed
233.0 dp**. Measured on the device: collapsing lifts content by **~146 px**.

**The number that matters is the equal one.** Round 5's 411-vs-225 gap existed only because of a
card; all three views now pay the same price, **pinned by a test**.

*Round 5's device pixel figures (820 / 634 / 712 / 565 px) are deliberately **not** reproducible on
this branch — they live in `TRACK-B-ROUND5-WORKSPACE-DUPLICATION.md` §5 and reproduce on
`lane-b/round5-experience` (PR #87).*

---

## 7. THE REALITY SCOREBOARD — never averaged

| Dimension | Round 5 | Round 6 |
|---|---|---|
| **SOURCE REALITY** | 97 | **97** |
| **SOURCE TRUST** | 0 / 97 | **0 / 97** — no trust threshold set (**Founder gate**) |
| **RECOGNITION REALITY** | not measured | **17/47 recovered on Bài 61, 17/17 correct; holdout digit recall 0.181; false recognition 0.049** |
| **REPAIR REALITY** | laboratory only, 0 connected | **9 validated · 6 crossed · 0 trusted · 0 violations** |
| **PEDAGOGY REALITY** | 7 / 17 | **7 / 17** |
| **EVIDENCE REALITY** | 0 of 0 | **0 of 0** |
| **PRODUCT DELIVERY REALITY** | 0 real lessons | **1 real lesson on a real device — minus its timeline** |

---

## 8. CANONICAL LESSON IDENTITY

| figure | value |
|---|---:|
| SOURCE ROWS | **3,679** |
| DISTINCT CURRENT KEYS `(sourceDocumentId, lessonNo)` | **3,240** |
| duplicated keys · excess rows | 154 · 439 |
| **TRUE DUPLICATES** | **29** |
| **KEY COLLISIONS** | **410** |
| SOURCE VARIANTS | **0** |
| **CANONICAL LESSON COUNT** | **3,650** (3,359 anchored · 291 unanchored) |

| duplicate class | keys | rows removed | evidence |
|---|---:|---:|---|
| `key_collision` | 132 | 0 | every row has its own `pageStart`: numbering **restarts** per chủ đề |
| `mixed` | 19 | 26 | a repeat and a collision in the same group |
| `true_duplicate` | 2 | 2 | identical number, `pageStart` and title |
| `unverifiable` | 1 | 1 | no `pageStart` and no title on any row |

**3,240 deletes 410 real lessons. 3,679 is wrong by 29. 63 of 301 books contribute zero rows
(`NO_TOC`) — so 3,679 was never «all SGK lessons». And 3,381 ranged = exactly the 3,679 rows that
carry a `pageStart` (3,679 − 298).**

**`3,650` is a MEASUREMENT, not an approved denominator. `3,679` remains HISTORICAL BASELINE ONLY.**

---

## 9. LEARNING-VIEW CENSUS — the product's own bridge over 238 canonical TSLs

| | lessons | share |
|---|---:|---:|
| **Trực quan has something to show** | **73** | **0.307** |
| **SAM has a script** | **1** | **0.004** |

| kind | instances | renderer |
|---|---:|---|
| `process` | **181** (96.8 %) | `ProcessFlowView` |
| `comparison` | 6 | `MindmapView` |
| `conceptMap` | **0** | `MindmapView` |
| `timeline` | **0** | `TimelineView` |

Withheld blocks, 2,170 of 14,241 learning blocks (0.152): `agree_text` **824 (0.380)** ·
`figure_dependent` **632 (0.291)** · **`unknown_role:*` 118** (`footnote` 64 · `activity` 50 ·
`option` 4).

---

## 10. TEST AND CI COUNTS

| Scope | Result |
|---|---|
| **Composed round** (5 branches, throw-away worktree, **real assets synced**) | **0 conflicts** · `flutter analyze` clean · **Python 748 OK** (23 skipped) · **Dart 1084 — all passed** |
| WS-B branch | `flutter analyze` clean · Dart **1019 passed / 45 skipped** · Python **672 OK / 15 skipped** (**50 new**) |
| WS-C branch | Python **672 passed / 14 skipped** (**30 new**) · analyze clean · Dart **1073 passed / 2 skipped / 1 failed** — the failure is `lesson_index_test.dart`, comparing two files **not in git**, reproducing identically in a clean worktree; **reported as pre-existing, left alone** |
| WS-D | 16 lineage tests + the corrected workspace/no-machine-ids suites |
| All five PRs | `Analyze & Test = SUCCESS` *(PROVEN)* |

---

## 11. PACKS — what shipped in the GATE E build

*(**PROVEN** — recomputed by the archive builder from the two pack sets archived in
`evidence/round6-artefacts/`; all 12 rebuilt files hash-match the device MANIFEST.)*

| | `packs-STALE-before` | `packs` (GATE E) |
|---|---:|---:|
| `packVersion` (g4) | `g4-20260905T0437Z-07a24504` | `g4-20260906T0424Z-eac69ea1` |
| **`attachmentRule`** | **`capped-toc-v1`** | **`capped-toc-v2`** |
| **`toanExercises`** | **41** (g4 **26** · g5 **15**) | **0** |
| tvReadings / tvWritings / khoaExperiments / sourceAssets / suSources / diaMaps | 66 / 54 / 46 / 36 / 4 / 1 | **unchanged, to the item** |
| **total activities** | **248** | **207** |
| files differing by sha256 | — | **12 of 12** |

**It reconciles exactly: 248 − 41 = 207.** *(PROVEN — recomputed from the archived bytes.)*

**`pack_provenance verify`: 0/12 FAIL → 12/12 PASS** *(MEASURED by WS-D)*.

**A correction of the archive builder's own, recorded rather than quietly fixed.** A first draft of
this file reported **217 → 207** and **`toanExercises` 10 → 0**. That was a counting error, not a
discrepancy: `toanExercises` is a **dict keyed by lesson number whose values are lists**, and
`len()` on it returns **keys**, so 10 *lessons* were reported as 10 *expressions*. The correct
count is **41**, and it corroborates round 5's Lane D from the other side — Lane D recorded «g4 26
expressions across **6 lessons**, g5 15 across **4 lessons**», and the archived backup holds exactly
**6 and 4** lesson keys. **WS-D's figures were right throughout.** Command and full working in
`evidence/structural-spot-checks.md` §8.

**One figure remains unsettled and is flagged rather than asserted:** *total activities* is a
derived metric with more than one plausible definition — summing leaf items gives **248 → 207**,
summing container keys gives 217 → 207, and a third naive sum has been reported elsewhere as 161.
**The `toanExercises` count does not depend on that choice**; the activities total does, and no
single definition is written down anywhere in the repository. See `10-OPEN-RISKS-BLOCKERS.md` §5.
