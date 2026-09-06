# Round 7 — TRUST GATE CALIBRATION + FIRST TRUSTED SLICE · plan (2026-09-06)

**NORTH STAR: TRUSTED CONTENT REACHES THE LEARNER WITHOUT LOWERING THE EVIDENCE BAR.**

**CALIBRATION BEFORE ACTIVATION.** This round **stops at the trust-activation Founder
gate.** Nothing is activated. Base: `integration/round7-2026-09-06`.

## The hard stop

> **STOP for Founder review BEFORE activating any production trust threshold.**

Steps **A** (freeze candidate policy from pre-existing evidence) and **B** (freeze the
blind evaluation population) happen this round. Steps **C–G** — apply, audit, measure,
and only then allow a bounded trusted slice — happen **only after Founder approval.**
Build the machinery for C–E so it can run immediately on approval; do not run it.

## NO THRESHOLD THEATRE

A threshold may not exist merely because the software wants a non-zero trusted count.
**Do not optimise for `eligible > 0`, lesson count, coverage, or demo quality.** If the
measured result misses the predeclared bound, the answer is `trusted = 0`,
`eligible = 0`, and a truthful zero — as round 6 already demonstrated is acceptable.

**The order is binding: the threshold is frozen from pre-existing trade-off evidence
BEFORE anyone looks at which lessons it would admit.** A policy chosen after seeing the
admitted set is not a policy, it is a selection.

## Workstreams — four, not nine

| WS | Scope | Owns |
|---|---|---|
| **M · METRIC TRUTH** | §2 §3. Permanent rule: **no important derived metric is accepted unless it can be re-derived from leaf records.** Build a **Metric Definition Registry** recording, per metric: semantic quantity · unit · leaf population · grouping key · denominator · aggregation function · exclusions · source artefact/version · **independent re-derivation command/test**. Resolve or **formally deprecate** «total activities» — the three observed totals are **248 (leaf items) · 217 (container keys) · 161**; determine what each represents and **deprecate any with no meaningful definition**. Define at minimum `TOAN_EXERCISE_LEAF_COUNT`, `ACTIVITY_LEAF_COUNT`, `LESSON_KEY_COUNT`, `ACTIVITY_FAMILY_COUNT`. The `toanExercises` incident becomes a **regression example** with a test. | `tool/metrics/**` (new), `docs/research/METRIC-REGISTRY-*.md` |
| **T · TRUST CALIBRATION** | §5 A+B and §12 only. Derive a **candidate threshold policy and bound from pre-existing evidence** — A3's round-5 trade-off curve (`TRUST-GATE-SENSITIVITY.md`, `THRESHOLDS.example.json`), round-5's 97-row evaluation set, round-6 accounting. **Freeze it, hashed, before any application.** Freeze a **blind evaluation population** — hashed, disjoint from tuning data. Build the audit and measurement machinery for false trust and teaching-critical error. **Express expected trade-offs WITHOUT lesson identities where possible.** Present **bound options** with consequences. **DO NOT APPLY THE THRESHOLD. DO NOT ACTIVATE.** | `tool/corpus/thresholds/**`, `docs/research/TRUST-CALIBRATION-*.md` |
| **S · STRUCTURED CONTENT GAP** | §9. Evaluate the **118 blocks withheld only because the app lacks a matching type** — `footnote` 64 · `activity` 50 · `option` 4. **This is NOT permission to serve them.** Determine whether bounded `LessonDocument`/app types would improve **truthful representation without weakening trust**. **Inspect the 4 `option` blocks with particular care: an incomplete multiple-choice structure can be unsafe even when individual blocks are correctly withheld** — round 5's defect 8 established that withholding a sibling can itself produce a teaching-critical error. | `lib/core/lesson_model/**`, `tool/corpus/tsl_to_lesson_document.py`, `docs/research/STRUCTURED-GAP-*.md` |
| **R · ROUND-6 DEBT** | §8. Triage every carried item as **ROUND7-P0 / ROUND7-P1 / DEFERRED WITH REASON** — **no silent dropping** — then execute the P0s: 17 lesson gaps with no page crops · Next Action contradiction («Về mục lục» telling a child to leave the lesson they just opened) · lowercased historical proper noun display defect · `si_expected_exponent` validator currently abstaining · recognition generalisation items. «Total activities» belongs to WS-M; merge debt is the coordinator's. | `lib/features/**`, `lib/core/agenda/**`, `tool/corpus/repair/validators/**`, `docs/research/ROUND6-DEBT-TRIAGE.md` |

## Acceptance gates — five, fixed now

- **A · METRIC TRUTH** — no ambiguous major metric remains; every critical total is **re-derivable from leaf records** by a committed command.
- **B · TRUST CALIBRATION** — threshold policy and bound **frozen and hashed before** any admitted lesson is inspected, provable by artefact order.
- **C · BLIND VALIDATION** — the audit machinery exists and is proven on a dry run that **does not** use the frozen bound to admit anything.
- **D · TRUST DELIVERY** — **not attemptable this round.** Reaches a device only after Founder activation. Round 7's honest outcome is a **prepared, unactivated gate**.
- **E · NO REGRESSION** — round 6's invariants hold: `UNACCOUNTED = 0`, served set unchanged, `trusted = 0`, repair records only on withheld blocks, the three honesty guards still red under mutation.

## Required proof if any content ever becomes trusted (post-approval)

`SOURCE → OBSERVATION → VALIDATION/REPAIR → TRUST DECISION → TSL → LESSON DOCUMENT → DEVICE`, **with provenance at every boundary.** Prefer the already-measured Golden lessons. **Do not scale to the whole corpus.**

## Standing rules carried forward

**FORMS BEFORE RULES** · composition check with **real assets** before closure · never turn PARTIAL into DONE · `false_correction_rate` is blind to a detector · **re-derive a number a second way before recording a disagreement** · LLM may detect/route/propose/review but never auto-correct canonical truth · `3,679` HISTORICAL BASELINE ONLY, `3,650` a measurement · `VISIBLE ≠ SERVED` · `OPENED != UNDERSTOOD` · `READ != MASTERY` · `TAP != COMPETENCE`.

Every workstream works **in its own git worktree**. Gitignored assets (`assets/pack/`, `assets/fixtures/`) do not travel — rsync them or produce false failures. Commit and push after every step.

**DO NOT MERGE. STOP AT THE TRUST-ACTIVATION FOUNDER GATE.**
