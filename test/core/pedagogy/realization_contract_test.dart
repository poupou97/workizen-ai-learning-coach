/// WAL-131 — contract: LLM không thể vượt policy; vi phạm rơi về deterministic.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/curriculum/pedagogical_boundary.dart';
import 'package:learning_coach/core/knowledge/slice_curriculum.dart';
import 'package:learning_coach/core/pedagogy/pedagogy_model.dart';
import 'package:learning_coach/core/pedagogy/realization_contract.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/core/tutor/output_guard.dart';

RealizationRequest req({
  TeachingAct act = TeachingAct.smallHint,
  AssistanceRung rung = AssistanceRung.smallHint,
  bool exam = false,
}) {
  final c = curriculumFor(
      const LearnerProfile(learnerId: 'l', displayName: 'M', grade: 5))!;
  final scope = TutorScope.forProblem(
      c.conceptId, 'denominator-non-divisible', c.stage, c.catalogue);
  return RealizationRequest(
    act: act,
    rung: rung,
    scope: scope,
    methodId: 'common-denom-by-product',
    grade: 5,
    facts: const DerivedFacts(
        commonDenominator: 20,
        answerForms: ['23/20'],
        intermediateForms: ['15/20', '8/20']),
    examMode: exam,
  );
}

void main() {
  group('§23 — realization policy per act (deterministic-first)', () {
    test('mọi act TÍNH ĐƯỢC từ bài: KHÔNG BAO GIỜ generative', () {
      for (final a in [
        TeachingAct.revealAnswer,
        TeachingAct.revealStep,
        TeachingAct.demonstrateStep,
        TeachingAct.workedExample,
      ]) {
        expect(realizationPolicyFor(a), RealizationPolicy.deterministic,
            reason: '$a: sai một con số là sai bài — không giao LLM');
      }
    });

    test('act generative đều thuộc nhóm ≤ hint (guard chặn được rò)', () {
      for (final a in TeachingAct.values) {
        if (realizationPolicyFor(a) == RealizationPolicy.generativeGuarded) {
          expect(supportLevelOf(a).index,
              lessThanOrEqualTo(SupportLevel.hint.index),
              reason: '$a generative mà lộ bước giải thì guard số học '
                  'không đủ (giới hạn L3 đã ghi ở output_guard)');
        }
      }
    });
  });

  group('§22 — validateRealization: LLM cannot override policy', () {
    test('văn bản sạch ở đúng mức: allowed', () {
      final v = validateRealization(
          'Hai mẫu số 4 và 5 không chia hết cho nhau — con nghĩ xem mẫu số '
          'chung lấy thế nào nhé?',
          req());
      expect(v.allowed, isTrue, reason: v.blockedReasons.join(','));
    });

    test('LLM nhắc BCNN (method lớp 6) ⇒ METHOD_NAME chặn', () {
      final v = validateRealization('Con dùng BCNN của 4 và 5 nhé!', req());
      expect(v.allowed, isFalse);
      expect(v.blockedReasons.join(), contains('METHOD_NAME'));
    });

    test('LLM rò mẫu số chung 20 ở mức hint ⇒ ESCALATION chặn', () {
      final v = validateRealization(
          'Mẫu số chung là 20 đó con!', req());
      expect(v.allowed, isFalse);
      expect(v.blockedReasons.join(), contains('ESCALATION'));
    });

    test('LLM rò đáp án khi chưa workedSolution ⇒ REVEAL chặn', () {
      final v = validateRealization(
          'Kết quả là 23/20 nhé.', req(rung: AssistanceRung.demonstration,
              act: TeachingAct.demonstrateStep));
      expect(v.allowed, isFalse);
      expect(v.blockedReasons.join(), contains('REVEAL'));
    });

    test('ENGINE lỗi — act nặng hơn rung ⇒ ACT_OVER_RUNG fail closed '
        '(không tin cả engine, huống gì model)', () {
      final v = validateRealization('...',
          req(act: TeachingAct.revealAnswer, rung: AssistanceRung.smallHint));
      expect(v.allowed, isFalse);
      expect(v.blockedReasons.single, startsWith('ACT_OVER_RUNG'));
    });

    test('exam mode: mọi lời dạy bị chặn (EXAM_TUTORING)', () {
      final v = validateRealization(
          'Con quy đồng hai phân số nhé', req(exam: true));
      expect(v.allowed, isFalse);
      expect(v.blockedReasons.join(), contains('EXAM_TUTORING'));
    });
  });

  group('interventionKind (WAL-130 finding #2)', () {
    test('id có hậu tố loại — replay ≠ transcript phân biệt được trong data',
        () {
      final replay = interventionIdWithKind('tutor-session-v1',
          'listen-1', SupportLevel.hint, InterventionKind.replayAudio);
      final script = interventionIdWithKind('tutor-session-v1',
          'listen-1', SupportLevel.hint, InterventionKind.transcript);
      expect(replay, 'tutor-session-v1/listen-1@hint#replayAudio');
      expect(replay == script, isFalse);
    });
  });
}
