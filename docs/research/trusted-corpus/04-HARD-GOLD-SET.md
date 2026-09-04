# 04 — Hard K-12 Source-Fidelity Gold Set (38 pages)

**Files:** `tool/corpus/tc_gold/<book>-pNNN.json` (38 files), page list `tool/corpus/tc_gold_pages.py`, renders with a coordinate grid in `poc-out/trusted-corpus/tc-v1/renders/` (bundle: `renders/`).

**How gold was written.** Each page was rendered from the source PDF at 150 dpi with a 0.0–1.0 coordinate grid (`tool/corpus/tc_render.py --grid`) and read by the annotator (Claude, vision) **from the image** — never from any extractor output. Selection was stratified from the census (`tc_gold_select.py`, seed 20260904) plus the 9 WAL-206 pages (kept, re-annotated in the richer format) and the WAL-204 failure page, which was located by grepping the OCR for "Trong số 118" (it is `07-sgk-khoa-hoc-tu-nhien-7` PDF page **32**, printed 31 — not p21 as first assumed).

**What a gold page records** (superset of WAL-206's anchors):

| field | meaning |
|---|---|
| `blocks[].order` | the reading order a learner follows |
| `blocks[].role` | fine role: heading, body, question, option, answer, answer_slot, activity, rule, objective, sidebar, caption, figure_label, diagram, table, formula, footnote, attribution, speech_bubble, running_head, page_number |
| `blocks[].bbox` | [x, y, w, h] normalised, by eye ±0.02 |
| `blocks[].text` | full transcription (for text accuracy) where feasible; `null` for formulas/diagrams/tables whose linear text is not well-defined (their content is described in `notes`) |
| `blocks[].anchor` | first words as printed (matching key) |
| `blocks[].contiguous` | the block must be delivered in ONE piece with nothing spliced in |
| `blocks[].column`, `rel` | column membership; caption_of / options_of / answer_of / refers_figure / continues |
| `lesson` | the lesson the page belongs to, from the printed content (with a note when the TOC disagrees) |
| `flex_groups` | blocks whose position relative to the main flow is not meaning-bearing (a sidebar may be read before or after the adjacent paragraph) — pairs across groups are not scored for order |
| `critical` | the page-specific ways a parser could produce a critical teaching error |

## The 38 pages

| # | page | grade / subject / type | why it is hard |
|---|---|---|---|
| 1 | KHTN 7 p20 | 7 KHTN SGK | objectives box, pie-chart labels, speech-bubble lead-in, photos + captions, sidebar beside photos (WAL-206) |
| 2 | KHTN 7 p21 | 7 KHTN SGK | activity box with (p, n) data, question boxes, footnote |
| 3 | **KHTN 7 p32** | 7 KHTN SGK | **the WAL-204 failure page**: body beside a blue sidebar, MCQ options in 2 columns, element chips, EM ĐÃ HỌC ∥ EM CÓ THỂ |
| 4 | Toán 5 p21 | 5 Toán SGK | speech bubbles with fractions, dashed formula box, worked steps (WAL-206) |
| 5 | Toán 5 p92 | 5 Toán SGK | theme + lesson banners, 3 speech bubbles, three definitions side by side |
| 6 | Ngữ văn 9 p67 | 9 Ngữ văn SGK | poem + "Theo dõi" box + 8 footnotes (the Ngữ văn falsification page) |
| 7 | Ngữ văn 9 p83 | 9 Ngữ văn SGK | body wrapping beside a yellow box, "+" sub-questions |
| 8 | Tin học 9 p20 | 9 Tin học SGK | two-column bullets continued from the previous page, MCQ, LUYỆN TẬP/VẬN DỤNG |
| 9 | Khoa học 4 p30 | 4 Khoa học SGK | mind-map diagram page |
| 10 | Khoa học 4 p78 | 4 Khoa học SGK | procedure step beside a drawing, 3-photo figure question, EM ĐÃ HỌC ∥ EM CÓ THỂ |
| 11 | LS&ĐL 5 p41 | 5 LS&ĐL SGK | story box beside a photo, attribution, timeline table with "?" cells |
| 12 | LS&ĐL 5 p80 | 5 LS&ĐL SGK | full physical map (~60 labels), legend, numbered-country box |
| 13 | Địa lí 10 p40 | 10 Địa lí SGK | two "Em có biết?" sidebars beside body and photo |
| 14 | Địa lí 10 p115 | 10 Địa lí SGK | back-matter pronunciation index (two 3-column tables, 163 lines) — must not attach to a lesson |
| 15 | Vật lí 10 p30 | 10 Vật lí SGK | vector formulas, figure, two side-by-side summary boxes |
| 16 | Vật lí 10 p89 | 10 Vật lí SGK | equipment list with numbered photo labels, 9 procedure steps, fraction formula, figure column |
| 17 | Vật lí 11 p105 | 11 Vật lí SGK | tall EM CÓ BIẾT sidebar with fractions, numbered equations (24.2)–(24.5), question box |
| 18 | Tiếng Việt 5 p8 | 5 TV SGK | image-only theme opener |
| 19 | Ngữ văn 11 p39 | 11 Ngữ văn SGK | true two columns; right box continues from the previous page; three attributions |
| 20 | LS&ĐL 7 p94 | 7 LS&ĐL SGK | narrow left column (2 sidebars + photo) beside wide body |
| 21 | Toán 2 p48 | 2 Toán SGK | base-ten block pictures with "<"/">" statements, "? ? ?" answer slot |
| 22 | Toán 3 p32 | 3 Toán SGK | two tables (Bảng nhân 7 ∥ Bảng chia 7) with "?" cells, robot hint, arrow diagrams |
| 23 | Tin học 6 p21 | 6 Tin học SGK | dialogue, two-column bullets with a sticky note inside the right column |
| 24 | Ngữ văn 6 p21 | 6 Ngữ văn SGK | exercises with an empty table beside a pink knowledge box that contains the answers |
| 25 | Toán 7 p41 | 7 Toán SGK | exponents/fractions everywhere, mascot bubbles, polynomial long division |
| 26 | LS&ĐL 8 p71 | 8 LS&ĐL SGK | timeline with boxes above/below the arrow (order follows markers, not y), portrait with caption on the LEFT |
| 27 | Toán 12 p20 | 12 Toán SGK | THUẬT NGỮ ∥ KIẾN THỨC box, integrals, graph figure |
| 28 | KHTN 9 p46 | 9 KHTN SGK | two 2-level-header tables with "?" cells, apparatus photo with labels |
| 29 | KHTN 9 p38 | 9 KHTN SGK | question wrapping beside a 4-prism figure, wide labelled diagram |
| 30 | Tiếng Việt 4 p28 | 4 TV SGK | reading continued from previous page, glossary, 8 options in a 4×2 grid, "?" table |
| 31 | Toán 9 p29 | 9 Toán SGK | fraction equations side by side, boxed definition, worked example with solution |
| 32 | Tiếng Việt 2 p14 | 2 TV SGK | keyword chips, model answer "M: ào ào", image-only exercise |
| 33 | Tiếng Việt 2 p103 | 2 TV SGK | reading continued, "(…)" blanks, model answer, handwriting grid |
| 34 | TN&XH 1 p6 | 1 TN&XH SGK | table of contents page (must not attach to a lesson) |
| 35 | SGV Toán 7 p43 | 7 Toán SGV | two 3-column lesson-plan tables (CẤU PHẦN / MỤC ĐÍCH / GỢI Ý, ĐÁP ÁN) |
| 36 | SGV Toán 4 p54 | 4 Toán SGV | flow diagrams, quoted teacher questions, model answers, Tiết 2 starts mid-page |
| 37 | SGV Tin học 10 p39 | 10 Tin học SGV | **two lessons on one page** (Bài 4 ends, Bài 5 starts) with a binary-addition table |
| 38 | Ngữ văn 8 p38 | 8 Ngữ văn SGK | control: plain prose with dialogue, footnotes, attribution |

Coverage: Toán ×7 (grades 2, 3, 5, 5, 7, 9, 12), Tiếng Việt/Ngữ văn ×9, Khoa học/KHTN/Vật lí ×10, LS&ĐL/Địa lí ×6, Tin học ×3, TN&XH ×1, SGV ×3 (incl. one inside "Tin học"). Features: side-by-side 21 pages, coloured boxes 21, sidebar 13, formula 11, table 10, diagram 10, two-column 7, continuation 8, speech bubbles 5, colour-heavy 5, non-lesson pages 4.

## Known limits of the gold

- One annotator (a VLM). Gold text was written from a 150-dpi render of a ~100-ppi scan; residual transcription error is estimated at < 0.5 % of characters (spot-checked against three parsers agreeing where the gold differed — none found in the checked blocks, but this is not a second human read).
- Lesson numbers were taken from printed content; the first draft had one error (Tin học 9 p20: Bài 3 → Bài 4) corrected against the book's TOC. Three pages carry a note where the parsed TOC is incomplete (Khoa học 4 p78, LS&ĐL 5 p80, LS&ĐL 7 p94).
- Formula/diagram/table blocks carry descriptions, not linear text; text accuracy is therefore measured on prose, questions, captions, sidebars and short formulas only (462 learning blocks, 335 with full text).
- 38 pages is enough to rank pipelines and to find error classes; it is **not** enough to certify a false-trust rate below ~1 % (a 0.1 % claim needs thousands of validated blocks — see 17-RESIDUAL-RISKS).
