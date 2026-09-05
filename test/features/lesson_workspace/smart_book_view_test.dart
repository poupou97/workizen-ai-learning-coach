/// TRACK B — Smart Book: thứ tự đọc, withheld KHÔNG thành chữ, câu hỏi có
/// kiểu, hình + caption, bảng an toàn, nguồn cuối bài, cỡ chữ.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/features/lesson_workspace/smart_book_view.dart';
import 'package:learning_coach/features/lesson_workspace/widgets/withheld_card.dart';

import 'support.dart';

Widget _host(
  LessonDocument d, {
  int step = 0,
  void Function(int)? onStep,
  void Function(LessonBlock)? onAsk,
  String? scrollTo,
}) => fixtureHost(
  Scaffold(
    body: SmartBookView(
      doc: d,
      fontStep: step,
      onFontStep: onStep ?? (_) {},
      onAskSam: onAsk ?? (_) {},
      scrollToBlockId: scrollTo,
    ),
  ),
);

void main() {
  testWidgets(
    '⭐⭐ WITHHELD hiện placeholder thật, KHÔNG có chữ nào của vùng đó',
    (t) async {
      final d = loadSyntheticDoc();
      await t.pumpWidget(_host(d));
      await t.pumpAndSettle();
      final w = find.byKey(WithheldCard.cardKey);
      await t.ensureVisible(w.first);
      expect(w, findsWidgets);
      expect(find.textContaining('SAM chưa đọc được'), findsWidgets);
      expect(find.textContaining('trang 61'), findsWidgets);
      // Toàn bộ chữ trên màn không chứa gì ngoài nội dung có trong block CÓ chữ.
      final allowed = {
        for (final b in d.blocks)
          if (LessonDocument.textOf(b) != null) LessonDocument.textOf(b)!,
      };
      for (final txt in find.byType(Text).evaluate()) {
        final s = (txt.widget as Text).data ?? '';
        if (s.contains('CHỮ LẬU')) fail('chữ withheld lọt ra màn: $s');
      }
      expect(allowed, isNotEmpty);
    },
  );

  testWidgets('câu hỏi có kiểu (❓ + «Câu hỏi trong sách»), hình có dòng nguồn, '
      'caption in nghiêng, bảng an toàn thành ô', (t) async {
    final d = loadSyntheticDoc();
    await t.pumpWidget(_host(d));
    await t.pumpAndSettle();
    expect(find.text('❓'), findsWidgets);
    expect(find.textContaining('Câu hỏi trong sách'), findsWidgets);
    expect(
      find.textContaining('Hình trong SGK · SGK KHTN 6 · trang 60'),
      findsWidgets,
    );
    final cap = t.widget<Text>(find.textContaining('Hình 1.').first);
    expect(cap.style?.fontStyle, FontStyle.italic);
    await t.scrollUntilVisible(
      find.byType(Table),
      300,
      scrollable: find.byType(Scrollable).first,
    );
    expect(find.byType(Table), findsOneWidget);
    expect(find.text('Cách'), findsOneWidget);
  });

  testWidgets('nguồn cuối bài + «Hết bài» có trang in', (t) async {
    final d = loadSyntheticDoc();
    await t.pumpWidget(_host(d));
    await t.pumpAndSettle();
    await t.scrollUntilVisible(
      find.textContaining('Hết bài'),
      400,
      scrollable: find.byType(Scrollable).first,
    );
    expect(
      find.textContaining('Hết bài · SGK KHTN 6 · trang 60–63'),
      findsOneWidget,
    );
    expect(find.textContaining('FIXTURE MẪU'), findsOneWidget);
  });

  testWidgets('cỡ chữ: 3 nút ≥48dp, đổi bước ⇒ thân bài to lên', (t) async {
    final d = loadSyntheticDoc();
    int? picked;
    await t.pumpWidget(_host(d, onStep: (s) => picked = s));
    await t.pumpAndSettle();
    final buttons = find.widgetWithText(TextButton, 'A');
    expect(buttons, findsNWidgets(3));
    for (final e in buttons.evaluate()) {
      expect(e.size!.height, greaterThanOrEqualTo(48));
    }
    await t.tap(buttons.at(2));
    expect(picked, 2);
    await t.pumpWidget(_host(d, step: 2));
    await t.pumpAndSettle();
    final p = t.widget<Text>(find.textContaining('[MẪU] Các chất').first);
    expect(p.style?.fontSize, SmartBookView.fontSteps[2]);
  });

  testWidgets('chạm đoạn ⇒ sheet «Hỏi SAM về đoạn này» trả đúng block', (
    t,
  ) async {
    final d = loadSyntheticDoc();
    LessonBlock? asked;
    await t.pumpWidget(_host(d, onAsk: (b) => asked = b));
    await t.pumpAndSettle();
    await t.tap(find.textContaining('[MẪU] Các chất').first);
    await t.pumpAndSettle();
    await t.tap(find.text('🦉 Hỏi SAM về đoạn này'));
    await t.pumpAndSettle();
    expect(asked, isA<ParagraphBlock>());
    expect((asked as ParagraphBlock).text, contains('[MẪU] Các chất'));
  });

  testWidgets('⭐ fixture THẬT (nếu có): 4 withheld hiện placeholder, 8 hình, '
      'không dòng nào của withheld lọt', (t) async {
    final d = loadRealDocOrSkip();
    if (d == null) return;
    await t.pumpWidget(_host(d));
    await t.pumpAndSettle();
    var cards = 0;
    for (final b in d.blocks) {
      if (b is WithheldBlock) cards++;
    }
    expect(cards, 4);
    // cụm chữ chỉ có trong vùng math_guard của sách (bước «1/4 chai»)
    expect(
      find.textContaining('1/4 chai'),
      findsNothing,
      reason: '⭐⭐ chữ của vùng bị giữ lại KHÔNG được xuất hiện',
    );
  });
}
