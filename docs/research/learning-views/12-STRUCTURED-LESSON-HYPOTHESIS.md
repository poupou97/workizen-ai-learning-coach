# 12 — Structured Lesson Contract · Hypothesis (Q4, Q5, Q6, §11)

**Status:** HYPOTHESIS — DO NOT IMPLEMENT. Corpus-dependent statements are tagged **PENDING
TRUSTED-CORPUS FINDINGS**; at the time of writing the Trusted Corpus Feasibility bundle did not
exist on the Desktop (checked 2026-09-05 00:0x). Its `11-STRUCTURED-DOCUMENT-MODEL.md` outranks
this file wherever they disagree — apply §6.

## 1. The question

What is the **minimum canonical data model** that lets ONE lesson power all three Views without
duplicating content and without letting any View hold a truth the others do not?

## 2. Candidate concepts — classification against SAM evidence and prior art

Scale: **RETAIN** (exists, keep) · **FORMALIZE** (exists implicitly, name it) · **EXTEND** (exists,
needs a field/scope) · **REJECT** (do not add now) · **HYPOTHESIS** (no evidence yet).

| Concept | Today in SAM (OBSERVED-IN-CODE / MEASURED) | Prior art | Class | Reason |
|---|---|---|---|---|
| **Book** | `BookRef{sourceDocumentId, subject, title, cover, volume, bookSeries?}` (`lesson_index.dart:229-269`) | DeepTutor `Book`; H5P `bookCover` | **RETAIN** | complete for Views; `bookSeries` still `null` (registry gap, not a model gap) |
| **Chapter** (Chủ đề/Chương) | `ContentNode(role ∈ BOOK/UNIT/THEME/WEEK/CHAPTER/TOPIC/LESSON/ACTIVITY)` in `tool/corpus/content_node.py` (WAL-173); **not** present in packs/`LessonIndex` (flat lesson list per book) | DeepTutor `Spine.chapters`; Mathigon `> section:` | **FORMALIZE** | board frame 2 groups lessons under Chủ đề; the corpus has the role; packs drop it — a pack field, no new extraction |
| **Lesson** | `LessonKey{sourceDocumentId, number, pageStart?}` (`slice_curriculum.dart:77-106`); `pageStart` missing for 2,033/7,626 records | Oppia exploration; H5P chapter | **RETAIN + EXTEND** with `boundary{pagePdfStart, pagePdfEnd, confidence, status}` | WAL-206 capped ranges at 2.5× median; the document must say how sure its own boundary is — PENDING TRUSTED-CORPUS FINDINGS (denominator re-derivation) |
| **ContentBlock · Heading / Paragraph / Question / Caption** | layout roles `heading · body · question · caption` with `id, order, regionPath, text, bbox, lines, ocrConf, trusted` (`poc-out/layout`, `layout_extract.py:231-244`) | DeepTutor `Block{type,status,payload,source_anchors}`; PreTeXt semantic elements | **FORMALIZE** | already typed with provenance; give them one name and one `trusted` semantics across tools and Dart |
| **ContentBlock · Activity** (Hoạt động, Em có biết?) | `sidebar` role (side boxes split from body, WAL-206 §2) + `LessonActivity` sealed objects (Exercise/Reading/Writing/Source/Experiment) | H5P Column blocks; Mathigon steps | **FORMALIZE** | two things share the word: the *book's* activity box (a block) and SAM's *learner activity* (an object). Keep both, name them `activityBox` (block) vs `LessonActivity` (object) |
| **ContentBlock · Quote / Source excerpt** | `SuSource{excerpt, attribution, samGloss?}` («TƯ LIỆU.» blocks, `build_lesson_index.py:83-140`) | Oppia none; H5P none | **FORMALIZE** as `sourceExcerpt` block with `attribution` required | verbatim + attribution already fail-closed (no attribution ⇒ dropped) |
| **ContentBlock · Image / Figure** | no role; `SourceAsset`/`IndexedSourceAsset` only by human curation (3 assets in every pack) | DeepTutor `figure` (generated); H5P `H5P.Image` | **HYPOTHESIS** | no extractor for figure regions on scanned pages — **PENDING TRUSTED-CORPUS FINDINGS**; until then a *page-region image* stands in |
| **ContentBlock · Table** | `layout.tableLike ⇒ page untrusted` | QTI/PreTeXt tables | **HYPOTHESIS** | fail-closed today by design; cell extraction feasibility — PENDING TRUSTED-CORPUS FINDINGS |
| **ContentBlock · Formula** | none (ADR-006 lists "formula index" as a target; Toán exercises are `expr` strings) | Mathigon `x-equation` | **HYPOTHESIS** | no detector; Toán 4–5 `CorpusExercise.expr` is the only formula-like data |
| **SemanticBinding** | proposed in `K12-CONVERGENCE-CENSUS.md` (WAL-200): `{activityRef, conceptId?, skillCaseId?, pedagogicalRole?, sourceSignal, confidence, provenance}` — **unbuilt**; 10 Toán lessons have an unvalidated `skillCaseId` string | Oppia `linked_skill_id`; DeepTutor `ConceptEdge` (LLM) | **HYPOTHESIS (retain the design)** | additive, zero-or-one, fail-closed — the only sanctioned bridge between Scale and Deep paths; Views must work with `bindings = []` |
| **Concept / SkillCase / Method** | `lib/core/curriculum/` — real types, 1 registered lesson, 14 concept nodes | Oppia `Skill`; KLI | **RETAIN** | do not mass-generate for Views (Census verdict FORMALIZE, not REPLACE) |
| **LearningObjective** | SGV «MỤC TIÊU» marker in 204/220 books; extractor built for Toán only (WAL-76) | DeepTutor `learning_objectives[]`; Oppia rubrics | **FORMALIZE + EXTEND (SGV only)** | objectives feed Mode 3 expectations (AutoTutor EMT) and the board's "Ghi nhớ" card — verbatim, never generated |
| **ProcessStep[]** | `KhoaExperiment.tienHanh: List<String>` verbatim + `chuanBi`, `duDoan?`, `quanSat?` | H5P none; DeepTutor none | **RETAIN → FORMALIZE** as generic `ProcessStep{order, text, sourceRef}` | proven Mode 2 shape (WAL-185); generalise the *type*, not the extractor |
| **HistoricalEvent[]** | none — Sử units are raw `SECTION_TEXT/ACTIVITY/NOTE` (VISUALIZER §4); stories pipeline has curated `story{year, monthDay, personId, sourceDocumentId, pagePdf}` (`sam-stories.db`) | H5P Timeline `date[]{startDate,endDate,headline,text,asset}` | **HYPOTHESIS — BLOCKED** | target shape = H5P Timeline model + `sourceRef`; only route today is the curated stories pattern |
| **ComparisonDimension[]** | none; tables untrusted | — | **HYPOTHESIS** | PENDING TRUSTED-CORPUS FINDINGS (tables) |
| **GeoEntity[]** | none; `DiaMap{asset, caption, questions, pagePdf, bboxFrac}` is asset-level | — | **REJECT (for now)** | MAP_SPATIAL is 15 lessons / 2 subjects; `DiaMap` already serves Mode 2 Spatial; a typed entity list has no source signal |
| **ConceptRelation[]** | `CurriculumEdge` (4 kinds, cross-lesson, provenance-gated; `citableAsDependency` only for `sourceStated`) | Oppia `prerequisite_skill_ids`; DeepTutor `ConceptEdge` | **RETAIN CurriculumEdge; HYPOTHESIS for intra-lesson relations** | a "mindmap of the lesson" needs relations that no extractor yields; `sourceSequence` must never be drawn as an arrow |
| **SourceRef** | three shapes coexist: `Provenance{sourceId, pageStart(printed)}`; layout block `{book, pagePdf, bbox[x,y,w,h]}`; `SourceAsset{sourceDocumentId, pagePdf, pagePrinted?, bboxFrac[x0,y0,x1,y1]}` | Caliper `DigitalResource` ids; DeepTutor `SourceAnchor` (snippet) | **FORMALIZE** into one `SourceRef{sourceDocumentId, pagePdf, pagePrinted?, blockId?, bbox?}` | MEASURED: **two bbox conventions** ([x,y,w,h] in layout vs [x0,y0,x1,y1] in assets) — a silent-error risk for «xem vùng trang» |
| **Page** | `pagePdf` vs printed page distinguished everywhere (`provenance.dart:71-75` warns) | — | **RETAIN** | keep both numbers, always |
| **BBox** | present in layout and assets (two conventions) | — | **FORMALIZE** (one convention, fractions of page) | see SourceRef |
| **Provenance** | `KnowledgeOrigin` (5) + `Provenance{extractionMethod, confidence, …}` with `citableAsTextbookFact` / `citableAsDependency` | — | **RETAIN + EXTEND** with block-level `trusted: bool` and `layoutVersion` | the block's `trusted` is a *pipeline* fact, provenance `origin` is a *knowledge* fact — keep separate |
| **Confidence** | three different numbers: block `ocrConf`, page `layout.confidence`, `Provenance.confidence` | — | **FORMALIZE** — define which one a View may surface (only block trust + a coarse glyph for the child; numbers for parents/Source screen) | Convergence §2: no % to the child |

## 3. Minimum contract (HYPOTHESIS — shape only, no schema)

```
TrustedLessonDocument                         ← ONE per LessonKey, built at pack-build time
  lessonKey        {sourceDocumentId, number, pageStart?}
  chapter?         {role: THEME|CHAPTER|UNIT, title}                (FORMALIZE)
  boundary         {pagePdfStart, pagePdfEnd, confidence, status: OK|CAPPED|UNKNOWN}
  pages[]          {pagePdf, pagePrinted?, imageRef, layoutTrusted, tableLike}
  blocks[]         {id, order, role: heading|body|question|caption|sidebar|sourceExcerpt|footnote,
                    text, sourceRef, ocrConf, trusted}
  activities[]     LessonActivity (existing sealed types; keys NOT here)
  typedData        {processSteps?[], mapAssets?[], objectives?[] /*verbatim*/,
                    events?[] /*BLOCKED*/, relations?[] /*BLOCKED*/, comparisons?[] /*PENDING*/}
  bindings[]       SemanticBinding (optional, zero-or-one per activity)
  version          {knowledgeVersion, layoutVersion, packVersion}
```

Invariants (the ones that make "one truth" real):

1. **Learner projection carries no keys.** Answer keys (SGV) live in a separate, key-only structure
   joined at Surface time — the Scaffold rule and QTI's item/response-processing split; SAM already
   does this for `TvQuestion` (no answer field).
2. **Every block and every typed datum has a `sourceRef`; a View may not render anything without one.**
3. **`trusted=false` blocks are never rendered as text**; they render as page-region images or are
   omitted with an explicit line.
4. **Views are pure functions of the document + learner state.** No View may fetch content outside
   the document (Mode 3 `DerivedFacts` are derived from it).
5. **Bindings are optional.** With `bindings=[]`, Mode 1 and Mode 2 work fully; Mode 3 falls back to
   Surface-level policies (`reader-v1`, `experiment-v1`).
6. **Version pins.** Evidence written under a document carries `knowledgeVersion` (existing) and
   should carry `layoutVersion` (new) — replay safety already proven for pack updates (WAL-85).

## 4. What is common vs View-specific (Q4, Q5, Q6)

| Shared by all three Views | Mode 1 only | Mode 2 only | Mode 3 only |
|---|---|---|---|
| `lessonKey`, `chapter`, `boundary`, `pages` (image refs), `blocks` with `sourceRef`/`trusted`, `version`, provenance wording rule (`sourceLineForChildOf`) | reading order, page rasters, per-block display trust, bookmarks/annotations (per learner, TRACE) | `typedData` (shape-dispatched), representation explanation (WAL-185), interaction claims | `activities`, `bindings`, blueprint/`PlannedAct` sequence, SGV keys (separate join), learner state (BKT/ConceptSummary), Surfaces |

**Q4 — can all three consume one canonical lesson?** Yes for Mode 1 and Mode 2 by construction;
Mode 3 consumes it *plus* two things that must stay outside it (keys, learner state). "One lesson"
is therefore one *document* plus two side-joins — not one blob.

## 5. What this contract does NOT do

- It does not merge the Deep and Scale paths (Review §9 open hypothesis #5 stays open).
- It does not add a graph database, a generic renderer, or LLM-generated fields.
- It does not promise Image/Table/Formula blocks.
- It is not a schema; field names are illustrative.

## 6. Reconciliation checklist — apply when the Trusted Corpus Feasibility bundle lands

Read its `01-FOUNDER-REPORT.md`, `11-STRUCTURED-DOCUMENT-MODEL.md`, `18-PRODUCT-FEASIBILITY-VERDICT.md`, then:

- [ ] Replace the `blocks[].role` list in §3 with the study's block model if it differs; keep
      `trusted`/`sourceRef` semantics or adopt the study's equivalents.
- [ ] Re-classify **Image/Figure**, **Table**, **Formula** rows in §2 (HYPOTHESIS → EXTEND or REJECT)
      per the study's feasibility verdict.
- [ ] Update `boundary` semantics and the 3,679 denominator per the study's lesson-boundary findings.
- [ ] Adopt the study's confidence definitions (§2 "Confidence") and its bbox convention.
- [ ] If the study proposes a structured document *format* (JSON/SQLite), map §3 onto it rather than
      keeping a second shape.
- [ ] If the study falsifies native text reconstruction for any subject family, mark Mode 1 for that
      family as "page image only" in `18`.
- [ ] Re-check `typedData` candidates (ProcessStep beyond experiments, objectives, comparisons)
      against what the study says can be extracted deterministically.
