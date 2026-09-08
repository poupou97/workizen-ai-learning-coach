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
import 'package:learning_coach/core/pack/lesson_figure_store.dart';
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

const _withImg = '''
{"book": "$_book", "lesson": 17, "title": "Tách chất khỏi hỗn hợp",
 "pageStart": 60, "pagePdfStart": 61, "pagePdfEnd": 64,
 "text": "một hai ba",
 "content": [{"t":"text","v":"đoạn trước hình"},
             {"t":"img","id":"$_book:p061:img03","w":640,"h":936,"page":61,
              "caption":"Hình 17.1"},
             {"t":"text","v":"đoạn sau hình"}]}''';

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
  group('đọc đa phương thức', () {
    LessonPages pagesOf(String raw) =>
        (_idx(readings: raw).activitiesFor(book: _book, lessonNo: 17).single
            as LessonPagesActivity).pages;

    test('dòng đọc giữ ĐÚNG thứ tự chữ → hình → chữ', () {
      // Gom hết hình xuống cuối bài thì trẻ đọc xong mới thấy hình và không
      // biết hình nào nói về đoạn nào.
      final c = pagesOf(_withImg).content;
      expect(c.map((e) => e.runtimeType.toString()).toList(),
          ['ReadText', 'ReadImage', 'ReadText']);
      expect((c[1] as ReadImage).caption, 'Hình 17.1');
      expect((c[1] as ReadImage).aspect, closeTo(640 / 936, 1e-9));
    });

    test('chú thích rỗng ⇒ null, KHÔNG dựng chú thích thay sách', () {
      final raw = _withImg.replaceAll('"caption":"Hình 17.1"', '"caption":"  "');
      expect((pagesOf(raw).content[1] as ReadImage).caption, isNull);
    });

    test('mục hình hỏng bị BỎ, phần chữ vẫn còn', () {
      for (final bad in ['"w":640,"h":0', '"w":0,"h":936']) {
        final raw = _withImg.replaceAll('"w":640,"h":936', bad);
        final c = pagesOf(raw).content;
        expect(c.whereType<ReadImage>(), isEmpty, reason: bad);
        expect(c.whereType<ReadText>(), hasLength(2), reason: bad);
      }
    });

    test('bài chưa dựng hình ⇒ dòng đọc rơi về một khối chữ, không rỗng', () {
      // Thiếu hình không được làm hỏng cả bài — đọc là trạng thái hợp lệ.
      final p = pagesOf(_good);
      expect(p.content, isEmpty);
      expect(p.stream, hasLength(1));
      expect((p.stream.single as ReadText).text, contains('TÁCH CHẤT'));
    });

    testWidgets('pack lớp chưa có ảnh ⇒ không chừa ô trống câm', (t) async {
      await t.pumpWidget(MaterialApp(
          home: LessonPagesScreen(
              pages: pagesOf(_withImg),
              lessonLabel: 'Bài 17',
              figures: LessonFigureStore.empty())));
      expect(find.textContaining('đoạn trước hình'), findsOneWidget);
      expect(find.textContaining('đoạn sau hình'), findsOneWidget);
      expect(find.byType(Image), findsNothing);
      expect(find.textContaining('Hình 17.1'), findsNothing);
    });
  });

  // ── CẤU TRÚC ĐỌC ────────────────────────────────────────────────────────
  //
  // Nguồn có 215.714 khối chữ và 16.680 tiêu đề mục; trước đây pack ghi ra
  // 14.119 khối và 0 tiêu đề vì mọi khối liền nhau bị dính làm một.

  test('⭐ mục `heading` của pack thành ReadHeading, không thành đoạn thường', () {
    final lp = LessonPages.fromJson({
      'book': 'b',
      'lesson': 5,
      'pagePdfStart': 1,
      'pagePdfEnd': 1,
      'text': 'x',
      'content': [
        {'t': 'heading', 'v': 'I. MỞ ĐẦU'},
        {'t': 'text', 'v': 'Thân bài ở đây.'},
      ],
    });
    expect(lp, isNotNull);
    expect(lp!.content.length, 2);
    expect(lp.content[0], isA<ReadHeading>());
    expect((lp.content[0] as ReadHeading).text, 'I. MỞ ĐẦU');
    expect(lp.content[1], isA<ReadText>());
  });

  test('hai đoạn liền nhau giữ nguyên là HAI mục, không bị gộp khi đọc', () {
    final lp = LessonPages.fromJson({
      'book': 'b',
      'lesson': 5,
      'pagePdfStart': 1,
      'pagePdfEnd': 1,
      'text': 'x',
      'content': [
        {'t': 'text', 'v': 'Đoạn một.'},
        {'t': 'text', 'v': 'Đoạn hai.'},
      ],
    });
    expect(lp!.content.whereType<ReadText>().length, 2);
  });

  test('tiêu đề rỗng bị BỎ, không dựng mục câm', () {
    final lp = LessonPages.fromJson({
      'book': 'b',
      'lesson': 5,
      'pagePdfStart': 1,
      'pagePdfEnd': 1,
      'text': 'x',
      'content': [
        {'t': 'heading', 'v': '   '},
        {'t': 'text', 'v': 'Thân bài.'},
      ],
    });
    expect(lp!.content.length, 1);
    expect(lp.content.single, isA<ReadText>());
  });
}
