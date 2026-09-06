# ROUND 7 · VÒNG 2 — HOME THÀNH **AI LEARNING HOME CHO MỘT NGÀY HỌC NHIỀU MÔN**

**Đơn hàng:** Founder order 50 (`docs/founder-orders/50-founder-addendum-round-7-multi-subject-home.md`,
nhánh `docs/order-50`). Dựa trên **vòng 1** (PR #115, `round7/v1-home-workspace-visual`) — chưa merge.

**Nhánh:** `round7/multi-subject-home` · **Trạng thái:** READY FOR FOUNDER REVIEW ·
**⛔ DO NOT MERGE.**

**Máy thật:** Nokia 6.1 (`192.168.1.3:5555`), `ai.workizen.learningcoach`, `adb install -r`
(giữ nguyên app data của Founder — **không gỡ cài lần nào**). Pack dựng lại từ chính nhánh này
trước khi build.

**Golden Lesson KHÔNG đổi:** KHTN 6 · Bài 17. Vòng này chỉ sửa **KIẾN TRÚC THÔNG TIN CỦA HOME**
để Bài 17 nằm trong một hệ nhiều môn thực tế hơn (order 50 §11).

---

## A · HOME **BEFORE** — landing page của Bài 17

`~/Desktop/wal-evidence/round7-v1-device-2026-09-06/10-AFTER-home.png` (khung của vòng 1).

Màn đầu Nokia 6.1 chứa **đúng một bài**, trong một mega-card chiếm gần trọn màn:

```
Chào Na
┌─ ĐANG HỌC ─────────────────────────────┐
│ Bài 17 · TÁCH CHẤT KHỎI HỖN HỢP        │   ← tên bài IN HOA, hai dòng
│ Chương IV · SGK KHTN 6 · trang 60–63   │
│ 🧪 Bản thử nghiệm · nguồn SGK…      ⓘ  │
│ ▬▬ ▬▬ ▬▬   đã mở 0/3 cách học          │
│ 🦉 «Con đọc bài trong sách trước nhé…» │
│ [        📖 Đọc ▸                    ] │
└────────────────────────────────────────┘
CÓ THỂ LÀM TIẾP · SAM ĐÃ THẤY GÌ · HÔM NAY …
```

Founder, sau khi cầm máy: «HOME hiện tại đang bị **tối ưu quá mức cho một Golden Lesson duy
nhất**. Đây KHÔNG đúng với hành vi học thực tế. Một học sinh trong một ngày có thể học Toán ·
Tiếng Việt · KHTN · Lịch sử & Địa lý · Ngoại ngữ…»

Và một môn thứ hai **có thật** trên máy — LS&ĐL 5 · Bài 8 — thì nằm dưới một khu riêng tên
«**SAM ĐANG TẬP ĐỌC SÁCH KHÁC**», kèm câu «Đây không phải bài của lớp con — SAM đang **tập đọc
thử một cuốn sách khác**. Con xem cho biết cũng được.» Một bài học bị hạ xuống thành phế phẩm
nghiên cứu (§6).

---

## B · HOME **AFTER** — hai tầng, thẻ trượt ngang

`10-AFTER-home-card1.png` · ghép đôi: `BEFORE-AFTER-home.png`.

```
Chào Na                                        ← một dòng
HÔM NAY                                        ← TẦNG 1 · NHIỀU MÔN
┌───────────────────────────┐ ┌─────────────
│ KHTN 6        ĐANG GỢI Ý  │ │ LS&ĐL 5      ← thẻ kế bên HÉ RA
│ Bài 17 · TÁCH CHẤT…       │ │ Bài 8 · Đấu…
│ [CHƯA BẮT ĐẦU]            │ │ Sách lớp 5 ·
│ SAM đã xếp sẵn 3 cách học │ │ [CHƯA BẮT ĐẦ
│ Tiếp theo: 📖 Đọc →       │ │ Tiếp theo: …
└───────────────────────────┘ └─────────────
        ▬▬ · · · · ·                          ← 6 thẻ
Con còn 5 môn nữa trên giá sách — mở «Môn học» để xem hết.
SAM GỢI Ý                                      ← TẦNG 2 · MỘT VIỆC
┌──────────────────────────────────────────┐
│ KHTN 6 · Bài 17                          │
│ Chương IV · SGK KHTN 6 · trang 60–63     │
│ 🧪 Bản thử nghiệm · nguồn SGK…        ⓘ  │
│ 🦉 «Con đọc bài trong sách trước nhé…»   │
│ [           📖 Đọc ▸                   ] │  ← nút TÔ ĐẶC DUY NHẤT của màn
└──────────────────────────────────────────┘
CÓ THỂ LÀM TIẾP · SAM ĐÃ THẤY GÌ · CÁC MÔN CỦA CON · … · CÁCH KHÁC ĐỂ HỌC
```

| Điều Founder yêu cầu | Đã làm | Đo được ở đâu |
|---|---|---|
| §2 hàng Smart Card trượt ngang | `PageView`, `padEnds: false`, không tự chạy, không lặp vòng | `10`–`12`; test «vuốt sang thẻ 2» |
| §4 thẻ chính 75–85 % viewport + thẻ kế bên hé | `viewportFraction = .82`; test đo **tỉ lệ thật ở 360 dp** và đòi mép phải còn chỗ | `home_multi_subject_test` §2·§4 |
| §5 hai tầng, **một** hành động | Cả màn **đúng một `FilledButton`** — «Chụp bài tập» ở hàng cuối hạ xuống viền, thẻ Scale thành «CÁC MÔN CỦA CON» viền | test `findsOneWidget` trên `FilledButton` |
| §7 hero co lại | Thanh «đã mở N/M» rời hero xuống «SAM ĐÃ THẤY GÌ»; tầng 2 chỉ còn **định danh bài · nguồn · lời SAM · nút** | `10` vs BEFORE |
| §6 môn khác không bị đẩy thành «sách khác» | Khu «LÁT CẮT NGHIÊN CỨU» **bị gỡ**; LS&ĐL 5 là thẻ học bình thường mang dòng «Sách lớp 5 · không phải sách lớp con» | `11`, `16`; `home_other_subject_card_test` |

**Nếp gấp thật.** Ở đúng 360×640 dp của Nokia, **cả hai tầng nằm trong màn đầu**: hàng thẻ ở
y≈110 dp, nút việc-tiếp-theo kết thúc trước nếp gấp. Có bài kiểm đo đúng con số ấy
(`⭐⭐ 1b. NẾP GẤP THẬT`) — vì nếu tầng 1 đẩy tầng 2 xuống dưới thì «MULTI-SUBJECT CONTEXT +
SINGLE NEXT ACTION» thành **hai màn**, không phải một.

**Vuốt KHÔNG đổi việc SAM gợi ý.** Hàng thẻ là **learning context switcher** (§4), không phải
bộ chọn đề xuất. Trẻ vuốt sang LS&ĐL, tầng 2 vẫn nói KHTN 6 · Bài 17 (`11`, `17`). Có test.

---

## C · TRẠNG THÁI THẺ — **cái nào thật, cái nào rỗng-trung-thực**

> «Không cần fake dữ liệu nếu chưa có. Nếu chỉ một số môn có real data, hiển thị đúng trạng thái
> của chúng.» (order 50 §2)

Trên máy của Na (lớp 6) hôm nay có **ĐÚNG HAI** bài SAM đã xếp sẵn. Mọi thứ còn lại trong
`assets/pack/lesson-index-g6.json` là **mục lục giá sách** — một mục trẻ giở xem được, **không
phải** một bài mở được cùng SAM.

| # | Thẻ | Loại | Trạng thái | Vì sao trạng thái đó |
|---|---|---|---|---|
| 1 | **KHTN 6 · Bài 17** | **THẬT** — fixture thật, 3 cách học (Đọc · Trực quan · Học với SAM), tutorScript 5 bước | `CHƯA BẮT ĐẦU` → `ĐÃ MỞ ĐỌC` → … | chưa mở cách nào ⇒ CHƯA BẮT ĐẦU (`10`); sau khi đọc ⇒ ĐÃ MỞ ĐỌC (`15`) |
| 2 | **LS&ĐL 5 · Bài 8** | **THẬT** — fixture thật, **chỉ có Đọc** (không SemanticData, không kịch bản) | `CHƯA BẮT ĐẦU` → `TIẾP TỤC` | mở hết 1/1 cách học có ⇒ TIẾP TỤC, **không phải «xong»** (`17`) |
| 3 | Toán | **RỖNG-TRUNG-THỰC** | `CHƯA BẮT ĐẦU` | «SAM chưa xếp sẵn bài nào ở môn này. Giá sách mới có **mục lục 43 bài**.» |
| 4 | GDTC | RỖNG-TRUNG-THỰC | `CHƯA BẮT ĐẦU` | mục lục 24 bài |
| 5 | Tin học | RỖNG-TRUNG-THỰC | `CHƯA BẮT ĐẦU` | mục lục 17 bài |
| 6 | Mĩ thuật | RỖNG-TRUNG-THỰC | `CHƯA BẮT ĐẦU` | mục lục 16 bài |
| — | Công nghệ 14 · Tiếng Anh 12 · Ngữ văn 6 · HĐTN-HN 4 · Âm nhạc 4 | không lọt vào hàng | — | màn **NÓI RA**: «Con còn **5 môn nữa** trên giá sách» |

**Không thẻ Toán giả với tiến độ giả.** Đây là chỗ đơn hàng dễ bị phản bội nhất và nó được khoá
bằng bài kiểm: thẻ rỗng không có `lessonLine`, không có việc tiếp theo trong bài, và **không bao
giờ** được đưa lên tầng 2. Chạm nó mở **Giá sách** — việc thật duy nhất có (`13`).

### Từ vựng trạng thái — khoá bằng `enum`

`HomeCardState` chứa **đúng sáu** nhãn Founder cho phép: `ĐANG HỌC` · `CHƯA BẮT ĐẦU` ·
`ĐÃ MỞ ĐỌC` · `ĐÃ XEM TRỰC QUAN` · `CÓ THỂ LUYỆN` · `TIẾP TỤC`. Luật gán, tất định, đọc được
thành lời:

```
chưa mở cách nào                      ⇒ CHƯA BẮT ĐẦU
đã mở HẾT cách bài này có             ⇒ TIẾP TỤC        («đã mở» ≠ «xong»)
đã mở đúng một cách, là Đọc           ⇒ ĐÃ MỞ ĐỌC
đã mở đúng một cách, là Trực quan     ⇒ ĐÃ XEM TRỰC QUAN
còn lại (>1, chưa hết)                ⇒ ĐANG HỌC
```

Ví dụ §3 của chính Founder — đã mở Đọc + Trực quan, còn Học với SAM ⇒ **ĐANG HỌC** — rơi đúng
nhánh cuối. Có bài kiểm dựng lại nguyên bảng.

> ⚠ **`CÓ THỂ LUYỆN` hiện KHÔNG được gán ở đâu, và đó là chủ ý.** Bản dựng hôm nay không đo được
> «sẵn sàng luyện tập» — vòng luyện tập thuộc nhánh `round7/v2-sam-teaching`. Gán nó bây giờ là
> suy diễn, đúng thứ §9 cấm. Có **một bài kiểm khoá đúng điều đó**: ai bắt đầu gán nó sẽ phải sửa
> bài kiểm ấy và nói ra bằng chứng của mình.

**Cấm bằng tên, quét CẢ MÀN:** `ĐÃ HIỂU` · `%` · `GIỎI` · `MASTERED` · `đã thạo` · `thành thạo` ·
`hoàn thành bài` · `điểm số` · `⭐` · `★`. Màu trạng thái lấy từ `LearningStateToken`, và
`mastered` (xanh «đầy + ấm») **không bao giờ** được dùng ở đây: không thẻ nào trên Home có bằng
chứng cho tuyên bố ấy.

---

## D · **ONE NEXT ACTION được chọn thế nào** (§12 D)

**Nó vẫn là TRÌNH BÀY, không phải động cơ thứ hai.** Mỗi bài đã có việc tiếp theo của riêng nó,
do `founderNextAction` — **đúng hàm mà Lesson Workspace gọi** — sinh ra. Home không tính lại gì.
Việc mới của vòng này hẹp hơn nhiều: **trong nhiều bài, đưa thẻ nào lên «SAM GỢI Ý»**.

`promotedCardIndex` (hàm thuần, `lib/features/mission/home_cards.dart`) là **bậc thang**, bậc
trên thắng tuyệt đối:

| # | Bậc | Vì sao |
|---|---|---|
| 1 | Có bài thật **và** có `LessonNextAction` | thẻ rỗng-trung-thực không có việc tiếp theo để nêu; đẩy nó lên là **bịa ra một đề xuất**. Mạch chưa nối động cơ cũng không được lên — **fail closed** |
| 2 | Sách **đúng lớp** của con | SAM không lấy sách lớp khác làm việc hôm nay, kể cả khi bài ấy đang dở |
| 3 | Việc tiếp theo mở được **một cách học** (`view != null`) | «xem tiếp bài này» là câu trả lời thật, nhưng một cách học cụ thể dẫn trẻ đi xa hơn |
| 4 | Bài **đang dở** (đã mở ≥ 1 cách) | tiếp việc đang làm trước khi mở việc mới |
| 5 | Thứ tự trong hàng | tất định — hai lần dựng ra cùng một kết quả |

Không thẻ nào đủ tư cách ⇒ trả `null`, và màn **rơi về thẻ đề xuất cũ** của «Hôm nay», không bịa
gì.

**Bằng chứng đã chấm vẫn thắng bài thử nghiệm.** Khi Toán đang khẩn vì bằng chứng thật
(`agenda.kind == review | retrieve`), việc ấy chiếm tầng 2 và bài fixture lùi về hàng thẻ — thứ
tự đã chốt từ Convergence §10, order 50 không đụng tới. Có test.

**Kỷ luật «không có động cơ thứ hai» được soi bằng mã.** `home_multi_subject_test` đọc
`home_cards.dart` (bỏ chú thích) và cấm `founderNextAction` · `nextActionFor` ·
`nextBestLessonAction` · `WorkspaceTrace` · `LearnerStore`. Đây là **cùng kỷ luật** mà
`assist_layer.dart` phải theo (`workspace_density_test` §3) — và **bài kiểm ấy vẫn xanh**.

Thứ tự **hàng thẻ** cũng là luật thuần, không phải quyết định rải trong widget:
bài **đúng lớp** → bài **lớp khác** → môn giá sách theo (**mở làm được ↓**, **mục lục ↓**,
**tên môn**), cắt ở `kHomeCardLimit = 6`, và số môn bị cắt **được nói ra**.

---

## E · MÁY THẬT (§10)

Thư mục: `~/Desktop/wal-evidence/round7-v2-multi-subject-home-2026-09-06/` — **KHÔNG commit**
(D4: khung chứa chữ SGK). `MANIFEST.json` có sha256 từng khung.

| Khung | Bước §10 | Thấy gì |
|---|---|---|
| `10-AFTER-home-card1.png` | **thẻ đầu** | hai tầng cùng trong màn đầu; thẻ 2 hé ra; 6 chấm; «còn 5 môn nữa» |
| `11-AFTER-swipe-card2-other-grade.png` | **vuốt sang thẻ 2** | LS&ĐL 5 · Bài 8 · «Sách lớp 5 · không phải sách lớp con» · CHƯA BẮT ĐẦU — **và tầng 2 KHÔNG đổi** |
| `12-AFTER-swipe-card3-empty-subject.png` | (thẻ 3) | TOÁN · «SAM chưa xếp sẵn bài nào» · «Giá sách mới có mục lục 43 bài» · «Tiếp theo: Xem mục lục →»; GDTC hé bên cạnh |
| `13-AFTER-empty-card-opens-bookshelf.png` | (chạm thẻ rỗng) | mở **Giá sách**, không mở một bài không tồn tại |
| `14-AFTER-tap-next-action-lands-in-doc.png` | **bấm Next Action** | vào **thẳng Đọc** (không màn hỏi lại) |
| `15-AFTER-back-home-state-advanced.png` | **quay Home** | thẻ tiến lên `ĐÃ MỞ ĐỌC` · «Đã mở: Đọc» · «Tiếp theo: ✨ Trực quan →», tầng 2 tiến theo — **một động cơ, hai chỗ trình bày** |
| `16-AFTER-switch-to-other-subject.png` | **chuyển sang môn khác** | mở LS&ĐL 5 · Bài 8 ở Đọc |
| `17-AFTER-back-home-after-switch.png` | quay Home | thẻ LS&ĐL thành `TIẾP TỤC` · «Tiếp theo: Xem tiếp bài này →»; **SAM GỢI Ý vẫn là KHTN 6** |
| `BEFORE-AFTER-home.png` | ghép đôi | vòng 1 ↔ vòng 2 |

**Pack.** Dựng lại `assets/pack/lesson-index-g6.json` **từ chính nhánh này** trước khi build APK
(`tool/` giống hệt `origin/main`, kiểm bằng `git diff`). `contentHash` = `846ccc69fa88…` —
**giống hệt** bản đang có; `pack_provenance.py verify` báo **DEFAULT build** ⇒ pack không cũ.
(Luật này có vì pack cũ từng đẩy 41 biểu thức bịa lên máy thật.)

**Build:** `flutter build apk --debug`. `--release` **thất bại** trên máy này ở
`:app:minifyReleaseWithR8` — chưa điều tra, ngoài phạm vi order 50; ghi lại để không ai tưởng đã
thử được bản release.

### ⚠ MÁY DÙNG CHUNG — điều làm hỏng lượt đo đầu, và cách đã chặn

Nokia 6.1 đang được **agent `round7/v2-sam-teaching` dùng song song**. Hai lần trong lượt 1, giữa
chừng phiên đo: một APK khác (Home **vòng 1**) thay bản của nhánh này, và một thao tác không phải
của tôi mở «Học với SAM». Tôi đã đuổi theo nó như một lỗi sản phẩm trước khi khung
`idle` chỉ ra Home vòng 1 đang chạy trên máy.

**Cách đã chặn, và nên thành luật:** mọi khung dùng làm bằng chứng đều chụp trong cửa sổ ngay sau
`adb install -r` của nhánh này, và **foreground được kiểm `ai.workizen.learningcoach` TRƯỚC và
SAU mỗi thao tác** — thao tác nào rơi ra ngoài app thì khung bị **vứt và chụp lại**, không bao
giờ được đưa vào báo cáo. Bốn khung đã bị vứt theo luật này.

---

## F · HAI LỖI TÌM RA TRÊN MÁY, SỬA Ở NGUỒN

| # | Lỗi | Khung | Sửa |
|---|---|---|---|
| **D1** | Tầng 2 in **LẠI nguyên tiêu đề IN HOA** của Smart Card ngay trên nó — «KHTN 6 · Bài 17 · TÁCH CHẤT KHỎI HỖN HỢP» hai lần trên một màn, ăn hai dòng. Đúng thứ §7 cấm | lượt 1 `01-home` | tầng 2 chỉ **định danh** bài: «KHTN 6 · Bài 17», đúng ví dụ §5 của Founder. Tên đầy đủ vẫn ở Smart Card và trong bài |
| **D2** | Thẻ LS&ĐL 5 — thẻ **duy nhất** có thêm dòng «Sách lớp 5…» — bị **cắt ngang thân chữ** ở dòng «đã mở gì»: nửa hàng chữ kẹt giữa nhãn trạng thái và «Tiếp theo». Chữ xén ngang là chữ không đọc được, và nó rơi đúng vào thẻ mang sự thật về lớp | lượt 1 `02-swipe-card2` | chiều cao thẻ 172 → **186 dp**, và dòng ấy giới hạn **một hàng** khi có dòng lớp (cắt bằng «…» đọc được) |

Cả hai có bài kiểm riêng trong nhóm **«§7 — HERO CO LẠI, KHÔNG LẶP (lỗi tìm ra TRÊN MÁY THẬT)»**,
mỗi bài trích đúng khung đã tìm ra nó.

### G · MỘT LỖI DỮ LIỆU TÌM RA KHI ĐỌC PACK THẬT

`listedLessonCountFor` bản đầu khử trùng theo `(sách, SỐ BÀI)`. **GDTC đánh số lại theo từng chủ
đề**: 24 bản ghi mục lục sụp xuống còn **4** số bài phân biệt. Hệ quả: thẻ Home nói «mục lục 4
bài» trong khi **Giá sách ngay sau một chạm nói «24 bài»** — hai con số cho cùng một giá sách,
trên hai màn; và thứ tự hàng thẻ cũng sai theo.

`_dedupeLessons` ở **ngay đầu `lesson_index.dart`** đã viết sẵn lý do từ vòng trước: «GDTC đánh
số LẠI theo từng chủ đề… **Gộp theo số là xoá bài của trẻ.**» Tôi đã đi đúng vào cái bẫy tệp ấy
cảnh báo.

Sửa: **hai phép đếm, hai mẫu số, cả hai ghi rõ ở docstring** —
`listed` = **bản ghi mục lục** (đã khử trùng-hệt lúc parse), **cùng con số** `BookRef.lessonCount`
mà Giá sách in; `openable` = **số bài phân biệt theo (sách, số bài)**, vì `activitiesFor` định địa
chỉ việc-làm-được **bằng số bài** — đó là độ phân giải thật của dữ liệu, không phải một lựa chọn.
Bài kiểm dựng đúng hình dạng GDTC (ba «Bài 1» khác chủ đề) và đòi **5**.

---

## H · GUARDRAIL — không cái nào bị nới

| Bất biến | Ở đâu trong vòng này |
|---|---|
| `OPENED != UNDERSTOOD` | Trạng thái thẻ suy từ **đúng một** tín hiệu «đã mở tab»; mở hết ⇒ `TIẾP TỤC`, **không** «xong». «SAM ĐÃ THẤY GÌ» giữ thanh «đã mở N/M» và nói thẳng «mở bài không phải là hiểu bài» |
| `TAP != COMPETENCE` | `openedViews` là dấu vết **PHIÊN** (`WorkspaceTrace`), không ra đĩa, không thành sự kiện học. Home **nhận** tập ấy đã dựng sẵn — nó không tự hỏi trace (có test soi mã) |
| `MOCK != EVIDENCE` | Không thêm đường ghi nào |
| `FIXTURE != TRUSTED CORPUS` | `FixtureChip` «Bản thử nghiệm» vẫn ở tầng 2, cùng widget + cùng sheet «Nguồn & độ tin» với workspace; có test canh nó không mất khi màn sắp lại |
| `LLM OUTPUT != TRUTH` | Không gọi gì. Mọi chữ về việc tiếp theo là **nguyên văn** `LessonNextAction` |
| `trusted = 0`, `eligible for teaching = 0` | **KHÔNG ĐỔI.** Vòng này không chạm pipeline, không chạm cổng TC; pack `contentHash` giống hệt |
| D4 | Fixture thật + pack + `poc-out` vẫn gitignore; `git status` sạch. Khung máy thật ra `~/Desktop/wal-evidence/`, **không commit**. ⚠ **Một lỗi của chính tôi, đã sửa và đã dựng cổng** — xem §H1 |

### H1 · ⚠ TÔI ĐÃ ĐƯA MỘT ĐƯỜNG DẪN NGUỒN VÀO GIT, VÀ HÀNG RÀO KHÔNG BẮT ĐƯỢC

Để dựng lại pack trong worktree, tôi symlink nguồn về: `nguon-chi-thuc →
/Users/…/workizen-ai-learning-coach/nguon-chi-thuc`. Một `git add -A` sau đó đưa **symlink ấy vào
commit `266cdff`**.

`.gitignore` **có** dòng `nguon-chi-thuc/` ngay đầu tệp, dưới ba lý do «KHÔNG BAO GIỜ COMMIT».
Dấu `/` cuối nói với git: *chỉ khớp THƯ MỤC*. Một **symlink** cùng tên không bị nó chặn —
`git check-ignore` xác nhận. Hàng rào đứng đó, và đi vòng qua được.

**Mức nghiêm trọng, nói thẳng:** symlink chỉ mang **một chuỗi đường dẫn**. **Không có nội dung
SGK nào rời khỏi máy** — đây không phải một vụ rò bản quyền. Nó nghiêm trọng vì hai lý do khác:
một đường dẫn máy-cụ-thể đi vào lịch sử chung, và **hàng rào bị chứng minh là rỗng** — lần sau có
thể là `poc-out` (text trích xuất SGK).

**Đã làm:**
1. `git rm --cached nguon-chi-thuc`, xoá symlink khỏi worktree;
2. `.gitignore` thêm `nguon-chi-thuc` **và** `poc-out` ở dạng **không có dấu `/`**, kèm ghi chú
   nói rõ vì sao dạng cũ không đủ (`poc-out` trước đây chỉ được chặn nhờ
   `.git/info/exclude` — **cục bộ máy này**, không đi theo repo);
3. **cổng mới** `test/ci/no_source_paths_tracked_test.dart`: (a) `git ls-files` không được trả về
   đường dẫn nguồn nào, (b) `git check-ignore --no-index` phải chặn cả dạng không-thư-mục.

**Kiểm-đột-biến (cả hai đã áp, cả hai giết được cổng):** bỏ dòng `nguon-chi-thuc` khỏi
`.gitignore` ⇒ bài kiểm (b) **đỏ**; `git add -f` symlink trở lại index ⇒ bài kiểm (a) **đỏ**.

**Không rewrite lịch sử:** blob chỉ là một chuỗi đường dẫn, không có gì phải xoá khỏi quá khứ, và
rewrite một nhánh đã đẩy thì hại hơn lợi.

---

## I · SỐ ĐO

| Đo | Vòng 1 | Vòng 2 |
|---|---|---|
| Số môn nhìn thấy trên màn đầu | **1** | **6** (trên 11 môn giá sách có; số bị cắt được nói ra) |
| Bài học mở được từ Home | 1 (+1 sau khi cuộn qua khu «nghiên cứu») | **2**, cùng một hàng, cùng một loại thẻ |
| Nút **tô đặc** trên Home | 2 (việc tiếp theo + «Chụp bài tập») | **1** (có test đếm) |
| Chiều cao khối «đang học» trước nút | mega-card ~ toàn màn đầu | thẻ **186 dp** + tầng 2 gọn |
| Test | 1185 xanh · 1 skip | **1211 xanh · 1 skip** |

**Mẫu số của con số test:** cả hai đo **có fixture thật trên đĩa** (`assets/fixtures/real/*.json`
— gitignored). Không có chúng, cùng nhánh này chạy **1187 xanh · 25 skip**: 24 bài kiểm chỉ chạy
khi máy đã sinh fixture thật. Hai mẫu số, ghi rõ, không gộp.

---

## J · PLANNED vs ACTUAL

| # | PLANNED | ACTUAL | Trạng thái |
|---|---|---|---|
| 1 | §1 Home thành AI Learning Home nhiều môn, không phải landing page Bài 17 | Hai tầng; hàng 6 thẻ nhiều môn; Bài 17 là **một** thẻ trong hệ | **DONE** |
| 2 | §2 §4 hàng Smart Card trượt ngang, 75–85 % viewport + thẻ kế bên hé | `PageView` .82, `padEnds: false`; test đo tỉ lệ thật ở 360 dp; vuốt được trên máy | **DONE** |
| 3 | §3 thẻ trả lời MÔN · BÀI · TRẠNG THÁI · VIỆC TIẾP THEO | Đúng bốn; test đòi ví dụ §3 của Founder hiện nguyên chữ | **DONE** |
| 4 | §5 hai tầng, đúng một next action | Cả màn một `FilledButton`; vuốt không đổi gợi ý | **DONE** |
| 5 | §6 môn khác không bị đẩy thành «sách khác» | Khu nghiên cứu gỡ; LS&ĐL 5 là thẻ học mang dòng «Sách lớp 5 · không phải sách lớp con»; ba chuỗi cũ bị **cấm bằng tên** trong test | **DONE** |
| 6 | §7 giảm kích thước hero | Thanh bằng chứng rời hero; tầng 2 không lặp tiêu đề (D1) | **DONE** |
| 7 | §9 không fake learning state | Từ vựng khoá bằng `enum`; cấm 10 chuỗi trên cả màn; thẻ rỗng nói thẳng | **DONE** |
| 8 | ⛔ không fake dữ liệu môn chưa có | 2 thẻ thật + 4 thẻ rỗng-trung-thực với con số mục lục THẬT; thẻ rỗng không lên tầng 2 được | **DONE** |
| 9 | §12 D luật chọn một việc, giải thích được | Bậc thang 5 tầng, hàm thuần, test từng bậc; soi mã cấm động cơ thứ hai | **DONE** |
| 10 | §10 POC máy thật: thẻ đầu · vuốt thẻ 2 · bấm Next Action · quay Home · chuyển môn khác | Cả năm bước, khung `10`–`17`, hai lượt (lượt 1 tìm D1+D2, lượt 2 xác nhận) | **DONE** |
| 11 | BEFORE/AFTER cạnh nhau | `BEFORE-AFTER-home.png` | **DONE** |
| 12 | §8 khung «GẦN ĐÂY / CÓ THỂ HỌC TIẾP» | Chưa dựng khu riêng: hôm nay **không có tín hiệu «gần đây»** nào ngoài dấu vết phiên đã hiện trên chính thẻ. Dựng một khu rỗng là dựng một lời hứa | **NOT STARTED** *(§8: «Không bắt buộc pixel đúng cấu trúc này»)* |
| 13 | `CÓ THỂ LUYỆN` | Không gán ở đâu — chưa có tín hiệu luyện tập nào; có test khoá | **DEFERRED** *(thuộc `round7/v2-sam-teaching`)* |
| 14 | Thứ tự môn theo **thời khoá biểu** | Không làm. Hôm nay thứ tự thẻ rỗng chỉ theo con số giá sách. TKB là tín hiệu thật đã có trong app (`_timetable`) và **sẽ xếp môn tốt hơn** — nhưng nó là một quyết định sản phẩm, không phải một tinh chỉnh | **NOT STARTED** |
| 15 | Bản **release** APK | `--release` chết ở R8 minify trên máy này; đo bằng bản `--debug` | **BLOCKED** |

**Không mục PARTIAL nào bị nâng thành DONE.** Mục 12, 14 là NOT STARTED và nói rõ vì sao; mục 15
là BLOCKED có nguyên nhân ghi lại.

---

## K · CẦN FOUNDER QUYẾT

1. **Trần 6 thẻ.** Giá sách lớp 6 có 11 môn; hàng hiện 6 và nói ra «còn 5 môn nữa». Giữ 6, hay
   cho hàng dài hết (11 thẻ, vuốt nhiều hơn)?
2. **Thứ tự môn chưa có bài.** Hôm nay: mở-làm-được ↓ rồi mục lục ↓. Điều đó đưa **GDTC (24 mục
   lục)** lên trước **Ngữ văn (6)**. Có nên để **thời khoá biểu** quyết định thứ tự khi gia đình
   đã nhập TKB không? (mục 14 ở trên)
3. **«CÓ THỂ LUYỆN».** Nhãn Founder cho phép nhưng chưa có tín hiệu nào chứng minh. Bằng chứng
   nào đủ để bật nó — và ai (Home hay nhánh SAM teaching) sở hữu tín hiệu ấy?
4. **Máy dùng chung.** Hai agent đang đo trên cùng một Nokia. Cần một luật (khoá máy theo lượt,
   hoặc một máy thứ hai) trước vòng 3, nếu không khung máy thật của round 7 sẽ tiếp tục lẫn.

---

## L · TEST ĐÃ THÊM / ĐỔI

| Tệp | Giữ điều gì |
|---|---|
| `test/ci/no_source_paths_tracked_test.dart` (**mới, 2**) | D4: không đường dẫn nguồn SGK nào được git theo dõi (kể cả symlink) · `.gitignore` chặn cả dạng không-thư-mục. Đã kiểm-đột-biến |
| `test/features/mission/home_multi_subject_test.dart` (**mới, 23**) | Luật thẻ thuần (bảng trạng thái · thẻ rỗng không được gọi mục lục là «bài học được» · thứ tự hàng · trần thẻ · bậc thang chọn một việc · soi mã cấm động cơ thứ hai · `CÓ THỂ LUYỆN` chưa gán) · hàng trượt ngang (tỉ lệ 75–85 % ở 360 dp · vuốt sang thẻ 2 · chạm thẻ rỗng mở giá sách · nói ra số môn bị cắt) · thẻ đúng bốn câu · một `FilledButton` · vuốt không đổi gợi ý · bằng chứng thắng fixture · cấm 10 chuỗi mastery · **hai lỗi máy thật D1/D2** · **lỗi đếm mục lục GDTC** |
| `test/features/mission/home_other_subject_card_test.dart` (**đổi tên** từ `home_research_card_test.dart`) | §6: ba chuỗi Founder bác bỏ bị **cấm bằng tên**; sự thật «Sách lớp 5 · không phải sách lớp con» ở **trên chính thẻ học**; sách lớp khác **không bao giờ** thành việc hôm nay (kể cả khi đứng trước) |
| `test/features/mission/home_learning_now_test.dart` | Giữ nguyên 11 bất biến vòng 1 trên IA mới, **thêm** `1b` — nếp gấp thật của Nokia 6.1: cả hai tầng trong màn đầu |
| `home_workspace_card_test` · `home_today_area_test` · `no_machine_ids_test` · `profile_switcher_test` · `onboarding_index_test` | Chuyển sang IA hai tầng. **Đổi TIỀN ĐỀ, không nới kỳ vọng**: mỗi kỳ vọng vẫn đòi một chuỗi CỤ THỂ, chỉ đổi chỗ nó phải xuất hiện; mỗi chỗ đổi có chú thích nói vì sao |

---

## M · MÃ MỚI

| Tệp | Vai |
|---|---|
| `lib/features/mission/home_cards.dart` (**mới**) | Mô hình thẻ + luật thuần: `HomeCardState` (từ vựng khoá) · `lessonCardState` · `cardForShelfSubject` · `buildHomeCards` (thứ tự + trần) · `promotedCardIndex` (bậc thang). **Không** gọi động cơ, **không** đọc trace — có test soi mã |
| `lib/features/mission/mission_center_screen.dart` | Hai tầng; `_SmartCardRow` (`PageView` .82) + `_SmartCard` (bốn câu); tầng 2 `_oneNextActionCard`; «CÁC MÔN CỦA CON»; hàng cuối hạ xuống viền |
| `lib/features/subjects/lesson_index.dart` | `listedLessonCountFor` / `openableLessonCountFor` — hai phép đếm, hai mẫu số, ghi rõ lý do (§G) |
| `lib/main.dart` | `_lessonThreads` (mọi bài SAM xếp sẵn, kèm dấu vết phiên + việc tiếp theo từ `founderNextAction`) · `_shelfSubjects` (môn giá sách chưa có bài) |
