/// WAL-101 — TUTOR EVAL LAYER 2: golden scenario bank (CI, tất định).
///
/// Mỗi kịch bản = input cố định → assert TRẠNG THÁI NỘI BỘ (decision /
/// evidence / speech-gate), không chấm văn phong. Nguồn: bảng 13 kịch bản
/// trong docs/research/SAM-TUTOR-EVALUATION-FRAMEWORK.md §2.
///
/// GHI THẬT phạm vi: các kịch bản cần perception hoặc NỘI DUNG lời dạy LLM
/// (reading-level ≤12 từ, phát hiện guessing theo thời gian, executionError→
/// practice khi chưa có ErrorHypothesis) thuộc sim-harness WAL-87 / Layer 3
/// — KHÔNG giả vờ đo ở đây. Bank này phủ các kịch bản kernel đo được ngay.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/curriculum/pedagogical_boundary.dart';
import 'package:learning_coach/core/eval/tutor_metrics.dart';
import 'package:learning_coach/core/knowledge/provenance.dart';
import 'package:learning_coach/core/store/learning_session.dart';
import 'package:learning_coach/core/student/concept_summary.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/core/tutor/learning_activity.dart';
import 'package:learning_coach/core/tutor/teaching_provenance.dart';
import 'package:learning_coach/core/tutor/tutor_feedback.dart';

LearningEvent ev(String id, EvidenceKind kind,
        {bool? correct, SupportLevel? support}) =>
    LearningEvent(
      eventId: id,
      skillCaseId: 'B57',
      kind: kind,
      at: DateTime(2026, 9, 2),
      correct: correct,
      support: support,
    );

LearningSession ses(String id, List<LearningEvent> events) => LearningSession(
      sessionId: id,
      learnerId: 'L1',
      subjectId: 'toan',
      startedAt: DateTime(2026, 9, 1),
      trigger: SessionTrigger.manual,
      events: events,
    );

final _stage = LearningStage(
  grade: 5,
  bookSeries: 'KNTT',
  lessonId: 'B57',
  conceptsIntroduced: const {'quy-dong'},
  methodsIntroduced: const {'m-quydong', 'm-bcnn'},
  terminologyIntroduced: const {'quy đồng'},
);

final _mQuyDong = TeachingMethod(
  id: 'm-quydong',
  name: 'Quy đồng mẫu số',
  appliesToConcepts: const {'quy-dong'},
  requiresConcepts: const {},
  requiresTerminology: const {'quy đồng'},
  skillCaseId: 'B57',
  provenance: const Provenance(
    origin: KnowledgeOrigin.sourceDemonstrated, // ca B57 canonical
    sourceId: 'toan-5-kntt-t2',
    extractionMethod: 'manual',
    confidence: 0.9,
    subject: 'Toán',
    grade: 5,
    pageStart: 32,
  ),
);

final _mBcnn = TeachingMethod(
  id: 'm-bcnn',
  name: 'Quy đồng bằng BCNN',
  appliesToConcepts: const {'quy-dong'},
  requiresConcepts: const {'bcnn'}, // lớp 5 KNTT CHƯA giới thiệu
  requiresTerminology: const {},
  skillCaseId: 'B57',
);

void main() {
  group('S1 — «Xin đáp án thẳng»: REVEAL gate', () {
    test('trace tuân gate (thử trước, xem lời giải sau) → premature = 0', () {
      final r = evaluateSessions([
        ses('ok', [
          ev('e1', EvidenceKind.independentAttempt,
              correct: false, support: SupportLevel.none),
          ev('e2', EvidenceKind.hintShown, support: SupportLevel.fullSolution),
        ]),
      ]);
      expect(r.prematureAnswerSessions, isEmpty);
    });

    test('trace lộ đáp án khi trẻ chưa thử → bank BẮT được', () {
      final r = evaluateSessions([
        ses('bad', [
          ev('e1', EvidenceKind.hintShown, support: SupportLevel.fullSolution),
        ]),
      ]);
      expect(r.prematureAnswerSessions, ['bad']);
    });
  });

  group('S2 — «Sai lặp nhiều lần»: leo thang đúng MỘT nấc mỗi lần', () {
    test('hint → workedStep → fullSolution: sạch', () {
      final r = evaluateSessions([
        ses('s', [
          ev('e1', EvidenceKind.independentAttempt,
              correct: false, support: SupportLevel.none),
          ev('e2', EvidenceKind.hintShown, support: SupportLevel.hint),
          ev('e3', EvidenceKind.guidedAttempt,
              correct: false, support: SupportLevel.workedStep),
          ev('e4', EvidenceKind.hintShown, support: SupportLevel.fullSolution),
        ]),
      ]);
      expect(r.escalationViolations, isEmpty);
    });

    test('hint → fullSolution (bỏ nấc) → bị gắn đúng sự kiện', () {
      final r = evaluateSessions([
        ses('s', [
          ev('e1', EvidenceKind.hintShown, support: SupportLevel.hint),
          ev('e2', EvidenceKind.hintShown, support: SupportLevel.fullSolution),
        ]),
      ]);
      expect(r.escalationViolations, ['e2']);
    });
  });

  group('S3 — «L4 quy đồng B57»: citation DEMONSTRATED, không «sách nói»', () {
    test('sourceLineForChild = «SAM làm theo ví dụ…», không phải «Theo SGK»',
        () {
      final scope = TutorScope.forProblem(
          'quy-dong', 'B57', _stage, [_mQuyDong, _mBcnn]);
      final t = explainTeaching(
          scope: scope, methodId: 'm-quydong', exerciseCase: 'B57');
      expect(t, isNotNull);
      expect(t!.sourceLineForChild, contains('SAM làm theo ví dụ'));
      expect(t.sourceLineForChild.startsWith('Theo'), false);
      expect(t.authority, KnowledgeOrigin.sourceDemonstrated);
    });
  });

  group('S4 — «L6 chưa có trong scope»: fail-closed, 0 nội dung bịa', () {
    test('không xác định được ca → scope RỖNG → explainTeaching null', () {
      final scope =
          TutorScope.forProblem('quy-dong', null, _stage, [_mQuyDong]);
      expect(scope.allowedMethods, isEmpty);
      expect(
          explainTeaching(
              scope: scope, methodId: 'm-quydong', exerciseCase: null),
          isNull);
    });
  });

  group('S5 — «L12 chuyên đề»: không dạy vượt stage dù đúng toán học', () {
    test('BCNN đòi concept chưa giới thiệu → bị loại + không giải thích', () {
      final scope = TutorScope.forProblem(
          'quy-dong', 'B57', _stage, [_mQuyDong, _mBcnn]);
      expect(scope.allowedMethods.map((m) => m.id), isNot(contains('m-bcnn')));
      expect(
          explainTeaching(
              scope: scope, methodId: 'm-bcnn', exerciseCase: 'B57'),
          isNull);
    });
  });

  group('S6 — «L9 nghị luận»: không chấm hộ, không văn mẫu', () {
    test('compose không gradable → UNKNOWN, và surface là compose riêng', () {
      const a = LearningActivity(
        activityId: 'a1',
        prompt: 'Viết đoạn văn nêu cảm nghĩ…',
        response: ResponseKind.compose,
        conceptId: 'nghi-luan',
      );
      expect(a.gradable, false); // không đáp án ⇒ không bao giờ chấm SAI
      expect(resolveSurface(a), SurfaceKind.compose);
    });

    test('shortText chưa có surface → unsupported, không ép vào quiz', () {
      const a = LearningActivity(
        activityId: 'a2',
        prompt: 'Trả lời ngắn',
        response: ResponseKind.shortText,
        conceptId: 'x',
      );
      expect(resolveSurface(a), SurfaceKind.unsupported);
    });
  });

  group('S7 — «Overconfident»: coverage chặn claim', () {
    final now = DateTime(2026, 9, 2);
    final strongCase = CaseMastery(
      skillCaseId: 'ca1',
      pMastery: 0.9,
      evidenceCount: 5,
      independentCorrect: 5,
      lastIndependentEvidenceAt: now,
    );

    test('vững ca đã quan sát nhưng còn ca chưa quan sát → KHÔNG «mastered»',
        () {
      final s = ConceptSummary.of(
        ConceptMastery(conceptId: 'c', cases: {'ca1': strongCase}),
        knownCaseIds: {'ca1', 'ca2'},
        now: now,
      );
      expect(s.claim, ConceptClaim.strongOnObserved);
      expect(s.unobservedCases, ['ca2']); // nói thẳng, không giấu
    });

    test('phủ hết ca đã biết → lúc đó mới được «mastered»', () {
      final s = ConceptSummary.of(
        ConceptMastery(conceptId: 'c', cases: {'ca1': strongCase}),
        knownCaseIds: {'ca1'},
        now: now,
      );
      expect(s.claim, ConceptClaim.mastered);
    });
  });

  group('S8 — affect: sai không bị phạt, khen không chạm tư chất', () {
    test('mọi nhánh feedbackFor sạch danh sách cấm khen-tư-chất', () {
      final all = [
        feedbackFor(
            correct: false,
            maxSupport: SupportLevel.none,
            selfCorrected: false),
        feedbackFor(
            correct: true, maxSupport: SupportLevel.none, selfCorrected: true),
        feedbackFor(
            correct: true, maxSupport: SupportLevel.none, selfCorrected: false),
        feedbackFor(
            correct: true, maxSupport: SupportLevel.hint, selfCorrected: false),
      ];
      for (final f in all) {
        for (final banned in bannedAbilityPraise) {
          expect(f.praise.toLowerCase(), isNot(contains(banned)),
              reason: 'khen tư chất «$banned» bị cấm');
          expect(f.evidenceLine.toLowerCase(), isNot(contains(banned)));
        }
      }
    });

    test('sai → evidence vẫn ghi nhận, lời lẽ không trừng phạt', () {
      final f = feedbackFor(
          correct: false, maxSupport: SupportLevel.none, selfCorrected: false);
      expect(f.evidenceNote, EvidenceNote.attemptRecorded);
      expect(f.praise, contains('dám thử'));
    });
  });

  group('S9 — toàn luyện-có-hỗ-trợ KHÔNG phải bằng chứng (F3)', () {
    test('chỉ supportedCount → insufficientEvidence, không claim gì hơn', () {
      final s = ConceptSummary.of(
        ConceptMastery(conceptId: 'c', cases: {
          'ca1': const CaseMastery(
              skillCaseId: 'ca1',
              pMastery: 0.5,
              evidenceCount: 0,
              supportedCount: 6),
        }),
        knownCaseIds: {'ca1'},
        now: DateTime(2026, 9, 2),
      );
      expect(s.claim, ConceptClaim.insufficientEvidence);
      expect(s.supportedPracticeCount, 6); // Coach nói được sự thật này
      expect(s.estimatedMastery, isNull); // không mượn số của ca không bằng chứng
    });
  });
}
