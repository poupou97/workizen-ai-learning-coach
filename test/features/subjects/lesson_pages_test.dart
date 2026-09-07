/// TRANG SÁCH CỦA BÀI — họ hoạt động mở được nhiều bài nhất.
///
/// Census toàn corpus đo được: 3.142 bài có nội dung đọc được, sản phẩm mở
/// được 117 (3,2%). Lớp 1, 2, 3, 11, 12 có ĐÚNG 0 bài mở được. Không phải
/// thiếu dữ liệu — `activitiesFor` không có họ nào là «đọc trang sách».
///
/// Test ở đây giữ hai thứ đối nghịch nhau: bài CÓ trang sách thì phải mở được,
/// và bài KHÔNG có thì tuyệt đối không được «mở được» rỗng.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';
import 'package:learning_coach/features/subjects/lesson_pages_screen.dart';

const _book = '06-sgk-khoa-hoc-tu-nhien-6';

LessonIndex _idx({String readings = ''}) => LessonIndex.fromJsonString('''
{
 "grade": 6,
 "subjects": {"KHTN": [{"sourceDocumentId": "$_book", "volume": null,
   "lessons": [{"no": 17, "title": "Tách chất khỏi hỗn hợp", "pageStart": 60}]}]},
 "toanExercises": {},
 "lessonReadings": [$readings]
}
''')!;

const _good = '''
{"book": "$_book", "lesson": 17, "title": "Tách chất khỏi hỗn hợp",
 "pageStart": 60, "pagePdfStart": 61, "pagePdfEnd": 64,
 "text": "TÁCH CHẤT KHỎI HỖN HỢP Bài 17 MỤC TIÊU"}''';

void main() {
  group('pack → sản phẩm', () {
    test('bài có trang sách ⇒ CÓ hoạt động ⇒ mở được', () {
      final acts = _idx(readings: _good).activitiesFor(book: _book, lessonNo: 17);
      expect(acts, hasLength(1));
      expect(acts.single, isA<LessonPagesActivity>());
    });

    test('bài KHÔNG có trang sách ⇒ không có hoạt động nào', () {
      // «Mở được» rỗng còn tệ hơn không mở được: trẻ bấm vào rồi thấy trang trắng.
      expect(_idx().activitiesFor(book: _book, lessonNo: 17), isEmpty);
    });

    test('mục của bài KHÁC không rơi vào bài này', () {
      final other = _good.replaceAll('"lesson": 17', '"lesson": 16');
      expect(_idx(readings: other).activitiesFor(book: _book, lessonNo: 17), isEmpty);
    });

    test('mục hỏng bị BỎ, không dựng nửa vời', () {
      for (final broken in [
        _good.replaceAll('"pagePdfEnd": 64', '"pagePdfEnd": 60'), // hết < bắt đầu
        _good.replaceAll('"text": "TÁCH CHẤT KHỎI HỖN HỢP Bài 17 MỤC TIÊU"',
            '"text": "   "'), // rỗng chữ
        _good.replaceAll('"pagePdfStart": 61,', ''), // thiếu dải
      ]) {
        expect(_idx(readings: broken).activitiesFor(book: _book, lessonNo: 17),
            isEmpty, reason: broken);
      }
    });
  });

  group('màn đọc nói thật', () {
    LessonPages pages({int? printed = 60, int end = 64}) => LessonPages(
        book: _book,
        lesson: 17,
        text: 'TÁCH CHẤT KHỎI HỖN HỢP Bài 17',
        pageStart: printed,
        pagePdfStart: 61,
        pagePdfEnd: end);

    testWidgets('dòng nguồn dùng TRANG IN, không phải trang PDF', (t) async {
      // Trang PDF là 61–64; trẻ cầm sách giấy thấy 60–63. Đưa số PDF ra là nói
      // với trẻ một số trang không có trong quyển sách trên tay nó.
      final s = LessonPagesScreen(
          pages: pages(), lessonLabel: 'Bài 17', bookTitle: 'KHTN 6');
      expect(s.sourceLine, 'KHTN 6 · trang 60–63');
      await t.pumpWidget(MaterialApp(home: s));
      expect(find.textContaining('trang 60–63'), findsOneWidget);
      expect(find.textContaining('61'), findsNothing);
    });

    test('mục lục không nói trang in ⇒ nói ít đi, KHÔNG đưa số PDF ra', () {
      final s = LessonPagesScreen(
          pages: pages(printed: null), lessonLabel: 'Bài 17', bookTitle: 'KHTN 6');
      expect(s.sourceLine, 'KHTN 6 · 4 trang');
      expect(s.sourceLine, isNot(contains('61')));
    });

    testWidgets('không chấm, không hỏi, không %', (t) async {
      await t.pumpWidget(MaterialApp(
          home: LessonPagesScreen(pages: pages(), lessonLabel: 'Bài 17')));
      for (final w in ['%', 'Đúng', 'Sai', 'Nộp', 'Trả lời', 'điểm']) {
        expect(find.textContaining(w), findsNothing, reason: w);
      }
    });

    testWidgets('nói thẳng SAM chưa soạn bài này, không hiện tab rỗng', (t) async {
      await t.pumpWidget(MaterialApp(
          home: LessonPagesScreen(pages: pages(), lessonLabel: 'Bài 17')));
      expect(find.textContaining('SAM chưa soạn'), findsOneWidget);
    });

    testWidgets('chữ của sách hiện nguyên văn', (t) async {
      await t.pumpWidget(MaterialApp(
          home: LessonPagesScreen(pages: pages(), lessonLabel: 'Bài 17')));
      expect(find.textContaining('TÁCH CHẤT KHỎI HỖN HỢP'), findsOneWidget);
    });
  });
}
