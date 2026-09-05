# D — Visual Learning (typed · source-grounded · fail-closed)

**Founder order (item 6):** Visual Learning must remain typed, source-grounded and fail-closed. This page states what the slice's source layer can and cannot feed a Visual Learning View, with numbers where they exist. No View was implemented.

## D.1 What "typed, source-grounded, fail-closed" means against the SDM (OBSERVED-IN-CODE / MEASURED)

| requirement | what the Trusted Structured Lesson gives today | status |
|---|---|---|
| **Typed** — a visual is rendered from a datum with a known shape, never from free text | `figures[]` (picture bbox + caption block id + label count) and `tables[]` (Docling cell grid, `cells[{r, c, text, header}]`) exist per page in the SDM (`tool/corpus/tc2_sdm.py`, `adapt_docling_v2`); the TSL carries `figures[]` per lesson. There is **no** `typedData` (no Concept/Process/Comparison datum) — the slice produced none and did not try to | figures/tables: source shapes exist; learning shapes: **absent** |
| **Source-grounded** — every visual element points at a page region | every figure carries `{page, bbox}`; every table block keeps `bbox` + cells; every withheld block keeps `{page, bbox, reasons}` | yes, by construction (B.1) |
| **Fail-closed** — when the datum is not trusted, nothing is drawn from text | tables are `TABLE` blocks; on the Mac path Docling flattens cells (TC-07: table role 1.00 precision but 0.55 recall on all gold; 1.00/1.00 on the 7 science gold tables) and the block is not a learning block for a text surface; diagram/map/picture pages are FIGURE-only by the page-feature guard (I.2) | yes for figures/diagrams; tables need a cell-level trust that does not exist yet |

## D.2 What the slice measured that matters for Visual Learning

- **Diagram pages are recognisable and can be failed closed.** On the held-out picture pages (KHTN 7 p26 periodic table; KHTN 9 p13 slide mock-ups; Khoa học 4 p6 colour-heavy opener) the pipeline withheld the figure text (`figure_text` 223 blocks, `page_feature:color_heavy` 48 on the held-out set — I.2) and trusted only headings/captions. The cost is visible on Khoa học 4 p6: its two real questions were withheld with the rest of the colour-heavy page — a measured price of the strict guard.
- **Figure ↔ caption association**: caption precision 0.75–0.86 / recall 0.78–0.91 on the science gold (I.3); `figures[].caption` is filled from adjacency (order ± 2). Good enough to *name* a figure, not to explain it.
- **Figure-dependent prompts are detectable**: `refers_figure` fires lexically ("Hình 20.1", "hình bên", "quan sát hình…"); on the slice it is the reason for withholding 8 (dev) / 5 (held-out) question-like blocks from a text surface. A Visual Learning View is exactly where those prompts belong — *with* the figure region.
- **Labels inside diagrams are text the OCR reads correctly but that geometry cannot order** (TC-06, TC-09 #3: timelines read row-wise). Nothing in this slice changed that; diagram labels stay `figure_text`, withheld, with bbox.

## D.3 What a Visual Learning View could consume from the TSL today (HYPOTHESIS, data-only)

1. `figures[]` with caption → an image region (subject to J.1) or, in `no_images` mode, a "see SGK page N, Hình 20.1" reference next to the trusted prose that refers to it.
2. `TABLE` blocks with cells → a native table **only after** a cell-level agreement gate exists (not built; the XY-cut verifier has no cells to agree with).
3. `refers_figure` question/activity blocks → prompts that a Visual View may show *next to* the figure and that a text View must never show alone (the guard already enforces the latter).

## D.4 Not done, on purpose

- No `ConceptRelation`, mind-map, process or comparison datum was inferred (WAL-207 `17` §2 item 5 — that would require LLM inference, forbidden as source truth).
- No rendering, no Flutter code, no image crops delivered anywhere except the review bundle (page crops for the Founder only).

**Verdict for the review:** the *source side* of Visual Learning (figure regions, captions, figure-dependent prompts, fail-closed diagram pages) is validated on the slice; the *typed learning datum* side is not started and needs its own gold before any View is built.
