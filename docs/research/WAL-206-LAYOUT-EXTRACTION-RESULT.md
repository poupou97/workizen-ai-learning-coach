# WAL-206 — Layout-Aware K–12 Extraction: RESULT

**Verdict on the P0 experiment (exact WAL-204 re-run): FAIL — +3 new content-valid lessons against the ≥50 bar (0 regression).**
**Verdict on the layout blocker: SOLVED for the classes we can see — reading order 0.99 on the cross-subject gold set; no column-scrambled passage reached a Surface; four further splice classes found on the device were fixed at the layout level and are now fail-closed.**
**Next measured bottleneck: the Science family's dominant learner interaction is EXPLAIN_SHORT / OBSERVE — 166 of 185 recovered lessons carry no READ/MCQ/WRITE question — and SAM has no Surface for it.** A measurement-only variant that routes EXPLAIN_SHORT into the Reader (ungraded, open-ended) reaches **96 content-valid / +76 new lessons** with the same gate and 0 regression; 6 of them were walked on the Nokia and are device-valid. That is what a Short-Answer Surface would unlock. It is evidence, not a PASS.

Date: 2026-09-04 · Model: Fable 5.1 · Branch `wal-206-layout-extraction` (PR #54) · Jira WAL-206 · Founder order "WAL-204 FAIL ACCEPTED / P0 NEXT: Layout-Aware K–12 Extraction"

---

## 1. What was ordered, what was built

| Order item | Delivered | Where |
|---|---|---|
| General (not KHTN-specific) column-aware extraction with reading order, block roles, provenance, fail-closed | Recursive XY-cut over Apple-Vision line geometry + partial-height gutter split (box / columns) + floating-label rule; roles heading/body/question/caption/sidebar/footnote/pageNumber; page and region trust; every block carries book · page · region path · order · bbox · OCR conf | `tool/corpus/layout_extract.py` → `poc-out/layout/<book>/pNNN.json` |
| Corpus impact audit, automated | 18,661 / 61,031 non-sparse pages two-column (30.6%); 2,635 / 3,357 SGK lessons with a page range (78.5%) contain ≥1 two-column page | WAL-206 description (`tool/corpus/layout_census.py`) |
| Reuse first, no large new dependency without evidence | PDFs are scanned images (no text layer) → PDF-native order unavailable; zero new dependencies | tool audit in WAL-206 |
| Cross-subject gold set (order + roles) | 9 hand-read pages, 6 subjects, 9 layout families | `tool/corpus/layout_gold.py` |
| Re-run the EXACT WAL-204 experiment | `UNITS_SOURCE=layout`, same 6 books, same scope (READ_TEXT / SELECT_MCQ / WRITE_TEXT), same baseline, same bar | `tool/ui/pattern_router.py`, `tool/corpus/wal206_funnel.py` |
| Content quality gate (Reader-opens ≠ device-valid) | Deterministic Q1–Q8 gate applied twice — at the source (router refuses to emit) and as an audit over the built packs; rules live in one place so the two cannot drift; tightened four times from device evidence | `tool/corpus/content_quality_gate.py` ← `tool/ui/pattern_router.py` |
| Mandatory cascade funnel | §4 | `poc-out/p0-experiment/funnel-{exact,variant}.json` |
| Device validation | 6 lessons walked on the Nokia, grade-6 profile (§5) | `~/Desktop/wal-evidence/wal206-final-*.png`, `poc-out/p0-experiment/device-walk-notes.json` |

Not done, by order: the 27 Activity Patterns were **not** implemented (WAL-203/205 preserved). No manual lesson annotation, no LLM generation anywhere in the chain.

## 2. Layout extraction — MEASURED

Gold set (9 pages, 6 subjects): pairwise reading-order agreement, role accuracy, anchor recall, passage fidelity (no foreign block spliced in).

| | found | **order** | roles | fidelity |
|---|---|---|---|---|
| MEAN | 0.86 | **0.99** | 0.90 | 0.86 |

- Two-column pages (Tin học 9 p20, the WAL-204 falsification family) score 1.0 / 1.0 / 1.0.
- The WAL-204 page itself (KHTN 7 p20: pie-chart labels, a sidebar beside a figure, two captions) is **not solved — it is fail-closed**: the page is untrusted (a marginal y-cut and an unsplittable gutter run), so none of its text can become a passage. Honest score on that page: order 0.90, roles 0.71, fidelity 0.0. Its scrambled passage cannot ship; the routed KHTN 7 Bài 3 passage comes from the neighbouring page (and is itself rejected by human review, §5).
- Fail-closed works as specified: table-like pages, marginal cuts, >5% block overlap and unsplittable gutter runs mark the page/region untrusted; `layout_units.py` never turns untrusted blocks into passages. Family coverage: 185 / 194 TOC lessons have ≥1 trusted PASSAGE or QUESTION unit in range (95%).

Layout classes fixed **from device evidence** (each reproduced on the page, then generalised, then re-checked against the gold set):

| Device evidence | Layout class | Fix |
|---|---|---|
| KHTN 6 p21 — "1 gam (g) = 0,001 kg" inside the body paragraph | partial-height side box beside body, full-width lines above and below (no whole-region x-gap) | y-swept gutter run ≥3 lines each side, alignment guards → `ML/MR` regions; right side becomes `sidebar` |
| KHTN 6 p58 — "Tiến hành: chất rắn thu được và so sánh với Pha 3 - 5 thìa…" | two-column activity box under a full-width lead-in | same gutter run, `kind=columns` → `CL/CR` regions, both stay `body` |
| KHTN 6 p35 — "gọi là sự **Nước lỏng** bay hơi" | diagram labels 0.02 page-widths from the text, below the x-gap threshold | short narrow line far right of the region's text edge → its own `caption` block after the paragraph |
| Tin học 9 p20 regressed to 0.97 during the above | a justified column line ends 0.01 short of the gutter | gutter tolerance 0.6·TX; alignment guards keep pie-chart/scatter text out |

## 3. The exact WAL-204 re-run — MEASURED

Same 6 books (Khoa học 4–5, KHTN 6–9), same pipeline order (layout → TOC-range attach → activity pattern → router → Surface → SAM → evidence → device), same baseline (`baseline-learnable.json`: 113 proven / 32 in family), same regression oracle (khoaExperiments byte-identical in all 6 packs — **True** on every run).

| Configuration | routed lessons | content-valid | **new vs baseline** | device-valid (new) | regression |
|---|---|---|---|---|---|
| EXACT scope (READ_TEXT / SELECT_MCQ / WRITE_TEXT) | 5 | 5 | **+3** | 0 walked (grade 4/5/7 lessons; see §5) | 0 |
| Variant: + EXPLAIN_SHORT → Reader, ungraded (measurement only, **not** the ordered scope) | 96 | 96 | +76 | 6 (6) | 0 |

Bar: ≥50 new device-valid AND 0 regression. **EXACT = FAIL.** The variant is not claimed as PASS: it routes a pattern outside the ordered scope into a Surface not designed for it.

Trajectory of the exact number during this ticket, all on the same books: +18 (first layout run) → +6 → +4 → +3. Every step down was a real defect removed by a gate rule or a layout fix (§5). Per the order, the bar was not lowered; the gate was raised.

## 4. Mandatory cascade funnel (unique canonical lessons, Khoa học/KHTN 4–9)

| Step | EXACT | Variant | lost at this step |
|---|---|---|---|
| TOC lessons in the 6 books | 194 | 194 | (see the TOC finding below) |
| BEFORE proven (family / all) | 32 / 113 | 32 / 113 | — |
| recovered by layout extraction (≥1 trusted passage/question in range) | 185 | 185 | 9 fail-closed (untrusted/figure-only pages) |
| attached to a lesson (TOC range, capped) | 185 | 185 | 0 |
| with any recognised activity pattern | 176 | 176 | 9 no classifiable directive |
| with a pattern in the re-run scope | 24 | 24 (+ EXPLAIN 166) | **166 lessons have only EXPLAIN/OBSERVE questions** |
| routed (gate-at-source) | 5 | 96 | exact: 19 refused — figure-dependent 17 · lead-in 7 · deictic 4 · observe-figure 3 · objective-list passage 2 · pronunciation 1 · mid-sentence start · no passage 35 (activities) |
| content-valid (audit gate) | 5 | 96 | 0 |
| device-valid (Nokia, grade-6 profile) | — | 6 | |
| AFTER proven if device-valid ship (all / 3,679) | 113 + 3 = 116 (3.15%) | 113 + 6 walked = 119 (3.23%); 113 + 76 if all content-valid ship = 189 (5.14%) | |

**TOC finding (new, affects the denominator):** the canonical TOC for KHTN 7 stops at Bài 18 and KHTN 8 at Bài 22 (the printed books have ~40–45 lessons); Khoa học 4 lists 27 of 31, Khoa học 5 22 of 30. An open-ended last range attributed KHTN 7 pages 87–172 — some twenty later lessons — to "Bài 18", and the Q5 provenance check could not see it because the range itself was wrong. Ranges are now capped at 2.5× the book's median lesson length; pages beyond belong to no lesson (fail closed). The 3,679 denominator undercounts these books; the Trusted-Corpus track should re-derive it.

## 5. Content quality gate and the device walk — what was falsified

Rules were added only when the device or the built pack showed a real defect; each rule is shared by router and gate.

| Evidence | Defect class | Rule | removed |
|---|---|---|---|
| KHTN 6 Bài 2 Reader: "• Nêu được các quy định an toàn…" as the passage (`wal206-khtn6-bai2-reader.png`) | objective box as passage | `passage_is_objectives` | 37 activities |
| KHTN 6 Bài 1: "trong các vật sau đây, vật nào là vật sống" — objects are in a figure | bare "sau đây/dưới đây" with no inline list | `prompt_points_offpage` | |
| KHTN 6 Bài 18: "Đọc ý kiến trên … trả lời các câu hỏi sau:" | lead-in, real questions elsewhere | `LEADIN_RE` | 10 |
| "ý kiến trên", "hình bên", "trong các hình" | deictic to something the Surface cannot show | `DEICTIC_RE` | 28 |
| KHTN 8 Bài 2: "Đọc là: iron tác dụng với sulfur…" | pronunciation instruction | `PRONOUNCE_RE` | 1 lesson |
| KHTN 9 Bài 47: "quan sát các Hình 47.2…" | observe-a-figure in a text Surface | `OBSERVE_FIG_RE` | 1 lesson |
| KHTN 6 Bài 6: "1 gam (g) = 0,001 kg" in the passage | side box spliced (also fixed in layout) | `passage_has_spliced_box` | 2 |
| KHTN 9 Bài 26: passage begins "nước, hòa tan được…" | passage starts on a continuation line | `passage_starts_midsentence` | 12 activities / 7 lessons |

Device walk on the FINAL build (Nokia, `ai.workizen.learningcoach`, grade-6 learner "Na", KHTN 6; screenshots `wal206-final-khtn6-*.png`):

| Lesson | Passage | Question | Verdict |
|---|---|---|---|
| Bài 6 Đo khối lượng | clean after the side-box split | "Hãy mô tả một tình huống cho thấy sự cần thiết của việc ước lượng khối lượng" | valid (note: passage–question relevance weak) |
| Bài 10 Các thể của chất | experiment procedure, no spliced labels | "Nhận xét nhiệt độ của nước trong quá trình nước sôi" | valid |
| Bài 14 Một số nhiên liệu | coherent (heading glued as "(II …" prefix — cosmetic) | "nêu một số nguồn năng lượng khác có thể dùng để thay thế…" — answer in passage | valid |
| Bài 15 Lương thực, thực phẩm | coherent, matches print | "Tại sao cần phải bảo quản lương thực, thực phẩm đúng cách?" — answer in passage | valid |
| Bài 16 Hỗn hợp các chất | coherent after the two-column split | "Kể tên một số nhũ tương và huyền phù xung quanh em" | valid |
| Bài 17 Tách chất khỏi hỗn hợp | coherent procedure | "Tại sao phải mở khóa phễu chiết một cách từ từ?" — answer in passage | valid |
| Bài 1, 2 (earlier builds) | figure-dependent prompt; objective box | — | invalid → now refused by the gate |

Human review of the exact-scope lessons from pack content (not walkable: grade 4/5/7, and no learner profile was created on the Founder's device): Khoa học 4 Bài 25 and Khoa học 5 Bài 17 plausible; **KHTN 7 Bài 3 invalid** — the passage is an activity-card list ("12 tấm thẻ ghi thông tin (p, n)…") and the question ("đọc tên một số nguyên tố có trong thành phần không khí") is answered by the pie chart, not the text. The gate has no relevance check; this class (question not answerable from the paired passage) is the remaining human-review class — 1 of 5 exact-scope lessons, 0 of 6 walked variant lessons.

UX defects seen on the walk (not blocking this experiment, logged for Track C): the lesson chooser lists identical "Đọc bài" labels when a lesson has several readings; the Home card says "SAM chưa có nội dung lớp 6" while KHTN 6 has 22 routed lessons (Home reads the Deep path only); a "Bạn có biết?" Danh nhân excerpt starts mid-word ("ương pháp nhuộm Gram…").

Process note: one adb launch went to the wrong package (`com.workizen.tongtai`) and three touches landed in that app's empty Khách hàng tab before the foreground check — no data changed; the package id and a mandatory foreground check are now in memory.

## 6. Next measured bottleneck

166 / 185 recovered Science lessons carry only EXPLAIN_SHORT / OBSERVE questions. Their directives are clear ("Nêu…", "Tại sao…", "Kể tên…", "Quan sát…") — this is a **Surface gap**, not a detector gap: SAM has no learner-facing activity for a short free-text answer checked against textbook text, and none for "observe then describe".

- The variant proves the whole chain (layout → attach → pattern → route → gate → device) delivers +76 content-valid Science lessons, 6/6 walked device-valid, 0 regression — the moment such a Surface exists.
- Proposed P0-NEXT (first item of the WAL-205 backlog): **Short-Answer Surface** — passage + question, learner answers by voice/text, SAM gives ungraded guidance; fail-closed: no correct/incorrect without an SGV key, evidence records `correct: null`. OBSERVE stays multimodal (required modality: figure) and is not routed.
- Do not start the 27-pattern expansion; recalculating the registry only makes sense once the exact-scope experiment passes — and once the Trusted-Corpus track (running in parallel) has re-derived the lesson denominator.

## 7. Reproduce

```
python3 tool/corpus/layout_extract.py <book…>          # poc-out/layout/
python3 tool/corpus/layout_gold.py                      # MEAN found/order/roles/fidelity
python3 tool/corpus/layout_units.py <book…>             # poc-out/units-layout/
for g in 4 5 6 7 8 9; do PATTERN_ROUTER=1 UNITS_SOURCE=layout python3 tool/ui/build_lesson_index.py $g; done   # exact
python3 tool/corpus/content_quality_gate.py 4 5 6 7 8 9 && python3 tool/corpus/wal206_funnel.py
# variant: prefix ROUTE_EXPLAIN=1 to the build loop
```
Default builds (no env) leave every pack unchanged — the router is an experiment gate, not a product change.
