# 02 — Assumption ledger: what KHTN 6 Bài 17 baked into the architecture (LANE C, WAL-210)

Each row names an assumption that is *embedded* in Track B's typed model, generator or rules (file given), and marks it **PROVEN / FALSIFIED / UNTESTED** with the evidence. «FALSIFIED» means *as a general K-12 rule* — a rule may still be right for the slice it was written on, and the scope is stated. Evidence labels: MEASURED (this lane's scripts, `poc-out/round3/lane-c/`), DOC-CLAIM (cited study), HYPOTHESIS.

| # | assumption (where it lives) | status | evidence |
|---|---|---|---|
| A01 | A question is a numbered directive whose verbatim text can be the tutor prompt (`QuestionBlock`, `AskStep.prompt/promptBlockId`; generator `role == 'question'`) | **FALSIFIED** as universal | MEASURED 1,642 trusted Science questions: enumerated 70.2 %, end with «?» 50.8 %. LS&ĐL 5 p38–39: one directive + dash sub-items («em hãy: – Kể tên … – Cho biết …»). Toán 6 p35–38: HĐ1–HĐ6, «Ví dụ N / Giải», «Luyện tập N», «2.10.» enumerators. Gold Toán 9 p029: question precision 0.0 (n = 5). DOC-CLAIM: Science Q precision 0.889, gate ≥ 0.95 not met |
| A02 | Process = enumerated body blocks after an `instruction` block on the same page (`tsl-enumerated-steps-v1`) | **PROVEN (narrow)** | MEASURED 68 / 238 lessons (60 with ≥ 2 steps); 28 instruction lessons yield nothing; 30 / 181 processes hold a withheld step |
| A03 | Comparison = «Em đã học» bullets with a parenthesised definition (`tsl-summary-parenthesis-v1`) | **FALSIFIED** | MEASURED 6 / 238 lessons, all KHTN 6; the rule hard-codes «Các cách tách chất — sách tóm tắt» and «Dùng để tách» |
| A04 | Figures carry captions; caption ⇒ keep (`figure_kept`, `captionBlockId`) | **FALSIFIED** | MEASURED 33.6 % of 3,864 figures have a caption link; 42.3 % kept; O5 mislink; DOC-CLAIM caption association 0.75 (science) |
| A05 | One lesson = one TOC page range (`LessonProvenance.pagePdfStart/End`; `FixtureSlot(book, lessonNo)`; TOC-based `toc_ranges`) | **FALSIFIED** (TOC) · header attachment PROVEN on Science | MEASURED: 3,381 / 3,679 ranged; LS&ĐL 5 18 / 28 lessons without `pageStart`; Bài 9 and Bài 15 TOC ranges 10 and 25 pages vs **4 pages by printed header**; TV5 Bài 3 reading on printed 17–18, TOC `pageStart` 19 (G9 re-measured); Science TSL header found 238 / 238; LS&ĐL 5 one-line headers found 9 / 9 (p38, p42, p67–p92); TV5 split «Bài / 3» header at PDF 18 vs TOC PDF 20 (+2), «Bài / 18» at 94 vs 96; Toán 6 p35 OCRs as «BAI» with no number (boundary found, number unconfirmed) |
| A06 | Chapters = «CHƯƠNG <roman> – …» segments of the printed TOC (`toc-ocr-chapters-v1`) | **FALSIFIED** as universal | MEASURED OCR: LS&ĐL 5 «Chủ đề 3», «Chủ đề 4»; Tin học 6 «Chủ đề 1…6»; Toán 6 «CHƯƠNG» (rule works) |
| A07 | Withheld ≈ diagram or math («Lý do: sơ đồ» card) | **FALSIFIED** | MEASURED 2,160 withheld regions: visual/math reasons 44.7 %; `agree_text`/`agree_order` in 222 / 238 lessons; only 11 / 236 lessons are Bài 17-like |
| A08 | Every trusted TSL role maps onto a `LessonBlock` kind (`to_block`) | **FALSIFIED** for 60 / 238 | MEASURED 118 trusted blocks dropped: `activity` 50, `footnote` 64, `option` 4 |
| A09 | Tables arrive with `rows`; `safe` gates cell rendering (`TableBlock`) | **FALSIFIED** (Mac path) | MEASURED 0 / 20 trusted table blocks carry `cells`; 174 table regions withheld; DOC-CLAIM tables as objects are Marker-only (GPU, GPL) |
| A10 | The tutor check is a regex over normalised free text, ≤ 2 hints, then scaffold (`answerMatches`, `AskStep.acceptable`) | **FALSIFIED** as the only check kind (UNTESTED as pedagogy) | MEASURED answer shapes on the candidate pages: Toán 6 2.14 (a digit set per sub-item), 2.15 (a set of numbers), 2.10 (subset of a list); LS&ĐL 5 Luyện tập 1 (event → year pairs), «Kể tên» (list membership); Tin học 6 câu 1 (3 pairs). DOC-CLAIM: only two option questions matched on the device; free text was deliberately unmatched |
| A11 | Answer keys are prototype now; SGV keys are pairable by printed enumerator later (`keySource`) | **UNTESTED** (H6) | DOC-CLAIM I.5 enumerator pairing 2 / 26; MEASURED today: Tin học verifier 2 / 9 HIGH_CONFIDENCE (Tin học 6 Bài 6, 7); LS&ĐL 5 SGV lesson 8 carries «3. Luyện tập Câu 1 …» (section-context key, 04 §1) |
| A12 | Next-Action rule 1: a lesson with a Process should open on Trực quan (`nextActionFor`) | **UNTESTED** (pedagogy) | MEASURED reachable 68 / 238; the reason string presumes an experiment («sơ đồ quy trình») |
| A13 | Next-Action rule 3: a tutor script exists (`doc.tutorScript`) | **FALSIFIED** beyond Bài 17 | MEASURED `tutor_script_bai17()` → `None` for 237 / 238 |
| A14 | Printed page = the footer digit; one printed→PDF offset per book (`SourceRef.pagePrinted`, `printed_to_pdf_offset`) | **PROVEN** on the 5 candidate books | MEASURED clear modal offsets (+2 LS&ĐL 5, +1 Toán 6, +1 Toán 5, +1 TV5, +1 Tin học 6) |
| A15 | Trust is declared per element; nothing is `trustedCorpus`; the fixture chip cannot be hidden (`ContentTrust`, `requiresFixtureChip`) | **PROVEN** (by type) | DOC-CLAIM census 0 / 98 `trustedCorpus`; `EvidencePolicy { none }` |
| A16 | The Role Layer lexicon transfers across families (stage labels, «Em có biết», directive verbs) | **FALSIFIED** | DOC-CLAIM SIDEBAR 0.96 science vs 0.44 dev; MEASURED gold Toán 9 p029 Q 0.0 / FTR 0.9; Toán 6 conventions (HĐ, Ví dụ, Giải, Thử thách nhỏ) absent from the lexicon; LS&ĐL «Câu chuyện Lịch sử» / «TƯ LIỆU» boxes absent |
| A17 | Gold lesson numbers are right, so a «lesson attach WRONG» row is a pipeline error | **FALSIFIED** on LS&ĐL 5 | MEASURED printed headers: p38 «BÀI 8», p42 «BÀI 9» → p41 is Bài 8 (gold says 9); p74 «BÀI 17», p78 «BÀI 18» (Chủ đề 4) → p80 (Trung Quốc geography) is Bài 18 (gold says 17). The header method was right both times; the History attachment score is inverted. **Contradiction to report, not resolved here** (single VLM annotator, RISKS #6/#8) |
| A18 | The workspace journey Bookshelf → Book → Chapter → Lesson is subject-agnostic (`WorkspaceCatalog.defaultSlots`, `ChapterRef`) | **UNTESTED** beyond KHTN 6 | structurally keyed by `book#lessonNo`; chapters depend on A06 |
| A19 | A lesson's question universe = its trusted questions | **FALSIFIED** | MEASURED 648 withheld question regions (28.3 %), 561 `figure_dependent`; 188 / 238 lessons |
| A20 | A lesson fits 2–5 pages and one boundary | **PROVEN** on Science, differs elsewhere | MEASURED 190 / 238 in 2–5 pages; LS&ĐL 5 candidates 4 pages by header; TV5 «Bài 3» = Đọc + LTVC + Viết over 5 pages while the TOC lists three sub-lessons |
| A21 | Page crops may be shown to the learner («Xem hình trong sách» with crop) | **UNTESTED** (legal gate J.1; D4 internal) | DOC-CLAIM |
| A22 | Every lesson has an «Em đã học» summary (end-card anchor «Đọc lại phần Em đã học») | **FALSIFIED** as universal | MEASURED 209 / 238 Science; LS&ĐL 5 Bài 8 and Toán 6 Bài 9 have no such label (LUYỆN TẬP / VẬN DỤNG, «EM CÓ BIẾT?» only) |

**Counts: PROVEN 5 (A02, A14, A15, A20 + header attachment inside A05) · FALSIFIED 14 (A01, A03, A04, A05-TOC, A06, A07, A08, A09, A10, A13, A16, A17, A19, A22) · UNTESTED 4 (A11, A12, A18, A21).**

What the pattern says: the assumptions that hold are all *document-layer* (trust per element, source lines, printed pages, header boundaries). The ones that fail are the *semantic* and *tutor* layers plus every «convention» string copied from KHTN 6's page furniture. That is the shape a second lesson must attack.

## Round 4 update — LS&ĐL 5 Bài 8 run through the unchanged pipeline, bridge and model (Lane C, 2026-09-05)

Evidence: `05-GOLDEN-SLICE-2-GATE.md` (numbers), `06-HISTORY-ABSTRACTIONS.md` (reading). MEASURED unless marked. The round-3 statuses above stand; this table adds what History did to each.

| # | on History (Bài 8) | status | evidence |
|---|---|---|---|
| A01 | dash sub-questions and the question lead are `body`; 4 / 4 (+ 4 more withheld on p38) | FALSIFIED again | second review vs pipeline: question → body ×4 trusted |
| A02 | no `instruction` block ⇒ no Process; nothing to test | n/a | 0 processes |
| A04 | 3 photos with captions; 14 pipeline figure regions (badges, mascots); 1 caption mis-link (Lý Bí badge → «Hình 2») | FALSIFIED again | figures table |
| A05 | header + TOC agree on Bài 8 (0.95); 18 / 28 TOC pages missing; 5 / 28 headers missed by one character class | header attachment PROVEN · TOC FALSIFIED · **regex gap found** | step 3 |
| A06 | 0 chapters («Chủ đề») | FALSIFIED again | bridge output |
| A07 | withheld reasons on Bài 8: colour-heavy 14, agree_text 3, agree_order 2, box_boundary 1 — none diagram/math | FALSIFIED again | TSL stats |
| A08 | attribution has no block kind — worked around by a Dart derivation over `body` blocks | FALSIFIED · mitigated | `timeline_sources.dart` |
| A09 | the timeline table is a figure with 5 `figure_text` labels; no cells | FALSIFIED again | p41 fig01 |
| A10 | the check is a typed validator (`TimelineValidator`) over the lesson's own prose; regex remains only for the option asks | FALSIFIED (as the only kind) | `timeline_validator.dart` |
| A13 | no script existed; a typed one was **generated** from the timeline + sources (7 steps) | FALSIFIED (hand-written) · new path | `history-tutor-v1` |
| A14 | printed offset +2, all 4 pages carry a printed number | PROVEN | attach |
| A15 | every element declares trust; chip mandatory; slice reachable only as «LÁT CẮT NGHIÊN CỨU · BẢN THỬ NGHIỆM» | PROVEN | Home card, fixture |
| A16 | lexicon gaps on History: attribution, sub-question, «Sưu tầm» objective, story-box badge | FALSIFIED again | step 2 disagreements |
| A17 | both LS&ĐL 5 gold lesson numbers wrong; header method right (second reviewer agrees) | FALSIFIED (gold) | step 2 |
| A18 | journey keyed by `book#lessonNo` worked; chapters absent; Bookshelf is grade-gated ⇒ needed the Home research card | UNTESTED → PARTIAL | `researchLessons` |
| A19 | figure-dependent question («quan sát các hình từ 1 đến 3») **trusted** and reaching the text universe — the guard missed it | FALSIFIED (in the other direction) | `figure-dependent-question-v1` |
| A20 | 4 pages, one boundary | PROVEN | boundary |
| A21 | crops rendered, internal only (23 files, gitignored) | UNTESTED (J.1) | — |
| A22 | no «Em đã học»; the summary tab falls back to objectives (withheld on p38 ⇒ empty) | FALSIFIED again | VisualView summary |
| **A23** (new) | «`TimelineSemantic` is text-derivable at its easiest» — 7 / 7 events from one trusted block with exact spans; the first anchor (179 TCN) lost to a page guard, not to the rule | **PROVEN (narrow)** | step 4 |
| **A24** (new) | «a deterministic, non-arithmetic validator can be keyed to the lesson's own prose» — pair / order / before-after checks, source ids attached | **PROVEN (narrow)** | `timeline-order-v1` |
| **A25** (new) | «the page that carries the lesson header is trustworthy for its own objectives» | **FALSIFIED** | p38: 0 / 15 learning blocks trusted |
| **A26** (new) | «two OCR stacks agreeing (`text_sim` = 100) means the text is verbatim to the print» | **FALSIFIED** | attribution 3 («Đăng», «hóa»), «Tìm hiếu», heading slips — all at 100 |

Round-4 count on History: PROVEN 6 (A05-header, A14, A15, A20, A23, A24) · FALSIFIED 14 (A01, A04, A05-TOC, A06, A07, A08, A09, A10, A13, A16, A17, A19, A22, A25, A26 — 15 rows, A05 counted once) · UNTESTED/PARTIAL 2 (A18, A21) · n/a 1 (A02).

## Round 5 update — Bài 8 re-run + the deliberate stress tests (Lane C, 2026-09-06)

Evidence: `07-ROUND5-HISTORY.md`; data in `data/lsdl5-round5-rerun.md`, `data/lsdl5-history-stress.md`, `data/lsdl5-tone-repair-probe.md`, `data/lsdl5-repair-plugin.md`, `data/lsdl5-bai8-verbatim-ledger.json`. MEASURED unless marked. Every claim is bounded to LS&ĐL 5 — the pipeline is the round-5 build, the raw OCR is round 4's, so differences are code.

| # | on the round-5 pipeline | status | evidence |
|---|---|---|---|
| A01 | the dash sub-items are trusted `question` now; the question LEAD is still `body` and the figure-dependent lead is withheld by the (fixed) guard | FALSIFIED · partly mitigated | Bài 8 roles |
| A05 | 28 / 28 headers found, 10 TOC-confirmed, 0 conflicts; the TOC still lacks 18 `pageStart` | header attachment **PROVEN again** · TOC FALSIFIED again | attach |
| A06 | 6 «Chủ đề» chapters parse; Bài 8 sits in Chủ đề 3 | **no longer FALSIFIED for this book** (the rule was extended) | bridge |
| A07 | Bài 8 withhold reasons are now `agree_tones` 7 · colour 4 · agree_text 3 · figure_dependent 1 · box_boundary 1 · agree_order 1 — still none diagram/math | FALSIFIED again | TSL stats |
| A08 | the `attribution` role exists; 4 on Bài 8, 31 across the book — the Dart work-around is no longer needed to FIND them | **repaired**, the assumption still fails for `activity`/`footnote`/`option` | roles |
| A17 | both gold errata are fixed | closed | gold |
| A19 | «quan sát các hình từ 1 đến 3» is now withheld `figure_dependent` | **repaired for this form** | p039:003 |
| A22 | still no «Em đã học» | FALSIFIED again | — |
| A23 | «`TimelineSemantic` is text-derivable at its easiest» — on the shipped build the rule yields **0** events for Bài 8 and **3** for the whole book; the 8 events (7 + the 179 TCN anchor) exist only **after** a validated repair | **PROVEN (narrow) → NARROWED FURTHER**: derivable, but only from a block the guards currently withhold | `history-rules-v2`, `repair-plugin` |
| A24 | «a deterministic non-arithmetic validator can be keyed to the lesson's own prose» — the function still works; **registering** it does not follow (empty domain · the book's own exercise has no unique answer set · the facts rest on a repair) | PROVEN (as a function) · **registration REFUSED** | 07 §6 |
| A25 | the header page is now **13 / 21** learning blocks trusted (round 4: 7 / 21, and 0 / 15 of its learning TEXT); the whole lesson head — objectives, Khởi động poem, its attribution — came back | **FALSIFIED assumption now REPAIRED for this page shape** (block-level colour) | p038 |
| A26 | «two stacks agreeing ⇒ verbatim» — **6 blocks are still trusted and not verbatim, all at `text_sim` 100 with `agree_tones` silent**, including the attribution | **FALSIFIED again, on new data** | verbatim ledger |
| **A27** (new) | «a guard that fires on a real disagreement is withholding a real error» — `agree_tones` withheld the events block because the **verifier** was wrong; `agree_text` withheld the 179 TCN column because the verifier **merged two columns** | **FALSIFIED**: 10 of 15 Bài 8 withholds are FALSE WITHHOLDS by the print | scoreboard; 6 of 16 restorable |
| **A28** (new) | «`prose-dated-events-v1` is a History rule» | **FALSIFIED**: it accepts 21 of the 112 date mentions its own book prints (centuries, reign phrases, un-parenthesised ranges and bare TCN years are invisible) and extracts 3 events in 28 lessons | T1 |
| **A29** (new) | «`story-attribution-v1` generalises» | **PROVEN in form** (31 / 31 attributions, incl. 1 quoted document) · **FALSIFIED in substance**: 2 / 31 stories complete, 17 / 31 without a title, and 5 of the 14 titles found draw an objection from an independent signal | T2 |
| **A30** (new) | «one lesson = one page range survives a two-lesson spread» | **PROVEN for the lesson's own text** (0 of 24 header pages has content above the header) · **FALSIFIED for the chapter banner**: 5 pages carry two lessons and the «Chủ đề N» banner attaches to the PREVIOUS one, trusted and served in the wrong lesson on 2 | T3 |
| **A31** (new) | «an in-corpus deterministic signal can repair Vietnamese tone slips safely» | **FALSIFIED as a stand-alone**: at its best recall (book scope, dominant majority) precision 0.889, recall 0.533, **false-correction rate 0.111** — and the false correction rewrites a person's name («Đăng Khoa» → «Đặng Khoa»). It is safe only behind an independent validator. | tone-repair probe |
| **A32** (new) | «a withheld block can only be recovered by loosening a guard» | **FALSIFIED**: 6 of 16 Bài 8 withholds become restorable with **no guard changed** — four of them without changing a single character of text (a disposition repair) | repair plugin |

**Round-5 count on History: PROVEN 4 (A05-header, A24-as-a-function, A29-in-form, A30-for-the-lesson-text) · FALSIFIED 12 (A01, A05-TOC, A07, A22, A26, A27, A28, A29-in-substance, A30-for-the-banner, A31, A32, plus A08 for the remaining roles) · REPAIRED 4 (A06, A08-attribution, A19, A25) · REFUSED 1 (A24 registration).**

What the pattern now says: round 4's answer — *the document layer is cross-domain, the semantic layer is per-shape* — survives, and round 5 sharpens it in two places. First, **the semantic rules are per-SHAPE, and a shape is narrower than a subject**: `prose-dated-events-v1` is a Bài-8 shape, not a History one. Second, **the failure classes are no longer only detection problems**: two thirds of what Bài 8 loses is FALSE withholding, and it comes back through repair + an independent validator without touching a guard. Accuracy and coverage stopped being opposites this round — but only because a human read the printed page.
