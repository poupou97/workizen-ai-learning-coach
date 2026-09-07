/// ⭐⭐ Lệnh 56 §P1 — THỜI KHOÁ BIỂU LÀ NGỮ CẢNH CỦA HOME.
///
/// «Home không được coi tất cả môn ngang nhau.» Tệp này trả lời đúng một câu:
/// **hôm nay và ngày mai con học môn gì** — rồi Home dùng nó để xếp lại thứ tự.
///
/// ⭐ BA ĐIỀU KHÔNG ĐƯỢC LÀM, giữ nguyên từ WAL-96 và lệnh 56 §P1:
/// - TIMETABLE SUBJECT ≠ SAM LESSON AVAILABLE. Có tiết Toán không có nghĩa là
///   có bài Toán để học; xếp lên trước KHÔNG được biến thành bịa bài.
/// - Thời khoá biểu chỉ **xếp lại** thứ tự các ứng viên ĐÃ HỢP LỆ. Nó không
///   thêm ứng viên, không mở rộng phạm vi lớp (§P1.5).
/// - Không sinh tiến độ / bằng chứng / mastery (§P3).
///
/// ⭐⭐ ĐỒNG HỒ ĐƯỢC TIÊM VÀO (§P5.1): mọi hàm ở đây nhận `now`, không hàm nào
/// gọi `DateTime.now()`. Test «hôm nay/ngày mai» vì thế không phụ thuộc ngày
/// CI chạy — và biên tuần (thứ Sáu → thứ Hai) kiểm được.
library;

import '../../core/curriculum/subject_id.dart';
import '../../core/store/timetable.dart';

/// Môn của hôm nay và của ngày mai, theo MÃ môn.
class TimetableContext {
  const TimetableContext({
    required this.todaySubjectIds,
    required this.tomorrowSubjectIds,
  });

  static const empty = TimetableContext(
    todaySubjectIds: [],
    tomorrowSubjectIds: [],
  );

  /// Mã môn hôm nay, theo thứ tự tiết, không lặp.
  final List<String> todaySubjectIds;

  /// Mã môn ngày mai — «ngày mai» là NGÀY LỊCH kế tiếp. Nếu ngày ấy không có
  /// tiết nào (chủ nhật chẳng hạn) thì rỗng: KHÔNG nhảy sang ngày học kế tiếp
  /// và tự gọi nó là «ngày mai» (§P5.1 — không bịa môn cho ngày không có).
  final List<String> tomorrowSubjectIds;

  bool get isEmpty => todaySubjectIds.isEmpty && tomorrowSubjectIds.isEmpty;

  /// Hạng ngữ cảnh của một môn: 0 = hôm nay, 1 = ngày mai, 2 = còn lại.
  int rankOfSubjectId(String subjectId) {
    if (todaySubjectIds.contains(subjectId)) return 0;
    if (tomorrowSubjectIds.contains(subjectId)) return 1;
    return 2;
  }

  /// Tiện cho nơi chỉ có TÊN môn (thẻ Home, ô giá sách).
  int rankOfSubject(String subject) => rankOfSubjectId(subjectIdOf(subject));
}

/// Dựng ngữ cảnh từ thời khoá biểu của MỘT người học.
///
/// [now] bắt buộc — xem ghi chú đồng hồ tiêm ở đầu tệp.
TimetableContext timetableContext(
  List<TimetableEntry> entries, {
  required DateTime now,
}) {
  if (entries.isEmpty) return TimetableContext.empty;
  final tomorrow = DateTime(
    now.year,
    now.month,
    now.day,
  ).add(const Duration(days: 1));
  return TimetableContext(
    todaySubjectIds: subjectsOn(entries, now),
    tomorrowSubjectIds: subjectsOn(entries, tomorrow),
  );
}
