# 14 — Activity Patterns × Learning Views (Q13)

**Founder rule (§6):** no 27 buttons/modes. Activity Patterns are underlying capabilities /
Learning Surfaces used **inside** a View. Learning View = product-level experience; Activity
Pattern / Surface = capability inside a View.

## 1. The rule, stated so implementation cannot drift

```
Learning View (3, visible, chosen or proposed)
   └─ uses ▸ Learning Surface (N, invisible as a menu — appears only when a lesson's activity needs it)
                 └─ hosts ▸ Activity Pattern (27, corpus-derived; never a button)
```

- A pattern reaches the child only through a Surface, and a Surface only through a View.
- The View decides **which patterns are eligible** (Mode 1: reading-safe ones; Mode 2:
  interactions on a representation; Mode 3: whatever the Pedagogy Runtime plans).
- The mapping pattern → Surface stays in **one** place (ADR-009 spirit: `resolveSurface` for the
  Deep path; `_activityAction` for the Scale path today — the two seams are a known duplication,
  not to be tripled).

## 2. Registry → View mapping (MEASURED counts from `K12-ACTIVITY-PATTERN-REGISTRY.md`)

| Pattern | Unique / primary lessons | Surface today | View(s) where it belongs | Notes |
|---|---|---|---|---|
| EXPLAIN_SHORT | 874 / 229 | **none** (`shortText → unsupported`) | **Mode 3** (planned by runtime as `askExplanation`/`diagnosticProbe`); Mode 1 inline «Hỏi SAM» | P0-NEXT Short-Answer Surface (WAL-206 §6): +76 content-valid Science lessons measured |
| OBSERVE | 352 / 166 | none | Mode 2 (observe a figure/process) → Mode 3 describe | text-only subset hostable in Short-Answer; figure-dependent stays blocked (needs figure block) |
| ORAL_SHARE | 375 / 53 | none (VOICE) | Mode 3 | modality gap — WAL-205 backlog |
| RESEARCH_PROJECT | 288 / 15 | none | Mode 3 (plan/reflect) | external object modality |
| SELECT_MCQ | 287 / 188 | QuizSelect | Mode 3; Mode 1 inline check | graded only with SGV key |
| DRAW_CREATE | 260 / 159 | none (camera) | Mode 3 (artifact submission, ungraded) | P2 |
| READ_TEXT | 253 / 151 | ReaderScreen | **Mode 1** (the book itself) → Mode 3 question | READ gate = Mode 1's own gate |
| FILL_BLANK | 150 / 43 | none | Mode 1 inline (Mathigon-style blanks) / Mode 3 | key required for grading |
| WRITE_TEXT | 149 / 50 | ComposeLite | Mode 3 | REVEAL gate |
| AUDIO_PERFORM | 143 / 24 | none | Mode 3 | modality gap |
| COMPUTE_SOLVE | 124 / 106 | TutorScreen (fractions only) | Mode 3 | general checker needed |
| COMPARE | 123 / 30 | none | **Mode 2** (Comparison renderer) → Mode 3 | needs `ComparisonDimension[]` (table extraction) |
| DIAGRAM_COMPLETE | 120 / 59 | none | **Mode 2** (complete the diagram) | needs typed diagram data |
| CLASSIFY_SORT | 110 / 24 | none | **Mode 2** (Classification tree) / Mode 3 | needs `Taxon[]` |
| ROLEPLAY_GAME | 102 / 32 | none | Mode 3 | group/voice modality |
| EXPERIMENT | 65 / 57 | ExperimentScreen | **Mode 2** (Process view) + **Mode 3** (predict → observe) | the one pattern already living in two Views (WAL-185) |
| DICTATION | 63 / 47 | none | Mode 3 | TTS |
| PLAN_REFLECT | 62 / 1 | none | Mode 3 (`reflect` act) | — |
| HANDS_ON_TOOL | 59 / 1 | none | Mode 3 | external object |
| CODE | 50 / 50 | none | Mode 3 | Tin học |
| MATCH | 48 / 13 | none | Mode 2/3 | key required |
| SOURCE_REASONING | 42 / 23 | SourceReaderScreen | **Mode 1** (source block) → **Mode 3** (conclusion) | three typed claims |
| PHYSICAL | 33 / 35 | none | — (EXTERNAL_MODALITY) | out of scope |
| DATA_CHART | 23 / 9 | none | **Mode 2** (Data/Chart) | table extraction |
| PROVE | 20 / 8 | none | Mode 3 | — |
| TRUE_FALSE | 17 / 5 | QuizSelect (2-option) | Mode 3 | key required |
| MAP_SPATIAL | 15 / 4 | MapReaderScreen | **Mode 2** (Spatial) → Mode 3 question | curated assets |

Reading: **Mode 3 hosts almost every pattern**; **Mode 2 hosts the six structural ones**
(OBSERVE-figure, COMPARE, DIAGRAM_COMPLETE, CLASSIFY_SORT, DATA_CHART, MAP_SPATIAL, plus
EXPERIMENT as Process); **Mode 1 hosts only READ_TEXT, SOURCE_REASONING and inline
checks** (FILL_BLANK/SELECT_MCQ where a key exists). This is the concrete meaning of "views ≠
27 modes".

## 3. Selection inside a View

- **Mode 3:** the Pedagogy Runtime (`decide()` / blueprint `sequence`) picks the next
  `PlannedAct`; the act's response kind selects the Surface (`resolveSurface`). The child never
  picks a pattern; SAM may say why («SAM hỏi con trước để xem con nhớ gì») — WAL-114 provenance
  applies.
- **Mode 2:** the representation is chosen by *data shape* (`05` §2); interactions offered are
  the patterns that the shape supports (Process → order steps; Classification → sort; Comparison
  → fill the cell). Each interaction is a `CandidateEvidence` claim.
- **Mode 1:** patterns appear only as the book's own questions/activities in reading order,
  behind the READ gate; answering routes to the same Surfaces as Mode 3 (so Mode 1 → Mode 3
  continuity is a Surface push, not a mode switch — Q15).

## 4. What the registry does NOT yet allow

- Any pattern whose detector is "directive classifier only (≈85% precision)" cannot be promised
  per lesson; it can be *offered* fail-closed (SAM: «bài này có câu hỏi ngắn — con thử trả lời
  nhé») with `correct: null`.
- Modality-blocked patterns (VOICE, AUDIO, DRAWING/CAMERA, EXTERNAL OBJECT, MOVEMENT, GROUP) stay
  in WAL-205; Views do not unblock modality.
- The 27-pattern expansion remains **not implemented** (WAL-203/205 preserved) — this document
  only places patterns; it does not promote any.

## 5. Naming for the Founder's list (§6)

SAM TUTOR → Observe (OBSERVE), Compare (COMPARE), Calculate (COMPUTE_SOLVE), Reading (READ_TEXT),
Writing (WRITE_TEXT), Experiment (EXPERIMENT), Question (SELECT_MCQ/TRUE_FALSE), Classify
(CLASSIFY_SORT), ShortAnswer (EXPLAIN_SHORT) — each is a registry pattern, each maps to exactly
one Surface family, none is a top-level control.
