# TSL → LessonDocument — the bridge contract (PROPOSED)

WAL-210 · Round 3 · Lane A-DATA (A1) · 2026-09-05 · status: **PROPOSED — bounded contract, nothing decided**.
Founder order: *build the real bridge TrustedLearningSource → Trusted Structured Lesson → LessonDocument; Track B's
`LessonDocument` is the candidate CONSUMER contract; do not create a third corpus model; preserve block id, source
document, page, bbox, role, relations, lesson identity, provenance, trust status, withholding reasons; WITHHELD stays
fail-closed.* Decisions this implements: D2 (bounded contracts only), D3 (no coverage claim), D4 (verbatim SGK = internal),
D5 (denominators), D6 (nothing "Founder-approved" here).

## 1. One path

```
tool/corpus/tsl_to_lesson_document.py      the bridge (pure `convert()` + I/O `build()`), tested in tool/tests/test_tsl_to_lesson_document.py
tool/fixtures/make_lesson_fixture.py       thin wrapper → the same `build()` (kept for the old command line)
lib/core/lesson_model/*.dart               the consumer (parses the JSON; extended minimally, see §4), tested in test/core/lesson_model/
```

```
python3 tool/corpus/tsl_to_lesson_document.py \
   --tsl poc-out/trusted-corpus/tc-v2/tc2-p1/lessons/06-sgk-khoa-hoc-tu-nhien-6/bai-17.tsl.json \
   --out assets/fixtures/real [--no-crops] [--audit-status notAudited|sampledNoGate] [--audit-ref <doc>]
→ assets/fixtures/real/lesson-06-sgk-khoa-hoc-tu-nhien-6-b17.json  (gitignored; the path Track B's WorkspaceCatalog loads)
→ assets/fixtures/real/crops/*.png                                  (figure + withheld-region crops, INTERNAL, D4)
```

- **Deterministic:** no timestamps; the same TSL bytes give the same document bytes. `document_hash()` = sha256 of the
  canonical JSON. Bài 17, two consecutive runs: identical hash (tests assert it on a synthetic TSL; the real run printed
  the same hash twice).
- **Read-only on the TSL.** No OCR "fixes", no invented captions, no renamed reason codes.
- **Refusals** (`BridgeRefusal`, nothing written): `docType ≠ SGK`; `answer_keys_included == true`; a `blocks` entry without
  text or with a non-TRUSTED status; a `withheld` entry that carries text; duplicate ids; unknown `--audit-status`.

## 2. Field-by-field mapping

### 2.1 Lesson level

| TSL | LessonDocument JSON | Dart | note |
|---|---|---|---|
| `book` | `book`, `provenance.book`, every `sourceRef.book` | `LessonDocument.book` | lesson identity |
| `lesson` | `lesson` | `lessonNo` | |
| `title` | `title` | `title` | verbatim (UI title-cases) |
| curriculum-structure `subject`/`grade` | `subject`, `grade`, `bookTitle` | same | outside the TSL (census file); fallback = book id |
| `pipeline` | `provenance.sourcePipeline`; `sourceRef.pipeline` on every block | `LessonProvenance.sourcePipeline`, `SourceRef.pipeline` | `tc2-p1` |
| block `provenance.sdm_version` | `provenance.sdmVersion`, `provenance.pipelineVersion` = `<pipeline>/<sdm_version>` | `sdmVersion`, `pipelineVersion` | doc level only |
| `docType` | `provenance.docType` | — (JSON only) | refused unless `SGK` |
| `boundary.{page_start,page_end,confidence,header_found,source,attach_methods}` | `provenance.boundary.{pageStart,pageEnd,confidence,headerFound,source,attachMethods}` + `provenance.boundaryConfidence` | `LessonBoundary` | **lost:** `boundary.pages[]`, `header_page` |
| `sourceability` | `provenance.sourceability` | `sourceability` | `FULL`/`PARTIAL` |
| `answer_keys_included` | `provenance.answerKeysIncluded` | `answerKeysIncluded` | Dart **rejects the document when true** |
| `stats` | `provenance.tslStats` | — (JSON only) | raw copy |
| sha256 of the TSL file | `provenance.sourceHash` | `sourceHash` | |
| (bridge) | `provenance.generator` = `tool/corpus/tsl_to_lesson_document.py@v1`, `tslPath`, `distribution` | same | `distribution` carries the D4 string |
| (bridge) | `provenance.auditStatus` (`notAudited` \| `sampledNoGate`), `provenance.auditRef` | `AuditStatus`, `auditRef` | no «passed» value exists |
| (bridge) | `provenance.blockCounts.{byTrust,tslTrusted,tslWithheld,unknownRoleWithheld,imagesKept,imagesWithoutCrop,figuresInTsl}` | — (JSON only; Dart recounts with `blockCountByTrust`) | |
| (bridge) | `licence` = `internalResearchOnly` | `ContentLicence` (single value) | **always**; orthogonal to trust |
| (bridge) | `evidencePolicy` = `none` | `EvidencePolicy` (single value) | unchanged from Track B |
| `hybridSmartBook` | — | — | **lost** (a render hint; Track B decides rendering from block types) |
| TOC of `poc-out/units-k12/<book>.json` (naive OCR, outside the TC gate) | `chapters[]`, `chapter` | `ChapterRef` | trust `fixtureFromTrustedCorpus`, derivation `toc-ocr-chapters-v1` — see §5 |

### 2.2 Block level (every TSL `blocks[]` entry → exactly one document block, asserted)

| TSL block field | JSON | Dart | note |
|---|---|---|---|
| `id` | `id`, `sourceRef.blockId` | `LessonBlock.id`, `SourceRef.blockId` | unchanged |
| `page` / `page_printed` | `sourceRef.pagePdf` / `sourceRef.pagePrinted` | `SourceRef.pagePdf` / `pagePrinted` | printed page may be null → UI says «trang PDF n» |
| `bbox` | `sourceRef.bbox` | `SourceRef.bbox` (4 doubles, required) | normalised [x, y, w, h] |
| `role.value` | `sourceRole` **and** the block `type`/`kind` (§3) | `LessonBlock.sourceRole` + typed block | the verbatim role survives even when the type collapses it |
| `role.confidence` / `role.method` | `roleConfidence` / `roleMethod` | same | `role.coarse` **lost** (derivable) |
| `text` | `text` (or `rows` for a table with cells) | typed block text | verbatim; asserted equal to the TSL |
| `heading_path` | `relations.headingPath` | `BlockRelations.headingPath` | |
| `refers_figure` | `relations.refersFigure` (+ `refersFigure` on captions, legacy) | `BlockRelations.refersFigure` | |
| `order` | `relations.order` | `BlockRelations.order` | reading order within the page |
| `enumerator_restored` | `relations.enumeratorRestored` | same | |
| figure `caption` → this block | `relations.captionOf` = figure id | `BlockRelations.captionOf` | inverse of `figures[].caption` |
| `provenance.extraction` / `ocr_conf` | `sourceRef.extraction` / `ocrConf` | same | |
| `provenance.text_sim` | `sourceRef.agreementScore` = text_sim / 100 | `SourceRef.agreementScore` (0..1) | for audits only, never for decisions |
| `provenance.{book,page_pdf,page_printed,bbox,block_id,pipeline}` | already carried by `sourceRef` | | duplicates in the TSL |
| `cells` (table) | `rows` | `TableBlock.rows`, `safe=false` | **0 of 20 corpus tables have cells today** → withheld `table_without_cells` |

### 2.3 Withheld regions (`withheld[]` → `WithheldBlock`, structurally without text)

| TSL | JSON | Dart |
|---|---|---|
| `id`, `page`, `page_printed`, `order`, `bbox`, `provenance.*` | `id`, `sourceRef.*`, `relations.order` | as above |
| `role` | `sourceRole` | `sourceRole` |
| `reasons[]` | `reasons[]` **and** `reason` = `a,b` | `WithheldBlock.reasons` (+ `reason` string kept for `withheld_card.dart`) |
| `status` (`WITHHELD` \| `CONFLICT`) | `status` | `WithheldBlock.status` |
| `text_len` | `textLen` | — (JSON only) |
| `text` (null, refused if not) | **no `text` key** (asserted) | `fromJson` never reads `text` on a withheld block |
| crop (bridge) | `crop` | `WithheldBlock.crop` | internal page crop for adults |

### 2.4 Figures (`figures[]` → `ImageBlock`)

`id`, `page`, `bbox`, `caption` → `captionBlockId`, `labels`; trust `trustedStructuredLesson`; `sourceRole = figure`; the crop
path and `aspect` come from the PDF render. Kept only when area ≥ 3 % of the page, or ≥ 1 % with a caption (Track B rule);
**figures below that, and every figure when no PDF is present, are not blocks** (`blockCounts.imagesWithoutCrop`).

## 3. Role → block type (no guessing; everything else is withheld)

| TSL role | block | kind |
|---|---|---|
| heading | `heading` (level = min(3, len(heading_path))) | |
| body | `paragraph` | |
| caption | `caption` | |
| question | `question` | |
| objective / instruction / sidebar / stage_label | `activity` | objective / instruction / sidebar / stageLabel |
| table with cells | `table` | |
| table without cells | `withheld` · reasons `[table_without_cells]` | |
| footnote (64 corpus-wide), activity (50), option (4), any other | `withheld` · reasons `[unknown_role:<role>]` · status `WITHHELD` | |

Bài 17 has none of the withheld-by-role cases (`unknownRoleWithheld = 0`).

## 4. Trust, licence, audit — what the chip means

| value | who may carry it | meaning | chip |
|---|---|---|---|
| `trustedCorpus` | nobody today | production truth (TC-10/11 gate passed) | none |
| **`trustedStructuredLesson`** (new) | text/image/provenance-line blocks from a TSL, semantic data derived from them, the document | TRUSTED by the TC-v2 pipeline (`tc2-p1`/`sdm-v2`); **not production trust** | «Bản thử nghiệm · nguồn SGK có cấu trúc, chưa kiểm định (nội bộ)» |
| **`withheld`** (new) | `WithheldBlock` only — a text-bearing block with this value makes `fromJson` return null | region the pipeline withheld / CONFLICT / role unknown to the consumer | (block-level card, no text) |
| `fixtureFromTrustedCorpus` | chapters from the naive-OCR TOC; the pre-bridge generator | machine-generated from corpus data **outside** the TC gate | «nội dung nội bộ (từ SGK, chưa phát hành)» |
| `fixtureSynthetic` | the committed `[MẪU]` fixture | fake | «nội dung mẫu (giả lập)» |
| `prototype` | the hand-written tutor script | not SGV, not the runtime | «nội dung mẫu / nội bộ» |

Removing the «chưa kiểm định» chip from `trustedStructuredLesson` content needs **two separate Founder decisions**:
(1) acceptance thresholds on the false-trust audit (G1; the measurement is in
`FALSE-TRUST-AUDIT-RESULT-2026-09-05.md` — the Bài 17 TSL stratum measures 0/60 teaching-critical but 12/60 display slips and
the shipped packs measure far worse), and (2) the licence decision (D4). Neither is encoded in the model: `ContentLicence`
has one value, `AuditStatus` has no «passed» value, and `ContentTrust.trustedStructuredLesson.isProductionTruth == false`.

Fail-closed on the Dart side (all tested): unknown `trust`/`licence`/`auditStatus`/`evidencePolicy` ⇒ document null;
`answerKeysIncluded == true` ⇒ null; `boundary` present but broken ⇒ null; a text block with trust `withheld` ⇒ null; a
withheld block without reasons ⇒ null; a block without `sourceRef` ⇒ null; `provenance.trust == withheld` ⇒ null.
Missing `licence` ⇒ `internalResearchOnly` (the only value); missing `auditStatus` ⇒ `notAudited` (the weakest claim);
missing `relations`/`sourceRole` ⇒ empty (navigation metadata, not trust) — so Lane B's committed synthetic fixture still parses.

## 5. What is lost or not yet honest (returned for the Founder / next round)

1. `hybridSmartBook`, `boundary.pages[]`, `boundary.header_page`, `role.coarse`, per-block `sdm_version` — dropped (derivable or render hints).
2. **Chapters** come from the naive-OCR table of contents (outside the TC gate; two OCR errors are visible on the Nokia). They carry
   `fixtureFromTrustedCorpus`, not `trustedStructuredLesson`. Alternative: withhold chapters until a gated TOC exists — Founder call.
3. **The provenance line** («SGK KHTN 6 · trang 60–63 · tc2-p1 / sdm-v2») is generated text carrying `trustedStructuredLesson`
   with `sourceRole = provenance_line`; the census lists it separately (`block.sourceRef`).
4. Figures are regions, not text: their `trustedStructuredLesson` says «the region comes from the TSL», nothing about the image's
   meaning; the one figure→caption mislink noted in the checkpoint is carried verbatim (`captionOf`), not fixed.
5. `footnote` / `activity` / `option` have no consumer type — withheld, never guessed. `ACTIVITY` labels measured 0.00 precision (audit 02).
6. The tutor script exists only for Bài 17 and is `prototype`; Lane B's Round-3 rewrite of hint q1 (answer-leak guard A7) is carried
   in the bridge so the real fixture keeps zero leaks (`test/core/pedagogy/pedagogy_runtime_test.dart`).
7. Semantic data (`process`, `comparison`) is derived by the two deterministic rules Track B wrote; it carries the source blocks' trust
   and the rule id — it is a projection, not new truth.

## 6. Measured on the golden slice (KHTN 6 Bài 17, TSL `tc2-p1`, read-only)

64 TSL learning blocks (60 TRUSTED + 4 withheld) + 19 figures → **73 document blocks**: heading 13 · activity 12 · question 11 ·
paragraph 16 · caption 8 · image 8 · withheld 4 · provenance line 1. **By trust: `trustedStructuredLesson` 69 · `withheld` 4 ·
`trustedCorpus` 0 · `fixtureSynthetic` 0.** Semantic: 2 process diagrams (one with a withheld step), 1 comparison (4 rows). Chapters:
10 (naive TOC, `fixtureFromTrustedCorpus`). Tutor script: 5 steps, `prototype`. `auditStatus = sampledNoGate` (the 64 TSL blocks are the
mandatory stratum of the false-trust sample), `licence = internalResearchOnly`.

Tests: `tool/tests/test_tsl_to_lesson_document.py` (10: provenance 100 %, verbatim text, withheld count = TSL withheld + unknown roles,
no withheld text, fail-closed refusals, deterministic hash, figure order, real TSL when present) ·
`test/core/lesson_model/lesson_bridge_contract_test.dart` (9: parse, WITHHELD ≠ TRUSTED, injected text ignored, fail-closed enums,
legacy fixture, round-trip, real fixture counts) · existing lesson_model tests updated (real fixture now `trustedStructuredLesson`).

## 7. PROPOSED (round 4, Lane C — Golden Slice #2, LS&ĐL 5 Bài 8): History additions on top of the bridge

Status: **PROPOSED**, nothing decided; owner of the bridge stays A-pipeline. Lane C did **not** modify `tsl_to_lesson_document.py`; the
additions run as a post-processor (`tool/research/lane_c/history_rules.py`) on the bridge's JSON and are consumed by
`lib/core/lesson_model/timeline_*.dart` without any change to `semantic_data.dart` / `lesson_document.dart`. Gate and numbers:
`docs/research/lane-c/05-GOLDEN-SLICE-2-GATE.md`.

| addition | JSON (document) | Dart | rule id | note |
|---|---|---|---|---|
| timeline from prose | `semantic[] += {type: timeline, id, title = nearest numbered section heading (verbatim), trust = source block trust, derivation, events[]}` | parsed by the existing `SemanticData.fromJson` (`when`, `title`, `text`, `sourceBlockId`) | `prose-dated-events-v1` | extra keys per event `yearStart`, `yearEnd`, `era` (`CN`/`TCN`), `charSpan` are **ignored** by the Dart parser (forward-compatible); `TimelineDate.parse(when)` recovers them on the Dart side, fail-closed |
| story sources | `semantic[timeline].sources[] = {attributionBlockId, titleBlockId, storyBlockIds[], withheldPartIds[], publisher, year, form, derivation}` | **not** parsed from JSON — re-derived from the document's blocks by `deriveStoryAttributions(doc)` (`timeline_sources.dart`), so the fixture cannot carry a source the blocks do not support | `story-attribution-v1` | no new block kind; the attribution keeps `sourceRole = body` (pipeline label) |
| lesson title | `title` (replaced) + `provenance.historyRules.titleDerivation` | `LessonDocument.title` | `lesson-title-v1` | header-confirmed-by-TOC ⇒ TOC title when the header title is a diacritics-insensitive suffix; else header |
| tutor script | `tutorScript` (`prototype`, `prototypeScripted`, `evidencePolicy none`) | existing `TutorScript` | `history-tutor-v1` | generated from the timeline + sources; ≤ 2 hints; `keySource` names the rule and block; patterns escape only regex syntax characters (Dart `RegExp(unicode: true)` rejects `\-` / `\ `) |
| record | `provenance.historyRules = {version, rules[], events, narrativeYearMentionsNotEvents, attributions, attributionsComplete, figureDependentQuestions[], withheldQuestionsNotUsed[], timelineAskBlockId, titleDerivation, tutorSteps}` | — (JSON only) | — | the census of what the rules did and did not use |

Requested from A-pipeline (bridge or upstream), in priority order: (1) `Ã/ã` in `tc2_attach.LESSON_HDR`; (2) block-level colour share instead of the
page-level `page_feature:color_heavy` withhold; (3) an `attribution` role (the gold already has it) and dash sub-questions; (4) `figure_dependent`
on «quan sát … hình»; (5) a «Chủ đề» variant of `toc-ocr-chapters-v1`; (6) fold `prose-dated-events-v1` / `story-attribution-v1` into the bridge
once accepted, so the post-processor disappears. Requested from the gold owner: lesson numbers on LS&ĐL 5 p041 (9 → 8) and p080 (17 → 18).
