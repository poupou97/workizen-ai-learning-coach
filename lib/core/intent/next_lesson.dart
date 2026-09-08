/// ⭐⭐ WAL-176 (Missing #1) — GỢI Ý BÀI cho Home, KHÔNG hỏi tên môn.
///
/// `LearningAgenda` (WAL-102) phát tín hiệu cho các dòng chương trình sư phạm
/// đã có (`curriculaForLearner`) — hôm nay CHỈ có Toán 5 Bài 6. Với môn CHƯA
/// có `SliceCurriculum` (Khoa học, Vật lí…) nhưng CÓ hoạt động thật + thời
/// khoá biểu, Home vẫn phải đề nghị được — không chờ tới khi có chương trình
/// sư phạm đầy đủ cho từng môn.
///
/// ⭐ Đây KHÔNG thay thế `LearningAgenda`. Bằng chứng (review-due) vẫn thắng
/// — hàm này chỉ được gọi khi agenda không có gì khẩn (Convergence §10: bằng
/// chứng → thời khoá biểu → làm dở → không có gì).
///
/// Quét TOÀN BỘ `index.books`, không nhắc tên môn nào — thêm một môn có bìa +
/// hoạt động thật là tự động vào diện được đề nghị, không sửa hàm này.
library;

import '../../features/subjects/lesson_index.dart';
import '../store/timetable.dart';
import 'learning_intent.dart';

/// Gợi ý ở cấp BÀI — đủ để mở thẳng đúng trải nghiệm, không cần hỏi lại.
class HomeRecommendation {
  const HomeRecommendation({
    required this.sourceDocumentId,
    required this.subject,
    required this.lessonNo,
    required this.intent,
    required this.reason,
  });

  final String sourceDocumentId;
  final String subject;
  final int lessonNo;
  final LearningIntent intent;

  /// Câu trẻ đọc được — cùng luật với `IntentProposal.reason`: không có lý do
  /// thì không được đề nghị.
  final String reason;
}

/// Quét thời khoá biểu NGÀY MAI cho MỌI cuốn sách có thật, không hỏi tên môn
/// nào cụ thể. Dùng LẠI `proposeIntent` (WAL-175) cho phép so khớp môn/ngày —
/// một luật, một chỗ, không chép lại cách đọc TKB lần thứ hai. Trả về bài ĐẦU
/// TIÊN (theo thứ tự mục lục) mà `proposeIntent` thật sự đề nghị «Chuẩn bị» vì
/// tín hiệu THỜI KHOÁ BIỂU. Không có gì ⇒ `null` — Home tự nói không có,
/// không bịa đề nghị.
HomeRecommendation? nextBookRecommendation({
  required LessonIndex index,
  required DateTime now,
  required List<TimetableEntry> timetable,
}) {
  if (timetable.isEmpty) return null;

  for (final book in index.books) {
    final lessons = (index.subjects[book.subject] ?? const [])
        .where((b) => b.sourceDocumentId == book.sourceDocumentId)
        .expand((b) => b.lessons);

    for (final lesson in lessons) {
      final acts =
          index.activitiesFor(book: book.sourceDocumentId, lessonNo: lesson.no);
      if (acts.isEmpty) continue;

      final available = availableIntents(
        hasExercises: acts.whereType<ExerciseActivity>().isNotEmpty,
        hasAnyActivity: true,
        hasSource: true,
      );
      final proposal = proposeIntent(
        subject: book.subject,
        now: now,
        available: available,
        timetable: timetable,
      );
      if (proposal == null ||
          proposal.intent != LearningIntent.prepare ||
          proposal.signal != IntentSignal.timetableTomorrow) {
        continue;
      }

      return HomeRecommendation(
        sourceDocumentId: book.sourceDocumentId,
        subject: book.subject,
        lessonNo: lesson.no,
        intent: proposal.intent,
        reason:
            'Mai lớp con có tiết ${book.subject}. Xem trước Bài ${lesson.no} nhé.',
      );
    }
  }
  return null;
}


/// ⭐ GỢI Ý KHÔNG PHỤ THUỘC SAM — Home phải có việc thật để đề nghị kể cả khi
/// SAM chưa soạn bài nào cho lớp này.
///
/// Máy thật, lớp 11: 441 bài mở đọc được, mà Home chỉ nói «Chưa có bài học
/// SAM chuẩn bị sẵn cho lớp 11» rồi đưa mỗi nút «Mở giá sách». Trẻ không có
/// đường vào, dù nội dung đã có sẵn trên máy.
///
/// Thứ tự lấy KHÔNG tuỳ tiện — dùng đúng thứ hạng sản phẩm đã dùng cho giá
/// sách: môn có tiết HÔM NAY trước, rồi số bài mở được nhiều hơn, rồi tên môn
/// (để hai lần dựng không ra hai kết quả). Trong môn thì lấy bài ĐẦU TIÊN mở
/// được theo mục lục.
///
/// Không có bài nào mở được ⇒ `null`. Home nói thật là chưa có, không bịa.
HomeRecommendation? firstReadableRecommendation({
  required LessonIndex index,
  int Function(String subject)? subjectRank,
}) {
  final bySubject = <String, List<BookLessons>>{};
  index.subjects.forEach((subject, books) {
    bySubject[subject] = books;
  });
  final names = bySubject.keys.toList()
    ..sort((a, b) {
      final ra = subjectRank?.call(a) ?? 0;
      final rb = subjectRank?.call(b) ?? 0;
      if (ra != rb) return ra.compareTo(rb);
      final na = _openableIn(index, bySubject[a]!);
      final nb = _openableIn(index, bySubject[b]!);
      if (na != nb) return nb.compareTo(na);
      return a.compareTo(b);
    });
  for (final subject in names) {
    for (final book in bySubject[subject]!) {
      for (final lesson in book.lessons) {
        final acts =
            index.activitiesFor(book: book.sourceDocumentId, lessonNo: lesson.no);
        if (acts.isEmpty) continue;
        return HomeRecommendation(
          sourceDocumentId: book.sourceDocumentId,
          subject: subject,
          lessonNo: lesson.no,
          // «Xem trong sách» — đúng ngữ nghĩa: mở trang sách để đọc,
          // sinh TRACE chứ không sinh EVIDENCE. Không đội lốt bài dạy.
          intent: LearningIntent.lookup,
          reason: 'SAM chưa soạn bài cho lớp này, nhưng sách của con có sẵn '
              'trang để đọc.',
        );
      }
    }
  }
  return null;
}

int _openableIn(LessonIndex index, List<BookLessons> books) {
  var n = 0;
  for (final b in books) {
    for (final l in b.lessons) {
      if (index.activitiesFor(book: b.sourceDocumentId, lessonNo: l.no).isNotEmpty) {
        n++;
      }
    }
  }
  return n;
}
