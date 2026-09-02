import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/agenda/learning_agenda.dart';
import 'package:learning_coach/core/classroom/teacher_intent.dart';
import 'package:learning_coach/core/student/concept_summary.dart';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/core/student/review_schedule.dart';

final _now = DateTime(2026, 9, 2);

TeacherIntent intent({
  TeacherIntentKind kind = TeacherIntentKind.focusThisWeek,
  DateTime? expiry,
  String? studentId,
}) =>
    TeacherIntent(
      teacherId: 'gv1',
      conceptId: 'quy-dong',
      subjectId: 'toan',
      kind: kind,
      statedAt: DateTime(2026, 9, 1),
      expiry: expiry ?? DateTime(2026, 9, 8),
      studentId: studentId,
    );

AgendaConceptInput weakConcept(String id) => AgendaConceptInput(
      conceptId: id,
      subjectId: 'toan',
      summary: ConceptSummary.of(
        ConceptMastery(conceptId: id, cases: {
          'ca1': CaseMastery(
            skillCaseId: 'ca1',
            pMastery: 0.3,
            evidenceCount: 4,
            independentIncorrect: 4,
            lastIndependentEvidenceAt: _now,
          ),
        }),
        knownCaseIds: {'ca1'},
        now: _now,
      ),
      worstReview: ReviewUrgency.fresh,
    );

void main() {
  test('intent còn hạn phát tín hiệu — đúng action theo kind', () {
    final sigs = teacherIntentSignals(
        [intent(kind: TeacherIntentKind.prepareAssessment)],
        now: _now, studentId: 'hs1');
    expect(sigs.single.kind, AgendaSignalKind.teacherIntent);
    expect(sigs.single.action, AgendaActionKind.retrieve);
    expect(sigs.single.reason, isNotEmpty);
  });

  test('hết hạn → im lặng, không cần ai dọn', () {
    final sigs = teacherIntentSignals(
        [intent(expiry: DateTime(2026, 9, 2))], // expiry = now ⇒ hết hạn
        now: _now, studentId: 'hs1');
    expect(sigs, isEmpty);
  });

  test('intent mức-học-sinh chỉ áp cho đúng em đó', () {
    final i = [intent(studentId: 'hs-a')];
    expect(teacherIntentSignals(i, now: _now, studentId: 'hs-a'), hasLength(1));
    expect(teacherIntentSignals(i, now: _now, studentId: 'hs-b'), isEmpty);
  });

  test('intent KHÔNG đảo được ưu tiên sư phạm khẩn của chính đứa trẻ', () {
    final a = resolveAgenda(
      [weakConcept('c-hong')], // weakCase 0.8 > teacherIntent 0.6
      today: _now,
      extraSignals:
          teacherIntentSignals([intent()], now: _now, studentId: 'hs1'),
    );
    expect(a.conceptId, 'c-hong');
    expect(a.signal!.kind, AgendaSignalKind.weakCase);
  });

  test('không có gì khẩn → intent của thầy cô dẫn hướng', () {
    final a = resolveAgenda(
      const [],
      today: _now,
      extraSignals:
          teacherIntentSignals([intent()], now: _now, studentId: 'hs1'),
    );
    expect(a.kind, AgendaActionKind.learn);
    expect(a.conceptId, 'quy-dong');
    expect(a.signal!.kind, AgendaSignalKind.teacherIntent);
  });
}
