/// WAL-142 #30 — Sessions: mỗi phiên kể đúng maxSupportIn (không kể đẹp).
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/core/store/learning_session.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/features/student/sessions_screen.dart';

const _p = LearnerProfile(learnerId: 'l', displayName: 'M', grade: 5);

LearningSession _s(String id, SupportLevel sup) => LearningSession(
      sessionId: id,
      learnerId: 'l',
      subjectId: 'toan',
      startedAt: DateTime(2026, 9, 2, 19),
      trigger: SessionTrigger.manual,
      events: [
        LearningEvent(
            eventId: '$id#0',
            skillCaseId: 'c',
            kind: EvidenceKind.independentAttempt,
            correct: true,
            at: DateTime(2026, 9, 2, 19),
            support: sup),
      ],
    );

void main() {
  testWidgets('⭐ phiên có hint KHÔNG kể «TỰ LÀM» — maxSupportIn là luật',
      (t) async {
    final store = JsonlLearnerStore();
    await store.appendSession(_s('s1', SupportLevel.none));
    await store.appendSession(_s('s2', SupportLevel.hint));
    await t.pumpWidget(
        MaterialApp(home: SessionsScreen(profile: _p, store: store)));
    await t.pumpAndSettle();
    expect(find.textContaining('TỰ LÀM trọn vẹn'), findsOneWidget);
    expect(find.textContaining('có gợi ý nhỏ'), findsOneWidget,
        reason: '⭐ đột biến label luôn-TỰ-LÀM ⇒ đỏ');
  });
}
