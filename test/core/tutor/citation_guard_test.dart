/// WAL-114 — KHÔNG FABRICATE CITATION sau LLM output: trích dẫn CHỈ được
/// render tất định từ Provenance; LLM tự nói «SGK/trang N/sách nói» ⇒ CHẶN.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/core/tutor/output_guard.dart';

const _facts = DerivedFacts(commonDenominator: 20, answerForms: ['19/20']);

void main() {
  test('⭐ LLM bịa «SGK … trang 21» ⇒ CHẶN kể cả ở fullSolution', () {
    final v = validateTutorOutput(
      text: 'Theo SGK Toán 5, trang 21, con lấy tích hai mẫu số nhé.',
      maxAllowed: SupportLevel.fullSolution,
      facts: _facts,
    );
    expect(v.allowed, isFalse,
        reason: '⭐ đột biến bỏ luật CITATION ⇒ test này đỏ');
    expect(v.blockedReasons.any((r) => r.startsWith('CITATION_FABRICATION')),
        isTrue);
  });

  test('«sách nói rằng…» cũng là fabricate — chặn', () {
    final v = validateTutorOutput(
      text: 'sách nói rằng muốn quy đồng thì nhân hai mẫu.',
      maxAllowed: SupportLevel.fullSolution,
      facts: _facts,
    );
    expect(v.blockedReasons.any((r) => r.startsWith('CITATION_FABRICATION')),
        isTrue);
  });

  test('lời dạy KHÔNG nhắc nguồn ⇒ không dính luật citation', () {
    final v = validateTutorOutput(
      text: 'Con thử tìm một mẫu số mà cả hai mẫu cùng chia hết nhé.',
      maxAllowed: SupportLevel.hint,
      facts: _facts,
    );
    expect(v.blockedReasons.where((r) => r.startsWith('CITATION_FABRICATION')),
        isEmpty,
        reason: 'guard không phạt oan lời dạy thường');
  });
}
