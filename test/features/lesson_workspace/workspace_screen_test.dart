/// TRACK B — Lesson Workspace: ba View nhìn thấy, chip bắt buộc, SAM đề xuất
/// có lý do, nhảy giữa View mang theo block.
///
/// ROUND 3 B1: lần đầu mở ⇒ màn «Vào bài học» (ba thẻ, thẻ đề xuất mang lý
/// do); đường dẫn «Giá sách › KHTN 6 › Chương IV»; chip gọn chạm ⇒ sheet
/// «Nguồn & độ tin».
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/next_action.dart';
import 'package:learning_coach/features/lesson_workspace/lesson_workspace_screen.dart';
import 'package:learning_coach/features/lesson_workspace/widgets/fixture_chip.dart';
import 'package:learning_coach/features/lesson_workspace/widgets/mode_picker.dart';
import 'package:learning_coach/features/lesson_workspace/workspace_trace.dart';

import 'support.dart';

void main() {
  testWidgets('⭐ ba View nhìn thấy + tiêu đề «Bài 17 · …» + chip thử nghiệm + '
      'đường dẫn', (t) async {
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
    // B1 câu 1 «con đang ở đâu»
    final crumb = t.widget<Text>(
      find.byKey(LessonWorkspaceScreen.breadcrumbKey),
    );
    expect(crumb.data, 'Giá sách › KHTN 6 › Chương IV');
  });

  testWidgets('⭐ lần đầu mở ⇒ màn «Vào bài học»: 3 thẻ đếm từ dữ liệu, thẻ '
      'Trực quan được đề xuất kèm lý do; chưa View nào bị đánh dấu', (
    t,
  ) async {
    final trace = WorkspaceTrace();
    final doc = loadSyntheticDoc();
    await t.pumpWidget(
      fixtureHost(LessonWorkspaceScreen(doc: doc, trace: trace)),
    );
    await t.pumpAndSettle();
    expect(find.byKey(const Key('mode-picker')), findsOneWidget);
    expect(find.textContaining('theo cách nào'), findsOneWidget);
    for (final v in WorkspaceView.values) {
      expect(find.byKey(ModePicker.cardKey(v)), findsOneWidget);
      expect(find.text(ModePicker.describe(doc, v)), findsOneWidget);
    }
    expect(find.textContaining('SAM đề xuất cách này'), findsOneWidget);
    expect(find.textContaining('sơ đồ quy trình'), findsWidgets);
    expect(
      find.byKey(LessonWorkspaceScreen.nextActionKey),
      findsNothing,
      reason: 'lý do đã nằm trên thẻ đề xuất — không lặp',
    );
    expect(trace.viewsFor(doc.slotKey), isEmpty);
    expect(trace.opened(doc.slotKey), isTrue);
  });

  testWidgets('mô tả thẻ: Đọc đếm đoạn/hình/câu hỏi; Trực quan liệt kê hình '
      'dạng; SAM nói số câu + «kịch bản thử nghiệm»', (t) async {
    final doc = loadSyntheticDoc();
    final read = ModePicker.describe(doc, WorkspaceView.read);
    expect(read, contains('đoạn'));
    expect(read, contains('câu hỏi trong sách'));
    final visual = ModePicker.describe(doc, WorkspaceView.visual);
    expect(visual, contains('Sơ đồ quy trình'));
    expect(visual, contains('Bảng tóm tắt'));
    final tutor = ModePicker.describe(doc, WorkspaceView.tutor);
    expect(tutor, contains('kịch bản thử nghiệm'));
    expect(tutor, contains('${doc.tutorScript!.asks.length} câu'));
  });

  testWidgets('chạm thẻ đề xuất ⇒ vào Trực quan, trace đánh dấu, thẻ đề xuất '
      'đổi sang Đọc', (t) async {
    final trace = WorkspaceTrace();
    final doc = loadSyntheticDoc();
    await t.pumpWidget(
      fixtureHost(LessonWorkspaceScreen(doc: doc, trace: trace)),
    );
    await t.pumpAndSettle();
    await t.tap(find.byKey(ModePicker.cardKey(WorkspaceView.visual)));
    await t.pumpAndSettle();
    expect(trace.viewsFor(doc.slotKey), {WorkspaceView.visual});
    expect(find.textContaining('Sơ đồ quy trình'), findsWidgets);
    expect(find.byKey(LessonWorkspaceScreen.nextActionKey), findsOneWidget);
    expect(find.text('SAM đề xuất'), findsOneWidget);
    expect(find.textContaining('đọc bài trong sách'), findsOneWidget);
  });

  testWidgets('mở lại bài đã xem trong phiên ⇒ KHÔNG hỏi lại, vào thẳng View '
      'SAM đề xuất', (t) async {
    final trace = WorkspaceTrace();
    final doc = loadSyntheticDoc();
    trace.markView(doc.slotKey, WorkspaceView.visual);
    await t.pumpWidget(
      fixtureHost(LessonWorkspaceScreen(doc: doc, trace: trace)),
    );
    await t.pumpAndSettle();
    expect(find.byKey(const Key('mode-picker')), findsNothing);
    expect(find.text('Cỡ chữ'), findsOneWidget, reason: 'đề xuất Đọc');
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
    expect(trace.viewsFor(doc.slotKey), {WorkspaceView.tutor});
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

  testWidgets('⭐ chip chạm được ⇒ sheet «Nguồn & độ tin»: mức tin, luật sơ '
      'đồ, SAM là kịch bản, KHÔNG ghi bằng chứng, sáu bất đẳng thức', (
    t,
  ) async {
    final doc = loadSyntheticDoc();
    await t.pumpWidget(
      fixtureHost(LessonWorkspaceScreen(doc: doc, trace: WorkspaceTrace())),
    );
    await t.pumpAndSettle();
    await t.tap(find.byKey(const Key('fixture-chip-tap')));
    await t.pumpAndSettle();
    expect(find.byKey(const Key('trust-sheet')), findsOneWidget);
    expect(find.textContaining('MẪU GIẢ LẬP'), findsOneWidget);
    for (final s in doc.semantic) {
      expect(find.textContaining('luật ${s.derivation}'), findsWidgets);
    }
    expect(find.textContaining('kịch bản viết sẵn'), findsOneWidget);
    expect(find.textContaining('KHÔNG ghi'), findsOneWidget);
    for (final s in [
      'MOCK ≠ EVIDENCE',
      'FIXTURE ≠ TRUSTED CORPUS',
      'UI COMPLETION ≠ MASTERY',
      'TAP ≠ COMPETENCE',
      'PROTOTYPE SAM ≠ PROVEN PEDAGOGY',
      'SCREEN EXISTS ≠ CAPABILITY PROVEN',
    ]) {
      expect(find.textContaining(s), findsOneWidget);
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
