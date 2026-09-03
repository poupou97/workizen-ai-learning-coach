/// ⭐⭐ CỔNG KIẾN TRÚC (Founder) — «một môn thứ hai + một lớp thứ hai phải chạy
/// Book → Lesson → Learn → Evidence mà KHÔNG thêm lesson-specific screen/runtime
/// code».
///
/// Test này chạy trên FILE PACK THẬT, không phải fixture: cổng hỏi «dữ liệu có
/// tới được tay trẻ không», mà fixture thì luôn tới được. Chưa dựng pack ⇒ skip,
/// KHÔNG xanh giả.
///
/// Vì sao cổng từng KHÔNG qua (C-008): runtime đã trung tính từ WAL-166/168/170,
/// nhưng hoạt động mang `lesson: null` nên không bài nào mở được nó. Sửa nằm ở
/// tầng NẠP (WAL-172), không phải ở Dart — và đó chính là điều cổng sinh ra để
/// phát hiện.
library;

import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';

LessonIndex? _pack(int grade) {
  final f = File('assets/pack/lesson-index-g$grade.json');
  if (!f.existsSync()) {
    markTestSkipped('pack lớp $grade chưa dựng trên máy này');
    return null;
  }
  return LessonIndex.fromJsonString(f.readAsStringSync());
}

/// Bài nào có ÍT NHẤT một việc trẻ làm được, trong một cuốn cụ thể.
List<int> _openableLessons(LessonIndex idx, String book) {
  final out = <int>[];
  for (final books in idx.subjects.values) {
    for (final b in books) {
      if (b.sourceDocumentId != book) continue;
      for (final l in b.lessons) {
        if (idx.activitiesFor(book: book, lessonNo: l.no).isNotEmpty) {
          out.add(l.no);
        }
      }
    }
  }
  return out;
}

void main() {
  test('⭐⭐ MÔN THỨ HAI — Khoa học lớp 5 mở được bài và có việc THẬT để làm',
      () {
    final idx = _pack(5);
    if (idx == null) return;
    const book = '05-sgk-khoa-hoc-5';

    // Cuốn phải lên được giá sách (có bìa + định danh).
    expect(idx.books.map((b) => b.sourceDocumentId), contains(book),
        reason: 'không lên giá thì trẻ không vào được sách');

    final openable = _openableLessons(idx, book);
    expect(openable, isNotEmpty,
        reason: '⭐⭐ ĐÂY LÀ CỔNG: trước WAL-172 mọi thí nghiệm mang '
            '`lesson: null` nên 0 bài mở được, dù dữ liệu có thật.');

    // …và việc đó phải là THÍ NGHIỆM có nội dung nguyên văn từ sách.
    final acts = idx.activitiesFor(book: book, lessonNo: openable.first);
    final exp = acts.whereType<ExperimentActivity>().toList();
    expect(exp, isNotEmpty);
    expect(exp.first.experiment.chuanBi.trim(), isNotEmpty);
    expect(exp.first.experiment.tienHanh, isNotEmpty);
  });

  test('⭐⭐ LỚP THỨ HAI — Vật lí/Hoá học lớp 10 cũng mở được bài', () {
    final idx = _pack(10);
    if (idx == null) return;

    // Mỗi thí nghiệm lớp 10 phải neo được vào một bài CỦA CHÍNH CUỐN nó.
    expect(idx.khoaExperiments, isNotEmpty);
    for (final e in idx.khoaExperiments) {
      expect(e.lesson, isNotNull,
          reason: '⭐⭐ thí nghiệm ${e.title} không neo được vào bài nào ⇒ '
              'không bài nào mở được nó ⇒ cổng đỏ');
    }

    final books = {for (final e in idx.khoaExperiments) e.book};
    for (final b in books) {
      expect(_openableLessons(idx, b), isNotEmpty,
          reason: 'cuốn $b có thí nghiệm nhưng không bài nào mở được');
    }
  });

  test('⭐ KHÔNG có mã Dart riêng theo bài trên đường Book → Lesson → Learn',
      () {
    // Cổng nói về RUNTIME: màn dùng chung không được rẽ nhánh theo tên môn.
    // Ba tên đã bỏ ở WAL-166 không được quay lại.
    final src = File('lib/features/subjects/subject_home_screen.dart')
        .readAsLinesSync()
        .where((l) => !l.trimLeft().startsWith('//'))
        .join('\n');
    for (final banned in ['_isToan', '_isTv', '_isSu']) {
      expect(src.contains(banned), isFalse,
          reason: '⭐ $banned quay lại ⇒ mở bài lại hỏi TÊN MÔN thay vì hỏi '
              'DỮ LIỆU ⇒ môn thứ hai lại bị khoá ngoài');
    }
  });
}
