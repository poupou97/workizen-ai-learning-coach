/// ⭐⭐ WAL-182 — LEARNING CONTEXT CANONICAL: "SAM đang đứng ở đâu."
///
/// Nhỏ, immutable, composable — KHÔNG phải một prompt, KHÔNG phải một Context
/// Engine khổng lồ (Founder Order 2026-09-04, P0-A §"Implementation
/// Constraint"). Enrich theo tầng Global → Subject → Book → Lesson; field
/// nào chưa biết thì giữ `null` — KHÔNG suy đoán chỉ để lấp object
/// (bất biến "UNKNOWN STAYS UNKNOWN").
///
/// ⭐ CONTEXT ≠ PROMPT: đây là sự thật runtime, không phải chuỗi ký tự đưa
/// LLM. Cái gì injection vào đâu là việc của tầng realization (chưa tồn tại
/// trong repo này hôm nay — không build LLM stack chỉ để chứng minh field
/// này rỗng khi chưa cần).
library;

import '../intent/learning_intent.dart';

class LearningContext {
  const LearningContext({
    required this.learnerId,
    required this.grade,
    this.subject,
    this.sourceDocumentId,
    this.lessonNo,
    this.intent,
  });

  final String learnerId;
  final int grade;

  /// `null` ở tầng Global (vd SAM gọi từ Home) — chưa biết môn, không đoán.
  final String? subject;

  /// `null` cho tới khi biết ĐÚNG cuốn sách (tầng Book trở lên).
  final String? sourceDocumentId;

  /// `null` cho tới khi biết ĐÚNG bài (tầng Lesson trở lên).
  final int? lessonNo;

  /// Ý định trẻ mang vào — chỉ có giá trị thật từ tầng Lesson trở lên
  /// (WAL-175). `lookup` ở đây là tín hiệu fail-closed cho Evidence
  /// Validator: tra cứu sinh Trace, không sinh Evidence.
  final LearningIntent? intent;

  bool get hasLesson => sourceDocumentId != null && lessonNo != null;

  LearningContext withSubject(String subject) => LearningContext(
      learnerId: learnerId,
      grade: grade,
      subject: subject,
      sourceDocumentId: sourceDocumentId,
      lessonNo: lessonNo,
      intent: intent);

  LearningContext withLesson({
    required String sourceDocumentId,
    required int lessonNo,
    required LearningIntent intent,
  }) =>
      LearningContext(
          learnerId: learnerId,
          grade: grade,
          subject: subject,
          sourceDocumentId: sourceDocumentId,
          lessonNo: lessonNo,
          intent: intent);
}
