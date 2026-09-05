/// ⭐⭐ WAL-210 — DOCTRINE TEST cho Founder D1 (2026-09-05):
///
/// «Ungraded learner self-report / completion MUST NOT create competence,
/// mastery or independent-attempt claims. A tap such as "Con đã trả lời xong"
/// may establish participation/completion only. Competence/mastery requires
/// ValidatedEvidence. No parent-facing claim such as "Con đã tự làm được" may
/// be derived solely from an unvalidated tap.»
///
/// Ba tầng kiểm:
/// 1. CẤU TRÚC — không dòng mã nào trong `lib/` mint `independentAttempt`
///    với `correct: null` (đúng hai mẫu chữ đã tồn tại trước D1: audit C6).
/// 2. CỬA VALIDATOR — mọi claim chưa kiểm chứng qua `validateCandidateEvidence`
///    là `participation`, bất kể `support`.
/// 3. HÀM TRẠNG THÁI + BKT — participation (và dữ liệu cũ tương đương) không
///    bao giờ thành «tự làm được» / không đổi belief.
///
/// Track B (Lesson Workspace) tham chiếu: surface KHÔNG phát bằng chứng thì
/// không gọi `LearningEvent(` — và nếu phát, chỉ [EvidenceKind.participation]
/// cho tự báo. Danh sách điểm phát được phép nằm ở test (3) bên dưới.
library;

import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/context/learning_context.dart';
import 'package:learning_coach/core/intent/learning_intent.dart';
import 'package:learning_coach/core/pedagogy/pedagogy_model.dart'
    show TeachingAct;
import 'package:learning_coach/core/student/evidence_validator.dart';
import 'package:learning_coach/core/student/evidence_weighting.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/learning_map_state.dart';
import 'package:learning_coach/core/student/mastery.dart';

const _ctx = LearningContext(
    learnerId: 'L1',
    grade: 6,
    subject: 'KHTN',
    sourceDocumentId: '06-sgk-khoa-hoc-tu-nhien-6',
    lessonNo: 17,
    intent: LearningIntent.review);

/// Mọi tệp Dart trong lib/, bỏ dòng chú thích.
Iterable<(String, String)> _libSources() sync* {
  for (final f in Directory('lib').listSync(recursive: true).whereType<File>()) {
    if (!f.path.endsWith('.dart')) continue;
    final code = f
        .readAsLinesSync()
        .where((l) => !l.trimLeft().startsWith('//'))
        .join('\n');
    yield (f.path, code);
  }
}

void main() {
  group('1. CẤU TRÚC — không đường mã nào mint independentAttempt chưa chấm', () {
    test('⭐⭐ không còn `_emit(EvidenceKind.independentAttempt, null)`', () {
      final hits = [
        for (final (path, code) in _libSources())
          if (RegExp(r'independentAttempt,\s*null\)').hasMatch(code)) path
      ];
      expect(hits, isEmpty,
          reason: '⭐⭐ audit C6: chính mẫu chữ này biến nút bấm thành «tự làm»');
    });

    test('⭐⭐ không còn `kind: EvidenceKind.independentAttempt` đi kèm '
        '`correct: null`', () {
      final re = RegExp(
          r'kind:\s*EvidenceKind\.independentAttempt,[\s\S]{0,200}?correct:\s*null');
      final hits = [
        for (final (path, code) in _libSources()) if (re.hasMatch(code)) path
      ];
      expect(hits, isEmpty,
          reason: '⭐⭐ audit C6: Map/Source từng mint theo mẫu này');
    });

    test('⭐ `_emit(EvidenceKind.independentAttempt` chỉ còn với correct THẬT '
        '(biến bool, không phải null)', () {
      // Reader/Quiz: `_emit(_hintShown ? … : EvidenceKind.independentAttempt, correct)`
      // Tutor: `_emit(EvidenceKind.independentAttempt, correct)` — correct là bool.
      final re = RegExp(r'EvidenceKind\.independentAttempt,\s*\n?\s*([a-zA-Z_]+)\)');
      for (final (path, code) in _libSources()) {
        for (final m in re.allMatches(code)) {
          expect(m.group(1), isNot('null'), reason: path);
        }
      }
    });
  });

  group('2. CỬA VALIDATOR — claim chưa kiểm chứng ⇒ participation', () {
    LearningEvent? validate(SupportLevel support) => validateCandidateEvidence(
          CandidateEvidence(
              skillCaseId: 'khtn-thi-nghiem',
              learnerText: 'dầu nổi lên trên nước',
              policyId: 'experiment-v1',
              support: support,
              act: TeachingAct.askExplanation),
          context: _ctx,
          eventId: 'e#0',
          at: DateTime(2026, 9, 5),
        );

    test('⭐⭐ audit C6: support = workedStep ⇒ participation, KHÔNG independentAttempt',
        () {
      final ev = validate(SupportLevel.workedStep)!;
      expect(ev.kind, EvidenceKind.participation);
      expect(ev.correct, isNull);
      expect(ev.support, SupportLevel.workedStep, reason: 'support vẫn giữ');
      expect(ev.isParticipation, isTrue);
      expect(ev.isValidatedIndependentSuccess, isFalse);
    });

    test('support = none cũng chỉ là participation — không có trường chấm nào '
        'trong CandidateEvidence để «kiểm chứng»', () {
      expect(validate(SupportLevel.none)!.kind, EvidenceKind.participation);
    });

    test('lookup ⇒ vẫn không sự kiện (C6c giữ nguyên)', () {
      final ev = validateCandidateEvidence(
          const CandidateEvidence(
              skillCaseId: 'k', learnerText: 'x', policyId: 'p'),
          context: const LearningContext(
              learnerId: 'L1', grade: 6, intent: LearningIntent.lookup),
          eventId: 'e',
          at: DateTime(2026));
      expect(ev, isNull);
    });
  });

  group('3. HÀM TRẠNG THÁI + BKT — tự báo không bao giờ thành năng lực', () {
    LearningEvent ev(EvidenceKind k, {bool? correct}) => LearningEvent(
        eventId: 'e-${k.name}-$correct',
        skillCaseId: 'khtn-doc-hieu',
        kind: k,
        correct: correct,
        at: DateTime(2026, 9, 5),
        sourceDocumentId: _ctx.sourceDocumentId,
        lessonNo: _ctx.lessonNo);

    test('⭐⭐ participation ⇒ Learning Map «Đã học», không «Tự làm được»', () {
      final s = learningMapStateFor(
          sourceDocumentId: _ctx.sourceDocumentId!,
          lessonNo: _ctx.lessonNo!,
          allEvents: [ev(EvidenceKind.participation)]);
      expect(s, LearningMapState.participation);
      expect(childLabelFor(s).$2.contains('Tự làm'), isFalse);
    });

    test('⭐⭐ dữ liệu cũ: independentAttempt + correct null ⇒ đọc như participation',
        () {
      final legacy = ev(EvidenceKind.independentAttempt); // correct null
      expect(legacy.isParticipation, isTrue);
      expect(legacy.isValidatedIndependentSuccess, isFalse);
      expect(
          learningMapStateFor(
              sourceDocumentId: _ctx.sourceDocumentId!,
              lessonNo: _ctx.lessonNo!,
              allEvents: [legacy]),
          LearningMapState.participation);
    });

    test('⭐ BKT không đổi: participation ⇒ noOp, không evidenceCount, không learn',
        () {
      final log = EvidenceLog(skillCaseId: 'khtn-doc-hieu', events: [
        for (var i = 0; i < 10; i++) ev(EvidenceKind.participation),
      ]);
      final m = replayMastery(log, BktParams.freeResponse);
      final fresh = CaseMastery.initial('khtn-doc-hieu', BktParams.freeResponse);
      expect(m.evidenceCount, 0);
      expect(m.pMastery, fresh.pMastery,
          reason: '⭐ 10 lần bấm «xong» không được đẩy belief lên một li');
      expect(m.hasEvidence, isFalse);
    });

    test('participation không phải một lần trả lời, không nằm trong '
        'independentAttempts, không bị hệ thống ảnh hưởng', () {
      final p = ev(EvidenceKind.participation);
      expect(p.isAttempt, isFalse);
      expect(p.isSystemInfluenced, isFalse);
      expect(EvidenceLog(skillCaseId: 'c', events: [p]).independentAttempts,
          isEmpty);
    });

    test('bằng chứng tự làm ĐÃ CHẤM vẫn là bằng chứng (D1 không cấm đường Deep)',
        () {
      final ok = ev(EvidenceKind.independentAttempt, correct: true);
      expect(ok.isValidatedIndependentSuccess, isTrue);
      expect(ok.isParticipation, isFalse);
      expect(
          learningMapStateFor(
              sourceDocumentId: _ctx.sourceDocumentId!,
              lessonNo: _ctx.lessonNo!,
              allEvents: [ok]),
          LearningMapState.independentEvidence);
    });

    test('participation sống qua JSON (tên enum) — kho cũ đọc kind mới', () {
      // `EvidenceKind.values.where((v) => v.name == kind)` trong
      // learning_session.dart — tên phải ổn định vì nó nằm trên đĩa.
      expect(EvidenceKind.participation.name, 'participation');
    });
  });
}
