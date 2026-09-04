# 05 — Parser Bake-off on the Hard Gold Set (MEASURED)

**Setup.** Every candidate ran on the same single-page PDFs cut from the source scans (no re-encoding) on one Apple M1 / 16 GB, in isolated venvs (`.venv-bakeoff*`, gitignored, never project dependencies). Raw outputs: `poc-out/trusted-corpus/tc-v1/bakeoff/raw/<candidate>/`; normalisation `tool/corpus/tc_sdm.py`; scoring `tool/corpus/tc_score.py`; tables `bakeoff/scores.md` (regenerated at the end of the study — page counts for Marker / VLM are those completed at report time; their per-page cost made a full 38-page run take hours on this Mac).

| candidate | what it is | version | licence | offline | deterministic | Vietnamese OCR |
|---|---|---|---|---|---|---|
| current-naive | Apple Vision lines in file order (WAL-204 generic extractor) | macOS Vision | Apple OS | yes | yes | yes (accurate-vi) |
| current-xycut | WAL-206 `layout_extract.py` recursive XY-cut + roles + trust | repo | — | yes | yes | same OCR |
| docling-ocrmac | IBM Docling layout model (heron) + reading order; OCR via ocrmac = Apple Vision | Docling 2.126.0, ocrmac 1.0.1 | MIT | yes (models cached) | yes (CPU) | same OCR |
| mineru | MinerU pipeline backend (DocLayout-YOLO + PaddleOCR) | 3.4.5 | AGPL-3.0 | yes | yes | **no Vietnamese model** (`-l latin`; `vi` not offered) |
| marker | Marker 2 / Surya 2 (650M VLM via llama.cpp) layout + OCR | marker-pdf 2.0.0, surya 0.22.1, llama.cpp 0.3.0 | GPL-3.0 (+ commercial terms) | yes | near (sampling off) | yes |
| pymupdf4llm | PyMuPDF4LLM (auto-OCR via RapidOCR on scanned pages) | 1.28.2 | AGPL-3.0 | yes | yes | RapidOCR default model: **no Vietnamese** |
| vlm-mlx | Qwen2.5-VL-3B-Instruct 4-bit via mlx-vlm, prompted for blocks+roles+bboxes | mlx-vlm 0.6.17 | Apache-2.0 (model: Qwen licence) | yes | greedy (T=0) | yes |

Not runnable here: PaddleOCR-VL-1.5 (MLX port exists, but its layout stage PP-DocLayoutV2 is Paddle-only; not attempted within the time box), dots.ocr / MinerU2.5 VLM (GPU); Tesseract has no `vie` traineddata on this Mac (`eng, osd, snum` only) so PyMuPDF's Tesseract path was not available.

## 1. Results (38 gold pages, 462 learning blocks; Marker 32 pages, VLM 31 pages — final `scores.md`)

| metric (kept separate on purpose) | current-naive | current-xycut | docling-ocrmac | mineru | marker | vlm-mlx |
|---|---|---|---|---|---|---|
| gold blocks found | 0.970 | 0.979 | 0.963 | 0.762 | 0.860 | 0.777 |
| **text accuracy, diacritics kept** (tone placement normalised) | 0.902 | 0.907 | **0.954** | 0.828 | **0.961** | 0.944 |
| CER, tone marks removed | 0.091 | 0.087 | 0.041 | 0.149 | 0.035 | 0.051 |
| CER, all diacritics removed | 0.089 | 0.085 | 0.040 | 0.123 | 0.032 | 0.050 |
| reading order (pairwise, main flow) | 0.966 | 0.976 | 0.987 | 0.977 | **0.991** | 0.992 |
| meaning-changing inversions | 49 | 34 | 21 | 22 | **2** | 3 |
| fidelity (contiguous block clean) | 0.718 | 0.847 | 0.975 | 0.985 | 0.963 | 0.576 |
| cross-column splices | 24 | 17 | 6 | 2 | 7 | 12 |
| role accuracy (coarse) | — | 0.658 | 0.634 | 0.567 | 0.647 | 0.101 |
| question precision / recall | — | 0.70 / 0.69 | — / 0 | — / 0 | — / 0 | 1.00 / 0.04 |
| caption association | 0 | 0.82 | 0.69 | 0.83 | **0.95** | 0 |
| table role / formula role | 0 / 0 | 0 / 0 | 0.50 / 0 | 0 / 0 | **1.00 / 1.00** | 0 / 0 |
| digits/operators intact | 0.932 | 0.914 | 0.904 | 0.930 | 0.890 | 0.982 |
| provenance (bbox on every block) | 1.00 | 1.00 | 1.00 | 0.97 | 1.00 | **0** |
| **TLSR** (delivered correctly AND trusted) | 0.656 | 0.193 | **0.814** | 0.323 | **0.863** | 0.615 |
| trusted / withheld blocks | 446 / 0 | 101 / 352 | 439 / 0 | 412 / 0 | 375 / 0 | 318 / 0 |
| **false trust rate** | 0.321 | 0.119 | 0.143 | 0.638 | **0.093** | 0.267 |
| critical-teaching-error events (all output) | 103 | 121 | 130 | 45 | 36 | 26 |
| seconds / page (median, this Mac, with contention) | 0.00 | 0.02 | 2.4 (pilot 3.3: see 16) | 18.5 | **129** | 81 |

Only Docling and Marker beat the current pipeline on every fidelity axis. Neither reaches the Founder's targets (text ≥ 99.5 %, false trust < 0.1 %, zero critical errors).

## 2. What each candidate is good and bad at (evidence in `bakeoff/scores.md` per page)

- **Docling + Apple Vision** — best cost/quality: 2–4 s/page, clean paragraphs, sidebars separated, captions found (0.69), full provenance. Weaknesses: **drops list enumerators** ("1." stripped from `list_item`, 65 events → question numbering lost, which breaks SGV answer pairing); no QUESTION/SIDEBAR concept (sidebars come out as `text` and get spliced into the Markdown projection between paragraphs); speech bubbles and lead-in boxes ordered after the body; formulas flattened (31 corrupted-data events, mostly Toán/Vật lí); tables detected on half the table pages.
- **Marker / Surya 2** — best fidelity: 2 meaning-changing inversions on 32 pages, captions 0.95, tables and formulas recognised (Equation blocks), text 0.961. Weaknesses: **129 s/page on this Mac** (≈ 94 days for the corpus; needs a GPU), **PageHeader blocks carry empty text** (lesson titles like "NGUYÊN TỐ HOÁ HỌC" are lost — 100 % CER on those blocks), still splices boxes on Tin học 9 p20, GPL-3 licence.
- **MinerU** — excellent layout (2 splices, captions 0.83, reading order 0.977) but its OCR has no Vietnamese model: 24 % of blocks unmatched, text 0.828, every diacritic damaged ("nguyên tő khí him"). Its layout could be used with Apple Vision text (a hybrid not built here) at ~18 s/page.
- **PyMuPDF4LLM** — not applicable: no text layer, auto-RapidOCR without Vietnamese, one page tested (text 0.737) and stopped.
- **Local VLM (3B)** — surprisingly good text (0.933, digits 0.985) and reading order (0.991) but **ignored the requested format** (no bboxes, no roles → provenance 0, role accuracy 0.11), 83 s/page, and hallucination risk is untested at scale. Useful as a *verifier*, not as a parser (10).
- **Current XY-cut** — the only candidate with QUESTION/SIDEBAR roles and a trust gate; role precision 0.70/0.45 and the page-level gate cost 76 % coverage.

## 3. Per-feature view (from `bakeoff/family.md`, docling>xycut+mathguard cascade)

Plain prose pages: TLSR 1.00, false trust 0. Formula pages: TLSR 0.55, FTR 0.17. Speech-bubble pages: TLSR 0.48, FTR 0.25. Colour-heavy elementary pages: TLSR 0.36, FTR 0.30. Tables: FTR 0.19. Sidebar pages: FTR 0.087. Question-block pages: FTR 0.091. — The residual risk concentrates in **math notation, elementary visual pages, speech bubbles and tables**; prose, questions and sidebars are close to trustworthy under a cascade.

## 4. Verdict of the bake-off

No single parser wins every layout (Founder question 6/7): Marker is the most faithful (32 pages), Docling the only one that is fast enough and free, the current pipeline is behind both on every fidelity axis but ahead on roles. The rest of the study therefore evaluates cascades (10) and answers the product question on that basis (18).
