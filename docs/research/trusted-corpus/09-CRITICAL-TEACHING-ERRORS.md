# 09 — Critical Teaching Errors (CTE): classes, counts, examples

A CTE is an extraction outcome that, if trusted, makes SAM teach something false, out of order, or from the wrong source. Counted per event over each candidate's **entire output** on the 38 gold pages (whether or not the pipeline trusted the block — the trusted subset is in 08). Scorer: `tool/corpus/tc_score.py`; per-page events with quotes: `bakeoff/scores.json` → `cte_examples`.

| class | definition | naive | xycut | docling | mineru | marker | vlm |
|---|---|---|---|---|---|---|---|
| **cross-column contamination** | one block contains text of ≥ 2 gold blocks from different columns/boxes | 24 | 17 | 6 | 2 | 7 | 12 |
| **order changes meaning** | inverted pair of learning blocks in the same column | 49 | 34 | 21 | 22 | 2 | 3 |
| **heading as learner question** | gold heading emitted with role QUESTION | 0* | 11 | 0* | 0* | 0* | 0 |
| **non-question as question** (objective, instruction, answer, option, table header) | | 0* | 23 | 0* | 0* | 0* | 0 |
| **corrupted data** | digit/operator sequence of a learning block altered (fractions, <, >, ≠, years, °C, n = 1,41) | 16 | 22 | 31 | 10 | 16 | 3 |
| **enumerator dropped** | "1." / "a)" / "HĐ1" removed from a question or option | 1 | 4 | **65** | 0 | 5 | 0 |
| **figure text as prose** | diagram/map labels emitted as a body block | 2 | 1 | 0 | 0 | 0 | 0 |
| **attribution detached** | source line separated from its excerpt | 1 | 0 | 0 | 1 | 0 | 2 |
| **wrong lesson (page-level TOC attach)** | pipeline-level, same for all candidates | 10 / 38 pages |
| total events (excl. lesson) | | 93 | 111 | 123 | 35 | 30 | 20 |
| pages with ≥ 1 event | | 30 | 30 | 32 | 21 | 20 (of 32) | 20 (of 31) |

\* candidates without a QUESTION role cannot commit this class — and cannot deliver questions either.

## Examples a Founder can look at (renders in the bundle)

1. **Contamination that creates false chemistry** — KHTN 7 p32, naive: "…có 7 nguyên tố là Các nguyên tử kim loại có nguyên tố khí hiếm…" (crop `07-sgk-khoa-hoc-tu-nhien-7-p032-crop-0.08-0.05-0.86-0.25.png`).
2. **Three definitions destroyed** — Toán 5 p92, MinerU/naive: "Hình tam giác có một góc vuông gọi là hình tam giác vuông. Hình tam giác có một góc tù…" interleaved line by line across three dashed boxes.
3. **A chronology reversed** — LS&ĐL 8 p71 timeline: every candidate reads the top row of boxes then the bottom row (1873, 1878–1907, early XX, then 1873–1909, 1884–1886, 1890). Order score looks fine (captions and questions are in order); the history is wrong. (crop `08-sgk-lich-su-va-dia-li-8-p071-crop-0.10-0.10-0.82-0.28.png`)
4. **Math facts corrupted** — Toán 3 p32 tables (crop `03-sgk-toan-3-tap-mot-p032-crop-0.10-0.44-0.80-0.30.png`): xycut "7 × 1 = 7 7 : 7 = 1 …" (two tables interleaved); Toán 5 p21 fractions (crop `05-sgk-toan-5-tap-mot-p021-crop-0.10-0.58-0.85-0.32.png`): Marker "1 5 + 1 2 = 2 10 + 5 10 = 7 10" — the fractions are gone in every candidate.
5. **Heading as question** — xycut: "a) So sánh các số tròn trăm." (Toán 2), "VIẾT" (TV 2), "1. Dụng cụ thí nghiệm (Hình 22.3)" pattern (Vật lí 10).
6. **Answer/objective as question** — xycut: "1. Chọn được nấm để làm thức ăn" (Khoa học 4 EM CÓ THỂ), "2. Tìm từ ngữ phù hợp với các cột trong bảng. Nghề nghiệp" (table header glued).
7. **Numbering lost** — Docling: "Sử dụng bảng tuần hoàn, hãy xác định vị trí…" without "1." on 65 questions/options → the question can no longer be paired with an SGV answer key "Câu 1".
8. **Teacher text as learner content / two lessons on one page** — SGV Tin học 10 p39: page-level attachment gives Bài 5 to the Bài 4 explanation of two's-complement addition; SGV Toán 4 p54 quoted teacher prompts ("Số đã cho gồm mấy trăm nghìn?") would become SGK questions.
9. **Wrong lesson / non-lesson page attached** — Địa lí 10 p115 (back-matter index) → Bài 31; TN&XH 1 p6 (table of contents) → Bài 1 unless the printed-page offset is applied; Khoa học 4 p78 → Bài 19 because Bài 20 is absent from the parsed TOC.

## Classes the gold set could not exercise (declared, not measured)

- **Future-lesson leakage across pages** (a passage from Bài 5 shown under Bài 4): only the SGV two-lesson page exercised it; needs cross-page gold.
- **Wrong source attribution SGK↔SGV** at scale: 3 SGV pages only.
- **Hallucinated text** by a VLM: the 3B VLM's text was 0.933 accurate with no fabricated sentences observed on 22 pages; not a proof.

## Bottom line

Zero critical errors was not reached by any candidate or cascade on the hard set. The classes with a clear deterministic defence are: contamination (layout parser + agreement gate), enumerators (keep the source line text), non-question-as-question (role layer with answer/objective lexicon), wrong lesson (header-based attachment + TOC repair). The classes without one yet are: 2-D math, diagram/timeline semantics, elementary picture-based exercises — these must be **withheld by feature detection** (03 census flags them) until a formula-/diagram-capable path exists.
