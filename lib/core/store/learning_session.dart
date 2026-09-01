/// WAL-95 — LearningSession: một lần ngồi học, LƯU MỘT LẦN.
///
/// Founder Task Order §5-6: lịch sử phải xem được theo NGÀY / theo MÔN / theo
/// TRI THỨC — nhưng **không nhân bản bản ghi**. Ở đây session lưu một lần với
/// đủ khoá (ngày qua [startedAt], môn qua [subjectId], tri thức qua
/// [conceptIds]/[skillCaseIds]); ba view là PHÉP CHIẾU, không phải ba kho.
///
/// §12: EXAM ≠ LEARN. [ExamSession] không phải class riêng mà là [mode]:
/// cùng một loại bản ghi, khác CHÍNH SÁCH — và chính sách đó phải kiểm được
/// (xem `assertNoTutoringDuringExam`).
library;

import '../student/learning_evidence.dart';
import '../student/mastery.dart';

/// Vì sao phiên này bắt đầu. Giả thuyết V1 — tên chưa đóng băng (lệnh §5).
enum SessionTrigger {
  manual,
  reviewDue,
  cameraHomework,
  samRecommendation,
  timetablePrep,
  assessment,
}

/// LEARN cho phép dạy; ASSESS thì không — ranh giới đi vào dữ liệu, không chỉ UI.
enum SessionMode { learn, assess }

class LearningSession {
  const LearningSession({
    required this.sessionId,
    required this.learnerId,
    required this.subjectId,
    required this.startedAt,
    required this.trigger,
    this.mode = SessionMode.learn,
    this.endedAt,
    this.conceptIds = const [],
    this.skillCaseIds = const [],
    this.events = const [],
  });

  final String sessionId;
  final String learnerId;
  final String subjectId;
  final DateTime startedAt;
  final DateTime? endedAt;
  final SessionTrigger trigger;
  final SessionMode mode;
  final List<String> conceptIds;
  final List<String> skillCaseIds;

  /// Sự kiện thô của phiên — nguồn sự thật; mastery luôn replay từ đây.
  final List<LearningEvent> events;

  Map<String, Object?> toJson() => {
        'sessionId': sessionId,
        'learnerId': learnerId,
        'subjectId': subjectId,
        'startedAt': startedAt.toIso8601String(),
        if (endedAt != null) 'endedAt': endedAt!.toIso8601String(),
        'trigger': trigger.name,
        'mode': mode.name,
        'conceptIds': conceptIds,
        'skillCaseIds': skillCaseIds,
        'events': [for (final e in events) _eventJson(e)],
      };

  static Map<String, Object?> _eventJson(LearningEvent e) => {
        'eventId': e.eventId,
        'skillCaseId': e.skillCaseId,
        'kind': e.kind.name,
        'at': e.at.toIso8601String(),
        if (e.correct != null) 'correct': e.correct,
        if (e.exerciseId != null) 'exerciseId': e.exerciseId,
        if (e.conceptIds.isNotEmpty) 'conceptIds': e.conceptIds,
        // ⭐ LINEAGE (§7) phải sống qua lưu-đọc, nếu không thì «đúng sau hint
        // nhỏ» lại lẫn với «đúng sau xem trọn lời giải» ngay khi khởi động lại.
        if (e.support != null) 'support': e.support!.name,
        if (e.policyId != null) 'policyId': e.policyId,
        if (e.priorEventId != null) 'priorEventId': e.priorEventId,
      };

  static LearningEvent? _eventFrom(Map<String, Object?> j) {
    final id = j['eventId'], caseId = j['skillCaseId'], kind = j['kind'],
        at = j['at'];
    if (id is! String || caseId is! String || kind is! String || at is! String) {
      return null;
    }
    final k = EvidenceKind.values.where((v) => v.name == kind);
    final parsedAt = DateTime.tryParse(at);
    if (k.isEmpty || parsedAt == null) return null;
    final s = j['support'];
    return LearningEvent(
      eventId: id,
      skillCaseId: caseId,
      kind: k.first,
      at: parsedAt,
      correct: j['correct'] as bool?,
      exerciseId: j['exerciseId'] as String?,
      conceptIds: [...?(j['conceptIds'] as List?)?.cast<String>()],
      // support khuyết ⇒ null (dữ liệu cũ), KHÔNG mặc định none — bất biến
      // «UNKNOWN không bao giờ thành một giá trị cụ thể».
      support: s is String
          ? SupportLevel.values.where((v) => v.name == s).firstOrNull
          : null,
      policyId: j['policyId'] as String?,
      priorEventId: j['priorEventId'] as String?,
    );
  }

  static LearningSession? fromJson(Map<String, Object?> j) {
    final id = j['sessionId'], learner = j['learnerId'],
        subject = j['subjectId'], started = j['startedAt'],
        trig = j['trigger'];
    if (id is! String || learner is! String || subject is! String ||
        started is! String || trig is! String) {
      return null;
    }
    final startedAt = DateTime.tryParse(started);
    final t = SessionTrigger.values.where((v) => v.name == trig);
    if (startedAt == null || t.isEmpty) return null;
    final modeName = j['mode'];
    final m = SessionMode.values.where((v) => v.name == modeName);
    final ended = j['endedAt'];
    return LearningSession(
      sessionId: id,
      learnerId: learner,
      subjectId: subject,
      startedAt: startedAt,
      endedAt: ended is String ? DateTime.tryParse(ended) : null,
      trigger: t.first,
      mode: m.isEmpty ? SessionMode.learn : m.first,
      conceptIds: [...?(j['conceptIds'] as List?)?.cast<String>()],
      skillCaseIds: [...?(j['skillCaseIds'] as List?)?.cast<String>()],
      events: [
        for (final e in (j['events'] as List? ?? const []))
          ?_eventFrom((e as Map).cast<String, Object?>())
      ],
    );
  }
}

/// ⭐ §12/F7 — bằng chứng thi KHÔNG được nhiễm dạy học. Trả danh sách sự kiện
/// vi phạm (rỗng = sạch). Là HÀM KIỂM ĐƯỢC, không phải lời dặn trong tài liệu:
/// phiên assess mà có sự kiện mang hỗ trợ hoặc loại-sự-kiện-của-tutor là hỏng.
List<LearningEvent> tutoringViolationsInExam(LearningSession s) {
  if (s.mode != SessionMode.assess) return const [];
  const tutorKinds = {
    EvidenceKind.hintRequested,
    EvidenceKind.hintShown,
    EvidenceKind.guidedAttempt,
    EvidenceKind.postHintSuccess,
  };
  return [
    for (final e in s.events)
      if (tutorKinds.contains(e.kind) ||
          (e.support != null && e.support != SupportLevel.none))
        e
  ];
}
