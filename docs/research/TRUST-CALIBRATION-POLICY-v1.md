# Trust calibration — the candidate policy, the bound options, and a recommendation

Round 7 · WS-T · steps **A** and **B** only · 2026-09-06 ·
**status: FROZEN CANDIDATE. Nothing is activated, nothing is applied, no content is admitted.
`trusted` is still 0 and this document does not change that.**

> Frozen policy `sha256 0dfc503266854b08725a444acd5163c80f35a993cbdc683e001fd43e3e14e69e`
> Blind population `dbadf4ad248b4eb9d6d0b122af8596153f32dab55a011cbd80f4f74bb2f99e03`
> Blind population (teaching scope) `69d1cacc1e8503769fb0495b243c6cc6e1425995c9f320740ac9ac26d3cb1397`
>
> Verify: `python3 tool/corpus/thresholds/freeze.py verify`

**No lesson, book or page identity appears anywhere in this document.** Every trade-off below is
a rate or a count. That is not modesty: it is the artefact-level proof that the policy was frozen
before anyone looked at what it admits, and a test enforces it
(`tool/tests/test_trust_calibration.py::IdentitySuppression`).

---

## 0 · The answer, before the working

**A production trust threshold over the signals this pipeline can read cannot bound
teaching-critical error to a level anyone could describe to a parent.** The best configuration
found admits 53 % of what the pipeline already serves and still carries a teaching-critical rate
of **0.0213** on the reference plane. At the 30 trusted blocks a real lesson delivered in round 6,
that rate means **about half of all lessons would contain at least one teaching-critical error.**

The recommendation is therefore to freeze **candidate C2 under BOUND-2 and run the blind
evaluation expecting it to fail** — because predicting the outcome before measuring it is the
only thing that distinguishes a calibration from a selection, and because the pre-existing
evidence predicts a truthful zero. The alternative that the arithmetic does support is not a
better threshold; it is **per-lesson certification of a bounded slice**, which is not a threshold
at all.

---

## 1 · What shape a trust policy has — the substantive decision of this round

Round 5's `gate.py` parameterises **how much to loosen**. Every scenario on Lane A3's curve is a
set of guards *waived*, and its axis is coverage. That instrument answers «what does each guard
cost?». It is the wrong instrument for «what may be called TRUSTED?».

Round 6 fixed the vocabulary: `VISIBLE ≠ SERVED`, and `trusted` is 0 by construction. What a
threshold decides is which of the blocks the pipeline **already serves** may additionally be
called trusted. So every candidate here is

```
TRUST  =  SERVED  ∩  admit(...)
```

with SERVED computed by the **unchanged** pipeline gate. Three consequences, each enforced in
code rather than promised in prose:

1. **Activation cannot serve one new block.** `trusted ⊆ served`, so round 6's «the served set is
   byte-identical before and after, in every population» survives activation *by construction*
   and acceptance gate E cannot regress. Property-tested over randomised rows.
2. **A waiver can never produce trust.** Waiving a guard validates nothing. No clause in the
   module removes a guard; there is no code path that could.
3. **A repair is not a trust source.** `REPAIRED ≠ TRUSTED`, `RESTORED ≠ TRUSTED`,
   `VALIDATED REPAIR ≠ TRUSTED`. The `no_repair` clause is inserted into every candidate by
   `normalise()` whether or not the author wrote it.

A clause may only ever **refuse**. `admits()` returns a refusal list, never a score, because
round 4 falsified `OCR_A == OCR_B ⇒ TEXT == TRUE` and §4 below contains a measured instance of
that falsification surviving every signal a gate can read.

---

## 2 · The evidence each candidate is derived from

| Evidence | What it contributed | Where |
|---|---|---|
| Lane A3's round-5 trade-off curve | the guard-cost table, the two guard classes, the finding that OCR confidence carries no information and that role confidence is a step function | `TRUST-GATE-SENSITIVITY.md` §2–§4 |
| Lane A3's frozen evidence rows | the reference plane, re-decided under trust policies instead of guard waivers | 643 rows, 54 hard pages |
| The round-5 97-row evaluation set | defect 8 (structural siblings), the over-withhold pool, the two Vietnamese/STEM defect families | `ROUND5-AUDIT-97-EVALUATION-SET.md` |
| The round-3 and legacy false-trust audits | the shipped-content reference points, and the plane disagreement of §5 | audit plane |
| Round 6's accounting | `trusted: 0` as a type invariant, the served-set invariant, the 30-block real lesson used as the planning figure for L | `ROUND6-CONSOLIDATED-REPORT` §1 §3 §7 |
| `THRESHOLDS.example.json` scenario F + TC-19 #3 | the question surface needs its own, tighter gate, and its precision requirement is already not met | round 5 |

**Nothing new was extracted, annotated or measured to produce a candidate.** The derivation
re-decides rows that already existed, and reproduces round 5's published baseline exactly —
643 rows, 354 served, coverage 0.5505, 26 wrong, FTR 0.0734 — which is asserted as a test.

---

## 3 · The candidates, and what they would cost

Measured on the reference plane. **That plane is 54 deliberately hard pages, not a sample. No
rate below transfers to the corpus, and none is offered as a corpus estimate.**

| candidate | trusted | share of served | false trust | ≤ 95 % | teaching-critical | ≤ 95 % | harm (union) |
|---|---|---|---|---|---|---|---|
| **served, today** (reference) | 354 | 1.000 | 0.0734 | 0.1054 | 0.0339 | 0.0583 | 0.0876 |
| **C0 · NULL** | 0 | 0.000 | — | — | — | — | — |
| **C1 · NAVIGATION-ONLY** | 129 | 0.364 | 0.0310 | 0.0770 | 0.0233 | 0.0661 | 0.0543 |
| **C2 · PROSE** | 188 | **0.531** | 0.0372 | 0.0749 | **0.0213** | **0.0534** | 0.0532 |
| **C3 · QUESTION SURFACE** | 37 | 0.105 | 0.0270 | 0.1382 | 0.0270 | 0.1382 | 0.0270 |
| **C4 · + machinery that does not exist** | — | — | \* | \* | \* | \* | \* |

\* C4 names two clauses with no implementation. `policy.evaluate` marks its numbers
`MEASUREMENT_INVALID` rather than publishing a rate that silently assumes the missing machinery
works, and `apply.py` refuses to run it at all.

**C2 dominates C1.** It admits 46 % more content **and** has a lower teaching-critical rate. The
only difference between them is the role-confidence floor — and that floor is not a safety dial:

> Raising role confidence to 0.70 moves false trust 0.0734 → 0.0593 and moves the
> **teaching-critical rate 0.0339 → 0.0407**, in the wrong direction, while removing **every
> block of continuous prose**, because 0.60 is the fallback confidence that means «we could not
> tell what this is». What survives a role-confidence floor is the part of a page that teaches
> least.

C1 is retained as a candidate anyway, because the choice between «only navigational furniture» and
«prose too» is a product decision, not a measurement.

**C3 is not available and was not available before this round started.** TC-19 #3 requires
QUESTION precision ≥ 0.95 before an auto-labelled question is graded; Lane A3 measured 0.903 at
n = 72. A question surface is out of scope for a first trusted slice regardless of any bound.

### What each candidate refuses, and why the numbers are small

For C2, of the 354 served rows: 78 refused for an interactive role, 46 for mathematics, 31 for
inexact two-stack agreement, 27 for figure dependence, 14 for a moved block. **The largest single
refusal is a role decision, not a fidelity one** — which is a way of saying that a trust threshold
over these signals is mostly a decision about *what kind of thing* to trust, and only marginally
about *how well it was read*.

### The child-facing translation, which the block rates hide

| candidate | pages carrying trusted blocks | median trusted blocks/page | **P(page has ≥1 teaching-critical)** | P(page has any harm) |
|---|---|---|---|---|
| C1 | 36 | 3 | 0.083 | 0.139 |
| C2 | 39 | 4 | **0.103** | 0.179 |

A lesson is several pages. Re-derived a second way from the block rate under independence:
`1 − (1 − 0.0213)^4 = 0.082` against 0.103 observed — the observed figure is *worse* than
independence predicts, which is the expected direction, because errors cluster by page.

---

## 4 · The finding that decides the recommendation

**All 12 teaching-critical errors in the served set fall into exactly two mechanisms:**

| mechanism | count | can a threshold see it? |
|---|---|---|
| digit corruption | 6 | **no** |
| a non-question served as a question | 6 | **no** |

And of the 6 digit corruptions, **3 survive character-exact agreement between two independent OCR
stacks** — both stacks read the same wrong digits. Those 3 also survive the role-confidence floor,
the figure-dependence refusal, the order check and the subject exclusion. **They pass every signal
a gate can read.** This is round 4's falsification of `OCR_A == OCR_B ⇒ TEXT == TRUE`, observed
not as a caution but as three specific blocks that no threshold in this repository can refuse.

Two further consequences of the same measurement:

- **Teaching-critical error is not a subset of false trust.** Of 354 served rows: 7 are both,
  19 are false trust only, **5 are teaching-critical only** — a corrupted digit in a short line
  does not reach the character-error rule that defines «wrong». A bound expressed on false trust
  alone would have missed those 5 entirely. This is why every measurement in the machinery reports
  the two separately and never sums them.
- **Role error is a component of false trust, not a separate failure class.** Half the
  teaching-critical harm is a role decision. That is a recognition-and-role problem with a
  targeted fix, and a threshold is not it.

---

## 5 · There is no single false-trust number for this system

The same quantity, measured on five annotated populations in this repository:

| population | served rows | false trust | teaching-critical |
|---|---|---|---|
| reference plane (hard pages, current pipeline) | 354 | **0.0734** | 0.0339 |
| independent 97-row evaluation set | 67 trusted | **0.090** | see §8 |
| legacy batch 1, after reprocessing | 74 | **0.365** | 0.068 |
| round-3 shipped-content sample | 480 | **0.650** | 0.292 |
| legacy batch 1, before reprocessing | 55 | **0.727** | 0.473 |

**A tenfold spread.** It is not noise: these are different pipeline versions, different content
populations and — critically — two different definitions of «wrong». On the reference plane
teaching-critical error is *not* a subset of false trust; on every audit plane it *is*, strictly.
**The two planes do not agree on the set relation**, let alone the rate.

Consequence, stated as a rule rather than an observation: **a bound quoted without its plane, its
pipeline version and its population is not a bound.** Every bound in §6 names all three.

---

## 6 · Bound options, with consequences

A block-level rate is not something a family can be told. What a family experiences is a lesson,
so the arithmetic runs in that direction: a promise about a lesson fixes the block rate, and the
block rate fixes the size of the blind audit that could demonstrate it.

```
block_rate ≤ 1 − p^(1/L)          L = trusted blocks in a lesson, planning figure 30
audit n    ≥ smallest n with wilson_upper(k, n) ≤ block_rate
```

L = 30 comes from round 6's real lesson delivery: **34 real blocks**. Independence between blocks
is assumed and is optimistic — §3 measured the clustering that makes it so.

| bound | promise | block TC rate ≤ | audit n (0 observed) | prediction from pre-existing evidence |
|---|---|---|---|---|
| **BOUND-0** | nothing admitted | — | 0 | holds by construction. Round 6's accepted outcome. |
| **BOUND-1** | 95 % of lessons clean | 0.00171 | 2,245 | **PREDICTED FAIL** — ~48 expected errors against a rule permitting 0 |
| **BOUND-2** | 90 % of lessons clean | 0.00351 | 1,092 | **PREDICTED FAIL** — ~23 expected against a rule permitting 0 |
| **BOUND-3** | 80 % of lessons clean | 0.00741 | 515 | **PREDICTED FAIL** — ~11 expected. Even this is 3× better than measured. |
| **BOUND-4** | none — a block rate only | 0.02 | 189 | **BORDERLINE.** The measured point is 0.0213, on the wrong side by a hair. |
| **BOUND-5** | per-lesson certification | — | 30 per lesson | **ACHIEVABLE**, and not a threshold. |

**BOUND-4 is the only bound on this list the evidence does not predict will fail, and its
consequence is the reason it is not recommended:** at a teaching-critical rate of 0.02 and
L = 30, **45 % of lessons carry at least one teaching-critical error.** The bound is passable and
its consequence is not sayable to a parent. Presenting it without that sentence would be the
purest form of threshold theatre available.

**BOUND-5 is not a threshold, which is precisely why the arithmetic permits it.** A threshold
spends a measured error rate across content nobody looked at; certification spends human attention
and leaves no residual rate to bound. It costs ~30 verifications per lesson, produces no
corpus-level claim, and must never be reported as a trust threshold having been met. Round 7's
plan already prefers this shape: *«prefer the already-measured Golden lessons. Do not scale to the
whole corpus.»*

---

## 7 · Recommendation

> **Freeze C2 · PROSE under BOUND-2, and run the blind evaluation expecting it to fail.**

- **C2**, because it is measurably better than C1 on both axes at once, and because the intuition
  that motivated C1 — tighten role confidence — was falsified by the same measurement.
- **BOUND-2**, because it is derived from a promise about a lesson rather than from what the
  pipeline happens to achieve, and it is the weakest such promise still worth making out loud.
- **Expecting failure**, because the pre-existing evidence predicts ~23 teaching-critical errors
  where the rule permits zero, and **a prediction recorded before the measurement is what
  separates a calibration from a selection**. The prediction is inside the frozen payload; it
  cannot be revised after the result.

If it passes, that is news. If it fails, round 7 ends where round 6 ended with one difference:
the zero will have been **measured against a predeclared bound** instead of inferred from the
absence of a threshold. That is a materially stronger statement, and it is the honest maximum
available this round.

**What would actually move the bound is not a threshold.** Half the measured harm is digit
corruption that survives two-stack agreement; the other half is a non-question served as a
question. An independent digit-sequence check and a question/non-question discriminator each
attack one half. A tighter threshold attacks neither — it only removes correct content, and §3
shows it removes prose first.

**If a non-zero is required this round**, the honest route is BOUND-5 on a bounded slice, reported
as certification and never as a threshold.

---

## 8 · What this workstream does not know

| | |
|---|---|
| **UNKNOWN** | The 97-row evaluation set's internal denominators. It reports TRUSTED 67 with false trust 6/67 = 0.090, and separately teaching-critical WRONG 5 · display WRONG 11 · role WRONG 10 — which sum to 26 against 6 false-trust rows. Whether those three are counted over 97 rows or over the 67 trusted ones is not stated, and the two readings give teaching-critical rates that differ by a factor of ~1.4. **Referred to WS-M for the Metric Definition Registry; not resolved here and not used as a bound anchor.** |
| **UNKNOWN** | Whether any rate on the reference plane transfers to the corpus. The plane is hard-selected. This is what the blind population exists to find out. |
| **NOT MEASURED** | Over-withholding under any candidate. The reference plane's withheld side has truth, but a *trust* policy's refusals are a different set from the pipeline's, and the audit protocol for them is built (§ blind protocol) and not run. |
| **NOT MEASURED** | What a child does with a trusted block. Every number here is about whether the text matches the print — the same limitation the round-3 audit recorded in its own §9. |

---

## 9 · Reproduce

```
python3 tool/corpus/thresholds/derive.py \
    --gold  poc-out/round5/lane-a3/evidence-gold-tc2-p2.jsonl \
    --audit poc-out/round5/lane-a3/evidence-audit.jsonl \
    --out   poc-out/round7/ws-t/derivation.json
python3 tool/corpus/thresholds/freeze.py verify
python3 tool/corpus/thresholds/measure.py --dry-run
python3 -m unittest discover -s tool/tests
```

The derivation asserts its own agreement with round 5's published baseline; a run that finishes is
a run whose numbers match the published scoreboard. The frozen payload is committed, so the
figures in §3 can be re-derived from it without the gitignored evidence rows.
