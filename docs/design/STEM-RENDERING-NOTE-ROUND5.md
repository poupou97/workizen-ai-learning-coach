# Track B · Round 5 — Kết xuất STEM trên di động: GHI CHÚ NGHIÊN CỨU (đã gác lại)

**Trạng thái:** ghi chú + khuyến nghị, **không phải bản dựng**. Ưu tiên vòng này là màn
Lesson Workspace và vòng lặp máy thật; mục này được gác theo đúng chỉ đạo. Chưa thêm phụ
thuộc nào vào `pubspec.yaml`.

Chỉ đạo Founder (§9): Text → chữ gốc · Math → renderer đọc được LaTeX · Physics → renderer
math + đơn vị có nghĩa · Chemistry → renderer hoá học có cấu trúc · **không hỗ trợ / chưa
kiểm định ⇒ WITHHELD / rơi về nguồn**. **Không dùng Markdown/HTML/chữ phẳng làm sự thật
STEM chuẩn.**

## 1. NHU CẦU THẬT — đo từ chính dữ liệu của mình, không từ giả định

- **41 biểu thức** trong các pack đang ship (`assets/pack/lesson-index-g*.json`,
  `toanExercises`). **41/41 (100 %)** có dạng `a/b ± c/d` — phân số cộng/trừ. Không có luỹ
  thừa, không có căn, không có đơn vị, không có chữ.
  Mẫu: `23/13 + 8/13`, `5/12 + 1/4`, `1/6 - 5/8`, `4/5 - 2/3`.
- **0 dấu hiệu STEM** trong hai fixture bài học thật đang chạy (KHTN 6 Bài 17, LS&ĐL 5 Bài 8):
  quét luỹ thừa/chỉ số Unicode, `a/b`, đơn vị đo, mũi tên phản ứng, công thức hoá học → **không
  khối văn bản nào khớp**. Hai bài đang trưng bày là bài **văn xuôi**.
- Hôm nay 41 biểu thức ấy được vẽ bằng **`Text(e.expr)` phẳng** (`assessment_screen.dart:205`,
  `camera_demo_flow.dart:77`) — tức đúng thứ chỉ đạo Founder cấm dùng làm sự thật STEM chuẩn.

**Kết luận thẳng:** renderer STEM là nhu cầu của **kế hoạch phủ 3.679 bài**, không phải lỗi
đang chảy máu trên golden slice. Tập con LaTeX cần **hôm nay** rất hẹp: `\frac`, `+`, `-`.

## 2. ỨNG VIÊN — đo được gì thì ghi, không đo được thì ghi là chưa đo

| | `flutter_math_fork` 0.7.4 | `catex` 0.0.1+8 | `flutter_tex` 5.2.7 | ảnh/SVG dựng sẵn ở pipeline |
|---|---|---|---|---|
| giấy phép | **Apache-2.0** (đã đọc file LICENSE) | — | — | không phụ thuộc |
| bản chất | Dart thuần, cổng KaTeX | Dart thuần | **WebView** (`webview_flutter_plus`) | ảnh tĩnh |
| kích thước | **3,1 MB gói**, trong đó **660 KB / 20 tệp `.ttf`** phông KaTeX đóng gói | nhỏ hơn, chưa đo | kéo theo WebView + `url_launcher` + `markdown` | bằng kích thước ảnh |
| offline | **có** — phông nằm trong gói, không gọi mạng | có | WebView cục bộ, nhưng là một môi trường web trong app | có |
| cập nhật lần cuối | 2025-05-21 | **2021-03** (SDK `<3.0.0`, không dùng được) | 2026-04-14 | — |
| kết quả trên biểu thức THẬT của mình | `\frac{3}{10}+\frac{5}{21}` và `b)\ \frac{3}{10}+\frac{5}{21}` **phân tích và dàn trang đúng**, không rơi về fallback (`fellBack: false`); hình học phân số (gạch ngang, tử/mẫu) đúng | chưa chạy | chưa chạy | — |
| **chưa kiểm chứng** | **độ trung thực GLYPH**: trong `flutter_test` không nạp phông của gói nên chữ ra ô đặc — đây là hạn chế của môi trường test, **không phải kết luận về renderer**. Cần một lần xem trên máy thật. | | | |

Bake-off chạy trong dự án nháp ngoài repo (`scratchpad/mathbake`), **không** đụng
`pubspec.yaml` của sản phẩm. Hai case còn lại (`3×10⁸ m/s`, phản ứng hoá học) **treo** ở
`pumpAndSettle` và bị dừng theo giới hạn thời gian — ghi là **chưa đo**, không suy diễn.

## 3. KHUYẾN NGHỊ

**Trước mắt (0 công app, 0 phụ thuộc): dùng ẢNH CẮT TỪ TRANG SÁCH.** Lane A2 đã chỉ đúng chỗ
— `withheld_card.dart:182-201` **đã** hiển thị một vùng cắt kèm xuất xứ cho trẻ hôm nay. Đó là
đường trung thực đã có: vùng biểu thức đã kiểm định được cho xem **đúng như sách in**, không
qua bất kỳ khâu dựng lại nào. Đây cũng là đường duy nhất hiện đúng được `3×10⁸` mà không cần
renderer.

**Khi cần dựng lại thật (nhiều bài, nhiều dạng): `flutter_math_fork`**, vì Apache-2.0, Dart
thuần, offline theo cấu tạo, và đã dàn đúng biểu thức thật của mình. Điều kiện: (a) xem glyph
một lần trên máy thật; (b) chấp nhận ~660 KB phông; (c) **chỉ dùng cho biểu thức ĐÃ VALIDATE**.
`catex` loại (chết từ 2021). `flutter_tex` loại cho app trẻ em: kéo WebView vào chỉ để in một
phân số là đổi một lớp bề mặt tấn công lấy một dòng chữ.

## 4. TRẠNG THÁI «CHƯA KIỂM ĐỊNH» CHO MỘT BIỂU THỨC — thiết kế, dùng lại mẫu đã có

Không dựng cách trình bày thứ hai. Mở rộng đúng `WithheldCard` đang chạy:

```
┌────────────────────────────────────────────┐
│ [ảnh cắt vùng biểu thức, nguyên trang sách] │   ← đường A2 khuyến nghị, đã có
│ Chỗ này SAM chưa đọc chắc — con xem trong   │
│ sách nhé (SGK Toán 5 · trang 21).           │
│ Lý do: đây là công thức, máy dễ đọc nhầm    │
│ số và dấu.                                  │
│ [Vì sao SAM để trống?] [Xem ảnh chụp trang] │
└────────────────────────────────────────────┘
```

Ba trạng thái, không có trạng thái thứ tư:

| trạng thái | trẻ thấy | điều kiện |
|---|---|---|
| **TRUSTED** | biểu thức dựng lại (hoặc ảnh cắt) | đã qua validator độc lập |
| **WITHHELD có ảnh** | ảnh cắt + lời giải thích + trang | có bbox tin được, chữ thì không |
| **WITHHELD không ảnh** | chỉ lời giải thích + trang | không có cả bbox |

**Cấm tuyệt đối:** in chuỗi đã hỏng («`b) 10 +`» thay cho `b) 3/10 + 5/21` — lỗi thật còn
sống trong pack cũ). Chuỗi hỏng nguy hiểm hơn một ô trống, vì nó trông như sách.

## 5. HỢP ĐỒNG ĐỀ NGHỊ VỚI LANE A2

`MathExpression` nên mang **cả hai**, và người vẽ chọn theo cái nào có:

| trường | vì sao người vẽ cần |
|---|---|
| `latex: String?` | đường dựng lại; **tập con tối thiểu cho lớp 1–5 hôm nay**: `\frac{}{}`, `+ - × ÷ =`, số nguyên, ngoặc. Mở rộng khi có dữ liệu thật cần: `^{}`, `_{}`, `\sqrt{}`, `\mathrm{}` cho đơn vị |
| `ast` (cây có kiểu) | thứ **validator** làm việc trên đó; người vẽ không tự phân tích LaTeX để suy nghĩa |
| `sourceRegion` (bbox + trang) | **đường ảnh cắt** — thứ dùng được ngay hôm nay, và là chỗ rơi về khi không validate được |
| `disposition` | TRUSTED / VALIDATED REPAIR / REPAIRED CANDIDATE / WITHHELD — người vẽ **fail closed** theo trường này, không tự đoán |
| `unit: String?` (nếu có) | vật lí: `m/s` phải là đơn vị có nghĩa, không phải chữ dính vào số |

**Ràng buộc từ phía app mà A2 nên biết:** `LessonDocument.fromJson` hiện **hạ cả tài liệu**
khi gặp một loại khối lạ (Lane A2 đã đo: `lesson_document.dart:343`). Nên **một `FormulaBlock`
mới sẽ làm trắng cả bài trên app cũ**. Trước khi phát một loại khối mới ra pack, cần một
đường xuống cấp mềm ở lớp `core` — việc này thuộc `lib/core/**`, không phải làn B.

## 6. ĐIỀU CÒN CHƯA BIẾT (ghi thẳng)

- Độ trung thực glyph của `flutter_math_fork` **trên máy thật** — chưa xem.
- Kích thước APK tăng thêm thật sự — chưa đo (mới đo kích thước gói và phông).
- Hành vi trên biểu thức vật lí/hoá học — hai case treo, chưa đo.
- Trợ năng của biểu thức dựng lại (trình đọc màn hình đọc một phân số ra sao) — **chưa nghiên
  cứu**, và với một app cho trẻ đây có thể là tiêu chí quyết định chứ không phải phụ.
