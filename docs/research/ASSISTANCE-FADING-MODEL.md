# WAL-68 — Assistance / Fading: MINIMUM SUFFICIENT ASSISTANCE (nghiên cứu, chưa ADR)

**Ngày:** 2026-09-01 · nối tiếp TEACHINGACT-TAXONOMY (WAL-67) · [ACADEMIC] kiểm trích dẫn khi ADR

## 1. Thang trợ giúp — ĐỐI CHIẾU, không hard-code

Thang ứng viên Founder (INDEPENDENT→PROMPT→SMALL_HINT→STRATEGIC_HINT→PARTIAL_SCAFFOLD→
DEMONSTRATION→WORKED_SOLUTION) khớp ba nguồn độc lập:
- [ACADEMIC] **Contingent tutoring (Wood/Bruner/Ross)**: 5 mức từ khích lệ chung → làm mẫu;
  LUẬT CHUYỂN MỨC là đóng góp chính: **sai ⇒ tăng ĐÚNG MỘT nấc; đúng ⇒ giảm ĐÚNG MỘT nấc** —
  đây là policy "minimum sufficient" có bằng chứng thực nghiệm lâu đời nhất.
- [ACADEMIC] **Assistance dilemma (Koedinger & Aleven 2007)**: không có mức tối ưu phổ quát —
  phụ thuộc miền/giai đoạn ⇒ thang phải là POLICY THAY ĐƯỢC (đúng khuôn EvidenceWeightingPolicy).
- [WAL] SupportLevel {none, hint, workedStep, fullSolution} = nén 4 mức của thang này,
  ĐÃ nối sẵn với evidence semantics (learn-only, no-credit...). Thang mới chỉ TINH HOÁ,
  không thay nền.

## 2. Policy đề xuất để POC (falsify trước khi ADR)

```
mức khởi đầu   = f(CaseMastery của ca đang gặp)      — vững thì vào INDEPENDENT, yếu thì PROMPT
sai            ⇒ +1 nấc (không nhảy cóc — Wood)       — trừ carelessError: giữ nấc
đúng có trợ    ⇒ −1 nấc NGAY bài sau (fade sớm)
đúng độc lập   ⇒ giữ INDEPENDENT + giãn ôn (ReviewSchedule đã có)
REVEAL_ANSWER  ⇒ chỉ khi trẻ đã thử ≥1 lần độc lập + đã qua nấc DEMONSTRATION
                 (bottom-out được PHÉP tồn tại — cấm nó là ép trẻ bế tắc; nhưng nó
                 không bao giờ là nước đầu, và evidence ghi fullSolution như đã có)
```

## 3. Metric fading — ĐO ĐƯỢC TỪ LOG HIỆN CÓ (không cần field mới)

| Metric (anti-goal §8: không tối ưu phụ thuộc) | Nguồn dữ liệu [WAL] |
|---|---|
| Independent attempt rate ↑ theo thời gian | EvidenceLog: independentAttempts / attempts |
| Hint depth trung bình ↓ | SupportLevel/EvidenceKind theo phiên |
| Khoảng cách giữa hai lần cần trợ giúp ↑ | timestamps của hintShown/hintRequested |
| Self-correction rate ↑ | EvidenceKind.selfCorrection |
| Transfer: đúng độc lập ở CA CHƯA GẶP của cùng concept | ConceptSummary.coverage tăng bằng independent |
| Retention: đúng khi reviewDue | ReviewSchedule × kết quả lần ôn |

**Câu trả lời cho câu hỏi lõi:** SAM chọn được minimum-sufficient vì (a) mức khởi đầu do
mastery quyết, (b) chuyển mức từng-nấc-một, (c) fade là MẶC ĐỊNH sau thành công — và cả ba
đều đo được bằng log đã ship. "SAM thành công khi trẻ cần SAM ít đi" thành 6 con số.

## 4. Việc mở → POC (ticket khi tới lượt): mô phỏng policy trên chuỗi evidence tổng hợp
(golden student trajectories) để falsify luật ±1 nấc trước khi ADR + trước khi slice dùng.
