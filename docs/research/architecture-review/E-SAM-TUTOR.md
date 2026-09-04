# E — SAM Tutor ≠ Chat (the LLM realises permitted pedagogy; it never decides it)

**Founder order (item 7).** This page maps the order onto what exists in code and onto what the slice's source layer permits. Nothing was implemented; the shadow LLM path stays shadow.

## E.1 What exists (OBSERVED-IN-CODE)

| layer | Dart | status |
|---|---|---|
| Pedagogy taxonomy | `PedagogicalIntent`, `TeachingAct`, `AssistanceRung`, `PlannedAct` — `lib/core/pedagogy/pedagogy_model.dart:41,54,99,125` | types exist |
| Patterns / blueprints | `PedagogicalPattern`, `LearningExperienceBlueprint` — `lib/core/pedagogy/pedagogical_pattern.dart:60`, `learning_blueprint.dart:24` (+ `blueprint_catalogue_v0.dart`, 8 constants) | **zero consumers in `lib/features/`** |
| Realisation guard | `RealizationPolicy`, `RealizationRequest`, `validateRealization()` — `lib/core/pedagogy/realization_contract.dart:30,59,88`; fails closed on `ACT_OVER_RUNG` (`:92`) then delegates to `validateTutorOutput` | header: *"VẪN SHADOW, WAL-30 gate"*; no caller in features |
| Tutor provenance | `TeachingProvenance {conceptId, skillCaseId?, stage, method, methodReason, authority?}` — `lib/core/tutor/teaching_provenance.dart:25` | used by `tutor_prompt.dart` |
| Evidence gate | `validateCandidateEvidence()` — `lib/core/student/evidence_validator.dart:58` (null on `lookup`, null on empty text) | only `experiment_screen.dart:81,92` mints through it |

So the architecture the order describes — *pedagogy decided deterministically, the model only words it* — is already the shape of `realization_contract.dart`; what is missing is (a) a runtime that calls it and (b) a **source** whose blocks carry the trust the realisation may quote.

## E.2 What the slice permits a Tutor to do — MEASURED (see I)

| Tutor act | needs | measured on the slice gold | permitted today? |
|---|---|---|---|
| **Read / paraphrase a trusted passage** (T1) | trusted BODY blocks with provenance | text accuracy 0.98 on science pages, FTR 0.10–0.12 (hard pages), 0 splices on 20/23 science pages | yes, with the same false-trust caveat as the Smart Book (≈ 1 in 10 hard-page blocks wrong) |
| **Ask a textbook question** (T1r) | QUESTION role precision ≥ 0.95 | 0.83–0.89 (all questions), 0.92–0.97 (TRUSTED questions), n = 33–84 | **no** — deferred (Short-Answer gate, see ROLE-LAYER-AND-SHORT-ANSWER-GATE.md) |
| **Grade an answer** | SGV `answer_of` relation | SGV sample: pairing by (lesson, enumerator) measured as an upper bound only (I.5); answer keys are withheld by the answer-leak guard | **no** — `correct: null` stays |
| **Explain a figure** | figure region + caption | figure/caption association 0.75–0.86 (D.2) | only as "see Hình N on page P" until J.1 |
| **State the lesson objective** | OBJECTIVE role | precision 0.70 / recall 0.92–0.94 | as a quoted line with provenance, not as a prompt |
| **Run an activity / experiment** | ACTIVITY + INSTRUCTION roles | ACTIVITY precision **0.00** (n=3–6), INSTRUCTION 0.5 | **no** |

## E.3 Where the LLM sits (HYPOTHESIS, consistent with the order and with `realization_contract.dart`)

```
TrustedStructuredLesson (blocks with role+trust)  ──►  PedagogyRuntime (deterministic: which act, which rung, which block ids)
                                                          │
                                                          ▼
                                            RealizationRequest{act, rung, facts = block texts by id}
                                                          │
                                                          ▼
                                            LLM wording  ──►  validateRealization()  ──►  Surface
```
The model receives *block ids and their trusted text* as facts and a *permitted act*; it may not add a fact, may not pick a block the runtime did not pick, and may not turn a BODY block into a question. `validateRealization` is the fail-closed seam that already exists (`realization_contract.dart:88`).

## E.4 What the slice says about "SAM Tutor ≠ Chat" concretely

- A chat needs retrieval over everything; a Tutor needs **the TSL of one lesson** and nothing else. The TSL is small (median lesson: tens of trusted blocks — I.4) and carries the withheld regions with reasons, so the Tutor can say *"the book has a figure here that I cannot show"* instead of hallucinating it.
- The QUESTION role is the boundary between reading and asking. Until the role layer reaches its target, the Tutor's permitted acts are read/paraphrase/point-to-page; **asking** is the act the deferral removes.

## E.5 Not done

No prompt was written, no model was called, no `PedagogyRuntime` was built. The four ABSENT symbols in F.1 remain absent.
