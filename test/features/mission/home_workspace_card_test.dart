/// ROUND 3 B1 — Home nhìn thấy sản phẩm: thẻ «Bài học SAM» cho bài có Lesson
/// Workspace của ĐÚNG lớp; không có bài ⇒ không có thẻ; thẻ nói rõ thử nghiệm
/// và KHÔNG thay thẻ «Việc SAM đề xuất» (hợp đồng G2 của Track A).
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
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

void main() {
  testWidgets('⭐ có bài workspace ⇒ thẻ «BÀI HỌC SAM · BẢN THỬ NGHIỆM» với tên '
      'bài, chương, trang, ba cách học; «Mở bài học» trả đúng tài liệu', (
    t,
  ) async {
    final doc = loadSyntheticDoc();
    LessonDocument? opened;
    await t.pumpWidget(
      fixtureHost(
        MissionCenterScreen(
          data: await _data(),
          onOpenSubjects: () {},
          workspaceLesson: doc,
          onOpenWorkspaceLesson: (d) => opened = d,
        ),
      ),
    );
    await t.pumpAndSettle();
    expect(find.byKey(MissionCenterScreen.workspaceCardKey), findsOneWidget);
    expect(find.text('BÀI HỌC SAM · BẢN THỬ NGHIỆM'), findsOneWidget);
    expect(find.textContaining('Bài 17 · Tách chất'), findsOneWidget);
    expect(find.textContaining('Chương IV'), findsOneWidget);
    expect(find.textContaining('trang 60–63'), findsOneWidget);
    expect(find.textContaining('Học với SAM'), findsOneWidget);
    // thẻ G2 của Track A vẫn còn nguyên
    expect(find.text('Bắt đầu'), findsOneWidget);
    await t.ensureVisible(find.text('Mở bài học'));
    await t.pumpAndSettle();
    await t.tap(find.text('Mở bài học'));
    expect(opened?.slotKey, doc.slotKey);
  });

  testWidgets('không có bài workspace ⇒ không có thẻ (không bịa)', (t) async {
    await t.pumpWidget(
      fixtureHost(
        MissionCenterScreen(data: await _data(), onOpenSubjects: () {}),
      ),
    );
    await t.pumpAndSettle();
    expect(find.byKey(MissionCenterScreen.workspaceCardKey), findsNothing);
    expect(find.textContaining('BÀI HỌC SAM'), findsNothing);
  });

  testWidgets('thẻ không có %, sao, «đã học»', (t) async {
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
    final card = find.descendant(
      of: find.byKey(MissionCenterScreen.workspaceCardKey),
      matching: find.byType(Text),
    );
    for (final e in card.evaluate()) {
      final s = ((e.widget as Text).data ?? '').toLowerCase();
      expect(s, isNot(contains('%')));
      expect(s, isNot(contains('★')));
      expect(s, isNot(contains('đã học')));
    }
  });
}
