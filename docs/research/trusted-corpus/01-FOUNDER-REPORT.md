# 01 — Founder Report: Can the SGK/SGV corpus become a Trusted Learning Corpus?

*One page, non-technical. Everything below is measured on the real books unless it says ESTIMATED. Details and every number's source are in files 02–19.*

**CURRENT.** What SAM reads today comes from the OCR lines sorted top-to-bottom. On 38 deliberately hard pages from Toán, Tiếng Việt/Ngữ văn, Khoa học/KHTN/Vật lí, Lịch sử/Địa lí, Tin học and teacher books, **1 block in 3 that SAM would trust is wrong** (a sidebar sentence spliced into a paragraph, two boxes interleaved, options out of order, a heading served as a question). The WAL-206 fix (column-aware XY-cut) is safer but only because it **refuses 3 blocks in 4** on such pages — and 1 in 8 of what it still accepts is wrong. The OCR itself is not the problem: the same recognised text, arranged by a modern layout model, is right 95 % of the time instead of 90 %.

**TESTED ALTERNATIVE.** Seven pipelines on the same pages: the two current ones, Docling (IBM, free) with Apple's OCR, MinerU, Marker/Surya, PyMuPDF4LLM, and a local vision model. Then "cascades" where two independent analyses must agree before a block is trusted, plus deterministic guards (for example: if a block contains a fraction that no parser recognised as a formula, withhold it).

**BEST RESULT.** Docling + Apple OCR, checked by the XY-cut, on one Mac at 3.3 seconds a page: **77–85 % of learning blocks accepted**, false trust **12 %** on the hard pages and **0 %** on plain prose. With Marker as the checker (needs a GPU): false trust **6.5 %**. In a 150-page pilot on three books, the new source accepted 84 % of blocks where the current gate accepted 33 % of pages — on Toán 5 the current gate accepts 3 pages in 50.

**TRUST LEVEL.** Text accuracy 95–96 % on hard pages (≈ 99 % on ordinary prose), reading order 99 %, but **no pipeline knows what a question, an answer, an objective or a sidebar is** — the only labeller (ours) is right 7 times in 10. Lesson attachment by page range is wrong on 10 of 38 pages.

**COVERAGE.** 64 % of the 62,729 pages carry at least one hard layout feature; only 3 % of lessons are clean on every page. Lessons with no *unhandled* feature (formulas, diagrams, tables, picture-based elementary pages): **555 of 3,381 with a page range (16 %)** — and only 4 of 554 Toán lessons, 4 of 145 KHTN, 1 of 82 Vật lí. The rest can be **partially** sourced (prose and questions trusted, math and diagrams withheld).

**FALSE TRUST.** Your target < 0.1 %. Measured best: 6.5 % (GPU cascade, 32 pages) / 12 % (Mac cascade, 38 pages) on hard pages, 0 % on prose. The residue is "shared errors": every OCR flattens 1/5 into "1 5", two layout models merge the same adjacent boxes, so agreement cannot see them. Only rules can, and only some rules exist.

**CRITICAL ERRORS.** Not zero anywhere. 21 wrong-but-trusted blocks remained in the best cascade on 32 pages: flattened math, merged boxes, a dropped lesson title. Classes with no automatic defence yet: 2-D math, timelines/diagrams (every parser reads the top row of boxes first — a wrong chronology), picture-based exercises, two lessons on one page.

**COST.** Re-parsing all 62,729 pages with the Mac cascade: ≈ 58 hours, ≈ 2 GB. Marker on this Mac: 94 days (1–3 days on a GPU, ESTIMATED). This study: ≈ 6 hours of Mac time, no cloud spend. Human review, if we ship 100 lessons: ≈ 50–65 person-hours for the withheld blocks.

**VERDICT — GO WITH SOURCE ARCHITECTURE CHANGE.** The whole corpus cannot be ingested automatically at teaching-grade trust. A **block-level, fail-closed structured source** (not Markdown, not page ranges) with a layout model + independent checker + rules + a real role layer can make the prose/question part of the books trustworthy, growing from ≈ 16 % of lessons fully and most lessons partially. Math, diagrams and elementary picture pages must be shown as images with provenance, not as extracted text, until a formula-capable path is measured. **Do not reprocess the corpus yet; do not implement the 27 patterns; build the source layer first and re-run the WAL-206 funnel on a 2,680-page Science slice.**

## Before / After

| | Before (today) | After (measured cascade on one Mac) | After (with GPU checker) |
|---|---|---|---|
| blocks accepted for teaching | 24.9 % (XY-cut, pilot) / 100 % (naive) | 77–85 % | ≈ 80 % |
| false trust among accepted (hard pages) | 12 % (XY-cut) / 32 % (naive) | 12 % | 6.5 % |
| false trust on plain prose | not measured | 0 % | 0 % |
| text accuracy (hard pages) | 90 % | 95.4 % | 96.1 % |
| reading order | 97 % | 98.7 % | 99.1 % |
| questions labelled | 0.69 precision | none until the role layer exists | same |
| lessons fully sourceable | 0 at your bar | ≈ 555 (16 %) | same |
| cost per page | 0.02 s | 3.3 s | 129 s here / ≈ 1–2 s GPU |

## Three pictures to look at (bundle `renders/`)

1. **Current failure** — `07-sgk-khoa-hoc-tu-nhien-7-p032-crop-0.08-0.05-0.86-0.25.png`: body paragraph beside a blue box. Today's text: *"…có 7 nguyên tố là Các nguyên tử kim loại có nguyên tố khí hiếm…"* — false chemistry made from two true sentences.
2. **Improved extractor success** — same page, Docling: body paragraph whole, box separate, options A-B-C-D in order (`bakeoff/raw/docling-ocrmac/07-sgk-khoa-hoc-tu-nhien-7-p032.json`; the full page: `07-sgk-khoa-hoc-tu-nhien-7-p032.png`).
3. **Unresolved hard case** — `08-sgk-lich-su-va-dia-li-8-p071-crop-0.10-0.10-0.82-0.28.png` (timeline: every parser reads 1873 → 1878 → early XX → 1873–1909 → 1884 → 1890) and `05-sgk-toan-5-tap-mot-p021-crop-0.10-0.58-0.85-0.32.png` (fractions become "1 5 + 1 2 = 7 10" in every parser).
