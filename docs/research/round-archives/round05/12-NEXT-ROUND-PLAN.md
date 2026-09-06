# 12 · NEXT ROUND PLAN — Round 6

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

Source of record: `docs/research/ROUND6-PLAN.md`, committed `1a75d24` on 2026-09-06, with a
**Founder addendum** committed `51711c0` the same day. Reproduced in full in
`reports/ROUND6-PLAN.md`.

**Round 6 had already begun when this archive was built.** Two round-6 artefacts postdate round 5
and are included because they change how round 5 should be read: the **Golden Delivery decision**
(§3a below) and the **merge-debt audit** (`reports/ROUND6-MERGE-DEBT-AUDIT.md`, §10 below).

---

## 1. NORTH STAR

> **MAKE VERIFIED ACCURACY REACH THE LEARNER.**
>
> Rounds 1–5 made us measure better, detect better, and build repair capability. Round 6 must
> start moving that to a real product.

**This is round 5's central finding turned into an objective.** Round 5's capability curve went
up sharply and its delivery curve did not move at all; round 6 exists to close that gap.

## 2. BASE — and why it is not a merge

`integration/round6-2026-09-06` = `integration/round5-2026-09-06` **+ all nine round-5 lane
branches, composed.**

This is **not** a merge to `main`: **PR #73 (round 4) and PR #79 (round 5) remain open and
untouched**, and the merge-debt recommendation is itself a round-6 deliverable (Part II).
Round 6 cannot proceed without R13's code, A1's repair framework and A2's mathfix — all of which
live in unmerged PRs — so the base composes them, exactly as round 5 composed round 4.

## 3. FOUR COORDINATED WORKSTREAMS — not nine lanes

| WS | Scope | Directly answers |
|---|---|---|
| **A · TRUTH ACCOUNTING** | **P0.1 — R13 zero-silent-loss conservation:** `INPUT = SERVED + WITHHELD + EXCLUDED_WITH_REASON + defined non-learning`; **any unexplained difference = HARD FAILURE.** Reproduce 0.632→0.589, holdout 0.523, Bài 61 0.211→0.078; determine **what** disappeared and **why**; repair root causes where safe — *do not simply convert every lost region to WITHHELD*. Recalculate affected round-5 metrics, **preserving historical numbers and marking corrections.** **A2: canonical lesson identity** — classify all 154 duplicated keys / 439 rows; report SOURCE ROWS · DISTINCT KEYS · TRUE DUPLICATES · KEY COLLISIONS · SOURCE VARIANTS · CANONICAL COUNT | round-5 open P0 **#1**, and the denominator risk |
| **B · RECOGNITION** | **P0.2 — the next bottleneck. Failure census first, FORMS BEFORE RULES**: DIGIT LOSS · OPERATOR LOSS · FRACTION STRUCTURE · SUPERSCRIPT · SUBSCRIPT · ROMAN NUMERAL · DIACRITIC · SYMBOL CONFUSION · SEGMENTATION · MATH REGION · FORMULA · TABLE/STRUCTURE · OTHER. Then bounded candidates: corpus/template-assisted recognition · targeted high-resolution re-crop · alternative OCR observation · multi-engine disagreement · specialised STEM recognition · geometry-aware recognition · Docling formula enrichment where licensing-safe. **Measure on SAM's actual failures, especially the 274/336 fractions** | round-5's identified next bottleneck |
| **C · REPAIR → PRODUCT** | **P0.3 —** `OriginalObservation → RepairCandidate → Validator → ValidatedRepair → Trust/Disposition → Trusted Structured Content → LessonDocument → Learning View`. **CONNECT ≠ TRUST.** `ValidatedRepair` retains original observation · candidate · source grounding · failure class · repair method · validator+version · validation result · repair version · provenance · disposition. **No second provenance universe.** No mutation of historical learner evidence. Preferred path stays `WITHHELD → FAILURE CLASS → REPAIR CANDIDATE → VALIDATION → RESTORE`; **never weaken a guard for coverage** | round-5 open P0 **#2** and **#5** |
| **D · GOLDEN DELIVERY** | **P0.4 —** 3–5 representative **real** lessons (Science · History · Math + one more if evidence supports); **at least one must exercise a real round-5/6 recognition or repair failure**; not cherry-picked easy ones. Prove `SOURCE → RECOGNITION → ACCOUNTED STRUCTURE → VALIDATED REPAIR → TRUST/DISPOSITION → TSL → LESSON DOCUMENT → LEARNING VIEW → REAL DEVICE`. **No fixture substitution in the final delivery claim.** Also: implement **Workspace OPTION B** (Founder-selected); and a **bounded** visual-grammar continuation — forms census, semantic-pattern census, provenance architecture, bounded POC; **do not expand renderer families** | the delivery gap itself |

## 3a. FOUNDER ADDENDUM — GOLDEN DELIVERY DECIDED (2026-09-06)

Lesson selection is **decided by the Founder**; no workstream runs its own selection.

| Slice | Lesson | Purpose |
|---|---|---|
| **GOLDEN #1** | **LS&ĐL 5 Bài 8** | Prove `REPAIR → TSL → LESSON DOCUMENT → APP → REAL DEVICE`. **The round's delivery claim rests on it.** |
| **GOLDEN #2** | **Toán 4 tập hai Bài 61** | Prove **R13 accounting + recognition recovery**. **Not** a learner-facing delivery target. |
| **REGRESSION** | **KHTN 6 Bài 17** | Prove round 6 does not break the existing real workspace. **Not** proof of repair effectiveness — it exercises essentially no repair. |

**Both Golden lessons come straight out of round 5's failures**, which is the point: Bài 8 is the
lesson where `agree_tones` withheld the block carrying all seven dated events; Bài 61 is the
lesson whose served share collapses from 0.211 to **0.078** once R13's silent loss is counted.

The addendum also records a coordinator verification worth carrying forward: **no new loading path
is needed.** `lib/core/lesson_model/workspace_catalog.dart:76-77` already tries `realPath` before
falling back to `syntheticPath`, and the Bài 8 slot is already registered as a **research slot**
(so it carries the mandatory experimental chip). The exact file the app will prefer is
`assets/fixtures/real/lesson-05-sgk-lich-su-va-dia-li-5-b8.json` — **which does not exist today**,
so the app is loading the synthetic fallback. **Do NOT use the old round-4 LessonDocument as the
final proof; prove lineage with hashes.**

## 4. ACCEPTANCE GATES — fixed now, in the repository, not redefined after results

| Gate | Criterion |
|---|---|
| **GATE A — ACCOUNTING** | zero unexplained silent loss on Golden + holdout |
| **GATE B — RECOGNITION** | ≥1 previously unrecoverable OCR failure class materially improves **at recognition level** |
| **GATE C — REPAIR** | a `ValidatedRepair` crosses the production-shaped pipeline |
| **GATE D — TEACHING** | ≥1 real lesson becomes **honestly** eligible for teaching, target >0. **Do not lower trust/safety gates to achieve >0. A truthful zero is acceptable if evidence demands it.** |
| **GATE E — DEVICE** | ≥1 Golden lesson on a real device visibly consumes validated/repaired real data, traceable `UI → LessonDocument → TSL → ValidatedRepair → Source` |

**Note for future archives: these five gates are committed in the repository with the plan.**
Round 5's were not, which is why `11-FOUNDER-ACCEPTANCE-CARD.md` had to reconstruct them.

## 5. EARLY FOUNDER CHECKPOINT — do not wait for round end

Report as soon as **all three** are proven:
1. R13 conservation/accounting works;
2. ≥1 previously unrecoverable recognition case improves;
3. one `ValidatedRepair` crosses into production-shaped TSL **without automatically becoming
   trusted**.

## 6. THE LLM RULE, CARRIED FORWARD ON ROUND-5 EVIDENCE

*(recall 0.717, false-correction 1.000, 13/13 wrong)*

**MAY** detect anomaly · route · propose candidate · perform semantic review.
**MUST NOT** auto-correct canonical truth · be trust authority · silently rewrite corpus.
**`LLM OUTPUT != TRUTH`.**

## 7. STANDING RULES ROUND 5 PRODUCED, NOW BINDING ON EVERY FUTURE ROUND

- **FORMS BEFORE RULES** — `FORM CENSUS → CLUSTER → REPRESENTATIVE EXAMPLES → RULE → HOLDOUT →
  MEASURE → GENERALIZE`. Never infer coverage from a few examples.
  *(From three independent falsifications: Lane C 1/12 date forms, E1 TIMELINE 3/224, E2 6/54.)*
- **Composition check before round closure** — individual PR green ≠ integrated product green.
  Report **INDIVIDUAL CI and COMPOSITION CI**. *(From the three integration defects.)*
- **`false_correction_rate` is blind to a detector** — a workstream raising detection recall must
  report **false demotion rate** beside it. *(From demotion precision 0.250.)*
- **Never turn PARTIAL into DONE.** Never silently rewrite history; historical metrics stay
  reproducible.
- **`3,679` = HISTORICAL BASELINE ONLY** until canonical identity is resolved.
- `OPENED != UNDERSTOOD` · `READ != MASTERY` · `TAP != COMPETENCE` · `REPROCESSED != TRUSTED` ·
  **`RESTORED != TRUSTED`** · `TRACE != EVIDENCE`

## 8. GOVERNANCE

**Autonomous:** audit · bounded research · R13 fix · recognition POCs · repair integration ·
Golden Delivery · Workspace B · tests · device tests under the existing protocol ·
Jira/Confluence · branches/PRs · disposable integration composition · **local Desktop archives**
*(which is the authority under which this archive was produced)*.

**Founder approval required:** **MERGE** · production trust threshold · mass corpus reprocess ·
destructive migration · unrestricted LLM generation · licensing / public SGK distribution · paid
infrastructure · public release · fundamental irreversible architecture replacement.

> **DO NOT MERGE. Every PR ends at READY FOR FOUNDER REVIEW.**

---

## 9. HOW ROUND 5'S OPEN ITEMS MAP ONTO ROUND 6

| Round-5 open item | Round-6 home | Covered? |
|---|---|---|
| R13 silent loss | **WS A**, GATE A | **fully** |
| Lesson identity (3,679 vs 3,240) | **WS A2** | **fully** |
| Recognition ceiling (274/336 fractions) | **WS B**, GATE B | **fully** |
| Wire the repair path (`CONNECT ≠ TRUST`) | **WS C**, GATE C | **fully** |
| No bridge carrier for structured STEM | **WS C** | **fully** |
| Delivery to a real device on real data | **WS D**, GATE D + E | **fully** |
| Workspace option B | **WS D** | **fully** |
| **R15 — attach provenance does not reproduce** | — | ⚠ **NOT explicitly assigned to a workstream.** It is a Founder decision item, and the pack build depends on it. **Flagged here as a gap in the round-6 plan.** |
| **Defect 8 on the lesson path** (9 → 9, 13 → 13) | implied by WS C's disposition work | ⚠ **not named explicitly** — flagged |
| **Q-ROLE-1 / 2 / 3** | — | ⚠ **not assigned** — they need a Founder ruling, not a workstream |
| **Semantic-yield gate** (E1's request) | WS D's bounded visual-grammar continuation, at most implicitly | ⚠ **not named explicitly** — flagged |
| Merge debt (#73, #79) | **Part II** deliverable | **DONE — see §10** |

**Four items are not explicitly carried into round 6.** They are recorded here so they cannot be
lost between rounds — which is the point of keeping a per-round archive.

---

## 10. ROUND 6 PART II — THE MERGE-DEBT AUDIT, ALREADY DELIVERED

Full text: `reports/ROUND6-MERGE-DEBT-AUDIT.md`. Its recommendation bears directly on what the
Founder should do with round 5, so it is summarised here.

> **Recommendation: merge #79. Close #73 as subsumed. Hold #80–#88.**

**Why it is safe, and checkable:**

| Relationship | Result |
|---|---|
| `origin/main` → #73 (round 4) | 73 commits |
| `origin/main` → #79 (round 5) | 89 commits |
| #73 → #79 | **16 commits — all documentation** (3 files, all under `docs/research/`; zero code, tests or assets) |
| Is #73 an ancestor of #79? | **YES** |
| Is `main` an ancestor of #79? | **YES** — no divergence; `MERGEABLE`, `CLEAN`, CI `SUCCESS` |

**#79 does NOT contain round 5's lane code.** PRs #80–#88 target #79 but were never merged into
it. So merging #79 ships **round-4 code the Founder has already accepted, plus round 5's report**
— and none of round 5's unreviewed lane work.

**And it delivers nothing to a child.** Packs under `assets/pack/` are gitignored build artefacts;
**merging #79 changes no APK.**

**Why holding is not neutral.** Round 4 is *accepted and unmerged*. Round 6's base is a synthetic
composition branch holding **114 commits reachable from nowhere else**. If round 6 also does not
merge, round 7's base is a composition of a composition — each round adding a layer whose only
integration evidence is a throw-away worktree. The audit puts it plainly: *the current state,
where a round is accepted but not merged and the next round quietly composes on top, is the one
combination that carries the cost of both options and the benefit of neither.*

**Nothing was merged in producing that audit, and nothing was merged in producing this archive.**
