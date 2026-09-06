# LỆNH 51 — AUDIT: PROFILE · LỚP/MÔN/SÁCH · THỜI KHOÁ BIỂU

Ngày 2026-09-06 · nhánh `docs/order-51` · **READY FOR FOUNDER REVIEW — DO NOT MERGE**

Lệnh 51 mở đầu bằng «KHÔNG ĐƯỢC GIẢ ĐỊNH IMPLEMENTATION HIỆN TẠI ĐÃ ĐÚNG.
PHẢI AUDIT CODE + DATA + DEVICE BEHAVIOR TRƯỚC.» Tài liệu này là phần CODE +
DATA. Phần DEVICE (§15) chạy sau, khi hai nhánh Home/SAM đang bay đáp xuống.

---

## A. PROFILE ISOLATION AUDIT — **PARTIAL**

**PASS ở nơi quan trọng nhất: tầng lưu trữ.** Cách ly KHÔNG chỉ ở UI — nó nằm
trong chính phép truy vấn, và nay có regression test giữ.

| Câu hỏi §1 | Kết quả | Bằng chứng |
|---|---|---|
| Na thấy đúng sách/môn lớp 6? | PASS | `main.dart:155` nạp index theo `p.grade`; lớp 6 → 13 cuốn / 10 môn |
| Minh thấy đúng sách/môn lớp 5? | PASS | lớp 5 → 15 cuốn / 12 môn, tập hợp môn KHÁC hẳn |
| Progress của Na rò sang Minh? | **KHÔNG** | `learner_store.dart:161` `if (s.learnerId != learnerId) continue` |
| History rò? | **KHÔNG** | cùng phép lọc trên |
| Evidence rò? | **KHÔNG** | `evidenceFor(learnerId:)` |
| Next Action rò? | **KHÔNG** | sinh từ `buildMissionFromStore(profile:, store:)` |
| Home Smart Cards rò? | **KHÔNG** | thẻ sinh từ mission của đúng profile |
| Timetable rò? | **KHÔNG** | `learner_store.dart:196` lọc `r['learnerId']` |

Tại sao chưa phải PASS toàn phần: **hai khiếm khuyết ở tầng catalog/hiển thị**
(C-1, C-2). **Không cái nào là rò dữ liệu học tập.** Không có tiến độ, lịch sử,
bằng chứng hay gợi ý nào của trẻ này hiện được dưới tên trẻ khác — điều đó nay
có test giữ. Thứ hỏng là **quyền sở hữu bài theo lớp** (C-1) và **tính tất định
của nhãn hiển thị** (C-2).

**Bằng chứng mới:** `test/core/store/profile_isolation_test.dart` — 9 test,
đi qua `toJsonl → fromJsonl` (đúng đường `FileLearnerStore` chạy khi mở lại
app), ba lần restart mô phỏng theo kịch bản §4. Không dựng widget nào: §1 đòi
trace persistence, nên test hỏi thẳng kho.

---

## B. BẢNG SỞ HỮU — thứ gì thuộc về ai

| Thứ | Thuộc về | Bằng chứng | Đúng? |
|---|---|---|---|
| Grade | **Profile** | `LearnerProfile.grade`, `withGrade` | ✅ |
| Books | **Profile** (qua grade) | `indexLoader(p.grade)` | ✅ |
| Subjects | **Profile** (qua grade) | `gradeSubjects(index)` — mới | ✅ |
| Timetable | **Profile** | `store.timetable(learnerId)` | ✅ |
| Learning History | **Profile** | `sessions(learnerId:)` | ✅ |
| Progress / Student State | **Profile** | `buildMissionFromStore` | ✅ |
| Evidence | **Profile** | `evidenceFor(learnerId:)` | ✅ |
| Next Action | **Profile** | suy từ mission của profile | ✅ |
| Người học đang chọn | **Device** | `saveActiveLearner` | ✅ đúng chỗ |
| PIN bố mẹ | **Device** | `learner_store.dart:236` ghi rõ «dữ liệu của MÁY» | ✅ đúng chỗ |
| Tên sách hiển thị | **GLOBAL** ⚠️ | `subject_display.dart:59` | ❌ C-2 (nhãn, không phải dữ liệu trẻ) |
| Fixture bài học | **GLOBAL** (cố ý) | `WorkspaceCatalog.shared` | ⚠️ C-1 |

Bất biến §2 **DEVICE != USER** và **ACCOUNT != LEARNER** đứng vững: hai thứ
duy nhất ở tầng máy (người học đang chọn, PIN) đều là thứ *đúng ra* phải ở
tầng máy, và cả hai đều được `_belongsTo()` cố ý loại khỏi xuất/xoá dữ liệu
trẻ (`learner_store.dart:239`).

---

## C. HARDCODED — phân loại theo §2

### C-1. `researchSlotKeys` — **BUG (product integrity)**, không phải fixture

`workspace_catalog.dart:53` ghim bài LS&ĐL **lớp 5** làm «lát cắt nghiên cứu»,
và `main.dart:133` cho nó hiện với **MỌI lớp**, kèm lời trong
`mission_center_screen.dart:52`:

> «Đây không phải bài của lớp con — SAM đang tập đọc thử một cuốn sách khác.»

Hệ quả khi dựng đúng hai hồ sơ §4:

| | Na — Lớp 6 | Minh — Lớp 5 |
|---|---|---|
| Bài KHTN 6 B17 | ✅ của em | — |
| Bài LS&ĐL 5 B8 | thấy, kèm lời xin lỗi «không phải bài của con» | **KHÔNG có bài nào** |

**Đảo ngược hoàn toàn.** Bài lớp 5 duy nhất đang tồn tại thì trẻ lớp 5 không
được nhận, còn trẻ lớp 6 nhận kèm lời xin lỗi. `_workspaceLessonFor` lọc
`d.grade == p.grade` ĐÚNG (`main.dart:120`), nhưng lại loại chính bài ấy bằng
`!isResearchSlot(d)` — nên Minh rơi vào rỗng.

Đây không phải lỗi ẩn: `workspace_catalog.dart:50` tự khai là «quyết định hiển
thị tạm cho vòng kiểm chứng, không phải luật sản phẩm — Founder chốt cách xử
lí khác lớp sau». **Lệnh 51 chính là lúc chốt.** Đề xuất: bỏ khái niệm
research slot, để bài thuộc về lớp của nó; Minh (lớp 5) nhận LS&ĐL 5 Bài 8 như
bài của mình, Na (lớp 6) không thấy nó nữa. Việc này cũng đóng luôn §6 của
lệnh 50 (cấm hạ các môn khác xuống hạng «sách khác»).

### C-2. `knownBookTitles` — **BUG (hiển thị phụ thuộc thứ tự mở hồ sơ)**

*Đã tự đính chính: bản đầu của tài liệu này gọi C-2 là «rò nhãn giữa hồ sơ».
Tái dẫn cho thấy nhãn ấy quá nặng.* Map chứa `mã sách → tên sách` — metadata
catalog công khai, **không phải dữ liệu của trẻ**. Nó không làm trẻ này thấy
thứ gì thuộc về trẻ kia.

Khiếm khuyết thật nằm chỗ khác và vẫn có thật: `subject_display.dart:59` là
`Map` toàn cục, `main.dart:155` `addAll` tên sách của lớp đang mở, và **không
ai xoá khi đổi hồ sơ**. «Kho khám phá» lại đọc từ `sam-stories.db` — kho của
TOÀN corpus, không lọc theo lớp. Nên cùng một mẩu truyện, dưới hồ sơ Minh:

- mở Na trước rồi đổi sang Minh → «Nguồn: **SGK Ngữ văn 6** · trang PDF 26»
- mở thẳng Minh                → «Nguồn: **06-sgk-ngu-van-6-tap-mot** · trang PDF 26»

Cùng màn hình, cùng hồ sơ, hai kết quả khác nhau tuỳ **thứ tự mở hồ sơ trong
phiên**. Đó là lỗi tất định, và nó làm mọi phép tái hiện trên máy thật không
đáng tin. Sửa: xoá map khi đổi hồ sơ (đã làm).

Câu hỏi lớn hơn — «Kho khám phá» có nên đưa sách lớp 6 cho học sinh lớp 5 hay
không — nằm ngoài lệnh 51, ghi lại để không mất.

### C-3. `khtn6_bai17.dart`, `WorkspaceCatalog.defaultSlots` — **GOLDEN FIXTURE** ✅

Khai báo rõ, registry là hằng đóng (`semantic_binding.dart:20`: «hôm nay ĐÚNG
MỘT binding»). Đúng như lệnh 49/50 chốt Bài 17 là Golden Lesson. Không sửa.

### C-4. `buildDemoDomain` (mastery Toán lớp 5 dựng tay) — **UI DEMO** ✅ *có bẫy*

`mission_center_screen.dart:775` mở màn «Bố mẹ» từ dữ liệu demo — nhưng CHỈ khi
`onParentArea == null`. Production truyền nó (`main.dart:543`), và
`parent_area.dart:326` dùng `profile` + dữ liệu THẬT. **Không tới tay người
dùng thật.** Bẫy còn lại: nếu ai đó quên truyền `onParentArea`, phụ huynh sẽ
đọc mastery bịa mà không có nhãn nào báo. Đề xuất: bỏ nhánh fallback, để test
tự dựng.

### C-5. `grade: 5` / `grade: 6` trong `blueprint_catalogue_v0`, `source_misconception`, `prerequisite_edges`, `slice_curriculum` — **PRODUCTION PATH, hợp lệ** ✅

Đây là **nội dung chương trình gắn theo lớp** (một hiểu lầm thuộc về một lớp),
không phải giả định về người học. Không phải hardcode learner.

---

## D. KIẾN TRÚC THỜI KHOÁ BIỂU — **EXISTS**, không phải MISSING

Lệnh 51 §5 nói «Round 7 hiện chưa thể hiện rõ concept Thời khóa biểu» — đúng,
nhưng nguyên nhân là **chôn**, không phải **thiếu**:

| Tầng | Trạng thái | Ở đâu |
|---|---|---|
| Model | ✅ có | `core/store/timetable.dart` (WAL-96) |
| Lưu trữ theo learner | ✅ có | `learner_store.dart:186–204` |
| Màn nhập tay | ✅ có | `features/timetable/timetable_screen.dart` (WAL-137) |
| Tham gia gợi ý | ✅ có | `prioritiseByTimetable` — CHỈ xếp lại |
| Sinh tự động | ❌ **thiếu** → **nay có** | `timetable_generator.dart` (mới) |
| Hiện trên Home | ❌ **thiếu** | §12 — việc tiếp theo |
| Tìm thấy được | ❌ **chôn trong Settings** | `settings_screen.dart:112` |

**Bất biến F4 đã có sẵn trong code từ trước và trùng khớp §14 của lệnh 51:**
«MÔN TRONG TKB ≠ BÀI HỌC CỤ THỂ… TKB chỉ được làm MỘT việc: xếp lại thứ tự các
hành động học đã HỢP LỆ» (`timetable.dart:6–14`). Màn nhập **cố ý không có ô
«bài»**. Không cần thêm luật mới — chỉ cần không phá luật cũ.

---

## E. CONCEPT TIMETABLE CŨ TÌM THẤY (§6 — research trước khi thiết kế)

| Nguồn | Nói gì |
|---|---|
| `SAM-PRODUCT-EXPERIENCE-REVIEW.md:508` | «04 Timetable — Giữ, **hạ ưu tiên**. Rất giá trị (sinh ra ý định «mai có tiết») nhưng **tuỳ chọn**, nhập sau.» |
| `…REVIEW.md:350` | Không có TKB ⇒ SAM **không đoán**, hỏi thẳng «Con muốn bắt đầu thế nào?» |
| `…REVIEW.md:19` | Luồng thiết lập gốc: vai → hồ sơ → chọn môn → **thời khoá biểu** |
| `SAM-PRODUCT-EXPERIENCE-CONVERGENCE.md:143` | TKB **chỉ phá hoà**, không thắng; `rest` là output hạng nhất |
| `…CONVERGENCE.md:359` | Thứ tự mỏ neo: bằng chứng → **TKB (mai có tiết) → chuẩn bị** |
| `SAM-MEMORY-RETENTION-ENGINE.md:34` | `prioritiseByTimetable` — CHỈ xếp lại, «đã enforce bằng API, test giữ» |
| `…REVIEW.md:620` | Câu hỏi mở: TKB trống thì lấy gì làm mỏ neo? Đề xuất: **không đoán, hỏi thẳng** |

Concept cũ **nhất quán và đã đúng**. Tôi không thiết kế lại — chỉ bổ sung phần
nó chưa có (sinh tự động) và đưa nó lên Home.

---

## F. LỚP → MÔN → SÁCH (§7) — giải từ catalog THẬT

`features/subjects/grade_subjects.dart` (mới). Nguồn: `assets/pack/lesson-index-g{N}.json`
— cùng pack Kho sách đang đọc. **Không có bảng môn viết tay nào.**

| | Cuốn | Môn | Môn |
|---|---|---|---|
| **Lớp 5** (Minh) | 15 | **12** | Toán · Tiếng Việt · Khoa học · LS&ĐL · Tiếng Anh · Tin học · Công nghệ · Đạo đức · Âm nhạc · GDTC · HĐTN · Tiếng Hàn |
| **Lớp 6** (Na) | 13 | **10** | Toán · Ngữ văn · KHTN · Tiếng Anh · Tin học · Công nghệ · Mĩ thuật · Âm nhạc · GDTC · HĐTN-HN |

§8 **BOOK → SUBJECT**: pack đã tách sẵn `subject` khỏi `volume`/`volumeLabel`,
nên «Toán 5 Tập 1» + «Toán 5 Tập 2» gom về MỘT môn «Toán». Test khoá điều này
trên pack thật (`grade_subjects_test.dart`), gồm cả «không tên môn nào mang
nhãn Tập».

Kỳ vọng §15 «Subject/book set khác» **đạt bằng dữ liệu thật**, không dàn dựng.

---

## G. SINH THỜI KHOÁ BIỂU CÓ RÀNG BUỘC (§9) — POC xong

`core/store/timetable_generator.dart` · `generateTimetable(learnerId:, subjects:, seed:, daysPerWeek:, slotsPerDay:)`

12 test giữ: cùng seed ⇒ từng tiết giống nhau; seed khác ⇒ khác; mỗi môn có ít
nhất một tiết; không môn nào trùng trong một ngày khi còn tránh được; không bịa
môn ngoài lớp; `TimetableEntry` **không có chỗ nào** để nhét bài/tiến độ/bằng
chứng vào (§14 giữ bằng KIỂU, không bằng lời hứa).

### ⭐ §10 — HEURISTIC TẦN SUẤT BỊ CHÍNH DỮ LIỆU BÁC BỎ

Lệnh yêu cầu tìm tần suất THẬT trước. Trong repo **không có** trường số
tiết/tuần. Tín hiệu duy nhất mang hình dạng tần suất là `lessonCount`. Tôi đo
thử — và nó tự bác bỏ:

```
Lớp 6:  KHTN 55 bài · Toán 43 · GDTC 24 · Tin học 17 · … · Ngữ văn 6
```

**Ngữ văn 6 có hai tập mà chỉ 6 bài bắt được.** Con số ấy đo **độ phủ OCR/gắn
bài**, không đo tuần học của trẻ. Lấy nó làm trọng số sẽ sinh ra thời khoá biểu
nói rằng con học GDTC nhiều hơn Ngữ văn — sai với thực tế, và sai theo kiểu trẻ
không có cách nào kiểm chứng.

**Quyết định: mặc định CHIA ĐỀU.** Trọng số chỉ tồn tại khi con người khai ra
(`subjectWeights`) — nghĩa là nguồn của nó luôn là người, không bao giờ là suy
đoán của máy. Ghi thẳng trong đầu tệp, kèm số đo.

Nhãn bắt buộc: `suggestedTimetableLabel = 'Thời khoá biểu gợi ý'`. Không chỗ
nào trong lớp này được nói đây là chương trình Bộ GD&ĐT.

---

## H. §13 — ONE NEXT ACTION CÓ LÝ DO — **EXISTS**

`reason` là trường hạng nhất suốt cả chuỗi: `lesson_next_action.dart:115` →
`learning_agenda.dart:141` → `MissionData.reason:47`, và
`mission_data.dart:30` ghi rõ «UI KHÔNG tự suy từ một câu sai: nó hiển thị
`reason` mà resolver đưa». Không cần dựng mới.

Việc còn thiếu: khi TKB góp phần vào gợi ý, `reason` phải NÓI RA điều đó
(«hôm nay có tiết KHTN»), thay vì đưa ra một câu không truy nguyên được. Thuộc
phần tích hợp Home (§12).

---

## §8 UX — [A] TẠO TỰ ĐỘNG / [B] TỰ SẮP / [C] BỎ QUA — **XONG**

Màn TKB nay có thẻ «THỜI KHOÁ BIỂU GỢI Ý» với:

- **[A]** «Tạo tự động» — sinh từ môn thật của lớp, ghi **mã** môn
- **[B]** chip thêm/xoá từng tiết như cũ · «Tạo lại» đổi phương án (§11)
- **[C]** không bấm gì cả — rỗng vẫn là trạng thái hợp lệ (F13 giữ nguyên)
- «Xoá hết» có hỏi lại, và nói rõ **không đụng tới những gì con đã học**

Lời trên màn, đúng chỗ phụ huynh đọc:

> «Đây là GỢI Ý để sửa cho nhanh — không phải thời khoá biểu chuẩn của trường
> hay của Bộ GD&ĐT.»

9 test giữ màn này, trong đó có: nhãn §10 phải còn, sinh ra phải là **mã** môn
(bẫy WAL-176), và **tạo TKB không tạo phiên học nào** (§14).

---

## CÒN LẠI

| Mục | Trạng thái |
|---|---|
| A. Profile isolation audit | ✅ **PARTIAL** — có test giữ |
| B. Bảng sở hữu | ✅ |
| C. Hardcoded findings | ✅ (C-1 chờ Founder chốt) |
| D. Kiến trúc TKB | ✅ EXISTS |
| E. Concept TKB cũ | ✅ |
| F. Lớp→Môn→Sách | ✅ |
| G. Sinh TKB có ràng buộc | ✅ |
| Sửa C-2 (tất định nhãn) | ✅ |
| §8/§11 UX tạo & sửa TKB | ✅ |
| §13 one next action + reason | ✅ EXISTS (thiếu quy nguồn TKB) |
| H. Multi-profile device test (§15) | ⏳ chờ Home/SAM đáp |
| I. Home + TKB integration (§12) | ⏳ nhánh `round7/multi-subject-home` |
| J. BEFORE/AFTER screenshots | ⏳ |
| K. Founder Acceptance Card | ⏳ |
| Sửa C-1 (đảo lớp) | ⛔ **CHỜ FOUNDER CHỐT** |

Toàn bộ suite: **1192 pass · 1 skip · 0 fail**.

---

## MỘT ĐIỂM CẦN FOUNDER CHỐT (C-1)

Bỏ khái niệm «lát cắt nghiên cứu» để bài LS&ĐL 5 thuộc về học sinh **lớp 5**,
đồng nghĩa Na (lớp 6) **không còn thấy nó**. Đó là mất một thẻ trên Home của
máy demo — nhưng là cách duy nhất để Minh có bài thật, và để bỏ được câu «đây
không phải bài của lớp con» mà lệnh 50 §6 đã gạch.
