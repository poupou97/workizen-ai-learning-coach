# 14 — SGV Impact: how teacher books change under a structured source

**Corpus facts (03).** 220 SGV documents, 31,981 pages (51 % of all pages). SGV pages are structurally easier than SGK pages — figures 12.0 % vs 63.7 %, coloured boxes 4.5 % vs 41.8 %, side-by-side 24 % vs 34 % — but 3.8 % carry tables and 7.7 % carry formulas (worked solutions), and 24.5 % have a sidebar-like narrow stack (the "Lưu ý"/"Gợi ý" style).

**Gold evidence (04, 3 SGV pages + WAL-192 history).**

| page | what it showed |
|---|---|
| SGV Toán 7 p43 | the lesson plan is a 3-column table (CẤU PHẦN / MỤC ĐÍCH, YÊU CẦU / GỢI Ý THỰC HIỆN, ĐÁP ÁN); row cells reference SGK activity labels ("Ví dụ 3", "Luyện tập 3", "HĐ4/HĐ5"). Docling found the table (role TABLE) but returned cells as one flattened string; Marker returned a table object; the XY-cut split it into 40+ line blocks and withheld the page. **Pairing key = the activity label inside the table cell**, not a page number. |
| SGV Toán 4 p54 | flow diagrams (3 boxes + arrows) read as a sentence by every candidate; quoted teacher prompts ("Số đã cho gồm mấy trăm nghìn?") sit inside guidance prose; **model answers** ("Một trăm bảy mươi hai nghìn chín trăm ba mươi tám. Chữ số 3 thuộc hàng chục…") appear as ordinary text; **Tiết 2 starts mid-page**. 19 meaning inversions for Docling/xycut came from this page (duplicate headings "1. Khám phá" ×2 — a real SGV pattern). |
| SGV Tin học 10 p39 | **two lessons on one page** (Bài 4 ends with a binary-addition table, Bài 5 starts with objectives). Page-level attachment assigns the whole page to Bài 5 (`lesson_attach_wrong`). The TOC of `10-sgv-tin-hoc-10` is OK, but that does not help within a page. |
| SGV structure in `curriculum-structure.json` | `07-sgv-toan-7` has no usable lesson range for p43 (`toc=None`); SGV lessons are numbered like SGK lessons only in some series (WAL-192 found 4/10 grades with one clean format). |

## What changes with the structured model (11)

1. **SGV pairing moves from page ranges to relations.** `answer_of` links an SGV ĐÁP ÁN cell / "Bài 2:" paragraph to the SGK block with the same printed enumerator ("Bài 2", "HĐ4", "Câu 1"). This is exactly why Docling's **enumerator dropping (65 events)** is disqualifying for SGV pairing unless the source line text is kept (the XY-cut keeps it; Marker keeps it). Pairing must fail closed when the enumerator is missing on either side.
2. **Lesson boundaries inside a page** become representable (`continues`, `heading_path` = "Bài 5. DỮ LIỆU LÔGIC"); header-based attachment supersedes TOC ranges on any page that carries a lesson header. On the 38 gold pages, header-based attachment would have fixed 6 of the 10 wrong attachments (the 4 non-lesson pages need a "no lesson" rule).
3. **Role layer with SGV lexicon**: `GV …` sentences → TEACHER_GUIDANCE; quoted prompts inside guidance → TEACHER_PROMPT (never a learner QUESTION); "Đáp án:", "M:", "Lời giải" → ANSWER. These are lexical and cheap; without them SGV text leaks into the learner surface (09 #8).
4. **Tables are the SGV's main structure.** Only Marker returned tables as objects (1.00/1.00 on gold tables); Docling found half; MinerU/XY-cut none. For SGV lesson-plan tables the cell grid *is* the pairing — a table-capable path is a prerequisite for SGV pairing at scale, or the pairing must stay restricted to the prose-style SGV series (WAL-192's 4/10 grades).

## Numbers that would change (ESTIMATED from measured parts)

- SGV pages are ~52 % of pages; at Docling's measured 3.5–4.3 s/page (pilot, under contention) the SGV half costs ≈ 35 h; at Marker's 129 s/page it is infeasible on this Mac.
- WAL-192 found 2 / 9 candidate Tin học lessons HIGH_CONFIDENCE with the current method. With enumerator-preserving blocks + table objects + answer-role lexicon, the same pairing rule applies to every SGV page that has an enumerated ĐÁP ÁN structure; the *upper bound* is the share of SGV lessons whose format is enumerated (not measured here — needs an SGV format census, one day of work with the census tooling).
- Risk that does not change: **SGV answers must never be shown before the learner answers**; the answer-leak guard (10) is the fail-closed rule, and it needs the `answer_of` relation to exist.

## Recommendation for the SGV track (feeds 19)

Do not build SGV pairing on page ranges or Markdown. Build it on SDM relations after the SGK side has enumerator-preserving, role-labelled blocks; run an SGV format census first (cheap), then a 20-page SGV gold set (the current gold has 3).
