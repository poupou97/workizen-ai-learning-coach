# SAM-TEACHING-STRATEGY-ENGINE — WS-B chẩn đoán + WS-C chiến lược dạy

**Ngày:** 2026-09-02 · WAL-99 · research-only. Bất biến §25.5/6/7 được falsify ở §3.

## 1. WS-B — chẩn đoán từ QUÁ TRÌNH, không chỉ đáp án

Câu hỏi order: *hai học sinh cùng sai một đáp án nhưng khác nguyên nhân → dạy khác thế nào?*

**Hiện trạng đo được:** SAM đã phân biệt được — theo CA (attributeFailure: executionError vs
ca-yếu vs attributionUnresolved→probe) và theo LINEAGE (support/prior trên event). CHƯA phân
biệt được — theo LOẠI LỖI trong cùng ca (conceptual vs procedural vs careless) và theo
MISCONCEPTION cụ thể.

Pipeline order đề xuất, đối chiếu hiện trạng:

| Bước pipeline | Hiện trạng | Gap |
|---|---|---|
| Problem → Student attempt | ✅ CanonicalProblem + TutorSession | — |
| Reasoning evidence | PARTIAL: lineage sự kiện; CHƯA có step-capture (scratch/verbal) | step-workspace là surface tương lai; voice RESEARCH LATER |
| Error classification | PARTIAL: 3 lớp thô | thiếu conceptual/procedural/careless TRONG ca |
| Misconception hypothesis | ❌ MISSING | cần CATALOG tất định (xem STUDENT-MODEL §3) — không LLM tự do |
| Teaching response → Retry → Verification | ✅ thang ±1 + REVEAL gate + retry; verification = bài tương tự | transfer-verify chưa có (xem §4) |

**Đề xuất nhỏ nhất có giá trị:** phân loại lỗi 3 mức TRONG-CA bằng luật tất định trên dữ liệu
đã có: careless = sai lần đầu + selfCorrection ngay không cần hỗ trợ; procedural = sai ở ca
đã từng vững (pMastery cao trước đó); conceptual = sai lặp + hintRequested + probe xác nhận
ca nền yếu. KHÔNG cần model mới — là POLICY đọc log. Đánh nhãn là GIẢ THUYẾT, kiểm ở WAL-49.

## 2. WS-C — TeachingStrategy như khái niệm CẤU TRÚC (không phải prompt to)

Falsify trước: socratiq-ai audit chứng minh «một prompt lớn» = pedagogy theater. Ngược lại,
tạo abstraction mới khi model cũ đã giải quyết = vi phạm §25.18. Vậy soi từng candidate:

| Strategy (order) | Đã có dưới tên gì? | Verdict |
|---|---|---|
| MINIMAL_HINT / STEP_BY_STEP_SCAFFOLD | thang ±1 hint→workedStep (test+sim) | ĐÃ CÓ — không tạo tên mới |
| WORKED_EXAMPLE | SupportLevel.workedStep + EXAMPLE units corpus | ĐÃ CÓ bậc; THIẾU nội dung từ corpus |
| SOCRATIC_GUIDANCE | probe/pump + khám-phá-trước | PARTIAL — đa lượt GATED WAL-30 |
| RETRIEVAL_QUIZ / SPACED_REVIEW | review lane + Quiz surface | ĐÃ CÓ khung; thiếu tường minh retrieval |
| ERROR_CORRECTION | try-again + contrastCases | PARTIAL |
| SELF_EXPLANATION | Compose checklist; parent «hỏi con giải thích» | PARTIAL |
| TRANSFER_PROBLEM | ❌ không có | GAP THẬT — duy nhất cần khái niệm mới |
| Fading | ±1 (GIẢ THUYẾT — WAL-87 không phân xử; expertise-reversal meta ỦNG HỘ hướng novice-cần-support) | ĐÃ CÓ + evidence văn liệu mới |

⇒ **TeachingStrategy mới như một ENUM lớn là KHÔNG cần** — sẽ trùng 80% với
LearningAction×SupportLevel×TeachingAct hiện có. Cái CẦN: (1) bảng thuộc tính
when/when-not/age/load/evidence cho từng tổ hợp ĐÃ CÓ (tài liệu hoá, không code mới);
(2) MỘT khái niệm mới: **TransferProbe** — bài cùng ca khác bề mặt để verify transfer
(§25 candidate «verify transfer, not same-question success»). Đề xuất, không implement.

## 3. Falsify bất biến §25.5/6/7

- **§25.5 Strategy ≠ Act ≠ Method**: thử gộp Strategy=Act → mất tầng «một chiến lược nhiều
  nước đi» (Socratic gồm pump+probe+reflect); thử gộp Act=Method → lặp lỗi F2 cũ (method là
  TRI THỨC MÔN, act là NƯỚC ĐI ĐỐI THOẠI — WAL-67 đã có 17 act prior-art). **ĐỨNG VỮNG.**
- **§25.6/7 applicability ∩ permission**: đã có phản ví dụ đo từ corpus (BCNN đúng toán,
  0 lần xuất hiện lớp 5) + test wildcard-đóng + explainTeaching F7. Thử falsify chiều ngược
  («chỉ cần permission»): bài 3/5+1/5 nhận method quy-đồng → dạy bước thừa cho bài cùng mẫu
  — chính là F2 lịch sử. **ĐỨNG VỮNG hai chiều.**

## 4. §16 — 10 scenario E2E (internal state, không phải kịch bản chat)

Định dạng nén: [diagnose → strategy → act → student action → evidence → update → next].
1. **L5 «không biết cộng 2/3+1/4»** — chi tiết đầy đủ bên dưới.
2. L2 đếm cộng trong phạm vi 20, sai liên tục → probe ca nền (đếm tiếp vs gộp chục) → workedStep → guidedAttempt → mastery ca nền cập nhật → bài dễ hơn.
3. L4 quy đồng lần đầu (B57) — nguồn DEMONSTRATED → worked-example từ ví dụ SGK tr.62 (citation «SAM làm theo ví dụ») → trẻ làm bài tương tự → independent.
4. L6 phân số âm (chưa có trong corpus WAL) → TutorScope rỗng → SAM nhận «chưa chắc» — fail-closed là MỘT scenario chuẩn, không phải lỗi.
5. L9 đọc-hiểu nghị luận: readRespond → SHORT_TEXT unsupported → Reader chỉ phần đọc, câu hỏi mở nói «chưa hỗ trợ» (trung thực).
6. TV5 liên-kết-câu: recognize vững + apply chưa quan sát → decide chọn COMPOSE task (coverage lái hành động) → draft→selfCorrection.
7. Học sinh xin đáp án thẳng («cho con kết quả đi») → REVEAL gate: từ chối + đề nghị thử bước đầu; nếu đã thử → workedStep, không bao giờ nhảy full.
8. Trả lời bừa liên tiếp (3 sai <5s/lần — timeSpent) → nghi guessing → chuyển probe dễ + báo affect «mình chậm lại nhé» (không phạt).
9. Overconfident: đúng nhanh 2 ca dễ, đòi bỏ qua → coverage chặn claim; TransferProbe bề mặt khác trước khi cho tiến.
10. Đúng-khái-niệm-sai-tính-toán: executionError (mọi thành phần vững) → practice ngắn, KHÔNG dạy lại — đã là luật attributeFailure.

**Scenario 1 chi tiết (internal state từng bước):**
`identify`: parse 2/3+1/4 → fractionCase(3,4)=non-divisible; concept quy-dong+cong-phan-so (Q-matrix 2 thành phần)
→ `prerequisite`: mastery đọc: cong-cung-mau vững? quy-dong ca nào có evidence?
→ `diagnose`: chưa có evidence ca non-divisible → LearningAction.teach (không phải remediate)
→ `strategy`: novice ⇒ worked-example-first (expertise-reversal), nguồn: B6-L5 tr.21 EXPLICIT «Muốn cộng…»
→ `act`: workedStep «mẫu chung 3×4=12» + YOUR_TURN
→ `student`: làm 1/2+1/3 tương tự, đúng → postHintSuccess(support=workedStep)
→ `retry independent`: bài mới 2/5+1/3, không hỗ trợ → independentAttempt ✓
→ `transfer` (đề xuất): bài lời văn cùng ca — TransferProbe
→ `mastery update`: replay; claim vẫn <mastered (coverage các ca khác)
→ `review`: ReviewSchedule đặt 7d
→ `parent`: «Con vừa học cộng phân số khác mẫu (SGK Toán 5 tr.21). Tối nay hỏi con: vì sao phải quy đồng?»
