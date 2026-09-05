/// ⭐ WAL-210 item G1 (audit 05-UIUX «lesson chooser shows identical “Đọc bài”
/// labels»): một bài có HAI bài đọc ⇒ hai dòng phải phân biệt được bằng thứ
/// có thật trong pack (trang in + câu hỏi đầu); một bài đọc ⇒ nhãn cũ.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';
import 'package:learning_coach/features/subjects/subject_home_screen.dart';

const _p = LearnerProfile(learnerId: 'l', displayName: 'M', grade: 5);
const _book = '05-sgk-tieng-viet-5-tap-mot';

LessonIndex _two() => LessonIndex.fromJsonString('''
{"grade":5,"subjects":{
  "Tiếng Việt":[{"sourceDocumentId":"$_book","volume":"1",
    "lessons":[{"no":2,"title":"Cánh đồng hoa","pageStart":15}]}]},
 "tvReadings":[
  {"book":"$_book","lesson":2,"page":15,
   "passage":"Cánh đồng hoa trải dài đến tận chân trời, vàng rực dưới nắng.",
   "questions":[{"prompt":"Cánh đồng hoa được tả như thế nào?","page":15}]},
  {"book":"$_book","lesson":2,"page":17,
   "passage":"Buổi chiều, đàn bò thong thả về chuồng qua con đường đất đỏ.",
   "questions":[{"prompt":"Đàn bò về chuồng vào lúc nào trong ngày?","page":17}]}]}
''')!;

LessonIndex _one() => LessonIndex.fromJsonString('''
{"grade":5,"subjects":{
  "Tiếng Việt":[{"sourceDocumentId":"$_book","volume":"1",
    "lessons":[{"no":2,"title":"Cánh đồng hoa","pageStart":15}]}]},
 "tvReadings":[
  {"book":"$_book","lesson":2,"page":15,
   "passage":"Cánh đồng hoa trải dài đến tận chân trời.",
   "questions":[{"prompt":"Cánh đồng hoa được tả như thế nào?","page":15}]}],
 "tvWritings":[{"book":"$_book","lesson":2,"page":16,
   "prompt":"Viết đoạn văn tả một cánh đồng em từng thấy."}]}
''')!;

Future<void> _open(WidgetTester t, LessonIndex idx) async {
  await t.pumpWidget(MaterialApp(
      home: SubjectHomeScreen(
          profile: _p,
          store: JsonlLearnerStore(),
          index: idx,
          subject: 'Tiếng Việt')));
  await t.pumpAndSettle();
  await t.tap(find.textContaining('Cánh đồng hoa'));
  await t.pumpAndSettle();
  expect(find.text('Con muốn làm phần nào trước?'), findsOneWidget);
}

void main() {
  testWidgets('⭐⭐ hai bài đọc ⇒ hai dòng KHÁC nhau (trang + câu hỏi thật), '
      'không còn hai dòng «📖 Đọc bài» y hệt', (t) async {
    await _open(t, _two());
    expect(find.text('📖 Đọc bài'), findsNothing,
        reason: '⭐⭐ đột biến trả lại nhãn trần cho cả hai ⇒ đỏ (audit 05)');
    final a = find.textContaining('📖 Đọc bài · trang 15 — Cánh đồng hoa được tả');
    final b = find.textContaining('📖 Đọc bài · trang 17 — Đàn bò về chuồng');
    expect(a, findsOneWidget);
    expect(b, findsOneWidget);
    // Nhãn dùng chữ THẬT của pack — không có tên bịa kiểu «(1)», «(2)».
    expect(find.textContaining('(1)'), findsNothing);
    expect(find.textContaining('(2)'), findsNothing);
  });

  testWidgets('bấm dòng THỨ HAI ⇒ mở ĐÚNG bài đọc thứ hai (đoạn văn tr. 17)',
      (t) async {
    await _open(t, _two());
    await t.tap(find.textContaining('trang 17 — Đàn bò'));
    await t.pumpAndSettle();
    expect(find.textContaining('đàn bò thong thả về chuồng'), findsOneWidget,
        reason: 'đúng đoạn văn của bài đọc thứ hai');
    expect(find.textContaining('vàng rực dưới nắng'), findsNothing,
        reason: 'không lẫn sang bài đọc thứ nhất');
  });

  testWidgets('MỘT bài đọc (+ đề viết) ⇒ nhãn giữ nguyên «📖 Đọc bài»',
      (t) async {
    await _open(t, _one());
    expect(find.text('📖 Đọc bài'), findsOneWidget,
        reason: 'không thêm chữ khi không có gì để phân biệt');
    expect(find.text('✍️ Luyện viết'), findsOneWidget);
  });
}
