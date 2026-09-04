# F — LearningContext vs LearningView semantics (runtime) — kept OPEN

**Founder order (2026-09-05, item 4):** retain the three Learning Views, but do **not** finalise that Views live inside LearningContext or that Smart Book = lookup. Keep the candidate model open:

```
LearningSession
 ├── LearningContext
 ├── LearningView
 ├── TrustedLearningSource
 └── PedagogyRuntime
```

This document says what the code already has (OBSERVED-IN-CODE, with file paths), what the research docs propose (HYPOTHESIS), and the options the Founder can choose between. It decides nothing. No Dart file was changed by this slice.

## F.1 What exists today — OBSERVED-IN-CODE (worktree `lib/`, 2026-09-05)

| Candidate node | Dart today | File | Note |
|---|---|---|---|
| **LearningContext** | `LearningContext {learnerId, grade, subject?, sourceDocumentId?, lessonNo?, intent?}` | `lib/core/context/learning_context.dart:17` | the single runtime address; built at `lib/features/subjects/subject_home_screen.dart:307,674`; consumed by `evidence_validator.dart:60`, `reader_screen.dart:45`, `compose_lite_screen.dart:53`, `experiment_screen.dart:41`, `source_reader.dart:68` |
| **intent** (learner-owned axis) | `LearningIntent {prepare, review, practice, lookup}`, `IntentProposal`, `proposeIntent()`, `availableIntents()` | `lib/core/intent/learning_intent.dart:21,49,85,65` | `proposeIntent` returns **null** when no signal (evidence → timetable → in-progress) |
| **LearningView** | **ABSENT** — no `LearningView`, `viewMode`, `SmartBook`, `VisualLearning`, `SamTutor` symbol anywhere in `lib/` | — | the nearest axes are `LearningIntent` (4 values) and two unwired presentation taxonomies `SurfaceKind`/`PresentationSurface` |
| **LearningSession** | `LearningSession {sessionId, learnerId, subjectId, startedAt, endedAt?, trigger, mode, conceptIds[], skillCaseIds[], events[]}` | `lib/core/store/learning_session.dart:30` (+ `SessionTrigger`, `SessionMode` :18/:28) | a **per-sitting record** written by `session_recorder.dart:37` — not a runtime container of Context/View/Source |
| **TrustedLearningSource** | **ABSENT** — no block, `trust.status`, `blockId`, `regionPath`, `ocrConf` reaches Dart | — | provenance exists per *asset* only: `SourceAsset {pagePdf, pagePrinted?, bboxFrac[4], extractionVersion}` `lib/core/assets/learning_asset.dart:29-56`, `IndexedSourceAsset` `lesson_index.dart:181`, `DiaMap` `lesson_index.dart:133`; per *chunk*: `Provenance {pageStart, pageEnd}` `lib/core/knowledge/provenance.dart:43` (printed pages) |
| **PedagogyRuntime** | **ABSENT as a runtime**; the *types* exist: `PedagogicalIntent`, `TeachingAct`, `AssistanceRung`, `PlannedAct` (`lib/core/pedagogy/pedagogy_model.dart`), `PedagogicalPattern`, `LearningExperienceBlueprint` (`learning_blueprint.dart:24` — 8 constants, **zero consumers in `lib/features/`**), `RealizationPolicy` + `validateRealization()` (`realization_contract.dart:88`, header says *"VẪN SHADOW, WAL-30 gate"*, no caller in features) | — | the LLM path is shadow-only; nothing in a Surface calls the pedagogy runtime |
| Surface resolution | `resolveSurface()` `lib/core/tutor/learning_activity.dart:90` is declared "the only mapping" but **no feature calls it**; screens are chosen in `_activityAction` (`subject_home_screen.dart:643`) and `LearningActivity` is filled in *after* the screen is chosen (`:791`, `:824`) | — | the ordering documented at `learning_activity.dart:3-6` is inverted in practice |
| Content licence seam | `ContentLicense.localResearchOnly` `lib/core/knowledge/knowledge_content_provider.dart:18` — *"Corpus SGK hôm nay ở mức này"*; `SourceAsset` asserts its path under `assets/pack/` (`learning_asset.dart:42`) | — | the legal seam exists as an enum + an assert; **no implementation of `KnowledgeContentProvider` exists in `lib/`** |

How a lesson reaches a surface today (OBSERVED-IN-CODE): `assets/pack/lesson-index-g{N}.json` → `LessonIndex.loadForGrade()` (`lesson_index.dart:627`, fail-closed parse) → `main.dart:187/487` → `BookShelfScreen`/`SubjectsScreen` → `SubjectHomeScreen.openLessonWithIntent:80` → `activitiesFor:367` → `_startIntent:668` builds one `LearningContext` (`:674`) → `activitiesForIntent:601` → `_activityAction:643` → `ReaderScreen` / `ComposeLiteScreen` / `ExperimentScreen` / `SourceReaderScreen` / `SourceGalleryScreen` / `MapReaderScreen` → `recordSession()` (`session_recorder.dart:25`).

## F.2 What the research proposes — HYPOTHESIS (docs/research/learning-views)

- `12-STRUCTURED-LESSON-HYPOTHESIS.md` §3: a `TrustedLessonDocument` per `LessonKey`, a **projection** of the SDM's TRUSTED subset, with invariants: no answer keys in the learner projection; every block has a `sourceRef`; non-TRUSTED blocks never render as text; **"Views are pure functions of the document + learner state"**; `bindings=[]` must still work.
- `13-LEARNING-VIEW-DATA-FLOW.md` line 49–50: `LearningContext {…, anchorBlockId?}` is *where SAM stands*; the **Learning View is a separate, chosen-or-proposed node downstream of the context**, fanning to Đọc / Trực quan / Học với SAM; §3: display in Views 1–2 is **TRACE only**, never a `LearningEvent`; the View id is **not** stored on the evidence record — the Surface/policy id is.
- `15-SOURCE-TRUST-AND-PROVENANCE.md` §2: the trust vocabulary a View may act on — T0 page image · T1 trusted block · **T1r trusted role (needs question precision ≥ 0.95)** · T2 withheld · T3 typed datum · T4 curated · T5 keyed · X inferred; *"a T1 block without T1r may be read but never asked."*

Neither document proposes a new `LearningSession` class: 13 §3 resolves session identity through `policyId` + TRACE and keeps the View out of the evidence record.

## F.3 What this slice adds to the question — MEASURED

The slice produced the first artefact that would sit under `TrustedLearningSource`: a **Trusted Structured Lesson** per attached lesson (see B / I). Its shape settles two things the runtime debate needed, without deciding the runtime:

1. A View has something *typed* to consume: ordered trusted blocks with roles + withheld regions with reasons (B.1). The three Views are not three extractors; they are three projections of one document — consistent with 12 §3's invariant.
2. **T1r is not reached** on the slice gold: QUESTION precision 0.83–0.89 (all questions) / 0.92–0.97 (TRUSTED questions), see I.3. So today only *reading* a trusted block is licensed by the evidence; *asking* it is not. Any runtime model must be able to represent "block readable, not askable" — which is a property of the **source**, not of the View or the Context.

## F.4 The options (not decided)

| # | Option | What it implies for code | Fits evidence? | Cost |
|---|---|---|---|---|
| F-a | **View inside LearningContext** (`LearningContext.view`) — the converged model of WAL-207 `03` §3 | one field added to `learning_context.dart:17`; `_activityAction` switches on it; no new node | fits 13 §3 (View is presentation) but makes a *presentation* choice part of the runtime address that evidence, `validateCandidateEvidence` and every screen already carry | lowest |
| F-b | **LearningView as a sibling node** chosen after the context (13's arrow) | a `LearningView` enum + a selector on `SubjectHomeScreen`; context untouched; View passed to the screen | fits 13 line 50 literally; keeps the context stable for evidence; introduces a fourth thing a screen receives | low |
| F-c | **LearningSession as the runtime container** (the Founder's candidate tree) | a new runtime object holding Context + View + TrustedLearningSource handle + PedagogyRuntime handle, created per lesson entry; today's `LearningSession` *record* (`learning_session.dart:30`) would be renamed or made the persisted projection of it | the only option that gives `TrustedLearningSource` and `PedagogyRuntime` a home; nothing in `lib/` implements either yet, so the container would hold two empty slots today | highest; risks anti-principle #5 if built before the two slots have content |
| F-d | **Keep today's shape** (Context + intent; Views deferred until a TrustedLearningSource exists in Dart) | no change; the slice's TSL stays offline data until the source layer is adopted (decision records in E / `docs/research/architecture-review/DECISIONS-REQUESTED.md`) | consistent with "no major Learning Views implementation yet" (Founder item 8) | zero now; delays the F question to the next review |

**Smart Book = lookup?** (explicitly kept open by the Founder.) OBSERVED-IN-CODE: `lookup` strips exercises (`activitiesForIntent:601`) and makes `validateCandidateEvidence` return null (`evidence_validator.dart:64`) — i.e. today `lookup` already *is* "read without evidence", which is what 13 §3 wants for the Smart Book View. That is an argument for F-a/F-d (no new axis); the counter-argument (WAL-207 `17` OQ9) is that a Smart Book *inside* `prepare`/`review` would also be read-only, so "lookup" is a poor name for a View. No evidence in this slice decides it.

## F.5 What must be true under every option (from the slice)

- The per-block `trust.status` and `role.confidence` must reach Dart **before** any View asks a question; today none of it does (F.1). Whichever option is chosen, the first Dart change is a `TrustedLearningSource` reader, not a View.
- `SourceAsset.bboxFrac` is `[l, t, r, b]` (`learning_asset.dart:54`) while the SDM/TSL bbox is `[x, y, w, h]` (B.1) — a one-time conversion, recorded as C10 in WAL-207 `17` §5.
- Page-image delivery to a learner is a **legal gate** (J.1), not a runtime option; the TSL's `no_images` projection (C.2) is the one every option must run on until that gate opens.
