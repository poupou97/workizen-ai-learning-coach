# WAL-239 — Audit vùng `code` (2026-09-09) · CHƯA ĐỔI GÌ, mang về cổng

Founder: «Do NOT automatically apply formula policy to the 875 CODE regions.
First validate the taxonomy itself.»

## 1 · Nhãn `code` KHÔNG dùng thẳng được — sai gần 60%

Phân loại bằng DẤU VẾT IN, không bằng nhãn:

| họ | n | | ví dụ |
|---|---|---|---|
| **chưa phân được — phần lớn là LỜI GIẢI TOÁN** | 516 | 59,0% | «Giải Tính một cách hợp lí: 66 + 289 + 134 + 311», «Giao hoán: a + b = b + a» |
| **mã nguồn thật** | 333 | 38,1% | «>>> a,b = 10,3» |
| pseudo-code / lệnh robot | 18 | 2,1% | «Xoay động cơ DC M1 (tiến, tốc độ)» |
| **trang bản quyền** | 8 | 0,9% | «Mã số: G3HH3R001a26» |

## ⚠ GIẢ THUYẾT TÔI ĐÃ BÁO CHO FOUNDER LÀ SAI

Tôi từng viết: *«53,5% vùng `code` ở Hoá học — gần chắc là trang bản quyền.»*
**Sai.** Trang bản quyền chỉ **8 vùng (0,9%)**. Con số 53,5% sinh ra từ chính
**bộ phân loại môn bị lỗi** (chuỗi `'khoa-hoc'` CHỨA `'hoa-hoc'`), nên «Tin học
định hướng **khoa học** máy tính» bị đếm thành Hoá học.

Đo lại bằng bộ đã sửa: **Tin học 803 (91,8%)** · Toán 39 · Hoá học **2 (0,2%)**.

## 2 · Phơi nhiễm

325 vùng mã nguồn thật · **246 (75,7%)** có chữ OCR hiện ra tại chỗ ấy.

## 3 · Soi mắt (n=16, seed 20260921, đóng băng trước khi soi)

| | n | |
|---|---|---|
| **mất gần hết** (chỉ còn SỐ DÒNG) | 8 | 50,0% |
| **mất cấu trúc** (nội dung đủ, thụt lề bẹp) | 4 | 25,0% |
| mất một phần | 2 | 12,5% |
| sai thứ tự | 1 | 6,2% |
| đọc được | 1 | 6,2% |

**⛔ HỎNG 15/16 = 93,8%.**

Ví dụ nặng nhất — chương trình 5–8 dòng, trẻ chỉ đọc được **dãy số dòng**:

- `BFS_Traversal` (5 dòng) → «1 2 3 4 5»
- `countNum` (6 dòng) → «3 4 2 6 1 5»
- `Hanoi` (7 dòng) → «3 4 5 6 7 1 2»
- `reverseorder` (5 dòng) → «2 3 4 5»

## ⭐ VÌ SAO CODE KHÔNG ĐƯỢC ÁP CHÍNH SÁCH CỦA CÔNG THỨC

**Với Python, THỤT LỀ LÀ NGỮ NGHĨA.** Bốn ca «nội dung đủ, thụt lề bẹp» không
phải mất định dạng — chúng là **chương trình khác**. `SelectionSort` bẹp thành
một dòng là một chương trình không chạy được và không dạy được.

Và mã nguồn có yêu cầu mà công thức không có: **sao chép được, đọc được bằng
giọng nói, gõ lại được**. Biến thành ảnh là giết cả ba.

## Đề xuất cho Founder Gate (KHÔNG tự làm)

Có một lựa chọn **tất định, trung thành nguồn**, không có ở công thức:

> **Dựng lại thụt lề từ TOẠ ĐỘ X IN TRÊN TRANG.** OCR đã cho x của từng dòng;
> thụt lề là thứ ĐO ĐƯỢC từ bản in, không phải đoán. Giữ được cả cấu trúc lẫn
> tính sao-chép-được.

Ba phương án để Founder chọn:

| | giữ ngữ nghĩa | sao chép được | đọc bằng giọng nói |
|---|---|---|---|
| A. giữ nguyên OCR (hiện tại) | ❌ 93,8% hỏng | ✅ | ✅ |
| B. ảnh vùng nguồn (như công thức) | ✅ | ❌ | ❌ |
| **E. dựng lại thụt lề từ toạ độ x** | ✅ nếu chữ đúng | ✅ | ✅ |

E chỉ đúng khi **chữ trong dòng vốn đã đúng** — mà 8/16 ca mất gần hết chữ,
nên E một mình không đủ. Nhiều khả năng cần **E cho ca chữ còn đủ, B cho ca
mất chữ**, nhưng đó là quyết định kiến trúc, tôi dừng ở đây.

## Trạng thái
`STEM_SAFE` = **UNKNOWN** · `LEARNABLE` = 0 · SAM mass scale = **BLOCKED**.
