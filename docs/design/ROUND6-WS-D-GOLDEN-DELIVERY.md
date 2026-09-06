# Round 6 · WS-D — GOLDEN DELIVERY + Workspace OPTION B (2026-09-06)

**Nhánh:** `ws-d/round6-golden-delivery` → base `integration/round6-2026-09-06`
· **Trạng thái:** READY FOR FOUNDER REVIEW — **chưa merge gì.**

---

## 0. Câu trả lời một đoạn

Phương án **B** đã được thi hành: bản dựng chỉ còn **một** cách trình bày gợi ý, cờ so
A/B đã gỡ, ba thứ trùng lặp đã xoá, và ba View nay có **cùng** chiều cao phần ghim
(281 dp thay vì 411 dp ở «Học với SAM»). **Golden #1 — LS&ĐL 5 Bài 8 — đã tới máy
thật bằng dữ liệu thật**, đi qua đúng chuỗi `nguồn → SDM → sổ sửa → ValidatedRepair →
TSL đã chiếu → LessonDocument → assets/fixtures/real/ → app`. Nhưng **thứ tới được trẻ
là chữ sách, KHÔNG phải bản sửa**: cả 6 vùng đã sửa và đã kiểm vẫn withheld, vẫn không
mang chữ. Đó là câu trả lời đúng, không phải lỗi cần vá. Và bản APK dựng cho GATE E là
**bản đầu tiên trên máy này** mang pack đã sửa theo luật fail-closed vòng 5 — hệ quả
nhìn thấy được: **41 bài tập Toán biến mất, `toanExercises` còn 0** (§5.5).

---

## 1. PLANNED vs ACTUAL

| # | Việc | Trạng thái | Ghi chú |
|---|---|---|---|
| 1 | Workspace **OPTION B** | **DONE** | cờ gỡ, ba phương án kia xoá, đo lại đủ |
| 1b | Thống nhất MỘT bộ tên cho ba View | **DONE** | không đụng `lib/core` |
| 2 | **Golden #1** LS&ĐL 5 Bài 8 tới `assets/fixtures/real/` | **DONE** | lineage gate PASS `--require-repair` |
| 2b | Golden #1 trên **máy thật** (GATE E) | xem §6 | |
| 2c | Golden #2 Toán 4 t2 Bài 61 | **DEFERRED** | Founder giao WS-A/WS-B; không phải đích giao hàng cho trẻ |
| 2d | Regression Bài 17 | **DONE** | lineage L2 PASS — fixture KHÔNG cũ; L4 UNKNOWN (không có bản sửa nào) |
| 3 | Cổng **lineage** năm trường phiên bản | **DONE** | `tool/evidence/fixture_lineage.py`, 16 test |
| 4 | Visual grammar (giới hạn) | **NOT STARTED** | §8 — ngân sách vòng này dồn cho §2 |

---

## 2. OPTION B — Founder đã chọn, đã thi hành

Vòng 5 dựng **bốn** cách trình bày cùng một `NextAction` từ **một** commit
(`--dart-define=WAL_ASSIST=card|icon|peek|inlineTab`) và đo cả bốn trên Nokia 6.1.
Founder chọn **B**. Vòng 6 **thi hành quyết định** thay vì để thí nghiệm chạy tiếp:
enum `AssistPresentation`, cờ `WAL_ASSIST` và hai phương án A/C **đã xoá**.

Còn lại đúng ba trạng thái:

```
COLLAPSED  💡 trong hàng tiêu đề (0 dòng)        ← sau «Để sau»
PEEK       «💡 SAM gợi ý: Xem Đọc →» (1 dòng)    ← MẶC ĐỊNH, 0 chạm biết ĐÍCH ĐẾN
EXPANDED   vì sao + CTA + «Để sau» + «Đã mở …»   ← trẻ chạm mới mở
```

Đề xuất chuyển sang View **khác** ⇒ hé lại một lần.

### 2.1 Ba thứ bị xoá cùng với quyết định

Bản đồ trùng lặp vòng 5 gọi tên bốn thứ; ba trong đó chết theo phương án B:

| bỏ | vì sao |
|---|---|
| **CTA đổi View trên thẻ đề xuất** | lặp đúng cái tab nằm ngay phía trên nó |
| **chân dung SAM trên thẻ** | SAM không nói ở đó — kỷ luật linh vật |
| **hàng «Đã mở ● ○ ○» thường trực** | dấu vết PHIÊN, không phải bằng chứng học (MỞ ≠ HIỂU) ⇒ chuyển vào EXPANDED, đúng đề nghị §2 mục 11 của vòng 5 |

Thứ tư — bong bóng «Con muốn học bài này theo cách nào?» ở màn chọn — **giữ nguyên**:
vòng 5 ghi là «chưa làm, chờ Founder», và đó không phải việc của làn này tự quyết.

Kèm theo: bản vá vòng 4 §6.3 và vòng 5 D1 — đẩy thẻ đề xuất **vào vùng cuộn** của Đọc
rồi Trực quan để trang sách và nút trung tâm sơ đồ không bị che — **không còn cần** và
đã gỡ.

### 2.2 Số đo (cây widget, khung Nokia 392.7 × 698.2 dp, fixture MẪU, chạy được ở CI)

| | Đọc | Trực quan | Học với SAM |
|---|---|---|---|
| chrome ghim vòng 4/5 (`card`) | 225 dp | 225 dp | **411 dp = 58.9 %** |
| chrome ghim vòng 6 (**B**) | **281 dp** | **281 dp** | **281 dp** |
| B sau «Để sau» | **225 dp** | 225 dp | 225 dp |
| nhãn View nhìn thấy | 4 | 4 | 3 |

Y của nội dung bài đầu tiên ở **Trực quan**: `card` 384.0 dp → **B hé 289.0 dp** →
**B thu gọn 233.0 dp**.

**Điều đáng chú ý nhất không phải con số nhỏ nhất mà là con số BẰNG NHAU.** Vòng 5 đo
411 dp ở «Học với SAM» so với 225 dp ở hai View kia — chênh lệch ấy tồn tại chỉ vì một
tấm thẻ. Nay ba View trả cùng một giá, và có test ghim điều đó.

Số đo máy thật của A/B/C (820 / 634 / 712 / 565 px) **không tái dựng được ở nhánh này**,
và đó là chủ ý: chúng nằm ở `TRACK-B-ROUND5-WORKSPACE-DUPLICATION.md` §5 và tái dựng
được ở `lane-b/round5-experience` (PR #87).

### 2.3 Một lỗi test bắt được, vòng 5 chưa từng chạm

Với nhãn CTA dài nhất — «🦉 Học với SAM» — hàng nút của trạng thái EXPANDED **tràn
2.2 px** ở bề ngang Nokia. Vòng 5 chỉ mở EXPANDED khi đích là «✨ Trực quan» nên không
gặp. Sửa bằng `Flexible` + cắt một dòng; vùng chạm và nhãn trợ năng không đổi.

### 2.4 MỘT bộ tên cho ba View

Vòng 5 đo được bộ đếm nhãn ra **5** chứ không phải 6, và chính con số ấy là phát hiện:
«Học **cùng** SAM» (thẻ) ≠ «Học **với** SAM» (tab), nên bộ đếm trượt một lần. Trẻ đọc
**sáu nhãn cho ba thứ**, hai trong số đó khác chữ.

`ModePicker` không còn bảng tên riêng; nhãn thẻ lấy đúng `WorkspaceView.label`, cùng
nguồn với tab. **Việc này nằm trọn trong `lib/features/**` — không cần đụng `lib/core`,
nên không phụ thuộc WS-C.**

Test không ghim «đếm được 6» (đếm không bắt được lỗi này — nó chỉ làm số trượt xuống).
Nó ghim: **mỗi tên View phải xuất hiện đúng 2 lần** (tab + thẻ), và ba chuỗi của bộ chữ
cũ phải biến mất khỏi cả màn lẫn mã nguồn.

### 2.5 Những điều B không được đánh đổi — có test

- đề xuất **nhìn thấy được ở CẢ BA View**, ở **cả ba trạng thái**;
- chạm 💡 khi đã thu gọn ⇒ mở **tại chỗ**, không bottom sheet (sheet là phương án A);
- vùng chạm ≥ 48 dp, nhãn + gợi ý cho trình đọc màn hình ở mọi dấu hiệu;
- bàn phím lên ⇒ gợi ý nhường chỗ;
- ở màn «Vào bài học» **không** có lớp trợ giúp (lý do đã nằm trên thẻ được đề xuất);
- **không có động cơ đề xuất thứ hai**: test soi mã cấm `assist_layer` chạm
  `LessonDocument` / `WorkspaceTrace` / `nextActionFor` / `founderNextAction`. Dòng
  «Đã mở …» đi vào lớp ấy dưới dạng **một chuỗi đã dựng sẵn**, nên lớp vẫn không hỏi
  được trace;
- **cờ A/B đã gỡ** — có test, để quyết định không lặng lẽ mở lại.

---

## 3. GOLDEN #1 — LS&ĐL 5 Bài 8, chuỗi đầy đủ với băm

Founder chốt: Golden #1 là **LS&ĐL 5 Bài 8** «Đấu tranh giành độc lập thời kì Bắc
thuộc» (SGK trang 36–39), và lời tuyên bố giao hàng đặt lên nó.

```
nguồn SGK (PDF trang 38–41)
  → SDM sdm-v3 · TSL tc2-r5      c9d2cf1f…  (canonical)
  → sổ sửa lane-c (240 dòng)
  → ValidatedRepair × 9 trên 6 khối
  → TSL ĐÃ CHIẾU (WS-C, tsl-repair-projection-v1)   d7825280…  (canonical)
  → LessonDocument (WS-C: 34 phục vụ / 17 giữ lại)  fb5dbfa8…  (bytes)
  → History rules v2 (hậu xử lí)                    a904d005…  (bytes)
  → assets/fixtures/real/lesson-05-sgk-lich-su-va-dia-li-5-b8.json
  → WorkspaceCatalog chọn ĐƯỜNG THẬT → ba Learning View → máy thật
```

Cổng `tool/evidence/fixture_lineage.py --require-repair`: **VERDICT PASS**.

### 3.1 Không cần đụng `lib/` — bẫy dây của điều phối viên KHÔNG nổ

`WorkspaceCatalog` đã ưu tiên `realPath` và ô `05-sgk-lich-su-va-dia-li-5#8` đã đăng
ký sẵn. Toàn bộ thay đổi là: **tệp ấy tồn tại**.

### 3.2 Hai quyết định phải nói thẳng

**(a) Tài liệu KHÔNG được bắc cầu lại ở nhánh này.** Chỉ cầu của WS-C đóng dấu
`provenance.repair`. Bắc cầu lại bằng cầu của nhánh này cho ra một tài liệu **trông
ổn và chứng minh được zero**: đo được 57 khối thay vì 52, và **không** có một dòng xuất
xứ sửa chữa nào. Nên `golden_delivery.py` mọc thêm chế độ `--doc`.

**(b) Hậu xử lí History rules ĐƯỢC áp, vì đúng MỘT lí do: cái tiêu đề.** Tài liệu của
WS-C mang tiêu đề pipeline **«THỜI KĨ BẮC THUỘC»** — một dòng tiêu đề hỏng OCR mà trẻ
đọc ngay đầu bài. `lesson-title-v1` suy ra «Đấu tranh giành độc lập thời kì Bắc thuộc»
từ **mục lục in**, khớp hậu tố không phân biệt dấu, đúng như vòng 4 đã làm, và ghi lại
`titleDerivation` trong provenance. Nó **không đổi gì khác**: mốc thời gian 0 → 0.

### 3.3 Trẻ được gì, và MẤT gì

| | bản MẪU (đang chạy trước vòng 6) | Golden #1 (vòng 6) |
|---|---|---|
| chữ phục vụ | 23 khối, mọi đoạn mở đầu `[MẪU]` | **34 khối chữ SGK thật** |
| chỗ để trống | ít, dựng sẵn | **17, mỗi chỗ nêu lý do** |
| dòng thời gian | **7 mốc** (dựng sẵn) | **0 mốc** |
| kịch bản SAM | **7 bước** (dựng sẵn) | **không có** |
| ảnh cắt trang | 5 ảnh mẫu | **0** — xem §5 |

**Đây là một đánh đổi thật, không phải một chiến thắng thuần.** Trẻ đổi một trục thời
gian dựng sẵn lấy chữ sách thật cộng những chỗ trống trung thực. Theo doctrine
(`FIXTURE ≠ TRUSTED CORPUS`, `MOCK ≠ EVIDENCE`) đó là hướng đúng — nhưng nói rằng vòng
này chỉ toàn thêm cho trẻ là nói sai.

### 3.4 Ca sắc nhất của Founder — và câu trả lời trung thực

`p039:000` là khối mang **cả bảy** mốc có năm. Trong Golden #1 nó là:

```
type: withheld · trust: withheld · reasons: ['agree_tones']
KHÔNG có trường text · textLen 272
repair.disposition: VALIDATED_REPAIR · servable: false
method: lanec.tone-corroboration-v1 · verdict: validated
```

**Đã sửa, đã kiểm, vẫn giữ lại, không viết lại gì.** Vì thế bài không còn mốc nào và
app **không được** vẽ trục thời gian. `VALIDATED REPAIR ≠ TRUSTED` · `RESTORED ≠
TRUSTED` · `CONNECT ≠ TRUST`.

### 3.5 Bản ghi sửa KHÔNG mang giá trị đề xuất — kiểm được

Đo được: bản ghi sửa ở mỗi khối mang `repairId · disposition · failureClass · method ·
repairVersion · validatorId · validatorVersion · verdict · supportingLayers · changed ·
servable · structuredKind · caps`, và **không một trường chữ nào**.

Test nặng nhất của Golden #1 ghim **điều đó**, chứ không đi tìm một chuỗi mà theo cấu
tạo không tồn tại — một test đi tìm cái không có mặt sẽ **xanh kể cả khi bảo đảm bị gỡ
bỏ**.

---

## 4. Cổng LINEAGE — thế hệ nào đây?

Founder ra luật vòng 6: mọi fixture thật dùng làm bằng chứng phải ghi **băm TSL nguồn ·
phiên bản pipeline · phiên bản SDM · phiên bản sửa · phiên bản generator**.
`assets/fixtures/real/` nằm trong `.gitignore`, nên **bản ghi bên trong tệp là cách duy
nhất** người đọc sau biết mình cầm thế hệ nào.

`tool/evidence/fixture_lineage.py` — L1 năm trường · L2 băm lại TSL · L3 nhất quán nội
tại · L3b gốc thế hệ · L4 xuất xứ sửa · L5 ảnh cắt · L6 dấu D4.

**UNKNOWN không bao giờ tính là PASS**, và một mình nó không làm đỏ build: công cụ này
không được trở thành lý do ai đó viết PASS khi sự thật là «tôi không kiểm được».

### 4.1 Nó bắt được một artefact cũ ngay lần dùng đầu

Golden #1 được dàn từ artefact **11:01** của WS-C. Đến **11:08** WS-C chạy lại; TSL trên
đĩa không còn băm ra con số tài liệu khai (khối 36 → 34, withheld 15 → 17). L2 đỏ với
đúng câu «THE FIXTURE WAS NOT BUILT FROM THE TSL IT NAMES». Chép lại từ artefact hiện
hành ⇒ PASS. **Đây chính là cái bẫy vòng 5 đã sập.**

### 4.2 Hai phát hiện về chính hệ đo

**(a) HAI CÁCH BĂM đang cùng tồn tại và cho số khác nhau.** Cầu đã commit ghi băm
**byte tệp** (`sha256_file`); đường sửa vòng 6 ghi băm **JSON chuẩn hoá**
(`sort_keys`, compact, không escape ASCII). Người kiểm chạy `shasum -a 256` trên một
artefact của đường sửa sẽ ra số khác và kết luận **artefact bị sửa trộm**. Cổng nay băm
cả hai cách, chấp nhận một trong hai, và **gọi tên** cách nào khớp.

**(b) TÊN PIPELINE KHÔNG PHÂN BIỆT ĐƯỢC THẾ HỆ.** Bản chạy lại vòng 5 của Bài 8 nằm dưới
`tc-v2/tc2-r5/` nhưng **khai `pipeline: tc2-p1`**, và id khối vẫn nhúng `tc2-p1`. Hai
tài liệu cách nhau nhiều tháng cùng đọc là `sourcePipeline: tc2-p1`. **Chỉ `sdmVersion`
và băm mới là thẩm quyền.** L3b nêu gốc thế hệ lấy từ `tslPath` và **báo bất đồng** thay
vì cho qua theo cái tên.

---

## 5. Hai khoảng trống của Golden #1 — trả về WS-C, không tự vá

| # | Điều | Hệ quả với trẻ |
|---|---|---|
| **G1** | Tài liệu WS-C dựng **không có ảnh cắt** (`--no-crops`, hoặc không có PDF trong sandbox) | 17 chỗ để trống hiện **không có ảnh trang**, chỉ có lời giải thích + số trang. Trạng thái «WITHHELD không ảnh» là hợp lệ theo thiết kế, nhưng «WITHHELD có ảnh» tốt hơn hẳn và **có sẵn dữ liệu**: cầu của nhánh này dựng được **20 ảnh cắt** từ đúng TSL ấy. |
| **G2** | `bookTitle`/`subject` của WS-C ra dạng dài («Lịch sử và Địa lí 5») vì `poc-out/graph/curriculum-structure.json` không giải được trong sandbox của họ | dòng nguồn dài hơn cần thiết trên màn; không sai, chỉ dài |

**Yêu cầu gửi WS-C:** chạy lại cầu **có ảnh cắt** và với `poc-out/graph/` giải được, rồi
Golden #1 dựng lại một lượt — lệnh đã có sẵn một dòng.

---

## 6. GATE E — máy thật

Xem `~/Desktop/wal-evidence/round6-ws-d/` (khung ảnh **không** commit — chữ SGK nguyên
văn và ảnh cắt trang là NỘI BỘ / NGHIÊN CỨU theo D4).

| | |
|---|---|
| máy | **Nokia 6.1**, `Plate2_00WW`, adb qua WiFi `192.168.1.3:5555` |
| hệ điều hành | **Android 10** (SDK 29) |
| gói | `ai.workizen.learningcoach` (máy còn `com.workizen.tongtai` — không grep «workizen») |
| bài | **LS&ĐL 5 Bài 8** · fixture thật · lineage PASS |

| bản dựng | `eac69ea` · `app-debug.apk` sha256 `7b2b2b79a5518a16…` · 245 952 191 B |
| pack | **dựng lại trước khi đo** · verify 12/12 OK · 41 `toanExercises` biến mất (§5.5) |
| fixture | `lesson-05-sgk-lich-su-va-dia-li-5-b8.json` sha256 `a904d0052aa9ff7d…` · 52 khối · semantic 0 · tutorSteps 0 |
| học sinh | «Na» — hồ sơ của Founder **giữ nguyên** (`adb install -r`, không gỡ) |
| kiểm tĩnh | **0 / 2 073 600 điểm ảnh** khác nhau qua 6 giây ⇒ không ai đang dùng máy |
| manifest | `~/Desktop/wal-evidence/round6-ws-d/MANIFEST.json` (`tool/evidence/retain.py`) |

| bước | mong đợi | kết quả | khung ảnh |
|---|---|---|---|
| 01 | Home, hồ sơ Founder còn | **PASS** | `round6-01-home.png` |
| 02 | thẻ lát cắt nghiên cứu mang **tiêu đề thật từ mục lục in** | **PASS** | `round6-02-home-research.png` |
| 03 | màn «Vào bài học»: **một** bộ tên · ba thẻ đếm từ chính bài | **PASS** | `round6-03-picker.png` |
| 04 | **B · PEEK** một dòng; chữ SGK thật hiện ngay | **PASS** | `round6-04-read-peek.png` |
| 05 | **B · EXPANDED** vì sao + «Đã mở ● ○ ○» + CTA, mở tại chỗ | **PASS** | `round6-05-read-expanded.png` |
| 06 | **B · COLLAPSED** 💡 lên hàng tiêu đề, KHÔNG biến mất | **PASS** | `round6-06-read-collapsed.png` |
| 07 | «Học với SAM» nói thật là chưa có kịch bản; chrome bằng hai View kia | **PASS** | `round6-07-tutor.png` |
| 08 | kiểm tĩnh từng điểm ảnh | **PASS** | — |
| 09 | 17 chỗ để trống có **ảnh cắt trang** | **FAIL** | khoảng trống **G1**, xem §5 |

### 6.1 Ba màn hình đáng xem nhất

**Màn «Vào bài học»** trả lời ba câu bằng dữ liệu thật của chính bài, và cả ba đều là
con số 0 trung thực ở hai chỗ:

```
📖 Đọc         Như trong sách · 18 đoạn · 3 câu hỏi trong sách · 17 chỗ SAM để trống
✨ Trực quan   Chưa có sơ đồ cho bài này — chỉ có bảng tóm tắt lời sách
🦉 Học với SAM Chưa có kịch bản cho bài này
```

Và **cả sáu nhãn dùng đúng một bộ chữ** — đo được trên máy, không phải trong test.

**Màn Đọc** hiện ngay chữ SGK nguyên văn («Kể được tên và vẽ được trục thời gian … ví
dụ: 179 TCN, 40, 248, 542, 938,…») cùng dải trang `36 · 37 · 38 · 39`, và **một chỗ SAM
để trống ở ngay khối đầu tiên**, kèm lý do và nút «Vì sao SAM để trống?».

**Đo được trên máy:** thu gọn gợi ý đưa nội dung bài lên **~146 px** (hé → thu gọn).

### 6.2 Hai điều máy thật cho thấy mà test không

**(a) SAM bảo trẻ RỜI bài vừa mở.** Ở cả ba View, gợi ý là **«SAM gợi ý: Về mục lục»**,
và khi mở ra, lý do là **«Con đã đi qua các cách học của bài này»** — trong khi dòng
«Đã mở» ngay bên dưới nó ghi **`● Đọc ○ Trực quan ○ Học với SAM`**. Trẻ mới mở MỘT cách.
Runtime đang coi «hai View kia không có gì để xem» là «đã đi qua rồi». Hai dòng chữ
**mâu thuẫn nhau trên cùng một thẻ**, và chính việc chuyển «Đã mở» vào trạng thái mở là
thứ phơi ra mâu thuẫn ấy. Chỗ sinh lỗi nằm ở `lib/core/agenda/**` (runtime Next Action),
**không thuộc làn này** — trả về cho chủ sở hữu, không tự sửa.

**(b) Tiêu đề bị hạ chữ hoa ở tầng hiển thị.** Fixture mang «… thời kì **B**ắc thuộc»;
màn hình hiện «… thời kì **b**ắc thuộc». Một quy tắc viết hoa câu đang áp lên tên riêng.
Nhỏ, nhưng đây là **tên riêng lịch sử** trong một app cho trẻ.

---

## 7. Ba test đã đổi ý nghĩa, và một test KHÔNG được đụng

| tệp | đổi gì | vì sao |
|---|---|---|
| `workspace_density_test.dart` | bỏ so A/B/C, ghim bất biến của B | Founder đã chọn |
| `round5_visual_test.dart` D1 | ghim «ba View cùng chrome» thay cho «thẻ nằm trong vùng cuộn» | bản vá cũ không còn thứ để vá |
| `round4_experience_test.dart` §6.7 | «Đã mở» chuyển vào EXPANDED | nội dung không đổi |
| `no_machine_ids_test.dart` | trục thời gian hiện ra **khi và chỉ khi** bài có `TimelineSemantic` | nới thành «có cũng được» sẽ xanh cả khi app vẽ trục từ hư không |
| **`test/core/lesson_model/timeline_history_test.dart`** | **KHÔNG ĐỤNG** | tệp của WS-C; nó chờ 7 mốc và tiêu đề cũ, nay **đỏ trên máy này**. Đó là **tín hiệu thật** thuộc về WS-C, không phải rác cần dọn. Nó **bỏ qua** trên bản sao sạch ⇒ **CI không ảnh hưởng**. |

---

## 8. Visual grammar — **NOT STARTED**, và nói thẳng

Ngân sách vòng này dồn vào Option B và Golden #1. Điều tra hình thái (forms census),
điều tra mẫu ngữ nghĩa, kiến trúc xuất xứ và POC giới hạn **chưa bắt đầu**. Không có
renderer nào được thêm — đúng chỉ đạo «không mở rộng họ renderer», nhưng vì **chưa
làm**, không phải vì đã đo rồi kết luận.

---

## 9. TRẺ DÙNG ĐƯỢC GÌ HÔM NAY MÀ TRƯỚC VÒNG NÀY CHƯA DÙNG ĐƯỢC?

**Hai điều, và chỉ hai.**

1. **Một bài Lịch sử THẬT.** Trước vòng này, mở LS&ĐL 5 Bài 8 là đọc 23 đoạn văn nhại
   mở đầu bằng `[MẪU]`. Nay là **34 khối chữ SGK thật** (trang 36–39) cộng **17 chỗ
   trống có lý do**. Đổi lại **mất** trục thời gian 7 mốc và kịch bản SAM 7 bước — cả
   hai đều là đồ dựng sẵn, và cả hai biến mất vì dữ liệu thật chưa đủ tin.
2. **Màn học bớt chật.** Ở «Học với SAM», phần ghim 411 dp → **281 dp**, còn **225 dp**
   sau «Để sau»; nội dung bài ở Trực quan bắt đầu ở **289 dp** thay vì 384 dp; ba tên
   View nay là **một** bộ chữ thay vì hai.

**PHỤ HUYNH:** *không có gì mới.*

**SAM:** *không có gì mới.* Không có kịch bản nào cho Bài 8 ở đường thật, và Next Action
không đổi luật.

**NỘI BỘ / NGHIÊN CỨU:** cổng lineage + driver giao hàng; chuỗi Golden #1 có băm; hai
phát hiện về hệ đo (§4.2); hai khoảng trống trả về WS-C (§5). **Công cụ và test không
tính là giao hàng cho người học.**

---

## 10. Còn là GIẢ THUYẾT

- Rằng chữ sách thật + chỗ trống trung thực **dạy tốt hơn** một trục thời gian dựng
  sẵn. Hợp doctrine, **chưa đo trên trẻ.**
- Rằng phương án B tốt hơn A/C với **trẻ** (số vòng 5 là mật độ và số chạm, không phải
  kết quả học).
- Rằng khôi phục ảnh cắt (G1) sẽ làm 17 chỗ trống dễ hiểu hơn — hợp lí, **chưa đo.**


---

## 5.5 PACK CŨ HƠN MÃ — và bản APK đầu tiên trên máy này không còn thế

Điều phối viên bắt đúng một cái bẫy GATE E: `assets/pack/*.json` **nằm trong
`.gitignore`**, và pack trên máy này được dựng **trước** bản vá fail-closed vòng 5 của
Lane D. Dựng APK từ chúng nghĩa là đo nhầm artefact — bản trên máy sẽ mang đúng thứ
pipeline đã phán là không được ship. `test/features/subjects/lesson_index_test.dart` đỏ
**không phải vì test hỏng, mà vì nó phát hiện đúng điều đó.**

Đi theo kỷ luật của `tool/corpus/legacy/packs.py` — `snapshot → rebuild → verify →
delta` — chứ không dựng lại bằng tay:

| | trước | sau |
|---|---|---|
| `pack_provenance verify` | **0/12 OK (FAIL)** | **12/12 OK (PASS)** |
| `attachmentRule` đóng dấu | `capped-toc-v1` (mã nói `capped-toc-v2`) | `capped-toc-v2` |
| hoạt động | 248 | **207** |
| unchanged / content-changed / moved / appeared | 207 / 0 / 0 / 0 | |
| **disappeared** | | **41** |

**Cả 41 thứ biến mất đều là `toanExercises`** — lớp 4 mất 26, lớp 5 mất 15. Họ hoạt động
`toanExercises` đi từ **41 xuống 0**. Mọi họ khác (`tvReadings` 66, `tvWritings` 54,
`khoaExperiments` 46, `sourceAssets` 36, `suSources` 4, `diaMaps` 1) **không đổi một
byte**, và 10/12 lớp băm nội dung y hệt.

Đó là 41 biểu thức **INFERRED** dựng lại bằng hình học mà bản dựng hiện hành **từ chối
phát** vì mất `status`/`provenance`. Bản vá đã có trong mã từ vòng 5; điều mới của vòng
6 là **nó lần đầu tới được một bản APK**.

**Với trẻ: app nay có 0 bài tập Toán.** Một số 0 trung thực, đúng chỗ Founder dặn không
được giả vờ có đường Toán khi chưa có. Ảnh chụp trước bản này đã đo một artefact khác —
đừng so trực tiếp.

Ảnh chụp tình trạng cũ vẫn dựng lại được: `packs.py restore poc-out/round6/ws-d/packs-before`.
