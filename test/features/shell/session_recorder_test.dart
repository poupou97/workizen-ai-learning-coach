/// WAL-95×97 — vòng khép kín: surface → recorder → kho → replay.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/core/store/learning_session.dart';
import 'package:learning_coach/core/student/evidence_weighting.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/features/shell/session_recorder.dart';

LearningEvent _e(String id, EvidenceKind k,
        {bool? correct, SupportLevel? sup}) =>
    LearningEvent(
        eventId: id,
        skillCaseId: 'lkc-nhan-biet-lap-tu',
        kind: k,
        correct: correct,
        conceptIds: const ['lien-ket-cau'],
        at: DateTime(2026, 9, 1, 19, id.length),
        support: sup,
        policyId: 'quiz-select-v1');

void main() {
  test('⭐ vòng khép kín: sự kiện surface → phiên → kho → REPLAY đúng', () async {
    final store = JsonlLearnerStore();
    final r = await recordSession(
      store: store,
      learnerId: 'l1',
      subjectId: 'tieng-viet',
      trigger: SessionTrigger.samRecommendation,
      events: [
        _e('e', EvidenceKind.independentAttempt,
            correct: true, sup: SupportLevel.none),
        _e('ee', EvidenceKind.finalCorrectness, correct: true),
      ],
    );
    expect(r.session, isNotNull);
    expect(r.violations, isEmpty);
    expect(r.session!.conceptIds, ['lien-ket-cau']);
    expect(r.session!.skillCaseIds, ['lkc-nhan-biet-lap-tu']);

    // nạp lại như khởi động app rồi replay
    final reloaded = JsonlLearnerStore.fromJsonl(store.toJsonl());
    final log = await reloaded.evidenceFor(
        learnerId: 'l1', skillCaseId: 'lkc-nhan-biet-lap-tu');
    // ROUND 4 (A-runtime, Founder §4): quiz-select (Scale) has NO registered
    // validator (Founder decision pending: `pack-option-key-v1`), so under the
    // default strict policy this event reads as `historicalUnvalidated`
    // (independentCorrect 0). The round-trip is asserted with the explicit
    // legacy read rule; the strict truth is asserted alongside.
    expect(replayMastery(log, BktParams.freeResponse).independentCorrect, 0,
        reason: 'mặc định siết: quiz-select chưa có validator ⇒ không phải năng lực');
    final m = replayMastery(log, BktParams.freeResponse,
        policy: const ConservativeBktPolicy());
    expect(m.independentCorrect, 1,
        reason: 'bằng chứng TỰ LÀM sống qua surface → kho → replay (luật đọc-cũ)');
  });

  test('không có sự kiện ⇒ KHÔNG tạo phiên rỗng', () async {
    final store = JsonlLearnerStore();
    final r = await recordSession(
        store: store,
        learnerId: 'l1',
        subjectId: 'toan',
        trigger: SessionTrigger.manual,
        events: const []);
    expect(r.session, isNull);
    expect(await store.sessions(learnerId: 'l1'), isEmpty);
  });

  test('⭐ phiên THI lẫn hỗ trợ ⇒ recorder TRẢ VỀ vi phạm, không im lặng',
      () async {
    final store = JsonlLearnerStore();
    final r = await recordSession(
      store: store,
      learnerId: 'l1',
      subjectId: 'toan',
      trigger: SessionTrigger.assessment,
      mode: SessionMode.assess,
      events: [
        _e('e', EvidenceKind.independentAttempt,
            correct: true, sup: SupportLevel.none),
        _e('ee', EvidenceKind.postHintSuccess,
            correct: true, sup: SupportLevel.hint),
      ],
    );
    expect(r.violations.map((e) => e.eventId), ['ee']);
    // vẫn LƯU (không giấu dữ liệu), nhưng vi phạm được nêu ra để xử lý
    expect(await store.sessions(learnerId: 'l1'), hasLength(1));
  });
}
