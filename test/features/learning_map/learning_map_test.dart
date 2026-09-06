/// WAL-142 #19 — Map: badge CHỈ khi có evidence thật — không tiến-độ-ảo.
/// + QA Nokia n64: môn CÓ bằng chứng phải nổi lên đầu và mở sẵn, môn khác gập.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/core/store/learning_session.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/evidence_validation.dart';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/features/learning_map/learning_map_screen.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';

const _p = LearnerProfile(learnerId: 'l', displayName: 'M', grade: 5);

/// GDTC đứng TRƯỚC trong mục lục — đúng như file thật g5 (thứ tự map JSON).
LessonIndex _idx() => LessonIndex.fromJsonString('''
{"grade":5,"subjects":{
 "GDTC":[{"sourceDocumentId":"05-sgk-giao-duc-the-chat-5","volume":null,
  "lessons":[{"no":1,"title":"BÀI TẬP ĐỘI HÌNH ĐỘI NGŨ","pageStart":6}]}],
 "Toán":[{"sourceDocumentId":"05-sgk-toan-5-tap-mot","volume":"1",
  "lessons":[{"no":6,"title":"CỘNG, TRỪ HAI PHÂN SỐ","pageStart":20},
  {"no":7,"title":null,"pageStart":24}]},
  {"sourceDocumentId":"05-sgk-toan-5-tap-hai","volume":"2",
  "lessons":[{"no":80,"title":"DIỆN TÍCH HÌNH TAM GIÁC","pageStart":8}]}]},
 "toanExercises":{}}
''')!;

Future<void> _pump(WidgetTester t, LearnerStore store) async {
  await t.pumpWidget(MaterialApp(
      home: LearningMapScreen(profile: _p, store: store, index: _idx())));
  await t.pumpAndSettle();
}

Future<LearnerStore> _storeWithB6() async {
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
          validation: _r4Stamp,
          at: DateTime(2026, 9, 2, 19),
          support: SupportLevel.none,
          conceptIds: const ['quy-dong']),
    ],
  ));
  return store;
}

/// ROUND 4 (A-runtime, Founder §4 — strict validation default): the graded
/// events this test seeds simulate the Deep path (TutorSession), which has
/// stamped `fraction-check-v1` since round 3; unstamped graded events now read
/// as `historicalUnvalidated` and never as «Tự làm được». Fixture-only change,
/// no assertion changed. — lane A-runtime touched this Lane B test file.
const _r4Stamp =
    EvidenceValidation(validatorId: 'fraction-check-v1', validatorVersion: '1');

void main() {
  testWidgets('⭐ kho trắng ⇒ KHÔNG badge nào (không tiến-độ-ảo)', (t) async {
    await _pump(t, JsonlLearnerStore());
    expect(find.text('Toán · 3 bài'), findsOneWidget);
    // Chưa có bằng chứng ⇒ không mở sẵn môn nào; mở tay vẫn xem được mục lục.
    expect(find.textContaining('Bài 6'), findsNothing);
    await t.tap(find.text('Toán · 3 bài'));
    await t.pumpAndSettle();
    expect(find.textContaining('Bài 6'), findsOneWidget);
    expect(find.text('đang học cùng SAM'), findsNothing,
        reason: '⭐ đột biến badge-luôn-hiện ⇒ đỏ');
  });

  testWidgets('có evidence B6 ⇒ badge hiện đúng MỘT bài', (t) async {
    await _pump(t, await _storeWithB6());
    expect(find.text('đang học cùng SAM'), findsOneWidget);
  });

  testWidgets(
      '⭐ QA n64: môn có bằng chứng LÊN ĐẦU + mở sẵn; môn khác gập lại '
      '(bài có badge không bị chôn dưới hàng trăm dòng)', (t) async {
    await _pump(t, await _storeWithB6());
    final toan = t.getTopLeft(find.text('Toán · 3 bài')).dy;
    final gdtc = t.getTopLeft(find.text('GDTC · 1 bài')).dy;
    expect(toan, lessThan(gdtc),
        reason: '⭐ đột biến giữ thứ tự JSON ⇒ đỏ');
    // Toán mở sẵn (thấy bài), GDTC gập (không thấy bài của nó).
    expect(find.textContaining('Bài 6'), findsOneWidget);
    expect(find.textContaining('ĐỘI HÌNH ĐỘI NGŨ'), findsNothing);
    // Hai tập ⇒ nói rõ tập nào, «Bài 6» và «Bài 80» không lẫn.
    expect(find.text('Tập 1'), findsOneWidget);
    expect(find.text('Tập 2'), findsOneWidget);
  });
}
