# 04 — Bounded research notes (only where they change a decision) — LANE C, WAL-210

## 1. SGV pairing feasibility for LS&ĐL 5 Bài 8 (MEASURED on units-k12; marker level, no SGV text copied — D4)

- The SGV `05-sgv-lich-su-va-dia-li-5` **does carry a lesson counter that matches the SGK** (261 / 283 units with a lesson; lesson 8 = 9 units on PDF p74–77) — unlike TV5 tập hai's SGV (0 units with a lesson) and Tin học 6's (drift: Bài 2's «Đáp án: B» units tagged lesson 1).
- The 9 units are teacher guidance keyed by **section context, not enumerator**: «Khởi động — … trả lời câu hỏi: Những câu thơ nhắc đến sự kiện …», «Hoạt động — Kể tên một số cuộc đấu tranh …», «Hoạt động 2 — Kể chuyện …», «**3. Luyện tập Câu 1.** GV hướng dẫn HS hoàn thiện thông tin … trên trục thời gian», «4. Vận dụng», plus two reference stories (Bà Triệu, Phùng Hưng) under a «Tư liệu tham khảo»-type section. Answer-lexicon hits 4 / 9 («Gợi ý»); objective hits 3 / 9.
- **Consequence for H6 (pairing on section context + table cells):** for this lesson the key is (lesson, stage label «Luyện tập», «Câu N») — exactly the TC-14 recommendation and *not* the enumerator-only rule that keyed 2 / 26 on Science (DOC-CLAIM I.5). It is a HYPOTHESIS until measured on ≥ 20 SGV pages; the SGV Toán 6 structure (3-column lesson-plan tables, MEASURED in the units) confirms that Math pairing stays table-blocked on the Mac path.
- **Guard consequence:** the two reference stories are teacher-side material that reads like SGK content; the `teacher_text` / `answer_leak` guards (I.5: 711 blocks would have leaked on 75 SGV pages) must be in force before any SGV page is parsed for this lesson. The timeline key for Luyện tập 1 does **not** need the SGV at all — the pairs are in the SGK prose.

## 2. Role-layer needs for Bài 8's question types (what the Science lexicon lacks)

| block on p38–41 | today's role (Science lexicon) | needed | why |
|---|---|---|---|
| «Đọc thông tin, em hãy: – Kể tên … – Cho biết …» | one `question` or `body` ×3 | `question` + two `sub_question` (dash items) | one prompt per sub-item |
| «… quan sát các hình từ 1 đến 3, em hãy …» | withheld `figure_dependent` (561 Science regions) | keep withheld, route as OBSERVE (figure-first) | the lesson's main activity otherwise shows «SAM chưa đọc được» |
| «Câu chuyện Lịch sử» + story + «(Theo …)» | `heading` + `body` + `footnote` | `source` box with an `attribution` child | gold p041 critical classes: attribution detached; caption spliced into story |
| «TƯ LIỆU. Trong Chiếu dời đô …» (Bài 9) | `body` | `source` + `attribution` | SourceClaim requires attribution + page |
| Luyện tập 1 table («?» cells) | withheld (table-like page gate) | `table` with `cells` + `answer_slot` | the validator's target |
| Khởi động poem + attribution | `body` ×4 + `footnote` | `quote` + `attribution` | line breaks; the attribution is a licence fact |
| objectives, stage labels, «Em có biết?», «Hình N.» | `objective`, `stage_label`, `sidebar`, `caption` | — | PROVEN unchanged |

Precondition inherited from D3: no auto-labelled History question is graded until QUESTION precision ≥ 0.95 is measured on History gold (today n = 7 across 4 pages: 3 + 1 + 1 + 2).

## 3. Renderer-family gaps exposed by H1 (against 05-VISUAL §2 and Track B's `VisualView`)

| shape | data type today | derivation today | renderer today | gap |
|---|---|---|---|---|
| Timeline (prose-dated events) | `TimelineSemantic{events[]{when, title, text?, sourceBlockId}}` — exists | none | none (tab hidden when the list is empty) | rule `prose-dated-events-v1` + a horizontal/vertical timeline renderer with tap → source; **the figure-timeline path stays BLOCKED (TC-10) — this is the text path** |
| Source + attribution | `SourceClaim` in the Deep path only | none in Track B | `SourceCard` shows page provenance, not attribution | a `source` block kind rendered as «NGUỒN NÓI GÌ» with the attribution line verbatim |
| Timeline completion (answer slots) | none | none | none | a table with `answer_slot` cells + the validator; the census labels this task **DRAW_CREATE** (camera) — a mis-route, it is DIAGRAM_COMPLETE with a text-checkable key |
| Map (Bài 15, Bài 2) | `DiaMap` asset (curated) | curated | `MapReaderScreen` | unchanged — figure-only; not needed for H1 |
| Process / Comparison | as Bài 17 | rules fire on 68 / 6 of 238 Science lessons | `VisualView` | no Bài 8 data — the tabs must stay hidden honestly |

## 4. Learning-Surface gaps: the 27 patterns Bài 8 needs, mapped (registry counts are DOC-CLAIM, old-extractor)

| pattern in Bài 8 | where | registry unique / primary (LS&ĐL) | Surface today | verdict for H1 |
|---|---|---|---|---|
| EXPLAIN_SHORT («Cho biết … thể hiện điều gì?») | KHÁM PHÁ 1 | 874 / 229 | none | participation-only; **missing** |
| OBSERVE («quan sát các hình từ 1 đến 3») | KHÁM PHÁ 2 | 352 / 166 | none | figure-first, withheld today; **missing** |
| ORAL_SHARE («Kể câu chuyện», «Chia sẻ») | KHÁM PHÁ 2, LT 2 | 375 / 53 | none (voice) | participation only |
| DIAGRAM_COMPLETE (timeline table «?») | LUYỆN TẬP 1 | 120 / 59 (**LS&ĐL 31, its top subject**) | none | **the one gradable activity** — a small completion Surface or a typed Tutor answer; classifier says DRAW_CREATE |
| SOURCE_REASONING (stories + attribution; Bài 9 TƯ LIỆU) | stories | 42 / 23 (LS&ĐL 17) | `SourceReaderScreen` (ungraded stance) | exists — reuse NGUỒN / SAM / EM |
| RESEARCH_PROJECT («Sưu tầm», «Tìm hiểu di tích») | VẬN DỤNG | 288 / 15 (LS&ĐL 40) | none | out-of-app; participation only |
| READ_TEXT (poem; stories) | p38–41 | 253 / 151 | `ReaderScreen` / Đọc View | exists |

So H1 needs: one existing Surface family (SourceReader), one new small Surface or Tutor answer type (timeline completion), and honest withheld/participation handling for the rest — no mass implementation, no 27-pattern build-out.

## 5. Contradictions to report (not resolved here — CLAUDE.md rule 5)

1. **Gold lesson numbers on LS&ĐL 5 p041 and p080** contradict the printed headers (02 A17); the TC-v2 «lesson attach» score treats the correct header attachment as WRONG on both History pages. Owner: the gold set (RISKS #6, second human read).
2. **The activity classifier labels the timeline-completion task DRAW_CREATE** (camera modality, P2) although it is a text-checkable DIAGRAM_COMPLETE; the registry's «LS&ĐL: DIAGRAM_COMPLETE 31» is therefore an under-count and «DRAW_CREATE» an over-count for History. Owner: `fable_activity_taxonomy.py` (rule «vẽ» → DRAW_CREATE).
3. **units-k12 lesson counters drift** on Toán 6 (Bài 9 pages tagged lesson 7) and Tin học 6 (42 units tagged lesson 1 for a 3-page lesson; SGV «Đáp án» units of Bài 2 tagged lesson 1) — the same failure WAL-192 documented; any per-lesson count built on `units-k12` for those books inherits it.

## 6. What this lane did not do (by order)

No pack, no fixture, no Dart, no reprocess, no coverage claim, no «learnable/trusted» claim from detection (BROWSABLE ≠ LEARNABLE, ACTIVITY_PRESENT ≠ EVIDENCE_CAPABLE, TRACE ≠ EVIDENCE), no 27-pattern implementation, no edits to older `poc-out/` outputs, no verbatim SGK text or crops in the repo.
