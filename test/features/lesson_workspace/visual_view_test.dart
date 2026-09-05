/// TRACK B — Trực quan: renderer trên dữ liệu có kiểu; tab chỉ cho hình dạng
/// có; nút chạm mở nguồn; bước withheld là chỗ trống thật.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/content_trust.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/features/lesson_workspace/visual_view.dart';

import 'support.dart';

void main() {
  testWidgets('tab: Sơ đồ quy trình + Bảng so sánh + Bảng tóm tắt; KHÔNG có '
      'Sơ đồ khái niệm / Dòng thời gian (bài không có dữ liệu)', (t) async {
    await t.pumpWidget(
      fixtureHost(
        Scaffold(
          body: VisualView(doc: loadSyntheticDoc(), onShowInRead: (_) {}),
        ),
      ),
    );
    await t.pumpAndSettle();
    expect(find.textContaining('Sơ đồ quy trình'), findsWidgets);
    expect(find.textContaining('Bảng so sánh'), findsOneWidget);
    expect(find.textContaining('Bảng tóm tắt'), findsOneWidget);
    expect(find.textContaining('Sơ đồ khái niệm'), findsNothing);
    expect(find.textContaining('Dòng thời gian'), findsNothing);
  });

  testWidgets('⭐ quy trình: 4 nút đúng thứ tự, bước 3 withheld là chỗ trống '
      'chỉ trang; «Vì sao SAM chọn» nêu luật', (t) async {
    await t.pumpWidget(
      fixtureHost(
        Scaffold(
          body: VisualView(doc: loadSyntheticDoc(), onShowInRead: (_) {}),
        ),
      ),
    );
    await t.pumpAndSettle();
    for (final n in ['1', '2', '3', '4']) {
      expect(find.text(n), findsWidgets);
    }
    expect(find.textContaining('Bước này SAM chưa đọc được'), findsOneWidget);
    expect(find.textContaining('Bước hai'), findsOneWidget);
    expect(find.text('Vì sao SAM chọn sơ đồ này'), findsOneWidget);
    expect(find.textContaining('luật: synthetic'), findsOneWidget);
  });

  testWidgets('chạm nút ⇒ sheet «Sách viết» + «Xem trong Đọc» trả đúng block', (
    t,
  ) async {
    String? shown;
    await t.pumpWidget(
      fixtureHost(
        Scaffold(
          body: VisualView(
            doc: loadSyntheticDoc(),
            onShowInRead: (id) => shown = id,
          ),
        ),
      ),
    );
    await t.pumpAndSettle();
    await t.tap(find.textContaining('Bước hai'));
    await t.pumpAndSettle();
    expect(find.text('Sách viết'), findsOneWidget);
    await t.tap(find.text('📖 Xem trong Đọc'));
    await t.pumpAndSettle();
    expect(shown, isNotNull);
    expect(shown, contains(':synthetic:'));
  });

  testWidgets('bảng so sánh: thực thể × chiều, chữ sách', (t) async {
    await t.pumpWidget(
      fixtureHost(
        Scaffold(
          body: VisualView(doc: loadSyntheticDoc(), onShowInRead: (_) {}),
        ),
      ),
    );
    await t.pumpAndSettle();
    await t.tap(find.textContaining('Bảng so sánh'));
    await t.pumpAndSettle();
    expect(find.text('Dùng để tách'), findsOneWidget);
    expect(find.text('Lọc (mẫu)'), findsOneWidget);
    expect(find.textContaining('hạt rắn không tan'), findsOneWidget);
  });

  testWidgets('bảng tóm tắt (fallback) = mục tiêu + «Em đã học» nguyên văn', (
    t,
  ) async {
    final d = loadSyntheticDoc();
    await t.pumpWidget(
      fixtureHost(
        Scaffold(
          body: VisualView(doc: d, onShowInRead: (_) {}),
        ),
      ),
    );
    await t.pumpAndSettle();
    await t.tap(find.textContaining('Bảng tóm tắt'));
    await t.pumpAndSettle();
    final blocks = VisualView.summaryBlocks(d);
    expect(blocks.whereType<ActivityBlock>().length, 1);
    expect(blocks.length, 3);
    expect(find.textContaining('Kể được vài cách'), findsOneWidget);
  });

  testWidgets('bài KHÔNG có dữ liệu ngữ nghĩa ⇒ SAM nói thật, vẫn có tóm tắt', (
    t,
  ) async {
    final d = loadSyntheticDoc();
    final empty = LessonDocument(
      schema: d.schema,
      book: d.book,
      bookTitle: d.bookTitle,
      subject: d.subject,
      grade: d.grade,
      lessonNo: d.lessonNo,
      title: d.title,
      provenance: d.provenance,
      blocks: d.blocks,
      evidencePolicy: EvidencePolicy.none,
    );
    await t.pumpWidget(
      fixtureHost(
        Scaffold(
          body: VisualView(doc: empty, onShowInRead: (_) {}),
        ),
      ),
    );
    await t.pumpAndSettle();
    expect(find.textContaining('SAM chưa có sơ đồ'), findsOneWidget);
    expect(find.textContaining('Bảng tóm tắt'), findsWidgets);
  });
}
