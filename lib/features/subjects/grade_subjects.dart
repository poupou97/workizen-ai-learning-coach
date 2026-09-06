/// ⭐ Lệnh 51 §7–§8 — LỚP → MÔN → SÁCH, giải từ CATALOG THẬT.
///
/// «Không hardcode một danh sách giả nếu catalog thật đã tồn tại» (§7). Nguồn
/// duy nhất ở đây là `assets/pack/lesson-index-g{N}.json` — cùng cái pack mà
/// Kho sách và Môn học đang đọc. Không có bảng môn viết tay nào.
///
/// ⭐⭐ §8 — BOOK ≠ SUBJECT. Một môn có thể có nhiều cuốn: Tập 1/Tập 2, và về
/// sau SGK/SBT/SGV. Chúng KHÔNG được thành nhiều môn. Gom theo `BookRef.subject`
/// — trường CÓ SẴN trong pack, không suy từ tên file, không tách theo tập.
///
///   Lớp 5: 15 cuốn → 12 môn   (Toán Tập 1 + Tập 2 = MỘT môn «Toán»)
///   Lớp 6: 13 cuốn → 10 môn
///
/// ⭐⭐⭐ KHÔNG rẽ nhánh theo TÊN môn. `subject_id.dart` đã ghi vì sao: một
/// `switch` theo tên môn làm bằng chứng của trẻ bị ghi sai môn khi thêm môn
/// mới, mà không ai báo. Ở đây môn chỉ được ĐẾM và XẾP, không được phân loại.
library;

import 'lesson_index.dart';

/// Một môn của một lớp, kèm những cuốn thuộc về nó.
class GradeSubject {
  const GradeSubject({required this.subject, required this.books});

  final String subject;

  /// Mọi cuốn của môn này — nhiều tập là NHIỀU CUỐN, vẫn MỘT môn.
  final List<BookRef> books;

  /// Tổng số bài BẮT ĐƯỢC trong pack. ⚠️ Đây là ĐỘ PHỦ corpus, KHÔNG phải số
  /// tiết trong tuần và KHÔNG phải tiến độ của trẻ. Đừng dùng nó để suy tần
  /// suất môn — xem `timetable_generator.dart` để biết vì sao phép suy ấy sai.
  int get lessonCount {
    var n = 0;
    for (final b in books) {
      n += b.lessonCount;
    }
    return n;
  }
}

/// Môn của lớp này, xếp theo bảng chữ cái tiếng Việt (ổn định giữa các lần
/// chạy — TKB sinh ra phải tái lập được, nên thứ tự đầu vào không được đổi).
List<GradeSubject> gradeSubjects(LessonIndex index) {
  final bySubject = <String, List<BookRef>>{};
  for (final b in index.books) {
    bySubject.putIfAbsent(b.subject, () => <BookRef>[]).add(b);
  }
  final names = bySubject.keys.toList()..sort();
  return [
    for (final s in names)
      GradeSubject(
        subject: s,
        books: bySubject[s]!
          // Tập 1 trước Tập 2; sách không chia tập giữ nguyên thứ tự.
          ..sort((a, b) => (a.volume ?? 0).compareTo(b.volume ?? 0)),
      ),
  ];
}

/// Chỉ TÊN môn — đầu vào cho `generateTimetable` và cho màn TKB.
List<String> gradeSubjectNames(LessonIndex index) => [
  for (final s in gradeSubjects(index)) s.subject,
];
