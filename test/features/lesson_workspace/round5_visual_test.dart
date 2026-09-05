/// ROUND 5 · Lane B — TRỰC QUAN THÀNH SƠ ĐỒ THẬT.
///
/// Founder §12: «Trực quan vẫn chưa tới khung concept … chỉ được cải thiện
/// bằng cấu trúc CÓ KIỂU, bám nguồn». Các test ở đây ghim đúng ba điều:
///  1. quy trình là NÚT + CẠNH + DÒNG CHẢY (không còn danh sách đánh số) và
///     mỗi nút vẫn mở được đúng block nguồn;
///  2. so sánh / sơ đồ khái niệm mở ra SƠ ĐỒ TƯ DUY — nút trung tâm + nhánh
///     màu — mà mọi chữ trong nút vẫn là chữ của dữ liệu có kiểu;
///  3. thứ gì KHÔNG có trong nguồn thì KHÔNG vẽ: chip hình chỉ hiện khi lời
///     sách nêu «Hình N.M» và có đúng MỘT chú thích mang nguyên văn chuỗi đó;
///     bài không có dữ liệu có kiểu thì nói thật, không bịa hình.
///
/// Màu trong sơ đồ là TRANG TRÍ (phân biệt nhánh) — nên nó phải đọc được:
/// mọi cặp nền/chữ của bảng màu bị kiểm tương phản WCAG ≥ 4.5:1 ở đây.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/content_trust.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/lesson_model/semantic_data.dart';
import 'package:learning_coach/features/lesson_workspace/views/mindmap_view.dart';
import 'package:learning_coach/features/lesson_workspace/views/process_flow_view.dart';
import 'package:learning_coach/features/lesson_workspace/visual_view.dart';

import 'support.dart';

double _contrast(Color a, Color b) {
  final la = a.computeLuminance(), lb = b.computeLuminance();
  final hi = la > lb ? la : lb, lo = la > lb ? lb : la;
  return (hi + 0.05) / (lo + 0.05);
}

LessonDocument _withSemantic(LessonDocument d, List<SemanticData> semantic) =>
    LessonDocument(
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

void main() {
  group('§1 quy trình = sơ đồ dòng chảy', () {
    testWidgets('⭐ nút + trục + dải tổng quan; mỗi nút mở đúng block nguồn; '
        'bước bị giữ lại là nút RỖNG nói thật', (t) async {
      String? shown;
      final d = loadSyntheticDoc();
      await t.pumpWidget(
        fixtureHost(
          Scaffold(
            body: VisualView(doc: d, onShowInRead: (id) => shown = id),
          ),
        ),
      );
      await t.pumpAndSettle();
      expect(find.byKey(ProcessFlowView.flowKey), findsOneWidget);
      expect(find.byKey(ProcessFlowView.railKey), findsOneWidget);
      final proc = d.semantic.whereType<ProcessSemantic>().first;
      for (final st in proc.steps) {
        expect(
          find.byKey(ProcessFlowView.stepKey(st.order)),
          findsOneWidget,
          reason: 'bước ${st.order} phải là MỘT nút chạm được',
        );
      }
      // các nút xếp theo thứ tự sách, trên xuống dưới
      var last = -1.0;
      for (final st in proc.steps) {
        final y = t
            .getTopLeft(find.byKey(ProcessFlowView.stepKey(st.order)))
            .dy;
        expect(y, greaterThan(last));
        last = y;
      }
      expect(find.textContaining('Bước này SAM chưa đọc được'), findsOneWidget);
      await t.tap(find.byKey(ProcessFlowView.stepKey(2)));
      await t.pumpAndSettle();
      expect(find.text('Sách viết'), findsOneWidget);
      await t.tap(find.text('📖 Xem trong Đọc'));
      await t.pumpAndSettle();
      expect(shown, proc.steps[1].sourceBlockId);
    });

    testWidgets('dải tổng quan chạm được ⇒ mở nguồn của đúng bước đó', (
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
      // số «1» đầu tiên trong dải tổng quan
      final rail = find.descendant(
        of: find.byKey(ProcessFlowView.railKey),
        matching: find.text('1'),
      );
      expect(rail, findsOneWidget);
      await t.tap(rail);
      await t.pumpAndSettle();
      expect(find.text('Sách viết'), findsOneWidget);
    });
  });

  group('§2 chip hình — chỉ khi CHÍNH lời sách chỉ tới, khớp nguyên văn', () {
    test('không có «Hình N.M» trong lời sách ⇒ không chip', () {
      final d = loadSyntheticDoc();
      final proc = d.semantic.whereType<ProcessSemantic>().first;
      for (final st in proc.steps) {
        expect(ProcessFlowView.figureRefIn(d, st), isNull);
      }
    });

    test('bước bị giữ lại (không có chữ) ⇒ không chip', () {
      final d = loadSyntheticDoc();
      final withheld = d.semantic
          .whereType<ProcessSemantic>()
          .first
          .steps
          .firstWhere((s) => s.isWithheld);
      expect(ProcessFlowView.figureRefIn(d, withheld), isNull);
    });

    test('⭐⭐ fixture THẬT: «(Hình 17.3)» có ĐÚNG MỘT chú thích khớp ⇒ chip '
        'trỏ tới chính block đó; «Hình 17.4» không có ⇒ KHÔNG chip', () {
      final d = loadRealDocOrSkip();
      if (d == null) return;
      final proc = d.semantic.whereType<ProcessSemantic>().firstWhere(
        (p) => p.steps.any((s) => (s.text ?? '').contains('Hình 17.3')),
      );
      final withFig = proc.steps.firstWhere(
        (s) => (s.text ?? '').contains('Hình 17.3'),
      );
      final ref = ProcessFlowView.figureRefIn(d, withFig);
      expect(ref, isNotNull);
      expect(ref!.label, 'Hình 17.3');
      final target = d.blockById(ref.blockId);
      expect(target, isA<CaptionBlock>());
      expect((target! as CaptionBlock).text.trim(), 'Hình 17.3');

      final noFig = proc.steps.firstWhere(
        (s) => (s.text ?? '').contains('Hình 17.4'),
      );
      expect(
        ProcessFlowView.figureRefIn(d, noFig),
        isNull,
        reason:
            'sách chỉ tới Hình 17.4 nhưng tài liệu không có chú thích '
            'nguyên văn ấy ⇒ fail closed, không đoán hình nào',
      );
    });

    testWidgets('⭐⭐ fixture THẬT: chip hiện trên nút và nhảy về Đọc đúng chỗ', (
      t,
    ) async {
      final d = loadRealDocOrSkip();
      if (d == null) return;
      String? shown;
      await t.pumpWidget(
        fixtureHost(
          Scaffold(
            body: VisualView(doc: d, onShowInRead: (id) => shown = id),
          ),
        ),
      );
      await t.pumpAndSettle();
      final proc = d.semantic.whereType<ProcessSemantic>().first;
      final st = proc.steps.firstWhere(
        (s) => ProcessFlowView.figureRefIn(d, s) != null,
      );
      final chip = find.byKey(ProcessFlowView.figureKey(st.order));
      await t.ensureVisible(chip);
      expect(find.textContaining('Sách chỉ tới Hình 17.3'), findsOneWidget);
      await t.tap(chip);
      await t.pumpAndSettle();
      expect(shown, ProcessFlowView.figureRefIn(d, st)!.blockId);
    });
  });

  group('§3 sơ đồ tư duy', () {
    testWidgets('⭐ 4 nút ⇒ bố cục khung concept: 2 nút TRÊN nút trung tâm, '
        '2 nút DƯỚI', (t) async {
      final d = loadSyntheticDoc();
      final src = d.blocks.whereType<ParagraphBlock>().first.id;
      final cmp = ComparisonSemantic(
        id: 'cmp-4',
        title: 'Các cách tách chất (mẫu)',
        trust: ContentTrust.fixtureSynthetic,
        derivation: 'synthetic-test',
        entities: [
          for (final n in ['Lọc', 'Lắng', 'Cô cạn', 'Chiết'])
            ComparisonEntity(name: n, sourceBlockId: src),
        ],
        dimensions: const [
          ComparisonDimension(
            name: 'Dùng để tách',
            values: ['một', 'hai', 'ba', null],
          ),
        ],
      );
      await t.pumpWidget(
        fixtureHost(
          Scaffold(
            body: VisualView(
              doc: _withSemantic(d, [cmp]),
              onShowInRead: (_) {},
            ),
          ),
        ),
      );
      await t.pumpAndSettle();
      final hubY = t.getCenter(find.byKey(MindmapView.hubKey)).dy;
      expect(
        t.getCenter(find.byKey(MindmapView.nodeKey(0))).dy,
        lessThan(hubY),
      );
      expect(
        t.getCenter(find.byKey(MindmapView.nodeKey(1))).dy,
        lessThan(hubY),
      );
      expect(
        t.getCenter(find.byKey(MindmapView.nodeKey(2))).dy,
        greaterThan(hubY),
      );
      expect(
        t.getCenter(find.byKey(MindmapView.nodeKey(3))).dy,
        greaterThan(hubY),
      );
      // hai nút cùng hàng nằm hai cột
      expect(
        t.getCenter(find.byKey(MindmapView.nodeKey(0))).dx,
        lessThan(t.getCenter(find.byKey(MindmapView.nodeKey(1))).dx),
      );
      // sách KHÔNG nói ở ô thứ tư ⇒ để trống, không điền hộ
      expect(find.text('— (sách không nói)'), findsOneWidget);
    });

    testWidgets('nhiều hơn 4 nút ⇒ bố cục cây, mọi nút vẫn còn và chạm được', (
      t,
    ) async {
      final d = loadSyntheticDoc();
      final src = d.blocks.whereType<ParagraphBlock>().first.id;
      final names = ['Một', 'Hai', 'Ba', 'Bốn', 'Năm', 'Sáu'];
      final cmp = ComparisonSemantic(
        id: 'cmp-6',
        title: 'Sáu cách (mẫu)',
        trust: ContentTrust.fixtureSynthetic,
        derivation: 'synthetic-test',
        entities: [
          for (final n in names) ComparisonEntity(name: n, sourceBlockId: src),
        ],
        dimensions: [
          ComparisonDimension(
            name: 'Chiều',
            values: [for (final _ in names) 'x'],
          ),
        ],
      );
      await t.pumpWidget(
        fixtureHost(
          Scaffold(
            body: VisualView(
              doc: _withSemantic(d, [cmp]),
              onShowInRead: (_) {},
            ),
          ),
        ),
      );
      await t.pumpAndSettle();
      for (var i = 0; i < names.length; i++) {
        expect(find.byKey(MindmapView.nodeKey(i)), findsOneWidget);
      }
      await t.ensureVisible(find.byKey(MindmapView.nodeKey(4)));
      await t.pumpAndSettle();
      await t.tap(find.byKey(MindmapView.nodeKey(4)));
      await t.pumpAndSettle();
      expect(find.text('Sách viết'), findsOneWidget);
    });

    testWidgets('>2 chiều so sánh ⇒ CHỈ bảng (fail closed, không nhồi nút)', (
      t,
    ) async {
      final d = loadSyntheticDoc();
      final src = d.blocks.whereType<ParagraphBlock>().first.id;
      final cmp = ComparisonSemantic(
        id: 'cmp-3d',
        title: 'Ba chiều (mẫu)',
        trust: ContentTrust.fixtureSynthetic,
        derivation: 'synthetic-test',
        entities: [
          ComparisonEntity(name: 'A', sourceBlockId: src),
          ComparisonEntity(name: 'B', sourceBlockId: src),
        ],
        dimensions: const [
          ComparisonDimension(name: 'c1', values: ['1', '2']),
          ComparisonDimension(name: 'c2', values: ['1', '2']),
          ComparisonDimension(name: 'c3', values: ['1', '2']),
        ],
      );
      expect(VisualView.mindmapFits(cmp), isFalse);
      await t.pumpWidget(
        fixtureHost(
          Scaffold(
            body: VisualView(
              doc: _withSemantic(d, [cmp]),
              onShowInRead: (_) {},
            ),
          ),
        ),
      );
      await t.pumpAndSettle();
      expect(find.byKey(MindmapView.viewKey), findsNothing);
      expect(find.byKey(VisualView.comparisonViewKey('mindmap')), findsNothing);
      expect(find.text('c3'), findsOneWidget);
    });
  });

  group('§4 màu là trang trí — nên phải đọc được', () {
    test('⭐ mọi cặp nền/chữ của bảng màu nhánh đạt WCAG AA ≥ 4.5:1', () {
      for (var i = 0; i < MindmapPalette.branches.length; i++) {
        final b = MindmapPalette.branches[i];
        expect(
          _contrast(b.bg, b.fg),
          greaterThanOrEqualTo(4.5),
          reason: 'nhánh $i: nền ${b.bg} + chữ ${b.fg} không đọc được',
        );
      }
    });

    test('bảng màu quay vòng ⇒ nút thứ n luôn ra CÙNG màu (kiểm lại được)', () {
      expect(MindmapPalette.at(0), same(MindmapPalette.branches[0]));
      expect(MindmapPalette.at(4), same(MindmapPalette.branches[0]));
      expect(MindmapPalette.at(5), same(MindmapPalette.branches[1]));
    });
  });

  group('§5 fail closed', () {
    testWidgets(
      'không có dữ liệu có kiểu ⇒ KHÔNG có sơ đồ nào, SAM nói vì sao',
      (t) async {
        final d = loadSyntheticDoc();
        await t.pumpWidget(
          fixtureHost(
            Scaffold(
              body: VisualView(
                doc: _withSemantic(d, const []),
                onShowInRead: (_) {},
              ),
            ),
          ),
        );
        await t.pumpAndSettle();
        expect(find.byKey(MindmapView.viewKey), findsNothing);
        expect(find.byKey(ProcessFlowView.flowKey), findsNothing);
        expect(
          find.textContaining('SAM chưa có sơ đồ cho bài này'),
          findsWidgets,
        );
        expect(find.textContaining('SAM không tự vẽ'), findsOneWidget);
      },
    );
  });
}
