/// ⭐ WAL-51 — dữ liệu màn "Hôm nay": LẮP TỪ DOMAIN THẬT, không mock hình dáng.
///
/// Luật slice 1 (WAL-48 AC): UI chỉ tiêu thụ AdaptiveDecision / ReviewState /
/// ConceptSummary đang có — file này là bằng chứng: fixture chạy ĐÚNG các hàm
/// domain (decide, reviewStateOf, ConceptSummary.of), không bịa cấu trúc mới.
library;

import '../../core/adaptive/adaptive_engine.dart';
import '../../core/agenda/learning_agenda.dart';
import '../../core/knowledge/slice_curriculum.dart';
import '../../core/store/learner_profile.dart';
import '../../core/store/learner_store.dart';
import '../../core/store/timetable.dart';
import '../learning_session/slice_flow.dart' show masteryFromStore;
import '../../core/curriculum/pedagogical_boundary.dart';
import '../../core/curriculum/skill_case.dart';
import '../../core/student/concept_summary.dart';
import '../../core/student/evidence_validation.dart';
import '../../core/student/evidence_weighting.dart';
import '../../core/student/learning_evidence.dart';
import '../../core/student/mastery.dart';
import '../../core/adaptive/review_priority.dart';
import '../../core/student/review_schedule.dart';
import '../subjects/lesson_index.dart';

/// Một mục ôn — tên hiển thị + độ khẩn (sự việc từ lịch) + MỨC ƯU TIÊN và
/// CÂU CHỮ do resolver quyết (WAL-164 / Founder D2).
///
/// UI KHÔNG tự suy từ một câu sai: nó hiển thị `reason` mà resolver đưa.
class ReviewItem {
  const ReviewItem({
    required this.displayName,
    required this.urgency,
    this.priority = ReviewPriority.normal,
    this.reason = '',
    this.becauseOfError = false,
    this.subjectId,
  });
  final String displayName;

  /// WAL-175 — môn của việc ôn này. Cần để BẰNG CHỨNG thắng THỜI KHOÁ BIỂU khi
  /// SAM đề nghị ý định ở đúng cuốn sách đó (Convergence §10).
  final String? subjectId;
  final ReviewUrgency urgency;
  final ReviewPriority priority;
  final String reason;
  final bool becauseOfError;
}

/// Toàn bộ dữ liệu màn Hôm nay.
class MissionData {
  const MissionData({
    required this.studentName,
    required this.decision,
    required this.nextActionTitle,
    required this.reviews,
    required this.unobservedCaseNames,
    this.agenda,
    this.upcomingSubjects = const [],
    this.scaleLessonCount = 0,
    this.nextActionReason,
  });

  final String studentName;
  final AdaptiveDecision decision;

  /// ⭐ WAL-210 item G2 — số bài mở được từ SGK (đường Scale) khi lớp này
  /// KHÔNG có chương trình sư phạm (Deep). `> 0` ⇒ thẻ Home nói con số thật
  /// và «Bắt đầu» mở Môn học, không mở camera. `0` = không biết / không có.
  final int scaleLessonCount;

  /// Lý do trẻ đọc được cho thẻ khi KHÔNG có agenda lẫn decision đáng nói
  /// (lớp chỉ có đường Scale). `null` ⇒ UI dùng `decision.reason` như cũ.
  final String? nextActionReason;

  /// WAL-138 — «Việc SAM đề xuất» qua resolveAgenda (WAL-102): REST là
  /// first-class. `null` = đường demo/fixture cũ ⇒ UI rơi về decision card.
  final NextBestLearningAction? agenda;

  /// Môn có tiết HÔM NAY theo TKB (rỗng = không hiện khu «Sắp tới» — F13).
  final List<String> upcomingSubjects;

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
        // ⭐ ROUND 4 (strict default, A-runtime R4.2–R4.4): các sự kiện MẪU
        // này mô phỏng câu trả lời Deep (phân số) mà `fraction-check-v1`
        // chấm — đóng đúng dấu của validator đó để fixture đi cùng luật đọc
        // nghiêm ngặt như dữ liệu thật. DEMO ≠ dữ liệu học sinh: domain này
        // chỉ dựng cho màn demo/camera-demo/Tonight-demo, không vào kho.
        validation: const EvidenceValidation(
            validatorId: 'fraction-check-v1', validatorVersion: '1'),
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
            urgency: review.urgency,
            // fixture demo là Toán — không có `SliceCurriculum` ở nhánh này.
            subjectId: 'toan'),
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
///
/// ⭐ WAL-210 item G2: [index] = mục lục pack của lớp (`null` khi chưa nạp).
/// Lớp KHÔNG có chương trình Deep nhưng CÓ bài mở được từ SGK ⇒ thẻ nói
/// «Có N bài để học ở Môn học» với N THẬT từ pack — trước đây nói «chưa có
/// nội dung» rồi «Bắt đầu» mở camera, dù KHTN 6 mở được từ giá sách.
Future<MissionData> buildMissionFromStore({
  required LearnerProfile profile,
  required LearnerStore store,
  DateTime? now,
  LessonIndex? index,
}) async {
  final t = now ?? DateTime.now();
  final all = curriculaForLearner(profile);
  final c = all.length == 1 ? all.single : null;
  if (c == null) {
    final scaleCount = index?.openableLessonCount ?? 0;
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
      nextActionTitle: scaleCount > 0
          ? 'Có $scaleCount bài để học ở Môn học'
          : 'SAM chưa có nội dung lớp ${profile.grade} — sắp có nhé',
      nextActionReason: scaleCount > 0
          ? 'SAM chưa có bài dạy riêng cho lớp ${profile.grade}, nhưng con '
              'mở được $scaleCount bài từ sách giáo khoa — đọc, làm thí '
              'nghiệm, viết. Vào Môn học nhé.'
          : null,
      scaleLessonCount: scaleCount,
      reviews: const [],
      unobservedCaseNames: const [],
    );
  }

  final mastery = await masteryFromStore(store, profile.learnerId, c);
  final names = {for (final sc in c.cases) sc.id: sc.condition};

  // ── AGENDA (WAL-102): tín hiệu từ SỰ THẬT trong kho + TKB + nhịp hôm nay ──
  final tt = await store.timetable(profile.learnerId);
  final todaySessions =
      await store.sessions(learnerId: profile.learnerId, onDay: t);
  final summaryForAgenda = ConceptSummary.of(mastery,
      knownCaseIds: {for (final sc in c.cases) sc.id}, now: t);
  var worst = ReviewUrgency.nothingToReview;
  for (final m in mastery.cases.values) {
    if (!m.hasEvidence) continue;
    final r = reviewStateOf(m, t);
    if (r.urgency.index > worst.index) worst = r.urgency;
  }
  final agenda = resolveAgenda(
    [
      AgendaConceptInput(
        conceptId: c.conceptId,
        subjectId: c.subjectId,
        summary: summaryForAgenda,
        worstReview: worst,
        studiedToday: todaySessions.isNotEmpty,
      ),
    ],
    today: t,
    sessionsToday: todaySessions.length,
    timetable: tt,
  );

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

  // WAL-164 (Founder D2): mission KHÔNG tự suy ưu tiên nữa — nó tiêu thụ
  // resolver. Lịch giãn cách vẫn là SỰ VIỆC (urgency); resolver quyết mức và
  // câu chữ. `prerequisiteCaseIds` để RỖNG vì chưa có nguồn tiền-đề-của-bài
  // đáng tin; bịa ra nó là mở đường cho mức `today` nổ bậy.
  final candidates = resolveReviewCandidates(mastery: mastery, now: t);
  final reviews = <ReviewItem>[];
  for (final cand in candidates) {
    final name = names[cand.skillCaseId];
    final m = mastery.cases[cand.skillCaseId];
    if (name == null || m == null) continue;
    reviews.add(ReviewItem(
      displayName: 'Quy đồng — $name',
      urgency: reviewStateOf(m, t).urgency,
      priority: cand.priority,
      reason: cand.reason,
      becauseOfError: cand.becauseOfError,
      subjectId: c.subjectId,
    ));
  }

  return MissionData(
    studentName: profile.displayName,
    decision: decision,
    agenda: agenda,
    upcomingSubjects: subjectsOn(tt, t),
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
