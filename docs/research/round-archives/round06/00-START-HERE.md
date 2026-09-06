# 00 · START HERE — Round 6 in five minutes

> **HỌC CÙNG SAM — ROUND 6 RETROSPECTIVE ARCHIVE**
> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.** Verbatim SGK text, SGK page crops and publisher
> cover artwork inside this archive — including the two real lesson fixtures and the twelve lesson
> packs under `evidence/round6-artefacts/` — are internal research material under Founder rule
> **D4**. Nothing here may be distributed outside Workizen.

| | |
|---|---|
| **ROUND** | 6 — *VERIFIED ACCURACY → REAL PRODUCT* |
| **DATE CLOSED** | **2026-09-06** (consolidated report dated 2026-09-06; last round-6 commit `d5a9946`; all five PRs #89–#93 opened and CI-green the same day; device manifest `generatedAt` 2026-09-06T04:30:13Z) |
| **NORTH STAR** | **MAKE VERIFIED ACCURACY REACH THE LEARNER** → **REACHED — and the first thing it did was take something away** |
| **GATES** | **A ACCOUNTING PASS · B RECOGNITION PASS · C REPAIR PASS · D TEACHING — TRUTHFUL ZERO · E DEVICE PASS** — graded independently in §11 of this archive; all five agree with the coordinator |
| **VERDICT (archive builder)** | **DELIVERED, HONESTLY — AND THE CHILD PAID FOR IT** |
| **MERGE STATUS** | **NOTHING MERGED.** #89–#93 open and CI-green; round 5's #79–#88 and round 4's #73 also still open *(PROVEN — GitHub API, 2026-09-06)* |

---

## WHAT REACHED THE CHILD — the loss first

**A real History lesson replaced a fake one, and the child lost the timeline.**

LS&ĐL 5 Bài 8 («Đấu tranh giành độc lập thời kì Bắc thuộc», SGK pages 36–39) used to open with
**23 `[MẪU]` placeholder blocks** — invented prose — plus a **7-event timeline** and a **7-step SAM
script**, both fabricated. On a real Nokia 6.1 today it opens with **34 blocks of real SGK text**
and **17 honest gaps, each stating its reason**.

**And the timeline is gone. Seven events → none. The SAM script is gone. Seven steps → none.**

The block carrying all seven dated events, `p039:000`, was **repaired and validated** in round 6 —
and is **still withheld**, because no production trust threshold exists. *(PROVEN — the archive
builder read the shipped fixture: `type: withheld`, `reasons: ["agree_tones"]`, **no `text`
field**, `repair.disposition: VALIDATED_REPAIR`, `servable: false`.)*

**Second loss, also on purpose: the app now offers ZERO Toán exercises.** Round 5's fail-closed fix
finally reached an APK on this machine, and **all 41 geometry-rebuilt `toanExercises` entries
stopped shipping** — g4 26, g5 15, activities **248 → 207**. *(PROVEN — recomputed by the archive
builder from the two pack sets archived here.)*

**The one gain that is not a subtraction:** the lesson screen is less cramped. Pinned chrome
**411 dp → 281 dp**, and — the number that matters more — **identical across all three views** for
the first time; 225 dp once dismissed; view labels **7 → 4**, now **one word set** instead of two.

### PARENT · **NOTHING NEW.** SAM · **NOTHING NEW.**

Not "small improvements" — **nothing**. There is no SAM script on the real Bài 8 path, and no
parent surface was touched or measured.

> **The honest sentence for this round: it bought honesty, and paid for it in visible content.**

---

## TOP COMPLETED ITEMS

1. **Silent loss is zero.** **138 unaccounted → 0** across **29 lesson ledgers / 1,878 input
   regions** — evaluation set, holdout, both Golden slices and **five lessons nobody selected** —
   enforced by a check that **exits non-zero**.
2. **And the served set is byte-identical before and after, in every population.** No guard
   weakened, no coverage bought. This was the claim most likely to fail; it did not.
3. **The root cause was rule order, not a missing rule.** The letterless test in `assign_role` ran
   second, swallowing **17 of 18** Docling FORMULA regions. One mechanism explains R13, A2's
   `empty_block` finding, and the `7 8 2 8 7 - 2 8 5 8` misdescription together.
4. **Recognition reached a defect round 5 called unreachable.** `b) 3/10 + 5/21` — whose numerator
   `3` is absent from the whole-page OCR entirely — is read correctly from a targeted re-crop.
   **Bài 61: 17 of 47 recovered, 17/17 correct, 0 disagreements on 38 controls.** No dependency
   added; **~0.46 s/region**; the same Apple Vision engine that ships on iOS.
5. **A `ValidatedRepair` crossed the production-shaped pipeline without becoming trusted.**
   **9 validated · 6 crossed · `trusted: 0` · violations 0** — verified by the archive builder in
   the shipped artefact, not taken on report.
6. **Capping demonstrated rather than asserted** — a second artefact (KHTN 7 Bài 20) where the
   laboratory said TRUSTED and what crossed was `VALIDATED_REPAIR` +
   `trust_gate:founder_decision_absent`.
7. **The lineage gate caught a stale artefact on its first real use** — the 11:01 copy no longer
   hashed to what it claimed at 11:08. **Round 5's trap, caught by machine.**
8. **Canonical lesson identity answered: neither 3,679 nor 3,240.** `3,650` — and **3,240 deletes
   410 real lessons**, the direction nobody was watching.
9. **Workspace Option B shipped**, the A/B/C flag removed, three duplicates deleted, one word set
   for three views.
10. **The round composes:** 5 branches, **0 conflicts**, `flutter analyze` clean, **748 Python**,
    **1084 Dart** — with the real gitignored assets synced in, which is what made §10 visible.

---

## TOP FAILURES AND DISCOVERIES

1. **The systemic finding: three tests, at three layers, all encoding the synthetic era's
   optimism.** `lesson_index_test.dart` (packs) · `timeline_history_test.dart` (`lib/core`) ·
   `no_machine_ids_test.dart` (UI). **Every one passes or skips on a clean clone.** Only a
   **composed tree with real assets** surfaces them. Each was corrected by **fixing the premise,
   never loosening the gate**, and mutation-checked.
2. **WS-D corrected its own too-weak first fix, and that is the sharper lesson.** Its first rewrite
   asserted an *equivalence* — the timeline appears **iff** the document carries a
   `TimelineSemantic` — which is satisfied by the app faithfully drawing whatever the data says.
   **Injecting a `TimelineSemantic` made a timeline appear and the test stayed green.** The
   property that matters is not «does this lesson have events» but **«has anyone been granted
   trust»**. The rule now reads the **published artefact** (`disposition` + `servable != true`).
3. **The coordinator falsified three of its own statements to the Founder.**
   · «The lost blocks are the printed exercises» — only partly right: of 82, **31** symbol
   fragments, **20** numeric labels, **13** unreadable FORMULA regions, **18** whole/stacked
   expressions.
   · **Round 5's *corrected* served shares are a LOWER BOUND, not the truth** — they put every lost
   region in the learning denominator, and **50 of 82 were defined non-learning**. Round 5 was
   wrong **in two opposite directions**. Accounted: batch 2 **0.617**, holdout **0.571**, Bài 61
   **0.154**.
   · «274 = the OCR never read the digit» is **two** failures: **DIGIT LOSS 312 (57 %)** vs
   **SEGMENTATION 196 (36 %)** — a third of that population *was* recognised and glued elsewhere.
4. **Scale is not the lever; segmentation is.** Every SGK page is a **100 ppi scan**, so scale 20
   is interpolation, not information — and recovery is **not monotonic in scale**.
5. **Ω is unreachable by this lever: 0 of 22, at every scale.** A crop recovers a character the
   engine *could* read but did not isolate; it recovers nothing when the glyph is not in its
   repertoire.
6. **A recovered digit does not become a repaired block** (RESTORE 10 → 10, Δ = 0). The recogniser
   *adds* an observation where the destroyed one must be *superseded*.
7. **More scales are not free.** DEV said the 8-scale ladder cost nothing; **the holdout said false
   recognition 0.049 → 0.083**. Four scales stays.
8. **Two of WS-B's own census rules were mostly false positives** — ohm 586 → **22**; subscript
   precision **5/16**; the unigram diacritic rule produced **26,703** "candidates" that are
   ordinary Vietnamese words. **All three found by probing, not by review.**
9. **WS-C falsified its own first design** — the projection initially kept a block served when the
   ledger ruled `WITHHELD`/`SUSPECT`/`CONFLICT`: *overriding a fail-closed ruling to protect
   coverage*, the mirror of «never weaken a guard». Default is now `withhold`.
10. **CodeFormulaV2 rejected on measurement** — 87.2 s/region vs 0.46 s, 4/7 correct, reads `7` as
    `T`/`E`/`F`.
11. **Two device-only findings no test could reach** — SAM tells the child to **leave the lesson
    they just opened** («SAM gợi ý: Về mục lục», reason «Con đã đi qua các cách học của bài này»,
    while the row beneath it reads `● Đọc ○ Trực quan ○ Học với SAM`); and the lesson title is
    **lowercased at the display layer** — «thời kì **b**ắc thuộc» — on a historical proper noun.
    *(The archive builder confirmed the second is a display defect: the data says **B**.)*

---

## KEY METRICS

| Dimension | Round 5 | Round 6 |
|---|---|---|
| **Silent loss (UNACCOUNTED)** | 138 across the same populations | **0** — 29 ledgers / 1,878 regions, enforced by a non-zero exit |
| Served set, before → after the fix | — | **byte-identical** in every population |
| **Served share, accounted** | reported 0.632 / corrected 0.589 | **0.617** (evaluation set) · **0.571** (holdout) · **0.154** (Bài 61) |
| Withheld counts | 135 · 124 · 30 | **144 · 147 · 37** — always-refused regions are now **visible** |
| **Recognition** | not measured | **17/47 recovered on Bài 61, 17/17 correct**; holdout digit recall **0.181**; false recognition **0.049** |
| **Repair** | laboratory only, 0 connected | **9 validated · 6 crossed · 0 trusted · 0 violations** |
| Source Reality | 97 | **97** |
| **Source Trust** | 0 / 97 | **0 / 97** — no trust threshold set (Founder gate) |
| Pedagogy Reality | 7 / 17 | **7 / 17** |
| Evidence Reality | 0 of 0 | **0 of 0** |
| **Product Delivery Reality** | 0 real lessons | **1 real lesson on a real device — minus its timeline** |
| Workspace pinned chrome | 411 dp («Học với SAM») vs 225 dp elsewhere | **281 dp, identical in all three views**; 225 dp dismissed |
| **Canonical lesson identity** | 3,679 rows / 3,240 keys, unresolved | **3,679 rows · 3,240 keys · 29 true duplicates · 410 key collisions · 3,650 canonical** |
| Composition CI | 0 conflicts · 623 Py · 1061 Dart | **0 conflicts · 748 Py · 1084 Dart · analyze clean** |

---

## NEXT BOTTLENECK — **ONE, AND IT IS NOT ENGINEERING**

**The trust decision.** `SOURCE TRUST 0/97`, `eligible for teaching 0`, `PEDAGOGY REALITY 7/17` and
the servable structured-content carrier are **all** blocked on a **production trust threshold**,
which is a Founder gate. *The pipeline can now detect, account, recognise, repair, validate and
carry — and it may not serve.*

The cheapest engineering win beside it: **118 blocks withheld solely because the app has no matching
type** (`footnote` 64 · `activity` 50 · `option` 4) — **a model gap, not a data gap.** The 4
`option` blocks are exactly defect #8 from the 97-row audit: a **mutilated multiple-choice set**,
where withholding is *not* the safe move.

## NEXT ROUND NORTH STAR

**Round 7 — TRUSTED CONTENT REACHES THE LEARNER, under a Founder-set threshold.** Target:
`eligible for teaching > 0` **with a stated, measured false-trust rate on a blind holdout**.
Dependency: **a Founder decision on the threshold. Nothing else.** Stop condition: measured false
trust above the chosen bound ⇒ **report the truthful zero again**.

---

## MERGE RECOMMENDATION

**Merge #79. Close #73 as subsumed. Hold #80–#88 and #89–#93.** Unchanged from round 6's Part II
audit, and the reasoning is checkable: #73 is a strict **ancestor** of #79, `main` is an ancestor of
both, and the whole delta #73 → #79 is **16 commits touching 3 files, all documentation**. So
merging #79 carries exactly the code risk of #73 — **already Founder-ACCEPTED** — plus a report, and
ships **none** of round 5's or round 6's unreviewed code.

**It delivers nothing to a child:** packs are gitignored build artefacts, so **merging #79 changes
no APK.**

**Holding is not neutral.** Round 6's base is a synthetic composition of nine round-5 branches;
round 7 would compose a composition. **This archive endorses the audit and does not act on it.**

## FOUNDER DECISIONS REQUIRED

| # | Decision | Why it blocks |
|---|---|---|
| **1** | **Set a production trust threshold.** | The single gate behind Gate D, Source Trust, Pedagogy Reality and servable structured content. **No amount of further engineering moves any of them.** |
| **2** | **Canonical lesson identity — four rulings.** (a) adopt `CanonicalLessonIdentity` as distinct from `SourceLessonRecord`? (b) the **291 unanchored** identities? (c) the **63 TOC-less books** — in or out? (d) does `Chuyên đề` count? | `3,650` is a **MEASUREMENT, not a decision**. `3,679` stays **HISTORICAL BASELINE ONLY** until these are answered. |
| **3** | **Merge debt** — merge #79, close #73? | Round 7's base would otherwise compose a composition. |
| **4** | **The 118-block model gap** — add `footnote` / `activity` / `option` block types? | Changes what a child reads; needs a wording decision before code. |
| **5** | **G1 — the 17 gaps have no page crops.** Re-run WS-C's bridge with crops? | The device walk's **one FAIL**. Data exists; 20 crops were buildable from the same TSL. |
| **6** | **Round 7 scope** — accept the proposal in §13 of the consolidated report? | |

---

### How to read this archive

`01`–`05` are the record: objective, plan vs actual, work, failures, metrics. `06`–`09` are the
reality: what reached a child, the test/CI/PR evidence, the device walk, the architecture and data
changes. `10`–`14` look forward: risks, the acceptance card, round 7, the roadmap, tracker status.
`15` is the file manifest with a SHA-256 per file.

**Claim labels:** **PROVEN** = re-verified first-hand by the archive builder (a command, a
recomputed hash, an API read, a parsed artefact) · **MEASURED** = an instrument's number recorded in
a committed report the coordinator verified · **OBSERVED** = seen on a real device or a page render
· **INFERRED** · **HYPOTHESIS** · **UNKNOWN / NOT CAPTURED / UNAVAILABLE** = the evidence does not
exist, and saying so is the correct answer.
