/// ⭐ Lệnh 56 §P1 + §P5.1 — ngữ cảnh «hôm nay / ngày mai», với ĐỒNG HỒ TIÊM.
///
/// Không test nào ở đây phụ thuộc ngày CI chạy.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/timetable.dart';
import 'package:learning_coach/features/mission/timetable_context.dart';

TimetableEntry _e(int weekday, int period, String subjectId) => TimetableEntry(
  learnerId: 'na',
  weekday: weekday,
  period: period,
  subjectId: subjectId,
);

/// 2026-09-07 là THỨ HAI; 2026-09-11 là THỨ SÁU.
final _monday = DateTime(2026, 9, 7, 8);
final _friday = DateTime(2026, 9, 11, 8);

void main() {
  final week = [
    _e(DateTime.monday, 1, 'toan'),
    _e(DateTime.monday, 2, 'khtn'),
    _e(DateTime.tuesday, 1, 'ngu-van'),
    _e(DateTime.friday, 1, 'tin-hoc'),
  ];

  group('hôm nay / ngày mai', () {
    test('thứ Hai ⇒ hôm nay Toán·KHTN, ngày mai Ngữ văn', () {
      final c = timetableContext(week, now: _monday);
      expect(c.todaySubjectIds, ['toan', 'khtn']);
      expect(c.tomorrowSubjectIds, ['ngu-van']);
    });

    test('môn xếp theo TIẾT, không lặp', () {
      final c = timetableContext([
        _e(DateTime.monday, 3, 'khtn'),
        _e(DateTime.monday, 1, 'toan'),
        _e(DateTime.monday, 2, 'toan'),
      ], now: _monday);
      expect(c.todaySubjectIds, ['toan', 'khtn']);
    });

    test(
      '⭐ biên tuần: thứ Sáu ⇒ ngày mai là THỨ BẢY, không nhảy sang thứ Hai',
      () {
        final c = timetableContext(week, now: _friday);
        expect(c.todaySubjectIds, ['tin-hoc']);
        // Thứ Bảy không có tiết ⇒ RỖNG. Không tự lấy môn thứ Hai rồi gọi là
        // «ngày mai» — đó là bịa (§P5.1).
        expect(c.tomorrowSubjectIds, isEmpty);
      },
    );

    test('không có thời khoá biểu ⇒ ngữ cảnh rỗng, không nổ', () {
      final c = timetableContext(const [], now: _monday);
      expect(c.isEmpty, isTrue);
      expect(c.rankOfSubjectId('toan'), 2);
    });
  });

  group('hạng ngữ cảnh', () {
    test('hôm nay 0 · ngày mai 1 · còn lại 2', () {
      final c = timetableContext(week, now: _monday);
      expect(c.rankOfSubjectId('toan'), 0);
      expect(c.rankOfSubjectId('khtn'), 0);
      expect(c.rankOfSubjectId('ngu-van'), 1);
      expect(c.rankOfSubjectId('tin-hoc'), 2);
    });

    test('tra được từ TÊN môn, qua đúng phép chuẩn hoá mã', () {
      final c = timetableContext([
        _e(DateTime.monday, 1, 'ngu-van'),
      ], now: _monday);
      expect(c.rankOfSubject('Ngữ văn'), 0);
      expect(c.rankOfSubject('Toán'), 2);
    });
  });

  group('⛔ thời khoá biểu KHÔNG được làm nhiều hơn việc xếp thứ tự', () {
    test(
      'ngữ cảnh chỉ mang MÃ MÔN — không bài, không tiến độ, không bằng chứng',
      () {
        final c = timetableContext(week, now: _monday);
        // Giữ bằng KIỂU: cả lớp chỉ có hai danh sách chuỗi. Không có trường nào
        // để nhét lessonId / progress / mastery vào (§P1, §P3).
        expect(c.todaySubjectIds, isA<List<String>>());
        expect(c.tomorrowSubjectIds, isA<List<String>>());
      },
    );
  });
}
