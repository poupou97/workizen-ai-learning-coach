/// TRACK B — «SAM đề xuất»: tất định, có lý do, không phút bịa.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/next_action.dart';

import '../../features/lesson_workspace/support.dart';

void main() {
  test(
    'bài có quy trình & chưa xem Trực quan ⇒ Trực quan, lý do nêu tên sơ đồ',
    () {
      final d = loadSyntheticDoc();
      final n = nextActionFor(doc: d, seen: {});
      expect(n.view, WorkspaceView.visual);
      expect(n.reason, contains('sơ đồ quy trình'));
      expect(n.basis, startsWith('semantic.process:'));
    },
  );

  test('đã xem Trực quan ⇒ Đọc; đã đọc ⇒ Học với SAM (nêu câu hỏi); đủ ba ⇒ '
      'về mục lục', () {
    final d = loadSyntheticDoc();
    expect(
      nextActionFor(doc: d, seen: {WorkspaceView.visual}).view,
      WorkspaceView.read,
    );
    final t = nextActionFor(
      doc: d,
      seen: {WorkspaceView.visual, WorkspaceView.read},
    );
    expect(t.view, WorkspaceView.tutor);
    expect(t.reason, contains('«'));
    final done = nextActionFor(doc: d, seen: WorkspaceView.values.toSet());
    expect(done.view, isNull);
    expect(done.label, 'Về mục lục');
    expect(
      done.reason,
      isNot(contains('hiểu')),
      reason: 'lời kết chỉ ghi nhận THAM GIA, không nói đã hiểu',
    );
  });

  test('⭐ không lý do nào chứa ước lượng thời gian (không có dữ liệu đo)', () {
    final d = loadSyntheticDoc();
    final seens = [
      <WorkspaceView>{},
      {WorkspaceView.visual},
      {WorkspaceView.visual, WorkspaceView.read},
      WorkspaceView.values.toSet(),
    ];
    for (final s in seens) {
      final r = nextActionFor(doc: d, seen: s).reason;
      expect(r, isNot(matches(RegExp(r'\d+\s*phút'))), reason: r);
      expect(r, isNot(contains('~')));
    }
  });
}
