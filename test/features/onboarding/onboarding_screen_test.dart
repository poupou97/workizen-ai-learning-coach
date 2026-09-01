/// WAL-95 — luật onboarding: hai câu hỏi, không hỏi thời khoá biểu (F13),
/// chọn lớp KHÔNG sinh bằng chứng (grade ≠ mastery).
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/features/onboarding/onboarding_screen.dart';

/// Nút nằm cuối ListView — trong khung test phải cuộn tới mới chạm được
/// (bài học từ Mission Center: lazy list không dựng widget dưới màn).
Future<void> _tapStart(WidgetTester tester) async {
  final btn = find.text('Bắt đầu học ▸');
  await tester.scrollUntilVisible(btn, 200,
      scrollable: find.byType(Scrollable).first);
  await tester.tap(btn);
  await tester.pumpAndSettle();
}

void main() {
  testWidgets('đúng HAI câu hỏi; KHÔNG hỏi thời khoá biểu (F13)',
      (tester) async {
    await tester.pumpWidget(MaterialApp(
        home: OnboardingScreen(onDone: (_) {})));
    expect(find.text('Tớ gọi con là gì?'), findsOneWidget);
    expect(find.text('Con đang học lớp mấy?'), findsOneWidget);
    for (final w in tester.widgetList<Text>(find.byType(Text))) {
      final t = (w.data ?? '').toLowerCase();
      expect(t.contains('thời khoá biểu') || t.contains('thời khóa biểu'),
          isFalse,
          reason: 'onboarding không được hỏi thời khoá biểu — F13');
      expect(t.contains('năm sinh'), isFalse,
          reason: 'năm sinh là tuỳ chọn, không hỏi ở bước đầu');
    }
  });

  testWidgets('chưa đủ hai câu trả lời ⇒ không bắt đầu được', (tester) async {
    LearnerProfile? got;
    await tester.pumpWidget(MaterialApp(
        home: OnboardingScreen(onDone: (p) => got = p)));
    await _tapStart(tester);
    expect(got, isNull);

    await tester.enterText(find.byType(TextField), 'Minh');
    await tester.pumpAndSettle();
    await _tapStart(tester); // vẫn thiếu lớp
    expect(got, isNull);
  });

  testWidgets('⭐ hoàn tất: hồ sơ đúng lớp đã chọn, và 0 bằng chứng được sinh',
      (tester) async {
    LearnerProfile? got;
    await tester.pumpWidget(MaterialApp(
        home: OnboardingScreen(onDone: (p) => got = p)));
    await tester.enterText(find.byType(TextField), 'Minh');
    await tester.pumpAndSettle();
    final five = find.widgetWithText(FilledButton, '5');
    await tester.scrollUntilVisible(five, 200,
        scrollable: find.byType(Scrollable).first);
    await tester.tap(five);
    await tester.pumpAndSettle();
    await _tapStart(tester);

    expect(got, isNotNull);
    expect(got!.displayName, 'Minh');
    expect(got!.grade, 5);
    expect(got!.birthYear, isNull);

    // lưu vào kho rồi kiểm: chọn lớp 5 KHÔNG tạo mastery/bằng chứng nào
    final store = JsonlLearnerStore();
    await store.saveProfile(got!);
    for (final c in [
      'denominator-equal',
      'denominator-divisible',
      'denominator-non-divisible'
    ]) {
      final log =
          await store.evidenceFor(learnerId: got!.learnerId, skillCaseId: c);
      expect(log.events, isEmpty,
          reason: 'CURRENT GRADE ≠ MASTERY — lớp 5 không nghĩa là đã vững '
              'mọi thứ lớp 1-4');
    }
  });

  testWidgets('màn onboarding không có % và không có điểm số', (tester) async {
    await tester.pumpWidget(MaterialApp(
        home: OnboardingScreen(onDone: (_) {})));
    for (final w in tester.widgetList<Text>(find.byType(Text))) {
      final t = w.data ?? '';
      expect(t.contains('%'), isFalse);
      expect(t.contains('điểm'), isFalse);
    }
  });
}
