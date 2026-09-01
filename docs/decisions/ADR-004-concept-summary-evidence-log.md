# ADR-004 — ConceptSummary ba trục + log bằng chứng thô thay bản vá F1/F3, đóng wildcard F2

**Ngày:** 2026-09-01 · **Trạng thái:** ACCEPTED (thi hành quyết định Founder 2026-09-01)
**Bằng chứng:** chỉ thị Founder (Decisions 1–4) · `test/core/student/concept_summary_golden_test.dart`
(14 test, 10 kịch bản do Founder liệt kê) · `evidence_replay_test.dart` (9) ·
`problem_applicability_test.dart` (10) · 3 phép đột biến đều đỏ

---

## CURRENT (trước ADR này)

ADR-003 vá F1–F4 ở mức TRIỆU CHỨNG: `coverageIncomplete` thêm vào một enum state,
`SupportLevel` truyền vào lúc update, `denominator-equal` thêm một nhánh if. Founder bác
khung *"Concept mastery = min hay mean"* và yêu cầu sửa NGỮ NGHĨA.

## PROPOSED — đã áp

### F1 · `ConceptSummary` — ba trục độc lập (`concept_summary.dart`)

```
MASTERY ước lượng cao  ≠  COVERAGE đủ  ≠  CONFIDENCE cao
```

- `estimatedMastery` — trung bình trọng số theo lượng bằng chứng; **chỉ để xếp hạng nội
  bộ**, `null` khi chưa quan sát gì (UNKNOWN không bao giờ thành 0/FAILED).
- `Coverage` — ca đã/chưa quan sát so với **danh mục ca đã biết**; "quan sát" = có bằng
  chứng ĐỘC LẬP (luyện-có-gợi-ý không đếm — chặn F3 chui vào F1 bằng cửa sau).
- `ConfidenceFactors` — min(volume, consistency, recency), từng thừa số min trên các ca.
  Consistency đo **trong từng ca**: một ca toàn đúng cạnh một ca toàn sai KHÔNG phải mâu
  thuẫn — đó là `caseTransitionGap`, tín hiệu quý nhất. (Phát hiện khi golden ③ đỏ:
  bản đo gộp toàn khái niệm nghiền tín hiệu đó thành nhiễu.)
- `ConceptClaim` — thứ DUY NHẤT Parent Coach được nói. `mastered` đòi đủ CẢ BA trục;
  vững-mọi-ca-đã-quan-sát + còn ca chưa hỏi = `strongOnObserved`, không bao giờ `mastered`.
  Không lưu trạng thái "mastered" nào — mỗi lần đều suy lại, nên **ca mới phát hiện tự
  hạ claim** (golden ⑩).
- `min`/`mean`: `min` chỉ còn sống làm **gate của claim** (lượng hoá trên mọi ca);
  không cái nào là "sự thật" của mastery nữa. Mọi ngưỡng nằm trong `SummaryPolicy` có
  tên + lý do + thay được; hai ngưỡng thời gian là placeholder chờ F5.

### F3 · `LearningEvidence` — sự kiện thô là nguồn sự thật (`learning_evidence.dart`, `evidence_weighting.dart`)

- 7 loại sự kiện Founder liệt kê, log **append-only có dấu thời gian** (F5-ready), sự
  kiện mang `conceptIds` dạng danh sách (F6/Q-matrix-ready) + `timeSpent` (EduStudio).
- Trọng số bằng chứng **suy từ likelihood, không đặt hằng số**: câu trả lời bị can
  thiệp quyết định ⇒ P(đúng|biết) = P(đúng|chưa biết) ⇒ hậu nghiệm = tiên nghiệm — rơi
  ra từ Bayes (`bktPosterior`), không phải nhánh if. `learn` chỉ áp khi có *cơ hội
  luyện tập có tự thử* (định nghĩa opportunity chuẩn của BKT) ⇒ bấm-xem-gợi-ý 20 lần
  hay chép lời giải đều không in ra mastery. MC4 ⇒ guess ≥ 0.25 **theo cấu trúc đề**.
- `EvidenceWeightingPolicy` thay được; `replayMastery` tính lại toàn bộ từ log ⇒ đổi
  luật không cần migration. Test giữ một `_NaivePolicy` đối chứng: chênh lệch với policy
  bảo thủ **chính là kích thước vòng tự xác nhận** bị chặn.

### F2 · `FractionPairAnalysis` — mô hình ca, không phải phép chia lấy dư (`problem_applicability.dart`)

- 4 ca biên **vét cạn, loại trừ nhau** (equal / divides / coprime / non-coprime-non-div),
  kiểm bằng sweep 144 cặp. Malformed (0, âm, null) ⇒ `null` ⇒ TutorScope rỗng.
- Giữ phân biệt coprime vs non-coprime dù sách dạy chung phương pháp: `productExceedsLcm`
  tồn tại để trình chấm **không đánh sai đứa trẻ quy đồng 4,6 ra 12** thay vì 24.
- **Wildcard đóng**: method không khai `skillCaseId` bị loại khỏi phạm-vi-bài với
  `caseNotDeclared` (không khai = unknown = fail closed); chỉ còn dùng ở duyệt-khái-niệm.

## CONSEQUENCE

- ADR-001 §luật tổng hợp (`min các ca có bằng chứng`) **bị thay** bởi ADR này; phần còn
  lại của ADR-001 (mastery đặt ở SkillCase) giữ nguyên hiệu lực.
- ADR-003 các bản vá F1/F3 được **nâng cấp ngữ nghĩa** như trên; F2 siết thêm wildcard.
- `ConceptMastery.stateAt`/`derived` hạ cấp thành heuristic nội bộ — mã mới hướng phụ
  huynh **phải** đi qua `ConceptSummary`. (Chưa xoá để không phá 48 test cũ; xoá khi
  Parent Coach có thật.)
- Hạn chế ghi nhận: consistency phạt cả chuỗi "sai nhiều rồi đúng dần" (đang HỌC) —
  hướng sai an toàn (đánh giá thấp); thay bằng consistency trọng số gần đây khi có dữ
  liệu thật.
