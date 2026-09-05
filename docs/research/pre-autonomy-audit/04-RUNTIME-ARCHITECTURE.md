# 04 — Layer C: Product / Runtime Architecture audit («Học cùng SAM», Founder pre-autonomy checkpoint 2026-09-05)

**Scope and method.** Same worktree, same rules as 03 (read-only; `flutter analyze`, `flutter test`, one Dart check script, one pack-count test; Jira read-only). Long tables: `data/04-segment-evidence-table.md` (segment × code path × test), `data/04-runtime-checks.md` (check results, skipped tests, LLM surface). Labels: OBSERVED-IN-CODE · TEST-PASSED · TEST-FAILED · DOC-CLAIM · RESEARCH-ONLY.

**Totals.** `flutter analyze`: no issues. `flutter test`: **633 passed / 14 skipped / 0 failed** without packs; **647 / 0 / 0** with the gitignored packs present. Runtime checks: 10 checks, **2 FAIL (C1, C3), 4 CONFIRMED defects (C6, C6b, C7, C9)**, rest PASS.

---

## C.1 Segment statuses (detail in `data/04-segment-evidence-table.md`)

| Segment | Status | Evidence in one line |
|---|---|---|
| Source (PDF → OCR) | RESEARCH ONLY (Python, offline) | `tool/ingest/*`, outputs in gitignored `poc-out/`; no Dart, no test |
| SDM / source extraction | RESEARCH ONLY | `tool/corpus/tc_sdm.py`, `layout_extract.py`, `tool/ui/pattern_router.py` on main; TC-v2 `tc2_*` only on the research branch; nothing reaches Dart (branch `F.1`, `G.5`) |
| Trusted Structured Lesson | MISSING in app (nearest: `LessonIndex` pack = PARTIAL) | `lesson_index.dart:390-624` fail-closed parse; no block id / trust / role in Dart; TEST-PASSED `lesson_index_test`, `architecture_gate_test` (with packs) |
| Learning Surface | PROVEN (6 reachable) | Reader/Compose/Experiment/SourceReader/MapReader/Tutor + Assessment; `QuizSelectScreen` built but **unrouted** (0 constructions); `resolveSurface` 0 callers |
| Pedagogy Runtime | PARTIAL | live: `decide()` + `TutorSession` ±1 ladder + `AssistancePolicy`; dormant: blueprints, patterns, `PlannedAct`, `validateRealization` (0 runtime callers) |
| SAM realization | PROVEN deterministic · LLM SHADOW | `hintTextFor`, `feedbackFor`, `sourceLineForChildOf`; no LLM client in app; `buildTutorPrompt` 0 callers |
| Learner Action | PROVEN | `TutorSession.submit/requestHint`, surface handlers; one event per action |
| Evidence | PROVEN with integrity caveats | 10 mint sites → `recordSession` (single writer) → JSONL; C1/C3 FAIL, C9 tamper undetected |
| Student State | PARTIAL, two disjoint functions | BKT/`ConceptSummary` over 2 cases; `LearningMapState` over lineage (experiment events only) |
| Next Action | PARTIAL | agenda over 1 concept; `decide` with hard-coded case; timetable-only book recommendation; REST first-class; grade ≠ 5 ⇒ static message |

**Closed loop that is real today (TEST-PASSED `slice_flow_test:158`, `session_recorder_test:25`):** camera or pack exercise → `ConfirmedProblem` → `curriculumForProblem` → `decide` → `TutorSession` → `recordSession` → `masteryFromStore` → `KnowledgeStateScreen` → Home changes. Reach: one lesson's two skill cases, grade-5 learners.

---

## C.2 The seven verification questions

### (1) Is fail-closed actually enforced?
**Yes at the kernel, with two holes at the edges.**
- `LearningActivity.gradable` false when `correctOption` null or out of range (`learning_activity.dart:81-83`; C4, C4b PASS). Reader/Quiz then mint `correct: null` and refuse to judge (`reader_screen.dart:114-118`, `quiz_select_screen.dart:78-83`; TEST-PASSED `reader_screen_test:139`, `quiz_select_screen_test:136`). `TvQuestion` has no answer field by construction (`lesson_index.dart:62-71`).
- Unknown case ⇒ `TutorScope.allowedMethods = []` (`pedagogical_boundary.dart:221`; C5 PASS) ⇒ `decide` says "chưa xác định được dạng bài" (`adaptive_engine.dart:103-111`) ⇒ no "Làm bài này" button (`slice_flow.dart:229-255`); `requestHint` returns null but still logs `hintRequested` (C5d).
- Unknown/unpermitted method ⇒ `explainTeaching` null, `buildTutorPrompt` null, `lineageFor` → `methodNotAllowed`/`methodUnknown` (C5b, C5c; TEST-PASSED `lineage_test:65-134`).
- Unknown shape on disk ⇒ event/session dropped, never defaulted (`learning_session.dart:97-136`; TEST-PASSED `learner_store_test:206,220`).
- **Hole A:** `assessment_screen.dart:86` mints graded evidence under `skillCaseId: e.skillCaseId ?? 'unknown-case'` — UNKNOWN becomes a bucket instead of a refusal (harmless today because no state reads that bucket, but it is evidence under a fake case).
- **Hole B:** `hintTextFor` returns `''` when a method has no hints (`tutor_session.dart:207`) and the UI shows nothing — silent rather than an explicit "chưa chắc" (only the empty-scope path speaks).

### (2) Is retrieved ≠ permitted enforced? Where can content reach the learner without a permission check?
- **Methods:** yes, type-enforced — `allowedMethods` is `required` with no default, computed as APPLICABLE ∩ ALLOWED (`pedagogical_boundary.dart:207-232, 258-277`); every consumer (`tutor_session.dart:150`, `teaching_provenance.dart:81`, `tutor_prompt.dart:39`, `lineage.dart:161`) fails closed. TEST-PASSED in 8 files.
- **Everything else is not gated by permission at all.** No RAG exists at runtime (`KnowledgeContentProvider` has 0 implementations; `sam-units.db` has no Dart consumer). Pack content reaches the child after **shape** checks only: Reader passages and questions (`subject_home_screen.dart:824-833` → `reader_screen.dart`), Sử excerpts (`source_reader.dart`), experiment steps (`experiment_screen.dart`), map questions and crops (`map_reader_screen.dart`, `source_gallery_screen.dart`), stories (`stories_store.dart` — runtime VERIFIED filter `:85-107`). This is by design ("trace, not evidence"), but it means the licence declaration `ContentLicense.localResearchOnly` — "Không hiển thị nguyên văn cho người dùng cuối" (`knowledge_content_provider.dart:16-18`) — is **contradicted by the running app**, which displays SGK passages verbatim. The only enforcement is the `SourceAsset` path assert (`learning_asset.dart:42`) and the `.gitignore`. Branch doc `J.1` calls page-image delivery a legal gate; text delivery has the same gap and no gate.
- Where a permission check would be bypassed *if* an LLM were wired: any `String` can be put into a widget; `validateRealization` is not required by any type (see Q7).

### (3) How are unknown role / unknown method handled?
- Unknown capability id ⇒ `CapabilityDecision.disable` (`education_safety_policy.dart:78-79`; TEST-PASSED `education_safety_policy_test:10`).
- Role: `AppRole.student` is denied every parent feature before tier is consulted; missing PIN denied (`entitlement.dart:84-90`; TEST-PASSED `entitlement_test:76`). Learning capabilities can never be asked about commercially (`refuseLearningCapability` throws, `:103`).
- Unknown method: see (1) — null/empty everywhere; on stored data `LineageViolation.methodUnknown`.
- Unknown `ResponseKind` (`shortText`) ⇒ `unsupported`, never coerced to quiz (C4c; `scenario_bank_test:180`). Unknown `Provenance.origin` ⇒ "cách của SAM", never "sách nói" (`teaching_provenance.dart:57-68`).
- Unknown *block role* (QUESTION/ACTIVITY…) does not exist in Dart at all — the role layer is offline (branch `ROLE-LAYER`), so the app cannot yet distinguish "readable" from "askable"; today it simply asks whatever the pack builder emitted as a question.

### (4) Can evidence be created wrongly from a UI interaction?
- "Con đọc xong rồi 📖" ⇒ **no event** (`reader_screen.dart:96-100`; TEST-PASSED `reader_screen_test:87`). "Con đọc nguồn xong 📜" ⇒ no event (`source_reader.dart:96-100`). Prediction submit ⇒ no event (`experiment_screen.dart:68-72`). Good.
- **But four taps do create `EvidenceKind.independentAttempt` with `correct: null` and no learner text check:** "Con đã trả lời xong 🗣" (`reader_screen.dart:104-109`), map "done" (`map_reader_screen.dart:41-55`), a stance button in Sử (`source_reader.dart:102-125`), and Compose draft submit (`compose_lite_screen.dart:109-114`, text required). The validator path adds one more: any non-empty observation text ⇒ `independentAttempt` **regardless of `support`** (`evidence_validator.dart:67-82`; C6 CONFIRMED).
- Consequence: `learningMapStateFor` treats that kind as 🔵 "Tự làm được" (`learning_map_state.dart:41-46`; C6b), and the parent line becomes "Con đã tự làm được Bài N" (`parent_session_summary.dart:70`). BKT is *not* fooled (`correct == null` ⇒ `noOp`, `evidence_weighting.dart:112-116`; TEST-PASSED `evidence_replay_test:89`), so `ConceptSummary` stays honest — but the Learning Map and the parent summary are a second, weaker truth. `learning_map_state.dart:26` documents the state as "bằng chứng TỰ LÀM", and `tutor_feedback.dart:83-85` reserves "tự làm được" for graded independent success. Doctrine (F1 "never claim beyond evidence") is honoured by one reader of the log and not by the other. **This is the emitting code for a competence claim from a self-report.**

### (5) Does device ≠ learner separation exist?
**Yes, structurally.** `LearnerProfile.learnerId` ≠ device (`learner_profile.dart:15`); every session/event carries `learnerId`; queries and export/delete filter by it (`learner_store.dart:152, 212-231`; C8 PASS; TEST-PASSED `learner_store_test:122`, `file_store_test:89`). Active learner persisted and restored (`main.dart:136-148`); switcher on Home; `confirmLearner` sheet **before assessment only** (`learner_confirm.dart:16`, `main.dart:341-350`). Parent area behind a PIN that is explicitly "rào chắn trẻ tò mò, không phải bảo mật" (`learner_store.dart:50-52`). Device-only records (PIN, active learner) are excluded from export/delete. Gap: no learner confirmation before Reader/Compose/Experiment evidence on a shared device (design choice per WAL-143, but the Learning Map badge now consumes that evidence).

### (6) Is replay / evidence history safe?
- **Deterministic and version-stamped:** `replayMastery` is pure (`evidence_replay_test:101` TEST-PASSED); `policyId` + `knowledgeVersion` baked at write (`replay_audit_test:42,80` TEST-PASSED); `support`/`act` absent on old data stay `null` (`learner_store_test:206,220`).
- **Append-only in memory, not on disk:** `JsonlLearnerStore` only appends lines, but `FileLearnerStore._flush` rewrites the whole file on every mutation (`file_store.dart:29-32`) — a crash mid-write risks the entire history, not the last line (the test `file_store_test:78` covers a torn last line only).
- **Identifiers:** `eventId` collides across re-open of the same exercise (C1 FAIL) and for surfaces (`'$activityId#$seq'`, experiment fixed `#0`); `appendSession` is not idempotent (C3 FAIL: evidenceCount doubles). `replay_audit_test:98` asserts uniqueness only for the core `attributeEvidence` helper.
- **Tamper:** no hash, signature or monotonic check; a hand-edited line is replayed silently (C9). `deleteLearner` is a real delete by design (`learner_store.dart:68-74`).
- **Re-open duplicates:** re-doing an exercise creates a new session with new (colliding-id) events — counted as new attempts, which is pedagogically right, but the ids cannot support future dedupe or audit.

### (7) Any path where a generic LLM bypasses the pedagogy runtime?
**No path exists today.** `pubspec.yaml` has no HTTP/LLM dependency; `grep` of `lib/` for LLM/HTTP/socket symbols finds comments only; `buildTutorPrompt`, `validateRealization`, `validateTutorOutput` have **0 callers in `lib/`**; `chat-generic` is `disable` and a test scans `lib/features` for a chat directory (TEST-PASSED). The only model call is the offline harness `tool/shadow/run_shadow.py` (`claude -p`), reported in `SAM-GENERATIVE-SHADOW-RESULTS.md` as KEEP SHADOW. On-device ML Kit OCR is gated by `ConfirmedProblem`.
**What is not true:** that the cage is *mandatory*. `RealizationRequest → validateRealization` is a well-tested seam (`realization_contract_test`, ACT_OVER_RUNG fails closed), but nothing at the type level forces model text through it before a `Text()` widget; `output_guard.dart:9-12` states it cannot catch verbal step descriptions. An agent wiring an LLM could route around the cage without any test going red.

---

## C.3 Five biggest architecture risks

| # | Risk | Evidence | Impact | Blast radius | Autonomous fix without Founder? |
|---|---|---|---|---|---|
| 1 | **Self-reports become competence claims** — ungraded taps mint `independentAttempt`; validator ignores `support`; Learning Map + parent summary read kind only | C6, C6b; `reader_screen.dart:104-109`, `map_reader_screen.dart:41-55`, `source_reader.dart:107`, `evidence_validator.dart:70`, `learning_map_state.dart:41-46`, `parent_session_summary.dart:70` | Parent told "Con đã tự làm được" from a button press; violates F1/F3 doctrine at the UI layer while BKT stays honest — two truths | All 5 Scale surfaces, Subject Home badge, Parent area | **No** — it needs the evidence contract for ungraded activities (docs: "needs evidence contract"); the fix changes what SAM may say to a parent |
| 2 | **Lineage gap: docs say wired, code is not** — only Experiment events carry `sourceDocumentId/lessonNo` | C7; grep of emitters; WAL-178/179/181/180 claims | Learning Map shows "Chưa học" for lessons done in Reader/Compose/Source/Tutor; parent summary omits them; "ONE EVIDENCE TRUTH" (`parent_session_summary.dart:4`) is false today | Learning Map, Parent view, any future Next-Action reading Scale evidence | **Yes, mechanically** (thread `LearningContext` into each emitter + a test per surface + Map reader context) — but it must land as a PR for Founder review because it changes stored evidence; the *Tutor* path needs a decision on which lesson to stamp when the problem came from camera |
| 3 | **Two paths, zero convergence code, unverifiable approval** — `SemanticBinding` absent, skillCase namespace split (2 registered vs 5+ free strings + `'unknown-case'`), `knowledgeModelVersion` constant stamped on non-Toán events, `CorpusExercise.skillCaseId` ignored | `data/03-two-paths-inventory.md` §C–D; Jira WAL-196 Ready/0 comments; CENSUS vs PROPOSAL contradiction | An agent extending either path deepens the fork; the census text would lead it to believe convergence is authorised | Every new lesson/subject/surface | **No** — architecture decision (WAL-196/WAL-200 Ready; F-a…F-d open); an agent may only file the contradiction as `TBD` |
| 4 | **Evidence store integrity** — colliding `eventId`s, non-idempotent `appendSession`, whole-file rewrite, no tamper detection | C1 FAIL, C3 FAIL, C9; `tutor_session.dart:88`, `learner_store.dart:138`, `file_store.dart:29-32` | Double-counted mastery on a retried `onFinished`; future dedupe would silently drop attempts; corrupted file loses all history; edited file changes a parent claim | Every learner's history; Parent claims; export/delete guarantees | **Partly yes:** unique ids (timestamp/session in id) and idempotent `appendSession(sessionId)` are mechanical with tests; append-on-disk and integrity hashing are a Founder policy (privacy/cost) — **No** for those |
| 5 | **Pedagogy runtime is a façade and the LLM cage is optional** — blueprints/patterns/`PlannedAct`/`validateRealization`/`lineageFor`/`evaluateSessions` have 0 runtime callers; `decide` runs with a hard-coded case on Home/Assessment; nothing forces model text through the guard | grep; `mission_data.dart:264`, `slice_flow.dart:375`; Q7 | Docs/Jira overstate "built and guarded"; an autonomous agent may wire realisation (or an LLM) around the guard with all tests green | Every future tutor act; Parent trust in "SGK dạy…" lines | **No** — wiring any model is the WAL-30 Founder gate; making the guard type-mandatory (a `RealizedText` type) is safe to propose but must not be bundled with wiring |

A sixth, outside the five: **legal** — verbatim SGK text is rendered to learners under a licence enum that says it must not be (`knowledge_content_provider.dart:16-18`); branch `J.1` only gates images. Founder/legal, not an agent.

---

## C.4 What an autonomous agent may safely touch (from this audit)

Mechanical, test-backed, no doctrine change: lineage threading (risk 2), id uniqueness + idempotent append (risk 4, part), routing or deleting the unrouted `QuizSelectScreen`, replacing the `knowledgeModelVersion` constant with a per-pack value, removing the `'unknown-case'` fallback in favour of refusing to grade. Everything else in C.3 needs a Founder decision first.
