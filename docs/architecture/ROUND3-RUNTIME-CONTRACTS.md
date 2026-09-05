# Round-3 runtime contracts — lane A-runtime (PROVE) · 2026-09-05 · WAL-210

**Status of every item: PROPOSED** (Founder D2 — bounded contracts only). Nothing here is
doctrine and nothing is "Founder-approved"; each item is the smallest mechanism that
makes one Founder order (A3–A8) *provable by a test*, on the golden slice **KHTN 6 (KNTT)
Bài 17 «Tách chất khỏi hỗn hợp»** (SGK tr. 60–63) and the existing Toán 5 Deep path.
Base branch: `integration/round3-2026-09-05` (= main + round-2 PRs #60/#61/#62/#63/#64/#65/#66).

Companion notes: `B-LANE-CONTRACTS-2026-09-05.md` (round 2),
`EVIDENCE-DURABILITY-AND-INTEGRITY-OPTIONS.md` (A4 research).

## Contract table

| # | Contract | Where | Definition | Held by |
|---|---|---|---|---|
| A3.1 | **`EvidenceValidation` stamp on events** | `lib/core/student/evidence_validation.dart`, `LearningEvent.validation` | `{validatorId, validatorVersion}`; JSON key `validation` (optional; absent ⇒ `null` = unvalidated or pre-contract). Never rewritten on disk. | `validated_evidence_doctrine_test` §1, `evidence_durability_test` |
| A3.2 | **`ValidatedEvidence` mintable only by a registered deterministic validator** | `DeterministicValidator.grade` → `ValidatedEvidence._` (library-private ctor) | Registry `approvedEvidenceValidators` is a closed const: `fraction-check-v1` (grants competence), `candidate-gate-v1` (participation only). Unregistered validator ⇒ `grade()` = `null`. Every entry declares `deterministic == true` (test-enforced). **No validator for Scale surfaces** (pack option keys, self-reports). | doctrine test §1 |
| A3.3 | **Deep path stamps** | `TutorSession` (all events with `correct != null`), `validateCandidateEvidence` (participation, `candidate-gate-v1`), `attributeEvidence` (carries the caller's stamp) | `TutorSession` refuses to open without a registered validator for its `SolvableProblem` (`ArgumentError`, fail closed) and refuses an injected validator that is not in the registry. | `tutor_lineage_a5_test`, `evidence_durability_test` |
| A3.4 | **Rejected stamp rule** | `LearningEvent.hasRejectedValidation`, `isValidatedIndependentSuccess`, `ConservativeBktPolicy`, `parentLineFor` | An event stamped by an unregistered / non-competence validator is **never** independent success: map state ⇒ `engaged`, BKT ⇒ `noOp`, parent line never "Con đã tự làm được". | doctrine test §3–4 |
| A3.5 | **Structural doctrine** | `test/core/student/validated_evidence_doctrine_test.dart` §2 | Every `LearningEvent(` in `lib/` with a non-null `correct:` must pass `validation:`, except the explicit allowlist: `assessment_screen.dart` (Deep, needs `fraction-check-v1` — one line, Lane B/coordinator), `reader_screen.dart`, `quiz_select_screen.dart` (Scale pack keys — Founder decision, see below), `mission_data.dart` (demo domain). The allowlist may only shrink. | doctrine test §2 |
| A3.6 | **Strict consumption mode (available, NOT default)** | `ValidatedOnlyBktPolicy` (`validated-only-bkt-v1`), `learningMapStateFor(requireValidation: true)`, `StudentLessonState.hasApprovedValidatedSuccess` | With strict mode, a graded event **without** a stamp (pre-contract data, unstamped emitters) does not move mastery and reads as `engaged`. Default remains the #63 legacy read (unstamped graded events count) until the Founder decides the legacy rule — flipping the default retroactively removes «Tự làm được» for every pre-contract history and breaks Lane-B-owned tests (`home1`, `parent_area`, `subjects_screen`, `assessment`, `knowledge_state`, `profile`, `progress`, `learning_map`) and the Home demo domain. **A8 already uses the strict signal** for "next lesson". | doctrine test §3, `lesson_next_action_test` |
| A4.1 | **Integrity regression on top of #60** | `test/core/store/evidence_durability_test.dart` | Torn last line keeps earlier sessions, also after the whole-file rewrite; re-open ×2 + retry of the same session ⇒ one line on disk, one session, `evidenceCount 1`; re-open of the same exercise ⇒ counted; validation stamp survives disk. | that test |
| A4.2 | **Durability/integrity options** | `EVIDENCE-DURABILITY-AND-INTEGRITY-OPTIONS.md` | Research only: D1 atomic rename, D2 true append, D3 = D1+D2 (recommended to propose), D4 SQLite (not justified); I1 hash, I2 hash chain (recommended to propose), I3 HMAC, I4 signed checkpoints; migration path. **No storage change made.** | — |
| A5.1 | **Lineage only from a resolved context** | `TutorSession.inContext(learningContext:)`, `TutorSession.lineageFromContext`, `LessonRef.fromContext` | Stamp `(sourceDocumentId, lessonNo)` **iff** `LearningContext.hasLesson`; Global/Subject/Book-tier contexts ⇒ `(null, null)` (no half stamp). Camera-originated sessions (`CanonicalProblem.fromConfirmedPerception`) default to `null/null` on the session and on every event. Same rule `openCanonicalProblem(learningContext:)` already applies. | `test/features/tutor/tutor_lineage_a5_test.dart` |
| A6.1 | **`SemanticBinding`** | `lib/core/curriculum/semantic_binding.dart` | `{activityId, lessonRef, conceptId?, skillCaseId?, methodIds[], bindingSource ∈ {fixture, curated, derived}, confidence, provenance {curatedBy, basis, note}, status = 'PROPOSED'}`. `methodIds` are **candidates**, never permissions. | `semantic_binding_test` |
| A6.2 | **RETRIEVED ≠ PERMITTED for bindings** | `resolveBinding(binding, BindingCurriculum?) → ResolvedBinding` | `allowedMethods = declared ∩ TutorScope.forProblem(concept, case, stage, catalogue) ∩ {provenance.origin == sourceStated ∧ citableAsTextbookFact}`. Missing curriculum / concept / case ⇒ no scope (`NO_CURRICULUM`, `NO_CONCEPT`, `NO_SKILL_CASE`); every dropped method carries `METHOD_NOT_IN_SCOPE`, `METHOD_NOT_SOURCE_STATED`, or `METHOD_NOT_DECLARED_IN_BINDING`. | `semantic_binding_test` |
| A6.3 | **Registry = one binding** | `SemanticBindingRegistry` (closed const), `lib/core/curriculum/khtn6_bai17.dart` | Bài 17 «Học với SAM» (`mode3:tutor-script`) → concept `tach-chat-khoi-hon-hop` / case `chon-cach-tach-theo-tinh-chat` / method `tach-chat-theo-tinh-chat` with `Provenance(sourceStated, 06-sgk-khoa-hoc-tu-nhien-6, pageStart 63)` — grounded in TSL `tc2-p1/bai-17` blocks 1:006 (objective), 4:003–007 («Em đã học», PDF 64 → printed 63), 3:011 (SGK question, tr. 62). The method has **no hints** (no SGV, `answer_keys_included: false`). The entry is **not** registered in `curriculumForProblem` (camera path unchanged). Any other lesson/activity ⇒ `null`. | `semantic_binding_test` |
| A7.1 | **`PedagogyRuntime.planForScript`** | `lib/core/pedagogy/pedagogy_runtime.dart` | `(TutorScript, ResolvedBinding?, StudentLessonState, LearningContext, blockText?) → RuntimePlan{steps: PlannedStep[], planRefusals, evidencePolicy}`. Step mapping: explain → `explainConcept@demonstration` (needs method + source block); ask → `diagnosticProbe@independent` (method-free; prompt must be **verbatim** a source block); hint i → `smallHint/strategicHint` (needs method; `HINT_UNSOURCED` today); feedbackMatched → `reflect@independent` (`KEY_NOT_VALIDATED`); scaffold → `revealAnswer@workedSolution` (`KEY_NOT_VALIDATED`, `OVER_CAP_WITHOUT_VALIDATOR`); next → `stepBack@independent`. Text is always verbatim from the script — the runtime writes no words. | `pedagogy_runtime_test` |
| A7.2 | **Per-step mode** | `PlannedStepMode {runtimeGuided, prototypeScripted}` with `samModeName` = `'runtimeGuided'` / `'prototypeScripted'` and `childLabel` | A step is `runtimeGuided` only if **all** hold: context resolved to the binding's lesson, binding has scope, act is method-free or an allowed (sourceStated) method exists, text traceable to a source block, `validateRealization` passes (`DerivedFacts.textOnly(answerForms from literal `acceptable`)`, lowercased). Otherwise `prototypeScripted` with reason codes. **`SamMode.runtimeGuided` is not added** — `lib/core/lesson_model/content_trust.dart` is Lane A-data's file and its test pins `SamMode.values == [prototypeScripted]`; Lane B maps `PlannedStepMode.samModeName` until Lane A-data adds the value. | `pedagogy_runtime_test` |
| A7.3 | **No evidence from the runtime** | `PlannedStep.validator` (always `null`), `RuntimePlan.evidencePolicy` | No registered validator exists for regex/free-text answers ⇒ participation-only, as Track B today. Runtime files contain no `LearningEvent(`, store, network, or LLM symbol (scanned). | `pedagogy_runtime_test` |
| A7.4 | **Measured on the Bài 17 synthetic fixture** | — | 12 planned steps: **4 runtime-guided** (explain e1, asks q1 q2 — verbatim SGK questions, next n1), **8 prototype** (4 hints, 2 feedback, 2 scaffold). The guard flags three real answer leaks in prototype hints (`q1#1` names «Cô cạn», `q2#0/#1` name «nặng»). The real fixture (gitignored) is expected to behave the same shape; its "SÁCH VIẾT … trang 62" feedback would additionally be refused as `GUARD:CITATION_FABRICATION` (citations must be rendered from `sourceBlockId`, not embedded in text). | `pedagogy_runtime_test` |
| A8.1 | **Lesson-level Next Best Learning Action** | `lib/core/agenda/lesson_next_action.dart`, `NextBestLearningAction.forLesson` | Rules in order: R0 context unresolved / lesson mismatch ⇒ contents (fail closed); R1 `hasApprovedValidatedSuccess` ⇒ next lesson (if known) else contents; R2 Đọc not seen ⇒ 📖; R3 read seen ∧ SemanticData ∧ Trực quan not seen ⇒ ✨; R4 read (+visual if any) ∧ script ∧ SAM not seen ⇒ 🦉 quoting the first SGK question; R5 all seen ⇒ contents with participation wording. `viewsSeen` is UI trace (not evidence); evidence comes from `StudentLessonState`. Never minutes/percent/mastery (scanned). Differs from Track B's `nextActionFor` (visual-first) — reconciliation for Lane B. | `lesson_next_action_test` |
| A8.2 | **`StudentLessonState`** | `lib/core/student/student_lesson_state.dart` | `fromEvents(LessonRef, allEvents)` → `{mapState, eventCount, hasApprovedValidatedSuccess}`; same lineage filter as Learning Map / Parent (one truth). | `lesson_next_action_test`, `pedagogy_runtime_test` |
| #7 | **Cross-grade source assets** | `LessonIndex.sourceAssetsFor(subject)` | Asset kept iff subject matches **and** its book is on the pack's shelf (`books`) or its id carries the grade prefix `NN-` equal to `grade`; unprovable ⇒ dropped. | `test/features/subjects/lesson_index_source_assets_grade_test.dart` |

## APIs for Lane B (Lesson Workspace)

```dart
// A6 — resolve the binding for the lesson the workspace is showing
final ref = LessonRef(doc.book, doc.lessonNo);
final binding = SemanticBindingRegistry.resolveFor(ref, SemanticBinding.tutorScriptActivity); // null ⇒ no runtime

// A8 — student state from the store (or unseen when the workspace has no store)
final state = StudentLessonState.fromEvents(ref, allEventsOfLearner); // or StudentLessonState.unseen(ref)

// A7 — plan the script; render each step with step.mode.childLabel (per step, not per script)
final plan = PedagogyRuntime.planForScript(
  script: doc.tutorScript!, binding: binding, studentState: state, context: learningContext,
  blockText: (id) => (doc.blockById(id) as dynamic)?.text as String?, // text of a source block
);
// plan.isBound, plan.runtimeGuidedCount, step.refusals (show as internal note, never to the child)

// A8 — «SAM đề xuất»
final next = NextBestLearningAction.forLesson(
  state: state, context: learningContext,
  lesson: LessonSummary.fromDocument(doc, nextLesson: chapterNext), viewsSeen: trace.seen);
// next.kind / next.view / next.reason / next.rule
```

Lane B must not construct `PlannedStep` or `EvidenceValidation` itself; it consumes plans and
actions. The only kind of evidence a workspace may ever mint stays `participation` (#63).

## Returned for Founder review

1. **Legacy read rule for graded events without a validator stamp** (A3.6): keep the #63
   read (counts, current default) or switch to `ValidatedOnlyBktPolicy` + `requireValidation`
   (loses «Tự làm được» for all pre-contract history). Option: a replay-only legacy table
   `{policyId 'tutor-session-v1' | 'assessment-v1' → fraction-check-v1}` — not implemented (it
   infers a validator from a policy id).
2. **Scale pack option keys** (`reader_screen`, `quiz_select_screen`): register a
   `pack-option-key-v1` validator (would grant competence from a pack-built key) or leave
   those picks as legacy-unstamped (today) / participation. Not decided here.
3. **`assessment_screen.dart` stamp** (`fraction-check-v1`, one line) — outside this lane's
   files; needed before A3.5's allowlist can shrink.
4. **`SamMode.runtimeGuided`** in `content_trust.dart` (Lane A-data) so the UI label is one
   enum; until then `PlannedStepMode.samModeName` carries the same strings.
5. **Durability D3 + integrity I2** (A4) — adopt, defer, or reject.
6. **Bài 17 method provenance**: `sourceStated` at printed p. 63 is read from the TSL «Em đã
   học» block; the printed-page offset (PDF 64 → 63) follows the TSL boundary 61–64 ↔ 60–63 —
   please confirm against the physical book before any child-facing citation.
7. **Next-action rule order**: Founder A8 order (Đọc → Trực quan → SAM) vs Track B's
   prototype (Trực quan first when a process diagram exists) — one must win in the UI.
