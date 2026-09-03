/// WAL-166 — mở bài theo DỮ LIỆU, không theo tên môn.
///
/// Phép thử thật của luận điểm «thêm môn = thêm data»: một môn KHÔNG hề có
/// trong mã (tên bịa) mà pack có dữ liệu thì bài phải mở được.
library;

import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';
import 'package:learning_coach/features/subjects/subject_home_screen.dart';

const _p = LearnerProfile(learnerId: 'l', displayName: 'Na', grade: 5);

/// Môn «Thiên văn» KHÔNG tồn tại ở đâu trong `lib/` — nếu bài của nó mở được
/// thì UI thật sự chạy bằng dữ liệu.
LessonIndex _madeUpSubject() => LessonIndex.fromJsonString('''
{"grade":5,"subjects":{"Thiên văn":[{"sourceDocumentId":"05-sgk-thien-van-5",
  "volume":null,"lessons":[{"no":3,"title":"CÁC VÌ SAO","pageStart":12}]}]},
 "toanExercises":{},
 "tvReadings":[{"book":"05-sgk-thien-van-5","lesson":3,"page":12,
   "passage":"Bầu trời đêm có hàng nghìn ngôi sao.",
   "questions":[{"prompt":"1. Kể tên một chòm sao em biết.","page":12}]}]}
''')!;

Widget _host(LessonIndex idx, String subject) => MaterialApp(
    home: SubjectHomeScreen(
        subject: subject, profile: _p, store: JsonlLearnerStore(), index: idx));

void main() {
  testWidgets('⭐⭐ MÔN KHÔNG CÓ TRONG MÃ mà pack có dữ liệu ⇒ bài MỞ ĐƯỢC',
      (t) async {
    await t.pumpWidget(_host(_madeUpSubject(), 'Thiên văn'));
    await t.pumpAndSettle();
    expect(find.textContaining('Bài 3'), findsOneWidget);
    expect(find.textContaining('1 bài đọc'), findsOneWidget,
        reason: '⭐⭐ đột biến quay lại nhánh cứng theo tên môn ⇒ đỏ');
    // Có mũi tên = bấm được (tile khoá thì trailing là null).
    expect(find.byIcon(Icons.chevron_right), findsWidgets);
  });

  testWidgets('bài KHÔNG có dữ liệu ⇒ vẫn khoá, nói thật (fail closed)',
      (t) async {
    final idx = LessonIndex.fromJsonString('''
{"grade":5,"subjects":{"Thiên văn":[{"sourceDocumentId":"b","volume":null,
  "lessons":[{"no":9,"title":"SAO CHỔI","pageStart":40}]}]},"toanExercises":{}}
''')!;
    await t.pumpWidget(_host(idx, 'Thiên văn'));
    await t.pumpAndSettle();
    expect(find.textContaining('SAM đang học bài này'), findsOneWidget);
    expect(find.byIcon(Icons.chevron_right), findsNothing);
  });

  test('⭐ việc được lọc theo ĐÚNG CUỐN SÁCH, không chỉ theo số bài', () {
    final idx = LessonIndex.fromJsonString('''
{"grade":5,"subjects":{},"toanExercises":{"6":[
   {"expr":"1/2 - 1/5","book":"sach-A","skillCaseId":"k","page":21},
   {"expr":"1/3 + 1/4","book":"sach-B","skillCaseId":"k","page":30}]},
 "suSources":[{"book":"sach-A","page":41,"lesson":6,"excerpt":"x",
   "attribution":"(Nguồn A)"},
  {"book":"sach-B","page":9,"lesson":6,"excerpt":"y","attribution":"(Nguồn B)"}]}
''')!;
    final a = idx.activitiesFor(book: 'sach-A', lessonNo: 6);
    expect(a.whereType<ExerciseActivity>().single.items.single.book, 'sach-A');
    expect(a.whereType<SourceActivity>().single.source.attribution,
        contains('Nguồn A'),
        reason: '⭐ bài số 6 của sách khác lôi nhầm tư liệu ⇒ đỏ');
    expect(idx.activitiesFor(book: 'sach-C', lessonNo: 6), isEmpty);
  });

  test('⭐ CẤU TRÚC: Subject Home không còn so tên môn bằng chuỗi', () {
    final src = File('lib/features/subjects/subject_home_screen.dart')
        .readAsLinesSync()
        .where((l) => !l.trimLeft().startsWith('//'))
        .join('\n');
    for (final banned in [
      "subject == 'Toán'",
      "subject == 'Tiếng Việt'",
      "subject == 'LS&ĐL'",
      '_isToan',
      '_isTv',
      '_isSu',
    ]) {
      expect(src.contains(banned), isFalse,
          reason: '⭐ nhánh cứng theo tên môn quay lại: «$banned»');
    }
  });

  test('FILE THẬT: pack lớp 5 mở được bài ở NHIỀU môn, không chỉ ba môn', () {
    final f = File('assets/pack/lesson-index-g5.json');
    if (!f.existsSync()) {
      markTestSkipped('pack chưa build trên máy này');
      return;
    }
    final idx = LessonIndex.fromJsonString(f.readAsStringSync())!;
    final subjectsWithOpenable = <String>{};
    var total = 0;
    for (final e in idx.subjects.entries) {
      for (final b in e.value) {
        for (final l in b.lessons) {
          if (idx
              .activitiesFor(book: b.sourceDocumentId, lessonNo: l.no)
              .isNotEmpty) {
            subjectsWithOpenable.add(e.key);
            total++;
          }
        }
      }
    }
    expect(total, greaterThan(30),
        reason: 'pack thật phải mở được hàng chục bài — thấy $total');
    expect(subjectsWithOpenable.length, greaterThanOrEqualTo(3),
        reason: 'nhiều môn phải mở được — thấy $subjectsWithOpenable');
  });

  test('⭐ PHƠI RA khoảng lệch dữ liệu: hoạt động MỒ CÔI vì lệch số bài', () {
    // Refactor này lộ ra một lỗi DỮ LIỆU có thật: Tiếng Việt TẬP HAI đánh số
    // bài 19–35 trong mục lục, nhưng bài đọc/đề viết mined lại đánh số LẠI từ
    // 1 ⇒ đúng một nửa nội dung TV không gắn được vào bài nào.
    //
    // Test này KHÔNG vá bằng offset (cộng 18 có thể gán nhầm, vì tập hai cũng
    // có bài 19-20 thật). Nó ĐO khoảng lệch để con số không âm thầm tệ đi, và
    // sẽ siết lại khi builder sửa đánh số.
    final f = File('assets/pack/lesson-index-g5.json');
    if (!f.existsSync()) {
      markTestSkipped('pack chưa build trên máy này');
      return;
    }
    final idx = LessonIndex.fromJsonString(f.readAsStringSync())!;
    final inIndex = <String>{
      for (final books in idx.subjects.values)
        for (final b in books)
          for (final l in b.lessons) '${b.sourceDocumentId}#${l.no}'
    };
    final mined = <String>{
      for (final r in idx.tvReadings) '${r.book}#${r.lesson}',
      for (final w in idx.tvWritings) '${w.book}#${w.lesson}',
    };
    final orphan = mined.difference(inIndex);
    expect(orphan.length, lessThanOrEqualTo(34),
        reason: 'số hoạt động mồ côi KHÔNG được tăng thêm — thấy '
            '${orphan.length}/${mined.length}');
  });
}
