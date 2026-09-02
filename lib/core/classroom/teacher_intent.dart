/// WAL-106 — TeacherIntent: ngữ cảnh giáo viên, KHÔNG phải Student Truth.
///
/// «Tuần này lớp học quy đồng» là một TUYÊN BỐ CÓ NGUỒN + CÓ HẠN — nó ảnh
/// hưởng Agenda như một tín hiệu, và tuyệt đối không sửa mastery/claim/
/// evidence. Cấu trúc này bảo đảm điều đó bằng KIỂU: không có API nào ở đây
/// nhận hay trả ConceptSummary/ConceptMastery — chỉ phát AgendaSignal.
///
/// expiry BẮT BUỘC (không nullable): intent không hạn là doctrine trôi —
/// cùng bài học QR-permanent. Hết hạn ⇒ im lặng, không cần ai dọn.
library;

import '../agenda/learning_agenda.dart';

enum TeacherIntentKind { focusThisWeek, extraPractice, prepareAssessment }

class TeacherIntent {
  const TeacherIntent({
    required this.teacherId,
    required this.conceptId,
    required this.subjectId,
    required this.kind,
    required this.statedAt,
    required this.expiry,
    this.skillCaseId,
    this.studentId,
  });

  final String teacherId;
  final String conceptId;
  final String subjectId;
  final TeacherIntentKind kind;
  final DateTime statedAt;

  /// BẮT BUỘC — sau thời điểm này intent tự im lặng.
  final DateTime expiry;

  final String? skillCaseId;

  /// `null` = intent mức LỚP; có giá trị = intent cho MỘT học sinh.
  final String? studentId;

  bool activeAt(DateTime now) =>
      !now.isBefore(statedAt) && now.isBefore(expiry);
}

/// Độ mạnh tín hiệu teacher-intent — NGANG learnStrength (0.6), cố ý DƯỚI
/// reviewDue/weakCase/overdue: giáo viên định hướng kế hoạch lớp, nhưng
/// không đảo được ưu tiên sư phạm khẩn của CHÍNH đứa trẻ (câu trả lời cho
/// research question delta L — cùng triết lý timetable-chỉ-ưu-tiên-hoá F4,
/// ở đây intent được là một tín hiệu thật vì nó CÓ NỘI DUNG sư phạm).
const teacherIntentStrength = 0.6;

/// Phát tín hiệu Agenda từ intents — thuần, chỉ đọc.
/// [studentId] để lọc intent mức-học-sinh; intent mức-lớp áp cho mọi em.
List<AgendaSignal> teacherIntentSignals(
  List<TeacherIntent> intents, {
  required DateTime now,
  required String studentId,
}) =>
    [
      for (final i in intents)
        if (i.activeAt(now) && (i.studentId == null || i.studentId == studentId))
          AgendaSignal(
            kind: AgendaSignalKind.teacherIntent,
            conceptId: i.conceptId,
            subjectId: i.subjectId,
            strength: teacherIntentStrength,
            action: switch (i.kind) {
              TeacherIntentKind.focusThisWeek => AgendaActionKind.learn,
              TeacherIntentKind.extraPractice => AgendaActionKind.practice,
              TeacherIntentKind.prepareAssessment => AgendaActionKind.retrieve,
            },
            reason: switch (i.kind) {
              TeacherIntentKind.focusThisWeek =>
                'Thầy cô cho biết tuần này lớp học phần này.',
              TeacherIntentKind.extraPractice =>
                'Thầy cô gợi ý con luyện thêm phần này.',
              TeacherIntentKind.prepareAssessment =>
                'Sắp có bài kiểm tra phần này — tự làm thử để chắc bài.',
            },
            skillCaseId: i.skillCaseId,
          )
    ];
