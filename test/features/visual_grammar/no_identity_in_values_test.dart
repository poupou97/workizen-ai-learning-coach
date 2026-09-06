/// ⭐⭐ ROUND 5 (Lane E2) — DANH TÍNH TRONG **GIÁ TRỊ**, không phải trong tên
/// trường.
///
/// Làn này đã có hai test quét mã: `VisualSpec` không có trường `book` /
/// `lessonNo` / `slotKey`, và không renderer nào import `LessonDocument`.
/// **Cả hai đều xanh trong khi danh tính vẫn đi lọt** — vì nó nằm trong GIÁ
/// TRỊ của `ProvenanceRef.blockIds`:
///
///     06-sgk-khoa-hoc-tu-nhien-6:p062:synthetic:015
///
/// Một renderer chỉ cần `startsWith('06-sgk-khoa-hoc-tu-nhien-6')` là rẽ theo
/// bài, và mọi rào theo TÊN TRƯỜNG vẫn báo an toàn. «Không viết ra được» chỉ
/// mạnh bằng cái kênh hẹp nhất còn hở.
///
/// Test này đi TOÀN BỘ đồ thị đối tượng mà renderer thật sự cầm, sau khi qua
/// `VisualRenderContext`, và soi từng CHUỖI.
library;

import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/visual_spec/document_sequence_rule.dart';
import 'package:learning_coach/core/visual_spec/semantic_to_spec.dart';
import 'package:learning_coach/core/visual_spec/visual_spec.dart';
import 'package:learning_coach/features/lesson_workspace/visual_grammar/visual_family_renderer.dart';

import '../../../tool/visual_spec/gold_page_adapter.dart';

/// Mã sách («06-sgk-…», «10-sgv-…»), số bài, hay id block có số trang.
final identity = RegExp(
  r'(\d{2}-sg[kv]-[a-z0-9-]+|bai-?\d+|khtn\d|:p\d+:)',
  caseSensitive: false,
);

/// Mọi chuỗi renderer đọc được từ một section — TRỪ chữ sách mà trẻ phải đọc
/// (`label`, `detail`, `badge`, `title`, `childSummary`, nhãn nhóm/cạnh).
/// Chữ sách CÓ THỂ chứa «Bài 22» vì sách in thế; nó là NỘI DUNG, không phải
/// một định danh để rẽ nhánh. Mọi thứ còn lại phải vô nghĩa.
List<String> machineStringsOf(VisualSection s) => [
  s.id,
  s.family,
  ..._ref(s.titleProvenance),
  for (final n in s.nodes) ...[n.id, n.status.name, ..._ref(n.provenance)],
  for (final e in s.edges) ...[
    e.fromId,
    e.toId,
    e.kind.name,
    e.status.name,
    ..._ref(e.provenance),
  ],
  for (final g in s.groups) ...[
    g.id,
    g.axis.name,
    ...g.nodeIds,
    ...(g.provenance == null ? const <String>[] : _ref(g.provenance!)),
  ],
  ...s.ordering,
  ...s.emphasis,
];

List<String> _ref(ProvenanceRef r) => [
  ...r.blockIds,
  r.derivationRule,
  r.trust.name,
  ...(r.claimId == null ? const <String>[] : [r.claimId!]),
];

List<VisualSection> _allSections() {
  final out = <VisualSection>[];
  for (final f in goldPageFiles()) {
    final doc = goldPageToDocument(f);
    if (doc == null) continue;
    final s = compileNumberedSequence(doc);
    if (s != null) out.add(s);
  }
  for (final path in const [
    'assets/fixtures/synthetic/'
        'lesson-06-sgk-khoa-hoc-tu-nhien-6-b17.synthetic.json',
    'assets/fixtures/synthetic/'
        'lesson-05-sgk-lich-su-va-dia-li-5-b8.synthetic.json',
  ]) {
    final doc = LessonDocument.fromJson(
      (jsonDecode(File(path).readAsStringSync()) as Map)
          .cast<String, Object?>(),
    )!;
    out.addAll(compileLesson(doc).spec!.sections);
  }
  return out;
}

void main() {
  final sections = _allSections();

  test('nền chứng minh có thật (test này không được xanh giả)', () {
    expect(sections.length, greaterThanOrEqualTo(5));
  });

  test('⭐ TRƯỚC rào chắn: artefact THẬT SỰ mang danh tính trong blockIds', () {
    // Ghi lại lỗ hổng để nó không lặng lẽ quay lại: id block trong artefact
    // CÓ mã sách và số trang. Artefact giữ nguyên là ĐÚNG — chuỗi nguồn phải
    // kiểm lại được. Điều phải chặn là renderer NHÌN THẤY nó.
    final leaks = <String>[];
    for (final s in sections) {
      for (final id in s.titleProvenance.blockIds) {
        if (identity.hasMatch(id)) leaks.add(id);
      }
    }
    expect(
      leaks,
      isNotEmpty,
      reason: 'nếu artefact hết danh tính thì rào chắn dưới đây vô nghĩa — '
          'hãy kiểm lại test, đừng xoá nó',
    );
  });

  test('⭐⭐ SAU rào chắn: không CHUỖI MÁY nào renderer cầm còn mang danh tính',
      () {
    for (final s in sections) {
      final ctx = VisualRenderContext(
        section: s,
        pageLabel: (_) => 'SGK · trang',
        onOpenSource: (_) {},
      );
      for (final v in machineStringsOf(ctx.section)) {
        final m = identity.firstMatch(v);
        expect(
          m,
          isNull,
          reason: 'renderer vẫn rẽ nhánh theo bài được qua «$v» '
              '(khớp «${m?.group(0)}») — bảo đảm chỉ là danh nghĩa',
        );
      }
    }
  });

  test('thẻ che vẫn đổi ngược được: chuỗi nguồn KHÔNG bị mất', () {
    for (final s in sections) {
      String? asked;
      final ctx = VisualRenderContext(
        section: s,
        pageLabel: (id) {
          asked = id;
          return 'SGK · trang';
        },
        onOpenSource: (_) {},
      );
      final node = ctx.section.nodes.first;
      ctx.pageOf(node.provenance);
      expect(asked, isNotNull);
      // Host nhận lại id block THẬT, không phải thẻ.
      expect(asked, s.nodes.first.provenance.primaryBlockId);
      expect(node.provenance.primaryBlockId, startsWith('h'));

      ProvenanceRef? opened;
      final ctx2 = VisualRenderContext(
        section: s,
        pageLabel: (_) => '',
        onOpenSource: (r) => opened = r,
      );
      ctx2.openSource(ctx2.section.nodes.first.provenance);
      expect(opened!.primaryBlockId, s.nodes.first.provenance.primaryBlockId);
    }
  });

  test('che KHÔNG làm hỏng thứ trẻ đọc: chữ sách + luật + độ tin giữ nguyên',
      () {
    for (final s in sections) {
      final ctx = VisualRenderContext(
        section: s,
        pageLabel: (_) => '',
        onOpenSource: (_) {},
      );
      expect(ctx.section.title, s.title);
      expect(ctx.section.childSummary, s.childSummary);
      expect(ctx.section.trust, s.trust);
      expect(ctx.section.derivationRules, s.derivationRules);
      for (var i = 0; i < s.nodes.length; i++) {
        expect(ctx.section.nodes[i].label, s.nodes[i].label);
        expect(ctx.section.nodes[i].badge, s.nodes[i].badge);
        expect(ctx.section.nodes[i].status, s.nodes[i].status);
      }
      expect(ctx.section.edges.length, s.edges.length);
      expect(ctx.section.groups.length, s.groups.length);
    }
  });

  test('id do bộ biên dịch đặt phải VÔ NGHĨA theo hình dạng, không chỉ hôm nay',
      () {
    // Chặn kênh thứ hai: `VisualSection.id` được CHÉP từ `SemanticData.id`,
    // nên tầng ngữ nghĩa có thể bơm «khtn6-bai17-process» vào và nó chảy
    // thẳng tới renderer. Ràng buộc HÌNH DẠNG bắt được điều đó.
    final opaque = RegExp(r'^[a-z]+(-[a-z]+)*(-\d+)*$');
    for (final s in sections) {
      expect(opaque.hasMatch(s.id), isTrue, reason: 'section.id «${s.id}»');
      for (final n in s.nodes) {
        expect(opaque.hasMatch(n.id), isTrue, reason: 'node.id «${n.id}»');
      }
      for (final g in s.groups) {
        expect(opaque.hasMatch(g.id), isTrue, reason: 'group.id «${g.id}»');
      }
    }
  });
}
