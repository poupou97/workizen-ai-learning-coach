/// Founder Task Order 2026-09-01 §7 — lineage của can thiệp phải nằm TRONG
/// dữ liệu, tái dựng được đúng ví dụ của lệnh:
///   Attempt 1 sai (support none) → SMALL_HINT → Attempt 2 đúng (support hint)
///   nghĩa là «đúng sau MỘT gợi ý nhỏ», KHÔNG phải «mastered».
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/curriculum/pedagogical_boundary.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/features/tutor/tutor_session.dart';

const _stage = LearningStage(
  grade: 5, bookSeries: 'kntt', lessonId: 'toan5-t1-bai6',
  conceptsIntroduced: {'phan-so', 'chia-het', 'nhan-so-tu-nhien'},
  methodsIntroduced: {'common-denom-by-product'},
  terminologyIntroduced: {'mẫu số chung'},
);
const _method = TeachingMethod(
  id: 'common-denom-by-product', name: 'tích hai mẫu',
  appliesToConcepts: {'quy-dong'},
  skillCaseId: 'denominator-non-divisible',
  requiresConcepts: {'phan-so', 'nhan-so-tu-nhien'},
  requiresTerminology: {'mẫu số chung'});

TutorSession _s() {
  var t = DateTime(2026, 9, 1, 19);
  return TutorSession(
    exerciseId: 'cp:test',
    skillCaseId: 'denominator-non-divisible',
    problem: FractionProblem.parse('3/4 + 2/5')!,
    scope: TutorScope.forProblem(
        'quy-dong', 'denominator-non-divisible', _stage, const [_method]),
    now: () => t = t.add(const Duration(seconds: 30)),
  );
}

void main() {
  test('⭐ ví dụ NGUYÊN VĂN của lệnh: sai(0) → hint → đúng(1) đọc được từ dữ liệu',
      () {
    final s = _s();
    s.submit('5/9'); // Attempt 1 — sai, chưa hỗ trợ
    s.requestHint(); // SMALL_HINT
    s.submit('23/20'); // Attempt 2 — đúng, đang có hint
    final answers =
        s.log.events.where((e) => e.correct != null && e.kind != EvidenceKind.finalCorrectness).toList();
    expect(answers[0].support, SupportLevel.none);
    expect(answers[0].correct, isFalse);
    expect(answers[1].support, SupportLevel.hint,
        reason: 'mức hỗ trợ TẠI sự kiện — không phải suy từ thứ tự log');
    expect(answers[1].correct, isTrue);
    expect(answers[1].priorEventId, answers[0].eventId,
        reason: 'pre/post quanh can thiệp là CHUỖI trong dữ liệu');
    expect(answers[1].policyId, TutorSession.policyId);
  });

  test('đúng-sau-hint-nhỏ PHÂN BIỆT ĐƯỢC với đúng-sau-xem-trọn-lời-giải', () {
    // ca A: 1 hint nhỏ
    final a = _s();
    a.submit('5/9');
    a.requestHint();
    a.submit('23/20');
    // ca B: leo tới fullSolution rồi mới đúng (chép lại)
    final b = _s();
    b.submit('5/9');
    b.requestHint(); // hint
    b.requestHint(); // workedStep
    b.requestHint(); // fullSolution (REVEAL mở vì đã thử)
    b.submit('23/20');
    LearningEvent last(TutorSession s) => s.log.events
        .lastWhere((e) => e.kind == EvidenceKind.postHintSuccess);
    expect(last(a).support, SupportLevel.hint);
    expect(last(b).support, SupportLevel.fullSolution,
        reason: 'trước bản vá, cả hai chỉ là postHintSuccess không phân biệt — '
            'gap §7 Founder chỉ đúng chỗ');
    expect(last(a).kind, last(b).kind,
        reason: 'kind giống nhau — chính vì thế support PHẢI nằm trên event');
  });

  test('dữ liệu cũ không có support ⇒ null, không đoán về none', () {
    final e = LearningEvent(
        eventId: 'legacy', skillCaseId: 'x',
        kind: EvidenceKind.independentAttempt, correct: true,
        at: DateTime(2026, 9, 1));
    expect(e.support, isNull);
    expect(e.policyId, isNull);
  });
}
