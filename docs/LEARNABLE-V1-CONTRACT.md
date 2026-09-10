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

### ③ VISUAL_GROUNDED
Có ít nhất một `SemanticData` **có kiểu**, dựng bởi một luật CÓ TÊN với trust
`trustedStructuredLesson`:

    tsl-enumerated-steps-v1      (process)
    tsl-summary-parenthesis-v1   (comparison)

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
| └ **và** qua cổng READ_SAFE | **44** | 71,0% của 62 |

**44 bài** qua đủ bốn điều, trải lớp **4 · 5 · 6 · 7 · 8 · 9**:

| lớp | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|
| bài | 5 | 5 | 18 | 2 | 5 | 9 |

⚠ **MẪU SỐ NÀY KHÔNG PHẢI 2.778.** TSL chỉ tồn tại cho lát cắt khoa học 6
cuốn. Trên toàn corpus, `VISUAL_GROUNDED` hiện **không đo được** vì luật dựng
semantic cần vai trò khối của tầng TSL, thứ pack canonical không mang. Đó là
giới hạn thật, không phải con số cần nống lên.

---

## 4 · LÁT CẮT ĐẦU TIÊN — Founder ĐÃ DUYỆT

Seed `20260910`, một bài mỗi lớp. Founder chốt: **không thay bằng ví dụ đẹp hơn.**

⛔ **Chưa thi công.** Điều kiện tiên quyết: kiểm MÁY THẬT cho công thức và mã
nhiều dòng. Bằng chứng phải là HÀNH VI TRẺ NHÌN THẤY, không phải chỉ test.

Một bài mỗi lớp, rút từ **44** bài trên bằng seed đóng băng `20260910` — lát
cắt THẬT, không phải bài trưng bày chọn tay:

| lớp | sách | bài | khối phục vụ | câu hỏi in | giữ lại | semantic |
|---|---|---|---|---|---|---|
| 4 | `04-sgk-khoa-hoc-4` | 4 | 49 | 10 | 7 | process ×1 |
| 5 | `05-sgk-khoa-hoc-5` | 4 | 46 | 8 | 6 | process ×1 |
| 6 | `06-sgk-khoa-hoc-tu-nhien-6` | 8 | 71 | 2 | 13 | process ×4 |
| 7 | `07-sgk-khoa-hoc-tu-nhien-7` | 4 | 90 | 18 | 24 | process ×2 |
| 8 | `08-sgk-khoa-hoc-tu-nhien-8` | 19 | 51 | 5 | 8 | process ×1 |
| 9 | `09-sgk-khoa-hoc-tu-nhien-9` | 14 | 65 | 9 | 20 | process ×9 |

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
