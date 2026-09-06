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

import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/content_trust.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/lesson_model/next_action.dart';
import 'package:learning_coach/core/lesson_model/semantic_data.dart';
import 'package:learning_coach/features/lesson_workspace/lesson_workspace_screen.dart';
import 'package:learning_coach/features/lesson_workspace/views/mindmap_view.dart';
import 'package:learning_coach/features/lesson_workspace/views/process_flow_view.dart';
import 'package:learning_coach/features/lesson_workspace/tutor_view.dart';
import 'package:learning_coach/features/lesson_workspace/visual_view.dart';
import 'package:learning_coach/features/lesson_workspace/widgets/assist_layer.dart';
import 'package:learning_coach/features/lesson_workspace/workspace_trace.dart';

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

/// Dựng `ComparisonSemantic` cho test QUA ĐƯỜNG JSON, không qua hàm dựng Dart.
///
/// ⭐ Lý do, không phải tiện tay: lane E2 (§8) đổi `ComparisonDimension` từ
/// `values: List<String?>` trần sang `cells: List<ComparisonValue>` để **không
/// ô nào lên màn mà không lần được về một block sách**. Hàm dựng Dart vì thế
/// đổi chữ ký; ĐƯỜNG JSON thì không — nó vẫn nhận `values` là chuỗi hoặc
/// `null`, và ở hợp đồng mới mỗi ô **thừa kế nguồn của chính hàng đó**
/// (`ValueGrounding.inheritedFromEntity`) — thừa kế là sự thật kiểm được, vì
/// hàng ấy sinh ra từ đúng block đó.
///
/// Nên test này đi qua **cùng bộ phân tích mà fixture thật đi qua** thay vì
/// dựng đối tượng bằng tay, và nó biên dịch được với cả hợp đồng cũ lẫn mới.
/// KHÔNG thêm hàm tiện dụng nào vào `lib/core`: một `fromStrings(...)` ở đó sẽ
/// mở lại đúng cái lỗ E2 vừa bịt (làm cho ô không nguồn dựng được).
/// `null` trong `values` = **sách không nói** — ô để trống, không điền hộ.
ComparisonSemantic _comparison({
  required String id,
  required String title,
  required List<String> entities,
  required String sourceBlockId,
  required List<({String name, List<String?> values})> dimensions,
}) {
  final s = SemanticData.fromJson({
    'type': 'comparison',
    'id': id,
    'title': title,
    'trust': ContentTrust.fixtureSynthetic.name,
    'derivation': 'synthetic-test',
    'entities': [
      for (final e in entities) {'name': e, 'sourceBlockId': sourceBlockId},
    ],
    'dimensions': [
      for (final d in dimensions) {'name': d.name, 'values': d.values},
    ],
  });
  if (s is! ComparisonSemantic) {
    throw StateError('fixture so sánh trong test không phân tích được');
  }
  return s;
}

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
      final cmp = _comparison(
        id: 'cmp-4',
        title: 'Các cách tách chất (mẫu)',
        sourceBlockId: src,
        entities: const ['Lọc', 'Lắng', 'Cô cạn', 'Chiết'],
        dimensions: const [
          (name: 'Dùng để tách', values: ['một', 'hai', 'ba', null]),
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
      final cmp = _comparison(
        id: 'cmp-6',
        title: 'Sáu cách (mẫu)',
        sourceBlockId: src,
        entities: names,
        dimensions: [
          (name: 'Chiều', values: [for (final _ in names) 'x']),
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
      final cmp = _comparison(
        id: 'cmp-3d',
        title: 'Ba chiều (mẫu)',
        sourceBlockId: src,
        entities: const ['A', 'B'],
        dimensions: const [
          (name: 'c1', values: ['1', '2']),
          (name: 'c2', values: ['1', '2']),
          (name: 'c3', values: ['1', '2']),
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

  group('§6 lỗi máy thật tìm ra (vòng 5, lượt 1)', () {
    testWidgets('⭐ D1 — ĐÃ ĐÓNG BẰNG PHƯƠNG ÁN B: không còn thẻ đề xuất để '
        'che nút trung tâm, và ba View nay có CÙNG chiều cao phần ghim', (
      t,
    ) async {
      // Vòng 5 vá D1 bằng cách đẩy thẻ đề xuất vào vùng cuộn của Trực quan
      // (như đã làm với Đọc ở vòng 4). Vòng 6 bỏ hẳn thẻ ấy: Founder chọn
      // phương án B, nên chỗ này ghim SỰ THẬT MỚI chứ không ghim bản vá cũ —
      // (a) không có gì của lớp trợ giúp nằm trong vùng cuộn của Trực quan,
      // (b) phần ghim của Học với SAM KHÔNG còn cao hơn Trực quan, đúng cái
      // Founder gọi là «tốn chiều dọc» (411 dp so với 225 dp ở vòng 5).
      t.view.physicalSize = const Size(1080, 1920);
      t.view.devicePixelRatio = 2.75;
      addTearDown(t.view.reset);
      await t.pumpWidget(
        fixtureHost(
          LessonWorkspaceScreen(
            doc: loadSyntheticDoc(),
            trace: WorkspaceTrace(),
          ),
        ),
      );
      await t.pumpAndSettle();
      await t.tap(
        find.byKey(LessonWorkspaceScreen.tabKey(WorkspaceView.visual)),
      );
      await t.pumpAndSettle();
      expect(
        find.descendant(
          of: find.byType(VisualView),
          matching: find.byKey(AssistPeek.peekKey),
        ),
        findsNothing,
        reason: 'gợi ý không nằm trong vùng cuộn của sơ đồ nữa',
      );
      expect(find.byKey(AssistPeek.peekKey), findsOneWidget);
      final chromeVisual = t.getTopLeft(find.byType(VisualView)).dy;

      await t.tap(
        find.byKey(LessonWorkspaceScreen.tabKey(WorkspaceView.tutor)),
      );
      await t.pumpAndSettle();
      final chromeTutor = t.getTopLeft(find.byType(TutorView)).dy;
      expect(
        chromeTutor,
        chromeVisual,
        reason:
            'phần ghim của Học với SAM phải bằng Trực quan — thẻ đề xuất '
            'thường trực đã bị xoá ở CẢ BA View',
      );
    });

    testWidgets('⭐ D2: «Vì sao SAM chọn sơ đồ này» nói ĐÚNG thứ trẻ đang nhìn '
        '— sơ đồ tư duy thì không được nói «xếp thành bảng»', (t) async {
      await t.pumpWidget(
        fixtureHost(
          Scaffold(
            body: VisualView(doc: loadSyntheticDoc(), onShowInRead: (_) {}),
          ),
        ),
      );
      await t.pumpAndSettle();
      await t.tap(find.byKey(VisualView.shapeKey('Bảng so sánh')));
      await t.pumpAndSettle();
      expect(find.textContaining('mỗi cách một ô xung quanh'), findsOneWidget);
      expect(find.textContaining('xếp thành bảng'), findsNothing);
      await t.tap(find.byKey(VisualView.comparisonViewKey('table')));
      await t.pumpAndSettle();
      expect(find.textContaining('xếp thành bảng'), findsOneWidget);
    });
  });

  group('§7 renderer KHÔNG được biết bài nào', () {
    /// P0 «Visual Learning tổng quát» (Founder): renderer chỉ được vẽ từ dữ
    /// liệu CÓ KIỂU; `if lesson == "KHTN6_BAI17"` là phản mẫu được gọi tên.
    /// Hai renderer vòng 5 là HÀM THUẦN trên `SemanticData` — test này giữ cho
    /// chúng như thế, kể cả khi lớp VisualSpec của lane E2 thay chỗ chúng.
    test('⭐⭐ mã nguồn renderer không chứa danh tính bài/sách nào', () {
      const files = [
        'lib/features/lesson_workspace/views/mindmap_view.dart',
        'lib/features/lesson_workspace/views/process_flow_view.dart',
      ];
      final identity = RegExp(
        r'(KHTN|LS&ĐL|Bài\s*\d+|bai-\d+|0\d-sgk-|lessonNo\s*==|slotKey'
        r'|doc\.book\s*==|\.lessonNo\b)',
      );
      for (final f in files) {
        final src = File(f).readAsStringSync();
        for (final line in src.split('\n')) {
          expect(
            identity.hasMatch(line),
            isFalse,
            reason: '$f khoá theo danh tính bài: «${line.trim()}»',
          );
        }
      }
    });

    test('renderer chỉ nhận SemanticData + callback nguồn — không nhận '
        'LessonDocument để tra bài', () {
      final src = File(
        'lib/features/lesson_workspace/views/mindmap_view.dart',
      ).readAsStringSync();
      expect(
        src,
        isNot(contains('LessonDocument')),
        reason: 'sơ đồ tư duy vẽ từ nút + nhánh, không cần cả tài liệu',
      );
    });
  });
}
