# 01 · ROUND OBJECTIVE

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

**Round 6 · VERIFIED ACCURACY → REAL PRODUCT · opened 2026-09-06 · closed 2026-09-06.**

Primary source: `docs/research/ROUND6-PLAN.md`, committed `1a75d24`, with the **Founder addendum**
committed `51711c0` the same day. Both reproduced in full in `reports/ROUND6-PLAN.md`.

**Unlike round 5, round 6's acceptance gates were committed with its plan, before the work
started.** That is a direct consequence of round 5's archive being unable to find §16 anywhere in
the repository. The gates in §3 below are quoted from a file that predates every result.

---

## 1. The North Star

> **MAKE VERIFIED ACCURACY REACH THE LEARNER.**
>
> Rounds 1–5 made us measure better, detect better, and build repair capability. Round 6 must start
> moving that to a real product.
>
> — `ROUND6-PLAN.md`, verbatim *(PROVEN — committed file)*

This is round 5's central finding turned into an objective. Round 5's capability curve rose sharply
and its delivery curve did not move at all: the repair path was a validated laboratory that
**no file outside `tool/corpus/repair/` and `tool/tests/` even imported**.

## 2. The base — composed, not merged

`integration/round6-2026-09-06` = `integration/round5-2026-09-06` **+ all nine round-5 lane
branches, composed.**

Explicitly **not** a merge to `main`: **PR #73 (round 4) and PR #79 (round 5) remain open and
untouched**, and the merge-debt recommendation is itself a round-6 deliverable (Part II). Round 6
could not proceed without R13's code, A1's repair framework and A2's mathfix — all of which live in
unmerged PRs — so the base composes them, exactly as round 5 composed round 4.

## 3. The four workstreams — four, not nine

| WS | The question it was given |
|---|---|
| **A · TRUTH ACCOUNTING** | Make `INPUT = SERVED + WITHHELD + EXCLUDED_WITH_REASON + defined non-learning` hold, with **any unexplained difference a HARD FAILURE**. Reproduce round 5's numbers first. Determine **what** disappeared and **why**. Repair root causes where safe — ***do not simply convert every lost region to WITHHELD***. Recalculate round-5 metrics **preserving history and marking corrections**. And answer canonical lesson identity: classify all 154 duplicated keys / 439 rows. |
| **B · RECOGNITION** | **Failure census first — FORMS BEFORE RULES**, across 13 named classes. *Then* bounded candidates. Measure on SAM's **actual** failures, especially the **274/336** fractions. |
| **C · REPAIR → PRODUCT** | Carry `OriginalObservation → RepairCandidate → Validator → ValidatedRepair → Trust/Disposition → TSL → LessonDocument → Learning View`. **CONNECT ≠ TRUST.** No second provenance universe. No mutation of historical learner evidence. **Never weaken a guard for coverage.** |
| **D · GOLDEN DELIVERY** | 3–5 representative **real** lessons, at least one exercising a real round-5/6 failure, **not cherry-picked easy ones**. Prove the whole chain to a **real device**. **No fixture substitution in the final delivery claim.** Plus Workspace **Option B**, and a **bounded** visual-grammar continuation that must **not** expand renderer families. |

## 4. The five acceptance gates — fixed before the round, in the repository

> - **GATE A — ACCOUNTING** · zero unexplained silent loss on Golden + holdout
> - **GATE B — RECOGNITION** · ≥1 previously unrecoverable OCR failure class materially improves
>   **at recognition level**
> - **GATE C — REPAIR** · a `ValidatedRepair` crosses the production-shaped pipeline
> - **GATE D — TEACHING** · ≥1 real lesson becomes **honestly** eligible for teaching, target >0.
>   **Do not lower trust/safety gates to achieve >0. A truthful zero is acceptable if evidence
>   demands it.**
> - **GATE E — DEVICE** · ≥1 Golden lesson on a real device visibly consumes validated/repaired
>   real data, traceable `UI → LessonDocument → TSL → ValidatedRepair → Source`
>
> — `ROUND6-PLAN.md`, verbatim *(PROVEN — committed before the work)*

**Gate D contains its own escape hatch, written by the Founder in advance.** That sentence is what
makes this round's central result reportable as a success rather than a shortfall — see
`11-FOUNDER-ACCEPTANCE-CARD.md` §2.

## 5. The Founder addendum — Golden Delivery decided by the Founder, not by a workstream

| Slice | Lesson | Purpose |
|---|---|---|
| **GOLDEN #1** | **LS&ĐL 5 Bài 8** | Prove `REPAIR → TSL → LESSON DOCUMENT → APP → REAL DEVICE`. **The round's delivery claim rests on it.** |
| **GOLDEN #2** | **Toán 4 tập hai Bài 61** | Prove **R13 accounting + recognition recovery**. **Not** a learner-facing delivery target. |
| **REGRESSION** | **KHTN 6 Bài 17** | Prove round 6 does not break the existing real workspace. **Not** proof of repair effectiveness — it exercises essentially no repair. |

Both Golden lessons come **straight out of round 5's failures**: Bài 8 is where `agree_tones`
withheld the block carrying all seven dated events; Bài 61 is where the served share collapses from
0.211 to **0.078** once silent loss is counted. **They were chosen because they are hard.**

The addendum also fixed the proof standard: *«Do NOT use the old round-4 LessonDocument as the final
proof. Prove lineage with hashes.»*

## 6. The LLM rule, carried in on round-5 evidence

*(recall 0.717, false-correction rate 1.000, 13/13 wrong)*

**MAY** detect anomaly · route · propose candidate · perform semantic review.
**MUST NOT** auto-correct canonical truth · be trust authority · silently rewrite corpus.
**`LLM OUTPUT != TRUTH`.**

*(Held. WS-A called no LLM; WS-C calls none, proposes with none, lets none rule; WS-B ran a VLM —
CodeFormulaV2 — **as a measured candidate** and rejected it, noting that even at zero cost its
output could only ever be a `RepairCandidate` behind deterministic checks.)*

## 7. Standing rules binding on this round

- **FORMS BEFORE RULES** — `FORM CENSUS → CLUSTER → REPRESENTATIVE EXAMPLES → RULE → HOLDOUT →
  MEASURE → GENERALIZE`. Never infer coverage from a few examples.
- **Composition check before round closure** — individual PR green ≠ integrated product green.
  Report **INDIVIDUAL CI and COMPOSITION CI**.
- **`false_correction_rate` is blind to a detector** — a workstream raising detection recall must
  report **false demotion rate** beside it.
- **Never turn PARTIAL into DONE.** Never silently rewrite history; historical metrics stay
  reproducible.
- **`3,679` = HISTORICAL BASELINE ONLY** until canonical identity is resolved.
- `OPENED != UNDERSTOOD` · `READ != MASTERY` · `TAP != COMPETENCE` · `REPROCESSED != TRUSTED` ·
  **`RESTORED != TRUSTED`** · `TRACE != EVIDENCE` — and round 6 adds **`VISIBLE != SERVED`** and
  **`CONNECT != TRUST`**.

## 8. Governance

**Autonomous:** audit · bounded research · the R13 fix · recognition POCs · repair integration ·
Golden Delivery · Workspace B · tests · device tests under the existing protocol · Jira/Confluence ·
branches/PRs · disposable integration composition · **local Desktop archives**.

**Founder approval required:** **MERGE** · **production trust threshold** · mass corpus reprocess ·
destructive migration · unrestricted LLM generation · licensing / public SGK distribution · paid
infrastructure · public release · fundamental irreversible architecture replacement.

> **DO NOT MERGE. Every PR ends at READY FOR FOUNDER REVIEW.** *(Held — PROVEN, §7 of this
> archive.)*
