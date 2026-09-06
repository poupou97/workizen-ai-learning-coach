/// ⭐ Concept «05 Home» — dải SẮP TỚI: các môn trong thời khoá biểu **từ NGÀY
/// MAI trở đi** (Founder chốt: hôm nay KHÔNG thuộc «sắp tới», hôm nay đã có
/// tầng «HÔM NAY» riêng).
///
/// ⭐⭐ HAI THỨ CONCEPT CÓ MÀ DỮ LIỆU KHÔNG CÓ — và vì sao không bịa:
///
/// 1. **Tên bài** («Luyện từ và câu», «Sự sinh sản»). Thời khoá biểu chỉ biết
///    MÔN. Bất biến F4 của WAL-96 cấm đúng phép suy này: «Thứ Ba tiết 1 = Toán»
///    KHÔNG cho phép nói «mai cô dạy Bài 5». Muốn có tên bài thì phải có nguồn
///    thật (giáo án trường, phụ huynh nhập) — và khi đó nó là DỮ LIỆU KHÁC.
///
/// 2. **Giờ đồng hồ** («08:00», «09:30»). `TimetableEntry` có `period` (tiết
///    thứ mấy), không có giờ. Trường học khác nhau vào học khác giờ. Nên thẻ
///    nói **«Tiết 1»** — thứ có thật — thay vì một giờ bịa trông đáng tin.
///
/// Thẻ vì thế nói đúng ba điều nó biết: THỨ · NGÀY · MÔN (+ tiết).
library;

import '../../core/store/timetable.dart';

/// Một ngày sắp tới trong thời khoá biểu.
class UpcomingDay {
  const UpcomingDay({
    required this.date,
    required this.subjectIds,
    required this.firstPeriod,
  });

  final DateTime date;

  /// Môn của ngày đó, theo thứ tự tiết, không lặp.
  final List<String> subjectIds;

  /// Tiết đầu tiên trong ngày — để thẻ nói «Tiết 1» thay vì một giờ bịa.
  final int firstPeriod;

  int get weekday => date.weekday;
}

/// Các ngày học sắp tới, **bắt đầu từ NGÀY MAI**.
///
/// [horizonDays] là số ngày lịch nhìn tới (mặc định 7 = trọn một tuần kể từ
/// mai). Ngày không có tiết nào bị bỏ qua — không dựng thẻ rỗng.
///
/// Không có thời khoá biểu ⇒ rỗng. Rỗng là trạng thái HỢP LỆ (F13): tầng UI
/// phải ẩn cả dải, không hiện một dải trống trông như đang hỏng.
List<UpcomingDay> upcomingDays(
  List<TimetableEntry> entries, {
  required DateTime today,
  int horizonDays = 7,
}) {
  if (entries.isEmpty || horizonDays < 1) return const [];
  final base = DateTime(today.year, today.month, today.day);
  final out = <UpcomingDay>[];
  for (var i = 1; i <= horizonDays; i++) {
    final day = base.add(Duration(days: i));
    final sameDay = [
      for (final e in entries)
        if (e.weekday == day.weekday) e,
    ]..sort((a, b) => a.period.compareTo(b.period));
    if (sameDay.isEmpty) continue;
    final subjects = <String>[];
    for (final e in sameDay) {
      if (!subjects.contains(e.subjectId)) subjects.add(e.subjectId);
    }
    out.add(
      UpcomingDay(
        date: day,
        subjectIds: subjects,
        firstPeriod: sameDay.first.period,
      ),
    );
  }
  return out;
}

const _weekdayShort = {
  DateTime.monday: 'Thứ Hai',
  DateTime.tuesday: 'Thứ Ba',
  DateTime.wednesday: 'Thứ Tư',
  DateTime.thursday: 'Thứ Năm',
  DateTime.friday: 'Thứ Sáu',
  DateTime.saturday: 'Thứ Bảy',
  DateTime.sunday: 'Chủ Nhật',
};

/// «Thứ Ba, 20/05» — đúng dạng concept, từ ngày THẬT.
String upcomingDateLabel(DateTime d) {
  final dd = d.day.toString().padLeft(2, '0');
  final mm = d.month.toString().padLeft(2, '0');
  return '${_weekdayShort[d.weekday]}, $dd/$mm';
}
