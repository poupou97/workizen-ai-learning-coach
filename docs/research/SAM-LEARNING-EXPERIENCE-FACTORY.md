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

**Bốn thứ KHÔNG được đánh đồng:**

- **Subject** (môn) — nhãn hành chính của sách.
- **Lesson** (bài) — một mục có định danh trong một cuốn.
- **Pattern** (mẫu trải nghiệm) — hình dạng sư phạm; một môn có nhiều pattern, một pattern
  dùng cho nhiều môn.
- **Surface** (mặt tương tác) — **primitive tương tác, KHÔNG phải sư phạm.**

---

## 4. Experience Pattern Registry

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

---

## 6. Trôi kiến trúc đang mở

| Mã | Hiện trạng | Rủi ro |
|---|---|---|
| D-1 | `resolveSurface()` có **0 caller** | mô hình surface tồn tại trên giấy; UI thật chưa đi qua nó |
| D-2 | 8 blueprint, **0 cái được runtime dùng** | blueprint chưa lái trải nghiệm nào |
| D-3 | `KnowledgeContentProvider` **0 implementation** | seam nội dung chưa nối |
| D-4 | 11% bài không có khoá định danh duy nhất | compiler chưa phát khoá cho phần này |

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

1. Nối **một blueprint có thật** vào runtime (gỡ trôi D-2), bắt đầu từ `blueprintQuyDongB6` vì
   nó đã trỏ đúng bài G-1.
2. Compiler phát **định danh bài** + **mức thẩm quyền**, chạy thử trên một họ nội dung.
3. Cổng kiến trúc: **môn thứ hai + lớp thứ hai** chạy Book → Lesson → Learn → Evidence, không
   Dart riêng theo bài. Qua rồi mới thêm sách/bài chủ yếu bằng data/config.
4. Sửa ingestion Tiếng Anh theo C-006 (có SGV làm nguồn đối chiếu).
