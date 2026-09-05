/// ROUND 4 (Lane B §6) — những gì đổi trên màn, ghim bằng test:
///   §6.3 Smart Book: đoạn văn là chữ liền (không thẻ); hình + chú thích liền
///        kề thành MỘT khối; dòng nguồn cuối bài không mang mã pipeline; thẻ
///        để trống có «Vì sao SAM để trống?» bằng lời trẻ.
///   §6.3/6.10 sheet «Sách viết» = tra cứu: dòng «Tra cứu · SGK … · Bài N ·
///        trang», «Trong mục: …» từ đường heading, mã máy sau nếp gấp.
///   §6.4 sheet «Nguồn & độ tin»: lời trẻ + «Dành cho bố mẹ» + nếp gấp.
///   §6.5 Trực quan: chú giải + chạm để tra cứu; fail-closed nói vì sao.
///   §6.6 Học với SAM: dòng runtime lời trẻ, chú giải nhãn, thang gợi ý.
///   §6.7 thẻ «SAM đề xuất» hiện ba cách và cách nào đã mở (trace).
///   §6.8 che mép ảnh (display-side) — ảnh gốc vẫn ở sheet.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/lesson_model/next_action.dart';
import 'package:learning_coach/features/lesson_workspace/lesson_workspace_screen.dart';
import 'package:learning_coach/features/lesson_workspace/smart_book_view.dart';
import 'package:learning_coach/features/lesson_workspace/tutor_view.dart';
import 'package:learning_coach/features/lesson_workspace/visual_view.dart';
import 'package:learning_coach/features/lesson_workspace/widgets/source_sheet.dart';
import 'package:learning_coach/features/lesson_workspace/widgets/tech_details.dart';
import 'package:learning_coach/features/lesson_workspace/widgets/withheld_card.dart';
import 'package:learning_coach/features/lesson_workspace/workspace_trace.dart';

import 'support.dart';

Widget _book(LessonDocument d) => fixtureHost(
  Scaffold(
    body: SmartBookView(
      doc: d,
      fontStep: 0,
      onFontStep: (_) {},
      onAskSam: (_) {},
    ),
  ),
);

void main() {
  group('§6.3 Smart Book', () {
    testWidgets('đoạn văn là chữ liền — KHÔNG nằm trong thẻ trắng; câu hỏi '
        'vẫn là thẻ', (t) async {
      final d = loadSyntheticDoc();
      await t.pumpWidget(_book(d));
      await t.pumpAndSettle();
      final para = find.textContaining('[MẪU] Các chất').first;
      // tổ tiên gần nhất là Padding rồi InkWell — không có Container nền trắng
      final ancestors = para.evaluate().single.debugGetDiagnosticChain();
      final container = ancestors
          .map((e) => e.widget)
          .whereType<Container>()
          .where((c) => (c.decoration as BoxDecoration?)?.color == Colors.white)
          .take(1)
          .toList();
      expect(container, isEmpty, reason: 'đoạn văn không đóng thẻ');
      expect(find.text('❓'), findsWidgets, reason: 'câu hỏi vẫn là thẻ');
    });

    testWidgets('hình + chú thích liền kề = MỘT khối; dòng nguồn có «chạm '
        'hình để xem ảnh gốc»; ảnh được phóng che mép', (t) async {
      final d = loadSyntheticDoc();
      await t.pumpWidget(_book(d));
      await t.pumpAndSettle();
      final firstImage = d.blocks.whereType<ImageBlock>().first;
      final fig = find.byKey(SmartBookView.figureKey(firstImage.id));
      expect(fig, findsOneWidget);
      expect(
        find.descendant(of: fig, matching: find.textContaining('Hình 1.')),
        findsOneWidget,
        reason: 'chú thích nằm TRONG khối hình',
      );
      expect(
        find.descendant(
          of: fig,
          matching: find.textContaining('chạm hình để xem ảnh gốc'),
        ),
        findsOneWidget,
      );
      final scale = t.widget<Transform>(
        find.descendant(of: fig, matching: find.byType(Transform)).first,
      );
      expect(scale.transform.storage[0], closeTo(SmartBookView.bleedScale, 1e-6));
    });

    test('dòng nguồn cuối bài: mã pipeline rời chữ trẻ đọc (chỉ khi tài liệu '
        'khai pipelineVersion); tài liệu mẫu giữ nguyên', () {
      final syn = loadSyntheticDoc();
      final srcSyn = syn.blocks.whereType<SourceRefBlock>().first.text;
      expect(SmartBookView.childSourceRefText(syn, srcSyn), srcSyn);
      final real = loadRealDocOrSkip();
      if (real == null) return;
      final src = real.blocks.whereType<SourceRefBlock>().first.text;
      final out = SmartBookView.childSourceRefText(real, src);
      expect(out, 'SGK KHTN 6 · trang 60–63');
      expect(out, isNot(contains('tc2')));
    });

    testWidgets('thẻ để trống: «Vì sao SAM để trống?» mở lời trẻ; không mã '
        'máy; ảnh trang gọi là «ảnh chụp trang sách»', (t) async {
      final d = loadSyntheticDoc();
      await t.pumpWidget(_book(d));
      await t.pumpAndSettle();
      await t.ensureVisible(find.byKey(WithheldCard.whyKey).first);
      expect(find.textContaining('số hoặc công thức'), findsNothing);
      await t.tap(find.byKey(WithheldCard.whyKey).first);
      await t.pumpAndSettle();
      expect(find.textContaining('số hoặc công thức'), findsOneWidget);
      expect(find.textContaining('math_guard'), findsNothing);
      expect(find.textContaining('nội bộ'), findsNothing);
      expect(find.text('Xem ảnh chụp trang sách'), findsWidgets);
      expect(withheldWhyForChild('page_feature:diagram'), contains('sơ đồ'));
      expect(withheldWhyForChild('unknown_role:footnote'), contains('không đoán'));
      expect(withheldWhyForChild('x'), contains('không đoán'));
    });
  });

  group('§6.3/6.10 sheet «Sách viết» = tra cứu', () {
    testWidgets('dòng tra cứu + «Trong mục» từ đường heading + mã máy sau '
        'nếp gấp (fixture thật, nếu có)', (t) async {
      final d = loadRealDocOrSkip();
      if (d == null) return;
      final para = d.blocks
          .whereType<ParagraphBlock>()
          .firstWhere((b) => b.relations.headingPath.length >= 3);
      expect(sectionLineFor(d, para), 'Trong mục: Nguyên tắc tách chất');
      expect(lookupLineFor(d, para), '📖 Tra cứu · SGK KHTN 6 · Bài 17 · trang 60');
      await t.pumpWidget(
        fixtureHost(
          Scaffold(
            body: Builder(
              builder: (ctx) => TextButton(
                onPressed: () => showSourceSheet(ctx, doc: d, block: para),
                child: const Text('open'),
              ),
            ),
          ),
        ),
      );
      await t.tap(find.text('open'));
      await t.pumpAndSettle();
      expect(find.byKey(const Key('source-lookup-line')), findsOneWidget);
      expect(find.byKey(const Key('source-section-line')), findsOneWidget);
      expect(find.textContaining('tc2-p1'), findsNothing, reason: 'nếp gấp đóng');
      await t.ensureVisible(find.byKey(TechDetails.foldKey));
      await t.tap(find.byKey(TechDetails.foldKey));
      await t.pumpAndSettle();
      expect(find.textContaining('Mã phần: '), findsOneWidget);
      expect(find.textContaining('tc2-p1'), findsWidgets);
    });

    test('không có đường heading ⇒ không bịa mục (fixture mẫu)', () {
      final d = loadSyntheticDoc();
      for (final b in d.blocks) {
        expect(sectionLineFor(d, b), isNull);
      }
    });
  });

  group('§6.4 sheet «Nguồn & độ tin»', () {
    testWidgets('lời trẻ giải nghĩa «chưa kiểm định» + «Dành cho bố mẹ» + '
        'sáu bất đẳng thức; mã máy sau nếp gấp (fixture thật, nếu có)', (
      t,
    ) async {
      final d = loadRealDocOrSkip();
      if (d == null) return;
      await t.pumpWidget(
        fixtureHost(LessonWorkspaceScreen(doc: d, trace: WorkspaceTrace())),
      );
      await t.pumpAndSettle();
      await t.tap(find.byKey(const Key('fixture-chip-tap')));
      await t.pumpAndSettle();
      expect(find.textContaining('«Chưa kiểm định» nghĩa là'), findsOneWidget);
      expect(find.textContaining('mở sách giấy ra so'), findsOneWidget);
      expect(find.textContaining('Dành cho bố mẹ'), findsOneWidget);
      expect(find.textContaining('chưa có giấy phép phát hành'), findsOneWidget);
      expect(find.textContaining('TAP ≠ COMPETENCE'), findsOneWidget);
      for (final s in ['tc2-p1', 'tsl-', 'HINT_UNSOURCED', '.py']) {
        expect(find.textContaining(s), findsNothing, reason: '$s lộ khi gấp');
      }
      await t.ensureVisible(find.byKey(TechDetails.foldKey));
      await t.tap(find.byKey(TechDetails.foldKey));
      await t.pumpAndSettle();
      expect(find.textContaining('tsl-enumerated-steps-v1'), findsWidgets);
      expect(find.textContaining('HINT_UNSOURCED'), findsOneWidget);
    });
  });

  group('§6.5 Trực quan', () {
    testWidgets('chú giải số tím/xám + «chạm để tra cứu»; bảng so sánh có '
        'hướng dẫn; link «Nguồn & độ tin»', (t) async {
      final d = loadSyntheticDoc();
      await t.pumpWidget(
        fixtureHost(Scaffold(body: VisualView(doc: d, onShowInRead: (_) {}))),
      );
      await t.pumpAndSettle();
      final legend = t.widget<Text>(find.byKey(const Key('visual-legend')));
      expect(legend.data, contains('số xám = bước SAM để trống'));
      expect(legend.data, contains('chạm một bước'));
      expect(find.byIcon(Icons.menu_book_outlined), findsWidgets);
      expect(find.text('ⓘ Nguồn & độ tin'), findsOneWidget);
      await t.tap(find.byKey(VisualView.shapeKey('Bảng so sánh')));
      await t.pumpAndSettle();
      expect(find.textContaining('chạm một hàng'), findsOneWidget);
    });
  });

  group('§6.6 Học với SAM', () {
    testWidgets('dòng runtime lời trẻ, chú giải nhãn, thang gợi ý 1·2 tô '
        'theo bậc đã dùng, hết thang nói SAM chỉ chỗ trong sách', (t) async {
      await t.pumpWidget(
        fixtureHost(
          Scaffold(body: TutorView(doc: loadSyntheticDoc(), onNext: (_, _) {})),
        ),
      );
      await t.pumpAndSettle();
      final line = t.widget<Text>(find.byKey(const Key('tutor-runtime-line')));
      expect(line.data, contains('lời lấy đúng trong sách'));
      expect(line.data, isNot(contains('Runtime')));
      expect(find.text(TutorView.labelLegend), findsOneWidget);
      await t.tap(find.text('Tiếp ▸'));
      await t.pumpAndSettle();
      expect(find.byKey(const Key('tutor-hint-ladder')), findsOneWidget);
      expect(find.text('Bậc gợi ý'), findsOneWidget);
      await t.tap(find.textContaining('Gợi ý cho tớ'));
      await t.pumpAndSettle();
      expect(find.text('Gợi ý 1/2'), findsOneWidget);
      await t.tap(find.textContaining('Gợi ý cho tớ'));
      await t.pumpAndSettle();
      expect(find.text('Gợi ý 2/2'), findsOneWidget);
      expect(find.textContaining('SAM sẽ chỉ chỗ trong sách'), findsOneWidget);
    });

    test('runtimeLineTechnical giữ mã máy cho nếp gấp', () {
      final d = loadSyntheticDoc();
      final r = TutorView.runtimeLineTechnical(
        // planForDoc qua widgets/runtime_plan — dùng lại qua trust sheet test;
        // ở đây chỉ kiểm dạng chuỗi với null.
        null,
      );
      expect(r, 'no tutor script');
      expect(d.tutorScript, isNotNull);
    });
  });

  group('§6.7 thẻ «SAM đề xuất»', () {
    testWidgets('hàng «Đã mở» ● / ○ theo trace của phiên', (t) async {
      // Màn dọc (Nokia): ở màn ngang thẻ đề xuất là chế độ gọn, không có hàng.
      t.view.physicalSize = const Size(1080, 1920);
      t.view.devicePixelRatio = 2.75;
      addTearDown(t.view.reset);
      final trace = WorkspaceTrace();
      final doc = loadSyntheticDoc();
      await t.pumpWidget(
        fixtureHost(
          LessonWorkspaceScreen(
            doc: doc,
            trace: trace,
            initialView: WorkspaceView.read,
          ),
        ),
      );
      await t.pumpAndSettle();
      final row = t.widget<Text>(find.byKey(const Key('workspace-seen-row')));
      expect(row.data, 'Đã mở: ● Đọc ○ Trực quan ○ Học với SAM');
      await t.tap(find.byKey(LessonWorkspaceScreen.tabKey(WorkspaceView.visual)));
      await t.pumpAndSettle();
      final row2 = t.widget<Text>(find.byKey(const Key('workspace-seen-row')));
      expect(row2.data, 'Đã mở: ● Đọc ● Trực quan ○ Học với SAM');
    });
  });
}
