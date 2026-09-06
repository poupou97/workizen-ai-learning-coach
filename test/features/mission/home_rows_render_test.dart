/// ⭐ Ba dải ngang phải VẼ ĐÚNG thứ dữ liệu đưa vào — bìa sách thật, tên môn
/// thật (không phải mã), ảnh cắt thật.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/timetable.dart';
import 'package:learning_coach/features/mission/home_cards.dart';
import 'package:learning_coach/features/mission/home_upcoming.dart';
import 'package:learning_coach/features/mission/mission_center_screen.dart';
import 'package:learning_coach/features/mission/mission_data.dart';

Future<void> _pump(WidgetTester t, Widget w) async {
  t.view.physicalSize = const Size(1080, 3000);
  t.view.devicePixelRatio = 3.0;
  addTearDown(t.view.resetPhysicalSize);
  addTearDown(t.view.resetDevicePixelRatio);
  await t.pumpWidget(MaterialApp(home: w));
  await t.pump();
}

void main() {
  testWidgets('⭐ ô môn dùng BÌA SÁCH thật khi có coverAsset', (t) async {
    await _pump(
      t,
      MissionCenterScreen(
        data: buildDemoMission(now: DateTime(2026, 9, 7, 19)),
        subjectChips: const [
          HomeSubjectChip(
            subject: 'Công nghệ',
            hasSamLesson: false,
            coverAsset: 'covers/06-sgk-cong-nghe-6.webp',
          ),
        ],
      ),
    );
    final img = t.widget<Image>(
      find.descendant(
        of: find.byKey(MissionCenterScreen.subjectRowKey),
        matching: find.byType(Image),
      ),
    );
    expect(
      (img.image as AssetImage).assetName,
      'assets/pack/covers/06-sgk-cong-nghe-6.webp',
    );
  });

  testWidgets('không có bìa ⇒ chữ cái đầu, KHÔNG bịa ảnh khác', (t) async {
    await _pump(
      t,
      MissionCenterScreen(
        data: buildDemoMission(now: DateTime(2026, 9, 7, 19)),
        subjectChips: const [
          HomeSubjectChip(subject: 'Toán', hasSamLesson: true),
        ],
      ),
    );
    expect(
      find.descendant(
        of: find.byKey(MissionCenterScreen.subjectRowKey),
        matching: find.byType(Image),
      ),
      findsNothing,
    );
    expect(find.text('T'), findsOneWidget);
  });

  testWidgets('⭐⭐ SẮP TỚI hiện TÊN môn, không phải MÃ', (t) async {
    final entries = [
      const TimetableEntry(
        learnerId: 'na',
        weekday: DateTime.tuesday,
        period: 1,
        subjectId: 'ngu-van',
      ),
    ];
    await _pump(
      t,
      MissionCenterScreen(
        data: buildDemoMission(now: DateTime(2026, 9, 7, 19)),
        upcoming: upcomingDays(entries, today: DateTime(2026, 9, 7)),
        subjectLabelOf: (id) => id == 'ngu-van' ? 'Ngữ văn' : id,
      ),
    );
    expect(find.textContaining('Ngữ văn'), findsWidgets);
    expect(
      find.textContaining('ngu-van'),
      findsNothing,
      reason: 'mã môn lọt ra màn hình trẻ đọc',
    );
  });

  testWidgets('không tra được tên ⇒ giữ MÃ trần, không bịa tên', (t) async {
    final entries = [
      const TimetableEntry(
        learnerId: 'na',
        weekday: DateTime.tuesday,
        period: 1,
        subjectId: 'mon-la',
      ),
    ];
    await _pump(
      t,
      MissionCenterScreen(
        data: buildDemoMission(now: DateTime(2026, 9, 7, 19)),
        upcoming: upcomingDays(entries, today: DateTime(2026, 9, 7)),
      ),
    );
    expect(find.textContaining('mon-la'), findsOneWidget);
  });
}
