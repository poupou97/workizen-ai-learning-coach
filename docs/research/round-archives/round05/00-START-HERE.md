# 00 · START HERE — Round 5 in five minutes

> **HỌC CÙNG SAM — ROUND 5 RETROSPECTIVE ARCHIVE**
> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.** Verbatim SGK text, SGK page crops and
> publisher cover artwork inside this archive are internal research material under Founder
> rule **D4**. Nothing in this archive may be distributed outside Workizen.

| | |
|---|---|
| **ROUND** | 5 — *DATA ACCURACY: REPAIR → VALIDATE → RESTORE* |
| **DATE CLOSED** | **2026-09-06** (consolidated report dated 2026-09-06; last round-5 commit `bab657a` 2026-09-06; all nine lane PRs opened 2026-09-05 → 2026-09-06) |
| **VERDICT (archive builder's assessment)** | **PARTIAL — CAPABILITY PROVEN, NOTHING DELIVERED TO A CHILD** |
| **NORTH STAR** | *Raise data accuracy; every failure class moves `DETECT → REPAIR → VALIDATE → RESTORE or WITHHOLD`; coverage begins to recover **without loosening a guard*** → **PARTIAL** |
| **ACCEPTANCE TALLY** (ten criteria, §11 of this archive) | **8 PASS · 1 PARTIAL · 1 FAIL** on the reconstructed ten — see §11 for why this differs by one from the Founder's own 7 · 1 · 2 |
| **MERGE STATUS** | **NOTHING MERGED.** 10 open PRs (#79 integration base + #80–#88), all CI green, none merged. *(PROVEN — GitHub API, 2026-09-06)* |

---

## ONE-LINE RESULT

**Round 5 proved that a validated repair path works — 10 of 10 restores correct, 8 of 8 on a
holdout the rules never saw — and that relaxing a guard instead does not: 1 region restored,
0 of 1 correct. Then it proved that neither result reached a child, because the repair path
is not wired into the pipeline and nothing merged.**

---

## NORTH STAR: **PARTIAL**

| Half of the North Star | Verdict | Why |
|---|---|---|
| *Every failure class moves `DETECT → REPAIR → VALIDATE → RESTORE or WITHHOLD`* | **PASS** | The framework exists (A1), a repairer plugin registered into it (A2), five verification signals registered into it (A4), and Lane C ran the loop to completion including a correct **WITHHOLD** when two signals objected to a repair candidate. |
| *Coverage begins to recover **without loosening a guard*** | **FAIL** | The only coverage that recovered came from **loosening a guard**, and it was wrong (0/1). Corrected for silent loss, served share **fell**: 0.632 → **0.589** (evaluation set), 0.613 → **0.523** (holdout). Over-withholding moved the wrong way, 0.400 → **0.633**. |

---

## TOP COMPLETED ITEMS

1. **A validated repair path, measured end to end (Lane A2, PR #84).** Fraction detection
   precision **1.000** / recall **0.955** on 89 hand-counted printed fractions; **10/10**
   restored expressions correct, all hand-verified against the printed page, **8/8** of them
   on a holdout; **2 fabricated expressions → 0**; physics false trust **−3 blocks at zero
   over-withhold cost** across 36,029 blocks / 1,410 pages.
2. **The pack machinery became trustworthy (Lane D, PR #82).** Pack `verify` **0/12 FAIL →
   12/12 PASS**; the OLD baseline reproduced **three times**; the provenance rebuild's content
   delta **exactly zero** (248/248 unchanged, 12/12 hashes identical); a blind badge audit of
   the diagnostic delta **27/27**.
3. **Attachment closed. 8/8 = 1.000** — every attachment defect in the batch fixed in the
   pipeline, plus the R1 class closed on a second book (tail-scan 1/6 → 0/6).
4. **False trust and teaching-critical error fell hard on the measured batches.** False trust
   **0.619 → 0.318**; teaching-critical **0.476 → 0.100**; display fidelity 0.595 → 0.164;
   reading order 0.455 → **0.000**.
5. **A written role taxonomy where there was none (Lane A3, PR #80).** ROLE DEFINITION SPEC v1,
   20 roles × 8 fields, plus a trust-gate **sensitivity curve** and no threshold chosen.
6. **The visual layer became general (Lanes E1/E2, PRs #85/#86).** One renderer proved across
   **three subjects and two independent semantic paths**; **6 primitives · 6 relations** carried
   everything built across 224 lessons; three planned per-subject graph subsystems **refuted**.
7. **The workspace stopped repeating itself (Lane B, PR #87).** First lesson content moved from
   **820 px to 712 px** peeking / **634 px** collapsed on the real Nokia; six labels for three
   views became four; four genuine duplicates removed. Three options built from one commit and
   measured; **the Founder selected B**.
8. **Trực quan finally reached the concept board** — 70–80 % → **85–90 %** — a lesson's structure
   renders as an actual mindmap and process flow instead of text pretending to be a diagram.
9. **The round composes.** Nine branches merged in a throw-away worktree: **0 conflicts**,
   `flutter analyze` clean, **623 Python tests OK**, **1061 Dart tests pass**.

---

## TOP FAILURES AND DISCOVERIES

1. **R13 — SILENT LOSS.** A block whose role is `empty` reaches **neither** `blocks` **nor**
   `withheld` of the Trusted Structured Lesson, and carries **no reason code**. It is a
   disappearance, not a withholding, and every rate every lane published is blind to it.
   Corrected served share: **0.632 → 0.589** (evaluation set), **0.613 → 0.523** (holdout),
   **Toán 4 tập hai Bài 61: 0.211 → 0.078**. **The lost blocks are the printed exercises.**
2. **Guard relaxation is not repair, and the round measured the price.** 1 of 19 falsely-withheld
   regions came back, at restore precision **0 / 1 = 0.000**. The region was served as
   `I1 - Định luật khúc xạ ánh sáng Ô C. SỐNG` — a Roman `II` read as `I1`, plus a watermark
   fragment spliced into lesson text.
3. **REPAIR IS BUILT AND NOT CONNECTED.** No file outside `tool/corpus/repair/` and
   `tool/tests/` imports the `repair` package at all. "No served text changed anywhere" is a
   **structural certainty of the wiring**, not a measurement outcome.
4. **The LLM finding.** Anomaly detection recall **0.717 — best in the lane** — with a
   false-correction rate of **1.000**: 13 corrections proposed on already-correct lines,
   **all 13 wrong**. Verdict: detector only, never a proposer.
5. **FORMS BEFORE RULES.** Enumeration is a nearly closed form — 7 of 10 forms, coverage
   **0.992** — which is why PROCESS reaches **104/224** lessons. Date is wide open — 3 of 12
   forms, **0.140** — which is exactly why TIMELINE reaches **3/224**. Lane C found the same
   thing independently: LS&ĐL 5 prints **112 date mentions in eight forms** and
   `prose-dated-events-v1` accepts **one**. Lane E2 found it a third time at 6/54 gold pages.
6. **Three integration defects no per-lane CI could see** — a constructor/getter compatibility
   gap, a plugin loader that silently returned an **empty** signal list, and lesson identity
   leaking inside a **value** while two field-name guards stayed green.
7. **The lesson-identity challenge.** `all-lessons.csv` has **3,679 rows but 3,240 distinct
   lesson keys** — **154 keys duplicated across 439 rows**. Every "/ 3,679" figure in every
   round depends on the answer. Reported, **not fixed** — Founder gate.
8. **`agree_tones` failed as a third signal.** Book-wide it cut trusted text 1,263 → 1,020, and
   on Bài 8 it withheld the one block carrying **all seven dated events** on a single token,
   **where the print says the primary stack was right**.

---

## WHAT REACHED THE CHILD

**Presentation only, and only on the test device.**

- On the Nokia 6.1 walked in this round (debug APK from `lane-b/round5-experience`, sha256
  `e3b3b433…`), a child opening KHTN 6 Bài 17 sees a **real mindmap** (hub + four coloured
  branches + curved edges) and a **real process flow** (nodes / edges / arrows) instead of a
  text stand-in, plus a source-grounded figure chip that fails closed.
- **Less clutter before the lesson starts** — first content at 712 px instead of 820 px, and
  four view labels instead of seven.
- **Five defects only the device could find** were fixed and re-walked — including a pinned card
  that was covering the very hub of the mindmap it was recommending.

## WHAT DID **NOT** REACH THE CHILD

- **No accuracy correction from this round reached anything.** The repair path is not wired into
  the pipeline; the main checkout's packs are still the old ones; **no APK built on this Mac
  carries any of this round's accuracy corrections**.
- **Nothing merged.** All ten round-5 PRs are open. Round 4's PR #73 is also still open.
- `trusted` = **0** and `eligible for teaching` = **0**, unchanged and by design — no production
  trust threshold exists, by Founder gate.
- The two Founder-named defects `II → I1` and `3×10⁸ → 3×10°` are **still present**; both are
  born at OCR recognition, where no parser can reach them.
- **UNAVAILABLE:** whether the round-5 debug APK is still installed on the Nokia today was not
  checked (the device protocol forbids interrupting the Founder's use of the phone).

---

## KEY METRICS (all with their denominator; never averaged)

| Metric | Round 4 | Round 5 | Direction |
|---|---|---|---|
| False trust (legacy batch 2, n=judged served rows) | 0.297 [0.199, 0.418] | **0.318** [0.218, 0.438] vs **OLD 0.619** | ↓ vs OLD |
| Teaching-critical error | 0.176 | **0.100** [0.043, 0.214] vs OLD 0.476 | ↓ |
| Display fidelity | — | 0.595 → **0.164** | ↓ |
| Reading order | — | 0.455 → **0.000** | ↓ |
| Role error | — | 0.116 → **0.151** | ⚠ **worse** |
| Over-withhold | 12/30 = 0.400 | **19/30 = 0.633** [0.455, 0.781] | ⚠ **worse** |
| Restore precision — guard relaxation | not measured | **0 / 1 = 0.000** | — |
| Restore precision — validated repair (A2) | not measured | **10 / 10 = 1.000**, holdout **8/8** | — |
| Correct served (as reported) | 221 served ≈155 correct | **239 served ≈163 correct — 0.632** | ↑ |
| **Correct served (corrected for R13 silent loss)** | — | **0.589** eval · **0.523** holdout · **0.078** on Toán 4 t2 Bài 61 | ⚠ **↓** |
| Attachment | 5/8 = 0.625 | **8/8 = 1.000 — closed** | ↑ |
| Pack `verify` | 0/12 FAIL | **12/12 PASS** | ↑ |
| Experience Fidelity | 80–85 % | **85–88 %** | ↑ |
| Source Reality / Source Trust | 97 / **0 of 97** | 97 / **0 of 97** | flat by design |
| Pedagogy Reality / Evidence Reality | 7/17 / 0 of 0 | **7/17** / **0 of 0** | flat |
| `trusted` / `eligible for teaching` | 0 / 0 | **0 / 0** | flat by design |

---

## NEXT BOTTLENECK — **RECOGNITION, NOT REASONING**

Both remaining Founder-named defects (`II → I1`, `3×10⁸ → 3×10°`) are born at OCR recognition;
the digits and letters around them survive. **82 % of Lane A2's unrepairable fractions —
274 of 336 — failed for the same reason: the OCR never read the digit.** No parser, normaliser
or agreement check can reach text that was never captured.

## NEXT ROUND NORTH STAR

**Round 6 — "MAKE VERIFIED ACCURACY REACH THE LEARNER."** Four workstreams (Truth Accounting ·
Recognition · Repair → Product · Golden Delivery) and five fixed acceptance gates.
See `12-NEXT-ROUND-PLAN.md`.

---

## MERGE RECOMMENDATION

**Hold the nine round-5 lane PRs (#80–#88). Clear the *governance* debt separately.**

- Round 5 is **READY FOR FOUNDER REVIEW**: nine lanes CI-green individually and green composed.
- But merging the **lane** work would ship a repair laboratory that is **not connected to the
  product**, a set of denominators that **R13 has invalidated**, and pack machinery whose attach
  provenance **does not reproduce (R15)**. Three of those nine branches also touch code that
  round 6's workstream A is changing right now. None of this argues for discarding the work; all
  of it argues against making it `main` before round 6 answers it.
- **On the merge debt itself, round 6 has already produced the audit** (Part II —
  `reports/ROUND6-MERGE-DEBT-AUDIT.md`, produced after round 5 closed) and its recommendation is
  **merge #79, close #73 as subsumed, hold #80–#88**. The reasoning is checkable: #73 is a strict
  **ancestor** of #79, and the entire delta between them is **documentation — 16 commits touching
  3 files, all under `docs/research/`, zero code, zero tests, zero assets**. #79 does **not**
  contain round 5's lane code. So merging #79 ships *round-4 code the Founder has already
  accepted, plus round 5's report.*
- **And it must not be mistaken for delivery:** packs under `assets/pack/` are gitignored build
  artefacts. **Merging #79 changes no APK.** It clears governance debt; it delivers nothing to a
  child.
- **The status quo is the expensive option.** Round 4 is *accepted and unmerged*; round 6's base is
  a synthetic composition branch holding 114 commits reachable from nowhere else. If round 6 also
  does not merge, round 7's base becomes a composition of a composition.

**This archive endorses that audit's recommendation and does not act on it.** Merging is a Founder
gate.

## FOUNDER DECISIONS REQUIRED

| # | Decision | Why it blocks |
|---|---|---|
| 1 | **Wire the repair path into the pipeline?** (`CONNECT ≠ TRUST`) | Today it is a validated laboratory with a measured false-correction rate and **no connection to the product**. Nothing a lane does can change served accuracy until this is decided. |
| 2 | **Set a production trust threshold?** | `THRESHOLDS.json` does not exist, so `trusted` computes to **0 by construction**. A3 built the instrument and the curve; **no point on it was chosen**, deliberately. |
| 3 | **R15 — attach provenance does not reproduce.** 950 of 6,176 page verdicts differ from a fresh run, **896 unexplained**. | The **pack build** depends on attach provenance. Batch comparisons never touch it; the pack build does. |
| 4 | **Lesson identity — is 3,679 a lesson count or a row count?** 154 keys duplicated across 439 rows; 3,240 distinct keys. | Every "/ 3,679" figure in every round depends on the answer. |
| 5 | **Q-ROLE-1 / Q-ROLE-2 / Q-ROLE-3** — the three role-definition questions the spec could not decide. | 1 of 6 measured role disagreements and 1 of 13 controls flip with the answer; Q-ROLE-2 decides whether the `math_guard` exemption applies to every arithmetic exercise in Toán. |
| 6 | **Merge debt** — #73 and #79 both open, round 6 composing on top. | The round-6 Part II audit is **done** and recommends **merge #79 · close #73 as subsumed · hold #80–#88**. Only the Founder can execute it. |
| 7 | ~~Workspace option A / B / C~~ | **ANSWERED — B selected** (recorded in `docs/research/ROUND6-PLAN.md`, workstream D). |

---

### How to read this archive

`01`–`05` are the round's *record*: objective, plan vs actual, work, failures, metrics.
`06`–`09` are the round's *reality*: what a child/parent/SAM actually got, the test and PR
evidence, the device walk, and the architecture/data changes. `10`–`14` are *forward-looking*:
risks, the acceptance card, the next round, the remaining roadmap, and tracker status.
`15` is the file manifest with a SHA-256 per file.

**Claim labels used throughout:**
**PROVEN** = re-verified first-hand by the archive builder against the repository, the GitHub
API, or a recomputed file hash · **MEASURED** = a number produced by a lane's instrument and
recorded in a committed report the coordinator verified · **OBSERVED** = seen on a real device
or a page render · **INFERRED** = a conclusion drawn from evidence, not itself measured ·
**HYPOTHESIS** = proposed, not tested · **UNKNOWN / NOT CAPTURED / UNAVAILABLE** = the evidence
does not exist, and saying so is the correct answer.
