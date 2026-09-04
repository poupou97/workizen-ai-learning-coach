/// ⭐⭐ WAL-180 — PARENT SESSION SUMMARY: kể chuyện gần đây bằng ĐÚNG cùng
/// bằng chứng đã chiếu lên Learning Map cho trẻ (WAL-181).
///
/// ONE EVIDENCE TRUTH, MULTIPLE PROJECTIONS (Founder Order 2026-09-04 §20):
/// [learningMapStateFor] không đổi nghĩa ở đây — Parent đọc CÙNG state trẻ
/// đang thấy trên Learning Map, không phải một hệ tính riêng. Không phần
/// trăm, không điểm số — đúng nguyên tắc `explainConcept` (`ParentExplanation`)
/// đã có: tất định, có thể truy ngược, "chưa đủ bằng chứng" là câu trả lời
/// hợp lệ.
library;

import '../store/learning_session.dart';
import '../student/learning_evidence.dart';
import '../student/learning_map_state.dart';

/// Một bài gần đây trẻ có chạm tới — CHỈ những bài THẬT SỰ có lineage
/// (WAL-178/179). Sự kiện thiếu lineage (dữ liệu cũ) không tạo dòng nào —
/// im lặng đúng hơn là bịa một câu không truy ngược được.
class RecentLessonTouch {
  const RecentLessonTouch({
    required this.sourceDocumentId,
    required this.lessonNo,
    required this.state,
    required this.at,
  });

  final String sourceDocumentId;
  final int lessonNo;
  final LearningMapState state;

  /// Lần chạm GẦN NHẤT khớp bài này — để xếp thứ tự "gần đây" trung thực.
  final DateTime at;
}

/// Gom TOÀN BỘ session của một con thành danh sách bài đã chạm gần đây,
/// mới nhất trước. Hàm THUẦN — không đọc kho, không đồng hồ hệ thống.
List<RecentLessonTouch> recentLessonTouches(
  List<LearningSession> sessions, {
  int maxLessons = 3,
}) {
  final events = sessions.expand((s) => s.events).toList();
  final byLesson = <(String, int), List<LearningEvent>>{};
  for (final e in events) {
    final doc = e.sourceDocumentId;
    final no = e.lessonNo;
    if (doc == null || no == null) continue; // thiếu lineage ⇒ bỏ, không đoán
    byLesson.putIfAbsent((doc, no), () => []).add(e);
  }
  final out = [
    for (final entry in byLesson.entries)
      RecentLessonTouch(
        sourceDocumentId: entry.key.$1,
        lessonNo: entry.key.$2,
        state: learningMapStateFor(
            sourceDocumentId: entry.key.$1,
            lessonNo: entry.key.$2,
            allEvents: entry.value),
        at: entry.value.map((e) => e.at).reduce((a, b) => a.isAfter(b) ? a : b),
      ),
  ]..sort((a, b) => b.at.compareTo(a.at));
  return out.take(maxLessons).toList();
}

/// Câu kể cho phụ huynh — CÙNG trạng thái badge trẻ đang thấy, dịch sang câu
/// người lớn đọc được. [lessonTitle] `null` ⇒ dùng "Bài N" trần, không bịa
/// tên bài không có thật.
String parentLineFor(RecentLessonTouch t, {String? lessonTitle}) {
  final name = lessonTitle ?? 'Bài ${t.lessonNo}';
  return switch (t.state) {
    LearningMapState.independentEvidence => 'Con đã tự làm được $name.',
    LearningMapState.engaged =>
      'Con đã học cùng SAM ở $name — chưa có lần nào tự làm được ghi lại.',
    // unseen không thể xảy ra ở đây: touch chỉ tồn tại khi CÓ event khớp.
    LearningMapState.unseen => '',
  };
}
