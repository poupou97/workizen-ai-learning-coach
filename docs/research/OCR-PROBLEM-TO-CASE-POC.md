# POC — chuỗi OCR → biểu diễn bài toán → ca → applicability (bounded)

**Ngày:** 2026-09-01 · **Status:** MEASURED trên BẢN QUÉT (chưa có ảnh điện thoại)
**Công cụ:** `tool/poc/problem_to_case_poc.py` · kết quả: `poc-out/case_mapping_poc.json`
**Chuỗi đo:** OCR (Apple Vision, có sẵn) → dựng phân số (hình học, tất định) → ghép biểu
thức (`phân số ± phân số`) → phân ca (bản sao 1:1 của `analyzeFractionPair`) → applicability.

## Thiết kế falsification — không cần nhãn tay

| Nhóm | Vai trò | Kỳ vọng |
|---|---|---|
| Mục lục Toán 5 + Toán 4 (9 trang) | **ĐỐI CHỨNG ÂM** | 0 biểu thức |
| Toán 4 Bài 57 tr.62→ (5 trang) | dương đã biết | ca **chia hết** |
| Toán 5 quanh Bài 6 tr.20 (4 trang) | dương đã biết | ca **không chia hết** |
| Toán 5 chương phân số p020–p049 | nền rộng | hỗn hợp |

## Kết quả đo

| Nhóm | fractions dựng được | biểu thức | phân bố ca |
|---|---|---|---|
| ĐỐI CHỨNG ÂM (mục lục) | **76 (giả!)** | **0** ✅ | — |
| Bài 57 (chia hết) | 43 | 1 | `divisible` ×1 ✅ |
| Bài 6 (không chia hết) | 37 | 3 | `non-divisible` ×3 ✅ |
| Nền rộng Toán 5 | 116 | 4 | `non-div` ×3 · `div` ×1 |

Biểu thức dựng được (đọc tay đối chiếu): `1/3 − 11/24` · `1/2 − 1/5` · `3/11 + 1/4` ·
`3/11 − 1/4` · `7/9 − 2/3` — đều là dạng bài thật của sách, ca phân đúng cả 5.

## Ba phát hiện

**① TẦNG PHÂN SỐ MỘT MÌNH BỊA CẤU TRÚC — tầng BIỂU THỨC là tường lửa thật.**
Trên MỤC LỤC, bộ dựng phân số "tìm ra" 76 phân số — đó là các **số trang xếp cột** thẳng
hàng dọc. Bộ ghép biểu thức (đòi dấu `+`/`−` nằm giữa, đúng dải dọc) đưa tất cả về 0.
⇒ Hệ quả kiến trúc: **không được gate applicability trên "phát hiện phân số"** — chỉ
được gate trên **biểu thức ghép được trọn vẹn**. Phát hiện phân số đơn lẻ = `caseUnknown`.

**② Precision cao, recall thấp — và sai theo HƯỚNG AN TOÀN.**
5/5 biểu thức ghép được đều phân ca đúng (đối chiếu cấu trúc bài học đã biết: Bài 57 ra
đúng `divisible`, Bài 6 ra đúng `non-divisible`, **0 nhiễm chéo**). Nhưng trần recall đo
bằng số token `+`/`−` trên trang: Bài 6 ghép được 3/8 (~38%), Bài 57 1/2. Chuỗi **fail
closed đúng doctrine**: cái không ghép được thì im lặng (→ Tutor nhận tập rỗng), không
phát bừa ca sai.

**③ Kênh viết ngang (`3/5 + 1/5` trong một dòng text) = 0 hit trên corpus quét** —
sách in phân số **xếp chồng** toàn bộ. Kênh regex ngang giữ lại cho ảnh chụp bài viết
tay/vở học sinh về sau.

## caseUnknown frequency (chỉ số Founder yêu cầu)

Trên biểu thức đã ghép: **0/5** (mẫu nhỏ!). Nhưng chỉ số trung thực hơn là **tỷ lệ
KHÔNG-GHÉP-ĐƯỢC ≈ 62%** trên trang bài học — mỗi ca đó chảy xuống hệ thống là một
`caseUnknown` (fail closed, Tutor im lặng). Nút thắt là **ghép biểu thức**, không phải
phân ca.

## Chưa đo — nói thẳng

- **Ảnh chụp điện thoại**: chưa có ảnh nào. Đây vẫn là ô đỏ P0 của E6.
- Recall so với nhãn tay từng bài (mới có trần ước lượng từ op-token).
- Chữ viết tay, biểu thức >2 phân số, hỗn số.
