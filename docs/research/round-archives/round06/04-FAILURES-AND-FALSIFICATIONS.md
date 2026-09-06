# 04 · FAILURES AND FALSIFICATIONS

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.** SGK fragments below are quoted for defect
> attribution and are internal research material under Founder rule D4.

Round 6 met four of five gates. **What it disproved is still the more useful half — and this round
it includes three statements the coordinator had already made to the Founder.**

---

## 1. THE SYSTEMIC FINDING — three tests, three layers, one failure mode

**Status: FOUND AND FIXED. Label: MEASURED, mutation-checked.**

| test | layer | the premise, and when it formed |
|---|---|---|
| `lesson_index_test.dart` | **packs** | formed when the packs still carried 41 INFERRED expressions |
| `timeline_history_test.dart` | **`lib/core`** | formed when seven timeline events came from an older build |
| `no_machine_ids_test.dart` | **UI** | formed when seven events came from the `[MẪU]` fixture |

> **Every one of them passes or skips on a clean clone. Only a composed tree with real assets
> present surfaces them.**

**The failure mode deserves a name:** *synthetic data supplied content that real,
honestly-withheld data does not, and a test froze that content into an expectation.* The suite
carries the synthetic era's optimism at multiple layers, and **individual per-PR CI is structurally
blind to it.**

Each was corrected by **fixing the premise, never loosening the gate**, and mutation-checked:
serving `p039:000` as a paragraph → **RED**; re-introducing a `TimelineSemantic` → **RED**; removing
the real fixture → **GREEN** (the synthetic route still walks). They are now guards on the honesty
property itself: **if a timeline reappears without a Founder trust decision, they go red.**

### 1.1 WS-D's correction to its own first fix — the sharper lesson

Its initial rewrite asserted an **equivalence**: the timeline appears **iff** the document carries a
`TimelineSemantic`. That is satisfied by the app **faithfully drawing whatever the data says** —
**injecting a `TimelineSemantic` made a timeline appear and the test stayed green.**

> The property that matters is not «does this lesson have events» but **«has anyone been granted
> trust».**

The rule now reads the **published artefact** (`disposition` + `servable != true`), not the parsed
model, and fires **at the data layer before the widget tree**. Both mutations now kill it.

### 1.2 A canary tried and rejected — recorded so nobody rebuilds it

WS-D tried a keyword leak check on «Bạch Đằng» / «Ngô Quyền» / «938». It gave a **false red** —
those words legitimately appear in the served lesson-objectives block («ví dụ: 179 TCN, 40, 248,
542, 938,…»).

> *A canary that fires on real book text guards nothing and teaches the next reader that red is
> normal.*

Replaced with a **structural count**: the number of `WithheldBlock`s the app builds must equal the
number the artefact declares — no region may quietly become text.

---

## 2. THREE OF THE COORDINATOR'S OWN STATEMENTS TO THE FOUNDER, FALSIFIED

**Status: FALSIFIED. Label: MEASURED. Recorded in the open, per round 5's own doctrine.**

### 2.1 «The lost blocks are the printed exercises» — only partly right

Of the 82 lost regions: **31** symbol fragments · **20** numeric labels · **13** unreadable FORMULA
regions · **18** whole or stacked expressions. The exercises are the *most important* share, not the
*whole* of it.

### 2.2 Round 5's *corrected* served shares are a LOWER BOUND, not the truth

Round 5 was wrong **in two opposite directions at once**:

- its **as-reported** share `trusted / (trusted + withheld)` was **too high**, because the base had
  already dropped content;
- its **corrected** share was **too low**, because it put **every** lost region into the learning
  denominator — and **50 of the 82 were defined non-learning** (figure text, a running head).

| | R5 reported | R5 corrected | **R6 accounted** |
|---|---:|---:|---:|
| batch 2 (evaluation set) | 0.632 | 0.589 | **0.617** |
| batch 1 (**holdout**) | 0.613 | 0.523 | **0.571** |
| Toán 4 tập hai Bài 61 | 0.211 | 0.078 | **0.154** |
| Toán 4 tập một Bài 37 | 0.489 | 0.371 | **0.434** |
| Toán 5 tập một Bài 6 | 0.480 | 0.353 | **0.364** |
| LS&ĐL 4 Bài 12 | 0.522 | 0.444 | **0.522** |
| LS&ĐL 5 Bài 8 (Golden #1) | 0.706 | 0.632 | **0.706** |

On the two LS&ĐL lessons the accounted value **returns to the as-reported number** — because every
lost region there was a figure label. *The as-reported number was right for the wrong reason.*

**Round 5's report stands exactly as published.** The correction sits beside it, marked
`HISTORICAL CORRECTION TO ROUND 5`.

**And three served shares must never be conflated** — the ledger now publishes all three:
`servedShareAsReported` · `servedShareOfLearningRegions` · `servedShareOfAllInputRegions`. The third
is **unchanged by the accounting fix**, as it must be — a reclassification touches neither the
numerator nor the whole population. It moves only under a demotion, *because a demotion really does
remove text from a child.*

### 2.3 «274 = the OCR never read the digit» is two failures, not one

| class | regions | share of the 548 unreadable |
|---|---:|---:|
| **DIGIT LOSS** — no OCR token of any kind over that half | **312** | **0.569** |
| **SEGMENTATION** — a token *is* there, and the digit is glued into it | **196** | **0.358** |
| FRACTION STRUCTURE | 40 | 0.073 |

**A third of that population was recognised and glued elsewhere**, as in `b) 10 +.` where the page
prints `b) 3/10 +`. *One needs a recogniser; the other needs a splitter — cheap, deterministic, no
recogniser at all. Reporting them as one number hid a third of the population.*

Block-level: «did not read the digit» falls **281 → 234 (−16.7 %)**.

---

## 3. THE RECOGNITION LEVER — what it is, and where it stops

**Status: MEASURED, with two clean falsifications.**

### 3.1 «Higher resolution» is the wrong description — FALSIFIED

Every SGK page is a **100 ppi scan embedded in the PDF**. Scale 20 renders 830 × 1090 px from
~58 × 76 source pixels: **interpolation, not information.** `ocr_pdf.swift` says so in its own
comment. What a crop changes is **context** (language correction off), **glyph-to-frame ratio**, and
**segmentation**.

**And recovery is not monotonic in scale** — on the `3/10` region, scale 12 misses the `3` that
scales 6 and 20 both read. *Which is precisely why several scales are asked, and why agreement
between them is evidence rather than ceremony.*

### 3.2 `Ω` is unreachable by this lever — **FALSIFIED, 0 of 22, at every scale**

Apple Vision returns `S2`, `22`, `U`, `Q`, `12`, `0` — never `Ω`. Including the Founder's own line:
`1 MS = 1 000 000 S2` comes back as `U0`, `U0`, `0 0`, nothing.

> **The generalisation, and it is a negative one:** a targeted re-crop recovers a character the
> engine **could** read but did not isolate. It recovers nothing when the glyph is **not in the
> engine's repertoire** for this typeface at this resolution.

Fractions and exponents are the first kind. **Ω is the second, and no amount of scale, cropping or
consensus reaches it.** The standing candidate for that class is an **in-corpus template
recogniser** — the corpus prints thousands of correct Ω glyphs in the same books.

### 3.3 A recovered digit does not become a repaired block — **FALSIFIED, RESTORE 10 → 10, Δ = 0**

Five blocks gained a proposed value and **every one is malformed**:

```
b) 10 +. 3/10          ← 05-sgk-toan-5-tap-mot p022
0) 1 3 8/14 2/7        ← 04-sgk-toan-4-tap-hai p083 (Bài 61)
```

The reason is precise and **not a tuning problem**: `math_line_candidate` assembles a line from
tokens in x-order. The recovered `3/10` is **added**; the destroyed observation `b) 10 +.` — still
carrying the denominator glued to the item letter — **is still there**.

> **Replacing a source observation is not something a recogniser may do.** It is a `RepairCandidate`
> crossing a `Validator` into a `ValidatedRepair` — WS-C's contract. Doing it inside `mathfix` would
> have been a second provenance universe.

One measurement kept from the attempt: with the crop box as the token's box, `numerator_ambiguous`
rose **2 → 27** and `prose_token_in_block` **29 → 44** — an over-wide box reaches into the
neighbouring fraction's strip. **The geometry has to be honest before the reading is usable.**

### 3.4 More scales are not free — the holdout said so when DEV did not

| | 4 scales | 8 scales |
|---|---|---|
| DEV recoveries | 44 | **62 (+41 %)**, control disagreements unchanged |
| Bài 61 | 17/17 correct | **27/27 correct**, 0 control disagreements |
| **HOLDOUT-3 recoveries** | 23 | **27 (+17 %)** |
| **HOLDOUT-3 wrong readings** | **2** | **4** |
| **HOLDOUT-3 FALSE RECOGNITION** | **0.049** | **0.083** |

**DEV and the Golden slice saw no cost. The independent holdout did. The holdout is the number to
trust.** Four scales remains the recommendation; eight is a measured option whose price is known.

**Both extra wrong readings are named forms with fixes that are deliberately NOT built:** a printed
minus inside the numerator strip, dropped (**round 5 already built the check that catches this —
`ink-accounted-v1` — and this lane does not run it; wiring an existing validator is the cheapest fix
available and it is not done**); and an algebraic denominator read as a digit (`3/(x²−x)` → `3/1`).
The second fix is one clause — *a half is read only when the crop holds a number and nothing else* —
and was withheld because **HOLDOUT-3 has now been looked at**, so a rule written from these errors
would owe a fresh holdout, *and inventing that draw at the end of a round is how a holdout stops
meaning anything.*

### 3.5 Two of WS-B's own census rules were mostly false positives

| rule | first version | corrected | what it was actually counting |
|---|---|---|---|
| `ohm-lost-v1` | **586** findings / 101 books | **22** / 11 books | primary-school arithmetic: `52 - 20 = ?`, `520 = 250` — **60 of 60 probed had no ohm on the page** |
| `subscript-flattened-v1` | 6,168 | 6,168 at **precision 5/16** | spreadsheet refs (`B5`), keyboard keys (`F4`), paper sizes (`A0`), language levels (`C1`) — and `√2` read as `V2` |
| unigram diacritic rule | **26,703 forms / 159,444 occurrences** | **FALSIFIED** | its top rows are `qua`/`quá`, `cung`/`cũng`, `nay`/`này` — **ordinary Vietnamese words**. Kept in code and pinned by a test *so nobody re-adopts it by accident* |

**Neither of the first two was found by review.** The ohm rule was found by handing its first 60
findings to the recogniser; the subscript rule by cropping 16 findings and reading the printed page.
**Probing a census is cheap and it is not optional.**

**And a form nobody had named surfaced inside another class's false positives:** on `11-sgv-toan-11`
p74 the page prints `−√2 / 2` and the OCR returns `V2` — **the radical sign read as the letter V**.
**687** such candidates corpus-wide — *an upper bound on the form, not a count of it*, because `V₂`
is a real physics symbol with the same shape in text. **Only the raster can separate them.**

### 3.6 Two holdouts returned ~0 — reported, not replaced

**HOLDOUT-1 (random, all grades): 0 of 66. HOLDOUT-2 (detector-dense, grades ≤6): 1 of 105.** The
contact sheets say **the population was wrong, not the recogniser**: a random Toán page across
grades 2–12 is full of *algebraic* fractions this rule can never read by construction, and regions
that are not fractions at all; **HOLDOUT-2 selected on «≥6 detected bar regions» and therefore drew
grades 1–3, whose dense bar regions are column-arithmetic rules — books that teach no fractions.
Selecting on the detector selected the detector's own errors.**

**All three numbers stand; none replaces another.** And the refusal behaviour holds where the
population is wrong: **95 of 105 UNREAD on HOLDOUT-2, with zero false readings.**

### 3.7 CodeFormulaV2 — run, measured, rejected

| | CodeFormulaV2 | the crop recogniser |
|---|---|---|
| seconds per region | **87.2** (MPS) | **0.46** for twelve observations |
| correct on 7 truth-labelled regions | **4 / 7** | 17/17 on the same page |
| failure mode | reads the digit **7** as `T`, `E`, `F` | refuses (`UNREAD` / `CONFLICT`) |

**~190× the cost of an observation that already works**, and it is a VLM — so even at zero cost its
output could only ever be a `RepairCandidate` behind the same deterministic checks. Licence
**CDLA-Permissive-2.0** (not the GPL-3 that disqualified Marker/Surya). **Kept as a fallback for the
class the crop lever cannot reach.**

---

## 4. WS-C FALSIFIED ITS OWN FIRST DESIGN — the mirror of «never weaken a guard»

**Status: FALSIFIED by its author, then fixed.**

The projection's first draft **kept a served block served when the ledger said
`WITHHELD`/`SUSPECT`/`CONFLICT`**, to avoid changing accounting.

> That is **overriding a fail-closed ruling to protect coverage** — the same sin as guard relaxation,
> from the other side.

The default is now `on_detected_unrepaired='withhold'`: **the ledger is honoured.** It can only
remove text, so it cannot serve anything wrong — but it can withdraw something right, so:

> **FALSE-DEMOTION EXPOSURE is published beside the restores, never folded into them.**
> Golden #1: **2 blocks demoted.** Round-5 prior for the comparable act: **demotion precision
> 0.250** on 4 blocks.

A demotion is applied **only** when the served text still equals the observation the ledger ruled
on; otherwise the join is unverified and nothing is done.

**And a served block carrying a repair is four different things, not one** — conflating them is how
a lane fools itself: `repair_served` (**VIOLATION**) · `restore_served` (**VIOLATION**) ·
`served_unrepaired` (a FINDING: pre-existing false trust) · `join_unverified` (**no claim, no
action**).

---

## 5. THE ENGINE DEFECT — a component reporting something other than what happened

**Status: FIXED FORWARD, with the correction marked.**

`engine.run_block` wrote the dispose row's `validation` as a merge over **every** candidate a block
produced, not the one that **won**. So a block whose disposition is `VALIDATED_REPAIR` could carry,
on the same row, a merged verdict of `rejected`. **A reader taking the verdict at face value
concludes the repair failed.**

| | |
|---|---|
| dispose rows with disposition `VALIDATED_REPAIR`, all 20 round-5 ledgers | **317** |
| …whose recorded verdict was not the winning candidate's ruling | **12 = 0.0379** (3 distinct blocks) |
| direction of every one | `rejected` → `validated` |
| in Lane A1's 19 pipeline ledgers | **0 of 305** — A1 registers one repairer per failure class, so the multi-candidate case never arises |

**No published round-5 metric changes** — the scoreboards read `disposition` and `final_value`,
never the dispose row's `validation`. What changes is **what a reader of a dispose row sees**, which
is exactly what a downstream integrator consumes. `entry_id` is derived from
block/class/disposition/stage/observations/candidate/reasons/prior and **never** from the
validation, so historical ledgers keep their identities and stay joinable.

> **It is the same family as R13's disappearance with no reason code and E2's self-strengthening
> grounding: a component reporting something other than what happened, with no test able to see
> it.**

---

## 6. REGRESSIONS AND COSTS, STATED

- **Withheld counts rise** — 135 → 144, 124 → 147, 30 → 37. Those regions **were always refused**;
  they are now *visible* as refused. **Any over-withhold rate measured after this change has a
  larger base than the same rate measured before it, and the two must not be compared without
  saying so.**
- **The child loses the timeline.** Seven events → none, on the flagship delivery slice.
- **The child loses every Toán exercise.** `toanExercises` → **0** *(PROVEN in the archived packs)*.
- **13 regions now carry three reasons** (`unread:unreadable_region`, `formula_unvalidated`,
  `empty`). The third is a pre-existing agreement-stage code with an unhelpful name — **not renamed
  here** (renaming touches thresholds tooling), recorded as a defect for the agreement layer's next
  owner.
- **`thresholds/gate.py::ALL_GUARDS` was missing `formula_unvalidated`** — harmless while exactly
  one block had role `formula`; **material now that 18 do**. Added.
- **`rederive_trust` does not pass `formula_structured`** to `role_guards` — pre-existing,
  fail-closed (it can only add a withhold), **not changed**, recorded.
- **`repair/run_gold.py::PERMISSION_REASONS`** contains `empty_block` but not the new `unread:*`
  codes. Arguably correct — *a lost arithmetic expression is a fidelity failure, not a permission
  one* — but it is a behaviour change in another workstream's file and was **left for WS-C to
  decide, not edited.**
- **49 regions are now `figure_text`** on Toán pages where a picture region contains pieces of
  printed exercises. Accounted with reasons and evidence, and the content-bearing ones counted
  separately as **a recognition work queue for WS-B — not a licence to serve them.**

---

## 7. THE ROUND DID NOT COMPOSE ON THE FIRST ATTEMPT

**Status: FOUND AND FIXED. Label: MEASURED — found only by composing with real assets.**

**1 · A conflict that was the downstream cost of a shared-checkout collision.** WS-C's branch
carried WS-A's `47247dd` while WS-A had rebased the same change as `24f6136`. **`git patch-id`
proved them byte-identical with different SHAs**, so git could not dedupe. None of WS-C's own
commits touched either file, so WS-A's newer version won and nothing was lost; WS-C then rebased
onto WS-A's branch, dropping both borrowed commits. **PR #90 is now a declared *stacked* PR rather
than a 17-commit mixed chain.**

**2 · The three stale premises of §1**, each corrected by fixing the premise and mutation-checked.

> **Five green CI badges did not mean the round worked. Running them together, with real assets, is
> what found out — for the second round running.** The composition check remains standing procedure.

---

## 8. WHAT IS STILL ONLY HYPOTHESIS

Recorded here so no later round mistakes it for a result:

- **That the R13 fix generalises past the 29 lesson ledgers / 1,878 regions measured.** It has been
  measured on three independent populations, one a holdout, on both a Math and a History/Geography
  loss profile, and on lessons nobody selected. **It has not been run over the whole corpus.**
- **That targeted re-crop generalises past the measured slices.** Holdout digit recall is **0.181**
  against DEV's 0.500 — *the honest expectation is much lower than the development figure.*
- **That `3,650` is the right canonical denominator.** It is a **MEASUREMENT**, not an approved
  denominator.
- That real book text plus honest gaps **teaches better** than a fabricated timeline. Consistent
  with doctrine; **never measured on a child.**
- That Option B is better **for a child** than A or C. Round 5's numbers are density and taps, **not
  learning outcomes.**
- That restoring the page crops (G1) makes the 17 gaps more understandable. Plausible; **not
  measured.**
- That adding three block types unlocks the 118 `unknown_role:*` blocks. **It is measured that they
  are withheld for want of a type**; it is *not* measured what a child would then read.
- That wiring `ink-accounted-v1` into the consensus rule refuses the dropped-minus reading; that
  «a half crop must hold a number and nothing else» refuses both algebraic-denominator readings;
  that a denominator ink-width check refuses `3/(x²−x)`; that an in-corpus template recogniser
  reaches Ω; that WS-B's bigram diacritic candidates are real failures. **None built. None checked
  against the page.**

## 9. UNKNOWN

Whether any lesson elsewhere in the corpus has a region whose role is a **learning** role but which
reaches neither TSL list. The ledger would report it as `dropped_with_role:<role>` and fail;
**none occurred in any population measured.**
