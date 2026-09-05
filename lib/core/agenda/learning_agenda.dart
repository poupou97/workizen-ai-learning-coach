/// WAL-102 — LEARNING AGENDA: «hôm nay con nên học gì?» (Founder §F, P0-2).
///
/// Kiến trúc signals→resolve (pattern OpenTutor đã audit): mỗi nguồn sự thật
/// sẵn có phát TÍN HIỆU có tên + độ mạnh + lý do; resolve chọn tín hiệu mạnh
/// nhất một cách tất định. KHÔNG có vòng tối ưu engagement nào ở đây — không
/// streak, không time-in-app, không session-count-target (§F cấm tường minh).
///
/// BẤT BIẾN:
/// - REST là output HẠNG NHẤT: không tín hiệu đủ mạnh ⇒ nghỉ, và nói lý do.
///   Học đủ nhịp hôm nay ⇒ nghỉ, kể cả khi còn tín hiệu.
/// - Thời khoá biểu chỉ ƯU TIÊN HOÁ trong nhóm tín hiệu ngang nhau (F4) —
///   không bao giờ thắng được một tín hiệu mạnh hơn hẳn.
/// - Không bao giờ đề xuất khái niệm ngoài [AgendaConceptInput.inStage].
/// - Mọi action truy được về tín hiệu sinh ra nó ([NextBestLearningAction.signal]).
library;

import '../context/learning_context.dart';
import '../lesson_model/next_action.dart' show WorkspaceView;
import '../store/timetable.dart';
import '../student/concept_summary.dart';
import '../student/review_schedule.dart';
import '../student/student_lesson_state.dart';
import 'lesson_next_action.dart';

/// 8 loại hành động của Founder Directive §F. Engine v1 phát 5 loại đầu;
/// `explain`/`transfer`/`assess` chờ TransferProbe (WAL-103) và Assignment —
/// khai sẵn để API không đổi khi chúng tới.
enum AgendaActionKind {
  learn,
  practice,
  review,
  retrieve,
  explain,
  transfer,
  assess,
  rest,
}

enum AgendaSignalKind {
  reviewOverdue,
  teacherIntent,
  reviewDue,
  weakCase,
  unobservedCoverage,
  noEvidenceInStage,
  supportedOnlyPractice,
  retrievalOpportunity,
}

/// Tham số — **có tên, có lý do, thay được** (doctrine ADR-004).
class AgendaPolicy {
  const AgendaPolicy({
    this.overdueStrength = 0.9,
    this.weakCaseStrength = 0.8,
    this.reviewDueStrength = 0.7,
    this.supportedOnlyStrength = 0.65,
    this.learnStrength = 0.6,
    this.coverageStrength = 0.55,
    this.retrievalStrength = 0.5,
    this.restBelow = 0.4,
    this.tieEpsilon = 0.05,
    this.cooldownFactor = 0.5,
    this.enoughSessionsToday = 3,
  });

  /// Thứ tự các mức là THỨ TỰ ƯU TIÊN SƯ PHẠM, không phải xác suất:
  /// quên-hẳn > ca-đang-hỏng > tới-hạn-ôn > lệ-thuộc-gợi-ý > học-mới >
  /// phủ-ca-chưa-quan-sát > lấy-lại-độc-lập. Khoảng cách giữa các mức đủ
  /// lớn hơn [tieEpsilon] để timetable không đảo được ưu tiên sư phạm.
  final double overdueStrength;
  final double weakCaseStrength;
  final double reviewDueStrength;
  final double supportedOnlyStrength;
  final double learnStrength;
  final double coverageStrength;
  final double retrievalStrength;

  /// Dưới ngưỡng này không tín hiệu nào đáng gọi trẻ vào bàn — REST.
  final double restBelow;

  /// Trong epsilon coi là NGANG NHAU — chỉ khi đó timetable mới được xếp lại
  /// (F4: reorder-only). 0.05 < mọi khoảng cách giữa hai mức ưu tiên.
  final double tieEpsilon;

  /// Khái niệm ĐÃ học hôm nay bị giảm nửa độ mạnh — chống nhồi một chỗ,
  /// không phải chống học: tín hiệu rất mạnh (overdue 0.9→0.45) vẫn vượt
  /// [restBelow] nếu thật sự khẩn.
  final double cooldownFactor;

  /// Đủ nhịp hôm nay ⇒ REST kể cả còn tín hiệu. 3 phiên/ngày — neo vào
  /// nhịp bài-tập-về-nhà tiểu học VN, GIẢ THUYẾT chờ dữ liệu (không phải
  /// mục tiêu để tối ưu LÊN — là TRẦN, không phải sàn).
  final int enoughSessionsToday;
}

/// Đầu vào cho MỘT khái niệm — tất cả từ nguồn sự thật đã có.
class AgendaConceptInput {
  const AgendaConceptInput({
    required this.conceptId,
    required this.subjectId,
    required this.summary,
    this.worstReview = ReviewUrgency.nothingToReview,
    this.inStage = true,
    this.studiedToday = false,
  });

  final String conceptId;
  final String subjectId;
  final ConceptSummary summary;

  /// Khẩn cấp ôn XẤU NHẤT trên các ca của khái niệm (từ [reviewStateOf]).
  final ReviewUrgency worstReview;

  /// Khái niệm có nằm trong LearningStage hiện tại không. `false` ⇒ engine
  /// KHÔNG BAO GIỜ đề xuất — kể cả tín hiệu mạnh (không dạy vượt chương trình).
  final bool inStage;

  /// Đã có phiên về khái niệm này hôm nay ⇒ cooldown.
  final bool studiedToday;
}

class AgendaSignal {
  const AgendaSignal({
    required this.kind,
    required this.conceptId,
    required this.subjectId,
    required this.strength,
    required this.action,
    required this.reason,
    this.skillCaseId,
  });

  final AgendaSignalKind kind;
  final String conceptId;
  final String subjectId;

  /// Sau cooldown — số cuối cùng resolve dùng.
  final double strength;

  final AgendaActionKind action;
  final String reason;
  final String? skillCaseId;
}

class NextBestLearningAction {
  const NextBestLearningAction({
    required this.kind,
    required this.reason,
    this.conceptId,
    this.skillCaseId,
    this.signal,
  });

  final AgendaActionKind kind;

  /// Lý do đọc được cho trẻ/phụ huynh — không có action câm.
  final String reason;

  final String? conceptId;
  final String? skillCaseId;

  /// Tín hiệu sinh ra action — audit trail. `null` CHỈ với REST.
  final AgendaSignal? signal;

  /// ⭐ WAL-210 round 3 (Founder A8) — hành động tiếp theo CHO MỘT BÀI
  /// (Đọc / Trực quan / Học với SAM / bài tiếp / mục lục) từ Student
  /// Knowledge State + Learning Context + luật sư phạm. Uỷ quyền cho
  /// [nextBestLessonAction]; tài liệu: ROUND3-RUNTIME-CONTRACTS.md §A8.
  static LessonNextAction forLesson({
    required StudentLessonState state,
    required LearningContext context,
    required LessonSummary lesson,
    required Set<WorkspaceView> viewsSeen,
  }) =>
      nextBestLessonAction(
          state: state, context: context, lesson: lesson, viewsSeen: viewsSeen);
}

/// Phát tín hiệu cho một khái niệm. Thuần — không đọc đồng hồ, không I/O.
List<AgendaSignal> signalsFor(
  AgendaConceptInput c, {
  AgendaPolicy policy = const AgendaPolicy(),
}) {
  if (!c.inStage) return const []; // ngoài chương trình ⇒ im lặng tuyệt đối

  final out = <AgendaSignal>[];
  final s = c.summary;
  void add(AgendaSignalKind kind, double raw, AgendaActionKind action,
      String reason, {String? skillCaseId}) {
    out.add(AgendaSignal(
      kind: kind,
      conceptId: c.conceptId,
      subjectId: c.subjectId,
      strength: c.studiedToday ? raw * policy.cooldownFactor : raw,
      action: action,
      reason: reason,
      skillCaseId: skillCaseId,
    ));
  }

  switch (c.worstReview) {
    case ReviewUrgency.overdue:
      add(AgendaSignalKind.reviewOverdue, policy.overdueStrength,
          AgendaActionKind.review, 'Đã quá hạn ôn khá lâu — gặp lại kẻo quên.');
    case ReviewUrgency.reviewDue:
      add(AgendaSignalKind.reviewDue, policy.reviewDueStrength,
          AgendaActionKind.review, 'Tới hạn ôn theo lịch giãn cách.');
    case ReviewUrgency.fresh:
    case ReviewUrgency.nothingToReview:
      break;
  }

  switch (s.claim) {
    case ConceptClaim.needsWork:
      add(AgendaSignalKind.weakCase, policy.weakCaseStrength,
          AgendaActionKind.practice,
          'Có dạng bài đang hỏng — luyện đúng chỗ đó.',
          skillCaseId: s.weakestObservedCases.isEmpty
              ? null
              : s.weakestObservedCases.first);
    case ConceptClaim.noEvidence:
      add(AgendaSignalKind.noEvidenceInStage, policy.learnStrength,
          AgendaActionKind.learn,
          'Trong chương trình nhưng chưa học đến — bắt đầu thôi.');
    case ConceptClaim.insufficientEvidence:
      if (s.supportedPracticeCount > 0) {
        add(AgendaSignalKind.supportedOnlyPractice,
            policy.supportedOnlyStrength, AgendaActionKind.retrieve,
            'Con mới luyện với gợi ý — thử một bài tự làm để có bằng chứng thật.');
      }
    case ConceptClaim.strongOnObserved:
      if (s.unobservedCases.isNotEmpty) {
        add(AgendaSignalKind.unobservedCoverage, policy.coverageStrength,
            AgendaActionKind.practice,
            'Vững các dạng đã gặp, còn dạng chưa thử — thử dạng mới.',
            skillCaseId: s.unobservedCases.first);
      }
    case ConceptClaim.developing:
      add(AgendaSignalKind.retrievalOpportunity, policy.retrievalStrength,
          AgendaActionKind.retrieve,
          'Đang tiến bộ — một bài tự làm hôm nay giúp nhớ lâu hơn.');
    case ConceptClaim.mastered:
      break; // transfer-probe là việc của WAL-103, không bịa trước
  }
  return out;
}

/// Resolve tất định: mạnh nhất thắng; trong nhóm ngang nhau (±tieEpsilon)
/// thời khoá biểu CHỈ ĐƯỢC XẾP LẠI; hoà nữa thì (kind-ordinal, conceptId).
NextBestLearningAction resolveAgenda(
  List<AgendaConceptInput> concepts, {
  required DateTime today,
  int sessionsToday = 0,
  List<TimetableEntry> timetable = const [],

  /// Tín hiệu từ nguồn ngoài học-trạng (vd teacherIntentSignals — WAL-106).
  /// Đi qua CÙNG một resolve: không nguồn nào có đường tắt quanh ưu tiên.
  List<AgendaSignal> extraSignals = const [],
  AgendaPolicy policy = const AgendaPolicy(),
}) {
  if (sessionsToday >= policy.enoughSessionsToday) {
    return NextBestLearningAction(
      kind: AgendaActionKind.rest,
      reason: 'Hôm nay con học đủ $sessionsToday phiên rồi — nghỉ là một phần '
          'của học. Mai gặp lại nhé!',
    );
  }

  final signals = [
    for (final c in concepts)
      ...signalsFor(c, policy: policy),
    ...extraSignals,
  ]..sort((a, b) {
      if (a.strength != b.strength) return b.strength.compareTo(a.strength);
      if (a.kind.index != b.kind.index) return a.kind.index - b.kind.index;
      return a.conceptId.compareTo(b.conceptId);
    });

  if (signals.isEmpty || signals.first.strength < policy.restBelow) {
    return const NextBestLearningAction(
      kind: AgendaActionKind.rest,
      reason: 'Không có gì gấp hôm nay — nghỉ ngơi cũng là học. '
          'SAM sẽ gọi con khi tới hạn ôn.',
    );
  }

  // nhóm dẫn đầu: mọi tín hiệu trong tieEpsilon của đỉnh — CHỈ nhóm này
  // được timetable xếp lại (F4: reorder-only, không thêm không bớt).
  final top = signals.first.strength;
  final leaders = [
    for (final s in signals)
      if (top - s.strength <= policy.tieEpsilon) s
  ];
  final ordered = prioritiseByTimetable<AgendaSignal>(
    leaders,
    entries: timetable,
    day: today,
    subjectOf: (s) => s.subjectId,
  );
  final winner = ordered.first;

  return NextBestLearningAction(
    kind: winner.action,
    conceptId: winner.conceptId,
    skillCaseId: winner.skillCaseId,
    reason: winner.reason,
    signal: winner,
  );
}
