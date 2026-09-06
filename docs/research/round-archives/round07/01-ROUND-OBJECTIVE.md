# 01 · ROUND OBJECTIVE

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

**Round 7 · TRUST GATE CALIBRATION + FIRST TRUSTED SLICE · closed 2026-09-06.**

Source of record: `docs/research/ROUND7-PLAN.md`, committed `1e31512` — **before any result
existed.** Reproduced in full in `reports/ROUND7-PLAN.md`.

---

## 1. The North Star, and the hard stop written beside it

> **TRUSTED CONTENT REACHES THE LEARNER WITHOUT LOWERING THE EVIDENCE BAR.**
>
> **CALIBRATION BEFORE ACTIVATION.** This round **stops at the trust-activation Founder gate.**
> **STOP for Founder review BEFORE activating any production trust threshold.**
>
> — `ROUND7-PLAN.md`, verbatim *(PROVEN — committed file)*

Steps **A** (freeze a candidate policy from pre-existing evidence) and **B** (freeze the blind
evaluation population) happened this round. Steps **C–G** — apply, audit, measure, and only then
allow a bounded trusted slice — happen **only after Founder approval.** The plan's instruction was
exact: *build the machinery for C–E so it can run immediately on approval; **do not run it.***

## 2. NO THRESHOLD THEATRE — the clause that shaped the whole round

> A threshold may not exist merely because the software wants a non-zero trusted count. **Do not
> optimise for `eligible > 0`, lesson count, coverage, or demo quality.** If the measured result
> misses the predeclared bound, the answer is `trusted = 0`, `eligible = 0`, and a truthful zero —
> as round 6 already demonstrated is acceptable.

**And the order was declared binding in advance:**

> The threshold is frozen from pre-existing trade-off evidence **BEFORE** anyone looks at which
> lessons it would admit. **A policy chosen after seeing the admitted set is not a policy, it is a
> selection.**

That sentence is why round 7's central artefact is a **hash chain** rather than a number. See
`11-FOUNDER-ACCEPTANCE-CARD.md` §2.2.

## 3. The four workstreams

| WS | The question it was given |
|---|---|
| **M · METRIC TRUTH** | Establish a permanent rule: **no important derived metric is accepted unless it can be re-derived from leaf records.** Build a **Metric Definition Registry** recording, per metric: semantic quantity · unit · leaf population · grouping key · denominator · aggregation · exclusions · source artefact/version · **an independent re-derivation command**. Resolve or **formally deprecate** «total activities» — the three observed totals **248 · 217 · 161**. Make the `toanExercises` incident a **regression example with a test**. |
| **T · TRUST CALIBRATION** | Derive a candidate threshold policy and bound **from pre-existing evidence only**. **Freeze it, hashed, before any application.** Freeze a **blind evaluation population**, hashed, disjoint from tuning data. Build the audit machinery. **Express trade-offs WITHOUT lesson identities where possible.** Present bound options with consequences. **DO NOT APPLY. DO NOT ACTIVATE.** |
| **S · STRUCTURED CONTENT GAP** | Evaluate the 118 blocks withheld only because the app lacks a type — `footnote` 64 · `activity` 50 · `option` 4. **«This is NOT permission to serve them.»** Would bounded types improve truthful representation **without weakening trust**? **Inspect the 4 `option` blocks with particular care: an incomplete multiple-choice structure can be unsafe even when individual blocks are correctly withheld.** |
| **R · ROUND-6 DEBT** | Triage **every** carried item as `ROUND7-P0` / `ROUND7-P1` / `DEFERRED WITH REASON` — **no silent dropping** — then execute the P0s: the 17 crop-less gaps · the Next Action contradiction · the lowercased proper noun · the abstaining validator · recognition generalisation. |

## 4. The five acceptance gates — fixed in the repository before the work

> - **A · METRIC TRUTH** — no ambiguous major metric remains; every critical total **re-derivable
>   from leaf records by a committed command**.
> - **B · TRUST CALIBRATION** — policy and bound **frozen and hashed before** any admitted lesson is
>   inspected, **provable by artefact order**.
> - **C · BLIND VALIDATION** — the audit machinery exists and is proven on a dry run that **does
>   not** use the frozen bound to admit anything.
> - **D · TRUST DELIVERY** — **not attemptable this round.** Round 7's honest outcome is a
>   **prepared, unactivated gate**.
> - **E · NO REGRESSION** — round 6's invariants hold: `UNACCOUNTED = 0`, served set unchanged,
>   `trusted = 0`, repair records only on withheld blocks, the three honesty guards still red under
>   mutation.

**Gate D is the unusual one, and it is unusual on purpose.** The plan declares in advance that the
gate is **not attemptable**, so it must be graded neither PASS nor FAIL. `11-FOUNDER-ACCEPTANCE-CARD.md`
§2.4 grades it as the plan defines it and refuses to convert it into either.

## 5. The proof standard required if anything ever becomes trusted

> `SOURCE → OBSERVATION → VALIDATION/REPAIR → TRUST DECISION → TSL → LESSON DOCUMENT → DEVICE`,
> **with provenance at every boundary.** Prefer the already-measured Golden lessons. **Do not scale
> to the whole corpus.**

## 6. Standing rules carried into this round

**FORMS BEFORE RULES** · composition check **with real assets** before closure · never turn PARTIAL
into DONE · `false_correction_rate` is blind to a detector · **re-derive a number a second way
before recording a disagreement** *(added after the round-6 archive incident, and it caught two
findings inside round 7 itself)* · an LLM may detect/route/propose/review but **never auto-correct
canonical truth** · `3,679` HISTORICAL BASELINE ONLY, `3,650` a measurement · **`VISIBLE ≠ SERVED`**
· `OPENED ≠ UNDERSTOOD` · `READ ≠ MASTERY` · `TAP ≠ COMPETENCE`.

Operationally: **every workstream in its own git worktree**; gitignored assets (`assets/pack/`,
`assets/fixtures/`) **do not travel** — rsync them or produce false failures. *That instruction
acquired a sharp exception during the round: see `04-FAILURES-AND-FALSIFICATIONS.md` §8.*

> **DO NOT MERGE. STOP AT THE TRUST-ACTIVATION FOUNDER GATE.** *(Both held — PROVEN.)*
