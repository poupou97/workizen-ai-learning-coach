# B-lane contracts — 2026-09-05 (WAL-210, Dart lane)

Status of every item below: **PROPOSED** (Founder D2: bounded contracts only, no
convergence work). Each contract is the minimum the pre-autonomy audit
(`docs/research/pre-autonomy-audit/`, PR #59) needed to close a measured defect; each
carries its definition (D5) and the test that holds it. None of this is doctrine — it
is mechanics under Founder decision **D1** (self-report ≠ competence). Anything the
mechanics could not settle is listed under *Returned for Founder review* in the PRs.

| # | Contract | Where | Definition (D5) | Held by |
|---|---|---|---|---|
| 1 | **Unique event ids** | `lib/core/student/evidence_ids.dart`; all seven emitters (`TutorSession`, Reader, Compose, SourceReader, MapReader, Experiment, Assessment, QuizSelect) | `eventId = '<exerciseId>@<sessionToken>#<seq>'`. `sessionToken = base36(openedAt µs) + '-' + base36(process ordinal)`, created **once** per opened session (wall clock; never the injected test clock). `exerciseId` on the event is unchanged. Old ids (`…#0`) are not rewritten. | `test/core/store/evidence_integrity_test.dart` (audit C1/C2), `test/features/evidence_id_uniqueness_test.dart` |
| 2 | **Idempotent `appendSession`** | `LearnerStore.appendSession → Future<bool>` (`JsonlLearnerStore`, `FileLearnerStore`); `RecordedSession.appended` | A `sessionId` already present (in memory or loaded from disk) ⇒ no-op, returns `false`; no file rewrite. Delete-then-append is accepted (no ghost id set). On-disk format unchanged. | `evidence_integrity_test.dart` (audit C3) |
| 3 | **No `'unknown-case'` bucket** | `AssessmentScreen` | An item with `skillCaseId == null` is shown as "chưa xác định được dạng bài", has no answer field, mints **no** event of any kind (participation needs a real case), and is skipped. | `test/features/assessment/assessment_test.dart` (+ `lib/` literal scan) |
| 4 | **`EvidenceKind.participation`** (Founder D1) | `lib/core/student/learning_evidence.dart` | Ungraded self-report / completion. `correct` always `null`. BKT `interpret` ⇒ `noOp`; `isAttempt == false`; excluded from `EvidenceLog.independentAttempts`. Minted by: Reader open-answer tap and ungraded option pick, Compose draft submit, SourceReader stance, MapReader done, `validateCandidateEvidence` (every claim, any `support`), QuizSelect ungraded pick. JSON name `participation` (append-only compatible; old readers that do not know the name drop the event, never coerce it). | `test/core/student/self_report_doctrine_test.dart` + each surface test |
| 5 | **Legacy read rule** | `LearningEvent.isParticipation`, `LearningEvent.isValidatedIndependentSuccess` | `isParticipation = kind == participation ∨ (kind == independentAttempt ∧ correct == null)` — old data read as participation, **not rewritten**. `isValidatedIndependentSuccess = kind ∈ {independentAttempt, selfCorrection} ∧ correct == true`. | `self_report_doctrine_test.dart`, `learning_map_state_test.dart` |
| 6 | **`LearningMapState.participation`** | `lib/core/student/learning_map_state.dart` | Four states, priority `independentEvidence` (any validated independent success) › `engaged` (any non-participation event) › `participation` (only self-reports) › `unseen`. Child label `🟣 Đã học`; `🔵 Tự làm được` only for `independentEvidence`. | `learning_map_state_test.dart` |
| 7 | **Parent line for participation** | `parentLineFor` | `'Con đã học <Bài N> — con tự báo đã làm xong; SAM không chấm phần này.'` — completion wording; the words "tự làm được" appear only for `independentEvidence`. | `test/core/coach/parent_session_summary_test.dart` |
| 8 | **Lineage on every Scale event** (audit C7) | Reader, Compose, SourceReader, MapReader (new optional `learningContext`, honours `lookup`), Experiment (via validator), `AssessmentScreen.learningContext`, `TutorSession.sourceDocumentId/lessonNo` | Every event emitted from a pack lesson carries `sourceDocumentId` + `lessonNo` from `LearningContext`. Map: book from `DiaMap.book`, lesson from `DiaMap.lesson` (new optional pack field) else context. Assessment: book from the exercise; lesson only when the context is about that same book. Tutor: lesson only when opened from a pack exercise (`openCanonicalProblem(learningContext:)`); **camera-originated problems stay `null`** (returned for Founder review). | `test/features/subjects/scale_lineage_test.dart` (KHTN 6 Bài 17 fixture + pack-gated) |
| 9 | **`buildProvenance` / `packVersion`** (shared with the Python lane) | `LessonIndex.buildProvenance` (`BuildProvenance`), `LessonIndex.packVersion` | Top-level pack field `buildProvenance` = `{schema:int, builderVersion, gitSha, builtAt:ISO-8601, grade, flags{PATTERN_ROUTER, UNITS_SOURCE, ROUTE_EXPLAIN}, experimental:bool, attachmentRule, contentHash:sha256(pack minus this field), packVersion:"<grade>-<builtAt-compact>-<sha8>"}`. Fail-closed: missing/ill-typed `schema`, `packVersion` or `experimental` ⇒ `buildProvenance == null`, nothing else changes. | `test/features/subjects/lesson_index_test.dart` (group `WAL-210 buildProvenance`) |
| 10 | **`LearningContext.knowledgeModelVersion`** | `lib/core/context/learning_context.dart`; built at the three context sites in `subject_home_screen.dart` from `index.packVersion` | Scale emitters stamp `knowledgeVersion = context.knowledgeModelVersion ?? knowledgeModelVersion` (legacy constant only when the pack declares no provenance). Compose stamps `context.knowledgeModelVersion` (it never carried the Toán constant; `null` stays `null`). The Deep path (Tutor, Assessment) keeps `slice-toan5-b6-v1+qmap-v1`. | `scale_lineage_test.dart` |

## For Track B (Lesson Workspace) — how to stay evidence-free

- A prototype surface that must emit **no** learning evidence simply does not construct
  `LearningEvent` and does not call `recordSession`. If it ever needs to acknowledge a
  tap, the only kind allowed for an unvalidated tap is `EvidenceKind.participation`.
- The doctrine test `test/core/student/self_report_doctrine_test.dart` scans `lib/` for
  the two textual patterns that used to turn a tap into `independentAttempt`
  (`independentAttempt, null)` and `kind: EvidenceKind.independentAttempt … correct: null`);
  any new emitter is covered automatically.
- Lineage: if a surface does emit, it should receive a `LearningContext` and stamp
  `sourceDocumentId`, `lessonNo`, and `knowledgeVersion: context.knowledgeModelVersion`.

## Not in these contracts (unchanged, Founder-owned)

Whole-file rewrite / tamper detection of the JSONL store (audit C9); the licence
contradiction on verbatim SGK text (audit C.2(2)); which lesson a camera-originated
Tutor session should be stamped with; the kind of Compose revision events
(`guidedAttempt` / `selfCorrection` with `correct == null`).
