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
  // Bề ngang 360 dp như Nokia; chiều cao lớn để MỌI dải đều được dựng —
  // `ListView` chỉ dựng phần trong tầm nhìn, nên khung thấp làm finder trượt.
  t.view.physicalSize = const Size(720, 6000);
  t.view.devicePixelRatio = 2.0;
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

  group('⭐ Lệnh 53 §1/§3 — hình thái vật thể', () {
    testWidgets('bìa sách DỌC 3:4 và KHÔNG bị cắt vuông', (t) async {
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
      // ⛔ `BoxFit.cover` là đúng thứ lệnh 53 §1 cấm: nó cắt bìa cho vừa khung,
      // mất tên sách in trên bìa. `contain` giữ nguyên khung bìa.
      expect(img.fit, BoxFit.contain);

      final box = t.getSize(
        find
            .ancestor(of: find.byType(Image), matching: find.byType(Container))
            .first,
      );
      expect(
        box.width / box.height,
        closeTo(3 / 4, 0.02),
        reason: 'bìa phải DỌC ~3:4, không vuông',
      );
    });

    testWidgets('⭐⭐ ba dải KHÁC hình thái — ba chiều cao khác nhau', (t) async {
      final entries = [
        const TimetableEntry(
          learnerId: 'na',
          weekday: DateTime.tuesday,
          period: 1,
          subjectId: 'toan',
        ),
      ];
      await _pump(
        t,
        MissionCenterScreen(
          data: buildDemoMission(now: DateTime(2026, 9, 7, 19)),
          upcoming: upcomingDays(entries, today: DateTime(2026, 9, 7)),
          subjectChips: const [
            HomeSubjectChip(subject: 'Toán', hasSamLesson: true),
          ],
        ),
      );
      final sched = t.getSize(find.byKey(MissionCenterScreen.upcomingRowKey));
      final books = t.getSize(find.byKey(MissionCenterScreen.subjectRowKey));
      // Lịch NÉN hơn kệ sách — nhìn thoáng qua đã phân biệt được (§3).
      expect(sched.height, lessThan(books.height));
    });
  });
}
