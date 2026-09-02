/// WAL-113 QA — bug thấy trên MÁY TRẮNG (Nokia walk): onboarding xong,
/// mở «Môn học» thì «SAM chưa nạp mục lục» dù asset có — vì _loadLessonIndex
/// chạy lúc CHƯA có hồ sơ rồi không chạy lại. Test giữ fix: sau onboarding,
/// index phải được nạp mà KHÔNG cần restart app.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';
import 'package:learning_coach/main.dart';

const _sampleIndex = '''
{"grade":5,"subjects":{"Tiếng Việt":[{"sourceDocumentId":"05-sgk-tieng-viet-5-tap-mot",
 "volume":null,"lessons":[{"no":1,"title":"THANH ÂM CỦA GIÓ","pageStart":8}]}]},
 "toanExercises":{}}
''';

void main() {
  testWidgets('⭐ máy trắng: onboarding → Môn học có mục lục NGAY (không restart)',
      (t) async {
    expect(LessonIndex.fromJsonString(_sampleIndex), isNotNull,
        reason: 'sample của test phải parse được — nếu đỏ ở đây là lỗi test');
    await t.pumpWidget(HocCungSamApp(
        store: JsonlLearnerStore(),
        indexLoader: (g) async =>
            g == 5 ? LessonIndex.fromJsonString(_sampleIndex) : null));
    await t.pumpAndSettle();
    // Onboarding (máy trắng — không bịa học sinh)
    expect(find.text('Tớ gọi con là gì?'), findsOneWidget);
    await t.enterText(find.byType(TextField), 'Na');
    // ListView lười — chip lớp + nút nằm dưới fold: cuộn tới rồi mới bấm.
    final five = find.widgetWithText(FilledButton, '5');
    await t.scrollUntilVisible(five, 200,
        scrollable: find.byType(Scrollable).first);
    await t.tap(five);
    await t.pumpAndSettle();
    final btn = find.text('Bắt đầu học ▸');
    await t.scrollUntilVisible(btn, 200,
        scrollable: find.byType(Scrollable).first);
    await t.tap(btn);
    await t.pumpAndSettle();
    expect(find.text('Chào Na!'), findsOneWidget);
    await t.pump(const Duration(milliseconds: 200)); // cho indexLoader settle
    // Mở Môn học ngay — KHÔNG restart. Đột biến bỏ _loadLessonIndex trong
    // _onboarded ⇒ test này đỏ («SAM chưa nạp mục lục môn học trên máy này»).
    await t.tap(find.text('📘 Học trước'));
    await t.pumpAndSettle();
    expect(find.text('Môn học · Lớp 5'), findsOneWidget);
    expect(find.textContaining('chưa nạp mục lục'), findsNothing,
        reason: '⭐ index phải nạp lại sau onboarding');
    expect(find.text('Tiếng Việt'), findsOneWidget);
  });
}
