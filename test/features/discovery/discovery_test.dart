/// WAL-152 — Discovery slice trên DB THẬT: Library/Person/Story + nhãn nguồn.
library;

import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/stories/stories_store.dart';
import 'package:learning_coach/features/discovery/discovery_library_screen.dart';
import 'package:learning_coach/features/discovery/story_detail_screen.dart';
import 'package:learning_coach/features/settings/settings_screen.dart';

const _db = 'assets/pack/sam-stories.db';

void main() {
  final has = File(_db).existsSync();

  testWidgets('Settings → entry Kho khám phá → Library render section thật',
      (t) async {
    if (!has) { markTestSkipped('pack chưa build'); return; }
    final s = StoriesStore.open(_db);
    await t.pumpWidget(MaterialApp(home: SettingsScreen(stories: s)));
    expect(find.text('Kho khám phá của SAM'), findsOneWidget);
    await t.tap(find.text('Kho khám phá của SAM'));
    await t.pumpAndSettle();
    // đầu trang trước (sẽ bị dispose khi cuộn — ListView lười)
    expect(find.textContaining('mỗi mục đều ghi rõ nguồn'), findsOneWidget);
    expect(find.textContaining('Danh nhân ('), findsOneWidget);
    await t.scrollUntilVisible(find.textContaining('Câu nói ('), 300,
        scrollable: find.byType(Scrollable).first);
    expect(find.textContaining('Câu nói ('), findsOneWidget);
  });

  testWidgets('Story detail: nhãn TRÍCH NGUYÊN VĂN + sourceLine (§34/§39)',
      (t) async {
    if (!has) { markTestSkipped('pack chưa build'); return; }
    final s = StoriesStore.open(_db);
    final quote = s.byType('QUOTE').first;
    await t.pumpWidget(
        MaterialApp(home: StoryDetailScreen(item: quote, stories: s)));
    expect(find.text('TRÍCH NGUYÊN VĂN TỪ NGUỒN'), findsOneWidget,
        reason: 'SOURCE FACT ≠ SAM EXPLANATION — nhãn bắt buộc');
    expect(find.textContaining('Nguồn: '), findsOneWidget);
    expect(find.textContaining('trang'), findsOneWidget);
  });

  testWidgets('Library search FTS: «Beethoven» ra kết quả, mở được detail',
      (t) async {
    if (!has) { markTestSkipped('pack chưa build'); return; }
    final s = StoriesStore.open(_db);
    await t.pumpWidget(
        MaterialApp(home: DiscoveryLibraryScreen(stories: s)));
    await t.enterText(find.byType(TextField), 'Beethoven');
    await t.testTextInput.receiveAction(TextInputAction.done);
    await t.pumpAndSettle();
    expect(find.textContaining('Kết quả'), findsOneWidget);
    expect(find.textContaining('Beethoven'), findsWidgets);
  });

  testWidgets('Library với store RỖNG ⇒ nói thật, không bịa nội dung',
      (t) async {
    final s = StoriesStore.open('/khong/ton/tai.db');
    await t.pumpWidget(
        MaterialApp(home: DiscoveryLibraryScreen(stories: s)));
    expect(find.textContaining('chưa được nạp'), findsOneWidget);
  });
}
