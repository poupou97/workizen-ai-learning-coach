# SkillCase — khái niệm #2: `so-sanh-so-thap-phan` (WAL-36)

**Ngày:** 2026-09-01 · **Nguồn:** OCR Toán 5 KNTT tập một, Bài 11 tr.38–40 (PDF p039–p041, đã đọc nguyên văn)
**Câu hỏi:** SkillCase có đứng vững ở khái niệm THỨ HAI không, hay chỉ khớp tình cờ với `quy-dong`?

## Bằng chứng — SÁCH TỰ PHÁT BIỂU quy tắc theo trường hợp

Tr.39, nguyên văn ba gạch đầu dòng:
> • "**Nếu phần nguyên của hai số đó khác nhau** thì số thập phân nào có phần nguyên lớn hơn thì số đó lớn hơn."
> • "**Nếu phần nguyên của hai số đó bằng nhau** thì so sánh phần thập phân, lần lượt từ hàng phần mười, hàng phần trăm, hàng phần nghìn…"
> • "**Nếu phần nguyên và phần thập phân của hai số thập phân bằng nhau** thì hai số đó bằng nhau."

Tr.38 gắn nhãn VÍ DỤ theo ca: *"3,5 > 2,75 (phần nguyên có 3 > 2)"* · *"2,75 > 2,29 (phần
nguyên bằng nhau, hàng phần mười có 7 > 2)"*. Bài tập 1 tr.39 phủ đúng ba ca (a: 37,29/36,92 —
ca ① · b: 135,74/135,75 — ca ② · c: 89,215/89,215 — ca ③).

**Ca thứ tư nằm ở MỤC SAU** (tr.40 "Số thập phân bằng nhau"): so sánh khi hai phần thập phân
KHÁC ĐỘ DÀI (76,3 vs 76,30 · 8,61 vs 8,6100) đòi luật *"viết thêm (hoặc bỏ) chữ số 0 ở tận
cùng"* — dạy tách riêng, SAU quy tắc ba ca.

## Kết luận

**① SkillCase verdict: KEEP, lần kiểm thứ hai.** 4 ca vét cạn/loại trừ nhau, phân tất định từ
bề mặt đề (`decimal_comparison_case.dart`, 7 test, sweep 13×13). Schema Concept→SkillCase→Method
**không đổi một dòng** — bất biến F1 (strongOnObserved khi ca ④ chưa quan sát) tái dùng nguyên.

**② Phát hiện cấu trúc MỚI: ranh giới ca nằm cả GIỮA CÁC MỤC trong một bài, không chỉ giữa các
lớp.** `quy-dong` tách ca theo lớp 4/5; `so-sanh-so-thap-phan` tách ca theo mục tr.39/tr.40 cùng
một cụm bài. Hệ quả: định vị "đã dạy chưa" không thể chỉ dựa `introducedGrade` — cần tới
mục/trang (`ConceptExposure.lessonId/pageStart` đã chứa được; `LearningStage.lessonId` đã đúng
độ mịn — không cần đổi schema, cần dữ liệu exposure đúng độ mịn khi ingest).

**③ Phân ca là thuộc tính BỀ MẶT đề bài, không phải giá trị.** 0,70 = 0,7 về giá trị nhưng thuộc
ca ④ vì đứa trẻ cần luật số-0 để NHÌN RA — chuẩn hoá trước khi phân ca là xoá mất đúng ca cần
chẩn đoán. (Trùng nguyên tắc `productExceedsLcm` của F2: giữ phân biệt toán học dù phương pháp
dạy gộp.)

**④ Bằng chứng phụ cho Q-matrix nội-khái-niệm:** bài 2 tr.39 ("Sắp xếp 3,604; 2,875; 2,857;
3,106") là MỘT bài chạm NHIỀU CA của cùng khái niệm (3,604/2,875 → ca ①; 2,875/2,857 → ca ②) —
`ExerciseSkillMap` hiện tại biểu diễn được (requirements cùng concept, khác case). WAL-54
(ca dùng chung giữa các CONCEPT khác nhau) vẫn mở.

## Giới hạn
Vẫn là MỘT MÔN (Toán) và một sách (KNTT). Khái niệm #3 nên lấy ở môn khác (Tiếng Việt?) trước
khi tin abstraction ở quy mô liên môn. Chưa có method catalogue cho khái niệm này (chỉ phân ca).
