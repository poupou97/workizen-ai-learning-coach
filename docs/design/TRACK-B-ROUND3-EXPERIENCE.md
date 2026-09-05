# Track B — Round 3 · Experience lane (B1–B5) · Golden Slice KHTN 6 Bài 17

**Ticket:** WAL-210 · **Date:** 2026-09-05 · **Branch:** `lane-b/round3-experience` → base
`integration/round3-2026-09-05` · **Status:** READY FOR FOUNDER REVIEW — nothing merged.

Founder order (essence): keep the product VISIBLE; move the Golden Slice from 55–65 % Experience
Fidelity toward 75–85 % (directional); the Founder holding the phone must immediately see
**1 where the child is · 2 which lesson · 3 which ways to learn · 4 what SAM is doing · 5 why SAM
proposes that · 6 what to do next**; hybrid Smart Book; typed Visual renderer family; a visible
tutor loop that never shames, never fake-grades, creates no evidence; misleading UI defects;
evidence retention; five separate numbers, never averaged.

Boundary is unchanged and still machine-held: `ContentTrust`, one-value `EvidencePolicy {none}`,
`WithheldBlock` without a text field, `boundary_test.dart` (throwing store across the whole journey,
source grep of `lib/features/lesson_workspace/**`). Round 3 adds nothing that can write.

## 0. The six questions — answered from the Nokia frames (`docs/design/track-b-evidence/round3/`)

| # | Question | Where the Founder sees it | Frames |
|---|---|---|---|
| 1 | Where is the child? | Home card «BÀI HỌC SAM · BẢN THỬ NGHIỆM» → workspace header breadcrumb **«Giá sách › KHTN 6 › Chương IV»** on every workspace frame; back = Home or Chương depending on the entry | `round3-1-02-home-card`, `1-03-workspace-picker`, `1-24-back-home` |
| 2 | Which lesson? | «Bài 17 · Tách chất khỏi hỗn hợp» + «SGK KHTN 6 · trang 60–63» (pack title, TSL page range) | every workspace frame |
| 3 | Which ways to learn? | first open = **«Vào bài học»**: three cards *Đọc như sách · Trực quan hoá · Học cùng SAM*, each with counts from the document («16 đoạn · 8 hình · 11 câu hỏi · 4 chỗ SAM để trống», «Sơ đồ quy trình ×2 · Bảng so sánh · Bảng tóm tắt», «SAM hỏi 3 câu trong sách… (kịch bản thử nghiệm)»); the three tabs stay on top | `1-03`, `2-03` |
| 4 | What is SAM doing? | tutor header «SAM (kịch bản thử nghiệm)» + **runtime line «Runtime kiểm được 5/17 bước…»** + **phase strip** `Giải thích › Hỏi › Con trả lời › Gợi ý › Phản hồi › Tiếp` lit at the current phase; per-bubble label «SAM (runtime có kiểm)» / «SAM (kịch bản thử nghiệm)»; «Câu 1/3» | `1-12`, `1-14`…`1-22`, `2-05c` |
| 5 | Why does SAM propose that? | the proposed card carries **«SAM đề xuất cách này — vì sao?»** + the rule's reason; after entering a View the «SAM đề xuất» card keeps the full reason (no longer clipped) — reasons come from `NextBestLearningAction` (Founder A8 order) | `2-03` (R2), `2-04` (R3), `2-05` (R4 quoting the SGK question), `2-05c` (R5) |
| 6 | What next? | one button on the proposal card; tutor end card «Con đã đi qua 3/3 câu hỏi của sách cùng SAM» → «Đọc lại phần Em đã học» lands on the badge | `1-22`, `1-23` |

## 1. What changed, per Founder item

### B1 JOURNEY (`lib/features/lesson_workspace/lesson_workspace_screen.dart`, `widgets/mode_picker.dart`, `widgets/fixture_chip.dart`, `widgets/trust_sheet.dart`, `widgets/runtime_plan.dart`, `book_screen.dart`, `chapter_screen.dart`, `lib/features/mission/mission_center_screen.dart`, `lib/main.dart`)
- Home: «BÀI HỌC SAM · BẢN THỬ NGHIỆM» card for the workspace lesson of the learner's grade (grade-filtered via `WorkspaceCatalog.shared`; Bi · Lớp 7 gets none); the Track A G2 card is untouched.
- First open in a session = `ModePicker` (concept learning-view frame 3); re-open goes straight to the proposed View. Counts are computed from the `LessonDocument`, never typed in.
- Breadcrumb header; compact one-line trust chip with ⓘ → **«Nguồn & độ tin»** sheet (trust level in child words, semantic rule ids, scripted SAM + runtime line, «KHÔNG ghi bằng chứng», the six `BoundaryClaim`s, machine provenance).
- «SAM đề xuất» now comes from **Lane A-runtime's `NextBestLearningAction`** (Founder A8: Đọc → Trực quan → Học với SAM → mục lục); the prototype `nextActionFor` (visual-first) is no longer used by the UI — conflict listed under *Returned for Founder review*.
- Book screen: «Bài 16–17 ·» ranges on chapter rows; OCR chapter titles carry «Tên chương lấy từ mục lục in của sách (máy đọc, chưa soát) — có thể còn lỗi chữ.» (verbatim kept, case only).

### B2 SMART BOOK (`smart_book_view.dart`, `widgets/withheld_card.dart`, `widgets/source_sheet.dart`)
- Page chips «Trang 60 · 61 · 62 · 63» (≥48 dp) + «— trang N —» dividers in reading order, both from the blocks' printed pages (no page without a block).
- Consecutive figures render as one row as on the printed page; consecutive captions group under the row («Hình N» bold). The pipeline's `captionBlockId` is deliberately **not** used to pair captions (its link is wrong for `p062:fig05`, O5) — nothing is asserted that the data does not prove.
- 🎯 MỤC TIÊU · 📌 Em đã học · 💡 Em có biết? badges keyed on the book's own label text; image source line «Hình trong sách · SGK KHTN 6 · trang 60»; withheld card shows the child reason only, the machine code moved to the source sheet.
- Page/image crops stay internal (gitignored fixture, chip on every screen).

### B3 VISUAL (`visual_view.dart`)
- Tabs per **shape** (🔁 Sơ đồ quy trình · ⚖️ Bảng so sánh · 🕸️ Sơ đồ khái niệm · 🕰️ Dòng thời gian · 📋 Bảng tóm tắt) only for shapes the `SemanticData` carries; a shape with several diagrams gets a second chooser row («1 · Lọc nước…», «2 · Tách dầu ăn…»).
- `ProcessStep[]` → overview strip 1→2→3 + detailed nodes (withheld = grey placeholder + page); `ComparisonDimension[]` → table; **`ConceptRelation[]` → radial concept map** (deterministic hub = most-mentioned entity, labelled spokes via `CustomPaint`, off-hub relations as cards); **`TimelineEvent[]` → axis + dots**. Bài 17 carries only Process + Comparison ⇒ the other two tabs do not exist on device (fail closed); they are proven with typed data in `visual_view_test.dart`. `GeoEntity[] → Map` has no type in `semantic_data.dart` (Lane A-data) — not built.
- «Vì sao SAM chọn sơ đồ này» keeps the child explanation; rule ids moved behind «ⓘ Nguồn & luật xếp». No path lesson text → LLM → visual exists (boundary grep).

### B4 HỌC VỚI SAM (`tutor_view.dart`, `widgets/sam_bubble.dart`, `widgets/runtime_plan.dart`)
- Visible loop: phase strip, «Câu n/N», A/B/C/D letters (labels only — the matched string is the option text), end card counts questions **gone through** (participation), never a score.
- **Per-step labels from `PedagogyRuntime.planForScript`** (Lane A-runtime #69): on the real Bài 17 fixture 17 planned steps → **5 runtime-guided** (explain e1, three verbatim SGK asks, next) / **12 prototype** (hints `HINT_UNSOURCED`, feedback `KEY_NOT_VALIDATED`, scaffold `OVER_CAP_WITHOUT_VALIDATOR`, plus `GUARD:CITATION_FABRICATION` on one feedback text). The runtime writes no words; `validator` is `null` on every step ⇒ no evidence type exists for the workspace.
- The runtime guard exposed **3 answer leaks in prototype hints**; rewritten so they scaffold without naming the answer (synthetic q1#1, q2#0, q2#1 in `tool/fixtures/make_synthetic_fixture.py`; real-fixture q1#1 in `tool/fixtures/make_lesson_fixture.py`); `pedagogy_runtime_test` now pins zero leaks.
- Still prototype-marked wherever the runtime cannot prove a step; swap path = the same `PlannedStep.mode` (no UI change needed when Lane A-data adds `SamMode.runtimeGuided`).

### B5 UI DEFECTS (priority = misleading)
| Defect (audit 05 / device) | Fix | Where |
|---|---|---|
| Android app label `learning_coach` in system dialogs | «Học cùng SAM» | `android/app/src/main/AndroidManifest.xml` + guard test |
| Cold-start blank | Flutter side: `BootScreen` replaces the two blank `Scaffold`s (`lib/app/boot_screen.dart`, `main.dart`); native side: launch window = surface colour + mascot (`android/…/launch_background.xml`, `colors.xml`, `drawable-nodpi/launch_mascot.png`) — **native fix not yet on the device** (see §4) |
| Raw ids: sessions «khtn», «Kho khám phá» «06-sgk-ngu-van-6-tap-mot · trang 26», gallery source lines | `subject_display.dart`: `subjectDisplayName`, `childSourceLine`, `storySourceLine` + `knownBookTitles` filled from the pack; unknown ids stay raw (never invented); story pages read «trang PDF N» (that is what the data has) |
| Cross-grade gallery asset (Toán 6 showing Toán 5) | core filter in #69 (`LessonIndex.sourceAssetsFor`); UI narrows to the open book only |
| MapReader hard-coded grade «5» | grade from the map's book id, context fallback, no «tr. null» | `lib/features/geography/map_reader_screen.dart` |
| Machine reason codes / rule ids on child screens | moved into the source sheet / trust sheet | `withheld_card.dart`, `visual_view.dart` |
| TOC OCR titles | footnote + case-only normalisation; nothing corrected by hand | `book_screen.dart` |
| Figure/caption mismatch (O5) | UI no longer pairs by machine link; captions grouped in reading order | `smart_book_view.dart` |

## 2. Lane A consumption

- **Lane A-runtime (PR #69, CI green) — merged into this branch** (`809adac`): `PedagogyRuntime.planForScript`, `NextBestLearningAction`, `StudentLessonState.unseen`, `SemanticBindingRegistry.resolveFor`, core cross-grade asset filter. Lane B only consumes plans/actions (`widgets/runtime_plan.dart`); it constructs no `PlannedStep` / `EvidenceValidation`. The workspace still has no store, so Student State is always `unseen` (true: the workspace emits nothing).
- **Lane A-data (`a-data/round3-tsl-bridge-ft-audit`) — not consumed**: no PR yet at the time of writing; its branch rewrites `lesson_document.dart`/`content_trust.dart` and moves the fixture generator into `tool/corpus/tsl_to_lesson_document.py`. What would be swapped when it lands: the real fixture regenerated by their bridge (this branch keeps consuming `assets/fixtures/real/*.json` through `WorkspaceCatalog`), `SamMode.runtimeGuided` as a real enum value (today the UI reads `PlannedStepMode.childLabel`), and the **three hint strings above must be carried into `tsl_to_lesson_document.py`** (their file) — listed under *Returned for Founder review / hand-off*.

## 3. The five numbers (never averaged)

### 3a. EXPERIENCE FIDELITY vs the concept boards (judgement bands, before → after)

| Screen / View | Round 2 | Round 3 | Basis |
|---|---|---|---|
| Home | 35–45 % | 50–60 % | workspace card with lesson/chapter/pages/three ways (concept «Tiếp tục học»); still no bottom tabs / hero |
| Giá sách | 60–70 % | 60–70 % | unchanged |
| Sách (Book) | 55–65 % | 65–75 % | lesson ranges per chapter, TOC honesty; no Mục lục/Giới thiệu/Ghi chú tabs by scope |
| Chương | 55–65 % | 60–70 % | unchanged rows + «Đã xem (phiên này)»; no stars by doctrine |
| Vào bài học / mode picker | 65–75 % | 80–90 % | three cards + SAM đề xuất + reason ≈ concept frame 3 |
| Mode 1 Đọc | 55–65 % | 70–80 % | page navigation, dividers, figure rows, badges, source lines; no page-image mode |
| Mode 2 Trực quan | 50–60 % | 65–75 % | shape tabs, overview strip, renderer family; no illustrated nodes, no mindmap data for Bài 17 |
| Mode 3 Học với SAM | 55–65 % | 70–80 % | phase strip, Câu n/N, A/B/C/D, per-step runtime label, participation count; no «Chính xác 🎉» by doctrine |
| Next Action | 60–70 % | 75–85 % | Founder order via runtime, reason always visible, «vì sao» on the picker |
| **Overall** | **55–65 %** | **70–80 %** | the concept's «1 bài học – 3 cách học – 1 bước tiếp» is now legible on every frame; density/illustration and navigation chrome remain below the boards |

### 3b. SOURCE REALITY — visible content elements by `ContentTrust` (real fixture, `capabilityCensus()`, printed by `round3_metrics_test.dart`)
**97 visible elements**: `fixtureFromTrustedCorpus` **92** (13 headings, 16 paragraphs, 11 questions, 12 activities, 8 captions, 8 image regions, 4 withheld, 1 sourceRef, 9 semantic items, 10 chapters) · `prototype` **5** (tutor script steps) · `fixtureSynthetic` 0 · `trustedCorpus` 0.

### 3c. SOURCE TRUST — elements through a production-trusted path: **0 / 97** (no `trustedCorpus` element exists; the TSL is a research pipeline output — expected 0 until the false-trust audit gates pass).

### 3d. PEDAGOGY REALITY — tutor steps (real fixture, `PedagogyRuntime.planForScript`): **17 planned steps = 5 runtimeGuided / 12 prototypeScripted** (refusal codes present: `HINT_UNSOURCED`, `KEY_NOT_VALIDATED`, `OVER_CAP_WITHOUT_VALIDATOR`, `GUARD`). Synthetic CI fixture: 12 = 4 / 8.

### 3e. EVIDENCE REALITY — interactions creating validator-permitted evidence: **0 of 0 possible** (`PlannedStep.validator == null` on all 17 steps; `EvidencePolicy.none`; Sessions list unchanged on the device after the full journey — `round3-1-26-sessions-unchanged`). Interactions performed on device in iteration 1: 5 tutor answers, 2 hint requests, 3 View switches, 26 frames — none minted an event.

## 4. Device loop (Track C) — Nokia 6.1, «Na · Lớp 6», portrait, WiFi adb

Protocol: read-only `dumpsys window` / `dumpsys power` before every input; never wake/unlock/swipe on a lock; no profile/settings/data change. The first capture of iteration 1 was the Founder's notification shade — deleted; the shade was collapsed with `cmd statusbar collapse` (a service call, no touch). Keyboard frames are kept (no personal content).

| Iter | Build | Walked | Defects found → fixed |
|---|---|---|---|
| 1 | `3409527` · APK `c1091bc0…` | Home → card → picker → trust sheet → Trực quan (2 processes, withheld step, comparison) → Đọc (page chips, figure row, captions, page 61 withheld) → Học với SAM (explain, Q1 A/B/C/D, matched, Q2 free text, hint 1, hint 2, scaffold, Q3, end card) → «Đọc lại» anchor → Home → menu → Sessions (unchanged). 26 frames `round3-1-01…26`. | D-R3-01 raw id on «Bạn có biết?» → `bab7cab`; D-R3-03 proposal reason clipped → `297687e`; D-R3-07 machine code on withheld card → `297687e`; D-R3-08 sixth phase off-screen → `297687e`; D-R3-10 anchor clipped → `08af1bf`. Observed, not UI: D-R3-05 crop bleed (TSL bbox), D-R3-06 caption-like paragraph role (TSL). |
| 2 | `08af1bf` · APK `c27e8dff…` (with #69 merged) | native launch window (white — finding), Home, picker now proposing **Đọc** (Founder A8), Đọc → proposal Trực quan (reason unclipped, D-R3-03 verified), Trực quan → proposal Học với SAM quoting Q1 (R4). Then **the Founder picked up the phone** and walked the tutor by hand (`round3-2-05c`: «Lọc» → hint → «Cô cạn» → matched, proposal R5 «Về mục lục») — all agent input stopped at that moment. | Native launch window white → `e3e9e9e` (drawables) — **verified by guard test only, not on device**; D-R3-07/08/10, story source line, Book footnote, Chapter «Đã xem», runtime label on the explain bubble: **not captured on device in iteration 2** (widget-tested; prototype label on hint/feedback bubbles is visible in `2-05c`). |

Evidence retention: `tool/evidence/retain.py` → `docs/design/track-b-evidence/round3/MANIFEST.json` (git SHA, APK sha256, packVersion per pack, fixture provenance, device `getprop`, frame sha256s, step → result; a PASS without a frame is downgraded to UNVERIFIED). Frames also in `~/Desktop/wal-evidence/`.

## 5. Returned for Founder review (not decided here)
1. **Next-action rule order** — Founder A8 (Đọc → Trực quan → SAM) is now what the UI shows; Track B's prototype rule (Trực quan first when a process diagram exists) still exists in `core/lesson_model/next_action.dart` (Lane A-data's file) but is unused. One should be deleted or the other made an intent option.
2. **Hint text hand-off** — the three rewritten hints live in `tool/fixtures/*` on this branch; Lane A-data's `tool/corpus/tsl_to_lesson_document.py` (their pending PR) must carry the same strings or the real-fixture leak returns (`q1#1`).
3. **`SamMode.runtimeGuided`** — until Lane A-data adds it to `content_trust.dart`, the UI shows `PlannedStepMode.childLabel` per step; the one-value `SamMode` invariant is untouched.
4. **Story source pages** — «trang PDF 26» is honest to the data (`StoryItem.pagePdf`); a printed-page field would need the stories builder (Lane A-data).
5. **Native launch window** — rebuilt drawables not yet installed on the Nokia (Founder was using the device); one more install + one frame closes it.
6. Concept elements deliberately not built (doctrine): stars/percent on chapters, «Chính xác! 🎉», free chat with SAM, bottom tab bar, XP.

## 6. Tests
`flutter analyze` clean · `flutter test` **884 passed / 1 skipped / 0 failed** with packs + real fixture (baseline 788 / 1 on the integration branch, +#69's suites). Round-3 tests: `test/app/boot_and_label_test.dart`, `test/features/subjects/subject_display_test.dart`, `test/features/geography/map_source_line_test.dart`, `test/features/mission/home_workspace_card_test.dart`, `test/features/lesson_workspace/{workspace_screen,smart_book_view,visual_view,tutor_view,book_and_chapter,round3_metrics}_test.dart`, `tool/evidence/test_retain.py` (6, stdlib; not in CI's `tool/tests` discovery — Founder/PM to widen the path).

## 7. How to run
```
cp <main>/assets/pack/{lesson-index-g*.json,*.png,sam-units.db,sam-stories.db} assets/pack/ && cp <main>/assets/pack/covers/* assets/pack/covers/
TC_ROOT=<main> python3 tool/fixtures/make_lesson_fixture.py --out assets/fixtures/real   # real fixture (gitignored)
flutter analyze && flutter test && flutter build apk --debug
python3 tool/evidence/retain.py --round round3 --frames docs/design/track-b-evidence/round3 \
  --steps docs/design/track-b-evidence/round3/steps.json --apk build/app/outputs/flutter-apk/app-debug.apk \
  --fixture assets/fixtures/real/lesson-06-sgk-khoa-hoc-tu-nhien-6-b17.json --adb $ANDROID_HOME/platform-tools/adb --print
```
