/// ⭐ WAL-210 round 3 (A-runtime, Founder A6) — MỤC CHƯƠNG TRÌNH TỐI THIỂU
/// cho lát cắt vàng: KHTN 6 (KNTT) · Bài 17 «Tách chất khỏi hỗn hợp» ·
/// SGK trang in 60–63 (PDF 61–64, TSL tc2-p1 `bai-17.tsl.json`, boundary
/// confidence 0.95, `answer_keys_included: false`).
///
/// Chỉ đủ để MỘT binding giải được `TutorScope`: một khái niệm, một ca, một
/// phương pháp CÓ NGUỒN NÓI THẲNG. Không phải chương trình môn KHTN, không
/// dùng cho bài nào khác, KHÔNG đăng ký vào `curriculumForProblem` (đường
/// chụp bài Toán 5 không đổi).
///
/// Cơ sở (đọc từ TSL, không suy diễn):
/// - Mục tiêu (block 1:tc2-p1:006): «…tách các chất ra khỏi hỗn hợp dựa trên
///   tính chất vật lí bằng cách lọc, cô cạn, chiết.»
/// - «Em đã học» (PDF 64 → trang in 63, block 4:tc2-p1:003–007): «Dựa vào
///   các tính chất khác nhau có thể áp dụng cách phù hợp để tách chất ra
///   khỏi hỗn hợp: Lọc / Lắng / Cô cạn / Chiết (…)». Sách NÓI THẲNG quy tắc
///   ⇒ `KnowledgeOrigin.sourceStated`, trích được trang.
/// - Câu hỏi SGK (block 3:tc2-p1:011, trang in 62): «Quá trình làm muối từ
///   nước biển sử dụng phương pháp tách chất nào?» — đúng ca «chọn cách tách».
///
/// Không có: SGV (không có mặt trong TSL này), khoá đáp án (SGK không in) ⇒
/// phương pháp KHÔNG có `hints` — SAM không có lời dạy tất định nào cho bài
/// này ngoài kịch bản Track B (được runtime kiểm, xem `pedagogy_runtime.dart`).
library;

import '../knowledge/provenance.dart';
import 'concept.dart';
import 'pedagogical_boundary.dart';
import 'semantic_binding.dart';
import 'skill_case.dart';

const khtn6Bai17 = LessonRef('06-sgk-khoa-hoc-tu-nhien-6', 17);

const String khtn6TachChatConceptId = 'tach-chat-khoi-hon-hop';
const String khtn6ChonCachTachCaseId = 'chon-cach-tach-theo-tinh-chat';
const String khtn6TachChatMethodId = 'tach-chat-theo-tinh-chat';

const khtn6TachChatConcept = Concept(
  id: khtn6TachChatConceptId,
  canonicalName: 'Tách chất khỏi hỗn hợp',
  exposures: [
    ConceptExposure(
        grade: 6,
        bookSeries: 'kntt',
        lessonId: 'khtn6-b17',
        role: ExposureRole.introduces,
        pageStart: 60),
  ],
  // Từ SÁCH dùng (mục tiêu + «Em đã học») — không thêm từ ngoài.
  textbookTerms: {
    6: {'lọc', 'lắng', 'cô cạn', 'chiết', 'hỗn hợp'},
  },
);

const khtn6ChonCachTachCase = SkillCase(
  id: khtn6ChonCachTachCaseId,
  conceptId: khtn6TachChatConceptId,
  // Điều kiện THEO LỜI SÁCH («Em đã học», trang in 63).
  condition:
      'Dựa vào các tính chất khác nhau có thể áp dụng cách phù hợp để tách '
      'chất ra khỏi hỗn hợp',
  introducedGrade: 6,
);

const khtn6Bai17Stage = LearningStage(
  grade: 6,
  bookSeries: 'kntt',
  lessonId: 'khtn6-b17',
  conceptsIntroduced: {khtn6TachChatConceptId},
  methodsIntroduced: {khtn6TachChatMethodId},
  terminologyIntroduced: {'lọc', 'lắng', 'cô cạn', 'chiết', 'hỗn hợp'},
);

/// Phương pháp DUY NHẤT có nguồn nói thẳng trong bài. `hints: null` là cố ý
/// (không có SGV/khoá đáp án ⇒ không bịa lời dạy).
const khtn6TachChatTheoTinhChat = TeachingMethod(
  id: khtn6TachChatMethodId,
  name: 'Chọn cách tách dựa vào tính chất khác nhau của các chất trong hỗn hợp',
  appliesToConcepts: {khtn6TachChatConceptId},
  skillCaseId: khtn6ChonCachTachCaseId,
  requiresConcepts: {khtn6TachChatConceptId},
  requiresTerminology: {'lọc', 'cô cạn', 'chiết'},
  provenance: Provenance(
    origin: KnowledgeOrigin.sourceStated,
    sourceId: '06-sgk-khoa-hoc-tu-nhien-6',
    extractionMethod:
        'manual:tsl-tc2-p1/bai-17 «Em đã học» blocks 4:tc2-p1:003–007 (PDF 64)',
    confidence: 0.9,
    bookSeries: 'kntt',
    grade: 6,
    subject: 'KHTN',
    pageStart: 63, // trang IN (PDF 64; lệch −1 theo boundary TSL 61–64 ↔ 60–63)
    pageEnd: 63,
  ),
);

const khtn6Bai17Curriculum = BindingCurriculum(
  conceptId: khtn6TachChatConceptId,
  cases: [khtn6ChonCachTachCase],
  stage: khtn6Bai17Stage,
  catalogue: [khtn6TachChatTheoTinhChat],
);

/// ⭐ Binding DUY NHẤT của sổ đăng ký hôm nay — hoạt động «Học với SAM» của
/// Bài 17 → khái niệm/ca «chọn cách tách theo tính chất» → phương pháp có
/// nguồn nói thẳng. PROPOSED.
const khtn6Bai17TutorBinding = SemanticBinding(
  activityId: SemanticBinding.tutorScriptActivity,
  lessonRef: khtn6Bai17,
  conceptId: khtn6TachChatConceptId,
  skillCaseId: khtn6ChonCachTachCaseId,
  methodIds: [khtn6TachChatMethodId],
  bindingSource: BindingSource.curated,
  confidence: 0.8,
  provenance: BindingProvenance(
    curatedBy: 'lane A-runtime · 2026-09-05 (round 3)',
    basis: 'TSL tc2-p1 bai-17: objective 1:tc2-p1:006; «Em đã học» '
        '4:tc2-p1:003–007 (tr. 63); SGK question 3:tc2-p1:011 (tr. 62)',
    note: 'Một binding cho lát cắt vàng — không phải chuyển đổi K-12. '
        'Khoá đáp án của kịch bản là prototype, KHÔNG thuộc binding.',
  ),
);
