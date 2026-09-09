# WAL-239 — `FormulaSourceBlock` đã vào canonical (2026-09-09)

Pack là artefact dựng, không nằm trong git. Đây là bản ghi duy nhất.

## Chính sách (Founder Gate duyệt: B mặc định, D dự phòng, CẤM C)

Vùng công thức của tầng bố cục → **khối `FormulaSourceBlock` có kiểu riêng**,
hiện **ảnh cắt từ chính trang in**, và **bỏ chuỗi OCR mà vùng ấy sở hữu**.
Không dựng được an toàn ⇒ **giữ lại** chuỗi OCR (D). Không bao giờ đặt bản in
đúng cạnh chữ OCR sai (C).

`FIGURE != TABLE != FORMULA != TEXT` — khối mang xuất xứ đầy đủ: sách · trang ·
**vùng ĐÃ CẮT** · neo thứ tự đọc · trạng thái tin cậy · số hiệu in khi có.

## Vì sao phải làm (đo trước, n=53, đóng băng)

**88,7% chuỗi OCR ở vùng công thức là HẠI**, Toán 23/23. Nặng nhất không phải
chữ vỡ — chữ vỡ thì trẻ biết là hỏng — mà là **mệnh đề sai đọc trôi chảy**:

| bản in | trẻ đọc |
|---|---|
| x²/9 + y²/5 = 1 | **5 = 1.** |
| AD/AB = AE/AC = 1/2 | **AE = AC** |
| 1/R = 1/R₁ + 1/R₂ | **1 = 1, + 1,** |
| 1,6·10⁻¹⁹ | 1,6.10**-17** |
| Li⁺ | **Lit** |

## Census toàn corpus

| | |
|---|---|
| `FORMULA_TOTAL` | 4.885 vùng |
| `FORMULA_SOURCE_REGION_AVAILABLE` | **2.815 (57,6%)** |
| `FORMULA_WITHHELD_AVOID_C` | 2.070 (42,4%) |
| `FORMULA_WITHHELD_UNSAFE_REGION` | 0 |
| bỏ vì **cắt không trọn** | 148 |
| `FORMULA_BLOCK_IN_READ` | **2.699 lượt** |
| `UNSAFE_OCR_SUPPRESSED` | 6.325 **đoạn** (đơn vị khác — không chia cho số vùng) |
| `SURROUNDING_PROSE_PRESERVED` | **mất đúng 1 khối** do công thức (đối chứng canonical: 597 vs 598; khối ấy là «sin a», bản thân là mảnh công thức) |
| `ORDER_PRESERVED` | **2.699/2.699 = 100%** |

## Mẫu đối chiếu bốn bên (seed 20260920, n=82, 38 sách, đóng băng trước khi soi)

| | n | |
|---|---|---|
| `SOURCE_FAITHFUL` | **76** | **92,7%** |
| `TRUNCATED` | 2 | 2,4% |
| `PROSE_CONTAMINATED` | 2 | 2,4% |
| `AMBIGUOUS` | 2 | 2,4% |
| `SYMBOL_MISSING` · `WRONG_REGION` · `ORDER_WRONG` | 0 | — |

Bốn ca còn lỗi: «⟶ Mⁿ⁺ + ne» mất vế trái · đáp án mất chữ «B.» · một khối kéo
theo mảnh chữ «cực khác được» · một khối nuốt tiêu đề mục «2. Giai đoạn phân
giải». Hai ca `AMBIGUOUS` là mảnh khuông nhạc — nhãn `formula` bắt nhầm, nhưng
hiện thành ảnh vẫn đúng.

## Bất biến sau promote
`OPENABLE_RECORDS` **2.974** · `DISTINCT_OPENABLE` **2.778** · Δ hình 0 · Δ bài 0
· băm kho ảnh khớp manifest cả 12 lớp.

## Cắt vừa vặn — vì sao không dùng đệm cố định

Soi mắt ba mức trên ca thật: đệm 0 làm «mv₁²/2» còn mỗi «/2» · 0,004 cứu được
«13/2» nhưng vẫn cụt «mv₁²/2» · 0,008 cứu cả hai nhưng ca khác đã kéo nửa dòng
văn xuôi vào · 0,012 (của HÌNH) ca nào cũng dính chữ hàng xóm. Nên hỏi **chính
trang in**: mực chạm mép nào thì nới đúng mép ấy; hết hạn mức mà vẫn chạm thì
đóng chặt, bỏ khối (148 ca).

## Nợ đã đo, KHÔNG làm trong vòng này
1. **2.070 vùng tránh-C** — chữ OCR vẫn phơi ra, không bỏ được vì không chứng
   minh được sở hữu. Tỉ lệ hại trong phần ấy **chưa soi**, không suy từ 88,7%.
2. **148 vùng cắt không trọn.**
3. **`code` 875 vùng chưa audit** — 53,5% ở Hoá học là lý do NGHI NGỜ CÁCH PHÂN
   LOẠI, không phải bằng chứng chúng là mã nguồn.
4. **TTS**: khối công thức hiện **câm**. Founder đã nhận nợ; KHÔNG được phơi lại
   OCR không an toàn để có giọng đọc.

## Khôi phục
`/private/tmp/wal-canon-pre-formula` (537 MB). ⚠ `/private/tmp` mất khi khởi
động lại máy.

## `STEM_SAFE` vẫn UNKNOWN
Không được đặt xanh chỉ vì `FormulaSourceBlock` đã ship. `LEARNABLE` = 0 ·
SAM mass scale = **BLOCKED**.
