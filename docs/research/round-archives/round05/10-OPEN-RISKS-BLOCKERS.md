# 10 · OPEN RISKS AND BLOCKERS

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

Ordered by **what they block**, not by severity in the abstract.

---

## 1. THE FIVE OPEN P0s

| # | Open P0 | Status | What it blocks | Owner of the decision |
|---|---|---|---|---|
| **1** | **R13 — silent loss.** A block the role layer drops must arrive in the TSL as a **withheld region with a truthful reason**, not vanish. | **OPEN** | **Every published rate has the wrong denominator** until this is closed. Served share, over-withhold rate, coverage — all of them. | Round-6 workstream A (engineering) |
| **2** | **Wire the repair path into the pipeline.** | **BLOCKED — Founder gate** | Nothing a lane does can change served accuracy. Today it is *a validated laboratory with a measured false-correction rate and no connection to the product.* | **FOUNDER** |
| **3** | **R15 — attach provenance does not reproduce.** **950 of 6,176** page verdicts differ from a fresh run, **896 unexplained**. | **OPEN** | Batch comparisons never touch attach provenance; **the pack build does**. Rebuilding against a fresh attach gives 207/207 and 12/12 identical — so the discrepancy is in the stored artefact, not the rebuild. | **FOUNDER** |
| **4** | **Defect 8 — mutilated structure on the lesson path.** A1 measures **7 → 0** on the gold set; Lane D measures **9 → 9** and **13 → 13** on the lesson path, with the Founder's option group **byte-identical**. | **PARTIAL** | Both lanes are right about their own population: **the class is closed where A1 looks and open where a child reads.** | engineering |
| **5** | **No bridge carrier for validated structured STEM.** `ROLE_MAP` has no `formula` *(PROVEN)*; the app's block union has no formula member and **fails closed on the whole document**. | **OPEN** | A2's 10 validated restores **cannot reach the app at all**. | engineering, gated on §1 of `09-…` |

---

## 2. RISKS THAT ARE NOT YET FAILURES

| Risk | Evidence | Why it matters |
|---|---|---|
| **The denominator itself is unsound.** `all-lessons.csv` has **3,679 rows but 3,240 distinct lesson keys** — **154 keys duplicated across 439 rows**. | E1 census *(MEASURED)* | **Every "/ 3,679" figure in every round depends on the answer.** Round 6 carries `3,679 = HISTORICAL BASELINE ONLY` until it is resolved. Reported, **not fixed** — Founder gate. |
| **Accuracy work can silently destroy semantic yield.** 4 of 28 LS&ĐL lessons **lost** a visual family and none gained — while the newer pipeline had *more* trusted blocks. | E1 *(MEASURED)* | **Nothing currently gates for it.** A round could improve every accuracy metric and delete lessons from Trực quan without any rule being at fault. E1 asks for a **semantic-yield gate**. |
| **One tone slip deletes a family.** «Tiền hành» for «Tiến hành» → **0 Steps instead of 5**. | E1 *(MEASURED)* | The distance between a working visual lesson and none is **one diacritic**. |
| **Over-withholding is now the larger error pool** — 19 of 30 withheld rows (0.633) withheld wrongly, worse than round 4's 0.400. | D + the 97-row audit *(MEASURED)* | Combined with **defect 8**, over-withholding does not merely lower coverage — **it can raise the teaching-critical error rate**, because a mutilated structure is served *wrong*, not merely *smaller*. |
| **A detector that scores perfectly by never repairing.** End-to-end: 0 repairs, 0 false corrections — **and 4 blocks moved TRUSTED → SUSPECT, 3 of them wrongly: demotion precision 0.250.** | A4 *(MEASURED)* | Standing rule adopted: **a workstream raising detection recall must report false demotion rate beside false correction rate.** |
| **`false_correction` understates harm on flattened formulas.** A flattened expression is always wrong *before*, so a bad repair scores `still_wrong` while showing a child arithmetic the book does not contain. | A2 *(MEASURED)* | For `formula_flattened` the honest figure is **`1 − correction_precision`**. Any scoreboard averaging a false-correction rate over a population containing formula rows is **true and misleading at once**. |
| **Packs and app must ship together.** A single unrecognised block kind rejects the **entire** LessonDocument. | `lesson_document.dart:1017-1018` *(PROVEN)* | Any future pipeline change that introduces a block kind **blanks the lesson on an older app**. |
| **The merge debt is compounding.** PR #73 (round 4) and PR #79 (round 5) are both open; round 6 composes on top of both. | *(PROVEN — GitHub)* | Three rounds of unmerged work now sit between `main` and the working base. Round 6 Part II makes the merge-debt recommendation a deliverable. |

---

## 3. WHAT IS **NOT** A RISK, AND SHOULD STOP BEING TREATED AS ONE

- **`trusted = 0` and `eligible for teaching = 0`** are **not** failures. They are the Founder's
  gate working. No threshold exists, so the tool returns 0 **and prints why** — `REPROCESSED ≠
  TRUSTED` is encoded in code, not asserted in prose.
- **Coverage falling because wrong content was removed** is a **correctness gain**, per the
  Founder's own rule — recorded with the count named (41 expressions, 10 exercise lists).
- **A lane falsifying its own rule** (Lane C) is the most valuable outcome available to it, not a
  shortfall.

---

## 4. THE THREE OPEN ROLE-DEFINITION QUESTIONS

A3 could not decide these, and says so rather than guessing. Each has a **measured cost of
leaving it open**:

| id | Question | Measured cost |
|---|---|---|
| **Q-ROLE-1** | Does role fidelity judge the **label** the block asserts, or the **extent** of what it covers? | **1 of 6** measured role disagreements and **1 of 13** OK controls flip with the answer. It also decides whether the round-3 `role` rate of 0.093 is right or **a large under-count**. |
| **Q-ROLE-2** | Is a bare printed mathematical expression that constitutes an exercise item a **FORMULA** or a **QUESTION**? | 19 gold blocks; 1 of 13 controls; and it decides whether the **`math_guard` exemption applies to every arithmetic exercise item in Toán**. |
| **Q-ROLE-3** | Does **INSTRUCTION** fold into ACTIVITY, or stay a first-class role? | Changes what the scoreboard's INSTRUCTION row (precision 0.300 / recall 0.500) measures. |

Note also: **applying SPEC v1 would raise the measured role-error rate**, because the spec is
stricter than the round-4 annotators were. Any before/after role rate must be **recomputed under
it**, not compared across it.

---

## 5. MEASUREMENT DEBT — things believed but not established

| Claim | Actual status |
|---|---|
| "Inter-annotator agreement on role has improved" | **NOT ESTABLISHED.** A3's result is **in-sample**; the spec was written after reading the rows. The defensible claim is *"the definitions decide 88.5 % of a known-hard sample and name the rest."* The settling measurement — a **fresh** disagreement sample, new seed, judged blind by two annotators given only the spec — **was not run**. |
| E1's `e1-definition-v1` extractor | **OVER-FIRES.** «68.8 % of lessons have a definition» is **not credible**, and E1 says so itself. Holdout precision and inter-annotator agreement are **unmeasured** — which is why the verdict is GO WITH ARCHITECTURE CHANGE and not GO. |
| The blind badge audit at 0.964 | **Reported as UNMEASURABLE, not as 0.964.** Four unbadged pages scored *unjudgeable*, and all three newly-flagged rows are among them. |
| R7c "FIXED" | **PARTIAL.** Lane D's own probe first reported FIXED and its blind audit caught the error. |
| Per-PR CI durations | **UNAVAILABLE** except Lane B's (2m16s). |
| Whether the round-5 APK is still installed on the Nokia | **UNAVAILABLE** — not checked; the device protocol forbids interrupting the Founder's use of the phone. |
| Parent-surface measurement in round 5 | **UNAVAILABLE** — no parent surface was walked or measured. |
| APK sha256 for device iterations 4 and 5 | **NOT CAPTURED** — the manifest records `gitSha` and a note, but no APK hash for those two. |

---

## 6. LARGE / EXTERNAL DATA — recorded, not copied

**This archive deliberately contains no corpus bytes.** The SGK source and every derivative of it
are copyright-restricted (`TEXTBOOK-LICENSING-QUESTIONS.md`) and gitignored. Inventory:
`manifests/large-data-inventory.txt`.

| What | Path | Size *(measured 2026-09-06)* | Version / identity | Included here? |
|---|---|---|---|---|
| SGK PDF source | `nguon-chi-thuc/` | **9.8 GB** | — | **NO** — copyright. Never commit, never archive. |
| All derived artefacts | `poc-out/` | **14 GB** | — | **NO** — derivative works of copyrighted source |
| Round-5 artefacts only | `poc-out/round5/` | **341 MB** | | **NO** — inventory only |
| ↳ Lane D legacy + snapshots | `poc-out/round5/legacy/` | 171 MB | three snapshots, each with `SHA256SUMS`, `buildProvenance`, baseline metrics, pipeline version, README | **NO** |
| ↳ pipeline / verify / lexicon / mathfix / semantic / lane-a3 / lane-c | `poc-out/round5/*` | 121 / 11 / 19 / 1.2 / 1.9 / 1.7 / 8.4 MB | | **NO** |
| Device frames | `docs/design/track-b-evidence/round5/` | ~11 MB | 36 PNG, hashes in manifest | **YES — all 36**, in `screenshots/` |
| Gold set | `tool/corpus/tc_gold/` | committed | 54 human-annotated pages across 10 subjects | **committed in the repo**, not duplicated here |

### How to reproduce the round-5 numbers

1. Check out the branch for the lane whose number you want (heads in
   `evidence/round5-branch-heads.txt`).
2. Restore the SGK source at `nguon-chi-thuc/` — **the Founder's local copy is the only one; it
   is not in git and must not be.**
3. Lane C's method is the cheapest reproduction and the most attributable: it **reuses round 4's
   raw Docling/XY-cut candidate files** and re-runs only
   `tc2_sdm → tc2_attach → tc2_tsl → tsl_to_lesson_document`, sandboxed with `TC_ROOT` and
   `--out`. **Every difference is therefore pipeline code, never OCR noise.**
4. Lane D's snapshots make the OLD baseline reproducible: `packs.py restore` re-checks every hash;
   the OLD baseline was reproduced **three times** and matched `BASELINE-METRICS.json` field for
   field.
5. Lane A3's `evidence.py` reproduces the published baseline **page by page** and **raises** if it
   drifts — use it as the canary that the corpus and pipeline are in the state the numbers assume.

**Clean-clone warning (learned in an earlier round and still binding):** tests that touch
gitignored files pass falsely on a dev machine. A `build/` cache can make a reproduction attempt
succeed for the wrong reason. Reproduce in a **clean clone** with assets deliberately synced, as
the composition check did (321 pack files, 24 fixtures synced first, precisely so a missing-asset
failure could not be mistaken for a defect).
