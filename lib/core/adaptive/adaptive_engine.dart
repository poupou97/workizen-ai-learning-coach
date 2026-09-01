/// ⭐ Adaptive Engine — từ bằng chứng ra **một** hành động, kèm lý do đọc được.
///
/// `reason` không phải để ghi log. Nó là **thứ Parent Coach hiển thị**. Một quyết định
/// không giải thích được thì không dùng được cho sản phẩm này — đó là lý do V1 không
/// dùng DKT, dù DKT có thể dự đoán tốt hơn.
library;

import '../curriculum/concept.dart';
import '../curriculum/pedagogical_boundary.dart';
import '../curriculum/problem_applicability.dart';
import '../curriculum/skill_case.dart';
import '../student/mastery.dart';

/// Ca của một bài phân số, suy ra TẤT ĐỊNH từ hai mẫu số.
///
/// Đây là chỗ *"đúng về toán học"* và *"đúng về sư phạm"* gặp nhau: điều kiện là
/// thuộc tính của BÀI TOÁN, còn được phép dùng phương pháp nào là thuộc tính của
/// HỌC SINH. Hàm này chỉ trả lời vế thứ nhất.
/// F2 (siết 2026-09-01): nay chỉ là bề mặt tương thích của
/// [analyzeFractionPair] — phân tích đầy đủ (gcd/lcm/bốn ca biên) nằm ở
/// `problem_applicability.dart`, nơi mọi kết luận truy vết được về cấu trúc
/// toán học thật thay vì một phép chia lấy dư.
String? fractionCase(int d1, int d2) => analyzeFractionPair(d1, d2)?.skillCase;

/// ⭐ Chọn ca để ĐỐI CHIẾU khi chẩn đoán `caseTransitionGap`.
///
/// Bản trước lấy `b.strong.first` — phần tử đầu theo **thứ tự chèn của Map**.
/// Câu nói với phụ huynh (*"con đã làm tốt dạng X"*) do đó phụ thuộc vào việc ai
/// thêm ca nào vào map trước, chứ không phải vào sư phạm. Với hai ca thì không lộ;
/// với ba ca trở lên thì nêu nhầm ca.
///
/// Thứ tự ưu tiên:
///   ① ca vững được dạy GẦN NHẤT TRƯỚC ca đang vướng (theo `introducedGrade`) —
///      đó mới là ca mà "luật đổi" so với nó;
///   ② nếu không có dữ liệu lớp: ca nhiều bằng chứng nhất, rồi theo id.
///      Tất định — không phụ thuộc thứ tự chèn.
String? contrastCaseFor({
  required List<String> strong,
  required String currentCase,
  required ConceptMastery mastery,
  List<SkillCase> caseCatalogue = const [],
}) {
  if (strong.isEmpty) return null;

  final byId = {for (final c in caseCatalogue) c.id: c};
  final currentGrade = byId[currentCase]?.introducedGrade;

  if (currentGrade != null) {
    final adjacent = strong
        .where((s) {
          final g = byId[s]?.introducedGrade;
          return g != null && g <= currentGrade;
        })
        .toList()
      ..sort((a, b) {
        final ga = byId[a]!.introducedGrade!, gb = byId[b]!.introducedGrade!;
        return ga != gb ? gb.compareTo(ga) : a.compareTo(b);
      });
    if (adjacent.isNotEmpty) return adjacent.first;
  }

  final fallback = [...strong]
    ..sort((a, b) {
      final ea = mastery.cases[a]?.evidenceCount ?? 0;
      final eb = mastery.cases[b]?.evidenceCount ?? 0;
      return eb != ea ? eb.compareTo(ea) : a.compareTo(b);
    });
  return fallback.first;
}

class AdaptiveDecision {
  const AdaptiveDecision({
    required this.diagnosis,
    required this.action,
    required this.reason,
    required this.scope,
    required this.remediation,
  });

  final DiagnosticOutcome diagnosis;
  final LearningAction action;
  final String reason;
  final TutorScope scope;
  final RemediationStatus? remediation;
}

/// Luật chẩn đoán. Cố ý là **luật**, không phải mô hình học được — để giải thích được,
/// kiểm toán được, và chạy được với **một** học sinh từ ngày đầu.
AdaptiveDecision decide({
  required String conceptId,
  required String? exerciseCase,
  required ConceptMastery mastery,
  required LearningStage stage,
  required List<TeachingMethod> catalogue,
  List<SkillCase> caseCatalogue = const [],
  double strongAt = 0.85,
  double weakBelow = 0.6,
}) {
  final scope =
      TutorScope.forProblem(conceptId, exerciseCase, stage, catalogue);

  // ⭐ Không biết ca ⇒ không chẩn đoán. Fail closed, và nói ra.
  if (exerciseCase == null) {
    return AdaptiveDecision(
      diagnosis: DiagnosticOutcome.insufficientEvidence,
      action: LearningAction.diagnosePrerequisite,
      reason: 'Chưa xác định được dạng bài nên chưa thể nói con vướng ở đâu.',
      scope: scope,
      remediation: RemediationStatus.diagnosticConfidenceLow,
    );
  }

  final b = mastery.caseBreakdown(strongAt: strongAt);
  final here = mastery.cases[exerciseCase];
  final hereWeak = here == null || !here.hasEvidence || here.pMastery < weakBelow;

  // ⭐⭐ Ca đang gặp còn yếu NHƯNG có ca khác đã vững ⇒ không phải hỏng khái niệm.
  if (hereWeak && b.strong.isNotEmpty) {
    final contrast = contrastCaseFor(
      strong: b.strong,
      currentCase: exerciseCase,
      mastery: mastery,
      caseCatalogue: caseCatalogue,
    );
    return AdaptiveDecision(
      diagnosis: DiagnosticOutcome.caseTransitionGap,
      action: LearningAction.contrastCases,
      reason: 'Con đã làm tốt dạng "$contrast". Bài này là dạng khác: '
          '"$exerciseCase". Cùng so hai dạng nhé.',
      scope: scope,
      remediation: RemediationStatus.remediateAvailable,
    );
  }

  if (hereWeak && b.strong.isEmpty && b.weak.isNotEmpty) {
    return AdaptiveDecision(
      diagnosis: DiagnosticOutcome.conceptGap,
      action: LearningAction.teach,
      reason: 'Chưa dạng nào của "$conceptId" vững, nên quay lại từ đầu.',
      scope: scope,
      remediation: RemediationStatus.remediateAvailable,
    );
  }

  if (here != null && here.hasEvidence && here.pMastery >= strongAt) {
    return AdaptiveDecision(
      diagnosis: DiagnosticOutcome.executionError,
      action: LearningAction.practice,
      reason: 'Con nắm cách làm dạng này rồi — nhiều khả năng chỉ nhầm khi tính.',
      scope: scope,
      remediation: null,
    );
  }

  return AdaptiveDecision(
    diagnosis: DiagnosticOutcome.insufficientEvidence,
    action: LearningAction.diagnosePrerequisite,
    reason: 'Chưa đủ dữ kiện để kết luận. Hỏi thêm vài câu ngắn đã.',
    scope: scope,
    remediation: RemediationStatus.diagnosticConfidenceLow,
  );
}
