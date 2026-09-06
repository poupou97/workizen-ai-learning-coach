/// ⭐ §27 (Lane E2) — BẢN GHI MÀN HÌNH cho checkpoint sớm của Founder.
///
/// Không có ảnh máy thật trong làn này (Lane B giữ vòng thiết bị round 5).
/// Thay vì mô tả bằng lời «màn sẽ trông thế nào», test này DỰNG THẬT widget
/// rồi in ra ĐÚNG mọi chuỗi trẻ nhìn thấy, theo thứ tự. Bản ghi là máy sinh,
/// chạy lại được trên clone sạch, và dán thẳng vào tài liệu checkpoint.
///
///     flutter test test/features/visual_grammar/checkpoint_transcript_test.dart
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/visual_spec/document_sequence_rule.dart';
import 'package:learning_coach/core/visual_spec/visual_spec.dart';
import 'package:learning_coach/features/lesson_workspace/visual_grammar/visual_spec_view.dart';

import '../../../tool/visual_spec/gold_page_adapter.dart';

void main() {
  testWidgets('§27 bản ghi màn hình: SOURCE → SEMANTIC → SPEC → UI', (t) async {
    for (final f in goldPageFiles()) {
      final doc = goldPageToDocument(f);
      if (doc == null) continue;
      final section = compileNumberedSequence(doc);
      if (section == null) continue;

      await t.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: VisualSpecView(
              spec: VisualSpec(
                specVersion: VisualSpec.currentVersion,
                primary: section,
              ),
              pageLabel: (id) {
                final b = doc.blockById(id);
                return b == null ? 'sách' : doc.sourceLineForBlock(b);
              },
              onOpenSource: (_) {},
            ),
          ),
        ),
      );
      await t.pumpAndSettle();

      debugPrint('--- ${doc.subject} · lớp ${doc.grade} · ${f.uri.pathSegments.last}');
      for (final w in t.widgetList<Text>(find.byType(Text))) {
        final s = w.data;
        if (s != null && s.trim().isNotEmpty) debugPrint('    $s');
      }
    }
    // Bản ghi là sản phẩm phụ; khẳng định là: màn dựng được cho ≥1 môn.
    expect(find.byKey(VisualSpecView.rootKey), findsOneWidget);
  });
}
