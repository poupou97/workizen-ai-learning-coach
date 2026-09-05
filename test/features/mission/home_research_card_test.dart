/// LANE C (round 4) — Home: lát cắt NGHIÊN CỨU của lớp khác hiện thành thẻ
/// riêng, ghi rõ «SÁCH LỚP 5», mở bằng cùng callback; không có ⇒ không thẻ;
/// thẻ Bài 17 của đúng lớp không đổi.
library;

import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/lesson_model/workspace_catalog.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/features/mission/mission_center_screen.dart';
import 'package:learning_coach/features/mission/mission_data.dart';

import '../lesson_workspace/support.dart';

const _g6 = LearnerProfile(learnerId: 'l6', displayName: 'Na', grade: 6);

Future<MissionData> _data() => buildMissionFromStore(
  profile: _g6,
  store: JsonlLearnerStore(),
  now: DateTime(2026, 9, 5, 19),
);

LessonDocument _history() {
  final j = jsonDecode(
    File('assets/fixtures/synthetic/lesson-05-sgk-lich-su-va-dia-li-5-b8.synthetic.json').readAsStringSync(),
  ) as Map;
  return LessonDocument.fromJson(j.cast<String, Object?>(), assetBase: FixtureSlot.syntheticDir)!;
}

void main() {
  testWidgets('thẻ Bài 17 (đúng lớp) + thẻ «LÁT CẮT NGHIÊN CỨU · SÁCH LỚP 5» (Bài 8); mở trả đúng tài liệu', (t) async {
    final b17 = loadSyntheticDoc();
    final b8 = _history();
    expect(WorkspaceCatalog.isResearchSlot(b8), isTrue);
    expect(WorkspaceCatalog.isResearchSlot(b17), isFalse);
    LessonDocument? opened;
    await t.pumpWidget(
      fixtureHost(
        MissionCenterScreen(
          data: await _data(),
          onOpenSubjects: () {},
          workspaceLesson: b17,
          researchLessons: [b8],
          onOpenWorkspaceLesson: (d) => opened = d,
        ),
      ),
    );
    await t.pumpAndSettle();
    expect(find.byKey(MissionCenterScreen.workspaceCardKey), findsOneWidget);
    // Home là ListView lười: thẻ thứ hai nằm dưới màn 600 px ⇒ cuộn tới khi thấy
    final card = find.byKey(MissionCenterScreen.researchCardKey(b8.slotKey));
    await t.scrollUntilVisible(card, 120, scrollable: find.byType(Scrollable).first);
    await t.pumpAndSettle();
    expect(card, findsOneWidget);
    expect(find.text('LÁT CẮT NGHIÊN CỨU · SÁCH LỚP 5 · BẢN THỬ NGHIỆM'), findsOneWidget);
    expect(find.textContaining('Bài 8 · Đấu tranh mẫu'), findsOneWidget);
    expect(find.textContaining('trang 36–39'), findsOneWidget);
    final open = find.descendant(of: card, matching: find.text('Mở bài học'));
    await t.ensureVisible(open);
    await t.tap(open);
    expect(opened?.slotKey, b8.slotKey);
  });

  testWidgets('không có lát cắt nghiên cứu ⇒ không có thẻ thứ hai', (t) async {
    await t.pumpWidget(
      fixtureHost(
        MissionCenterScreen(
          data: await _data(),
          onOpenSubjects: () {},
          workspaceLesson: loadSyntheticDoc(),
          onOpenWorkspaceLesson: (_) {},
        ),
      ),
    );
    await t.pumpAndSettle();
    expect(find.textContaining('LÁT CẮT NGHIÊN CỨU'), findsNothing);
  });
}
