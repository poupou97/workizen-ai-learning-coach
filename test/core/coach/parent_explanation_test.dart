/// ⭐⭐ F4 — lời với phụ huynh: tất định, truy vết được, không vượt bằng chứng.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/coach/parent_explanation.dart';
import 'package:learning_coach/core/student/concept_summary.dart';
import 'package:learning_coach/core/student/evidence_validation.dart';
import 'package:learning_coach/core/student/evidence_weighting.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/mastery.dart';

void main() {
  const p = BktParams.freeResponse;
  const concept = 'quy-dong';
  const div = 'denominator-divisible';
  const nonDiv = 'denominator-non-divisible';
  const eq = 'denominator-equal';
  final now = DateTime(2026, 9, 1, 20);
  const names = {
    div: 'một mẫu chia hết cho mẫu kia',
    nonDiv: 'hai mẫu không chia hết cho nhau',
    eq: 'hai mẫu bằng nhau',
  };

  var seq = 0;
  CaseMastery drill(String id, List<bool> answers,
      {Duration age = const Duration(days: 1)}) {
    var log = EvidenceLog.empty(id);
    for (var i = 0; i < answers.length; i++) {
      log = log.append(LearningEvent(
          eventId: 'e${seq++}', skillCaseId: id,
          kind: EvidenceKind.independentAttempt,
          correct: answers[i],
          // ROUND 4 (strict default): đường Deep thật đóng dấu validator.
          validation: const EvidenceValidation(
              validatorId: 'fraction-check-v1', validatorVersion: '1'),
          at: now.subtract(age).add(Duration(minutes: i))));
    }
    return replayMastery(log, p);
  }

  ParentExplanation explain(Map<String, CaseMastery> cases, Set<String> known) =>
      explainConcept(
        ConceptSummary.of(ConceptMastery(conceptId: concept, cases: cases),
            knownCaseIds: known, now: now),
        conceptDisplayName: 'quy đồng mẫu số',
        caseDisplayNames: names,
      );

  test('⭐⭐ CẤM chữ "vững" khi còn ca chưa kiểm — và phải NÓI RA ca đó', () {
    final e = explain({
      div: drill(div, [true, true, true]),
      nonDiv: drill(nonDiv, [true, true, true]),
    }, {div, nonDiv, eq});
    expect(e.claim, ConceptClaim.strongOnObserved);
    expect(e.message, isNot(contains('đã vững')),
        reason: '⭐⭐ đây chính là câu nói dối mà F1 tồn tại để chặn');
    expect(e.message, contains('chưa kiểm'));
    expect(e.message, contains(names[eq]!),
        reason: 'ca chưa kiểm phải được nêu TÊN, không nói mơ hồ');
  });

  test('mastered thật ⇒ được nói "vững", kèm citation đủ các ca', () {
    final e = explain({
      div: drill(div, [true, true, true]),
      nonDiv: drill(nonDiv, [true, true]),
    }, {div, nonDiv});
    expect(e.claim, ConceptClaim.mastered);
    expect(e.message, contains('đã vững'));
    expect(e.citations.map((c) => c.skillCaseId), containsAll([div, nonDiv]));
    for (final c in e.citations) {
      expect(c.observation, contains('lần tự làm'),
          reason: 'citation phải mang SỐ LIỆU lần ngược được, không câu suông');
    }
  });

  test('⭐ nhiều ca yếu không phân giải được ⇒ tóm tắt CẢ NHÓM, nói rõ lý do', () {
    final e = explain({
      div: drill(div, [false, false]),
      nonDiv: drill(nonDiv, [false, false]),
    }, {div, nonDiv});
    expect(e.claim, ConceptClaim.needsWork);
    expect(e.message, contains('2 dạng'));
    expect(e.message, contains('chưa phân biệt được'),
        reason: '⭐ Decision 5: không chọn bừa một ca khi bằng chứng không '
            'chọn được — nói thẳng là chưa phân biệt được');
    expect(e.citations.length, 2);
  });

  test('một ca yếu rõ ⇒ nêu đích danh bằng TÊN SÁCH, không phải id nội bộ', () {
    final e = explain({
      div: drill(div, [true, true, true]),
      nonDiv: drill(nonDiv, [false, false, false]),
    }, {div, nonDiv});
    expect(e.claim, ConceptClaim.needsWork);
    expect(e.message, contains(names[nonDiv]!));
    expect(e.message, isNot(contains('denominator-non-divisible')),
        reason: 'id nội bộ không phải ngôn ngữ của phụ huynh');
    expect(e.citations.single.skillCaseId, nonDiv);
  });

  test('chỉ luyện với gợi ý ⇒ nói đúng thực tế đó, không kết luận hai hướng', () {
    var log = EvidenceLog.empty(div);
    for (var i = 0; i < 3; i++) {
      log = log
          .append(LearningEvent(
              eventId: 'h$i', skillCaseId: div,
              kind: EvidenceKind.hintShown, at: now))
          .append(LearningEvent(
              eventId: 's$i', skillCaseId: div,
              kind: EvidenceKind.postHintSuccess, correct: true, at: now));
    }
    final e = explain({div: replayMastery(log, p)}, {div});
    expect(e.claim, ConceptClaim.insufficientEvidence);
    expect(e.message, contains('với gợi ý'));
    expect(e.message, isNot(contains('đã vững')));
  });

  test('chưa có gì ⇒ "chưa làm" chứ KHÔNG PHẢI "chưa biết"', () {
    final e = explain({}, {div, nonDiv});
    expect(e.claim, ConceptClaim.noEvidence);
    expect(e.message, contains('Chưa làm KHÔNG có nghĩa là chưa biết'));
  });

  test('⭐⭐ tất định: thứ tự chèn Map không đổi một ký tự nào của câu', () {
    Map<String, CaseMastery> build(List<String> order) =>
        {for (final id in order) id: drill(id, [false, false])};
    final a = explain(build([div, nonDiv]), {div, nonDiv});
    final b = explain(build([nonDiv, div]), {div, nonDiv});
    expect(a.message, b.message);
    expect(a.citations.map((c) => c.skillCaseId).toList(),
        b.citations.map((c) => c.skillCaseId).toList());
  });
}
