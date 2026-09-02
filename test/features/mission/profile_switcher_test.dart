/// WAL-109 — A→B→A: switch không logout, KHÔNG lẫn dữ liệu giữa hai trẻ,
/// mission của mỗi người tính từ KHO CỦA CHÍNH NGƯỜI ĐÓ.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/core/store/learning_session.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/main.dart';

Future<JsonlLearnerStore> seed() async {
  final store = JsonlLearnerStore();
  await store.saveProfile(const LearnerProfile(
      learnerId: 'l-a', displayName: 'Minh', grade: 5));
  await store.saveProfile(const LearnerProfile(
      learnerId: 'l-b', displayName: 'Lan', grade: 5));
  // A ĐÃ học: một lần tự-làm-đúng dạng không-chia-hết → A hết «chưa thử»
  // dạng đó; B thì CHƯA — hai màn Hôm nay phải KHÁC nhau.
  await store.appendSession(LearningSession(
    sessionId: 's-a-1',
    learnerId: 'l-a',
    subjectId: 'toan',
    startedAt: DateTime(2026, 9, 2, 8),
    trigger: SessionTrigger.cameraHomework,
    skillCaseIds: const ['denominator-non-divisible'],
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
  testWidgets('A học → switch B → switch A: mỗi người thấy ĐÚNG kho của mình',
      (tester) async {
    final store = await seed();
    await tester.pumpWidget(HocCungSamApp(store: store));
    await tester.pumpAndSettle();

    // A (hồ sơ đầu) đang active — đã có bằng chứng nên KHÔNG còn
    // «chưa thử» dạng không-chia-hết.
    expect(find.text('Chào Minh!'), findsOneWidget);
    expect(find.textContaining('hai mẫu số không chia hết'), findsNothing);

    // SWITCH → B. Không logout, không mất màn.
    await tester.tap(find.byIcon(Icons.switch_account_outlined));
    await tester.pumpAndSettle();
    expect(find.text('Ai đang học?'), findsOneWidget);
    await tester.tap(find.textContaining('Lan · Lớp 5'));
    await tester.pumpAndSettle();

    // B: KHÔNG thừa kế bằng chứng của A — dạng mới vẫn là «chưa thử».
    expect(find.text('Chào Lan!'), findsOneWidget);
    expect(find.text('Chào Minh!'), findsNothing);
    await tester.scrollUntilVisible(
        find.textContaining('hai mẫu số không chia hết'), 120,
        scrollable: find.byType(Scrollable).first);
    expect(find.textContaining('hai mẫu số không chia hết'), findsWidgets,
        reason: 'NO CROSS-LEARNER EVIDENCE CONTAMINATION: B chưa học gì');

    // SWITCH lại → A: state A y nguyên (mission lại tính từ kho của A).
    await tester.tap(find.byIcon(Icons.switch_account_outlined));
    await tester.pumpAndSettle();
    await tester.tap(find.textContaining('Minh · Lớp 5'));
    await tester.pumpAndSettle();
    expect(find.text('Chào Minh!'), findsOneWidget);
    expect(find.textContaining('hai mẫu số không chia hết'), findsNothing,
        reason: 'bằng chứng của A còn nguyên sau vòng A→B→A');
  });

  testWidgets('switcher liệt kê đủ hồ sơ + lối «Thêm người học»',
      (tester) async {
    final store = await seed();
    await tester.pumpWidget(HocCungSamApp(store: store));
    await tester.pumpAndSettle();
    await tester.tap(find.byIcon(Icons.switch_account_outlined));
    await tester.pumpAndSettle();
    expect(find.textContaining('Minh · Lớp 5'), findsOneWidget);
    expect(find.textContaining('Lan · Lớp 5'), findsOneWidget);
    expect(find.text('Thêm người học'), findsOneWidget);
  });
}
