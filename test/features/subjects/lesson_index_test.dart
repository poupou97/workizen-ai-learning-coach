/// WAL-136 — LessonIndex parser: dữ liệu thật, fail-closed khi vỡ.
library;

import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';

const _sample = '''
{"grade":5,"version":"lesson-index-v1",
 "subjects":{"Toán":[{"sourceDocumentId":"05-sgk-toan-5-tap-mot","volume":"1",
   "lessons":[{"no":6,"title":"CỘNG, TRỪ HAI PHÂN SỐ KHÁC MẪU SỐ","pageStart":20},
              {"no":7,"title":null,"pageStart":24}]}],
  "Tiếng Việt":[{"sourceDocumentId":"05-sgk-tieng-viet-5-tap-mot","volume":null,
   "lessons":[{"no":1,"title":"THANH ÂM CỦA GIÓ","pageStart":8}]}]},
 "toanExercises":{"6":[{"expr":"1/2 - 1/5","skillCaseId":"denominator-non-divisible",
   "page":21,"book":"05-sgk-toan-5-tap-mot"}]}}
''';

void main() {
  test('parse dữ liệu thật: môn, bài, title null giữ nguyên, exercises', () {
    final idx = LessonIndex.fromJsonString(_sample)!;
    expect(idx.grade, 5);
    expect(idx.subjects.keys, containsAll(['Toán', 'Tiếng Việt']));
    final toan = idx.subjects['Toán']!.single;
    expect(toan.lessons.first.no, 6);
    expect(toan.lessons.first.title, contains('KHÁC MẪU SỐ'));
    expect(toan.lessons[1].title, isNull, reason: 'không bịa tên bài');
    final ex = idx.exercisesForToan(6).single;
    expect(ex.expr, '1/2 - 1/5');
    expect(ex.page, 21);
    expect(idx.exercisesForToan(99), isEmpty);
  });

  test('FILE THẬT builder sinh ra parse được (chống schema-drift kiểu int/str)',
      () {
    final f = File('assets/pack/lesson-index-g5.json');
    if (!f.existsSync()) {
      markTestSkipped('asset chưa build trên máy này');
      return;
    }
    final idx = LessonIndex.fromJsonString(f.readAsStringSync());
    expect(idx, isNotNull, reason: 'parser phải nuốt được file THẬT');
    expect(idx!.subjects['Toán'], isNotEmpty);
    expect(idx.exercisesForToan(6), isNotEmpty, reason: 'B6 có bài tập thật');
  });

  test('JSON vỡ / thiếu grade ⇒ null (fail closed)', () {
    expect(LessonIndex.fromJsonString('{hỏng'), isNull);
    expect(LessonIndex.fromJsonString('{"subjects":{}}'), isNull);
  });
}