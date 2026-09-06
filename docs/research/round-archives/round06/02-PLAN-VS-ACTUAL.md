# 02 · PLAN vs ACTUAL

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

Plan of record: `docs/research/ROUND6-PLAN.md` (`1a75d24`) + the Founder addendum (`51711c0`).
Allowed statuses: **DONE · PARTIAL · FAILED · FALSIFIED · BLOCKED · DEFERRED · NOT STARTED**.
**Nothing was promoted from PARTIAL to DONE.**

---

## 1. Workstreams: four planned, four ran

Round 5 grew from six lanes to nine mid-round. **Round 6 did not grow.** Four workstreams were
planned and four ran, each with one PR.

| WS | PR | Head *(verified)* | CI | Status |
|---|---|---|---|---|
| **A · TRUTH ACCOUNTING** | **#91** | `02e28dc` | PASS | **DONE** |
| **B · RECOGNITION** | **#92** | `371b6b0` | PASS | **DONE** |
| **C · REPAIR → PRODUCT** | **#90** (stacked on WS-A) | `4193c50` | PASS | **DONE with one PARTIAL** |
| **D · GOLDEN DELIVERY** | **#93** | `eeb38c1` | PASS | **DONE with one DEFERRED and one NOT STARTED** |
| *(archive)* | **#89** | `73a5321` | PASS | round-5 retrospective tooling |

*(**PROVEN** — heads re-resolved from `origin`, 5 of 5 match §10.1 of the consolidated report; CI and
`mergedAt: null` re-read from the GitHub API.)*

---

## 2. WS-A · TRUTH ACCOUNTING — PR #91

| Planned | Status | Actual |
|---|---|---|
| Reproduce round-5 numbers (0.632→0.589, 0.613→0.523, Bài 61 0.211→0.078) | **DONE** | Exact, **from a second independent construction** — the ledger partitions the whole input population where round 5's `silent_loss.py` scanned for role `empty`; the two agree to four decimal places. `silent_loss.py` re-run unchanged reproduces its published output **byte for byte**. |
| R13 conservation invariant as a HARD FAILURE | **DONE** | `ledger.py audit` **exits non-zero**; `--historical` reports without failing, so a round-5 artefact can be measured without pretending its numbers changed. |
| What disappeared and why, per class with counts | **DONE** | All **82** regions, **six** classes, decided by the block's own text and the OCR lines under its bbox — no thresholds. |
| Repair root causes without mass over-withhold | **DONE** | **50 became `EXCLUDED_WITH_REASON` · 32 became `WITHHELD` with a truthful reason.** 61 % was never learning content; converting all of it to withheld would have been the easy wrong answer. |
| Recalculate round-5 metrics, history preserved | **DONE** | Published under **`HISTORICAL CORRECTION TO ROUND 5`**, beside round 5's figures, never in place of them. |
| A2 canonical lesson identity | **DONE** | Six figures + a four-class duplicate taxonomy + two rejected key candidates. |

**Unplanned and delivered:** a **determinism control** run *before* the fix (re-running SDM+TSL with
unchanged code produces a byte-identical ledger), so every before→after difference is attributable
to the fix and nothing else. And a **free widening of the sample**: 29 lesson ledgers / 1,878 input
regions, including **five lessons nobody selected**.

---

## 3. WS-B · RECOGNITION — PR #92

| # | Planned | Status | Actual |
|---|---|---|---|
| 1 | Failure census by class | **DONE** | 5 line classes over **2,398,513** lines / 531 books / 62,729 pages; 3 region classes over 784 regions; **4 classes named NOT MEASURED** rather than estimated |
| 2 | Corpus/template-assisted recognition | **DEFERRED** | not needed to meet Gate B; recommended for the Ω class |
| 3 | Targeted high-resolution re-crop | **DONE** | built, measured on **five** populations, hand-checked |
| 4 | Alternative OCR observation | **DONE** | same engine, different parameters (crop · scale · language correction off) |
| 5 | Multi-engine disagreement | **NOT STARTED** | round 5 already measured that both stacks agree on the wrong character |
| 6 | Specialised Math/STEM recognition | **DONE** (verdict: **not recommended**) | CodeFormulaV2 run head-to-head |
| 7 | Geometry-aware recognition | **PARTIAL** | only the raster superscript-sign guard was built |
| 8 | Docling formula enrichment, licensing-safe | **DONE** | licence **CDLA-Permissive-2.0** confirmed; run; cost and accuracy measured |
| 9 | Evaluate the 274/336 population | **PARTIAL** | 281 → 234 blocks at recognition level; **0 change in restores** |
| 10 | Six metrics, separately | **DONE** | five populations, never summed |
| 11 | CI green without corpus | **DONE** | 50 new tests, none touching corpus/PyMuPDF/numpy/Vision/network |
| 12 | Block-level repair from recovered digits | **FALSIFIED** | measured, does not work; diagnosis and hand-off to WS-C |

**The plan asked for a census before rules, and the census earned its keep immediately:** it caught
**two of WS-B's own five line-level rules** as mostly false positives, and surfaced a failure form
nobody had named (a radical `√` read as the letter `V`, **687** candidates).

---

## 4. WS-C · REPAIR → PRODUCT — PR #90

| Planned | Status | Actual |
|---|---|---|
| `ValidatedRepair` type bridging round-5 model + E1 grounding | **DONE** | E1's `SourceGrounding` is **imported**, with a test asserting `isinstance` and byte-equal `to_json()` — reuse checked, not claimed |
| TSL join making a validated repair visible | **DONE** | joined on `block_key`, the pipeline-agnostic normalisation the bridge already used |
| Bridge carries it, cannot serve it | **DONE** | `repair_of()` **refuses rather than sanitises** |
| App parses it, cannot serve it | **DONE** | `repair` is a field only on `WithheldBlock` *(PROVEN)* |
| GOLDEN #1 artefact on disk | **DONE** | 9 validated · 6 crossed · **0 trusted** · 0 violations |
| **Carrier for structured content** | **PARTIAL** | `no_carrier:formula` replaces the false `unknown_role:formula`; a **servable** structured kind is **DEFERRED** — it needs rendering *and* a Founder trust decision |
| Per-block failure mode | **DONE, scoped** | version skew only; **every integrity violation still rejects the whole document** |
| Rich text | **ACCEPTED AS IS** | nothing added; the page crop is the honest path |

**Unplanned and delivered:** the **cap demonstration** on a second artefact (KHTN 7 Bài 20), where
the laboratory said TRUSTED and what crossed was `VALIDATED_REPAIR` +
`trust_gate:founder_decision_absent` — *capping demonstrated rather than asserted*. Plus a
**HISTORICAL CORRECTION TO ROUND 5** (the dispose-row verdict, §7 of its report).

---

## 5. WS-D · GOLDEN DELIVERY — PR #93

| Planned | Status | Actual |
|---|---|---|
| Workspace **Option B**, flag removed | **DONE** | enum, `WAL_ASSIST` flag and options A/C **deleted**; three duplicates removed |
| One word set for three views | **DONE** | and **no `lib/core` change was needed**, so it did not depend on WS-C |
| GOLDEN #1 → `assets/fixtures/real/` | **DONE** | lineage gate **PASS** under `--require-repair` |
| GATE E on a real Nokia 6.1 | **DONE** | see §7 below for the exact step tally |
| **Golden #2 Toán Bài 61** | **DEFERRED** | reassigned **by the Founder** to WS-A/WS-B; not a learner-facing delivery target |
| Bài 17 regression | **DONE** | lineage **L2 PASS** (fixture not stale); **L4 UNKNOWN** — there is no repair in it |
| Five-field lineage gate | **DONE** | `tool/evidence/fixture_lineage.py`, 16 unit tests |
| Visual grammar forms census | **DONE** | 238 lessons, 238 bridged, 0 refused |
| **Visual grammar bounded POC** | **NOT STARTED** | **the census says do not build one yet** |

**The most valuable thing WS-D did was not build something.** The plan permitted a bounded visual
POC; the census returned **`conceptMap` 0 instances and `timeline` 0 instances** — two of the four
renderer families have **no real data at all** — so it recommended adding none. That is
FORMS BEFORE RULES applied to a licence the plan had already granted.

---

## 6. What the plan assumed that turned out not to hold

| Plan assumption | What was found |
|---|---|
| R13 is a missing rule | **It is rule order.** The letterless test ran second, before every rule that could name the region — swallowing **17 of 18** Docling FORMULA regions. |
| Every silently-lost region is learning content that must become WITHHELD | **50 of 82 were defined non-learning.** Converting all of them would have traded a silent loss for a mass over-withhold. |
| Round 5's *corrected* served shares are the truth | **They are a LOWER BOUND.** Round 5 was wrong in **two opposite directions** — as-reported too high, corrected too low. |
| «274 = the OCR never read the digit» is one failure class | **Two.** DIGIT LOSS 312 (57 %) vs SEGMENTATION 196 (36 %). |
| Higher resolution is the recognition lever | **Falsified.** Every page is a **100 ppi scan**; scale 20 is interpolation. What changes is **context, framing and segmentation** — and recovery is **not monotonic in scale**. |
| A recovered digit improves a block | **Falsified.** RESTORE 10 → 10. The recogniser *adds* an observation where the destroyed one must be *superseded*. |
| More scales are free | **Falsified by the holdout.** +17 % recall for false recognition **0.049 → 0.083**. |
| Connecting the repair path risks trusting it | **True, and it took a design revision to avoid the mirror-image sin** — WS-C's first projection kept a block served against a fail-closed ruling. |
| A green suite means the app is honest | **Falsified three times over** — three tests at three layers encoded the synthetic era's optimism, and **all three pass or skip on a clean clone.** |

---

## 7. The one number this archive records differently from the coordinator

**GATE E device steps.**

| Source | Tally |
|---|---|
| Coordinator's report and WS-D's own table | **8 PASS / 1 honest FAIL** (9 steps) |
| **The device MANIFEST, which is the artefact** | **7 PASS · 1 FAIL · 1 UNVERIFIED · downgraded 1** *(PROVEN — re-read by the archive builder)* |

Both are honest, and the difference is a rule doing its job. **Step 08** — the per-pixel idle check
proving nobody was using the phone — **produced no frame**, and the manifest's own retention rule
says *«a PASS without an existing frame is downgraded to UNVERIFIED»*. The tool downgraded it; the
prose counted it as passed.

**This archive reports the manifest's tally**, because the manifest is the artefact a later reader
can check. See `08-DEVICE-EVIDENCE.md` §4.

---

## 8. Timeline

| Time (UTC, 2026-09-06) | Event | Source |
|---|---|---|
| — | Round-6 plan committed `1a75d24`; Founder addendum `51711c0` | git log *(PROVEN)* |
| 04:24:15 | Packs rebuilt for GATE E (`gitSha eac69ea1`, `capped-toc-v2`) | pack `buildProvenance` *(PROVEN)* |
| ~04:26–04:28 | Device walk on the Nokia 6.1, 7 frames | frame mtimes *(PROVEN)* |
| 04:30:13 | Device evidence manifest generated | manifest `generatedAt` *(PROVEN)* |
| 11:01 → 11:08 (local) | WS-C re-ran; **the lineage gate caught the 11:01 artefact as stale** | WS-D report §4.1 *(MEASURED)* |
| — | PRs #90–#93 opened, all CI green | GitHub API *(PROVEN)* |
| — | Composition verified in a throw-away worktree with real assets synced | consolidated §10.1 *(MEASURED)* |
| — | `ROUND5-ACCEPTANCE-CRITERIA.md` committed (`8ae8b9a`); consolidated report (`ba90f16`); composition CI (`d5a9946`) | git log *(PROVEN)* |

**A note worth keeping: round 6 also closed a round-5 gap.** The round-5 archive had to grade
against **RECONSTRUCTED** criteria because §16 was never committed. It is now committed as
`ROUND5-ACCEPTANCE-CRITERIA.md`, and the settled tally — **8 PASS · 1 PARTIAL · 1 FAIL** — matches
the round-5 archive's independent grading exactly. See `11-FOUNDER-ACCEPTANCE-CARD.md` §5.
