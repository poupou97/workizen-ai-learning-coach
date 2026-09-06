# 05 — Golden Slice #2 gate: LS&ĐL 5 Bài 8 «Đấu tranh giành độc lập thời kì Bắc thuộc» (LANE C, round 4)

**Founder order (§7):** approve Candidate #2; before it becomes a product slice run five gate steps; build only if the gate passes; the slice must test what Bài 17 could not (prose-dated `TimelineSemantic`, historical source, attribution, lesson identity, deterministic `TimelineValidator`, History-specific tutor behaviour); do not copy the Science architecture mechanically.

**Verdict: PASS WITH WITHHOLDS — the bounded slice was built.** Steps 1, 2, 4 PASS; step 3 PASS for Bài 8 and PARTIAL for the book (5 / 28 lessons withheld, fix requested); step 5 PARTIAL (100 % block provenance; 2 / 3 attributions verbatim to the print, 1 carries two display-font tone slips that both OCR stacks agree on). Nothing here is production trust: every element stays `trustedStructuredLesson` / `prototype` under the «chưa kiểm định» chip, `licence = internalResearchOnly`, `auditStatus = notAudited`, `EvidencePolicy.none`. No coverage claim — one lesson, one book (denominators stated per table, D5). D4: crops, TSL and full SGK text live only in the gitignored `poc-out/round4/lane-c/` and `assets/fixtures/real/`; this document quotes anchors and single numbers only.

Evidence files: `poc-out/round4/lane-c/tc2-lsdl5/v1/` (sandboxed pipeline run: `root/poc-out/trusted-corpus/tc-v2/tc2-p1/{manifest.json,attach,sdm,lessons}`, `renders/` grid pages 37–42 + 80, `lesson-document/` bridge output + 23 crops, `history-rules/` augmented document + provenance report, `report/run-report.{json,md}`); repo copies: `docs/research/lane-c/data/lsdl5-run-report.md`, `data/lsdl5-bai8-second-review.json`. Scripts: `tool/research/lane_c/{lsdl5_run_report.py,history_rules.py,make_history_synthetic_fixture.py,test_history_rules.py}`. Pipeline code (`tool/corpus/**`) untouched — run with `TC_ROOT` pointing at a sandbox root whose inputs are symlinks.

## Step 1 — bounded TC-v2 run on LS&ĐL 5 · PASS (with a withhold on the opener page)

Whole book, unchanged `tc2-p1` chain (`tc2_run --fast` → docling-ocrmac 2 workers → `tc2_sdm` → `tc2_attach` → `tc2_tsl` → `tsl_to_lesson_document`), docling 2.126.0 / ocrmac 1.0.1, git `2e42487`:

| measure | value |
|---|---|
| pages | 123 / 123 docling ok, 0 errors; xycut 123; docling median 1.686 s, p90 2.139 s, **total 227.8 s** (the 3–4 min estimate held) |
| attachment | canonical 28 · TOC-ranged 10 · **headers detected 23** (6 TOC-confirmed, 17 header-only) · repaired-ranged 27 · rejected 0 · pages with a lesson 117 / 123 (6 front-matter) · printed offset +2 |
| TSL (23 lessons) | learning blocks **1 483 = 1 263 trusted + 220 withheld** (14.8 %) · figures 387 · withheld by reason: agree_text 115 · figure_dependent 39 · page_feature:color_heavy 23 · agree_order 21 · box_boundary 19 · page_feature:diagram 12 · low_ocr_conf 1 |
| **Bài 8** | boundary **PDF 38–41 (printed 36–39), confidence 0.95, source `both`, header found on p38**; sourceability PARTIAL; learning **51 = 34 trusted + 17 withheld**; roles trusted: body 14 · heading 8 · stage_label 5 · question 4 · caption 3; figures 14 (6 kept by the bridge's area rule); withheld: page_feature:color_heavy 14 · agree_text 3 (overlapping) · agree_order 2 · box_boundary 1 |
| per page (trusted / withheld) | **p38: 7 / 14** (only headings + stage labels trusted; 0 / 15 learning-text blocks) · p39: 12 / 2 · p40: 6 / 1 · p41: 9 / 0 |
| bridge | 58 document blocks = 41 `trustedStructuredLesson` + 17 `withheld` (image 6 · heading 8 · paragraph 14 · activity 5 · question 4 · caption 3 · provenance line 1); **deterministic**: two no-crops runs identical (`c7a1a7a9…`), with-crops `6b97c09e…`; semantic `[]`, chapters 0 (TOC says «Chủ đề», rule expects «Chương»), tutor script none — before the History rules |

Gate criteria from 03 §4 item 1: Bài 8 attached by header at ≥ 0.85 → **0.95 ✓**; the 7 dated events TRUSTED on p39 → **✓** (block `p039:tc2-p1:000`, text_sim 100, ocr_conf 1.0); p38 objectives and Khởi động «trusted or withheld with a reason the UI can state» → **withheld, reason `page_feature:color_heavy`** (page ≥ 25 % saturated colour) — stateable, but it takes the objectives, the Hồ Chí Minh poem + its attribution, KHÁM PHÁ question 1 with both sub-items, the two body paragraphs (incl. **«Âu Lạc (179 TCN)» — the first timeline anchor**) and the «Em có biết?» sidebar with it. **Withhold recorded; fix requested from A-pipeline** (block-level colour share instead of the page-level flag; the SDM already measures `colour.share` per block).

## Step 2 — independent second review · PASS

Lane C read the grid renders (never extractor output) of **every Bài 8 page (p38–41, first review)** and of **gold p041 / p080 (second review)**; judgments are anchors only (`data/lsdl5-bai8-second-review.json`); `lsdl5_run_report.py` scores them against the SDM and the gold.

**Bài 8 pages — Lane C vs pipeline (denominator: my learning blocks per page, figures/tables/page numbers excluded):**

| PDF page | my blocks | found | role agree | trusted | withheld | anchor verbatim | order inversions / pairs | pipeline blocks | pipeline-only |
|---|---|---|---|---|---|---|---|---|---|
| 38 | 19 | 19 | 15 | 7 | 12 | 16 | 0 / 136 | 22 | 3 |
| 39 | 13 | 13 | 9 | 12 | 1 | 9 | 0 / 66 | 14 | 1 |
| 40 | 9 | 9 | 8 | 6 | 3 | 6 | 0 / 21 | 7 | 0 |
| 41 | 9 | 9 | 8 | 9 | 0 | 8 | 0 / 21 | 9 | 0 |
| **total** | **50** | **50** | **40** | **34** | **16** | **39** | **0 / 244** | 52 | 4 |

The 10 role disagreements are all vocabulary the Science lexicon lacks: **attribution → body 4 / 4** («(Theo …)» ×3 trusted, «(Hồ Chí Minh …)» withheld), **dash sub-question / question lead → body 4** (p38 lead + sub-item, p39 sub-items ×2 — A01 on History), objective bullet «Sưu tầm …» → body 1 (verb not in the objective lexicon), story-box badge «Câu chuyện Lịch sử» → body CONFLICT 1. The 11 anchor slips are display-font tone marks (ĐẦU/KĨ, TRỮ/HÂN, BĨ, PHẢ/HÃN, «Sưu tẩm», «Tìm hiếu», «& pọc»), the hyphen for the printed en dash, and the «▲» caption marker read as «A». Reading order: **0 inversions in 244 pairs**. Figures: my 3 photos vs the pipeline's 14 regions (mascots and badges count as figures; the Lý Bí badge is mis-linked to caption «Hình 2» — the O5 class).

**Gold pages — gold vs pipeline vs Lane C:**

| page | printed | gold lesson | pipeline lesson (method) | Lane C lesson | gold blocks scored | found | role agree | trusted | text exact / with text | char diffs | order inv / pairs |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 41 | 39 | **9** | 8 (continuation, 0.95) | **8** | 10 | 10 | 8 | 9 | 7 / 9 | 7 | 1 / 28 |
| 80 | 78 | **17** | 18 (continuation, 0.85) | **18** | 7 | 7 | 5 | 5 | 3 / 6 | 54 | 0 / 10 |

p041: role misses = attribution (gold) → body, table (gold, «?» cells) → figure + figure_text withheld (fail-closed agreement, not a text emission); text misses = attribution b03 (3 chars: «Đăng»/«hóa»), question b10 («hiếu», 4); the one order inversion is the timeline figure's labels after question 2. p080: the 88 map labels are all `figure_text` withheld — the gold's most dangerous class («map labels emitted as body») **did not occur**; misses = legend/numbered-country boxes withheld as figure text (54 chars of linearisation difference), body b01 3 chars.

**Lane C vs the gold annotator: p041 11 / 11 blocks agree, p080 9 / 9 agree — and both lesson numbers are wrong in the gold** (9 → 8: printed «BÀI 8» on p38, «BÀI 9» on p42; 17 → 18: printed «BÀI 18» on p78 = printed 76, «BÀI 19» on p84; the gold's own title strings are already the right lessons). The pipeline's header attachment was right both times (A17 confirmed a second time). **Gold errata requested** (`tool/corpus/tc_gold/05-sgk-lich-su-va-dia-li-5-p041.json` lesson 9 → 8; `…-p080.json` lesson 17 → 18) — owned by A-pipeline; not edited here.

## Step 3 — header vs TOC · PASS for Bài 8, PARTIAL for the book

| status (28 lessons) | n | lessons |
|---|---|---|
| RESOLVED — header and TOC agree (± 1 printed page) | 6 | 1, 2, **8**, 9, 15, 21 |
| RESOLVED — header only, sequence-consistent (TOC has no page) | 17 | 4, 5, 6, 10, 12, 14, 16–20, 22, 24–28 |
| CONFLICT header vs TOC | **0** | — |
| **WITHHELD — header missed by the regex** | **5** | 3, 7, 11, 13, 23 |

**Bài 8 is unambiguous:** printed «BÀI 8» on PDF 38 (printed 36; TOC 36), next header «BÀI 9» on PDF 42 (TOC 40) ⇒ pages 38–41; confidence 0.95. The header rule's *title* is truncated («THỜI KĨ BẮC THUỘC» — the banner's first line lies 0.012 above the «BÀI 8» line and falls outside the rule's y-window); PROPOSED `lesson-title-v1` resolves deterministically to the printed TOC title when the lesson is header-confirmed-by-TOC and the header title is a diacritics-insensitive suffix of it → «Đấu tranh giành độc lập thời kì Bắc thuộc» (else the header title, fail closed).

**Withheld (not resolved here, listed):** Bài 3, 7, 11, 13, 23 — their banners OCR as «BÃI 3 / 7 / 11 / 13 / 23» (tilde tone slip); the pipeline regex `B[ÀÁẢẠ]I` has no `Ã`. A research probe with `Ã/ã` added finds **28 / 28 headers** and would move **17 / 123 pages** from lessons 2, 6, 10, 12, 22 to 3, 7, 11, 13, 23. **Fix requested from A-pipeline** (one character class in `LESSON_HDR`, `tc2_attach.py`; re-measure). Consequence today: TSLs for Bài 2/6/10/12/22 contain their successor's pages; Bài 8 is unaffected.

## Step 4 — proposed semantic / runtime rules · PASS (PROPOSED — nothing Founder-approved)

All rules are deterministic, run only on trusted blocks, keep block ids, and are implemented twice on purpose: in Python (`history_rules.py`, produces the fixture; 11 tests) and in Dart (`lib/core/lesson_model/timeline_*.dart`, consumes the fixture; tests below) — the two agree on the real document (test `fixture THẬT … chỉ khi máy có`).

| rule | statement | measured on Bài 8 |
|---|---|---|
| **`prose-dated-events-v1`** | in a trusted `body` block, «CapitalisedRun (Y[ TCN][ – Y])» ⇒ `TimelineEvent{when = parenthesised text verbatim, title = the run, text = enclosing clause verbatim, sourceBlockId, yearStart, yearEnd, era, charSpan}`; narrative years («năm 544») are counted, never promoted; withheld blocks never yield | **7 / 7 events** (Hai Bà Trưng 40–43 · Bà Triệu 248 · Lý Bí – Triệu Quang Phục 542–602 · Mai Thúc Loan 713–722 · Phùng Hưng 766–779 · Khúc Thừa Dụ 905 · Ngô Quyền 938), all from block `p039:tc2-p1:000`, chronological; narrative mentions not promoted: 2; **«179 TCN» not extractable** (its block is withheld on p38) |
| **`story-attribution-v1`** | a trusted text block «(Theo …)» or «(…, NXB …, YYYY)» closes a story = the preceding paragraphs back to the nearest heading (cross-page; images skipped; withheld parts listed); parse NXB + year only (authors/title not split — italics are lost); `complete ⇔ title found ∧ no withheld part` | **3 / 3 attributions** (2017 NXB Giáo dục Việt Nam · 2005 NXB Giáo dục · 2014 NXB Văn hóa Thông tin); stories: Trưng Vương 3 paragraphs complete · Lý Bí 1 paragraph + **1 withheld part ⇒ incomplete** · Ngô Quyền 3 paragraphs across p40→p41 complete |
| **`TimelineValidator`** (`timeline-order-v1`) | exists only when ≥ 2 events all parse (`TimelineDate.parse`, fail-closed: no centuries, no «năm N»); `checkPair(name, when)`, `checkOrder(names)`, `checkBefore(a, b)` return typed `TimelineCheck` with the source ids and a «sách viết …» reason; never writes evidence | available (7 dated events); book order chronological ✓; used by the «Thử xếp thứ tự» exercise in the timeline view (participation only) and by the tutor's q4 |
| **`history-tutor-v1`** | typed `TutorScript` (`prototype`, `prototypeScripted`): e1 explain (events block) · q1 **who/when** (option ask on event 1) · q2 **before/after** (two events, years withheld from the prompt) · q3 **cause/effect** (the story's concluding sentence before its attribution) · e2 **source awareness** (explain on the attribution block) · q4 the **verbatim** SGK «hoàn thiện trục thời gian» ask keyed to the extracted names/years · n1 next → Trực quan; ≤ 2 hints, `keySource` on every ask, answer-leak guard self-checked, patterns valid in Dart unicode `RegExp` | 7 steps; prompts grounded in 3 blocks; not used (listed): the figure-dependent question `p039:003` and the two withheld SGK questions `p038:010/:022` |
| `figure-dependent-question-v1` | «quan sát … hình» ⇒ never a tutor prompt (the pipeline's guard needs «Hình N») | 1 flagged |
| `lesson-title-v1` | see step 3 | TOC title chosen (diacritics-insensitive suffix) |

Boundary unchanged (03 §4 item 4): `fixtureFromTrustedCorpus`/`trustedStructuredLesson` chips, `EvidencePolicy.none`, `prototypeScripted`, no `LearningEvent`, no registered validator in Lane A-runtime's registry (the History validator is a pure function the view and tests call; registering it is a Founder/A-runtime decision).

## Step 5 — provenance · PARTIAL

Every timeline event and every attribution is traceable to page / bbox / block id — and each event to a character span inside its block (`history-rules/history-rules-report.md`):

| item | block | PDF (printed) | bbox | span / note |
|---|---|---|---|---|
| events 1–7 | `p039:tc2-p1:000` | 39 (37) | [0.075, 0.068, 0.835, 0.08] | spans [0,22] [24,38] [40,76] [78,103] [105,127] [129,147] [175,190] |
| attribution 1 (Trưng Vương) | `p039:tc2-p1:013` | 39 (37) | [0.214, 0.695, 0.678, 0.038] | verbatim to the print ✓ |
| attribution 2 (Lý Bí) | `p040:tc2-p1:005` | 40 (38) | [0.412, 0.334, 0.498, 0.039] | verbatim to the print ✓; story incomplete (`p040:003` withheld `box_boundary`) |
| attribution 3 (Ngô Quyền) | `p041:tc2-p1:002` | 41 (39) | [0.137, 0.331, 0.48, 0.055] | **not verbatim to the print: «Bạch Đăng» for «Bạch Đằng», «Văn hóa» for «Văn hoá»** (gold b03 char diff 3; `text_sim` = 100 — both OCR stacks agree on the slip) |

Verbatim checks: document text = TSL text 100 % (asserted by the bridge); events vs print: 7 / 7 names and 7 / 7 year figures exact, dash glyph «-» for the printed «–» on 7 / 7 (glyph only, both parse); attributions vs print 2 / 3 exact; the title now matches the print (TOC path). Carried as-is, not corrected by hand: the story headings' tone slips («TRỮ … HÂN», «BĨ», «PHẢ … HÃN») appear verbatim in the q3 prompt and the e2 explanation — the display-slip class of the false-trust audit, which `text_sim` cannot catch. **Why PARTIAL:** «attribution text is verbatim» holds for the pipeline's text, not for the print, on 1 / 3; the honest statement in the UI is «Kể theo: NXB Văn hóa Thông tin, 2014» (publisher + year, both exact).

## Verdict and what was built (bounded)

| step | verdict | withhold / request |
|---|---|---|
| 1 bounded run | **PASS** | p38 0 / 15 learning blocks trusted (page-level colour guard) → A-pipeline |
| 2 second review | **PASS** | 2 gold errata (lesson numbers) → gold owner |
| 3 header vs TOC | **PASS (Bài 8) · PARTIAL (book)** | 5 lessons withheld; `Ã` in `LESSON_HDR` → A-pipeline |
| 4 rules | **PASS (PROPOSED)** | registration of `timeline-order-v1` as a runtime validator → Founder / A-runtime |
| 5 provenance | **PARTIAL** | 1 / 3 attributions carries display slips → G1 display threshold |

Built (all under the «Bản thử nghiệm» chip; announced Lane B files in the PR): `lib/core/lesson_model/timeline_date.dart`, `timeline_sources.dart`, `timeline_validator.dart` (+ `workspace_catalog.dart` slot + research-slot marker); `lib/features/lesson_workspace/views/timeline_view.dart` (mốc · nguồn kể chuyện · thử xếp thứ tự) hooked from `visual_view.dart` (the inline timeline renderer moved there); Home «LÁT CẮT NGHIÊN CỨU · SÁCH LỚP 5 · BẢN THỬ NGHIỆM» card (`mission_center_screen.dart` `researchLessons`, `main.dart`) so the grade-6 learner on the device reaches the slice without a new profile; real fixture `assets/fixtures/real/lesson-05-sgk-lich-su-va-dia-li-5-b8.json` + 23 crops (gitignored); synthetic `[MẪU]` fixture (committed) generated by the same rules; tests: `timeline_date_test` (3), `timeline_history_test` (7, one real-if-present), `timeline_view_test` (3), `test_history_rules.py` (11). Not built: production packs, any coverage change, the 27-pattern registry, a registered runtime validator, SGV keys, an LLM.

## Contradictions and requests (CLAUDE.md rule 5 — reported, not resolved)

1. Gold `05-sgk-lich-su-va-dia-li-5-p041` lesson 9 and `-p080` lesson 17 contradict the printed headers (8 and 18) — second reviewer agrees with the pipeline; the TC-v2 attachment score on these two pages is inverted (A17).
2. `LESSON_HDR` lacks `Ã` — 5 / 28 LS&ĐL 5 lessons unranged and 17 pages misattached; `printed_offset`/sequence logic is fine.
3. The page-level `page_feature:color_heavy` guard withholds white-column body text on theme-opener pages (p38: 15 / 15 learning blocks).
4. The `figure_dependent` guard misses «quan sát các hình từ 1 đến 3» (question trusted, reaches the text universe).
5. Role lexicon: no `attribution`, no sub-question, «Sưu tầm» not an objective verb, story-box badge conflicts.
6. `toc-ocr-chapters-v1` returns 0 chapters for «Chủ đề» books (A06).
7. Persona / grade: the slice is a grade-5 book on a grade-6 learner's device — shown as a research card; the product rule for cross-grade lessons is a Founder decision.
