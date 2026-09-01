# WAL-32 proxy — ảnh-giả-điện-thoại: chuỗi OCR→ca SẬP THẾ NÀO khi input xấu đi

**Ngày:** 2026-09-01 · **Loại bằng chứng:** tổng hợp tất định (proxy), KHÔNG phải ảnh thật
**Công cụ:** `tool/poc/degrade_phone_sim.py` (Pillow, seed cố định) + `ocr_pdf.swift` + pipeline WAL-33
**Vì sao proxy:** Founder không có ảnh; không tìm được dataset ảnh-SGK-Việt công khai (CROHME/
HME100K là biểu thức viết tay cô lập, cần đăng ký — ghi follow-up). Proxy đo được ĐƯỜNG CONG
suy giảm có kiểm soát; ảnh thật vẫn là chuẩn vàng khi có.

## Thiết kế
3 trang baseline (chứa đúng 5 biểu thức đã xác minh trên scan sạch) × 3 mức hỏng:
L1 nhẹ (nghiêng 1.5%, sáng 92%, JPEG75) · L2 vừa (+bóng góc, blur 1.0, JPEG55) ·
L3 nặng (nghiêng 9%, sáng 62%, bóng đậm, blur 1.6, nhiễu, JPEG30).

## Kết quả đo

| Mức | Recall (5 biểu thức chuẩn) | Biểu thức LẠ (không có trong baseline) |
|---|---|---|
| Scan sạch | **5/5** | 0 |
| L1 nhẹ | **2/5** | 3 |
| L2 vừa | 1/5 | 1 |
| L3 nặng | **0/5** | 5 (toàn bịa: `15/1−5/7`, `4/7−14/40`, `1/7+43/60`…) |

## Ba phát hiện — hai cái ĐỔI KIẾN TRÚC

**① FALSIFIED: "chuỗi hiện tại fail-closed dưới input xấu."** Trên scan sạch nó chỉ IM LẶNG
khi không chắc (đối chứng âm 0 false-positive). Dưới ảnh-giả-điện-thoại, OCR đọc nhầm chữ số
→ bộ dựng LẮP RÁP token nhầm thành biểu thức trông-hợp-lệ → phân ca TỰ TIN trên dữ liệu bịa.
Vi phạm trực tiếp lệnh "không bù OCR xấu bằng cách bịa cấu trúc toán học". (Một phần "biểu
thức lạ" có thể là nội dung thật của trang mà baseline chưa ghép được — chưa có nhãn tay để
tách; nhưng các mẫu như mẫu-số-1 `15/1` gần chắc là misread.)

**② Apple Vision conf ≈ 1.00 NGAY CẢ ở L3** ⇒ confidence của OCR **không dùng được** làm
cổng fail-closed. Cổng phải là kiểm tra ĐỘC LẬP phía WAL: (a) plausibility số học theo khối
lớp (mẫu số 1, tử >> mẫu bất thường…); (b) tái-phát-hiện nhất quán qua ≥2 biến thể tiền xử
lý (deskew/binarize) trước khi nhận; (c) chỉnh phối cảnh trước OCR (document rectification
chuẩn).

**③ Màn xác nhận "tớ đọc được thế này" (WAL-52) KHÔNG phải tiện ích UX — nó là TẦNG AN TOÀN
BẮT BUỘC** ở chất lượng OCR hiện tại: mọi biểu thức từ ảnh camera phải qua xác nhận của học
sinh trước khi vào chẩn đoán/evidence. Nâng từ "nice UX + thu nhãn" lên yêu cầu kiến trúc.

## Giới hạn
Proxy không tái tạo: cong giấy, moiré, rung tay, autofocus. Ảnh thật từ Founder (WAL-32) vẫn
cần để chốt số; đường cong ở đây là CHẶN DƯỚI hành vi cần phòng thủ.
