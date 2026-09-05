# 03 — Layer B: Learning Architecture audit («Học cùng SAM», Founder pre-autonomy checkpoint 2026-09-05)

**Scope.** Read-only audit of `main` @ e5155f4 (worktree), plus the TC-v2 Architecture Review on `origin/research/tc-v2-science-slice` (read via `git show`, not merged). No fixes, no Jira edits, no device. Labels: OBSERVED-IN-CODE · TEST-PASSED · TEST-FAILED · DOC-CLAIM · RESEARCH-ONLY. Long tables: `data/03-concept-status-table.md`, `data/03-two-paths-inventory.md`; traceability rows: `data/concept-to-code-rows.md`; scripts and logs: `scripts/`.

**Test evidence used throughout.** `flutter analyze`: no issues. `flutter test` (worktree, packs absent): **633 passed · 14 skipped · 0 failed**. Same suite with the gitignored packs copied in: **647 passed · 0 skipped · 0 failed** (`scripts/flutter-test-B-C*.log`). Runtime checks `scripts/runtime_checks.dart` (10 checks against production classes) and `scripts/pack_counts_test.dart` (counts through the production `LessonIndex` parser) — results in `data/04-runtime-checks.md`.

---

## B.1 Verdict up front

**Is the current architecture coherent enough for an autonomous agent to keep building? — NO, not yet.** The *kernel* is coherent and genuinely proven (fail-closed method gating, raw-event evidence, replayable mastery, three-axis claims — all with real data flowing on one lesson). But the codebase carries **two evidence disciplines, two learner-state functions, two activity types, a dead "single" surface resolver, an unregistered skill-case namespace, and four named Founder concepts with no code** (LearningView, TrustedLearningSource, SemanticBinding, PedagogyRuntime-as-runtime). None of these is dangerous by itself; together they mean an autonomous agent cannot know which side of each fork to extend, and the docs that would tell it disagree with each other and with Jira (§B.5). Six conflicts must be locked first (§B.6).

---

## B.2 Concept-by-concept status (summary; evidence in `data/03-concept-status-table.md`)

| Founder concept | Status | One-line evidence |
|---|---|---|
| Concept | IMPLEMENTED type · data = 1 id | `Concept` class never constructed in `lib/` (grep); runtime concept is the string `'quy-dong'` (`slice_curriculum.dart:150`); surfaces mint 5 free-string concept ids |
| SkillCase / MethodCase | SkillCase IMPLEMENTED (2 instances) · **MethodCase NOT IMPLEMENTED** (0 hits in lib/test/docs) | `slice_curriculum.dart:229-240`; surfaces mint unregistered case ids incl. `'unknown-case'` (`assessment_screen.dart:86`) |
| Method | IMPLEMENTED (2 instances + hints + provenance) | `TeachingMethod` `pedagogical_boundary.dart:80`; TEST-PASSED `pedagogical_boundary_golden_test` (BCNN blocked at grade 5) |
| CurriculumEdge / prerequisite | IMPLEMENTED type · 1 edge · **0 runtime consumers** | `prerequisite_edges.dart:20-38`; `grep` in `lib/features` → none |
| LearningActivity | IMPLEMENTED · two shapes | built at 2 sites (`subject_home_screen.dart:791,824`); `resolveSurface` **0 callers**; parallel sealed `LessonActivity` (`lesson_index.dart:281`) is the live one |
| SemanticBinding | **NOT IMPLEMENTED** | 0 hits; DOC-CLAIM "proposed, not implemented" (`K12-CONVERGENCE-CENSUS.md:75`); WAL-200 Ready |
| TutorScope.allowedMethods | IMPLEMENTED + ENFORCED (Deep path only) | `pedagogical_boundary.dart:192-277`; consumers `tutor_session.dart:150`, `teaching_provenance.dart:81`, `tutor_prompt.dart:39`, `lineage.dart:161`; runtime checks C5a–d PASS |
| Pedagogy Runtime | **POC ONLY** | 8 blueprints, patterns, `validateRealization`, `PlannedAct` exist; **0 callers in `lib/features`/`main.dart`** (grep); only `decide()` + the TutorSession ladder run |
| PlannedAct / TeachingAct | PlannedAct **dead type** (0 constructions anywhere) · TeachingAct narrow (1 runtime writer: `experiment_screen.dart:87`) | `pedagogy_model.dart:125,54` |
| LearningEvidence | IMPLEMENTED · PROVEN · gate not universal | 10 minting sites; validator used by 1 (`experiment_screen.dart:92`); single writer `recordSession` (7 callers); TEST-PASSED replay/lineage suites; script C1/C3 **FAIL** (ids/idempotency) |
| Student Knowledge State | IMPLEMENTED · PARTIAL reach · **two disjoint functions** | BKT/`ConceptSummary` over 2 registered cases (`slice_flow.dart:38`) vs `LearningMapState` by lineage (`learning_map_state.dart:33`) fed by experiment events only (C7) |
| Next Action | IMPLEMENTED (3 mechanisms) · PARTIAL | agenda over exactly 1 concept (`mission_data.dart:249`); `decide` hard-codes the case (`:264`); book recommendation timetable-only (`next_lesson.dart:52`); REST first-class |
| LearningContext | IMPLEMENTED · not threaded to Map/Tutor/Assessment | `learning_context.dart:17`; built `subject_home_screen.dart:307,674`; `lookup` gate at 4 of 5 lesson surfaces (Map reader lacks it) |
| LearningView | **NOT IMPLEMENTED** | 0 hits; RESEARCH-ONLY (WAL-207); Founder kept OPEN (branch doc F) |
| TrustedLearningSource | **NOT IMPLEMENTED in Dart** · RESEARCH-ONLY offline | nearest: `Provenance`, `SourceAsset`, `KnowledgeContentProvider` (0 implementations); TSL exists only on the research branch |

**PROVEN architecture (code + tests + real data):** Method gating (`TutorScope`), `TutorSession` ladder with REVEAL gate, `LearningEvent`/`EvidenceLog` + JSONL persistence, `replayMastery` + `ConceptSummary` + `ParentExplanation`, `Provenance` → `sourceLineForChildOf`, `LessonIndex` fail-closed parse, `LearningContext` + `LearningIntent` (`proposeIntent` returns `null` without a signal), `recordSession` single writer, perception boundary (`ConfirmedProblem`). All TEST-PASSED and all exercised by real data at runtime.

**RESEARCH PROPOSAL (no runtime code):** LearningView, TrustedLearningSource/TSL, SemanticBinding, Pedagogy Runtime as a runtime (blueprints/realization), PlannedAct, KST/prerequisite reasoning, LLM realisation (shadow only, no client in the app).

---

## B.3 The two parallel paths (detail in `data/03-two-paths-inventory.md`)

**A — Deep / Concept-SkillCase path.** Spine `SliceCurriculum` with **one** registration (`slice_curriculum.dart:114-118`). Entered by camera/OCR (`slice_flow.dart:84-108`), by tapping a pack exercise (`subject_home_screen.dart:248-265`), by the Home review chip and the assessment (`main.dart:243-380`, both hard-code lesson 6 / case `denominator-non-divisible`). Serves grade-5 learners on `a/b ± c/d` problems; grade ≠ 5 ⇒ honest out-of-scope screen. State = BKT over 2 SkillCases → `ConceptSummary` → parent explanation. Tests: `thin_slice_test`, `slice_flow_test`, `falsification_test`, `lineage_test` — TEST-PASSED.

**B — Scale / Learnable path.** Spine `LessonIndex` packs (`tool/ui/build_lesson_index.py` → `assets/pack/lesson-index-g{N}.json`, gitignored). Measured through the production parser on the packs built 2026-09-04 on this machine: **3,650 TOC lessons, 187 openable** (activities ≠ ∅), **1** with a Deep curriculum. Surfaces: Reader, Compose, Experiment, SourceReader, MapReader, SourceGallery. Docs quote 113 (SCALE) / 111 (CENSUS) — stale vs the packs now on disk; both denominators reported, not merged. State = `LearningMapState` (3 values) keyed by `(sourceDocumentId, lessonNo)`.

**Where they touch.** Same `LearnerStore`/`LearningSession` schema (shared, good). Everything else is duplicated or mis-shared: two minting disciplines (validator vs direct), two state functions that never read each other's events, two activity types, and the constant `knowledgeModelVersion = 'slice-toan5-b6-v1+qmap-v1'` stamped on Reader/Source/Map/Assessment events (8 feature files) — a Toán-5 version tag on Tiếng Việt evidence. The pack's `CorpusExercise.skillCaseId` (the one existing join key) is ignored; the case is re-derived from the expression (`slice_flow.dart:138`).

**Convergence in code: zero.** `SemanticBinding` absent; Deep registrations still 1. The "Founder-approved convergence direction" is asserted only in `K12-CONVERGENCE-CENSUS.md:3-6`, citing a Desktop zip that is not on the Desktop today; the phrase "APPROVE ARCHITECTURE CONVERGENCE" appears in **no** doc and in **no** WAL Jira comment/description (JQL, read-only); WAL-196 is **Ready** with 0 comments, WAL-200 **Ready**, WAL-195 **Ideas**. The proposal it would converge says of itself "NOT AN ARCHITECTURE DECISION… Nothing authorizes implementation" (`PROPOSAL.md:3-4,136-139`). Per `CLAUDE.md` rule 5 this is a doc-vs-doc contradiction to **report, not resolve**: the census's approval claim is currently unverifiable.

---

## B.4 What the architecture actually enforces today (for the Founder's confidence)

- **Retrieved ≠ permitted for methods** — type-enforced: `allowedMethods` required, `forProblem(null case) ⇒ []`, F2 wildcard closed (`caseNotDeclared`), `explainTeaching`/`buildTutorPrompt`/`lineageFor` all return `null` outside the set. TEST-PASSED in 8 files; runtime checks C5a–d.
- **Raw events, derived mastery** — `LearningEvent` immutable, `correct` nullable, `replayMastery` deterministic; policy change = replay, no migration (`evidence_replay_test:101,116` TEST-PASSED).
- **Claims never exceed evidence** — `ConceptSummary` three axes, `strongOnObserved ≠ mastered` (`falsification_test` F1, `scenario_bank_test` S7 TEST-PASSED).
- **Provenance rendering** — `sourceDemonstrated` never renders as "sách nói" (`teaching_provenance.dart:57-68`; `scenario_bank_test` S3).
- **Perception ≠ evidence** — only `ConfirmedProblem` can become a `CanonicalProblem` (`canonical_problem.dart:59`); OCR adapter returns `null` on 0 or ≥2 expressions.
- **Safety boundary in code** — unknown capability ⇒ `disable`; pubspec scanned for ad/analytics SDKs; no `chat` feature dir (`education_safety_policy_test` TEST-PASSED).

---

## B.5 Where the documents disagree with the code (an autonomous agent would inherit these)

| Topic | Doc says | Code says |
|---|---|---|
| Evidence gate | WAL-178 / `evidence_validator.dart:1-9`: validator is "the ONLY door" | 9 of 10 emitters bypass it (`data/03-concept-status-table.md` row 10); `REVIEW.md:164-178` admits "not universal" |
| Lineage on events | WAL-178/179/181/180: context "flows through" to Learning Map and parent view | only the validator and the Map reader set `sourceDocumentId`; Reader/Compose/Source/Tutor/Assessment events have none (grep; check C7) ⇒ Learning Map badge and parent line are blind to them |
| Surface resolver | ADR-009: `resolveSurface` "the ONLY mapping" | 0 callers; `_activityAction` decides screens (`subject_home_screen.dart:643`) |
| Pedagogy runtime reach | `learning-views/18:46` "Already built and guarded"; `REVIEW.md:254` "wired (Experiment only)" | blueprints/realization/PlannedAct have 0 runtime callers; Experiment writes one `TeachingAct` value into an event — that is not a runtime |
| TeachingAct count | `SAM-LEARNING-CURRENT-TRUTH.md:17` "17, chưa thành code" | enum of 15 in code |
| Prerequisite edges | `CURRENT-TRUTH.md:23` "còn llmInferred" | 1 `sourceStated` edge, no llmInferred (OIC) |
| Next action | `ADAPTIVE-LEARNING-ENGINE-HYPOTHESIS.md:3` "not implemented" | `NextBestLearningAction` live on Home |
| Convergence | CENSUS: "Founder-approved" | PROPOSAL/REVIEW: not authorised; Jira: Ready, no approval comment |
| Learnable count | 113 / 111 | 187 openable in packs on disk |

---

## B.6 Conflicts to lock before autonomous building (exact, in priority order)

1. **One evidence contract, one gate.** Decide whether `validateCandidateEvidence` is mandatory for every emitter (then `TutorSession`, Reader, Compose, Source, Map, Assessment must route through it) or whether direct minting is sanctioned (then delete the "only door" claim). Also decide the contract for **ungraded self-reports**: today `independentAttempt` with `correct: null` is minted by Reader open-answer (`reader_screen.dart:104-109`), Map reader (`map_reader_screen.dart:41-55`), Source stance (`source_reader.dart:107-118`), Compose draft (`compose_lite_screen.dart:112`) and the validator (`evidence_validator.dart:70`, regardless of `support`, check C6) — and `LearningMapState` reads that kind as "🔵 Tự làm được" (check C6b) while BKT ignores it. That is a doctrine question (F1/F3), not a bug fix.
2. **Lineage is mandatory or it is not.** Either every emitter carries `sourceDocumentId/lessonNo` from `LearningContext` (then thread the context into Map/Tutor/Assessment and stamp it), or the Learning Map/parent summary are declared Deep+Experiment-only. Today the UI silently shows "Chưa học" for lessons the child did (check C7).
3. **One state function per question.** `masteryFromStore` (registered cases) vs `learningMapStateFor` (lineage) vs `LearningMapScreen` (curricula) — decide which screen may say what, and register or reject the free-string `skillCaseId`s (`'unknown-case'` must go).
4. **One activity model.** Keep `LessonActivity` (live) and retire `LearningActivity`/`resolveSurface` to the Deep path only, or make the resolver real. Same for `knowledgeModelVersion`: a per-pack/per-book version, not one constant.
5. **Runtime containment for Views/Source/Pedagogy** — choose F-a…F-d from the branch doc (or record F-d "keep today's shape" explicitly). Until chosen, an agent adding a "View" has no home to put it in.
6. **Record the truth about WAL-196.** Either the Founder approval exists (attach it to WAL-196 and `05_DECISIONS.md`) or the census sentence is marked `TBD`. An agent reading CENSUS today would believe convergence is authorised.

Locking 1–3 is a Founder decision (they change what SAM may claim to a parent). 4 and the version constant are mechanical once 1–3 are decided. 5–6 are governance.

---

## B.7 Method note

Counts come from `grep` over `lib/`+`test/` (`scripts/concept_scan.py`, output in `scripts/concept_scan.out`), the production parser run on the real packs (`scripts/pack_counts_test.dart`), and `dart run scripts/runtime_checks.dart` against real classes. Doc claims were read from `docs/architecture/`, `docs/design/07`, `docs/design/SAM-CONCEPT-DATA-CAPABILITY-MATRIX.md`, `docs/research/SAM-EDUCATION-DATA-ARCHITECTURE-REVIEW.md`, `BREADTH-DEPTH-UX-MATRIX.md`, `learning-views/12,13,14,15,18`, ADR-001…010, `K12-CONVERGENCE-CENSUS.md`, `LEARNABLE-COVERAGE-SCALE-STRATEGY.md`, and the branch's `E/F/G/H/DECISIONS-REQUESTED/ROLE-LAYER/RISKS/01` — cited by path:line where used. Jira was read, not edited.
