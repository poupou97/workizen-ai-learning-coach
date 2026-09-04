# 02 — Current Extraction: what fails, how often, and why it is not an OCR bug

Two "current" pipelines were measured on the 38-page hard gold set (04), both from the same Apple-Vision OCR (`apple-vision-accurate-vi`, 3× render of ~100-ppi scans):

- **current-naive** = the WAL-204 generic order: OCR lines in file order (top→bottom, left→right with 0.012 y-tolerance), joined into paragraphs on vertical gaps. This is what `units-k12` and the packs were built from.
- **current-xycut** = WAL-206 `layout_extract.py`: recursive XY-cut, block roles, page/region trust (fail closed).

Full tables: `05-PARSER-BAKEOFF.md`, `bakeoff/scores.md`.

## 1. Headline (MEASURED, 462 learning blocks on 38 pages)

| | current-naive (WAL-204) | current-xycut (WAL-206) |
|---|---|---|
| text accuracy, with diacritics (tone-placement-normalised) | 0.902 | 0.907 |
| CER without diacritics | 0.089 | 0.085 |
| reading order (pairwise, main flow) | 0.966 | 0.976 |
| meaning-changing inversions (same column) | 49 | 34 |
| fidelity (contiguous block delivered clean) | 0.718 | 0.847 |
| cross-column splices (blocks mixing two columns/boxes) | 24 | 17 |
| question precision / recall | none / — | 0.70 / 0.69 |
| Trusted Learning Source Rate (blocks delivered correctly AND trusted) | **0.656** | **0.193** |
| blocks trusted / withheld | 446 / 0 | 101 / 352 |
| **False trust rate** (wrong among trusted) | **0.321** | **0.119** |
| critical-teaching-error events (all output) | 103 on 30 pages | 121 on 30 pages |

Reading: the naive pipeline trusts everything and is wrong on **one block in three**. The XY-cut pipeline fixed most column interleaving but its trust gate withholds **76 % of all learning blocks** on hard pages, and **12 % of what it still trusts is wrong** — nowhere near the < 0.1 % the Founder expects.

## 2. The three failure classes, with the WAL-204 page (KHTN 7 PDF p32, printed 31)

The page: a body paragraph in a left column, a blue "Em có biết" sidebar on the right, an MCQ whose options sit in two columns, then EM ĐÃ HỌC ∥ EM CÓ THỂ side by side. Renders: `renders/07-sgk-khoa-hoc-tu-nhien-7-p032.png`, crops `…-p032-crop-0.08-0.05-0.86-0.25.png` (body + sidebar) and `…-crop-0.08-0.59-0.86-0.33.png` (the two boxes).

**(a) Cross-column contamination — current-naive, block 1 (as shipped in WAL-204):**

> "3. Các nguyên tố khí hiếm Trong số 118 nguyên tố đã biết có 7 nguyên tố là **Các nguyên tử kim loại có** nguyên tố khí hiếm. Nguyên tử của chúng có lớp **xu hướng như**…"

The sidebar's lines are merged into the body line by line. The sentence "có 7 nguyên tố là các nguyên tử kim loại" is false chemistry, produced from two true texts. **OCR was correct on every word.**

**(b) Option order and answer confusion — current-xycut, MCQ block:** options come out as A, B, D, then "C. Kim loại và khí hiếm Hãy chọn đáp án đúng nhất." labelled QUESTION; the instruction line is glued to option C. The page is marked untrusted by the gate (confidence 0.85, a marginal cut) so nothing ships — safe, but the lesson loses its only MCQ.

**(c) Box interleaving — current-naive, last block:** "• Các nguyên tố hóa học trong bảng tuần hoàn được **Vận dụng mỗi quan hệ** sắp xếp theo chiều tăng dần của điện tích hạt nhân **giữa vị trí trong bảng** nguyên tử…" — EM ĐÃ HỌC and EM CÓ THỂ read as one paragraph.

For contrast, on the same page Docling+ocrmac (same OCR, different layout analysis) returns the body as one clean paragraph, the sidebar as a separate block, and the four options as four blocks in A-B-C-D order; Marker does the same. The failure is layout analysis, not recognition.

## 3. Where the current XY-cut still goes wrong (measured error classes)

| class | events | example |
|---|---|---|
| heading emitted as learner question | 11 | "a) So sánh các số tròn trăm." (Toán 2), "VIẾT" (TV 2) |
| non-question emitted as question (instruction, objective, table header) | 23 | "2. Tìm từ ngữ phù hợp với các cột trong bảng. Nghề nghiệp" (TV 4 — table header glued) |
| cross-column contamination | 17 | Toán 5 p92: "Hình tam giác có một góc vuông…" spliced with the neighbouring definition |
| meaning-changing order inversion | 34 | options / worked steps / procedure lists |
| corrupted data (digits, operators) | 22 | Toán 3 p32 tables: "7 × 1 = 7 7 : 7 = 1 …" |
| sidebar precision / recall | 0.45 / 0.43 | narrow columns of body text labelled sidebar and vice-versa |

The gate is doing its job (352 blocks withheld, 12 false-trusted) but it withholds by *page geometry*, so a marginal cut anywhere loses the whole page — coverage collapses to 19 % on hard pages. On the 150-page pilot it trusted **N/A** — see 13-OLD-VS-NEW-CORPUS for the pilot figures.

## 4. Why "not an OCR bug" is now measured, not asserted

- Text accuracy of the same OCR under three different layout analyses is 0.902 / 0.907 / 0.954 (naive / XY-cut / Docling): the recognition is constant, the *block boundaries* decide how much of the text survives as correct blocks.
- CER without diacritics is 0.085–0.089 for the current pipelines vs 0.040–0.044 for Docling/Marker on the same pages: half of the remaining "OCR" error is text that landed in the wrong block, not misread characters.
- Apple Vision's genuine weaknesses (07-/09-): tone-mark slips on decorative fonts ("EM CÓ THẾ"), fractions and exponents flattened ("1 5", "6x4"), mind-map/timeline labels read as prose. These are shared by every text-line OCR and are not fixable by layout.

## 5. Lesson attachment is a separate, pipeline-level failure

Comparing the gold lesson of each page with the current TOC-range attachment (printed pages, offset calibrated): **10 of 38 gold pages attach wrongly** — 4 non-lesson pages (TOC, back matter, theme opener, SGV) attach to a lesson; Khoa học 4 p78 attaches to Bài 19 because Bài 20 is missing from the parsed TOC; LS&ĐL 5 p80 and LS&ĐL 7 p94 attach to the wrong lesson because their TOCs are PARTIAL (10 and 12 lessons parsed); SGV Tin học 10 p39 holds two lessons. This error class is invisible to every parser and to the WAL-206 gate.
