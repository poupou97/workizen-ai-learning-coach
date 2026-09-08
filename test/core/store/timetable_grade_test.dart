/// ⭐ THỜI KHOÁ BIỂU THUỘC VỀ MỘT LỚP.
///
/// Máy thật: hồ sơ đổi lớp 6 → 11, dải «Sắp tới» vẫn hiện «Khoa học tự nhiên»
/// cho học sinh lớp 11 — môn ấy chỉ có ở lớp 6–9. Và vì không cuốn nào của
/// lớp 11 khớp môn trong TKB, gợi ý bài của Home im lặng luôn.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/timetable.dart';

TimetableEntry _e(String subjectId, {int weekday = 1, int period = 1}) =>
    TimetableEntry(
      learnerId: 'l1',
      weekday: weekday,
      period: period,
      subjectId: subjectId,
    );

void main() {
  test('⭐ môn KHÔNG có ở lớp đang học bị loại khỏi chỗ trẻ đọc', () {
    final kept = entriesForSubjectIds(
      [_e('khtn'), _e('toan', period: 2), _e('tin-hoc', period: 3)],
      {'toan', 'tin-hoc', 'vat-li'},
    );
    expect(kept.map((e) => e.subjectId), ['toan', 'tin-hoc']);
  });

  test('lọc KHÔNG đụng vào kho: danh sách gốc giữ nguyên', () {
    final original = [_e('khtn'), _e('toan', period: 2)];
    entriesForSubjectIds(original, {'toan'});
    expect(original.length, 2);
    expect(original.first.subjectId, 'khtn');
  });

  test('chưa nạp mục lục (không biết lớp có môn gì) ⇒ không khẳng định gì', () {
    // Rỗng chứ không phải «giữ nguyên»: thà không hiện còn hơn hiện môn sai.
    expect(entriesForSubjectIds([_e('khtn')], const {}), isEmpty);
  });

  test('mọi môn đều thuộc lớp ⇒ giữ đủ', () {
    final all = [_e('toan'), _e('ngu-van', period: 2)];
    expect(entriesForSubjectIds(all, {'toan', 'ngu-van'}).length, 2);
  });
}
