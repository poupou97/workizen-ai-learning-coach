import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/eval/tutor_metrics.dart';
import 'package:learning_coach/core/store/learning_session.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/mastery.dart';

LearningEvent ev(
  String id,
  EvidenceKind kind, {
  bool? correct,
  SupportLevel? support,
  String? policyId,
}) =>
    LearningEvent(
      eventId: id,
      skillCaseId: 'sc1',
      kind: kind,
      at: DateTime(2026, 9, 2),
      correct: correct,
      support: support,
      policyId: policyId,
    );

LearningSession ses(
  String id,
  List<LearningEvent> events, {
  SessionMode mode = SessionMode.learn,
  DateTime? at,
}) =>
    LearningSession(
      sessionId: id,
      learnerId: 'L1',
      subjectId: 'toan',
      startedAt: at ?? DateTime(2026, 9, 1),
      trigger: SessionTrigger.manual,
      mode: mode,
      events: events,
    );

void main() {
  group('premature answer', () {
    test('fullSolution TRƯỚC khi trẻ tự thử → phiên bị gắn cờ', () {
      final r = evaluateSessions([
        ses('s1', [
          ev('e1', EvidenceKind.hintShown, support: SupportLevel.fullSolution),
          ev('e2', EvidenceKind.guidedAttempt,
              correct: true, support: SupportLevel.fullSolution),
        ]),
      ]);
      expect(r.prematureAnswerSessions, ['s1']);
    });

    test('trẻ tự thử trước rồi mới xem lời giải → KHÔNG premature', () {
      final r = evaluateSessions([
        ses('s2', [
          ev('e1', EvidenceKind.independentAttempt,
              correct: false, support: SupportLevel.none),
          ev('e2', EvidenceKind.hintShown, support: SupportLevel.fullSolution),
        ]),
      ]);
      expect(r.prematureAnswerSessions, isEmpty);
    });

    test('gắn cờ mỗi phiên tối đa một lần', () {
      final r = evaluateSessions([
        ses('s3', [
          ev('e1', EvidenceKind.hintShown, support: SupportLevel.fullSolution),
          ev('e2', EvidenceKind.hintShown, support: SupportLevel.fullSolution),
        ]),
      ]);
      expect(r.prematureAnswerSessions, ['s3']);
    });
  });

  group('hint strength — mức hỗ trợ mở màn', () {
    test('đếm mức hỗ trợ ĐẦU TIÊN của mỗi phiên, bỏ qua none', () {
      final r = evaluateSessions([
        ses('s1', [
          ev('e1', EvidenceKind.independentAttempt,
              correct: true, support: SupportLevel.none),
          ev('e2', EvidenceKind.hintShown, support: SupportLevel.hint),
          ev('e3', EvidenceKind.hintShown, support: SupportLevel.workedStep),
        ]),
        ses('s2', [
          ev('e4', EvidenceKind.hintShown, support: SupportLevel.workedStep),
        ]),
      ]);
      expect(r.firstSupportDistribution[SupportLevel.hint], 1);
      expect(r.firstSupportDistribution[SupportLevel.workedStep], 1);
      expect(r.firstSupportDistribution.containsKey(SupportLevel.none), false);
    });
  });

  group('thang ±1', () {
    test('hint → fullSolution (nhảy 2 bậc) bị gắn cờ đúng sự kiện', () {
      final r = evaluateSessions([
        ses('s1', [
          ev('e1', EvidenceKind.hintShown, support: SupportLevel.hint),
          ev('e2', EvidenceKind.hintShown, support: SupportLevel.fullSolution),
        ]),
      ]);
      expect(r.escalationViolations, ['e2']);
    });

    test('hint → workedStep → fullSolution: từng bậc một → sạch', () {
      final r = evaluateSessions([
        ses('s1', [
          ev('e1', EvidenceKind.hintShown, support: SupportLevel.hint),
          ev('e2', EvidenceKind.hintShown, support: SupportLevel.workedStep),
          ev('e3', EvidenceKind.hintShown, support: SupportLevel.fullSolution),
        ]),
      ]);
      expect(r.escalationViolations, isEmpty);
    });

    test('hạ mức (de-escalation) không bao giờ là vi phạm', () {
      final r = evaluateSessions([
        ses('s1', [
          ev('e1', EvidenceKind.hintShown, support: SupportLevel.fullSolution),
          ev('e2', EvidenceKind.hintShown, support: SupportLevel.hint),
        ]),
      ]);
      expect(r.escalationViolations, isEmpty);
    });
  });

  group('độc lập & policy coverage', () {
    test('chỉ tính trên câu-trả-lời thật (correct != null, không phải finalCorrectness)', () {
      final r = evaluateSessions([
        ses('s1', [
          ev('a1', EvidenceKind.independentAttempt,
              correct: true, support: SupportLevel.none),
          ev('a2', EvidenceKind.guidedAttempt,
              correct: true, support: SupportLevel.hint, policyId: 'p1'),
          ev('a3', EvidenceKind.hintRequested), // không phải câu trả lời
          ev('a4', EvidenceKind.finalCorrectness, correct: true), // loại
        ]),
      ]);
      expect(r.independentShare, 0.5);
      expect(r.policyCoverage, 0.5);
    });

    test('không có câu trả lời nào → 0, không chia cho 0', () {
      final r = evaluateSessions([ses('s1', [])]);
      expect(r.independentShare, 0);
      expect(r.policyCoverage, 0);
    });
  });

  group('exam violations', () {
    test('phiên assess có hintShown → sự kiện bị liệt kê', () {
      final r = evaluateSessions([
        ses('s1', [
          ev('e1', EvidenceKind.hintShown, support: SupportLevel.hint),
        ], mode: SessionMode.assess),
      ]);
      expect(r.examViolationEvents, ['e1']);
    });

    test('cùng sự kiện đó ở phiên learn → KHÔNG phải violation', () {
      final r = evaluateSessions([
        ses('s1', [
          ev('e1', EvidenceKind.hintShown, support: SupportLevel.hint),
        ]),
      ]);
      expect(r.examViolationEvents, isEmpty);
    });
  });

  group('independence trend', () {
    test('mỗi cửa sổ 7 ngày một mốc, theo thứ tự thời gian', () {
      final t = independenceTrend([
        ses('w0', [
          ev('e1', EvidenceKind.independentAttempt,
              correct: true, support: SupportLevel.none),
        ], at: DateTime(2026, 8, 1)),
        ses('w1', [
          ev('e2', EvidenceKind.guidedAttempt,
              correct: true, support: SupportLevel.hint),
        ], at: DateTime(2026, 8, 10)),
      ]);
      expect(t, [1.0, 0.0]);
    });

    test('rỗng → rỗng', () {
      expect(independenceTrend([]), isEmpty);
    });
  });
}
