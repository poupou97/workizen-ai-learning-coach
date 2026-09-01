/// WAL-96 — Thời khoá biểu như NGỮ CẢNH học tập (Founder Task Order §4).
///
/// ⭐ SAM KHÔNG phải ứng dụng quản lý thời khoá biểu. Thời khoá biểu tồn tại
/// để CẢI THIỆN gợi ý học — không hơn.
///
/// ⭐⭐ F4 — BẤT BIẾN CỨNG: **MÔN TRONG TKB ≠ BÀI HỌC CỤ THỂ.**
/// «Thứ Ba tiết 1 = Toán» KHÔNG cho phép suy ra «cô sẽ dạy Bài 17». Ở đây
/// TKB chỉ được làm MỘT việc: **xếp lại thứ tự** các hành động học đã HỢP LỆ
/// theo LearningStage. Nó không tạo ra hành động mới, không chọn bài, không
/// sinh dự đoán. Muốn biết bài cụ thể thì phải có nguồn tin cậy (giáo án
/// trường/GV, phụ huynh nhập, bài tập về nhà đã xác nhận) — và khi đó nó là
/// DỮ LIỆU KHÁC, không phải suy từ TKB.
library;

/// Một tiết trong tuần. Cố ý NGHÈO: chỉ đủ để biết «mai có môn gì».
class TimetableEntry {
  const TimetableEntry({
    required this.learnerId,
    required this.weekday, // DateTime.monday..sunday (1..7)
    required this.period, // tiết thứ mấy trong buổi (1..n)
    required this.subjectId,
  });

  final String learnerId;
  final int weekday;
  final int period;
  final String subjectId;

  Map<String, Object?> toJson() => {
        'learnerId': learnerId,
        'weekday': weekday,
        'period': period,
        'subjectId': subjectId,
      };

  static TimetableEntry? fromJson(Map<String, Object?> j) {
    final l = j['learnerId'], w = j['weekday'], p = j['period'],
        s = j['subjectId'];
    if (l is! String || w is! int || p is! int || s is! String) return null;
    if (w < 1 || w > 7 || p < 1) return null; // ngoài miền ⇒ từ chối, không kẹp
    return TimetableEntry(
        learnerId: l, weekday: w, period: p, subjectId: s);
  }
}

/// Các môn học của MỘT ngày, theo thứ tự tiết. Rỗng = không có TKB cho ngày đó
/// (hoàn toàn bình thường: TKB là TUỲ CHỌN — F13).
List<String> subjectsOn(List<TimetableEntry> entries, DateTime day) {
  final sameDay = [
    for (final e in entries)
      if (e.weekday == day.weekday) e
  ]..sort((a, b) => a.period.compareTo(b.period));
  final out = <String>[];
  for (final e in sameDay) {
    if (!out.contains(e.subjectId)) out.add(e.subjectId);
  }
  return out;
}

/// ⭐ Việc DUY NHẤT thời khoá biểu được làm với gợi ý học.
///
/// [candidates] là các hành động ĐÃ HỢP LỆ (do engine sinh ra theo
/// LearningStage + bằng chứng). Hàm này CHỈ sắp xếp lại: môn có trong TKB
/// của [day] lên trước, giữ nguyên thứ tự tương đối trong mỗi nhóm (ổn định).
///
/// Bất biến (test giữ):
/// - KHÔNG thêm, KHÔNG bớt phần tử — tập hợp trước và sau y hệt.
/// - Không TKB ⇒ trả về nguyên trạng (app chạy y như chưa từng có tính năng).
List<T> prioritiseByTimetable<T>(
  List<T> candidates, {
  required List<TimetableEntry> entries,
  required DateTime day,
  required String Function(T) subjectOf,
}) {
  final todays = subjectsOn(entries, day);
  if (todays.isEmpty) return List<T>.from(candidates);
  final inTimetable = <T>[], rest = <T>[];
  for (final c in candidates) {
    (todays.contains(subjectOf(c)) ? inTimetable : rest).add(c);
  }
  return [...inTimetable, ...rest];
}
