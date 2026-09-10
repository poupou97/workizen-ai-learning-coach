# WAL-239 — CHECKPOINT vòng bằng chứng (2026-09-09)

`STEM_SAFE` = **UNKNOWN** · `LEARNABLE` = **0** · SAM mass scale = **BLOCKED**.
Ticket giữ ở trạng thái checkpoint: phần CODE **chưa** thi công. Sự thật hơn
việc đóng ticket.

---

## A · FORMULA — ĐÃ XONG, ĐÃ PROMOTE

| | |
|---|---|
| `FORMULA_TOTAL` | 4.885 |
| `FORMULA_BLOCK_BUILT` | **2.815 (57,6%)** |
| `FORMULA_IN_READ_STREAM` | 2.699 |
| AVOID-C / chưa chứng minh được sở hữu | 2.070 |
| `BO_CAT_KHONG_TRON` | 148 |

Kiểm giao hàng đúng thứ trẻ thấy (n=82, 38 sách, đóng băng trước khi soi):
**`SOURCE_FAITHFUL` 76/82 = 92,7%** · TRUNCATED 2 · PROSE_CONTAMINATED 2 ·
AMBIGUOUS 2 · **SYMBOL_MISSING 0 · WRONG_REGION 0 · ORDER_WRONG 0** ·
`ORDER_PRESERVED` **100%**.

Bất biến sản phẩm: `OPENABLE_RECORDS` **2.974** · `DISTINCT_OPENABLE` **2.778**.

**Nợ:** 2.070 vùng AVOID-C (tỉ lệ hại **chưa đo**, KHÔNG suy từ 88,7% cũ) ·
148 vùng cắt không trọn · TTS câm (nợ đã nhận).

---

## B · CODE — DỮ LIỆU ĐÃ SỬA

`CODE_LABELED_TOTAL` = 875. Theo môn (bộ phân loại **đã sửa**):
Tin học 803 (91,8%) · Toán 39 · môn khác 20 · Công nghệ 9 · **Hoá học 2 (0,2%)**.

Phân họ theo bằng chứng in: `TRUE_PROGRAM_CODE` **333 (38,1%)** ·
pseudocode/robot 18 · **metadata in ấn 8 (0,9%)** · **chưa phân được 516 (59,0%)**.

⇒ **`DOCLING_CODE != TRUE_PROGRAM_CODE`.**

### Phép đo đã bị bác bỏ — giữ nguyên để tái hiện
| đã báo | đúng | nguyên nhân gốc |
|---|---|---|
| «53,5% vùng code ở Hoá học ⇒ gần chắc là trang bản quyền» | Hoá học **0,2%**; bản quyền **0,9%** | bộ phân loại môn khớp **chuỗi con**: `'khoa-hoc'` chứa `'hoa-hoc'` |

Đã sửa: `tool/corpus/subject.py` khớp theo **ranh giới đoạn**, 6 test hồi quy
phân biệt `hoa-hoc` · `khoa-hoc` · `khoa-hoc-tu-nhien` · `dinh-huong-khoa-hoc-may-tinh`.

---

## ⚠ ĐÍNH CHÍNH 2026-09-10 — MỤC C VÀ D DƯỚI ĐÂY DỰA TRÊN MỘT PHÉP ĐO SAI

Xếp loại «mất gần hết (chỉ còn SỐ DÒNG)» — 8/16 ca — **là artefact của phép
đo, không phải sự thật sản phẩm.** Truy bốn ca ấy xuyên suốt tới `assets/pack`:
**21/21 dòng mã đều tới tay trẻ.** `stem_exposure` chỉ đếm đoạn phủ ≥60% vào
vùng; cột số dòng hẹp nên phủ 100% và được đếm, còn dòng mã thật đã bị hàn vào
văn xuôi rộng cả trang nên phủ 0,9%–39,7% và rớt ngưỡng.

Hư hại có thật, nhưng là **BĂM NHỎ VÀ ĐẶT SAI CHỖ**, không phải mất nội dung:
`blocks()` xé 60,2% chương trình thành nhiều khối và hàn 88,0% vào văn xuôi.

Giữ nguyên mục C và D làm bằng chứng về một phép đo đã bị bác bỏ.
Căn nguyên, bản vá và số đo đúng: [WAL-239-CODE-ROOT-CAUSE.md](WAL-239-CODE-ROOT-CAUSE.md).

---

## C · CODE — AN TOÀN HIỆN TẠI (mẫu, KHÔNG suy rộng)

n=16 `TRUE_PROGRAM_CODE`, đóng băng: **HẠI 15/16 = 93,8%**.

Hai họ hỏng:
- **A · nội dung còn, CẤU TRÚC MẤT** (4 ca) — thụt lề bẹp. Với Python
  **thụt lề là NGỮ NGHĨA**, nên đây là chương trình KHÁC, không phải mất
  trình bày.
- **B · nội dung MẤT** (8 ca) — chỉ còn số dòng: `BFS_Traversal` → «1 2 3 4 5» ·
  `countNum` → «3 4 2 6 1 5» · `Hanoi` → «3 4 5 6 7 1 2».

---

## D · POC (KHÔNG canonical) — hình học có dựng lại được cấu trúc không

`tool/corpus/code_poc.py` · mẫu đóng băng n=17, seed 20260922, 5 sách, phân
tầng theo họ ký hiệu (REPL · hàm nhiều dòng · lồng nhau · if/else · vòng lặp ·
gọi hàm · chuỗi · toán tử · ngoặc · số).

Chỉ dùng ba thứ **đo được từ trang in**: `y` → ranh giới & thứ tự dòng ·
`x` → bậc thụt lề · chuỗi ký tự → nội dung **giữ nguyên**.

| trục | kết quả |
|---|---|
| `LINES_PRESERVED` | **17/17 = 100%** |
| `CONTENT_COMPLETE` | **17/17 = 100%** |
| `INDENTATION_RECONSTRUCTED` | 9/17 = 52,9% |
| `INDENTATION_PRESERVED` (một bậc, không có gì để dựng) | 4/17 = 23,5% |
| `INDENTATION_UNRESOLVED` | 4/17 = 23,5% |
| `ORDER_WRONG` | 0 |

### ⭐ Phát hiện quyết định

Đúng ca tới tay trẻ thành «1 2 3 4 ⏎ 5» dựng lại **hoàn chỉnh, 4 bậc thụt lề**,
từ **chính dữ liệu OCR mà đường dựng đã có**:

```
def BFS_Traversal (V,Adj) :
    mark = [False]*len(V)
    for s in V:
        if not mark[s]:
            BFS (Adj, s)
```

⇒ **HƯ HẠI KHÔNG NẰM Ở OCR. Nó nằm ở BƯỚC GỘP KHỐI của đường đọc**
(`page_paragraphs` bẹp mã thành khối văn xuôi rồi đánh rơi các dòng mã).

### Giới hạn đã đo
- 4/17 `INDENTATION_UNRESOLVED`: sách in **số dòng ở lề trái** và OCR gộp con
  số vào cùng dòng chữ ⇒ `x` mất nghĩa. **Không đoán** — trả UNRESOLVED.
- Trang có **hai cột** (mã + chú giải bên phải) bị gộp ngang thành một dòng.

---

## E · SO SÁNH BỐN BIỂU DIỄN

| | trung thành nguồn | token | dòng | thụt lề | sao chép | đọc giọng | phủ |
|---|---|---|---|---|---|---|---|
| **A. OCR hiện tại** | ❌ 93,8% hỏng | ⚠ | ❌ | ❌ | ✅ | ✅ | 100% |
| **B. dựng lại từ hình học** | ✅ | ✅ 100% | ✅ 100% | ✅ 76,5% | ✅ | ✅ | 76,5% |
| **C. ảnh vùng nguồn** | ✅ | — | — | ✅ | ❌ | ❌ | 100% |
| **D. lai (B khi chứng minh được, C khi không)** | ✅ | ✅ | ✅ | ✅ | phần lớn | phần lớn | 100% |

---

## F · KHUYẾN NGHỊ — hướng NHỎ NHẤT có bằng chứng

**SỬA ĐƯỜNG CHỮ (fix text pipeline), không dựng kiến trúc mới.**

Lý do: dữ liệu nguồn **đã đủ tốt** — 100% dòng và nội dung dựng lại được từ
OCR sẵn có. Không cần `CodeSourceBlock`, không cần ảnh làm biểu diễn chính, và
mã vẫn **sao chép được / đọc được** — điều mà ảnh sẽ giết.

Dự phòng **C (ảnh)** chỉ cho phần `INDENTATION_UNRESOLVED`, tức khoảng 23,5%.

**KHÔNG thi công tối nay** theo đúng lệnh Founder. Đây là khuyến nghị, quyết
định kiến trúc để lại cho checkpoint sau.

---

## G · 516 CHƯA PHÂN ĐƯỢC
Không phân tay tối nay. Mẫu nhanh cho thấy phần lớn là **lời giải Toán**
(«Giao hoán: a + b = b + a»), không phải mã. `UNKNOWN` là trạng thái hợp lệ.
