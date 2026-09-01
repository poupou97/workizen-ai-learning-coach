# Kiểm kê concept asset — đã XEM TRỰC QUAN từng ảnh, không dựa tên file

**Ngày:** 2026-09-01 · **Phương pháp:** mở và mô tả từng ảnh trong `concept/` (5 tệp)

## ⚠️ Phát hiện lớn nhất: BA định danh thị giác đang tồn tại song song

| Định danh | Xuất hiện ở | Mức hoàn thiện |
|---|---|---|
| **Cú tím–vàng đội mũ cử nhân** | `logo.png` + `mascote.png` + `mascote-transparent.png` | RẤT CAO — hệ nhận diện gần đủ sản xuất |
| Robot trắng generic | `intro-1.png` (ảnh minh hoạ giữa board) | THẤP — stock-style, không có hệ |
| Blob xanh lá đội hood chữ W (kiểu Workizen Hub) | `intro-2.png` | TRUNG BÌNH — vài pose, palette xanh corporate |

Đây là mâu thuẫn định danh thật, không phải tiểu tiết: sản phẩm không thể ship với ba nhân vật.
**Đề xuất (thuộc thẩm quyền tự quyết vì reversible): dùng CÚ làm baseline** — đúng lệnh Founder
§19 ("mascot hiện tại là baseline"), và là bộ duy nhất có: pose × biểu cảm × sticker × props ×
góc nhìn × size ladder × chế độ App Student/App Parent. ~~Robot trắng~~ DROP. Blob xanh =
REFERENCE ONLY (đại diện Workizen corporate, không phải WAL).
**Naming/brand cuối cùng: Founder-only** — mọi chữ "Workizen" trên asset giữ nguyên chờ quyết.

## Chi tiết từng asset

### 1. `mascote.png` (1536×1024) — KEEP ⭐ (asset giá trị nhất)
Character sheet đầy đủ của mascot cú: 5 tư thế chính (Chào bạn / Cổ lên / Học thôi / Tớ giúp
bạn / Tuyệt vời) · 6 pose học tập (Đang đọc / Đang ghi chú / Đang suy nghĩ / Khám phá / Dùng
laptop / Học nhóm) · 10 biểu cảm mặt (vui, cười tươi, nháy mắt, bất ngờ, yêu thích, tập trung,
suy nghĩ, thắc mắc, buồn, tự hào) · 6 sticker thoại nhanh ("Good job!", "Cổ lên!", "Tuyệt
vời!", "Ồ… hiểu rồi!", "Mình thử lại nhé!", "Không sao!") · props (mũ, kính, tai nghe, laptop,
sách, cúp, balo, kính lúp, bảng xanh…) · 4 góc nhìn (trước/nghiêng×2/sau) · bảng màu · **chế độ
App Student vs App Parent (cú đeo kính + tablet) vs Thông báo** · **size ladder 128→16px**.
- Audience: học sinh (chính), phụ huynh (chế độ riêng).
- Reusable: gần như toàn bộ. Tagline trên sheet: "Hiểu con – Dạy đúng – Tiến bộ mỗi ngày 💜".
- Conflict: không có pose CAMERA_SCAN và REVIEW_DUE (xem MASCOT-AUDIT).

### 2. `mascote-transparent.png` (1536×1024, RGBA) — KEEP
Cùng hệ cú, ~40 sprite tách nền sẵn để cắt dùng: poses + biểu cảm + props rời (balo, sách,
địa cầu, cúp, bảng a²+b²=c², bóng đèn, tên lửa, bong bóng thoại ?, !, Zz…). Nền chưa trong
suốt thật 100% (RGBA nhưng nền mờ tím-vàng) — cần cắt lại khi dùng thật; ghi việc vào Jira.

### 3. `logo.png` (1254×1254) — KEEP (chờ Founder chốt brand)
Bộ logo cú hoàn chỉnh: lockup ngang + dọc + app icon + phiên bản 1 màu (tím/đen/trắng-trên-tím)
+ **bảng màu có mã hex: 7C4DFF (tím chủ) · A78BFA (tím nhạt) · FFB800 (vàng) · FF7AC8 (hồng) ·
4CD4B0 (xanh ngọc) · F3EEFF · F7F7FC (nền) · 2D2D3A (chữ)** + thuyết minh ý nghĩa (cú = trí
tuệ; mũ = tri thức đồng hành; sách + W; ngôi sao = cảm hứng). Chữ "WORKIZEN AI Learning
Coach" — naming Founder-only, không tự đổi.

### 4. `intro-1.png` (1536×1024) — REFERENCE ONLY (nội dung) / DROP (thị giác)
Board giới thiệu kiểu corporate (logo Workizen XANH LÁ + robot trắng stock). **Giá trị nằm ở
NỘI DUNG:** chuỗi 7 khối "Nội dung giáo dục → Knowledge Graph → Student Model → Adaptive
Engine → Tutor Scope → AI Tutor → Learning Evidence" **khớp 1:1 kiến trúc mã hiện tại**, và
5 trải nghiệm chính: Camera Tutor · Ask Tutor · Daily Quest · Home & Learning Map · Parent
Coach. Vision "AI không chỉ giải bài, AI hiểu con đang ở đâu để dạy con đúng cách" — đúng
doctrine. ⚠️ "Ask Tutor — Hỏi bất kỳ" xung đột với lệnh Founder "tránh blank chatbot" —
khi làm UX phải chuyển thành tutor-trong-ngữ-cảnh, không phải ô hỏi tự do.

### 5. `intro-2.png` (1536×1024) — REFERENCE ONLY
Cùng nội dung 7 khối + 5 trải nghiệm nhưng mascot blob xanh lá kiểu Workizen Hub. Giá trị:
cách diễn đạt phụ huynh-đọc-được của từng khối ("Không chỉ biết đáp án, mà hiểu em đang ở
đâu trong bản đồ kiến thức"); tagline "Học cùng bạn, lớn cùng bạn". Thị giác xanh corporate
không hợp định hướng "ấm áp giáo dục gia đình" — không tái dùng.

## Khoảng trống asset (chưa có gì)
Không có: màn hình UI thật nào (Home/Mission/Camera/Map/Parent) · flow onboarding · learning
map visual · biểu diễn mastery/coverage/confidence · dark mode. ⇒ đúng trạng thái NOT STARTED
của UI; các board intro là pitch material, không phải thiết kế sản phẩm.
