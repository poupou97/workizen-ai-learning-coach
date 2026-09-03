# SAM Learning Experience Factory — Living Research

**Đây không phải báo cáo tiến độ.** Đây là hồ sơ nghiên cứu/thiết kế SỐNG, viết trong lúc
làm, để Founder và kiến trúc đánh giá cách SAM **công nghiệp hoá** trải nghiệm học.

Mọi con số trong file này đều **đo được** và ghi kèm đường dẫn/lệnh đo. Không có số nào
là mục tiêu đẹp đặt trước.

Cập nhật lần cuối: 2026-09-03 · nhánh `main` sau WAL-170.

---

## 1. Câu hỏi lõi

> Làm sao SAM tạo được trải nghiệm học **đúng môn, đủ chất lượng** cho toàn bộ corpus K–12
> mà **không thiết kế tay từng bài**?

Bài toán KHÔNG được phép giải theo lối: **7.626 bài → 7.626 thiết kế UI tay.**

Hướng nghiên cứu:

```
SGK / SGV
  → pedagogical intent (có provenance)
  → LearningExperienceBlueprint
  → Experience Pattern
  → hợp thành Surface dùng lại được
  → Learning Experience dựng ra
  → QA
  → LearningEvidence
```

Tiêu chí thành công một câu: **thêm bài phải chủ yếu là thêm DỮ LIỆU, không phải thêm Dart
theo từng bài.**

---

## 2. Baseline đo được (2026-09-03)

Đây là vạch xuất phát. Chưa đặt mục tiêu số nào cho tới khi có baseline này.

### 2.1 Corpus

| Chỉ số | Giá trị | Nguồn |
|---|---|---|
| Bản ghi bài toàn corpus | 7.626 | `poc-out/graph/curriculum-structure.json` |
| Bài có `title` | 2.219 (29%) | như trên |
| Bài có `pageStart` | 5.593 (73%) | như trên |
| `structureStatus` OK / OK_ALT | 169 tài liệu | như trên |
| `structureStatus` PARTIAL | 237 tài liệu | như trên |
| `structureStatus` NO_TOC | 125 tài liệu | như trên |
| Khoá (sách, số, trang) DUY NHẤT | 6.856/7.626 (89%) | đo trực tiếp |
| **Mục lục DÙNG ĐƯỢC NGAY** | **122/531 cuốn (22%)** | `tool/corpus/toc_health.py` |

### 2.1b Sức khoẻ mục lục toàn corpus — `tool/corpus/toc_health.py`

Chặng **validation tự động** của nhà máy: chấm từng cuốn, phân loại kiểu hỏng, rồi mới
nhắm việc sửa. Không sửa mò từng cuốn. Một cuốn có thể mang nhiều cờ.

| Cờ | Số cuốn | Nghĩa |
|---|---|---|
| `DUP_NUMBERS` | 147 (27%) | số bài trùng trong cùng cuốn |
| `HEAD_UNCOVERED` | 135 (25%) | mục lục bắt đầu quá muộn ⇒ **nửa đầu sách không bài nào phủ** |
| `NO_TOC` | 125 (23%) | không bắt được mục lục |
| `OK` | **122 (22%)** | **dùng được ngay** |
| `NON_MONOTONIC` | 119 (22%) | số bài tăng mà trang không tăng ⇒ xương sống gãy |
| `PARTIAL_COVERAGE` | 118 (22%) | mục lục phủ dưới 40% số trang cuốn sách |
| `NO_PAGES` | 13 (2%) | có bài, không trang nào |

`05-sgk-khoa-hoc-5` (ca C-008): `xươngSống=0.5 · phủ=0.39 · hởĐầu=0.56` — **56% đầu cuốn
sách không có bài nào phủ**, đúng chỗ 5 thí nghiệm nằm (trang in 5–56). Đây là lý do đo
được, không phải phỏng đoán.

**Ý nghĩa**: 78% số cuốn cần sửa mục lục trước khi hoạt động gắn được vào bài. Đây là việc
của **ingestion**, không phải của runtime — và nó chặn cổng kiến trúc (C-008).

### 2.2 Pack lớp 5 (bản đang chạy trên máy thật)

| Chỉ số | Giá trị |
|---|---|
| Tổng bài | 251 |
| Bài có bài tập Toán | 4 bài (15 bài tập) |
| Đoạn đọc-hiểu Tiếng Việt | 68 |
| Đề viết Tiếng Việt | 57 |
| Tư liệu gốc Sử/Địa | 2 |
| Thí nghiệm Khoa học | 5 |
| Hình SGK đã cắt | 3 |
| Bài có **chương trình sư phạm** (`SliceCurriculum`) | **1** |

### 2.3 Chỉ số nhà máy (theo dõi dần, chưa đặt target)

| Chỉ số | Hôm nay | Ghi chú |
|---|---|---|
| % bài ánh xạ được tới một Experience Pattern | chưa đo | registry mới ở mức EXPERIMENTAL |
| % bài không cần Dart riêng | 100% *trong phạm vi đang có* | sau WAL-166/168, xem §5 |
| Số bài cần ngoại lệ | 0 | chưa có ngoại lệ nào được ghi |
| Blueprint đã có | 8 (`blueprint_catalogue_v0.dart`) | **0 blueprint được runtime dùng** |
| Surface có mã, được gọi | `resolveSurface` **0 caller** | trôi kiến trúc, xem §6 |

---

## 3. Phân loại giả thuyết (CHƯA phải sự thật)

```
Learning Family → Experience Pattern → Surface Composition → Lesson Data/Assets
```

Danh sách family dưới đây là **giả thuyết**, corpus + SGV + lần triển khai thật được phép
**GỘP / TÁCH / THÊM / BỎ / ĐỔI TÊN**:

Problem Solving · Reading & Evidence · Inquiry & Investigation · Spatial & Data ·
Language & Communication · Creation & Performance · Scenario & Reflection.

**Phân cấp KHÔNG được đóng cứng một kiểu.** Corpus đã bác bỏ cả «số bài là định danh» lẫn
«mọi sách cùng một cây»:

| Sách | Cây thật đo được |
|---|---|
| Tiếng Việt | Sách → **Tuần** → Bài → *Đọc / Nói và nghe / Viết* |
| GDTC | Sách → **Chủ đề** → Bài (số bài **đánh lại** mỗi chủ đề) |
| Khoa học | Sách → **Chủ đề** → Bài |
| Tiếng Anh | Sách → **Unit** |

⇒ mô hình cần là `ContentNode` mang **vai trò ngữ nghĩa** (`UNIT` · `THEME` · `WEEK` ·
`CHAPTER` · `TOPIC` · `LESSON` · `ACTIVITY`…), tên vai trò còn đổi được theo bằng chứng.
**Định danh bền = vị trí trong cây + provenance nguồn**, không phải số bài hiển thị.

**Bốn thứ KHÔNG được đánh đồng:**

- **Subject** (môn) — nhãn hành chính của sách.
- **Lesson** (bài) — một mục có định danh trong một cuốn.
- **Pattern** (mẫu trải nghiệm) — hình dạng sư phạm; một môn có nhiều pattern, một pattern
  dùng cho nhiều môn.
- **Surface** (mặt tương tác) — **primitive tương tác, KHÔNG phải sư phạm.**

---

## 4. Experience Pattern Registry

> ⚠️ **BÀI ≠ MỘT TRẢI NGHIỆM NGUYÊN TỬ.** Mục lục Tiếng Việt liệt kê *Đọc* / *Nói và nghe* /
> *Viết* **bên trong cùng một bài** — sách tự nói rằng một bài gồm nhiều hoạt động sư phạm
> khác nhau. Nên giả thuyết làm việc là
> `Bài → ActivityBlueprint[] → Experience Pattern → Surface Composition`,
> và **chọn pattern ở mức HOẠT ĐỘNG**, không ép cả bài vào một pattern. EP-002 (đọc) và
> EP-005 (viết) rất có thể là hai hoạt động của **cùng một bài** Tiếng Việt, không phải hai
> bài khác nhau.


Giữ **bộ pattern nhỏ nhất giải thích được sự đa dạng thật**, không đẻ hàng trăm pattern sớm.

Độ tin: `EXPERIMENTAL` → `PROVISIONAL` → `VALIDATED`.

### EP-001 · Luyện có thang hỗ trợ (Worked Practice with Support Ladder)

| Trường | Nội dung |
|---|---|
| Family | Problem Solving |
| Môn áp dụng | Toán (đã chạy); giả thuyết: Vật lí, Hoá — **chưa kiểm** |
| Lớp | đã chạy lớp 5 |
| Ý đồ sư phạm | trẻ **tự thử trước**, hỗ trợ leo từng nấc, lời giải trọn chỉ sau khi đã thử |
| Chuỗi điển hình | activate → discover → practice → apply → consolidate |
| Surface bắt buộc | thẻ đề · ô nhập đáp án · thang gợi ý · thẻ provenance |
| Nội dung cần | biểu thức + ca (skill case) + phương pháp có nguồn + **mẫu lời dạy 3 nấc** |
| Bằng chứng sinh ra | `independentAttempt`, `hintRequested`, `postHintSuccess`, `finalCorrectness` |
| Hành vi hỗ trợ | REVEAL gate — `fullSolution` khoá cho tới khi có ≥1 lần tự thử |
| Nguồn | `05-sgv-toan-5` p36 → `blueprintQuyDongB6` |
| Gold lesson | Toán 5 · Bài 6 · trang 20 |
| Thất bại đã biết | lời dạy từng viết tay trong Dart (SF-1, đã sửa WAL-168) |
| Độ tin | **PROVISIONAL** — chạy thật trên máy, nhưng mới **một** bài |

### EP-002 · Đọc rồi trả lời MỞ (Read & Answer Openly)

| Trường | Nội dung |
|---|---|
| Family | Reading & Evidence |
| Môn | Tiếng Việt (68 đoạn trong pack lớp 5) |
| Ý đồ | hiểu văn bản; câu trả lời **không có đáp án in trong sách** |
| Surface | thẻ đoạn văn (verbatim) · câu hỏi mở · ô trả lời tự do |
| Ràng buộc cứng | **SGK không in đáp án ⇒ cấu trúc dữ liệu cố ý KHÔNG có trường đáp án.** Tầng UI *không thể* chấm dù muốn. `correct: null` — **UNKNOWN ≠ SAI** |
| Bằng chứng | một `attempt` với `correct == null` |
| Nguồn | `lib/features/subjects/lesson_index.dart` `TvQuestion` |
| Độ tin | **PROVISIONAL** |

### EP-003 · Dự đoán → Làm → Quan sát (Predict–Observe–Explain)

| Trường | Nội dung |
|---|---|
| Family | Inquiry & Investigation |
| Môn | Khoa học (5 thí nghiệm trong pack lớp 5) |
| Ý đồ | trẻ **dự đoán trước khi thấy kết quả** |
| Surface | thẻ chuẩn bị · các bước · **cổng dự đoán** · ô quan sát |
| Ràng buộc | có câu «Dự đoán…» in trong sách ⇒ surface **bắt buộc** gate dự đoán trước khi lộ bước sau |
| Nguồn | `KhoaExperiment` (Chuẩn bị/Tiến hành verbatim) |
| Thất bại đã biết | LIMITATION v0: demo TRƯỚC khi trẻ quan sát ⇒ `LEARNER_FIRST_VIOLATED` (đã có test) |
| Độ tin | **EXPERIMENTAL** — có dữ liệu, **chưa** chạy hết luồng trên máy thật |

### EP-004 · Tra hỏi tư liệu gốc (Source Interrogation)

| Trường | Nội dung |
|---|---|
| Family | Reading & Evidence |
| Môn | Lịch sử & Địa lí (2 tư liệu trong pack lớp 5) |
| Ý đồ | đọc tư liệu gốc, phân biệt **lời nguồn** với **lời SAM** |
| Surface | khối trích verbatim + attribution · gloss của SAM **dán nhãn riêng** |
| Ràng buộc cứng | thiếu attribution ⇒ **loại thẳng ở tầng parse**; không bao giờ trình bày gloss như lời nguồn |
| Độ tin | **EXPERIMENTAL** |

### EP-005 · Viết theo đề, có checklist (Compose with Checklist)

| Trường | Nội dung |
|---|---|
| Family | Language & Communication |
| Môn | Tiếng Việt (57 đề viết) |
| Ràng buộc cứng | dữ liệu **chỉ có đề, không trường nào chứa bài mẫu** ⇒ REVEAL gate đúng theo cấu trúc |
| Độ tin | **EXPERIMENTAL** |

### EP-006 · Đọc hình trong sách (Read the Printed Figure)

| Trường | Nội dung |
|---|---|
| Family | Spatial & Data |
| Surface | ảnh cắt từ SGK + provenance (trang PDF, bbox, phiên bản trích) |
| Ràng buộc cứng | `printedCaption` = **chỉ** chữ in thật; `samGloss` = phần SAM thêm, **nhãn riêng**. Thiếu provenance ⇒ không được nói «hình trong sách» |
| Độ tin | **EXPERIMENTAL** — 3 hình |

---

## 5. Ca thật đã học được (research through implementation)

Chỉ ghi ca **tạo pattern mới / bác bỏ pattern cũ / lộ primitive thiếu / lộ luật compiler /
lộ trừu tượng sai**.

### C-001 · Toán 5 Bài 6 — lời dạy từng là MÃ

- **Nguồn**: `05-sgk-toan-5-tap-mot` Bài 6 tr.20 · SGV `05-sgv-toan-5` p36
- **Pattern**: EP-001 · **Surface**: thẻ đề, thang gợi ý, thẻ provenance
- **Primitive đã có mà chạy được**: `TutorScope`, `EvidenceLog`, `explainTeaching`
- **Primitive THIẾU**: mẫu lời dạy dạng dữ liệu
- **SCALABILITY FAILURE (SF-1)**: `hintTextFor` là `switch` theo `method.id`, nội suy số học
  phân số trong Dart. Mỗi phương pháp mới = một hàm prose mới → ở 531 cuốn là **hàng nghìn hàm**.
- **Thiếu cái gì**: *data* (mẫu câu) + *abstraction* (slot)
- **Đã sửa**: WAL-168 — `MethodHints` trên `TeachingMethod`, `SolvableProblem.slots`. Chữ
  không đổi một dấu, chỉ đổi chỗ ở.
- **Còn Dart riêng theo bài?** Không.

### C-002 · Mở bài mà phải hỏi tên môn

- **SCALABILITY FAILURE (SF-2)**: `subject_home_screen` quyết định bài mở được hay không bằng
  `_isToan/_isTv/_isSu`. Đo trên pack: Khoa học (5 thí nghiệm) và Tiếng Anh (môn lớn nhất) **không
  có đường vào** dù dữ liệu có sẵn.
- **Thiếu cái gì**: *abstraction* — câu hỏi sai. Phải hỏi «bài này có VIỆC gì», không hỏi «môn tên gì».
- **Đã sửa**: WAL-166 — `sealed LessonActivity` + `activitiesFor`. `sealed` ⇒ thêm loại việc mới mà
  quên nối UI thì **không biên dịch được**, thay vì im lặng biến mất.
- **Luật rút ra**: *khả năng mở một bài là thuộc tính của DỮ LIỆU, không phải của tên môn.*

### C-003 · Phân loại ca nằm trong màn dùng chung

- **SCALABILITY FAILURE (SF-3)**: `ProblemContextScreen` tự gọi `FractionProblem.parse` →
  `fractionCase`. Môn nào không viết được thành `a/b ± c/d` ⇒ không có ca ⇒ TutorScope rỗng ⇒
  **không dạy được gì**.
- **Thiếu cái gì**: *adapter* theo **họ môn**, đặt trong dòng dữ liệu của bài.
- **Đã sửa**: WAL-168 — `SliceCurriculum.classifyCase`. Test cổng dựng một môn **không phải Toán**
  và đòi màn dùng chung dạy được nó.
- **Luật rút ra**: *runtime không được biết môn; môn nằm trong dữ liệu của bài.*

### C-004 · Định danh bài KHÔNG được dựa vào số bài

- **Bằng chứng**: GDTC lớp 5 có **5 bài mang số 1** (tr.8, 24, 37, 53, 65) — sách đánh số lại theo
  từng chủ đề. Corpus mang `unitKind` ∈ {`bai` 243, `tuan` 175, `chuDe` 9}: **nghĩa của con số đổi
  theo họ sách**. Tiếng Anh Global Success đánh số theo **Unit** (tập một: 2,3,4,5,8,9,10).
- **SCALABILITY FAILURE (SF-4)**: `curriculumFor(profile)` tra theo **LỚP** (`if (p.grade != 5)`),
  nghĩa là **mọi** bài của trẻ lớp 5 nhận provenance của Toán 5 Bài 6 — «Nguồn bài học» của một bài
  Khoa học sẽ trưng ra trang 21 SGK Toán. **Nói dối về nguồn.**
- **Đã sửa**: WAL-170 — `LessonKey(sách, số, trang in)`, tra khớp chính xác, không khớp ⇒ `null`.
  Bài chụp được giải bằng **classifier**: đúng một dòng nhận ra đề thì dùng, không ai nhận **hoặc
  nhiều hơn một** đều fail closed.
- **Luật compiler rút ra**: *compiler phải phát định danh tường minh cho mỗi bài; số bài chỉ là
  metadata hiển thị.* Khoá (sách, số, trang) duy nhất ở **89%** — 11% còn lại cần chiều định danh
  bổ sung (thứ tự trong chủ đề, hoặc anchor văn bản).

### C-005 · Bìa sách có trên đĩa ≠ có trong bản build

- **Pattern**: không tạo pattern học tập mới; đây là **luật đóng gói asset**.
- Khai báo asset của Flutter **không đệ quy**; thư mục asset bị gitignore phải có file mốc,
  nếu không `flutter analyze` đỏ trên mọi bản checkout sạch.
- **Ý nghĩa cho nhà máy**: pipeline sinh asset (bìa, hình cắt) phải có **kiểm tra đóng gói tự động**,
  vì lỗi kiểu này **im lặng** — màn hình rơi vào nhánh dự phòng chứ không crash.

### C-006 · Tiếng Anh — khoảng trống INGESTION theo họ nội dung

- **Đo**: cả hai cuốn SGK Tiếng Anh lớp 5 có **100% bản ghi thiếu trang**, và thiếu cả unit
  (tập một có 2,3,4,5,8,9,10 — mất 1,6,7; tập hai chỉ 11–15). Nhưng **SGV cùng bộ** thì
  `structureStatus=OK` với **đủ 20 unit kèm trang** (18, 33, 46, 61, …).
- **Kết luận**: không phải «thiếu nội dung» mà là **TOC miner không đọc được layout SGK Tiếng Anh**.
  Có nguồn sửa sẵn trong corpus (SGV cùng bộ).
- **Việc cần**: sửa **ingestion theo họ nội dung**, KHÔNG xoá bản ghi, KHÔNG bịa nội dung.
- **Cảnh báo**: 53/251 bản ghi rỗng ở lớp 5 **đều** là bản ghi thiếu trang — một nguyên nhân duy
  nhất, không phải hai.

### C-007 · ⚠️ BÁC BỎ — «SGV findings → blueprint theo từng bài» KHÔNG chạy trên dữ liệu hôm nay

Đây là giả thuyết nền của Blueprint Compiler. Đo xong thì **sai**.

**Cái đang có (thật, dùng được):** 13.634 finding sư phạm trích từ **18 cuốn SGV**
(`poc-out/pedagogy/findings/`), mỗi finding mang `field`, `page`, `headline`, `authority`,
`extractionMethod`. Trường hay gặp nhất: `perExerciseGuide` 2.227 · `intent` 1.931 ·
`teacherNote` 924 · `objective` 708 · `procedure` 590. Đây là **cấu trúc sư phạm có toạ độ**.

**Ba thứ bị bác bỏ:**

1. **Finding KHÔNG chứa lời dạy.** 0/13.634 finding có trường văn bản dài quá 200 ký tự —
   chỉ có `headline` + toạ độ. ⇒ **Compiler không thể sinh lời dạy.** Mọi câu hướng dẫn
   sinh ra từ đây sẽ là **bịa**. Đây chính là ranh giới Founder yêu cầu: đủ bằng chứng cho
   *cấu trúc*, không đủ cho *lời*.

2. **Trường `lesson` của finding không tin được.** Ở `04-sgv-khoa-hoc-4`, «Bài 31» ôm 285
   finding trải từ trang 15 đến 152 — cả cuốn sách, không phải một bài. Đo toàn bộ:
   **15/15 tài liệu** có ít nhất một «bài» trải hơn 40 trang. Nhưng **median spread chỉ 2–6
   trang** ở nhiều cuốn ⇒ chẩn đoán chính xác là **thùng chứa gom**: khi bắt tiêu đề bài
   thất bại, finding rơi vào bài đọc được gần nhất.

3. **Không sửa được bằng cách lấy TOC của SGV làm khung.** Bản thân TOC của SGV tự mâu
   thuẫn: **10/18 cuốn** có số bài trùng và/hoặc thứ tự trang không đơn điệu theo số bài
   (`04-sgv-khoa-hoc-4`: 37 bài khai, 28 có trang, 5 số trùng, thứ tự sai). Luật lọc
   «giữ finding có trang nằm trong khoảng trang của bài» giữ lại **0/350** — vì cả hai vế
   đều hỏng, không phải vì luật sai.

**Luật compiler rút ra:**
- Đơn vị bám của bằng chứng SGV là **TRANG**, không phải số bài. Trang là toạ độ đo được;
  số bài là suy diễn của miner.
- Cần một bước **căn trang → bài** cho SGV trước khi có blueprint theo bài. Chừng nào chưa
  có, finding SGV chỉ đỡ được claim **mức sách** hoặc **mức trang**.
- `authority` hiện **chỉ có một giá trị** `SOURCE_EXPLICIT` cho cả 13.634 finding. Một
  trường phân loại chỉ có một giá trị thì **không phân loại gì cả**. Compiler phải **tự suy
  ra** `SOURCE_DEMONSTRATED` / `INFERRED` / `UNKNOWN`, không được thừa kế.

**Ý nghĩa với cổng kiến trúc:** không chặn. Cổng cần một dòng chương trình cho môn thứ hai;
dòng đó dựng được từ **hoạt động phía SGK** (thí nghiệm, đọc, tư liệu) với method **có
provenance nhưng KHÔNG có lời dạy** ⇒ SAM im lặng ở phần gợi ý (bất biến WAL-168), trẻ vẫn
làm được việc và vẫn sinh bằng chứng. Thà im còn hơn bịa.

### C-008 · ⚠️ Cổng kiến trúc bị chặn — nhưng KHÔNG phải vì Dart

Cổng đòi: **môn thứ hai + lớp thứ hai** chạy Book → Lesson → Learn → Evidence mà không thêm
Dart theo bài. Đo xong: **không qua được hôm nay**, và lý do đáng giá hơn cả cái cổng.

**Không phải vì thiếu mã.** Sau WAL-166/168/170 runtime đã trung tính: `activitiesFor` hỏi
dữ liệu chứ không hỏi tên môn, `classifyCase` nằm trong dòng dữ liệu, lời dạy là dữ liệu,
tra chương trình theo định danh bài. Không có nhánh Dart nào theo môn còn lại trên đường
Book → Lesson → Learn.

**Chặn vì HOẠT ĐỘNG KHÔNG GẮN ĐƯỢC VÀO BÀI:**

| Đo | Kết quả |
|---|---|
| Thí nghiệm Khoa học lớp 5 | 5 khối có thật, verbatim Chuẩn bị/Tiến hành — **`lesson: null` cả 5** ⇒ **0/5** gắn được vào bài |
| Thí nghiệm lớp 10 (Vật lí 2, Hoá học 3) | có thật — **`lesson: null` cả 5** |
| Gắn theo KHOẢNG TRANG (Vật lí 10) | thí nghiệm ở trang in 61, 73; bài đầu tiên có trang là **Bài 2 ở trang 91** ⇒ không bài nào chứa |
| Sách Hoá học 10 | `10-sgk-hoa-hoc-10` **không có trong mục lục g10** (chỉ có bản chuyên đề) ⇒ thí nghiệm trỏ vào cuốn không có bài nào |
| Giả thuyết «lệch trang in ↔ trang PDF» | **BÁC BỎ**: offset đo được chỉ **1–2 trang** (`05-sgk-toan-5-tap-mot` 23↔22, `05-sgk-khoa-hoc-5` 17↔16, `05-sgk-lich-su-va-dia-li-5` 12↔10). Không giải thích được khoảng cách 5→64 |

Trên máy thật khớp đúng số đo: Book Home của Khoa học 5 **có** thẻ «Thí nghiệm trong sách ·
5 thí nghiệm» ở mức **sách**, nhưng **mọi bài** đều nói «SAM đang học bài này» — vì không bài
nào nhận được thí nghiệm nào.

**Nguyên nhân gốc — một vấn đề đeo ba mặt nạ:**

C-006 (Tiếng Anh mất trang) · C-007 (finding SGV gán sai bài) · C-008 (hoạt động không gắn
được vào bài) **đều là cùng một thứ**: **quy trình nạp gán sai/không gán được đơn vị bài.**
Nội dung có thật, toạ độ trang có thật; cái thiếu là **phép căn giữa nội dung và bài.**

**Đây chính là điều cổng sinh ra để phát hiện.** Nếu lúc này đi viết tay `lesson: 3` cho năm
thí nghiệm để cổng «qua», thì cổng thành vô nghĩa và nợ đi thẳng vào sản phẩm. **Không làm.**

**Luật rút ra cho nhà máy:** hoạt động (thí nghiệm, đoạn đọc, tư liệu, bài tập) phải được
căn về bài bằng **toạ độ trang + ranh giới bài đã xác thực**, và bài nào không căn được thì
mang `UNKNOWN` — hiện lên ở mức **sách**, không bịa gắn vào một bài.

### C-009 · ✅ Tìm ra nguyên nhân gốc của C-006/C-007/C-008 — và sửa được

Đào tiếp từ C-008. Nguyên nhân **không** phải cửa sổ quét (`structure_scan.py` OCR 8 trang
đầu + 5 trang cuối) — mục lục của `05-sgk-khoa-hoc-5` **nằm gọn ở trang PDF 5 và ĐÃ được
OCR**. Nguyên nhân nằm ở chỗ đọc nó.

**Mục lục HAI CỘT bị đọc lẫn.** `parse_structure.py` v2 có phát hiện cột, nhưng hai chỗ
đóng cứng làm nó gộp hai cột thành một:

1. `detect_columns(gap=0.25)` — thân cột trái kết thúc ở x≈0.4, thân cột phải bắt đầu ở
   x≈0.5; cách nhau 0.1 < 0.25 nên **bị gộp**.
2. Cột số trang lấy theo `x > 0.80` — đúng với mục lục MỘT cột. Ở mục lục hai cột, số trang
   của cột TRÁI nằm **giữa trang** (x≈0.46) nên bị coi là chữ thân bài.

Hậu quả đúng như đã đo ở C-008: «Bài 1» nhận **trang 64** của «Bài 17» ở cột phải ⇒ hai dãy
đơn điệu chồng nhau ⇒ 56% đầu cuốn sách không bài nào phủ ⇒ 5 thí nghiệm ở trang 5–56 không
gắn được vào bài nào.

**Cách sửa (tất định, 0 LLM)** — `tool/corpus/toc_columns.py`, ba luật:

| Luật | Vì sao |
|---|---|
| Cột số trang = **cụm x của dòng TOÀN CHỮ SỐ**, không đoán trước vị trí | mỗi cột số trang định ra một DẢI; chữ bên trái nó thuộc dải ấy |
| Giữ lại **TỪ KHOÁ** đã khớp (`bai`/`chuDe`/`tuan`/`unit`) | «Chủ đề 1» và «Bài 1» đánh số ĐỘC LẬP — gộp chung là sinh số trùng giả |
| Đơn vị bài **theo từng cuốn**: có `bai` thì `bai`; không thì loại phổ biến nhất | Âm nhạc 3 **không có «Bài» nào** — «Chủ đề N» chính là đơn vị học. Lọc cứng `bai` xoá sạch mục lục cuốn đó |

Thêm một lỗi nhỏ mà hậu quả to: `đ` **không phải** `d` có dấu, nên bỏ dấu bằng NFD vẫn phải
thay riêng — thiếu dòng đó thì «Chủ đề» rơi nhầm vào rổ «Bài».

**Kết quả đo trên 415 cuốn có trang mục lục đã OCR:**

| | Cũ | Mới |
|---|---|---|
| Cuốn tốt lên / như cũ / xấu đi | — | **243 / 139 / 33** |
| Tổng số bài **TRÙNG SỐ** toàn corpus | 1.776 | **1.048** (−41%) |
| `05-sgk-khoa-hoc-5` | 36 mục · 3 trùng · phủ 0.39 · hở đầu 0.56 | **30 bài · 0 trùng · đơn điệu · trang 5→108** |

Khoa học 5 nay ra **đúng 30 bài + 6 chủ đề** — đúng cấu trúc thật của cuốn sách.

**Còn lại**: 33 cuốn xấu đi, hầu hết là Tiếng Việt (quy ước «Tuần»/«Chủ điểm» chưa phủ).
Chưa nối vào pipeline: đổi `curriculum-structure.json` là sinh lại pack và ảnh hưởng máy
thật, nên bước nối phải có đối chiếu trước/sau riêng.

---

### C-010 · Mục lục có HAI HỌ, và họ thứ hai lộ ra phân cấp thật

33 cuốn tụt hạng sau C-009 hầu hết là Tiếng Việt. Đọc OCR thì thấy lý do: **Tiếng Việt
không viết «Bài 1. …» — nó KẺ BẢNG.**

```
Tuần | Bài | Nội dung                | Trang
     |     | NHỮNG TRẢI NGHIỆM THÚ VỊ|   9
  1  |  1  | Đọc: Ngày gặp lại       |  10
     |     | Nói và nghe: Mùa hè…    |  11
     |     | Viết: Nghe-viết…        |  12
```

Số bài là **chữ số trần trong cột riêng**; chữ «Bài» chỉ xuất hiện MỘT lần ở dòng tiêu đề.
Mọi regex đòi từ khoá đều ra 0 mục.

**Hai điều quan trọng hơn cả bản sửa:**

1. **Phân cấp thật hiện ra: Sách → Tuần → Bài.** Số bài **lặp lại qua từng tuần** ⇒ số bài
   một mình **không bao giờ** đủ làm định danh. Đây là bằng chứng độc lập thứ hai cho
   WAL-170 (bằng chứng thứ nhất là GDTC đánh số lại theo chủ đề).
2. **Một «Bài» Tiếng Việt là KHỐI NHIỀU HOẠT ĐỘNG** — cột nội dung liệt kê *Đọc* / *Nói và
   nghe* / *Viết* bên trong cùng một bài. Sách tự liệt kê hoạt động của bài. Đây đúng là thứ
   EP-002 và EP-005 cần, và là đường vào tự nhiên để gắn hoạt động vào bài cho môn Tiếng
   Việt — khác hẳn Toán (một bài = một chuỗi bài tập).

**Đo lại sau khi thêm họ BẢNG** (415 cuốn có trang mục lục đã OCR):

| | Trước C-009 | Sau C-009 | Sau C-010 |
|---|---|---|---|
| Tốt lên / như cũ / xấu đi | — | 243 / 139 / 33 | **276 / 139 / 37** |
| Số bài trùng số toàn corpus | 1.776 | 1.048 | **1.051** |
| Cuốn dùng họ BẢNG | — | — | **49** |

**Còn lại**: 37 cuốn (Tiếng Việt lớp 1–3) ra ít bài hơn bản cũ — cột số bài của các cuốn đó
chưa nhận đủ. Phải xong trước khi nối vào pipeline.

---

### C-011 · ⚠️ «Bài» Tiếng Việt trong pack hiện tại thật ra là «TUẦN»

Điều tra 37 cuốn tụt hạng (Founder: *nếu parser mới làm xấu dữ liệu cũ thì fail closed và
điều tra*). Kết quả bác bỏ chính dữ liệu cũ:

`03-sgk-tieng-viet-3-tap-mot` — bản cũ có 13 «bài» mang số **3, 5, 6, 9…18**, trang 27…145.
Đó là **số TUẦN**, không phải số bài. `02-sgk-tieng-viet-2-tap-hai` cũng vậy: «bài» 19…35 là
tuần 19–35 (tuần chạy tiếp qua tập hai). Đọc đúng bảng thì ra **28 bài, đánh số 1…28, đủ
trang, 0 trùng**.

⇒ **Đây là lời giải thích cho nợ đã ghi ở WAL-166**: 34/68 hoạt động Tiếng Việt tập hai bị
mồ côi vì hoạt động khoá theo *bài* còn mục lục khoá theo *tuần*. Không phải lệch offset —
là **sai đơn vị**.

**Nguyên nhân kỹ thuật chung** (không phải chuyện riêng cuốn nào): mục lục Tiếng Việt trải
**4 trang** (p5–p8) nhưng `structure_scan` chỉ nhận trang có chữ «MỤC LỤC» hoặc ≥3 dòng khớp
regex bài ⇒ **chỉ nhận trang đầu**, mất 3/4 số bài. Trang nối tiếp chỉ lặp lại **dòng tiêu đề
cột**, và OCR có khi nuốt mất chính dòng đó (p007 chỉ đọc ra «Nội dung», «Trang») ⇒ phải
**thừa kế hình học cột** từ trang trước của cùng cuốn, và chỉ nhận trang **liền kề**.

**Chính sách hoà dữ liệu — không bao giờ để bản mới làm xấu bản cũ:**
nhận bản mới khi số bài **dùng được** (có trang **và** nằm trên xương sống đơn điệu) không
giảm và số bài trùng không tăng; ngược lại **giữ bản cũ + `REVIEW_REQUIRED`**. Đếm trần «có
trang» là sai — mục lục hai cột đọc lẫn vẫn cho nhiều bài «có trang», nhưng là trang của bài
khác.

| Toàn corpus | Cũ | Sau hoà |
|---|---|---|
| Cuốn lấy bản mới / giữ cũ để điều tra | — | **318 / 145** |
| Tổng bài | 7.626 | 8.254 |
| Bài **có trang** | 5.593 | **6.345** |
| Bài **trùng số** | 1.776 | **1.554** (−12%) |

Bốn cuốn lớp 5 đang chạy trên máy thật đều lấy bản mới; `05-sgk-toan-5-tap-mot` **không đổi**
(35 bài/29 trang/0 trùng) — cuốn vốn đã đúng thì không bị xáo.

**Hệ quả cho mô hình nội dung (Founder Delta):** bảng Tiếng Việt cho ra **hai tầng cùng lúc**
— `Tuần` và `Bài` — nên bộ đọc nay phát ra node kèm **vai trò**, chứ không phải một danh sách
bài phẳng. Đây là mảnh bằng chứng đầu tiên cho mô hình `ContentNode(role)` tổng quát; xem §3.

---

---

## 6. Trôi kiến trúc đang mở

| Mã | Hiện trạng | Rủi ro |
|---|---|---|
| D-1 | `resolveSurface()` có **0 caller** | mô hình surface tồn tại trên giấy; UI thật chưa đi qua nó |
| D-2 | 8 blueprint, **0 cái được runtime dùng** | blueprint chưa lái trải nghiệm nào |
| D-3 | `KnowledgeContentProvider` **0 implementation** | seam nội dung chưa nối |
| D-4 | 11% bài không có khoá định danh duy nhất | compiler chưa phát khoá cho phần này |
| D-5 | finding SGV chưa gán được về bài (C-007) | blueprint theo bài chưa dựng tự động được |
| D-6 | `authority` chỉ có một giá trị trong toàn bộ 13.634 finding | phân loại thẩm quyền hiện **không phân loại gì** |
| D-7 | hoạt động (thí nghiệm/đọc/tư liệu) mang `lesson: null` | có nội dung nhưng **không bài nào mở được nó** (C-008) — nguyên nhân gốc tìm ra ở C-009 |

Ba mục D-1..D-3 là lý do **không được** đẻ blueprint hàng loạt trước: chưa có gì tiêu thụ chúng.

---

## 7. Nối với Blueprint Compiler

```
SGK/SGV → bằng chứng trích được → sư phạm ứng viên → PHÂN LOẠI THẨM QUYỀN
        → chọn Experience Pattern → Blueprint → validation
```

**Cấm tuyệt đối**: *LLM đọc SGV → tự nghĩ ra sư phạm → thành sự thật production.*

Bốn mức thẩm quyền phải đi kèm mọi trường compiler phát ra:

| Mức | Nghĩa |
|---|---|
| `SOURCE_EXPLICIT` | sách/SGV **nói thẳng** |
| `SOURCE_DEMONSTRATED` | sách **dạy qua ví dụ** (⇒ SAM nói «làm theo ví dụ», KHÔNG «sách nói rằng») |
| `INFERRED / REVIEW_REQUIRED` | suy ra được, **phải người duyệt** trước khi tới trẻ |
| `UNKNOWN` | **để trống** — không bịa method/sequence/misconception/assistance |

Không đủ bằng chứng thì **để unknown**, không lấp.

---

## 8. Chiến lược chất lượng (không QA tay toàn corpus)

```
toàn corpus → compiler → validation tự động → gom cụm theo Experience Pattern
→ lấy mẫu đại diện → Gold Lesson QA sâu → phát hiện ngoại lai
→ sửa PATTERN/COMPILER (không sửa từng bài) → sinh lại
```

**Gold Set** (nhỏ, đa dạng, dùng để **bác bỏ** kiến trúc — không phải cách sản xuất nội dung):

| Gold | Bài | Vì sao có trong tập |
|---|---|---|
| G-1 | Toán 5 · Bài 6 | EP-001, đã chạy hết luồng trên máy thật |
| G-2 | *(trống)* | cần một bài **môn khác + lớp khác** cho Architecture Gate |
| G-3 | *(trống)* | cần một bài Khoa học để kiểm cổng dự đoán EP-003 |

Nguyên tắc khi tỉ lệ ngoại lệ tăng: **không vá từng bài** — chất vấn taxonomy/compiler.

---

## 9. Việc kế tiếp của nhà máy

Thứ tự này đổi sau C-007: **không** bắt đầu bằng compiler-sinh-blueprint, vì dữ liệu chưa
đỡ nổi.

1. **CĂN HOẠT ĐỘNG VỀ BÀI** (C-008) — điều kiện cần của cổng kiến trúc, và là cùng một
   nguyên nhân gốc với C-006/C-007. Không có bước này thì nội dung có thật vẫn không tới
   được bài nào, và cổng không thể qua bằng cách trung thực.
2. **Nối một blueprint có thật vào runtime** (gỡ trôi D-2), bắt đầu từ `blueprintQuyDongB6`
   vì nó đã trỏ đúng bài G-1. Chưa sinh blueprint hàng loạt.
3. **Căn trang → bài cho SGV** (D-5). Đây là điều kiện cần của compiler; trước bước này mọi
   blueprint sinh tự động đều gán sai bài.
4. **Compiler tự suy mức thẩm quyền** (D-6), không thừa kế `SOURCE_EXPLICIT` có sẵn.
5. Sửa ingestion Tiếng Anh theo C-006 (có SGV cùng bộ làm nguồn đối chiếu).
