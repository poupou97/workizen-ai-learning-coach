/// ⭐⭐ Lệnh 53 — DẤU VẾT «ĐÃ MỞ» KHÔNG ĐƯỢC THEO NGƯỜI HỌC SANG HỒ SƠ KHÁC.
///
/// Lỗi thật, đo trên Nokia: Na mở «Đọc» của Bài 17, đổi sang hồ sơ lớp 5, và
/// Home của em hiện «Đã mở: Đọc» cho chính bài ấy. `WorkspaceTrace.session` là
/// MỘT instance cho cả app, khoá theo bài chứ không theo người học.
///
/// Audit lệnh 51 kiểm TẦNG LƯU TRỮ và kết luận không rò — đúng, nhưng trace
/// này nằm trong BỘ NHỚ và không đi qua kho, nên nó lọt khỏi phép kiểm ấy.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/next_action.dart';
import 'package:learning_coach/features/lesson_workspace/workspace_trace.dart';

void main() {
  test('clear() xoá sạch dấu vết khi đổi hồ sơ', () {
    final trace = WorkspaceTrace();
    trace.markView('06-sgk-khoa-hoc-tu-nhien-6#17', WorkspaceView.read);
    expect(trace.opened('06-sgk-khoa-hoc-tu-nhien-6#17'), isTrue);
    expect(trace.viewsFor('06-sgk-khoa-hoc-tu-nhien-6#17'), isNotEmpty);

    trace.clear();

    expect(
      trace.opened('06-sgk-khoa-hoc-tu-nhien-6#17'),
      isFalse,
      reason: 'người học mới thừa hưởng «đã mở» của người trước',
    );
    expect(trace.viewsFor('06-sgk-khoa-hoc-tu-nhien-6#17'), isEmpty);
  });

  test('clear() trên trace rỗng không nổ', () {
    WorkspaceTrace().clear();
  });
}
