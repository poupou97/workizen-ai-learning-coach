# 08 — DeepTutor (HKUDS) — Findings (P0)

Source: https://github.com/HKUDS/DeepTutor — shallow clone read in scratch (README, `deeptutor/book/`,
`web/lib/book-types.ts`, `deeptutor/book/blocks/*.py`, `CITATION.cff`, `LICENSE`). All FROM-REFERENCE.

## The twelve fields

1. **Reusable product principle.** "Book turns selected sources into an interactive living book —
   not a static PDF, but a reading environment built from typed blocks." Books start from knowledge
   bases, notebooks, question banks, or chat history; the workflow "first proposes chapter outlines
   for review before generating content". Reading state is per reader: "Shared content lives in the
   admin workspace, but reading state belongs to the reader" (`learning_overlay.py` docstring).
2. **Content model.** `Book` (manifest) → `BookInputs` (Stage 0) → `BookProposal` (Stage 1, LLM) →
   `Spine{chapters[], concept_graph?}` (Stage 2) → `Page{chapter_id, learning_objectives,
   content_type, blocks[], links[], parent_page_id}` → `Block{id, type, status, title, params,
   payload, source_anchors[], metadata, error}` (Stages 3–4) → `Progress` (Stage 5).
   `BlockType` (19): text, callout, quiz, user_note, figure, interactive, animation, code, timeline,
   flash_cards, deep_dive, section, concept_graph, diagnostic, pretest, retrieval_practice,
   error_diagnosis, module_test, progress_dashboard. `BlockStatus`: pending, generating, ready,
   error, **hidden**. `ConceptGraph{nodes[{id,label,chapter_id,description,weight}],
   edges[{src,dst,relation: depends_on|extends|related, rationale}]}`.
3. **Lesson model.** Chapter ≈ lesson: `learning_objectives[]`, `content_type` ∈ theory ·
   derivation · history · practice · concept · overview, `prerequisites[]` (chapter ids),
   `source_anchors[]`. `ContentType` "drives Page Planner template selection" (e.g. HISTORY = "text
   + timeline + figure + quiz"); `BookDepth` brief/standard/deep scales target words (0.5/1.0/1.6).
4. **Renderer model.** Next.js 16 / React 19 reader; one component per block type; "each chapter
   compiles into editable typed blocks … with its own Page Chat".
5. **Interaction model.** Insert/move/regenerate/rewrite blocks; selected passages go to a
   "learning-capture inbox"; bookmarks, notes, quiz attempts private per reader; export to Markdown;
   pause/resume compilation (`BookStatus.PAUSED`).
6. **Tutor model.** "agent-native architecture … One unified runtime powers Chat, Ask Questions,
   Quiz, Research, Visualize"; the loop: "the model thinks in rounds, calls tools when useful,
   observes the results, and finishes with a tool-free message"; `ask_user` pauses for structured
   clarification. Memory: "file-backed, three-layer system" (L1 traces, L2 curated facts, L3
   cross-surface synthesis). Retrieval: LlamaIndex (hybrid vector+BM25, optional reranking),
   PageIndex ("reasoning retrieval with page-level citations"), GraphRAG, LightRAG.
7. **Assessment / evidence model.** `QuizGenerator` delegates to `QuestionPipeline` (RAG-backed
   LLM generation) and stores `{question, question_type, options, correct_answer, explanation,
   difficulty}` — the key is LLM output. Guided-learning blocks (diagnostic, pretest,
   retrieval_practice, error_diagnosis, module_test, progress_dashboard) exist as block types.
   Reader progress/quiz stats in a per-reader overlay.
8. **Strengths.** A clean, explicit lesson-document schema with per-block status and anchors;
   separation of shared book vs reader overlay; page-scoped chat context; resumable long builds;
   a vocabulary of guided-learning blocks that maps well onto SAM's `TeachingAct`s.
9. **Weaknesses (for SAM's problem).** (a) **Content is written by the model**, not extracted:
   `text.py`, `section.py`, `timeline.py`, `flash_cards.py` are `llm_json`/`_llm_writer` generators.
   (b) **Visual and quiz blocks return empty anchors**: `timeline.py` returns `({"events": …}, [],
   …)`; `quiz.py` returns `(…, [], …)`. (c) `SourceAnchor{kind, kb_name, ref, snippet ≤300 chars}`
   — no page/bbox; a snippet cannot fail closed. (d) The agent loop decides what to do; there is no
   pedagogy runtime that constrains the model. (e) Concept graph edges carry a free-text
   `rationale`, not a source citation.
10. **License.** Apache License 2.0 (`LICENSE`).
11. **Maturity.** README claims "20k stars in 111 days"; paper "DeepTutor: Towards Agentic
    Personalized Tutoring" (CITATION.cff; arXiv 2604.26962 surfaced in search); Python 3.11–3.14,
    FastAPI; Docker/Podman; multi-user permissions (`multi_user/book_permission.py`); tests for
    reader navigation/page chat.
12. **Applicability to SAM.**
    - *Use the shape, not the pipeline.* `Chapter → Page → Block{type, status, payload,
      source_anchors}` is a good template for the **Trusted Structured Lesson** (`12`), with two
      SAM-specific changes: anchors must be `book·page·blockId·bbox·ocrConf`, and `status` must
      include `untrusted` (fail-closed) rather than `hidden` (cosmetic).
    - *Per-reader overlay* mirrors SAM's shared-device multi-profile requirement
      (`docs/design/SHARED-DEVICE-MULTI-PROFILE-ARCHITECTURE.md`): lesson content is shared,
      TRACE/EVIDENCE per learner.
    - *Page Chat* is the closest analogue to «Hỏi SAM về đoạn này» — but in SAM the anchor narrows
      `LearningContext`; it does not open a free chat.
    - *Guided-learning block vocabulary* (diagnostic, retrieval practice, error diagnosis) maps to
      existing acts/signals (`diagnosticProbe`, `retrievalOpportunity`, `ErrorHypothesis`) — useful
      naming evidence that SAM's taxonomy is conventional.

## What NOT to copy

- LLM-authored prose/timeline/flashcard/quiz blocks (violates OCR TEXT ≠ TRUSTED SOURCE and
  RETRIEVED ≠ PERMITTED).
- Snippet-only anchors.
- "Regenerate block" as a learner-facing action on a trusted lesson.
- The agent loop as the pedagogy decision-maker.

## Does "Living Book" inform *Trusted Structured Lesson → multiple SAM Views*? (Founder question A)

Yes, on **structure and reader-state separation**; no, on **content origin and grounding**.
DeepTutor demonstrates that a typed-block document can feed a reader, a concept graph view, and
a chat — three views from one document — which is the Founder's thesis. It also demonstrates the
failure the Founder wants to avoid: when blocks are generated, the "one source of truth" is the
model's output, not the book.
