import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/assistance_policy.dart';
import 'package:learning_coach/core/store/learning_session.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/mastery.dart';

LearningSession ses(List<LearningEvent> events) => LearningSession(
      sessionId: 's1',
      learnerId: 'L1',
      subjectId: 'toan',
      startedAt: DateTime(2026, 9, 2),
      trigger: SessionTrigger.manual,
      events: events,
    );

LearningEvent ev(String id, SupportLevel? support) => LearningEvent(
      eventId: id,
      skillCaseId: 'B57',
      kind: EvidenceKind.guidedAttempt,
      at: DateTime(2026, 9, 2),
      support: support,
    );

void main() {
  test('bảng ánh xạ đúng như doc §2 — cả 4 policy', () {
    final practice = rulesFor(AssistancePolicy.practice);
    expect(practice.mode, SessionMode.learn);
    expect(practice.revealAllowed, true);

    final hw = rulesFor(AssistancePolicy.homework);
    expect(hw.mode, SessionMode.learn); // homework KHÔNG phải thi
    expect(hw.supportCap, SupportLevel.workedStep);
    expect(hw.revealAllowed, false); // sản phẩm nộp phải là CỦA TRẺ

    final mock = rulesFor(AssistancePolicy.mock);
    final exam = rulesFor(AssistancePolicy.assessment);
    expect(mock.mode, SessionMode.assess);
    expect(exam.mode, SessionMode.assess);
    // MOCK ≠ ASSESSMENT duy nhất ở reviewAfter
    expect(mock.reviewAfter, true);
    expect(exam.reviewAfter, false);
    expect(mock.supportCap, exam.supportCap);
    expect(mock.revealAllowed, exam.revealAllowed);
  });

  test('homework: fullSolution vượt trần bị bắt, hint thì không', () {
    final s = ses([
      ev('e-hint', SupportLevel.hint),
      ev('e-step', SupportLevel.workedStep),
      ev('e-full', SupportLevel.fullSolution),
    ]);
    expect(supportCapViolations(s, AssistancePolicy.homework), ['e-full']);
    expect(supportCapViolations(s, AssistancePolicy.practice), isEmpty);
  });

  test('mock/assessment: MỌI hỗ trợ là vượt trần (cap = none)', () {
    final s = ses([ev('e1', SupportLevel.hint), ev('e2', SupportLevel.none)]);
    expect(supportCapViolations(s, AssistancePolicy.mock), ['e1']);
  });

  test('support null (nguồn không biết) KHÔNG bị kết tội — fail closed', () {
    final s = ses([ev('e1', null)]);
    expect(supportCapViolations(s, AssistancePolicy.assessment), isEmpty);
  });
}
