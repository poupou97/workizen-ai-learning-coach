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

---

# FOUNDER ADDENDUM — GOLDEN DELIVERY DECISION (2026-09-06)

Lesson selection is **decided**. No workstream runs its own selection.

| Slice | Lesson | Purpose |
|---|---|---|
| **GOLDEN #1** | **LS&ĐL 5 Bài 8** | Prove `REPAIR → TSL → LESSON DOCUMENT → APP → REAL DEVICE`. **Primary delivery slice** — the round's delivery claim rests on it. |
| **GOLDEN #2** | **Toán 4 tập hai Bài 61** | Prove **R13 accounting + recognition recovery**. **Not** a learner-facing delivery target. |
| **REGRESSION** | **KHTN 6 Bài 17** | Prove round 6 does not break the existing real workspace. **Not** proof of repair effectiveness — it exercises essentially no repair. |

## Golden #1 — the required chain, every link

```
real source → current observation/SDM → repair ledger → ValidatedRepair
  → projected/repaired TSL → LessonDocument generated FROM that TSL
  → assets/fixtures/real/ → WorkspaceCatalog real-path load → real device
```

**Do NOT use the old round-4 LessonDocument as the final proof.** Prove lineage **with hashes**.

**Verified by the coordinator — no new loading path is needed, exactly as the Founder required:**

- `lib/core/lesson_model/workspace_catalog.dart:76-77` already tries `realPath` **then** falls back to `syntheticPath`.
- The slot is already registered: `FixtureSlot(book: '05-sgk-lich-su-va-dia-li-5', lessonNo: 8)` at `:47`, key `05-sgk-lich-su-va-dia-li-5#8`, and it is a **research slot** (`researchSlotKeys`, `:53`) so it carries the mandatory experimental chip.
- `_stem()` is `lesson-$book-b$lessonNo`, so the exact file the app will prefer is:

  **`assets/fixtures/real/lesson-05-sgk-lich-su-va-dia-li-5-b8.json`**

- `assets/fixtures/real/` currently holds **only** `lesson-06-sgk-khoa-hoc-tu-nhien-6-b17.json` (plus `crops/`). **There is no real Bài 8 fixture, so the app is loading the synthetic fallback today.**

Early-checkpoint item **C** is therefore precisely: *that file exists, generated from the round-6 projected/repaired TSL, so `_try(realPath)` succeeds.* **No `lib/` change is required to achieve it** — and if one appears to be, that is a signal something is being special-cased.

## Repair gate

Round 6 has `ValidatedRepair` code and `tsl_projection.py` but **no projected TSL artefact**. **That is not integration.** Produce a real projected TSL for Golden #1, and demonstrate at least one validated repair crossing `RepairLedger → Projected TSL → LessonDocument`. **Do not automatically promote a repair to TRUSTED**; disposition and trust rules stay fail-closed.

## The sharp case — LS&ĐL 5 Bài 8, block `p039:000`

One tone disagreement («Bạch **Đằng**» primary vs «đăng» verifier — **the print says the primary was right**) withheld the single block carrying **all seven dated events**. Round 6 must show what happens to it now: **repaired and validated → exact lineage; still withheld → report honestly.** **Do NOT restore the timeline by special-casing lesson identity.**

Prior art (Lane C, PR #81): the block is recoverable as a **disposition repair — text unchanged** — and with the verbatim gate ON yields **8 events** (round 4's seven plus the «Âu Lạc (179 TCN)» anchor round 4 lost). The same lane also showed the correct negative: a proposed attribution correction was **rejected** by two independent signals, so the attribution stopped being served rather than being half-corrected. **Both behaviours must survive integration.**

## Fixture version safety — hard requirement

Every real fixture used for Founder or device evidence records: **source TSL hash · pipeline version · SDM version · repair version · generator version.** A fixture reproducible from `tc2-p1` / `sdm-v2` is **not** a current-pipeline fixture. **Do not silently mix generations.**

## Math — do not fake delivery

The bridge has no formula role mapping; `LessonDocument` has no formula type; the app has no math renderer; the pack path drops provenance/status. **Do not claim Math structure reaches a child until that path exists. A withheld crop is not structured Math delivery.** Learner-facing Math is explicitly **not** required this round.

## The delivery claim — the exact bar

Round 6 may claim **«VERIFIED ACCURACY REACHED THE LEARNER»** *only* if the device-loaded Golden #1 file traces to a current round-6 projected/repaired TSL. **Old generated documents or synthetic fallback do not count.**

## Early checkpoint — return as soon as all three are true

- **A** (WS-A) · R13 ledger has **zero unexplained loss** on one Golden slice
- **B** (WS-C) · a **projected TSL containing a `ValidatedRepair` exists on disk**
- **C** (WS-D) · **LS&ĐL 5 Bài 8 real fixture loads instead of synthetic fallback**

C depends on B; B depends in practice on A. Then continue to real-device verification.
