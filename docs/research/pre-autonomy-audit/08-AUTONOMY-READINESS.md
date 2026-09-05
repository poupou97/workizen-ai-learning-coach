# 08 — Autonomy readiness verdict · 2026-09-05

## Verdict: **C — NOT READY — RESOLVE P0 FIRST** (with a narrow B-lane for mechanical, test-backed work)

Why C and not D (rebase): the kernel is proven and coherent — fail-closed method gating, raw-event evidence, replayable BKT, three-axis claims, provenance rendering, perception boundary — all TEST-PASSED with real data (`03` §B.4, `04` C.1). Nothing measured says the architecture must be replaced. Why C and not B: five P0 gaps (`07` #1–#5) are decisions or measurements the agent cannot make on its own, and two of them (self-report → competence claim; untrusted shipped text with no false-trust audit) directly touch what a child sees and what a parent is told.

## Layer scorecard (evidence in 02/03/04/05)

| Layer | Rating | One-line basis |
|---|---|---|
| A · Data / trusted corpus | **RED** (trusted) · YELLOW (wired) | Trust exists only for 238 Science lessons (all PARTIAL, FTR ≈ 0.10–0.12 on hard pages); the shipped 113 come from the FTR-0.32 extractor; 0 device evidence on disk; packs on disk are the experiment build |
| B · Learning architecture | **YELLOW** | Kernel proven on 1 lesson; six forks open (`03` §B.6); four named concepts have no code; docs disagree with code and Jira |
| C · Product / runtime | **YELLOW** | Closed loop real for one lesson; fail-closed at the kernel; two evidence truths, integrity defects (C1/C3/C9), pedagogy runtime dormant, licence contradiction |
| D · UI/UX vs concept | **RED** vs the approved Lesson-Workspace concept · YELLOW as a reduced product | Overall 20–30 % of the approved concept; Learning-View concept 5–15 % (no Lesson Workspace, no Smart Book, no Trực quan, no in-lesson SAM); SAM Tutor 15–25 % (rules-only, one lesson, unreachable for the lớp-6 learner); visual tokens 55–65 %; navigation 35–45 % (`05`) |

## What Claude may run autonomously now (B-lane; every item = PR → CI → READY FOR FOUNDER REVIEW, never merge)
- Build-provenance manifest for packs + a test that a default build carries no `pattern-router*` entries (`07` #3).
- Unique `eventId`s and idempotent `appendSession` with tests (`07` #4, mechanical half).
- Lineage threading: `LearningContext` → every Scale emitter + one test per surface (`07` #6), excluding the Tutor stamp decision.
- Capped/header-based attachment and lesson-identity check in `build_lesson_index.py` (`02` gates G2/G3), regenerating packs with the regression oracle byte-identical.
- The two honest UI defects (identical "Đọc bài" chooser labels; Home card ignoring Scale lessons) as bounded PRs.
- Route-or-delete the unrouted `QuizSelectScreen`; replace the `knowledgeModelVersion` constant with a per-pack value; remove the `'unknown-case'` fallback in favour of refusing to grade.
- Research-only: Role Layer signal work (icon/colour), gold extension, statistical false-trust audit *protocol* (not its acceptance).

## What must stay behind the Founder gate
- The evidence contract for ungraded self-reports (`07` #1) and any change to what the Learning Map / parent summary may claim.
- Locking the six architecture forks (`03` §B.6) incl. WAL-196 truth, runtime containment F-a…F-d, LearningContext ↔ LearningView.
- Acceptance thresholds for false trust on shipped lessons; adopting header-repaired denominators; the canonical count.
- Licence: verbatim SGK text and page images to learners (`07` #8).
- Any LLM wiring (WAL-30), Short-Answer Surface, 27-pattern expansion, mass Learning Views implementation, full-corpus reprocess — all explicitly deferred by the Founder.

## What must never be auto-expanded
- Coverage numbers (lessons "learnable"/"proven") without the G1–G3 gates; router/EXPLAIN variant content in default builds; any surface that grades without an SGV key; any claim to a parent derived from a tap; any content path that bypasses `LessonIndex` fail-closed parse or the SourceAsset boundary.

## If a night run is allowed, the safest tasks (in order)
1. Pack build-provenance manifest + test (no product behaviour change).
2. Evidence-store id uniqueness + idempotent append + tests (fixes C1/C3, no semantic change).
3. Lineage threading PR (data completeness, no new claims).
4. `build_lesson_index.py` attachment cap + identity check + pack regeneration with byte-identical `khoaExperiments`.
5. Chooser label / Home card defects.
Each stops at READY FOR FOUNDER REVIEW with its own evidence folder and device screenshot retained in the repo-adjacent bundle.

## Success criteria for the next autonomous round (measurable, no coverage targets)
- A default build is provably default: manifest asserted by test; 0 router entries; regression oracle byte-identical.
- C1 and C3 pass; a retried `onFinished` does not change mastery; ids unique across re-open.
- 100 % of Scale emitters carry `sourceDocumentId/lessonNo`; Learning Map no longer says "Chưa học" for a completed lesson (device screenshot retained).
- Attachment: every shipped `khoaExperiments` entry resolves to a canonical lesson and lies inside a capped/header range; the 3 mis-attached KHTN/Khoa học experiments are gone or withheld.
- No new claim vocabulary reaches a parent; `ConceptSummary` unchanged; `flutter test` green with packs (647) and without (633 + skips accounted for).
- Every PR: READY FOR FOUNDER REVIEW, none merged; evidence retained on disk and in the bundle.
