/// TRACK B — Lesson Workspace: ba View nhìn thấy, chip bắt buộc, SAM đề xuất
/// có lý do, nhảy giữa View mang theo block.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/next_action.dart';
import 'package:learning_coach/features/lesson_workspace/lesson_workspace_screen.dart';
import 'package:learning_coach/features/lesson_workspace/widgets/fixture_chip.dart';
import 'package:learning_coach/features/lesson_workspace/workspace_trace.dart';

import 'support.dart';

void main() {
  testWidgets('⭐ ba View nhìn thấy + tiêu đề «Bài 17 · …» + chip thử nghiệm', (
    t,
  ) async {
    await t.pumpWidget(
      fixtureHost(
        LessonWorkspaceScreen(doc: loadSyntheticDoc(), trace: WorkspaceTrace()),
      ),
    );
    await t.pumpAndSettle();
    expect(find.textContaining('Bài 17 · Tách chất'), findsOneWidget);
    for (final v in WorkspaceView.values) {
      expect(find.byKey(LessonWorkspaceScreen.tabKey(v)), findsOneWidget);
      expect(find.textContaining(v.label), findsWidgets);
    }
    expect(
      find.byKey(FixtureChip.chipKey),
      findsOneWidget,
      reason: '⭐⭐ fixture ⇒ chip bắt buộc',
    );
    expect(find.textContaining('giả lập'), findsWidgets);
    expect(find.byKey(LessonWorkspaceScreen.nextActionKey), findsOneWidget);
    expect(find.text('SAM đề xuất'), findsOneWidget);
  });

  testWidgets('mở ở View SAM đề xuất (Trực quan vì có quy trình), rồi đề xuất '
      'đổi sang Đọc', (t) async {
    final trace = WorkspaceTrace();
    final doc = loadSyntheticDoc();
    await t.pumpWidget(
      fixtureHost(LessonWorkspaceScreen(doc: doc, trace: trace)),
    );
    await t.pumpAndSettle();
    expect(trace.viewsFor(doc.slotKey), {WorkspaceView.visual});
    expect(find.textContaining('Sơ đồ quy trình'), findsWidgets);
    // thẻ đề xuất giờ chỉ sang Đọc (đã xem Trực quan)
    expect(find.textContaining('đọc bài trong sách'), findsOneWidget);
  });

  testWidgets('bấm tab đổi View; mỗi tab ≥48dp', (t) async {
    final trace = WorkspaceTrace();
    final doc = loadSyntheticDoc();
    await t.pumpWidget(
      fixtureHost(LessonWorkspaceScreen(doc: doc, trace: trace)),
    );
    await t.pumpAndSettle();
    for (final v in WorkspaceView.values) {
      final size = t.getSize(find.byKey(LessonWorkspaceScreen.tabKey(v)));
      expect(size.height, greaterThanOrEqualTo(48));
    }
    await t.tap(find.byKey(LessonWorkspaceScreen.tabKey(WorkspaceView.tutor)));
    await t.pumpAndSettle();
    expect(find.text('SAM (kịch bản thử nghiệm)'), findsWidgets);
    expect(
      trace.viewsFor(doc.slotKey),
      containsAll([WorkspaceView.visual, WorkspaceView.tutor]),
    );
    await t.tap(find.byKey(LessonWorkspaceScreen.tabKey(WorkspaceView.read)));
    await t.pumpAndSettle();
    expect(find.text('Cỡ chữ'), findsOneWidget);
  });

  testWidgets('⭐ Đọc → chạm đoạn → «Hỏi SAM về đoạn này» ⇒ sang Tutor mang '
      'theo đoạn', (t) async {
    final doc = loadSyntheticDoc();
    await t.pumpWidget(
      fixtureHost(
        LessonWorkspaceScreen(
          doc: doc,
          trace: WorkspaceTrace(),
          initialView: WorkspaceView.read,
        ),
      ),
    );
    await t.pumpAndSettle();
    final q = find.textContaining('Làm muối từ nước biển');
    await t.ensureVisible(q.first);
    await t.tap(q.first);
    await t.pumpAndSettle();
    await t.tap(find.text('🦉 Hỏi SAM về đoạn này'));
    await t.pumpAndSettle();
    expect(find.textContaining('Con hỏi về đoạn:'), findsOneWidget);
    expect(find.text('SAM (kịch bản thử nghiệm)'), findsWidgets);
  });

  testWidgets('đủ ba View ⇒ đề xuất «Về mục lục» (ghi nhận tham gia, không '
      '«đã hiểu»)', (t) async {
    final trace = WorkspaceTrace();
    final doc = loadSyntheticDoc();
    for (final v in WorkspaceView.values) {
      trace.markView(doc.slotKey, v);
    }
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
    expect(find.text('Về mục lục'), findsOneWidget);
    expect(find.textContaining('đã hiểu'), findsNothing);
  });

  testWidgets('không có chip khi… không tồn tại: mọi fixture đều có chip', (
    t,
  ) async {
    // Hôm nay không có tài liệu trustedCorpus — test này ghim rằng cả hai
    // fixture (mẫu, và thật nếu có) đều nổi chip.
    final docs = [loadSyntheticDoc(), ?loadRealDocOrSkip()];
    for (final d in docs) {
      await t.pumpWidget(
        fixtureHost(LessonWorkspaceScreen(doc: d, trace: WorkspaceTrace())),
      );
      await t.pumpAndSettle();
      expect(find.byKey(FixtureChip.chipKey), findsOneWidget);
    }
  });

  testWidgets('back ở header pop được (đường về mục lục)', (t) async {
    await t.pumpWidget(
      MaterialApp(
        home: Builder(
          builder: (ctx) => TextButton(
            onPressed: () => Navigator.of(ctx).push(
              MaterialPageRoute(
                builder: (_) => LessonWorkspaceScreen(
                  doc: loadSyntheticDoc(),
                  trace: WorkspaceTrace(),
                ),
              ),
            ),
            child: const Text('go'),
          ),
        ),
      ),
    );
    await t.tap(find.text('go'));
    await t.pumpAndSettle();
    expect(find.textContaining('Bài 17'), findsWidgets);
    await t.tap(find.byTooltip('Về mục lục'));
    await t.pumpAndSettle();
    expect(find.text('go'), findsOneWidget);
  });
}
