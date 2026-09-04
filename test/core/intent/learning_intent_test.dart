/// ⭐ WAL-175 — SAM ĐỀ NGHỊ ý định, và KHÔNG BỊA khi không có căn cứ.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/intent/learning_intent.dart';
import 'package:learning_coach/core/store/timetable.dart';

const _all = {
  LearningIntent.prepare,
  LearningIntent.review,
  LearningIntent.practice,
  LearningIntent.lookup,
};

/// Thứ Năm 2026-09-03 ⇒ mai là thứ Sáu (weekday 5).
final _now = DateTime(2026, 9, 3);

List<TimetableEntry> _tt(String subjectId, int weekday) => [
      TimetableEntry(
          learnerId: 'l', weekday: weekday, period: 1, subjectId: subjectId)
    ];

void main() {
  test('⭐⭐ KHÔNG có căn cứ ⇒ KHÔNG đề nghị (fail closed, không bịa lý do)', () {
    expect(proposeIntent(subject: 'Khoa học', now: _now, available: _all),
        isNull,
        reason: '⭐⭐ đột biến trả một ý định mặc định ⇒ đỏ. SAM phải HỎI, '
            'không đoán hộ.');
  });

  test('⭐ mai có tiết ⇒ đề nghị CHUẨN BỊ, kèm lý do đọc được', () {
    final p = proposeIntent(
        subject: 'Khoa học',
        now: _now,
        available: _all,
        timetable: _tt('khoa-hoc', DateTime.friday));
    expect(p, isNotNull);
    expect(p!.intent, LearningIntent.prepare);
    expect(p.signal, IntentSignal.timetableTomorrow);
    expect(p.reason.trim(), isNotEmpty);
  });

  test('⭐ tiết NGÀY KHÁC không kích hoạt đề nghị', () {
    expect(
        proposeIntent(
            subject: 'Khoa học',
            now: _now,
            available: _all,
            timetable: _tt('khoa-hoc', DateTime.monday)),
        isNull,
        reason: '⭐ đột biến bỏ so ngày ⇒ đỏ');
  });

  test('⭐ môn KHÁC trong thời khoá biểu không kích hoạt', () {
    expect(
        proposeIntent(
            subject: 'Khoa học',
            now: _now,
            available: _all,
            timetable: _tt('toan', DateTime.friday)),
        isNull);
  });

  test('⭐⭐ BẰNG CHỨNG thắng thời khoá biểu (đúng thứ tự ưu tiên §10)', () {
    final p = proposeIntent(
        subject: 'Khoa học',
        now: _now,
        available: _all,
        reviewDue: true,
        timetable: _tt('khoa-hoc', DateTime.friday));
    expect(p!.intent, LearningIntent.review,
        reason: '⭐⭐ đột biến để thời khoá biểu thắng bằng chứng ⇒ đỏ');
    expect(p.signal, IntentSignal.evidence);
  });

  test('⭐ chỉ đề nghị ý định bài này CÓ THẬT', () {
    final p = proposeIntent(
        subject: 'Khoa học',
        now: _now,
        available: const {LearningIntent.lookup},
        timetable: _tt('khoa-hoc', DateTime.friday));
    expect(p, isNull, reason: '⭐ đột biến mời ý định bài không làm được ⇒ đỏ');
  });

  test('⭐ ý định hợp lệ suy từ HOẠT ĐỘNG CÓ THẬT, không từ tên môn', () {
    expect(
        availableIntents(
            hasExercises: false, hasAnyActivity: false, hasSource: true),
        {LearningIntent.lookup},
        reason: 'bài SAM chưa dạy được vẫn phải có lối «xem trong sách»');
    expect(
        availableIntents(
            hasExercises: true, hasAnyActivity: true, hasSource: false),
        _all);
  });
}
