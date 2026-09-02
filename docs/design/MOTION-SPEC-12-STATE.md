# WAL-50 — MOTION SPEC 12 STATE (token-hoá, không số rời trong widget)

Token: `WalMotion` (wal_tokens.dart). Luật: state chỉ dùng token; CELEBRATE là
NƠI DUY NHẤT được «rình rang» và chỉ khi claim thật (luật mascot giữ nguyên).
Band 6-9/10-12 nhân thêm `WalBandDensity.celebrateScale` (0.5 / 0) — cùng
motion, «âm lượng» khác.

| State | Vào | Nhịp | Ghi chú |
|---|---|---|---|
| HELLO | fade+rise `gentle` | một lần | không lặp — chào rồi thôi |
| LISTENING | fade `gentle` | tĩnh | không nhấp nháy khi trẻ đang nói/đọc |
| THINKING | fade `gentle` | loop `thinkingLoop` (nhún nhẹ ≤4px) | sự chờ có gương mặt, không spinner |
| PROBE | fade `gentle` | tĩnh | câu hỏi cần yên tĩnh |
| HINT | fade+rise `gentle` | một lần | xuất hiện CÙNG sự kiện hintShown (F3) |
| YOUR_TURN | slide-in `stage` | tĩnh | chuyển vai rõ ràng |
| STEP_BACK | slide-out `stage` | một lần | SAM lùi có hình hài |
| TRY_AGAIN | fade `gentle` | tĩnh | KHÔNG rung lắc — sai là chuyện thường |
| EXPLAIN | fade `gentle` | tĩnh | bảng xanh đứng yên cho trẻ đọc |
| ADMIT_UNCERTAINTY | fade `gentle` | tĩnh | thú thật thì khiêm tốn |
| CELEBRATE | scale-bounce `celebrate` | một lần ×`celebrateScale(band)` | chỉ khi mastered/tiến bộ có bằng chứng |
| CAMERA_SCAN / REVIEW_DUE | fade `gentle` | tĩnh | badge tự nói, không cần động |

Tap feedback mọi nút: `tap` (120ms). Reduce-motion (hệ điều hành): mọi loop
tắt, giữ fade — sẽ nối khi làm accessibility pass.
