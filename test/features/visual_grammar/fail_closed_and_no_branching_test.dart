/// LANE E2 (round 5) — hai thứ phải ĐÚNG kể cả khi không ai nhìn:
///
/// A. **Fail closed ở ba chỗ khác nhau, ba câu khác nhau.** Không có spec ≠
///    có spec mà chưa có renderer ≠ có renderer mà dữ liệu sai hình dạng.
///    Gộp ba thứ ấy vào một câu là nói dối một cách tiện tay.
/// B. **KHÔNG rẽ nhánh theo bài.** Quét MÃ NGUỒN của cả hai thư mục làn E2:
///    không có `lessonNo`, `slotKey`, tên sách, hay chuỗi kiểu «bai17». Test
///    đọc file, nên nó bắt được cả thứ mà kiểu dữ liệu không chặn được.
library;

import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/content_trust.dart';
import 'package:learning_coach/core/visual_spec/visual_spec.dart';
import 'package:learning_coach/features/lesson_workspace/visual_grammar/renderers/ordered_steps_renderer.dart';
import 'package:learning_coach/features/lesson_workspace/visual_grammar/visual_family_renderer.dart';
import 'package:learning_coach/features/lesson_workspace/visual_grammar/visual_registry.dart';
import 'package:learning_coach/features/lesson_workspace/visual_grammar/visual_spec_view.dart';

ProvenanceRef _ref() => const ProvenanceRef(
  blockIds: ['blk-1'],
  derivationRule: 'tsl-enumerated-steps-v1',
  trust: ContentTrust.trustedStructuredLesson,
);

VisualNode _node(String id, String label) => VisualNode(
  id: id,
  label: label,
  status: InferenceStatus.stated,
  provenance: _ref(),
);

VisualSection _section({
  String family = 'process',
  List<VisualNode>? nodes,
  List<VisualEdge>? edges,
}) => VisualSection(
  id: 'sec',
  family: family,
  title: 'Tách chất khỏi hỗn hợp',
  titleProvenance: _ref(),
  nodes: nodes ?? [_node('a', 'Bước một'), _node('b', 'Bước hai')],
  edges: edges ?? const [],
  ordering: const ['a', 'b'],
  trust: ContentTrust.trustedStructuredLesson,
);

Widget _host(VisualSpec? spec, {VisualRendererRegistry? registry}) => MaterialApp(
  home: Scaffold(
    body: VisualSpecView(
      spec: spec,
      pageLabel: (_) => 'SGK KHTN 6 · trang 62',
      onOpenSource: (_) {},
      registry: registry ?? defaultVisualRegistry,
    ),
  ),
);

VisualSpec _spec(VisualSection s) =>
    VisualSpec(specVersion: VisualSpec.currentVersion, primary: s);

void main() {
  testWidgets('A1 không có spec ⇒ nói VÌ SAO, không vẽ gì', (t) async {
    await t.pumpWidget(_host(null));
    await t.pumpAndSettle();
    expect(find.byKey(VisualSpecView.emptyKey), findsOneWidget);
    expect(find.byKey(OrderedStepsRenderer.rootKey), findsNothing);
    expect(find.textContaining('SAM chỉ vẽ khi tìm được đúng chỗ sách viết'),
        findsOneWidget);
  });

  testWidgets('A2 họ hình chưa có renderer ⇒ nói CÂU KHÁC, vẫn không vẽ',
      (t) async {
    await t.pumpWidget(_host(_spec(_section(family: 'causeEffect'))));
    await t.pumpAndSettle();
    expect(find.byKey(VisualSpecView.unsupportedKey), findsOneWidget);
    expect(find.byKey(OrderedStepsRenderer.rootKey), findsNothing);
    expect(find.textContaining('chưa biết vẽ thành hình'), findsOneWidget);
    // KHÔNG được rơi xuống một renderer khác «cho có hình».
    expect(find.textContaining('Bước một'), findsNothing);
  });

  testWidgets('A3 dữ liệu sai hình dạng ⇒ renderer TỪ CHỐI, câu thứ ba',
      (t) async {
    await t.pumpWidget(
      _host(_spec(_section(nodes: [_node('a', 'Chỉ một ý')]))),
    );
    await t.pumpAndSettle();
    expect(find.byKey(VisualSpecView.unsupportedKey), findsOneWidget);
    expect(find.textContaining('ít nhất hai ý'), findsOneWidget);
  });

  test('renderer từ chối cạnh nó không hiểu, có MÃ lý do đếm được', () {
    const r = OrderedStepsRenderer();
    expect(r.unsupportedReason(_section()), isNull);
    expect(
      r.unsupportedReason(_section(nodes: [_node('a', 'một')])),
      'need_two_nodes',
    );
    final s = _section(
      edges: [
        VisualEdge(
          fromId: 'a',
          toId: 'b',
          kind: EdgeKind.contains,
          status: InferenceStatus.stated,
          provenance: _ref(),
        ),
      ],
    );
    expect(r.unsupportedReason(s), 'edge_kind:contains');
  });

  testWidgets('«Vì sao SAM vẽ thế này» tra theo LUẬT, không theo kiểu Dart',
      (t) async {
    await t.pumpWidget(_host(_spec(_section())));
    await t.pumpAndSettle();
    expect(find.byKey(VisualSpecView.whyKey), findsOneWidget);
    expect(find.textContaining('dấu đầu dòng theo thứ tự'), findsOneWidget);

    // CÙNG kiểu dữ liệu, LUẬT khác ⇒ câu khác. Đây chính là lỗi của
    // `visual_view.dart` hôm nay: nó sẽ nói y hệt câu trên cho luật này.
    final other = VisualSection(
      id: 'sec',
      family: 'sequence',
      title: 'Bài 22',
      titleProvenance: const ProvenanceRef(
        blockIds: ['blk-1'],
        derivationRule: 'numbered-section-sequence-v1',
        trust: ContentTrust.fixtureFromTrustedCorpus,
      ),
      nodes: [
        VisualNode(
          id: 'a',
          label: '1. Dụng cụ thí nghiệm',
          status: InferenceStatus.stated,
          provenance: const ProvenanceRef(
            blockIds: ['blk-1'],
            derivationRule: 'numbered-section-sequence-v1',
            trust: ContentTrust.fixtureFromTrustedCorpus,
          ),
        ),
        VisualNode(
          id: 'b',
          label: '2. Tiến hành thí nghiệm',
          status: InferenceStatus.stated,
          provenance: const ProvenanceRef(
            blockIds: ['blk-2'],
            derivationRule: 'numbered-section-sequence-v1',
            trust: ContentTrust.fixtureFromTrustedCorpus,
          ),
        ),
      ],
      ordering: const ['a', 'b'],
      trust: ContentTrust.fixtureFromTrustedCorpus,
    );
    await t.pumpWidget(_host(_spec(other)));
    await t.pumpAndSettle();
    expect(find.textContaining('thứ tự SÁCH IN'), findsOneWidget);
    expect(find.textContaining('dấu đầu dòng theo thứ tự'), findsNothing);
  });

  testWidgets('luật CHƯA có mục từ ⇒ câu tổng quát, KHÔNG mượn câu luật khác',
      (t) async {
    const unknown = ProvenanceRef(
      blockIds: ['blk-1'],
      derivationRule: 'luat-chua-co-v1',
      trust: ContentTrust.trustedStructuredLesson,
    );
    final s = VisualSection(
      id: 'sec',
      family: 'process',
      title: 'X',
      titleProvenance: unknown,
      nodes: [
        VisualNode(
          id: 'a',
          label: 'một',
          status: InferenceStatus.stated,
          provenance: unknown,
        ),
        VisualNode(
          id: 'b',
          label: 'hai',
          status: InferenceStatus.stated,
          provenance: unknown,
        ),
      ],
      ordering: const ['a', 'b'],
      trust: ContentTrust.trustedStructuredLesson,
    );
    await t.pumpWidget(_host(_spec(s)));
    await t.pumpAndSettle();
    expect(find.textContaining('không thêm ý nào'), findsOneWidget);
    expect(find.textContaining('dấu đầu dòng theo thứ tự'), findsNothing);
  });

  testWidgets('nút SUY DIỄN nói ra là suy diễn, ngay cạnh chữ', (t) async {
    final s = VisualSection(
      id: 'sec',
      family: 'process',
      title: 'X',
      titleProvenance: _ref(),
      nodes: [
        _node('a', 'Bước một'),
        VisualNode(
          id: 'b',
          label: 'SAM viết lại cho gọn',
          status: InferenceStatus.inferred,
          provenance: _ref(),
        ),
      ],
      ordering: const ['a', 'b'],
      trust: ContentTrust.trustedStructuredLesson,
    );
    await t.pumpWidget(_host(_spec(s)));
    await t.pumpAndSettle();
    expect(find.byKey(OrderedStepsRenderer.inferredNoteKey('b')), findsOneWidget);
    expect(find.byKey(OrderedStepsRenderer.inferredNoteKey('a')), findsNothing);
  });

  // ── B. không rẽ nhánh theo bài ──

  test('KHÔNG có nhánh theo danh tính bài trong mã của làn E2', () {
    final dirs = [
      Directory('lib/core/visual_spec'),
      Directory('lib/features/lesson_workspace/visual_grammar'),
    ];
    // Mẫu chống chỉ định: so sánh với một bài / một sách cụ thể.
    final branching = RegExp(
      r'(lessonNo\s*==|slotKey\s*==|\bbook\s*==|bai\s*-?\s*17|Bai17|BAI17'
      r'|khtn6|lessonId\s*==)',
      caseSensitive: false,
    );
    final scanned = <String>[];
    for (final d in dirs) {
      expect(d.existsSync(), isTrue, reason: '${d.path} phải tồn tại');
      for (final f in d.listSync(recursive: true).whereType<File>()) {
        if (!f.path.endsWith('.dart')) continue;
        scanned.add(f.path);
        // Bỏ dòng chú thích: bảng «đã chứng minh trên môn nào» được phép
        // nhắc tên bài; mã thì không.
        final code = f
            .readAsLinesSync()
            .where((l) => !l.trimLeft().startsWith('//'))
            .where((l) => !l.trimLeft().startsWith('///'))
            .join('\n');
        final m = branching.firstMatch(code);
        expect(
          m,
          isNull,
          reason: '${f.path}: rẽ nhánh theo bài — «${m?.group(0)}»',
        );
      }
    }
    expect(scanned.length, greaterThanOrEqualTo(6));
  });

  test('renderer KHÔNG có đường nào chạm tới `LessonDocument`', () {
    final d = Directory('lib/features/lesson_workspace/visual_grammar');
    for (final f in d.listSync(recursive: true).whereType<File>()) {
      if (!f.path.endsWith('.dart')) continue;
      final src = f.readAsStringSync();
      expect(
        src.contains("import '../../../core/lesson_model/lesson_document.dart'"),
        isFalse,
        reason: '${f.path}: renderer không được biết tài liệu bài',
      );
    }
  });
}
