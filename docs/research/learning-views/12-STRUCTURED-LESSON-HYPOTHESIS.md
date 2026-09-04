# 12 — Structured Lesson Contract · Hypothesis (Q4, Q5, Q6, §11)

> **Reconciled with TC-v1 (2026-09-05).** `TC-nn` = `docs/research/trusted-corpus/nn-….md` (WAL-208). §3 is now mapped onto TC-11's Structured Document Model (SDM); §2 classes changed where the evidence forced it (marked **↯**); §6 is the applied checklist.

**Status:** HYPOTHESIS — DO NOT IMPLEMENT. Corpus-dependent statements were tagged PENDING
TRUSTED-CORPUS FINDINGS at writing (2026-09-05 00:0x, no bundle on the Desktop); they now carry the
MEASURED finding or **STILL UNMEASURED after TC-v1**. `TC-11` outranks this file wherever they
disagree; §3 is a *lesson-scoped projection* of the SDM, not a second model.

## 1. The question

What is the **minimum canonical data model** that lets ONE lesson power all three Views without
duplicating content and without letting any View hold a truth the others do not?

## 2. Candidate concepts — classification against SAM evidence, prior art and TC-v1

Scale: **RETAIN** (exists, keep) · **FORMALIZE** (exists implicitly, name it) · **EXTEND** (exists,
needs a field/scope) · **REJECT** (do not add now) · **HYPOTHESIS** (no evidence yet). **↯** = class
changed by TC-v1 (summary in `18` §3a).

| Concept | Today in SAM (OBSERVED-IN-CODE / MEASURED) | Prior art | Class | Reason (TC-v1 citations where measured) |
|---|---|---|---|---|
| **Book** | `BookRef{sourceDocumentId, subject, title, cover, volume, bookSeries?}` (`lesson_index.dart:229-269`) | DeepTutor `Book`; H5P `bookCover` | **RETAIN** | complete for Views; `bookSeries` still `null` (registry gap). SDM `SourceDocument` adds `pdf sha256, scan_ppi` (TC-11 §2) — pack fields, no extraction |
| **Chapter** (Chủ đề/Chương) | `ContentNode(role ∈ BOOK/UNIT/THEME/WEEK/CHAPTER/TOPIC/LESSON/ACTIVITY)` (WAL-173); **not** in packs | DeepTutor `Spine.chapters`; Mathigon `> section:` | **FORMALIZE** | board frame 2 groups lessons under Chủ đề; the corpus has the role; packs drop it. SDM carries it per block as `heading_path` (TC-11 §2) |
| **Lesson** ↯ | `LessonKey{sourceDocumentId, number, pageStart?}` (`slice_curriculum.dart:77-106`); `pageStart` missing for 2,033/7,626 records | Oppia exploration; H5P chapter | **RETAIN + EXTEND** — `boundary` becomes per-block `lesson{number, title, attach_method: header\|toc_range\|continuation, confidence}` + `continues` (TC-11 §2); the page range is *derived* | MEASURED: 3,381 of 3,679 SGK lessons have a page range (TC-03 §5); TOC-range attachment is wrong on 10/38 hard gold pages (4 non-lesson pages, missing TOC entries, PARTIAL TOCs, two lessons on one page); header-based attachment fixes 6 of the 10 (TC-02 §5, TC-14 §2); 25.8 % of pages continue from the previous page (TC-03 §2). Denominator for sourceability shares = 3,381; canonical count stays 3,679 (`17` §5 C1) |
| **ContentBlock · Heading / Paragraph / Caption** | layout roles `heading · body · caption` with `id, order, regionPath, text, bbox, lines, ocrConf, trusted` (`layout_extract.py:231-244`) | DeepTutor `Block{type,status,payload,source_anchors}`; PreTeXt | **FORMALIZE** onto SDM HEADING · BODY · CAPTION | MEASURED on 38 hard pages: heading precision 0.81–0.89, caption 0.85–0.95, body fidelity 0.847 (XY-cut) → 0.975 (Docling) (TC-05, TC-07). One `trust` semantics = SDM tri-state (Confidence row) |
| **ContentBlock · Question** ↯ | `question` role (XY-cut) with Q1–Q8 gate | Oppia state; QTI item | **HYPOTHESIS (was FORMALIZE)** — keep the slot, withhold the label | MEASURED: the only labeller has precision 0.69 / recall 0.79; 11 headings + 23 non-questions emitted as questions; no layout parser has a QUESTION concept (TC-07). A role layer with its own confidence and a `role_conflict` gate must measure ≥ 0.95 before a QUESTION block is used as a prompt (TC-07 §Consequence, TC-19 #3) |
| **ContentBlock · Activity** (Hoạt động, Em có biết?) ↯ | `sidebar` role + `LessonActivity` sealed objects | H5P Column blocks; Mathigon steps | **FORMALIZE the block boundary; HYPOTHESIS for its label** | MEASURED: XY-cut sidebar 0.45 / 0.43; Docling separates side boxes (splices 17 → 6) but labels them `text` (TC-07, TC-05 §2). SDM roles SIDEBAR · ACTIVITY · RULE · OBJECTIVE exist (TC-11 §2); assigning them is the unbuilt role layer. Keep `activityBox` (block) vs `LessonActivity` (object) |
| **ContentBlock · Quote / Source excerpt** | `SuSource{excerpt, attribution, samGloss?}` (`build_lesson_index.py:83-140`) | — | **FORMALIZE** as `sourceExcerpt` + SDM ATTRIBUTION role, `part_of_box` relation | verbatim + attribution already fail-closed; TC-09: "attribution detached" 0–2 events per candidate — low risk |
| **ContentBlock · Image / Figure** ↯ | no role; `SourceAsset` only by human curation (3 assets) | DeepTutor `figure` (generated); H5P `H5P.Image` | **EXTEND (was HYPOTHESIS)** — as SDM `Figure{bbox, kind: photo\|drawing\|diagram\|map\|chart, labels[], caption → Block}` rendered as a **page-region image**, never as text | MEASURED: page-level figure presence on all 62,729 pages (37.4 % figure, 19.0 % diagram, TC-03 §2); `caption_of` 0.90 / 0.79 (Docling), 0.95 / 1.00 (Marker) (TC-07); layout parsers return picture bboxes natively (TC-11 §3). Figure bbox precision **STILL UNMEASURED after TC-v1** (gold scores text blocks, TC-04). Diagram/timeline/map labels must never be prose (TC-09) |
| **ContentBlock · Table** ↯ | `layout.tableLike ⇒ page untrusted` | QTI/PreTeXt tables | **EXTEND — GPU path only; REJECT as text on the Mac path** — SDM `Table{bbox, cells[row][col] with spans, header rows, "?" answer slots}` | MEASURED: Marker TABLE 1.00 / 1.00 as objects (129 s/page here; GPU needed); Docling 1.00 / 0.47 with cells flattened to one string; tables FTR 0.19 under the Mac cascade (TC-07, TC-14, TC-05 §3). Until a table-capable path runs, a table is an image region |
| **ContentBlock · Formula** ↯ | none (ADR-006 "formula index" target; Toán `expr` strings) | Mathigon `x-equation` | **REJECT as a text block (was HYPOTHESIS)**; RETAIN the SDM FORMULA role only as a *withholding trigger* (math guard) | MEASURED: every OCR stack flattens notation identically ("1 5 + 1 2 = 7 10"); only Marker labels FORMULA (0.81 / 1.00); formula pages TLSR 0.55 / FTR 0.17; shared-mode errors are invisible to agreement (TC-07, TC-08 §3–4, TC-09 #4). Image-first until a formula-capable path is measured (TC-19 #7) |
| **SemanticBinding** | proposed in `K12-CONVERGENCE-CENSUS.md` (WAL-200) — **unbuilt** | Oppia `linked_skill_id` | **HYPOTHESIS (retain the design)** | additive, zero-or-one, fail-closed; Views must work with `bindings = []`. Not in TC-v1's scope |
| **Concept / SkillCase / Method** | `lib/core/curriculum/` — 1 registered lesson, 14 concept nodes | Oppia `Skill`; KLI | **RETAIN** | do not mass-generate for Views |
| **LearningObjective** | SGV «MỤC TIÊU» marker in 204/220 books; extractor Toán only (WAL-76) | DeepTutor `learning_objectives[]`; Oppia rubrics | **FORMALIZE + EXTEND (SGV only)** | objectives feed Mode 3 expectations — verbatim, never generated. TC-v1: objectives are a class the XY-cut emits *as questions* ("1. Chọn được nấm…", TC-09 #6); SDM OBJECTIVE role + "… được" lexicon is the defence (TC-19 #3) |
| **ProcessStep[]** | `KhoaExperiment.tienHanh: List<String>` verbatim | — | **RETAIN → FORMALIZE** as `ProcessStep{order, text, sourceRef}` | proven shape (WAL-185). TC-v1 caveat: Docling drops enumerators on 65 gold blocks — enumerator preservation from OCR lines is a required guard before numbered steps outside experiments are typed (TC-09, TC-19 #4) |
| **HistoricalEvent[]** | none; curated `story{…}` in `sam-stories.db` | H5P Timeline | **HYPOTHESIS — BLOCKED** | TC-v1: every parser reads timeline boxes top row then bottom row (TC-06); timeline pages stay FIGURE-only (TC-10). Curated stories pattern is the only route |
| **ComparisonDimension[]** | none; tables untrusted | — | **HYPOTHESIS — BLOCKED on the GPU table path** | MEASURED: table objects from Marker only (TC-07) |
| **GeoEntity[]** | none; `DiaMap` is asset-level | — | **REJECT (for now)** | unchanged; TC-10: maps are FIGURE + labels |
| **ConceptRelation[]** | `CurriculumEdge` (4 kinds, provenance-gated) | Oppia `prerequisite_skill_ids` | **RETAIN CurriculumEdge; HYPOTHESIS for intra-lesson relations** | TC-11 relations are structural (`caption_of`, `options_of`, `answer_of`, `refers_figure`, `continues`, `part_of_box`), not semantic; `sourceSequence` must never be drawn as an arrow |
| **SourceRef** ↯ | three shapes coexist (`Provenance`, layout block, `SourceAsset`) | Caliper ids; DeepTutor snippet anchor | **FORMALIZE onto SDM** `{sourceDocumentId, pdf_page, printed_page, blockId = <doc>:p<NNN>:<parser>:<n>, bbox [x, y, w, h] normalised}` | TC-11 §2 fixes the bbox convention to `[x, y, w, h]` normalised to the page (never optional) — the layout convention wins; `SourceAsset.bboxFrac [x0,y0,x1,y1]` converts once |
| **Page** | `pagePdf` vs printed page distinguished everywhere | — | **RETAIN + EXTEND** with SDM `layout_features[]` (census flags) and `render sha256` | the page-feature guard (formula / diagram / map / timeline / colour-heavy → FIGURE only) reads `layout_features` (TC-10, TC-18 Q16); the census already computes them for every page (TC-03) |
| **BBox** | two conventions | — | **FORMALIZE** — `[x, y, w, h]` fractions of page (TC-11 §2) | see SourceRef |
| **Provenance** ↯ | `KnowledgeOrigin` (5) + `Provenance{extractionMethod, confidence, …}` | — | **RETAIN + EXTEND** with SDM `provenance{extraction_method, ocr_conf, model versions, run id}` and `trust{status, reasons[], verifier agreements[]}` | `layoutVersion` becomes `provenance.extraction_method` + run id (pipeline id in every block, TC-12). Pipeline fact (`trust`) and knowledge fact (`origin`) stay separate |
| **Confidence** ↯ | three numbers: block `ocrConf`, page `layout.confidence`, `Provenance.confidence` | — | **FORMALIZE onto SDM**: `trust.status ∈ {TRUSTED, WITHHELD, CONFLICT}` + `trust.reasons[]` (gate rule ids) + a **separate role confidence** + `provenance.ocr_conf` | a block may be TRUSTED for text and WITHHELD for role (`role_conflict`, TC-10); the child sees only a coarse glyph (Convergence §2); numbers go to parents/Source screen |

## 3. Minimum contract (HYPOTHESIS — shape only; a projection of TC-11's SDM)

```
TrustedLessonDocument                         ← ONE per LessonKey; a PROJECTION of the SDM's
                                                TrustedLearningSource (TC-11 §2), built at pack-build time
  lessonKey        {sourceDocumentId, number, pageStart?}
  chapter?         {role: THEME|CHAPTER|UNIT, title}               (FORMALIZE; from SDM heading_path)
  lesson           {attach_method: header|toc_range|continuation, confidence}   (TC-11; worst of its blocks)
  boundary         {pagePdfStart, pagePdfEnd}   — DERIVED from block attachment, never the other way round
  pages[]          {pdf_page, printed_page, imageRef, render_sha256, layout_features[] /*census flags*/}
  blocks[]         {id /*<doc>:p<NNN>:<parser>:<n>*/, order, column?, heading_path[],
                    role: HEADING|BODY|QUESTION|OPTION|ANSWER|CAPTION|SIDEBAR|TABLE|FORMULA|FIGURE|
                          FIGURE_TEXT|FOOTNOTE|ATTRIBUTION|OBJECTIVE|ACTIVITY|RULE|SPEECH_BUBBLE|
                          RUNNING_HEAD|PAGENUM|UNKNOWN,           (TC-11 §2 — 20 roles)
                    roleConfidence, text, bbox[x,y,w,h],
                    relations{caption_of?, options_of?, answer_of?, refers_figure?, continues?, part_of_box?},
                    provenance{extraction_method, ocr_conf, run_id},
                    trust{status: TRUSTED /*only these are serialised*/, reasons[], verifier_agreements[]}}
  figures[]        {bbox, kind, labels[], captionBlockId?}          (EXTEND — image regions)
  tables[]         {bbox, cells[][], headerRows, answerSlots[]}    (GPU path only; else absent)
  activities[]     LessonActivity (existing sealed types; keys NOT here)
  typedData        {processSteps?[], mapAssets?[], objectives?[] /*verbatim*/,
                    events?[] /*BLOCKED — TC-06*/, relations?[] /*BLOCKED*/, comparisons?[] /*BLOCKED — GPU tables*/}
  bindings[]       SemanticBinding (optional, zero-or-one per activity)
  version          {knowledgeVersion, packVersion, sdmVersion /*tc-v2…*/, pipelineIds[]}
```

Invariants (the ones that make "one truth" real):

1. **Learner projection carries no keys.** Answer keys (SGV) live in a separate, key-only structure
   joined at Surface time — the Scaffold rule and QTI's item/response-processing split; SAM already
   does this for `TvQuestion` (no answer field). TC-14: the join is `answer_of` by printed
   enumerator, behind an answer-leak guard.
2. **Every block and every typed datum has a `sourceRef`; a View may not render anything without one.**
3. **`trust.status ≠ TRUSTED` blocks are never rendered as text** — the serializer refuses to emit
   them (TC-11 §4); they render as page-region images or are omitted with an explicit line.
4. **Views are pure functions of the document + learner state.** No View may fetch content outside
   the document (Mode 3 `DerivedFacts` are derived from it).
5. **Bindings are optional.** With `bindings=[]`, Mode 1 and Mode 2 work fully; Mode 3 falls back to
   Surface-level policies (`reader-v1`, `experiment-v1`).
6. **Version pins.** Evidence written under a document carries `knowledgeVersion` (existing) and
   should carry `sdmVersion` + pipeline ids (TC-12) — replay safety already proven for pack updates (WAL-85).
7. **A block's role is gated separately from its text.** A QUESTION whose role confidence is below
   the measured bar (≥ 0.95) renders as BODY with no prompt affordance (TC-07 §Consequence).
8. **Page-feature guard.** Pages whose `layout_features` include formula / diagram / map / timeline /
   colour-heavy deliver FIGURE blocks and page images only (TC-10, TC-18 Q16).

## 4. What is common vs View-specific (Q4, Q5, Q6)

| Shared by all three Views | Mode 1 only | Mode 2 only | Mode 3 only |
|---|---|---|---|
| `lessonKey`, `chapter`, `lesson`/`boundary`, `pages` (image refs + `layout_features`), `blocks` with `sourceRef`/`trust`, `figures`, `version`, provenance wording rule (`sourceLineForChildOf`) | reading order, page rasters, per-block display trust, bookmarks/annotations (per learner, TRACE) | `typedData` + `tables` (GPU path), representation explanation (WAL-185), interaction claims | `activities`, `bindings`, blueprint/`PlannedAct` sequence, SGV keys (separate `answer_of` join), learner state (BKT/ConceptSummary), Surfaces |

**Q4 — can all three consume one canonical lesson?** Yes for Mode 1 and Mode 2 by construction;
Mode 3 consumes it *plus* two things that must stay outside it (keys, learner state). "One lesson"
is therefore one *document* plus two side-joins — not one blob. After TC-v1 "one lesson" is the
lesson's TRUSTED-block subset plus page images for the rest (TC-18 verdict).

## 5. What this contract does NOT do

- It does not merge the Deep and Scale paths (Review §9 open hypothesis #5 stays open).
- It does not add a graph database, a generic renderer, or LLM-generated fields.
- It promises Figure *regions* (image), Table objects only on the GPU path, and **no Formula text** — per TC-v1; it never promised re-typeset Image/Table/Formula blocks.
- It is not a schema; field names are illustrative. The SDM's JSON per page (`pNNN.sdm.json`, TC-12) is the store; this document is one projection of it.

## 6. Reconciliation checklist — APPLIED 2026-09-05 against TC-01, TC-11, TC-18

- [x] `blocks[].role` list replaced by the SDM's 20 roles; `trusted: bool` replaced by `trust{status, reasons[]}`; `sourceRef` kept as the SDM id + bbox (TC-11 §2).
- [x] Image/Figure → EXTEND (image region + caption relation); Table → EXTEND on the GPU path / REJECT as text on the Mac path; Formula → REJECT as text, RETAIN as withholding trigger (TC-07, TC-09, TC-19 #7).
- [x] `boundary` derived from per-block `lesson{attach_method, confidence}`; denominator 3,381 ranged of 3,679 canonical (TC-03 §5); 10/38 wrong by TOC range (TC-02 §5).
- [x] Confidence = SDM tri-state trust + reasons + role confidence + `ocr_conf`; bbox = `[x, y, w, h]` normalised (TC-11 §2).
- [x] Format: SDM is JSON per page (≈ 30–40 KB/page ESTIMATED, TC-12, TC-16); §3 is its per-lesson projection — no second shape.
- [x] Native text reconstruction falsified **per layout feature**, not per subject: formula, speech-bubble, colour-heavy elementary, table, diagram/map/timeline pages → page image only (TC-05 §3, TC-06); `18` §4 answer 7 carries the list. Per-subject fidelity STILL UNMEASURED after TC-v1 (gold ≤ 10 pages per family, TC-04).
- [x] `typedData` re-checked: ProcessStep needs enumerator preservation (TC-09, TC-19 #4); objectives need the OBJECTIVE role/lexicon (TC-09 #6); comparisons blocked on GPU tables (TC-07); events blocked (TC-06).
