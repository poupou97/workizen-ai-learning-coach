# 03 · WORK COMPLETED — four workstreams, what each built, and its PR

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

**Status vocabulary:** DONE · PARTIAL · FAILED · FALSIFIED · BLOCKED · DEFERRED · NOT STARTED.

---

## 0. The PR table — five open, none merged

*(**PROVEN** — GitHub API, 2026-09-06; raw output in `evidence/round6-pull-requests.json` and
`evidence/round6-ci-status.txt`.)*

| PR | Branch | Head *(re-resolved)* | Workstream | CI | State |
|---|---|---|---|---|---|
| **#89** | `ws-archive/round5-retrospective` | `73a5321` | round-5 archive tooling | **PASS** | **OPEN** |
| **#90** | `ws-c/round6-repair-integration` *(stacked on WS-A)* | `4193c50` | C · repair → product | **PASS** | **OPEN** |
| **#91** | `ws-a/round6-accounting` | `02e28dc` | A · truth accounting | **PASS** | **OPEN** |
| **#92** | `ws-b/round6-recognition` | `371b6b0` | B · recognition | **PASS** | **OPEN** |
| **#93** | `ws-d/round6-golden-delivery` | `eeb38c1` | D · golden delivery | **PASS** | **OPEN** |

Plus round 5's **#79–#88** and round 4's **#73** — all still OPEN, `mergedAt: null` *(PROVEN)*.

**5 of 5 heads match §10.1 of the consolidated report.**

---

## 1. WS-A — TRUTH ACCOUNTING · PR #91 · **DONE**

**Built:** `tool/corpus/accounting/**` (new — `dispositions.py`, `ledger.py`, `lesson_identity.py`,
`golden-slices.json`), plus the root-cause fix in `tc2_sdm.py` / `tc2_tsl.py`, the `gate.py` guard
list, and `test_accounting_ledger.py` / `test_lesson_identity.py`.

### The invariant

```
INPUT SOURCE REGIONS = SERVED + WITHHELD + EXCLUDED_WITH_REASON + explicitly defined non-learning
```

`INPUT SOURCE REGIONS` for a lesson = **every SDM block on the lesson's own boundary pages** — the
population round 5's served share and over-withhold rate were both computed *inside*, after content
had already been dropped from it.

Four dispositions and nothing else. `UNACCOUNTED` ⇒ **HARD FAILURE**: `ledger.py audit` **exits
non-zero** *(PROVEN — the exit path was read; the run is MEASURED by WS-A)*. Round 5's silent loss
survived precisely because **nothing failed**.

**`EXCLUDED_WITH_REASON` is deliberately not a synonym for `WITHHELD`.** *A page number is a defined
non-learning region. A block of digits is not.*

### The result

| population | ledgers | input regions | UNACCOUNTED before → after | served |
|---|---:|---:|---|---|
| batch 2, all lessons | 11 | 787 | **33 → 0** | 285 → **285** |
| batch 1 (holdout), all lessons | 14 | 814 | **62 → 0** | 234 → **234** |
| golden run, all lessons | 4 | 277 | **43 → 0** | 43 → **43** |
| **total** | **29** | **1,878** | **138 → 0** | **byte-identical** |

**Five of the lessons that close here were never in any batch spec and were never looked at while
the fix was written.**

### The root cause, and why one mechanism explains three findings

`assign_role`'s **letterless test ran second**, before the rules for TABLE, FORMULA, page furniture,
figure text and the printed `?` answer slot. Every letterless region reached `empty` before anything
could name it. Measured: **17 of 18 Docling FORMULA regions never reached the `formula` role**, so
`role.value == 'formula'` occurred exactly **once in 1,655 blocks**.

One mechanism explains **R13**, Lane A2's **`empty_block`** finding, and the
**`7 8 2 8 7 - 2 8 5 8` misdescription** together.

`letterless_role()` restores the order **for letterless text only** and asks nothing new — it uses
the pipeline's own vocabulary with the guards that vocabulary already carries (a `formula` without a
validated structure is still withheld). `tc2_tsl.py` no longer `continue`s past a furniture role;
**that `continue` was the disappearance.**

### The census of all 82 lost regions

| class | what it is | batch 2 | batch 1 | total |
|---|---|---:|---:|---:|
| `symbol_fragment` | an operator torn off its expression (`- -`, `=`, `+•`) | 7 | 24 | **31** |
| `numeric_label` | letterless digits — map/table/diagram figures (`1408`, `0,6`) | 9 | 11 | **20** |
| `numeric_expression_inline` | a whole printed exercise on one line (`40 613 + 47 519`) | 8 | 7 | **15** |
| `unreadable_region` | **block text empty while OCR lines under it carry printed content** | 3 | 10 | **13** |
| `numeric_expression_stacked` | a stacked expression flattened from ≥3 printed lines | 0 | 3 | **3** |
| `no_content` | nothing was lost | 0 | 0 | **0** |

**`unreadable_region` is the class that most changes the reading of round 5.** Under one of those
13 sit nine OCR lines reading `9 · 3 · a) · 11 · 11` — the printed exercise `9/11 − 3/11`. *They did
not lose nothing. They lost everything, and `empty_block` / "no letters" said the opposite.*

**Not a Toán-only effect, and not one root cause:** on LS&ĐL 4 Bài 12 all 8 losses are map/table
figures; on LS&ĐL 5 Bài 8 all 6 are figure text inside a picture region; on Bài 61, 25 of 32 are
figure text and 7 are FORMULA regions.

### Canonical lesson identity — the Founder's open question, answered

| figure | value |
|---|---:|
| SOURCE ROWS | **3,679** |
| DISTINCT CURRENT KEYS `(sourceDocumentId, lessonNo)` | **3,240** |
| duplicated keys · excess rows | 154 · 439 |
| **TRUE DUPLICATES** | **29** |
| **KEY COLLISIONS** | **410** |
| SOURCE VARIANTS | **0** |
| **CANONICAL LESSON COUNT** `(sourceDocumentId, lessonNo, pageStart, title)` | **3,650** (3,359 page-anchored · 291 unanchored) |

**`3,240` is wrong in the direction nobody was watching: it deletes 410 real lessons.** In
`01-sgk-giao-duc-the-chat-1`, «Bài 1» is printed **seven times**, once per chủ đề, starting at pdf
pages 10, 27, 40, 63 and 79. **`3,679` is wrong by 29.**

`(sourceDocumentId, pageStart)` was **tested and rejected**: 88 page values carry two different
lesson numbers.

**Two facts that dissolve older confusions:** **63 of 301 SGK books contribute zero rows**
(`NO_TOC`), so *3,679 was never «all SGK lessons»* — it is «lessons in the 238 books with a
parseable TOC». And **3,381 ranged is exactly the subset of the 3,679 rows carrying a `pageStart`**
(3,679 − 298 = 3,381) — **the Founder's two denominators agree precisely; there was never a
contradiction.**

---

## 2. WS-B — RECOGNITION · PR #92 · **DONE**

**Built:** `tool/corpus/recognition/**` (new — `census.py`, `consensus.py`, `recrop.py`,
`vision.py`, `boxes.py`, `exponent.py`, `symbols.py`, `sheet.py`, `study.py`, `codeformula.py`,
`cli.py`), `tool/ocr/ocr_crop.swift`, and **50 new tests** that touch no corpus, no PyMuPDF, no
numpy, no Vision and no network.

### GATE B — met, on the class the Founder named and the slice the Founder chose

`b) 3/10 + 5/21` on Toán 5 tập một p22 — the numerator `3` is **absent from the whole-page OCR
output entirely**, and round 5 said nothing but recognition on the printed region could reach it —
is now read correctly, **both halves**, confirmed at two independent scales and seen stacked in a
third observation.

**GOLDEN #2 · Bài 61 (p81–83):** 85 printed fraction regions, 47 unreadable by whole-page OCR.
**17 recovered · 17 of 17 correct against the printed page · 0 disagreements on 38 controls.**

### What "high resolution" turned out to mean

Every SGK page is a **100 ppi scan embedded in the PDF**. Rendering a crop at scale 20 produces
830 × 1090 px from ~58 × 76 source pixels: **interpolation, not information.** What a crop actually
changes is **context** (language correction off, no surrounding prose to resolve a digit into),
**glyph-to-frame ratio**, and — the load-bearing one — **segmentation**. Recovery is **not monotonic
in scale**: on the `3/10` region, scale 3 reads `-` and `10`; scale 6 reads `3`,`1`,`0`; scale 12
reads `10` alone; scale 20 reads `3` then `10`.

**Cost: ~0.46 s per region for twelve observations. No dependency added.**

### The rule — fail-closed at every step

A printed fraction is READ only when **all** of: the numerator box alone returns exactly one bare
digit run, the same one, at **≥2 distinct scales**, with **no scale returning a different one**; the
same for the denominator; **and** the whole-region crop returns exactly those two digit runs **in
that vertical order** — an independent observation that they *stack*. A scale returning two digit
runs in one half **abstains**. *Two boxes each holding a digit do not make a fraction.*

### The six metrics, five populations, never summed

| | DEV | **SDM** | HOLDOUT-1 | HOLDOUT-2 | **HOLDOUT-3** | Bài 61 |
|---|---|---|---|---|---|---|
| pages | 16 | 113 | 24 | 12 | 14 | 3 |
| recovery population | 128 | 548 | 66 | 105 | 177 | 47 |
| **DIGIT RECALL** | 0.500 | **0.403** | 0.061 | 0.038 | **0.181** | 0.532 |
| **STRUCTURAL EXACT MATCH** | 0.344 | 0.259 | 0.000 | 0.010 | 0.130 | 0.362 |
| control disagreements | 1 | 1 | 0 | 0 | 2 | **0** |

**FALSE RECOGNITION RATE, beside every recall figure:** DEV + Bài 61 **0.000** (28 recoveries) ·
**HOLDOUT-3 0.049** · SDM control 0.004 (and the hand-check says *the baseline is wrong, not the
re-crop*).

### The other two named defects — one recovered, one falsified

- **`3×10⁸ → 3×10°`:** 171 corpus-wide, 21 read, 17 right raw (**false rate 0.190**), **16 accepted
  after three guards, 16/16 correct, false recognition 0.000** — at a cost of one correct reading
  refused. Among the 16 is a block **served TRUSTED today** with a destroyed exponent
  (`1 Bar = 10⁵ Pa`). The other two (the speed of light, twice) are **STILL_BROKEN**. And round 5's
  independent validator `si_expected_exponent` **abstained on all 171** — *an independent validator
  that never fires is not yet an independent validator.*
- **`II → I1`:** 106 findings, 8 read, 7 correct; the Founder's line recovers at **four scales out
  of four** and **the book's own section sequence PASSES it**. Gated on PASS: 3 accepted, **0
  errors**. `sequence_validator` is *exactly* the signal round 5 named and nothing consulted.
- **`Ω → S2`: FALSIFIED. 0 of 22, at every scale.** *A targeted re-crop recovers a character the
  engine could read but did not isolate; it recovers nothing when the glyph is not in the engine's
  repertoire.*

### The honest negative, and the hand-off

**RESTORE 10 → 10.** Five blocks gained a proposed value and every one is malformed
(`b) 10 +. 3/10`). The reason is precise: the recovered `3/10` is **added** while the destroyed
observation `b) 10 +.` **is still there**. *Replacing a source observation is not something a
recogniser may do* — it is a `RepairCandidate` crossing a `Validator`, which is **WS-C's contract**.
Doing it inside `mathfix` would have been a second provenance universe.

---

## 3. WS-C — REPAIR → PRODUCT · PR #90 · **DONE, with one PARTIAL**

**Built:** `repair/validated.py`, `repair/tsl_projection.py`, `repair/ledger.py::entry_from_json`,
the `repair/engine.py` dispose-row fix, `tsl_to_lesson_document.py::repair_of` +
`KNOWN_UNCARRIED_ROLES`, `lib/core/lesson_model/repair_record.dart`, `LessonBlock.unsupported`,
`test_repair_integration.py` (30 tests), `repair_record_test.dart` (12 tests).

### GATE C — the result

**9 validated · 6 crossed · `trusted: 0` · violations 0 · demotions 2 · served text changed: none.**

*(**PROVEN** — the archive builder parsed the shipped fixture: 6 repair-bearing blocks, 6/6
`VALIDATED_REPAIR`, 6/6 `servable: false`, 6/6 on type `withheld`, **0 carrying a `text` field**, 0
carrying any forbidden value key.)*

### `CONNECT ≠ TRUST`, enforced in five places — none of them a policy anyone must remember

| where | mechanism |
|---|---|
| `repair/validated.py` | `disposition` is a **class attribute, not a field** — no argument, flag or setter yields `TRUSTED`; `from_entry` raises on a `restore` row; `from_json` raises on any other disposition *(PROVEN — read at line 167)* |
| `repair/tsl_projection.py` | **there is no promotion mechanism at all**; a laboratory restore is *capped*, with the reason written in three places |
| `tsl_to_lesson_document.py` | `repair_of()` **refuses rather than sanitises**; a **served** block carrying a repair is itself a refusal — *that is the shape of an ungated restore* |
| `check_document` | searches the **whole serialised document** for each proposed value, so a future field or a careless `**record` cannot open the door quietly |
| `lib/core/lesson_model/` | `repair` is a field **only on `WithheldBlock`**; a null `ValidatedRepairRef` **rejects the whole document** *(PROVEN)* |

### The Founder's sharp case, on the artefact

`p039:000` carries **all seven dated events**. Round 5 withheld it on one token — «Bạch **Đằng**»
(primary) vs «Đăng» (verifier) — and the print says the primary is right.

```
type withheld · trust withheld · reasons ["agree_tones"] · textLen 272 · NO `text` field
repair.disposition VALIDATED_REPAIR · method lanec.tone-corroboration-v1 · verdict validated
repair.changed false   (a DISPOSITION repair: nothing is rewritten)
repair.servable false
signals  D.in_corpus_majority ABSTAINS · E.human_print_read SUPPORTS 1.0
```

**No lesson identity is named anywhere** — no `if lesson == 8`, no book allow-list, no special case.

**And Lane C's *opposite* result survives:** `p041:002`, the attribution whose repair candidate two
independent signals **rejected**, is now **WITHHELD** with `detected_unrepaired:vi_tone_disagreement`
and no text — *it stops being served rather than being half-corrected.* **That row is what proves
the integration is not a coverage exercise.**

### Capping demonstrated, not asserted

KHTN 7 Bài 20 against Lane A1's `tc2-p3-lin` ledger, which restores in place: **the laboratory said
TRUSTED; what crossed was `VALIDATED_REPAIR` + `trust_gate:founder_decision_absent`**, with the cap
written onto the region's reasons as well.

### Three structural obstacles

1. **No carrier for structured content — PARTIAL.** `no_carrier:formula` replaces the false
   `unknown_role:formula` *(PROVEN — `KNOWN_UNCARRIED_ROLES = {'formula': 'no_carrier:formula'}`)*.
   Behaviour-neutral for the app today. A **servable** structured kind is **deliberately not done**:
   it needs app rendering *and* a Founder trust decision, and round 5's harm was precisely a
   flattened expression shown as arithmetic the book does not contain.
2. **The app fails closed on the whole document — DONE, scoped.** `LessonBlock.unsupported()` lowers
   **exactly one** case to the block: an unknown `type` becomes a `WithheldBlock` with reason
   `unsupported_block_type:<type>`, **counted**, with `trust` **forced** to withheld. **Every
   integrity violation still rejects the whole document** (six such cases asserted), and
   `strictBlockTypes: true` restores all-or-nothing for a packaging gate.
3. **The app has no rich text — ACCEPTED AS IS.** Nothing added. *The page crop with provenance is
   the honest path, and it costs zero app work.*

---

## 4. WS-D — GOLDEN DELIVERY · PR #93 · **DONE, with one DEFERRED and one NOT STARTED**

**Built:** Option B in `lesson_workspace/**`, `tool/evidence/fixture_lineage.py` (16 tests),
`tool/evidence/golden_delivery.py`, `tool/evidence/learning_view_census.py`, and the corrected
`no_machine_ids_test.dart` / `round4_experience_test.dart` / `round5_visual_test.dart` /
`workspace_density_test.dart`.

### Option B — executing a decision rather than running the experiment forever

Round 5 built four presentations from one commit and measured all four; **the Founder chose B**.
Round 6 **removed the enum, the `WAL_ASSIST` flag and options A and C**, leaving three states:
`COLLAPSED` (💡 in the title row) → `PEEK` (one line «💡 SAM gợi ý: … →», the default, **destination
known at zero taps**) → `EXPANDED` (why + CTA + «Để sau» + «Đã mở»).

**Three duplicates deleted with the decision:** the view-changing CTA on the card (it repeated the
tab directly above it) · SAM's portrait where SAM is not speaking · the permanent «Đã mở ● ○ ○» row
(*a **session** trace, not learning evidence — `OPENED ≠ UNDERSTOOD`*), which moved into EXPANDED.

| pinned chrome | Đọc | Trực quan | Học với SAM |
|---|---|---|---|
| round 4/5 (`card`) | 225 dp | 225 dp | **411 dp = 58.9 %** |
| **round 6 (B)** | **281 dp** | **281 dp** | **281 dp** |
| B after «Để sau» | **225 dp** | 225 dp | 225 dp |

**The number that matters is not the smallest one — it is the equal one.** Round 5's 411 vs 225
gap existed only because of a card. Now all three views pay the same price, **and a test pins it.**

**One word set for three views**, and the test does **not** pin «count 6» — counting could not catch
this defect, it only made the number slip. It pins that **each view name appears exactly twice**
(tab + card) and that the three old strings are gone **from the screen and from the source**.

### GOLDEN #1 — the chain, with hashes

```
SGK source (pdf 38–41) → SDM sdm-v3 · TSL tc2-r5   c9d2cf1f… (canonical)
  → lane-c repair ledger (240 rows) → ValidatedRepair ×9 on 6 blocks
  → PROJECTED TSL (WS-C)                            d7825280… (canonical)
  → LessonDocument (34 served / 17 withheld)        fb5dbfa8… (bytes)
  → History rules v2 (post-pass)                    a904d005… (bytes)
  → assets/fixtures/real/lesson-05-…-b8.json → WorkspaceCatalog real path → device
```

`fixture_lineage.py --require-repair` → **VERDICT PASS**.

**Two decisions stated plainly.** (a) The document was **not re-bridged on this branch** — only
WS-C's bridge stamps `provenance.repair`, and re-bridging produced a document that *looked fine and
proved zero*: 57 blocks instead of 52 and **not one repair provenance line**. (b) The History-rules
post-pass **was** applied, for exactly one reason: **the title**. WS-C's document carried the
OCR-broken pipeline title «THỜI KĨ BẮC THUỘC»; `lesson-title-v1` derives the real title from the
**printed table of contents** and records `titleDerivation`. **It changed nothing else — timeline
events 0 → 0.**

### The lineage gate caught a stale artefact on its first real use

Golden #1 was staged from WS-C's **11:01** artefact. At **11:08** WS-C re-ran; the TSL on disk no
longer hashed to what the document claimed (blocks 36 → 34, withheld 15 → 17). **L2 went red with
«THE FIXTURE WAS NOT BUILT FROM THE TSL IT NAMES».** Re-staging from the current artefact → PASS.
**This is exactly the trap round 5 fell into, caught by machine.**

**Two findings about the measuring system itself:** (a) **two hash methods coexist** — the committed
bridge hashes **file bytes**, the round-6 repair path hashes **canonical JSON** — so a reviewer
running `shasum -a 256` would get a different number and conclude tampering; the gate now computes
both and **names which one matched**. (b) **The pipeline name does not identify a generation** —
a round-5 re-run sits under `tc2-r5` but declares `pipeline: tc2-p1`; **only `sdmVersion` and the
hashes are authoritative**, and L3b reports the disagreement rather than passing on the label.

### The learning-view census — and its recommendation not to build

`learning_view_census.py` runs **the product's own bridge** over **238 canonical TSLs**: 238
bridged, 0 refused.

| | lessons | share of 238 |
|---|---:|---:|
| **✨ Trực quan has something to show** | **73** | **0.307** |
| 🦉 Học với SAM has a script | **1** | **0.004** |

So **165 lessons (0.693)** open Trực quan to «Chưa có sơ đồ cho bài này», and **SAM's teaching reach
on the canonical corpus is exactly one lesson.**

| kind | instances | renderer |
|---|---:|---|
| `process` | **181** (96.8 %) | `ProcessFlowView` |
| `comparison` | 6 | `MindmapView` |
| **`conceptMap`** | **0** | `MindmapView` |
| **`timeline`** | **0** | `TimelineView` |

**Two of the four renderer families have no real data at all.** Recommendation: **add no renderer
family this round.**

**Where the real volume is, and it is not a renderer.** Of 2,170 withheld blocks (0.152 of 14,241
learning blocks): `agree_text` **824 (0.380)** — WS-B's ground; `figure_dependent` **632 (0.291)** —
measured support for E1's **LABELED_FIGURE** nomination, but step 2 of FORMS BEFORE RULES, not a
licence to build; and **`unknown_role:*` 118** (`footnote` 64 · `activity` 50 · `option` 4) —
**withheld because the consumer has no type, not because the text is untrustworthy. A model gap,
not a data gap** — and the cheapest item on the table.

---

## 5. The composition check — standing procedure, second round running

Verified in a throw-away worktree from `integration/round6-2026-09-06` with all five branches merged
**and the real gitignored assets synced in** (packs + fixtures) — so a missing asset could not be
mistaken for a defect and, more importantly, **so the stale premises of §10 could not hide**.

| Check | Result |
|---|---|
| Git merge, 5 branches | **0 conflicts** |
| `flutter analyze` | **No issues found** |
| Python suite | **748 tests OK** (23 skipped) |
| Dart suite | **1084 tests — All tests passed** |

**It did not compose on the first attempt, and both failures were worth having** — see
`04-FAILURES-AND-FALSIFICATIONS.md` §7.
