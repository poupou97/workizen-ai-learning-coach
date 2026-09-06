# ROUND 7 · VÒNG 1 — HOME + LESSON WORKSPACE + TRỰC QUAN

**Golden Lesson:** KHTN 6 · Bài 17 «Tách chất khỏi hỗn hợp» (Founder order 49 — đã duyệt,
không xét lại). Fixture thật: 73 block · 2 `process` + 1 `comparison` · tutorScript 5 bước.

**Máy thật:** Nokia 6.1 (`192.168.1.3:5555`), `ai.workizen.learningcoach`, `adb install -r`
(giữ nguyên app data của Founder — không gỡ cài lần nào).

**Trạng thái:** READY FOR FOUNDER REVIEW. **DO NOT MERGE** (order 48 thu hồi quyền merge).

---

## 0 · BEFORE / AFTER — nhìn bằng mắt

Ảnh máy thật, KHÔNG commit (D4 — chữ SGK). Chúng nằm trên Desktop của Founder:

| Ghép đôi | Đường dẫn |
|---|---|
| **HOME** BEFORE ↔ AFTER | `~/Desktop/wal-evidence/round7-v1-device-2026-09-06/BEFORE-AFTER-home.png` |
| **TRỰC QUAN** BEFORE ↔ AFTER | `~/Desktop/wal-evidence/round7-v1-device-2026-09-06/BEFORE-AFTER-truc-quan.png` |

Khung BEFORE lấy từ `round7-r1-device-walk-2026-09-06/02-home.png` và
`round5-1-07-visual-mindmap.png` (Trực quan ở mức tốt nhất trước vòng này).

Khung rời của vòng 1, cùng thư mục:

| Khung | Nội dung |
|---|---|
| `01-home.png` | Home lượt 1 (trước khi sửa hierarchy) |
| `03b-mode-picker.png` | ⚠ lỗi hành trình lượt 1: nút «📖 Đọc ▸» mở ra màn HỎI LẠI |
| `10-AFTER-home.png` | Home lượt 2 — eyebrow một từ, chip nguồn, CTA trong màn đầu |
| `11-AFTER-cta-lands-in-doc.png` | nút Home giữ lời hứa: vào thẳng Đọc |
| `12-AFTER-truc-quan-top.png` | Trực quan — một điều hướng, sơ đồ thật |
| `05-tq-comparison.png` | sơ đồ tư duy 4 cách tách (khung concept) |
| `06-tap-chiet-explain.png` | ⭐ chạm «Chiết» → tách cái gì + **bài này dùng ở đâu** |
| `07-crosslink-jump.png` | chạm liên hệ → nhảy tới sơ đồ «Tách dầu ăn khỏi nước» |
| `08-tap-lang-no-link.png` | ⭐ chạm «Lắng» → **không có liên hệ thì nói thẳng** |
| `14-AFTER-tap-step-explain.png` | ⚠ lỗi lượt 2: lời sách in HAI lần |
| `16-AFTER-step-explain-nodup.png` | lượt 3 — in một lần, vừa một màn |

---

## 1 · HOME — «đang học gì + việc tiếp theo» chiếm màn đầu

### Cái sai, đo được

Máy thật lượt 1 (`02-home.png`): lời chào → SAM **nhắc lại** đúng tên bài nằm ngay dưới →
**5 chip chung chung** ăn một phần ba màn → nhãn HÔM NAY → thẻ bài → nút «Mở bài học»
**rơi xuống dưới nếp gấp**. Không có gì nói con đang học tới đâu.

### Cái đã làm

Đường «đang có bài dở» nay là:

```
Chào Na                         (một dòng, không lặp)
┌─ ĐANG HỌC ──────────────────┐
│ Bài 17 · Tách chất…         │  ← đang học gì
│ Chương IV · SGK KHTN 6 · tr │
│ 🧪 Bản thử nghiệm · …    ⓘ  │  ← sự thật về nguồn, chip gọn
│ ▬▬ ▬▬ ▬▬  đã mở 0/3 cách học│  ← BẰNG CHỨNG, không mastery
│ 🦉 «Con đọc bài trước nhé…» │  ← NGUYÊN VĂN lý do của động cơ
│ [    📖 Đọc ▸            ]  │  ← việc tiếp theo, TRONG màn đầu
└─────────────────────────────┘
CÓ THỂ LÀM TIẾP  [✨ Trực quan] [🦉 Học với SAM]
SAM ĐÃ THẤY GÌ   (trắng phẳng, chữ nhỏ, KHÔNG nút)
HÔM NAY → CÒN CÓ THỂ MỞ → … → CÁCH KHÁC ĐỂ HỌC (5 chip)
```

- **Dòng SAM ở đầu màn bị xoá khỏi đường này.** Nó lặp đúng tiêu đề ngay dưới nó
  (Founder: «lời chào lặp hai lần») và nó đẩy nút xuống. Lời SAM đi **vào trong thẻ**, và
  nó là NGUYÊN VĂN `lessonNext.reason` — Home không viết lại.
- **Nhãn nút đến từ `founderNextAction`** — ĐỘNG CƠ DUY NHẤT mà workspace cũng dùng. Home
  không có luật riêng, nên Home và bài không thể trỏ hai nơi khác nhau cho cùng một
  trạng thái. R2 ⇒ «📖 Đọc ▸», R4 ⇒ «🦉 Học với SAM ▸», R5 ⇒ «Xem tiếp bài này ▸».
- **«SAM thấy gì» là hỗ trợ** (order 49 §1): đứng SAU nút, nền trắng phẳng, chữ 13sp,
  **không có nút nào bên trong** — nó không tranh hành động với Next Action. Có test đo
  đúng ba điều đó.
- **5 chip chung chung xuống dưới**, dưới nhãn «CÁCH KHÁC ĐỂ HỌC». Chúng vẫn còn.
- Đường KHÔNG có bài dở giữ nguyên thứ tự cũ.

### Lỗi máy thật tìm ra trong chính vòng này, và đã sửa

| # | Lỗi | Khung | Sửa |
|---|---|---|---|
| H1 | Nút Home nói «📖 Đọc ▸» → app mở màn **hỏi lại** «con muốn học theo cách nào?» | `03b-mode-picker.png` | `onOpenWorkspaceLesson(doc, at: view)` → `LessonWorkspaceScreen.initialView`. Nút mang tên một cách học thì mở đúng cách học ấy. Chip «CÓ THỂ LÀM TIẾP» cũng vậy. |
| H2 | Eyebrow ba vế IN HOA 15sp **xuống hai dòng**, át tên bài | `01-home.png` | Eyebrow còn một từ «ĐANG HỌC»; nhãn nguồn thành `FixtureChip` gọn — **dùng lại** widget của workspace, một bộ chữ, một đường mở sheet «Nguồn & độ tin». |

---

## 2 · LESSON WORKSPACE — một điều hướng

Không đổi cấu trúc: `[📖 Đọc] [✨ Trực quan] [🦉 Học với SAM]` vẫn là điều hướng duy nhất,
và gợi ý của SAM vẫn là **một dòng** (`AssistPeek`, phương án B đã chốt vòng 6).

Thứ vòng 7 gỡ là **hai hàng điều hướng thứ hai và thứ ba nằm bên trong Trực quan** — xem §3.

Sau H1, hành trình từ Home vào bài **không còn một màn hỏi lại**: Home đã trả lời «làm gì
tiếp», nên app không được hỏi lại đúng câu đó (`11-AFTER-cta-lands-in-doc.png`). Màn «Vào
bài học» vẫn còn cho đường KHÔNG có lời hứa (R5, thẻ nghiên cứu, mở từ Giá sách).

---

## 3 · TRỰC QUAN — sơ đồ thật, chạm được

### Cái sai, đo được

`round5-1-07-visual-mindmap.png` đếm được **BA hàng điều hướng** cho một màn: tab của
workspace · hàng chip HÌNH DẠNG (tự xuống hai dòng trên Nokia) · hàng chip CÁCH NHÌN.
Cộng thêm thẻ «SAM đề xuất» to. Nội dung học đầu tiên ở **~85 % chiều cao màn**.

### Cái đã làm

- **Xoá hàng chip hình dạng + hàng chip sơ đồ.** Bài có bao nhiêu sơ đồ thì cuộn bấy
  nhiêu, **theo thứ tự tài liệu** — không phải chọn rồi mới thấy. Bài 17 ⇒ ba thẻ:
  «Lọc nước từ hỗn hợp nước lẫn đất» (3 bước), «Tách dầu ăn khỏi nước» (2 bước, 1 bước
  bị giữ lại), «Các cách tách chất» (4 cách).
- **«Cách nhìn» (sơ đồ tư duy / bảng) vào ĐẦU THẺ của chính bảng so sánh** — đó là lựa
  chọn TRONG một sơ đồ, không phải điều hướng của màn. `Wrap`, không `Row`: `Row` tràn
  5,5 dp trên màn 360 dp (test mật độ bắt được trước khi lên máy).
- **«Bảng tóm tắt» thành nếp gấp cuối màn.** Nó là bản dự phòng khi không có sơ đồ; khi
  CÓ sơ đồ nó không được đứng ngang hàng. Bài không có sơ đồ ⇒ nó tự mở.
- **«Vì sao SAM chọn sơ đồ này»** từ thẻ lavender to → **một dòng ⓘ** mở sheet. Nội dung
  không đổi một chữ; nó là lời về CÔNG CỤ, không phải nội dung học.
- Phụ đề sơ đồ bỏ vế lặp tên sách (hàng tiêu đề đã có): «3 bước · trang 61 · chữ sách,
  SAM chỉ xếp lại» — một dòng thay hai.

### ⭐ Chạm một ô thì được GIẢI THÍCH (order 49 §3)

`lib/features/lesson_workspace/views/visual_explain.dart` — **hàm THUẦN trên
`SemanticData`**, không biết `LessonDocument`, không biết bài nào.

**Chạm một BƯỚC** → «Bước 3 trong 3 bước sách viết cho «…»» · lời sách của bước · **bước
trước / bước sau** (rút gọn). Bước bị giữ lại ⇒ nói VÌ SAO trống, không bịa lời sách.

**Chạm một CÁCH TÁCH** («Lọc», «Chiết») → từng chiều so sánh NGUYÊN VĂN + **«Bài này dùng
ở đâu»**: những sơ đồ KHÁC của cùng tài liệu có nhắc đúng từ ấy, **chạm là nhảy tới**.

> «Chiết» → *Dùng để tách: tách các chất lỏng không tan vào nhau ra khỏi nhau* →
> **Bài này dùng ở đâu: «Tách dầu ăn khỏi nước» →** (`06`, `07`)
>
> «Lắng» → **«Bài này chưa có sơ đồ riêng cho cách «Lắng» — sách chỉ nhắc tên nó ở phần
> tóm tắt. SAM không dựng thêm sơ đồ.»** (`08`)

Cách khớp là **so khớp NGUYÊN TỪ** giữa hai mẩu dữ liệu có kiểu của cùng một tài liệu
(biên là ký tự không phải chữ cái, Unicode — tiếng Việt có dấu). Nó **không suy ra kiến
thức mới**: nó nói «chỗ kia trong bài có nhắc đúng từ này», kiểm lại được bằng mắt.
Không tìm được ⇒ nói thẳng, không gợi bừa.

Phần giải thích chèn **lên TRÊN** phần «Sách viết» của **cùng một sheet** — không thêm
màn, «📖 Xem trong Đọc» không đổi chỗ.

### Lỗi máy thật tìm ra trong chính vòng này, và đã sửa

| # | Lỗi | Khung | Sửa |
|---|---|---|---|
| V1 | Phụ đề sơ đồ lặp «SGK KHTN 6» (hàng tiêu đề đã có) ⇒ xuống hai dòng | `04-truc-quan-top.png` | chỉ giữ vế trang |
| V2 | Chú thích còn nói «chạm một bước để **tra cứu lời sách**» trong khi chạm nay **giải thích** | `04` | đổi lời cho đúng việc sắp xảy ra |
| V3 | Nhảy theo liên hệ cắt mất đầu thẻ đích | `07-crosslink-jump.png` | neo cuộn ôm CẢ thẻ, không phải phần trong |
| V4 | Lời sách của bước **in hai lần** («Sách viết ở bước này» rồi «Sách viết») — trên Nokia là mười dòng cho một câu | `14-AFTER-tap-step-explain.png` | `VisualExplain.withoutVerbatim()` khi lời bước TRÙNG lời block nguồn. Sau sửa, sheet vừa một màn (`16`) |

---

## 4 · GUARDRAIL — không cái nào bị nới

| Bất biến | Ở đâu trong vòng này |
|---|---|
| `OPENED != UNDERSTOOD` | Thanh tiến độ đọc «đã mở 0/3 cách học»; thẻ «SAM ĐÃ THẤY GÌ» nói thẳng «mở bài không phải là hiểu bài». Test quét CẢ MÀN Home cấm `%`, `⭐`, «đã thạo», «thành thạo», «hoàn thành bài», «điểm số». |
| `TAP != COMPETENCE` | `openedViews` là dấu vết PHIÊN (`WorkspaceTrace`), không ra đĩa, không thành sự kiện học. Home **nhận** tập ấy đã dựng sẵn — nó không tự hỏi trace. |
| `MOCK != EVIDENCE` | Không thêm đường ghi nào. Workspace vẫn không có kho. |
| `FIXTURE != TRUSTED CORPUS` | Chip «Bản thử nghiệm» nay có mặt **cả trên Home**, dùng lại `FixtureChip` + sheet «Nguồn & độ tin» của workspace. Test canh chip không mất khi màn được sắp lại. |
| `LLM OUTPUT != TRUTH` | `visual_explain.dart` không gọi gì; nó xếp lại chữ đã có. Chữ trong sơ đồ là lời sách, và màn NÓI ĐÚNG THẾ («chữ sách, SAM chỉ xếp lại» · «màu chỉ để phân biệt, không phải điểm số»). |
| `trusted = 0`, `eligible for teaching = 0` | **Không đổi.** Vòng này không chạm pipeline, không chạm cổng TC, không chạm pack. |
| D4 | Fixture thật + pack vẫn gitignore (kiểm lại bằng `git check-ignore`). Khung máy thật ra `~/Desktop/wal-evidence/`, không commit. |

**Pack:** dựng lại `assets/pack/lesson-index-g6.json` từ `origin/main` (782757f4) trước khi
build APK. `contentHash` **giống hệt** bản đang có (`846ccc69fa88…`), `pack_provenance.py
verify` báo DEFAULT build ⇒ **pack không cũ**. (Luật này có vì pack cũ từng đẩy 41 biểu
thức bịa lên máy thật.)

---

## 5 · SỐ ĐO

| Đo | Trước | Sau |
|---|---|---|
| Hàng điều hướng ở Trực quan | **3** | **1** |
| Nội dung học đầu tiên ở Trực quan (máy thật, 1920 px) | ~85 % | **40 %** (thẻ sơ đồ) · **54 %** (dòng chảy) |
| Y của thẻ sơ đồ đầu tiên (widget test, dp) | 384 (bản thẻ vòng 5) | **305** hé · **249** thu gọn |
| Nút việc-tiếp-theo trên Home | dưới nếp gấp | **trong màn đầu** (có test đo) |
| Số bước từ Home tới Đọc | 2 chạm (qua màn hỏi lại) | **1 chạm** |
| Test | 1126 xanh | **1184 xanh**, 0 đỏ |

---

## 6 · PLANNED vs ACTUAL

| # | PLANNED | ACTUAL | Trạng thái |
|---|---|---|---|
| 1 | Home: đang học gì · việc tiếp theo · SAM thấy gì, Next Action nổi bật | Thẻ ĐANG HỌC + CTA từ động cơ + hàng «có thể làm tiếp» + thẻ hỗ trợ; 9 test khoá hierarchy và cấm mastery | **DONE** |
| 2 | Giảm «card trong card» | Dòng SAM đầu màn xoá khỏi đường này; 5 chip xuống dưới; eyebrow một dòng; nhãn nguồn thành chip | **DONE** |
| 3 | Workspace: một điều hướng, gợi ý một dòng | Đã đúng từ vòng 6 và được giữ; xác nhận trên máy | **DONE** |
| 4 | Nội dung học xuất hiện sớm | 85 % → 40 % (máy thật) | **DONE** |
| 5 | Trực quan: process + comparison thật sự tương tác | Chạm bước → giải thích bước; chạm cách tách → tách cái gì + bài này dùng ở đâu + nhảy tới; không có liên hệ ⇒ nói thẳng | **DONE** |
| 6 | Renderer dùng lại, không hard-code pixel cho một bài | `visual_explain*` là hàm thuần trên `SemanticData`; test quét CẢ THƯ MỤC `views/` (thay danh sách tay của vòng 5) + cấm `import lesson_document` | **DONE** |
| 7 | Máy thật → screenshot → sửa hierarchy/layout → chụp lại | **3 lượt**: lượt 1 tìm H1+H2, lượt 2 tìm V4, lượt 3 xác nhận | **DONE** |
| 8 | Guardrail không nới | Bảng §4 | **DONE** |
| 9 | BEFORE/AFTER cạnh nhau | Hai ảnh ghép trong thư mục evidence | **DONE** |
| 10 | Vòng 2 — SAM teaching loop (phản hồi theo lỗi) | Ngoài phạm vi vòng 1 theo order 49 | **NOT STARTED** |
| 11 | Vòng 3 — Golden Journey đầy đủ + Luyện tập | Ngoài phạm vi vòng 1 | **NOT STARTED** |
| 12 | «Đọc» và «Học với SAM» redesign | Không chạm trong vòng này (order 49 xếp cho vòng 2/3) | **DEFERRED** |

### Chưa xong, nói thẳng

- **Phần ghim của workspace vẫn 281 dp** (breadcrumb + tiêu đề 2 dòng + trang + chip
  nguồn + tab + gợi ý) — ~38 % màn Nokia trước khi nội dung bắt đầu. Vòng này rút phần
  CUỘN, chưa rút phần GHIM. Muốn xuống nữa thì phải thu gọn tiêu đề khi cuộn, và đó là
  một quyết định trình bày đáng đưa Founder xem chứ không nên tự quyết. **PARTIAL.**
- **Tiêu đề bài hiển thị IN HOA** («TÁCH CHẤT KHỎI HỖN HỢP») vì quyết định vòng 7 của
  Founder là GIỮ NGUYÊN VĂN NGUỒN (`lib/core/display/lesson_title.dart`). Không đụng tới.
  Nếu Founder muốn khác, điều kiện bật đã viết thành hàm chạy được ở chính tệp đó.
- Bài 17 chỉ có `process` + `comparison`. Renderer `timeline` và `conceptMap` **được kiểm
  bằng dữ liệu có kiểu dựng trong test**, không có bằng chứng máy thật ở vòng này.

---

## 7 · Test đã thêm

| Tệp | Giữ điều gì |
|---|---|
| `test/features/mission/home_learning_now_test.dart` (11) | CTA trong màn đầu · «SAM thấy gì» không tranh hierarchy · không mastery · số vạch = số cách học bài NÀY có · nhãn nút theo động cơ · **nút giữ đúng lời hứa** (mở đúng cách học nó nêu tên) |
| `test/features/lesson_workspace/visual_explain_test.dart` (17) | Bước: số thứ tự, lời sách, hàng xóm, bước giữ lại · Cách tách: từng chiều, liên hệ, **không có liên hệ thì nói thẳng** · so khớp NGUYÊN TỪ · giải thích đứng TRÊN nguồn · **không in lời sách hai lần** · **quét CẢ THƯ MỤC `views/`** tìm danh tính bài |

Test đổi theo là **CHỦ Ý**, không phải sửa cho xanh: `VisualView.shapeKey` /
`instanceKey` không còn tồn tại vì **hàng chip không còn tồn tại**. Mỗi chỗ đổi đều có
chú thích nói vì sao.

---

## 8 · Cần Founder quyết

1. **Phần ghim 281 dp của workspace** — có thu gọn tiêu đề khi cuộn không? Đánh đổi:
   trẻ mất câu «mình đang ở bài nào» khi đang đọc giữa chừng.
2. **Màn «Vào bài học»** nay chỉ còn trên đường KHÔNG có lời hứa. Giữ hay bỏ hẳn?
3. **Tiêu đề IN HOA** trên cả Home lẫn workspace — giữ nguyên văn nguồn như đã chốt, hay
   mở lại nghiên cứu chuẩn hoá?
