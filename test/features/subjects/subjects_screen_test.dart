/// WAL-136 — Subjects/SubjectHome: grid từ data, bài mở được vs nói thật.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';
import 'package:learning_coach/features/subjects/subject_home_screen.dart';
import 'package:learning_coach/features/subjects/subjects_screen.dart';

const _p = LearnerProfile(learnerId: 'l', displayName: 'M', grade: 5);

LessonIndex idx() => LessonIndex.fromJsonString('''
{"grade":5,"subjects":{
  "Toán":[{"sourceDocumentId":"05-sgk-toan-5-tap-mot","volume":"1",
    "lessons":[{"no":6,"title":"CỘNG, TRỪ HAI PHÂN SỐ KHÁC MẪU SỐ","pageStart":20},
               {"no":9,"title":"THỂ TÍCH","pageStart":40}]}],
  "Khoa học":[{"sourceDocumentId":"05-sgk-khoa-hoc-5","volume":null,
    "lessons":[{"no":1,"title":"ĐẤT VÀ NƯỚC","pageStart":6}]}]},
 "toanExercises":{"6":[{"expr":"1/2 - 1/5","page":21,"book":"05-sgk-toan-5-tap-mot"}]}}
''')!;

void main() {
  testWidgets('grid môn sinh từ data; thiếu index ⇒ nói thật', (t) async {
    await t.pumpWidget(MaterialApp(
        home: SubjectsScreen(
            profile: _p, store: JsonlLearnerStore(), index: idx())));
    expect(find.text('Môn học · Lớp 5'), findsOneWidget);
    expect(find.text('Toán'), findsOneWidget);
    expect(find.text('Khoa học'), findsOneWidget);

    await t.pumpWidget(MaterialApp(
        home: SubjectsScreen(
            profile: _p, store: JsonlLearnerStore(), index: null)));
    expect(find.textContaining('chưa nạp mục lục'), findsOneWidget);
  });

  testWidgets('Subject Home: tên bài THẬT; bài có bài tập mở được, bài chưa '
      'nối engine nói thật (không dead-end)', (t) async {
    await t.pumpWidget(MaterialApp(
        home: SubjectHomeScreen(
            profile: _p,
            store: JsonlLearnerStore(),
            index: idx(),
            subject: 'Toán')));
    expect(find.textContaining('Cộng, trừ hai phân số khác mẫu số'),
        findsOneWidget, reason: 'title mined thật, đổi về câu thường');
    expect(find.textContaining('1 bài tập từ SGK'), findsOneWidget);
    expect(find.textContaining('SAM đang học bài này'), findsOneWidget,
        reason: 'bài 9 chưa có exercises — nói thật');

    // Toán B6 giờ có 2 hoạt động (làm bài + nguồn) ⇒ sheet chọn (WAL-141 #17).
    await t.tap(find.textContaining('Cộng, trừ hai phân số'));
    await t.pumpAndSettle();
    expect(find.text('📖 Nguồn bài học'), findsOneWidget);
    // Nguồn bài học: cả 2 cách với sourceLine ĐÚNG LUẬT (demonstrated ≠ sách nói)
    await t.tap(find.text('📖 Nguồn bài học'));
    await t.pumpAndSettle();
    expect(find.textContaining('làm theo ví dụ trong SGK Toán 5, trang 21'),
        findsOneWidget);
    expect(find.textContaining('làm theo ví dụ trong SGK Toán 4, trang 77'),
        findsOneWidget, reason: 'take-larger cũng demonstrated — cùng luật');
    expect(find.textContaining('sách nói'), findsNothing);
    await t.tapAt(const Offset(400, 50)); // đóng sheet
    await t.pumpAndSettle();
    await t.tap(find.textContaining('Cộng, trừ hai phân số'));
    await t.pumpAndSettle();
    await t.tap(find.text('🧮 Làm bài tập'));
    await t.pumpAndSettle();
    expect(find.text('1/2 - 1/5'), findsOneWidget,
        reason: 'bài THẬT từ SGK (cur: origin), không placeholder');
    expect(find.textContaining('SAM làm theo ví dụ trong SGK Toán 5'),
        findsOneWidget, reason: 'provenance hiện TRƯỚC khi học');
  });
}
