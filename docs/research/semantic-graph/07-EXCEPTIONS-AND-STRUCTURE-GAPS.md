# Lane E1 · §15 exception clusters · §17 source-structure gaps

Reproduce: `python3 tool/semantic/gaps.py` → `poc-out/round5/semantic/gaps.json`.

---

## 1. §15 — exception clusters, ranked by lessons-unlocked-per-extension

Denominator **3,240 censused lessons** (distinct `(book, lessonNo)`; see `06-CENSUS.md` §0).
Clusters are assigned in order and are disjoint, so the counts add up.

| rank | cluster | lessons | % of 3,240 | what **one** change would unlock |
|---:|---|---:|---:|---|
| 1 | **NO_SOURCE_AT_ALL** | **1,384** | 42.7 % | **Nothing — this is not a grammar problem.** No units and no TSL: the lesson has never been read. Owned by the ingest/pipeline lanes, not by the semantic grammar. |
| 2 | **NEEDS_MATH_AST** | **1,096** | 33.8 % | one structured-expression node (Lane A2's `MathExpression`) **plus a bridge carrier** — `ROLE_MAP` has no `formula` key and the consumer nulls the whole document on an unknown kind |
| 3 | **NEEDS_PHYS_QUANTITY** | 113 | 3.5 % | `Quantity(value, unit, symbol)` promoted from a composed value to a first-class node |
| 4 | **NO_CUE_AND_NO_EXTRACTION** | 63 | 1.9 % | unknown — needs a human read. **This is the honest tier E**: 63 lessons that have source text and match nothing. |
| 5 | **NEEDS_LIT_TEXT** | 50 | 1.5 % | `Line` / `Stanza` / `Character` / `Attribution`. Lane C's `story-attribution-v1` already implements the last of these. |
| 6 | **NEEDS_CHEM_REACTION** | 7 | 0.2 % | `Species` + `Reaction` |
| 7 | **CUES_BUT_NO_EXTRACTION** | 2 | 0.1 % | an extraction rule for a family that has none (COMPARISON is the obvious one) |
| — | *not an exception* (representable and/or extractable) | 525 | 16.2 % | — |

### Reading this honestly

**The single largest cluster is not a language problem at all.** 42.7 % of the corpus cannot be
represented because nobody has read it — no OCR-derived units, no TSL. No grammar extension, no
renderer and no ontology change moves that number by one lesson. It moves when the ingest pipeline
covers more books.

**The largest cluster that IS a language problem is MATH_AST, at 1,096 lessons (33.8 %) — and it
is one extension.** That is the strongest possible case for *«FIX THE LANGUAGE, NOT 100 INDIVIDUAL
LESSONS»*: a single node kind plus a bridge carrier is worth more than every other extension
combined, by a factor of nine.

Everything below rank 3 is small. Ranks 3–7 together are **235 lessons (7.3 %)**. So the ranking
is not a gentle gradient — it is **one pipeline problem, one grammar problem, and a long tail**.

### What this implies for sequencing

1. Nothing in the semantic grammar should be tuned before **MATH_AST has a carrier**. It is the
   only extension with corpus-scale leverage, and it is blocked on two bridge defects, not on
   modelling.
2. The **63 tier-E lessons** are the right size for a human read. That is a tractable curation
   task, and it is where a genuinely new pattern would show up if one exists.
3. LIT_TEXT (50) and CHEM_REACTION (7) do not justify architecture work yet. They justify being
   *recorded as unsupported* so nothing silently misrepresents them.

---

## 2. §17 — which source-structure losses currently block visualization

Measured on the source record itself, not argued from the model. Denominator: the TSL slice —
**238 lessons / 11,971 blocks / 3,864 figures** (Science). Never divide these by 3,240 or 3,679.

| structure | measured state | blocks visualization? |
|---|---|---|
| **question stem + options** | 1,642 question blocks · **4** blocks with role `option` · **4** lines even *shaped* like an option | **YES, totally.** A question is one flat string. There is no stem→option link anywhere, and `QuestionBlock` (`lesson_document.dart:472`) is `text` only. Any option-bearing family is unreachable. |
| **figure + caption** | 3,864 figures · **1,300 (33.6 %)** carry a caption · 1,055 carry labels · **465 orphan «Hình N.M» label blocks** whose descriptive caption is a *different* block | **YES, partially.** LABELED_FIGURE can anchor a figure and attach prose that names it, but the book's own caption is not attached to the figure record two thirds of the time. |
| **table rows/cols** | **20** blocks with role `table` · **0** carry cells · 261 blocks *mention* a table | **YES, totally.** A table block is a string. Any grid family (COMPARISON from a printed table, DATA_CHART) is unreachable from this layer. |
| **fraction / exponent geometry** | **0** blocks retain either shape | **YES, totally.** Math is *withheld*, not modelled (`math_guard`, 41 withheld regions). Lane A2 owns the repair; the carrier is missing (§3 of `01-AUDIT-CLASSIFICATION.md`). |
| **procedure label + steps** | recoverable, but only through the **governing block** | **PARTIALLY — and fragile.** One tone slip removes it (§3 below). |
| **poetry line / stanza** | **0** in the Science slice | **UNMEASURABLE HERE.** Ngữ văn and Tiếng Việt have no TSL at all, so the one corpus where verse structure matters has never been measured. |
| **dialogue speaker + utterance** | 1,102 blocks start with a dash — but a leading dash is *also* the bullet enumerator | **UNMEASURED.** The two are not distinguishable in the current record. |

### Withholding, as a structure loss

**236 of 238 TSL lessons** carry at least one withheld region. By reason:

| reason | regions |
|---|---:|
| `agree_text` | 824 |
| `figure_dependent` | 632 |
| `agree_order` | 224 |
| `page_feature:diagram` | 197 |
| `page_feature:color_heavy` | 95 |
| `box_boundary` | 92 |
| `math_guard` | 41 |
| `answer_leak` | 29 |
| `low_ocr_conf` | 19 |
| `role_conflict` | 7 |

`figure_dependent` (632) is the one that bites this lane hardest: it withholds exactly the text
that would have said what a figure shows. And `page_feature:diagram` (197) withholds text on the
pages most likely to carry a process or a labelled figure — i.e. **the safety mechanism withholds
most densely precisely where the visual families live.**

This is round 5's defect 8 seen from the semantic side: withholding is not free. It does not merely
reduce coverage, it removes structure, and a structure with a member removed is not a smaller
structure — it is a wrong one. The VisualSpec's `gap` element (`03-VISUALSPEC-CONTRACT.md` §3.3)
is the contract for handling that honestly; **it is not yet implemented**, because v0 compilers read
only trusted blocks.

---

## 3. Two measured ways a visual family disappears with no rule at fault

### 3.1 A pipeline rebuild deletes a family

Four LS&ĐL 5 lessons have two TSL builds that disagree about which families they support — and
**every disagreement runs the same way**:

| lesson | `tc2-p1` (round 4) | `tc2-r5` (round 5) |
|---|---|---|
| Bài 8 | DEFINITION · HIERARCHY · **TIMELINE** | DEFINITION · HIERARCHY |
| Bài 9 | **CAUSAL** · DEFINITION · HIERARCHY | DEFINITION · HIERARCHY |
| Bài 18 | **CAUSAL** · DEFINITION · HIERARCHY | DEFINITION · HIERARCHY |
| Bài 27 | DEFINITION · HIERARCHY · **PROCESS** | DEFINITION · HIERARCHY |

**4 of 28 LS&ĐL lessons (14.3 %) lost a family. None gained one.** And on Bài 8 the round-5 build
has **more** trusted blocks (36 vs 34): the single block carrying all seven dated events is not
present as trusted, so `Event` count goes 7 → 1 and TIMELINE stops compiling.

**Block counts and semantic yield are not the same quantity.** A pipeline change scored only on
the DATA ACCURACY SCOREBOARD can delete the visual layer while its numbers improve. Round 5 needs a
**semantic-yield regression check** run on every pipeline change. `tool/semantic/census.py` computes
it per lesson today; wiring it into A1's and D's gates is a coordination decision, not an E1 one.

### 3.2 A tone slip deletes a family

Bài 17's filtering procedure is governed by a block reading **«Chuẩn bị: … Tiền hành:»** — OCR's
version of «Tiến hành». Round 4 lists this exact slip among the four that survive *because both OCR
stacks make the same error*, so no agreement guard reaches it.

Matching the accented spelling only: **0 `Step` primitives, PROCESS gone.**
Comparing tone-stripped: **5 `Step` primitives, PROCESS restored.**

This raises the stakes of Lane A1's Vietnamese fidelity work beyond display fidelity. A tone slip
in a *structural* word is not a cosmetic defect — it is a structural one, and it is invisible to
every metric that counts characters.

E1's mitigation (comparing tone-stripped for structural markers only) is a **workaround, not a
repair**: it makes the discriminator robust, and it does nothing for the text the child reads.
