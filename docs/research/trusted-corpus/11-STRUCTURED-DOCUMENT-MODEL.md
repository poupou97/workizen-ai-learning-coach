# 11 — Structured Document Model (SDM): Markdown is a projection, not the truth

**Status:** proposal backed by a working normaliser (`tool/corpus/tc_sdm.py`) that already maps seven extraction stacks onto one model and a scorer (`tc_score.py`) that measures it. Nothing here is adopted; it is what the evidence says the source layer must look like.

## 1. Why the current chain cannot be trusted structurally

Today: `PDF → Apple Vision lines (x, y, w, h, conf, text) → line sort (WAL-204) or XY-cut blocks (WAL-206) → units-k12 / units-layout JSON → Markdown / pack`. Provenance stops at the page; a unit has no bbox, no region, no column, no relation to the figure it talks about, no extraction method, and its "role" is a regex guess. Nothing downstream can ask "which part of the printed page does this come from and how sure are we?". That is exactly why WAL-204 shipped a scrambled passage with a heading as its question: the pipeline had no representation in which that failure is visible.

## 2. The model (one page)

```
SourceDocument   id, grade, subject, docType (SGK/SGV), volume, pdf sha256, page_count, scan_ppi
  Page           doc, pdf_page, printed_page (calibrated), size, render sha256, layout_features[] (census)
    Block        id = <doc>:p<NNN>:<parser>:<n>
                 order              reading order within the page (int), column (int|null), region_path
                 role               HEADING | BODY | QUESTION | OPTION | ANSWER | CAPTION | SIDEBAR |
                                    TABLE | FORMULA | FIGURE | FIGURE_TEXT | FOOTNOTE | ATTRIBUTION |
                                    OBJECTIVE | ACTIVITY | RULE | SPEECH_BUBBLE | RUNNING_HEAD | PAGENUM | UNKNOWN
                 text               NFC; for FORMULA/TABLE also a structured payload (latex / cells)
                 bbox               [x, y, w, h] normalised to the page (never optional)
                 heading_path       ["Bài 4", "3. Các nguyên tố khí hiếm"]
                 relations          caption_of, options_of, answer_of, refers_figure, continues (cross-page), part_of_box
                 lesson             {number, title, attach_method: header|toc_range|continuation, confidence}
                 provenance         extraction_method (e.g. docling-2.126+ocrmac), ocr_conf, model versions, run id
                 trust              {status: TRUSTED | WITHHELD | CONFLICT, reasons[], verifier agreements[]}
    Figure       bbox, kind (photo|drawing|diagram|map|chart), labels[] (FIGURE_TEXT blocks), caption → Block
    Table        bbox, cells[row][col] with spans, header rows, "?" cells flagged as answer slots
TrustedLearningSource   the subset of Blocks with trust.status == TRUSTED, grouped by lesson; this — not
                        Markdown, not units — is what LearningActivity / Pedagogy / SAM may read.
```

Markdown, `units-k12`, packs and retrieval indexes are **projections** generated from the SDM with a deterministic serializer; they carry the block ids so that anything shown to a child can be traced back to a page region. Debug renders (page image + block boxes) come from the same ids.

## 3. What the bake-off proved about the model (05, 07)

- Every candidate can be normalised into it (naive lines, XY-cut, Docling JSON, MinerU middle.json, Marker JSON, VLM text) — `tc_sdm.py`. Docling, MinerU and Marker deliver bbox + reading order + native labels; the current pipeline delivers bbox + regionPath; the VLM delivers text only.
- **No candidate has the roles a teaching pipeline needs.** QUESTION, OPTION, ANSWER, SIDEBAR, SPEECH_BUBBLE, OBJECTIVE, ACTIVITY do not exist in Docling/MinerU/Marker (they emit text / list_item / section_header). The current XY-cut has QUESTION and SIDEBAR but with precision 0.69 / 0.45 (07). Role assignment must therefore be a separate, deterministic, geometry + typography + lexicon stage on top of the layout parser, with its own trust flag — never inferred from Markdown.
- Relations matter for safety: `answer_of` / `options_of` (model answers "M:", "?" answer slots, SGV ĐÁP ÁN columns) are the difference between a question and a leaked answer (09).
- `continues` (cross-page) is needed on 25.8 % of pages (03); a page-level unit is wrong for 1 in 4 pages and for every SGV page where two lessons meet (gold #37).

## 4. Trust semantics (fail closed)

`trust.status` is set by the cascade (10): TRUSTED only when independent analyses agree on text and order and no deterministic guard fires (math guard, role conflict, figure-dependence, answer leak). Anything else is WITHHELD with reasons; CONFLICT when two stacks disagree materially. The projection layer must refuse to serialise WITHHELD/CONFLICT blocks into anything SAM reads; it may serialise them into a review queue.

## 5. Storage / cost of the model (MEASURED on the gold + pilot outputs)

Docling JSON ≈ 17.6 KB/page median, Marker ≈ 13 KB, MinerU ≈ 27 KB, current XY-cut ≈ 6 KB; an SDM page with two stacks + trust ≈ 30–40 KB → **~2–2.5 GB for 62,729 pages**, plus 200-dpi page renders only for withheld pages under review (≈ 0.3 MB each). Trivial next to the 11 GB of PDFs.

## 6. What must NOT be done

- Do not make Markdown the store and re-derive structure from it (headings from `#`, questions from "?").
- Do not let an LLM/VLM re-guess a block and write the guess back as the block (H).
- Do not attach a page to a lesson by page range alone when the page carries a lesson header or a `continues` relation that says otherwise (14).
