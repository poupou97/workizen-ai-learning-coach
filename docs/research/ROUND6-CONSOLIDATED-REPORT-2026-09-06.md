# ROUND 6 — VERIFIED ACCURACY → REAL PRODUCT
## Consolidated Founder report — 2026-09-06

> **North Star: MAKE VERIFIED ACCURACY REACH THE LEARNER.**
>
> **Nothing is merged.** Every number here was verified by the coordinator against the
> repository, an artefact on disk, a page render, or by running the suites — not relayed
> from a workstream's summary. Where a workstream's wording or my own was wrong, the
> correction is stated in place.

---

## 0 · The one-paragraph answer

Verified accuracy **reached the learner**, and the first thing it did was **take
something away**. A real History lesson replaced 23 `[MẪU]` placeholder blocks with
**34 real SGK blocks** — and its seven-event timeline and seven-step tutor script
**vanished**, because the block carrying them is honestly withheld. Forty-one fabricated
Toán expressions stopped shipping, so the app now offers **zero** Toán exercises: a
truthful zero. Silent loss went to **zero** across every population measured, recognition
recovered a defect round 5 said was unreachable, and one `ValidatedRepair` crossed into
the production-shaped pipeline **without becoming trusted**. `eligible for teaching`
remains **0**, and it cannot be otherwise: no production trust threshold exists, and that
is a Founder gate no workstream may touch. **This round bought honesty, and paid for it
in visible content.**

---

## 1 · Acceptance gates — fixed before the round, graded after

| Gate | Requirement | Verdict |
|---|---|---|
| **A · ACCOUNTING** | Zero unexplained silent loss on Golden + holdout | **PASS** |
| **B · RECOGNITION** | ≥1 previously unrecoverable OCR failure class materially improves at recognition level | **PASS** |
| **C · REPAIR** | A `ValidatedRepair` crosses the production-shaped pipeline | **PASS** |
| **D · TEACHING** | ≥1 real lesson honestly eligible for teaching, target >0 | **TRUTHFUL ZERO — blocked on a Founder decision, not on engineering** |
| **E · DEVICE** | ≥1 Golden lesson on a real device consuming validated/repaired real data | **PASS** |

**4 PASS · 1 TRUTHFUL ZERO.**

**On Gate D, stated plainly.** `eligible for teaching` cannot exceed 0 because **no
production trust threshold has been set**, and setting one is a Founder gate. This is not
an engineering failure and no amount of further work moves it. The Founder wrote *«a
truthful zero is acceptable if evidence demands it»* — this is that zero. The round did
not lower a single trust or safety gate to avoid it.

---

## 2 · Plan vs Actual

### WS-A · TRUTH ACCOUNTING — PR #91, CI green

| Item | Status |
|---|---|
| Reproduce round-5 numbers (0.632→0.589, 0.613→0.523, Bài 61 0.211→0.078) | **DONE** — exact, from a second independent construction |
| R13 conservation invariant as a HARD FAILURE | **DONE** — `ledger.py audit` exits non-zero |
| What disappeared and why, per class with counts | **DONE** — all 82 regions, six classes |
| Repair root causes without mass over-withhold | **DONE** — served set byte-identical everywhere |
| Recalculate round-5 metrics, history preserved | **DONE** — marked `HISTORICAL CORRECTION TO ROUND 5` |
| A2 canonical lesson identity | **DONE** |

### WS-B · RECOGNITION — PR #92, CI green

| Item | Status |
|---|---|
| Failure census, forms before rules | **DONE** — 531 books / 62,729 pages / 2,398,513 lines |
| Bounded candidate evaluation | **DONE** — targeted re-crop adopted; CodeFormulaV2 measured and **rejected** |
| Six metrics reported separately | **DONE** |
| 274/336 fraction population | **DONE** — and the framing falsified |

### WS-C · REPAIR → PRODUCT — PR #90, CI green (stacked on WS-A)

| Item | Status |
|---|---|
| `ValidatedRepair` type bridging round-5 model + E1 grounding | **DONE** |
| TSL join making a validated repair visible | **DONE** |
| Bridge carries it, cannot serve it | **DONE** |
| App parses it, cannot serve it | **DONE** |
| GOLDEN #1 artefact on disk | **DONE** |
| Carrier for structured content | **PARTIAL** — `no_carrier:formula` replaces the false `unknown_role:formula`; a **servable** structured kind is **DEFERRED** (needs rendering + a Founder trust decision) |
| Per-block failure mode | **DONE, scoped** — version skew only; integrity violations still reject the document |
| Rich text | **ACCEPTED AS IS** — nothing added; the page crop is the honest path |

### WS-D · GOLDEN DELIVERY — PR #93, CI green

| Item | Status |
|---|---|
| Workspace **Option B** implemented, flag removed | **DONE** |
| One word set for three views | **DONE** — no `lib/core` change needed |
| GOLDEN #1 → `assets/fixtures/real/` | **DONE** — lineage PASS under `--require-repair` |
| GATE E on a real Nokia 6.1 | **DONE** — 7 frames, 8 PASS / 1 honest FAIL |
| Golden #2 Toán Bài 61 | **DEFERRED** — reassigned by the Founder to WS-A/WS-B |
| Bài 17 regression | **DONE** — L2 PASS (not stale); L4 UNKNOWN (no repair in it) |
| Five-field lineage gate | **DONE** — 16 unit tests |
| Visual grammar forms census | **DONE** — 238 lessons |
| Visual grammar bounded POC | **NOT STARTED** — *the census says do not build one yet* |

**Nothing was promoted from PARTIAL to DONE.**

---

## 3 · PROVEN

- **Silent loss is zero.** 29 ledgers / 1,878 regions: **138 unaccounted → 0**, enforced by a check that exits non-zero. Evaluation set, holdout, both Golden slices, and five lessons nobody selected.
- **The served set is byte-identical before and after, in every population.** No guard weakened, no coverage bought. This was the claim most likely to fail and it did not.
- **Root cause of R13 is rule order, not a missing rule.** The letterless test in `assign_role` ran second, before any rule that could name the region — swallowing **17 of 18** Docling FORMULA regions (`role=='formula'` occurred once in 1,655 blocks) and every numeric label inside a picture. One mechanism explains R13, A2's `empty_block` finding, and the `7 8 2 8 7 - 2 8 5 8` misdescription.
- **Recognition reached a defect nothing else could.** `b) 3/10 + 5/21`, whose numerator `3` is absent from the whole-page OCR entirely, is now read correctly from a targeted re-crop. GOLDEN #2 Bài 61: **17 of 47** unreadable fraction regions recovered, **17/17 correct**, **0 disagreements on 38 controls**. No dependency added; ~0.46 s/region; same Apple Vision engine that ships on iOS.
- **A `ValidatedRepair` crossed the pipeline without becoming trusted.** 9 validated, 6 crossed as withheld regions, **`trusted: 0`**, violations 0. `p039:000` — the block with all seven dated events — is present, withheld, **carries no `text` field**, disposition `VALIDATED_REPAIR`, method `lanec.tone-corroboration-v1` with `changed=false`. Lineage provable hash by hash. **No lesson identity named anywhere.**
- **Capping demonstrated, not asserted.** A second artefact (KHTN 7 Bài 20) where the laboratory said TRUSTED and what crossed was `VALIDATED_REPAIR` + `trust_gate:founder_decision_absent`.
- **The lineage gate caught a stale artefact on its first real use.** WS-C re-ran at 11:08; the 11:01 copy no longer hashed to what it claimed. Round 5's trap, caught by machine.

---

## 4 · FALSIFIED — including three of my own statements

- **«The lost blocks are the printed exercises» — my words to the Founder, only partly right.** Of 82: 31 symbol fragments, 20 numeric labels, 13 unreadable FORMULA regions, 18 whole or stacked expressions.
- **Round 5's *corrected* served shares are not the truth either — they are a LOWER BOUND.** They put every lost region in the learning denominator; **50 of 82 were defined non-learning**. Round 5 was wrong in **two opposite directions**: as-reported too high, corrected too low. Accounted: batch 2 **0.617**, holdout **0.571**, Bài 61 **0.154**.
- **«274 = the OCR never read the digit» is two failures, not one.** **DIGIT LOSS 312 (57 %)** vs **SEGMENTATION 196 (36 %)** — a third of that population *was* recognised and glued into another token. Block-level, «did not read the digit» falls **281 → 234 (−16.7 %)**.
- **Scale is not the lever; segmentation is.** Every SGK page is a **100 ppi scan**, so scale 20 is interpolation, not information. Recovery is **not monotonic in scale** — scale 12 misses the `3` that scales 6 and 20 read. What a crop changes is context, framing and Vision's own segmentation.
- **Ω is unreachable by this lever: 0 of 22, at every scale.** A crop recovers a character the engine *could* read but did not isolate; it recovers nothing when the glyph is not in its repertoire.
- **A recovered digit does not become a repaired block** (10 → 10, Δ = 0). The recogniser *adds* an observation where the destroyed one must be *superseded*.
- **More scales are not free.** DEV said the 8-scale ladder's extra recall cost nothing; the **holdout said false recognition 0.049 → 0.083**. Four scales stays.
- **CodeFormulaV2 rejected on measurement**: 87.2 s/region vs 0.46 s, 4/7 correct, reads `7` as `T`/`E`/`F`.
- **WS-C falsified its own first design.** Its projection initially kept a block served when the ledger ruled `WITHHELD`/`SUSPECT`/`CONFLICT` — overriding a fail-closed ruling to protect coverage, the mirror of «never weaken a guard». Default is now `withhold`.
- **WS-B falsified two of its own census rules** by probing, not review: ohm 586 → 22 candidates; subscript precision 5/16; the unigram diacritic rule produced 26,703 «candidates» that are ordinary Vietnamese words.
- **Two of WS-B's holdouts returned ~0** because they measured the wrong population. Reported in full, not replaced.

---

## 5 · STILL HYPOTHESIS

- That the R13 fix generalises past the 29 lesson ledgers / 1,878 regions measured. **Not run over the whole corpus.**
- That targeted re-crop generalises past the measured slices — holdout digit recall was **0.181** against DEV's 0.500, so the honest expectation is *much* lower than the development figure.
- That `3,650` is the right canonical denominator. It is a **measurement**, not an approved denominator.

---

## 6 · Canonical lesson identity — the Founder's open question, answered

**The answer to «3,679 or 3,240?» is: neither.** I reproduced every figure independently by joining `all-lessons.csv` against `curriculum-structure.json`.

| Measure | Value |
|---|---|
| SOURCE ROWS | **3,679** |
| DISTINCT CURRENT KEYS `(book, lessonNo)` | **3,240** |
| TRUE DUPLICATES | 29 |
| KEY COLLISIONS | 410 |
| SOURCE VARIANTS | 0 |
| **CANONICAL LESSON COUNT** `(sourceDocumentId, lessonNo, pageStart, title)` | **3,650** — 3,359 page-anchored, 291 unanchored |

- **3,240 is wrong in the direction nobody was watching: it deletes 410 real lessons.** «Bài 1» is printed seven times in one GDTC book, once per chủ đề. I had implicitly treated 3,240 as the plausible true number; **it is the more dangerous one.**
- **3,679 is wrong by 29.**
- **63 of 301 SGK books contribute zero rows** (`NO_TOC`) — only 238 books are present, so **3,679 was never «all SGK lessons».**
- **3,381 ranged = exactly the rows in 3,679 that carry a `pageStart`.** The Founder's two denominators agree precisely; there was never a contradiction between them.

**`3,650` is a MEASUREMENT. `3,679` remains HISTORICAL BASELINE ONLY** pending four Founder rulings listed in `TRUTH-ACCOUNTING-ROUND6.md`.

---

## 7 · PRODUCT REALITY

### What can a CHILD use now that they could not before this round?

1. **A real History lesson.** LS&ĐL 5 Bài 8 replaces **23 `[MẪU]` placeholder blocks with 34 real SGK blocks**, plus 17 reasoned gaps. **But the seven-event timeline and the seven-step tutor script are gone**, because the block carrying them is honestly withheld. **A trade, not a pure win — and the child is the one who pays it.**
2. **A less cramped lesson screen.** Pinned chrome **411 dp → 281 dp**, now **identical across all three views**; 225 dp when dismissed; view labels **7 → 4**; first visual content 384 → 289/233 dp.
3. **Forty-one fabricated Toán expressions are gone.** The app ships **zero** Toán exercises — a truthful zero, and the first APK built on this machine to carry round 5's fix.

### PARENT · **NOTHING NEW.**
### SAM · **NOTHING NEW.**
### INTERNAL / RESEARCH ONLY
The recognition harness, the conservation ledger, the repair projection, the lineage gate, the forms census, the archive tooling. **Tests, tools and prototypes are not learner delivery.**

---

## 8 · Reality Scoreboard — never averaged

| Dimension | Round 5 | Round 6 |
|---|---|---|
| **SOURCE REALITY** | 97 | **97** |
| **SOURCE TRUST** | 0 / 97 | **0 / 97** — no trust threshold set (Founder gate) |
| **RECOGNITION REALITY** | not measured | **17/47 recovered on Bài 61, 17/17 correct; holdout digit recall 0.181; false recognition 0.049** |
| **REPAIR REALITY** | laboratory only, 0 connected | **9 validated · 6 crossed · 0 trusted · 0 violations** |
| **PEDAGOGY REALITY** | 7 / 17 | **7 / 17** |
| **EVIDENCE REALITY** | 0 of 0 | **0 of 0** |
| **PRODUCT DELIVERY REALITY** | 0 real lessons | **1 real lesson on a real device — minus its timeline** |

---

## 9 · Regressions, and metrics discovered wrong

- **Withheld counts rise** (135→144, 124→147, 30→37). Regions that were always refused are now **visible**. **Over-withhold rates before and after are not comparable without saying so.**
- **The child loses the timeline.** Seven events → none, on the flagship research slice.
- **`thresholds/gate.py` `ALL_GUARDS` was missing `formula_unvalidated`** — added; material now that 18 blocks reach role `formula`.
- **`rederive_trust` does not pass `formula_structured`** — pre-existing, fail-closed, **not changed**, recorded.
- **Engine defect, fixed forward with a marked correction:** `engine.run_block` wrote the dispose row's `validation` as a merge over *every* candidate rather than the winner. **12 of 317 round-5 rows (0.0379)** read `rejected` where the ruling was `validated`; **0 of 305** in Lane A1's ledgers. **No published round-5 metric changes.**
- **HISTORICAL CORRECTION TO ROUND 5** — round 5's corrected served shares are a lower bound (§4). Round 5's report stands exactly as published; the correction sits beside it.
- **§16 of the round-5 order was never committed.** The retrospective archive had to grade against RECONSTRUCTED criteria. Now committed as `ROUND5-ACCEPTANCE-CRITERIA.md`, and the settled tally is **8 PASS · 1 PARTIAL · 1 FAIL** — my earlier summary of «7 · 1 · 2» contradicted my own table and was wrong.

---

## 10 · The systemic finding of the round

**Three tests, at three layers, all encoded expectations formed when synthetic data supplied content that real, honestly-withheld data does not.**

- `lesson_index_test.dart` — packs vs the case map (stale packs)
- `timeline_history_test.dart` — «7 mốc» from the real fixture
- `no_machine_ids_test.dart` — «the research slice opens into a timeline»

**Every one of them passes or skips on a clean clone.** Only a **composed tree with real assets present** surfaces them. The suite carries the synthetic era's optimism at multiple layers, and individual per-PR CI is structurally blind to it.

Each was corrected by **fixing the premise, never loosening the gate**, and mutation-checked: serving `p039:000` as a paragraph → RED; re-introducing a `TimelineSemantic` → RED. They are now guards on the honesty property itself — **if a timeline reappears without a Founder trust decision, they go red.**

---

## 10.1 · Composition CI — the round composes

Verified in a throw-away worktree from `integration/round6-2026-09-06` with all five
branches merged and the **real gitignored assets synced in** (packs + fixtures), so a
missing asset could not be mistaken for a defect and — more importantly — so the stale
premises of §10 could not hide.

| Check | Result |
|---|---|
| Git merge, 5 branches | **0 conflicts** |
| `flutter analyze` | **No issues found** |
| Python suite | **748 tests OK** (23 skipped) |
| Dart suite | **1084 tests — All tests passed** |

Heads: WS-A `02e28dc` · WS-C `4193c50` · WS-B `371b6b0` · WS-D `eeb38c1` · archive `73a5321`.

**It did not compose on the first attempt**, and both failures were worth having.

1. **A conflict that was the downstream cost of a shared-checkout collision.** WS-C's
   branch carried WS-A's `47247dd` while WS-A had rebased the same change as `24f6136`;
   `git patch-id` proved them **byte-identical with different SHAs**, so git could not
   dedupe. I confirmed none of WS-C's own commits touched either file, so WS-A's newer
   version won and nothing was lost. WS-C then rebased onto WS-A's branch, dropping both
   borrowed commits — PR #90 is now a declared **stacked PR** rather than a 17-commit
   mixed chain.
2. **The three stale premises of §10**, each corrected by fixing the premise and
   mutation-checked.

**A correction WS-D made to its own first fix, which is the sharper lesson.** Its initial
rewrite asserted an *equivalence*: the timeline appears **iff** the document carries a
`TimelineSemantic`. That is satisfied by the app faithfully drawing whatever the data
says — injecting a `TimelineSemantic` made a timeline appear **and the test stayed
green**. The property that matters is not «does this lesson have events» but **«has
anyone been granted trust»**. The rule now reads the **published artefact**
(`disposition` + `servable != true`), not the parsed model, and fires at the data layer
before the widget tree. Both mutations now kill it; removing the fixture still walks the
synthetic route green.

WS-D also **tried a canary and rejected it**: a keyword leak check on «Bạch Đằng» /
«Ngô Quyền» / «938» gave a **false red**, because those words legitimately appear in the
served lesson-objectives block. *A canary that fires on real book text guards nothing and
teaches the next reader that red is normal.* Replaced with a structural count — the
number of `WithheldBlock`s the app builds must equal the number the artefact declares.

**Recommendation stands: the composition check is standing procedure.** Five green CI
badges did not mean the round worked. Running them together, with real assets, is what
found out — for the second round running.

---

## 11 · Merge debt

**Recommendation unchanged: MERGE #79.** #73 is a strict ancestor of #79; `main` is an ancestor of both; the entire delta #73 → #79 is **16 commits touching 3 files, all documentation**. So merging #79 carries exactly the code risk of #73 — already Founder-ACCEPTED — plus a report, and ships **none** of round 5's unreviewed lane code. Close #73 as subsumed. Hold #80–#88. Full analysis in `ROUND6-MERGE-DEBT-AUDIT.md`.

**The cost of holding is now visible in round 6:** this round's base is a synthetic composition of nine round-5 branches, and round 7 would compose a composition.

---

## 12 · Next bottleneck — ONE

**The trust decision, not engineering.** Every remaining gate is now blocked on the same thing: `SOURCE TRUST 0/97`, `eligible for teaching 0`, `PEDAGOGY REALITY 7/17` and the servable structured-content carrier all wait on a **production trust threshold**, which is a Founder gate. The pipeline can now detect, account, recognise, repair, validate and carry — and it may not *serve*.

The cheapest engineering win beside it is **118 blocks withheld solely because the app has no matching type** (`footnote` 64 · `activity` 50 · `option` 4) — **a model gap, not a data gap.**

---

## 13 · Round 7 — proposed

**NORTH STAR: TRUSTED CONTENT REACHES THE LEARNER — under a Founder-set threshold.**

| | |
|---|---|
| **WHY NOW** | Round 6 proved the whole chain end to end and stopped at the one gate no lane may open. |
| **PROBLEM** | Validated content is visible and countable but unservable; `trusted = 0` by construction. |
| **OBJECTIVE** | A Founder-set threshold, applied to the Golden slices, with false-trust measured against it. |
| **MEASURABLE TARGET** | `eligible for teaching > 0` with a **stated, measured false-trust rate** on a blind holdout. |
| **DELIVERABLE** | Threshold policy + the trust gate wired + a blind audit of everything it admits. |
| **DEPENDENCIES** | **Founder decision on the threshold. Nothing else.** |
| **RISKS** | Setting it to reach a number rather than to reflect evidence. Mitigation: the threshold is chosen from A3's round-5 trade-off curve **before** seeing which lessons it admits. |
| **STOP CONDITION** | Measured false trust above the chosen bound ⇒ report the truthful zero again. |
| **FOUNDER GATE** | The threshold itself. |

Secondary, non-competing: **the 118-block model gap** (cheapest win); **canonical identity ruling** (four questions pending); **recognition generalisation** beyond the measured slices.

---

## 14 · Remaining roadmap — forecast, not promise

| Round | Status | Theme | North Star | Exit condition |
|---|---|---|---|---|
| 6 | **DONE** | Delivery + Recognition | Verified accuracy reaches the learner | 4 PASS · 1 truthful zero |
| 7 | **PROPOSED** | Trust threshold | Trusted content reaches the learner | `eligible > 0` with measured false trust |
| 8 | **PROPOSED** | Scale the validated pipeline | Beyond Golden slices | Generalisation proven on a holdout |
| 9 | **TBD** | Semantic / visual generalisation | One grammar, many lessons | Census-justified renderer families |
| 10 | **TBD** | Pedagogy / evidence breadth | Learning that is measured | Based on the measured bottleneck |

## 15 · Major product gates

| Gate | Status |
|---|---|
| SOURCE ACCURACY | **PARTIAL** |
| RECOGNITION | **POC** |
| TRUSTED CORPUS | **RESEARCH** — blocked on the threshold |
| STRUCTURED LEARNING CONTENT | **PARTIAL** — carried, not servable |
| SEMANTIC GENERALIZATION | **RESEARCH** |
| VISUAL LEARNING | **POC** — 2 of 4 families have zero real data |
| PEDAGOGY | **RESEARCH** |
| EVIDENCE | **RESEARCH** |
| DEVICE UX | **PRODUCT-INTEGRATED** |
| PRIVACY | **PARTIAL** |
| LICENSING | **NOT STARTED** — SGK verbatim remains INTERNAL/RESEARCH ONLY |
| PERFORMANCE · RELEASE QUALITY | **NOT STARTED** |

---

## 16 · Pull requests — all open, none merged

| PR | Branch | CI |
|---|---|---|
| #89 | `ws-archive/round5-retrospective` | PASS |
| #90 | `ws-c/round6-repair-integration` (stacked on WS-A) | PASS |
| #91 | `ws-a/round6-accounting` | PASS |
| #92 | `ws-b/round6-recognition` | PASS |
| #93 | `ws-d/round6-golden-delivery` | PASS |

Plus round 5's #79–#88 and round 4's #73, all still open.

**DO NOT MERGE. READY FOR FOUNDER REVIEW.**
