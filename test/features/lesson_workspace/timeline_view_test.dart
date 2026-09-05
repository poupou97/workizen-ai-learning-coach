/// LANE C (round 4) — TimelineView: mốc theo thứ tự sách, nguồn kể chuyện,
/// thử xếp thứ tự với TimelineValidator (tham gia, không ghi gì).
library;

import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/lesson_model/semantic_data.dart';
import 'package:learning_coach/core/lesson_model/workspace_catalog.dart';
import 'package:learning_coach/features/lesson_workspace/views/timeline_view.dart';
import 'package:learning_coach/features/lesson_workspace/visual_view.dart';

import 'support.dart';

LessonDocument _history() {
  final j = jsonDecode(
    File('assets/fixtures/synthetic/lesson-05-sgk-lich-su-va-dia-li-5-b8.synthetic.json').readAsStringSync(),
  ) as Map;
  return LessonDocument.fromJson(j.cast<String, Object?>(), assetBase: FixtureSlot.syntheticDir)!;
}

void main() {
  testWidgets('VisualView mở tab Dòng thời gian; mốc theo thứ tự sách; nguồn kể chuyện; chạm mốc mở nguồn', (t) async {
    final d = _history();
    await t.pumpWidget(fixtureHost(Scaffold(body: VisualView(doc: d, onShowInRead: (_) {}))));
    await t.pumpAndSettle();
    expect(find.byKey(VisualView.shapeKey('Dòng thời gian')), findsOneWidget);
    expect(find.byKey(TimelineView.rootKey), findsOneWidget);
    expect(find.textContaining('5 mốc'), findsOneWidget);
    final y0 = t.getTopLeft(find.text('101 - 103')).dy;
    final y1 = t.getTopLeft(find.text('205')).dy;
    expect(y1, greaterThan(y0));
    // ⭐ ROUND 4 (Lane B, lỗi thấy trên máy thật): thẻ mốc KHÔNG lặp ba lần
    // một điều. Câu trích chỉ là «Tên (năm)» ⇒ không vẽ dòng thứ ba; năm và
    // tên vẫn hiện đủ.
    expect(find.text('101 - 103'), findsOneWidget);
    expect(find.text('Bà Mẫu B (205)'), findsNothing,
        reason: 'câu trích trùng «tên + năm» đã hiện ⇒ không lặp lại');
    expect(find.text('Chiến thắng mẫu của Ông Mẫu G (450)'), findsOneWidget,
        reason: 'câu trích NÓI THÊM điều gì thì vẫn hiện đủ — không cắt dữ liệu');
    expect(find.text('NGUỒN KỂ CHUYỆN — sách ghi'), findsOneWidget);
    expect(find.text('Kể theo: NXB Mẫu, 2000'), findsOneWidget);
    // tên mốc xuất hiện hai lần (mốc trên trục + chip xếp thứ tự) — chạm mốc
    await t.tap(find.text('Bà Mẫu B').first);
    await t.pumpAndSettle();
    expect(find.text('Sách viết'), findsOneWidget);
  });

  testWidgets('thử xếp thứ tự: đúng ⇒ «khớp với năm sách nêu»; sai ⇒ «Theo sách, … diễn ra trước»; không khen/chê', (t) async {
    final d = _history();
    final tl = d.semantic.whereType<TimelineSemantic>().single;
    await t.pumpWidget(
      fixtureHost(
        Scaffold(
          body: SingleChildScrollView(child: TimelineView(doc: d, semantic: tl, onOpenSource: (_) {})),
        ),
      ),
    );
    await t.pumpAndSettle();
    // nút kiểm mờ khi chưa chọn đủ 2 mốc
    expect(t.widget<FilledButton>(find.byKey(TimelineView.orderCheckKey)).onPressed, isNull);
    await t.ensureVisible(find.byKey(TimelineView.pickKey(3)));
    await t.tap(find.byKey(TimelineView.pickKey(3))); // Ông Mẫu E (398)
    await t.tap(find.byKey(TimelineView.pickKey(1))); // Bà Mẫu B (205)
    await t.pumpAndSettle();
    expect(find.textContaining('1 · Ông Mẫu E'), findsOneWidget);
    await t.tap(find.byKey(TimelineView.orderCheckKey));
    await t.pumpAndSettle();
    expect(find.textContaining('Theo sách, Bà Mẫu B (205) diễn ra trước Ông Mẫu E (398)'), findsOneWidget);
    expect(find.textContaining('sai'), findsNothing);
    expect(find.textContaining('giỏi'), findsNothing);
    await t.tap(find.byKey(TimelineView.orderResetKey));
    await t.pumpAndSettle();
    await t.tap(find.byKey(TimelineView.pickKey(0)));
    await t.tap(find.byKey(TimelineView.pickKey(4)));
    await t.pumpAndSettle();
    await t.tap(find.byKey(TimelineView.orderCheckKey));
    await t.pumpAndSettle();
    expect(find.textContaining('Thứ tự khớp với năm sách nêu'), findsOneWidget);
    expect(find.textContaining('không phải bài kiểm tra'), findsOneWidget);
  });

  testWidgets('mốc không đọc được năm ⇒ không có phần kiểm, nói lí do (fail closed)', (t) async {
    final d = loadSyntheticDoc();
    final src = d.blocks.whereType<ParagraphBlock>().first.id;
    final tl = TimelineSemantic(
      id: 'tl', title: 'Mốc (mẫu)', trust: d.trust, derivation: 'synthetic-test',
      events: [
        TimelineEvent(when: 'Bước đầu', title: 'Khuấy (mẫu)', sourceBlockId: src),
        TimelineEvent(when: 'Sau đó', title: 'Lọc (mẫu)', sourceBlockId: src),
      ],
    );
    await t.pumpWidget(
      fixtureHost(Scaffold(body: SingleChildScrollView(child: TimelineView(doc: d, semantic: tl, onOpenSource: (_) {})))),
    );
    await t.pumpAndSettle();
    expect(find.byKey(TimelineView.orderCheckKey), findsNothing);
    expect(find.textContaining('chưa đọc được năm'), findsWidgets);
  });
}
