/// TRACK B — Học với SAM: vòng lặp nhìn thấy, nhãn kịch bản, không chê,
/// thẻ kết chỉ ghi nhận THAM GIA.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/tutor_script.dart';
import 'package:learning_coach/features/lesson_workspace/tutor_view.dart';

import 'support.dart';

void main() {
  testWidgets('⭐ nhãn «SAM (kịch bản thử nghiệm)» + giải thích → Tiếp → hỏi', (
    t,
  ) async {
    await t.pumpWidget(
      fixtureHost(
        Scaffold(
          body: TutorView(doc: loadSyntheticDoc(), onNext: (_, _) {}),
        ),
      ),
    );
    await t.pumpAndSettle();
    expect(find.text('SAM (kịch bản thử nghiệm)'), findsWidgets);
    expect(find.textContaining('không ghi bằng chứng học'), findsOneWidget);
    expect(find.textContaining('[MẪU] Bài này nói về'), findsOneWidget);
    expect(find.text('SÁCH VIẾT'), findsOneWidget, reason: 'trích block nguồn');
    await t.tap(find.text('Tiếp ▸'));
    await t.pumpAndSettle();
    expect(find.textContaining('Làm muối từ nước biển'), findsOneWidget);
    expect(find.text('Cô cạn'), findsOneWidget);
  });

  testWidgets('⭐⭐ chọn sai ⇒ gợi ý (không chê); sai tiếp ⇒ gợi ý 2; sai nữa ⇒ '
      'scaffold và đi tiếp — không «Chính xác», không kẹt', (t) async {
    await t.pumpWidget(
      fixtureHost(
        Scaffold(
          body: TutorView(doc: loadSyntheticDoc(), onNext: (_, _) {}),
        ),
      ),
    );
    await t.pumpAndSettle();
    await t.tap(find.text('Tiếp ▸'));
    await t.pumpAndSettle();
    final loc = find.widgetWithText(FilledButton, 'Lọc');
    await t.tap(loc);
    await t.pumpAndSettle();
    expect(find.textContaining('Gợi ý 1'), findsOneWidget);
    await t.tap(loc);
    await t.pumpAndSettle();
    expect(find.textContaining('Gợi ý 2'), findsOneWidget);
    await t.tap(loc);
    await t.pumpAndSettle();
    expect(find.textContaining('Chưa khớp, không sao'), findsOneWidget);
    expect(find.textContaining('Khớp với bảng mẫu'), findsNothing);
    expect(find.textContaining('Chính xác'), findsNothing);
    // đã sang câu hỏi mở tiếp theo
    expect(find.byKey(const Key('tutor-answer-field')), findsOneWidget);
    for (final s in ['sai', 'kém', 'tệ']) {
      expect(find.textContaining(s), findsNothing, reason: 'không chê');
    }
  });

  testWidgets('chọn đúng ⇒ phản hồi khớp; gõ trả lời khớp mẫu ⇒ thẻ kết THAM '
      'GIA + bước tiếp', (t) async {
    NextTarget? target;
    await t.pumpWidget(
      fixtureHost(
        Scaffold(
          body: TutorView(
            doc: loadSyntheticDoc(),
            onNext: (tg, _) => target = tg,
          ),
        ),
      ),
    );
    await t.pumpAndSettle();
    await t.tap(find.text('Tiếp ▸'));
    await t.pumpAndSettle();
    await t.tap(find.text('Cô cạn'));
    await t.pumpAndSettle();
    expect(find.textContaining('Khớp với bảng mẫu'), findsOneWidget);
    await t.enterText(
      find.byKey(const Key('tutor-answer-field')),
      'vì cát nặng hơn nước',
    );
    await t.tap(find.byKey(const Key('tutor-send')));
    await t.pumpAndSettle();
    expect(find.textContaining('nặng hơn» — khớp ý mẫu'), findsOneWidget);
    expect(find.byKey(TutorView.endCardKey), findsOneWidget);
    expect(find.text('Con đã học cùng SAM phần này'), findsOneWidget);
    expect(find.textContaining('chưa phải bằng chứng'), findsOneWidget);
    await t.tap(find.textContaining('Đọc lại phần'));
    expect(target, NextTarget.read);
  });

  testWidgets('nút gợi ý dùng được trước khi trả lời, ẩn khi hết', (t) async {
    await t.pumpWidget(
      fixtureHost(
        Scaffold(
          body: TutorView(doc: loadSyntheticDoc(), onNext: (_, _) {}),
        ),
      ),
    );
    await t.pumpAndSettle();
    await t.tap(find.text('Tiếp ▸'));
    await t.pumpAndSettle();
    await t.tap(find.textContaining('Gợi ý cho tớ'));
    await t.pumpAndSettle();
    await t.tap(find.textContaining('Gợi ý cho tớ'));
    await t.pumpAndSettle();
    expect(find.textContaining('SAM đã gợi ý hết rồi'), findsOneWidget);
  });

  testWidgets('neo vào đoạn có bước ⇒ bắt đầu ở câu hỏi của đoạn đó', (
    t,
  ) async {
    final d = loadSyntheticDoc();
    final q = d.tutorScript!.asks.first.promptBlockId!;
    await t.pumpWidget(
      fixtureHost(
        Scaffold(
          body: TutorView(doc: d, anchorBlockId: q, onNext: (_, _) {}),
        ),
      ),
    );
    await t.pumpAndSettle();
    expect(find.textContaining('Con hỏi về đoạn:'), findsOneWidget);
    expect(find.text('Cô cạn'), findsOneWidget, reason: 'vào thẳng câu hỏi');
  });
}
