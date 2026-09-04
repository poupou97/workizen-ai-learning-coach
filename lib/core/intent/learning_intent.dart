/// ⭐ LEARNING INTENT — «con muốn đạt được gì lúc này».
///
/// Thuộc về NGƯỜI HỌC, không thuộc về nội dung. Đây là chiều đã thiếu suốt: mã
/// có `LearningAgenda` giải được «hôm nay làm gì», nhưng luồng của trẻ **vứt nó
/// đi ở cửa giá sách** — vào bằng lối nào thì cũng ra cùng một trải nghiệm
/// (Convergence §25).
///
/// Từ `LEARNING MODE` đã bị bỏ khỏi ngôn ngữ chung: nó trùng với INTENT.
///
/// LUẬT RÀNG BUỘC (Convergence, tranh luận #2):
/// - Trải nghiệm chỉ chạy khi ràng buộc đủ: `activity` + `intent`.
/// - Chiều thiếu do SAM giải, **kèm lý do nhìn thấy được**.
/// - Trẻ đổi được mọi chiều đã ràng buộc.
/// - ⭐ **Fail closed**: không có căn cứ THẬT ⇒ `null` ⇒ tầng UI phải HỎI,
///   không được đoán hộ.
library;

import '../curriculum/subject_id.dart';
import '../store/timetable.dart';

enum LearningIntent {
  /// «Mai có tiết này» — quan sát, dự đoán, biết điều cần chú ý trên lớp.
  /// KHÔNG dạy trước bài của cô, KHÔNG kiểm tra.
  prepare,

  /// «Cô dạy rồi» — nhớ lại, giải thích, làm thử, bắt lỗi hiểu sai.
  review,

  /// «Con có bài tập» — làm bài có thang hỗ trợ.
  practice,

  /// «Xem trong sách» — tra cứu. Sinh TRACE, **không** sinh EVIDENCE.
  lookup,
}

/// Vì sao SAM đề nghị ý định này. Không có action câm — mọi đề nghị phải truy
/// được về một tín hiệu có thật.
enum IntentSignal {
  /// Đến hạn ôn / có chỗ vướng có bằng chứng.
  evidence,

  /// Thời khoá biểu: mai có tiết môn này.
  timetableTomorrow,

  /// Bài đang làm dở.
  inProgress,
}

class IntentProposal {
  const IntentProposal({
    required this.intent,
    required this.reason,
    required this.signal,
  });

  final LearningIntent intent;

  /// Câu trẻ đọc được. Đề nghị nào không nêu được lý do thì không được hiện.
  final String reason;
  final IntentSignal signal;
}

/// Ý định nào là hợp lệ cho bài này — suy từ HOẠT ĐỘNG CÓ THẬT, không phải từ
/// tên môn. Bài không có bài tập thì không mời trẻ «làm bài tập».
Set<LearningIntent> availableIntents({
  required bool hasExercises,
  required bool hasAnyActivity,
  required bool hasSource,
}) =>
    {
      if (hasAnyActivity) LearningIntent.prepare,
      if (hasAnyActivity) LearningIntent.review,
      if (hasExercises) LearningIntent.practice,
      // Tra cứu luôn mời được khi có gì đó để xem — kể cả khi SAM chưa dạy
      // được bài này. Đây là lối ra tử tế thay cho một câu xin lỗi lặp lại.
      if (hasSource || hasAnyActivity) LearningIntent.lookup,
    };

/// SAM đề nghị ý định nào, và vì sao.
///
/// Thứ tự ưu tiên đúng bằng thứ tự của `LearningAgenda` (Convergence §10):
/// bằng chứng → thời khoá biểu → làm dở → **không có gì thì trả `null`**.
///
/// Thuần: không đọc đồng hồ, không I/O. `now` truyền vào để test được.
IntentProposal? proposeIntent({
  required String subject,
  required DateTime now,
  required Set<LearningIntent> available,
  List<TimetableEntry> timetable = const [],
  bool reviewDue = false,
  bool inProgress = false,
}) {
  // 1 · Bằng chứng thắng mọi thứ khác.
  if (reviewDue && available.contains(LearningIntent.review)) {
    return const IntentProposal(
      intent: LearningIntent.review,
      reason: 'Con còn vướng ở phần này — mình gặp lại nhé.',
      signal: IntentSignal.evidence,
    );
  }

  // 2 · Thời khoá biểu: mai có tiết môn này.
  if (_hasClassTomorrow(subject, now, timetable) &&
      available.contains(LearningIntent.prepare)) {
    return const IntentProposal(
      intent: LearningIntent.prepare,
      reason: 'Mai lớp con có tiết này.',
      signal: IntentSignal.timetableTomorrow,
    );
  }

  // 3 · Đang làm dở.
  if (inProgress && available.contains(LearningIntent.review)) {
    return const IntentProposal(
      intent: LearningIntent.review,
      reason: 'Hôm trước con đang làm dở bài này.',
      signal: IntentSignal.inProgress,
    );
  }

  // 4 · ⭐ Không căn cứ ⇒ KHÔNG đề nghị. Tầng UI phải hỏi, không bịa lý do.
  return null;
}

bool _hasClassTomorrow(
    String subject, DateTime now, List<TimetableEntry> timetable) {
  if (timetable.isEmpty) return false;
  final tomorrow = DateTime(now.year, now.month, now.day + 1).weekday;
  // Thời khoá biểu lưu MÃ MÔN; mục lục giữ TÊN MÔN. Dùng lại đúng bộ chuyển của
  // WAL-173 thay vì so chuỗi — thêm môn không phải sửa dòng nào.
  final id = subjectIdOf(subject);
  return timetable.any((e) => e.weekday == tomorrow && e.subjectId == id);
}
