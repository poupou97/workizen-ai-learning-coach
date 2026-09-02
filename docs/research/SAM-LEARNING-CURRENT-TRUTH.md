# SAM-LEARNING-CURRENT-TRUTH — audit sự thật hiện tại (đọc CODE, không đoán từ tên)

**Ngày:** 2026-09-02 · Task Order P0 Pedagogy §1 · nhánh `research/sam-pedagogy-p0`
**Phương pháp:** grep/đọc trực tiếp 11.303 LOC lib+test (233 test xanh tại HEAD 24de575),
đối chiếu 29 doc research + 9 ADR + Jira WAL (98 issue) + Confluence (17 trang).

## Bảng năng lực — phân loại theo BẰNG CHỨNG CODE

| Capability | Trạng thái | Bằng chứng thật (file:dòng / test) |
|---|---|---|
| **Student mastery model** | `BUILT` | BKT per-SkillCase: `mastery.dart` (`bktPosterior`, CaseMastery với independentCorrect/Incorrect); ConceptSummary 3 trục mastery≠coverage≠confidence (`concept_summary.dart`, 17 golden test); claim gate + pha loãng hỗ trợ ADR-007 |
| **Misconception model** | `MISSING` | grep "misconception" toàn lib = **0**. Chỉ có phân loại lỗi THÔ: executionError vs ca-yếu (`multi_skill_diagnosis.dart`) + `attributionUnresolved`. WAL-27 ở Ideas ghi rõ "giả thuyết SGV-là-nguồn đã bị bác bằng đo" — chưa có mô hình lỗi-hệ-thống nào |
| **Learning history** | `BUILT` (V0, mới) | `LearningSession` lưu-một-lần + 3 projection ngày/môn/tri-thức (`learning_session.dart`, `learner_store.dart` JSONL append-only, 18 test); lineage support/policyId/priorEventId trên từng event |
| **Spaced review** | `PARTIAL` | `review_schedule.dart`: SM-2-shape (7d ×2 cap 112d), TÁCH khỏi pMastery (F5 — quyết định Founder); NHƯNG interval cố định theo policy, chưa có forgetting model (code tự khai: "mô hình quên chưa được bật"), chưa FSRS, chưa đo với dữ liệu thật |
| **Retrieval practice** | `PARTIAL` | grep "retrieval" = 0 NHƯNG cơ chế tương đương tồn tại: review tile trong Mission + Quiz/Select surface = retrieval về hành vi; KHÔNG có khái niệm retrieval-vs-reread tường minh, không có test cho nó |
| **Adaptive difficulty** | `MISSING` | grep "difficulty" = 0. Thích ứng hiện có là THEO CA (đúng ca, đúng stage) — không có trục độ-khó trong-ca. Chưa từng thiết kế |
| **Teaching strategy selector** | `PARTIAL` | `decide()` (rule-based, 8 DiagnosticOutcome → LearningAction 8 giá trị: teach/practice/review/diagnosePrerequisite/remediate/contrastCases/isolateSkills…) + thang hỗ trợ ±1 (TutorSession) + `nextProbe` (WAL-70). Đây LÀ strategy selector nhưng thô: không có khái niệm TeachingStrategy first-class với when-to-use/cognitive-load/success-criteria; taxonomy 17 TeachingAct mới ở mức RESEARCH (doc WAL-67), chưa thành code |
| **Socratic tutoring** | `PARTIAL` | Khám-phá-trước (trẻ thử trước mọi reveal — REVEAL gate có test+đột biến), probe hỏi-vì-thông-tin (WAL-70), hint mở đầu bằng câu hỏi. NHƯNG hint content là template tĩnh 2 method; không có vòng hỏi-đáp Socratic đa lượt |
| **Worked-example logic** | `PARTIAL` | `SupportLevel.workedStep` là bậc riêng trong thang ±1 (11 refs, có test + sim WAL-87); NHƯNG nội dung worked-step là template, và corpus GĐ2 cho thấy EXAMPLE unit mới trích được 7 cái — chưa nối example-từ-SGK vào tutor |
| **Parent insight** | `BUILT` (V0) | `explainConcept` claim-gated 6 nhánh + EvidenceCitation per-case (7 test) + màn «Tối nay» MỘT khuyến nghị (4 widget test, cấm mascot/%/so sánh). CHƯA có: weekly brief, escalation, habit coaching |
| **Source-level provenance** | `BUILT` | Provenance 5 mức (sourceStated/**sourceDemonstrated**/sourceSequence/systemDerived/llmInferred) + citable phân theo loại khẳng định; Method.provenance + `explainTeaching` fail-closed (F7); 2.202 ContentUnit đều mang assertion + trang |
| **Tutoring evaluation** | `MISSING` (có mầm) | KHÔNG có eval harness (ls test | grep eval = rỗng). Có mầm: WAL-63 benchmark 6 chỉ số perception (FTP Rate), sim WAL-87 đo policy dạy trên học sinh mô phỏng, và điều kiện mở WAL-30 ghi "eval harness đo được" là gate. Chưa có bộ scenario chuẩn, chưa có judge |
| Knowledge-component graph | `PARTIAL` | Concept→SkillCase→Method + CurriculumEdge citable + cross-grade (6 test); prerequisite edges còn `llmInferred` (WAL-18 mở) — chưa đủ nguồn |
| Confidence/uncertainty | `BUILT` | ConfidenceFactors min(volume/consistency/recency) per-case; `attributionUnresolved` không đoán; UNKNOWN≠FAILED xuyên suốt |
| Forgetting | `MISSING` (cố ý hoãn) | F5 ghi trong ADR-003: "cần mô hình thời gian trong toàn chuỗi bằng chứng"; recency chỉ là belief-phai-đi của ƯỚC LƯỢNG, không phải mô hình quên |
| Transfer | `MISSING` | Không có khái niệm transfer-problem/verify-transfer nào trong code; gần nhất là `contrastCases` (đối chiếu 2 ca) — khác bản chất |
| Learning velocity | `MISSING` | Không có |
| Interleaving | `MISSING` | grep = 0; Mission xếp review+học-mới nhưng không có luật xen kẽ có chủ đích |

## CONFLICTING / cần Founder biết

1. **«Điểm môn Toán» vs knowledge-component**: câu hỏi WS-A đã được trả lời TRONG KIẾN TRÚC
   từ ADR-001/004 — mastery ở mức **SkillCase** (dưới cả concept), tổng hợp lên concept qua
   3 trục, KHÔNG BAO GIỜ một-số-một-môn. Cây ví dụ của order (Toán→Phân số→Quy đồng→Cộng
   khác mẫu) khớp 1:1 với concept/case hiện có. Node hiện có: mastery ✅ confidence ✅
   evidence ✅ attempts ✅ last-practiced ✅ source-ref ✅ · common-mistakes ❌ forgetting-risk ❌.
2. **Socratic đa lượt & strategy engine phong phú đều đang GATED sau WAL-30** (Generative
   Tutor cần safety+eval) — mọi đề xuất WS-C phải tôn trọng gate này.
3. Từng REJECTED (không làm lại nếu không có bằng chứng mới): min/mean một-số-cho-concept
   (Founder bác); wildcard method (F2); conjunctive toàn cục (WAL-54); REMEDIATION làm nhãn
   content-graph (Delta 2026-09-01); MCQ-4/MAP/ORAL surface khi corpus 0 hit.

## Đã RESEARCHED nhưng chưa build (đỡ trùng công khi research mới)

TeachingAct taxonomy 17 act có prior art (WAL-67) · fading ±1 GIẢ THUYẾT với 3 bất biến sim
(WAL-87: jump-to-full bị nghiền; hỗ-trợ-không-fade = hệ mù 100%) · diagnostic probe loop
(WAL-70, đã thành code) · 4 chiều CORRECTNESS/ASSISTANCE/EVIDENCE/AFFECT (WAL-69, đã code)
· AI curriculum QĐ2422 267 outcome máy-đọc-được (E16) · assistance-fading model doc ·
adaptive-learning OSS benchmark (EduStudio/pyBKT/OATutor đã chấm một vòng trước đây).
