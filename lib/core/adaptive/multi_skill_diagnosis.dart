/// ⭐⭐ F6 — quy công / quy lỗi trên bài tập ĐA KỸ NĂNG.
///
/// Vấn đề ADR-003 §F6 gọi tên: trẻ sai `3/4 + 2/5`, engine cũ buộc phải quy
/// lỗi cho MỘT concept mà không có cách biểu diễn *"sai, nhưng chưa biết vì
/// thành phần nào trong ba"*. Quy lỗi sai địa chỉ tệ hơn không quy lỗi.
///
/// Hai hàm, hai câu hỏi khác nhau:
/// - [attributeEvidence] — sinh sự kiện THÔ cho log (đúng ⇒ công cho từng
///   thành phần theo giả định conjunctive; sai ⇒ GHI LẠI, không chấm);
/// - [attributeFailure] — chẩn đoán bài sai: lỗi nằm ở thành phần nào, hay
///   phải nói thật là chưa cô lập được.
library;

import '../curriculum/exercise_skill_map.dart';
import '../curriculum/pedagogical_boundary.dart';
import '../curriculum/skill_case.dart';
import '../student/learning_evidence.dart';
import '../student/evidence_validation.dart';
import '../student/mastery.dart';
import 'adaptive_engine.dart';

/// ⭐ Sinh sự kiện thô từ một lần làm bài đa kỹ năng. Log là nguồn sự thật
/// (F3) — kể cả bài sai cũng phải ĐƯỢC GHI, chỉ là không được chấm.
///
/// | Kết quả | Sự kiện mỗi thành phần | Được chấm? |
/// |---|---|---|
/// | đúng, tự làm     | `independentAttempt(true)`  | ✅ conjunctive: mọi thành phần đã chạy |
/// | đúng, sau gợi ý  | `postHintSuccess(true)`     | ❌ F3: can thiệp nhuộm bằng chứng |
/// | sai              | `finalCorrectness(false)`   | ❌ chưa biết lỗi ở đâu — chẩn đoán lo |
List<LearningEvent> attributeEvidence({
  required ExerciseSkillMap map,
  required bool correct,
  required bool independent,
  required DateTime at,
  ResponseFormat format = ResponseFormat.freeResponse,
  Duration? timeSpent,

  /// ⭐ Round 3 (A3): dấu validator của LẦN CHẤM gốc — hàm này chỉ FAN-OUT
  /// một kết quả đã chấm sang từng thành phần, không tự chấm; dấu đi theo.
  /// `null` = người gọi chưa đóng dấu ⇒ sự kiện đọc như dữ liệu cũ.
  EvidenceValidation? validation,
}) {
  final concepts = map.conceptIds;
  final kind = !correct
      ? EvidenceKind.finalCorrectness
      : independent
          ? EvidenceKind.independentAttempt
          : EvidenceKind.postHintSuccess;
  return [
    for (final r in map.requirements)
      LearningEvent(
        // ⭐ §G: eventId phải DUY NHẤT qua các lần làm — thiếu thời điểm thì
        // hai lần làm cùng bài sinh cùng id và hệ lưu trữ khử-trùng-lặp sẽ
        // nuốt mất lần sau (falsified bởi replay_audit_test trước khi vá).
        eventId:
            '${map.exerciseId}@${at.microsecondsSinceEpoch}:${r.conceptId}:${r.skillCaseId}',
        skillCaseId: r.skillCaseId,
        conceptIds: concepts,
        exerciseId: map.exerciseId,
        kind: kind,
        correct: correct,
        at: at,
        format: format,
        timeSpent: timeSpent,
        validation: validation,
      ),
  ];
}

/// Kết quả chẩn đoán một bài đa kỹ năng bị SAI.
class MultiSkillDecision {
  const MultiSkillDecision({
    required this.diagnosis,
    required this.action,
    required this.reason,
    required this.implicatedCases,
    this.delegated,
  });

  final DiagnosticOutcome diagnosis;
  final LearningAction action;
  final String reason;

  /// Các ca bị nghi — SORT tất định (doctrine F4). Rỗng khi không nghi ca nào.
  final List<String> implicatedCases;

  /// Khi lỗi cô lập được về MỘT thành phần: quyết định đơn-kỹ-năng đầy đủ
  /// cho thành phần đó (tái dùng `decide` — không chép luật).
  final AdaptiveDecision? delegated;
}

/// ⭐⭐ Bài sai: tìm thành phần lỗi, hoặc NÓI THẬT là chưa cô lập được.
///
/// Luật loại trừ — giải thích được, không cần mô hình CD:
///   ① mọi thành phần đều vững        ⇒ lỗi thực thi (số học/cẩu thả);
///   ② đúng MỘT thành phần không vững ⇒ nghi phạm duy nhất, chẩn đoán sâu
///                                       bằng `decide` cho riêng nó;
///   ③ ≥2 thành phần không vững       ⇒ `attributionUnresolved` — hỏi từng
///                                       kỹ năng RIÊNG, không đoán.
MultiSkillDecision attributeFailure({
  required ExerciseSkillMap map,
  required Map<String, ConceptMastery> masteryByConcept,
  required LearningStage stage,
  required List<TeachingMethod> catalogue,
  List<SkillCase> caseCatalogue = const [],
  double strongAt = 0.85,
}) {
  // Không có hàng Q-matrix ⇒ không biết bài chạm gì ⇒ fail closed.
  if (map.isEmpty) {
    return const MultiSkillDecision(
      diagnosis: DiagnosticOutcome.insufficientEvidence,
      action: LearningAction.diagnosePrerequisite,
      reason: 'Chưa biết bài này cần những kỹ năng nào, nên chưa thể nói con '
          'vướng ở đâu.',
      implicatedCases: [],
    );
  }

  // Phân loại từng thành phần theo bằng chứng ĐỘC LẬP hiện có.
  final notStrong = <SkillRequirement>[];
  for (final r in map.requirements) {
    final c = masteryByConcept[r.conceptId]?.cases[r.skillCaseId];
    final strong = c != null && c.hasEvidence && c.pMastery >= strongAt;
    if (!strong) notStrong.add(r);
  }

  if (notStrong.isEmpty) {
    return MultiSkillDecision(
      diagnosis: DiagnosticOutcome.executionError,
      action: LearningAction.practice,
      reason: 'Mọi kỹ năng bài này cần con đều đã vững — nhiều khả năng chỉ '
          'nhầm khi tính. Làm thêm vài bài tương tự là đủ.',
      implicatedCases: const [],
    );
  }

  if (notStrong.length == 1) {
    final r = notStrong.single;
    final delegated = decide(
      conceptId: r.conceptId,
      exerciseCase: r.skillCaseId,
      mastery: masteryByConcept[r.conceptId] ??
          ConceptMastery(conceptId: r.conceptId, cases: const {}),
      stage: stage,
      catalogue: catalogue,
      caseCatalogue: caseCatalogue,
      strongAt: strongAt,
    );
    return MultiSkillDecision(
      diagnosis: delegated.diagnosis,
      action: delegated.action,
      reason: 'Bài này cần ${map.requirements.length} kỹ năng; '
          '${map.requirements.length - 1} kỹ năng con đã vững. '
          '${delegated.reason}',
      implicatedCases: [r.skillCaseId],
      delegated: delegated,
    );
  }

  // ⭐⭐ ≥2 nghi phạm: nói thật. Đây là biểu diễn mà ADR-003 §F6 nói là
  // "không có cách nào" — giờ có.
  final implicated = notStrong.map((r) => r.skillCaseId).toList()..sort();
  return MultiSkillDecision(
    diagnosis: DiagnosticOutcome.attributionUnresolved,
    action: LearningAction.isolateSkills,
    reason: 'Bài này cần ${map.requirements.length} kỹ năng, trong đó '
        '${implicated.length} kỹ năng chưa có bằng chứng vững. Chưa thể nói '
        'con vướng ở kỹ năng nào — cần làm vài bài NGẮN, mỗi bài chỉ chạm '
        'một kỹ năng, để cô lập.',
    implicatedCases: implicated,
  );
}
