# G — Evidence flow (source provenance → learner evidence), as it is and as the slice makes possible

## G.1 Today's chain (OBSERVED-IN-CODE)

```
SGK PDF (scan, no text layer)                              poc-out/pdf/…                          [derived data, gitignored]
  → Apple Vision OCR lines (x, y, w, h, conf, text)        poc-out/graph/ocr-body/<book>/pNNN.json
  → units-k12 (WAL-204) | units-layout (WAL-206 XY-cut)    poc-out/units-*/                       provenance: page (+ regionPath on layout)
  → pattern router → tvReadings / tvWritings / khoaExperiments in assets/pack/lesson-index-g{N}.json
  → LessonIndex.fromJsonString (fail-closed parse)          lib/features/subjects/lesson_index.dart:390
  → LearningActivity {sourcePage?, sourceBook?, passage?}   lib/core/tutor/learning_activity.dart:35
  → Surface → CandidateEvidence → validateCandidateEvidence lib/core/student/evidence_validator.dart:58
  → LearningEvent {sourceDocumentId?, lessonNo?, policyId?, knowledgeVersion?}  lib/core/student/learning_evidence.dart:73
  → LearningSession record                                  lib/core/store/learning_session.dart:30
```
What reaches the evidence record from the source today: **book id + lesson number + printed page** (on some records). No block id, no bbox, no trust status, no pipeline version.

## G.2 The chain the slice validated (MEASURED, offline)

```
SGK PDF page
  → Docling layout (heron) + Apple Vision text [primary]     tc-v2/tc2-p1/bakeoff/raw/docling-ocrmac/   1,049 + 75 pages, deterministic (7/7 shared pages byte-identical with TC-v1)
  → WAL-206 XY-cut on the OCR lines [verifier]               tc-v2/tc2-p1/bakeoff/raw/current-xycut/
  → SDM-v2 page: blocks {id, order, bbox, text (enumerator-preserved), role{value,confidence,method,evidence}, agreement, guards[], trust{status,reasons}}
                                                             tc-v2/tc2-p1/sdm/<book>/pNNN.sdm.json     tool/corpus/tc2_sdm.py
  → header-based lesson attachment + TOC repair              tc-v2/tc2-p1/attach/<book>.json           tool/corpus/tc2_attach.py
  → Trusted Structured Lesson (per lesson)                   tc-v2/tc2-p1/lessons/<book>/bai-NN.tsl.json  tool/corpus/tc2_tsl.py
        blocks[].provenance = {book, page_pdf, page_printed, bbox, extraction, ocr_conf, text_sim, pipeline, sdm_version, block_id}
        withheld[] = {bbox, reasons, provenance}  (no answer-key text ever)
```
Every unit a learner could see or be asked now has a **block id** that resolves to `(book, pdf page, bbox, pipeline version)`. That is the provenance the evidence record lacks.

## G.3 What the evidence record would gain (HYPOTHESIS — no Dart changed)

| field | source | why |
|---|---|---|
| `blockIds[]` on `CandidateEvidence` / `LearningEvent` | TSL `blocks[].id` | the passage/prompt a child answered can be traced to a page region; a later false-trust audit (TC-17 #2) can find every event built on a block that turns out wrong |
| `sdmVersion` + `pipeline` | TSL `provenance.pipeline` (`tc2-p1`) | "derived data dies with its source" (D-132): when a pipeline version is retired, its events are identifiable |
| `roleConfidence` of the prompt block | TSL `blocks[].role.confidence` | evidence minted on a QUESTION with confidence 0.75 (enumerated stem) is weaker than one minted on 0.92 (ends with "?") |
| `trace` (View 1/2 display) vs `evidence` (Surface) | WAL-207 `13` §3 | display is never evidence; unchanged by the slice |

## G.4 Invariants the slice enforces at the source (so downstream cannot violate them)

1. WITHHELD/CONFLICT blocks are never serialised with text into the TSL projection a learner reads (`tc2_tsl.py`, `NEVER_TEXT` for answer keys / teacher text — checked on the SGV sample: 0 answer-key blocks with text in any TSL).
2. A QUESTION that refers to a figure is withheld from text surfaces (`figure_dependent`), so the WAL-206 device defects "figure-dependent prompt" cannot recur from this source.
3. Enumerators are restored (`enumerator_restored` = 3,4xx blocks on the slice — I.4), so an SGV key "Câu 2" can in principle be paired to the SGK "2." (I.5) — the relation, not the leak, is what reaches the evidence chain.

## G.5 Gaps (for H / J)

- No Dart reader of the TSL exists; until one does, G.2 is offline data (F.1).
- The audit loop "evidence → block → page crop → human" requires page images *for the reviewer* — allowed under `localResearchOnly` for research; **not** the same as delivery to a learner (J.1).
