# 10 — Oppia — Findings (P0)

Source: https://github.com/oppia/oppia — README fetch; raw `core/domain/state_domain.py` and
`core/domain/skill_domain.py` (develop) fetched and summarised. Not cloned (size). All
FROM-REFERENCE. Field names quoted from source; where a field could not be confirmed it is said.

## The twelve fields

1. **Reusable product principle.** "a free, online learning platform to make quality education
   accessible for all"; explorations "simulate a one-on-one conversation with a tutor" and let
   "students learn by doing while getting feedback".
2. **Content model.** Exploration → ordered **States**. `State{content, interaction, param_changes,
   recorded_voiceovers, solicit_answer_details, card_is_checkpoint, linked_skill_id, …}`.
   `InteractionInstance{id, customization_args, answer_groups[], default_outcome,
   confirmed_unclassified_answers, hints[], solution}`. `AnswerGroup{rule_specs[], outcome,
   training_data[], tagged_skill_misconception_id ('<skill_id>-<misconception_id>')}` — "These
   rules are ORed together." `Outcome{dest, feedback, labelled_as_correct, param_changes,
   refresher_exploration_id, missing_prerequisite_skill_id}`. `Hint{hint_content}`.
   `Solution{answer_is_exclusive, correct_answer, explanation}` — "A solution consists of
   answer_is_exclusive, correct_answer and an explanation." (A `dest_if_really_stuck` field was
   asked for but not confirmed in the fetched excerpt — not claimed.)
3. **Lesson model.** Exploration = a tutoring state machine; checkpoints per card; states link to
   skills (`linked_skill_id`). Skills: `Skill{description, misconceptions[], rubrics[],
   skill_contents{explanation}, prerequisite_skill_ids[], superseding_skill_id,
   all_questions_merged}`; `Misconception{id, name, notes, feedback, must_be_addressed}`;
   `Rubric{difficulty, explanations}`. Topics/stories/questions sit above (not fetched).
4. **Renderer model.** Angular front end; one component per interaction id (text input, multiple
   choice, numeric, drag-and-drop, etc.); Python domain layer on Google App Engine.
5. **Interaction model.** Learner answers the current state's interaction; answer matched against
   answer groups' rule specs; outcome gives feedback and the destination state (branching), possibly
   labelled correct, possibly pointing to a missing prerequisite skill or a refresher exploration.
6. **Tutor model.** Authored, deterministic branching with targeted feedback; ordered `hints[]`
   then `solution`; misconception-tagged answer groups auto-populate feedback from the skill's
   misconception (`Misconception.feedback`; `must_be_addressed` forces coverage in linked questions).
7. **Assessment / evidence model.** `labelled_as_correct` is an **authored key** per outcome;
   `training_data` supports classifier-assisted matching; progress by checkpoints. Skill mastery
   is computed from question responses (not fetched here).
8. **Strengths.** A mature, open, ITS-shaped data model in which *misconceptions are first-class
   objects with feedback*, prerequisites are explicit, hints are an ordered ladder, and correctness
   is never inferred — it is authored. Apache-2.0. Production usage.
9. **Weaknesses (for SAM).** Everything is authored per exploration (thousands of states for a
   K-12 corpus); no notion of a source document or provenance (the exploration *is* the content);
   card-by-card conversation UI is a chat-like primary experience; web/App Engine stack irrelevant
   to a local-first Flutter app.
10. **License.** Apache v2 (README: "The Oppia code is released under the Apache v2 license").
11. **Maturity.** 6.8k stars, 5.7k forks, 16,921 commits on `develop`, 1.7k open issues, 245
    watchers (GitHub page at fetch time); lessons on basic mathematics in production.
12. **Applicability to SAM — prior art, not a model to force SAM into.**

| Oppia | SAM today | Read-across |
|---|---|---|
| `Skill` | `Concept` / `SkillCase` | same granularity split (SAM's SkillCase is below Concept; Oppia's rubric difficulty is a third axis SAM lacks — SAM has `ChallengeSignal` 🌱/🎯/🚀 instead) |
| `Misconception{feedback, must_be_addressed}` | **MISSING** (seed `source_misconception.dart`; `Blueprint.misconceptionIds`) | the shape to adopt when SGV "lưu ý/sai lầm thường gặp" extraction exists; `must_be_addressed` ↔ `evidenceRequired` |
| `AnswerGroup.rule_specs` + `tagged_skill_misconception_id` | `ExerciseSkillMap` (Q-matrix) + `ErrorHypothesis{careless, procedural, conceptual}` | SAM diagnoses at runtime; Oppia matches authored patterns — SAM must not author per lesson |
| `hints[]` → `solution` | `AssistanceRung` ladder → `revealAnswer` (`SupportLevel.fullSolution`) | same monotone ladder; SAM additionally records the rung into evidence |
| `Outcome.labelled_as_correct` | `LearningActivity.gradable` / `correctOption` | **same fail-closed rule**: no authored key ⇒ nothing is "correct" |
| `Outcome.dest` (authored next state) | `decide()` → `LearningAction`; `PlannedAct` | SAM computes the next move; Oppia stores it. SAM should keep runtime decision, but Oppia's `missing_prerequisite_skill_id` is a good *typed reason* for a `diagnosePrerequisite` action |
| `card_is_checkpoint` | `LearningSession` projections | a checkpoint concept could name "where Mode 3 resumes" (`13`) |

## What NOT to copy

- Authoring explorations per lesson.
- Card-conversation as the primary learner UI (Convergence §5/§23).
- `training_data` classifiers as a substitute for an SGV key.

## Founder question C — compare against Concept / SkillCase / Evidence / Student State / Pedagogy Runtime / PlannedAct / Next Action

SAM's model is *runtime-decided and provenance-gated*; Oppia's is *author-decided and
key-labelled*. They agree on the invariant that matters most to Mode 3 — **correctness is only
ever an authored/keyed fact** — and Oppia offers the cleanest public shape for the one object
SAM is missing (misconception with feedback and a must-address flag). Nothing in Oppia argues for
replacing `decide()`/`PlannedAct` with authored branching.
