# SAM-TUTOR-EVALUATION-FRAMEWORK — WS-E: đo «tutor tốt» thay vì «LLM trả lời hợp lý»

**Ngày:** 2026-09-02 · WAL-99 · Đây là GATE của WAL-30 (Generative Tutor): chưa có harness
này thì LLM-tutor không được bật — đã ghi trong điều kiện mở từ trước, nay có thiết kế.

## 1. Kiến trúc 3 tầng (rẻ→đắt), pattern từ mathtutorbench + socratic-bench

**Tầng 1 — deterministic checks trên LOG (rẻ, chạy mọi phiên, không cần judge):**
đo từ lineage/event ĐÃ CÓ trong data model:
- Premature-answer rate: %phiên có fullSolution TRƯỚC ≥1 independent attempt (REVEAL gate
  vi phạm — hiện = 0 do gate cấu trúc; với LLM-tutor thành metric giám sát).
- Hint-strength: phân bố support-level-đầu-tiên (quá mạnh = nhảy workedStep khi chưa cần).
- Question-rate kiểu mathtutorbench `_is_question` (thô nhưng đo được): %lượt tutor kết bằng
  câu hỏi cho trẻ thay vì phát biểu.
- Independence trend: independent-share theo tuần (metric TỐI THƯỢNG — §25.11).
- Ức chế: %phiên assess có tutoring (tutoringViolationsInExam — ĐÃ là hàm).
- Provenance: %câu dạy có explainTeaching ≠ null; support-type correctness (Delta-2 metrics).
- Consistency đa lượt: cùng exerciseId, hint sau không mâu thuẫn hint trước (so template id).

**Tầng 2 — scenario bank tất định (golden), chạy CI:** kịch bản có expected-internal-state
(không chấm văn phong): input cố định → assert decision/act/evidence đúng loại.

**Tầng 3 — judge hiệu chỉnh (đắt, offline):** pipeline socratic-bench Seed→Dialogue→Judge;
judge được calibrate với nhãn GIÁO VIÊN VN trước khi tin; trả về pass/fail/**undecidable**;
báo cáo kèm κ (bài học κ=0.50: đồng thuận người-người đã thấp — mọi số tầng 3 mang khoảng
tin cậy, quyết định gate dựa tầng 1+2, tầng 3 chỉ xếp hạng).

## 2. Scenario bank khởi điểm (13 kịch bản order yêu cầu — thành bảng đo)

| # | Kịch bản | Metric chính phải giữ |
|---|---|---|
| L2 toán đếm | câu ≤12 từ (reading level), không thuật ngữ ngoài stage |
| L4 quy đồng B57 | citation DEMONSTRATED («làm theo ví dụ»), không «sách nói» |
| L6 chưa có trong scope | fail-closed: nhận «chưa chắc», 0 nội dung bịa |
| L9 nghị luận | không viết hộ; góp ý chỉ sau draft |
| L12 chuyên đề | không dạy vượt stage dù model biết |
| Math/VN/Science/writing | đúng surface family + đúng evidence kind |
| Xin đáp án thẳng | premature-answer = 0; đề nghị thử bước |
| Trả lời bừa | phát hiện guessing (time+pattern), đổi probe, affect không phạt |
| Sai lặp nhiều lần | leo thang ĐÚNG MỘT nấc/lần; không tụt xuống chì chiết |
| Overconfident | coverage chặn claim; giao transfer trước khi cho qua |
| Hiểu-concept-sai-tính | executionError → practice, KHÔNG dạy lại concept |

## 3. Nối hiện trạng
FTP-Rate/WAL-63 (perception) + sim-harness WAL-87 (policy) là hai mảnh ĐÃ CÓ của tầng 1/2;
mistake_location-F1 (mathtutorbench) khớp attributeFailure — dùng làm eval cho chẩn đoán.
**Không số nào trong framework này cần LLM để TỒN TẠI** — LLM chỉ xuất hiện ở tầng 3 và ở
chính đối tượng bị đo.
