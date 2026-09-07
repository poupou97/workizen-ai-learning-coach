# FULL CORPUS CENSUS — baseline phase «FULL DATA 1–12»

Sinh bằng `tool/corpus/coverage_matrix.py`, đo 2026-09-07 trên `main` sau WAL-228.
**Không bảo trì tay.** Chạy lại:

```bash
python3 tool/corpus/tc2_attach.py --out <attach-root> $(danh sách 238 sách canonical)
python3 tool/corpus/coverage_matrix.py --attach <attach-root> --csv out.csv
```

## Mẫu số thật

| | |
|---|---|
| Sách canonical (có mục lục) | **238** |
| Bài canonical | **3.679** |
| Sách có OCR | **238 / 238** — không sách nào thiếu nguồn |
| Trang OCR toàn kho | 62.729 (531 sách) |

Kho OCR (531) rộng hơn mục lục canonical (238). Mẫu số của sản phẩm là **mục lục**,
không phải số sách đã OCR — đo pipeline bằng mẫu số của chính pipeline là tự chấm điểm mình.

## Ba mức (định nghĩa Founder)

| mức | định nghĩa | đo được |
|---|---|---|
| **L1 READABLE** | định danh đúng + dải trang đúng + đủ chữ để đọc | **3.142 / 3.679 = 85,4 %** |
| ├ trang sách xác nhận định danh | tiêu đề trên trang khớp mục lục | 2.824 = 76,8 % |
| **L2 VISUAL READY** | L1 + `semantic` dùng được | **63 = 1,7 %** |
| **L3 SAM READY** | L2 + kịch bản dạy đã soạn | **1 = 0,0 %** |

Theo lớp (L1 %): L1 64,6 · L2 90,9 · L3 81,5 · L4 83,1 · L5 82,2 · L6 92,3 ·
L7 94,2 · L8 90,0 · L9 79,3 · L10 87,3 · L11 88,3 · L12 86,0.

## ⭐ KHOẢNG CÁCH HỘI TỤ — con số quan trọng nhất của lần đo này

| | |
|---|---|
| Dữ liệu **đọc được** | 3.142 (85,4 %) |
| Sản phẩm **mở được** | **117 (3,2 %)** |
| Chênh | **3.025 bài** |

Lớp **1, 2, 3, 11, 12 có ĐÚNG 0 bài mở được** — 1.760 bài mà trẻ mở app ra không thấy gì.

Nguyên nhân đo được, không suy đoán: `LessonIndex.activitiesFor` chỉ trả về **5 họ
hoạt động** (Toán bài tập · TV đọc · TV viết · Sử nguồn · Khoa thí nghiệm) và
`subject_home_screen` khoá bằng `openable = acts.isNotEmpty`. **Không có họ «đọc
trang sách».** Nội dung đọc được của 3.025 bài kia không có đường nào vào sản phẩm.

`toanExercises` rỗng ở **mọi** lớp (đã kiểm hình dạng container, không phải lỗi đếm).

## Top blockers khỏi Level 1 (theo blast radius)

| # | họ nguyên nhân | số bài |
|---|---|---|
| 1 | `LESSON_IDENTITY_TITLE` — mục lục không có tên bài | **395** |
| 2 | `SOURCE_RANGE` — attach không gắn được vào trang nào | 107 |
| 3 | `LESSON_IDENTITY_AMBIGUOUS` — khoá định danh va chạm | 80 |
| 4 | `CONTENT_THIN` — dải trang có dưới 300 ký tự | 10 |

**Tiêu đề rỗng trong mục lục: 1.340 / 3.679 (36,4 %)** — nhưng attach **đọc lại được
681 tên từ chính trang sách** (581 có xác nhận hai chiều, conf 0,95), nên chỉ còn 395
bài thật sự không có tên. Đây là chữ của sách, không phải chữ máy đặt ra.

## Định danh bài — `(book, lessonNo)` KHÔNG ĐỦ (A4)

Đo trên corpus này:

| | |
|---|---|
| Bản ghi va chạm dưới `(book, no)` | **439** |
| Thêm `volume` cứu được | **0** |
| ├ trùng thật (cùng số, cùng trang) | 6 — lỗi đọc mục lục |
| ├ **đánh số reset theo chủ đề** | **310 — BÀI KHÁC NHAU** |
| └ không quyết được (thiếu `pageStart`) | 123 |
| Còn va chạm khi thêm `pageStart` | 43 |

Tin học 9 có hai «Bài 9» ở hai chủ đề khác nhau; GDTC có «Bài 1» cho mỗi môn thể
thao. Nối hai bài ấy làm một để tăng coverage nghĩa là **cho trẻ mở nhầm bài**.

## Nội dung KHÔNG phải nút thắt

Trung vị **5.420 ký tự/bài**, p10 1.281, **0 trang OCR thiếu** trên toàn bộ dải đã gắn.
Mỗi dòng OCR có bbox chuẩn hoá (x, y, w, h) ⇒ reading order / multi-column **có dữ
liệu để giải** (A5), không kẹt ở OCR phẳng.
