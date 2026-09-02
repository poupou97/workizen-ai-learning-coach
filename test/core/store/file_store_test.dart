/// WAL-108 — FileLearnerStore: kho sống qua «restart» (đóng rồi mở lại file),
/// lineage (support/policy/interventionId) sống qua đĩa, dòng hỏng không sập.
library;

import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/file_store.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learning_session.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/mastery.dart';

void main() {
  late Directory tmp;
  setUp(() async {
    tmp = await Directory.systemTemp.createTemp('sam-store-test');
  });
  tearDown(() async {
    await tmp.delete(recursive: true);
  });

  File f() => File('${tmp.path}/learner-store.jsonl');

  LearningSession session(String learnerId) => LearningSession(
        sessionId: 's-1',
        learnerId: learnerId,
        subjectId: 'toan',
        startedAt: DateTime(2026, 9, 2, 19),
        trigger: SessionTrigger.cameraHomework,
        skillCaseIds: const ['denominator-non-divisible'],
        events: [
          LearningEvent(
            eventId: 'e1',
            skillCaseId: 'denominator-non-divisible',
            kind: EvidenceKind.hintRequested,
            at: DateTime(2026, 9, 2, 19, 1),
            support: SupportLevel.none,
            policyId: 'tutor-session-v1',
            interventionId: 'tutor-session-v1/common-denom-by-product@hint',
          ),
          LearningEvent(
            eventId: 'e2',
            skillCaseId: 'denominator-non-divisible',
            kind: EvidenceKind.postHintSuccess,
            correct: true,
            at: DateTime(2026, 9, 2, 19, 2),
            support: SupportLevel.hint,
            policyId: 'tutor-session-v1',
            interventionId: 'tutor-session-v1/common-denom-by-product@hint',
          ),
        ],
      );

  test('ghi → đóng → mở lại: profile + phiên + LINEAGE nguyên vẹn', () async {
    final s1 = await FileLearnerStore.open(f());
    await s1.saveProfile(const LearnerProfile(
        learnerId: 'l-a', displayName: 'Minh', grade: 5));
    await s1.appendSession(session('l-a'));

    // «restart»: instance MỚI đọc từ đĩa, không còn gì trong bộ nhớ cũ.
    final s2 = await FileLearnerStore.open(f());
    final p = await s2.profile('l-a');
    expect(p?.displayName, 'Minh');
    expect(p?.grade, 5);

    final log = await s2.evidenceFor(
        learnerId: 'l-a', skillCaseId: 'denominator-non-divisible');
    expect(log.events, hasLength(2));
    final hint = log.events.first;
    expect(hint.interventionId,
        'tutor-session-v1/common-denom-by-product@hint',
        reason: '«exact hint identity» phải sống qua đĩa (§3)');
    expect(log.events.last.support, SupportLevel.hint);
    expect(log.events.last.isSystemInfluenced, isTrue);
  });

  test('dòng cuối hỏng ⇒ kho vẫn nạp được các dòng lành', () async {
    final s1 = await FileLearnerStore.open(f());
    await s1.saveProfile(const LearnerProfile(
        learnerId: 'l-a', displayName: 'Minh', grade: 5));
    await f().writeAsString('\n{"type":"session","hỏng',
        mode: FileMode.append); // torn write: dòng MỚI vỡ, dòng cũ nguyên

    final s2 = await FileLearnerStore.open(f());
    expect((await s2.profiles()).map((p) => p.learnerId), ['l-a']);
  });

  test('hai learner cùng kho: bằng chứng KHÔNG lẫn (tiền đề WAL-109)',
      () async {
    final s1 = await FileLearnerStore.open(f());
    await s1.appendSession(session('l-a'));

    final s2 = await FileLearnerStore.open(f());
    final logB = await s2.evidenceFor(
        learnerId: 'l-b', skillCaseId: 'denominator-non-divisible');
    expect(logB.events, isEmpty,
        reason: 'NO CROSS-LEARNER EVIDENCE CONTAMINATION');
  });
}
