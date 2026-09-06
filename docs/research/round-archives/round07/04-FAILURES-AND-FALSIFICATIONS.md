# 04 · FAILURES AND FALSIFICATIONS

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.** Short verbatim SGK fragments below are quoted for
> defect attribution under Founder rule **D4**.

Round 7 met four gates and left the fifth deliberately unattempted. **What it disproved is the
round's actual product** — including three of the coordinator's own statements to the Founder, one
claim by each of two workstreams, and the premise the whole round was built on.

---

## 1. THE PREMISE OF THE ROUND, FALSIFIED BY THE ROUND

**Status: FALSIFIED. Label: MEASURED on 643 rows / 354 served / 54 deliberately hard pages.**

> **«A trust threshold is the thing standing between the pipeline and a trusted slice.»**

**It is not.**

- **All 12 teaching-critical errors reduce to two mechanisms** — digit corruption (6), and a
  non-question served as a question (6).
- **Neither is visible to any signal a gate can read.** **3 of the 6 digit corruptions survive
  character-exact agreement between two independent OCR stacks**, the role-confidence floor, the
  figure refusal, the order check and the subject exclusion. **They pass everything.**
- **No available combination of signals bounds teaching-critical error below ≈0.021** at any
  coverage — 0.0233 at 36 % of served, best **0.0213 at 53 %**.
- The gap between that and a 90 %-clean-lesson promise (**0.0035**) is **a factor of six**.

> **The blocker is recognition and role disambiguation, not calibration.** Round 7 built the gate
> correctly and then measured that the gate was never the thing in the way.

**This is what a well-run round looks like when the answer is no.** The machinery is built, frozen,
tested and refusing; the recommendation predicts its own truthful zero; and the finding that
matters is that *the next round must go somewhere else entirely.*

---

## 2. THREE OF THE COORDINATOR'S OWN STATEMENTS TO THE FOUNDER

**Recorded in the open, per the standing rule.**

### 2.1 «The cheapest win on the board» — wrong, and wrong in a diagnosable way

Round 6 called the 118 blocks *«a model gap, not a data gap, and the cheapest win on the board»*,
and **the coordinator relayed that to the Founder without measuring it.**

**Measured: it is not a win at all.** A servable type is recommended for **zero**; **114 of the 118
gain nothing** (exactly **one** structural group across 238 lessons contains a gap block, so the 64
footnotes and 50 activity blocks belong to **no group**); and **adding all three types removes 1 of
31 mutilations.**

> *«It was never re-derived from leaf records»* — **which is exactly what this round's own permanent
> rule exists to catch.** The rule caught its author.

**Also falsified with it:** round 6's *«these blocks passed every trust gate»*. They passed the
**TSL** gate and became `trustedStructuredLesson` — **a schema label, not a trust grant.**

### 2.2 A rate published without its denominator

Round 6 §4 published **«DIGIT LOSS 312 (57 %) vs SEGMENTATION 196 (36 %)»**. **The denominator, 548,
is missing.** It should read **312 / 548 = 0.569** and **196 / 548 = 0.358**. The percentages are
correct; **the Founder's standing rule since 2026-09-05 is that every metric states its denominator
explicitly, and this one did not.**

### 2.3 A re-derivation that used the wrong field

The coordinator's **first** attempt to re-derive the lesson denominators used field `number`. **The
field is `no`.** It returned **238 and 3,497** and was wrong. *Recorded because the failure mode is
the subject of the document it appears in.*

---

## 3. TWO WORKSTREAMS WITHDREW THEIR OWN CLAIMS

**WS-T withdrew its clustering finding.** It first computed the expected page incidence from the
**median** blocks-per-page (0.082) and reported the observed 0.103 as evidence that errors cluster.
Computing the expectation over the **actual per-page counts** gives **0.0975 against 0.1026
observed** — **the disagreement it was about to record did not exist.**

> ***«Re-derive a number a second way before recording a disagreement» caught this one inside the
> same round.*** *(That rule entered the project because of the round-6 archive's own `toanExercises`
> error. It has now paid for itself twice.)*

**WS-T also corrected its own first framing, in place.** It began by treating A3's round-5
trade-off curve as *the object to pick a point on*. **It is a curve over guard waivers — an axis of
loosening.** A trust threshold moves along the **opposite** axis, restricting the already-served
set. **Reading the A3 curve as a menu of trust thresholds would have produced a policy that serves
new content in the name of trusting it.**

**WS-S withdrew its own anchor count: 22 → 10.** Twelve «anchors» were **other footnote-roled blocks
anchoring each other** — a run of «(1)…(6)» each finding its own number in a sibling that is itself
withheld. **A footnote is never another footnote's referent.** *The exclusion is now in the code with
the reason written next to it.*

---

## 4. THE OPTION LETTERS — the round's sharpest single finding

**Status: PROVEN, from the artefact and the source order.**

```
text_docling : "Kim loại và phi kim"          ← the primary stack's output
text         : "A. Kim loại và phi kim"       ← after enumerator restoration
enumerator_restored : true
agreement    : {"text_sim": 100.0, ...}
```

`agreement()` runs at `tc2_sdm.py:1193`. The enumerator is prepended at `:1221` — **after.** All
four options carry `enumerator_restored: true`.

> **`text_sim = 100.0` certifies «Kim loại và phi kim» and says nothing about the «A.». On a
> multiple-choice question the letter IS the answer's identity, and it is precisely the part no
> agreement measurement covers.**

**And the two stacks do not agree on the order of C and D, with no guard firing** — verifier ids
align **c005, c006, c008, c007**, option C and the trailing directive both mapping to `c008`, while
`order_ok` is `true` for every one. A **2×2 grid** — round 5's two-column linearisation hazard.
*(OBSERVED, not PROVEN: `verifier_pos` is not persisted, and WS-S said so rather than overclaiming.)*

**Every multiple-choice group in the canonical corpus is mutilated. There are two of them, and both
are broken** — one **by the type gap itself**: a served question, four blank cards, then «Hãy chọn
đáp án đúng nhất.»

---

## 5. ADDING THE TYPE WOULD MAKE IT WORSE — a loud failure becomes a quiet one

**Status: INFERRED, from the measured Group A / Group B pair.**

Today a child sees four blank cards under a question: **a child, a parent or a reviewer can see
something is missing.** Add the `option` type and the failure mode changes shape — the day a trust
threshold withholds one option of four (**which already happens in Group B**), the app serves **a
three-option multiple-choice question that looks complete.** A question with a missing distractor
can have no correct answer, or appear to have one when it does not, **and nothing on screen says
so.**

> **The type does not remove the danger; it removes the evidence of it.**

**And «add it only with an all-or-nothing sibling rule» would still be wrong**, because of §4: with
the rule *and* the type, the group becomes a complete, served, four-option MCQ **whose four option
letters are outside every measurement the trust gate makes.** *The rule is a precondition, not a
sufficient condition.*

---

## 6. A GATE THAT WAS GREEN BECAUSE ITS SUBJECT WAS ABSENT

**Status: FOUND AND FIXED.**

`fixture_lineage` **L5** checked *«every crop a block REFERENCES exists»*. A document that
references **none** has none absent — so it printed **`0/0 present · PASS`**, and **round 6 shipped
through it.**

> **The gate was green precisely because the thing it guards was missing** — the same shape as the
> timeline test round 6 had to correct one layer up.

Fixed by **L5b CROP COVERAGE**, which measures the **population** rather than the references, FAILs
when a croppable withheld region has no crop, and **downgrades to UNKNOWN — never to PASS — under
`--allow-missing-crops`**. `CropCoverageTest` rebuilds the very document round 6 placed and asserts
**L5 PASS `0/0` and L5b FAIL `0/17` on the same document.** *That gap is what shipped, and the
assertion is what notices if L5b is ever removed.*

**And the same family, in the validator:** `si_expected_exponent` recorded `NOT_APPLICABLE` whenever
the recogniser produced no candidate, **conflating «no relation printed» (166 lines) with «nothing
to check» (5 lines)** — *one bucket carrying two causes, which is exactly how round 6's «it abstains
on all 171» went wrong.* **It was never abstaining. It was never asked.**

---

## 7. THE SYSTEMIC FINDING — two rounds running, and now four more shapes

Round 6 found three tests encoding synthetic-era optimism. **Round 7 found the same shape in four
more places, and they are not tests:**

1. **`len()` on a keyed container — three independent occurrences across three rounds.** Round 3's
   `subject_family_census.py:143` (whose code comment — *«some packs carry bare ids»* — **was a
   misdiagnosis of this very bug, written into the source as if it were a property of the data**);
   round 3's `second_lesson_candidates.py:240`, which *did* check the shape but **flattened one
   level short**, making `pack_wiring['toanExercises']` **0 for every candidate**; and the round-6
   archive's own count of 10 lessons reported as 10 expressions.
2. **A gate green because its subject was absent** — L5 `0/0 PASS`.
3. **A metric that could not distinguish «not applicable» from «not asked»** — `si_expected_exponent`.
4. **Tests whose populations contained only their own precondition** — the `titleCase` tests were
   fed **only ALL-CAPS strings**, i.e. only the precondition the transform assumes. *A whole-string
   lowercaser is always green when its input has no lowercase left to destroy.* Likewise §6.7's
   round-4 test pins the exact «Đã mở» string but runs on the **synthetic** fixture, where the lesson
   **has** all three ways. **The tests were not missing; the populations were.**

> **A number that is the right type and the wrong quantity passes every check that is not a
> re-derivation.** **That is now enforced in code, not doctrine** — a container lint, a metric
> registry, and 18/18 re-derivations.

---

## 8. THE ROUND DID NOT COMPOSE ON THE FIRST ATTEMPT — and the failure caught the coordinator

**Status: FOUND. Label: MEASURED.**

**WS-M's anti-rot guard** — *«a baselined finding that has disappeared must be removed in the same
commit»* — **fired on its first real encounter and caught the coordinator**, who had repaired the two
round-3 census defects its baseline still asserted were live. **They had worked in parallel.**

**The resolution improved on both positions.** WS-M had deliberately *not* repaired those scripts,
reasoning that changing published-census code changes what a reader finds. It then verified the fix
**behaviourally rather than by reading the diff**, **withdrew the weaker half of its own argument**,
and pointed out that a broken committed command is — **by the round's own Gate A rule** — a metric
that *was never re-derivable*.

**But it kept the concern as a live assertion rather than a note.** Entries were **moved** to a new
`REPAIRED_FINDINGS` record, not deleted, on the principle that **a repair is also a change to what
old numbers mean.** Three new guards make a repaired defect's return **fail by name**.

**And that surfaced a consequence nobody had looked for:** the round-3 second-golden-lesson census
had `pack_wiring['toanExercises'] = 0` **for every candidate** — *a column of zeroes that looked like
absence of data and was absence of flattening.* **Any candidate ranked or dismissed on that column
was ranked on a wrong input.** Round 7 does not lean on that ranking; **round 8 must not.**

**One consequence recorded as a live assertion, not a footnote:** the round-3 census scripts are
repaired, so **the published round-3 census outputs are no longer reproducible from the fixed
code.**

### 8.1 The composition trap this round created, and defused

`assets/fixtures/` is gitignored, so **the fixed Golden #1 does not travel with the branch.** The
main checkout still held round 6's crop-less copy, and **rsyncing it — the standing composition
procedure — re-introduces the defect this round fixed**, with the fixture reading as current
because *its lineage fields are all intact.* **Round 5's stale-fixture trap wearing a new hat.**

It can no longer pass silently — **L5b goes FAIL on the stale copy (`0/17`)** — but the instruction
is stronger than the guard: **regenerate rather than rsync**, and check the line `L5b … 17/17` before
building any APK. **The composition run did exactly that.**

### 8.2 Two process failures recorded rather than tidied away

**WS-M and, in round 5, Lane E2 each destroyed uncommitted work with `git checkout --`.** The
mutation protocol's cp-backup rule exists for exactly this and **has now been skipped twice.**
WS-M's second attempt also **verified each mutation had actually landed before reading its result** —
***a mutation that «survives» because it never applied is not evidence.***

---

## 9. THE HOLDOUT THAT WAS NEVER A HOLDOUT

**Status: FALSIFIED. Label: MEASURED.**

> **«The evidence file's `held_out` flag marks a usable holdout.»**

**It does not.** Lane A3's published curve was computed over **all 643 rows including the 181 marked
`held_out`**, and the published baseline **only reproduces on the pooled set.** *Pooling them spent
them.*

> **The repository contains no pre-existing blind population.** Every annotated set was consumed by
> the derivation, and the 97-row set was not merely measured on but **used in round 5 §8.3 to route
> restores.**

**That is why this round had to freeze two new populations** — and why the honest weakness is stated
in the artefact: **disjointness from the 97-row set is argued, not proven, because that set's rows
do not exist as data.**

---

## 10. OTHER FALSIFICATIONS, EACH WITH ITS CONSEQUENCE

- **«Tightening role confidence buys safety.»** A 0.70 floor moves false trust 0.0734 → 0.0593 and
  teaching-critical **0.0339 → 0.0407 — the wrong way** — while removing **every block of continuous
  prose**, because 0.60 is the fallback meaning *«we could not tell»*. **C2 admits 46 % more content
  *and* has the lower teaching-critical rate; it dominates C1 outright.**
- **«Teaching-critical error ⊆ false trust.»** Of 354 served rows: 7 both, 19 false-trust only,
  **5 teaching-critical only.** **A bound on false trust alone misses them.**
- **«There is a false-trust number for this system.»** The same quantity measures **0.073 · 0.090 ·
  0.365 · 0.650 · 0.727** across five annotated populations — and the reference and audit planes
  **do not even agree on whether teaching-critical error is a subset of false trust.**
- **«Defect 6 is absent.»** Round 6's Lane D measured **the pack surface** (0 of 207). WS-S measured
  **the lesson path** and found **22 imprint blocks served to children today.** **Both are true;
  neither supersedes the other** — *but «defect 6 is absent» must never be quoted without naming the
  surface, or it reads as «defect 6 is fixed», which it is not.*

---

## 11. WHAT IS STILL ONLY HYPOTHESIS

- **That any rate on the reference plane transfers to the corpus.** It is **54 deliberately hard
  pages**. *This is exactly what the blind population exists to test, and it has not been tested.*
- **That 30 trusted blocks per lesson is the right planning figure** — it comes from **one** real
  lesson.
- **That the blind population is disjoint from the 97-row set** — argued from book coverage, **not
  provable**.
- **That the two named machinery gaps would move the bound.** They address **100 % of the *measured*
  mechanisms, which is not the same as 100 % of the mechanisms.**
- That closing defect 6 makes `ActivityKind.activity` safe — **45 of the 50 were never individually
  audited for content**, only for imprint.
- That the group rule's **72-block cost** is acceptable to a child — **nobody has read a lesson with
  it on.**
- That a `footnote_referent` group kind could work with a better anchor rule.

## 12. UNKNOWN

- **The 97-row evaluation set's internal denominators.** It publishes TRUSTED 67 with false trust
  6/67, and separately teaching-critical 5 · display 11 · role 10 — **which sum to 26 against 6
  false-trust rows.** The denominator of those three **is not stated** and the two readings differ by
  **~1.4×**. **A published headline metric with an ambiguous leaf population.** Referred to WS-M;
  **deliberately not used as a bound anchor.**
- Over-withholding under any candidate.
- **What a child does with a trusted block.**
