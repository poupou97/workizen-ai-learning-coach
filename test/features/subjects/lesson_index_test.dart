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
   "page":21,"book":"05-sgk-toan-5-tap-mot"}]},
 "tvReadings":[{"book":"05-sgk-tieng-viet-5-tap-mot","lesson":1,"page":8,
   "passage":"THANH ÂM CỦA GIÓ Chúng tôi đi chăn trâu, ngày nào cũng qua suối.",
   "questions":[{"prompt":"1. Khung cảnh thiên nhiên được miêu tả thế nào?","page":9}]}],
 "suSources":[{"book":"05-sgk-lich-su-va-dia-li-5","page":41,"lesson":9,
   "lessonTitle":"TRIỀU LÝ VÀ VIỆC ĐỊNH ĐÔ Ở THĂNG LONG",
   "excerpt":"Trong Chiếu dời đô có đoạn ...",
   "attribution":"(Theo Ngô Sỹ Liên..., Đại Việt sử ký toàn thư, Tập I)",
   "samGloss":"Nguồn này cho thấy việc dời đô có tính toán."},
  {"book":"05-sgk-lich-su-va-dia-li-5","page":18,"lesson":3,
   "excerpt":"khối hỏng: KHÔNG có attribution — phải bị loại"}]}
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
    // WAL-113: file thật phải mang cross-subject data (build từ poc-out).
    expect(idx.tvReadings, isNotEmpty, reason: 'TV5 có bài đọc mined thật');
    expect(idx.suSources, hasLength(2),
        reason: '2 khối TƯ LIỆU thật (đội Hoàng Sa + Chiếu dời đô)');
    expect(idx.suSources.every((s) => s.attribution.endsWith(')')), isTrue,
        reason: 'mọi tư liệu bundle đều có attribution đầy đủ');
  });

  test('⭐ WAL-113: tvReadings + suSources parse; tư liệu THIẾU attribution '
      'bị loại (fail closed — không render nguồn không dẫn được)', () {
    final idx = LessonIndex.fromJsonString(_sample)!;
    final r = idx.readingsForTv('05-sgk-tieng-viet-5-tap-mot', 1).single;
    expect(r.passage, contains('chăn trâu'));
    expect(r.questions.single.prompt, contains('Khung cảnh'));
    expect(idx.readingsForTv('05-sgk-tieng-viet-5-tap-mot', 99), isEmpty);
    final su = idx.suSources;
    expect(su, hasLength(1),
        reason: '⭐ khối thiếu attribution KHÔNG được thành SuSource');
    expect(su.single.attribution, contains('Đại Việt sử ký'));
    expect(idx.suSourcesFor(9).single.samGloss, contains('tính toán'));
    expect(idx.suSourcesFor(3), isEmpty, reason: 'khối hỏng đã bị loại');
  });

  test('JSON vỡ / thiếu grade ⇒ null (fail closed)', () {
    expect(LessonIndex.fromJsonString('{hỏng'), isNull);
    expect(LessonIndex.fromJsonString('{"subjects":{}}'), isNull);
  });
}