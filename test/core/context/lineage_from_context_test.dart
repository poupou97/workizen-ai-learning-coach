/// ⭐⭐ ROUND 4 (A-runtime) — Founder §4 CAMERA LINEAGE, giữ nguyên A5:
///
/// «Camera Tutor: DEFAULT lineage null/null; stamp only from an explicit
/// resolved LearningContext; never camera → AI guess → lineage truth.»
///
/// Kiểm ở TẦNG CORE (không widget): mọi cửa stamp lineage trong core —
/// `LessonRef.fromContext`, `TutorSession.lineageFromContext`,
/// `validateCandidateEvidence` — đều trả `null/null` khi context CHƯA giải ra
/// đủ (sách + số bài); một `CanonicalProblem` từ nhận dạng ảnh KHÔNG mang
/// trường lineage nào để «đoán» được; và không có đường mã nào trong core
/// suy `lessonNo` từ biểu thức / ảnh.
library;

import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/context/learning_context.dart';
import 'package:learning_coach/core/curriculum/canonical_problem.dart';
import 'package:learning_coach/core/curriculum/semantic_binding.dart';
import 'package:learning_coach/core/intent/learning_intent.dart';
import 'package:learning_coach/core/perception/perception_provenance.dart';
import 'package:learning_coach/core/student/evidence_validator.dart';
import 'package:learning_coach/features/tutor/tutor_session.dart';

const _book = '05-sgk-toan-5-tap-mot';

/// Ba tầng context CHƯA giải ra bài — cùng bộ với `tutor_lineage_a5_test`.
const _unresolved = [
  LearningContext(learnerId: 'L1', grade: 5),
  LearningContext(learnerId: 'L1', grade: 5, subject: 'Toán'),
  LearningContext(
      learnerId: 'L1', grade: 5, subject: 'Toán', sourceDocumentId: _book),
  // Có số bài mà KHÔNG có sách — nửa context theo chiều ngược lại.
  LearningContext(learnerId: 'L1', grade: 5, subject: 'Toán', lessonNo: 6),
];

const _resolved = LearningContext(
    learnerId: 'L1',
    grade: 5,
    subject: 'Toán',
    sourceDocumentId: _book,
    lessonNo: 6,
    intent: LearningIntent.practice);

void main() {
  test('⭐⭐ context CHƯA giải ra bài ⇒ không cửa nào stamp được (null/null)', () {
    for (final c in _unresolved) {
      expect(c.hasLesson, isFalse, reason: '$c');
      expect(LessonRef.fromContext(c), isNull, reason: 'A6/A8 cửa: $c');
      expect(TutorSession.lineageFromContext(c), (null, null),
          reason: 'A5 cửa Tutor: $c');
      // Cửa claim tự do: sự kiện participation vẫn sinh, nhưng lineage null.
      final ev = validateCandidateEvidence(
        const CandidateEvidence(
            skillCaseId: 'k', learnerText: 'dầu nổi', policyId: 'exp-v1'),
        context: c,
        eventId: 'e',
        at: DateTime(2026, 9, 5),
      );
      expect(ev, isNotNull);
      expect(ev!.sourceDocumentId, isNull, reason: '$c');
      expect(ev.lessonNo, isNull, reason: '$c');
    }
    expect(LessonRef.fromContext(null), isNull);
    expect(TutorSession.lineageFromContext(null), (null, null));
  });

  test('CHỈ context đã giải (sách + bài) mới stamp — và stamp ĐÚNG cặp', () {
    expect(_resolved.hasLesson, isTrue);
    expect(LessonRef.fromContext(_resolved), const LessonRef(_book, 6));
    expect(TutorSession.lineageFromContext(_resolved), (_book, 6));
  });

  test('⭐⭐ bài từ NHẬN DẠNG ẢNH không mang trường lineage nào để đoán', () {
    final h = PerceptionHypothesis(
        hypothesisId: 'h1',
        rawImageRef: 'img:sha256:abc',
        expression: '3/4 + 2/5',
        pipelineVersion: 'test-ocr-v0',
        at: DateTime(2026, 9, 5));
    final p = CanonicalProblem.fromConfirmedPerception(
        ConfirmedProblem.confirm(h, at: DateTime(2026, 9, 5)));
    expect(p.origin, ProblemOrigin.confirmedPerception);
    // Kiểm bằng cấu trúc: lớp CanonicalProblem không khai
    // sourceDocumentId/lessonNo — không có chỗ để một bước «AI đoán bài»
    // ghi vào. Nếu ai thêm trường đó, test này phải được sửa CÓ CHỦ ĐÍCH.
    final src = File('lib/core/curriculum/canonical_problem.dart')
        .readAsLinesSync()
        .where((l) => !l.trimLeft().startsWith('//'))
        .join('\n');
    expect(src.contains('lessonNo'), isFalse,
        reason: 'CanonicalProblem không được mang số bài');
    expect(src.contains('sourceDocumentId'), isFalse,
        reason: 'CanonicalProblem không được mang sách');
  });

  test('⭐ không đường mã nào trong core/perception hay core/curriculum suy '
      'lessonNo từ ảnh/biểu thức', () {
    final banned = RegExp(r'lessonNo\s*[:=]');
    for (final dir in ['lib/core/perception', 'lib/core/curriculum']) {
      for (final f in Directory(dir).listSync(recursive: true).whereType<File>()) {
        if (!f.path.endsWith('.dart')) continue;
        final code = f
            .readAsLinesSync()
            .where((l) => !l.trimLeft().startsWith('//'))
            .join('\n');
        // semantic_binding.dart chỉ ĐỌC lessonNo từ context (LessonRef.fromContext)
        // và khai LessonRef; không suy từ ảnh.
        if (f.path.endsWith('semantic_binding.dart') ||
            f.path.endsWith('khtn6_bai17.dart') ||
            f.path.endsWith('concept.dart') ||
            f.path.endsWith('skill_case.dart')) {
          continue;
        }
        expect(banned.hasMatch(code), isFalse,
            reason: '${f.path}: gán lessonNo ngoài context');
      }
    }
  });
}
