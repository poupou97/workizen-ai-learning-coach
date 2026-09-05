/// WAL-142 #31 — Progress: chữ claim-gated, KHÔNG %/điểm/XP/streak (§16).
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/core/store/learning_session.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/evidence_validation.dart';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/features/progress/progress_screen.dart';

const _p = LearnerProfile(learnerId: 'l', displayName: 'M', grade: 5);

LearningSession _s(String id, SupportLevel sup, {bool selfCorrect = false}) {
  final at = DateTime(2026, 9, 2, 19);
  return LearningSession(
    sessionId: id,
    learnerId: 'l',
    subjectId: 'toan',
    startedAt: at,
    trigger: SessionTrigger.manual,
    events: [
      LearningEvent(
          eventId: '$id#0',
          skillCaseId: 'denominator-non-divisible',
          kind: selfCorrect
              ? EvidenceKind.selfCorrection
              : EvidenceKind.independentAttempt,
          correct: true,
          validation: _r4Stamp,
          at: at,
          support: sup,
          conceptIds: const ['quy-dong']),
    ],
  );
}

/// ROUND 4 (A-runtime, Founder §4 — strict validation default): the graded
/// events this test seeds simulate the Deep path (TutorSession), which has
/// stamped `fraction-check-v1` since round 3; unstamped graded events now read
/// as `historicalUnvalidated` and never as «Tự làm được». Fixture-only change,
/// no assertion changed. — lane A-runtime touched this Lane B test file.
const _r4Stamp =
    EvidenceValidation(validatorId: 'fraction-check-v1', validatorVersion: '1');

void main() {
  testWidgets('⭐ đếm TỰ-LÀM vs CÓ-HỖ-TRỢ đúng; tự-sửa được khen QUÁ TRÌNH; '
      'claim từ explainConcept; KHÔNG %/điểm', (t) async {
    final store = JsonlLearnerStore();
    await store.appendSession(_s('s1', SupportLevel.none));
    await store.appendSession(_s('s2', SupportLevel.hint));
    await store.appendSession(_s('s3', SupportLevel.none, selfCorrect: true));
    await t.pumpWidget(
        MaterialApp(home: ProgressScreen(profile: _p, store: store)));
    await t.pumpAndSettle();
    expect(find.textContaining('TỰ LÀM trọn vẹn 2 phiên'), findsOneWidget,
        reason: '⭐ đột biến kể phiên-có-hint thành tự-làm ⇒ đỏ');
    expect(find.textContaining('có SAM giúp 1 phiên'), findsOneWidget);
    expect(find.textContaining('tự phát hiện và sửa 1 lần'), findsOneWidget);
    // claim card đi qua explainConcept — có mặt câu về concept
    expect(find.textContaining('cộng, trừ phân số khác mẫu số'), findsWidgets);
    for (final w in t.widgetList<Text>(find.byType(Text))) {
      final txt = w.data ?? '';
      expect(txt.contains('%'), isFalse, reason: 'cấm %: "$txt"');
      expect(txt.toLowerCase().contains('xp'), isFalse);
      expect(txt.contains('điểm'), isFalse, reason: 'cấm điểm: "$txt"');
    }
  });

  testWidgets('kho trắng ⇒ nói thật «chưa có bằng chứng», không bịa', (t) async {
    await t.pumpWidget(MaterialApp(
        home: ProgressScreen(profile: _p, store: JsonlLearnerStore())));
    await t.pumpAndSettle();
    expect(find.textContaining('chưa có bằng chứng học nào'), findsOneWidget);
  });
}
