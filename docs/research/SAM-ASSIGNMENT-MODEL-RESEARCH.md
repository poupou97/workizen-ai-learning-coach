# Assignment domain model — bài GIAO khác bài TỰ HỌC (WAL-104, delta J)

**Trạng thái:** research + đề xuất model nhỏ nhất. Chưa UI, chưa store schema.

## 1. Câu hỏi falsify trung tâm: «assistancePolicy đã tồn tại chưa?»

Kiểm code thật: `SessionMode` chỉ có HAI mức (`learn`/`assess`) và
`tutoringViolationsInExam` chỉ nổ khi `assess`. `maxSupportIn` đo hậu-kiểm,
không cấm trước. Vậy hiện trạng biểu diễn được PRACTICE (learn, thang ±1 đầy
đủ) và ASSESSMENT (assess, mọi tutoring là violation) — nhưng KHÔNG biểu diễn
được hai vùng giữa:
- **HOMEWORK**: hint được phép (trẻ vẫn đang học) nhưng REVEAL lời giải trọn
  vẹn bị khoá — «làm hộ bài về nhà» chính là ca EEF bác (parental
  homework-help KHÔNG nâng attainment; SAM làm hộ càng tệ hơn cha mẹ làm hộ).
- **MOCK**: luật TRONG-phiên y hệt ASSESSMENT (assess, không tutoring) — chỉ
  khác SAU-phiên: được xem lại và luyện lại ngay. Khác biệt nằm ở
  review-after, KHÔNG phải ở một mode thứ ba.

**Kết luận falsification:** một nửa tồn tại rồi. KHÔNG thêm giá trị mới vào
`SessionMode` (bài học TeachingStrategy-enum: đừng nhân khái niệm khi thứ đã
có biểu diễn được). Cái thiếu là MỘT BẢNG ÁNH XẠ policy → tham số sẵn có.

## 2. Model nhỏ nhất

`AssistancePolicy` (4 giá trị) ánh xạ TẤT ĐỊNH sang bộ tham số đã tồn tại:

| Policy | SessionMode | supportCap | revealAllowed | reviewAfter |
|---|---|---|---|---|
| practice | learn | fullSolution | ✅ (sau attempt — REVEAL gate giữ) | ✅ |
| homework | learn | workedStep | ❌ khoá đến hết hạn | ✅ sau dueAt |
| mock | assess | none | ❌ | ✅ ngay khi nộp |
| assessment | assess | none | ❌ | theo giáo viên |

- `supportCap` = trần `SupportLevel` surface được phép phát — thang ±1 vẫn
  chạy BÊN DƯỚI trần, không phải mode mới; vi phạm trần đo được bằng
  `maxSupportIn(session) > cap` (hậu kiểm, cùng chỗ với eval L1).
- `Assignment` aggregate = {assignmentId, source (teacherStated/parentStated/
  samGenerated — tái dùng ngữ nghĩa KnowledgeOrigin, không thêm hệ nguồn mới),
  problems (CanonicalProblem ids — mọi nguồn đề đã mint qua đó), policy,
  dueAt?, expiry}. Nguồn nào GIAO không đổi luật — chỉ policy đổi luật.
- Nối sẵn có: ASSESSMENT/MOCK dùng `tutoringViolationsInExam` nguyên trạng;
  Agenda đã chừa `upcomingAssessment` signal; eval L1 đo homework-violation
  bằng cùng lineage (premature-answer trong homework = REVEAL lọt trần).

## 3. Vì sao HOMEWORK xứng đáng là mức riêng (evidence)

EEF parental engagement: can-thiệp-kiểu-giúp-làm-bài-tập KHÔNG tăng attainment
— «làm hộ» là failure mode có meta-analysis. HOMEWORK ≠ PRACTICE ở đúng một
chỗ: sản phẩm nộp cho giáo viên phải là CỦA TRẺ. Hint (định hướng) giữ được
điều đó; fullSolution thì không. Đây là luật cấu trúc, không phải prompt.

## 4. Ngoài phạm vi (ghi thật)

Store schema cho Assignment, UI giao/nhận bài, luồng teacher tạo bài (cần
TeacherAssignment — WAL-100), và enforcement supportCap TRONG surface (hiện
mới có bảng ánh xạ + đo hậu kiểm). Triển khai khi Assignment có người dùng
thật đầu tiên (teacher hoặc parent flow).
