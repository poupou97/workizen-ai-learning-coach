/// LANE C (round 4) — TimelineDate: đọc chuỗi «(năm)» của sách thành số, fail-closed.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/timeline_date.dart';

void main() {
  test('đọc được các dạng sách LS&ĐL 5 dùng: năm · khoảng · TCN', () {
    final a = TimelineDate.parse('40 - 43')!;
    expect((a.start, a.end, a.era, a.isRange), (40, 43, TimelineEra.cn, true));
    final b = TimelineDate.parse('248')!;
    expect((b.start, b.end, b.isRange), (248, 248, false));
    final c = TimelineDate.parse('542 – 602')!; // gạch ngang như sách in
    expect((c.start, c.end), (542, 602));
    final d = TimelineDate.parse('179 TCN')!;
    expect((d.era, d.astronomicalStart), (TimelineEra.tcn, -179));
    expect(TimelineDate.parse(' 938 ')!.astronomicalEnd, 938);
    expect(a.childLabel, 'năm 40 – 43');
    expect(d.childLabel, 'năm 179 TCN');
  });

  test('fail-closed: thế kỉ, «năm 544», khoảng ngược, chuỗi lạ ⇒ null', () {
    for (final s in ['thế kỉ VI', 'năm 544', '602 - 542', 'Bước đầu', '', '40-43-44']) {
      expect(TimelineDate.parse(s), isNull, reason: s);
    }
    expect(TimelineDate.parse(null), isNull);
  });

  test('so sánh thứ tự bằng năm thiên văn: TCN trước CN', () {
    final tcn = TimelineDate.parse('179 TCN')!;
    final cn = TimelineDate.parse('40 - 43')!;
    expect(tcn.astronomicalStart < cn.astronomicalStart, isTrue);
  });
}
