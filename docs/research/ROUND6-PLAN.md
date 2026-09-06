# Round 6 — VERIFIED ACCURACY → REAL PRODUCT · plan and ownership (2026-09-06)

**North Star: MAKE VERIFIED ACCURACY REACH THE LEARNER.**

Rounds 1–5 made us measure better, detect better, and build repair capability. Round 6
must start moving that to a real product.

**Base:** `integration/round6-2026-09-06` = `integration/round5-2026-09-06` + all nine
round-5 lane branches, composed. This is **not** a merge to `main`: PR #73 (round 4) and
PR #79 (round 5) remain open and untouched, and the merge-debt recommendation is a
round-6 deliverable (Part II). Round 6 cannot proceed without R13's code, A1's repair
framework and A2's mathfix, all of which live in unmerged PRs — so the base composes
them, exactly as round 5 composed round 4.

**Four coordinated workstreams. Not nine lanes.**

| WS | Scope | Owns | Never touches |
|---|---|---|---|
| **A · TRUTH ACCOUNTING** | P0.1 R13 zero-silent-loss conservation (`INPUT = SERVED + WITHHELD + EXCLUDED_WITH_REASON + defined non-learning`; any unexplained difference = HARD FAILURE); reproduce 0.632→0.589, holdout 0.523, Bài 61 0.211→0.078; determine **what** disappeared and **why**; repair root causes where safe — *do not simply convert every lost region to WITHHELD*; recalculate affected round-5 metrics, preserving historical numbers and marking corrections. **A2: canonical lesson identity** — classify all 154 duplicated keys / 439 rows; `SourceLessonRecord` vs `CanonicalLessonIdentity` if evidence supports; report SOURCE ROWS · DISTINCT KEYS · TRUE DUPLICATES · KEY COLLISIONS · SOURCE VARIANTS · CANONICAL COUNT | `tool/corpus/accounting/**` (new), `tool/corpus/tc2_sdm.py` role layer, `tool/corpus/legacy/silent_loss.py`, `docs/research/TRUTH-ACCOUNTING-*.md` | recognition code (B), `lib/**`, packs |
| **B · RECOGNITION** | P0.2 the next bottleneck. **Failure census first — FORMS BEFORE RULES**: DIGIT LOSS · OPERATOR LOSS · FRACTION STRUCTURE · SUPERSCRIPT · SUBSCRIPT · ROMAN NUMERAL · DIACRITIC · SYMBOL CONFUSION · SEGMENTATION · MATH REGION · FORMULA · TABLE/STRUCTURE · OTHER. Then bounded candidates: corpus/template-assisted recognition · targeted high-resolution re-crop · alternative OCR observation · multi-engine disagreement · specialised STEM recognition · geometry-aware recognition · Docling formula enrichment where licensing-safe. Measure on SAM's **actual** failures, especially **274/336 fractions** | `tool/corpus/recognition/**` (new), `tool/corpus/mathfix/**`, `docs/research/RECOGNITION-*.md` | `tool/corpus/accounting/**` (A), `lib/**` |
| **C · REPAIR → PRODUCT** | P0.3 `OriginalObservation → RepairCandidate → Validator → ValidatedRepair → Trust/Disposition → Trusted Structured Content → LessonDocument → Learning View`. **CONNECT ≠ TRUST.** `ValidatedRepair` retains original observation · candidate · source grounding · failure class · repair method · validator+version · validation result · repair version · provenance · disposition. **No second provenance universe.** No mutation of historical learner evidence. Preferred path stays `WITHHELD → FAILURE CLASS → REPAIR CANDIDATE → VALIDATION → RESTORE`; **never weaken a guard for coverage** | `tool/corpus/repair/**`, `tool/corpus/tsl_to_lesson_document.py`, `lib/core/lesson_model/**`, `docs/research/REPAIR-INTEGRATION-*.md` | recognition internals (B), `lib/features/**` (D) |
| **D · GOLDEN DELIVERY** | P0.4 3–5 representative **real** lessons — Science · History · Math + one more if evidence supports; **at least one must exercise a real round-5/6 recognition or repair failure**; not cherry-picked easy ones. Prove `SOURCE → RECOGNITION → ACCOUNTED STRUCTURE → VALIDATED REPAIR → TRUST/DISPOSITION → TSL → LESSON DOCUMENT → LEARNING VIEW → REAL DEVICE`. **No fixture substitution in the final delivery claim.** Also: implement **Workspace OPTION B** (Founder-selected) — `💡 SAM gợi ý: <Next Action> →`, reason on demand, presentation of Next Action and **not** a second recommendation engine. Also: **bounded** visual-grammar continuation — forms census, semantic-pattern census, provenance architecture, bounded POC; **do not expand renderer families** | `lib/features/**`, `assets/fixtures/**`, `test/features/**`, `tool/evidence/**`, `docs/design/**` | `tool/corpus/**` (request from A/B/C) |

## Acceptance gates (fixed now, not redefined after results)

- **GATE A — ACCOUNTING** · zero unexplained silent loss on Golden + holdout
- **GATE B — RECOGNITION** · ≥1 previously unrecoverable OCR failure class materially improves **at recognition level**
- **GATE C — REPAIR** · a `ValidatedRepair` crosses the production-shaped pipeline
- **GATE D — TEACHING** · ≥1 real lesson becomes **honestly** eligible for teaching, target >0. **Do not lower trust/safety gates to achieve >0. A truthful zero is acceptable if evidence demands it.**
- **GATE E — DEVICE** · ≥1 Golden lesson on a real device visibly consumes validated/repaired real data, traceable `UI → LessonDocument → TSL → ValidatedRepair → Source`

## Early Founder checkpoint (Part XI) — do not wait for round end

Report as soon as all three are proven:
1. R13 conservation/accounting works;
2. ≥1 previously unrecoverable recognition case improves;
3. one `ValidatedRepair` crosses into production-shaped TSL **without automatically becoming trusted**.

## LLM rule (round-5 evidence: recall 0.717, false-correction 1.000, 13/13 wrong)

**MAY** detect anomaly · route · propose candidate · perform semantic review.
**MUST NOT** auto-correct canonical truth · be trust authority · silently rewrite corpus.
`LLM OUTPUT != TRUTH`.

## Standing rules carried into every future round

- **FORMS BEFORE RULES** — `FORM CENSUS → CLUSTER → REPRESENTATIVE EXAMPLES → RULE → HOLDOUT → MEASURE → GENERALIZE`. Never infer coverage from a few examples.
- **Composition check before round closure** — individual PR green ≠ integrated product green. Report INDIVIDUAL CI **and** COMPOSITION CI.
- **`false_correction_rate` is blind to a detector** — a workstream raising detection recall must report **false demotion rate** beside it.
- **Never turn PARTIAL into DONE.** Never silently rewrite history; historical metrics stay reproducible.
- `3,679` = **HISTORICAL BASELINE ONLY** until A2 resolves canonical identity.
- `OPENED != UNDERSTOOD` · `READ != MASTERY` · `TAP != COMPETENCE` · `REPROCESSED != TRUSTED` · `RESTORED != TRUSTED` · `TRACE != EVIDENCE`

## Governance

Autonomous: audit · bounded research · R13 fix · recognition POCs · repair integration ·
Golden Delivery · Workspace B · tests · device tests under existing protocol · Jira/Confluence ·
branches/PRs · disposable integration composition · local Desktop archives.

**Founder approval required:** MERGE · production trust threshold · mass corpus reprocess ·
destructive migration · unrestricted LLM generation · licensing / public SGK distribution ·
paid infrastructure · public release · fundamental irreversible architecture replacement.

**DO NOT MERGE.** Every PR ends at READY FOR FOUNDER REVIEW.
