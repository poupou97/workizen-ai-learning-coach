# 02 — Current Lesson Experience · AS-IS (from code, not from memory)

Every claim below is **OBSERVED-IN-CODE** or **MEASURED** unless labelled otherwise. Paths are
relative to the repo root (`/Users/alexnguyen/projects/workizen-ai-learning-coach`). Read on
2026-09-04 at `main` = `ad03a56` (worktree base `3f0c160`, WAL-206 merged).

## 1. The learner journey today

```
Home «Hôm nay» (mission_data.dart · main.dart)
  └─ 📚 Giá sách  BookShelfScreen (lib/features/subjects/book_shelf_screen.dart)
       └─ Book Home = SubjectHomeScreen filtered by book (lib/features/subjects/subject_home_screen.dart)
            └─ tap a lesson row → _openLesson()  (subject_home_screen.dart:426)
                 ├─ if every intent yields the same activity list → start directly (no sheet)  (:460-468)
                 └─ else INTENT sheet: SAM's reason first, then tiles  (:478-522)
                      🌱 Mai có tiết này (prepare) · 🔁 Cô dạy rồi (review) · ✏️ Con có bài tập (practice) · 📖 Xem trong sách (lookup)
                      └─ _startIntent() builds LearningContext{learner, grade, subject, book, lessonNo, intent}  (:668-680)
                           ├─ one activity → open its Surface directly  (:688-691)
                           └─ several → ACTIVITY sheet «Con muốn làm phần nào trước?»  (:692-735)
                                └─ Surface (Reader / ComposeLite / Experiment / SourceReader / Exercise)
                                     └─ events → recordSession() → LearnerStore (JSONL, append-only)
```

- **No PDF viewer exists in the app.** `pubspec.yaml` declares no PDF/webview/markdown dependency (MEASURED: `grep -i "pdf|webview|graphview|fl_chart|markdown" pubspec.yaml` → no hits). The bookshelf doc-comment states the intent: *"bấm vào sách KHÔNG mở PDF lật trang"* (`book_shelf_screen.dart:9-11`). So today's "Đọc" is `LearningIntent.lookup`, which reorders activities and drops exercises (`activitiesForIntent`, `subject_home_screen.dart:601-633`) — it does not show the book.
- **No LLM call is wired in `lib/`.** `grep -ril "anthropic|openai|gemini|dio|llm" lib/` → no client; `learning_context.dart:9-12` says the realization layer "chưa tồn tại trong repo này hôm nay". The tutor's LLM path is SHADOW behind the WAL-30 gate (`realization_contract.dart:5`).

## 2. Surfaces and their evidence rules

| Surface | File | Data it consumes | Evidence rule (fail-closed) | Tests |
|---|---|---|---|---|
| **ReaderScreen** (Đọc bài) | `lib/features/shell/reader_screen.dart` | `LearningActivity{passage, prompt, options, correctOption}` built from `TvReading` (`subject_home_screen.dart:818-845`) | READ gate (question locked until "Con đọc xong rồi"); "đọc xong" emits **no** event; open question → `independentAttempt correct=null`; options without key → `gradable=false` → `correct=null` (WAL-204); `lookup` intent → no events at all (`_emit`, :76-94) | `test/features/shell/reader_screen_test.dart` |
| **ComposeLiteScreen** (Luyện viết) | `lib/features/shell/compose_lite_screen.dart` | `TvWriting.prompt` + optional checklist | REVEAL gate (feedback only after a draft); no field can hold a model essay; never graded; draft = `independentAttempt`, revise-after-feedback = `guidedAttempt`, self-revise = `selfCorrection` | `compose_lite_screen_test.dart` |
| **ExperimentScreen** (Làm thí nghiệm) | `lib/features/science/experiment_screen.dart` | `KhoaExperiment{chuanBi, tienHanh[], duDoan?, quanSat?}` | PREDICT gate when the book prints «Dự đoán…»; verbatim book text under its own labels; observation → `CandidateEvidence` → `validateCandidateEvidence` (act `askExplanation`, `correct=null`) | `test/features/science/experiment_screen_test.dart` |
| **SourceReaderScreen** (Đọc tư liệu gốc) | `lib/features/history/source_reader.dart` | `SuSource{excerpt, attribution, samGloss?}` | Three typed claims (SourceClaim / SamInterpretation / StudentConclusion) with separate labels; read gate; conclusion `correct=null` | (widget tests under `test/features/`) |
| **MapReaderScreen** (Địa) | `lib/features/geography/map_reader_screen.dart` | `DiaMap{asset, caption, questions, pagePdf, bboxFrac, extractionVersion}` | Source image only (no AI illustration); questions verbatim; `correct=null`; no LearningContext parameter yet (constructor takes `map`, `onFinished`, `now` only) | — |
| **QuizSelectScreen** | `lib/features/shell/quiz_select_screen.dart` | `LearningActivity{options, correctOption}` | graded only when `gradable` | `quiz_select_screen_test.dart` |
| **Tutor / exercise flow** (Toán) | `lib/features/learning_session/slice_flow.dart`, `lib/core/tutor/` | `SliceCurriculum` (Deep path) | ±1 support ladder, REVEAL gate, `explainTeaching` provenance | many `test/core/*` |

Shared rule set: no %, no scores, no ability praise; provenance rendered only through
`sourceLineForChildOf(Provenance?)` (`lib/core/tutor/teaching_provenance.dart:57-69`), three
wordings: «Theo SGK …, trang N» (sourceStated) / «SAM làm theo ví dụ trong SGK …» (sourceDemonstrated)
/ «Đây là cách của SAM — con có thể kiểm lại» (anything else). An LLM may never emit a citation
(`CITATION_FABRICATION` guard, `docs/design/PEDAGOGICAL-PROVENANCE-UX.md`, WAL-114).

## 3. The two curriculum paths (unchanged since the architecture review)

| Path | Model | Reach today | Where |
|---|---|---|---|
| **Deep Intelligence** | `Concept` / `SkillCase` / `CurriculumEdge` / `TutorScope` / `LearningExperienceBlueprint` / `PlannedAct` | **1 lesson** registered: `'05-sgk-toan-5-tap-mot#6@20'` (`lib/core/knowledge/slice_curriculum.dart:114-118`) | `lib/core/curriculum/`, `lib/core/pedagogy/`, `lib/core/knowledge/` |
| **Scale / Learnable** | `LessonIndex` packs → `LessonActivity` (sealed: Exercise · Reading · Writing · Source · Experiment) → Surface → `CandidateEvidence` | 113 proven lessons (WAL-206 baseline; +3 exact-scope, +76 variant not shipped) | `lib/features/subjects/lesson_index.dart:281-308`, packs |

**Home reads only the Deep path (MEASURED defect).** `buildMissionFromStore` calls
`curriculaForLearner(profile)` and, when no `SliceCurriculum` exists for the grade, renders
«SAM chưa có nội dung lớp N — sắp có nhé» (`lib/features/mission/mission_data.dart:204-229`),
while `main.dart:190` separately computes `nextBookRecommendation()` from the packs. A grade-6
learner with 22 routed KHTN lessons therefore sees "no content" on the mission card (WAL-206 §5).

**Duplicate «Đọc bài» labels (MEASURED defect).** `_activityAction` returns the constant
`'📖 Đọc bài'` for every `ReadingActivity` (`subject_home_screen.dart:650-653`); a lesson with
several readings shows identical rows (WAL-206 §5 UX note). `_countLabel` (`:418-424`) is used
for the lesson row subtitle, not for the sheet rows.

## 4. What a lesson *is* today (data)

- **Identity:** `LessonKey{sourceDocumentId, number, pageStart}` — triple unique for 89% of
  7,626 records; `number` alone is display metadata (`slice_curriculum.dart:66-106`).
- **Structure:** `poc-out/graph/curriculum-structure.json` — 531 documents, `lessons[]{number,
  title, pageStart, unitKind}`; `structureStatus` PARTIAL for Khoa học 4/5 (MEASURED: Khoa học 5
  has 30 lessons, 8 missing `pageStart`).
- **Packs (`assets/pack/lesson-index-g{N}.json`, `lesson-index-v2`, gitignored, built by
  `tool/ui/build_lesson_index.py`)** — MEASURED counts on the main checkout:

| Grade | books | tvReadings | tvWritings | suSources | khoaExperiments | diaMaps | toanExercises | sourceAssets |
|---|---|---|---|---|---|---|---|---|
| 1 / 2 / 3 | 7 / 8 / 14 | 0 | 0 | 0 | 0 | 0 | 0 | 3 |
| 4 | 14 | 32 | 0 | 2 | 11 | 0 | 6 lessons | 3 |
| 5 | 15 | 81 | 57 | 2 | 5 | 1 | 4 lessons | 3 |
| 6 / 7 / 8 / 9 | 13 / 13 / 14 / 16 | 32 / 18 / 22 / 87 | 0 / 0 / 0 / 1 | 0 | 4 / 2 / 8 / 15 | 0 | 0 | 3 |
| 10 / 11 / 12 | 41 / 42 / 41 | 0 | 0 | 0 | 5 / 0 / 0 | 0 | 0 | 3 |

  (`sourceAssets` = the same 3 human-curated crops in every pack: a map, an experiment figure, a
  fraction figure; `assets/pack/*.png` sizes 0.5–4.0 MB each.)

- **Retrieval pack:** `assets/pack/sam-units.db` (1.9 MB) — table `unit(id, book, grade, vol,
  lesson, role, page, text)` + FTS5; **no Dart consumer** (`KnowledgeContentProvider` has zero
  implementations — `lib/core/knowledge/knowledge_content_provider.dart`, review doc §7).
- **Layout blocks (WAL-206):** `poc-out/layout/<book>/pNNN.json` → `{pagePdf, book,
  layout{regions, trusted, tableLike, confidence, marginalCuts, overlapShare}, blocks[]{id, order,
  regionPath, role, text, bbox, lines, ocrConf, trusted}}`; roles are exactly heading · body ·
  question · caption · sidebar · footnote · pageNumber (`tool/corpus/layout_extract.py:231-244`).
  Only 6 books have layout output today (Khoa học 4–5, KHTN 6–9).
- **Corpus:** 531 docs, 62,729 OCR pages (scanned, no text layer), 3,679 canonical SGK lessons
  (known to undercount KHTN 7/8), 27 activity patterns; 40 lessons CONVERGENCE_READY (1.09%).

## 5. The concept board's lesson, checked against the corpus (MEASURED)

`concept/concept-ai-first/learning-view.png` shows "Khoa học 5 · Bài 2 · Dinh dưỡng và sức khỏe"
under "Chủ đề 1. Con người và sức khỏe". In `curriculum-structure.json`:

- `05-sgk-khoa-hoc-5` Bài 2 = **"Ô nhiễm, xói mòn đất và bảo vệ"**, `pageStart: null` (Chủ đề 1 is
  *Chất*; "Con người và sức khoẻ" is Bài 22–27). No lesson titled "Dinh dưỡng và sức khỏe" exists in
  any of the 531 documents.
- The nutrient-group content matches **Khoa học 4 Bài 23 "Vai trò của chất dinh dưỡng" (p.84)** and
  Bài 24 "Chế độ ăn uống cân bằng" (p.88).
- For Khoa học 4 PDF pages 84–93 (WAL-206 output): `layout.trusted` is `false` on 8/10 pages
  (only p090 is trusted 12/12 blocks); `units-layout/04-sgk-khoa-hoc-4.json` contains **0 units
  for lesson 23**; OCR headings read "SỨC KHOE", "VAI TRÔ", "CUỌC SON". In the g4 pack this lesson
  has no activity of any kind (it is one of the "Browsable but not Learnable" 3,566).

So the board's Mode 1/2/3 frames depict a lesson that today has **no trusted structured content
and no activity** — which is the honest baseline any Learning View design must start from.

## 6. Existing pieces the concept can reuse (inventory)

| Piece | Status | Path |
|---|---|---|
| Learning context canonical (learner·grade·subject·book·lesson·intent) | BUILT | `lib/core/context/learning_context.dart` |
| Intent proposal with visible reason, fail-closed `null` | BUILT | `lib/core/intent/learning_intent.dart` |
| Next Best Action (signals→resolve, `rest` first-class) | BUILT, thresholds un-tuned | `lib/core/agenda/learning_agenda.dart` |
| Evidence validator (one gate; TRACE on `lookup`) | BUILT, not universal (Tutor/Quiz mint directly) | `lib/core/student/evidence_validator.dart` |
| Pedagogy model: `TeachingAct`(15), `AssistanceRung`, `PlannedAct` | BUILT | `lib/core/pedagogy/pedagogy_model.dart` |
| LLM realization contract (engine decides; guard) | BUILT, LLM shadow | `lib/core/pedagogy/realization_contract.dart` |
| Blueprint (sequence, cap, evidence required, learnerFirst) | BUILT, 8 instances | `lib/core/pedagogy/learning_blueprint.dart` |
| Provenance (5 origins; `citableAsTextbookFact`, `citableAsDependency`) | BUILT | `lib/core/knowledge/provenance.dart` |
| Source asset with crop provenance | BUILT (3 assets) | `lesson_index.dart:179-219`, `lib/core/assets/learning_asset.dart` |
| Mascot 13 state chips, design tokens, 4 age bands | BUILT | `docs/design/MASCOT-STATE-SYSTEM.md`, `DESIGN-SYSTEM-DIRECTION.md`, `AGE-ADAPTIVE-UX.md` |
| Representation explanation (WAL-185: SAM says why a representation fits) | SHIPPED per research doc; no `representation` identifier found in `lib/` by grep — verify by ticket before citing further | `docs/research/SAM-LEARNING-VISUALIZER-RESEARCH.md` |

## 7. AS-IS gaps that the Learning Views concept would touch

1. No lesson-level document: content lives in five per-type lists (`tvReadings`…), not "the lesson".
2. No block roles for image/table/formula/activity; 6/531 books have layout output at all.
3. Home mission card ignores the Scale path; the lesson sheet does not name readings distinctly.
4. `MapReaderScreen` does not take a `LearningContext` (the only Surface without the WAL-189 gate).
5. `shortText` → `SurfaceKind.unsupported` (`lib/core/tutor/learning_activity.dart:90-97`): the
   EXPLAIN_SHORT family (874 lessons, largest pattern) has no Surface — WAL-206 §6.
6. `assets/pack/` is declared as an asset directory (`pubspec.yaml`) and currently contains
   `sam-synthetic-100mb.db` (105 MB, gitignored) — on a dev machine this file is bundled into
   local builds. Not a product bug; relevant to Q17–18 measurements (see `18`).
