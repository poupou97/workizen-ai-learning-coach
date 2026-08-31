# POC tri thức — Toán 5 (Kết nối tri thức), chương 1–3

**Ngày:** 2026-08-31 · Status: `TECHNICAL_POC_ALLOWED_BY_FOUNDER`
**LLM calls: 0.** Toàn bộ kết quả dưới đây bằng OCR local + luật hình học.

---

## ⭐ Kết quả quan trọng nhất — sách dạy KHÁC generic model

`Bài 6. Cộng, trừ hai phân số khác mẫu số` (trang in 20), nguyên văn OCR:

> *"Quy đồng mẫu số: Hai mẫu số 5 và 2 không chia hết cho nhau. **Lấy mẫu số chung là
> tích của hai mẫu số (5 × 2 = 10)**."*
>
> *"Muốn cộng (hoặc trừ) hai phân số khác mẫu số, ta quy đồng mẫu số rồi cộng (hoặc trừ)
> hai phân số đã quy đồng mẫu số."*

**Đo trên 53 trang đã OCR:**

| Chuỗi | Số trang xuất hiện |
|---|---|
| `BCNN` · `bội chung` · `ước chung` · `ƯCLN` | **0** |
| `tích của hai mẫu số` | 1 (Bài 6, trang 20) |

⇒ **SGK Toán 5 KNTT dạy lấy TÍCH hai mẫu số. Không dạy BCNN.**

### Vì sao đây đúng là ca §4 mà work order mô tả

Hỏi `3/4 + 2/5`, một model tổng quát gần như chắc chắn sẽ dùng **BCNN** — nhanh hơn,
"đúng hơn" về toán học. Đó chính là *"Method D"* trong work order.

Nhưng học sinh lớp 5 học bộ KNTT **chưa được dạy BCNN**. Nếu AI nói *"tìm BCNN của 4 và
5"*, đứa trẻ gặp một khái niệm chưa từng học; và Parent Coach bảo phụ huynh *"hỏi con về
BCNN"* là **dạy sai chương trình** — đúng thứ phá vỡ niềm tin khiến phụ huynh chọn ta.

> ⚠️ **Điều này bác một chi tiết trong ví dụ của Founder.** Work order §B viết: *"AI phát
> hiện root cause có thể nằm ở BCNN"*. Với bộ sách này, ở lớp 5, root cause **không thể**
> nằm ở BCNN — vì sách chưa dạy. Nguyên tắc §4 của Founder là đúng; ví dụ minh hoạ thì
> lệch. Và chính POC này là thứ phát hiện ra, bằng đo chứ không bằng phỏng đoán.

⇒ **Yêu cầu kiến trúc:** `Method` là entity hạng nhất, gắn với `Lesson`, và Tutor phải bị
**ràng buộc** bởi method của learning path hiện tại. Không phải gợi ý trong prompt — phải
là ràng buộc kiểm được.

---

## Cấu trúc trích được — TẤT ĐỊNH, 1 trang OCR

`tool/extract/parse_toc.py` đọc trang MỤC LỤC (PDF 5) bằng luật cột
(chủ đề x≈0.17 · nội dung x≈0.23 · trang x≈0.86) → **3 chủ đề, 18 bài**, đủ tiêu đề và
khoảng trang. **0.4 giây, 0 token.**

| Chủ đề | Bài | Trang |
|---|---|---|
| 1. ÔN TẬP VÀ BỔ SUNG | Bài 1–9 | 6–31 |
| 2. SỐ THẬP PHÂN | Bài 10–14 | 32–52 |
| 3. MỘT SỐ ĐƠN VỊ ĐO DIỆN TÍCH | Bài 15–18 | 53–62 |

⭐ **Chuỗi tiên quyết là SOURCE FACT, không phải suy luận LLM.** Sách tự xếp
`Bài 3. Ôn tập phân số` → `Bài 5. Ôn tập các phép tính với phân số` →
`Bài 6. Cộng, trừ hai phân số khác mẫu số`. Thứ tự do NXB quyết định, có số trang,
`citableAsTextbookFact = true`.

Đối chiếu: trích tiêu đề bằng hình học từ **trang bài** cho kết quả *kém hơn* mục lục —
"CỘNG, TRỪ HẠI PHẬN SỐ" (sai dấu), "DƯỚI DẠNG SỐ THẬP PHÂN" (cụt). **Mục lục là nguồn
chuẩn**, trang bài chỉ để xác nhận.

---

## Chất lượng OCR — đo, không ước

Dụng cụ: **Apple Vision** `accurate` + `vi-VT`, render 100ppi × 3. Chọn Vision vì đây
**chính là engine sẽ chạy trên iOS** trong sản phẩm ⇒ số đo chuyển thẳng sang production.

| Loại nội dung | Chất lượng | Bằng chứng |
|---|---|---|
| Văn xuôi tiếng Việt | ≈ **100%** | *"Viết rồi đọc phân số chỉ phần đã tô màu của mỗi hình dưới đây."* — đúng từng dấu |
| Mục lục | ≈ **100%** | 18/18 bài, đúng số trang |
| **Câu mô tả phương pháp** | ✅ **nguyên vẹn** | trích dẫn Bài 6 ở trên |
| Tiêu đề trang trí | ~85% | "luyện tập"→"luyện Cập", "Hình C"→"Hình &" |
| **Công thức toán** | ⛔ **53%** | xem dưới |

### Công thức toán — giới hạn thật, đã đo

`24/40 = 12/? = ?/5` ra thành các mảnh rời "24" "12" "40" "5" "=" "?". Dựng lại bằng
**hình học** (hai token chồng dọc, trùng dải x): **8/15 phân số** trên trang mẫu.

Bảy ca sót chia hai loại: một số do ngưỡng, nhưng `3/5`, `7/9`, `56/42` là **OCR không
hề tạo ra token** — hình học không cứu được thứ chưa từng đọc.

⚠️ **Tăng độ phân giải KHÔNG cứu được.** Render 6× thay vì 3×: **47 dòng y hệt, vẫn
8/15**. Nguồn chỉ 100 ppi nên phóng to không thêm thông tin. *Độ phân giải không phải
cần gạt* — đây là kết quả âm tính sạch, đừng thử lại.

### Hệ quả kiến trúc — và vì sao nó KHÔNG chặn sản phẩm

Knowledge base **không cần đọc từng phân số**. Thứ nó cần là: cấu trúc chương/bài, tên
concept, **câu mô tả phương pháp**, giải thích văn xuôi, thứ tự học. Tất cả những thứ đó
OCR ở mức ≈100%.

Còn *bài tập cụ thể* là thứ **Camera Tutor đọc từ ảnh học sinh chụp** — ảnh điện thoại
hiện đại sắc nét hơn hẳn bản quét 100 ppi, nên đó là bài toán khác và nhiều khả năng dễ
hơn. **Cần đo riêng, chưa đo.**

---

## Chi phí — đo thật

| | |
|---|---|
| OCR | **0,37 giây/trang**, chạy local, **0 đ** |
| 53 trang đã xử lý | ~20 giây |
| LLM calls | **0** |
| Embedding | **0** (chưa cần: cấu trúc lấy bằng luật, không bằng vector) |

Suy ra thô: một cuốn 142 trang ≈ **53 giây** OCR. Toán 5+9 (4 cuốn SGK) ≈ 3,5 phút.
Cả 12 lớp × 37 cuốn × ~150 trang ≈ **66.000 trang ≈ 6,8 giờ** OCR local, **0 đ**.

⭐ Nhưng nếu chỉ cần **mục lục + bảng thuật ngữ**: ~3 trang/cuốn × 444 cuốn = **1.332
trang ≈ 8 phút**. Đó là hai bậc độ lớn, và đủ để dựng khung Curriculum Graph toàn quốc.

---

## Phân loại xuất xứ (§6) — áp dụng cho POC này

| Đối tượng | Origin | Trích dẫn được? |
|---|---|---|
| Chủ đề, bài, số trang (từ mục lục) | `sourceDerived` | ✅ có trang |
| Câu mô tả phương pháp Bài 6 | `sourceDerived` | ✅ trang 20 |
| Thứ tự Bài 3→5→6 | `sourceDerived` | ✅ do NXB xếp |
| *"Bài 6 cần Bài 5 làm tiên quyết"* | `llmInferred` | ❌ sách xếp thứ tự, **không nói** "cần" |
| Khái niệm từ bảng thuật ngữ | `sourceDerived` | ✅ có trang |

⚠️ Khác biệt ở dòng thứ tư là tinh tế và quan trọng: **thứ tự** là sự thật trong sách;
**quan hệ tiên quyết** là diễn giải của ta. Trộn hai thứ là đúng cái §6 cấm.

---

## Chưa làm

Toán 9 (đã giải nén, chưa OCR) · retrieval POC · Camera Tutor POC · embedding ·
bảng thuật ngữ Toán 9 · tập hai của cả hai lớp.

---

# ⭐⭐ Chuỗi xuyên lớp — đo được, không giả định

*(Trích tối thiểu Toán 4 theo uỷ quyền §POC CONSEQUENCE. Chỉ 2 cuốn SGK, chỉ mục lục +
bài 57. KHÔNG ingest lớp 4 diện rộng.)*

## Chuỗi thật

| Lớp | Bài | Trang | Vai trò |
|---|---|---|---|
| **4** | Bài 57. Quy đồng mẫu số các phân số | 62 | **DẠY** |
| 5 | Bài 3. Ôn tập phân số | 11–13 | ÔN |
| 5 | Bài 6. Cộng, trừ hai phân số khác mẫu số | 20–22 | DÙNG |

Toán 4 tập hai, chủ đề PHÂN SỐ: Bài 53 Khái niệm phân số (tr.49) → Bài 55 Tính chất cơ
bản (tr.56) → Bài 56 Rút gọn (tr.59) → **Bài 57 Quy đồng (tr.62)** → Bài 58 So sánh (tr.64).

## ⭐ Và hai lớp dạy HAI PHƯƠNG PHÁP KHÁC NHAU

**Lớp 4, Bài 57** (tr.62), nguyên văn:
> *"Ta thấy: Mẫu số của phân số 3/8 **chia hết** cho mẫu số của phân số 1/4 (8 : 4 = 2)…
> 12 : 4 = 3, mẫu số chung là 12… **giữ nguyên** phân số 5/12."*

**Lớp 5, Bài 6** (tr.20), nguyên văn:
> *"Hai mẫu số 5 và 2 **không chia hết cho nhau**. Lấy mẫu số chung là **tích** của hai
> mẫu số (5 × 2 = 10)."*

| | Điều kiện | Mẫu số chung |
|---|---|---|
| Lớp 4 | mẫu này **chia hết** cho mẫu kia | lấy mẫu **lớn hơn**, giữ nguyên một phân số |
| Lớp 5 | **không chia hết** | lấy **tích** hai mẫu |

Một khái niệm, **hai ca bổ sung nhau, chia đôi qua hai lớp**. Và lớp 5 mở đầu bằng đúng
cụm *"không chia hết cho nhau"* — **sách tự tham chiếu ca của lớp 4**. Đây là bằng chứng
tiên quyết mạnh gần mức source-stated, tuy vẫn chưa phải câu *"cần học Bài 57 trước"*.

## Hệ quả sản phẩm — lớn hơn dự kiến

⭐ Một học sinh lớp 5 sai `3/4 + 2/5` **có thể không hề hổng quy đồng**. Em ấy có thể nắm
chắc ca lớp 4 (chia hết) và bối rối vì **luật đổi**. Đó là **misconception**, không phải
knowledge gap — và can thiệp hoàn toàn khác:

| Chẩn đoán | Can thiệp đúng |
|---|---|
| chưa biết quy đồng | dạy lại từ lớp 4 Bài 57 |
| **biết ca chia hết, chưa biết ca không chia hết** | dạy **phân biệt hai ca**, không dạy lại |

Đây đúng ca §4 của addendum: *hai học sinh cùng trả lời sai cần can thiệp khác nhau*.
Và nó chỉ lộ ra khi đọc **cả hai lớp** — đọc riêng lớp 5 sẽ kết luận sai.

⇒ `Method` phải gắn **điều kiện áp dụng**, không chỉ gắn lớp.
