/// ⭐ WAL-210 item G2 (audit 05-UIUX): Home của lớp KHÔNG có chương trình Deep
/// nhưng CÓ bài mở được từ SGK phải nói THẬT con số bài và «Bắt đầu» phải mở
/// MÔN HỌC, không mở camera. Trước đây: «SAM chưa có nội dung lớp 6 — sắp có
/// nhé» + «Bắt đầu» → camera, dù KHTN 6 mở được từ giá sách.
///
/// Ba lớp: 6 chỉ-Scale (fixture KHTN 6 với Bài 17 «Tách chất khỏi hỗn hợp»),
/// 6 không pack, 5 có Deep (thẻ của agenda giữ nguyên; camera vẫn là đường
/// của nội dung Deep qua chip 📷 / nút «Chụp bài tập»).
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/features/mission/mission_center_screen.dart';
import 'package:learning_coach/features/mission/mission_data.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';

const _g6 = LearnerProfile(learnerId: 'l6', displayName: 'Na', grade: 6);
const _g5 = LearnerProfile(learnerId: 'l5', displayName: 'Minh', grade: 5);
const _book = '06-sgk-khoa-hoc-tu-nhien-6';

/// KHTN 6: 3 bài mở được (17 đọc, 18 thí nghiệm, 20 đọc), 1 bài không (19).
LessonIndex _khtn6() => LessonIndex.fromJsonString('''
{"grade":6,"subjects":{"KHTN":[{"sourceDocumentId":"$_book","volume":null,
   "lessons":[{"no":17,"title":"Tách chất khỏi hỗn hợp","pageStart":60},
              {"no":18,"title":"Tế bào","pageStart":64},
              {"no":19,"title":"Cấu tạo tế bào","pageStart":68},
              {"no":20,"title":"Sự lớn lên của tế bào","pageStart":72}]}]},
 "tvReadings":[
  {"book":"$_book","lesson":17,"page":62,"passage":"Tách dầu ăn khỏi nước…",
   "questions":[{"prompt":"2. Tại sao phải mở khoá phễu chiết từ từ?","page":62}]},
  {"book":"$_book","lesson":20,"page":73,"passage":"Tế bào lớn lên…",
   "questions":[{"prompt":"1. Tế bào lớn lên nhờ đâu?","page":73}]}],
 "khoaExperiments":[{"subject":"KHTN","book":"$_book","lesson":18,"page":65,
   "title":"Quan sát tế bào","chuanBi":"kính hiển vi","tienHanh":["Đặt tiêu bản."]}]}
''')!;

Future<(bool, bool)> _pumpAndStart(WidgetTester t, MissionData data) async {
  var subjects = false, camera = false;
  await t.pumpWidget(MaterialApp(
      home: MissionCenterScreen(
    data: data,
    onOpenSubjects: () => subjects = true,
    onStartHomework: () => camera = true,
    onReview: () {},
  )));
  await t.pumpAndSettle();
  // Nút «Bắt đầu» nằm trong thẻ hành động — thẻ ở đầu màn.
  await t.tap(find.text('Bắt đầu').first);
  await t.pumpAndSettle();
  return (subjects, camera);
}

void main() {
  final today = DateTime(2026, 9, 5, 19);

  testWidgets('⭐⭐ lớp 6 + pack KHTN có 3 bài mở được ⇒ thẻ nói «Có 3 bài để '
      'học ở Môn học», «Bắt đầu» mở MÔN HỌC, KHÔNG mở camera', (t) async {
    final data = await buildMissionFromStore(
        profile: _g6, store: JsonlLearnerStore(), now: today, index: _khtn6());
    expect(data.scaleLessonCount, 3, reason: 'bài 19 không có việc ⇒ không đếm');
    expect(data.nextActionTitle, 'Có 3 bài để học ở Môn học');
    expect(data.agenda, isNull, reason: 'không có chương trình Deep ⇒ không agenda');

    final (subjects, camera) = await _pumpAndStart(t, data);
    expect(find.text('Có 3 bài để học ở Môn học'), findsOneWidget);
    expect(find.textContaining('mở được 3 bài từ sách giáo khoa'), findsOneWidget,
        reason: 'lý do nói con số THẬT của pack');
    expect(find.textContaining('chưa có nội dung lớp 6'), findsNothing,
        reason: '⭐⭐ audit 05: câu này là sai khi KHTN 6 mở được từ giá sách');
    expect(subjects, isTrue, reason: '⭐⭐ đột biến giữ camera ⇒ đỏ');
    expect(camera, isFalse);
    // Camera vẫn là đường của nội dung Deep — chip không bị gỡ.
    expect(find.text('📷 Làm bài tập'), findsOneWidget);
  });

  testWidgets('lớp 6 KHÔNG có pack (index null) ⇒ câu cũ, nói thật là chưa có',
      (t) async {
    final data = await buildMissionFromStore(
        profile: _g6, store: JsonlLearnerStore(), now: today);
    expect(data.scaleLessonCount, 0);
    expect(data.nextActionTitle, 'SAM chưa có nội dung lớp 6 — sắp có nhé');
    await t.pumpWidget(MaterialApp(home: MissionCenterScreen(data: data)));
    expect(find.text('SAM chưa có nội dung lớp 6 — sắp có nhé'), findsOneWidget);
  });

  testWidgets('lớp 6 + pack KHÔNG có bài mở được ⇒ vẫn câu cũ (không bịa số 0 bài)',
      (t) async {
    final empty = LessonIndex.fromJsonString(
        '{"grade":6,"subjects":{"KHTN":[{"sourceDocumentId":"$_book",'
        '"lessons":[{"no":1,"title":"Mở đầu","pageStart":5}]}]}}')!;
    final data = await buildMissionFromStore(
        profile: _g6, store: JsonlLearnerStore(), now: today, index: empty);
    expect(data.scaleLessonCount, 0);
    expect(data.nextActionTitle, contains('chưa có nội dung lớp 6'));
  });

  testWidgets('lớp 5 CÓ chương trình Deep ⇒ thẻ agenda như cũ, không «Có N bài»',
      (t) async {
    final data = await buildMissionFromStore(
        profile: _g5, store: JsonlLearnerStore(), now: today, index: _khtn6());
    expect(data.agenda, isNotNull);
    expect(data.scaleLessonCount, 0,
        reason: 'đường Deep có agenda riêng — không trộn con số Scale vào');
    expect(data.nextActionTitle, isNot(startsWith('Có ')));
    await t.pumpWidget(MaterialApp(home: MissionCenterScreen(data: data)));
    expect(find.text('VIỆC SAM ĐỀ XUẤT'), findsOneWidget);
    expect(find.textContaining('bài để học ở Môn học'), findsNothing);
  });
}
