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

  test('đã xem Trực quan ⇒ Đọc; đã đọc ⇒ Học với SAM (nêu câu hỏi); đã MỞ đủ '
      'ba ⇒ Ở LẠI BÀI', () {
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
    // ⭐⭐ ROUND 7 · WS-S (HO-2) — «Về mục lục» là chuỗi đã bảo một đứa trẻ rời
    // khỏi bài nó vừa mở, trên máy thật. Nó không còn được phép ra từ đây.
    expect(done.label, 'Xem tiếp bài này');
    expect(
      done.reason,
      contains('Mở không phải là đã hiểu'),
      reason: 'lời kết phải nói thẳng OPENED != UNDERSTOOD',
    );
  });

  test('⭐⭐ KHÔNG tổ hợp `seen` nào khiến SAM bảo trẻ rời bài', () {
    // QUÉT, không lấy mẫu: cả 8 tập con của ba View. Bản trước chỉ kiểm MỘT tổ
    // hợp (đủ ba) — cùng hạng lỗi «quần thể thử» với `titleCase`. Bất biến ở
    // đây là CẤU TRÚC («không câu nào mời rời bài»), không phải một chuỗi cụ
    // thể, nên nó vẫn đỏ nếu ai đó viết lại lời theo kiểu khác.
    final d = loadSyntheticDoc();
    final views = WorkspaceView.values;
    for (var mask = 0; mask < 1 << 3; mask++) {
      final seen = {
        for (var i = 0; i < views.length; i++)
          if (mask & (1 << i) != 0) views[i],
      };
      final n = nextActionFor(doc: d, seen: seen);
      for (final text in [n.label, n.reason]) {
        expect(text.toLowerCase(), isNot(contains('mục lục')),
            reason: 'seen=$seen ⇒ «$text» mời trẻ rời bài');
        expect(text.toLowerCase(), isNot(contains('bài khác')),
            reason: 'seen=$seen ⇒ «$text» mời trẻ rời bài');
      }
      expect(n.reason, isNot(contains('đã đi qua')),
          reason: 'seen=$seen ⇒ dấu vết MỞ TAB được kể như đã HỌC');
    }
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
