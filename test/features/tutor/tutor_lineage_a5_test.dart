/// ⭐⭐ WAL-210 round 3 (A-runtime) — Founder A5 LINEAGE:
///
/// «Camera-originated Tutor: DEFAULT sourceDocumentId = null, lessonNo = null;
/// stamp only when the camera is invoked from an explicit, resolved,
/// trustworthy LearningContext. Never camera image → AI guess → lineage truth.»
///
/// Kiểm: (1) phiên từ bài CHỤP (ConfirmedProblem → CanonicalProblem) không
/// mang lineage; (2) `TutorSession.inContext` chỉ stamp khi context ĐÃ GIẢI
/// ra sách + bài; context tầng Global/Subject/Book ⇒ không stamp; (3) dấu
/// validator A3 đi cùng mọi sự kiện có chấm của phiên.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/context/learning_context.dart';
import 'package:learning_coach/core/curriculum/canonical_problem.dart';
import 'package:learning_coach/core/curriculum/pedagogical_boundary.dart';
import 'package:learning_coach/core/curriculum/solvable_problem.dart';
import 'package:learning_coach/core/intent/learning_intent.dart';
import 'package:learning_coach/core/knowledge/slice_curriculum.dart';
import 'package:learning_coach/core/perception/perception_provenance.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/student/evidence_validation.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/features/tutor/tutor_session.dart';

const _p5 = LearnerProfile(learnerId: 'L1', displayName: 'A', grade: 5);
const _expr = '3/4 + 2/5';
const _book = '05-sgk-toan-5-tap-mot';

TutorScope _scope() {
  final c = curriculumForProblem(_p5, _expr)!;
  return TutorScope.forProblem(
      c.conceptId, c.classifyCase(_expr), c.stage, c.catalogue);
}

/// Bài CHỤP — đúng cửa duy nhất của camera: hypothesis → confirm → canonical.
CanonicalProblem _cameraProblem() {
  final h = PerceptionHypothesis(
      hypothesisId: 'h1',
      rawImageRef: 'img:sha256:abc',
      expression: _expr,
      pipelineVersion: 'test-ocr-v0',
      at: DateTime(2026, 9, 5));
  return CanonicalProblem.fromConfirmedPerception(
      ConfirmedProblem.confirm(h, at: DateTime(2026, 9, 5)));
}

TutorSession _session(CanonicalProblem p, LearningContext? ctx) =>
    TutorSession.inContext(
      exerciseId: p.exerciseId,
      skillCaseId: 'denominator-non-divisible',
      problem: FractionProblem.parse(p.expression)!,
      scope: _scope(),
      learningContext: ctx,
      now: () => DateTime(2026, 9, 5, 10),
      sessionToken: 'tok',
    );

final class _NotFraction implements SolvableProblem {
  @override
  bool checkAnswer(String raw) => true;
  @override
  Map<String, String> get slots => const {};
}

void main() {
  test('⭐⭐ A5 MẶC ĐỊNH: phiên từ bài CHỤP ⇒ sourceDocumentId == null && '
      'lessonNo == null trên phiên VÀ trên mọi sự kiện', () {
    final p = _cameraProblem();
    expect(p.origin, ProblemOrigin.confirmedPerception);
    final s = _session(p, null)..submit('23/20');
    expect(s.sourceDocumentId, isNull);
    expect(s.lessonNo, isNull);
    expect(s.log.events, isNotEmpty);
    for (final e in s.log.events) {
      expect(e.sourceDocumentId, isNull, reason: e.eventId);
      expect(e.lessonNo, isNull, reason: e.eventId);
    }
  });

  test('⭐⭐ camera + context CHƯA giải ra bài (tầng Global/Subject/Book) ⇒ '
      'vẫn KHÔNG stamp — không stamp nửa vời', () {
    const global = LearningContext(learnerId: 'L1', grade: 5);
    const subject = LearningContext(learnerId: 'L1', grade: 5, subject: 'Toán');
    const bookOnly = LearningContext(
        learnerId: 'L1', grade: 5, subject: 'Toán', sourceDocumentId: _book);
    for (final ctx in [global, subject, bookOnly]) {
      final s = _session(_cameraProblem(), ctx)..submit('23/20');
      expect(s.sourceDocumentId, isNull, reason: 'ctx=$ctx');
      expect(s.lessonNo, isNull, reason: 'ctx=$ctx');
      expect(TutorSession.lineageFromContext(ctx), (null, null));
    }
    expect(bookOnly.hasLesson, isFalse);
  });

  test('⭐⭐ CHỈ context ĐÃ GIẢI (sách + bài) mới stamp — cùng luật với '
      'openCanonicalProblem(learningContext:)', () {
    const resolved = LearningContext(
        learnerId: 'L1',
        grade: 5,
        subject: 'Toán',
        sourceDocumentId: _book,
        lessonNo: 6,
        intent: LearningIntent.practice);
    expect(resolved.hasLesson, isTrue);
    expect(TutorSession.lineageFromContext(resolved), (_book, 6));
    final s = _session(_cameraProblem(), resolved)..submit('23/20');
    expect(s.sourceDocumentId, _book);
    expect(s.lessonNo, 6);
    for (final e in s.log.events) {
      expect(e.sourceDocumentId, _book);
      expect(e.lessonNo, 6);
    }
  });

  test('⭐ A3: sự kiện CÓ CHẤM của phiên mang dấu fraction-check-v1; sự kiện '
      'xin gợi ý không mang dấu', () {
    final s = _session(_cameraProblem(), null);
    s.requestHint();
    s.submit('1/2'); // sai, có hỗ trợ ⇒ guidedAttempt
    s.submit('23/20');
    final hint = s.log.events.firstWhere((e) => e.kind == EvidenceKind.hintRequested);
    expect(hint.validation, isNull);
    for (final e in s.log.events.where((e) => e.correct != null)) {
      expect(e.validation?.validatorId, 'fraction-check-v1', reason: e.kind.name);
      expect(e.hasApprovedValidation, isTrue);
    }
    expect(s.validator.validation.validatorId, 'fraction-check-v1');
  });

  test('⭐ A3 fail closed: loại bài chưa có validator đăng ký ⇒ KHÔNG mở được '
      'phiên chấm', () {
    expect(
        () => TutorSession(
              exerciseId: 'x',
              skillCaseId: 'c',
              problem: _NotFraction(),
              scope: _scope(),
            ),
        throwsArgumentError);
  });

  test('⭐ A3 fail closed: validator tiêm vào mà không có trong sổ ⇒ từ chối',
      () {
    expect(
        () => TutorSession(
              exerciseId: 'x',
              skillCaseId: 'c',
              problem: FractionProblem.parse(_expr)!,
              scope: _scope(),
              validator: const _Rogue(),
            ),
        throwsArgumentError);
  });
}

final class _Rogue extends DeterministicValidator {
  const _Rogue();
  @override
  String get validatorId => 'llm-judge-v1';
  @override
  String get validatorVersion => '1';
  @override
  bool check(String rawAnswer) => true;
}
