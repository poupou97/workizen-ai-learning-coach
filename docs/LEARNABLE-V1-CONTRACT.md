# LEARNABLE_V1 — HỢP ĐỒNG NHỎ NHẤT (Founder DUYỆT 2026-09-10)

Trạng thái: **APPROVED — LEARNABLE_V1**. Chưa thi công: còn chờ kiểm máy thật
cho `FormulaSourceBlock` và mã nhiều dòng.

---

## ⛔ RANH GIỚI NGỮ NGHĨA — ĐỌC TRƯỚC KHI DÙNG SỐ Ở ĐÂY

**`LEARNABLE_V1` là hợp đồng CÓ BẰNG CHỨNG cho LÁT CẮT TSL ĐẦU TIÊN.
Nó CHƯA phải định nghĩa LEARNABLE của toàn K-12.**

`VISUAL_GROUNDED` là cổng bắt buộc **ở V1** vì quần thể ứng viên đo được đầu
tiên chính là lát cắt Khoa học/KHTN của TSL. Điều đó **KHÔNG** được suy rộng
thành «mọi bài K-12 muốn LEARNABLE đều phải có SemanticData / Trực quan».

Mô hình năng lực giữ nguyên ba bậc:

    READ  →  READ + VISUAL  →  READ + VISUAL + SAM

Các môn sau này — Ngữ văn · Lịch sử · Toán — và các dạng bài khác **có thể cần
bằng chứng học chủ động KIỂU KHÁC**. Khi tới lúc ấy, việc phải làm là tìm bằng
chứng đúng cho môn ấy, **KHÔNG phải chế ra `process`/`comparison`** cho đủ chỉ
số.

### Thiên lệch của quần thể V1 — nói thẳng

    100% Khoa học / KHTN   ·   lớp 4–9   ·   6 cuốn

**Không được trình bày như phủ K-12.** `SAM_READY` vẫn là **1**, không đổi
theo hợp đồng này.

Câu hỏi Founder đặt: *«What minimum evidence makes a real lesson safe and
useful enough to become LEARNABLE?»*

---

## 0 · VÌ SAO KHÔNG PHẢI MỘT BỘ DÒ MỚI

Thử đầu tiên của tôi là dò «câu hỏi in» thẳng trên pack bằng dấu hiệu chữ. Nó
khớp **92,6%** bản ghi — và mẫu đóng băng cho thấy nó là **nhiễu**:

    «?»  ·  «Bình ?»  ·  «>; ≤;= ?»  ·  «m2 ? ? ?»  ·  «EM CÓ BIẾT?»  ·  «Khám phá»

Một tín hiệu bắn ở 92,6% thì không phân biệt được gì. Bỏ. Founder cũng đã chốt
**thôi tối ưu extractor** — nên hợp đồng dưới đây chỉ dùng bằng chứng ĐÃ CÓ và
ĐÃ CHỨNG MINH, không thêm luật nhận dạng nào.

---

## 1 · HỢP ĐỒNG

Một bài là `LEARNABLE` khi **cả bốn** điều sau đúng. Mỗi điều đọc được từ dữ
liệu, không cần người phán đoán, không suy diễn.

### ① OPENABLE
Bài có bản ghi trong pack canonical với dòng đọc thật.
Đã đo: **2.974** bản ghi · **2.778** bài duy nhất.

### ② READ_SAFE
Mọi biểu diễn ĐÃ BIẾT LÀ HẠI trong dòng đọc ấy đã được thay bằng bản trung
thành nguồn, hoặc đã bị giữ lại:

* vùng công thức ⇒ ảnh trang in (`FormulaSourceBlock`), **không** phải chuỗi
  OCR chưa chứng minh;
* vùng mã chương trình ⇒ giữ nguyên dòng, hoặc để nguyên đường cũ khi hình học
  không đủ bằng chứng (fail closed);
* **bài còn vùng AVOID-C thì TRƯỢT** — chỗ ấy trẻ vẫn đang đọc chuỗi OCR mà
  ta chưa chứng minh được sở hữu, và tỉ lệ hại của 2.070 vùng ấy **chưa đo**.

⭐ Đây là cổng cắn thật, không phải cổng trang trí: nó loại **18/62 = 29,0%**
ứng viên.

### ③ VISUAL_GROUNDED  *(SỬA 2026-09-10 — bản cũ đã bị BÁC BỎ)*

Có ít nhất một `SemanticData` **có kiểu**, dựng bởi một luật CÓ TÊN với trust
`trustedStructuredLesson`:

    tsl-enumerated-steps-v1      (process)
    tsl-summary-parenthesis-v1   (comparison)

**VÀ** ít nhất **MỘT phần tử trẻ nhìn thấy** bên trong `SemanticData` ấy mang
**chữ nguồn đọc được, đã tin cậy**.

⛔ **BỊ GIỮ LẠI / chỗ trống / «xem trong sách» KHÔNG tính** là phần tử ấy.

Với `process` hôm nay: **≥ 1 bước đọc được**.

⚠ KHÔNG đóng đinh «bước» thành định nghĩa chung cho mọi kiểu về sau. Kiểu
semantic mới phải thoả **cùng nguyên tắc** bằng phần tử có nghĩa của CHÍNH NÓ.

#### Vì sao phải sửa — bằng chứng từ ĐƯỜNG HỌC THẬT

Câu cũ — «có ít nhất một `SemanticData` có kiểu» — **nhận cả sơ đồ rỗng ruột**.

Phản ví dụ cụ thể, **KHTN 6 Bài 8**: nó CÓ một `process`, nên đạt cổng cũ về
mặt chữ. Nhưng `process` ấy có đúng **một bước, và bước ấy BỊ GIỮ LẠI**. Trẻ
bấm ✨ Trực quan và nhận được **một tiêu đề với một ô xám, không chữ nào**.

Đo trên 44 ứng viên của cổng cũ: **7 bài (15,9%)** đúng dạng ấy.

Không viết tay, không LLM. Đây là thứ làm ✨ **Trực quan** thành một lối học
thật thay vì một tab rỗng.

### ④ NEXT_ACTION_REAL
`nextActionFor` trả về một bước có `basis` trỏ vào một thứ CÓ THẬT trong chính
bài ấy (`semantic.process:<id>`, số đoạn văn, hoặc câu hỏi in). Luật này đã
chạy trong sản phẩm, tất định, không recommender.

---

## 2 · HAI ĐIỀU CỐ Ý **KHÔNG** ĐƯA VÀO

**🦉 Kịch bản SAM KHÔNG phải điều kiện.** Kịch bản là hàng viết tay; đòi nó thì
`LEARNABLE` bị khoá ở **1** vĩnh viễn. Kiến trúc Founder nói *«SAM when
pedagogically allowed»* — tuỳ chọn, không phải cổng.

**Chấm điểm KHÔNG phải điều kiện, và phần lớn là KHÔNG ĐƯỢC PHÉP.** Đo trên
**238/238** TSL: `answer_keys_included = False`. SGK không in đáp án, nên câu
hỏi in được hiện đúng như sách và **không được chấm** — trừ khi có kịch bản đã
duyệt mang bộ đáp án chấp nhận được. `UNKNOWN != SAI`.

---

## 3 · QUẦN THỂ ỨNG VIÊN — ĐÃ ĐO

Mẫu số: **238** bài có Trusted Structured Lesson (6 cuốn, lớp 4–9).

| chặng | n | |
|---|---|---|
| có `SemanticData` dựng được tất định | **73** | 30,7% |
| ├ trong đó có câu hỏi in | **73** | 100% |
| ├ **và** mở được trong pack canonical | **62** | |
| ├ **và** qua cổng READ_SAFE | **44** | 71,0% của 62 |
| └ **và** qua cổng ③ ĐÃ SỬA (≥1 phần tử đọc được) | **37** | 84,1% của 44 |

**37 bài** qua đủ bốn điều, trải lớp **4 · 5 · 6 · 7 · 8 · 9**:

| lớp | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|
| bài | 5 | 5 | **11** | 2 | 5 | 9 |

Môn: **100% Khoa học / KHTN** — không phải phủ K-12.

### ⚠ GIỮ LẠI LỊCH SỬ — 44 KHÔNG BỊ XOÁ

**44** là kết quả dưới cổng ③ **đã bị bác bỏ**. Nó có thật, đã được báo cáo, và
ở lại đây có dán nhãn. Bảy bài chênh lệch là bảy bài cho trẻ một tab ✨ Trực
quan RỖNG — phát hiện từ ĐƯỜNG HỌC THẬT, không phải từ suy luận.

⚠ **MẪU SỐ NÀY KHÔNG PHẢI 2.778.** TSL chỉ tồn tại cho lát cắt khoa học 6
cuốn. Trên toàn corpus, `VISUAL_GROUNDED` hiện **không đo được** vì luật dựng
semantic cần vai trò khối của tầng TSL, thứ pack canonical không mang. Đó là
giới hạn thật, không phải con số cần nống lên.

---

## 4 · LÁT CẮT ĐẦU TIÊN — Founder ĐÃ DUYỆT

Seed `20260910`, một bài mỗi lớp. Founder chốt: **không thay bằng ví dụ đẹp hơn.**

Kiểm MÁY THẬT cho công thức và mã nhiều dòng: **ĐÃ XONG**
(xem [WAL-239-DEVICE-CHECK.md](WAL-239-DEVICE-CHECK.md)).

### RÚT LẠI SAU KHI SỬA CỔNG ③

Quần thể đổi **44 → 37**, nên mẫu tất định phải rút **LẠI TỪ ĐẦU**, cả sáu lớp.
Không giữ năm bài cũ rồi chỉ rút lại lớp 6.

CÙNG thuật toán · CÙNG seed `20260910` · một bài mỗi lớp, rổ **37**:

| lớp | sách | bài | khối | câu hỏi in | giữ lại | process | bước đọc được |
|---|---|---|---|---|---|---|---|
| 4 | `04-sgk-khoa-hoc-4` | 4 | 69 | 10 | 7 | ×1 | ✅ |
| 5 | `05-sgk-khoa-hoc-5` | 4 | 63 | 8 | 6 | ×1 | ✅ |
| **6** | `06-sgk-khoa-hoc-tu-nhien-6` | **9** | 56 | 6 | 3 | ×1 | ✅ |
| 7 | `07-sgk-khoa-hoc-tu-nhien-7` | 4 | 122 | 18 | 24 | ×2 | ✅ |
| 8 | `08-sgk-khoa-hoc-tu-nhien-8` | 19 | 68 | 5 | 8 | ×1 | ✅ |
| 9 | `09-sgk-khoa-hoc-tu-nhien-9` | 14 | 96 | 9 | 20 | ×4 | ✅ |

Thuật toán cho ra **đúng năm bài cũ**; chỉ ô lớp 6 đổi **Bài 8 → Bài 9**, vì
Bài 8 đã bị chính cổng ③ đã sửa loại ra. Không thay tay, không chọn bài đẹp.

⚠ `09-sgk-khoa-hoc-tu-nhien-9` b14 ghi **process ×4** chứ không phải ×9 như
bảng cũ: bản cũ đếm cả process TRÙNG LẶP, lỗi ấy đã sửa.

### Thi công — dùng nguyên đường đã có, không dựng tầng mới

1. `tool/fixtures/make_lesson_fixture.py` (vỏ mỏng của cầu chính thức
   `tsl_to_lesson_document.py`) sinh sáu `LessonDocument`.
2. Thêm sáu `FixtureSlot` vào `WorkspaceCatalog.defaultSlots` (nay có 5).
3. Ba lối học và `nextActionFor` **đã chạy sẵn** — không sửa gì.
4. Nghiệm thu là **soi mắt so với bản in** trên từng bài, rồi kiểm máy thật.

Không chuyển đổi hàng loạt. Không hạ cổng để tăng số.

---

## 5 · ĐO ĐƯỢC GÌ SAU LÁT CẮT NÀY

`LEARNABLE` = số bài qua cả bốn điều **và** có `LessonDocument` trong sản phẩm.
Hôm nay **0**. Sau lát cắt: mục tiêu **6**, trần hiện thấy được **44**.

Con số ấy chỉ có nghĩa nếu đi kèm mẫu số: **44 / 238 TSL**, không phải
44 / 2.778.
