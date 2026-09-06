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
// ⭐ ROUND 7 · WS-S — QUYẾT ĐỊNH CỦA FOUNDER: tiêu đề hiển thị NGUYÊN VĂN NGUỒN.
// Các kỳ vọng dưới đây từng ghim chuỗi ĐÃ ĐƯỢC HẠ CHỮ; nay chúng ghim đúng chuỗi
// mà fixture của chính test này mang. Sửa TIỀN ĐỀ, không nới assertion: mỗi kỳ
// vọng vẫn đòi một chuỗi CỤ THỂ, chỉ là chuỗi thật thay vì chuỗi biến đổi.

  testWidgets('⭐ có bài workspace ⇒ thẻ «BÀI HỌC SAM · BẢN THỬ NGHIỆM» với tên '
      'bài, chương, trang, ba cách học; «Mở bài học» trả đúng tài liệu', (
    t,
  ) async {
    final doc = loadSyntheticDoc();
    LessonDocument? opened;
    // ROUND 4: hai thẻ xếp dọc — màn cao để ListView dựng cả hai.
    t.view.physicalSize = const Size(1080, 5000);
    t.view.devicePixelRatio = 2.75;
    addTearDown(t.view.reset);
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
    // ROUND 7 V1: thẻ nay mở đầu bằng «ĐANG HỌC» — nhãn bản thử nghiệm KHÔNG
    // được mất khi màn được sắp lại.
    expect(find.text('ĐANG HỌC · BÀI HỌC SAM · BẢN THỬ NGHIỆM'), findsOneWidget);
    final inCard = find.descendant(
      of: find.byKey(MissionCenterScreen.workspaceCardKey),
      matching: find.textContaining('Bài 17 · TÁCH CHẤT'),
    );
    expect(inCard, findsOneWidget);
    expect(find.textContaining('Chương IV'), findsOneWidget);
    expect(find.textContaining('trang 60–63'), findsOneWidget);
    // ROUND 7 V1: ba cách học không còn là MỘT DÒNG CHỮ trong thẻ — mỗi cách
    // còn lại là một nút bấm được ở hàng «CÓ THỂ LÀM TIẾP».
    expect(find.byKey(MissionCenterScreen.continueRowKey), findsOneWidget);
    expect(find.textContaining('Học với SAM'), findsWidgets);
    // thẻ G2 của Track A vẫn còn — ROUND 4: đứng sau như «CÒN CÓ THỂ MỞ»
    expect(find.byKey(MissionCenterScreen.secondaryCardKey), findsOneWidget);
    expect(find.text('Vào Môn học ▸'), findsOneWidget);
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
