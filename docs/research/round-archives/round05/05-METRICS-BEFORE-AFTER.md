# 05 · METRICS — BEFORE → AFTER

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

**Reading rules that are binding on this file.**

1. **Denominators are never pooled.** Every number below names its population. Two numbers on
   different populations are not a trend.
2. **Nothing is averaged into a single score.** The five product scores in particular are
   reported separately, by Founder rule.
3. **Two served-share numbers exist and they answer different questions.** *As reported* =
   "of the blocks the pipeline classified, what share did it serve?" *Corrected* = "of what was
   extracted from the page, what share reached a child?" **Until R13 nothing distinguished them.**
4. Sources: `metrics/` and `reports/ROUND5-CONSOLIDATED-REPORT-2026-09-06.md`.

---

## 1. DATA ACCURACY SCOREBOARD — BEFORE → AFTER

**Population:** Lane D legacy batch 2 = six lessons across five failure classes, including
History/Geography (never measured before). Batch 1 is the holdout. PR #82, CI PASS on `0113019`.
*(MEASURED, with Wilson 95 % intervals where the lane computed them.)*

| Founder direction | Round 4 | Round 5 REPAIRED | Note |
|---|---|---|---|
| **FALSE TRUST ↓** | 0.297 [0.199, 0.418] | **0.318** [0.218, 0.438] vs **OLD 0.619** | 10/13 = 0.769 of batch 1's false-trust rows no longer served as before (was 7/13) |
| **TEACHING-CRITICAL ↓** | 0.176 [0.062, 0.410] | **0.100** [0.043, 0.214] vs OLD 0.476 | 2/5 closed; **9 and 13 mutilated structures unchanged** |
| **CORRECT SERVED ↑** | 221 served, ≈155 correct | **239 served**, ≈163 correct — **0.632 as reported, 0.589 once silent loss is in the denominator** | −8 colophon, +1 guard fix; **no served text changed** |
| **OVER-WITHHOLD ↓** | 12/30 = 0.400 | **19/30 = 0.633** [0.455, 0.781] | ⚠ **Moved the wrong way.** 1 of the 19 restored |
| **RESTORE PRECISION ↑** | not measured | **3/6 = 0.500** [0.188, 0.812]; the one NEW restore is **0/1 — wrong** | |
| **ATTACHMENT** (added this round) | 5/8 = 0.625 rescued | **8/8 = 1.000 — closed** | credited to Lane A1 |
| Display fidelity | — | 0.595 → **0.164** | |
| Reading order | — | 0.455 → **0.000** | |
| Role | — | 0.116 → **0.151** | ⚠ **Not better** |
| `trusted` / `eligible for teaching` | 0 / 0 | **0 / 0** | Unchanged, **by design** |

**Round-4 comparison caveat (important).** The round-4 column above is round 4's own tc2-p2
measurement on a *different* sample. Round 5's "vs OLD" column is the correct like-for-like
comparison — OLD is the shipped product's own output on the same batch.

---

## 2. R13 — the correction that changes how every other number reads

**Population:** the same batches, but counting from *extraction* rather than from
*classification*. *(MEASURED — reproduced in a second committed document,
`metrics/DATA-ACCURACY-SCOREBOARD-LANE-D.md` lines 78–79.)*

| batch | trusted | withheld | **silently lost** | digits | expressions | as reported | **corrected** |
|---|---|---|---|---|---|---|---|
| batch 2 (evaluation set) | 232 | 135 | **27** (27/394 = 0.069) | 17 | 8 | 0.632 | **0.589** |
| batch 1 (**holdout**) | 196 | 124 | **55** (55/375 = 0.147) | 21 | 10 | 0.613 | **0.523** |

| lesson | trusted | withheld | silently lost | as reported | corrected |
|---|---|---|---|---|---|
| **Toán 4 tập hai Bài 61** | 4 | 15 | **32** | 0.211 | **0.078** |
| Toán 4 tập một Bài 37 | 23 | 24 | 15 | 0.489 | 0.371 |
| Toán 5 tập một Bài 6 | 12 | 13 | 9 | 0.480 | 0.353 |
| LS&ĐL 4 Bài 12 | 24 | 22 | 8 | 0.522 | 0.444 |

**Round-6 workstream A exists to close this**, with a hard conservation identity:
`INPUT = SERVED + WITHHELD + EXCLUDED_WITH_REASON + defined non-learning`; **any unexplained
difference is a HARD FAILURE**.

---

## 3. RESTORE — separated by mechanism, because the mechanisms differ by everything

| Path | Restored | Precision | 95 % interval |
|---|---|---|---|
| Guard relaxation (legacy batch 2) | 1 of 19 falsely-withheld | **0 / 1 = 0.000** | [0.000, 0.793] |
| Verdicts transferred (legacy batch 1) | 4 of 12 falsely-withheld | **3 / 6 = 0.500** | [0.188, 0.812] |
| **Validated math repair (A2)** | 10 | **10 / 10 = 1.000** | [0.722, 1.000] |
| …of which on the **HOLDOUT** | 8 | **8 / 8 = 1.000** | — |
| History disposition repair (C) | 6 of 16, + 1 event anchor | print-confirmed, **guard unchanged** | — |

**Predictive power of the 97-row audit's own labels:** 3 of 4 **OVER**-withheld → **correct**;
2 of 2 **SAFE** refusals → **wrong**.

---

## 4. LANE A2 — the validated math path

**Population:** 89 hand-counted printed fractions across 3 pages (detection); 97 Toán pages /
2,692 blocks (coverage); 36,029 blocks / 1,410 pages (physics false trust). *(MEASURED)*

| Measure | Result |
|---|---|
| Fraction detection precision | **1.000** [0.957–1.000] |
| Fraction detection recall | **0.955** [0.890–0.982] |
| Restored expressions, hand-verified | **10 / 10 = 1.000** [0.722–1.000] |
| …on the HOLDOUT | **8 / 8 = 1.000** |
| Surviving false corrections | **0** |
| Fabricated expressions | 2 → **0** |
| Physics false trust | **−3 blocks** at **0** over-withhold cost |
| Toán coverage | 0.1686 → **0.1705** |
| Unrepairable fractions | **336**, of which **274 (82 %)** the OCR never read |

---

## 5. LANE A4 — signal quality, and false correction as P0

**Populations, never pooled:** H = 480 injected OCR lines / 6,554 tokens from a **held-out book**;
H-clean = the same rows uncorrupted; L = Lane C Bài 8, 51 SDM blocks / 15 token slips; S = 1,200
real SDM blocks (routing only). *(MEASURED)*

| Signal | Detection recall | Correction precision | **False correction rate** | Proposals / 1,000 clean tokens |
|---|---|---|---|---|
| **Cross-corpus (strict)** | 0.500 | 0.938 | **0.063** | **0.92** |
| Cross-corpus (recall policy) | 0.644 | — | 0.092 | 2.90 |
| **LLM semantic** | **0.717** | — | **1.000** (13/13 wrong) | 26.7 % of rows flagged |

| Router | human-review rate |
|---|---|
| Router (composed) | **0.0900** |
| LLM alone | 0.416 |
| Cross-corpus alone | 0.993 |
| External alone | **0.000** |

- Proper-noun false correction **0.000** at all three cross-corpus policies.
- **End-to-end with A1's engine: 0 repairs, 0 false corrections — and 4 blocks moved TRUSTED →
  SUSPECT, 1 rightly and 3 wrongly: demotion precision 0.250.**
- Edge hypothesis: line-end tokens carry **3–4×** the interior unattested rate, **n = 486,000** —
  confirmed. Its "runs into the right margin" refinement — **falsified at 0.5×**.

---

## 6. LANE A3 — role agreement, and the honest measure

*(MEASURED, n = 26 — deliberately over-sampling known disagreements; **in-sample**.)*

| | agreement | κ | #1 WRONG | #2 WRONG |
|---|---|---|---|---|
| before (round-4 judgement, these 26 rows) | 0.769 | **0.524** | 0.308 | 0.462 |
| after (spec applied) | 0.962 | **0.923** | 0.500 | 0.538 |
| after, on the 23 rows the spec decides | 1.000 | **1.000** | — | — |

**The honest measure is decidability: 23/26 = 0.885 decided · 3 convention-dependent · 0
undecidable.** κ on the whole round-3 second-annotation sample was 0.713 and on the batch-1 rows
0.423; **0.524 here is lower than both only because this sample over-samples disagreements. The
three numbers are on three different samples and must not be compared as a trend.**

**Baseline reproduction, asserted page by page:** 643 learning blocks · 354 served ·
coverage **0.5505** · 26 false trusted · FTR **0.0734**. Audit plane: round-3 484-row sample
**312/480 = 0.650**; legacy batch-1 NEW **27/74 = 0.365**.

---

## 7. LANE C — Bài 8, print-verified ledger

*(MEASURED / OBSERVED against a 150-dpi print read by a human.)*

| | round 4 | round 5 |
|---|---|---|
| false trust | 8 | **6** |
| correct served | 26 | **30** |
| false withheld | 14 | **10** |
| Bài 8 learning blocks | 51 = 34 trusted + 17 withheld | 51 = **36 trusted + 15 withheld** |
| LS&ĐL 5 lessons with a TSL | 23 / 28 | **28 / 28** |
| book trusted blocks | 1,263 | **1,020** (`agree_tones` 0 → 179) |
| `prose-dated-events-v1` events | 7 (round-4 document) | **0** — and 3 across 28 lessons at book scale |
| date mentions printed in the book | — | **112 in 8 forms**; the rule accepts **1** |

---

## 8. LEGACY REPROCESS SCOREBOARD — packs

*(MEASURED, PR #82.)*

| Measure | Result |
|---|---|
| Pack `verify` | **0/12 FAIL → 12/12 PASS** |
| OLD baseline reproduced | **three times**, identical to `BASELINE-METRICS.json` field for field |
| Content delta of the provenance rebuild | **exactly zero** — 248/248 unchanged, 12/12 hashes identical |
| Blind badge audit of the diagnostic delta | **27/27 = 1.000**; 4 unbadged pages *unjudgeable* → reported **unmeasurable**, not 0.964 |
| Founder §3 fail-closed | **−41 of 248** activities; **10 lessons lose their exercise list entirely**; 10 grades byte-identical; defect 6 **ABSENT** on shipped packs (0 of 207) |
| **R15 — attach provenance reproduction** | ⚠ **950 of 6,176** page verdicts differ from a fresh run, **896 unexplained** |
| Surviving defects | R1 **FIXED** (class closed on a second book, tail-scan 1/6 → 0/6) · R2, R3 **PRESENT** on a fourth build · R7c **PARTIAL** |

---

## 9. THE FIVE PRODUCT SCORES — reported separately, never averaged

*(MEASURED on device / by machine census. Lane B, PR #87.)*

| Score | Round 4 | Round 5 | Basis |
|---|---|---|---|
| **Experience Fidelity** | 80–85 % | **85–88 %** | Trực quan **70–80 % → 85–90 %** (reached the board) · Bookshelf 65–75 % → 80–85 % · Book 70–80 % → 80–88 % |
| **Source Reality** | 97 visible elements | **97** | unchanged |
| **Source Trust** | 0 / 97 | **0 / 97** | unchanged — no trust threshold set, **by Founder gate** |
| **Pedagogy Reality** | 7 / 17 | **7 / 17** | unchanged |
| **Evidence Reality** | 0 of 0 | **0 of 0** | unchanged |

**Only Experience Fidelity moved, and §8.1 of the consolidated report is why: the repair path is
not wired into the product, so nothing this round could have moved Source Trust or Pedagogy
Reality even in principle.**

---

## 10. WORKSPACE DENSITY — measured on the device before anything was designed

*(MEASURED — real Nokia 6.1, real Bài 17 fixture, template match error 0.0; plus a widget-tree
measurement at the exact viewport 392.7 × 698.2 dp.)*

| Option | first content (device) | % screen consumed before content | view labels on screen | «why» in place |
|---|---|---|---|---|
| **CURRENT (card)** | **820 px** | **42.7 %** | **7** | 0 taps |
| A · icon | 634 px | 33.0 % | 3 | 1 tap (sheet) |
| **B · peek** | **712 px** (634 collapsed) | **37.1 %** | **4** | **1 tap, in place** |
| C · inlineTab | **565 px** | **29.4 %** | 3 | none |

Widget tree, «Học với SAM»: pinned chrome **411 dp = 58.9 % of the viewport**, with **7
occurrences** of the three view names on one screen.

**Founder decision: B** *(recorded in `docs/research/ROUND6-PLAN.md`, workstream D — PROVEN)*.

---

## 11. TEST AND CI COUNTS

*(PROVEN — CI status re-read from the GitHub API; suite counts MEASURED as recorded per lane.)*

| Scope | Result |
|---|---|
| **Composed round** (9 branches, throw-away worktree) | **0 conflicts** · `flutter analyze` clean · **Python 623 OK** (19 skipped) · **Dart 1061 pass** (3 skipped) |
| Lane B | Dart **995 passed / 1 skipped**, CI 2m16s |
| Lane E2 | Dart **973 pass / 42 skipped** |
| Lane C | Dart 928 passed / 42 skipped · Lane C Python 31 passed / 2 skipped |
| Lane D | Dart **948 pass / 15 skipped** · Python **348 OK** |
| Lane A4 | Python **321 passed / 8 skipped** |
| Lane E1 | **285 tool tests OK** |
| Lane A3 | 25 unit tests in `tool/tests/test_thresholds.py` |
| All 10 PRs | `Analyze & Test = SUCCESS` |

---

## 12. DENOMINATORS IN USE THIS ROUND — stated, never summed

| Denominator | Count | What it is |
|---|---|---|
| canonical rows in `all-lessons.csv` | **3,679** | **HISTORICAL BASELINE ONLY** until lesson identity is resolved |
| **distinct lesson keys** | **3,240** | E1's finding — **154 keys duplicated across 439 rows** |
| ranged | 3,381 | source-pipeline measurement denominator |
| units-backed | 1,784 | |
| TSL-backed | 224 | the only population with structured lessons |
| gold pages / blocks | 54 / 643 | the fidelity plane |
| legacy lessons in scope | 243 | |
| 97-row independent audit | 97 | **evaluation set, not a tuning set** |

E1's tiers: A 222 · B 368 · **C 1,384** · D 1,266.
REPRESENTABLE **1,654 / 1,784** · EXTRACTABLE **220 / 224** (191 multi-family) ·
VALIDATABLE **3 lessons / 1 family** · **LEARNER_READY 0**.

**Exception clusters:** NO_SOURCE_AT_ALL **1,384 lessons (42.7 %)** — *no grammar change moves
this; it is a source-pipeline problem wearing a semantics costume*. NEEDS_MATH_AST **1,096
(33.8 %)** — one extension worth **9×** everything else. Ranks 3–7 together: 235.

**Source-structure gaps:** 1,642 questions and **4** option blocks · **20** table blocks and **0**
with cells · **0** blocks retaining fraction or exponent shape · 3,864 figures, 33.6 % with a
caption, 465 orphan «Hình N.M» labels. **Ngữ văn / Tiếng Việt — the subjects where verse matters
— have no TSL at all, so they have never been measured.**
