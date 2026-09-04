# 03 — The Three Learning Views Concept (restated, situated, and challenged)

## 1. The Founder's concept board — what it shows (described, not copied)

`concept/concept-ai-first/learning-view.png` — "CONCEPT: 1 BÀI HỌC – 3 CÁCH HỌC – 1 NGƯỜI BẠN ĐỒNG
HÀNH". Six phone frames:

1. **Giá sách** — greeting, search, grade filter chips (Tất cả · Tiểu học · THCS · Yêu thích), a
   grid of subject book covers (Toán, Tiếng Việt, Khoa học, Lịch sử, Địa lí, Tin học …), bottom nav
   with five tabs (Trang chủ · Giá sách · Học cùng SAM · Tiến bộ · Cá nhân).
2. **Chọn sách → chương** — cover + "Đã học 3/18 bài · 17%", tabs Mục lục / Giới thiệu / Ghi chú,
   Chủ đề → Bài rows with a done check on Bài 1.
3. **Vào bài học** — mascot: "Con muốn học theo cách nào?" then three cards: ① Đọc như sách "Gần
   giống SGK, có hình ảnh, bảng biểu, dễ theo dõi" · ② Trực quan hóa "Sơ đồ tư duy, dòng thời gian,
   sơ đồ quá trình…" · ③ Học cùng SAM "SAM sẽ dạy, hỏi, gợi ý và luyện tập cùng con"; plus a card
   "SAM đề xuất: Bắt đầu với Trực quan hóa vì bài này có nhiều khái niệm liên quan…".
4. **Mode 1 Đọc như sách** — tab bar Đọc | Trực quan | Học với SAM; numbered section heading
   "1. Các nhóm chất dinh dưỡng", paragraph, photo with caption "Hình 2.1", an "Em có biết?" box, a
   table "Bảng 2.1" (Nhóm chất / Vai trò chính / Thực phẩm tiêu biểu), pager "Trước 3/8 Tiếp".
5. **Mode 2 Trực quan hóa** — sub-tabs Sơ đồ tư duy | Sơ đồ quá trình | Bảng tóm tắt; concept map
   Chất dinh dưỡng → 4 nutrient groups with icons; "Ghi nhớ cùng SAM" summary card.
6. **Mode 3 Học cùng SAM** — SAM opens with a pre-question ("Trước khi bắt đầu, con thử trả lời
   nhé: Vì sao chúng ta cần ăn nhiều loại thực phẩm khác nhau?"), A–D options, "Chính xác! 🎉"
   feedback, "Thử thách tiếp theo" free-text prompt with an input bar.

Bottom band "KIẾN TRÚC NỘI DUNG — Một nguồn dữ liệu chuẩn – nhiều cách hiển thị": PDF SGK/SGV →
Structured Book (Text · Image · Table · Formula · Question · Activity · Source Page · Confidence) →
Learning Views → Học sinh. "LỢI ÍCH": accurate & safe (SGK, provenance); many ways to learn;
personalised with SAM; lighter & flexible (no PDF, download per book/lesson); modern experience.

**Reading of the board (not praise):** it is a product-level statement, and it is internally
consistent with SAM's doctrine on provenance and one-source-of-truth. It also makes assumptions the
evidence does not yet support (listed in `17` §2): the lesson does not exist in the corpus
(`02` §5); "17%" progress and a 5-tab nav conflict with the converged IA (`SAM-PRODUCT-EXPERIENCE-
CONVERGENCE.md` §5: three tabs, no % anywhere); the graded "Chính xác!" needs an SGV key; the
Image/Table/Formula/Activity blocks have no extractor; and the "SAM đề xuất" card is the §7
hypothesis, not an existing capability.

## 2. Definitions this package uses (aligned with the converged vocabulary)

| Term | Definition | Relation to existing terms |
|---|---|---|
| **Trusted Learning Source** | SGK/SGV pages as scanned + OCR + layout, with per-block trust and provenance. | `Provenance`, layout blocks, `SourceAsset` |
| **Trusted Structured Lesson** *(HYPOTHESIS name)* | One lesson-scoped document assembled at build time from trusted blocks, activity objects and optional semantic bindings. | proposed in `12`; not a new source of truth — a *projection* of the corpus keyed by `LessonKey` |
| **Learning View** | A *representation + interaction style* for the same Trusted Structured Lesson: Đọc (Smart Book) · Trực quan (Visual Learning) · Học với SAM (SAM Tutor). | **new** product-level term; sits *inside* a `LearningContext`, chosen after intent |
| **Learning Surface** | An interaction primitive (Reader, ComposeLite, Experiment, SourceReader, MapReader, QuizSelect, future ShortAnswer). | existing ADR-009 / Convergence "SURFACE" |
| **Activity Pattern** | A corpus-derived learner action type (EXPLAIN_SHORT, OBSERVE, …, 27). | `K12-ACTIVITY-PATTERN-REGISTRY.md` — capabilities used *inside* a View (`14`) |
| **LEARNING INTENT** | prepare · review · practice · lookup — belongs to the learner. | `learning_intent.dart`; **not** a View |

Invariant: **Learning View ≠ Learning Source ≠ Learning Intent ≠ Learning Surface.**

## 3. Where the three Views sit in the converged experience model

The converged model (`SAM-PRODUCT-EXPERIENCE-CONVERGENCE.md` §4) is
`LearningContext → ACTIVITY × INTENT → EXPERIENCE PATTERN → SURFACE(s) → EVIDENCE|TRACE → STATE → NEXT BEST ACTION`.
The Founder's concept adds one layer, and the only safe place for it is here:

```
LearningContext {learner, subject, book, lesson, intent, state, evidence}
        │
        ▼
   LEARNING VIEW  ← chosen by the child (3 visible options) or proposed by SAM with a reason
   ┌───────────────┬─────────────────────┬──────────────────────────┐
   │ 📖 Đọc        │ ✨ Trực quan         │ 🦉 Học với SAM            │
   │ (Smart Book)  │ (Visual Learning)   │ (SAM Tutor session)       │
   ├───────────────┼─────────────────────┼──────────────────────────┤
   │ TRACE only    │ TRACE only unless   │ EVIDENCE via Pedagogy     │
   │ (= lookup)    │ the child interacts │ Runtime + Surfaces        │
   └───────────────┴─────────────────────┴──────────────────────────┘
        │                   │                       │
        └──────── the SAME Trusted Structured Lesson ────────┘
```

Consequences (each one falsifiable):

- **Đọc is `lookup`** made visible as a book, not a fourth intent. It emits TRACE ("đã mở bài, đã xem
  trang") and never EVIDENCE — exactly the READ-gate precedent (`reader_screen.dart:96-100`).
- **Học với SAM is the evidence-producing path** for prepare/review/practice; the Pedagogy Runtime
  selects Surfaces (Activity Patterns) inside it. It is *not* a chat tab (Convergence §5 explicitly
  removed the floating SAM/chat button).
- **Trực quan is intent-agnostic on entry** (a representation), but may host interactions
  (order the steps, fill the missing node) which then become `CandidateEvidence` through the
  existing validator — the precedent in `SAM-LEARNING-VISUALIZER-RESEARCH.md` §6.
- A View never changes *what is true*; it changes *how it is shown and what the child can do*.

## 4. Why three, and why not 27 (Q1, Q13)

- Three is the number of **distinct epistemic relationships** a child can have with the same
  lesson: *see the source as it is* (fidelity), *see its structure* (representation), *be taught
  from it* (pedagogy + evidence). Adding "Quiz", "Flashcards", "Mindmap" as top-level modes would
  re-create the H5P/DeepTutor block zoo (`08`, `11`) and violate "no 27 buttons".
- The 27 Activity Patterns are *what the child does inside a View*, selected by the Pedagogy
  Runtime (Mode 3) or offered as interactions on a representation (Mode 2). They are never
  top-level (`14`).
- HYPOTHESIS to falsify with U1-style measurement: children will mostly follow SAM's proposal
  and rarely switch Views; if >85% never switch, the three-way chooser collapses to "SAM's
  proposal + đổi cách khác" (same test as Convergence §24 U1 for intents).

## 5. Falsification attempts on the whole architecture (Q10, Q25)

The Founder asked to try to break `SGK/SGV → Trusted Corpus Pipeline → TRUSTED STRUCTURED LESSON →
{SMART BOOK | VISUAL LEARN | SAM TUTOR} → Evidence → State → NEXT ACTION`. Attempts:

| # | Attack | Result | Evidence |
|---|---|---|---|
| F1 | "One canonical lesson document cannot exist because the corpus lesson boundary is unreliable." | **PARTLY HOLDS.** 8/30 Khoa học 5 lessons lack `pageStart`; KHTN 7/8 TOC truncated; ranges capped at 2.5× median. A lesson document must carry a *boundary confidence* and fail closed. | MEASURED (`curriculum-structure.json`), WAL-206 §4 |
| F2 | "Native block reconstruction is impossible on scanned PDFs." | **HOLDS TODAY for image/table/formula; NOT for text.** Reading order 0.99 on gold set, but no non-text roles; tableLike ⇒ untrusted. | WAL-206 §2, `layout_extract.py` |
| F3 | "Typed relationships for visuals will require LLM inference, breaking §12." | **HOLDS for History/Concept map today; FALSE for Process/Spatial.** `KhoaExperiment.tienHanh[]` and `DiaMap` are typed, verbatim, provenance-bearing. Sử units are raw `SECTION_TEXT` with no event fields. | `lesson_index.dart:104-156`; VISUALIZER §4 |
| F4 | "Three Views duplicate content and will drift (Mode 1 says X, Mode 3 teaches Y)." | **AVOIDABLE by construction**: if all three render the same lesson document and Mode 3's realizations pass `validateRealization` with `DerivedFacts` from that document, drift is a build-time diff, not a runtime risk. It is a *real* risk if Mode 2/3 use any content not in the document. | `realization_contract.dart:88-102` |
| F5 | "The concept re-introduces LEARNING MODE." | **HOLDS unless Views are defined inside LearningContext** (§3). | Convergence §1 |
| F6 | "Evidence cannot move between Views." | **FALSE**: evidence is keyed by `skillCaseId`/`conceptId` + `sourceDocumentId`/`lessonNo`, not by Surface (`LearningEvent` fields via validator). Views are irrelevant to the evidence log; only Surfaces mint. | `evidence_validator.dart:67-82` |
| F7 | "A View recommendation needs a new recommender / an LLM." | **FALSE**: `proposeIntent` + `LearningAgenda` already produce a reasoned proposal; mapping intent→View is a small deterministic table. Whether the recommendation *helps* is untested. | `learning_intent.dart:85-123` |
| F8 | "This complicates the Learning OS (anti-principle #5)." | **DOES NOT HOLD if** no new planes are added: Views are a presentation policy over the existing seven planes (`SAM-EDUCATION-DATA-ARCHITECTURE-PROPOSAL.md` §2). It **would** hold if a generic layout engine, a graph DB, or a second resolver were built (`SAM-LEARNING-VISUALIZER-RESEARCH.md` §5 warns precisely against a parallel resolver). | Proposal §2, §3 |
| F9 | "Trusted Corpus findings may invalidate the block model." | **OPEN** — PENDING TRUSTED-CORPUS FINDINGS. | — |

Net: the architecture survives as a *direction* with two hard preconditions (block-level
extraction for non-text; typed relationship extraction for visuals) and one definitional guard
(Views inside LearningContext).

## 6. What "close enough to the book" must mean (Mode 1 principle)

The Founder's phrase — *"close enough to the book that the child recognises the lesson, but
native, responsive and AI-ready"* — is operationalised in `04` as: **preserve order, headings,
figures with captions, tables, formulas, questions and activities**; allow reflow, font size,
zoom, highlight, bookmark, annotation, "Hỏi SAM về đoạn này", source reference; and **never
present an untrusted block as text** — show the source page region image instead, labelled.
