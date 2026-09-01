/// WAL-53 — luật của màn Parent «Tối nay» giữ bằng widget test.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/student/concept_summary.dart';
import 'package:learning_coach/features/parent/parent_tonight_screen.dart';

void main() {
  Future<void> pump(WidgetTester tester, Widget screen) =>
      tester.pumpWidget(MaterialApp(home: screen));

  List<String> allTexts(WidgetTester tester) => [
        for (final w in tester.widgetList<Text>(find.byType(Text)))
          w.data ?? ''
      ];

  testWidgets('câu trạng thái là NGUYÊN VĂN của explainConcept + citation hiện',
      (tester) async {
    final s = buildDemoParentTonight();
    await pump(tester, s);
    // thông điệp claim-gated xuất hiện nguyên văn — UI không viết lại
    expect(find.text(s.explanation.message), findsOneWidget);
    for (final c in s.explanation.citations) {
      expect(find.textContaining(c.observation), findsWidgets);
    }
  });

  testWidgets('fixture demo KHÔNG được nói «vững» khi claim chưa mastered',
      (tester) async {
    final s = buildDemoParentTonight();
    expect(s.explanation.claim, isNot(ConceptClaim.mastered),
        reason: 'fixture: 1/3 ca có bằng chứng — không thể là mastered');
    await pump(tester, s);
    for (final t in allTexts(tester)) {
      // "chưa ... vững" / "nói là vững" là lời RÀO — cấm mỗi khẳng định trần
      final bad = RegExp(r'(?<!chưa[^.]{0,40})đã vững|con vững');
      expect(bad.hasMatch(t), isFalse, reason: 'khẳng định vượt claim: "$t"');
    }
  });

  testWidgets('đúng MỘT khuyến nghị hành động — không dashboard', (tester) async {
    await pump(tester, buildDemoParentTonight());
    expect(find.text('VIỆC CHO TỐI NAY · ~10 PHÚT'), findsOneWidget);
    expect(find.textContaining('Cùng con làm 1–2 bài'), findsOneWidget);
  });

  testWidgets('không mascot, không %, không điểm số, không so sánh',
      (tester) async {
    await pump(tester, buildDemoParentTonight());
    expect(find.byType(Image), findsNothing,
        reason: 'mascot cấm ở vùng claim (luật Hub)');
    for (final t in allTexts(tester)) {
      expect(t.contains('%'), isFalse, reason: 'cấm %: "$t"');
      expect(t.contains('điểm'), isFalse, reason: 'cấm điểm số: "$t"');
      expect(t.toLowerCase().contains('các bạn'), isFalse,
          reason: 'cấm so sánh với trẻ khác: "$t"');
    }
  });
}
