/// WAL-108 — CURRICULUM CONTEXT của First Vertical Slice: Toán 5 · Bài 6
/// («Cộng, trừ hai phân số khác mẫu số»).
///
/// Provenance là TOẠ ĐỘ THẬT từ corpus (method-catalogue, qmap-v1):
/// - `m:quy-dong:g5:b6:p21` — SGK Toán 5 tập một, Bài 6, trang in 21,
///   quy tắc chung được NÓI THẲNG (sourceStated); cách «lấy tích hai mẫu»
///   cho ca không-chia-hết được dạy QUA VÍ DỤ trang 21–22 ⇒ method ở đây khai
///   [KnowledgeOrigin.sourceDemonstrated] — trung thực với corpus, và
///   `sourceLineForChild` sẽ render «SAM làm theo ví dụ…», KHÔNG «sách nói rằng».
/// - `m:quy-dong:g4:b60:p77` — SGK Toán 4 tập hai, Bài 60, trang in 77 (ca
///   chia-hết của lớp 4, cách «lấy mẫu lớn hơn» dạy qua ví dụ).
/// KHÔNG nhúng nguyên văn câu sách (ADR-002 / WAL-43): chỉ toạ độ + origin.
///
/// Fail closed: grade != 5 ⇒ KHÔNG có context — không dạy generic method sai
/// cấp. BCNN không tồn tại trong catalogue này (Bài 6 chưa dạy BCNN) — guard
/// test giữ bất biến «BCNN không thể xuất hiện ở Math5 B6» (§3 Master Order).
library;

import '../curriculum/fraction_problem.dart' show fractionSumCase;
import '../curriculum/pedagogical_boundary.dart';
import '../curriculum/skill_case.dart';
import '../store/learner_profile.dart';
import 'provenance.dart';

/// Phân LOẠI CA của một bài: chuỗi đề → id ca trong chương trình, `null` khi
/// không nhận ra. Đây là chỗ DUY NHẤT còn biết môn — và nó thuộc về dữ liệu
/// của bài, không thuộc runtime (WAL-168).
typedef CaseClassifier = String? Function(String expression);

/// Phiên bản model tri thức — đi vào provenance drill-down và mọi phiên ghi.
const String knowledgeModelVersion = 'slice-toan5-b6-v1+qmap-v1';

/// Ngữ cảnh chương trình cho MỘT bài học cụ thể — mọi thứ Tutor cần để
/// quyết định «được dạy gì», lắp từ object canonical đã có.
class SliceCurriculum {
  const SliceCurriculum({
    required this.subjectId,
    required this.conceptId,
    required this.activityLabel,
    required this.stage,
    required this.catalogue,
    required this.cases,
    required this.classifyCase,
  });

  final String subjectId;
  final String conceptId;

  /// ⭐ WAL-168 — «bài này thuộc DẠNG nào»: hàm của HỌ MÔN, đặt trong DÒNG DỮ
  /// LIỆU của bài chứ không trong màn hình.
  ///
  /// Trước đây `ProblemContextScreen` tự gọi `FractionProblem.parse` rồi
  /// `fractionCase(...)` — mẩu kiến thức-môn duy nhất còn nằm trong màn dùng
  /// chung, và là lý do môn thứ hai không dạy được gì (Architecture Gate).
  /// Nay thêm một bài phân số = trỏ tới `fractionSumCase`; thêm một họ môn mới
  /// = viết MỘT classifier dùng chung cho mọi bài của họ đó.
  final CaseClassifier classifyCase;

  /// Nhãn hoạt động cho trẻ/phụ huynh — «Bài tập về nhà · Toán 5 · Bài 6».
  final String activityLabel;
  final LearningStage stage;
  final List<TeachingMethod> catalogue;
  final List<SkillCase> cases;
}

/// ⭐⭐ WAL-170 — ĐỊNH DANH MỘT BÀI, đủ chặt để tra chương trình.
///
/// KHÔNG dựa vào số bài một mình. Đo trên corpus (7.626 bản ghi bài):
/// - `number` là DISPLAY METADATA, nghĩa đổi theo họ sách — corpus mang
///   `unitKind` ∈ {bai, tuan, chuDe}, và Tiếng Anh Global Success đánh số theo
///   UNIT (tập một: 2,3,4,5,8,9,10). GDTC lớp 5 có 5 bài cùng mang số 1.
/// - Bộ ba (sách, số, trang in) là DUY NHẤT ở 6.856/7.626 bản ghi (89%);
///   770 bản ghi còn nhập nhằng ở 131 cuốn.
///
/// Vì không có khoá tự nhiên nào chắc 100%, chương trình phải khai định danh
/// TƯỜNG MINH và tra khớp CHÍNH XÁC. Không khớp ⇒ `null` ⇒ fail closed.
class LessonKey {
  const LessonKey({
    required this.sourceDocumentId,
    required this.number,
    this.pageStart,
  });

  final String sourceDocumentId;

  /// Số IN TRÊN SÁCH. Giữ để hiển thị và để so khớp, KHÔNG dùng một mình.
  final int number;

  /// Trang in nơi bài bắt đầu — mảnh phân biệt hai bài trùng số trong một
  /// cuốn. `null` khi TOC miner chưa bắt được (2.033/7.626 bản ghi).
  final int? pageStart;

  /// Dạng chuỗi để làm khoá `Map` hằng. Hằng số không cho phép khoá là object
  /// có `==` riêng, nên định danh đi qua chuỗi chuẩn hoá này.
  String get canonical => '$sourceDocumentId#$number@${pageStart ?? '-'}';

  @override
  bool operator ==(Object other) =>
      other is LessonKey && other.canonical == canonical;

  @override
  int get hashCode => canonical.hashCode;

  @override
  String toString() => canonical;
}

/// Đăng ký chương trình THEO BÀI. Thêm một bài = thêm MỘT DÒNG ở bảng này.
///
/// ⭐ Khoá là định danh CHÍNH XÁC của bài (sách + số + trang in), không phải
/// lớp. Trước WAL-170 việc tra chỉ hỏi `p.grade != 5`, nghĩa là MỌI bài của
/// trẻ lớp 5 đều nhận provenance của Toán 5 Bài 6 — «Nguồn bài học» của một
/// bài Khoa học sẽ trưng ra trang 21 SGK Toán. Đó là nói dối về nguồn.
const Map<String, SliceCurriculum> _curriculumByLesson = {
  // 05-sgk-toan-5-tap-mot · Bài 6 · trang in 20 (corpus: pageStart 20,
  // titleSource ocr-header:p21).
  '05-sgk-toan-5-tap-mot#6@20': _toan5Bai6,
};

/// Chương trình cho ĐÚNG bài này. Không có dòng nào khớp ⇒ `null`.
///
/// Đây là đường DUY NHẤT để một màn hình xin chương trình của một bài cụ thể.
SliceCurriculum? curriculumForLesson(LessonKey key) =>
    _curriculumByLesson[key.canonical];

/// Các dòng chương trình đã nạp cho LỚP của trẻ — dùng cho màn hình nói về
/// TÌNH HÌNH HỌC (bản đồ, tiến trình, thẻ bố mẹ). Những màn đó nói về bằng
/// chứng của trẻ, không trưng nguồn của một bài, nên lọc theo lớp là trung
/// thực. Chúng KHÔNG được dùng để trả lời «bài này lấy từ đâu».
List<SliceCurriculum> curriculaForLearner(LearnerProfile p) =>
    [for (final c in _curriculumByLesson.values) if (c.stage.grade == p.grade) c];

/// Chương trình cho MỘT BÀI CHỤP ĐƯỢC (camera / tự gõ) — nơi không có định
/// danh bài nào cả.
///
/// Hỏi từng dòng chương trình trong lớp của trẻ: «anh có NHẬN RA đề này
/// không?» Đúng MỘT dòng nhận ⇒ dùng dòng đó. Không dòng nào ⇒ ngoài phạm vi.
/// Nhiều hơn một ⇒ NHẬP NHẰNG ⇒ cũng fail closed: thà nhận chưa chắc còn hơn
/// dạy bằng chương trình của bài khác.
SliceCurriculum? curriculumForProblem(LearnerProfile p, String expression) {
  final hits = [
    for (final c in curriculaForLearner(p))
      if (c.classifyCase(expression) != null) c
  ];
  return hits.length == 1 ? hits.single : null;
}

const SliceCurriculum _toan5Bai6 = SliceCurriculum(
    subjectId: 'toan',
    conceptId: 'quy-dong',
    activityLabel: 'Toán 5 · Bài 6 · Cộng, trừ hai phân số khác mẫu số',
    classifyCase: fractionSumCase,
    stage: LearningStage(
      grade: 5,
      bookSeries: 'kntt',
      lessonId: 'toan5-t1-bai6',
      conceptsIntroduced: {'phan-so', 'chia-het', 'nhan-so-tu-nhien'},
      methodsIntroduced: {'common-denom-take-larger', 'common-denom-by-product'},
      terminologyIntroduced: {'mẫu số chung'},
    ),
    catalogue: [
      TeachingMethod(
        id: 'common-denom-by-product',
        name: 'Lấy mẫu số chung là tích hai mẫu số',
        appliesToConcepts: {'quy-dong'},
        skillCaseId: 'denominator-non-divisible',
        requiresConcepts: {'phan-so', 'nhan-so-tu-nhien'},
        requiresTerminology: {'mẫu số chung'},
        // WAL-168 — LỜI DẠY LÀ DỮ LIỆU. Nguyên văn ba nấc trước đây nằm trong
        // `hintTextFor`; chữ không đổi một dấu, chỉ đổi chỗ ở: nay đi cùng
        // phương pháp (thứ có provenance), số do bài điền vào slot.
        hints: MethodHints(
          hint: 'Hai mẫu số {b} và {d} không chia hết cho nhau. '
              'Muốn cộng được thì hai phân số phải cùng mẫu số — '
              'con nghĩ xem mẫu số chung lấy thế nào nhé?',
          workedStep: 'Bước đầu tiên: lấy mẫu số chung là {b} × {d} = {product}. '
              'Giờ con quy đồng hai phân số về mẫu {product} nhé — đến lượt con!',
          fullSolution: 'Cả bài nhé: mẫu số chung là {b} × {d} = {product}. '
              '{a}/{b} = {aOverProduct}/{product} và '
              '{c}/{d} = {cOverProduct}/{product}. '
              'Vậy {a}/{b} {op} {c}/{d} = {resultNum}/{product}. '
              'Mai mình làm lại một bài giống thế này không cần SAM nhé!',
        ),
        // m:quy-dong:g5:b6:p21 — dạy qua ví dụ ⇒ sourceDemonstrated.
        provenance: Provenance(
          origin: KnowledgeOrigin.sourceDemonstrated,
          sourceId: '05-sgk-toan-5-tap-mot',
          extractionMethod: 'rule-method-v1',
          confidence: 0.9,
          bookSeries: 'kntt',
          grade: 5,
          subject: 'Toán',
          pageStart: 21,
          pageEnd: 22,
        ),
      ),
      TeachingMethod(
        id: 'common-denom-take-larger',
        name: 'Giữ mẫu số lớn hơn làm mẫu số chung',
        appliesToConcepts: {'quy-dong'},
        skillCaseId: 'denominator-divisible',
        requiresConcepts: {'phan-so', 'chia-het'},
        requiresTerminology: {'mẫu số chung'},
        // Cách lớp 4 — cố ý KHÔNG nêu số: giữ nguyên văn bản cũ, vốn hỏi lại
        // chứ không đưa số (trẻ phải tự nhìn ra mẫu nào chia hết cho mẫu nào).
        hints: MethodHints(
          hint: 'Con thử xem mẫu số lớn hơn có chia hết cho mẫu số kia không?',
          workedStep: 'Bước đầu tiên: giữ nguyên phân số có mẫu lớn hơn, '
              'quy đồng phân số còn lại. Đến lượt con!',
          fullSolution: 'Cả bài nhé: mẫu số chung là {b} × {d} = {product}. '
              '{a}/{b} = {aOverProduct}/{product} và '
              '{c}/{d} = {cOverProduct}/{product}. '
              'Vậy {a}/{b} {op} {c}/{d} = {resultNum}/{product}. '
              'Mai mình làm lại một bài giống thế này không cần SAM nhé!',
        ),
        // m:quy-dong:g4:b60:p77 — ca lớp 4, dạy qua ví dụ.
        provenance: Provenance(
          origin: KnowledgeOrigin.sourceDemonstrated,
          sourceId: '04-sgk-toan-4-tap-hai',
          extractionMethod: 'rule-method-v1',
          confidence: 0.9,
          bookSeries: 'kntt',
          grade: 4,
          subject: 'Toán',
          pageStart: 77,
        ),
      ),
    ],
    cases: [
      SkillCase(
          id: 'denominator-divisible',
          conceptId: 'quy-dong',
          condition: 'một mẫu số chia hết cho mẫu số còn lại',
          introducedGrade: 4),
      SkillCase(
          id: 'denominator-non-divisible',
          conceptId: 'quy-dong',
          condition: 'hai mẫu số không chia hết cho nhau',
          introducedGrade: 5),
    ],
  );
