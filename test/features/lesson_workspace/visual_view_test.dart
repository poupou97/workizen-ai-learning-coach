/// TRACK B — Trực quan: renderer trên dữ liệu có kiểu; tab chỉ cho hình dạng
/// có; nút chạm mở nguồn; bước withheld là chỗ trống thật.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/content_trust.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/lesson_model/semantic_data.dart';
import 'package:learning_coach/features/lesson_workspace/visual_view.dart';
import 'package:learning_coach/features/lesson_workspace/widgets/tech_details.dart';

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
    // ROUND 3 B5: mã luật rời màn trẻ đọc — nằm trong sheet «Nguồn & luật xếp».
    expect(find.textContaining('luật: synthetic'), findsNothing);
    expect(find.textContaining('synthetic'), findsNothing);
    await t.ensureVisible(find.byKey(const Key('visual-trust-link')));
    await t.tap(find.byKey(const Key('visual-trust-link')));
    await t.pumpAndSettle();
    expect(find.byKey(const Key('trust-sheet')), findsOneWidget);
    // ROUND 4: mã luật sau nếp gấp kỹ thuật (đóng mặc định).
    expect(find.textContaining('luật synthetic'), findsNothing);
    await t.ensureVisible(find.byKey(TechDetails.foldKey));
    await t.tap(find.byKey(TechDetails.foldKey));
    await t.pumpAndSettle();
    expect(find.textContaining('luật synthetic'), findsWidgets);
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

  LessonDocument withSemantic(List<SemanticData> semantic) {
    final d = loadSyntheticDoc();
    return LessonDocument(
      schema: d.schema,
      book: d.book,
      bookTitle: d.bookTitle,
      subject: d.subject,
      grade: d.grade,
      lessonNo: d.lessonNo,
      title: d.title,
      provenance: d.provenance,
      blocks: d.blocks,
      semantic: semantic,
      evidencePolicy: EvidencePolicy.none,
    );
  }

  testWidgets('ROUND 3 B3: hai sơ đồ cùng hình dạng ⇒ MỘT tab hình dạng + hàng '
      'chọn «1 · …» «2 · …»; dải tổng quan 1→2→3', (t) async {
    final d = loadSyntheticDoc();
    final proc = d.semantic.whereType<ProcessSemantic>().first;
    final second = ProcessSemantic(
      id: 'process-2',
      title: 'Quy trình thứ hai (mẫu)',
      trust: proc.trust,
      derivation: proc.derivation,
      steps: [proc.steps.first, proc.steps[1]],
    );
    final doc = withSemantic([proc, second, ...d.semantic.skip(1)]);
    await t.pumpWidget(
      fixtureHost(Scaffold(body: VisualView(doc: doc, onShowInRead: (_) {}))),
    );
    await t.pumpAndSettle();
    expect(find.byKey(VisualView.shapeKey('Sơ đồ quy trình')), findsOneWidget);
    expect(find.byKey(VisualView.instanceKey('process-2')), findsOneWidget);
    expect(find.byKey(const Key('visual-process-strip')), findsOneWidget);
    await t.tap(find.byKey(VisualView.instanceKey('process-2')));
    await t.pumpAndSettle();
    expect(find.text('Quy trình thứ hai (mẫu)'), findsOneWidget);
    expect(find.textContaining('2 bước'), findsOneWidget);
  });

  testWidgets('ROUND 3 B3: ConceptRelation[] ⇒ sơ đồ khái niệm: nút trung tâm '
      'tất định (gặp nhiều nhất), nan hoa có nhãn, nút chạm mở nguồn', (
    t,
  ) async {
    final d = loadSyntheticDoc();
    final src = d.blocks.whereType<ParagraphBlock>().first.id;
    final map = ConceptMapSemantic(
      id: 'cm-1',
      title: 'Hỗn hợp (mẫu)',
      trust: ContentTrust.fixtureSynthetic,
      derivation: 'synthetic-test',
      relations: [
        ConceptRelation(a: 'Hỗn hợp', relation: 'tách bằng', b: 'Lọc', sourceBlockId: src),
        ConceptRelation(a: 'Hỗn hợp', relation: 'tách bằng', b: 'Cô cạn', sourceBlockId: src),
        ConceptRelation(a: 'Chiết', relation: 'dùng cho', b: 'Hỗn hợp', sourceBlockId: src),
        ConceptRelation(a: 'Lọc', relation: 'cần', b: 'Giấy lọc', sourceBlockId: src),
      ],
    );
    expect(VisualView.hubOf(map), 'Hỗn hợp');
    String? shown;
    await t.pumpWidget(
      fixtureHost(
        Scaffold(
          body: VisualView(
            doc: withSemantic([map]),
            onShowInRead: (id) => shown = id,
          ),
        ),
      ),
    );
    await t.pumpAndSettle();
    expect(find.byKey(VisualView.shapeKey('Sơ đồ khái niệm')), findsOneWidget);
    expect(find.byKey(const Key('visual-concept-map')), findsOneWidget);
    expect(find.text('Hỗn hợp'), findsOneWidget, reason: 'nút trung tâm');
    for (final leaf in ['Lọc', 'Cô cạn', 'Chiết']) {
      expect(find.text(leaf), findsOneWidget);
    }
    expect(find.text('tách bằng'), findsNWidgets(2));
    // quan hệ không chạm nút trung tâm ⇒ thẻ bên dưới, không bị bỏ
    expect(find.textContaining('Giấy lọc'), findsOneWidget);
    expect(find.textContaining('4 quan hệ'), findsOneWidget);
    await t.tap(find.text('Cô cạn'));
    await t.pumpAndSettle();
    expect(find.text('Sách viết'), findsOneWidget);
    await t.tap(find.text('📖 Xem trong Đọc'));
    await t.pumpAndSettle();
    expect(shown, src);
  });

  testWidgets('ROUND 3 B3: TimelineEvent[] ⇒ dòng thời gian theo thứ tự dữ '
      'liệu, mốc + tiêu đề + chữ, chạm mở nguồn', (t) async {
    final d = loadSyntheticDoc();
    final src = d.blocks.whereType<ParagraphBlock>().first.id;
    final tl = TimelineSemantic(
      id: 'tl-1',
      title: 'Mốc (mẫu)',
      trust: ContentTrust.fixtureSynthetic,
      derivation: 'synthetic-test',
      events: [
        TimelineEvent(when: 'Bước đầu', title: 'Khuấy (mẫu)', sourceBlockId: src),
        TimelineEvent(
          when: 'Sau đó',
          title: 'Lọc (mẫu)',
          text: '[MẪU] đổ qua giấy lọc',
          sourceBlockId: src,
        ),
      ],
    );
    await t.pumpWidget(
      fixtureHost(
        Scaffold(
          body: VisualView(doc: withSemantic([tl]), onShowInRead: (_) {}),
        ),
      ),
    );
    await t.pumpAndSettle();
    expect(find.byKey(VisualView.shapeKey('Dòng thời gian')), findsOneWidget);
    expect(find.byKey(const Key('visual-timeline')), findsOneWidget);
    final y0 = t.getTopLeft(find.text('Bước đầu')).dy;
    final y1 = t.getTopLeft(find.text('Sau đó')).dy;
    expect(y1, greaterThan(y0));
    expect(find.textContaining('2 mốc'), findsOneWidget);
    expect(find.textContaining('[MẪU] đổ qua giấy lọc'), findsOneWidget);
    await t.tap(find.text('Lọc (mẫu)'));
    await t.pumpAndSettle();
    expect(find.text('Sách viết'), findsOneWidget);
  });
}
