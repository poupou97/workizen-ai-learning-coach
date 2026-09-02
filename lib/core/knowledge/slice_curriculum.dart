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

import '../curriculum/pedagogical_boundary.dart';
import '../curriculum/skill_case.dart';
import '../store/learner_profile.dart';
import 'provenance.dart';

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
  });

  final String subjectId;
  final String conceptId;

  /// Nhãn hoạt động cho trẻ/phụ huynh — «Bài tập về nhà · Toán 5 · Bài 6».
  final String activityLabel;
  final LearningStage stage;
  final List<TeachingMethod> catalogue;
  final List<SkillCase> cases;
}

/// Context theo HỒ SƠ THẬT. `null` = ngoài phạm vi slice (grade ≠ 5) —
/// fail closed: tầng trên phải để SAM nhận «chưa chắc», không dạy bừa.
SliceCurriculum? curriculumFor(LearnerProfile p) {
  if (p.grade != 5) return null;
  return const SliceCurriculum(
    subjectId: 'toan',
    conceptId: 'quy-dong',
    activityLabel: 'Toán 5 · Bài 6 · Cộng, trừ hai phân số khác mẫu số',
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
}
