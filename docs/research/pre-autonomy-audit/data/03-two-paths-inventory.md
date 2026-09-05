# Data 03 — The two parallel paths: where each lives, how much each serves, where they touch

## A. Deep path (Concept → SkillCase → Method → TutorScope → TutorSession → BKT/ConceptSummary)

| Item | Evidence |
|---|---|
| Spine | `SliceCurriculum` `lib/core/knowledge/slice_curriculum.dart:35`; registry `_curriculumByLesson` `:114-118` — **1 row**: `'05-sgk-toan-5-tap-mot#6@20'` (Toán 5 · Bài 6) |
| Entry points | (1) camera/OCR → `ConfirmProblemScreen` → `openCanonicalProblem` → `curriculumForProblem` (`slice_flow.dart:84-108`, `slice_curriculum.dart:140-146`); (2) Subject Home exercise tap `_openExercise` (`subject_home_screen.dart:248-265`); (3) Home "Ôn luyện" chip (`main.dart:243-280`, hard-codes lesson 6 + case `denominator-non-divisible`); (4) "Kiểm tra hiểu bài" (`main.dart:318-380`, same hard-coded case) |
| Reach (OIC) | `curriculaForLearner(grade 5)` = 1, grade 6 = 0 (script INFO). Any `a/b ± c/d` expression recognised by `fractionSumCase` for a grade-5 learner enters this path; grade ≠ 5 ⇒ `_outOfScope` (`slice_flow.dart:126-133,311`). Pack exercises with `ExerciseActivity`: grade 4 = 6, grade 5 = 4 lessons (pack_counts) — but only a grade-5 learner can open them into the tutor |
| State | `masteryFromStore` replays 2 SkillCases (`slice_flow.dart:38-48`); `ConceptSummary.of` (`concept_summary.dart:250`); `ParentExplanation` (`parent_explanation.dart:52`) |
| Tests | `thin_slice_test` (17-step chain), `slice_flow_test` (closed loop store → mission), `falsification_test` F1–F4, `tutor_session_test`, `lineage_test` — all TEST-PASSED |

## B. Scale path (Corpus → LessonIndex pack → LessonActivity → Surface → LearningEvent)

| Item | Evidence |
|---|---|
| Spine | `LessonIndex` `lib/features/subjects/lesson_index.dart:310`; built offline by `tool/ui/build_lesson_index.py` from `poc-out/graph/curriculum-structure.json` + `poc-out/units*/` (gitignored); loaded `LessonIndex.loadForGrade` `:627` (null when asset missing) |
| Entry points | Home → `BookShelfScreen`/`SubjectsScreen` → `SubjectHomeScreen._openLesson` `:426` → `proposeIntent` → `_startIntent` `:668` → `_activityAction` `:643` → Reader / Compose / Experiment / SourceReader / MapReader / SourceGallery; timetable recommendation `main.dart:187-225` |
| Reach (MEASURED through the production parser, `scripts/pack_counts_test.dart`, packs built 2026-09-04 23:23 on this machine) | see table below: **3,650** TOC lessons in packs, **187** openable (`activitiesFor ≠ ∅`), **1** with a Deep-path curriculum |
| State | none per SkillCase (ids unregistered); `LearningMapState` by lineage only (`learning_map_state.dart:33`) — fed by experiment events only (data/04 C7) |
| Tests | `architecture_gate_test` (pack-gated: second subject + second grade open with no lesson-specific code — TEST-PASSED with packs), `data_driven_lesson_test`, `lesson_index_test`, per-surface widget tests — TEST-PASSED |

### Pack counts per grade (production parser `LessonIndex.fromJsonString`)

| grade | books (shelf) | subjects | lessons (TOC) | openable lessons | Deep-path lessons | activities by kind |
|---|---|---|---|---|---|---|
| 1 | 7 | 6 | 179 | 0 | 0 |  |
| 2 | 8 | 6 | 203 | 0 | 0 |  |
| 3 | 14 | 11 | 296 | 0 | 0 |  |
| 4 | 14 | 11 | 300 | 23 | 0 | Reading 32, Experiment 11, Source 2, Exercise 6 |
| 5 | 15 | 12 | 312 | 76 | 1 | Reading 79, Experiment 5, Source 2, Writing 54, Exercise 4 |
| 6 | 13 | 10 | 195 | 24 | 0 | Reading 32, Experiment 4 |
| 7 | 13 | 11 | 171 | 10 | 0 | Reading 18, Experiment 1 |
| 8 | 14 | 12 | 200 | 14 | 0 | Reading 22, Experiment 8 |
| 9 | 16 | 12 | 204 | 35 | 0 | Reading 87, Experiment 15, Writing 1 |
| 10 | 41 | 16 | 526 | 5 | 0 | Experiment 5 |
| 11 | 42 | 17 | 551 | 0 | 0 |  |
| 12 | 41 | 17 | 513 | 0 | 0 |  |
| **total** | 238 | | **3,650** | **187** | **1** | |

Denominators (per memory rule, never merged): canonical 3,679 (docs), pack-TOC 3,650 (this machine), ranged 3,381 (pipeline). Docs say 113 EVIDENCE_CAPABLE (`LEARNABLE-COVERAGE-SCALE-STRATEGY.md`) / 111 uxConnected (`K12-CONVERGENCE-CENSUS.md`); the packs on this machine give **187** openable — the packs are newer than the docs (Ngữ văn readings in g6–g9 present). DOC-CLAIM numbers are stale relative to built data; report both.

## C. Where the paths touch (OBSERVED-IN-CODE)

| Touchpoint | Code | Shared or duplicated? |
|---|---|---|
| Exercise tap → Deep | `subject_home_screen.dart:248-265` builds `CanonicalProblem.fromCurriculum` from a pack `CorpusExercise` and calls `openCanonicalProblem` | Bridge. Note `CorpusExercise.skillCaseId` (from qmap) is **ignored**; the case is re-derived from the expression (`slice_flow.dart:138`) |
| `curriculumForLesson(LessonKey)` | `subject_home_screen.dart:432-436, 94-98` | Bridge for "Nguồn bài học" sheet + `hasSource`; returns non-null for 1 lesson |
| Evidence store | both paths write `LearningSession` via `recordSession` into the same `LearnerStore` | **Shared** (one store, one schema) |
| Evidence gate | Deep: `TutorSession._emit` direct; Scale: 1 surface via validator, 4 direct | **Duplicated** — two minting disciplines (`REVIEW.md:164-178` admits it) |
| Learner state | Deep: BKT/ConceptSummary over registered cases; Scale: `LearningMapState` by lineage | **Duplicated, disjoint** — neither reads the other's events meaningfully |
| Knowledge version | `knowledgeModelVersion = 'slice-toan5-b6-v1+qmap-v1'` (`slice_curriculum.dart:31`) stamped on Reader/Source/Map/Assessment/Experiment events (grep: 8 feature files) | **Mis-shared** — Scale events carry the Toán-5-B6 version tag |
| Activity type | `LearningActivity` (core/tutor) vs `LessonActivity` (features/subjects) | **Duplicated** shapes; `resolveSurface` dead, `_activityAction` live |
| Next action | `resolveAgenda` (Deep, 1 concept) + `nextBookRecommendation` (Scale, timetable only) merged in `mission_center_screen.dart:228-248` (evidence-urgent agenda wins) | Composed at UI, not in a resolver |

## D. Convergence (WAL-196 / "APPROVE ARCHITECTURE CONVERGENCE") — how far in code

| Claim | Evidence | Label |
|---|---|---|
| "Founder-approved architecture convergence direction (2026-09-04)" | `docs/research/K12-CONVERGENCE-CENSUS.md:3-6`; cites a Desktop-only zip `HOC-CUNG-SAM-K12-CONVERGENCE-REVIEW-LATEST.zip` — `ls ~/Desktop` on 2026-09-05: **not present** | DOC-CLAIM, unverifiable |
| Founder text "APPROVE ARCHITECTURE CONVERGENCE" | grep `docs/` (case-insensitive) → 0; Jira JQL `comment ~ "APPROVE ARCHITECTURE CONVERGENCE"` in WAL → 0 issues; WAL-196 status **Ready**, 0 comments (read 2026-09-05); WAL-200 (Thin Convergence Bridge) **Ready**; WAL-195 **Ideas** | NOT FOUND |
| Proposal authorisation | `SAM-EDUCATION-DATA-ARCHITECTURE-PROPOSAL.md:3-4,136-139` and `REVIEW.md:3-5`: "NOT AN ARCHITECTURE DECISION … Nothing … authorizes implementation" | DOC-CLAIM (contradicts CENSUS) |
| Convergence code | `SemanticBinding` 0 hits; join of `CorpusExercise.skillCaseId` → `SkillCase` registry not performed (`slice_flow.dart:138` re-classifies); Deep registrations still 1 | OBSERVED-IN-CODE: **0 convergence code** |
| Convergence readiness | CENSUS funnel: 40/3,679 CONVERGENCE_READY, `deepIntelligenceReady` = 1 | DOC-CLAIM consistent with code (1) |
