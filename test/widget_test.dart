/// ⭐ WAL-51 — widget test màn HÔM NAY: luật hiển thị do TEST giữ.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/curriculum/skill_case.dart';
import 'package:learning_coach/features/mission/mission_center_screen.dart';
import 'package:learning_coach/features/mission/mission_data.dart';

void main() {
  final data = buildDemoMission(now: DateTime(2026, 9, 1, 19));

  Future<void> pump(WidgetTester t) async {
    await t.pumpWidget(MaterialApp(home: MissionCenterScreen(data: data)));
    await t.pump();
  }

  testWidgets('⭐ MỘT hành động kế tiếp + reason NGUYÊN VĂN của engine', (t) async {
    await pump(t);
    expect(data.decision.diagnosis, DiagnosticOutcome.caseTransitionGap,
        reason: 'fixture đi đường domain thật — vững ca lớp 4, chưa gặp ca mới');
    expect(find.text(data.decision.reason), findsOneWidget,
        reason: 'UI hiển thị reason của engine nguyên văn, không suy diễn thêm');
    expect(find.text('Bắt đầu'), findsOneWidget);
  });

  testWidgets('⭐⭐ CẤM %: không ký tự % nào trên toàn màn', (t) async {
    await pump(t);
    for (final w in t.widgetList<Text>(find.byType(Text))) {
      expect(w.data ?? '', isNot(contains('%')),
          reason: '⭐⭐ không con số nào giả vờ chính xác — luật hiển thị '
              'Decision 1, do widget test giữ');
    }
  });

  testWidgets('ôn tới hạn hiển thị dịu (không chữ đỏ hối thúc)', (t) async {
    await pump(t);
    expect(data.reviews, isNotEmpty,
        reason: 'fixture: bằng chứng 9 ngày trước, khoảng ôn 3 lần = ~28 ngày… '
            'kiểm bằng ReviewSchedule thật');
    expect(find.text('Tới lúc gặp lại rồi'), findsWidgets);
    expect(find.textContaining('quá hạn', findRichText: true), findsNothing);
  });

  testWidgets('⭐ dạng CHƯA THỬ được nêu TÊN — coverage nhìn thấy được', (t) async {
    await pump(t);
    expect(data.unobservedCaseNames, contains('hai mẫu số không chia hết cho nhau'));
    // ListView build lười — cuộn tới tile (đây cũng là smoke test cuộn của màn)
    await t.scrollUntilVisible(
        find.text('Mình chưa thử dạng này').first, 120,
        scrollable: find.byType(Scrollable).first);
    expect(find.textContaining('hai mẫu số không chia hết'), findsWidgets);
  });
}
