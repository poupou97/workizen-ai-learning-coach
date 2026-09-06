/// LANE C (round 4, Golden Slice #2 — LS&ĐL 5 Bài 8) — NGÀY THÁNG CÓ KIỂU cho
/// `TimelineEvent.when`.
///
/// `TimelineEvent.when` là CHUỖI NGUYÊN VĂN trong ngoặc của sách («40 - 43»,
/// «248», «179 TCN», «542 – 602»). Sơ đồ vẽ chuỗi ấy; nhưng để KIỂM thứ tự
/// (TimelineValidator) hay so trước/sau thì cần số. Bộ đọc này TẤT ĐỊNH và
/// FAIL-CLOSED: chuỗi không đúng dạng ⇒ `null`, không đoán năm.
///
/// Dạng nhận: `<năm>` · `<năm> TCN` · `<năm> - <năm>` (gạch nối/gạch ngang,
/// khoảng trắng tuỳ ý) · `<năm> - <năm> TCN`. Không nhận thế kỉ («thế kỉ VI»),
/// không nhận «năm 544» (đó là mốc kể chuyện, luật `prose-dated-events-v1`
/// KHÔNG nâng thành sự kiện).
library;

import 'semantic_data.dart';

/// Kỉ nguyên: `tcn` = trước Công nguyên (sách viết «TCN»), `cn` = Công nguyên.
enum TimelineEra { tcn, cn }

/// Một mốc/khoảng thời gian đã đọc thành số. `start <= end` luôn đúng trên
/// trục thời gian có dấu (TCN âm) — `astronomical*` là số để so sánh.
class TimelineDate {
  const TimelineDate({
    required this.raw,
    required this.start,
    required this.end,
    required this.era,
  });

  /// Chuỗi sách nguyên văn (không sửa dấu gạch).
  final String raw;
  final int start, end;
  final TimelineEra era;

  bool get isRange => start != end;

  /// Năm để so sánh: TCN ⇒ âm (179 TCN → −179). Không có năm 0 trong lịch,
  /// nhưng để so thứ tự thì số âm là đủ và đơn giản.
  int get astronomicalStart => era == TimelineEra.tcn ? -start : start;
  int get astronomicalEnd => era == TimelineEra.tcn ? -end : end;

  static final _pattern = RegExp(
    r'^\s*(\d{1,4})\s*(?:[-–—]\s*(\d{1,4}))?\s*(TCN)?\s*$',
    caseSensitive: false,
  );

  /// Fail-closed: chuỗi lạ ⇒ `null`.
  static TimelineDate? parse(String? when) {
    if (when == null) return null;
    final m = _pattern.firstMatch(when);
    if (m == null) return null;
    final a = int.tryParse(m.group(1)!);
    final b = m.group(2) == null ? a : int.tryParse(m.group(2)!);
    if (a == null || b == null) return null;
    final era = m.group(3) == null ? TimelineEra.cn : TimelineEra.tcn;
    // TCN: «542 – 602 TCN» hiếm; nếu có thì năm lớn hơn là SỚM hơn — vẫn giữ
    // start = số đầu như sách viết, so sánh dùng astronomical*.
    if (era == TimelineEra.cn && b < a) return null; // «602 - 542» không phải khoảng hợp lệ
    return TimelineDate(raw: when, start: a, end: b, era: era);
  }

  /// Nhãn trẻ đọc: «năm 40 – 43», «năm 248», «năm 179 TCN».
  String get childLabel {
    final e = era == TimelineEra.tcn ? ' TCN' : '';
    return isRange ? 'năm $start – $end$e' : 'năm $start$e';
  }

  @override
  String toString() => 'TimelineDate($raw → $astronomicalStart..$astronomicalEnd)';
}

/// Sự kiện đã đọc ngày — cặp (sự kiện của sơ đồ, ngày có kiểu). `date == null`
/// ⇔ sách viết dạng SAM chưa đọc được ⇒ validator không dùng mốc đó.
class DatedEvent {
  const DatedEvent({required this.event, required this.date});
  final TimelineEvent event;
  final TimelineDate? date;

  bool get isDated => date != null;
}

/// Đọc ngày cho mọi mốc của một `TimelineSemantic` — thứ tự sách giữ nguyên.
List<DatedEvent> dateEvents(TimelineSemantic s) => [
  for (final e in s.events) DatedEvent(event: e, date: TimelineDate.parse(e.when)),
];
