/// WAL-137 #04 — TKB: tuỳ chọn, và KHÔNG BAO GIỜ suy ra bài học cụ thể.
library;

import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/features/timetable/timetable_screen.dart';

const _p = LearnerProfile(learnerId: 'na', displayName: 'Na', grade: 5);
const _subjects = ['Toán', 'Tiếng Việt', 'Khoa học'];

Future<void> _pump(WidgetTester t, LearnerStore store) async {
  await t.pumpWidget(MaterialApp(
      home: TimetableScreen(
          profile: _p, store: store, subjects: _subjects)));
  await t.pumpAndSettle();
}

void main() {
  testWidgets('⭐ TKB RỖNG là trạng thái HỢP LỆ, không phải việc còn dở',
      (t) async {
    await _pump(t, JsonlLearnerStore());
    expect(find.textContaining('để trống cũng không sao'), findsOneWidget,
        reason: '⭐ đột biến bắt buộc nhập TKB ⇒ đỏ (F13: tuỳ chọn)');
  });

  testWidgets('thêm môn ⇒ ghi kho; xoá ⇒ mất khỏi kho', (t) async {
    final store = JsonlLearnerStore();
    await _pump(t, store);
    await t.tap(find.widgetWithText(ActionChip, 'Toán'));
    await t.pumpAndSettle();
    var saved = await store.timetable('na');
    expect(saved, hasLength(1));
    expect(saved.single.subjectId, 'Toán');
    expect(saved.single.weekday, DateTime.monday);
    expect(saved.single.period, 1);

    await t.tap(find.byIcon(Icons.close));
    await t.pumpAndSettle();
    saved = await store.timetable('na');
    expect(saved, isEmpty);
  });

  testWidgets('mỗi ngày một danh sách riêng — thêm ở Thứ Hai không lộ sang Thứ Ba',
      (t) async {
    final store = JsonlLearnerStore();
    await _pump(t, store);
    await t.tap(find.widgetWithText(ActionChip, 'Toán'));
    await t.pumpAndSettle();
    expect(find.textContaining('Tiết 1 · Toán'), findsOneWidget);
    await t.tap(find.widgetWithText(FilledButton, 'Thứ Ba'));
    await t.pumpAndSettle();
    expect(find.textContaining('Tiết 1 · Toán'), findsNothing);
    expect(find.textContaining('để trống cũng không sao'), findsOneWidget);
  });

  testWidgets('⭐ màn NÓI RÕ giới hạn: không đoán cô dạy bài nào', (t) async {
    await _pump(t, JsonlLearnerStore());
    expect(find.textContaining('KHÔNG đoán cô sẽ dạy bài nào'), findsOneWidget);
  });

  test('⭐⭐ CẤU TRÚC (F4): màn TKB không có đường nào chạm tới BÀI học', () {
    final src =
        File('lib/features/timetable/timetable_screen.dart').readAsStringSync();
    for (final banned in [
      'LessonRef',
      'exercisesForToan',
      'CanonicalProblem',
      'lessonNo',
      'openCanonicalProblem',
    ]) {
      expect(src.contains(banned), isFalse,
          reason: '⭐⭐ F4: «môn trong TKB» KHÔNG được suy ra bài cụ thể — '
              'màn này chạm vào «$banned»');
    }
  });
}
