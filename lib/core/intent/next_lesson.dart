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
