/// WAL-96 — thời khoá biểu: ưu-tiên-hoá được, DỰ-ĐOÁN-BÀI thì không (F4).
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/timetable.dart';

const _mon = 1, _tue = 2;
final _tuesday = DateTime(2026, 9, 1); // thứ Ba
final _monday = DateTime(2026, 8, 31);

const _tt = [
  TimetableEntry(
      learnerId: 'l1', weekday: _tue, period: 1, subjectId: 'toan'),
  TimetableEntry(
      learnerId: 'l1', weekday: _tue, period: 2, subjectId: 'tieng-viet'),
  TimetableEntry(
      learnerId: 'l1', weekday: _mon, period: 1, subjectId: 'khoa-hoc'),
];

class _Action {
  const _Action(this.id, this.subject);
  final String id;
  final String subject;
}

void main() {
  test('môn trong ngày, theo thứ tự tiết', () {
    expect(subjectsOn(_tt, _tuesday), ['toan', 'tieng-viet']);
    expect(subjectsOn(_tt, _monday), ['khoa-hoc']);
    expect(subjectsOn(_tt, DateTime(2026, 9, 6)), isEmpty); // chủ nhật
  });

  test('⭐ F4: TKB CHỈ xếp lại thứ tự — không thêm, không bớt hành động nào', () {
    const actions = [
      _Action('a1', 'tieng-viet'),
      _Action('a2', 'khoa-hoc'),
      _Action('a3', 'toan'),
    ];
    final out = prioritiseByTimetable(actions,
        entries: _tt, day: _tuesday, subjectOf: (a) => a.subject);
    expect(out.map((a) => a.id), ['a1', 'a3', 'a2'],
        reason: 'môn có trong TKB hôm nay lên trước, thứ tự trong nhóm giữ nguyên');
    expect(out.length, actions.length);
    expect(out.map((a) => a.id).toSet(), {'a1', 'a2', 'a3'},
        reason: 'TẬP HỢP hành động không đổi — TKB không sinh việc mới, '
            'không loại việc nào (bài học vẫn do LearningStage + bằng chứng quyết định)');
  });

  test('không có TKB ⇒ app chạy y như chưa từng có tính năng này (F13)', () {
    const actions = [_Action('a1', 'toan'), _Action('a2', 'tieng-viet')];
    final out = prioritiseByTimetable(actions,
        entries: const [], day: _tuesday, subjectOf: (a) => a.subject);
    expect(out.map((a) => a.id), ['a1', 'a2']);
    final sunday = prioritiseByTimetable(actions,
        entries: _tt, day: DateTime(2026, 9, 6), subjectOf: (a) => a.subject);
    expect(sunday.map((a) => a.id), ['a1', 'a2']);
  });

  test('⭐ F4: API KHÔNG có đường nào trả về BÀI HỌC từ thời khoá biểu', () {
    // Toàn bộ bề mặt công khai của module: subjectsOn (trả MÔN) và
    // prioritiseByTimetable (xếp lại danh sách có sẵn). Không hàm nào nhận
    // hay trả lessonId — «Thứ Ba có Toán» không thể thành «cô dạy Bài 17».
    final subjects = subjectsOn(_tt, _tuesday);
    expect(subjects, everyElement(isA<String>()));
    expect(subjects.any((s) => s.contains('bai') || s.contains('lesson')),
        isFalse);
  });

  test('dữ liệu TKB hỏng bị TỪ CHỐI, không kẹp về biên', () {
    expect(
        TimetableEntry.fromJson(
            {'learnerId': 'l', 'weekday': 8, 'period': 1, 'subjectId': 's'}),
        isNull);
    expect(
        TimetableEntry.fromJson(
            {'learnerId': 'l', 'weekday': 2, 'period': 0, 'subjectId': 's'}),
        isNull);
    expect(
        TimetableEntry.fromJson(
            {'learnerId': 'l', 'weekday': 2, 'period': 1, 'subjectId': 'toan'}),
        isNotNull);
  });
}
