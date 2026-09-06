/// ⭐ Lệnh 51 §7–§8 — LỚP → MÔN → SÁCH giải từ CATALOG THẬT, và
/// BOOK ≠ SUBJECT: nhiều tập của một môn KHÔNG được thành nhiều môn.
///
/// Test này đọc THẲNG `assets/pack/lesson-index-g{5,6}.json` — pack thật của
/// app, không phải mẫu dựng tay. Nếu ai đó đổi cách gom môn, hai lớp mà Founder
/// yêu cầu dựng trên máy (Na lớp 6 · Minh lớp 5) sẽ báo ngay tại đây.
library;

import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/features/subjects/grade_subjects.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';

LessonIndex _pack(int grade) {
  final f = File('assets/pack/lesson-index-g$grade.json');
  final idx = LessonIndex.fromJsonString(f.readAsStringSync());
  expect(idx, isNotNull, reason: 'pack lớp $grade không đọc được');
  return idx!;
}

void main() {
  group('§7 — môn giải từ catalog thật, không phải danh sách bịa', () {
    test('lớp 6 có KHTN và Ngữ văn; lớp 5 có Khoa học và Tiếng Việt', () {
      final g6 = gradeSubjectNames(_pack(6));
      final g5 = gradeSubjectNames(_pack(5));
      expect(g6, containsAll(['KHTN', 'Ngữ văn', 'Toán']));
      expect(g5, containsAll(['Khoa học', 'Tiếng Việt', 'Toán', 'LS&ĐL']));
    });

    test('hai lớp cho hai bộ môn KHÁC nhau — Na và Minh không thể trùng', () {
      final g6 = gradeSubjectNames(_pack(6)).toSet();
      final g5 = gradeSubjectNames(_pack(5)).toSet();
      expect(g6, isNot(equals(g5)));
      // Môn chỉ có ở cấp 2 không được lọt xuống lớp 5, và ngược lại.
      expect(g5, isNot(contains('KHTN')));
      expect(g5, isNot(contains('Ngữ văn')));
      expect(g6, isNot(contains('Khoa học')));
      expect(g6, isNot(contains('Tiếng Việt')));
    });

    test('mọi môn đều có ít nhất một cuốn sách thật đứng sau', () {
      for (final grade in [5, 6]) {
        for (final s in gradeSubjects(_pack(grade))) {
          expect(s.books, isNotEmpty, reason: '${s.subject} không có sách nào');
          for (final b in s.books) {
            expect(b.subject, s.subject);
          }
        }
      }
    });
  });

  group('§8 — BOOK ≠ SUBJECT', () {
    test('Toán Tập 1 + Tập 2 là MỘT môn «Toán», không phải hai', () {
      for (final grade in [5, 6]) {
        final subs = gradeSubjects(_pack(grade));
        final toan = subs.where((s) => s.subject == 'Toán').toList();
        expect(toan.length, 1, reason: 'lớp $grade tách Toán thành nhiều môn');
        expect(
          toan.single.books.length,
          greaterThan(1),
          reason: 'lớp $grade: Toán chỉ có một cuốn — mẫu thử không còn đúng',
        );
      }
    });

    test('số MÔN nhỏ hơn số CUỐN — chuẩn hoá thật sự có gom', () {
      for (final grade in [5, 6]) {
        final idx = _pack(grade);
        expect(
          gradeSubjects(idx).length,
          lessThan(idx.books.length),
          reason: 'lớp $grade: gom môn không làm gì cả',
        );
      }
    });

    test('không tên môn nào lặp lại', () {
      for (final grade in [5, 6]) {
        final names = gradeSubjectNames(_pack(grade));
        expect(names.toSet().length, names.length);
      }
    });

    test('không tên môn nào mang nhãn tập («Tập 1», «Tập 2»)', () {
      for (final grade in [5, 6]) {
        for (final n in gradeSubjectNames(_pack(grade))) {
          expect(n.contains('Tập'), isFalse, reason: '«$n» mang nhãn tập');
        }
      }
    });

    test('Tập 1 đứng trước Tập 2 trong mỗi môn', () {
      for (final s in gradeSubjects(_pack(5))) {
        final vols = [
          for (final b in s.books) b.volume,
        ].whereType<int>().toList();
        final sorted = [...vols]..sort();
        expect(vols, sorted, reason: '${s.subject} xếp sai thứ tự tập');
      }
    });
  });

  group('thứ tự ổn định — TKB sinh ra phải tái lập được', () {
    test('gọi hai lần cho cùng một pack ⇒ cùng thứ tự môn', () {
      expect(gradeSubjectNames(_pack(6)), gradeSubjectNames(_pack(6)));
    });
  });
}
