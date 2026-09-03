/// WAL-86 — luật của TutorSession giữ bằng test, không cần widget.
///
/// Mỗi test hỏi một câu có thể TRẢ LỜI SAI: chuỗi event có đúng loại không,
/// thang có leo quá một nấc không, REVEAL có mở sớm không, tự-sửa có bị ghi
/// nhầm thành tự-làm-thường không, hết scope có bịa gợi ý không.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/curriculum/pedagogical_boundary.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/features/tutor/tutor_session.dart';
import '../../support/curriculum.dart';

const _stage = LearningStage(
  grade: 5,
  bookSeries: 'kntt',
  lessonId: 'toan5-t1-bai6',
  conceptsIntroduced: {'phan-so', 'chia-het', 'nhan-so-tu-nhien'},
  methodsIntroduced: {'common-denom-by-product'},
  terminologyIntroduced: {'mẫu số chung'},
);

/// WAL-168: lấy ĐÚNG method của sản phẩm thay vì chép lại — lời dạy nay là dữ
/// liệu đi cùng method, nên fixture chép tay sẽ kiểm một bản sao không có lời.
final _method = toan5Bai6
    .catalogue
    .firstWhere((m) => m.id == 'common-denom-by-product');

TutorSession _session({List<TeachingMethod>? catalogue}) {
  var t = DateTime(2026, 9, 1, 19);
  return TutorSession(
    exerciseId: 'cp:test',
    skillCaseId: 'denominator-non-divisible',
    problem: FractionProblem.parse('3/4 + 2/5')!,
    scope: TutorScope.forProblem(
        'quy-dong', 'denominator-non-divisible', _stage, catalogue ?? [_method]),
    now: () => t = t.add(const Duration(seconds: 30)),
  );
}

List<EvidenceKind> _kinds(TutorSession s) =>
    [for (final e in s.log.events) e.kind];

void main() {
  test('tự làm đúng ngay: independentAttempt + finalCorrectness, không hơn', () {
    final s = _session();
    expect(s.submit('23/20'), SubmitOutcome.independentCorrect);
    expect(_kinds(s),
        [EvidenceKind.independentAttempt, EvidenceKind.finalCorrectness]);
    expect(s.outcome.independent, isTrue);
    expect(s.outcome.maxSupport, SupportLevel.none);
  });

  test('sai → xin gợi ý → đúng: postHintSuccess, KHÔNG phải independentAttempt',
      () {
    final s = _session();
    expect(s.submit('5/9'), SubmitOutcome.wrong);
    expect(s.requestHint(), isNotNull);
    expect(s.submit('23/20'), SubmitOutcome.supportedCorrect);
    expect(_kinds(s), [
      EvidenceKind.independentAttempt, // lần sai — vẫn là bằng chứng tự làm
      EvidenceKind.hintRequested,
      EvidenceKind.postHintSuccess,
      EvidenceKind.finalCorrectness,
    ]);
    // ⭐ cốt lõi: lần đúng-sau-gợi-ý KHÔNG lọt vào independentAttempts
    expect(s.log.independentAttempts.length, 1);
    expect(s.log.independentAttempts.single.correct, isFalse);
    expect(s.outcome.independent, isFalse);
  });

  test('thang leo TỪNG nấc và fullSolution bị chặn khi chưa tự thử', () {
    final s = _session();
    s.requestHint();
    expect(s.support, SupportLevel.hint);
    s.requestHint();
    expect(s.support, SupportLevel.workedStep);
    s.requestHint(); // chưa có lần thử nào → REVEAL đóng
    expect(s.support, SupportLevel.workedStep,
        reason: 'fullSolution chỉ mở sau ≥1 lần tự thử');
    s.submit('1/2'); // sai — nhưng là một lần thử thật
    s.requestHint();
    expect(s.support, SupportLevel.fullSolution);
    // nội dung lời giải phải chứa số THẬT của bài, không phải template rỗng
    expect(hintTextFor(_method, SupportLevel.fullSolution, s.problem),
        contains('23/20'));
  });

  test('tự sửa không cần hỗ trợ mới = selfCorrection, không phải attempt thường',
      () {
    final s = _session();
    s.submit('5/9'); // sai
    expect(s.submit('23/20'), SubmitOutcome.selfCorrected);
    expect(_kinds(s), [
      EvidenceKind.independentAttempt,
      EvidenceKind.selfCorrection,
      EvidenceKind.finalCorrectness,
    ]);
    expect(s.outcome.selfCorrected, isTrue);
    expect(s.outcome.independent, isTrue);
  });

  test('sai → gợi ý → sai → đúng KHÔNG được tính selfCorrection', () {
    final s = _session();
    s.submit('5/9');
    s.requestHint(); // có hỗ trợ mới giữa hai lần → không còn là "tự sửa"
    expect(s.submit('23/20'), SubmitOutcome.supportedCorrect);
    expect(_kinds(s), isNot(contains(EvidenceKind.selfCorrection)));
  });

  test('hết scope: hintRequested vẫn ghi (siêu nhận thức) nhưng KHÔNG bịa gợi ý',
      () {
    final s = _session(catalogue: const []); // không method nào trong scope
    expect(s.requestHint(), isNull, reason: 'fail closed — không bịa');
    expect(s.support, SupportLevel.none, reason: 'không leo thang khi tay trắng');
    expect(_kinds(s), [EvidenceKind.hintRequested]);
    expect(s.log.events.single.correct, isNull,
        reason: 'xin gợi ý không phải câu trả lời — UNKNOWN không thành FAILED');
  });

  test('chấm đáp án: nhận phân số chưa rút gọn cùng giá trị, chặn mẫu 0', () {
    final p = FractionProblem.parse('3/4 + 2/5')!;
    expect(p.checkAnswer('23/20'), isTrue);
    expect(p.checkAnswer('46/40'), isTrue, reason: 'chưa rút gọn vẫn đúng');
    expect(p.checkAnswer('23/0'), isFalse);
    expect(p.checkAnswer('xyz'), isFalse);
    final m = FractionProblem.parse('7/2 - 1/2')!;
    expect(m.checkAnswer('3'), isTrue, reason: 'kết quả nguyên nhập không mẫu');
  });
}
