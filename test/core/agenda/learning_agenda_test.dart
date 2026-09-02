import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/agenda/learning_agenda.dart';
import 'package:learning_coach/core/store/timetable.dart';
import 'package:learning_coach/core/student/concept_summary.dart';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/core/student/review_schedule.dart';

final _now = DateTime(2026, 9, 2); // thứ Tư

/// Fixture qua ConceptSummary.of THẬT — claim không được bịa tay.
ConceptSummary sum({
  required String concept,
  double pMastery = 0.7,
  int evidence = 4,
  int correct = 4,
  int incorrect = 0,
  int supported = 0,
  Set<String> known = const {'ca1'},
}) =>
    ConceptSummary.of(
      ConceptMastery(conceptId: concept, cases: {
        if (evidence > 0 || supported > 0)
          'ca1': CaseMastery(
            skillCaseId: 'ca1',
            pMastery: pMastery,
            evidenceCount: evidence,
            independentCorrect: correct,
            independentIncorrect: incorrect,
            supportedCount: supported,
            lastIndependentEvidenceAt: evidence > 0 ? _now : null,
          ),
      }),
      knownCaseIds: known,
      now: _now,
    );

AgendaConceptInput input(
  String concept, {
  String subject = 'toan',
  ConceptSummary? summary,
  ReviewUrgency review = ReviewUrgency.fresh,
  bool inStage = true,
  bool studiedToday = false,
}) =>
    AgendaConceptInput(
      conceptId: concept,
      subjectId: subject,
      summary: summary ?? sum(concept: concept),
      worstReview: review,
      inStage: inStage,
      studiedToday: studiedToday,
    );

void main() {
  test('không có gì → REST hạng nhất, có lý do, không có signal', () {
    final a = resolveAgenda([], today: _now);
    expect(a.kind, AgendaActionKind.rest);
    expect(a.reason, isNotEmpty);
    expect(a.signal, isNull);
  });

  test('học đủ nhịp hôm nay → REST kể cả khi còn overdue (trần, không phải sàn)',
      () {
    final a = resolveAgenda(
      [input('c1', review: ReviewUrgency.overdue)],
      today: _now,
      sessionsToday: 3,
    );
    expect(a.kind, AgendaActionKind.rest);
  });

  test('quên-hẳn (overdue) thắng ca-đang-hỏng — ưu tiên sư phạm cố ý', () {
    final a = resolveAgenda([
      input('c-hong',
          summary: sum(
              concept: 'c-hong',
              pMastery: 0.3,
              correct: 0,
              incorrect: 4)),
      input('c-quen', review: ReviewUrgency.overdue),
    ], today: _now);
    expect(a.conceptId, 'c-quen');
    expect(a.kind, AgendaActionKind.review);
    expect(a.signal!.kind, AgendaSignalKind.reviewOverdue);
  });

  test('timetable CHỈ xếp lại nhóm ngang nhau (F4)', () {
    final tkb = [
      TimetableEntry(learnerId: 'L1', weekday: _now.weekday, period: 1, subjectId: 'tieng-viet'),
    ];
    // hai tín hiệu NGANG NHAU (cùng needsWork) — TKB được chọn môn hôm nay
    final tie = resolveAgenda([
      input('c-toan',
          summary:
              sum(concept: 'c-toan', pMastery: 0.3, correct: 0, incorrect: 4)),
      input('c-tv',
          subject: 'tieng-viet',
          summary:
              sum(concept: 'c-tv', pMastery: 0.3, correct: 0, incorrect: 4)),
    ], today: _now, timetable: tkb);
    expect(tie.conceptId, 'c-tv');

    // tín hiệu MẠNH HƠN HẲN — TKB không đảo được ưu tiên sư phạm
    final strong = resolveAgenda([
      input('c-toan', review: ReviewUrgency.overdue),
      input('c-tv',
          subject: 'tieng-viet',
          summary:
              sum(concept: 'c-tv', pMastery: 0.3, correct: 0, incorrect: 4)),
    ], today: _now, timetable: tkb);
    expect(strong.conceptId, 'c-toan');
  });

  test('ngoài stage → im lặng tuyệt đối, kể cả overdue', () {
    final a = resolveAgenda(
      [input('c-vuot', review: ReviewUrgency.overdue, inStage: false)],
      today: _now,
    );
    expect(a.kind, AgendaActionKind.rest);
  });

  test('cooldown giảm nửa: chỗ học rồi hôm nay nhường chỗ chưa học', () {
    final a = resolveAgenda([
      input('c-vua-hoc',
          studiedToday: true,
          summary: sum(
              concept: 'c-vua-hoc',
              pMastery: 0.3,
              correct: 0,
              incorrect: 4)), // 0.8 → 0.4
      input('c-moi'), // developing → retrieve 0.5
    ], today: _now);
    expect(a.conceptId, 'c-moi');
    expect(a.kind, AgendaActionKind.retrieve);
  });

  test('cooldown KHÔNG dập được khẩn thật: overdue đã-học-hôm-nay vẫn hành động',
      () {
    final a = resolveAgenda(
      [input('c1', review: ReviewUrgency.overdue, studiedToday: true)],
      today: _now,
    ); // 0.9 → 0.45 ≥ restBelow 0.4
    expect(a.kind, AgendaActionKind.review);
  });

  test('claim map: noEvidence→learn, supportedOnly→retrieve, '
      'strongOnObserved→practice ca chưa quan sát', () {
    final learn = resolveAgenda(
        [input('c', summary: sum(concept: 'c', evidence: 0))],
        today: _now);
    expect(learn.kind, AgendaActionKind.learn);

    final retrieve = resolveAgenda(
        [input('c', summary: sum(concept: 'c', evidence: 0, supported: 5))],
        today: _now);
    expect(retrieve.kind, AgendaActionKind.retrieve);
    expect(retrieve.signal!.kind, AgendaSignalKind.supportedOnlyPractice);

    final cover = resolveAgenda(
        [
          input('c',
              summary: sum(
                  concept: 'c',
                  pMastery: 0.9,
                  evidence: 5,
                  correct: 5,
                  known: {'ca1', 'ca2'}))
        ],
        today: _now);
    expect(cover.kind, AgendaActionKind.practice);
    expect(cover.skillCaseId, 'ca2'); // đúng ca chưa quan sát
  });

  test('mastered → không tín hiệu (transfer là việc WAL-103, không bịa trước)',
      () {
    final a = resolveAgenda(
        [
          input('c',
              summary:
                  sum(concept: 'c', pMastery: 0.9, evidence: 5, correct: 5))
        ],
        today: _now);
    expect(a.kind, AgendaActionKind.rest);
  });

  test('mọi action không-REST truy được về tín hiệu + lý do đọc được', () {
    final a = resolveAgenda(
        [input('c', review: ReviewUrgency.reviewDue)],
        today: _now);
    expect(a.signal, isNotNull);
    expect(a.reason, isNotEmpty);
    expect(a.signal!.conceptId, a.conceptId);
  });
}
