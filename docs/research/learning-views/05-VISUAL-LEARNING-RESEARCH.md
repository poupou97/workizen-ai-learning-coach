# 05 — Mode 2 · Visual Learning / Trực quan hóa — Research

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
data shape**, not a feature to schedule.

## 2. Renderer family × data shape × corpus readiness (Q3, Q11, Q12)

| Renderer (Founder list) | Typed input it needs | Exists in SAM today? | Corpus signal | Deterministic? | Verdict |
|---|---|---|---|---|---|
| **Process / Flow** | `ProcessStep[]` ordered, verbatim | **YES** — `KhoaExperiment.tienHanh[]` (`lesson_index.dart:104-129`) | EXPERIMENT pattern 65 lessons (37 proven) | Yes | **PROVEN narrow** (WAL-185) |
| **Map / Spatial** | image asset + bbox + questions | **YES** — `DiaMap` (`:133-156`), `SourceAsset` | MAP_SPATIAL 15 lessons; 1 curated map | Yes | **PROVEN narrow** (WAL-185) |
| **Timeline** | `HistoricalEvent[]{date, title, text, sourceRef}` | **NO** — Sử units are `SECTION_TEXT/ACTIVITY/NOTE` raw text, "no date/event field" (VISUALIZER §4) | SOURCE_REASONING 42; Sử 4–5 books present | Only if extracted with provenance | **HYPOTHESIS — BLOCKED** on extraction (ADR-009 gate) |
| **Concept Map / Mindmap** | `ConceptRelation[]{a, relation, b, sourceRef}` | **NO** — `CurriculumEdge` has 4 kinds, 14 concept nodes, 1 prerequisite edge | glossary parse exists (`extractionMethod: glossary-parse` in `provenance.dart`) — untested for relations | Only from typed edges | **HYPOTHESIS — BLOCKED**; reject "generic mindmap of the lesson" |
| **Cause–Effect** | `CausalLink[]` | NO | none measured | — | HYPOTHESIS |
| **Comparison** | `ComparisonDimension[]` (entities × dimensions) | NO — but COMPARE directives exist (123 lessons) | Tables in SGK are the natural source and are `tableLike ⇒ untrusted` | Yes if table cells extracted | **HYPOTHESIS — depends on table extraction (PENDING TRUSTED-CORPUS FINDINGS)** |
| **Classification Tree** | `Taxon[]` parent/child | NO | CLASSIFY_SORT 110 lessons | Yes | HYPOTHESIS |
| **System Diagram** | nodes + typed links + figure | NO | figure-dependent (17 refused prompts in WAL-206) | Partly (needs figure) | HYPOTHESIS |
| **Data / Chart** | table/series | NO | DATA_CHART 23 lessons | Yes | HYPOTHESIS — table extraction |
| **Flashcard-like summary** | `Concept{term, definition, sourceRef}` | Partial — glossary parse; `KnowledgeChunk.contentType: definition` | — | Yes | HYPOTHESIS — cheapest next after Process/Spatial if glossary units are trusted |

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

Conclusion for Q12: **deterministic for structure and facts; AI at most for optional commentary,
never for nodes/edges/dates.** Caching follows for free (a renderer over static typed data is a
pure function of pack version). Checkability: a Mode 2 artifact can be diffed against the lesson
document at build time.

## 4. Where the typed data would come from (HYPOTHESIS, PENDING TRUSTED-CORPUS FINDINGS)

| Typed shape | Candidate deterministic extractor | Risk |
|---|---|---|
| `ProcessStep[]` beyond experiments | numbered/“Bước” lists in `body` blocks; TOC-attached | list detection on OCR lines; already done for Chuẩn bị/Tiến hành |
| `Concept{term, definition}` | glossary boxes / bold-term + definition sentence in trusted blocks | needs bold detection (Vision gives no font weight) — likely blocked |
| `HistoricalEvent[]` | year/date regex on Sử trusted blocks + sentence | low precision without human curation; "Ngày này năm xưa" stories pipeline (§28 VERIFIED gate) is the existing precedent for *curated* events |
| `ComparisonDimension[]` | table cells | tableLike ⇒ untrusted today |
| `GeoEntity[]` | curated map assets only | human curation (WAL-133) |

The honest scaling path for Mode 2 is the **stories pipeline pattern** (build-time deterministic
extraction → gold-set → VERIFIED status → runtime re-check), not runtime generation.

## 5. Learning-science grounding (Q11 — "genuinely useful by subject")

- **Concept/knowledge maps** (FROM-REFERENCE — Nesbit & Adesope 2006, *Review of Educational
  Research* 76(3), 55 studies, 5,818 participants): using concept maps is associated with increased
  knowledge retention, effect sizes small to large depending on whether learners *construct*
  or *view* maps and on the comparison treatment. **Decision it changes:** a *viewed* map is a
  representation (TRACE); a *constructed/completed* map is an activity (evidence). Mode 2 should
  offer "hoàn thành sơ đồ" interactions where a typed structure exists, not only display.
- **Multimedia principles** (well-established: coherence, signalling, spatial contiguity — not
  re-fetched here) support captions adjacent to figures and removing decorative content — i.e.
  Mode 1 should keep the book's own figure–caption pairing rather than add illustration.
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

## 8. Answers

- **Q3 — one renderer or a family?** A family, dispatched by *data shape* not by subject; two
  members exist; add the third only when a third typed shape is extracted (VISUALIZER §9 trigger).
- **Q10 — source-grounded?** Every node/edge/date carries `sourceRef{book, page, blockId}`;
  renderers refuse untyped input; visuals are built at pack-build time and diffed against the
  lesson document; SAM's commentary is guarded and cites only through `sourceLineForChildOf`.
- **Q11 / Q12** — see §2, §3, §5.
