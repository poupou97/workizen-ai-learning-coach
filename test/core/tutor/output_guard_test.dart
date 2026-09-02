import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/core/tutor/output_guard.dart';

const facts = DerivedFacts(
  commonDenominator: 20,
  answerForms: ['19/20'],
  intermediateForms: ['15/20', '4/20'],
);

GuardVerdict g(String text,
        {SupportLevel level = SupportLevel.hint, bool exam = false}) =>
    validateTutorOutput(
        text: text, maxAllowed: level, facts: facts, examMode: exam);

void main() {
  test('transcript vi phạm THẬT từ shadow-run bị chặn (s06 r4)', () {
    final v = g('Tớ không dạy cách BCNN, vì em còn chưa học. '
        'Em hãy lấy tích của hai mẫu số (4 × 5 = 20) làm mẫu số chung.');
    expect(v.allowed, false);
    expect(v.blockedReasons.join(','), contains('METHOD_NAME:bcnn'));
    expect(v.blockedReasons.join(','), contains('ESCALATION'));
  });

  test('khen tư chất cho BẤT KỲ ai cũng chặn (s06 r2: «anh em tớ thông minh»)',
      () {
    final v = g('Tớ biết anh em tớ thông minh đó, nhưng mình dùng cách đã học nhé.');
    expect(v.allowed, false);
    expect(v.blockedReasons.single, startsWith('PRAISE:'));
  });

  test('hint sạch (Socratic, không số dẫn xuất) → cho qua', () {
    final v = g('Mẫu số của 3/4 và 1/5 có giống nhau không? '
        'Khi khác nhau, con cần làm gì trước tiên nhỉ?');
    expect(v.allowed, true);
  });

  test('số 20 hợp lệ ở workedStep, đáp án 19/20 vẫn cấm tới trước fullSolution',
      () {
    expect(g('Mẫu số chung là 20 nhé.', level: SupportLevel.workedStep).allowed,
        true);
    expect(
        g('Vậy kết quả là 19/20!', level: SupportLevel.workedStep).allowed,
        false);
    expect(
        g('Cả bài: mẫu chung 20, kết quả 19/20.',
                level: SupportLevel.fullSolution)
            .allowed,
        true);
  });

  test('echo đáp án TRẺ TỰ NÊU không phải reveal (fix false-positive s07)',
      () {
    final v = validateTutorOutput(
      text: 'Đúng rồi, 19/20! Con tự làm được không cần tớ gợi ý gì luôn!',
      maxAllowed: SupportLevel.none,
      facts: facts,
      childStatedFacts: const ['19/20', '20'],
    );
    expect(v.allowed, true);
  });

  test('exam mode: mọi từ khoá dạy đều chặn', () {
    final v = g('Con thử quy đồng mẫu số xem!', exam: true);
    expect(v.allowed, false);
    expect(v.blockedReasons.join(','), contains('EXAM_TUTORING'));
  });

  test('số 120 không bị bắt oan vì chứa «20» (ranh giới số)', () {
    final v = g('Bài này có 120 viên bi nhé.');
    expect(v.allowed, true);
  });
}
