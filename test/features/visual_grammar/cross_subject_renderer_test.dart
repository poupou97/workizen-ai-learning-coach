/// ⭐⭐ ROUND 5 §19 (Lane E2) — BẰNG CHỨNG TRUNG TÂM CỦA LÀN NÀY:
/// **CÙNG một renderer + CÙNG một lược đồ `VisualSpec` trên các MÔN KHÁC NHAU.**
///
/// Thất bại của làn này được định nghĩa trước: «một hình đẹp chỉ chạy cho Bài
/// 17». Nên test này KHÔNG nhắc tên bài nào; nó quét toàn bộ trang gold đang
/// được commit (10 môn, người chú giải) và đòi:
///
/// 1. ít nhất HAI môn khác nhau dựng được `VisualSpec` cùng họ `sequence`;
/// 2. MỘT thực thể `OrderedStepsRenderer` nhận hết — không renderer riêng
///    theo môn, không nhánh theo môn;
/// 3. mọi nút đều lần được về một block CÓ THẬT, có trang và bbox;
/// 4. widget vẽ ra ĐÚNG chữ sách của từng môn, không phải chữ SAM viết.
library;

import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/visual_spec/document_sequence_rule.dart';
import 'package:learning_coach/core/visual_spec/visual_spec.dart';
import 'package:learning_coach/features/lesson_workspace/visual_grammar/renderers/ordered_steps_renderer.dart';
import 'package:learning_coach/features/lesson_workspace/visual_grammar/visual_spec_view.dart';

import '../../../tool/visual_spec/gold_page_adapter.dart';

/// Một môn + spec dựng được từ một trang gold.
class _Case {
  const _Case(this.subject, this.doc, this.section);
  final String subject;
  final LessonDocument doc;
  final VisualSection section;
}

List<_Case> _cases() {
  final out = <_Case>[];
  for (final f in goldPageFiles()) {
    final doc = goldPageToDocument(f);
    if (doc == null) continue;
    final s = compileNumberedSequence(doc);
    if (s != null) out.add(_Case(doc.subject, doc, s));
  }
  return out;
}

Widget _host(_Case c) => MaterialApp(
  home: Scaffold(
    body: VisualSpecView(
      spec: VisualSpec(
        specVersion: VisualSpec.currentVersion,
        primary: c.section,
      ),
      pageLabel: (id) {
        final b = c.doc.blockById(id);
        return b == null ? 'sách' : c.doc.sourceLineForBlock(b);
      },
      onOpenSource: (_) {},
    ),
  ),
);

void main() {
  final cases = _cases();

  test('§19 dữ liệu chứng minh tồn tại: ≥2 MÔN khác nhau, cùng họ hình', () {
    final subjects = {for (final c in cases) c.subject};
    expect(
      subjects.length,
      greaterThanOrEqualTo(2),
      reason: 'một hình chỉ chạy cho một môn không chứng minh được gì. '
          'Đang có: $subjects',
    );
    for (final c in cases) {
      expect(c.section.family, 'sequence');
    }
  });

  test('§19 MỘT renderer nhận hết mọi môn — không nhánh nào theo môn', () {
    const renderer = OrderedStepsRenderer();
    for (final c in cases) {
      expect(
        renderer.unsupportedReason(c.section),
        isNull,
        reason: '${c.subject}: renderer từ chối một spec hợp lệ',
      );
    }
  });

  test('chuỗi nguồn: mọi nút → block CÓ THẬT → trang in + bbox', () {
    for (final c in cases) {
      for (final n in c.section.nodes) {
        expect(n.provenance.blockIds, isNotEmpty);
        final block = c.doc.blockById(n.provenance.primaryBlockId);
        expect(block, isNotNull, reason: '${c.subject}: nút trỏ vào hư không');
        expect(block!.sourceRef.bbox.length, 4);
        expect(block.sourceRef.pagePdf, greaterThan(0));
        // Nhãn phải là NGUYÊN VĂN chữ của chính block ấy.
        expect(LessonDocument.textOf(block), n.label);
        expect(n.status, InferenceStatus.stated);
      }
      // Mũi tên thứ tự KHÔNG BAO GIỜ được khai là câu của sách.
      for (final e in c.section.edges) {
        expect(e.status, InferenceStatus.derivedDeterministic);
      }
    }
  });

  testWidgets('§19 CÙNG widget vẽ được HAI môn khác nhau, ra chữ sách của môn đó',
      (t) async {
    final bySubject = <String, _Case>{};
    for (final c in cases) {
      bySubject.putIfAbsent(c.subject, () => c);
    }
    expect(bySubject.length, greaterThanOrEqualTo(2));

    var walked = 0;
    for (final c in bySubject.values) {
      await t.pumpWidget(_host(c));
      await t.pumpAndSettle();
      expect(
        find.byKey(OrderedStepsRenderer.rootKey),
        findsOneWidget,
        reason: '${c.subject}: renderer không dựng',
      );
      for (final n in c.section.nodes) {
        expect(
          find.text(n.label!),
          findsOneWidget,
          reason: '${c.subject}: mất chữ sách «${n.label}»',
        );
      }
      walked++;
    }
    expect(walked, greaterThanOrEqualTo(2));
  });

  testWidgets('không mã máy nào lọt lên màn trẻ đọc', (t) async {
    // id block gold mang tên sách + số trang + «gold» — chính là thứ không
    // được phép hiện. Quét mọi `Text` thật sự vẽ ra.
    final machine = RegExp(r'(:p\d{3}:|gold:|sequence|section-\d|-v\d\b)');
    for (final c in _cases()) {
      await t.pumpWidget(_host(c));
      await t.pumpAndSettle();
      for (final w in t.widgetList<Text>(find.byType(Text))) {
        final s = w.data;
        if (s == null) continue;
        expect(
          machine.hasMatch(s),
          isFalse,
          reason: '${c.subject}: mã máy trên màn trẻ — «$s»',
        );
      }
    }
  });

  test('trang gold vẫn còn trong repo (test này không được xanh giả)', () {
    expect(
      goldPageFiles().length,
      greaterThan(40),
      reason: 'không có trang gold thì mọi khẳng định trên đều rỗng',
    );
    expect(Directory('tool/corpus/tc_gold').existsSync(), isTrue);
  });
}
