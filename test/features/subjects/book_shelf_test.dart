/// WAL-167 — Giá sách: trẻ nhận ra ĐÚNG cuốn sách, và bìa không bao giờ
/// trở thành nội dung.
library;

import 'dart:io';
import 'dart:ui' show Size;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/features/subjects/book_shelf_screen.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';
import 'package:learning_coach/features/subjects/subject_home_screen.dart';

import '../../support/pack_bundle.dart';

const _p = LearnerProfile(learnerId: 'l', displayName: 'Na', grade: 5);

LessonIndex _idx() => LessonIndex.fromJsonString('''
{"grade":5,"subjects":{"Toán":[
  {"sourceDocumentId":"05-sgk-toan-5-tap-mot","volume":"1",
   "lessons":[{"no":6,"title":"CỘNG, TRỪ HAI PHÂN SỐ","pageStart":20}]},
  {"sourceDocumentId":"05-sgk-toan-5-tap-hai","volume":"2",
   "lessons":[{"no":80,"title":"DIỆN TÍCH TAM GIÁC","pageStart":8}]}]},
 "toanExercises":{"6":[{"expr":"1/2 - 1/5","book":"05-sgk-toan-5-tap-mot",
   "skillCaseId":"denominator-non-divisible","page":21}]},
 "books":[
  {"sourceDocumentId":"05-sgk-toan-5-tap-mot","subject":"Toán","grade":5,
   "title":"Toán 5","volumeLabel":"Tập 1","cover":"covers/a.webp",
   "lessonCount":1,"bookSeries":null},
  {"sourceDocumentId":"05-sgk-toan-5-tap-hai","subject":"Toán","grade":5,
   "title":"Toán 5","volumeLabel":"Tập 2","cover":"covers/b.webp",
   "lessonCount":1,"bookSeries":null}]}
''')!;

void main() {
  testWidgets('⭐ giá sách hiện ĐÚNG cuốn: tên + tập + số bài', (t) async {
    await t.pumpWidget(packHost(
        BookShelfScreen(profile: _p, index: _idx(), onOpenBook: (_) {})));
    await t.pumpAndSettle();
    expect(find.text('Sách của con · Lớp 5'), findsOneWidget);
    expect(find.text('Toán 5 · Tập 1'), findsOneWidget);
    expect(find.text('Toán 5 · Tập 2'), findsOneWidget);
    expect(find.text('1 bài'), findsNWidgets(2));
  });

  testWidgets('⭐ bấm sách trả về ĐÚNG cuốn đó', (t) async {
    BookRef? opened;
    await t.pumpWidget(packHost(BookShelfScreen(
        profile: _p, index: _idx(), onOpenBook: (b) => opened = b)));
    await t.pumpAndSettle();
    await t.tap(find.text('Toán 5 · Tập 2'));
    await t.pumpAndSettle();
    expect(opened?.sourceDocumentId, '05-sgk-toan-5-tap-hai');
  });

  testWidgets('THIẾU bìa trên máy ⇒ vẫn vào sách được bằng TÊN', (t) async {
    await t.pumpWidget(missingPackHost(
        BookShelfScreen(profile: _p, index: _idx(), onOpenBook: (_) {})));
    await t.pumpAndSettle();
    // Tên sách hiện cả ở ô thay-ảnh lẫn nhãn dưới ⇒ không mất đường vào.
    expect(find.textContaining('Toán 5'), findsWidgets);
  });

  testWidgets('⭐⭐ Book Home chỉ hiện bài của ĐÚNG cuốn đã bấm', (t) async {
    final idx = _idx();
    final b2 = idx.bookById('05-sgk-toan-5-tap-hai')!;
    await t.pumpWidget(packHost(SubjectHomeScreen(
        profile: _p,
        store: JsonlLearnerStore(),
        index: idx,
        subject: 'Toán',
        book: b2)));
    await t.pumpAndSettle();
    expect(find.text('Toán 5 · Tập 2'), findsOneWidget);
    expect(find.textContaining('Bài 80'), findsOneWidget);
    expect(find.textContaining('Bài 6'), findsNothing,
        reason: '⭐⭐ Book Home rò bài của cuốn khác ⇒ đỏ');
  });

  testWidgets('không truyền book ⇒ vẫn là Subject Home cũ (hai lối, một màn)',
      (t) async {
    await t.pumpWidget(packHost(SubjectHomeScreen(
        profile: _p,
        store: JsonlLearnerStore(),
        index: _idx(),
        subject: 'Toán')));
    await t.pumpAndSettle();
    expect(find.text('Toán · Lớp 5'), findsOneWidget);
    expect(find.textContaining('Bài 6'), findsOneWidget);
    expect(find.textContaining('Bài 80'), findsOneWidget);
  });

  testWidgets(
      '⭐ QA n91: giá sách xếp NHIỀU cuốn một hàng — 13 cuốn không thành '
      '13 màn cuộn', (t) async {
    // Kích thước THẬT của Nokia 6.1: 1080×1920 @2.75 ⇒ ~393dp ngang.
    t.view.physicalSize = const Size(1080, 1920);
    t.view.devicePixelRatio = 2.75;
    addTearDown(t.view.reset);

    final books = [
      for (var i = 0; i < 6; i++)
        '{"sourceDocumentId":"d$i","subject":"Môn $i","title":"Môn $i 5",'
            '"cover":"covers/c$i.webp","lessonCount":3}'
    ].join(',');
    final idx = LessonIndex.fromJsonString(
        '{"grade":5,"subjects":{},"toanExercises":{},"books":[$books]}')!;

    await t.pumpWidget(
        packHost(BookShelfScreen(profile: _p, index: idx, onOpenBook: (_) {})));
    await t.pumpAndSettle();

    final y0 = t.getTopLeft(find.text('Môn 0 5')).dy;
    final y1 = t.getTopLeft(find.text('Môn 1 5')).dy;
    final y2 = t.getTopLeft(find.text('Môn 2 5')).dy;
    expect(y1, y0,
        reason: '⭐ đột biến quay lại mỗi môn một tiêu đề ⇒ mỗi hàng một cuốn '
            '⇒ đỏ (đúng lỗi đo được trên máy n91)');
    expect(y2, y0, reason: 'máy ~393dp phải xếp được 3 cột');
    expect(t.getTopLeft(find.text('Môn 3 5')).dy, greaterThan(y0),
        reason: 'cuốn thứ 4 phải xuống hàng — không tràn ra ngoài màn');
  });

  test('⭐ QA n93: cùng môn thì TẬP 1 đứng trước TẬP 2, môn giữ thứ tự mục lục',
      () {
    // Mục lục xếp theo mã tài liệu ⇒ «tap-hai» vào trước «tap-mot».
    final idx = LessonIndex.fromJsonString('''
{"grade":5,"subjects":{},"toanExercises":{},"books":[
 {"sourceDocumentId":"05-sgk-tieng-viet-5-tap-hai","subject":"Tiếng Việt",
  "title":"Tiếng Việt 5","volumeLabel":"Tập 2","volume":2,
  "cover":"covers/tv2.webp","lessonCount":16},
 {"sourceDocumentId":"05-sgk-tieng-viet-5-tap-mot","subject":"Tiếng Việt",
  "title":"Tiếng Việt 5","volumeLabel":"Tập 1","volume":1,
  "cover":"covers/tv1.webp","lessonCount":17},
 {"sourceDocumentId":"05-sgk-toan-5-tap-hai","subject":"Toán",
  "title":"Toán 5","volumeLabel":"Tập 2","volume":2,
  "cover":"covers/t2.webp","lessonCount":40},
 {"sourceDocumentId":"05-sgk-toan-5-tap-mot","subject":"Toán",
  "title":"Toán 5","volumeLabel":"Tập 1","volume":1,
  "cover":"covers/t1.webp","lessonCount":35}]}
''')!;
    expect(
        BookShelfScreen.shelfOrder(idx.books)
            .map((b) => '${b.subject} ${b.volumeLabel}')
            .toList(),
        ['Tiếng Việt Tập 1', 'Tiếng Việt Tập 2', 'Toán Tập 1', 'Toán Tập 2'],
        reason: '⭐ đột biến bỏ sắp xếp theo tập ⇒ đỏ (đúng lỗi đo trên n93); '
            'môn vẫn giữ thứ tự mục lục, không tự xếp hạng môn');
  });

  test('⭐ số cột theo bề ngang, có SÀN để bìa còn nhận ra được', () {
    expect(BookShelfScreen.columnsFor(361), 3, reason: 'Nokia 6.1');
    expect(BookShelfScreen.columnsFor(288), 2, reason: 'máy hẹp 320dp');
    expect(BookShelfScreen.columnsFor(120), 2,
        reason: '⭐ đột biến bỏ clamp dưới ⇒ 1 cột (hoặc 0) ⇒ đỏ');
    expect(BookShelfScreen.columnsFor(2000), 5,
        reason: '⭐ đột biến bỏ clamp trên ⇒ bìa bé li ti trên tablet ⇒ đỏ');
  });

  test('⭐ sách THIẾU bìa/định danh ⇒ KHÔNG lên giá (fail closed)', () {
    final idx = LessonIndex.fromJsonString('''
{"grade":5,"subjects":{},"toanExercises":{},"books":[
 {"sourceDocumentId":"x","subject":"Toán","title":"Toán 5"},
 {"sourceDocumentId":"y","subject":"Toán","cover":"covers/y.webp"},
 {"subject":"Toán","title":"Toán 5","cover":"covers/z.webp"}]}
''')!;
    expect(idx.books, isEmpty,
        reason: '⭐ một ô trống trên giá còn tệ hơn không có giá');
  });

  test('⭐ chiều bookSeries GIỮ CHỖ, không bịa giá trị', () {
    final b = _idx().books.first;
    expect(b.bookSeries, isNull,
        reason: 'registry chưa có bộ sách ⇒ null, không đoán KNTT');
  });

  test('FILE THẬT: pack lớp 5 có giá sách với bìa có thật trên đĩa', () {
    final f = File('assets/pack/lesson-index-g5.json');
    if (!f.existsSync()) {
      markTestSkipped('pack chưa build');
      return;
    }
    final idx = LessonIndex.fromJsonString(f.readAsStringSync())!;
    expect(idx.books.length, greaterThanOrEqualTo(10),
        reason: 'thấy ${idx.books.length} sách');
    for (final b in idx.books) {
      expect(File('assets/pack/${b.cover}').existsSync(), isTrue,
          reason: 'bìa ${b.cover} phải có thật — index không được hứa suông');
      expect(b.lessonCount, greaterThan(0));
    }
  });
}
