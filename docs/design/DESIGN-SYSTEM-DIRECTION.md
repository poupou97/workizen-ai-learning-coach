# Design System Direction — WAL

**Ngày:** 2026-09-01 · **Trạng thái:** DESIGNED (direction, chưa phải spec) · dựa trên asset THẬT
(`logo.png` palette) + bài học đo được của Tổng Tài (WCAG) + luật Hub (mascot, calm).

## 1. Tính cách (đánh giá theo tiêu chí Founder §11)
Ấm áp giáo dục gia đình ✓ (tím lavender + vàng ấm, mascot cú) · bình tĩnh ✓ (nền off-white, không
badge đỏ) · thông minh ✓ (cú/mũ cử nhân) · khích lệ ✓ (sticker hệ thống) · đáng tin ✓ (ngôn ngữ
bằng chứng) · AI-native ✓ (mascot = hoá thân trạng thái engine) · không corporate ✓ (bỏ xanh lá
Workizen corporate khỏi bề mặt trẻ em) · không quá trẻ con 🟡 (rủi ro THPT — giảm bằng chế độ gọn).

## 2. Màu — lấy từ `logo.png`, áp bài học Tổng Tài
| Vai trò | Nền (-500) | Chữ trên trắng (-700, PHẢI đo ≥4.5:1) |
|---|---|---|
| Primary / AI | `#7C4DFF` | đậm hoá (~`#5B21B6` — đo khi làm token) |
| Accent ấm / khích lệ | `#FFB800` | KHÔNG dùng làm chữ trên trắng |
| Nền | `#F7F7FC` / `#F3EEFF` | — |
| Chữ chính | — | `#2D2D3A` |
| Hồng (yêu thích) `#FF7AC8` · Xanh ngọc (đúng/mới) `#4CD4B0` | trang trí/biểu đồ | cặp -700 riêng |
**Luật cứng:** màu bước -500 là màu NỀN/ICON; chữ dùng cặp -700 đo được (lỗi 2.31:1 của Tổng Tài
không được tái diễn). Dark mode: chưa làm — token phải khai từ đầu theo cặp sáng/tối.

## 3. Trạng thái HỌC — ánh xạ domain → thị giác (điểm khác biệt của WAL)
| Domain (ConceptClaim/…) | Thị giác | Cấm |
|---|---|---|
| `mastered` | đầy + ấm (vàng/ngọc), mascot CELEBRATE | dùng khi coverage chưa đủ |
| `strongOnObserved` | đầy MỘT PHẦN + phần "chưa thử" hiển thị rõ, trung tính | che phần chưa thử |
| `developing` | đang lớn (mầm/nửa) | thanh % |
| `needsWork` | "dạng cần luyện" — ấm, không đỏ | ngôn ngữ khiếm khuyết |
| `insufficientEvidence` / `noEvidence` | dấu hỏi thân thiện "chưa đủ dữ liệu để nói" | coi như 0/fail |
| `reviewDue` | vòng lặp/đồng hồ nhẹ | Zz (buồn ngủ), đỏ hối thúc |
| caseUnknown (camera) | mascot CURIOUS + "chụp lại gần hơn?" | spinner trơ, đoán bừa |
| AI đang chẩn đoán | mascot THINKING | skeleton vô hồn |

## 4. Hình khối · chữ · chuyển động
Bo góc lớn (16–20dp) · thẻ mềm, đổ bóng nhẹ · đệm rộng · chạm ≥48dp · type scale lớn cho tiểu học
(≥16sp thân bài học sinh), hệ chữ hỗ trợ tiếng Việt đầy đủ dấu · motion: ease nhẹ, mascot có nhịp
"thở" khi idle; KHÔNG bounce ở màn nghiêm túc; tôn trọng reduce-motion. Accessibility: TalkBack/
VoiceOver + dynamic type từ ngày đầu (luật Hub); TTS cho gợi ý là ứng viên POC.

## 5. Age adaptation
Một hệ token, hai "âm lượng": Tiểu học = mascot đậm, sticker, chữ to; THCS+ = mascot thu về góc
(chỉ đầu, biểu cảm điềm tĩnh), mật độ thông tin cao hơn. Cắt theo LearningStage đã có trong domain.

## 6. Việc mở (Jira)
Token hoá đầy đủ (đo contrast từng cặp) · cắt alpha sprite mascot + 2 state thiếu (CAMERA_SCAN,
REVIEW_DUE) · thử nghiệm chế độ gọn cho THCS · dark palette · motion spec cho 12 state.
