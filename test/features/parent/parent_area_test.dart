/// WAL-109 §26 — PIN gate + «Tình hình các con»: không lẫn con, không xếp hạng.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/core/store/learning_session.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/features/parent/parent_area.dart';

const _a = LearnerProfile(learnerId: 'l-a', displayName: 'Minh', grade: 5);
const _b = LearnerProfile(learnerId: 'l-b', displayName: 'Lan', grade: 5);

Future<JsonlLearnerStore> seed({bool withPin = true}) async {
  final store = JsonlLearnerStore();
  await store.saveProfile(_a);
  await store.saveProfile(_b);
  if (withPin) await store.saveParentPin('1234');
  // Minh có bằng chứng tự làm; Lan chưa học gì — hai thẻ PHẢI kể khác nhau.
  await store.appendSession(LearningSession(
    sessionId: 's-a',
    learnerId: 'l-a',
    subjectId: 'toan',
    startedAt: DateTime(2026, 9, 2, 8),
    trigger: SessionTrigger.cameraHomework,
    events: [
      LearningEvent(
        eventId: 'a1',
        skillCaseId: 'denominator-non-divisible',
        kind: EvidenceKind.independentAttempt,
        correct: true,
        at: DateTime(2026, 9, 2, 8, 1),
      ),
    ],
  ));
  return store;
}

void main() {
  testWidgets('PIN sai ⇒ đứng ngoài; PIN đúng ⇒ vào Tình hình các con',
      (tester) async {
    final store = await seed();
    await tester.pumpWidget(MaterialApp(
        home: Builder(
            builder: (context) => TextButton(
                onPressed: () =>
                    openParentArea(context, store: store, profiles: [_a, _b]),
                child: const Text('go')))));
    await tester.tap(find.text('go'));
    await tester.pumpAndSettle();

    expect(find.text('Nhập PIN khu bố mẹ'), findsOneWidget);
    await tester.enterText(find.byType(TextField), '9999');
    await tester.tap(find.text('Mở khu bố mẹ'));
    await tester.pumpAndSettle();
    expect(find.text('PIN chưa đúng.'), findsOneWidget);
    expect(find.text('Tình hình các con'), findsNothing);

    await tester.enterText(find.byType(TextField), '1234');
    await tester.tap(find.text('Mở khu bố mẹ'));
    await tester.pumpAndSettle();
    expect(find.text('Tình hình các con'), findsOneWidget);
  });

  testWidgets('chưa có PIN ⇒ đặt 2 lần rồi vào; PIN được LƯU', (tester) async {
    final store = await seed(withPin: false);
    await tester.pumpWidget(MaterialApp(
        home: Builder(
            builder: (context) => TextButton(
                onPressed: () =>
                    openParentArea(context, store: store, profiles: [_a]),
                child: const Text('go')))));
    await tester.tap(find.text('go'));
    await tester.pumpAndSettle();
    expect(find.text('Đặt PIN cho khu bố mẹ'), findsOneWidget);
    await tester.enterText(find.byType(TextField), '2468');
    await tester.tap(find.text('Đặt PIN'));
    await tester.pumpAndSettle();
    expect(find.text('Nhập lại PIN lần nữa'), findsOneWidget);
    await tester.enterText(find.byType(TextField), '2468');
    await tester.tap(find.text('Đặt PIN'));
    await tester.pumpAndSettle();
    expect(find.text('Tình hình các con'), findsOneWidget);
    expect(await store.parentPin(), '2468');
  });

  testWidgets('mỗi con MỘT thẻ claim-gated riêng — không merge, không xếp hạng',
      (tester) async {
    final store = await seed();
    await tester.pumpWidget(MaterialApp(
        home: ParentOverviewScreen(store: store, profiles: const [_a, _b])));
    await tester.pumpAndSettle();

    expect(find.text('Minh · Lớp 5'), findsOneWidget);
    expect(find.text('Lan · Lớp 5'), findsOneWidget);
    // Lan CHƯA học ⇒ thẻ Lan phải là noEvidence («chưa làm bài nào»); Minh
    // có bằng chứng ⇒ KHÔNG được mang câu đó. Hai kho không lẫn.
    expect(find.textContaining('Con chưa làm bài nào'), findsOneWidget,
        reason: 'đúng MỘT thẻ noEvidence (Lan) — Minh không bị kể nhầm');
    // Không ngôn ngữ xếp hạng.
    for (final banned in ['giỏi hơn', 'kém hơn', 'hơn em', 'hơn anh', 'nhất']) {
      expect(find.textContaining(banned), findsNothing, reason: banned);
    }
    // Lối đi tiếp theo TỪNG con.
    expect(find.text('Tối nay cùng Minh ▸'), findsOneWidget);
    expect(find.text('Tối nay cùng Lan ▸'), findsOneWidget);
  });
}
