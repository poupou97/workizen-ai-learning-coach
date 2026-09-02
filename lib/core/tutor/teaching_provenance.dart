/// FOUNDER DELTA (2026-09-01) — PEDAGOGICAL PROVENANCE / EXPLAINABLE TEACHING.
///
/// Bất biến: **NO TEACHING WITHOUT PEDAGOGICAL PROVENANCE.** Mỗi TeachingAct
/// học thuật phải trả lời được WHAT/WHERE/SOURCE/HOW/WHY/AUTHORITY/ALLOWED —
/// không đủ thì FAIL CLOSED, không bịa thẩm quyền chương trình.
///
/// Đây KHÔNG phải mega-object mới: nó LẮP từ các object canonical đã có
/// (TutorScope, TeachingMethod, LearningStage, Provenance) — đúng chỉ thị
/// «reuse, avoid duplicate provenance object».
///
/// Luật phát ngôn nguồn (giữ bằng test):
/// - sourceStated       → «Theo SGK …, trang N» (sách NÓI THẲNG)
/// - sourceDemonstrated → «SAM làm theo VÍ DỤ trong SGK …, trang N» — KHÔNG
///   BAO GIỜ render thành «sách nói rằng» (ca B57; Delta §2: loại hỗ trợ là
///   một phần của tính đúng trích dẫn)
/// - systemDerived/llmInferred/null → «Đây là cách của SAM — con có thể kiểm
///   lại» (không claim thẩm quyền sách)
library;

import '../curriculum/pedagogical_boundary.dart';
import '../knowledge/provenance.dart';

/// Câu trả lời 7 chiều cho MỘT hành động dạy. Bất biến kiểu: chỉ mint qua
/// [explainTeaching] — method ngoài scope không thể có provenance object.
class TeachingProvenance {
  const TeachingProvenance._({
    required this.conceptId,
    required this.skillCaseId,
    required this.stage,
    required this.method,
    required this.methodReason,
    required this.authority,
  });

  final String conceptId; // WHAT
  final String? skillCaseId; // WHAT (ca)
  final LearningStage stage; // WHERE (môn/lớp/vị trí chương trình)
  final TeachingMethod method; // HOW
  final String methodReason; // WHY — đọc được, tất định
  final KnowledgeOrigin? authority; // AUTHORITY (null = SAM tự nhận)

  /// SOURCE — chỉ tồn tại khi method có provenance trích dẫn được.
  Provenance? get source =>
      (method.provenance?.citableAsTextbookFact ?? false)
          ? method.provenance
          : null;

  /// Dòng nguồn cho TRẺ — tuổi-thích-ứng tầng chữ, không thuật ngữ kỹ thuật.
  String get sourceLineForChild => sourceLineForChildOf(source);

  /// Vì-sao-cách-này cho TRẺ.
  String get whyLineForChild => methodReason;
}

/// LUẬT RENDER NGUỒN — một chỗ duy nhất (WAL-141 #17 tái dùng cho sheet
/// «Nguồn bài học»); mutation-guard của sourceLineForChild phủ luôn hàm này.
String sourceLineForChildOf(Provenance? p) {
  if (p == null || !p.citableAsTextbookFact) {
    return 'Đây là cách của SAM — con có thể kiểm lại cùng thầy cô nhé.';
  }
  final where = 'SGK ${p.subject ?? ''} ${p.grade ?? ''}'.trim();
  return switch (p.origin) {
    KnowledgeOrigin.sourceStated => 'Theo $where, trang ${p.pageStart}.',
    KnowledgeOrigin.sourceDemonstrated =>
      'SAM làm theo ví dụ trong $where, trang ${p.pageStart}.',
    // sequence không phải chỗ dựa cho MỘT phương pháp — coi như cách của SAM
    _ => 'Đây là cách của SAM — con có thể kiểm lại cùng thầy cô nhé.',
  };
}

/// Mint DUY NHẤT. Trả `null` (fail closed) khi:
/// - [scope] không chứa method nào (caseUnknown / hết scope), hoặc
/// - [methodId] không nằm trong `scope.allowedMethods` (F7 Delta: có map
///   được ca nhưng method KHÔNG có phép sư phạm ⇒ không dạy, không giải thích).
TeachingProvenance? explainTeaching({
  required TutorScope scope,
  required String methodId,
  required String? exerciseCase,
}) {
  TeachingMethod? m;
  for (final c in scope.allowedMethods) {
    if (c.id == methodId) m = c;
  }
  if (m == null) return null; // ALLOWED thất bại ⇒ không có gì để giải thích

  final why = StringBuffer()
    ..write('Cách «${m.name}» dùng được cho dạng bài này')
    ..write(exerciseCase != null ? ' (dạng: $exerciseCase)' : '')
    ..write(', và con đã học nó trong chương trình '
        '(lớp ${scope.stage.grade}, ${scope.stage.lessonId}).');

  return TeachingProvenance._(
    conceptId: scope.targetConcept,
    skillCaseId: exerciseCase,
    stage: scope.stage,
    method: m,
    methodReason: why.toString(),
    authority: m.provenance?.origin,
  );
}
