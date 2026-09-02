/// WAL-114 — LINEAGE end-to-end: từ MỘT LearningEvent truy ngược về ĐÚNG
/// TRANG SÁCH nguồn, trả lời 7 chiều WHAT/WHERE/WHY/HOW/SOURCE/AUTHORITY/
/// PERMISSION — hoặc FAIL CLOSED với mã vi phạm cụ thể.
///
/// Đây là kiểm-tra-lúc-truy-vấn (defense in depth): scope đã gate lúc dạy,
/// nhưng dữ liệu LƯU rồi vẫn phải chứng minh lại được — evidence cũ có thể
/// tới từ policy cũ, catalogue đổi, hay dữ liệu hỏng. Không chứng minh được
/// thì KHÔNG kể chuyện nguồn cho phụ huynh («thà im còn hơn trích dẫn sai»).
library;

import '../curriculum/pedagogical_boundary.dart';
import '../student/learning_evidence.dart';
import '../tutor/teaching_provenance.dart';
import 'provenance.dart';

/// Mức thẩm quyền khi kể lại cho người dùng — ánh xạ TẤT ĐỊNH từ
/// [KnowledgeOrigin]; mọi thứ không phải sách-nói/sách-làm-mẫu đều là
/// SAM_INFERRED (kể cả sourceSequence: thứ tự mục lục KHÔNG phải lời sách).
enum TeachingAuthority { sourceExplicit, sourceDemonstrated, samInferred }

TeachingAuthority authorityFor(KnowledgeOrigin? origin) => switch (origin) {
      KnowledgeOrigin.sourceStated => TeachingAuthority.sourceExplicit,
      KnowledgeOrigin.sourceDemonstrated => TeachingAuthority.sourceDemonstrated,
      _ => TeachingAuthority.samInferred,
    };

/// 5+1 điều kiện fail-closed của WAL-114 (mỗi cái một test đỏ khi vi phạm).
enum LineageViolation {
  /// Sự kiện không gắn can thiệp dạy nào — không có lineage dạy để kể.
  noTeachingIntervention,

  /// interventionId trỏ tới method KHÔNG tồn tại trong catalogue
  /// (provenance mismatch — dữ liệu và tri thức lệch nhau).
  methodUnknown,

  /// Method tồn tại nhưng KHÔNG nằm trong APPLICABLE∩ALLOWED của scope.
  methodNotAllowed,

  /// Method không khai nguồn — không có gì để trích.
  missingSource,

  /// Nguồn thuộc LỚP CAO HƠN stage hiện tại (future-knowledge leakage).
  futureKnowledge,

  /// Method không áp cho concept của scope (curriculum conflict).
  curriculumConflict,
}

class LineageResult {
  const LineageResult._(this.trace, this.violation);
  const LineageResult.ok(LineageTrace t) : this._(t, null);
  const LineageResult.fail(LineageViolation v) : this._(null, v);
  final LineageTrace? trace;
  final LineageViolation? violation;
  bool get proven => trace != null;
}

/// Vết truy nguồn ĐẦY ĐỦ của một teaching interaction — in được thành JSON.
class LineageTrace {
  const LineageTrace({
    required this.eventId,
    required this.skillCaseId,
    required this.what,
    required this.stage,
    required this.teaching,
    required this.supportLevel,
    required this.policyId,
    this.knowledgeVersion,
  });

  final String eventId;
  final String skillCaseId;
  final String what; // targetConcept
  final LearningStage stage; // WHERE
  final TeachingProvenance teaching; // HOW/WHY/SOURCE/AUTHORITY (mint duy nhất)
  final String supportLevel; // PERMISSION — nấc đã hiển thị
  final String policyId; // tutor policy version
  final String? knowledgeVersion; // knowledge model version

  TeachingAuthority get authority => authorityFor(teaching.authority);

  Map<String, Object?> toJson() {
    final src = teaching.source;
    return {
      'eventId': eventId,
      'what': {'conceptId': what, 'skillCaseId': skillCaseId},
      'where': {
        'grade': stage.grade,
        'lessonId': stage.lessonId,
        'bookSeries': stage.bookSeries,
      },
      'how': {
        'methodId': teaching.method.id,
        'methodName': teaching.method.name,
      },
      'why': teaching.methodReason,
      'source': src == null
          ? null // authority=samInferred ⇒ KHÔNG có citation — không bịa
          : {
              'sourceDocumentId': src.sourceId,
              // ⚠️ trang IN TRÊN SÁCH — đúng hệ quy chiếu trích dẫn cho người.
              'pagePrinted': src.pageStart,
              'pageEnd': src.pageEnd,
              'origin': src.origin.name,
              'extractionMethod': src.extractionMethod,
            },
      'authority': authority.name,
      'permission': {
        'supportLevel': supportLevel,
        'allowedByScope': true, // đã qua kiểm — fail thì không có trace
      },
      'versions': {
        'tutorPolicy': policyId,
        'knowledgeModel': knowledgeVersion,
      },
      'sourceLineForChild': teaching.sourceLineForChild,
    };
  }
}

/// Truy lineage cho MỘT sự kiện. [catalogue] là tri thức hiện có; [scope] là
/// quyền sư phạm tại ngữ cảnh bài. Trả về trace ĐÃ CHỨNG MINH hoặc mã vi phạm.
LineageResult lineageFor({
  required LearningEvent e,
  required List<TeachingMethod> catalogue,
  required TutorScope scope,
}) {
  final iid = e.interventionId;
  if (iid == null) {
    return const LineageResult.fail(LineageViolation.noTeachingIntervention);
  }
  // interventionId = '<policyId>/<methodId>@<level>' (interventionIdFor).
  final slash = iid.indexOf('/');
  final at = iid.lastIndexOf('@');
  if (slash <= 0 || at <= slash) {
    return const LineageResult.fail(LineageViolation.methodUnknown);
  }
  final policyId = iid.substring(0, slash);
  final methodId = iid.substring(slash + 1, at);
  final level = iid.substring(at + 1);

  TeachingMethod? m;
  for (final c in catalogue) {
    if (c.id == methodId) m = c;
  }
  if (m == null) return const LineageResult.fail(LineageViolation.methodUnknown);

  // Kiểm ĐỘC LẬP từng điều kiện — thứ tự cố định để test đỏ đúng mã.
  if (m.provenance == null) {
    return const LineageResult.fail(LineageViolation.missingSource);
  }
  final srcGrade = m.provenance!.grade;
  if (srcGrade != null && srcGrade > scope.stage.grade) {
    return const LineageResult.fail(LineageViolation.futureKnowledge);
  }
  if (!m.appliesToConcepts.contains(scope.targetConcept)) {
    return const LineageResult.fail(LineageViolation.curriculumConflict);
  }
  // ALLOWED cuối cùng — mint qua explainTeaching (mint DUY NHẤT, không nhân
  // bản luật): null ⇒ method không nằm trong scope.allowedMethods.
  final tp = explainTeaching(
      scope: scope, methodId: methodId, exerciseCase: e.skillCaseId);
  if (tp == null) {
    return const LineageResult.fail(LineageViolation.methodNotAllowed);
  }

  return LineageResult.ok(LineageTrace(
    eventId: e.eventId,
    skillCaseId: e.skillCaseId,
    what: scope.targetConcept,
    stage: scope.stage,
    teaching: tp,
    supportLevel: level,
    policyId: policyId,
    knowledgeVersion: e.knowledgeVersion,
  ));
}
