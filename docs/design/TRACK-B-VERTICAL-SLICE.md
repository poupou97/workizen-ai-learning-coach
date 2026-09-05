# Track B — Lesson Workspace vertical slice (Đọc / Trực quan / Học với SAM)

**Ticket:** WAL-210 · **Date:** 2026-09-05 · **Branch:** `feat/wal-210-track-b-lesson-workspace` · **Status:** READY FOR FOUNDER REVIEW — nothing merged.

**Founder order (essence):** one learner × one real representative lesson × one complete journey
(Bookshelf → Book → Chapter → Lesson → Workspace) × three Views × one Next Action × real device —
without waiting for full-corpus readiness, without creating any Business/Learning Truth.

> **Boundary, machine-readable** (`lib/core/lesson_model/content_trust.dart`):
> `MOCK ≠ EVIDENCE · FIXTURE ≠ TRUSTED CORPUS · UI COMPLETION ≠ MASTERY · TAP ≠ COMPETENCE ·
> PROTOTYPE SAM ≠ PROVEN PEDAGOGY · SCREEN EXISTS ≠ CAPABILITY PROVEN` — `BoundaryClaim` enum;
> `EvidencePolicy` and `SamMode` are one-value enums (`none`, `prototypeScripted`), so there is no
> type with which the workspace could record evidence or pretend to be the real SAM.

## 1. What was built

| Layer | Files | What |
|---|---|---|
| Typed model | `lib/core/lesson_model/` — `content_trust.dart`, `lesson_document.dart`, `semantic_data.dart`, `tutor_script.dart`, `next_action.dart`, `workspace_catalog.dart` | `LessonDocument` (book, chapter, lesson, title, provenance with `ContentTrust`), `LessonBlock` sealed union (heading · paragraph · image(crop+bbox+page) · caption · table(rows, safe) · question · activity · **withheld(reason, page, bbox — no text field by construction)** · sourceRef), `SemanticData` union (ProcessStep[] · ComparisonDimension[] · ConceptRelation[] · TimelineEvent[]), `TutorScript` (explain / ask(acceptable patterns, ≤2 hints, scaffold, keySource) / next) + deterministic `TutorRunner`, `nextActionFor` (deterministic, no invented minutes), `WorkspaceCatalog` (real fixture if present, else synthetic), `capabilityCensus()` (counts every visible element by trust). |
| Screens | `lib/features/lesson_workspace/` | `BookScreen` (real cover + «Mục lục» by chapter from the printed TOC + one-tap legacy path), `ChapterScreen` (lesson rows; state = session TRACE «Chưa xem / Đã xem (phiên này)», never evidence), `LessonWorkspaceScreen` (header «Bài 17 · …», non-dismissable fixture chip, segmented [📖 Đọc] [✨ Trực quan] [🦉 Học với SAM], «SAM đề xuất» with a reason), `SmartBookView`, `VisualView`, `TutorView`, widgets (`FixtureChip`, `SamBubble`, `SourceCard`/`showSourceSheet`, `WithheldCard`), `WorkspaceTrace` (in-memory). |
| Entry point | `lib/features/subjects/book_shelf_screen.dart` | Books that have ≥1 workspace lesson open `BookScreen` (tile shows «55 bài · ✨ SAM»); all other books keep today's `SubjectHomeScreen` path. |
| Fixtures | `assets/fixtures/` (+ `README.md`, `.gitignore`), `tool/fixtures/make_lesson_fixture.py`, `tool/fixtures/make_synthetic_fixture.py` | Real fixture (gitignored, internal D4) generated from the TSL + SGK PDF crops; synthetic `[MẪU]` fixture (committed) for CI. |
| Tests | `test/core/lesson_model/` (5 files), `test/features/lesson_workspace/` (7 files) | 61 tests: (de)serialisation fail-closed, withheld-never-text, runner loop, next action, catalog fallback, per-screen widget tests, boundary gate (throwing fake `LearnerStore` across the whole journey, source grep for forbidden imports/calls, `git ls-files` on `assets/fixtures/real`, pubspec dirs). |

Not touched (owned by Track A): `subject_home_screen.dart`, `main.dart`, `lesson_index.dart`,
`learning_context.dart`, any reader/tutor/evidence code, packs, `tool/corpus`, `docs/research`.

## 2. The representative lesson — KHTN 6 · Bài 17 «Tách chất khỏi hỗn hợp»

Decided by the Founder addendum and confirmed by the data: TSL
`poc-out/trusted-corpus/tc-v2/tc2-p1/lessons/06-sgk-khoa-hoc-tu-nhien-6/bai-17.tsl.json`
(read-only; never edited). Why it is the right single lesson:

- Device-valid in WAL-206 (Bài 6/10/14/15/16/17 set) and pack-openable for «Na · Lớp 6».
- Boundary confidence 0.95 (header found on PDF p.61; printed pages 60–63; p.65 is Chương V/Bài 18 and correctly excluded by the blocks).
- 60 trusted blocks / **4 withheld** (3 `page_feature:diagram`, 1 `math_guard` — the «Rót nước đến 1/4 chai…» step), 19 figures (8 kept by the ≥3 % / caption rule), 8 captions, 11 questions, 2 instructions, 2 objectives, 5 sidebars → every block type of the model appears except `table` (Bài 17 has none; the synthetic fixture covers it).
- Two real experiments with enumerated steps (**Process**) and an «Em đã học» summary with parenthesised definitions (**Comparison**) — both derivable by a deterministic rule from trusted blocks; a concept map / timeline is *not* derivable, and the UI shows no tab for them.
- The real question «Tại sao phải mở khóa phễu chiết một cách từ từ?» (p.62) anchors the free-text tutor step.

## 3. Machine-readable boundary — how each inequality is enforced

| Inequality | Enforcement (type / test) |
|---|---|
| MOCK ≠ EVIDENCE | `EvidencePolicy { none }` only; `LessonDocument.fromJson` returns `null` for any other value; `boundary_test.dart` drives the full journey against a `LearnerStore` whose every write throws; source grep forbids `learner_store`, `learning_session`, `learning_evidence`, `session_recorder`, `recordSession(`, `appendSession(`, `LearningEvent(` in `lib/features/lesson_workspace/**` and `lib/core/lesson_model/**`. |
| FIXTURE ≠ TRUSTED CORPUS | `ContentTrust.trustedCorpus` exists but **no element carries it** (census test asserts); every fixture element is `fixtureFromTrustedCorpus`, `fixtureSynthetic` or `prototype`; `requiresFixtureChip` ⇒ `FixtureChip` on Book / Chapter / Workspace, no close button, no parameter to hide. |
| UI COMPLETION ≠ MASTERY | `WorkspaceTrace` is in-memory only; the label is «Đã xem (phiên này)»; the tutor end card says «SAM ghi nhận con đã THAM GIA, chưa phải bằng chứng con đã hiểu»; `nextActionFor` never says «đã hiểu» (test). |
| TAP ≠ COMPETENCE | No `LearningEvent` type is reachable from the workspace; taps change only `_view`/trace. |
| PROTOTYPE SAM ≠ PROVEN PEDAGOGY | `SamMode { prototypeScripted }` only; `SamMode.childLabel` = «SAM (kịch bản thử nghiệm)» rendered in the tutor header and on every SAM bubble; every `AskStep.keySource` must state it is not SGV (parse fails otherwise); scripts contain no `bannedAbilityPraise`, no «Chính xác!», no 🎉 (test). |
| SCREEN EXISTS ≠ CAPABILITY PROVEN | §5 below separates EXPERIENCE FIDELITY from REAL CAPABILITY RATIO; `capabilityCensus()` is machine-derived. |

## 4. Deterministic derivations (documented in `make_lesson_fixture.py`)

- `tsl-enumerated-steps-v1` → ProcessStep[]: after each `instruction` block, `body` blocks on the same page with `enumerator_restored = true`, in `order`, until a `question`/`heading` (except «Tiến hành:»); WITHHELD blocks in between become withheld steps. Bài 17: «Lọc nước từ hỗn hợp nước lẫn đất» (3 steps), «Tách dầu ăn khỏi nước» (step 1 withheld by `math_guard`, step 2 verbatim).
- `tsl-summary-parenthesis-v1` → Comparison: after the `stage_label` «Em đã học», body blocks matching `^[·•]\s*(.+?)\s*\((.+)\)\.?$` → entity × «Dùng để tách». Bài 17: Lọc / Lắng / Cô cạn / Chiết.
- `toc-ocr-chapters-v1` → ChapterRef[]: the printed MỤC LỤC (OCR, `poc-out/units-k12`) split on «CHƯƠNG <roman> - <title>»; lesson numbers = every «Bài N.» in the segment. 10 chapters; OCR errors kept verbatim (see Needs from Track A).
- Figures: TSL figure with area ≥ 3 % of the page, or ≥ 1 % with a linked caption; inserted in reading order before the first block on the same page whose y > the figure's centre y. Crops at 150 dpi with 1.2 % padding, `aspect` recorded so the UI reserves the box.
- Tutor script: hand-written **prototype** keyed to real block ids (prompts are verbatim SGK question blocks); emitted only for `06-sgk-khoa-hoc-tu-nhien-6` Bài 17 — any other TSL gets no script (no invented pedagogy).

## 5. Two percentages — never combined

### 5a. EXPERIENCE FIDELITY (how close this slice is to the concept boards)

Basis: screen-by-screen comparison of `concept/concept-ai-first/learning-view.png` (6 frames) and
`concept-chuong.png` (9 frames) against the device screenshots in `docs/design/track-b-evidence/`.
Ranges are judgement bands, not computed scores.

| Screen / View | Fidelity | What matches | What is missing / different (by decision or scope) |
|---|---|---|---|
| Giá sách | 60–70 % | real covers grid, grade title, ✨ marker on the workspace book | search / filter chips / bottom tabs (removed by doctrine); no % |
| Sách (Book) | 55–65 % | cover header, title, «Mục lục» grouped by Chương from the real TOC, one-tap legacy path | tabs Mục lục/Giới thiệu/Ghi chú, «Đã học 3/18 · 17 %» (no % by doctrine) |
| Chương | 55–65 % | chapter title, lesson rows with state, ✨ marker | stars (no stars by doctrine — «Đã xem (phiên này)» instead) |
| Vào bài học / mode picker | 65–75 % | three visible ways to learn + «SAM đề xuất» with a reason, opens on the proposed View | concept's three big cards → segmented control (16-UX-CONCEPT §3 «the only new control») |
| Mode 1 Đọc | 55–65 % | numbered headings, paragraphs, figure crops + captions, MỤC TIÊU / Em đã học badges, question boxes, source footer, font size, «Hỏi SAM về đoạn này» | pager «3 / 8», «Em có biết?» styled box (rendered as ⓘ box), table (Bài 17 has none), withheld placeholders instead of full-page fidelity |
| Mode 2 Trực quan | 50–60 % | sub-tabs per shape, process diagram with arrows, comparison table, «Bảng tóm tắt» fallback, «Vì sao SAM chọn sơ đồ này», tap → source | concept's mindmap (no ConceptRelation data — tab deliberately absent), illustrated nodes |
| Mode 3 Học với SAM | 55–65 % | SAM explains → asks (verbatim SGK question) → options / free text → hint ladder → feedback / scaffold → next; label «SAM (kịch bản thử nghiệm)»; end card | concept's «Chính xác! 🎉» (forbidden without a key), «Thử thách tiếp theo» card styling, free chat box |
| Next Action | 60–70 % | one action + reason on every workspace frame, end card → «Đọc lại phần Em đã học» | concept's «~5 phút» (no measured durations — omitted on purpose) |
| **Overall** | **55–65 %** | the whole «1 bài học – 3 cách học – 1 bước tiếp» journey exists end-to-end on a real device | illustration density, bottom navigation, progress visuals |

### 5b. REAL CAPABILITY RATIO (how much of what is visible is real)

Machine-derived from `LessonDocument.capabilityCensus()` on the real fixture (printed by
`test/core/lesson_model/lesson_document_test.dart` when the fixture is present):

| Element | Count | `ContentTrust` | Basis |
|---|---|---|---|
| block.heading | 13 | fixtureFromTrustedCorpus | verbatim TSL text, `tc2-p1` |
| block.paragraph | 16 | fixtureFromTrustedCorpus | verbatim |
| block.question | 11 | fixtureFromTrustedCorpus | verbatim; role confidence 0.78–0.92 (TC-07: not a graded prompt) |
| block.activity (objective / instruction / sidebar / stage label) | 12 | fixtureFromTrustedCorpus | verbatim |
| block.caption | 8 | fixtureFromTrustedCorpus | verbatim |
| block.image (source crop) | 8 | fixtureFromTrustedCorpus | real page region, **internal only (D4)** |
| block.withheld | 4 | fixtureFromTrustedCorpus | honest placeholders, no text |
| block.sourceRef | 1 | fixtureFromTrustedCorpus | derived from block pages |
| semantic · Process steps | 3 + 2 | fixtureFromTrustedCorpus | verbatim text; **structure by rule `tsl-enumerated-steps-v1` (unvalidated beyond this lesson)** |
| semantic · Comparison rows | 4 | fixtureFromTrustedCorpus | verbatim text; rule `tsl-summary-parenthesis-v1` |
| chapters | 10 | fixtureFromTrustedCorpus | printed TOC via OCR; rule `toc-ocr-chapters-v1`; 2 OCR errors visible |
| tutor steps | 5 | **prototype** | hand-written; answer keys are prototype, not SGV |
| next-action | 1 rule | prototype rule on fixture facts | `nextActionFor` |
| evidence writes | **0** | — | `EvidencePolicy.none` |

Ratios (denominator = 98 visible elements: 73 blocks + 9 semantic items + 10 chapters + 5 tutor steps + 1 next-action):

- **Content that is verbatim real SGK text / real page region:** 92 / 98 = **94 %** (all `fixtureFromTrustedCorpus`).
- **Content that is production-trusted (`trustedCorpus`):** 0 / 98 = **0 %** — the TSL is a research pipeline output, not the gated TrustedLearningSource (TC-10/11).
- **Structure / behaviour produced by a prototype rule or hand-written script:** 25 / 98 = **26 %** (9 semantic + 10 chapters + 5 tutor + 1 next-action).
- **Pedagogy runtime behind «Học với SAM»:** 0 % (scripted, no `PlannedAct`, no BKT, no LLM).
- **Learning evidence produced by the whole journey:** 0 events (by type and by test).

## 6. Track C — device loop log (Nokia over WiFi, «Na · Lớp 6», package `ai.workizen.learningcoach`)

Process notes: every input was preceded by a read-only `dumpsys window` / `dumpsys power` check; the
device was **unlocked and awake** when the walk started (the Founder had picked it up), and was in
**landscape** for iteration 1–2 (later rotated to portrait by the Founder). Two frames that showed the
Android launcher were deleted from the evidence (not our UI). Nothing was unlocked, no settings,
profiles or data were touched. The install (`adb install -r`) kept the Founder's app data.

Lesson learned (protocol): in landscape, a swipe **starting at y ≥ 1000** on this Nokia triggers the
system home gesture — both launcher frames came from that, not from the Founder. Keep swipe starts ≤ 950.

| Iter | Build | Steps walked | Defects found | Fixed in | Re-verified |
|---|---|---|---|---|---|
| 1 | commit `0cc6c55` (+tests) | Home → Môn học → Giá sách → KHTN 6 → Chương IV → Bài 17 → Trực quan (2 processes, withheld step, source sheet, «Xem trong Đọc») → Đọc top | D1 «Hỗn hợp. tách chất» lowercase after «.»; D2 two identical «Sơ đồ quy trình» tabs; D3 landscape: fixed chrome leaves ~225 px for the body; D4 «Xem trong Đọc» anchor landed early (images decode after the scroll) | D1/D2/D4 → `538174c` | iter 2: `trackb-2-03-book-chapters` (D1), `trackb-2-05-workspace-visual` (D2) |
| 2 | `538174c` | Home → … → Bài 17 → both process tabs → Bảng so sánh → Đọc (objectives, Hình 17.1, p.61) → Học với SAM (explain + SÁCH VIẾT card → Tiếp → Q1) | D5 image crops at full width (a portrait photo ≈ 2 600 px tall in landscape); D6 tutor auto-scroll to the bottom hides the question/options on a short viewport | D5 → `567b8b1`; D6 + D3 mitigation → `8222b35` | iter 3 (below) |
| 3 | `8222b35` (portrait) | Home → Giá sách → KHTN 6 → Chương IV → Bài 17 → Trực quan → Đọc (top, Hình 17.1, p.61 headings, withheld card + internal crop, question box → «Hỏi SAM về đoạn này») → Học với SAM (anchored, explain + SÁCH VIẾT, Tiếp, Q1 at top, wrong → hint 1, «Cô cạn» → matched, Q2 free text, keyboard) → back to Chương («Đã xem (phiên này)») | D7 the two Hình 17.1 photos were inserted in reverse order (same-row sort tie); D8 keyboard: fixed chrome + keyboard overflow the tutor by 60 px and hide the answer field | D7 → `f195ce8` (generator); D8 → `34672ad` | iter 4 (below) |
| 4 | `34672ad` (portrait) | Home → … → Bài 17 → Học với SAM (whole body scrolls) → Tiếp → Q1 (all 4 options visible) → «Cô cạn» matched → Q2 free text: keyboard open = no overflow, next-action card hidden, field + «Gửi» visible → ASCII answer → hint 1 → hint 2 (button reads «SAM đã gợi ý hết rồi») → second answer → scaffold («Ý trong sách là…», `sam-step-back`, source card) → Q3 → correct option → matched → end card «Con đã học cùng SAM phần này» → «Đọc lại phần Em đã học» → Đọc anchored exactly on the summary (D4 re-verified) → back to Chương («Đã xem (phiên này)») → Sách → Giá sách → Home | D9 the matched turn used the `sam-celebrate-independence` mascot — CELEBRATE is reserved for evidence-backed claims | D9 → `6151e0b` (matched turns use `sam-explain`; unit test forbids the celebrate mascot on any turn) | widget test; not re-walked on device (mascot asset swap only) |

### 6a. What the four iterations proved on the device

Every step of `TRACK-B-DEVICE-CHECKLIST.md` except 15 (font-size tap — widget-tested) and 25 (Sessions
screen — see the note below) was walked on the Nokia in portrait on build 4, after D1–D8 were fixed
and re-verified. The free-text answers were typed through `adb shell input text`, which cannot
carry Vietnamese diacritics, so both free-text attempts were deliberately *unmatched*: that is the
path that proves «never stuck, never shamed» (hint 1 → hint 2 → scaffold → next question). The
matched path was proved on the two option questions (Q1, Q3).

Sessions screen (step 25, `trackb-4-19-sessions-unchanged`): after four complete workspace journeys
with tutor answers, Home → «…» → Các phiên học lists exactly one session — «5/9 · khtn · học · 1 lượt
trả lời · có gợi ý nhỏ», the legacy Reader session recorded by this morning's audit — and nothing from
this branch. The workspace has no store by type (§3) and `boundary_test.dart` drives the same journey
against a throwing store; the device confirms it.

### 6b. Evidence index (`docs/design/track-b-evidence/`, copies in `~/Desktop/wal-evidence/`)

Iteration 1: `trackb-1-01-home` · `1-02-home-scrolled` · `1-03-bookshelf` (KHTN 6 «55 bài · ✨ SAM») ·
`1-04-book-khtn6` (cover, chip, Mục lục) · `1-05-book-chapters` (D1 visible) · `1-06-chapter-iv` ·
`1-07-workspace-visual` (opens on the proposed view; D2 visible) · `1-08-workspace-resumed` ·
`1-09-visual-withheld-step` · `1-10-visual-withheld-node` · `1-11-visual-source-sheet` ·
`1-12-read-anchored-from-visual` (D4 visible) · `1-13-read-top`.
Iteration 2: `trackb-2-01-home` (cold-start blank first frame — pre-existing, see audit) ·
`2-02-home-bottom` · `2-03-book-chapters` (D1 fixed) · `2-04-chapter-iv` · `2-05-workspace-visual`
(D2 fixed) · `2-06-visual-comparison` · `2-07-read-objectives` · `2-08-read-images` ·
`2-09-read-figure-17-1` (D5 visible) · `2-10-read-question-box` · `2-11-read-p61` ·
`2-12-tutor-explain` · `2-13-tutor-explain-source` · `2-14-tutor-tiep` · `2-15-tutor-ask-q1` (D6
visible) · `2-16-tutor-q1-options` (portrait, Đọc — the Founder had rotated) ·
`2-17-legacy-book-congnghe6` (a non-workspace book keeps the old Book Home).

Iteration 3 (build 3, portrait): `trackb-3-01-home` (blank cold-start frame, O1) · `3-02-home-bottom` ·
`3-03-bookshelf` · `3-04-book-khtn6` · `3-05-book-chapters` (O4 OCR titles visible) · `3-06-chapter-iv` ·
`3-07-workspace-visual` (D2 fixed, portrait) · `3-08-read-top` · `3-09-read-figure-17-1` (D5 fixed; D7
visible) · `3-10-read-p61` · `3-11-read-p61-activity` · `3-12-read-withheld-card` · `3-13-read-withheld-crop`
(internal crop revealed) · `3-14-read-question-box` · `3-15-read-question-sheet` · `3-16-tutor-anchored`
(«Hỏi SAM về đoạn này» carried the block) · `3-17-tutor-tiep` · `3-18-tutor-ask-q1` (D6 fixed) ·
`3-19-tutor-hint1` · `3-20-tutor-matched-q2` · `3-21-tutor-typed` (D8 visible: overflow + hidden field) ·
`3-22-chapter-da-xem` · `3-23-back-book` · `3-24-back-shelf`.
Iteration 4 (build 4, portrait): `trackb-4-01-workspace` · `4-02-tutor-tiep` (whole body scrolls) ·
`4-03-tutor-q1` · `4-04-tutor-matched-q2` · `4-05-tutor-keyboard` (D8 fixed) · `4-06-tutor-free-text-hint1`
· `4-07-tutor-hint2` · `4-08-tutor-typed2` · `4-09-tutor-scaffold-q3` · `4-10-tutor-scaffold` ·
`4-10b-tutor-q3-options` · `4-11-tutor-end-card` (D9 visible: celebrate mascot) · `4-12-tutor-end-card` ·
`4-13-read-anchored-em-da-hoc` (D4 fixed) · `4-14-chapter-da-xem` · `4-15-back-book` · `4-16-back-shelf` ·
`4-17-home-top` · `4-18-home-more-menu` · `4-19-sessions-unchanged`.

Page crops of the SGK appear inside some frames (e.g. `2-09`, `2-10`, `2-11`, `3-09`, `3-12`, `3-13`):
internal repo, Founder D4 — not for distribution.

## 7. The Founder's five questions (from the screenshots)

1. **Where is the child?** — `trackb-3-07-workspace-visual` / `4-01-workspace`: header «Bài 17 · Tách chất khỏi hỗn hợp / Chương IV · SGK KHTN 6 · trang 60–63»; the back stack is visible frame by frame: Giá sách (`3-03`) → KHTN 6 (`3-04`) → Chương IV (`3-06`) → Bài 17, and back again (`4-14` → `4-15` → `4-16` → `4-17`).
2. **What lesson?** — «Bài 17 · Tách chất khỏi hỗn hợp» — real title from the pack, real chapter from the printed TOC (`3-05`, `3-06`), real page range «trang 60–63» from the TSL blocks.
3. **The three ways to learn it?** — the segmented control [📖 Đọc] [✨ Trực quan] [🦉 Học với SAM] on every workspace frame; each View walked: Trực quan (`3-07`, `2-06`), Đọc (`3-08`…`3-15`), Học với SAM (`4-02`…`4-12`).
4. **What is SAM doing?** — «SAM đề xuất» with a reason on every frame (`3-07`: «Con đã xem sơ đồ — giờ đọc bài trong sách…»; `3-08`: «Con đã đọc — thử trả lời cùng SAM câu hỏi trong sách: «1. Quá trình làm muối…»»); in the tutor the label «SAM (kịch bản thử nghiệm)» and «SAM đi theo kịch bản viết sẵn — chưa phải SAM thật, không ghi bằng chứng học» (`3-16`), then explain → ask → hint → scaffold → feedback visibly (`4-03`…`4-11`).
5. **What happens next?** — the next-action button on the card (`3-07` → Đọc, `3-08` → Học với SAM, `3-16` → Về mục lục after all three), «Tiếp ▸» in the tutor (`4-02`), and the end card's «📖 Đọc lại phần «Em đã học» trong sách» (`4-12`) that lands exactly on that section (`4-13`).

## 8. Defects — found / fixed / open

Fixed on this branch: D1, D2, D4, D5, D6, D7, D8, D9 (see §6). Mitigated: D3 (compact chrome in
landscape; the portrait layout is the primary target). Open / observed, not in Track B scope:

- O1 Cold start shows a blank first frame (`trackb-2-01-home`) — pre-existing (audit §4 «Splash quote»).
- O2 Home still says «SAM chưa có nội dung lớp 6» while KHTN 6 Bài 17 has a workspace — `mission_data.dart` (Track A).
- O3 In landscape the fixed chrome still takes ~55 % of the height after D3; a collapsing header would be the real fix.
- O4 Chapter titles carry two OCR errors from the printed TOC («TỪ TỀ BÀO ĐỀN CƠ THỂ», «BẢU TRỜI») — kept verbatim by rule; needs the TOC gate (Track A).
- O5 TSL figure→caption link `p062:fig05 → :024 («Hình 17.3»)` is the 17.4 photo — a pipeline linkage finding, shown as-is.

## 9. Needs from Track A

1. A `trustedCorpus` `LessonDocument` producer (TrustedLearningSource → this JSON shape) so the chip can go away for real; the loader already prefers a real document and the model rejects anything else.
2. Chapter/TOC gate: `ChapterRef` from `curriculum-structure` (ContentNode CHAPTER/THEME) instead of the OCR rule; pack `lesson-index-g6.json` carries no chapter today.
3. `mission_data.dart` / Home: read the workspace catalog before saying «SAM chưa có nội dung lớp 6», and offer «Bài 17 · KHTN 6» as the Home recommendation.
4. Role layer ≥ 0.95 question precision (TC-07) before any `QuestionBlock` becomes a graded prompt; today the tutor's three prompts are verbatim but the keys are prototype.
5. `LearningContext.anchorBlockId` (12-STRUCTURED-LESSON §2 hypothesis) if the real tutor should receive «Hỏi SAM về đoạn này».
6. Figure bbox precision (TC-04 open) — 8 of 19 TSL figures were kept by an area/caption rule; the pipeline's caption links have at least one mislink (O5).

## 10. How to run

```
# real fixture (needs poc-out on this Mac); output is gitignored
TC_ROOT=/Users/alexnguyen/projects/workizen-ai-learning-coach python3 tool/fixtures/make_lesson_fixture.py --out assets/fixtures/real
python3 tool/fixtures/make_synthetic_fixture.py          # committed CI fixture
flutter analyze && flutter test                           # 61 Track B tests inside the suite
flutter build apk --debug                                 # with assets/pack/ + assets/fixtures/real/ copied in
```
