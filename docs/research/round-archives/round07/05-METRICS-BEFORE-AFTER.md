# 05 · METRICS — BEFORE → AFTER

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

**Reading rules, binding on this file.**

1. **Every metric states its denominator.** Round 7 exists partly because round 6 published a rate
   without one.
2. **Denominators are never pooled**, and populations are named.
3. **«Total activities» is DEPRECATED** and must not appear as a metric. §2.
4. **A rate measured before the round-6 accounting fix is not comparable with one measured after**
   without saying so.
5. Machine-readable companions: `metrics/round7-gate-results.json`,
   `metrics/frozen-calibration/`.

---

## 1. GATE A — METRIC TRUTH

| | |
|---|---|
| metrics in the registry | **18** |
| **metrics that re-derive to their recorded value** | **18 / 18** |
| fields recorded per metric | 9 — semantic quantity · unit · leaf population · grouping key · denominator · aggregation · exclusions · source artefact/version · **runnable re-derivation command** |

**Two re-derivations that landed exactly** *(MEASURED)*:

| metric | re-derived from | result |
|---|---|---|
| recognition REGION census — `DIGIT LOSS 312 (0.569) · SEGMENTATION 196 (0.358) · FRACTION STRUCTURE 40 (0.073)` **of 548** | the 784 leaf rows of `study-sdm.json` | **every count and share, to four decimals** |
| WS-D learning-view census — 238 lessons · 11,971 TSL served · 2,032 withheld · 3,864 figures | the 238 `tc2-p1` TSLs directly | **all four exact** |

## 2. «TOTAL ACTIVITIES» — RESOLVED BY DEPRECATION

| value | what it counts | verdict |
|---|---|---|
| **248** | seven-family activity **leaf rows** on the pack build **before** the Founder §3 fail-closed change (`207 + 41`) — a correct earlier **value of `ACTIVITY_LEAF_COUNT`** | **SUPERSEDED** |
| **217** | 207 activity leaf **rows** + 10 `toanExercises` container **KEYS** — **a sum of two different units** | **DEPRECATED** |
| **161** | `tvReadings 66 + tvWritings 54 + toanExercises 41` — **three of seven families** under a whole-corpus name, silently dropping **87** of the rows it purports to total | **DEPRECATED as a total** |

> **The phrase «total activities» is DEPRECATED.** Named replacements: `TOAN_EXERCISE_LEAF_COUNT`,
> `ACTIVITY_LEAF_COUNT`, `LESSON_KEY_COUNT`, `ACTIVITY_FAMILY_COUNT`.

---

## 3. THE FOUR LESSON DENOMINATORS — one leaf population under four grouping keys

**Re-derived by the coordinator from `assets/pack/` — an artefact that does not depend on WS-A's
`all-lessons.csv`** *(MEASURED; independently re-stated in the frozen population's own `universe`
block, which the archive builder read)*:

| grouping key over `pack.subjects[*][*].lessons[*]` | count |
|---|---|
| leaf rows | **3,679** |
| distinct `(sourceDocumentId, no)` | **3,240** |
| distinct `(sourceDocumentId, no, pageStart, title)` | **3,650** |
| rows carrying `pageStart` | **3,381** |

> **All four are ONE leaf population under FOUR grouping keys.** `3,679` and `3,650` were never two
> artefacts disagreeing, and `3,381 ranged` is exactly the `pageStart` subset — **the Founder's two
> denominators never conflicted.** `3,240` remains the dangerous one: it **deletes 410 real
> lessons** to key collision.

**`3,679` remains HISTORICAL BASELINE ONLY** until the Founder chooses a key. **This is now a
definition decision, not a data conflict.** *(The field is `no`, not `number` — the first
re-derivation attempt used `number`, returned 238 and 3,497, and was wrong.)*

---

## 4. GATE B / C — TRUST CALIBRATION, measured

**Population:** the round-5 evidence rows — **643 rows · 354 served · 54 deliberately hard pages**.
*(MEASURED. Every rate re-derivable by a committed command.)*

### The reference baseline reproduces round 5 exactly, asserted as a test

**643 rows · 354 served · coverage 0.5505 · 26 wrong · FTR 0.0734** — so the candidates are
**re-decisions of a published scoreboard**, not a new measurement.

### The decomposition — the round's result

| | count | of 354 served |
|---|---:|---|
| **teaching-critical errors** | **12** | 0.0339 |
| ↳ digit corruption | **6** | — |
| ↳ non-question served as a question | **6** | — |
| both teaching-critical **and** false trust | 7 | — |
| false trust **only** | 19 | — |
| **teaching-critical only** | **5** | **a bound on false trust alone misses these** |
| digit corruptions surviving **character-exact two-stack agreement** + every other clause | **3 of 6** | — |

### The bound, and what no signal reaches

| | value |
|---|---|
| best achievable teaching-critical bound, any coverage | **≈0.0213 at 53 % of served** |
| strictest principled stack | 0.0233 at 36 % of served |
| **required by a 90 %-clean-lesson promise** | **0.0035** |
| **the gap** | **a factor of six** |
| P(a lesson carries ≥1 teaching-critical error) at 30 trusted blocks | **≈0.48** — **assuming independence**, stated |
| page-level incidence, measured | **0.1026 observed vs 0.0975 expected** on 39 pages / 4 events — **no measurable clustering at this n** |

### Role confidence — tightening it moves the wrong metric the wrong way

| floor | false trust | **teaching-critical** | side effect |
|---|---|---|---|
| current | 0.0734 | **0.0339** | — |
| 0.70 | 0.0593 ↓ | **0.0407 ↑ — worse** | **removes every block of continuous prose** |

**C2 admits 46 % more content *and* has the lower teaching-critical rate. It dominates C1 outright.**

### There is no single false-trust number for this system

**0.073 · 0.090 · 0.365 · 0.650 · 0.727** across five annotated populations — and **the reference
and audit planes do not agree on whether teaching-critical error is a subset of false trust.**

### The bound options

| | consequence |
|---|---|
| **BOUND-2** (recommended, with C2) | 90 % of lessons clean ⇒ per-block ≤ **0.0035**, audit ≥ **1,092 rows**. **Predicted outcome: a TRUTHFUL ZERO — sealed inside the frozen payload.** |
| **BOUND-4** | **the only passable bound** — and its consequence, **45 % of lessons carrying a teaching-critical error, is «not sayable to a parent»** |
| **BOUND-5** | per-lesson certification of a bounded slice. **Not a threshold, and must never be reported as one.** |

### The freeze chain

*(PROVEN — the archive builder read `LEDGER.jsonl`.)*

| seq | kind | sha256 | binds policy | frozen |
|---|---|---|---|---|
| 1 | policy | `0dfc5032…` | — | 06:41:54Z |
| 2 | population BLIND-CORE | `dbadf4ad…` | `0dfc5032…` | 06:47:21Z |
| 3 | population BLIND-TEACHING | `69d1cacc…` | `0dfc5032…` | 06:47:21Z |

**No `approval` entry. No `admitted` entry. Three lines and no more.**

**Populations:** 120 lessons each — **84 distinct books** (CORE) and **72** (TEACHING) — drawn from
**2,536 eligible lessons in 192 eligible books** after excluding **44 contaminated books**.

**The identity claim, stated exactly:** **0 identity-shaped strings in all three calibration
documents** *(PROVEN)*. The frozen **payloads** do name their lessons — `sourceDocumentId`,
`lessonNo`, `pageStart`, with the **title hashed** (`title_sha256`, no raw title). **That is the
evaluation frame, frozen before anything could be admitted; the claim is «no identity in an
admission context», and it holds.** *«Zero lesson identities anywhere» would be false.*

---

## 5. GATE E — the regenerated Golden #1, before → after

*(**PROVEN** — recomputed by the archive builder from the bytes; full output in
`evidence/round7-artefact-verification.txt`.)*

| | round 6 | **round 7** |
|---|---|---|
| blocks | 52 | **57** |
| **withheld regions** | 17 | **17 — id set IDENTICAL** |
| **withheld regions carrying a crop** | **0** | **17 / 17** |
| **served text blocks** | 35 | **35 — id set IDENTICAL** |
| `image` blocks (carrying **no text**) | 0 | **5** |
| crops on disk | 0 | **22** |
| withheld blocks carrying `text` | 0 | **0** |
| blocks carrying a repair record | 6, all withheld | **6, all withheld** |
| repair dispositions / `servable` | 6/6 `VALIDATED_REPAIR` / `false` | **6/6 / `false`** |
| `provenance.repair`: validatedRepairs · onBlocks · **trusted** · capped | 9 · 6 · **0** · — | **9 · 6 · 0 · 0** |
| `semantic` · `tutorSteps` | 0 · 0 | **0 · 0** |
| lineage verdict `--require-repair` | PASS *(with L5 vacuous)* | **PASS — L5 22/22, L5b 17/17** |

**The withheld and served-text id sets are identical between rounds. Nothing became servable; 17
gaps gained a page image.** *The projection also reproduces WS-C's round-6 hashes exactly
(`c9d2cf1f…`, `d7825280…`) — the same generation, re-derived, not a new one.*

---

## 6. WS-S — the 118, and the 31

| | count |
|---|---|
| gap blocks (`unknown_role:*`) | **118** — footnote **64** · activity **50** · option **4** |
| structural groups across 238 lessons | **1,447** — figure_caption 1,300 · procedure_steps 139 · table_rows 6 · **question_options 2** |
| **mutilated structures served TODAY** | **31** — procedure_steps **29** (*a LOWER BOUND*) · **question_options 2 of 2** |
| **servable types recommended** | **0 of 118** |
| gap blocks belonging to **no structural group** | **114** |
| cost of the all-or-nothing rule | **31 → 0** mutilated, at **72** blocks (served 11,833 → 11,761) |
| documents byte-identical with both switches off | **238 / 238** |

| counterfactual | mutilated | served |
|---|---|---|
| TODAY | **31** | 11,833 |
| `+option` | 30 | 11,837 |
| `+activity` | 31 | 11,883 |
| `+footnote` | 31 | 11,897 |
| `+all three` | **30** | 11,951 |
| **TODAY + group rule** | **0** | **11,761** |

**Footnote anchors:** well-formed «(N)» **34 / 64** · **anchored to a SERVED non-footnote block
10 / 64 (0.156)** · «(\*)» 12 · **mark itself OCR-mangled 14** · no mark 4.

**Defect 6 on the lesson path:** imprint text at role `heading` **17** and `body` **5** — **22
served to a child today** — plus **5** in the `activity` bucket withheld only by the type gap.

---

## 7. THE TITLE MEASUREMENT — a decision measured, not argued

*(MEASURED on the shipping packs.)*

| | value |
|---|---|
| titles in `assets/pack/lesson-index-*.json` | **2,623** (2,382 unique) |
| ALL-CAPS titles | **175 (6.7 %)** |
| ↳ single letter-bearing word (acronyms — «GDTC 5», «TN&XH 1») | **67 — FIXED**, left alone |
| ↳ **multi-word ALL-CAPS** | **108** — **the Founder's figure exactly** |
| titles the candidate normalisation **strips capitals from** | **107 of 107** |
| titles `displayTitle` changes | **0 of 2,382** |

**Named casualties it would have caused, from the shipping pack:** `ASEAN AND VIET NAM` →
*Asean and viet nam* · `BÁC HÔ VỚI THIÊU NHI` → *Bác hô với thiêu nhi* · `… THẾ KỈ XX` → *… thế kỉ
xx* — **an acronym, a person's name and a Roman numeral.**

**The activation precondition is a function, not a promise:** `titlesLosingCapitals(transform,
titles)` **must return empty on the real population** before any normalisation may be proposed.
**The cost is stated plainly: «MỞ ĐẦU» now reads «MỞ ĐẦU» on screen.**

---

## 8. REALITY SCOREBOARD — never averaged

| Dimension | Round 6 | Round 7 |
|---|---|---|
| SOURCE REALITY | 97 | **97** |
| **SOURCE TRUST** | 0 / 97 | **0 / 97 — and now measured as unreachable by calibration alone** |
| RECOGNITION REALITY | 17/47 on Bài 61 | **unchanged — no recognition workstream** |
| REPAIR REALITY | 9 validated · 6 crossed · 0 trusted | **unchanged + 17/17 crops restored** |
| PEDAGOGY REALITY | 7 / 17 | **7 / 17** |
| EVIDENCE REALITY | 0 of 0 | **0 of 0** |
| **PRODUCT DELIVERY REALITY** | 1 real lesson, minus its timeline | **unchanged — nothing new reached a child** |

---

## 9. TEST AND CI COUNTS

| Scope | Result |
|---|---|
| **Composed round** (4 branches, fixture **regenerated in-tree**) | **0 conflicts** · `flutter analyze` clean · **Python 866 OK** (18 skipped) · **Dart 1106 — all passed** · **L5b 17/17 · lineage PASS** |
| WS-T (#96) | Python **800 OK** (748 before + **52 new**) |
| WS-R (#97) | `flutter analyze` clean · Dart **1,100 passed / 2 skipped** · Python **756 OK / 15 skipped** |
| WS-M (#94) | registry `verify` **18/18** |
| WS-S (#95) | 238/238 byte-identical; 4 Dart mutation checks |
| All four PRs | `Analyze & Test = SUCCESS` *(PROVEN)* |

---

## 10. MERGE DEBT — measured at the round's final head

*(PROVEN — recomputed by the archive builder.)*

| | commits ahead of `main` |
|---|---|
| `integration/round4` (#73) | **73** |
| `integration/round5` (#79) | **89** |
| `integration/round6` | **208** |
| **`integration/round7`** | **259** |

| structural check | result |
|---|---|
| #73 an ancestor of #79 | **YES** |
| `main` an ancestor of #79 | **YES** — `main` is still `61dbfdb` |
| delta #73 → #79 | **16 commits, 3 files, all `docs/research/`** |

**The report says «254»; measured at the re-audit's own commit `457a970` it is 255, and at the
round's final head 259 — the four documentation commits that closed the round.** *Same stack, later
measurement point.* **Every structural claim re-verified true.**
