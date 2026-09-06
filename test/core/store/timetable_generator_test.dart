/// ⭐ Lệnh 51 §9 — «RANDOM ≠ CHAOTIC». Random phải tái lập được bằng seed, và
/// phải có ràng buộc: mỗi môn có chỗ, không dồn một môn vào một ngày, không
/// bịa ra môn không có trong lớp.
///
/// §14 — TIMETABLE ENTRY != LEARNING SESSION: test cuối giữ điều đó bằng KIỂU.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/timetable.dart';
import 'package:learning_coach/core/store/timetable_generator.dart';

/// Môn THẬT của lớp 6 trong pack (13 cuốn → 10 môn).
const _g6 = [
  'Công nghệ',
  'GDTC',
  'HĐTN-HN',
  'KHTN',
  'Mĩ thuật',
  'Ngữ văn',
  'Tin học',
  'Tiếng Anh',
  'Toán',
  'Âm nhạc',
];

/// Môn THẬT của lớp 5 (15 cuốn → 12 môn).
const _g5 = [
  'Công nghệ',
  'GDTC',
  'HĐTN',
  'Khoa học',
  'LS&ĐL',
  'Tin học',
  'Tiếng Anh',
  'Tiếng Hàn',
  'Tiếng Việt',
  'Toán',
  'Âm nhạc',
  'Đạo đức',
];

List<TimetableEntry> _gen(
  List<String> subjects, {
  int seed = 12345,
  String learner = 'na',
  int days = 5,
  int slots = 4,
}) => generateTimetable(
  learnerId: learner,
  subjects: subjects,
  seed: seed,
  daysPerWeek: days,
  slotsPerDay: slots,
);

void main() {
  group('§9 — seed tái lập được', () {
    test('cùng seed ⇒ CÙNG thời khoá biểu, từng tiết một', () {
      final a = _gen(_g6, seed: 12345);
      final b = _gen(_g6, seed: 12345);
      expect(a.length, b.length);
      for (var i = 0; i < a.length; i++) {
        expect(a[i].weekday, b[i].weekday);
        expect(a[i].period, b[i].period);
        expect(a[i].subjectId, b[i].subjectId);
      }
    });

    test('seed khác ⇒ thời khoá biểu khác (không phải hằng số trá hình)', () {
      final a = _gen(_g6, seed: 12345);
      final b = _gen(_g6, seed: 999);
      final sa = [for (final e in a) '${e.weekday}.${e.period}=${e.subjectId}'];
      final sb = [for (final e in b) '${e.weekday}.${e.period}=${e.subjectId}'];
      expect(sa, isNot(equals(sb)));
    });
  });

  group('§9 — ràng buộc', () {
    test('đủ đúng số tiết', () {
      expect(_gen(_g6, days: 5, slots: 4).length, 20);
      expect(_gen(_g6, days: 6, slots: 5).length, 30);
    });

    test('mỗi môn của lớp xuất hiện ít nhất một lần khi còn chỗ', () {
      for (final seed in [1, 7, 12345, 90210]) {
        final got = {for (final e in _gen(_g6, seed: seed)) e.subjectId};
        expect(got, containsAll(_g6), reason: 'seed $seed bỏ sót môn');
      }
    });

    test(
      'không môn nào bị lặp trong CÙNG một ngày khi số tiết còn cho phép',
      () {
        for (final seed in [1, 7, 12345, 90210]) {
          final byDay = <int, List<String>>{};
          for (final e in _gen(_g6, seed: seed)) {
            byDay.putIfAbsent(e.weekday, () => []).add(e.subjectId);
          }
          for (final entry in byDay.entries) {
            expect(
              entry.value.toSet().length,
              entry.value.length,
              reason: 'seed $seed, thứ ${entry.key} có môn trùng',
            );
          }
        }
      },
    );

    test('KHÔNG bịa môn ngoài danh sách của lớp', () {
      for (final e in _gen(_g5)) {
        expect(_g5, contains(e.subjectId));
      }
      // Lớp 5 có Tiếng Việt/Khoa học; lớp 6 có Ngữ văn/KHTN — không lẫn nhau.
      final g5 = {for (final e in _gen(_g5)) e.subjectId};
      expect(g5, isNot(contains('KHTN')));
      expect(g5, isNot(contains('Ngữ văn')));
    });

    test('tiết đánh số từ 1 và liên tục trong mỗi ngày', () {
      final byDay = <int, List<int>>{};
      for (final e in _gen(_g6)) {
        byDay.putIfAbsent(e.weekday, () => []).add(e.period);
      }
      for (final periods in byDay.values) {
        periods.sort();
        expect(periods.first, 1);
        for (var i = 0; i < periods.length; i++) {
          expect(periods[i], i + 1);
        }
      }
    });

    test('mọi tiết mang ĐÚNG learnerId được truyền vào', () {
      for (final e in _gen(_g6, learner: 'minh')) {
        expect(e.learnerId, 'minh');
      }
    });
  });

  group('biên', () {
    test('không có môn ⇒ thời khoá biểu rỗng, không nổ', () {
      expect(_gen(const []), isEmpty);
    });

    test('nhiều môn hơn số tiết ⇒ cắt bớt, không nhân bản, không nổ', () {
      final got = _gen(_g5, days: 2, slots: 2); // 4 tiết, 12 môn
      expect(got.length, 4);
      expect({for (final e in got) e.subjectId}.length, 4);
    });

    test('một môn duy nhất ⇒ được phép lặp (số tiết ép phải)', () {
      final got = _gen(const ['Toán'], days: 2, slots: 2);
      expect(got.length, 4);
      expect(got.every((e) => e.subjectId == 'Toán'), isTrue);
    });
  });

  group('§14 — TKB không sinh ra việc học', () {
    test(
      'TimetableEntry không mang bài, không mang tiến độ, không bằng chứng',
      () {
        final e = _gen(_g6).first;
        final json = e.toJson();
        expect(json.keys.toSet(), {
          'learnerId',
          'weekday',
          'period',
          'subjectId',
        });
        // Không có chỗ nào để nhét «đã học», «đã hiểu», «lessonId» vào — bất
        // biến giữ bằng KIỂU, không bằng lời hứa.
      },
    );
  });
}
