# 07 — Reference Repository Comparison

Method: each P0 repo was shallow-cloned to the session scratch directory and read (README, docs,
key source); P1 repos read via README/source; standards and papers via fetch/search. Every cell is
FROM-REFERENCE unless marked. Where a fetch failed it is stated. Full 12-field write-ups: `08`
(DeepTutor), `09` (Mathigon), `10` (Oppia), `11` (H5P, Scaffold, OpenMAIC, standards, ITS).

## 1. Matrix

| Field | DeepTutor (P0) | Mathigon textbooks (P0) | Oppia (P0) | H5P (P1) | Scaffold (P1, experimental) | OpenMAIC (P1) |
|---|---|---|---|---|---|---|
| **Reusable product principle** | "not a static PDF, but a reading environment built from typed blocks"; per-reader overlay separate from shared book | "Part textbook and part virtual personal tutor" — reading and tutoring on one page, gated by steps | "simulate a one-on-one conversation with a tutor" — feedback → next state; skills with misconceptions | reusable interactive content types composed into a book | "build once, deliver through different platforms"; authoring ≠ runtime; "learner projections must not expose private answer-key data" | "turns any topic or document into a rich, interactive classroom" |
| **Content model** | Book → Spine → Chapter{learning_objectives, source_anchors, prerequisites} → Page{content_type} → Block{type(19), status, payload, source_anchors} + ConceptGraph | course folder: `content.md` (custom Markdown), `functions.ts`, `styles.scss`, `hints.yaml`; shared glossary/bios | Exploration → States; Skill{description, misconceptions, rubrics, prerequisite_skill_ids}; Topic/Story/Question | library.json + semantics.json + content.json per content type; Interactive Book = chapters of `H5P.Column` | `@scaffold/contracts` provider-neutral document schema; pages and slideshows share one model | `Stage` → `Scene{type: slide|quiz|interactive|pbl}`; `@openmaic/dsl` JSON schema |
| **Lesson model** | chapter = lesson; page templates by ContentType (theory/derivation/history/practice/concept/overview) choose block mix | course = chapters; section (`> section:`) → steps (`> id:` with `> goals:`) | exploration with checkpoints (`card_is_checkpoint`) and linked skills | book → chapter → column of blocks | course artifact | classroom = ordered scenes with actions/narration |
| **Renderer model** | Next.js reader; one component per BlockType; Page Chat per chapter | `@mathigon/studio` parser + web components (`x-geopad`, `x-slider`, `x-equation`, …), TS per course | Angular; one interaction component per interaction id | H5P runtime loads libraries; each content type renders itself | React/Tiptap; separate authoring vs learner-runtime view registries | `@openmaic/renderer`; interactive = LLM-generated HTML in iframe `srcDoc` |
| **Interaction model** | insert/move/regenerate blocks; capture inbox; quiz attempts; flash cards | inline blanks `[[a|b|c]]`, reveal-on-goal, drag/gesture, sliders; `btn:next` | interaction id + customization_args + answer groups (rule_specs) | per content type (quiz, timeline, video, …) | blocks + assessment contracts | quiz (MCQ/short answer), simulations, PBL milestones, multi-agent discussion |
| **Tutor model** | unified agent loop ("thinks in rounds, calls tools"), modes: Chat/Ask/Quiz/Research/Visualize; memory 3-layer | "Archie" virtual tutor: keyed messages from `hints.yaml` on step events (`$step.addHint`) | outcome.feedback per answer group; hints[]; solution; misconception-tagged feedback | none (content-local feedback) | none (Agent is a separate hosted product) | "AI teachers and peers lecture, discuss, and interact… in real time" (LangGraph) |
| **Assessment / evidence model** | quiz via QuestionPipeline (LLM-generated, `correct_answer` from LLM); progress + quiz stats per reader | step `score(goal)`; correct/incorrect events | `labelled_as_correct` authored per outcome; `Solution{answer_is_exclusive, correct_answer, explanation}` | xAPI statements from content types | deterministic TypeScript grading in `@scaffold/grading`, outside React | "quizzes with real-time AI feedback" |
| **Strengths** | clear typed-block schema; per-block status (hidden/error); separation of shared book vs reader overlay; anchors as first-class field | textbook+tutor coexistence; deterministic keyed hints; goal-gated progression; rich typed components | mature open ITS-shaped data model; explicit misconceptions + prerequisites; Apache-2.0 | ecosystem of reusable types; typed Timeline model (startDate/endDate/headline/text/asset/era) | clean contracts/grading/core boundaries; answer keys never in learner projection | scene DSL with schema validation; multi-modal outputs |
| **Weaknesses (for SAM)** | content is LLM-written; visual/quiz blocks have empty `source_anchors`; anchors are snippets not page/bbox; model decides pedagogy | hand-authored per course with TS; no provenance concept (content *is* the source); random praise lists; proprietary content | authored branching per exploration; web-app scale; no source-document provenance | authoring, not extraction; GPL core; no learner model | pre-alpha, AGPL-3.0, format may change; no tutor | everything generated; diagrams are HTML; AI grading |
| **License** | Apache-2.0 (`LICENSE`) | no LICENSE file; README "© Mathigon 2016–2022, All rights reserved"; CLA required; `@mathigon/studio` separate | Apache-2.0 | core `h5p-php-library` GPL-3.0; Interactive Book MIT; Timeline MIT | AGPL-3.0-only | MIT (bundled `mathml2omml` LGPL-3.0-or-later) |
| **Maturity** | README: "20k stars in 111 days"; CITATION.cff paper "DeepTutor: Towards Agentic Personalized Tutoring" (arXiv 2604.26962); Python 3.11–3.14, FastAPI, Next.js 16 | 392 stars / 160 forks (GitHub page at fetch time); production site; ages 12–18 | 6.8k stars, 16.9k commits, Python/Angular/GAE; production (basic maths lessons) | Interactive Book 1,211 commits; H5P widely deployed in LMSs | "pre-alpha" (README); adapters for Open edX/Moodle | v1.0.0 2026-08-27; JCST 2026 paper; Tsinghua |
| **Applicability to SAM** | schema template for a lesson document; per-reader overlay ↔ shared-device profiles; "Page Chat" ↔ «Hỏi SAM về đoạn này» | Mode 1+3 coexistence; keyed deterministic hints = `RealizationPolicy.template`; goal-gating = READ/PREDICT gates generalised | misconception shape for the MISSING model; hint ladder; "no key ⇒ no correct label" | Timeline typed model as a target shape for `HistoricalEvent[]`; composition of surfaces | boundary discipline (contracts ≠ grading ≠ UI) validates SAM's own split | scene/action DSL idea for a *deterministic* session script (Mode 3 blueprint realisation) |
| **What NOT to copy** | LLM content generation; unanchored visuals; agent loop as pedagogy | authored content; random praise; license | authoring per lesson; card-conversation UI | GPL core into a Flutter app; H5P runtime | pre-alpha format dependency | generated HTML widgets; AI-graded quizzes; agent classroom |

## 2. The single most important cross-reference finding

Every reference that *generates* content (DeepTutor, OpenMAIC) sacrifices source grounding for
the visual/assessment blocks, and every reference that *keeps* grounding (Mathigon, Oppia, H5P,
Scaffold) does so by **hand authoring**. Neither path is available to SAM at 3,679 lessons.
SAM's third path — **deterministic extraction with per-block provenance and fail-closed trust** —
has no reference implementation among the six; the closest analogues are PreTeXt's
semantic-source philosophy and SAM's own stories pipeline (§28 VERIFIED gate). This is why the
Learning Views concept must be gated by the Trusted Corpus study rather than by any repo.

## 3. Fetch/clone log

| Reference | Method | Result |
|---|---|---|
| HKUDS/DeepTutor | `git clone --depth 1` → scratch (86 MB) + README fetch | OK |
| mathigon/textbooks | `git clone --depth 1` → scratch + README/GitHub page fetch | OK (no LICENSE file present) |
| oppia/oppia | README fetch + raw `core/domain/state_domain.py`, `skill_domain.py` | OK (not cloned — repo size) |
| h5p/h5p-interactive-book, h5p-timeline, h5p-php-library | GitHub page + raw `semantics.json` fetches | OK (timeline README absent; semantics fetched) |
| brainjamworks/scaffold | `git clone --depth 1` → scratch + README fetch | OK |
| THU-MAIC/OpenMAIC | `git clone --depth 1` → scratch + README fetch | OK |
| PreTeXt guide | `overview-philosophy.html` → **404**; guide index → empty body; philosophy page found via search (`philosophy.html`) | partial |
| QTI 3.0 overview, Caliper 1.2, xAPI spec | fetch | OK (QTI overview lacks response-processing detail) |
| AutoTutor, ASSISTments, Cognitive Tutors, Nesbit & Adesope, Runestone | search → abstracts | OK |
