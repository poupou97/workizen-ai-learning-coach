/// TRACK B — Giá sách → Sách (bìa + Chương) → Chương (bài + trạng thái) →
/// Workspace; cuốn không có workspace giữ lối cũ; đường cũ vẫn mở được.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/workspace_catalog.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/features/lesson_workspace/book_screen.dart';
import 'package:learning_coach/features/lesson_workspace/chapter_screen.dart';
import 'package:learning_coach/features/lesson_workspace/widgets/fixture_chip.dart';
import 'package:learning_coach/features/lesson_workspace/workspace_trace.dart';
import 'package:learning_coach/features/subjects/book_shelf_screen.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';

import 'support.dart';

const _p = LearnerProfile(learnerId: 'na', displayName: 'Na', grade: 6);

LessonIndex _idx() => LessonIndex.fromJsonString('''
{"grade":6,"subjects":{"KHTN":[
  {"sourceDocumentId":"06-sgk-khoa-hoc-tu-nhien-6","volume":null,
   "lessons":[{"no":16,"title":"HỖN HỢP CÁC CHẤT","pageStart":56},
              {"no":17,"title":"TÁCH CHẤT KHỎI HỖN HỢP","pageStart":60},
              {"no":18,"title":"TẾ BÀO","pageStart":64},
              {"no":99,"title":"BÀI NGOÀI MỤC LỤC","pageStart":190}]}],
 "Toán":[{"sourceDocumentId":"06-sgk-toan-6-tap-mot","volume":"1",
   "lessons":[{"no":1,"title":"TẬP HỢP","pageStart":7}]}]},
 "toanExercises":{},
 "books":[
  {"sourceDocumentId":"06-sgk-khoa-hoc-tu-nhien-6","subject":"KHTN","grade":6,
   "title":"KHTN 6","cover":"covers/k.webp","lessonCount":4},
  {"sourceDocumentId":"06-sgk-toan-6-tap-mot","subject":"Toán","grade":6,
   "title":"Toán 6","volumeLabel":"Tập 1","volume":1,"cover":"covers/t.webp",
   "lessonCount":1}]}
''')!;

void main() {
  testWidgets(
    '⭐ giá sách: cuốn CÓ workspace mở BookScreen; cuốn khác giữ lối cũ',
    (t) async {
      BookRef? legacy;
      final catalog = WorkspaceCatalog.withDocs([loadSyntheticDoc()]);
      await t.pumpWidget(
        fixtureHost(
          BookShelfScreen(
            profile: _p,
            index: _idx(),
            catalog: catalog,
            trace: WorkspaceTrace(),
            onOpenBook: (b) => legacy = b,
          ),
        ),
      );
      await t.pumpAndSettle();
      expect(
        find.textContaining('✨ SAM'),
        findsOneWidget,
        reason: 'chỉ cuốn có workspace được đánh dấu',
      );
      await t.tap(find.text('Toán 6 · Tập 1'));
      await t.pumpAndSettle();
      expect(legacy?.sourceDocumentId, '06-sgk-toan-6-tap-mot');
      expect(find.byType(BookScreen), findsNothing);

      await t.tap(find.text('KHTN 6'));
      await t.pumpAndSettle();
      expect(find.byType(BookScreen), findsOneWidget);
      expect(find.text('Mục lục'), findsOneWidget);
      expect(find.byKey(FixtureChip.chipKey), findsOneWidget);
    },
  );

  testWidgets('BookScreen: chương từ mục lục in; bài ngoài mục lục vào «Bài '
      'khác»; đường cũ một chạm', (t) async {
    var legacyTaps = 0;
    final doc = loadSyntheticDoc();
    final idx = _idx();
    final lessons = idx.subjects['KHTN']!.first.lessons;
    await t.pumpWidget(
      fixtureHost(
        BookScreen(
          book: idx.bookById('06-sgk-khoa-hoc-tu-nhien-6')!,
          lessons: lessons,
          docs: [doc],
          trace: WorkspaceTrace(),
          onOpenLegacy: () => legacyTaps++,
        ),
      ),
    );
    await t.pumpAndSettle();
    expect(find.textContaining('Chương IV · Hỗn hợp'), findsOneWidget);
    expect(find.textContaining('bài · ✨ 1 bài học SAM'), findsOneWidget);
    // ROUND 3 B1/B5: dải số bài từ mục lục; tên chương OCR nói rõ nguồn.
    expect(find.textContaining('Bài 16–17 · '), findsOneWidget);
    // Fixture MẪU: chương không phải OCR ⇒ KHÔNG có chú thích (không nói
    // thừa); fixture THẬT (nếu có, ở test dưới) mới có.
    expect(find.textContaining('mục lục in của sách'), findsNothing);
    expect(find.textContaining('Bài khác'), findsOneWidget);
    expect(find.textContaining('✨ 1 bài học SAM: Bài 17'), findsOneWidget);
    await t.ensureVisible(find.text('Mục lục & hoạt động (bản hiện tại)'));
    await t.tap(find.text('Mục lục & hoạt động (bản hiện tại)'));
    expect(legacyTaps, 1);
  });

  testWidgets('⭐ Chương → bài có workspace mở Workspace; trạng thái «Chưa xem» '
      '→ «Đã xem (phiên này)»; bài không có ⇒ lối cũ', (t) async {
    var legacyTaps = 0;
    final doc = loadSyntheticDoc();
    final idx = _idx();
    final lessons = idx.subjects['KHTN']!.first.lessons;
    final trace = WorkspaceTrace();
    await t.pumpWidget(
      fixtureHost(
        ChapterScreen(
          book: idx.bookById('06-sgk-khoa-hoc-tu-nhien-6')!,
          chapter: doc.chapter!,
          lessons: [
            for (final l in lessons)
              if (doc.chapter!.contains(l.no)) l,
          ],
          docs: [doc],
          trace: trace,
          onOpenLegacy: () => legacyTaps++,
        ),
      ),
    );
    await t.pumpAndSettle();
    expect(find.textContaining('Bài 16 · Hỗn hợp'), findsOneWidget);
    expect(find.textContaining('Bài 17 · Tách chất'), findsOneWidget);
    expect(
      find.textContaining('Bài 18'),
      findsNothing,
      reason: 'chương chỉ hiện bài của chương',
    );
    expect(find.textContaining('Chưa xem'), findsOneWidget);
    expect(find.textContaining('Chưa có Bài học SAM'), findsOneWidget);

    await t.tap(find.textContaining('Bài 16 · Hỗn hợp'));
    expect(legacyTaps, 1);

    await t.tap(find.textContaining('Bài 17 · Tách chất'));
    await t.pumpAndSettle();
    // ROUND 3 B1: lần đầu ⇒ màn «Vào bài học», thẻ đề xuất mang lý do.
    expect(find.byKey(const Key('mode-picker')), findsOneWidget);
    expect(find.textContaining('SAM đề xuất cách này'), findsOneWidget);
    await t.tap(find.byTooltip('Về mục lục'));
    await t.pumpAndSettle();
    expect(find.textContaining('Đã xem (phiên này)'), findsOneWidget);
    expect(trace.opened(doc.slotKey), isTrue);
  });

  testWidgets('trạng thái bài không dùng sao/%/«đã học»', (t) async {
    final doc = loadSyntheticDoc();
    final idx = _idx();
    final trace = WorkspaceTrace()..markOpened(doc.slotKey);
    await t.pumpWidget(
      fixtureHost(
        ChapterScreen(
          book: idx.bookById('06-sgk-khoa-hoc-tu-nhien-6')!,
          chapter: doc.chapter!,
          lessons: idx.subjects['KHTN']!.first.lessons,
          docs: [doc],
          trace: trace,
          onOpenLegacy: () {},
        ),
      ),
    );
    await t.pumpAndSettle();
    for (final txt in find.byType(Text).evaluate()) {
      final s = (txt.widget as Text).data ?? '';
      expect(s, isNot(contains('%')));
      expect(s, isNot(contains('★')));
      expect(s.toLowerCase(), isNot(contains('đã học')));
    }
  });

  testWidgets('ROUND 3 B5 (O4): fixture THẬT — tên chương OCR có chú thích '
      '«mục lục in của sách (máy đọc, chưa soát)», chữ giữ nguyên văn', (
    t,
  ) async {
    final doc = loadRealDocOrSkip();
    if (doc == null) return;
    final idx = _idx();
    await t.pumpWidget(
      fixtureHost(
        BookScreen(
          book: idx.bookById('06-sgk-khoa-hoc-tu-nhien-6')!,
          lessons: idx.subjects['KHTN']!.first.lessons,
          docs: [doc],
          trace: WorkspaceTrace(),
          onOpenLegacy: () {},
        ),
      ),
    );
    await t.pumpAndSettle();
    expect(find.textContaining('mục lục in của sách'), findsOneWidget);
    // lỗi OCR của mục lục in KHÔNG bị sửa tay (chỉ đổi hoa/thường)
    await t.scrollUntilVisible(
      find.textContaining('Chương VI ·'),
      300,
      scrollable: find.byType(Scrollable).first,
    );
    expect(find.textContaining('Từ tề bào đền cơ thể'), findsOneWidget);
  });
}
