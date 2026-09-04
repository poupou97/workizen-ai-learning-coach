# 06 — Reading-Order Benchmark

**Definition.** Reading order is scored on the gold blocks the candidate found: pairwise agreement (1.0 = every pair in the printed order). Pairs that involve a block in a `flex_group` (a sidebar, a speech bubble, a box whose position relative to the main flow is not meaning-bearing) are skipped unless both blocks are in the same group; so the score measures the **main flow** a learner must follow. Separately, a **meaning-changing inversion** is an inverted pair of two learning blocks in the same column outside any flex group (steps of a worked solution, options of an MCQ, paragraphs of a text, timeline events).

| candidate | order (main flow) | pages with order = 1.0 | meaning-changing inversions | splices (two columns/boxes merged into one block) |
|---|---|---|---|---|
| current-naive | 0.966 | 17 / 38 | 49 | 24 |
| current-xycut | 0.976 | 20 / 38 | 34 | 17 |
| docling-ocrmac | 0.987 | 24 / 38 | 21 | 6 |
| mineru | 0.977 | — | 22 | 2 |
| marker (32 p) | 0.991 | — | **2** | 7 |
| vlm-mlx (31 p) | 0.992 | — | 3 | 12 |

(Per-page values: `bakeoff/scores.md`, column *order*.)

## Where order still breaks — by layout, with the page that shows it

| layout | what happens | who fails |
|---|---|---|
| **side-by-side boxes** (EM ĐÃ HỌC ∥ EM CÓ THỂ; Toán 5 p92 three definitions; Khoa học 4 p78) | lines of the two boxes alternate | naive always; XY-cut when the gap is marginal; Docling/Marker separate them |
| **body beside a sidebar** (KHTN 7 p32, Địa lí 10 p40, Vật lí 11 p105) | sidebar lines spliced into the paragraph | naive; XY-cut on 3 of 13 sidebar pages; Docling 1; Marker 1 |
| **options in a grid** (KHTN 7 p32 2×2, TV 4 p28 4×2) | column-wise instead of row-wise (A C B D) | XY-cut (A B D C); Docling correct; naive merges the row |
| **timeline boxes above/below an arrow** (LS&ĐL 8 p71) | top row then bottom row (1 3 6 2 4 5) — a wrong chronology | every candidate; only the marker numbers define the order, and no parser reads them |
| **speech bubbles / lead-in boxes** (KHTN 7 p20, Toán 3 p32, Toán 5 p21) | placed after the body or merged with figure labels | Docling/MinerU place them late (flex, not counted); naive merges them |
| **two-column text continuing from the previous page** (Tin học 9 p20, Ngữ văn 11 p39) | left/right interleave | naive; XY-cut correct; Docling/Marker correct |
| **long-division / stacked formulas** (Toán 7 p41, Toán 9 p29) | 2-D scheme linearised | all candidates; only Marker labels them Equation |
| **procedure lists with numbered photo labels** (Vật lí 10 p89, KHTN 9 p46) | labels (1)…(6) injected into the list | naive, XY-cut; Docling keeps them as separate short blocks |

## Findings

1. **Reading order is essentially solved for prose by the layout-model parsers** (0.987–0.992; Marker 2 inversions on 32 pages). The residue is not "columns" any more; it is *semantic* order that geometry cannot see (timelines, worked-example schemes, bubbles that belong before a section).
2. **The XY-cut's remaining inversions (34) are concentrated on math and elementary pages** (Toán 2/3/5, Khoa học 4) where boxes are close together and cuts are marginal — exactly the pages its gate withholds. Its order score on trusted pages is high, its coverage is not.
3. **A page-level order score hides block-level harm.** 0.966 (naive) looks fine but corresponds to 49 meaning-changing inversions and 24 splices on 38 pages — roughly two corrupted learning blocks per page.
4. Order agreement between two independent stacks (Docling ⟷ Marker/XY-cut) is a workable trust signal: in the cascade (10) order disagreement withheld 88 of 1,043 Docling blocks on the gold set, and 21 of the 51 false-trusted blocks that remained were still order errors — so the signal catches most, not all, of them.
