# 11 — H5P, Scaffold, OpenMAIC, standards and ITS prior art (P1 + additional)

Only references that **change a SAM decision** are included. Each P1 repo gets the twelve fields
in compact form. All FROM-REFERENCE.

## A. H5P (P1)

| Field | Finding |
|---|---|
| Principle | reusable interactive content types (libraries) composed by authors; a book is a container of pages of blocks |
| Content model | per type: `library.json` + `semantics.json` (schema) + `content.json`; **Interactive Book** `semantics.json`: `showCoverPage`, `bookCover`, `chapters` (1–50) each a group with one `chapter` library field accepting `H5P.Column 1.22`; `behaviour{baseColor, defaultTableOfContents, progressIndicators, progressAuto, displaySummary, enableRetry}` |
| Lesson model | chapter = page of Column blocks |
| Renderer | H5P runtime loads each library's JS; each type renders itself |
| Interaction | per type (quiz, interactive video, presentation, timeline…) |
| Tutor | none |
| Assessment/evidence | xAPI statements emitted by types; per-page progress indicators (`progressAuto` or manual) |
| Strengths | ecosystem breadth; **Timeline** has a typed model: `headline`, `text`, `asset{media, credit, caption}`, `date[]{startDate, endDate (YYYY,MM,DD), headline, text, tag, asset}`, `era[]{startDate, endDate, headline, text, tag}` |
| Weaknesses | authoring not extraction; PHP/JS runtime; core GPL |
| License | `h5p-php-library` **GPL-3.0** ("GPL licensed due to GPL code being used for purifying HTML"); Interactive Book **MIT**; Timeline **MIT** |
| Maturity | Interactive Book 1,211 commits; widely deployed in Moodle/Canvas |
| Applicability | (1) Timeline's typed date model is a ready target shape for `HistoricalEvent[]` (`05`); (2) "lesson = composition of reusable blocks" applies to **Surfaces inside a View**, not to the source; (3) `progressAuto` vs manual completion mirrors TRACE vs evidence — H5P treats "viewed" as progress; SAM must not |
| Not to copy | GPL core into the app; authored content; "viewed = progress" |

**Founder question D — "Lesson → composition of reusable Learning Surfaces?"** Yes at the
Surface level (already ADR-009), no at the source level: the composition must be *derived* from
the trusted lesson document by rules (pattern → surface), not authored.

## B. Scaffold (brainjamworks, P1 / experimental)

| Field | Finding |
|---|---|
| Principle | "build course content once and deliver it through different learning platforms"; "Hosts stay in control" via explicit ports |
| Content model | `@scaffold/contracts` — "serializable, provider-neutral persisted document schemas"; pages and slideshows "share the same provider-neutral document model" |
| Lesson model | one portable course artifact |
| Renderer | `@scaffold/core` React/Tiptap with **separate authoring and learner-runtime view registries**; "Neither lane imports or traverses the opposite binding inventory" |
| Interaction | blocks + layouts + assessment contracts |
| Tutor | none public ("Scaffold Agent … separate hosted product") |
| Assessment/evidence | `@scaffold/grading` — "deterministic, framework-free answer-key validation"; "Learner projections must not expose private answer-key data"; learner responses/attempts live in host-provided ports, not in the document |
| Strengths | disciplined boundaries enforced by dependency-cruiser ("zero accepted debt"); answer keys structurally absent from the learner projection |
| Weaknesses | "pre-alpha"; "document format, package APIs, and adapter contracts can change before 1.0"; AGPL |
| License | AGPL-3.0-only |
| Maturity | pre-alpha; Open edX XBlock and Moodle adapters |
| Applicability | Validates SAM's existing split (content ≠ pedagogy ≠ evidence ≠ UI) and adds one idea worth adopting as a rule: **the learner projection of a lesson document must be a type that cannot carry answer keys** — SAM already does this for `TvQuestion` (no answer field) and `LearningActivity.composeChecklist` (no model essay); make it a stated invariant of the Trusted Structured Lesson (`12`) |
| Not to copy | the format (unstable); AGPL code |

**Founder question E** — yes, the separation "authoring/content/runtime with deterministic
logic outside UI" is exactly what lets one document feed many renderers; SAM's equivalent is
`tool/` (build) ≠ `lib/core` (deterministic runtime) ≠ `lib/features` (UI).

## C. OpenMAIC (THU-MAIC, P1)

| Field | Finding |
|---|---|
| Principle | "turns any topic or document into a rich, interactive classroom experience" |
| Content model | `@openmaic/dsl`: `Stage` (classroom) → `Scene{type: 'slide' | 'quiz' | 'interactive' | 'pbl'}`; `SCENE_TYPES` frozen; JSON schema generated with `additionalProperties: false`; `DSL_VERSION` |
| Lesson model | outline stage → scene generation per section |
| Renderer | `@openmaic/renderer`; `InteractiveContent{type:'interactive', html? (iframe srcDoc), url?, widgetType?: simulation|diagram|code|game|visualization3d|procedural-skill, widgetConfig?}` |
| Interaction | quizzes (MCQ, short answer) "with real-time AI feedback"; simulations; PBL milestones; Deep Interactive Mode (mind maps, games, coding) |
| Tutor | multi-agent (LangGraph): "AI teachers and peers lecture, discuss, and interact with you in real time"; `GeneratedAgentConfig{persona, voiceDesign…}` |
| Assessment/evidence | AI-graded |
| Strengths | a versioned, validated scene/action DSL; explicit `StageMode: autonomous|playback|edit` |
| Weaknesses | all content generated; diagrams/mind maps are LLM HTML; grading by AI |
| License | MIT (`mathml2omml` LGPL-3.0-or-later bundled) |
| Maturity | v1.0.0 (2026-08-27); JCST 2026 paper (DOI 10.1007/s11390-025-6000-0) |
| Applicability (Modes 2–3 only) | (1) A **deterministic session script** — Scene/Action with `playback` mode — is a reasonable shape for a Mode 3 *blueprint realisation*: SAM's `PatternStep` sequence could compile to a scene list whose actions are `PlannedAct`s; (2) frozen, exhaustiveness-checked type unions match SAM's `sealed class` discipline |
| Not to copy | generated slides/diagrams; AI grading; multi-agent classroom; autonomous mode |

## D. Standards that change a decision

| Standard | What it says (quoted/summarised) | Decision it changes for SAM |
|---|---|---|
| **PreTeXt** (https://pretextbook.org/doc/guide/html/philosophy.html) | "you explicitly specify the logical parts of your document and not how these parts should be displayed"; single source → PDF, HTML, EPUB, Jupyter, braille | the Trusted Structured Lesson is semantic (roles), presentation-free; Views are conversions |
| **IMS QTI 3.0** (https://www.imsglobal.org/spec/qti/v3p0/oview) | "a data format that enables a transform-free authoring-to-delivery capability"; item content is separate from response/outcome processing; accessibility built in (the overview lacks response-processing detail) | the *question* block in a lesson document must not carry scoring; scoring lives with the key (SGV) — SAM's `TvQuestion` (no answer) + `LearningActivity.correctOption` split is QTI-shaped |
| **xAPI** (https://github.com/adlnet/xAPI-Spec/blob/master/xAPI-Data.md) | `result.success` ≠ `result.completion`; verbs by IRI; `context.contextActivities.parent/grouping` | evidence events keep `correct` (success) and completion separate — SAM's `correct: null` with `EvidenceKind` already does; lesson/book lineage ≈ parent/grouping (WAL-179) |
| **IMS Caliper 1.2** (https://www.imsglobal.org/spec/caliper/v1p2) | Reading profile `NavigatedTo`/`Viewed` ≠ Assessment `Started`/`Completed`/`Submitted` | Mode 1/2 emit reading-profile TRACE; only Surfaces emit assessment-profile evidence |
| **Common Cartridge / CNXML** | not fetched in this track | none claimed |

## E. ITS and learning-science literature that changes a decision

| Source | Finding | Decision it changes |
|---|---|---|
| **AutoTutor** — Graesser et al. (IJAIED 2016 "Conversations with AutoTutor Help Students Learn"; FLAIRS 2005 "AutoTutor's Coverage of Expectations") | expectation- & misconception-tailored dialogue; pump ("What else?") → hint → prompt → assertion; student turns matched to expectations | Mode 3 is a dialogue *state machine* over expectations (= SGV objectives) and misconceptions; `TeachingAct` order pumpRecall → smallHint → strategicHint → explainConcept is the same ladder |
| **ASSISTments** — Heffernan & Heffernan 2014 (IJAIED); Razzaq & Heffernan 2006 "Scaffolding vs. Hints" | scaffolding questions after an error beat hints carrying the same information | prefer `diagnosticProbe`/scaffold question before content hints in the Short-Answer Surface |
| **Cognitive Tutors** — Anderson, Corbett, Koedinger & Pelletier 1995 (JLS 4(2)) | model tracing + knowledge tracing over production rules; "immediate feedback, consisting of short and directed error messages" worked best | keep BKT per SkillCase (ADR-001); short deterministic feedback (`RealizationPolicy.template`) is evidence-backed |
| **Nesbit & Adesope 2006** (RER 76(3)) | concept maps ↑ retention; effects vary with constructing vs viewing | Mode 2 should offer *completion/construction* interactions, not only display |
| **Runestone** — Ericson & Miller 2020 | interactive ebook elements ↑ outcomes vs static | interactivity *inside* the reading view (Mode 1 with Surfaces) has evidence |
| **Knowledge Space Theory / KLI / ECD** | already classified in `SAM-EDUCATION-DATA-ARCHITECTURE-REVIEW.md` §5 (HYPOTHESIS / RETAIN / FORMALIZE) | no change; View recommendation must not pretend to be a KST fringe computation (1 prerequisite edge exists) |

## F. What explicitly NOT to copy (consolidated, Q24)

1. LLM-generated content blocks presented as lesson content (DeepTutor, OpenMAIC).
2. Empty or snippet-only source anchors for visuals/quizzes (DeepTutor).
3. AI-graded answers without a key (OpenMAIC; DeepTutor quiz `correct_answer`).
4. Chat-first or agent-loop-first tutoring (DeepTutor, OpenMAIC).
5. Hand-authored lessons/explorations/courses as the source of truth at K-12 scale (Mathigon,
   Oppia, H5P, Scaffold).
6. Random praise banks (Mathigon).
7. "Viewed = progress" (H5P `progressAuto`).
8. GPL/AGPL code into the Flutter app (H5P core, Scaffold).
9. Generic graph/layout engines before three typed shapes exist.
10. Any block type that has no extractor and no key (e.g. "flashcards" generated per lesson).
