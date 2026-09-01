# Hệ trạng thái mascot — ánh xạ 12 state Founder yêu cầu vào asset ĐÃ CÓ

**Ngày:** 2026-09-01. Nguyên tắc: tái dùng sprite có sẵn; chỉ 2 state thiếu thật.

| State (Founder §8) | Asset có sẵn | Trạng thái |
|---|---|---|
| HELLO | pose "Chào bạn!" (vẫy cánh) | ✅ có |
| THINKING | pose "Đang suy nghĩ" + biểu cảm "suy nghĩ"/bong bóng "?" | ✅ có |
| HINT | sprite bóng đèn + bong bóng 💡 (transparent sheet) | ✅ có |
| ENCOURAGE | pose "Cổ lên!" (tua vàng) + sticker "Cổ lên!" | ✅ có |
| CELEBRATE | pose "Tuyệt vời!" (cúp + confetti) + sticker | ✅ có |
| TRY_AGAIN | sticker "Mình thử lại nhé!" + "Không sao!" + biểu cảm buồn-nhẹ | ✅ có |
| CURIOUS | pose "Khám phá" (kính lúp) + biểu cảm "thắc mắc" | ✅ có |
| EXPLAIN | pose bảng xanh + que chỉ (có bản a²+b²=c²) | ✅ có |
| LISTENING | pose tai nghe | 🟡 tạm dùng — tai nghe gợi "nghe nhạc" hơn "đang lắng nghe con nói"; cân nhắc biến thể nghiêng đầu + tai vểnh |
| CAMERA_SCAN | — | ❌ THIẾU — không có prop camera/khung scan nào trong cả 3 sheet |
| DAILY_MISSION | sprite tên lửa (tạm) | 🟡 tạm dùng — tên lửa = "khởi hành nhiệm vụ" chấp nhận được; biến thể cầm checklist sẽ đúng nghĩa hơn |
| REVIEW_DUE | sprite trăng + Zz (nghĩa "nghỉ", KHÔNG phải "tới hạn ôn") | ❌ THIẾU về ngữ nghĩa — cần biến thể đồng hồ/vòng lặp; tuyệt đối không dùng Zz cho "ôn tập" (gợi buồn ngủ/chán) |

## Việc tạo (đưa vào Jira, không vẽ lại cả bộ)
1. Sprite **CAMERA_SCAN** (cú cầm điện thoại/khung ngắm) — cần cho Camera Loop.
2. Sprite **REVIEW_DUE** (cú + đồng hồ/mũi tên vòng, thân thiện không hối thúc).
3. Biến thể LISTENING nghiêng đầu; biến thể DAILY_MISSION cầm checklist (ưu tiên thấp hơn).
4. Cắt alpha thật cho toàn bộ sprite; kiểm nền tối; chuẩn hoá kích thước xuất.

## Luật dùng state gắn với domain (không phải trang trí)
- HINT chỉ xuất hiện khi hệ THẬT SỰ phát gợi ý (sự kiện `hintShown`/`hintRequested` được ghi log — F3).
- CELEBRATE gắn claim thật (`mastered`/tiến bộ có bằng chứng) — mascot không được khen vượt bằng chứng, cùng luật với Parent Coach.
- TRY_AGAIN là mặt định danh của `insufficientEvidence`/sai lần đầu — thất bại được thiết kế thành chuyện bình thường ("Không sao!").
- THINKING dùng khi engine đang chẩn đoán — sự chờ đợi có gương mặt, không spinner trơ.


## Cập nhật 2026-09-01 (WAL-47) — 13 CHIP TRẠNG THÁI PRODUCTION-USABLE

`assets/mascot/sam-<state>.png` (256px + @64): hello · listen · think · probe · hint ·
your-turn · step-back (cú đeo balo bước đi — SAM lùi lại có hình hài) · try-again (mặt
hiền ấm, KHÔNG dùng mặt khóc) · explain (letterbox-on-blur) · admit-uncertainty ·
celebrate-independence · camera-scan (kính lúp + badge camera) · review-due (đọc sách +
badge đồng hồ). Kiểm nền tối 2D2D3A + nền sáng: `_proof-dark.png` / `_proof-light.png`.
Sinh tất định bằng `tool/design/make_state_chips.py` (box tay-chọn từ lưới toạ độ).

**Dạng CHIP TRÒN thay vì alpha-cut** — quyết định có lý do: nền sheet là gradient mờ,
chroma-key local sẽ lem viền; chip viền tím dùng được trên MỌI nền (pattern avatar chuẩn),
đủ cho slice 1. **Residual (design pass sau):** ① alpha-cut thật từng sprite; ② art GỐC cho
CAMERA_SCAN/REVIEW_DUE thay badge lập trình (badge là giải pháp tạm đúng ngôn ngữ bộ cú).
