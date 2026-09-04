# 01 — Learning Views · Founder Summary / Tóm tắt cho Founder

**Status:** RESEARCH + ARCHITECTURE HYPOTHESIS — không phải quyết định, không phải lệnh code.

---

## Trang 1 — Đọc trong 3 phút / Page 1 — three-minute read

**Ý tưởng của Founder:** một bài học không phải là một màn PDF hay một màn chat. MỘT BÀI HỌC ĐÁNG
TIN → BA CÁCH HỌC: **📖 Đọc như sách · ✨ Trực quan hóa · 🦉 Học với SAM.** Cùng một nguồn sự thật
(SGK/SGV), nhiều trải nghiệm — không phải ba bản sao nội dung.

**Kết luận của nghiên cứu này: B — CHẤP NHẬN CÓ ĐIỀU CHỈNH.**

Ý tưởng đúng và phần lớn **đã có sẵn trong kiến trúc SAM hôm nay** — nhưng có ba chỗ phải sửa
trước khi nó trở thành thiết kế:

1. **Mode 1 «Đọc như sách» hôm nay chưa dựng được từ nội dung có cấu trúc** cho hầu hết bài.
   Bộ trích bố cục (WAL-206) chỉ biết 7 loại khối chữ (heading/body/question/caption/sidebar/
   footnote/pageNumber) — **không có** khối Hình / Bảng / Công thức / Hoạt động; trang có bảng
   bị đánh dấu *không tin cậy*. Bài gần nhất với bài trên bảng concept (Khoa học 4 Bài 23 «Vai
   trò của chất dinh dưỡng») có **8/10 trang không tin cậy và 0 đơn vị nội dung** dùng được.
   → Mode 1 phiên bản thật đầu tiên phải là **«Mảnh tin cậy + ảnh trang gốc»**, không phải
   sách tái dựng nguyên khối. Kết luận cuối cùng chờ Trusted Corpus Feasibility.
2. **Mode 2 «Trực quan» phải là một HỌ renderer ăn dữ liệu đã tách kiểu**, không phải LLM «vẽ
   sơ đồ» mỗi lần mở bài. SAM đã chứng minh hai hình dạng (Thí nghiệm → Quy trình; Bản đồ → Không
   gian, WAL-185). Dòng thời gian / Sơ đồ khái niệm **chưa có dữ liệu** trong corpus. Repo tham
   chiếu nổi tiếng nhất (DeepTutor) sinh timeline và quiz bằng LLM **với danh sách nguồn rỗng**
   — đúng thứ luật §12 cấm. Không sao chép.
3. **Mode 3 «Học với SAM» đã tồn tại dưới tên khác**: Pedagogy Runtime của SAM (PlannedAct →
   RealizationRequest → guard) đã là «LLM diễn đạt, không quyết định». Cái thiếu không phải
   runtime mới mà là **một Surface trả lời ngắn** (nút thắt đo được ở WAL-206) và nối runtime đó
   tới nhiều bài hơn 1 bài. Câu «Chính xác! 🎉» trên bảng concept **vi phạm luật không chấm khi
   không có đáp án SGV** — bản trung thực: «SAM ghi nhận con đã trả lời», chỉ chấm ở 309 bài có
   đáp án SGV đo được.

**Điều quan trọng nhất về ngôn ngữ:** tài liệu hội tụ Claude × GPT × Founder đã **bỏ từ
"LEARNING MODE"** vì trùng với **LEARNING INTENT** (Chuẩn bị · Ôn · Bài tập · Tra cứu). Ba «cách
học» phải được định nghĩa là **cách trình bày (VIEW) được chọn bên trong một Learning Context**,
không phải một tầng mode mới cạnh tranh với ý định. Nếu không, implementation sẽ hiểu theo hai
cách — đúng rủi ro Founder từng cảnh báo.

**Founder's idea:** a lesson is not a PDF screen or a chat screen. ONE TRUSTED LESSON → THREE
WAYS TO LEARN. **Verdict: B — ADOPT WITH CHANGES.** The idea is right and mostly already in
SAM's code; three corrections are needed: (1) Mode 1 cannot be built block-by-block today
because the extractor has no image/table/formula/activity blocks and most pages are untrusted —
first honest Mode 1 is "trusted fragments + source page image"; (2) Mode 2 must be a family of
deterministic renderers fed by typed data, of which only Process and Spatial exist today; (3)
Mode 3 is SAM's existing Pedagogy Runtime reaching more lessons plus a Short-Answer Surface, not
a chat — and the board's graded MCQ must become fail-closed.

---

## Verdicts / Phán quyết (A adopt · B adopt with changes · C keep as hypothesis · D reject)

| Item | Verdict | One-line reason |
|---|---|---|
| **Concept: One Trusted Lesson → Three Views** | **B** | Right product framing; must be expressed as Views-inside-LearningContext (not a mode layer) and must consume Trusted-Corpus findings before any block-level promise. |
| **MODE 1 Smart Book / Đọc như sách** | **B** | Extractor has no image/table/formula blocks; tableLike pages untrusted; first version = trusted fragments + source-page image, never a re-typeset "book" that hides uncertainty. |
| **MODE 2 Visual Learning / Trực quan** | **B** | Renderer family fed by typed relationships (deterministic) — Process/Spatial PROVEN narrow; Timeline/Concept-map/Comparison HYPOTHESIS blocked on extraction, not on UI. |
| **MODE 3 SAM Tutor / Học với SAM** | **B** | Already SAM's Pedagogy Runtime (PlannedAct/Realization guard) — adopt the name, add the Short-Answer Surface, keep LLM shadow gate (WAL-30), fail-closed grading. |
| Trusted Structured Lesson (data contract) | **B** | FORMALIZE existing pieces (LessonKey, layout blocks w/ provenance, LessonActivity, SemanticBinding) into one lesson-scoped document; do **not** use it to force Deep/Scale path unification. |
| Multi-View Renderer | **B** | One lesson document, N renderers — but the renderer dispatch is the existing `LessonActivity`/`_activityAction` seam (ADR-009 spirit), not a new generic layout engine. |
| Visual Renderer Family | **B** | Build a template only when a typed data shape exists; today: Process, Spatial. Reject "generic mindmap of the lesson". |
| SAM Tutor Runtime | **A** | Exists (`lib/core/pedagogy/`, `realization_contract.dart`); nothing new to adopt — extend reach. |
| View Recommendation / Next Action | **C** | Keep as hypothesis: reuse `proposeIntent`/`LearningAgenda` signals; no evidence yet that a *view* recommendation changes behaviour; U1 in Convergence §24 is the test. |
| PDF-as-Reference | **A** | Source page image is a required fallback and provenance anchor (SAM already crops pages with bbox provenance); not a "viewer mode". |
| Structured Content Delivery (tải theo sách/bài) | **B** | ADR-006 already says per-pack local delivery; MEASURED: text is ~10× smaller than PDF per book, but figure crops (0.5–4 MB each) dominate — savings depend on image policy. |

## Top 5 decision-changing findings

1. **MEASURED — Mode 1 is blocked upstream, not in UI.** `tool/corpus/layout_extract.py` roles = heading · body · question · caption · sidebar · footnote · pageNumber; no image/table/formula; `tableLike ⇒ untrusted`. Khoa học 4 pp.84–93 (PDF) around Bài 23: 8/10 pages `trusted=false`, `units-layout` has 0 units for lesson 23; OCR heading reads "SỨC KHOE", "VAI TRÔ".
2. **FROM-REFERENCE — the best-known "living book" does not source-ground its visual blocks.** DeepTutor `deeptutor/book/blocks/timeline.py` and `quiz.py` return `source_anchors = []`; events are LLM-generated from the chapter summary. Its `SourceAnchor` is a ≤300-char snippet, not a page/bbox. This is the pattern §12 forbids — SAM's typed-data route is the right one, and it is more, not less, demanding than DeepTutor's.
3. **OBSERVED-IN-CODE — Mode 3 already exists as a runtime and the LLM is not wired.** `realization_contract.dart` (`RealizationRequest`, `validateRealization`, `realizationPolicyFor`), `pedagogy_model.dart` (`PlannedAct`, 15 `TeachingAct`), `learning_blueprint.dart`; `grep` finds no LLM client in `lib/`. "SAM Tutor" is a naming decision plus a Surface gap, not a new subsystem.
4. **OBSERVED-IN-CODE — Views would collide with Intent unless defined carefully.** `SAM-PRODUCT-EXPERIENCE-CONVERGENCE.md` §1 struck "LEARNING MODE" from the vocabulary; the current lesson sheet offers intents (`subject_home_screen.dart` `_intentTile`), and `lookup` produces TRACE not EVIDENCE (`evidence_validator.dart`). Đọc ≈ `lookup`; Học với SAM = evidence-producing intents; Trực quan is intent-agnostic. The three Views must be a *representation* choice, resolved after intent.
5. **MEASURED — the concept board's lesson does not exist in the corpus.** `curriculum-structure.json`: Khoa học 5 Bài 2 is "Ô nhiễm, xói mòn đất và bảo vệ" (pageStart `null`); the nutrition content on the board is closest to Khoa học 4 Bài 23–24. The board is illustrative; every quantitative promise on it must be re-tested on a real lesson.

## What is PENDING the Trusted Corpus Feasibility Study

Text fidelity per subject, reading order at scale, image/table/formula block feasibility, lesson boundary re-derivation (KHTN 7/8 TOC truncation), per-block confidence semantics, and the structured-document model itself (`11-STRUCTURED-DOCUMENT-MODEL.md` of that study). `12`, `13`, `15`, `18` each carry a reconciliation checklist.

## What this package does NOT recommend

No new screens beyond a lesson-level view switch on the existing Book Home; no generic layout/graph engine; no LLM composition of visuals; no "27 buttons"; no unification of the Deep and Scale curriculum paths by decree; no re-opening of closed Founder questions.

## Suggested next step (if the Founder accepts B)

A **measurement-only** follow-up on ONE real lesson (candidate: KHTN 6 Bài 16 or 17, already device-valid in WAL-206): count trusted blocks by role, list what a Trusted-Fragments Mode 1 would show vs. hide, and what typed data (if any) Mode 2 could consume — before any ticket to build.
