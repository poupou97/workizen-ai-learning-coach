# Bộ chọn hình — biên bản promote canonical (2026-09-09)

Pack là artefact dựng, không nằm trong git. Biên bản này là bản ghi duy nhất
của lần đổi trạng thái ấy.

## Chính sách

`TRUSTED DOCLING ƯU TIÊN → D DỰ PHÒNG → GIỮ LẠI`, và chỉ khi **chứng minh
được cùng một hình nguồn**: cùng trang · **cùng một dòng chú thích IN** · có
chồng nhau. Hình học chỉ làm bằng chứng phụ, không có quyền phán quyết.

## Ba chốt an toàn (đều hỏng về phía GIỮ D)

| chốt | bắt gì | chặn |
|---|---|---|
| `naming_conflict` | nhiều vùng đòi một tên mà không có nhãn con in phân biệt | **0** |
| `partial_claim` + `covers` | mảnh của hình nhiều ô mượn tên cả hình | **62** |
| `containment.swallowed` | khung nuốt một vật thể mang TÊN KHÁC | **25** |

## Toàn corpus (ứng cử DUY NHẤT 3.540)

| | |
|---|---|
| DOCLING_SUPERSEDES_D | **3.453** |
| PART_OF_NAMED_FIGURE | 62 |
| CONTAINS_SEPARATE_CAPTION | 19 |
| CONTAINS_OTHER_NAMED_VISUAL | 6 |
| CONTAINS_OTHER_TRUSTED_REGION | 0 |
| AMBIGUOUS_CONTAINMENT | 0 |
| SUBFIGURE_NAME_CLASH | 0 |

## Trước / sau

| | trước | sau |
|---|---|---|
| OPENABLE_RECORDS | 2.974 | **2.974** |
| DISTINCT_OPENABLE | 2.778 | **2.778** |
| hình phân biệt | 18.297 | 17.365 (−932) |
| hình D | 12.075 | 8.557 |
| hình Docling | 4.184 | 6.787 |
| **cặp ảnh trùng cùng-nguồn** | 937 / 856 trang | **134 / 130 trang** (−86%) |

Băm kho ảnh khớp manifest cả 12 lớp.

## Mẫu đối chiếu bốn bên (seed 20260912, n=60, 37 sách, đóng băng trước khi soi)

Ca thay chỗ (n=42): **DOCLING_BETTER 27 (64,3%) · EQUIVALENT 15 (35,7%) ·
D_BETTER 0 · BOTH_BAD 0 · IDENTITY_WRONG 0 · AMBIGUOUS 0.**

Ca bị chặn (n=18): chặn đúng 10 · chặn oan 5 · vô hại 1 · không phân giải 2.

## NỢ ĐÃ ĐO — đọc kỹ trước khi động vào

1. **5 ca chặn oan đều cùng một hình dạng**: chính **D** mới là bên cắt tràn
   sang hình bên cạnh, còn Docling cắt đúng phạm vi tên gọi; hai chốt đọc
   ngược thành «Docling là một mảnh» / «Docling nuốt vật khác». Lỗi BẢO THỦ:
   chặn = giữ hiện trạng, không sinh hại mới.
2. **`CONTAINS_SEPARATE_SEMANTIC_BLOCK` không có nguồn bằng chứng dùng được.**
   Đã thử và BÁC BỎ hai tín hiệu: «nuốt khối văn xuôi» (ở mọi ngưỡng đều lẫn
   chú giải bản đồ, nhãn hình, ô bảng — chặn theo nó là chặn đúng ca Docling
   đang cứu) và «chứa đề xuất bố cục khác» (100–124% diện tích khung ⇒ cùng
   một vùng). Ca «Hình 5.4» Chuyên đề Hoá 12 tr.25 vì vậy KHÔNG bắt được.
3. **134 cặp ảnh trùng còn lại** trên 130 trang.

## Hai con số tôi đã báo SAI, và vì sao

- `CONTAINS_OTHER_NAMED_VISUAL` **822 → 6**: lỗi thật trong mã — chốt so khung
  với hình D của MỌI trang trong bài, mà hộp là toạ độ chuẩn hoá THEO TRANG.
- `SUBFIGURE_NAME_CLASH` **450 → 0**: lỗi đếm — nhật ký ghi một dòng mỗi LƯỢT
  XỬ LÝ, attach làm một trang đi qua nhiều bài, nên một vùng duy nhất hiện ra
  thành sáu dòng. Ví dụ «Hình 8 thành sáu ảnh cùng tên» KHÔNG có thật.

⭐ **NHẬT KÝ THEO LƯỢT XỬ LÝ KHÔNG PHẢI MẪU SỐ ĐỂ ĐẾM VẬT THỂ.**

## Khôi phục

Bản canonical trước promote: `/private/tmp/wal-canon-pre-selector`
(12 index + 12 kho ảnh + manifest). ⚠ `/private/tmp` bị xoá khi khởi động lại
máy — xem [[learning-coach-build-input-durability]].

---

# Đo lại chất lượng SAU promote (mẫu tươi, đóng băng trước khi soi)

## FIGURE_CROP_VALID — mức HÌNH (n=120, seed 20260913, khung 15.344)

| | toàn bộ | chỉ hình học tập thật |
|---|---|---|
| **VALID** | 90/120 = **75,0%** | 90/105 = **85,7%** |
| D (n=71) | 66,2% | 82,5% |
| Docling (n=49) | **87,8%** | **89,6%** |

Họ hỏng còn lại, xếp theo độ lớn:

| họ | số | tỉ lệ | nguồn |
|---|---|---|---|
| `NOT_A_LEARNING_VISUAL` | 15 | 12,5% | **14/15 từ D** |
| `PROSE_CONTAMINATED` | 9 | 7,5% | 5 D · 4 Docling |
| `TRUNCATED` | 4 | 3,3% | **4/4 từ D**, Docling 0 |
| `NEIGHBOR_VISUAL_INCLUDED` | 1 | 0,8% | Docling |
| `AMBIGUOUS` | 1 | 0,8% | D |

⭐ **Họ hỏng số 1 nay là ĐỒ TRANG TRÍ, không phải cắt hỏng** — và 14/15 đến từ
đường D. Đây là thay đổi thứ hạng so với vòng trước.

## Mức BÀI (n=40, seed 20260913, khung 2.974) — mẫu số RIÊNG

- `NO_REQUIRED_VISUAL` **20/40** — trạng thái HỢP LỆ, không gộp vào mẫu số.
- Trong 20 bài có «Hình N» in trong thân bài: **đủ 6 (30,0%)** · thiếu một
  phần 14 (70,0%) · không có ảnh nào **0**.
- Mức hình: **119/144 = 82,6%** hình mà sách nhắc tên đã có mặt.

⚠ Đây là **CÓ MẶT ĐÚNG TÊN**, KHÔNG phải `MULTIMODAL_FAITHFUL_VALIDATED`.
Đúng tên không chứng minh đúng ảnh. `UNKNOWN != VALID`.

## Lỗ hổng phạm vi đã phát hiện (KHÔNG sửa trong vòng này)

Chốt nuốt chỉ chạy trên **ứng cử thay chỗ**, không chạy trên vùng
`DOCLING_NEW`. Ca #053 (Toán 7, một khung chứa cả «Hình 4.6» lẫn «Hình 4.7»)
là vùng THÊM MỚI nên không đi qua chốt. Cùng một họ, khác đường mã.

Founder Gate: «If another material repeated structural failure appears after
this round: STOP. Report it.» → báo cáo, KHÔNG dựng chốt thứ tư.
