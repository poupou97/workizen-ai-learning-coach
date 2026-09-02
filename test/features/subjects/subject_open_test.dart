/// WAL-144 — SubjectHome mở HOẠT ĐỘNG đúng loại: đề «Viết» thật → Compose
/// (không nuốt hoạt động khi bài có nhiều việc — sheet chọn).
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';
import 'package:learning_coach/features/subjects/subject_home_screen.dart';

const _p = LearnerProfile(learnerId: 'l', displayName: 'M', grade: 5);

LessonIndex _idx() => LessonIndex.fromJsonString('''
{"grade":5,"subjects":{
  "Tiếng Việt":[{"sourceDocumentId":"05-sgk-tieng-viet-5-tap-mot","volume":null,
    "lessons":[{"no":4,"title":"LUYỆN VIẾT","pageStart":24},
               {"no":1,"title":"THANH ÂM CỦA GIÓ","pageStart":8}]}]},
 "toanExercises":{},
 "tvReadings":[{"book":"05-sgk-tieng-viet-5-tap-mot","lesson":1,"page":8,
   "passage":"Chúng tôi đi chăn trâu, ngày nào cũng qua suối.",
   "questions":[{"prompt":"1. Khung cảnh được miêu tả thế nào?","page":9}]},
  {"book":"05-sgk-tieng-viet-5-tap-mot","lesson":4,"page":24,
   "passage":"Đoạn văn mẫu quan sát trước khi viết.",
   "questions":[{"prompt":"1. Đoạn văn tả gì?","page":24}]}],
 "tvWritings":[{"book":"05-sgk-tieng-viet-5-tap-mot","lesson":4,"page":25,
   "prompt":"1. Dựa vào dàn ý đã lập, viết bài văn theo yêu cầu của đề bài."}]}
''')!;

Future<void> _pump(WidgetTester t) async {
  await t.pumpWidget(MaterialApp(
      home: SubjectHomeScreen(
          profile: _p,
          store: JsonlLearnerStore(),
          index: _idx(),
          subject: 'Tiếng Việt')));
  await t.pump();
}

void main() {
  testWidgets('bài CHỈ có đọc ⇒ mở thẳng Reader, không sheet', (t) async {
    await _pump(t);
    expect(find.textContaining('1 bài đọc từ SGK'), findsOneWidget);
    await t.tap(find.textContaining('Thanh âm của gió'));
    await t.pumpAndSettle();
    expect(find.text('Con đọc xong rồi 📖'), findsOneWidget,
        reason: 'một hoạt động ⇒ vào thẳng, không hỏi thừa');
  });

  testWidgets('⭐ bài có ĐỌC + VIẾT ⇒ sheet chọn; «Luyện viết» → Compose '
      '(dàn ý trước, KHÔNG viết hộ)', (t) async {
    await _pump(t);
    expect(find.textContaining('1 bài đọc · 1 đề viết'), findsOneWidget,
        reason: 'subtitle kể ĐỦ hoạt động — không nuốt');
    await t.tap(find.textContaining('Luyện viết').first.hitTestable(),
        warnIfMissed: false);
    // tile title là «Bài 4 · Luyện viết» — tap tile:
    await t.tap(find.textContaining('Bài 4'));
    await t.pumpAndSettle();
    expect(find.text('📖 Đọc bài'), findsOneWidget);
    expect(find.text('✍️ Luyện viết'), findsOneWidget);
    await t.tap(find.text('✍️ Luyện viết'));
    await t.pumpAndSettle();
    expect(find.textContaining('viết bài văn theo yêu cầu'), findsOneWidget,
        reason: 'đề THẬT từ SGK hiện trên Compose');
    expect(find.text('Xong dàn ý — viết nháp ✍️'), findsOneWidget,
        reason: '⭐ đột biến dispatch viết→Reader ⇒ test này đỏ — '
            'bước 1 là DÀN Ý CỦA TRẺ, không có góp ý/bài mẫu nào');
    expect(find.text('Con đọc xong rồi 📖'), findsNothing);
  });
}
