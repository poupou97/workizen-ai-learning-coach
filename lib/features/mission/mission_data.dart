/// ⭐ WAL-51 — dữ liệu màn "Hôm nay": LẮP TỪ DOMAIN THẬT, không mock hình dáng.
///
/// Luật slice 1 (WAL-48 AC): UI chỉ tiêu thụ AdaptiveDecision / ReviewState /
/// ConceptSummary đang có — file này là bằng chứng: fixture chạy ĐÚNG các hàm
/// domain (decide, reviewStateOf, ConceptSummary.of), không bịa cấu trúc mới.
library;

import '../../core/adaptive/adaptive_engine.dart';
import '../../core/knowledge/slice_curriculum.dart';
import '../../core/store/learner_profile.dart';
import '../../core/store/learner_store.dart';
import '../learning_session/slice_flow.dart' show masteryFromStore;
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

/// Bó domain demo dùng chung giữa màn Hôm nay và flow camera.
class DemoDomain {
  const DemoDomain({
    required this.mastery,
    required this.stage,
    required this.catalogue,
    required this.cases,
  });
  final ConceptMastery mastery;
  final LearningStage stage;
  final List<TeachingMethod> catalogue;
  final List<SkillCase> cases;
}

/// Fixture "Minh, lớp 5, giữa Bài 6" — đúng golden scenario của repo:
/// vững ca chia-hết (lớp 4), CHƯA GẶP ca không-chia-hết ⇒ caseTransitionGap.
DemoDomain buildDemoDomain({DateTime? now}) {
  final t = now ?? DateTime(2026, 9, 1, 19);
  const p = BktParams.freeResponse;
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

  final divisible =
      replayMastery(log('denominator-divisible', 3, const Duration(days: 30)), p);
  return DemoDomain(
    mastery: ConceptMastery(conceptId: 'quy-dong', cases: {
      'denominator-divisible': divisible,
      'denominator-non-divisible':
          CaseMastery.initial('denominator-non-divisible', p),
    }),
    stage: const LearningStage(
      grade: 5, bookSeries: 'kntt', lessonId: 'toan5-t1-bai6',
      conceptsIntroduced: {'phan-so', 'chia-het', 'nhan-so-tu-nhien'},
      methodsIntroduced: {'common-denom-take-larger', 'common-denom-by-product'},
      terminologyIntroduced: {'mẫu số chung'},
    ),
    catalogue: const [
      TeachingMethod(
          id: 'common-denom-by-product',
          name: 'Lấy mẫu số chung là tích hai mẫu số',
          appliesToConcepts: {'quy-dong'},
          skillCaseId: 'denominator-non-divisible',
          requiresConcepts: {'phan-so', 'nhan-so-tu-nhien'},
          requiresTerminology: {'mẫu số chung'}),
    ],
    cases: const [
      SkillCase(id: 'denominator-divisible', conceptId: 'quy-dong',
          condition: 'một mẫu số chia hết cho mẫu số còn lại', introducedGrade: 4),
      SkillCase(id: 'denominator-non-divisible', conceptId: 'quy-dong',
          condition: 'hai mẫu số không chia hết cho nhau', introducedGrade: 5),
    ],
  );
}

MissionData buildDemoMission({DateTime? now}) {
  final t = now ?? DateTime(2026, 9, 1, 19);
  const names = {
    'denominator-divisible': 'một mẫu số chia hết cho mẫu kia',
    'denominator-non-divisible': 'hai mẫu số không chia hết cho nhau',
    'denominator-equal': 'hai mẫu số bằng nhau',
  };
  final domain = buildDemoDomain(now: t);
  final mastery = domain.mastery;
  final divisible = mastery.cases['denominator-divisible']!;

  final decision = decide(
    conceptId: 'quy-dong',
    exerciseCase: 'denominator-non-divisible',
    mastery: mastery,
    stage: domain.stage,
    catalogue: domain.catalogue,
    caseCatalogue: domain.cases,
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

/// ⭐ WAL-108 — mission «Hôm nay» từ KHO THẬT: replay bằng chứng của learner
/// NÀY (không fixture), decide/review/unobserved đều sinh từ trạng thái đó.
/// Vòng khép kín: học xong → recordSession → màn Hôm nay đổi theo — đo được.
///
/// Grade ngoài phạm vi slice ⇒ fail closed: nói thẳng «chưa có nội dung»,
/// KHÔNG mượn nội dung lớp 5 dạy lớp khác.
Future<MissionData> buildMissionFromStore({
  required LearnerProfile profile,
  required LearnerStore store,
  DateTime? now,
}) async {
  final t = now ?? DateTime.now();
  final c = curriculumFor(profile);
  if (c == null) {
    final stage = LearningStage(
      grade: profile.grade,
      bookSeries: profile.bookSeries ?? 'chua-ro',
      lessonId: 'chua-co-noi-dung',
      conceptsIntroduced: const {},
      methodsIntroduced: const {},
      terminologyIntroduced: const {},
    );
    final d = decide(
      conceptId: 'quy-dong',
      exerciseCase: null,
      mastery: const ConceptMastery(conceptId: 'quy-dong', cases: {}),
      stage: stage,
      catalogue: const [],
    );
    return MissionData(
      studentName: profile.displayName,
      decision: d,
      nextActionTitle:
          'SAM chưa có nội dung lớp ${profile.grade} — sắp có nhé',
      reviews: const [],
      unobservedCaseNames: const [],
    );
  }

  final mastery = await masteryFromStore(store, profile.learnerId, c);
  final names = {for (final sc in c.cases) sc.id: sc.condition};

  final decision = decide(
    conceptId: c.conceptId,
    exerciseCase: 'denominator-non-divisible', // mục tiêu của Bài 6
    mastery: mastery,
    stage: c.stage,
    catalogue: c.catalogue,
    caseCatalogue: c.cases,
  );
  final summary =
      ConceptSummary.of(mastery, knownCaseIds: {...names.keys}, now: t);

  final reviews = <ReviewItem>[];
  for (final sc in c.cases) {
    final m = mastery.cases[sc.id];
    if (m == null || !m.hasEvidence) continue;
    final r = reviewStateOf(m, t);
    if (r.urgency == ReviewUrgency.reviewDue ||
        r.urgency == ReviewUrgency.overdue) {
      reviews.add(ReviewItem(
          displayName: 'Quy đồng — ${names[sc.id]!}', urgency: r.urgency));
    }
  }

  return MissionData(
    studentName: profile.displayName,
    decision: decision,
    nextActionTitle: switch (decision.diagnosis) {
      DiagnosticOutcome.caseTransitionGap => 'Hôm nay mình thử dạng mới nhé',
      DiagnosticOutcome.executionError => 'Luyện thêm cho chắc tay',
      _ => 'Cùng SAM tìm hiểu tiếp nhé',
    },
    reviews: reviews,
    unobservedCaseNames: [
      for (final id in summary.unobservedCases)
        if (names.containsKey(id)) names[id]!
    ],
  );
}
