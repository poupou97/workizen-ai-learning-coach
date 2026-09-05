/// WAL-95×97 — nối SURFACE với KHO: mọi lượt học thành một LearningSession.
///
/// Đây là mắt xích còn thiếu của vòng khép kín: surface phát sự kiện (có đủ
/// lineage), recorder gói thành phiên và ghi MỘT LẦN vào store. Không màn nào
/// tự ghi kho — một chỗ ghi, một chỗ chịu trách nhiệm.
///
/// Bất biến giữ bằng test:
/// - Không có sự kiện nào ⇒ KHÔNG tạo phiên rỗng (không rác lịch sử).
/// - Phiên ASSESS ghi xong phải SẠCH: nếu lẫn hỗ trợ, [recordSession] trả về
///   danh sách vi phạm để tầng trên xử lý — không im lặng nuốt.
library;

import '../../core/store/learner_store.dart';
import '../../core/store/learning_session.dart';
import '../../core/student/learning_evidence.dart';

class RecordedSession {
  const RecordedSession(this.session, this.violations, {this.appended = true});
  final LearningSession? session;

  /// Rỗng = sạch. Không rỗng = phiên thi bị nhiễm dạy học (F7).
  final List<LearningEvent> violations;

  /// ⭐ WAL-210 (audit C3) — `false` khi kho đã có phiên cùng `sessionId`
  /// (callback bắn hai lần / thử lại): không ghi thêm, không đếm kép.
  final bool appended;
}

Future<RecordedSession> recordSession({
  required LearnerStore store,
  required String learnerId,
  required String subjectId,
  required List<LearningEvent> events,
  required SessionTrigger trigger,
  SessionMode mode = SessionMode.learn,
  DateTime? startedAt,
  DateTime? endedAt,
}) async {
  if (events.isEmpty) return const RecordedSession(null, []);
  final start = startedAt ?? events.first.at;
  final session = LearningSession(
    sessionId: 's-$learnerId-${start.microsecondsSinceEpoch}',
    learnerId: learnerId,
    subjectId: subjectId,
    startedAt: start,
    endedAt: endedAt ?? events.last.at,
    trigger: trigger,
    mode: mode,
    conceptIds: {for (final e in events) ...e.conceptIds}.toList()..sort(),
    skillCaseIds: {for (final e in events) e.skillCaseId}.toList()..sort(),
    events: events,
  );
  final violations = tutoringViolationsInExam(session);
  final appended = await store.appendSession(session);
  return RecordedSession(session, violations, appended: appended);
}
