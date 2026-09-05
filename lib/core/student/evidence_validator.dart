/// ⭐⭐ WAL-178 — EVIDENCE VALIDATOR: cửa DUY NHẤT một CLAIM trở thành bằng
/// chứng học tập thật (Founder Order 2026-09-04 §5).
///
/// Learning Tool KHÔNG tự mint `LearningEvent`. Nó trả về [CandidateEvidence]
/// — một CLAIM, không phải một sự thật — và [validateCandidateEvidence] quyết
/// định claim đó có đáng ghi thành bằng chứng hay không. Đúng nguyên tắc đã
/// có sẵn trong repo (`experiment_screen.dart` cũ): *"Dự đoán CHỈ mở gate —
/// chưa phải bằng chứng (giả thuyết ≠ mastery)"* — vé này biến kỷ luật đó
/// thành MỘT cơ chế dùng chung, không phải lựa chọn riêng của từng widget.
library;

import '../intent/learning_intent.dart';
import '../pedagogy/pedagogy_model.dart' show TeachingAct;
import 'learning_evidence.dart';
import 'mastery.dart';
import '../context/learning_context.dart';

/// Một CLAIM từ Learning Tool — CHƯA phải bằng chứng. Tool điền đúng những gì
/// nó quan sát được từ tương tác của trẻ; nó không tự quyết claim này có
/// "đáng tin" hay không.
class CandidateEvidence {
  const CandidateEvidence({
    required this.skillCaseId,
    this.conceptIds = const [],
    this.exerciseId,
    this.learnerText,
    this.act,
    this.support = SupportLevel.none,
    required this.policyId,
    this.knowledgeVersion,
  });

  final String skillCaseId;
  final List<String> conceptIds;
  final String? exerciseId;

  /// Chữ trẻ viết nguyên văn — validator dùng để quyết claim có "chất liệu"
  /// hay không (rỗng ⇒ không có gì để làm bằng chứng thật).
  final String? learnerText;

  final TeachingAct? act;
  final SupportLevel support;
  final String policyId;
  final String? knowledgeVersion;
}

/// ⭐⭐ Cửa DUY NHẤT quyết một [CandidateEvidence] có thành `LearningEvent`
/// thật hay không. Fail-closed — trả `null` (Trace, không phải "sai") khi:
///
/// - ý định là `lookup` (WAL-175: tra cứu sinh Trace, không sinh Evidence,
///   dù trẻ có viết gì đi nữa — bịa evidence từ một lần xem sách là nói dối
///   về sự thật học tập);
/// - chữ trẻ viết rỗng (không có "chất liệu" nào để làm bằng chứng — im lặng
///   không phải là sai, nó chỉ là chưa có gì để nói).
///
/// KHÔNG chấm đúng/sai ở đây: `correct` luôn `null` cho dạng bằng chứng quan
/// sát/giải thích tự do (UNKNOWN ≠ SAI, bất biến đã có từ trước).
///
/// ⭐⭐ WAL-210 — Founder D1: [CandidateEvidence] KHÔNG có trường chấm điểm,
/// nên mọi claim qua cửa này là **chưa được kiểm chứng** ⇒ loại sự kiện là
/// [EvidenceKind.participation] — không phải `independentAttempt` (audit C6:
/// trước đây `support = workedStep` vẫn thành «tự làm»). Khi nào có hợp đồng
/// ValidatedEvidence (Founder quyết) mới có đường lên bằng chứng năng lực.
LearningEvent? validateCandidateEvidence(
  CandidateEvidence c, {
  required LearningContext context,
  required String eventId,
  required DateTime at,
}) {
  if (context.intent == LearningIntent.lookup) return null;
  final text = c.learnerText?.trim() ?? '';
  if (text.isEmpty) return null;
  return LearningEvent(
    eventId: eventId,
    skillCaseId: c.skillCaseId,
    kind: EvidenceKind.participation,
    correct: null,
    exerciseId: c.exerciseId,
    conceptIds: c.conceptIds,
    at: at,
    support: c.support,
    policyId: c.policyId,
    knowledgeVersion: c.knowledgeVersion,
    sourceDocumentId: context.sourceDocumentId,
    lessonNo: context.lessonNo,
    act: c.act,
    learnerText: c.learnerText,
  );
}
