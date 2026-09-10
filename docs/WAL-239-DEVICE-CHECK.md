# WAL-239 — KIỂM MÁY THẬT (2026-09-10)

Thiết bị: **Samsung SM-S928B (S24 Ultra)** · Android **16** · `R5CX62RCBNB`
qua cáp USB. Bản dựng: `app-debug.apk` từ `main = 8680573`.

Ảnh màn hình: `~/Desktop/wal-evidence/2026-09-10-device/` (29 khung).

---

## 0 · KIỂM ĐÚNG BẢN ĐANG CHẠY

«Success» của `adb install` **không phải bằng chứng**. Nên APK được **kéo
NGƯỢC từ máy** rồi mở ra đếm:

    khối `formula` trong index lớp 1   =   5
    khối mã nhiều dòng trong index l12 =  55
    kernel_blob.bin                     có mặt

Kho ảnh đẩy vào đúng thư mục app đọc (`app_flutter/hoc-cung-sam/incoming`),
`figures-g1` và `figures-g12`.

---

## A · `FormulaSourceBlock` — **ĐẠT**

Toán 1 · Bài 32 «Phép trừ số có hai chữ số cho số có hai chữ số» · trang in 61.

Đúng chỗ mà **trước PR #171 trẻ thấy TRỐNG RỖNG** (chuỗi OCR đã bị gỡ, khối
mới thì client không đọc được), nay hiện **ảnh cắt từ chính trang sách**:

    60 − 20 = ?     6 chục − 2 chục = 4 chục
                    60 − 20 = 40

* nội dung trọn vẹn, đọc được, không cắt cụt
* đứng **đúng thứ tự đọc**: sau «Tính nhẩm (theo mẫu).», trước «a) 70 − 50…»
* không có chú thích bịa, không có nhãn «Hình…»

## B · MÃ NGUỒN NHIỀU DÒNG — **ĐẠT**

Chuyên đề Tin học 12 (định hướng KHMT) · Bài 16 · trang in 80.

Trẻ đang thấy:

```
1 def BFS_Traversal (V,Adj) :
2     mark = [False]*len(V)
3     for s in V:
4         if not mark[s]:
5             BFS (Adj, s)
```

| trục | kết quả |
|---|---|
| ranh giới dòng | **5/5** |
| nội dung | **đủ, nguyên văn** |
| thứ tự | **đúng** — `def` đứng TRƯỚC thân hàm |
| thụt lề | **4 bậc nhìn thấy rõ** |
| số dòng in của sách | **giữ nguyên**, canh cột |
| vị trí trong bài | đúng, sau «Bảng 16.2» |

Chương trình thứ hai trên cùng trang cũng giữ đủ dòng:
`from Queue import *` · `fname = "graph.inp"` · `V,Adj = BuildGraph (fname)` ·
`BFS_Traversal (V,Adj)`.

**Đường sao chép còn nguyên:** nhấn giữ ra đúng bảng chọn của Android —
**Copy · Share · Select all**. Đây chính là thứ mà biểu diễn bằng ẢNH sẽ giết,
và là lý do khuyến nghị «sửa đường đọc» thay vì dựng `CodeSourceBlock`.

⚠ **So sánh trước/sau, cùng một bài:** trước bản vá, năm dòng ấy nằm ở **hai
khối khác nhau** và dòng `def` bị xếp **SAU** thân hàm (khối 39 so với 38),
mỗi mảnh hàn vào văn xuôi, tất cả bẹp thành một dòng.

---

## C · ĐIỀU THẤY THÊM, KHÔNG PHẢI HỒI QUY

Ngay dưới khối mã, bảng 16.2 vẫn còn **một bản bẹp thành văn xuôi**:
«STT 1 2 3 4 … 24 Thứ tự các đỉnh đã đánh dấu…», trong khi ảnh bảng đã hiện
đúng ngay phía trên. Đó là **nợ TABLE cũ**, không do vòng này sinh ra và không
nằm trong phạm vi được phép mở lại hôm nay. Ghi lại để không ai tưởng đã xong.

Chữ OCR của Toán 1 vẫn nhiễu nặng ở phần bảng tính dọc («5/khâm phô !! Il 14»)
— cũng là nợ cũ, không phải vùng công thức.

---

## KẾT

`FormulaSourceBlock` và mã nguồn nhiều dòng **đều tới được tay trẻ đúng như
thiết kế**, trên máy thật, qua đúng đường sản phẩm. Không phát hiện lỗi nào
cần vá.

Điều kiện tiên quyết cho `LEARNABLE_V1` đã xong.
