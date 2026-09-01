/// ⭐ WAL-51 — dữ liệu màn "Hôm nay": LẮP TỪ DOMAIN THẬT, không mock hình dáng.
///
/// Luật slice 1 (WAL-48 AC): UI chỉ tiêu thụ AdaptiveDecision / ReviewState /
/// ConceptSummary đang có — file này là bằng chứng: fixture chạy ĐÚNG các hàm
/// domain (decide, reviewStateOf, ConceptSummary.of), không bịa cấu trúc mới.
library;

import '../../core/adaptive/adaptive_engine.dart';
import '../../core/curriculum/pedagogical_boundary.dart';
import '../../core/curriculum/skill_case.dart';
import '../../core/student/concept_summary.dart';
import '../../core/student/evidence_weighting.dart';
import '../../core/student/learning_evidence.dart';
import '../../core/student/mastery.dart';
import '../../core/student/review_schedule.dart';

/// Một mục ôn tới hạn — tên hiển thị + độ khẩn từ ReviewSchedule.
class ReviewItem {
  const ReviewItem({required this.displayName, required this.urgency});
  final String displayName;
  final ReviewUrgency urgency;
}

/// Toàn bộ dữ liệu màn Hôm nay.
class MissionData {
  const MissionData({
    required this.studentName,
    required this.decision,
    required this.nextActionTitle,
    required this.reviews,
    required this.unobservedCaseNames,
  });

  final String studentName;
  final AdaptiveDecision decision;

  /// Tiêu đề thẻ hành động — dịch từ diagnosis, KHÔNG phải id nội bộ.
  final String nextActionTitle;
  final List<ReviewItem> reviews;

  /// Thử-thách-phủ: dạng CHƯA từng thử (ConceptSummary.unobservedCases → tên sách).
  final List<String> unobservedCaseNames;
}

/// Fixture "Minh, lớp 5, giữa Bài 6" — đúng golden scenario của repo:
/// vững ca chia-hết (lớp 4), CHƯA GẶP ca không-chia-hết ⇒ caseTransitionGap.
MissionData buildDemoMission({DateTime? now}) {
  final t = now ?? DateTime(2026, 9, 1, 19);
  const p = BktParams.freeResponse;
  const names = {
    'denominator-divisible': 'một mẫu số chia hết cho mẫu kia',
    'denominator-non-divisible': 'hai mẫu số không chia hết cho nhau',
    'denominator-equal': 'hai mẫu số bằng nhau',
  };

  // Bằng chứng qua ĐƯỜNG THẬT: log sự kiện → replay (không đặt tay pMastery).
  EvidenceLog log(String caseId, int n, Duration age) {
    var l = EvidenceLog.empty(caseId);
    for (var i = 0; i < n; i++) {
      l = l.append(LearningEvent(
        eventId: 'demo:$caseId:$i',
        skillCaseId: caseId,
        kind: EvidenceKind.independentAttempt,
        correct: true,
        at: t.subtract(age).add(Duration(minutes: i)),
      ));
    }
    return l;
  }

  final divisible = replayMastery(log('denominator-divisible', 3, const Duration(days: 30)), p);
  final mastery = ConceptMastery(conceptId: 'quy-dong', cases: {
    'denominator-divisible': divisible,
    'denominator-non-divisible': CaseMastery.initial('denominator-non-divisible', p),
  });

  const stage = LearningStage(
    grade: 5, bookSeries: 'kntt', lessonId: 'toan5-t1-bai6',
    conceptsIntroduced: {'phan-so', 'chia-het', 'nhan-so-tu-nhien'},
    methodsIntroduced: {'common-denom-take-larger', 'common-denom-by-product'},
    terminologyIntroduced: {'mẫu số chung'},
  );
  const catalogue = [
    TeachingMethod(
        id: 'common-denom-by-product', name: 'Lấy mẫu số chung là tích hai mẫu số',
        appliesToConcepts: {'quy-dong'}, skillCaseId: 'denominator-non-divisible',
        requiresConcepts: {'phan-so', 'nhan-so-tu-nhien'},
        requiresTerminology: {'mẫu số chung'}),
  ];
  const cases = [
    SkillCase(id: 'denominator-divisible', conceptId: 'quy-dong',
        condition: 'một mẫu số chia hết cho mẫu số còn lại', introducedGrade: 4),
    SkillCase(id: 'denominator-non-divisible', conceptId: 'quy-dong',
        condition: 'hai mẫu số không chia hết cho nhau', introducedGrade: 5),
  ];

  final decision = decide(
    conceptId: 'quy-dong',
    exerciseCase: 'denominator-non-divisible',
    mastery: mastery,
    stage: stage,
    catalogue: catalogue,
    caseCatalogue: cases,
  );

  final summary = ConceptSummary.of(mastery,
      knownCaseIds: {...names.keys}, now: t);

  final review = reviewStateOf(divisible, t);

  return MissionData(
    studentName: 'Minh',
    decision: decision,
    nextActionTitle: switch (decision.diagnosis) {
      DiagnosticOutcome.caseTransitionGap => 'Hôm nay mình thử dạng mới nhé',
      DiagnosticOutcome.executionError => 'Luyện thêm cho chắc tay',
      _ => 'Cùng SAM tìm hiểu tiếp nhé',
    },
    reviews: [
      if (review.urgency == ReviewUrgency.reviewDue ||
          review.urgency == ReviewUrgency.overdue)
        ReviewItem(
            displayName: 'Quy đồng — ${names['denominator-divisible']!}',
            urgency: review.urgency),
    ],
    unobservedCaseNames: [
      for (final id in summary.unobservedCases)
        if (names.containsKey(id)) names[id]!
    ],
  );
}
