# DATA ACCURACY SCOREBOARD — Lane D contribution (round 5, 2026-09-06)

**Measurement only. No threshold, no PASS/FAIL, nothing merged.** `trusted` and `eligible for
teaching` are **0** and stay 0 until the Founder sets a record. Every rate is per **served block** on
a small audited sample; the Wilson intervals are shown so they cannot be read as precision.

This is Lane D's half of the round-5 scoreboard. Other lanes feed the same rows from their own
populations — **the numbers are not interchangeable**: a rate measured on six adversarially chosen
legacy lessons and a rate measured on 54 gold pages answer different questions, and quoting one in
the other's place is a denominator error (D5).

---

## 0. Denominators (D5 — never summed, never averaged into one number)

| denominator | N | what it is |
|---|---|---|
| **canonical** | 3,679 | SGK lessons with a lesson number in `curriculum-structure.json` (Grade 1–12, 301 SGK documents) |
| **ranged** | 3,381 | canonical lessons that also have a TOC `pageStart` |
| **in scope (Lane D)** | 243 | 113 baseline-learnable ∪ lessons with `sam-units` rows = 6.6 % of canonical, 7.2 % of ranged |
| batch 2 OLD | 43 served blocks | what the old product served, audited |
| batch 2 NEW | 67 served blocks + 30 withheld regions | what the new pipeline serves, audited |
| batch 1 (holdout) | 74 served + 30 withheld (round 4) | re-run on the current build |
| shipped packs | 207 activities across 12 packs | after the §3 fail-closed change (248 before) |

**Coverage is stated three ways and never collapsed:** 12 of 243 in scope reprocessed (4.9 %);
12 of 3,679 canonical (0.3 %); **0 trusted, 0 eligible for teaching.**

---

## 1. The five directions the round is judged on

Founder: *not just* `FALSE TRUST ↓`, but **FALSE TRUST ↓ · TEACHING-CRITICAL ↓ · CORRECT SERVED ↑ ·
OVER-WITHHOLD ↓ · RESTORE PRECISION ↑** — at once.

| direction | BEFORE | NEW (`tc2-p2`) | **REPAIRED (`tc2-p3`, A1 merged)** | denominator |
|---|---|---|---|---|
| **FALSE TRUST ↓** | OLD product **0.619** [0.468, 0.750] | **0.318** [0.218, 0.438] ✅ | **10/13 = 0.769** of batch 1's false-trust rows no longer served as before (was 7/13) | 42 / 66 judged served blocks, batch 2 · 13 rows, batch 1 |
| — same measure, vs round 4 | round 4 `tc2-p2` **0.297** | batch 2 **0.318** ➖ | — | different lessons; not a paired comparison |
| **TEACHING-CRITICAL ↓** | OLD **0.476** [0.283, 0.676] | **0.100** [0.043, 0.214] ✅ | 2/5 rows closed; mutilated structures **unchanged** | 21 / 50 judged, batch 2 |
| **CORRECT SERVED ↑** | OLD 80 blocks, ≈ 30 correct | 239 blocks, ≈ 163 correct ✅ | **232** — −8 colophon, +1 guard fix; **no served text changed** | batch 2 |
| — served share | OLD served everything it had | **239 of 378 = 63 %** | 232 of 367 = 63 % | learning blocks, batch 2 |
| **OVER-WITHHOLD ↓** | round 4 **12/30 = 0.400** | **19/30 = 0.633** [0.455, 0.781] ❌ | 19/30 unchanged; 1 of the 19 restored | reviewed withheld regions |
| **RESTORE PRECISION ↑** | not measured | **3/6 = 0.500** [0.188, 0.812] ⚠️ | 3/6 transferred · the one NEW restore **0/1, wrong** | guard-change restores; no text repairer reached this path |
| **ATTACHMENT** (added — the class A1 closed) | OLD 2/43 = 0.046 | 5/8 = 0.625 rescued | **8/8 = 1.000 rescued** ✅ | batch 1 attachment-WRONG rows |

**Before the merge, two of five moved the wrong way.** After it, **attachment closed completely and
nothing else moved**: the merged build changed no served text on either batch, because Lane A1's
Vietnamese repairers and its structural-group rule live in `repair/run_gold.py` and are not imported
by `tc2_sdm.py` or `tc2_tsl.py`. What reached the lesson-producing path is two guard/attach fixes.

**The two lanes' figures are both right about their own population and must not be summed.** Lane A1
on 54 gold pages / 643 blocks: coverage 0.551 → 0.577, FTR 0.0734 → 0.0701, mutilated structures
7 → 0, 28 restored at restore precision 0.852. Lane D on six legacy lessons: mutilated structures
9 → 9, one restore at precision 0/1. The difference is not disagreement — it is *where the code runs*.

---

## 2. Full row set, BEFORE → AFTER

`—` means *not measured*, never *zero*.

| metric | BEFORE (OLD product) | AFTER (NEW `tc2-p2` post-review) | denominator |
|---|---|---|---|
| false trust (derived, 5 criteria) | 26/42 = **0.619** [0.468, 0.750] | 21/66 = **0.318** [0.218, 0.438] | judged served blocks, batch 2 |
| false trust (annotator's own field) | 20/43 = 0.465 [0.325, 0.611] | 6/67 = **0.090** [0.042, 0.182] | same |
| teaching-critical | 10/21 = **0.476** [0.283, 0.676] | 5/50 = **0.100** [0.043, 0.214] | rows where the class applies |
| display fidelity | 25/42 = **0.595** [0.445, 0.730] | 11/67 = **0.164** [0.094, 0.271] | judged served blocks |
| reading order | 10/22 = **0.455** [0.269, 0.653] | 0/30 = **0.000** [0.000, 0.114] | multi-line rows |
| role | 5/43 = 0.116 [0.051, 0.245] | 10/66 = **0.151** [0.084, 0.257] | judged served blocks — **not better** |
| attachment | 2/43 = 0.046 [0.013, 0.155] | 1/66 = **0.015** [0.003, 0.081] | activities |
| formula / number / unit (tagged) | 5/42 = 0.119 [0.052, 0.250] | 1/67 = **0.015** [0.003, 0.080] | judged served blocks |
| figure / caption (within class, quota) | — (n = 0) | 5/18 = **0.278** [0.125, 0.509] | 20 caption blocks, 4 lessons |
| — caption **detached from its figure** | — (no field existed) | **10/19 = 0.526** | same quota; two rubric readings, see report §2.4 |
| **correct served** | ≈ 30 of 80 blocks | ≈ **163 of 239** blocks | point estimates |
| **wrong served** | ≈ 50 of 80 blocks | ≈ **76 of 239** blocks | point estimates |
| **withheld** | 0 (the product served everything) | **139 of 378 learning blocks = 0.368** | batch 2 |
| **false withheld (over-withheld)** | — | **19/30 = 0.633** [0.455, 0.781] | reviewed withheld regions |
| — withheld regions that **orphan a sibling** | — | **12/139 = 0.086** [0.050, 0.145] | all withheld regions, batch 2 |
| — same, independent holdout | — | **12/126 = 0.095** [0.055, 0.159] | batch 1 re-run, different lessons |
| **restored** | — | **6** of 30 reviewed withheld regions | guard change, not repair |
| — falsely-withheld recovered | — | **4/12 = 0.333** [0.138, 0.609] | of the 12 judged over-withheld |
| — restored that had been a **safe** refusal | — | **2** — both judged WRONG afresh | the dangerous direction |
| **RESTORE PRECISION** | — | **3/6 = 0.500** [0.188, 0.812] | fresh blind judgement of what is served now |
| **coverage — reprocessed** | 6 of 243 (round 4) | **12 of 243 = 4.9 %** | in scope |
| **coverage — trusted** | 0 | **0** | no Founder threshold record exists |
| **coverage — eligible for teaching** | 0 | **0** | requires trusted ∧ a teaching authorisation |

---

## 2a. Provenance of the artefacts these numbers rest on

| question | answer |
|---|---|
| does the stored `tc2-p1` attach artefact reproduce from current code? | **No** — 950 of 6,176 page verdicts differ across 38 books (15.4 %); 54 explained by the named end-matter rules, **896 unexplained**, 874 of those moving a page to a different lesson |
| do the batch OLD/NEW comparisons in this report use it? | **No.** `run_batch.py` regenerates attach into the batch's shadow root as step 1 |
| does the pack rebuild use it? | **Yes** — `lesson_attach.TC2_ATTACH_DEFAULT` hard-codes `poc-out/trusted-corpus/tc-v2/tc2-p1/attach` |
| does that change what ships? | **No** — rebuilding all 12 packs against freshly regenerated attach leaves **207/207 activities unchanged and 12/12 contentHash identical**. It moves the *diagnosis* only (repaired starts 17 → 18 and 0 → 1; grade-5 flagged rows 22 → 19) |

The stored files are `tc2-p1`, written by round-3-era code, and read as current by a hard-coded path
three rounds later. It is harmless today by luck, not by design, and `buildProvenance` cannot say
which attach a pack used. **Provenance decision for the Founder:** pin it (record the attach dir, its
pipeline id and a content hash in `buildProvenance`, fail closed when absent) or regenerate per build
and drop the default. Lane D recommends pinning and did not implement it — it changes the pack
manifest schema the Dart side parses.

---

## 3. The shipped surface (packs), BEFORE → AFTER

| metric | BEFORE | AFTER | note |
|---|---|---|---|
| packs passing `pack_provenance verify` | **0 / 12** | **12 / 12** | `attachmentRule` stamped `capped-toc-v1` while the code said `v2` |
| pack activities | 248 | **207** | −41 |
| INFERRED geometry-rebuilt expressions shipped **without provenance** | **41** | **0** | Founder §3 — fail closed |
| lessons whose exercise list is now empty | 0 | **10** | every `toanExercises` entry in the corpus was INFERRED |
| imprint / back-matter activities in the packs | 0 | **0** | defect 6 does not reach the pack path |
| activities past their book's last lesson start | 1 | **0** | it was itself an INFERRED expression |
| content delta of the **provenance** rebuild | — | **0 of 248** (12/12 grades byte-identical) | the rule change is diagnostic-only by design |
| flag-level restore precision of that delta | — | **27/27 = 1.000** [0.875, 1.000] | blind badge reading; 4 rows unjudgeable |

**−41 activities is a coverage loss that is a correctness gain** and is reported as such, not hidden:
the product used to serve 41 expressions it had reconstructed from geometry, one of which round 3
caught serving `2/5 + 1/4` for the printed `2/5 − 1/4`.

---

## 4. Regression corpus — named defects, per build

| defect | round 4 `tc2-p2` | round 5 `tc2-p2r` |
|---|---|---|
| R1 imprint page served as the last lesson's body | PRESENT | **PRESENT** — and now confirmed on a **second book** (Toán 4 tập một Bài 37, colophon p133) |
| R2 fraction fragment served (`b) 10 +`) | PRESENT | **PRESENT** |
| R3 tone slips in the lesson title | PRESENT | **PRESENT** |
| R7c verse joined into prose | CHANGED | **PARTIAL** — 7 regions withheld by `line_structure`, 1 stanza still served joined |
| defect 6 on the **shipped packs** | not asked | **ABSENT** |
| defect 8 orphaned siblings | not measured | **9** structures (batch 2) · **13** (holdout) |

After merging Lane A1 (`tc2-p3`):

| defect | `tc2-p2r` | **`tc2-p3` (A1 merged)** |
|---|---|---|
| R1 imprint page served as the last lesson's body | PRESENT | **FIXED** — p121 unattached; the class also closed on the second book (tail-scan 1/6 → **0/6**) |
| R2 fraction fragment · R3 tone-slipped title | PRESENT | **PRESENT** — unchanged |
| R7c verse joined into prose | PARTIAL | **PARTIAL** — unchanged |
| defect 8 orphaned siblings | 9 · 13 | **9 · 13 — unchanged**; the Founder's own option group is byte-identical |
| `chem_guard` false positive | 1 region withheld | **released — and the released block is wrong** (`II` → `I1`, watermark spliced) |

---

## 5. What this scoreboard does not say

- It sets **no threshold** and makes **no teaching claim**. `trusted` = 0, `eligible for teaching` = 0.
- It does not average the five directions into one number. Two of them moved the wrong way and a mean
  would hide that.
- OLD and NEW are **different block sets**. What is comparable is the share of what each side served
  that is wrong, always read beside how much each side served.
- An **empty** cell is not a zero. `RESTORE PRECISION` is empty for batch 2 because no restore stage
  ran there; that is a different fact from "no restores were correct".
- The rates come from small samples judged by one annotator per side. The intervals are wide on
  purpose.
- **A withheld block is not automatically a safe one.** Since round 5 a withhold that orphans a
  sibling is counted teaching-critical, so the "coverage cost" of a guard and its "error rate" are no
  longer separable in the way round 4 assumed.
