/// ⭐⭐ WAL-210 round 3 (A-runtime, Founder A6) — SEMANTIC BINDING (PROPOSED).
///
/// Mắt xích còn thiếu giữa hai đường (audit 03 §B.2: «SemanticBinding NOT
/// IMPLEMENTED»):
///
///   Trusted Structured Lesson → LearningActivity → **SemanticBinding**
///     → Concept / SkillCase → Method → Pedagogy Runtime
///
/// Một binding nói: HOẠT ĐỘNG này (của BÀI này trong SÁCH này) nói về KHÁI
/// NIỆM / CA nào, và những PHƯƠNG PHÁP nào được phép — với xuất xứ và độ tin
/// của chính cái ánh xạ đó. Binding KHÔNG chứa nội dung, KHÔNG chứa lời dạy.
///
/// Bất biến (giữ bằng test):
/// - RETRIEVED ≠ PERMITTED: `methodIds` khai trong binding chỉ là ỨNG VIÊN.
///   Phương pháp được phép = ∩ của (khai trong binding) ∩ (TutorScope.forProblem
///   cho ca) ∩ (provenance `sourceStated`, trích được trang). Thiếu một điều
///   kiện ⇒ loại, có lý do.
/// - Không có curriculum tối thiểu cho bài ⇒ binding KHÔNG giải được (không
///   scope, không method) — fail closed, không mượn bài khác.
/// - Sổ đăng ký là hằng đóng: hôm nay ĐÚNG MỘT binding (KHTN 6 Bài 17, lát
///   cắt vàng). Không chuyển đổi K-12 hàng loạt (Founder A6).
library;

import '../context/learning_context.dart';
import '../knowledge/provenance.dart';
import 'pedagogical_boundary.dart';
import 'skill_case.dart';

/// Định danh MỘT BÀI trong MỘT CUỐN — cùng khoá với lineage trên
/// `LearningEvent` (`sourceDocumentId` + `lessonNo`).
class LessonRef {
  const LessonRef(this.sourceDocumentId, this.lessonNo);

  final String sourceDocumentId;
  final int lessonNo;

  String get key => '$sourceDocumentId#$lessonNo';

  /// `null` khi context CHƯA giải ra bài (tầng Global/Subject/Book) — cùng
  /// luật A5: không đoán bài từ nửa context.
  static LessonRef? fromContext(LearningContext? c) =>
      (c != null && c.hasLesson)
          ? LessonRef(c.sourceDocumentId!, c.lessonNo!)
          : null;

  @override
  bool operator ==(Object other) =>
      other is LessonRef &&
      other.sourceDocumentId == sourceDocumentId &&
      other.lessonNo == lessonNo;

  @override
  int get hashCode => Object.hash(sourceDocumentId, lessonNo);

  @override
  String toString() => key;
}

/// Ai/cái gì đã tạo ra ánh xạ này.
enum BindingSource {
  /// Đọc thẳng từ fixture/TSL (trường có sẵn trong dữ liệu).
  fixture,

  /// Người biên soạn, có cơ sở trích dẫn được (TSL block ids).
  curated,

  /// Máy suy ra bằng luật tất định (chưa có binding nào loại này).
  derived,
}

/// Xuất xứ của CHÍNH ánh xạ (không phải của nội dung).
class BindingProvenance {
  const BindingProvenance({
    required this.curatedBy,
    required this.basis,
    this.note,
  });

  /// Ai/lane nào, ngày nào.
  final String curatedBy;

  /// Trỏ về dữ liệu nguồn kiểm lại được (vd id block TSL, số trang IN).
  final String basis;
  final String? note;
}

class SemanticBinding {
  const SemanticBinding({
    required this.activityId,
    required this.lessonRef,
    required this.methodIds,
    required this.bindingSource,
    required this.confidence,
    required this.provenance,
    this.conceptId,
    this.skillCaseId,
    this.status = 'PROPOSED',
  }) : assert(confidence >= 0 && confidence <= 1);

  /// Hoạt động của Mode 3 «Học với SAM» — một kịch bản cho mỗi bài.
  static const tutorScriptActivity = 'mode3:tutor-script';

  final String activityId;
  final LessonRef lessonRef;

  /// `null` = chưa quy được về khái niệm/ca ⇒ không giải được scope.
  final String? conceptId;
  final String? skillCaseId;

  /// ỨNG VIÊN — chưa phải phép. Xem [resolveBinding].
  final List<String> methodIds;

  final BindingSource bindingSource;
  final double confidence;
  final BindingProvenance provenance;

  /// Mọi binding hôm nay là PROPOSED (D2). Không có giá trị nào khác được
  /// dùng cho tới khi Founder duyệt.
  final String status;
}

/// Mục chương trình TỐI THIỂU mà một binding trỏ vào — đủ để dựng
/// `TutorScope.forProblem` (khái niệm, ca, vị trí học, catalogue phương pháp).
/// Tách khỏi `SliceCurriculum` (đường camera Toán 5) — không đăng ký vào
/// `curriculumForProblem`, nên đường chụp bài không đổi hành vi.
class BindingCurriculum {
  const BindingCurriculum({
    required this.conceptId,
    required this.cases,
    required this.stage,
    required this.catalogue,
  });

  final String conceptId;
  final List<SkillCase> cases;
  final LearningStage stage;
  final List<TeachingMethod> catalogue;

  bool hasCase(String id) => cases.any((c) => c.id == id);
}

/// Kết quả giải một binding: scope + phương pháp ĐƯỢC PHÉP + lý do loại.
class ResolvedBinding {
  const ResolvedBinding({
    required this.binding,
    required this.scope,
    required this.allowedMethods,
    required this.refusals,
  });

  final SemanticBinding binding;

  /// `null` khi không dựng được scope (không curriculum / không khái niệm).
  final TutorScope? scope;

  /// Giao của ba điều kiện — xem doc đầu tệp. Rỗng = binding fail closed
  /// cho mọi act mang NỘI DUNG; act không cần phương pháp vẫn có thể chạy
  /// nếu [scope] tồn tại.
  final List<TeachingMethod> allowedMethods;

  /// Mã lý do, đọc được, cố định để test: `NO_CURRICULUM`, `NO_CONCEPT`,
  /// `NO_SKILL_CASE`, `CASE_NOT_IN_CURRICULUM:<id>`,
  /// `METHOD_NOT_IN_SCOPE:<id>`, `METHOD_NOT_SOURCE_STATED:<id>`,
  /// `METHOD_NOT_DECLARED_IN_BINDING:<id>`.
  final List<String> refusals;

  bool get hasScope => scope != null;
  bool get permitsContent => allowedMethods.isNotEmpty;
}

/// ⭐⭐ RETRIEVED ≠ PERMITTED cho binding. Thuần, tất định.
ResolvedBinding resolveBinding(
    SemanticBinding b, BindingCurriculum? curriculum) {
  final refusals = <String>[];
  if (curriculum == null) {
    return ResolvedBinding(
        binding: b,
        scope: null,
        allowedMethods: const [],
        refusals: const ['NO_CURRICULUM']);
  }
  final concept = b.conceptId;
  if (concept == null || concept != curriculum.conceptId) {
    return ResolvedBinding(
        binding: b,
        scope: null,
        allowedMethods: const [],
        refusals: const ['NO_CONCEPT']);
  }
  final caseId = b.skillCaseId;
  if (caseId == null) refusals.add('NO_SKILL_CASE');
  if (caseId != null && !curriculum.hasCase(caseId)) {
    refusals.add('CASE_NOT_IN_CURRICULUM:$caseId');
  }
  final effectiveCase =
      (caseId != null && curriculum.hasCase(caseId)) ? caseId : null;
  // Ca không xác định ⇒ TutorScope.forProblem trả [] (fail closed sẵn).
  final scope = TutorScope.forProblem(
      concept, effectiveCase, curriculum.stage, curriculum.catalogue);

  final allowed = <TeachingMethod>[];
  for (final m in scope.allowedMethods) {
    if (!b.methodIds.contains(m.id)) {
      refusals.add('METHOD_NOT_DECLARED_IN_BINDING:${m.id}');
      continue;
    }
    final p = m.provenance;
    if (p == null ||
        p.origin != KnowledgeOrigin.sourceStated ||
        !p.citableAsTextbookFact) {
      refusals.add('METHOD_NOT_SOURCE_STATED:${m.id}');
      continue;
    }
    allowed.add(m);
  }
  for (final id in b.methodIds) {
    if (!scope.allowedMethods.any((m) => m.id == id)) {
      refusals.add('METHOD_NOT_IN_SCOPE:$id');
    }
  }
  return ResolvedBinding(
      binding: b, scope: scope, allowedMethods: allowed, refusals: refusals);
}
