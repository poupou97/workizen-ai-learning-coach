/// ⭐⭐ F3 — LearningEvidence: sự kiện thô là nguồn sự thật, mastery TÍNH LẠI ĐƯỢC.
///
/// Founder Decision 4: không để
///   CAN THIỆP HỆ THỐNG → POST-HINT SUCCESS → GHI CÔNG MASTERY → HỆ THỐNG TỰ TIN
/// khép thành vòng tự xác nhận. Và: *"Preserve raw events. Derived mastery must
/// remain recomputable."*
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/student/evidence_weighting.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/mastery.dart';

void main() {
  const p = BktParams.freeResponse;
  const kase = 'denominator-divisible';
  final t0 = DateTime(2026, 9, 1, 8);

  var seq = 0;
  LearningEvent ev(EvidenceKind kind,
          {bool? correct, ResponseFormat format = ResponseFormat.freeResponse}) =>
      LearningEvent(
        eventId: 'e${seq++}',
        skillCaseId: kase,
        kind: kind,
        correct: correct,
        at: t0.add(Duration(minutes: seq)),
        format: format,
      );

  EvidenceLog log(List<LearningEvent> events) =>
      events.fold(EvidenceLog.empty(kase), (l, e) => l.append(e));

  test('⭐⭐ vòng tự xác nhận BỊ CHẶN: 10 post-hint success ⇒ 0 bằng chứng độc lập',
      () {
    final l = log([
      for (var i = 0; i < 10; i++) ...[
        ev(EvidenceKind.hintShown),
        ev(EvidenceKind.postHintSuccess, correct: true),
      ]
    ]);
    final m = replayMastery(l, p);
    expect(m.evidenceCount, 0,
        reason: '⭐⭐ mười lần "đúng sau gợi ý" không được thành một mẩu bằng '
            'chứng độc lập nào — nếu thành, hệ thống đang tự chấm điểm cho '
            'chính can thiệp của nó');
    expect(m.supportedCount, 10);
    expect(m.hasEvidence, isFalse);
  });

  test('⭐ bấm "xem gợi ý" liên tục KHÔNG đẩy mastery lên', () {
    final l = log([for (var i = 0; i < 20; i++) ev(EvidenceKind.hintRequested)]);
    expect(replayMastery(l, p).pMastery, p.prior,
        reason: 'công `learn` gắn vào lần TỰ THỬ sau gợi ý, không gắn vào '
            'việc hiện gợi ý — nếu không, nút gợi ý là máy in mastery');
  });

  test('⭐ tự làm đúng TRƯỚC gợi ý được tính đầy đủ (pre-hint independent)', () {
    final l = log([
      ev(EvidenceKind.independentAttempt, correct: true),
      ev(EvidenceKind.independentAttempt, correct: true),
    ]);
    final m = replayMastery(l, p);
    expect(m.evidenceCount, 2);
    expect(m.pMastery, greaterThan(0.85));
    expect(m.lastIndependentEvidenceAt, isNotNull);
  });

  test('⭐ selfCorrection là bằng chứng ĐỘC LẬP — mô hình cũ không biểu diễn được',
      () {
    final l = log([ev(EvidenceKind.selfCorrection, correct: true)]);
    final m = replayMastery(l, p);
    expect(m.evidenceCount, 1);
    expect(m.pMastery, greaterThan(p.prior));
  });

  test('finalCorrectness KHÔNG chấm hai lần cùng một lần làm', () {
    final attempt = log([ev(EvidenceKind.independentAttempt, correct: true)]);
    final withFinal = log([
      ev(EvidenceKind.independentAttempt, correct: true),
      ev(EvidenceKind.finalCorrectness, correct: true),
    ]);
    expect(replayMastery(withFinal, p).pMastery,
        replayMastery(attempt, p).pMastery,
        reason: 'kết quả chốt TRÙNG với lần thử cuối — chấm cả hai là đếm '
            'đôi một bằng chứng');
  });

  test('⭐ UNKNOWN không thành FAILED: dạng bài không rõ ⇒ không claim gì', () {
    final l = log([
      ev(EvidenceKind.independentAttempt,
          correct: false, format: ResponseFormat.unknown),
    ]);
    final m = replayMastery(l, p);
    expect(m.pMastery, p.prior,
        reason: 'không biết guess theo cấu trúc thì không diễn giải được câu '
            'trả lời — fail closed, không trừ điểm mò');
    expect(m.evidenceCount, 0);
  });

  test('⭐⭐ mastery TÍNH LẠI ĐƯỢC: replay tất định, log không đổi', () {
    final events = [
      ev(EvidenceKind.independentAttempt, correct: true),
      ev(EvidenceKind.hintShown),
      ev(EvidenceKind.postHintSuccess, correct: true),
      ev(EvidenceKind.independentAttempt, correct: false),
    ];
    final l = log(events);
    final a = replayMastery(l, p);
    final b = replayMastery(l, p);
    expect(a.pMastery, b.pMastery);
    expect(a.evidenceCount, b.evidenceCount);
    expect(l.events.length, 4, reason: 'replay không được ăn mất sự kiện nào');
  });

  test('⭐⭐ ĐỔI POLICY = tính lại, KHÔNG migration — và policy ngây thơ chính là F3',
      () {
    final l = log([
      ev(EvidenceKind.hintShown),
      ev(EvidenceKind.postHintSuccess, correct: true),
      ev(EvidenceKind.hintShown),
      ev(EvidenceKind.postHintSuccess, correct: true),
    ]);
    final conservative = replayMastery(l, p);
    final naive = replayMastery(l, p, policy: const _NaivePolicy());
    expect(naive.evidenceCount, 2,
        reason: 'policy ngây thơ tính post-hint như tự làm — đây là hành vi '
            'CŨ trước F3, giữ ở test làm bằng chứng đối chứng');
    expect(conservative.evidenceCount, 0);
    expect(naive.pMastery, greaterThan(conservative.pMastery),
        reason: '⭐⭐ chênh lệch này CHÍNH LÀ kích thước của vòng tự xác nhận '
            'mà policy bảo thủ chặn lại');
  });

  test('tương thích: observeWithSupport cho CÙNG số với replay tương đương', () {
    // Chuỗi: tự làm đúng ×2 — đường cũ và đường mới phải ra cùng một số.
    var old = CaseMastery.initial(kase, p);
    old = old.observe(true, p);
    old = old.observe(true, p);
    final viaReplay = replayMastery(
        log([
          ev(EvidenceKind.independentAttempt, correct: true),
          ev(EvidenceKind.independentAttempt, correct: true),
        ]),
        p);
    expect(viaReplay.pMastery, closeTo(old.pMastery, 1e-12),
        reason: 'hai đường cùng một số học — khác nhau chỉ ở chỗ replay giữ '
            'được sự kiện gốc');
  });
}

/// Policy đối chứng — hành vi TRƯỚC F3. Chỉ dùng trong test.
class _NaivePolicy implements EvidenceWeightingPolicy {
  const _NaivePolicy();
  @override
  String get policyId => 'naive-pre-f3';
  @override
  EvidenceUpdate interpret(LearningEvent e, BktParams p) {
    if (e.correct == null) return EvidenceUpdate.noOp;
    return EvidenceUpdate(
      likelihood: ObservationLikelihood(
          pCorrectGivenKnown: 1 - p.slip, pCorrectGivenUnknown: p.guess),
      appliesLearning: true,
      countsAsIndependent: true,
    );
  }
}
