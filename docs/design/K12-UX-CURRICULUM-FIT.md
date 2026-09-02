# K-12 UX × CURRICULUM FIT (Task Order §18)

**Nguồn số:** registry 537 docs (304 SGK/220 SGV, 12 lớp) + curriculum-structure 7.199
bài + corpus semantic Toán/TV + AI curriculum 267 YCCĐ. Môn không có corpus/official
source → **UNKNOWN/NEED SOURCE**, không suy đoán.

## Grade band × môn (theo corpus THẬT trong registry)

| Band | Môn có trong corpus | Ghi chú fit |
|---|---|---|
| 1-2 | Toán, TV, Đạo đức, TNXH, ÂN, MT, GDTC, HĐTN, T.Anh | Concept 01-15 dùng được sau age-pass (chữ to, voice-heavy, ít text); «Tiết/Tuần» units (TV1 dạy theo TUẦN — structure-alt đã bắt `tuan`) |
| 3-5 | + Tin học, Công nghệ, Khoa học(4-5), LS&ĐL(4-5), T.Anh bắt buộc | Sweet-spot của concept hiện tại (overfit lớp 4-5 — xem dưới) |
| 6-9 | Ngữ văn, Toán, KHTN, LS&ĐL, GDCD, Tin, CN, ÂN, MT, GDTC, HĐTN-HN, NN2 | Concept CHƯA đủ: KHTN gộp Lý-Hoá-Sinh (màn 25/26 tách môn là mô hình 10-12, sai cho 6-9); cần Subject Home theo KHTN + phân môn |
| 10-12 | Văn, Toán, NN, Sử, Địa, GDKT&PL, Lý, Hoá, Sinh, Tin, CN, GDQP, chuyên đề | Concept KHÔNG đủ: thiếu chuyên đề học tập, tổ hợp môn lựa chọn, mật độ text cao, workspace formula-first; mascot phải rất nhẹ |

## Overfit đo được của bộ concept

- 34/38 màn minh hoạ bằng **Toán 4-5 phân số** → đúng cảnh báo «overfit Grade 4/5».
- Grade 1-2: onboarding wizard 5 bước, Home nhiều text, Settings XP — KHÔNG dùng được
  nguyên trạng; cần variant theo AGE-ADAPTIVE-UX.md.
- Grade 10-12: không màn nào xử lý «tổ hợp môn», «chuyên đề», ôn thi TN THPT — gap ghi
  nhận, KHÔNG chế màn mới khi chưa research corpus 10-12 sâu (240 sách vừa OCR xong sẽ nuôi).

## MODE READINESS ánh xạ UI (nối Coverage Dashboard §XXXII)

5 intent chip trên Home chỉ ENABLE khi mode READY theo lesson (từ pack):
Học trước cần overview+example (SECTION/EXAMPLE units) · Ôn cần review targets
(objectives+exercises) · Làm bài cần EXERCISE+mapping · Học phương pháp cần METHOD
(29 method Toán 4-5 hiện có — môn khác PARTIAL) · Kiểm tra cần assessment-suitable
items. Chip disabled kèm lý do thật («Bài này SAM chưa có bài tập») — không fabricate.
