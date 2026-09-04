# 06 — Mode 3 · SAM Tutor / Học với SAM — Research

**Founder principle (§5):** not "Chat" — chat is one interaction mechanism. SAM actively organises
a learning session; Student Action → Evidence → Pedagogy Runtime → Student State → Next Teaching
Action. **The LLM does not decide pedagogy**; the Pedagogy Runtime decides what SAM may teach/ask
and which evidence is valid; the LLM realises the permitted action.

## 1. Finding: Mode 3 already exists as a runtime — under other names (OBSERVED-IN-CODE)

| Founder's phrase | SAM code today | Path |
|---|---|---|
| "Pedagogy Runtime determines what SAM may teach/ask" | `TutorScope = APPLICABLE ∩ PEDAGOGICALLY_ALLOWED`; `decide()` → `LearningAction`; `PlannedAct{act: TeachingAct(15), methodId?}` | `lib/core/curriculum/pedagogical_boundary.dart`, `lib/core/pedagogy/pedagogy_model.dart:125-129` |
| "which method is allowed" | `LearningExperienceBlueprint{sequence, assistanceCap, evidenceRequired, learnerFirst, misconceptionIds}` + `blueprintViolations()` | `lib/core/pedagogy/learning_blueprint.dart` |
| "LLM realises the permitted action" | `RealizationRequest{act, rung, scope, methodId, facts}` → `buildTutorPrompt` → model (SHADOW, WAL-30) → `validateRealization` → `fallbackRealization` (deterministic) | `lib/core/pedagogy/realization_contract.dart:1-10, 58-102` |
| "which evidence is valid" | `validateCandidateEvidence` (lookup ⇒ null; empty ⇒ null; `correct: null`) | `lib/core/student/evidence_validator.dart` |
| "Student Knowledge State" | BKT per `SkillCase` → `ConceptSummary` 3-axis (mastery ≠ coverage ≠ confidence) | `lib/core/student/mastery.dart`, `concept_summary.dart` |
| "Next Teaching Action" | `LearningAgenda` signals→resolve (`rest` first-class); `ReviewUrgency`, `ChallengeSignal`, `resolveReviewCandidates` | `lib/core/agenda/learning_agenda.dart`, `lib/core/adaptive/` |
| "misconception" | `grep misconception lib/` = 0 in the 2026-09-02 audit (`SAM-LEARNING-CURRENT-TRUTH.md`); a seed file `lib/core/pedagogy/source_misconception.dart` exists and blueprints carry `misconceptionIds` — **model MISSING, hook present** | — |
| "explain / ask / hint / scaffold / demonstrate / diagnose / practice / review / check" | `TeachingAct`: explainConcept · diagnosticProbe · smallHint/strategicHint · workedExample/demonstrateStep · askExplanation · askVerification · reflect · stepBack · revealStep/revealAnswer · pumpRecall · observeWait · contrastCases | `pedagogy_model.dart:54-70` |

So "SAM Tutor" is a **product name for the Deep path reaching a lesson**, plus the Surfaces the
runtime needs. What is *not* there: (a) reach — 1 lesson registered (`slice_curriculum.dart:114-118`);
(b) a Surface for short free-text answers (`shortText → unsupported`, `learning_activity.dart:96`)
which WAL-206 §6 measured as the next bottleneck (166/185 recovered Science lessons carry only
EXPLAIN/OBSERVE questions); (c) a misconception model; (d) any wired LLM (shadow).

## 2. Chat vs Tutor (Q2) — answer with evidence

**SAM Tutor.** Three independent reasons:

1. **Doctrine already decided it.** Convergence §5 removed the floating SAM/chat button ("it
   advertises 'chat with AI' as the main activity — wrong positioning; SAM lives in the flow"), and
   §23 item 8 forbids "a general-purpose chatbot instead of the learning flow". A "Chat" Mode 3
   would contradict a converged Founder decision.
2. **The runtime is act-driven, not turn-driven.** `RealizationPolicy` makes reveal/demonstrate
   deterministic and only pump/probe/hint/askExplanation generative-guarded — a chat UI would
   invite the model to take turns the runtime never planned. The LLM is a *renderer* of a
   `PlannedAct`, exactly the Founder's "LLM realises the permitted teaching action".
3. **Prior art converges.** AutoTutor's dialogue is *expectation & misconception-tailored*: the
   tutor holds expectations and anticipated misconceptions, matches student turns semantically, and
   moves pump → hint → prompt → assertion (FROM-REFERENCE — Graesser et al., "Conversations with
   AutoTutor Help Students Learn", IJAIED 2016; FLAIRS 2005 "AutoTutor's coverage of expectations").
   That is a *state machine with a language surface*, not a chat. Cognitive Tutors (FROM-REFERENCE —
   Anderson, Corbett, Koedinger & Pelletier 1995, JLS 4(2)) found the best interaction style was
   "immediate feedback, consisting of short and directed error messages" over production-rule
   models — again, model-tracing decides, text realises.

Chat remains *one mechanism*: free text is how a child answers a short question (Short-Answer
Surface) or asks «Hỏi SAM về đoạn này» from Mode 1 — always carrying `LearningContext`
(Convergence §11: "a chat box that does not know which lesson is open is the definition of a
chatbot").

## 3. The concept board's frame 6, reconciled with the fail-closed rule

Frame 6 shows: pre-question → A–D options → "Chính xác! 🎉" → "Thử thách tiếp theo" free text.

| Board element | Rule it touches | Honest version |
|---|---|---|
| Pre-question A–D graded "Chính xác!" | No grading without an SGV key (`TvQuestion` has *no* answer field by design; WAL-204: options without key ⇒ `gradable=false` ⇒ `correct=null`; MEASURED: SGV answer keys exist for 309 lessons in the registry, deterministic SGK↔SGV linkage proven for 2 Tin học lessons only) | The pre-question is a **`diagnosticProbe`** (SupportLevel.none): SAM records the answer as `independentAttempt correct=null` and says what it *can* say — «SAM ghi nhận câu trả lời của con — mình cùng xem trong bài nhé» — unless a key exists, in which case `QuizSelect` grading applies with `feedbackFor` (4-axis, no ability praise). "🎉" only on evidence-backed events (Convergence §6 test 1: *can the praise be wrong?*). |
| "Thử thách tiếp theo" free-text | `shortText → unsupported` today | This **is** the Short-Answer Surface (WAL-206 §6 P0-NEXT): passage/context + question, learner answers by text/voice, SAM gives *ungraded* guidance (pumpRecall/smallHint, generative-guarded), evidence `correct: null`, act `askExplanation`. |
| Mascot "SAM sẽ dạy, hỏi, gợi ý và luyện tập cùng con" | Blueprint sequence + `learnerFirst` | Correct as a promise only where a blueprint or a routed activity exists; otherwise the fail-closed line «SAM chưa dạy được bài này» (`PEDAGOGICAL-PROVENANCE-UX.md`) |
| SAM chat-bubble layout | Convergence §7 "presence inversely proportional to the child's momentary capability" | Keep bubbles for SAM's moves; **SAM disappears while the child is answering**; no free-form input except where a Surface asks for it |

## 4. Prior art per field (compact)

| System | Content model | Tutor model | Evidence model | What SAM takes | What SAM does NOT take |
|---|---|---|---|---|---|
| **Oppia** (`10`) | Exploration = states; each State{content, interaction{answer_groups[{rule_specs, outcome{dest, feedback, labelled_as_correct, missing_prerequisite_skill_id}, tagged_skill_misconception_id}], hints[], solution}} | authored branching; misconception-tagged feedback; Skill{misconceptions[{feedback, must_be_addressed}], rubrics, prerequisite_skill_ids} | `labelled_as_correct` is an *authored* key | misconception object shape; hints as ordered ladder; "no key ⇒ no correct label" | authoring 3,679 explorations; card-by-card conversation as the primary UI |
| **AutoTutor** | expectations + misconceptions per problem | EMT dialogue; pump/hint/prompt/assertion | semantic match of turns to expectations | act taxonomy already mirrors it (`pumpRecall`, `smallHint`, `explainConcept` = assertion last) | LSA-era semantic matching as a grader |
| **Cognitive Tutor** | production rules per skill | model tracing; immediate short feedback; knowledge tracing | per-rule mastery | BKT per SkillCase (already ADR-001) | rule authoring per domain |
| **ASSISTments** (FROM-REFERENCE — Heffernan & Heffernan 2014, IJAIED; "Scaffolding vs. Hints in the Assistment System", 2006) | problem + hints + scaffolds + videos | scaffolding questions after a wrong answer outperformed hints conveying the same information | correctness + hint count | scaffold-as-question before hint-as-content (SAM's `diagnosticProbe` before `smallHint`) | teacher-authored problem sets at scale |
| **DeepTutor** (`08`) | Guided-learning block types: diagnostic · pretest · retrieval_practice · error_diagnosis · module_test · progress_dashboard | agent loop "thinks in rounds, calls tools" — the *model* decides | quiz attempts per reader (overlay) | the *vocabulary* of guided-learning blocks matches SAM's acts | agent loop deciding pedagogy; LLM-graded quizzes |
| **Mathigon** (`09`) | steps with `goals`; blanks `[[a|b|c]]`; per-step hint keys | virtual tutor "Archie" sends `hints.yaml` messages on step events | step scored when goals met | deterministic, keyed hints per step; textbook + tutor in one page | random praise lists ("Well done", "Great Work!") |

## 5. Evidence moving between Views (Q14) and continuity from Mode 1 (Q15)

- Evidence is keyed by `skillCaseId`/`conceptIds` + `sourceDocumentId`/`lessonNo` + `act`, never
  by Surface or View (`evidence_validator.dart:67-82`). A Mode 3 session can therefore *read*
  state produced anywhere and Mode 1/2 can *show* state (e.g. a "con còn nhầm phần này" marker
  on a block) without minting anything.
- Continuity Mode 1 → Mode 3: the block id under the child's finger (`Hỏi SAM về đoạn này`) is
  added to `LearningContext` (a new optional field `anchorBlockId` — HYPOTHESIS, `12`); the
  Pedagogy Runtime treats it as scope narrowing, not as a question the LLM may answer freely.
  TRACE from Mode 1 ("đã xem trang 14") lets SAM *greet with context* (Convergence §7) — never
  infer understanding.

## 6. What NOT to copy

- A chat-first Mode 3 (DeepTutor Chat/Ask, OpenMAIC "AI teachers and peers … in real time").
- LLM-generated MCQs with LLM-declared `correct_answer` (DeepTutor quiz; OpenMAIC "quizzes with
  AI grading") — violates "RETRIEVED ≠ PERMITTED" and "no key ⇒ no grade".
- Random praise banks (Mathigon `hints.yaml` `correct:` list) — violates `bannedAbilityPraise`.
- Oppia-style hand-authored branching per lesson at K-12 scale.

## 7. What Mode 3 needs before it can be promised for a lesson (checklist)

1. A routed activity or blueprint for that `LessonKey` (else «SAM chưa dạy được bài này»).
2. A Surface for the activity's response kind (Short-Answer is the missing one).
3. `LearningContext` with intent ≠ lookup.
4. A `PlannedAct` sequence with cap and required evidence (blueprint) or the Scale path's
   per-Surface policy (`reader-v1`, `experiment-v1`).
5. An SGV key if anything is to be marked correct; otherwise `correct: null` and SAM says so.
