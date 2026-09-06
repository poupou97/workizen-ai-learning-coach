# SUPERSESSION CONTRACT — WAL-213

**Status: PREREQUISITE DELIVERED, WITH A NEGATIVE HEADLINE THAT IS THE POINT.**
Not a round. No threshold activated, nothing served, `trusted = 0` and `eligible for teaching = 0`
unchanged. Branch `wal-213/supersession-contract`, based on `main` @ `4718dfa`.

---

## 0 · The one-paragraph answer

A recovered observation can now **replace** a destroyed one instead of sitting beside it, and the
replacement is a **relation** — the original observation carried whole and never written to, the
superseding observation, the engine, the agreeing scales, the region and stacking evidence, and a
disposition **derived from geometry rather than declared by a caller**. Measured on the real
population — the 17 recovered fraction regions of Toán 4 Bài 61 p081–083, reproduced line for line
from round 7's own run — **the honest number did not move: `10 → 10, Δ 0` on repaired blocks
becomes `2 → 3 → 2` proposals across BEFORE / ADD / SUPERSEDE, and not one recovered digit produced
a well-formed repaired block.** What changed is that the **contradiction is now named and refused
rather than concatenated**: the single block the round-7 ADD path "improved" produced the malformed
`0) 1 3 8/14 2/7`, and the contract refuses it, along with 7 others, with a reason an auditor can
read. And the reason the number is still zero is now **measured and attributable**, which it was
not before: **13 of 17 recoveries would have to overwrite a source observation to stand.**

---

## 1 · What supersession means here

**A supersession is a relation between observations, not a mutation of one.**

`tool/corpus/repair/supersession.py`. It carries, per the ticket, all six required things:

| required | where it lives |
|---|---|
| the original observation, never overwritten | `superseded` — round 5's frozen `model.Observation`, carried whole; `assertIs` in the tests |
| the superseding observation | `superseding` — the same type, from a **different** `source` |
| the engine that produced it | `engine`, which must equal `superseding.source`; a source may not supersede its own observation |
| the agreeing scales | `region.agreeing_scales` — `{box kind → the scales that returned the same string}` |
| the region / stacking evidence | `region` — the crop boxes actually read, the bar, and `stacking_scale`: the scale at which the whole-region crop showed the two halves **stacked** |
| a disposition | `disposition` — **derived**, not passed in (see §2) |

**Nothing was invented.** `Observation`, `RepairCandidate`, `ValidationResult`, `Signal`, `Verdict`
and every disposition string are round 5's own types, imported. `SUPERSEDED` already existed in the
doctrine (`model.Disposition`, round 5 §14) and was **unused for this purpose**; this is what uses
it. `CONFLICT` — "signals contradict each other and neither side is decisive" — is the other one,
also already in the frozen set. Round 6 refused to build a fourth provenance universe; this refuses
too, and a test feeds `ValidatedRepair` a dict that serialises identically, a duck-typed stand-in
that answers every question, and a string, and requires all three to be refused.

### The three coverage outcomes

A destroyed observation is not always the same shape as the region that recovered it.

```
FULL      the superseded ink lies inside the crop the recogniser read  ->  SUPERSEDED
PARTIAL   printed ink remains outside it                               ->  CONFLICT   (fail closed)
NONE      nothing was observed there at all                            ->  not a supersession
```

**PARTIAL is the important one and it is a refusal.** Cutting a token down to the part the crop
covers is *editing a source observation*, which round 5 forbids outright. So both readings leave the
current view, the region is undecided, and **the block that holds it is refused**. The contradiction
is recorded, attributable and visible to an auditor; it is invisible to a validator.

**NONE is refused as a supersession by construction.** `Supersession` requires at least one
superseded observation. A recovered value with nothing behind it is an **ADDITION**, and calling it
a supersession is exactly how an invented value acquires the authority of a replaced one. (On Bài 61
there are **0** additions — every recovered region had at least a fragment of a page-pass token over
it. That is a measurement, not an assumption.)

### What the resolution answers

`ObservationSet.resolve()` returns, for one block: `current` (what a validator reads), `superseded`
(audit-only), `conflicted` (undecided), and `usable` — **False whenever any region is undecided**,
because a block holding one undecided contradiction is a block whose text nobody can name.
`current_for(region_key)` returns **exactly one** observation or raises; it never returns "the first
one". Two supersessions of the same observation are combined **by area**, never by order; two
*overlapping* replacements of the same observation raise rather than being ordered; a cycle raises;
and `assert_conserved()` proves every observation lands in exactly one bucket.

---

## 2 · What this does NOT authorise

- **No threshold was activated.** Nothing in this branch can produce `Disposition.TRUSTED`.
  `servable` is a **property returning `False`**, not a field, on both the Python and the Dart type,
  so no JSON can set it; `from_json` raises `TrustEscalation` on `servable: true` or a `TRUSTED`
  disposition, on both sides.
- **`CONNECT ≠ TRUST`.** A superseded-then-recovered block does **not** become servable. `trusted = 0`
  and `eligible for teaching = 0` are unchanged, and the round-7/round-6 served set is untouched:
  this work adds no path from a recogniser to a rendered string.
- **A caller may not declare a partial replacement clean.** `disposition` is a derived property;
  there is no argument, field or setter for it. The mutation `coverage always FULL` kills 8 tests.
- **No constructor from a presentation form.** There is `from_json`, which reads exactly what
  `to_json` wrote and requires the whole trace. There is no `from_text`, `from_line`, `from_reading`,
  `from_latex` or `from_summary`, and a test asserts each is absent.
- **No value reaches a block.** The block projection is an **allowlist** of ten keys — id,
  disposition, a count, an engine, a coverage class and four booleans. A denylist would only close
  the doors somebody thought of; the allowlist closes the ones nobody has.
- **`study.py` is unmodified**, so round 5's and round 7's projections still come out of the code
  that produced them.

---

## 3 · The measurement — BEFORE → ADD → SUPERSEDE

**Population: Toán 4 tập hai, Bài 61, p081–083.** The 4-scale ladder `(6, 10, 14, 20)` frozen in
`vision.DEFAULT_SCALES`. The run reproduces round 7's own `study-dev.log` line for line:

```
p081  regions=15  recovery_read=1   control_same=5   control_differs=0
p082  regions=30  recovery_read=4   control_same=6   control_differs=0
p083  regions=40  recovery_read=12  control_same=10  control_differs=0
                  --------------
                  17 recovered · 47 recovery regions · 38 controls · 0 control disagreements
```

**The BEFORE and ADD columns are not re-implemented, they are re-derived and checked.**
`assert_add_column_reproduces_round7()` compares all 44 block projections against `study.py`'s own
output and refuses to publish otherwise. **44/44 reproduce.**

> That guard earned itself within the hour. The first version of the driver read `study.py`'s
> `bbox=[x, y, w, h]` as `(x0, y0, x1, y1)`. Every token was still a token, every block still had a
> verdict, and the ADD column quietly went **3 → 2** proposals. *A number that is the right type and
> the wrong quantity passes every check that is not a re-derivation* — round 7's own finding, met
> again, in this work, on the first try.

### The relations

| | count |
|---|---|
| recovered regions | **17** |
| supersessions built | **17** |
| additions (nothing to replace) | **0** |
| **resolved** — FULL coverage → `SUPERSEDED` | **4** |
| **refused** — PARTIAL → `CONFLICT` | **13** |
| observations superseded | 6 |
| observations left conflicted | 16 |

Refused by class: **DIGIT_LOSS 7 · SEGMENTATION 6.** Resolved by class:
**FRACTION_STRUCTURE 2 · DIGIT_LOSS 2 · SEGMENTATION 0.**

Coverage fractions of the 13 refusals: `0.05 0.06 0.07 0.07 0.33 0.34 0.43 0.44 0.46 0.48 0.51 0.52
0.55`. **None is near the line.** These are not borderline cases a looser threshold would rescue:
the destroyed observation carries an item letter (`0)`), an operator, or a neighbouring fraction's
digit, and half of it or more is printed content the crop never read.

All 4 resolved relations had **≥ 2 agreeing scales and a stacking observation**; none of the 13
refusals was refused for want of agreement. **The recogniser was not the limiter here — the geometry
of the destroyed observation was.**

### The blocks — the honest number

| blocks (of 44 carrying a fraction region) | BEFORE | ADD | SUPERSEDE |
|---|---|---|---|
| carrying a proposed value | **2** | **3** | **2** |
| refused with a named reason | 0 | 0 | **8** |

**Does a recovered digit now reach a repaired block? NO. Zero. `Δ 0` stands.**

What changed:

- The **one** block the ADD path changed is `04-sgk-toan-4-tap-hai:p083:tc2-p3:012`, whose text went
  from nothing to `0) 1 3 8/14 2/7` — the destroyed `0) 1 3` **plus** the two recovered fractions,
  glued in x-order. Under the contract it is **REFUSED_UNRESOLVED_SUPERSESSION**. *A malformed
  concatenation is worse than a refusal, and the contract turns one into the other.*
- **8 of 44 blocks** are now refused with a reason, instead of silently holding two contradictory
  readings.
- **2 blocks** hold only resolved supersessions. Neither becomes proposable, and the reasons are new
  and specific:
  - `p083:tc2-p3:010` — the region resolved cleanly (`3` and `18` replaced by a crop reading at
    coverage 1.00), but the **SDM block boundary contains only the numerator**; the denominator is
    in another block. `math_line_candidate` returns `no_surviving_token`. **The next limiter is
    segmentation of the block, not of the glyph.**
  - `p083:tc2-p3:077` — one region resolved, but a **second region in the same block was never
    recovered** (`denominator_token_missing`), so the line is still incomplete. **Partial recovery
    of a block is not recovery of a block.**

---

## 4 · PLANNED vs ACTUAL

| # | Planned | Status | Actual |
|---|---|---|---|
| 1 | A typed contract by which one observation replaces another | **DONE** | `repair/supersession.py`; `RegionEvidence` · `Supersession` · `ObservationSet` · `Resolution`; reuses round 5's frozen types throughout |
| 2 | Carry original observation · engine · agreeing scales · region evidence · disposition | **DONE** | all six, with `disposition` derived from geometry; `assertIs` proves the original object is carried, not copied or edited |
| 3 | A recovered region that is correct produces a block whose text CHANGES | **FALSIFIED on this population** | 0 of 44 blocks. The mechanism works — 4 regions resolve and the recovered reading becomes the current observation — but no block becomes proposable. §3 says why, per block |
| 4 | The trust decision reads exactly one current observation per block | **DONE** | `Resolution.current_for(region_key)` returns exactly one or raises; superseded is audit-only; tested both ways |
| 5 | A superseded observation can never silently become the served text | **DONE** | `servable` is a property returning False on both sides; `TRUSTED` unreachable; the block projection is a ten-key allowlist with no text field; the bridge and the Dart type each refuse independently |
| 6 | Population-adequacy guard: the suite goes red if the fixture contains no supersession case | **DONE** | `assert_population_adequate` — red on empty, on all-clean, on all-refused, on nothing-changed; and the *real* census was degenerated four ways, killing 3–10 tests each time |
| 7 | Expressible end to end: recogniser → block record → trust decision → app | **DONE** | `recognition/supersede.py` → `ValidatedRepair.supersession` → `tsl_to_lesson_document` → Dart `SupersessionRef` |
| 8 | Round-trip test asserting nothing strengthens | **DONE** | Python and Dart; the WAL-213-specific axis is that **the audit set may not shrink** |
| 9 | Mutation-check every test | **DONE** | 20 mutations, 20 killed. One SURVIVED first and is now covered (§6) |
| 10 | Report the before→after honestly | **DONE** | §3. The number did not move, and it says so first |
| — | Make the 13 refusals resolvable | **DEFERRED** | It needs a **recogniser** change, not a contract change (§7). Deliberately not attempted here |
| — | Run on any population but Bài 61 | **NOT STARTED** | See §8 |

**Nothing was promoted from PARTIAL to DONE.** Item 3 is recorded as **FALSIFIED**, not as a
partial success: the acceptance criterion as written did not hold on the real population, and the
contract is delivered anyway because the ticket's own reasoning — *measuring WAL-214 and WAL-215 on
blocks holding two contradictory texts measures the wrong thing* — is satisfied either way.

---

## 5 · PROVEN · FALSIFIED · STILL HYPOTHESIS

### PROVEN

- **A recovered observation can replace a destroyed one without overwriting it.** 4 of 17 on Bài 61;
  the original object is carried whole and is byte-identical after the relation is built, serialised
  and read back.
- **13 of 17 recoveries on Bài 61 cannot replace what they read without destroying printed content.**
  Coverage `0.05 … 0.55`, none near the line. This is a *property of the destroyed observations*,
  measured, not a tuning choice.
- **The round-7 ADD path produced exactly one block-level change on Bài 61, and it was malformed.**
  Reproduced at 44/44 blocks, then refused by the contract.
- **The contract's refusals are decidable from geometry alone** — no threshold, no confidence, no
  model. `FULL_COVERAGE = 0.98` is a statement about rounding in normalised bboxes, not a knob.
- **Every guard in this work goes red for the right reason.** 20 mutations, 20 killed.
- **The population contains the failing case** — and the suite proves it by degenerating the real
  census four ways and requiring each to fail.

### FALSIFIED

- **«A supersession contract makes a recovered digit reach a repaired block.»** It does not. Not one
  of 44. The prerequisite was necessary and is not sufficient, and the ticket's acceptance criterion
  as written is not met on this population.
- **«The recogniser's 17/17 accuracy is the thing standing between recovery and repair.»** No: all
  four resolvable cases had ≥ 2 agreeing scales *and* a stacking observation, and the 13 refusals
  were refused for geometry, not for disagreement. Accuracy was never the limiter on this page.
- **My own first re-derivation of the ADD column.** 3 proposals became 2 because a token bbox was
  read in the wrong coordinate form. Caught by re-derivation, not by any test of shape.

### STILL HYPOTHESIS

- **That the FULL/PARTIAL split is ≈ 4/13 anywhere but Bài 61.** One lesson, three pages, one book,
  one grade, one failure family. HOLDOUT-3's 23–27 recoveries have never been put through this.
- **That resolving the two remaining blockers (`no_surviving_token`, a second unrecovered region)
  would move the number.** Plausible, unmeasured, and the second is a *coverage* problem, not a
  contract problem.
- **That re-reading the residual would convert the 13.** See §7 — the mechanism is clear and the
  false-recognition cost is not known.

---

## 6 · How the tests were checked

**75 Python tests** (`tool/tests/test_supersession_contract.py`) + **11 corpus-gated**
(`test_supersession_population.py`) + **19 Dart** (`test/core/lesson_model/supersession_ref_test.dart`).
Full suites: **Python 952 OK** · **`flutter analyze`: No issues found** · **`flutter test` 1084 OK**.

**20 mutations applied, 20 killed:**

| target | mutation | result |
|---|---|---|
| `supersession.py` | coverage always FULL · empty superseded allowed · partial keeps both current · round-trip guard a no-op · population guard a no-op · area fraction always 1.0 · empty evidence bag constructs · same-source supersession allowed · `servable` returns True · overlap check disabled · acyclic check disabled · «no supersession needed» accepts emptiness · audit set may shrink | **13 killed** |
| `validated.py` | supersession dropped from `to_json` · laundering guard disabled · inner strengthening guard disabled · type check removed | **4 killed** — the last **SURVIVED** first |
| `tsl_to_lesson_document.py` | allowlist disabled · disposition check disabled · forbidden keys shrunk to round 6 | **3 killed** |
| the **census itself** | emptied · only-resolvable kept · only-refused kept · refusals rewritten as proposals | **4 killed** (3–10 tests each) |

**The survivor is worth recording.** Removing the check that keeps a look-alike out of
`ValidatedRepair.supersession` broke nothing, because every test was passing the real type. A dict
that serialises identically and a duck-typed object that answers every question would both have been
accepted — *a fourth provenance universe entering through a place no test was looking*. Now tested
with a dict, a stand-in and a string.

**Two tests failed first for the right reason and were fixed rather than weakened:**

1. the round trip is stable **on disk**, not in memory — round 5 deep-freezes provenance to tuples,
   which return from a file as lists. The property that matters is *save, load, save is stable*, and
   that is now what is asserted.
2. «the reading never reaches a block» was a substring search, and a one-character reading like `4`
   occurs by coincidence inside a region key. It is now a **key allowlist plus a type/enum check** —
   the block form has no free-text field at all — which is strictly stronger.

**On absence.** `test_supersession_population.py` skips where the corpus is absent (D4: SGK
derivatives never enter git). The skip is not allowed to look like a pass: the reason names the
missing file and says `THIS IS A SKIP, NOT A PASS`; a **present-but-empty** artefact FAILS; the
structural population is **committed** (`tool/tests/data/wal213-bai61-population.json` — no SGK text,
no readings, no values, no geometry) so a clean clone still tests against the real distribution; and
on the one machine that holds the corpus, the committed census is **re-derived and compared**, so
structure and measurement cannot drift apart.

---

## 7 · Why the 13 refusals are a recogniser problem, not a contract problem

The destroyed observation `0) 1 3` covers two recovered regions and also carries the item letter
`0)`. Three ways to handle it:

1. **Replace it wholesale** — deletes the item letter. This is a silent loss of printed content, and
   round 7 already recorded that *«the option letters A.–D. are restored after `agreement()` runs —
   the one part that identifies the answer is the part no agreement measurement covers.»* Refused.
2. **Trim it to the covered part** — edits a source observation. Refused by round 5's standing rule,
   which this contract exists to keep.
3. **Re-read the residual** — ask the crop recogniser for the box the two recovered regions do *not*
   cover, and let its answer be an observation in its own right. Then the supersession is total by
   construction, because every part of the destroyed token has been independently re-read.

**(3) is the only honest route, and it is a change to `recognition/`, not to the contract.** It is
deliberately not attempted here: it would raise recall and it has an unmeasured false-recognition
cost, and this ticket must not silently become a recogniser round. The contract is already shaped
for it — `ObservationSet` combines several regions' coverage by area and reaches `FULL` when they
together cover the observation, and there is a test for exactly that shape.

---

## 8 · What remains unverified

- **Everything outside Bài 61.** One book, one lesson, three pages, 17 relations. The FULL/PARTIAL
  split, the class distribution and the block-level zero are all single-population facts. **The
  frozen blind populations (`BLIND-CORE`, `BLIND-TEACHING`) have not been touched by this work**,
  deliberately: they are for measuring a *signal*, and this is a contract.
- **The exponent, Roman-numeral and Ω classes.** The contract is class-agnostic, but only the
  fraction recogniser has been wired to it. `Ω → S2` remains outside every engine's repertoire and no
  supersession helps.
- **The app path is unit-tested, not device-verified.** `SupersessionRef` is proven by 19 Dart tests
  and `flutter analyze`; **no device walk was performed and no Golden artefact was regenerated.**
  TECHNICALLY VALIDATED ≠ HARDWARE VERIFIED.
- **No TSL was regenerated carrying a supersession.** `tsl_projection.project()` is untouched: it
  will carry the field the moment a `ValidatedRepair` holds one, and no ledger yet does, because no
  validator has been wired to the recogniser's candidates. **That is the next joint, and it is
  small.**
- **`FULL_COVERAGE = 0.98` and `TOUCH_COVERAGE = 0.05`** are geometric constants that have never been
  swept. On this population nothing sits near either (0.55 is the highest refusal, 1.00 the lowest
  acceptance), so no result here depends on them — but that is a property of this population.

---

## 9 · Files

| file | what |
|---|---|
| `tool/corpus/repair/supersession.py` | the contract |
| `tool/corpus/recognition/supersede.py` | recogniser row → relation; token resolution |
| `tool/corpus/recognition/supersede_study.py` | the BEFORE/ADD/SUPERSEDE measurement + census writer + the round-7 reproduction guard |
| `tool/corpus/repair/validated.py` | `ValidatedRepair.supersession`, and the laundering axis |
| `tool/corpus/tsl_to_lesson_document.py` | forbidden keys + the block-projection allowlist |
| `lib/core/lesson_model/repair_record.dart` | `SupersessionRef` |
| `tool/tests/test_supersession_contract.py` | 75 tests, contract + real census |
| `tool/tests/test_supersession_population.py` | 11 tests, corpus-gated, value level |
| `test/core/lesson_model/supersession_ref_test.dart` | 19 tests |
| `tool/tests/data/wal213-bai61-population.json` | the committed, D4-safe census of the real population |

Reproduce:

```
python3 tool/corpus/recognition/study.py dev                 # Apple Vision, macOS, needs the corpus
python3 tool/corpus/recognition/supersede_study.py <study.json>
python3 -m unittest discover -s tool/tests
flutter test test/core/lesson_model/supersession_ref_test.dart
```

The measurement artefacts live in `poc-out/round7/wal213/` and are **gitignored**: they carry
verbatim SGK readings. **No SGK page, crop or reading was committed by this work.**

---

`trusted = 0` · `eligible for teaching = 0` · **CONNECT ≠ TRUST** ·
**TECHNICALLY VALIDATED ≠ HARDWARE VERIFIED ≠ DISTRIBUTION RIGHT.**
