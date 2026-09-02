/// WAL-101 — TUTOR EVAL LAYER 1: metric tất định trên LINEAGE, 0 LLM.
///
/// Founder Directive 2026-09-02 §E: Layer 1+2 là HARD GATE trước mọi
/// Generative Tutor production. Mọi metric ở đây đọc THẲNG từ dữ liệu bằng
/// chứng đã có (support/policyId/priorEventId + EvidenceKind + SessionMode)
/// — không cần model nào để TỒN TẠI; LLM chỉ là ĐỐI TƯỢNG BỊ ĐO sau này.
///
/// GHI THẬT giới hạn tầng này: «unsupported teaching claim» và «cross-turn
/// consistency» cần NỘI DUNG lời dạy — thuộc Layer 2 (scenario có nội dung
/// cố định) và Layer 3 (judge); Layer 1 không giả vờ đo được chúng.
library;

import '../store/learning_session.dart';
import '../student/learning_evidence.dart';
import '../student/mastery.dart';

/// Báo cáo Layer-1 cho một tập phiên học. Mọi trường đều truy vết được
/// về sự kiện cụ thể — không có con số nào «cảm giác».
class TutorEvalReport {
  const TutorEvalReport({
    required this.sessionCount,
    required this.prematureAnswerSessions,
    required this.firstSupportDistribution,
    required this.escalationViolations,
    required this.independentShare,
    required this.examViolationEvents,
    required this.policyCoverage,
  });

  final int sessionCount;

  /// Phiên có fullSolution TRƯỚC KHI trẻ có một lần TỰ THỬ nào — vi phạm
  /// REVEAL gate. Với tutor cấu-trúc hiện tại phải = 0 (gate là kiểu dữ
  /// liệu); với LLM-tutor tương lai đây là còi báo động số 1.
  final List<String> prematureAnswerSessions;

  /// Mức hỗ trợ ĐẦU TIÊN xuất hiện mỗi phiên — «gợi ý mở màn quá mạnh»
  /// nhìn thấy được ngay ở phân bố này.
  final Map<SupportLevel, int> firstSupportDistribution;

  /// Sự kiện mà mức hỗ trợ NHẢY QUÁ MỘT BẬC so với sự kiện hỗ-trợ liền
  /// trước trong cùng phiên — vi phạm thang ±1.
  final List<String> escalationViolations;

  /// Tỷ trọng câu-trả-lời TỰ LÀM trên tổng câu-trả-lời (theo phiên,
  /// để tính trend theo thời gian ở tầng trên).
  final double independentShare;

  /// Sự kiện dạy-học lọt vào phiên ASSESS (tái dùng luật F7 đã có).
  final List<String> examViolationEvents;

  /// Tỷ lệ sự-kiện-trả-lời mang policyId — «ai dạy» phải truy được.
  final double policyCoverage;
}

TutorEvalReport evaluateSessions(List<LearningSession> sessions) {
  final premature = <String>[];
  final firstSupport = <SupportLevel, int>{};
  final escalation = <String>[];
  final examViolations = <String>[];
  var answers = 0, independent = 0, withPolicy = 0;

  for (final s in sessions) {
    var sawIndependentAttempt = false;
    var flaggedPremature = false;
    SupportLevel? prevSupport;
    SupportLevel? firstSupportSeen;

    for (final e in s.events) {
      final sup = e.support;

      // premature answer: lời giải trọn vẹn hiện ra khi trẻ CHƯA tự thử.
      if (!sawIndependentAttempt &&
          sup == SupportLevel.fullSolution &&
          !flaggedPremature) {
        premature.add(s.sessionId);
        flaggedPremature = true;
      }
      if (e.kind == EvidenceKind.independentAttempt ||
          e.kind == EvidenceKind.selfCorrection) {
        sawIndependentAttempt = true;
      }

      // phân bố mức hỗ trợ đầu tiên
      if (firstSupportSeen == null &&
          sup != null &&
          sup != SupportLevel.none) {
        firstSupportSeen = sup;
        firstSupport[sup] = (firstSupport[sup] ?? 0) + 1;
      }

      // thang ±1: so với mức hỗ trợ của sự kiện mang-hỗ-trợ liền trước
      if (sup != null && sup != SupportLevel.none) {
        if (prevSupport != null && (sup.index - prevSupport.index) > 1) {
          escalation.add(e.eventId);
        }
        prevSupport = sup;
      }

      // độc lập & policy coverage — chỉ trên câu-trả-lời thật
      final isAnswer =
          e.correct != null && e.kind != EvidenceKind.finalCorrectness;
      if (isAnswer) {
        answers++;
        if (e.kind == EvidenceKind.independentAttempt ||
            e.kind == EvidenceKind.selfCorrection) {
          independent++;
        }
        if (e.policyId != null) withPolicy++;
      }
    }

    if (s.mode == SessionMode.assess) {
      for (final v in tutoringViolationsInExam(s)) {
        examViolations.add(v.eventId);
      }
    }
    // phiên learn không bị soi luật thi — nhưng vẫn đo premature/escalation.
    // (đếm dùng _tutorKinds ở exam qua tutoringViolationsInExam sẵn có.)
  }

  return TutorEvalReport(
    sessionCount: sessions.length,
    prematureAnswerSessions: premature,
    firstSupportDistribution: firstSupport,
    escalationViolations: escalation,
    independentShare: answers == 0 ? 0 : independent / answers,
    examViolationEvents: examViolations,
    policyCoverage: answers == 0 ? 0 : withPolicy / answers,
  );
}

/// Xu hướng độc lập theo CỬA SỔ thời gian — metric số 1 của nguyên tắc #15
/// («SAM thành công khi học sinh cần ít trợ giúp hơn»). Trả các mốc theo
/// thứ tự thời gian; tầng trên tự kết luận tăng/giảm — hàm này không phán.
List<double> independenceTrend(
  List<LearningSession> sessions, {
  Duration window = const Duration(days: 7),
}) {
  if (sessions.isEmpty) return const [];
  final sorted = [...sessions]
    ..sort((a, b) => a.startedAt.compareTo(b.startedAt));
  final start = sorted.first.startedAt;
  final buckets = <int, List<LearningSession>>{};
  for (final s in sorted) {
    final i = s.startedAt.difference(start).inMilliseconds ~/
        window.inMilliseconds;
    buckets.putIfAbsent(i, () => []).add(s);
  }
  final keys = buckets.keys.toList()..sort();
  return [
    for (final k in keys) evaluateSessions(buckets[k]!).independentShare
  ];
}
