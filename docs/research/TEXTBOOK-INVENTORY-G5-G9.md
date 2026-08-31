# Kiểm kê SGK — Lớp 5 & Lớp 9

**Ngày:** 2026-08-31 · Đo bằng `unzip -l`, `pdfinfo`, `pdfimages`, `pdffonts`.
**Không** gọi LLM cho phần kiểm kê. Bốn ảnh trang được xem trực tiếp để đánh giá chất lượng.

> 🔴 Đọc `TEXTBOOK-LICENSING-QUESTIONS.md` trước. POC đã **dừng** ở phase này.

---

## 1. Kho nguồn

`nguon-chi-thuc/` — **9,8 GB**, 12 archive (lớp 1→12) + `tam nhin ai vietnam.jpg`
+ `tap huan tri tue nhan tao/`. Work order chỉ cho phép chạm **lớp 5 và 9**.

| | Lớp 5 | Lớp 9 |
|---|---|---|
| archive | 741 MB | 923 MB |
| giải nén | 0,81 GB | 1,01 GB |
| số PDF | **37** | **37** |

## 2. Quy ước đặt tên — máy đọc được

```
<lớp>-<loại>-<môn>-<lớp>[-<biến thể>][-tap-<tập>].pdf
```
`sgk` = sách giáo khoa · `sgv` = **sách giáo viên** · `sbt` = sách bài tập (chỉ 1 tệp, TA9)

⭐ **`sgv` là phát hiện đáng giá nhất về mặt nội dung.** Sách giáo viên chứa mục tiêu
bài học, lỗi học sinh thường mắc, gợi ý tổ chức dạy — đúng nguyên liệu cho
`common_mistakes`, `mastery_hypothesis` và **Parent Coach**. Toán 5 SGV: 306 trang;
Toán 9 SGV: 282 trang, đều **dày hơn** SGK.

## 3. Bộ sách

**Kết nối tri thức với cuộc sống** — NXB Giáo dục Việt Nam. Xác nhận hai lần: watermark
trên từng trang, và bìa sau liệt kê trọn bộ 15 cuốn lớp 5.

⚠️ **Chỉ có MỘT bộ.** Việt Nam có ba bộ được phê duyệt (Kết nối tri thức · Chân trời
sáng tạo · Cánh Diều). Trường của học sinh có thể dùng bộ khác ⇒ *"AI hiểu con đang học
gì"* sẽ sai nếu ta chỉ biết một bộ. **Rủi ro sản phẩm, không phải rủi ro kỹ thuật.**

## 4. Mục tiêu POC (đã giải nén, 176 MB)

| Tệp | Trang |
|---|---|
| `05-sgk-toan-5-tap-mot.pdf` | 142 |
| `05-sgk-toan-5-tap-hai.pdf` | 138 |
| `05-sgv-toan-5.pdf` | 306 |
| `09-sgk-toan-9-tap-mot.pdf` | 122 |
| `09-sgk-toan-9-tap-hai.pdf` | 134 |
| `09-sgv-toan-9.pdf` | 282 |
| **tổng** | **1.124 trang** |

## 5. ⛔ Chất lượng: KHÔNG có lớp text — toàn bộ là ảnh quét

Ba phép đo độc lập, cùng một kết luận:

| Phép đo | Kết quả |
|---|---|
| `pdftotext` toàn bộ 142 trang | **0 ký tự** |
| `pdffonts` | **không font nhúng nào** |
| `pdfimages -list` | mỗi trang = **1 ảnh JPEG toàn trang**, 1094×1536, **100 ppi** |

**Hiệu chuẩn dụng cụ:** `pdftotext` chạy trên một PDF đối chứng cho 27.922 ký tự ⇒ công
cụ không hỏng, sách thật sự không có chữ. *(Con số 0 đồng loạt ở cả 6 tệp là dạng kết
quả phải nghi ngờ trước khi tin — đã kiểm.)*

### Hệ quả với pipeline trong work order §N

Work order giả định: `Files → Metadata → TOC → Structural parsing → …`
**Không chạy được.** Không có TOC để parse, không có heading, không có text. Mọi cấu
trúc phải đi qua OCR/vision trước.

Nguyên tắc *"CODE HANDLES BULK, LLM HANDLES SEMANTICS"* vẫn đúng — nhưng "code" ở đây
là **OCR**, và OCR mới là chi phí chính, không phải LLM.

## 6. ⭐ Nhưng có hai đường tắt do chính NXB tạo sẵn

Xem trang thật, không suy đoán:

**① Bảng thuật ngữ** — *"MỘT SỐ THUẬT NGỮ DÙNG TRONG SÁCH"* (trang in 139).
Danh sách **khái niệm kèm số trang do NXB biên soạn**: Chu vi hình tròn 107 · Diện tích
hình tam giác 95 · Diện tích hình thang 102 · Diện tích hình tròn 110 · Đường cao của
hình tam giác 92 · Đường tròn 105 · Héc-ta 54 · Hình tam giác nhọn/tù/vuông 91 · Hình
thang 98 · Hỗn số 23 · Ki-lô-mét vuông 53 · Phân số thập phân 14 · Số thập phân 32.

**13 concept từ MỘT trang**, và chúng là **SOURCE FACT** — không phải LLM inference.

**② Trang bài có cấu trúc thị giác rõ:** cờ "Bài 3" góc trên trái · hộp tiêu đề
"ÔN TẬP PHÂN SỐ" · mốc mục "luyện tập" · bài đánh số ①②③ · số trang góc dưới.
OCR + luật bố cục lấy được `chapter/lesson/heading` mà không cần LLM.

⇒ Ước tính lại: OCR **2–3 trang/cuốn** (thuật ngữ + mục lục) là đủ dựng khung concept,
thay vì 142 trang. Chi phí giảm khoảng **hai bậc độ lớn**.

## 7. Độ lệch số trang — bẫy cho `reference_pages`

PDF 12 = trang in 11 · PDF 140 = trang in 139 ⇒ **PDF = trang in + 1** (Toán 5 tập một).
Số trang trong bảng thuật ngữ là **trang in**. Nhầm hệ quy chiếu là trích dẫn sai trang
cho học sinh. Phải đo offset **cho từng cuốn**, không suy từ một cuốn.

## 8. Đọc được không?

**Có.** Dù chỉ 100 ppi, chữ và dấu tiếng Việt sắc nét trên trang đã xem. OCR khả thi.
⚠️ 100 ppi vẫn dưới chuẩn OCR thường dùng (300 ppi) — cần đo tỉ lệ lỗi thật trước khi
tin, đặc biệt với **công thức toán** và **phân số xếp chồng**.

⚠️ Bố cục giàu hình: nhiều bài hỏi về *hình vẽ* ("Hình A/B/C", ô màu). **OCR thuần sẽ
mất nghĩa** những bài đó ⇒ Camera Tutor cần vision, không chỉ text.

## 9. Chưa làm (đúng phạm vi cho phép)

Chưa OCR trang nào · chưa trích concept bằng LLM · chưa index · chưa embedding · chưa
chạm lớp nào ngoài 5 và 9 · chưa chạm môn nào ngoài Toán.
**LLM calls cho toàn bộ phase này: 0.**
