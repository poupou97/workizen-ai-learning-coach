# WS-T · TRUST CALIBRATION — round 7 report

2026-09-06 · branch `ws-t/round7-trust-calibration` → `integration/round7-2026-09-06` ·
**DO NOT MERGE. READY FOR FOUNDER REVIEW.**

> **NOTHING WAS ACTIVATED. NO THRESHOLD WAS APPLIED. NO CONTENT WAS ADMITTED.**
> `trusted` is still 0, and this workstream added no code path that could change that without a
> Founder approval artefact naming a frozen policy by hash.

Companion documents: `TRUST-CALIBRATION-POLICY-v1.md` (the candidate, the evidence, the bounds,
the recommendation) · `TRUST-CALIBRATION-BLIND-PROTOCOL-v1.md` (the population and the C–E
runbook).

---

## 1 · PLANNED vs ACTUAL

| # | Planned | Status | Actual |
|---|---|---|---|
| 1 | Candidate threshold policy + bound from pre-existing evidence only | **DONE** | 5 candidates, 6 bound options, frozen `sha256 0dfc5032…`. Every clause carries the prior finding it comes from. Nothing new was extracted, annotated or measured. |
| 2 | Frozen blind evaluation population, hashed, disjoint from tuning data | **DONE, with a declared weakness** | Two populations frozen (`dbadf4ad…`, `69d1cacc…`), 120 lessons each, drawn from 2,536 eligible after excluding 44 contaminated books. **Disjointness from the 97-row set is argued, not proven** — its rows do not exist as data. |
| 3 | Audit + measurement machinery for false trust and teaching-critical error, ready to run, not run | **DONE** | `apply.py` (inert), `audit_sheet.py` (worklist + sealed key), `measure.py` (bound from the ledger, decision on the upper bound). 52 tests. Dry run shows one PASS and three refusal modes on fabricated rows. |
| 4 | Expected trade-offs without lesson identities wherever possible | **DONE** | No book id, lesson number or page appears in any artefact or document this workstream produced. Enforced by `identity_leaks` at freeze time and by a test over the documents. |
| 5 | Bound options with consequences, and a recommendation | **DONE** | Six options, each with its audit cost and its predicted outcome. Recommendation: **C2 · PROSE under BOUND-2, expecting a truthful zero.** |
| — | Apply / audit / measure / allow a slice (steps C–G) | **NOT STARTED — correctly** | Requires Founder approval. The machinery refuses without it. |

**Nothing was promoted from PARTIAL to DONE.** Item 2 is DONE *with a declared weakness*, and the
weakness is in the artefact, not only in this table.

### Gates

| Gate | Requirement | Verdict |
|---|---|---|
| **B · TRUST CALIBRATION** | policy and bound frozen and hashed **before** any admitted lesson is inspected, provable by artefact order | **PASS** — hash chain, order enforced at write time, no admitted set exists, no artefact names an identity in an admission context |
| **C · BLIND VALIDATION** | audit machinery exists and is proven on a dry run that does not use the frozen bound to admit anything | **PASS** — `measure.py --dry-run`, fabricated rows, one PASS and three refusal modes |
| **D · TRUST DELIVERY** | — | **NOT ATTEMPTABLE THIS ROUND**, as the plan states. The outcome is a prepared, unactivated gate. |

---

## 2 · PROVEN

Claims below are **MEASURED** on the round-5 evidence rows unless marked otherwise, and each is
re-derivable by a committed command.

- **A trust policy can be given a shape that cannot regress the served set.** `TRUST = SERVED ∩
  admit(...)`, so `trusted ⊆ served` holds by construction; activation cannot serve one block the
  pipeline withholds today. Property-tested over randomised rows; asserted again on `apply.py`'s
  output. **This makes round 6's byte-identical served set safe against activation.**
- **The derivation reproduces round 5's published baseline exactly** — 643 rows, 354 served,
  coverage 0.5505, 26 wrong, FTR 0.0734 — asserted as a test, so the candidates are re-decisions
  of the published scoreboard rather than a new measurement.
- **Teaching-critical error is NOT a subset of false trust.** Of 354 served rows: 7 both, 19 false
  trust only, **5 teaching-critical only**. A bound on false trust alone would have missed those 5.
  Re-derived a second way from the underlying flags (6 digit corruptions + 6 non-questions-served-
  as-questions = 12 teaching-critical, of which one is also `cer`/`order` wrong).
- **All 12 teaching-critical errors fall into exactly two mechanisms** — digit corruption (6) and
  a non-question served as a question (6) — **and neither is visible to any signal a gate can
  read.** 3 of the 6 digit corruptions survive character-exact agreement between two independent
  OCR stacks, the role-confidence floor, the figure refusal, the order check and the subject
  exclusion. They pass everything.
- **No available combination of signals bounds teaching-critical error below ~0.021** on the
  reference plane, at any coverage. The strictest principled stack reaches 0.0233 at 36 % of
  served; the best reaches 0.0213 at 53 %.
- **The child-facing consequence.** At the best candidate's rate and the 30 trusted blocks a real
  lesson delivered in round 6, `P(a lesson contains ≥ 1 teaching-critical error) ≈ 0.48`
  **under an assumption of independence between blocks.** Measured at page level: 0.1026 observed
  against 0.0975 expected under independence, on 39 pages carrying 4 events — **no measurable
  clustering at this n.**
- **No single false-trust number exists for this system.** The same quantity measures 0.073 ·
  0.090 · 0.365 · 0.650 · 0.727 across the five annotated populations, and the reference and audit
  planes **do not even agree on whether teaching-critical error is a subset of false trust.**
- **The order of this round is provable by artefact**, not asserted: an append-only hash chain
  whose population entries embed the policy hash, which refuses at write time to freeze a
  population before a policy or an admitted set before an approval, and which refuses any payload
  naming a lesson identity in an admission context.

---

## 3 · FALSIFIED

- **«Tightening role confidence buys safety.»** It does not. Raising the floor to 0.70 moves false
  trust 0.0734 → 0.0593 and moves the **teaching-critical rate 0.0339 → 0.0407 — in the wrong
  direction** — while removing **every block of continuous prose**, because 0.60 is the fallback
  meaning «we could not tell». The candidate that keeps prose (C2) admits 46 % more content *and*
  has the lower teaching-critical rate. C2 dominates C1 outright.
- **«The evidence file's `held_out` flag marks a usable holdout.»** It does not. Lane A3's
  published curve was computed over **all 643 rows including the 181 held-out ones**; the
  published baseline only reproduces on the pooled set. Pooling them spent them. **The repository
  contains no pre-existing blind population** — every annotated set was consumed by the
  derivation, and the 97-row set was not merely measured on but used in round 5 §8.3 to route
  restores.
- **«A trust threshold is the thing standing between the pipeline and a trusted slice.»** The
  arithmetic says otherwise. The gap between what any threshold achieves (~0.021) and what a
  90 %-clean-lesson promise requires (0.0035) is a factor of six, and the residual errors are
  invisible to every signal a threshold can read. **The blocker is recognition and role
  disambiguation, not calibration.**
- **My own clustering claim, falsified by my own second derivation.** I first computed the
  expected page incidence from the median blocks-per-page (0.082) and reported the observed 0.103
  as evidence that errors cluster. Computing the expectation over the actual per-page counts gives
  **0.0975 against 0.1026 observed** — the disagreement I was about to record did not exist. The
  lesson-level probabilities remain labelled optimistic, but on the strength of an assumption,
  not of a measurement. *Re-derive a number a second way before recording a disagreement* caught
  this one inside the same round.
- **My own first framing, corrected in place.** I began by treating Lane A3's trade-off curve as
  the object to pick a point on. It is a curve over *guard waivers* — an axis of loosening. A
  trust threshold moves along the opposite axis, restricting the already-served set. Reading the
  A3 curve as a menu of trust thresholds would have produced a policy that serves new content in
  the name of trusting it.

---

## 4 · STILL HYPOTHESIS

- That any rate on the reference plane transfers to the corpus. It is 54 deliberately hard pages.
  **This is exactly what the blind population exists to test, and it has not been tested.**
- That 30 trusted blocks per lesson is the right planning figure. It comes from one real lesson
  delivered in round 6. The blind population will measure the real yield.
- That the blind population is disjoint from the 97-row evaluation set. **Argued from book
  coverage; not provable**, because that set's rows exist only as a summary table.
- That the two named machinery gaps — independent digit verification, structural-sibling
  completeness — would actually move the bound. They address 100 % of the *measured* mechanisms,
  which is not the same as addressing 100 % of the mechanisms.

---

## 5 · Claims by label

| Label | Claim |
|---|---|
| **PROVEN** | `trusted ⊆ served` for every implementable candidate; the ledger's order properties; the machinery's refusals |
| **MEASURED** | every rate in §2, on the round-5 evidence rows, 643 rows / 54 hard pages |
| **OBSERVED** | page-level incidence 0.1026 (95 % upper 0.236) on 39 pages carrying 4 events — consistent with independence, and far too few events to detect clustering either way |
| **INFERRED** | the audit sizes each bound requires; the lesson-level probabilities, which assume independence and are therefore optimistic |
| **HYPOTHESIS** | corpus transfer; the 30-blocks-per-lesson figure; the value of the two missing clauses |
| **UNKNOWN** | the 97-row set's internal denominators (referred to WS-M); over-withholding under any candidate; what a child does with a trusted block |

---

## 6 · Handover

**To the Founder — the decision this round asks for:** approve a candidate and a bound, or decline
and keep the truthful zero. Both are legitimate outcomes and the recommendation predicts the
second. Approval starts steps C–G; the runbook is five commands and the machinery refuses to run
any of them without an approval artefact.

**To WS-M · METRIC TRUTH:** the 97-row evaluation set publishes TRUSTED 67 with false trust
6/67 = 0.090, and separately teaching-critical 5 · display 11 · role 10, which sum to 26 against
6 false-trust rows. The denominator of those three is not stated and the two readings differ by
~1.4×. It is a published headline metric with an ambiguous leaf population — squarely the
registry's business. **Not resolved here, and deliberately not used as a bound anchor.**

**To whoever owns recognition and role:** half the measured teaching-critical harm is digit
corruption that survives agreement between two independent OCR stacks, and the other half is a
non-question served as a question. Those are the two fixes that would move a trust bound. A
threshold moves neither.

**To the coordinator:** no file outside `tool/corpus/thresholds/**`,
`docs/research/TRUST-CALIBRATION-*.md` and one new test file was touched. Python suite **800
tests OK** (748 before this workstream + 52 new). `poc-out/` outputs are gitignored by design; the
frozen payloads carry the derived figures so §3 of the policy document is re-derivable without
them.
