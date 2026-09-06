/// ⭐ Dải SẮP TỚI — từ NGÀY MAI trở đi, và chỉ nói điều thời khoá biểu biết.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/timetable.dart';
import 'package:learning_coach/features/mission/home_upcoming.dart';

TimetableEntry _e(int weekday, int period, String subject) => TimetableEntry(
  learnerId: 'na',
  weekday: weekday,
  period: period,
  subjectId: subject,
);

/// Thứ Hai 2026-09-07.
final _monday = DateTime(2026, 9, 7);

void main() {
  group('«SẮP TỚI» bắt đầu từ NGÀY MAI', () {
    test('⭐ NGÀY hôm nay KHÔNG lọt vào dải sắp tới', () {
      final got = upcomingDays([
        _e(DateTime.monday, 1, 'toan'), // hôm nay
        _e(DateTime.tuesday, 1, 'khtn'), // mai
      ], today: _monday);
      // Không thẻ nào mang NGÀY hôm nay.
      expect(
        got.any((d) => d.date == _monday),
        isFalse,
        reason: 'tiết của chính hôm nay lọt vào «sắp tới»',
      );
      expect(got.first.date, DateTime(2026, 9, 8));
      // Thứ Hai TUẦN SAU thì được — đó thật sự là sắp tới.
      expect(got.last.date, DateTime(2026, 9, 14));
    });

    test('ngày đầu tiên trả về đúng là NGÀY MAI, không phải hôm nay', () {
      final got = upcomingDays([
        _e(DateTime.tuesday, 1, 'khtn'),
      ], today: _monday);
      expect(got.first.date, DateTime(2026, 9, 8));
    });

    test('tuần lặp lại: đủ 7 ngày tới, mỗi ngày có tiết mới có thẻ', () {
      final got = upcomingDays([
        _e(DateTime.monday, 1, 'toan'),
        _e(DateTime.wednesday, 1, 'khtn'),
      ], today: _monday);
      // Từ mai (T3) tới hết 7 ngày: T4 (khtn) và T2 tuần sau (toan).
      expect(got.map((d) => d.weekday), [DateTime.wednesday, DateTime.monday]);
    });

    test('ngày không có tiết nào ⇒ KHÔNG dựng thẻ rỗng', () {
      final got = upcomingDays([
        _e(DateTime.friday, 1, 'toan'),
      ], today: _monday);
      expect(got.length, 1);
      expect(got.single.weekday, DateTime.friday);
    });
  });

  group('nội dung thẻ — chỉ điều dữ liệu biết', () {
    test('môn xếp theo TIẾT, không lặp', () {
      final got = upcomingDays([
        _e(DateTime.tuesday, 3, 'khtn'),
        _e(DateTime.tuesday, 1, 'toan'),
        _e(DateTime.tuesday, 2, 'toan'),
      ], today: _monday);
      expect(got.single.subjectIds, ['toan', 'khtn']);
      expect(got.single.firstPeriod, 1);
    });

    test('⭐⭐ F4 — UpcomingDay KHÔNG có chỗ nào để nhét TÊN BÀI hay GIỜ', () {
      final d = upcomingDays([
        _e(DateTime.tuesday, 1, 'toan'),
      ], today: _monday).single;
      // Giữ bằng KIỂU: cả lớp chỉ có ba thứ, không có `lessonTitle`, không có
      // `startTime`. Ai muốn thêm phải sửa test này và nói ra nguồn dữ liệu.
      expect(d.date, isA<DateTime>());
      expect(d.subjectIds, isA<List<String>>());
      expect(d.firstPeriod, isA<int>());
    });

    test('nhãn ngày đúng dạng concept «Thứ Ba, 08/09»', () {
      expect(upcomingDateLabel(DateTime(2026, 9, 8)), 'Thứ Ba, 08/09');
      expect(upcomingDateLabel(DateTime(2026, 9, 7)), 'Thứ Hai, 07/09');
    });
  });

  group('F13 — thời khoá biểu là TUỲ CHỌN', () {
    test('không có TKB ⇒ dải rỗng, không nổ', () {
      expect(upcomingDays(const [], today: _monday), isEmpty);
    });

    test('horizon 0 ⇒ rỗng', () {
      expect(
        upcomingDays(
          [_e(DateTime.tuesday, 1, 'toan')],
          today: _monday,
          horizonDays: 0,
        ),
        isEmpty,
      );
    });
  });
}
