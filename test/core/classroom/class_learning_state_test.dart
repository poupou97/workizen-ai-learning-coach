import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/classroom/class_learning_state.dart';
import 'package:learning_coach/core/student/concept_summary.dart';
import 'package:learning_coach/core/student/mastery.dart';

final _now = DateTime(2026, 9, 2);

ConceptSummary sum({
  double pMastery = 0.7,
  int evidence = 4,
  int correct = 4,
  int incorrect = 0,
  int supported = 0,
  String caseId = 'ca1',
  Set<String>? known,
}) =>
    ConceptSummary.of(
      ConceptMastery(conceptId: 'c', cases: {
        if (evidence > 0 || supported > 0)
          caseId: CaseMastery(
            skillCaseId: caseId,
            pMastery: pMastery,
            evidenceCount: evidence,
            independentCorrect: correct,
            independentIncorrect: incorrect,
            supportedCount: supported,
            lastIndependentEvidenceAt: evidence > 0 ? _now : null,
          ),
      }),
      knownCaseIds: known ?? {caseId},
      now: _now,
    );

StudentConceptRow row(String id, ConceptSummary s) =>
    StudentConceptRow(studentId: id, summary: s);

void main() {
  test('1 em mastered + 1 em noEvidence KHÔNG thành «lớp trung bình» — '
      'hai nhóm tách bạch, không có trường mean nào tồn tại', () {
    final st = classConceptState('c', [
      row('hs-gioi', sum(pMastery: 0.9, evidence: 5, correct: 5)),
      row('hs-moi', sum(evidence: 0)),
    ]);
    expect(st.strong, ['hs-gioi']);
    expect(st.noData, ['hs-moi']);
    expect(st.needsWork, isEmpty); // em mới KHÔNG bị xếp «yếu»
  });

  test('UNKNOWN ≠ weak: toàn-luyện-có-hỗ-trợ cũng vào noData', () {
    final st = classConceptState('c', [
      row('hs-hint', sum(evidence: 0, supported: 6)),
    ]);
    expect(st.noData, ['hs-hint']);
    expect(st.needsWork, isEmpty);
  });

  test('ca yếu phổ biến = MODE có danh sách tên — truy về từng em (F4)', () {
    final weak = sum(pMastery: 0.3, correct: 0, incorrect: 4);
    final st = classConceptState('c', [
      row('hs-b', weak),
      row('hs-a', weak),
      row('hs-kha', sum()),
    ]);
    expect(st.commonWeakCases.length, 1);
    expect(st.commonWeakCases.first.$1, 'ca1');
    expect(st.commonWeakCases.first.$2, ['hs-a', 'hs-b']);
    expect(st.developing, ['hs-kha']);
  });

  test('mode sắp theo SỐ EM giảm dần — tên ca không đảo được thứ tự', () {
    final weakZ = sum(pMastery: 0.3, correct: 0, incorrect: 4, caseId: 'ca-z');
    final weakA = sum(pMastery: 0.3, correct: 0, incorrect: 4, caseId: 'ca-a');
    final st = classConceptState('c', [
      row('hs1', weakZ),
      row('hs2', weakZ),
      row('hs3', weakA),
    ]);
    // ca-z có 2 em, ca-a có 1 em ⇒ ca-z đứng trước dù 'ca-a' < 'ca-z'
    expect(st.commonWeakCases.map((e) => e.$1), ['ca-z', 'ca-a']);
    expect(st.commonWeakCases.first.$2, ['hs1', 'hs2']);
  });

  test('unobservedByAll = giao các tập: một em từng được quan sát ca đó '
      'thì ca đó KHÔNG còn là lỗ của cả lớp', () {
    final st = classConceptState('c', [
      row('hs1', sum(known: {'ca1', 'ca2'})), // ca2 chưa quan sát ở hs1
      row('hs2', sum(known: {'ca1'})), // hs2 không có ca2 trong danh mục
    ]);
    expect(st.unobservedByAll, isEmpty);
    final st2 = classConceptState('c', [
      row('hs1', sum(known: {'ca1', 'ca2'})),
      row('hs2', sum(known: {'ca1', 'ca2'})),
    ]);
    expect(st2.unobservedByAll, ['ca2']);
  });

  test('lớp rỗng → mọi nhóm rỗng, không nổ', () {
    final st = classConceptState('c', []);
    expect(st.noData, isEmpty);
    expect(st.unobservedByAll, isEmpty);
  });
}
