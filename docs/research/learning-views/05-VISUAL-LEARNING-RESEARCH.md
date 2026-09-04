# 05 — Mode 2 · Visual Learning / Trực quan hóa — Research

> **Reconciled with TC-v1 (2026-09-05).** `TC-nn` = `docs/research/trusted-corpus/nn-….md`. Changes: §2 table rows Map · Timeline · Comparison · System Diagram · Data/Chart + a counts caveat; §4 (was "PENDING", now per-row measured / still unmeasured); §8 Q10 relation vocabulary.

**Founder hypothesis (§4):** no LLM "composing a mindmap" each time; instead Trusted Semantic
Content → Typed relationships → Visual Renderer (HistoricalEvent[] → Timeline; ConceptRelation[]
→ Concept Map; ProcessStep[] → Process; ComparisonDimension[] → Comparison; GeoEntity[] → Map) —
deterministic, source-grounded, cacheable, checkable, cheaper, hallucination-resistant.

## 1. Verdict in one paragraph

The hypothesis is **correct and already partially proven in SAM**, and the reference repositories
*strengthen* it by counter-example: the systems that generate visuals with an LLM (DeepTutor
`timeline.py`/`concept_graph.py`, OpenMAIC interactive HTML widgets) return **no source anchors**
for those blocks. The binding constraint is not rendering — it is that **typed relationships do
not exist in the corpus** for most subjects. Mode 2 is therefore a **renderer family gated by
data shape**, not a feature to schedule. TC-v1 measured the gate: the only relations a layout
parser yields today are structural (`caption_of`, `options_of`, `heading_path`); everything
semantic needs the unbuilt role layer (TC-07, TC-11 §2).

## 2. Renderer family × data shape × corpus readiness (Q3, Q11, Q12)

| Renderer (Founder list) | Typed input it needs | Exists in SAM today? | Corpus signal | Deterministic? | Verdict |
|---|---|---|---|---|---|
| **Process / Flow** | `ProcessStep[]` ordered, verbatim | **YES** — `KhoaExperiment.tienHanh[]` (`lesson_index.dart:104-129`) | EXPERIMENT pattern 65 lessons (37 proven) | Yes | **PROVEN narrow** (WAL-185) |
| **Map / Spatial** | image asset + bbox + questions | **YES** — `DiaMap` (`:133-156`), `SourceAsset` | MAP_SPATIAL 15 lessons; 1 curated map. TC-v1: a full map page carries ~60 labels (LS&ĐL 5 p80, TC-04) and is FIGURE + labels only, never prose (TC-10) — confirms the curated-asset route | Yes | **PROVEN narrow** (WAL-185) |
| **Timeline** | `HistoricalEvent[]{date, title, text, sourceRef}` | **NO** — Sử units are `SECTION_TEXT/ACTIVITY/NOTE` raw text, "no date/event field" (VISUALIZER §4) | SOURCE_REASONING 42; Sử 4–5 books present. TC-v1: every parser reads a timeline's top row of boxes then the bottom row — a wrong chronology (LS&ĐL 8 p71, TC-06, TC-09 #3); timeline pages must stay FIGURE-only (TC-10) | Only if extracted with provenance | **HYPOTHESIS — BLOCKED** on extraction (ADR-009 gate); blocked *harder* after TC-v1 |
| **Concept Map / Mindmap** | `ConceptRelation[]{a, relation, b, sourceRef}` | **NO** — `CurriculumEdge` has 4 kinds, 14 concept nodes, 1 prerequisite edge | glossary parse exists (`extractionMethod: glossary-parse` in `provenance.dart`) — untested for relations | Only from typed edges | **HYPOTHESIS — BLOCKED**; reject "generic mindmap of the lesson" |
| **Cause–Effect** | `CausalLink[]` | NO | none measured | — | HYPOTHESIS |
| **Comparison** | `ComparisonDimension[]` (entities × dimensions) | NO — but COMPARE directives exist (123 lessons) | Tables in SGK are the natural source and are `tableLike ⇒ untrusted`. TC-v1: table objects only from Marker (1.00 / 1.00, GPU class); Docling finds half and flattens cells (TC-07, TC-14) | Yes if table cells extracted | **HYPOTHESIS — BLOCKED on the GPU table path** (MEASURED, TC-07) |
| **Classification Tree** | `Taxon[]` parent/child | NO | CLASSIFY_SORT 110 lessons | Yes | HYPOTHESIS |
| **System Diagram** | nodes + typed links + figure | NO | figure-dependent (17 refused prompts in WAL-206). TC-v1: the SDM `refers_figure` relation + figure-dependence guard make such questions *identifiable* and withholdable (TC-10, TC-15) | Partly (needs figure) | HYPOTHESIS |
| **Data / Chart** | table/series | NO | DATA_CHART 23 lessons. TC-v1: needs table objects (GPU path) or stays an image | Yes | HYPOTHESIS — BLOCKED on the GPU table path |
| **Flashcard-like summary** | `Concept{term, definition, sourceRef}` | Partial — glossary parse; `KnowledgeChunk.contentType: definition` | — | Yes | HYPOTHESIS — cheapest next after Process/Spatial if glossary units are trusted |

**Counts caveat (TC-15, TC-17 #13):** the registry counts in this table (65 · 15 · 42 · 123 ·
110 · 23) were produced by the old extractor; on identical pilot pages the new source yields 4×
the directive units (49 → 199), and 23 of the XY-cut's 100 gold "questions" were non-questions.
The counts rank shapes; they do not size them. Recompute on a role-labelled SDM before any is used
as a target.

Reading rule from the table: **two renderers are real, eight need an extractor that does not
exist.** The Founder's subject mapping (History → Timeline, Geography → Map, Science → Process,
Biology → Classification, concept-heavy → Concept map) is a sound *target*, and SAM should
**not** ship a renderer until its typed input has ≥1 corpus-extracted, provenance-bearing
instance validated on device — the same rule that produced WAL-185.

## 3. Deterministic vs AI-generated (Q12) — the trust argument, with reference evidence

- **FROM-REFERENCE, DeepTutor** `deeptutor/book/blocks/timeline.py:22-61`: events come from
  `llm_json(user_prompt=chapter_title+chapter_summary …)`; the generator returns `([], …)` for
  `source_anchors`. `quiz.py:74-77` likewise returns `[]` anchors; `correct_answer` is LLM output.
  `models.py:216-224` `SourceAnchor{kind, kb_name, ref, snippet≤300}` — a text snippet, no page/
  bbox. So the most popular "living book" produces *unanchored* timelines and quizzes.
- **FROM-REFERENCE, OpenMAIC** `packages/@openmaic/dsl/src/interactive.ts`: interactive content is
  `{type:'interactive', html?: string (iframe srcDoc), widgetType?: simulation|diagram|code|game|
  visualization3d|procedural-skill}` — the diagram *is* generated HTML; there is no typed data
  model for the diagram's facts.
- **OBSERVED-IN-CODE, Hub Output Engine** (per `SAM-LEARNING-VISUALIZER-RESEARCH.md` §3): typed
  `MindmapBody{root, branches: MindNode{label, children, cite}}` + `OutputCitation{docId, page}`
  chips parsed only from engine-verified page markers — retrieval-before-generate, one LLM call to
  a fixed JSON contract. This is the *least bad* generative pattern and still an LLM composing
  structure per request.
- **SAM's rule** (`realization_contract.dart:32-56`): anything computable from the lesson is
  `RealizationPolicy.deterministic`; retrieval-based for concept explanation; generative only
  guarded. Applied to visuals: **structure = deterministic from typed data; wording of node labels
  = verbatim or template; SAM's commentary on the visual = generative-guarded at most.**
- **TC-v1 (Founder order H, TC-10; TC-11 §6):** neither an LLM/VLM nor any single parser is source
  truth; a 3B VLM prompted for structure ignored the format on 20 of 22 pages and 3-way voting
  with it *lowered* trust (TC-10 reading 3) — the corpus side reaches the same conclusion.

Conclusion for Q12: **deterministic for structure and facts; AI at most for optional commentary,
never for nodes/edges/dates.** Caching follows for free (a renderer over static typed data is a
pure function of pack version). Checkability: a Mode 2 artifact can be diffed against the lesson
document at build time.

## 4. Where the typed data would come from (HYPOTHESIS — reconciled with TC-v1)

| Typed shape | Candidate deterministic extractor | Risk — after TC-v1 |
|---|---|---|
| `ProcessStep[]` beyond experiments | numbered/“Bước” lists in `body` blocks; TOC-attached | MEASURED risk: Docling **drops list enumerators** ("1.", "a)", "HĐ1") on 65 gold blocks (TC-09); the XY-cut and Marker keep them; an enumerator-preservation guard (restore from OCR lines) is required before numbered steps can be typed (TC-19 #4). Procedure lists with photo labels come out as separate short blocks in Docling (TC-06). |
| `Concept{term, definition}` | glossary boxes / bold-term + definition sentence in trusted blocks | **STILL UNMEASURED after TC-v1:** the role layer is specified as geometry + typography "where available" + lexicon (TC-07 §Consequence), but no candidate's font-weight signal was scored. Closing measurement: bold detection from the page raster on the 38 gold pages against the gold's glossary/definition blocks. |
| `HistoricalEvent[]` | year/date regex on Sử trusted blocks + sentence | MEASURED: timeline pages fail every parser (TC-06); "Ngày này năm xưa" curated stories pipeline (§28 VERIFIED gate) remains the only route. |
| `ComparisonDimension[]` | table cells | MEASURED: table objects from Marker only (GPU); the Mac path flattens cells (TC-07, TC-14). |
| `GeoEntity[]` | curated map assets only | unchanged — human curation (WAL-133); TC-10: maps are FIGURE + labels. |

The honest scaling path for Mode 2 is the **stories pipeline pattern** (build-time deterministic
extraction → gold-set → VERIFIED status → runtime re-check), not runtime generation. TC-v1's own
gold + gate + review-queue design (TC-10, TC-19 #9) is the same pattern at block level.

## 5. Learning-science grounding (Q11 — "genuinely useful by subject")

- **Concept/knowledge maps** (FROM-REFERENCE — Nesbit & Adesope 2006, *Review of Educational
  Research* 76(3), 55 studies, 5,818 participants): using concept maps is associated with increased
  knowledge retention, effect sizes small to large depending on whether learners *construct*
  or *view* maps and on the comparison treatment. **Decision it changes:** a *viewed* map is a
  representation (TRACE); a *constructed/completed* map is an activity (evidence). Mode 2 should
  offer "hoàn thành sơ đồ" interactions where a typed structure exists, not only display.
- **Multimedia principles** (well-established: coherence, signalling, spatial contiguity — not
  re-fetched here) support captions adjacent to figures and removing decorative content — i.e.
  Mode 1 should keep the book's own figure–caption pairing rather than add illustration. TC-07
  shows that pairing is extractable (`caption_of` 0.90–0.95).
- **Timeline for history**: no fetched meta-analysis in this track; treat as HYPOTHESIS with face
  validity. The registry shows SOURCE_REASONING (42) and OBSERVE dominate Sử, not chronology
  exercises — so Timeline may be less central for Sử 4–5 than the board assumes.

## 6. Interaction on visuals → evidence (Q14)

Precedent (`SAM-LEARNING-VISUALIZER-RESEARCH.md` §6): viewing a Process/Map is TRACE; a real
interaction (order the steps, fill the missing node, place the label) mints `CandidateEvidence`
through `validateCandidateEvidence` — `correct` stays `null` unless a deterministic key exists
(e.g. step order *is* known verbatim ⇒ ordering can be graded deterministically; this would be the
first gradable non-Toán activity and deserves its own falsification slice).

## 7. Anti-patterns (what NOT to copy)

- LLM-composed mindmap/timeline per open (DeepTutor timeline, OpenMAIC diagram HTML).
- A generic graph-layout engine before three real shapes exist (VISUALIZER §7: no generic renderer
  in the Hub either; adding a kind = new typed body + widget).
- Hand-drawn concept maps per lesson as content (H5P-style authoring at 3,679-lesson scale).
- Presenting `sourceSequence` (TOC order) as a causal/prerequisite arrow (`provenance.dart:89-96`).
- Reading a diagram's labels as prose or a timeline's boxes in y-order (TC-09 #3, TC-06).

## 8. Answers

- **Q3 — one renderer or a family?** A family, dispatched by *data shape* not by subject; two
  members exist; add the third only when a third typed shape is extracted (VISUALIZER §9 trigger).
- **Q10 — source-grounded?** Every node/edge/date carries `sourceRef{book, page, blockId}`;
  renderers refuse untyped input; visuals are built at pack-build time and diffed against the
  lesson document; SAM's commentary is guarded and cites only through `sourceLineForChildOf`.
  TC-11 §2 supplies the relation vocabulary a renderer may consume: `caption_of`, `options_of`,
  `answer_of`, `refers_figure`, `continues`, `part_of_box` — structural, provenance-bearing, and
  gated like text.
- **Q11 / Q12** — see §2, §3, §5.
