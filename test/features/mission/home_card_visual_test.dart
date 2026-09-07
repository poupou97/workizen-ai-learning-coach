/// ⭐ Lệnh 56 §P2.1/§P2.2/§P2.4 — thẻ bài học: có hình, chữ vẫn đọc được,
/// và luật giống nhau cho mọi bài.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/features/mission/mission_center_screen.dart';
import 'package:learning_coach/features/mission/mission_data.dart';

import '../lesson_workspace/support.dart';

Future<void> _pump(
  WidgetTester t, {
  required LessonDocument doc,
  String? Function(String subject)? cover,
}) async {
  t.view.physicalSize = const Size(1080, 2400);
  t.view.devicePixelRatio = 3.0;
  addTearDown(t.view.resetPhysicalSize);
  addTearDown(t.view.resetDevicePixelRatio);
  await t.pumpWidget(
    MaterialApp(
      home: MissionCenterScreen(
        data: buildDemoMission(now: DateTime(2026, 9, 7, 19)),
        learnerGrade: doc.grade,
        lessonThreads: [HomeLessonThread(doc: doc)],
        coverOfSubject: cover,
      ),
    ),
  );
  await t.pump();
}

void main() {
  final doc = loadSyntheticDoc();

  testWidgets('⭐ có bìa môn ⇒ thẻ vẽ ẢNH THẬT làm nền', (t) async {
    await _pump(
      t,
      doc: doc,
      cover: (_) => 'covers/06-sgk-khoa-hoc-tu-nhien-6.webp',
    );
    final card = find.byKey(MissionCenterScreen.smartCardKey(doc.slotKey));
    expect(card, findsOneWidget);
    final img = t.widget<Image>(
      find.descendant(of: card, matching: find.byType(Image)).first,
    );
    expect(
      (img.image as AssetImage).assetName,
      'assets/pack/covers/06-sgk-khoa-hoc-tu-nhien-6.webp',
    );
  });

  testWidgets('⭐ KHÔNG có bìa ⇒ vẫn có nền (dải màu), KHÔNG trắng trơn', (
    t,
  ) async {
    await _pump(t, doc: doc);
    final card = find.byKey(MissionCenterScreen.smartCardKey(doc.slotKey));
    expect(card, findsOneWidget);
    // Không ảnh, nhưng phải có ít nhất một nền tô gradient trong thẻ.
    final decorated = t
        .widgetList<DecoratedBox>(
          find.descendant(of: card, matching: find.byType(DecoratedBox)),
        )
        .where((d) => (d.decoration as BoxDecoration).gradient != null);
    expect(decorated, isNotEmpty, reason: 'thẻ không có nền nào');
  });

  testWidgets('⭐⭐ §P2.2 — CHỮ không tràn sang nửa ảnh', (t) async {
    await _pump(
      t,
      doc: doc,
      cover: (_) => 'covers/06-sgk-khoa-hoc-tu-nhien-6.webp',
    );
    final card = find.byKey(MissionCenterScreen.smartCardKey(doc.slotKey));
    final cardW = t.getSize(card).width;
    final title = find.descendant(
      of: card,
      matching: find.textContaining('Bài ${doc.lessonNo}'),
    );
    expect(title, findsOneWidget);
    final right = t.getBottomRight(title).dx - t.getTopLeft(card).dx;
    expect(
      right,
      lessThan(cardW * 0.66),
      reason: 'tiêu đề bài lấn sang vùng ảnh — đọc được phụ thuộc vào ảnh',
    );
  });
}
