# Round 6 · Workstream A — TRUTH ACCOUNTING

**P0.1 R13 zero silent loss · A2 canonical lesson identity — 2026-09-06**

> **Status: READY FOR FOUNDER REVIEW. Nothing merged.**
> Every number below was produced by a committed tool on real corpus data and can be
> re-run. No LLM was called anywhere in this workstream.
>
> **Round 5's published numbers are not changed by this document.** They stand exactly as
> written in `ROUND5-CONSOLIDATED-REPORT-2026-09-06.md`. Where round 6 measures something
> different, it is written beside them under **HISTORICAL CORRECTION TO ROUND 5**, never
> in place of them.

---

## 0. The one-paragraph answer

Round 5 found that a block whose role is `empty` reached neither `blocks` nor `withheld` of
the Trusted Structured Lesson — a disappearance carrying no reason code, invisible to every
rate in the repository. The cause turns out to be **rule order, not a missing rule**: the
letterless test in `assign_role` ran second, before every rule that could already name such
a region, so it swallowed **17 of the 18** Docling FORMULA regions in the two legacy batches
and every numeric label that sat inside a picture. One mechanism explains R13, Lane A2's
`empty_block` finding and the `7 8 2 8 7 - 2 8 5 8` misdescription together. The fix asks
the pipeline's own existing vocabulary first and records every region that is neither served
nor withheld as `EXCLUDED_WITH_REASON`. **UNACCOUNTED goes 27 → 0 on the evaluation set,
55 → 0 on the holdout and 38 → 0 across the two Golden slices — and in all three the SERVED
SET IS BYTE-IDENTICAL before and after.** No guard was weakened and no coverage was bought.

---

## 1. The invariant, and the check that fails

```
INPUT SOURCE REGIONS
  = SERVED + WITHHELD + EXCLUDED_WITH_REASON + explicitly defined non-learning regions
```

`INPUT SOURCE REGIONS` for a lesson = **every SDM block on the lesson's own boundary pages**.
That is the population round 5's served share and over-withhold rate were both computed
*inside*, after content had already been dropped from it.

Four dispositions and nothing else — `tool/corpus/accounting/dispositions.py`:

| disposition | meaning |
|---|---|
| `SERVED` | reached the child (TSL `blocks[]`) |
| `WITHHELD` | refused, with reasons (TSL `withheld[]`) |
| `EXCLUDED_WITH_REASON` | a *defined* non-learning region, or accounted in a neighbouring lesson's ledger — always with an explicit reason code |
| `UNACCOUNTED` | none of the above ⇒ **HARD FAILURE** |

`tool/corpus/accounting/ledger.py audit` **exits non-zero** when one region is UNACCOUNTED.
Not a warning: round 5's silent loss survived precisely because nothing failed.
`--historical` reports without failing, which is the only way a round-5 artefact is measured
without pretending its numbers changed.

**`EXCLUDED_WITH_REASON` is deliberately not a synonym for `WITHHELD`.** Converting every
lost region into a withheld one would trade a silent loss for a mass over-withhold, and
round 5 already measured over-withholding getting worse (0.400 → 0.633). A page number is a
defined non-learning region. A block of digits is not.

---

## 2. Round 5 reproduced first, from a different construction

Before changing anything, the ledger was run on the round-5 artefacts. It partitions the
whole input population; round 5's `silent_loss.py` scans for role `empty`. The two agree
exactly.

| | round 5 published | round 6 ledger, `--historical` |
|---|---|---|
| batch 2 (evaluation set) | 232 trusted · 135 withheld · **27** silently lost · 0.632 → 0.589 | 232 · 135 · **27** · 0.6322 → 0.5888 |
| batch 1 (**holdout**) | 196 · 124 · **55** · 0.613 → 0.523 | 196 · 124 · **55** · 0.6125 → 0.5227 |
| Toán 4 tập hai Bài 61 | 4 · 15 · **32** · 0.211 → 0.078 | 4 · 15 · **32** · 0.2105 → 0.0784 |

`silent_loss.py` itself was re-run unchanged and reproduces its published output byte for
byte. **Round 5 stays reproducible.**

A determinism control was run first: re-running SDM + TSL on the round-5 artefacts with the
**unchanged** code produces a byte-identical ledger. So every before → after difference
below is caused by the fix and by nothing else.

---

## 3. What disappeared, and why — the census of all 82 lost regions

The single `empty` bucket was hiding six physically different things. Classes are decided by
the block's own text and the OCR lines under its bbox — no thresholds, no guessing at
content.

| class | what it is | batch 2 | batch 1 | total |
|---|---|---:|---:|---:|
| `symbol_fragment` | an operator or rule torn off its expression (`- -`, `=`, `+•`) | 7 | 24 | **31** |
| `numeric_label` | letterless digits, no operator — map/table/diagram figures (`1408`, `1010`, `0,6`) | 9 | 11 | **20** |
| `numeric_expression_inline` | a whole printed arithmetic exercise on one line (`40 613 + 47 519`) | 8 | 7 | **15** |
| `unreadable_region` | **block text empty while OCR lines under it carry printed content** | 3 | 10 | **13** |
| `numeric_expression_stacked` | a stacked/fraction expression flattened from ≥ 3 printed lines (`3 7 + 11 12`) | 0 | 3 | **3** |
| `no_content` | no block text and no OCR line: nothing was lost | 0 | 0 | **0** |
| | | **27** | **55** | **82** |

`unreadable_region` is the class that most changes the reading of round 5. Those 13 regions
are Docling FORMULA blocks whose flat text is empty — and under one of them sit nine OCR
lines reading `9 · 3 · a) · 11 · 11`, the printed exercise `9/11 − 3/11`. They did not lose
nothing. They lost everything, and `empty_block` / "no letters" said the opposite.

**Not a Toán-only effect, and not one root cause.** On LS&ĐL 4 Bài 12 all 8 losses are map
and table figures; on LS&ĐL 5 Bài 8 all 6 are figure text inside a map/table picture region;
on Toán 4 tập hai Bài 61, 25 of 32 are figure text and 7 are FORMULA regions.

### Where each class went after the fix

| before | Docling label | → role | disposition | reason | n |
|---|---|---|---|---|---:|
| `symbol_fragment` | text | `figure_text` | EXCLUDED | `non_learning:figure_text` | 30 |
| `numeric_label` | text / list_item | `figure_text` | EXCLUDED | `non_learning:figure_text` | 16 |
| `unreadable_region` | formula | `formula` | **WITHHELD** | `unread:unreadable_region, formula_unvalidated` | 13 |
| `numeric_expression_inline` | text | `empty` | **WITHHELD** | `unread:numeric_expression_inline` | 12 |
| `numeric_expression_inline` | text / list_item | `figure_text` | EXCLUDED | `non_learning:figure_text` | 3 |
| `numeric_label` | list_item | `empty` | **WITHHELD** | `unread:numeric_label` | 3 |
| `numeric_expression_stacked` | list_item / formula | `empty` / `formula` | **WITHHELD** | `unread:numeric_expression_stacked` / `formula_unvalidated` | 3 |
| `symbol_fragment` | list_item | `empty` | **WITHHELD** | `unread:symbol_fragment` | 1 |
| `numeric_label` | page_footer | `running_head` | EXCLUDED | `non_learning:running_head` | 1 |
| | | | | | **82** |

**50 became `EXCLUDED_WITH_REASON` · 32 became `WITHHELD` with a truthful reason.** That
ratio is the answer to the Founder's constraint: 61 % of the "silent loss" was never
learning content, and turning all of it into withheld regions would have been the easy wrong
answer.

---

## 4. The repair, and why it is safe

**Root cause — `tool/corpus/tc2_sdm.py`, `assign_role`.** The letterless test was the second
rule in the function, before the rules for TABLE, FORMULA, page furniture, figure text and
the printed `?` answer slot. Every letterless region reached `empty` before anything could
name it. Measured consequence across the two batches: **17 of 18 Docling FORMULA regions
never reached the `formula` role at all**, and `role.value == 'formula'` occurred exactly
once in 1 292 blocks.

`letterless_role()` restores the order for letterless text only and asks nothing new. It
uses the pipeline's own existing vocabulary, with the guards that vocabulary already carries:
a `formula` without a validated structure is still withheld (`formula_unvalidated`, Founder
STEM §4). Only when no structural evidence names the region does it stay `empty`, and then
its evidence says which of the six classes it is instead of claiming there was nothing there.

**`tool/corpus/tc2_tsl.py`** no longer `continue`s past a furniture role. That `continue`
*was* the disappearance. Every region that is neither served nor withheld is now recorded in
a new `excluded[]` with `disposition`, `reason`, `bbox` and its role evidence, and each
document states its own `conservation` arithmetic.

**Why this is not a coverage change.** Across all three runs the served set is byte-identical
before and after — 285 blocks (batch 2), 234 (batch 1), 43 (Golden). Zero blocks moved from
served to withheld; zero moved the other way. Nothing was promoted, nothing was demoted, no
threshold was touched.

### Regressions and costs, stated

- **Withheld counts rise**: batch 2 135 → 144, batch 1 124 → 147, Golden 30 → 37. Those 35
  regions were always refused; they are now *visible* as refused. Any over-withhold rate
  measured after this change has a larger base than the same rate measured before it, and the
  two must not be compared without saying so.
- **13 regions carry three reasons** (`unread:unreadable_region`, `formula_unvalidated`,
  `empty`). The third comes from the agreement stage, where a block with no normalisable text
  gets reason `empty` — a pre-existing code whose name is unhelpful. **Not renamed here**
  (it is an agreement guard, not a role guard, and renaming it touches thresholds tooling);
  recorded as a defect for whoever owns the agreement layer next.
- **`tool/corpus/thresholds/gate.py`** listed "every guard the round-4/5 pipeline can raise"
  and was **missing `formula_unvalidated`**. Harmless while exactly one block had role
  `formula`; material now that 18 do. Added, with the new `unread:*` codes.
- **`rederive_trust` does not pass `formula_structured`** to `role_guards`, so a
  post-pass role change would re-guard a structured formula as unvalidated. Pre-existing,
  fail-closed (it can only add a withhold, never remove one), **not changed**, recorded here.
- **`repair/run_gold.py:PERMISSION_REASONS`** (WS-C's file) contains `empty_block` but not
  the new `unread:*` codes, so a region carrying one is no longer "permission only" there.
  That is arguably the correct reading — a lost arithmetic expression is a fidelity failure,
  not a permission one — but it is a behaviour change in another workstream's file and was
  **left for WS-C to decide**, not edited.
- **49 regions are now `figure_text`** on Toán pages where the picture region contains pieces
  of printed exercises. They are accounted, with a reason and their evidence, and the ledger
  counts the content-bearing ones separately (`excludedCarryingAnExpression`: 2 on each
  batch, 3 on Golden) as a **recognition work queue for WS-B — not a licence to serve them.**

---

## 5. GOLDEN SLICES — the Founder's two named slices, before and after

Run from one spec (`tool/corpus/accounting/golden-slices.json`) by one runner, once with the
pre-fix pipeline (`1a75d24`) and once with the fix, so before → after is a controlled
comparison and not two different populations.

### GOLDEN #1 · LS&ĐL 5 Bài 8 — the delivery slice

| | input | SERVED | WITHHELD | EXCLUDED | **UNACCOUNTED** |
|---|---:|---:|---:|---:|---:|
| before (pre-fix) | 84 | 36 | 15 | 27 | **6** |
| after (WS-A fix) | 84 | 36 | 15 | 33 | **0** |
| **composed** (WS-A fix × WS-C demotion) | 84 | **34** | **17** | 33 | **0** |

All six lost regions were figure text inside a map/table picture region. **Zero new withholds
from the accounting fix on the delivery slice.** The History/Geography loss profile is not the
Toán one, exactly as the Founder warned, and the Toán root cause did not have to generalise
for this slice to close.

The composed row is **not** part of the accounting fix — see §5.1.

### GOLDEN #2 · Toán 4 tập hai Bài 61 — round 5's worst case

| | input | SERVED | WITHHELD | EXCLUDED | **UNACCOUNTED** |
|---|---:|---:|---:|---:|---:|
| before | 148 | 4 | 15 | 97 | **32** |
| after | 148 | 4 | 22 | 122 | **0** |

25 were figure text; 7 are Docling FORMULA regions now withheld as `unread:unreadable_region`
/ `formula_unvalidated` — including the block round 5 named, `7 8 2 8 7 - 2 8 5 8`.

`ledger.py audit` exits **1** on the before run and **0** on the after run.

Two-slice totals:

| | input | SERVED | WITHHELD | EXCLUDED | **UNACCOUNTED** | conserves |
|---|---:|---:|---:|---:|---:|---|
| before | 232 | 40 | 30 | 124 | **38** | false |
| after (WS-A fix) | 232 | 40 | 37 | 155 | **0** | true |
| **composed** (× WS-C demotion) | 232 | **38** | **39** | 155 | **0** | **true** |

### 5.1 The demotion is a SECOND, separate movement — reported apart, never folded in

WS-C's repair projection (PR #90) now defaults to `on_detected_unrepaired='withhold'`: when the
repair ledger rules a region `WITHHELD` / `SUSPECT` / `CONFLICT`, the projection honours the
ruling and withdraws the text. On LS&ĐL 5 Bài 8 that demotes **2 regions from SERVED to
WITHHELD** — including `p041:002`, the attribution whose repair candidate two independent
signals rejected, which was previously served silently.

Two different things moved a served share this round and they must not be added together:

| movement | what it did | effect on Golden #1 |
|---|---|---|
| **WS-A rule-order fix** | reclassified regions that were **never accounted for** | served **unchanged** (36 → 36); UNACCOUNTED 6 → 0 |
| **WS-C ledger-honouring demotion** | withdrew regions that **were** served | served 36 → 34; withheld 15 → 17 |

The ledger keeps them apart in code: `--demotions` applies a downstream stage's withdrawals and
reports `demotedDownstream` as its own figure, joined on `(book, page, native block index)`
because WS-C's generation is `tc2-p1` / `sdm-v3` and this ledger's is `tc2-p3`.

**Conservation across the demotion, verified rather than assumed.** WS-C's artefact and this
workstream's are two different generations of the same lesson, so the check is whether the
learning population survived the move:

- WS-C: 34 served + 17 withheld = **51 learning regions**
- WS-A: 36 served + 15 withheld = **51 learning regions**
- the two `(page, native index)` sets are **identical**
- exactly **2** regions moved SERVED → WITHHELD; **0** moved the other way
- composed ledger: `conserves: true`, `unaccounted: 0`, `demotedDownstream: 2`

This is the round-5 rule A4 established, working in both directions: `false_correction_rate` is
blind to a detector, so a workstream that raises detection must publish **false demotion**
beside it. WS-C publishes its false-demotion exposure (Golden #1: 2 blocks, against round 5's
prior of demotion precision 0.250 on 4). This workstream's half is the invariant: **a demotion
must not lose a region.** It did not.

---

## 6. HISTORICAL CORRECTION TO ROUND 5

> Round 5's published figures are unchanged and stay reproducible. What follows is what the
> same lessons measure once every region carries a disposition.

**Round 5 was wrong in two opposite directions at once, for two different reasons.**

- Its **as-reported** served share `trusted / (trusted + withheld)` was too high, because the
  base had already dropped content.
- Its **corrected** served share `trusted / (trusted + withheld + silently lost)` was too
  low, because it put **every** lost region into the learning denominator — and 50 of the 82
  turned out to be defined non-learning regions (figure text, a running head) that were never
  learning content on any reading.

So round 5's corrected column is a **LOWER BOUND**, not the answer. The accounted value sits
between the two.

| | R5 reported | R5 corrected | **R6 accounted** |
|---|---:|---:|---:|
| batch 2 (evaluation set) | 0.632 | 0.589 | **0.617** |
| batch 1 (**holdout**) | 0.613 | 0.523 | **0.571** |
| Toán 4 tập hai Bài 61 | 0.211 | 0.078 | **0.154** |
| Toán 4 tập một Bài 37 | 0.489 | 0.371 | **0.434** |
| Toán 5 tập một Bài 6 | 0.480 | 0.353 | **0.364** |
| LS&ĐL 4 Bài 12 | 0.522 | 0.444 | **0.522** |
| LS&ĐL 5 Bài 8 (Golden #1) | 0.706 | 0.632 | **0.706** |

For Golden #1 the composed served share, **after** WS-C's two demotions, is **0.667** (34 / 51).
That fall is WS-C's fail-closed ruling reaching the served set — a separate movement from the
accounting fix, and it is reported in §5.1 rather than mixed into this column.

`R6 accounted` = `SERVED / (SERVED + WITHHELD)` computed **after** conservation holds, so its
denominator is the learning population with nothing missing from it. On LS&ĐL 4 Bài 12 and
LS&ĐL 5 Bài 8 it returns to the as-reported value, because on those lessons every lost region
was a figure label — the as-reported number was right for the wrong reason.

### Three served shares, and they must never be conflated

The ledger publishes all three, on the Golden slices:

| rate | before | after | reading |
|---|---:|---:|---|
| `servedShareAsReported` | 0.5714 | 0.5195 | of the regions the pipeline **classified**, what share did it serve? |
| `servedShareOfLearningRegions` | 0.3704 | 0.5195 | of the regions that are learning content, what share reached a child? |
| `servedShareOfAllInputRegions` | 0.1724 | 0.1724 | of **everything** extracted from the page, what share reached a child? |

`servedShareOfAllInputRegions` is unchanged, as it must be: the numerator and the whole
population are both untouched by the fix. The first two converge once nothing is unaccounted
— which is what conservation *means*.

**Standing rule reaffirmed:** every metric states its denominator; `3,679` canonical and
`3,381` ranged are never collapsed. Note for the record: **3,381 is exactly the subset of the
3,679 canonical rows that carries a `pageStart`** (3,679 − 298 unanchored rows = 3,381) —
the two denominators are one population under two evidence conditions, which is a reason to
keep them separate, not to merge them.

---

## 7. A2 — CANONICAL LESSON IDENTITY

Reproduce: `python3 tool/corpus/accounting/lesson_identity.py report`.

The evidence is upstream of the CSV. Each row of `all-lessons.csv` is one entry in a book's
`lessons[]` array in `poc-out/graph/curriculum-structure.json`, and that entry carries
`number`, `pageStart` **and** `title` — three fields the CSV projects down to `number`. So
"is 3,679 a lesson count or a row count?" is answerable without new judgement: **ask whether
two rows that share a key also share the printed page they start on.**

| figure | value |
|---|---:|
| **SOURCE ROWS** | **3,679** |
| **DISTINCT CURRENT KEYS** `(sourceDocumentId, lessonNo)` | **3,240** |
| duplicated keys · excess rows | 154 · 439 |
| **TRUE DUPLICATES** (excess rows) | **29** |
| **KEY COLLISIONS** (excess rows) | **410** |
| **SOURCE VARIANTS** | **0** |
| **CANONICAL LESSON COUNT** `(sourceDocumentId, lessonNo, pageStart, title)` | **3,650** |
| … page-anchored | 3,359 |
| … unanchored (no `pageStart`) | 291 |

| duplicate class | keys | rows it removes | evidence |
|---|---:|---:|---|
| `key_collision` | 132 | 0 | every row has its own `pageStart`: the printed numbering **restarts** inside each chủ đề |
| `mixed` | 19 | 26 | the group holds both a repeat and a collision |
| `true_duplicate` | 2 | 2 | identical `number`, `pageStart` and `title`: one record emitted twice |
| `unverifiable` | 1 | 1 | no `pageStart` and no `title` on any row — the evidence cannot decide |

### The finding

**`3,240` is wrong in the direction nobody was watching.** Collapsing on
`(sourceDocumentId, lessonNo)` **deletes 410 real lessons**. In `01-sgk-giao-duc-the-chat-1`,
«Bài 1» is printed **seven times**, once per chủ đề, starting at pdf pages 10, 27, 40, 63 and
79 — seven lessons, not one. The duplicated keys are concentrated exactly where numbering
restarts: GDTC 64 keys · Chuyên đề 31 · GDKT&PL 21 · Tin học 12 · Âm nhạc 12 · HĐTN 9 ·
Lịch sử 5, and by grade in 10–12 (100 of 154).

`3,679` is wrong by **29** — the true duplicates.

### The two concepts, and the evidence that they are different things

- **`SourceLessonRecord`** — one entry as parsed from one book's table of contents:
  `(sourceDocumentId, lessonNo, pageStart, title)`. **3,679** of them. This is what
  `all-lessons.csv` actually counts, and it is a sound thing to count.
- **`CanonicalLessonIdentity`** — one actual lesson in one book. `(sourceDocumentId,
  lessonNo)` is **not** it. The measured identity is
  `(sourceDocumentId, lessonNo, pageStart, title)` = **3,650**.

`(sourceDocumentId, pageStart)` was tested and rejected: **88** page values in the corpus
carry two different lesson numbers (two short lessons genuinely start on the same printed
page), so page alone over-collapses.

### Residual uncertainty, stated rather than resolved

- **291 canonical identities have no `pageStart`** (298 source rows across 77 books; 11 books
  have no page on any row). For those the identity rests on `title` alone, and where the
  title is also null the evidence cannot decide. That is the whole of the `unverifiable`
  class and part of `mixed`.
- **63 of the 301 SGK documents contribute ZERO rows** — `structureStatus: NO_TOC`, empty
  `lessons[]`. So **3,679 is not "all SGK lessons"; it is "lessons in the 238 SGK books with
  a parseable TOC."** This is the same failure family as R13: a whole book leaving the
  denominator with no record in the artefact. Reported, not fixed.
- **`Chuyên đề` (specialised-topic) books contribute 31 of the 154 duplicated keys.** Whether
  a specialised-topic volume belongs in a canonical K-12 lesson count at all is a product
  question, not a data one.

### What this does and does not settle

`3,650` is a **MEASUREMENT, not a Founder decision.** Per the standing rule, **`3,679`
remains HISTORICAL BASELINE ONLY** and must be labelled as such beside every use, until the
Founder rules on: (a) whether `CanonicalLessonIdentity` is adopted as a distinct concept from
`SourceLessonRecord`; (b) what to do with the 291 unanchored identities; (c) whether the 63
TOC-less books are in or out of the denominator; (d) whether `Chuyên đề` counts.

---

## 8. What is PROVEN, what is not

**PROVEN (measured, reproducible, committed tool):**

- Round 5's silent-loss numbers reproduce exactly, from two independent constructions.
- `UNACCOUNTED = 0` on the evaluation set, the holdout and both Golden slices, enforced by a
  check that exits non-zero — and still `0` after WS-C's demotion is composed in.
- Conservation across a downstream demotion: the learning population of Golden #1 is identical
  (51 regions) in two different pipeline generations; exactly 2 regions moved, 0 were lost.
- The served set is byte-identical before and after on every population measured.
- The root cause is rule order: 17 of 18 Docling FORMULA regions never reached the `formula`
  role.
- A2's six figures, and that `(book, lessonNo)` deletes 410 lessons.

**OBSERVED, not proven:** that classing 49 Toán picture-interior regions as `figure_text` is
the *right* disposition. It is auditable and evidence-backed (they sit inside a Docling
picture bbox), and the ledger counts the content-bearing ones separately — but whether a
diagram-aware recogniser should recover them is WS-B's question, not this workstream's.

**HYPOTHESIS:** that the fix generalises beyond these 12 lessons + 2 Golden slices. It has
been measured on 1 524 input regions in three independent populations, one of them a holdout,
and on both a Math and a History/Geography loss profile. It has **not** been run over the
whole corpus.

**UNKNOWN:** whether any lesson elsewhere in the corpus has a region whose role is a *learning*
role but which reaches neither TSL list. The ledger would report it as
`dropped_with_role:<role>` and fail; none occurred in any population measured here.
