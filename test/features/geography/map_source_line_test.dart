/// ROUND 3 B5 — dòng nguồn bản đồ: lớp suy từ MÃ SÁCH của bản đồ, không phải
/// hằng «5»; thiếu trang in thì không in «tr. null».
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/features/geography/map_reader_screen.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';

import '../../support/pack_bundle.dart';

DiaMap _map({required String book, int? page}) => DiaMap(
  subject: 'LS&ĐL',
  book: book,
  page: page,
  asset: 'map-ls-dia-5-p012-tu-nhien-vn.png',
  caption: 'Hình 1. Bản đồ tự nhiên Việt Nam',
  pagePdf: 12,
  bboxFrac: const [0.075, 0.05, 0.935, 0.905],
  extractionVersion: 'map-crop-v1',
  questions: const ['Kể tên một số khoáng sản.'],
);

Future<void> _scrollToSource(WidgetTester t) => t.scrollUntilVisible(
  find.textContaining('Nguồn:'),
  150,
  scrollable: find.byType(Scrollable).first,
);

void main() {
  testWidgets('sách lớp 7 ⇒ «SGK LS&ĐL 7 · tr. 10» (không phải 5)', (t) async {
    await t.pumpWidget(
      packHost(
        MapReaderScreen(map: _map(book: '07-sgk-lich-su-va-dia-li-7', page: 10)),
      ),
    );
    await t.pump();
    await _scrollToSource(t);
    expect(find.text('Nguồn: SGK LS&ĐL 7 · tr. 10'), findsOneWidget);
    expect(find.textContaining('LS&ĐL 5'), findsNothing);
  });

  testWidgets('thiếu trang in ⇒ không in «tr. null»', (t) async {
    await t.pumpWidget(
      packHost(MapReaderScreen(map: _map(book: '05-sgk-lich-su-va-dia-li-5'))),
    );
    await t.pump();
    await _scrollToSource(t);
    expect(find.text('Nguồn: SGK LS&ĐL 5'), findsOneWidget);
    expect(find.textContaining('null'), findsNothing);
  });
}
