# UX Principles + Information Architecture — dẫn xuất từ USER LOOPS, không từ màn hình

**Ngày:** 2026-09-01 · **Trạng thái:** DESIGNED (hypothesis — validate bằng vertical slice đầu tiên)
**Đầu vào:** 4 loop Founder (§9) · EDUCATION-UX-RESEARCH.md · domain state thật (ADR-004/005)

## 1. Bảy nguyên tắc UX của WAL

1. **Hành-động-kế-tiếp là màn hình chính.** Học sinh mở app thấy MỘT việc do engine đề xuất kèm lý
   do trẻ-đọc-được — không phải danh mục nội dung. (`AdaptiveDecision.reason` là copy, không phải log.)
2. **Không con số nào giả vờ chính xác.** Mastery hiển thị bằng mức + độ phủ ("vững 2/3 dạng"),
   confidence hiển thị bằng chữ ("khá chắc"/"chưa đủ bằng chứng"). Cấm %; ước lượng trông như ước lượng.
3. **Thất bại là dạng-bài-mới, không phải khiếm khuyết.** Ngôn ngữ hiển thị của `caseTransitionGap`
   là "dạng này MỚI với con"; mascot TRY_AGAIN; không đỏ, không trừ điểm hiện hình.
4. **Gợi ý là thang sinh-bằng-chứng.** Nhắc hướng → câu-hỏi-con (scaffold) → làm mẫu → lời giải; mỗi
   nấc ghi sự kiện; UI vẫn chúc mừng đúng-sau-gợi-ý, model lặng lẽ không ghi công (OATutor OnOpen).
5. **AI hiện diện trong ngữ cảnh, không phải hộp thoại trống.** Tutor mở lời bằng câu hỏi về BÀI ĐANG
   LÀM ("Con thử tới đâu rồi?"); mascot là hoá thân của trạng thái hệ thống (THINKING khi chẩn đoán,
   HINT khi thật sự có gợi ý) — không nhảy múa trang trí.
6. **Fail closed có gương mặt tử tế.** caseUnknown/ảnh mờ ⇒ "Tớ chưa chắc mình đọc đúng đề — chụp
   gần hơn nhé?" — không bao giờ đoán bừa rồi dạy sai.
7. **Mascot có vùng cấm** (kế thừa Hub): cấm ở màn claim-bằng-chứng của phụ huynh, màn riêng
   tư/dữ liệu, màn lỗi mất dữ liệu. Ở đó UI phẳng và nghiêm túc.

## 2. IA tối thiểu (hypothesis — validate trước khi commit)

**Học sinh — 3 bề mặt + 1 overlay** (trẻ em: càng ít điểm đến càng tốt; KHÔNG copy bottom-nav Hub):
```
① Hôm nay (Mission)   — hành động kế tiếp · hàng ôn tới hạn · thử-thách-phủ (ca chưa quan sát)
② Camera / Tutor      — chụp bài → chẩn đoán → dạy trong ngữ cảnh (một flow, không phải hai tab)
③ Bản đồ học          — Concept↦dạng đã vững/mới/chưa thử; cửa vào ôn tự do
   (overlay) Hồ sơ/cài đặt — góc màn hình, không chiếm tab
```
**Phụ huynh — 2 bề mặt** (tách chế độ, cùng app):
```
① Tối nay             — MỘT khuyến nghị (ParentExplanation + citation) · trạng thái con 5 giây
② Tiến bộ             — theo thời gian, theo khái niệm; mức claim + độ phủ, không %
```
AI Lab: **chưa vào IA MVP** — giữ ở backlog (P2), tránh loãng core loop.

## 3. AI-first — cụ thể hoá (§12)
- Tutor presence theo ngữ cảnh (đang làm bài nào, ca gì, mastery ra sao) — đã có sẵn trong domain state.
- Mission sinh từ engine mỗi ngày (adaptive), giải thích được "vì sao bài này" (explain-why = `reason`).
- Camera→Tutor là MỘT cử chỉ liền mạch; kết quả scan hiển thị "tớ đọc được thế này" cho trẻ xác nhận
  (confidence hiển thị + sửa được) trước khi dạy — vừa UX vừa thu nhãn cho OCR.
- Bản đồ học tự đổi màu theo bằng chứng mới — "app hiểu mình" đến từ nhìn thấy tiến bộ thật.

## 4. Vertical slice đầu tiên (§18)
Student Mission → Camera/Problem → Tutor interaction → Evidence → next action — trên đúng lát
`quy-dong` đã có domain đầy đủ. Parent slice theo sau khi evidence model đỡ được claim thật (đã đỡ được).
