/// ⭐⭐ WAL-210 round 3 (A-runtime) — DOCTRINE TEST cho Founder A3:
///
/// «SELF REPORT ≠ COMPETENCE. Only deterministic/approved validators may
/// create evidence strong enough to change competence/mastery.»
///
/// Bốn tầng kiểm:
/// 1. KIỂU — `ValidatedEvidence` chỉ mint được qua `DeterministicValidator`
///    ĐÃ ĐĂNG KÝ; validator lạ không mint được; sổ đăng ký chỉ chứa validator
///    tất định; surface Scale KHÔNG có validator.
/// 2. CẤU TRÚC — mọi chỗ trong `lib/` dựng `LearningEvent(` với `correct:`
///    KHÁC null đều đóng dấu `validation:` — trừ danh sách CÔNG KHAI các
///    emitter chưa đóng dấu (ngoài quyền sửa của lane này; phải RÚT NGẮN,
///    không được dài ra).
/// 3. HÀM TRẠNG THÁI + BKT — dấu validator LẠ ⇒ không «Tự làm được», không
///    đẩy belief; chế độ SIẾT (`requireValidation`) ⇒ không dấu cũng không.
/// 4. PARENT — câu «tự làm được» chỉ khi state là independentEvidence, và ở
///    chế độ siết state đó chỉ đến từ sự kiện có dấu được duyệt.
library;

import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/coach/parent_session_summary.dart';
import 'package:learning_coach/core/context/learning_context.dart';
import 'package:learning_coach/core/curriculum/fraction_problem.dart';
import 'package:learning_coach/core/curriculum/solvable_problem.dart';
import 'package:learning_coach/core/intent/learning_intent.dart';
import 'package:learning_coach/core/store/learning_session.dart';
import 'package:learning_coach/core/student/evidence_validation.dart';
import 'package:learning_coach/core/student/evidence_validator.dart';
import 'package:learning_coach/core/student/evidence_weighting.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/learning_map_state.dart';
import 'package:learning_coach/core/student/mastery.dart';

const _book = '06-sgk-khoa-hoc-tu-nhien-6';
const _fraction = EvidenceValidation(
    validatorId: 'fraction-check-v1', validatorVersion: '1');
const _rogue =
    EvidenceValidation(validatorId: 'llm-judge-v1', validatorVersion: '1');

LearningEvent _ev(EvidenceKind k,
        {bool? correct, EvidenceValidation? validation, int lessonNo = 17}) =>
    LearningEvent(
      eventId: 'e-${k.name}-$correct-${validation?.validatorId}',
      skillCaseId: 'chon-cach-tach-theo-tinh-chat',
      kind: k,
      correct: correct,
      at: DateTime(2026, 9, 5),
      sourceDocumentId: _book,
      lessonNo: lessonNo,
      validation: validation,
    );

/// `strict == null` ⇒ dùng MẶC ĐỊNH THẬT của hàm (ROUND 4: siết); truyền
/// `false` chỉ để kiểm luật đọc-cũ tường minh.
LearningMapState _state(List<LearningEvent> es, {bool? strict}) => strict == null
    ? learningMapStateFor(sourceDocumentId: _book, lessonNo: 17, allEvents: es)
    : learningMapStateFor(
        sourceDocumentId: _book,
        lessonNo: 17,
        allEvents: es,
        requireValidation: strict);

/// Validator KHÔNG đăng ký — thứ một agent về sau có thể viết ra.
final class _RogueValidator extends DeterministicValidator {
  const _RogueValidator();
  @override
  String get validatorId => 'llm-judge-v1';
  @override
  String get validatorVersion => '1';
  @override
  bool check(String rawAnswer) => true;
}

final class _NotFraction implements SolvableProblem {
  @override
  bool checkAnswer(String raw) => true;
  @override
  Map<String, String> get slots => const {};
}

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

/// Thân của mỗi lời gọi `LearningEvent(` — cân ngoặc để lấy đúng một lời gọi.
Iterable<String> _eventConstructions(String code) sync* {
  var from = 0;
  while (true) {
    final i = code.indexOf('LearningEvent(', from);
    if (i < 0) return;
    var depth = 0;
    var j = i + 'LearningEvent'.length;
    for (; j < code.length; j++) {
      final c = code[j];
      if (c == '(') depth++;
      if (c == ')') {
        depth--;
        if (depth == 0) break;
      }
    }
    yield code.substring(i, j + 1);
    from = j + 1;
  }
}

void main() {
  group('1. KIỂU — ValidatedEvidence chỉ từ validator đã đăng ký', () {
    test('⭐⭐ fraction-check-v1 mint được; đúng/sai theo số học', () {
      final v = FractionCheckValidator(FractionProblem.parse('3/4 + 2/5')!);
      expect(v.grade('23/20')!.correct, isTrue);
      expect(v.grade('1/2')!.correct, isFalse);
      expect(v.grade('23/20')!.validation, _fraction);
      expect(v.validation.grantsCompetence, isTrue);
    });

    test('⭐⭐ validator KHÔNG đăng ký ⇒ grade() trả null, không mint được gì',
        () {
      const rogue = _RogueValidator();
      expect(rogue.grade('bất kỳ'), isNull,
          reason: 'không có đường mint ValidatedEvidence ngoài sổ đăng ký');
      expect(rogue.validation.isRegistered, isFalse);
      expect(rogue.validation.grantsCompetence, isFalse);
    });

    test('⭐ sổ đăng ký: mọi validator đều tất định; Scale KHÔNG có validator',
        () {
      for (final r in approvedEvidenceValidators.values) {
        expect(r.deterministic, isTrue, reason: r.validatorId);
      }
      expect(approvedEvidenceValidators.keys.toSet(),
          {'fraction-check-v1', 'candidate-gate-v1'},
          reason: '⭐ Founder A3: không bịa validator cho surface Scale — thêm '
              'một id là một quyết định phải ghi vào ROUND3-RUNTIME-CONTRACTS');
      expect(approvedEvidenceValidators['candidate-gate-v1']!.grantsCompetence,
          isFalse,
          reason: 'cửa claim tự do chỉ cấp participation');
    });

    test('approvedValidatorFor: phân số ⇒ fraction-check-v1; loại khác ⇒ null',
        () {
      expect(approvedValidatorFor(FractionProblem.parse('1/2 + 1/3')!),
          isA<FractionCheckValidator>());
      expect(approvedValidatorFor(_NotFraction()), isNull,
          reason: 'fail closed — không có validator thì không được chấm');
    });

    test('EvidenceValidation JSON: đi-về nguyên vẹn; lệch kiểu ⇒ null', () {
      expect(EvidenceValidation.fromJson(_fraction.toJson()), _fraction);
      expect(EvidenceValidation.fromJson(null), isNull);
      expect(EvidenceValidation.fromJson({'validatorId': 'x'}), isNull);
      expect(EvidenceValidation.fromJson({'validatorId': '', 'validatorVersion': '1'}),
          isNull);
    });

    test('⭐ dấu sống qua LearningSession JSON; sự kiện cũ không dấu ⇒ null',
        () {
      final s = LearningSession(
        sessionId: 's',
        learnerId: 'L',
        subjectId: 'khtn',
        startedAt: DateTime(2026, 9, 5),
        trigger: SessionTrigger.manual,
        events: [
          _ev(EvidenceKind.independentAttempt,
              correct: true, validation: _fraction),
          _ev(EvidenceKind.independentAttempt, correct: true),
        ],
      );
      final back = LearningSession.fromJson(s.toJson())!;
      expect(back.events[0].validation, _fraction);
      expect(back.events[1].validation, isNull);
      expect(back.events[1].isLegacyUnstampedGrade, isTrue);
      expect(s.toJson().toString().contains('validation'), isTrue);
    });

    test('validateCandidateEvidence đóng dấu candidate-gate-v1 (participation)',
        () {
      final ev = validateCandidateEvidence(
        const CandidateEvidence(
            skillCaseId: 'k', learnerText: 'dầu nổi', policyId: 'exp-v1'),
        context: const LearningContext(
            learnerId: 'L',
            grade: 6,
            sourceDocumentId: _book,
            lessonNo: 17,
            intent: LearningIntent.review),
        eventId: 'e',
        at: DateTime(2026),
      )!;
      expect(ev.kind, EvidenceKind.participation);
      expect(ev.validation?.validatorId, 'candidate-gate-v1');
      expect(ev.hasApprovedValidation, isFalse,
          reason: 'dấu participation KHÔNG cấp năng lực');
      expect(ev.isValidatedIndependentSuccess, isFalse);
    });
  });

  group('2. CẤU TRÚC — mọi emitter có chấm trong lib/ đều đóng dấu', () {
    /// Emitter CÓ CHẤM nhưng CHƯA đóng dấu — ngoài quyền sửa của lane
    /// A-runtime (Lane B / Founder). Danh sách chỉ được NGẮN ĐI.
    const unstampedAllowlist = {
      // Deep (Toán 5) — chấm bằng FractionProblem.checkAnswer ⇒ cần
      // `validation: fraction-check-v1` (một dòng, Lane B / coordinator).
      'lib/features/assessment/assessment_screen.dart',
      // Scale — khoá `correctOption` của pack: KHÔNG bịa validator; Founder
      // quyết có đăng ký «pack-option-key» hay để participation.
      'lib/features/shell/reader_screen.dart',
      'lib/features/shell/quiz_select_screen.dart',
      // Demo domain của Home (dữ liệu mẫu, không phải bằng chứng thật).
      'lib/features/mission/mission_data.dart',
    };

    test('⭐⭐ LearningEvent( với correct ≠ null ⇒ có validation:, hoặc nằm '
        'trong danh sách công khai', () {
      final gradedRe = RegExp(r'correct:\s*(?!null\b)[A-Za-z_][\w.!]*');
      final unstamped = <String>{};
      for (final (path, code) in _libSources()) {
        for (final ctor in _eventConstructions(code)) {
          if (!gradedRe.hasMatch(ctor)) continue; // không chấm ⇒ không cần dấu
          if (ctor.contains('validation:')) continue;
          unstamped.add(path);
        }
      }
      expect(unstamped.difference(unstampedAllowlist), isEmpty,
          reason: '⭐⭐ emitter MỚI có chấm mà không đóng dấu validator');
      expect(unstampedAllowlist.difference(unstamped), isEmpty,
          reason: 'đã đóng dấu rồi thì RÚT khỏi danh sách — không giữ nợ ma');
    });

    test('⭐ TutorSession (Deep) đóng dấu — không còn trong danh sách', () {
      expect(unstampedAllowlist.contains('lib/features/tutor/tutor_session.dart'),
          isFalse);
    });
  });

  group('3. HÀM TRẠNG THÁI + BKT', () {
    test('⭐⭐ dấu validator LẠ ⇒ KHÔNG «Tự làm được», BKT noOp', () {
      final rogue = _ev(EvidenceKind.independentAttempt,
          correct: true, validation: _rogue);
      expect(rogue.hasRejectedValidation, isTrue);
      expect(rogue.isValidatedIndependentSuccess, isFalse);
      expect(_state([rogue]), LearningMapState.engaged,
          reason: 'có chấm nhưng validator không được duyệt ⇒ chỉ «đã học cùng SAM»');
      final m = replayMastery(
          EvidenceLog(skillCaseId: 'c', events: [rogue, rogue, rogue]),
          BktParams.freeResponse);
      expect(m.evidenceCount, 0);
      expect(m.pMastery, BktParams.freeResponse.prior);
    });

    test('⭐⭐ dấu được duyệt + correct ⇒ independentEvidence, BKT đếm', () {
      final ok = _ev(EvidenceKind.independentAttempt,
          correct: true, validation: _fraction);
      expect(ok.hasApprovedValidation, isTrue);
      expect(_state([ok]), LearningMapState.independentEvidence);
      expect(_state([ok], strict: true), LearningMapState.independentEvidence);
      expect(
          replayMastery(EvidenceLog(skillCaseId: 'c', events: [ok]),
                  BktParams.freeResponse)
              .evidenceCount,
          1);
    });

    test('⭐⭐ ROUND 4 — SIẾT LÀ MẶC ĐỊNH: có chấm nhưng KHÔNG dấu (dữ liệu cũ) '
        '⇒ historicalUnvalidated ⇒ engaged, BKT noOp; luật đọc-cũ chỉ khi gọi '
        'tường minh (audit), và log không đổi', () {
      final legacy = _ev(EvidenceKind.independentAttempt, correct: true);
      expect(legacy.isLegacyUnstampedGrade, isTrue);
      expect(legacy.isHistoricalUnvalidated, isTrue);
      expect(legacy.readClass, EvidenceReadClass.historicalUnvalidated);
      expect(_state([legacy]), LearningMapState.engaged,
          reason: '⭐⭐ Founder §4: không viết lại lịch sử để tạo sự thật mới');
      expect(_state([legacy], strict: true), LearningMapState.engaged);
      expect(_state([legacy], strict: false), LearningMapState.independentEvidence,
          reason: 'luật đọc-cũ (#63) chỉ khi GỌI TƯỜNG MINH — audit/đối chiếu');
      final log = EvidenceLog(skillCaseId: 'c', events: [legacy]);
      expect(replayMastery(log, BktParams.freeResponse).evidenceCount, 0,
          reason: '⭐⭐ mặc định = ValidatedOnlyBktPolicy');
      expect(
          replayMastery(log, BktParams.freeResponse,
                  policy: const ValidatedOnlyBktPolicy())
              .evidenceCount,
          0);
      expect(
          replayMastery(log, BktParams.freeResponse,
                  policy: const ConservativeBktPolicy())
              .evidenceCount,
          1,
          reason: 'luật cũ giữ nguyên id + hành vi — không diễn giải lại lặng lẽ');
      expect(const ValidatedOnlyBktPolicy().policyId, 'validated-only-bkt-v1');
      expect(const ConservativeBktPolicy().policyId, 'conservative-bkt-v1');
      expect(defaultEvidencePolicy.policyId, 'validated-only-bkt-v1');
      expect(log.events.single.validation, isNull, reason: 'không đóng dấu hộ');
    });

    test('participation có dấu candidate-gate ⇒ vẫn participation ở cả hai '
        'chế độ', () {
      const gate = EvidenceValidation(
          validatorId: 'candidate-gate-v1', validatorVersion: '1');
      final p = _ev(EvidenceKind.participation, validation: gate);
      expect(_state([p]), LearningMapState.participation);
      expect(_state([p], strict: true), LearningMapState.participation);
    });
  });

  group('5. ROUND 4 — lớp đọc (EvidenceReadClass): mỗi sự kiện đúng MỘT lớp', () {
    test('⭐ phân lớp đúng cho từng dạng sự kiện', () {
      expect(_ev(EvidenceKind.independentAttempt, correct: true, validation: _fraction).readClass,
          EvidenceReadClass.validatedCompetence);
      expect(_ev(EvidenceKind.independentAttempt, correct: false, validation: _fraction).readClass,
          EvidenceReadClass.validatedCompetence,
          reason: 'sai-có-kiểm vẫn là bằng chứng đã kiểm (BKT đọc correct)');
      expect(_ev(EvidenceKind.independentAttempt, correct: true).readClass,
          EvidenceReadClass.historicalUnvalidated);
      expect(_ev(EvidenceKind.postHintSuccess, correct: true).readClass,
          EvidenceReadClass.historicalUnvalidated);
      expect(_ev(EvidenceKind.independentAttempt, correct: true, validation: _rogue).readClass,
          EvidenceReadClass.rejectedValidation);
      expect(_ev(EvidenceKind.participation).readClass, EvidenceReadClass.participation);
      expect(_ev(EvidenceKind.independentAttempt).readClass, EvidenceReadClass.participation,
          reason: 'D1: independentAttempt + correct null = tự báo cũ');
      expect(
          _ev(EvidenceKind.participation,
                  validation: const EvidenceValidation(
                      validatorId: 'candidate-gate-v1', validatorVersion: '1'))
              .readClass,
          EvidenceReadClass.participation);
      expect(_ev(EvidenceKind.hintRequested).readClass, EvidenceReadClass.unscored);
      expect(_ev(EvidenceKind.hintShown).readClass, EvidenceReadClass.unscored);
    });

    test('⭐⭐ chỉ validatedCompetence mới «tự làm được»; historicalUnvalidated '
        'không bao giờ — kể cả selfCorrection', () {
      for (final k in [EvidenceKind.independentAttempt, EvidenceKind.selfCorrection]) {
        expect(_ev(k, correct: true, validation: _fraction).isValidatedIndependentSuccess, isTrue);
        expect(_ev(k, correct: true).isValidatedIndependentSuccess, isFalse, reason: k.name);
        expect(_ev(k, correct: true).isLegacyUnstampedSuccess, isTrue, reason: k.name);
        expect(_ev(k, correct: true, validation: _rogue).isLegacyUnstampedSuccess, isFalse);
      }
    });
  });

  group('4. PARENT — «tự làm được» chỉ từ bằng chứng có dấu được duyệt', () {
    LearningSession sess(List<LearningEvent> es) => LearningSession(
        sessionId: 's',
        learnerId: 'L',
        subjectId: 'khtn',
        startedAt: DateTime(2026, 9, 5),
        trigger: SessionTrigger.manual,
        events: es);

    test('⭐⭐ dấu lạ ⇒ câu cho phụ huynh KHÔNG chứa «tự làm được»', () {
      final touches = recentLessonTouches([
        sess([
          _ev(EvidenceKind.independentAttempt,
              correct: true, validation: _rogue)
        ])
      ]);
      final line = parentLineFor(touches.single);
      // Câu «engaged» nói rõ «chưa có lần nào tự làm được ghi lại» — đó là
      // PHỦ ĐỊNH; cấm là câu KHẲNG ĐỊNH «Con đã tự làm được …».
      expect(line.startsWith('Con đã tự làm được'), isFalse, reason: line);
      expect(line, contains('chưa có lần nào tự làm được'));
    });

    test('dấu được duyệt ⇒ «Con đã tự làm được Bài 17.»', () {
      final touches = recentLessonTouches([
        sess([
          _ev(EvidenceKind.independentAttempt,
              correct: true, validation: _fraction)
        ])
      ]);
      expect(parentLineFor(touches.single), 'Con đã tự làm được Bài 17.');
    });

    test('tự báo ⇒ câu hoàn thành, không «tự làm được» (D1 giữ nguyên)', () {
      final touches =
          recentLessonTouches([sess([_ev(EvidenceKind.participation)])]);
      expect(parentLineFor(touches.single), contains('SAM không chấm'));
    });
  });
}
