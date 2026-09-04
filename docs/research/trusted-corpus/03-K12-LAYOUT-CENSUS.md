# 03 — K-12 Layout Census (whole corpus, MEASURED)

**Scope:** all 531 documents / 62,729 OCR pages in `poc-out/graph/ocr-body` (301 SGK, 220 SGV, 7 UNKNOWN, 3 WORKBOOK). Every page was measured twice, from two independent signals: (a) Apple-Vision OCR line geometry, (b) a 30-dpi render of the source PDF page (PyMuPDF). Run time: 179 s for 62,729 pages on 6 workers (`tool/corpus/tc_layout_census.py`, `tc_census_augment.py`, `tc_census_report.py`). Full tables: `03A-CENSUS-TABLES.md`; raw rows: `poc-out/trusted-corpus/tc-v1/census/pages.jsonl`.

**Rule:** features overlap. Every number below is "pages carrying feature X"; they are never summed.

## 1. Source facts

| fact | value | how measured |
|---|---|---|
| native text layer | **0 of 62,729 pages** | `page.get_text()` on every page = 0 chars |
| sparse / image-only pages | 165 (0.3 %) | < 3 OCR lines or < 40 chars |
| source resolution | ~100 ppi scans (OCR script renders at 3×; 6× gave identical output) | `tool/ocr/ocr_pdf.swift` comment + test |
| OCR confidence < 0.75 | 815 pages (1.3 %) | mean line confidence |
| overlapping OCR boxes > 5 % | 497 pages (0.8 %) | rotated / garbled regions |

Consequence: PDF-native structure (fonts, text order, tagged PDF) is unavailable for the entire corpus. Every candidate pipeline must start from pixels.

## 2. Feature census (pages carrying each feature)

| feature | pages | % of 62,729 | what it means for extraction |
|---|---|---|---|
| globally 2-column | 2,887 | 4.6 % | classic two-column text |
| globally 3-column | 683 | 1.1 % | tables, TOC, indices, multi-column exercises |
| **side-by-side region** (≥ 3 rows where two text blocks sit beside each other) | **18,476** | **29.5 %** | the layout that a top→bottom line sort interleaves (WAL-204). This is what the WAL-206 census called "two-column" (30.6 %) — both counts are right; they measure different things |
| table (≥ 4 aligned rows × ≥ 3 cells) | 4,461 | 7.1 % | |
| formula (≥ 3 lines with math tokens) | 5,751 | 9.2 % | Toán 45 %, Vật lí 46 %, Hoá 28 % of their pages |
| sidebar / labelled box beside body | 16,481 | 26.3 % | Em có biết, Lưu ý, Ghi nhớ, narrow right-hand stacks |
| figure (ink outside OCR boxes ≥ 4 % of page) | 23,459 | 37.4 % | SGK 63.7 %, SGV 12.0 % |
| diagram (figure + ≥ 8 short scattered labels) | 11,919 | 19.0 % | mind maps, timelines, apparatus, maps |
| coloured box under text (≥ 10 % of lines) | 14,354 | 22.9 % | activity / summary / objective boxes |
| colour-heavy page (≥ 25 % saturated pixels) | 3,361 | 5.4 % | elementary visual layouts (grade 1: 14 %) |
| cross-page continuation (first body line lower-case) | 16,170 | 25.8 % | a page is not a unit of meaning |

Pages with **no** hard feature at all: **22,276 (35.5 %)**. Pages with ≥ 2 hard features: 27,481 (43.8 %).

## 3. Layout families

A family = the set of features on a page. **241 distinct families** exist; **20 families cover 80 % of pages, 39 cover 90 %, 62 cover 95 %.** The top families: `1col` 35.5 %, `1col+sidebar` 6.7 %, `1col+figure` 6.6 %, `1col+figure+box` 4.1 %, `1col+side-by-side+sidebar` 4.0 %, `1col+side-by-side` 2.9 %, `1col+formula` 2.4 %. Globally two-column families are a long tail (`2col+sbs` 0.8 %).

Reading: "one parser per family" is not a plan — the families are combinations, not types. What matters is per-FEATURE handling (side-by-side regions, boxes, figures/diagrams, formulas, tables) and a gate that recognises when a page carries a feature the pipeline cannot handle.

## 4. By grade / subject / document type (selected; full table in 03A)

- **Grades 1–5** are figure-heavy (45–52 % of pages carry a figure; 28–39 % coloured boxes; grade 1: 14 % colour-heavy). **Grades 10–12** are text-heavy but formula-heavy (11–12 % formula pages) and sidebar-heavy (26–30 %).
- **Toán:** formula 45.2 %, sidebar 46.1 %, table 12.8 %. **Vật lí:** formula 45.7 %. **Tin học:** sidebar 42.9 %, table 13.5 %. **Tiếng Anh:** globally two-column 21.3 %, figure 55 %, diagram 53 %. **Ngữ văn:** the "cleanest" (figure 12 %, formula 0.5 %) but sidebar 23.6 %. **Lịch sử/Địa lí:** diagram/map pages 14 %, table 7–16 %.
- **SGK vs SGV:** SGK pages carry figures 5× more often (63.7 % vs 12.0 %) and coloured boxes 9× more often (41.8 % vs 4.5 %). SGV pages are mostly prose + tables (3.8 %) — structurally easier, but their *content* is teacher guidance and answer keys, which must never leak to the child (see 14-SGV-IMPACT).

## 5. Lesson impact (SGK lessons with a page range: 3,381 of 3,679)

| feature | lessons containing ≥ 1 such page | % |
|---|---|---|
| figure | 3,265 | 96.6 % |
| coloured box | 2,844 | 84.1 % |
| side-by-side region | 2,629 | 77.8 % |
| diagram | 2,455 | 72.6 % |
| sidebar | 2,377 | 70.3 % |
| cross-page continuation | 1,983 | 58.7 % |
| table | 1,170 | 34.6 % |
| formula | 939 | 27.8 % |
| globally 2-column | 589 | 17.4 % |
| **no hard feature on any page** | **103** | **3.0 %** |

Reading: a "clean lesson" essentially does not exist (3 %). Trust must be decided per **block**, not per lesson or per page; a lesson is trusted when the blocks SAM will use are trusted, and untrusted blocks are withheld.

## 6. Reconciliation with earlier numbers

- WAL-206: "18,661 / 61,031 non-sparse pages two-column (30.6 %)" → reproduced here as **side-by-side regions 18,476 / 62,564 (29.5 %)**. Global two-column pages are only 4.6 %. The earlier number is a *local multi-column* count and remains the right one for the interleaving risk.
- WAL-206: "2,635 / 3,357 lessons contain ≥ 1 two-column page" → **2,629 / 3,381 (77.8 %)** here.

## 7. Limits of this census (honest)

- Feature detectors are heuristics calibrated on the 38 gold pages (see 04): the sidebar detector over-triggers on figure-label stacks; "table" misses borderless tables; "diagram" catches map labels and timelines but also dense figure legends. Treat shares as ±15 % relative.
- It measures layout, not meaning: it cannot tell a worked example from a learner question — that is a block-role problem (07).
