import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/adaptive/error_hypothesis.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/mastery.dart';

LearningEvent ev(String id, EvidenceKind kind,
        {bool? correct, SupportLevel? support}) =>
    LearningEvent(
      eventId: id,
      skillCaseId: 'B57',
      kind: kind,
      at: DateTime(2026, 9, 2),
      correct: correct,
      support: support,
    );

void main() {
  test('careless: sai rồi TỰ sửa đúng không hỗ trợ → giả thuyết careless', () {
    final h = proposeErrorHypotheses(skillCaseId: 'B57', events: [
      ev('e1', EvidenceKind.independentAttempt, correct: false),
      ev('e2', EvidenceKind.selfCorrection,
          correct: true, support: SupportLevel.none),
    ]);
    expect(h.single.type, ErrorHypothesisType.careless);
    expect(h.single.status, HypothesisStatus.proposed); // KHÔNG BAO GIỜ confirmed từ luật
    expect(h.single.supportingEvidence, ['e1', 'e2']);
    expect(h.single.policyId, 'error-rules-v1'); // ai đoán phải ký tên
  });

  test('tự-sửa SAU GỢI Ý → KHÔNG phải careless (có hỗ trợ)', () {
    final h = proposeErrorHypotheses(skillCaseId: 'B57', events: [
      ev('e1', EvidenceKind.independentAttempt, correct: false),
      ev('e2', EvidenceKind.selfCorrection,
          correct: true, support: SupportLevel.hint),
    ]);
    expect(h, isEmpty);
  });

  test('procedural: sai ở ca từng vững — CHỈ khi biết belief trước', () {
    final events = [
      ev('e1', EvidenceKind.independentAttempt, correct: false),
    ];
    final known = proposeErrorHypotheses(
        skillCaseId: 'B57', events: events, pMasteryBeforeErrors: 0.9);
    expect(known.single.type, ErrorHypothesisType.procedural);

    // fail closed: không biết belief trước → KHÔNG đoán procedural
    final unknown =
        proposeErrorHypotheses(skillCaseId: 'B57', events: events);
    expect(unknown, isEmpty);

    // ca chưa từng vững → không phải procedural
    final weak = proposeErrorHypotheses(
        skillCaseId: 'B57', events: events, pMasteryBeforeErrors: 0.4);
    expect(weak, isEmpty);
  });

  test('conceptual: sai lặp ≥2 + TỰ xin gợi ý', () {
    final h = proposeErrorHypotheses(skillCaseId: 'B57', events: [
      ev('e1', EvidenceKind.independentAttempt, correct: false),
      ev('e2', EvidenceKind.independentAttempt, correct: false),
      ev('e3', EvidenceKind.hintRequested),
    ]);
    expect(h.single.type, ErrorHypothesisType.conceptual);
    expect(h.single.supportingEvidence, containsAll(['e1', 'e2', 'e3']));
  });

  test('MỘT lần sai + xin gợi ý → CHƯA đủ ngưỡng sai-lặp (2), im lặng', () {
    final h = proposeErrorHypotheses(skillCaseId: 'B57', events: [
      ev('e1', EvidenceKind.independentAttempt, correct: false),
      ev('e2', EvidenceKind.hintRequested),
    ]);
    expect(h, isEmpty);
  });

  test('sai lặp KHÔNG xin gợi ý → không đủ hai tín hiệu, im lặng', () {
    final h = proposeErrorHypotheses(skillCaseId: 'B57', events: [
      ev('e1', EvidenceKind.independentAttempt, correct: false),
      ev('e2', EvidenceKind.independentAttempt, correct: false),
    ]);
    expect(h, isEmpty);
  });

  test('giả thuyết trung thực mang bằng chứng NGHỊCH (lần đúng đã thấy)', () {
    final h = proposeErrorHypotheses(
        skillCaseId: 'B57',
        pMasteryBeforeErrors: 0.9,
        events: [
          ev('e1', EvidenceKind.independentAttempt, correct: false),
          ev('e2', EvidenceKind.independentAttempt, correct: true),
        ]);
    expect(h.single.conflictingEvidence, ['e2']);
  });

  test('không sự kiện trả lời → không giả thuyết nào (không bịa)', () {
    expect(
        proposeErrorHypotheses(skillCaseId: 'B57', events: [
          ev('e1', EvidenceKind.hintShown, support: SupportLevel.hint),
        ]),
        isEmpty);
  });
}
