/// WAL-164 — bảng luật D2: mỗi dòng một test, cộng bất biến trùm.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/adaptive/error_hypothesis.dart';
import 'package:learning_coach/core/adaptive/review_priority.dart';
import 'package:learning_coach/core/student/mastery.dart';

final _now = DateTime(2026, 9, 3, 15);

CaseMastery _case({
  int correct = 0,
  int incorrect = 0,
  int supported = 0,
  DateTime? last,
}) =>
    CaseMastery(
      skillCaseId: 'k',
      pMastery: 0.5,
      evidenceCount: correct + incorrect,
      supportedCount: supported,
      independentCorrect: correct,
      independentIncorrect: incorrect,
      lastIndependentEvidenceAt:
          (correct + incorrect) > 0 ? (last ?? _now) : null,
    );

ConceptMastery _m(Map<String, CaseMastery> cases) =>
    ConceptMastery(conceptId: 'quy-dong', cases: {
      for (final e in cases.entries)
        e.key: CaseMastery(
          skillCaseId: e.key,
          pMastery: e.value.pMastery,
          evidenceCount: e.value.evidenceCount,
          supportedCount: e.value.supportedCount,
          independentCorrect: e.value.independentCorrect,
          independentIncorrect: e.value.independentIncorrect,
          lastIndependentEvidenceAt: e.value.lastIndependentEvidenceAt,
        )
    });

ReviewCandidate? _one(List<ReviewCandidate> l, String id) {
  for (final c in l) {
    if (c.skillCaseId == id) return c;
  }
  return null;
}

void main() {
  test('⭐⭐ BẤT BIẾN D2: MỘT câu sai KHÔNG tự thành báo động ở Hôm nay', () {
    final r = resolveReviewCandidates(
        mastery: _m({'k': _case(correct: 0, incorrect: 1)}), now: _now);
    expect(todayCandidates(r), isEmpty,
        reason: '⭐⭐ một lỗi đi thẳng lên Hôm nay ⇒ đỏ (WRONG ANSWER CREATES '
            'EVIDENCE, NOT AN ALARM)');
    expect(_one(r, 'k')!.priority, ReviewPriority.nearTerm);
  });

  test('sai LẺ giữa nhiều lần đúng ⇒ sơ suất, giữ nhịp bình thường', () {
    final r = resolveReviewCandidates(
        mastery: _m({'k': _case(correct: 3, incorrect: 1)}), now: _now);
    final c = _one(r, 'k')!;
    expect(c.priority, ReviewPriority.normal);
    expect(c.reason, contains('lỡ tay'));
  });

  test('tự làm SAI (chưa có nền đúng) ⇒ gặp lại GẦN, trong dải 1–3 ngày', () {
    final r = resolveReviewCandidates(
        mastery: _m({'k': _case(correct: 1, incorrect: 2)}), now: _now);
    final c = _one(r, 'k')!;
    expect(c.priority, ReviewPriority.nearTerm);
    final days = c.dueBy!.difference(_now).inDays;
    expect(days, inInclusiveRange(1, 3),
        reason: 'Founder D2: near-term là 1–3 ngày');
  });

  test('⭐ hiểu sai LẶP LẠI ⇒ NÂNG mức', () {
    final r = resolveReviewCandidates(
      mastery: _m({'k': _case(correct: 0, incorrect: 2)}),
      now: _now,
      hypotheses: const [
        ErrorHypothesis(
            type: ErrorHypothesisType.conceptual,
            skillCaseId: 'k',
            confidence: 0.55,
            supportingEvidence: ['e1', 'e2'],
            conflictingEvidence: [],
            policyId: 'error-rules-v1'),
      ],
    );
    expect(_one(r, 'k')!.priority, ReviewPriority.elevated,
        reason: '⭐ đột biến coi lặp lại như sai lẻ ⇒ đỏ');
    expect(_one(r, 'k')!.reason, contains('lặp lại'));
  });

  test('sai kiểu ẩu (careless) lặp lại ⇒ KHÔNG nâng — cẩu thả ≠ hổng kiến thức',
      () {
    final r = resolveReviewCandidates(
      mastery: _m({'k': _case(correct: 0, incorrect: 2)}),
      now: _now,
      hypotheses: const [
        ErrorHypothesis(
            type: ErrorHypothesisType.careless,
            skillCaseId: 'k',
            confidence: 0.6,
            supportingEvidence: ['e1', 'e2'],
            conflictingEvidence: [],
            policyId: 'error-rules-v1'),
      ],
    );
    expect(_one(r, 'k')!.priority, ReviewPriority.nearTerm);
  });

  test('⭐ TIỀN ĐỀ YẾU mà bài đang học cần ⇒ được lên Hôm nay', () {
    final r = resolveReviewCandidates(
        mastery: _m({'k': _case(correct: 0, incorrect: 1)}),
        now: _now,
        prerequisiteCaseIds: {'k'});
    expect(_one(r, 'k')!.priority, ReviewPriority.today);
    expect(todayCandidates(r), hasLength(1));
  });

  test('tiền đề CHƯA HỌC ⇒ không phải việc ÔN, không lên Hôm nay', () {
    final r = resolveReviewCandidates(
        mastery: _m({'k': _case()}), now: _now, prerequisiteCaseIds: {'k'});
    expect(todayCandidates(r), isEmpty,
        reason: 'chưa có bằng chứng nào thì đó là việc HỌC, không phải ÔN');
  });

  test('⭐ mapping KHÔNG CHẮC ⇒ fail conservative, không nâng mạnh', () {
    final r = resolveReviewCandidates(
      mastery: _m({'k': _case(correct: 0, incorrect: 3)}),
      now: _now,
      prerequisiteCaseIds: {'k'}, // đủ điều kiện lên Hôm nay…
      uncertainMappingCaseIds: {'k'}, // …nhưng mapping mơ hồ
      hypotheses: const [
        ErrorHypothesis(
            type: ErrorHypothesisType.conceptual,
            skillCaseId: 'k',
            confidence: 0.9,
            supportingEvidence: ['e1', 'e2', 'e3'],
            conflictingEvidence: [],
            policyId: 'error-rules-v1'),
      ],
    );
    final c = _one(r, 'k')!;
    expect(c.priority, ReviewPriority.normal,
        reason: '⭐ nâng ưu tiên dựa trên phép gán sai ⇒ bắt trẻ ôn thứ nó '
            'không hề làm sai');
    expect(c.becauseOfError, isFalse);
    expect(todayCandidates(r), isEmpty);
  });

  test('⭐ ĐÚNG NHỜ TRỢ GIÚP ⇒ ôn sớm hơn, nhưng KHÔNG bị coi là lỗi', () {
    final r = resolveReviewCandidates(
        mastery: _m({'k': _case(supported: 2)}), now: _now);
    final c = _one(r, 'k')!;
    expect(c.priority, ReviewPriority.nearTerm);
    expect(c.becauseOfError, isFalse,
        reason: '⭐ gọi một lần làm được là «sai» ⇒ đỏ');
    expect(c.reason, contains('tự làm'));
  });

  test('tất định: cùng đầu vào ⇒ cùng kết quả, thứ tự ổn định', () {
    final m = _m({
      'a': _case(correct: 0, incorrect: 2),
      'b': _case(correct: 5, incorrect: 0, last: DateTime(2026, 1, 1)),
      'c': _case(supported: 1),
    });
    final r1 = resolveReviewCandidates(mastery: m, now: _now);
    final r2 = resolveReviewCandidates(mastery: m, now: _now);
    expect(r1.map((e) => '${e.skillCaseId}:${e.priority}'),
        r2.map((e) => '${e.skillCaseId}:${e.priority}'));
    // mức cao đứng trước
    for (var i = 1; i < r1.length; i++) {
      expect(r1[i - 1].priority.index, greaterThanOrEqualTo(r1[i].priority.index));
    }
  });

  test('⭐ mọi ứng viên PHẢI mang câu chữ đọc được (UI không tự chế)', () {
    final r = resolveReviewCandidates(
        mastery: _m({
          'a': _case(correct: 0, incorrect: 2),
          'b': _case(supported: 1),
          'c': _case(correct: 3, incorrect: 1),
        }),
        now: _now);
    expect(r, isNotEmpty);
    for (final c in r) {
      expect(c.reason.trim(), isNotEmpty);
      expect(c.reason.length, greaterThan(20));
      // không đổ lỗi, không điểm số
      for (final bad in ['kém', 'dốt', 'điểm', '%']) {
        expect(c.reason.toLowerCase().contains(bad), isFalse,
            reason: 'câu «${c.reason}» chứa «$bad»');
      }
    }
  });
}
