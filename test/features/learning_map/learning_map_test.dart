/// WAL-142 #19 — Map: badge CHỈ khi có evidence thật — không tiến-độ-ảo.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/core/store/learning_session.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/features/learning_map/learning_map_screen.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';

const _p = LearnerProfile(learnerId: 'l', displayName: 'M', grade: 5);

LessonIndex _idx() => LessonIndex.fromJsonString('''
{"grade":5,"subjects":{"Toán":[{"sourceDocumentId":"05-sgk-toan-5-tap-mot",
 "volume":"1","lessons":[{"no":6,"title":"CỘNG, TRỪ HAI PHÂN SỐ","pageStart":20},
 {"no":7,"title":null,"pageStart":24}]}]},"toanExercises":{}}
''')!;

void main() {
  testWidgets('⭐ kho trắng ⇒ KHÔNG badge nào (không tiến-độ-ảo)', (t) async {
    await t.pumpWidget(MaterialApp(
        home: LearningMapScreen(
            profile: _p, store: JsonlLearnerStore(), index: _idx())));
    await t.pumpAndSettle();
    expect(find.textContaining('Bài 6'), findsOneWidget);
    expect(find.text('đang học cùng SAM'), findsNothing,
        reason: '⭐ đột biến badge-luôn-hiện ⇒ đỏ');
  });

  testWidgets('có evidence B6 ⇒ badge hiện đúng MỘT bài', (t) async {
    final store = JsonlLearnerStore();
    await store.appendSession(LearningSession(
      sessionId: 's1',
      learnerId: 'l',
      subjectId: 'toan',
      startedAt: DateTime(2026, 9, 2, 19),
      trigger: SessionTrigger.manual,
      events: [
        LearningEvent(
            eventId: 'e#0',
            skillCaseId: 'denominator-non-divisible',
            kind: EvidenceKind.independentAttempt,
            correct: true,
            at: DateTime(2026, 9, 2, 19),
            support: SupportLevel.none,
            conceptIds: const ['quy-dong']),
      ],
    ));
    await t.pumpWidget(MaterialApp(
        home: LearningMapScreen(profile: _p, store: store, index: _idx())));
    await t.pumpAndSettle();
    expect(find.text('đang học cùng SAM'), findsOneWidget);
  });
}
