/// WAL-168 — LỜI DẠY LÀ DỮ LIỆU: `hintTextFor` không còn biết phương pháp nào
/// là phương pháp nào, và không còn biết bài thuộc môn gì.
///
/// Đây là điểm chặn thứ ba của Architecture Gate: trước đây mỗi phương pháp mới
/// là một hàm prose viết tay trong Dart. Ở quy mô 531 cuốn thì đó là hàng nghìn
/// hàm — «HARDCODED BLUEPRINT ≠ SCALABILITY».
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/curriculum/fraction_problem.dart';
import 'package:learning_coach/core/curriculum/pedagogical_boundary.dart';
import 'package:learning_coach/core/curriculum/solvable_problem.dart';
import 'package:learning_coach/core/knowledge/slice_curriculum.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/student/mastery.dart' show SupportLevel;
import 'package:learning_coach/features/tutor/tutor_session.dart' show hintTextFor;

const _p5 = LearnerProfile(learnerId: 't', displayName: 'T', grade: 5);

TeachingMethod _byId(String id) =>
    curriculumFor(_p5)!.catalogue.firstWhere((m) => m.id == id);

/// Bài của một môn KHÔNG PHẢI toán — chỉ tồn tại trong test, để chứng minh
/// `hintTextFor` chạy được mà không biết gì về phân số.
class _FakeProblem implements SolvableProblem {
  @override
  bool checkAnswer(String raw) => raw == 'x';
  @override
  Map<String, String> get slots => {'b': 'BÊ', 'd': 'DÊ'};
}

void main() {
  test('⭐ số trong lời dạy lấy từ CHÍNH BÀI, không phải hằng số trong mã', () {
    final m = _byId('common-denom-by-product');
    final t = hintTextFor(m, SupportLevel.hint, FractionProblem.parse('3/4 + 2/5')!);
    expect(t, contains('4'));
    expect(t, contains('5'));
    final t2 =
        hintTextFor(m, SupportLevel.hint, FractionProblem.parse('1/2 - 1/7')!);
    expect(t2, contains('7'),
        reason: '⭐ đột biến gắn cứng số của một bài ⇒ đỏ');
    expect(t2, isNot(contains('4')));
  });

  test('⭐ lời giải trọn vẹn dựng đúng số học của bài', () {
    final t = hintTextFor(_byId('common-denom-by-product'),
        SupportLevel.fullSolution, FractionProblem.parse('3/4 + 2/5')!);
    // mẫu chung 20, 3/4 = 15/20, 2/5 = 8/20, tổng 23/20.
    expect(t, contains('20'));
    expect(t, contains('15/20'));
    expect(t, contains('8/20'));
    expect(t, contains('23/20'));
  });

  test('⭐⭐ hintTextFor KHÔNG biết môn: bài không-phải-toán vẫn điền được slot',
      () {
    final m = _byId('common-denom-by-product');
    final t = hintTextFor(m, SupportLevel.hint, _FakeProblem());
    expect(t, contains('BÊ'));
    expect(t, contains('DÊ'),
        reason: '⭐⭐ đột biến bắt hintTextFor nhận FractionProblem ⇒ không '
            'biên dịch nổi — đây chính là điểm chặn 2 của Architecture Gate');
  });

  test('⭐ phương pháp CHƯA có lời dạy ⇒ SAM im lặng, KHÔNG bịa câu', () {
    const bare = TeachingMethod(
      id: 'chua-co-loi',
      name: 'Cách chưa soạn lời',
      appliesToConcepts: {'quy-dong'},
      requiresConcepts: {},
      requiresTerminology: {},
    );
    for (final lv in SupportLevel.values) {
      expect(hintTextFor(bare, lv, FractionProblem.parse('1/2 + 1/3')!), '',
          reason: '⭐ đột biến rơi về một câu chung chung ⇒ đỏ: SAM nói lời '
              'không có nguồn còn tệ hơn SAM im');
    }
  });

  test('⭐ slot thiếu thì LỘ RA, không thành câu cụt âm thầm', () {
    const h = MethodHints(hint: 'Mẫu {b} và {khong_co}', workedStep: '', fullSolution: '');
    expect(h.fill(h.hint, {'b': '4'}), 'Mẫu 4 và {khong_co}',
        reason: '⭐ đột biến thay slot thiếu bằng chuỗi rỗng ⇒ đỏ');
  });

  test('mọi phương pháp trong chương trình đều CÓ lời dạy đủ ba nấc', () {
    for (final m in curriculumFor(_p5)!.catalogue) {
      final h = m.hints;
      expect(h, isNotNull, reason: '${m.id} thiếu lời dạy');
      expect(h!.hint.trim(), isNotEmpty);
      expect(h.workedStep.trim(), isNotEmpty);
      expect(h.fullSolution.trim(), isNotEmpty);
    }
  });
}
