/// WAL-27 — ErrorHypothesis: misconception học LÚC CHẠY, không bao giờ là truth.
///
/// Founder Directive 2026-09-02 delta C (khuôn bắt buộc): luật tất định trên
/// log CHỈ ĐƯỢC tạo GIẢ THUYẾT — ba tầng tách bạch:
///   OBSERVED ERROR (sự kiện, bất biến)
///   ≠ ERROR HYPOTHESIS (giả thuyết có độ tin + bằng chứng thuận/nghịch + nguồn)
///   ≠ CONFIRMED MISCONCEPTION (chỉ sau probe/verify — WAL-49/70).
/// LLM lẫn heuristic đều KHÔNG mint truth; cả hai đề xuất vào CÙNG khuôn này.
///
/// Cấu trúc bảo đảm bằng KIỂU: module không nhận/trả CaseMastery ghi được —
/// không có đường nào từ hypothesis vào belief/claim.
library;

import '../student/learning_evidence.dart';
import '../student/mastery.dart';

enum ErrorHypothesisType { careless, procedural, conceptual }

enum HypothesisStatus { proposed, confirmed, retired }

class ErrorHypothesis {
  const ErrorHypothesis({
    required this.type,
    required this.skillCaseId,
    required this.confidence,
    required this.supportingEvidence,
    required this.conflictingEvidence,
    required this.policyId,
    this.status = HypothesisStatus.proposed,
  });

  final ErrorHypothesisType type;
  final String skillCaseId;

  /// Độ tin CỦA GIẢ THUYẾT — không phải xác suất misconception là thật.
  /// Hằng số có tên trong [ErrorRulePolicy], không trôi nổi.
  final double confidence;

  /// eventIds — mọi giả thuyết truy được về sự kiện cụ thể (F4).
  final List<String> supportingEvidence;

  /// Bằng chứng NGHỊCH đã thấy — giả thuyết trung thực mang cả hai phía.
  final List<String> conflictingEvidence;

  /// Nguồn đề xuất: `error-rules-v1` hoặc `llm:tên-model`… — ai đoán phải ký tên.
  final String policyId;

  final HypothesisStatus status;
}

/// Ngưỡng — có tên, có lý do, thay được (ADR-004). GIẢ THUYẾT V1 chờ WAL-49.
class ErrorRulePolicy {
  const ErrorRulePolicy({
    this.carelessConfidence = 0.6,
    this.proceduralConfidence = 0.5,
    this.conceptualConfidence = 0.55,
    this.strongBefore = 0.85,
    this.repeatThreshold = 2,
  });

  /// 0.6 — tự-sửa-ngay là tín hiệu hành vi khá rõ, nhưng vẫn là giả thuyết.
  final double carelessConfidence;

  /// 0.5 — «từng vững mà sai» có thể là quên/mệt/đề lạ — mức tin thấp nhất.
  final double proceduralConfidence;

  /// 0.55 — sai lặp + tự xin gợi ý: hai tín hiệu độc lập cùng hướng.
  final double conceptualConfidence;

  /// Ca coi là «từng vững» khi pMastery TRƯỚC lỗi ≥ mức này (khớp strongAt).
  final double strongBefore;

  /// Số lần sai độc-lập liên-tiếp tối thiểu để gọi là «sai lặp».
  final int repeatThreshold;
}

/// Sinh giả thuyết từ chuỗi sự kiện MỘT ca (thứ tự thời gian) — thuần, chỉ đọc.
/// [pMasteryBeforeErrors] = belief TRƯỚC chuỗi lỗi (caller replay tới đó);
/// `null` = không biết — luật procedural im lặng thay vì đoán (fail closed).
List<ErrorHypothesis> proposeErrorHypotheses({
  required String skillCaseId,
  required List<LearningEvent> events,
  double? pMasteryBeforeErrors,
  ErrorRulePolicy policy = const ErrorRulePolicy(),
}) {
  final out = <ErrorHypothesis>[];
  const src = 'error-rules-v1';

  // Chuỗi trả-lời độc lập, giữ thứ tự.
  final answers = [
    for (final e in events)
      if (e.correct != null &&
          (e.kind == EvidenceKind.independentAttempt ||
              e.kind == EvidenceKind.selfCorrection))
        e
  ];
  if (answers.isEmpty) return out;

  // ── CARELESS: sai lần đầu + selfCorrection ĐÚNG ngay sau, không hỗ trợ ──
  for (var i = 0; i + 1 < answers.length; i++) {
    final a = answers[i], b = answers[i + 1];
    if (a.correct == false &&
        b.kind == EvidenceKind.selfCorrection &&
        b.correct == true &&
        (b.support == null || b.support == SupportLevel.none)) {
      out.add(ErrorHypothesis(
        type: ErrorHypothesisType.careless,
        skillCaseId: skillCaseId,
        confidence: policy.carelessConfidence,
        supportingEvidence: [a.eventId, b.eventId],
        conflictingEvidence: const [],
        policyId: src,
      ));
    }
  }

  // ── chuỗi sai độc lập liên tiếp (không tự sửa) ──
  final wrongStreak = <LearningEvent>[];
  for (final a in answers) {
    if (a.correct == false) {
      wrongStreak.add(a);
    } else {
      break; // chuỗi đầu tiên là đủ cho một giả thuyết — không gộp cả lịch sử
    }
  }
  final corrects =
      [for (final a in answers) if (a.correct == true) a.eventId];

  // ── PROCEDURAL: sai ở ca TỪNG VỮNG — cần biết belief trước đó ──
  if (wrongStreak.isNotEmpty &&
      pMasteryBeforeErrors != null &&
      pMasteryBeforeErrors >= policy.strongBefore) {
    out.add(ErrorHypothesis(
      type: ErrorHypothesisType.procedural,
      skillCaseId: skillCaseId,
      confidence: policy.proceduralConfidence,
      supportingEvidence: [for (final e in wrongStreak) e.eventId],
      conflictingEvidence: corrects,
      policyId: src,
    ));
  }

  // ── CONCEPTUAL: sai lặp + trẻ TỰ xin gợi ý (siêu nhận thức: biết mình bí) ──
  final asked = [
    for (final e in events)
      if (e.kind == EvidenceKind.hintRequested) e.eventId
  ];
  if (wrongStreak.length >= policy.repeatThreshold && asked.isNotEmpty) {
    out.add(ErrorHypothesis(
      type: ErrorHypothesisType.conceptual,
      skillCaseId: skillCaseId,
      confidence: policy.conceptualConfidence,
      supportingEvidence: [
        for (final e in wrongStreak) e.eventId,
        ...asked,
      ],
      conflictingEvidence: corrects,
      policyId: src,
    ));
  }

  return out;
}
