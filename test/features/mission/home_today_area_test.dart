/// ROUND 4 (Lane B §6 «Home») — MỘT vùng «Hôm nay»: dòng SAM nói học gì và vì
/// sao (lời trẻ), thẻ Bài học SAM là việc chính, thẻ Scale trung thực đứng sau
/// như «còn có thể mở» và KHÔNG còn nói «SAM chưa có bài dạy riêng cho lớp 6»
/// ngay dưới một bài học SAM. Không mic, không hứa chat.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/features/mission/mission_center_screen.dart';
import 'package:learning_coach/features/mission/mission_data.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';

import '../lesson_workspace/support.dart';

const _g6 = LearnerProfile(learnerId: 'l6', displayName: 'Na', grade: 6);
const _book = '06-sgk-khoa-hoc-tu-nhien-6';

/// KHTN 6 với 4 thí nghiệm mở được (như pack thật g6: bài 11, 46, 48, 50).
LessonIndex _khtn6() => LessonIndex.fromJsonString('''
{"grade":6,"subjects":{"KHTN":[{"sourceDocumentId":"$_book","volume":null,
   "lessons":[{"no":11,"title":"Oxygen","pageStart":40},
              {"no":17,"title":"Tách chất khỏi hỗn hợp","pageStart":60},
              {"no":46,"title":"Năng lượng","pageStart":160}]}]},
 "khoaExperiments":[
  {"subject":"KHTN","book":"$_book","lesson":11,"page":41,
   "title":"Oxygen","chuanBi":"que đóm","tienHanh":["Đốt."]},
  {"subject":"KHTN","book":"$_book","lesson":46,"page":161,
   "title":"Năng lượng","chuanBi":"xe","tienHanh":["Đẩy."]}]}
''')!;

Future<MissionData> _data() => buildMissionFromStore(
  profile: _g6,
  store: JsonlLearnerStore(),
  now: DateTime(2026, 9, 5, 19),
  index: _khtn6(),
);

void main() {
  testWidgets('⭐ có bài học SAM ⇒ «HÔM NAY»: dòng SAM nêu bài + vì sao; thẻ '
      'Bài học SAM đứng TRÊN thẻ «CÒN CÓ THỂ MỞ»; không mâu thuẫn «chưa có '
      'bài dạy riêng»', (t) async {
    var subjects = 0;
    final data = await _data();
    expect(data.scaleLessonCount, 2);
    // Màn cao để ListView dựng cả hai thẻ (so vị trí).
    t.view.physicalSize = const Size(1080, 5000);
    t.view.devicePixelRatio = 2.75;
    addTearDown(t.view.reset);
    await t.pumpWidget(
      fixtureHost(
        MissionCenterScreen(
          data: data,
          onOpenSubjects: () => subjects++,
          workspaceLesson: loadSyntheticDoc(),
          onOpenWorkspaceLesson: (_) {},
        ),
      ),
    );
    await t.pumpAndSettle();
    expect(find.text('HÔM NAY'), findsOneWidget);
    final line = t.widget<Text>(
      find.descendant(
        of: find.byKey(MissionCenterScreen.samLineKey),
        matching: find.byType(Text),
      ),
    );
    expect(line.data, contains('Bài 17'));
    expect(line.data, contains('Mở bài học'));
    expect(line.data, isNot(contains('trò chuyện')));
    expect(find.byIcon(Icons.mic_none), findsNothing);
    // vì sao bài này — lời trẻ, đếm từ tài liệu
    final why = t.widget<Text>(find.byKey(const Key('home-workspace-why')));
    expect(why.data, startsWith('Vì sao bài này?'));
    expect(why.data, contains('đọc như trong sách'));
    expect(why.data, contains('câu hỏi trong sách cùng SAM'));
    // thứ tự: bài học SAM trên, thẻ Scale dưới
    final yWs = t.getTopLeft(find.byKey(MissionCenterScreen.workspaceCardKey)).dy;
    final ySc = t.getTopLeft(find.byKey(MissionCenterScreen.secondaryCardKey)).dy;
    expect(yWs, lessThan(ySc));
    expect(find.text('CÒN CÓ THỂ MỞ'), findsOneWidget);
    expect(find.text('Có 2 bài để học ở Môn học'), findsOneWidget);
    expect(find.textContaining('chưa có bài dạy riêng'), findsNothing,
        reason: 'mâu thuẫn với thẻ Bài học SAM ngay trên');
    expect(find.textContaining('mở được 2 bài từ sách giáo khoa'), findsOneWidget);
    expect(find.text('Bắt đầu'), findsNothing);
    await t.ensureVisible(find.text('Vào Môn học ▸'));
    await t.tap(find.text('Vào Môn học ▸'));
    expect(subjects, 1);
  });

  testWidgets('không có bài học SAM ⇒ thẻ Scale là việc chính như round 3 '
      '(«Bắt đầu» mở Môn học); dòng SAM chỉ mời chọn thẻ', (t) async {
    final data = await _data();
    await t.pumpWidget(
      fixtureHost(MissionCenterScreen(data: data, onOpenSubjects: () {})),
    );
    await t.pumpAndSettle();
    expect(find.text('HÔM NAY'), findsOneWidget);
    expect(find.byKey(MissionCenterScreen.secondaryCardKey), findsNothing);
    expect(find.text('Bắt đầu'), findsOneWidget);
    expect(find.textContaining('chưa có bài dạy riêng'), findsOneWidget,
        reason: 'không có bài học SAM ⇒ câu này vẫn đúng');
    expect(find.textContaining('chọn một thẻ bên dưới'), findsOneWidget);
  });

  testWidgets('vùng «Hôm nay» không có %, sao, phút, «đã học»', (t) async {
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
    for (final w in t.widgetList<Text>(find.byType(Text))) {
      final s = (w.data ?? '').toLowerCase();
      expect(s, isNot(contains('%')), reason: s);
      expect(s, isNot(contains('★')), reason: s);
      expect(s, isNot(matches(RegExp(r'\d+\s*phút'))), reason: s);
      expect(s, isNot(contains('đã học')), reason: s);
    }
  });
}
