# 08 — False-Trust Audit

**Definition (Founder order J/K).** A block SAM would teach from (gold roles body, question, option, heading, sidebar, caption, footnote, formula, objective, activity, rule, answer, attribution, speech bubble — 462 blocks on 38 pages) is **false-trusted** when the pipeline marks it trusted (or has no trust concept → implicitly trusted) AND at least one of: text error > 10 % of characters with ≥ 3 wrong characters (tone-placement variants hoá/hóa excluded), foreign text spliced in, emitted as a QUESTION although it is not one, or inverted with a same-column neighbour. **False trust rate (FTR) = false-trusted / trusted.** A block withheld by the pipeline is a **safe rejection**, never an error. **TLSR** = blocks delivered correctly AND trusted / all learning blocks.

## 1. Single candidates

| pipeline | trusted | false-trusted | **FTR** | safe rejections | TLSR | dominant reasons |
|---|---|---|---|---|---|---|
| current-naive (WAL-204) | 446 | 143 | **0.321** | 0 | 0.656 | splice 24, order 49, text |
| current-xycut (WAL-206) | 101 | 12 | **0.119** | 352 | 0.193 | text, as_question, order |
| docling-ocrmac | 439 | 63 | **0.143** | 0 | 0.814 | text (formulas, list enumerators), order 21 |
| mineru | 412 | 263 | 0.638 | 0 | 0.323 | text (no Vietnamese OCR) |
| marker (32 p) | 375 | 35 | **0.093** | 0 | 0.863 | text (formulas, empty PageHeader titles), splice 7 |
| vlm-mlx (31 p) | 318 | 85 | 0.267 | 0 | 0.615 | text on long blocks, splices |

## 2. Cascades (10) — the best measured trust

| cascade | coverage (trusted / 462) | TLSR | false-trusted | **FTR** | withheld | wrong kinds among trusted |
|---|---|---|---|---|---|---|
| docling ▸ xycut | 0.810 | 0.699 | 51 | 0.136 | 65 | cer 28, order 21, splice 6 |
| docling ▸ xycut + math guard | 0.766 | 0.673 | 43 | 0.121 | 85 | cer 23, order 18, splice 6 |
| marker ▸ docling (32 p) | 0.817 | 0.764 | 21 | **0.065** | 53 | cer 11, splice 9, order 4 |
| marker ▸ docling + math guard | 0.797 | 0.744 | 21 | 0.067 | 61 | cer 11, splice 9, order 4 |
| marker ▸ vlm (31 p) | 0.784 | 0.728 | 21 | 0.071 | 63 | cer 12, splice 8, order 4 |
| docling ▸ marker + vlm (3-way) | 0.699 | 0.607 | 35 | 0.132 | 94 | cer 19, order 15, splice 5 |

## 3. What the remaining false-trusted blocks are (marker ▸ docling, 18 blocks hand-checked on the first 24 pages; 21 on the final 32)

| # | kind | page / block | what a child would see | class |
|---|---|---|---|---|
| 5 | formula text both stacks flatten the same way | Toán 2 p48 "200 < 300" → "200 300"; Toán 3 p32 "7 × 2 = ?" | wrong or meaningless math | agreement cannot catch (same failure in both) |
| 2 | Marker PageHeader with empty text, Docling has it | KHTN 7 p20 "NGUYÊN TỐ HOÁ HỌC", Tin học 6 "INTERNET" | lesson title missing | scorer counts CER 1.0 on the Marker block; the cascade trusted it because the *verifier* had the text (gate compared the empty string? no — Marker's bbox-matched block had different text). Fix: reject empty-text blocks |
| 7 | splices on Tin học 9 p20 | summary box + question 1 merged; question + options merged | question text carries the summary | both stacks merged the same boxes |
| 2 | dialogue split differently (Tin học 6 p21 An/Minh) | passage half-delivered | scorer limitation (extension window) as much as pipeline |
| 2 | order: Tin học 6 headings "INTERNET" / "SAU BÀI NÀY EM SẼ" | heading after objectives | low harm |

**Honest reading:** after removing the two scorer-side cases, the best cascade still false-trusts **~17 of 322 blocks (≈ 5 %)**, and the residue is structural: (i) math notation that every OCR stack flattens identically, (ii) coloured boxes that both layout models merge, (iii) headers that one stack drops.

## 4. Why agreement does not go to zero

Agreement gates detect *disagreement*. Two stacks that share an OCR (Docling ▸ XY-cut) share every OCR error; two stacks that share a failure mode (all flatten fractions; both merge adjacent boxes) agree on the wrong answer. The math guard is the first deterministic rule of this kind (withhold blocks with math tokens no parser recognised as a formula); it removed 8 of the false-trusted blocks in docling ▸ xycut. Similar rules are needed for: coloured-box boundaries (withhold a block whose bbox spans two background colours), empty/heading blocks, figure-dependent questions ("hình 6", "Hình 7.7"), and model answers ("M:").

## 5. Against the Founder's expectations

| expectation | measured best | gap |
|---|---|---|
| text ≥ 99.5 % | 96.1 % (Marker, 32 p), 95.4 % (Docling) on hard pages; ≈ 99 % on plain prose blocks | 4 points on hard pages; the last 0.5 % is tone marks on decorative fonts and formulas |
| reading order ≥ 99 % | 99.1 % (Marker), 98.7 % (Docling) | met for prose; not for timelines / bubbles / 2-D math |
| lesson attachment ≥ 99 % | 28 / 38 pages (74 %) by TOC range | TOC gaps + non-lesson pages; needs header-based attachment |
| learning-block precision ≥ 98 % | question precision 0.69 (only labeller); coarse role accuracy ≤ 0.70 | no role layer exists |
| false trust < 0.1 % | **6.5 %** (best cascade, 32 pages), ≈ 5 % after scorer corrections | ~50× off on hard pages; plain prose pages: 0 of 15 blocks |
| critical teaching errors = 0 | 21 false-trusted blocks in the best cascade on 32 pages | not 0 |

The expectations are reachable only on the easy part of the corpus (plain prose, question boxes, sidebars) and only with a cascade; they are not reachable on math, elementary visual and box-dense pages with the stacks tested. That is the core input to the verdict (18).
