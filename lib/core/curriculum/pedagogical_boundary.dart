/// ⭐ P0 INVARIANT — RANH GIỚI SƯ PHẠM.
///
/// > *AI Tutor MUST NOT introduce a concept, terminology, method, or shortcut
/// > merely because the foundation model knows it.*
///
/// Đây là chỗ **đúng về toán học** và **đúng về sư phạm** tách nhau. Chúng
/// không phải một thứ, và model nền chỉ biết loại thứ nhất.
///
/// Ca đã đo trên corpus thật (Toán 5 KNTT, 53 trang OCR): sách dạy mẫu số chung
/// = **tích hai mẫu số**; `BCNN` xuất hiện **0 lần**. Model tổng quát hỏi
/// `3/4 + 2/5` gần như chắc chắn chọn BCNN — nhanh hơn, "toán học hơn", và
/// **ngoài chương trình** với đứa trẻ đang ngồi trước màn hình.
///
/// Nên biên giới đặt ở đây, nơi kiểu dữ liệu giữ: Tutor **không nhận** một
/// method rồi tự hỏi có được dùng không. Nó chỉ nhận **tập method đã được lọc**.
library;

/// Vị trí học tập hiện tại — thứ quyết định cái gì được phép dùng.
///
/// Không phải "trình độ" của đứa trẻ. Là **đã đi tới đâu trong sách nào**.
class LearningStage {
  const LearningStage({
    required this.grade,
    required this.bookSeries,
    required this.lessonId,
    required this.conceptsIntroduced,
    required this.methodsIntroduced,
    required this.terminologyIntroduced,
  });

  final int grade;
  final String bookSeries;

  /// Bài học sinh đang ở — không phải bài khó nhất từng làm được.
  final String lessonId;

  final Set<String> conceptsIntroduced;
  final Set<String> methodsIntroduced;

  /// ⭐ Từ vựng tách riêng khỏi khái niệm. Đo được từ corpus: Toán 5 KNTT dùng
  /// `rút gọn` / `phân số tối giản`; cụm `phân số bằng nhau` xuất hiện **0 lần**.
  /// Một method đúng nhưng gọi tên bằng từ đứa trẻ chưa gặp vẫn là dạy sai.
  final Set<String> terminologyIntroduced;
}

class TeachingMethod {
  const TeachingMethod({
    required this.id,
    required this.name,
    required this.appliesToConcepts,
    required this.requiresConcepts,
    required this.requiresTerminology,
  });

  final String id;
  final String name;
  final Set<String> appliesToConcepts;

  /// Khái niệm phải ĐÃ được giới thiệu thì method mới dùng được.
  /// `bcnn-common-denominator` đòi `bcnn` — lớp 5 KNTT chưa có.
  final Set<String> requiresConcepts;
  final Set<String> requiresTerminology;
}

/// Vì sao một method bị loại. Trả lý do chứ không chỉ `false` — Parent Coach
/// phải giải thích được, và người sửa lỗi cũng vậy.
enum MethodRejection {
  notApplicable,
  conceptNotIntroduced,
  terminologyNotIntroduced,
  notInCurriculumForStage,
}

class MethodEligibility {
  const MethodEligibility.allowed()
      : eligible = true,
        rejection = null,
        missing = const {};
  const MethodEligibility.rejected(this.rejection, this.missing)
      : eligible = false;

  final bool eligible;
  final MethodRejection? rejection;
  final Set<String> missing;
}

MethodEligibility eligibilityOf(
  TeachingMethod m,
  String concept,
  LearningStage stage,
) {
  if (!m.appliesToConcepts.contains(concept)) {
    return const MethodEligibility.rejected(MethodRejection.notApplicable, {});
  }
  final missingConcepts = m.requiresConcepts.difference(stage.conceptsIntroduced);
  if (missingConcepts.isNotEmpty) {
    return MethodEligibility.rejected(
        MethodRejection.conceptNotIntroduced, missingConcepts);
  }
  final missingTerms =
      m.requiresTerminology.difference(stage.terminologyIntroduced);
  if (missingTerms.isNotEmpty) {
    return MethodEligibility.rejected(
        MethodRejection.terminologyNotIntroduced, missingTerms);
  }
  if (!stage.methodsIntroduced.contains(m.id)) {
    return const MethodEligibility.rejected(
        MethodRejection.notInCurriculumForStage, {});
  }
  return const MethodEligibility.allowed();
}

/// ⭐ Thứ **duy nhất** Tutor được nhận.
///
/// `allowedMethods` là `required` và **không có mặc định** — cùng doctrine với
/// `FlowTrigger` ở Workizen Hub, nơi một mặc định tưởng vô hại đã mở đường cho
/// entry point OS tiêu tiền mà không ai bấm gì. Ở đây, mặc định "cho phép mọi
/// method" sẽ để model nền dạy BCNN cho học sinh lớp 5 — và không test nào bắt
/// được, vì câu trả lời **đúng về toán học**.
class TutorScope {
  const TutorScope({
    required this.targetConcept,
    required this.allowedMethods,
    required this.allowedTerminology,
    required this.prerequisiteScope,
    required this.stage,
  });

  final String targetConcept;
  final List<TeachingMethod> allowedMethods;
  final Set<String> allowedTerminology;
  final Set<String> prerequisiteScope;
  final LearningStage stage;

  static TutorScope forConcept(
    String concept,
    LearningStage stage,
    List<TeachingMethod> catalogue, {
    Set<String> prerequisiteScope = const {},
  }) =>
      TutorScope(
        targetConcept: concept,
        allowedMethods: [
          for (final m in catalogue)
            if (eligibilityOf(m, concept, stage).eligible) m
        ],
        allowedTerminology: stage.terminologyIntroduced,
        prerequisiteScope: prerequisiteScope,
        stage: stage,
      );
}
