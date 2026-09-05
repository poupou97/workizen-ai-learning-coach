/// WAL-210 round 3 (A7) — `DerivedFacts.textOnly`: guard cho bài KHÔNG có mẫu
/// số chung (câu trả lời bằng chữ). Các luật khác của guard giữ nguyên.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/core/tutor/output_guard.dart';

void main() {
  const facts = DerivedFacts.textOnly(answerForms: ['côcạn']);

  test('không mẫu số chung ⇒ số trong lời không bị coi là rò mẫu số', () {
    final v = validateTutorOutput(
        text: 'con xem lại 2 dòng đầu nhé', maxAllowed: SupportLevel.hint, facts: facts);
    expect(v.allowed, isTrue, reason: v.blockedReasons.join(','));
  });

  test('⭐ đáp án chữ lộ ra dưới fullSolution ⇒ REVEAL', () {
    final v = validateTutorOutput(
        text: 'cách này là cô cạn đấy', maxAllowed: SupportLevel.hint, facts: facts);
    expect(v.allowed, isFalse);
    expect(v.blockedReasons, contains('REVEAL:côcạn'));
  });

  test('trẻ đã tự nêu đáp án ⇒ SAM xác nhận lại không bị phạt', () {
    final v = validateTutorOutput(
        text: 'đúng rồi, cô cạn',
        maxAllowed: SupportLevel.none,
        facts: facts,
        childStatedFacts: ['côcạn']);
    expect(v.allowed, isTrue);
  });

  test('facts phân số cũ vẫn chặn mẫu số chung ở mức hint (không hồi quy)', () {
    const fr = DerivedFacts(commonDenominator: 20, answerForms: ['19/20']);
    final v = validateTutorOutput(
        text: 'mẫu số chung là 20', maxAllowed: SupportLevel.hint, facts: fr);
    expect(v.allowed, isFalse);
    expect(v.blockedReasons, contains('ESCALATION:common-denominator-20-at-hint'));
  });
}
