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
    this.skillCaseId,
  });

  final String id;
  final String name;
  final Set<String> appliesToConcepts;

  /// ⭐ Ca mà phương pháp này xử lý.
  ///
  /// Đây là lỗ hổng của bản trước: phương pháp chỉ gate theo **lớp**, mà bằng
  /// chứng cho thấy phải gate theo **ca**. Một phương pháp đúng về toán học
  /// nhưng sai ca thì không được tới tay Tutor — cũng nghiêm như chưa được dạy.
  ///
  /// ⚠️ F2 (siết 2026-09-01): `null` KHÔNG còn nghĩa "áp cho mọi ca". Một
  /// phương pháp không khai ca chỉ dùng được ở mức duyệt-khái-niệm
  /// ([TutorScope.forConcept]); trong phạm vi MỘT BÀI CỤ THỂ nó bị loại với
  /// [MethodRejection.caseNotDeclared]. Lý do: wildcard là cửa sau đưa một
  /// phương pháp quy đồng tới bài cùng-mẫu-số — đúng lỗi F2, chỉ khác đường
  /// vào. Phương pháp thật sự áp mọi ca thì khai TỪNG ca một cách tường minh.
  final String? skillCaseId;

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

  /// ⭐ Đúng về toán học nhưng **không áp cho ca của bài này**.
  notApplicableToCase,

  /// Không xác định được ca ⇒ **fail closed**, không đoán.
  caseUnknown,

  /// ⭐ F2 — phương pháp KHÔNG KHAI ca thì không được vào phạm vi một bài cụ
  /// thể. "Không khai" là một dạng unknown, và unknown fail closed.
  caseNotDeclared,
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

  /// ⭐⭐ AVAILABLE_TO_TUTOR = APPLICABLE_TO_PROBLEM ∩ PEDAGOGICALLY_ALLOWED
  ///
  /// [exerciseCase] `null` ⇒ **không xác định được ca** ⇒ trả tập RỖNG. Fail
  /// closed. Tutor không nhận gì và phải nói "chưa chắc" — thà im còn hơn dạy
  /// một phương pháp cho sai loại bài.
  static TutorScope forProblem(
    String concept,
    String? exerciseCase,
    LearningStage stage,
    List<TeachingMethod> catalogue, {
    Set<String> prerequisiteScope = const {},
  }) =>
      TutorScope(
        targetConcept: concept,
        allowedMethods: exerciseCase == null
            ? const []
            : [
                for (final m in catalogue)
                  if (eligibilityForProblem(m, concept, exerciseCase, stage)
                      .eligible)
                    m
              ],
        allowedTerminology: stage.terminologyIntroduced,
        prerequisiteScope: prerequisiteScope,
        stage: stage,
      );

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


/// ⭐⭐ Giao của hai điều kiện. **Fail closed** ở mọi nhánh không chắc.
///
/// Hai câu hỏi độc lập, và thiếu câu nào cũng loại:
///   ① phương pháp có áp cho CA của bài này không  (đúng về toán học)
///   ② học sinh đã được dạy nó chưa                (đúng về sư phạm)
MethodEligibility eligibilityForProblem(
  TeachingMethod m,
  String concept,
  String? exerciseCase,
  LearningStage stage,
) {
  if (exerciseCase == null) {
    return const MethodEligibility.rejected(MethodRejection.caseUnknown, {});
  }
  if (m.skillCaseId == null) {
    // ⭐ F2: wildcard bị đóng. Xem doc của [TeachingMethod.skillCaseId].
    return const MethodEligibility.rejected(
        MethodRejection.caseNotDeclared, {});
  }
  if (m.skillCaseId != exerciseCase) {
    return MethodEligibility.rejected(
        MethodRejection.notApplicableToCase, {exerciseCase});
  }
  return eligibilityOf(m, concept, stage);
}
