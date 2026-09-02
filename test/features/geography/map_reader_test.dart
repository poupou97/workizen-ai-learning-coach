/// WAL-144 #28 — MapReader: bản đồ SGK thật + câu hỏi verbatim, không chấm.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/features/geography/map_reader_screen.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';

const _map = DiaMap(
  subject: 'LS&ĐL',
  book: '05-sgk-lich-su-va-dia-li-5',
  page: 10,
  asset: 'map-ls-dia-5-p012-tu-nhien-vn.png',
  caption: 'Hình 1. Bản đồ tự nhiên Việt Nam',
  questions: [
    'Kể tên và xác định trên bản đồ một số khoáng sản ở nước ta.',
    'Nêu vai trò của tài nguyên khoáng sản đối với sự phát triển kinh tế.',
  ],
);

void main() {
  testWidgets('bản đồ + caption + câu hỏi VERBATIM hiện; nguồn có trang', (t) async {
    await t.pumpWidget(const MaterialApp(home: MapReaderScreen(map: _map)));
    await t.pump();
    expect(find.text('BẢN ĐỒ TRONG SÁCH'), findsOneWidget);
    expect(find.text('Hình 1. Bản đồ tự nhiên Việt Nam'), findsOneWidget);
    // dòng nguồn nằm dưới fold — ListView lười: cuộn tới rồi mới assert.
    await t.scrollUntilVisible(find.textContaining('tr. 10'), 150,
        scrollable: find.byType(Scrollable).first);
    expect(find.textContaining('Kể tên và xác định trên bản đồ'), findsOneWidget);
    expect(find.textContaining('tr. 10'), findsOneWidget);
    expect(find.byType(InteractiveViewer), findsOneWidget,
        reason: 'bản đồ phải phóng to được — để soi, không để ngắm');
  });

  testWidgets('⭐ hoàn tất ⇒ MỘT event correct=null policy map-reader-v1', (t) async {
    List<LearningEvent> out = const [];
    await t.pumpWidget(MaterialApp(
        home: MapReaderScreen(
            map: _map,
            now: () => DateTime(2026, 9, 2, 22),
            onFinished: (e) => out = e)));
    await t.pump();
    await t.scrollUntilVisible(find.text('Con đã chỉ được trên bản đồ ✅'), 150,
        scrollable: find.byType(Scrollable).first);
    await t.tap(find.text('Con đã chỉ được trên bản đồ ✅'));
    await t.pumpAndSettle();
    expect(out.single.correct, isNull,
        reason: '⭐ đột biến chấm việc chỉ-bản-đồ ⇒ test đỏ');
    expect(out.single.policyId, 'map-reader-v1');
    expect(out.single.knowledgeVersion, isNotNull);
    expect(find.textContaining('không chấm'), findsOneWidget);
  });
}
