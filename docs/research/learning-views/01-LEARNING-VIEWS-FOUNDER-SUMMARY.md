# 01 — Learning Views · Founder Summary / Tóm tắt cho Founder

> **Reconciled with TC-v1 (2026-09-05).** `TC-nn` = `docs/research/trusted-corpus/nn-….md` (WAL-208).
> Verdicts unchanged; reasons now cite measured numbers; the "pending" section is replaced by
> "resolved / still unmeasured".

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
   sách tái dựng nguyên khối. **TC-v1 (WAL-208) đã đo và xác nhận hình dạng này:** trên 38 trang
   khó, bộ trích hiện tại chỉ tin 19 % số khối và 12 % số khối được tin vẫn sai (TC-08 §1: TLSR
   0.193, FTR 0.119); nguồn khối theo mô hình bố cục + kiểm chéo giữ được 67–77 % khối với FTR 12 %
   trên trang khó, 0 % trên văn xuôi thường (TC-10); **chưa bộ nào biết khối nào là câu hỏi** (độ
   chính xác nhãn câu hỏi 0.69, TC-07); công thức, sơ đồ/dòng thời gian/bản đồ và trang tranh
   tiểu học **phải giữ dạng ảnh** (TC-19 #7). Chỉ **555/3,381** bài có khoảng trang là nguồn hoá
   được hoàn toàn (TC-03 §5, TC-18 Q17); phần còn lại nguồn hoá **một phần** (văn xuôi + câu hỏi
   tin được, toán/sơ đồ giữ lại).
2. **Mode 2 «Trực quan» phải là một HỌ renderer ăn dữ liệu đã tách kiểu**, không phải LLM «vẽ
   sơ đồ» mỗi lần mở bài. SAM đã chứng minh hai hình dạng (Thí nghiệm → Quy trình; Bản đồ → Không
   gian, WAL-185). Dòng thời gian / Sơ đồ khái niệm **chưa có dữ liệu** trong corpus. Repo tham
   chiếu nổi tiếng nhất (DeepTutor) sinh timeline và quiz bằng LLM **với danh sách nguồn rỗng**
   — đúng thứ luật §12 cấm. Không sao chép. **TC-v1 thêm:** mọi bộ đọc đều đọc sai thứ tự dòng
   thời gian (TC-06); bảng chỉ thành đối tượng trên đường GPU (Marker 1.00/1.00, TC-07); công thức
   bị làm phẳng ở mọi bộ (TC-09) — Timeline/Comparison/Data lùi xa hơn, không gần hơn.
3. **Mode 3 «Học với SAM» đã tồn tại dưới tên khác**: Pedagogy Runtime của SAM (PlannedAct →
   RealizationRequest → guard) đã là «LLM diễn đạt, không quyết định». Cái thiếu không phải
   runtime mới mà là **một Surface trả lời ngắn** (nút thắt đo được ở WAL-206) và nối runtime đó
   tới nhiều bài hơn 1 bài. Câu «Chính xác! 🎉» trên bảng concept **vi phạm luật không chấm khi
   không có đáp án SGV** — bản trung thực: «SAM ghi nhận con đã trả lời», chỉ chấm ở 309 bài có
   đáp án SGV đo được. **TC-07 §Hệ quả thêm một luật:** chừng nào tầng vai trò chưa đạt ≥ 0.95 độ
   chính xác câu hỏi, **không câu hỏi tự gán nhãn nào được đưa cho trẻ như câu hỏi chấm điểm**.

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
a chat — and the board's graded MCQ must become fail-closed. **TC-v1 (2026-09-05) confirms all
three from the corpus side and adds a fourth:** the trust unit must move from page to **block**
(Structured Document Model, TC-11), and a **role layer** must exist before any auto-labelled
question is used as a prompt (TC-07).

---

## Verdicts / Phán quyết (A adopt · B adopt with changes · C keep as hypothesis · D reject)

Unchanged after TC-v1 (re-evaluation with one-line reasons: `18` §3a).

| Item | Verdict | One-line reason (TC-v1 citations where measured) |
|---|---|---|
| **Concept: One Trusted Lesson → Three Views** | **B** | Right product framing; must be expressed as Views-inside-LearningContext (not a mode layer). **TC-v1:** "One Trusted Lesson" must mean *the TRUSTED-block subset of a lesson* — 555/3,381 ranged lessons fully, ≈ 2,800 partially (TC-18 Q17); the thesis "3,679 lessons from the books" becomes "a growing trusted subset" (TC-18 verdict; Founder decision, `17` §5 C11). |
| **MODE 1 Smart Book / Đọc như sách** | **B** | First version = trusted fragments + source-page image. **TC-v1 supports this shape** (TC-10 escalation paths, TC-19 #7) and sharpens it: trust per block via an agreement cascade (TC-10); `question`-role blocks shown as plain text until role precision ≥ 0.95 (TC-07); formula / diagram / timeline / map / colour-heavy elementary / table pages stay image regions (TC-18 Q15–16). Today's XY-cut fragments are page-gated with FTR 0.119 on hard pages (TC-08 §1) — prototype only. |
| **MODE 2 Visual Learning / Trực quan** | **B** | Renderer family fed by typed relationships — Process/Spatial PROVEN narrow. **TC-v1:** typed data extractable now = captions (`caption_of` 0.90–0.95, TC-07), MCQ options in order (TC-06), `heading_path`; withheld = formulas (flattened by every stack, TC-09), tables on the Mac path (Docling finds half, cells flattened; Marker 1.00/1.00 needs a GPU, TC-07/TC-14), timeline order (wrong in every parser, TC-06). Timeline / Concept-map / Comparison stay HYPOTHESIS-BLOCKED, now with measured reasons. |
| **MODE 3 SAM Tutor / Học với SAM** | **B** | Already SAM's Pedagogy Runtime; add the Short-Answer Surface; keep LLM shadow gate (WAL-30); fail-closed grading. **TC-v1:** no auto-labelled question may be a graded prompt until the role layer measures ≥ 0.95 (TC-07 §Consequence); SGV pairing moves from page ranges to `answer_of` relations with an answer-leak guard (TC-14); the "+76 lessons" and pattern counts are old-extractor artefacts to recompute (TC-15). |
| Trusted Structured Lesson (data contract) | **B** | FORMALIZE onto TC-11's Structured Document Model: `TrustedLessonDocument` = the per-lesson projection of `TrustedLearningSource` (SDM blocks with `trust.status = TRUSTED`); adopt SDM roles, tri-state trust, block ids, one bbox convention (`12` §3). Do **not** use it to force Deep/Scale path unification. |
| Multi-View Renderer | **B** | One lesson document, N renderers — dispatch is the existing `LessonActivity`/`_activityAction` seam (ADR-009 spirit). TC-11 §2 states the same rule: projections carry block ids. |
| Visual Renderer Family | **B** | Build a template only when a typed data shape exists; today: Process, Spatial. TC-v1 names which shapes are extractable now vs withheld (`05` §2). Reject "generic mindmap of the lesson". |
| SAM Tutor Runtime | **A** | Exists (`lib/core/pedagogy/`, `realization_contract.dart`); not in TC-v1's scope — extend reach. |
| View Recommendation / Next Action | **C** | Keep as hypothesis: reuse `proposeIntent`/`LearningAgenda` signals; no evidence yet that a *view* recommendation changes behaviour; U1 in Convergence §24 is the test. Not in TC-v1's scope. |
| PDF-as-Reference | **A** | **Strengthened:** TC-v1's own recommendation for math/visual content is image-first delivery of the page crop with provenance (TC-10 escalation, TC-19 #7) — the page is a delivery path, not only a fallback. Licensing (OQ8) stays a Founder/Legal decision: TC-v1 assumes it, does not decide it (`17` §5 C6). |
| Structured Content Delivery (tải theo sách/bài) | **B** | ADR-006 already says per-pack local delivery. MEASURED now per page (TC-16): Docling JSON 17.6 KB, SDM ≈ 30–40 KB, 200-dpi page render ≈ 330 KB — rasters, not text, decide the size; reader-dpi/webp policy STILL UNMEASURED after TC-v1. |

## Top 5 decision-changing findings

1. **MEASURED — Mode 1 is blocked upstream, not in UI.** `tool/corpus/layout_extract.py` roles = heading · body · question · caption · sidebar · footnote · pageNumber; no image/table/formula; `tableLike ⇒ untrusted`. Khoa học 4 pp.84–93 (PDF) around Bài 23: 8/10 pages `trusted=false`, `units-layout` has 0 units for lesson 23; OCR heading reads "SỨC KHOE", "VAI TRÔ".
2. **FROM-REFERENCE — the best-known "living book" does not source-ground its visual blocks.** DeepTutor `deeptutor/book/blocks/timeline.py` and `quiz.py` return `source_anchors = []`; events are LLM-generated from the chapter summary. Its `SourceAnchor` is a ≤300-char snippet, not a page/bbox. This is the pattern §12 forbids — SAM's typed-data route is the right one, and it is more, not less, demanding than DeepTutor's.
3. **OBSERVED-IN-CODE — Mode 3 already exists as a runtime and the LLM is not wired.** `realization_contract.dart` (`RealizationRequest`, `validateRealization`, `realizationPolicyFor`), `pedagogy_model.dart` (`PlannedAct`, 15 `TeachingAct`), `learning_blueprint.dart`; `grep` finds no LLM client in `lib/`. "SAM Tutor" is a naming decision plus a Surface gap, not a new subsystem.
4. **OBSERVED-IN-CODE — Views would collide with Intent unless defined carefully.** `SAM-PRODUCT-EXPERIENCE-CONVERGENCE.md` §1 struck "LEARNING MODE" from the vocabulary; the current lesson sheet offers intents (`subject_home_screen.dart` `_intentTile`), and `lookup` produces TRACE not EVIDENCE (`evidence_validator.dart`). Đọc ≈ `lookup`; Học với SAM = evidence-producing intents; Trực quan is intent-agnostic. The three Views must be a *representation* choice, resolved after intent.
5. **MEASURED — the concept board's lesson does not exist in the corpus.** `curriculum-structure.json`: Khoa học 5 Bài 2 is "Ô nhiễm, xói mòn đất và bảo vệ" (pageStart `null`); the nutrition content on the board is closest to Khoa học 4 Bài 23–24. The board is illustrative; every quantitative promise on it must be re-tested on a real lesson.

**What TC-v1 changed in these five.** (1) stands and is now measured on 38 hard pages: XY-cut
TLSR 0.193, FTR 0.119 (TC-08 §1); Toán 5 pilot: 3 of 50 pages trusted (TC-13 §1). One number is
superseded: "0.90 heading role accuracy" (WAL-206 9-page gold) → precision 0.81 / recall 0.51 on
the hard set (TC-07). (2) unchanged. (3) unchanged; TC-11 §6 adds "do not let an LLM/VLM re-guess
a block". (4) unchanged. (5) unchanged; lesson attachment itself is wrong on 10/38 gold pages by
TOC range (TC-02 §5), so "re-test on a real lesson" must include its boundary.

## What TC-v1 resolved · what is STILL UNMEASURED after TC-v1

**Resolved (MEASURED).** Reading order: 0.987 (Docling) / 0.991 (Marker) on hard pages — prose is
solved, semantic order (timelines, 2-D math, bubbles) is not (TC-06). Image / table / formula
blocks: figures feasible as *image regions* with a caption relation (TC-11 §2, TC-07); tables as
objects only on the GPU path (Marker 1.00/1.00; Docling finds half, cells flattened, TC-07/TC-14);
formulas never as text (flattened by every stack, TC-09; image-first, TC-19 #7). Lesson boundary:
10/38 gold pages attach wrongly by TOC range, header-based attachment fixes 6 (TC-02 §5, TC-14 §2);
denominator 3,381 ranged of 3,679 canonical (TC-03 §5). Per-block confidence: tri-state
`trust{status, reasons[], verifier agreements[]}` + separate role confidence + `ocr_conf`
(TC-11 §2, §4). The structured-document model: TC-11 (adopted as the base of `12` §3).

**STILL UNMEASURED after TC-v1.** (a) Text fidelity *per subject* — TC-v1 measures per layout
feature (TC-05 §3) and gives per-subject only fully-sourceable lesson counts (Toán 4/554, KHTN
4/145, Vật lí 1/82, TC-18 Q17); the gold has ≤ 10 pages per subject family (TC-04) — a ≥ 20-page
per-family gold (TC-19 #9) would close it. (b) False trust and reading order *at scale* — 38
pages cannot certify < 1 %; ≥ 3,000 validated blocks are needed (TC-17 #2); the 150-page pilot is
unannotated (TC-13 §1). (c) Figure bbox precision — the SDM `Figure` object exists, only page-level
figure presence was measured (TC-03 §2). (d) A typography (bold) signal for glossary terms
(`05` §4). (e) Reader-dpi / webp raster size — TC-16 measured 200-dpi review renders only.
(f) SGV pairing upper bound — needs an SGV format census (TC-14).
**Open decision, not a measurement:** page-image licensing (OQ8) — TC-v1 assumes image-first
delivery (TC-19 #7) and leaves governance unchanged (TC-17 #15).

## What this package does NOT recommend

No new screens beyond a lesson-level view switch on the existing Book Home; no generic layout/graph engine; no LLM composition of visuals; no "27 buttons"; no unification of the Deep and Scale curriculum paths by decree; no re-opening of closed Founder questions.

## Suggested next step (if the Founder accepts B)

A **measurement-only** follow-up on ONE real lesson (candidate: KHTN 6 Bài 16 or 17, already
device-valid in WAL-206 — and inside the Science slice TC-19 #6 names): count trusted blocks by
**SDM role** on *both* sources (XY-cut vs Docling ▸ XY-cut + math guard, the TC-13 pattern), list
what a Trusted-Fragments Mode 1 would show vs. hide under the page-feature guard, and what typed
data (if any) Mode 2 could consume — before any ticket to build.
