/// WAL-139 — polish states theo concept 13/14 NHƯNG doctrine-safe:
/// thang hiển thị mức ENGINE quyết; «Các bước con đã làm» trung thực; không %.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/adaptive/adaptive_engine.dart';
import 'package:learning_coach/core/curriculum/pedagogical_boundary.dart';
import 'package:learning_coach/core/knowledge/slice_curriculum.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/features/tutor/tutor_screen.dart';
import 'package:learning_coach/features/tutor/tutor_session.dart';

TutorSession newSession() {
  final c = curriculumFor(
      const LearnerProfile(learnerId: 'l', displayName: 'M', grade: 5))!;
  final fp = FractionProblem.parse('3/4 + 2/5')!;
  final ec = fractionCase(fp.b, fp.d)!;
  return TutorSession(
      exerciseId: 'ex',
      skillCaseId: ec,
      problem: fp,
      scope: TutorScope.forProblem(c.conceptId, ec, c.stage, c.catalogue));
}

Future<void> pump(WidgetTester t, TutorSession s) async {
  await t.pumpWidget(MaterialApp(
      home: TutorScreen(session: s, expression: '3/4 + 2/5')));
}

void main() {
  testWidgets('thang 4 nấc hiển thị và đi theo ENGINE: none → hint', (t) async {
    final s = newSession();
    await pump(t, s);
    for (final l in ['Tự làm', 'Gợi ý', 'Làm mẫu', 'Lời giải']) {
      expect(find.text(l), findsOneWidget, reason: l);
    }
    // chưa có bước nào ⇒ chưa có panel các-bước
    expect(find.text('CÁC BƯỚC CON ĐÃ LÀM'), findsNothing);

    // thử sai → xin gợi ý: panel ghi ĐÚNG chuyện đã xảy ra
    await t.enterText(find.byType(TextField), '1/2');
    await t.scrollUntilVisible(find.text('Con làm xong rồi ✓'), 150,
        scrollable: find.byType(Scrollable).first);
    await t.tap(find.text('Con làm xong rồi ✓'));
    await t.pump();
    await t.scrollUntilVisible(find.text('Gợi ý cho tớ ✋'), 150,
        scrollable: find.byType(Scrollable).first);
    await t.tap(find.text('Gợi ý cho tớ ✋'));
    await t.pump();
    // panel nằm TRÊN — kéo về đầu danh sách rồi mới đọc
    await t.drag(find.byType(Scrollable).first, const Offset(0, 600));
    await t.pumpAndSettle();
    expect(find.text('CÁC BƯỚC CON ĐÃ LÀM'), findsOneWidget);
    expect(find.text('· Con thử: chưa đúng — không sao'), findsOneWidget);
    expect(find.text('✋ SAM gợi ý một chút'), findsOneWidget);
  });

  testWidgets('không ký tự % nào trong working state (luật hiển thị)', (t) async {
    final s = newSession();
    await pump(t, s);
    await t.enterText(find.byType(TextField), '1/2');
    await t.scrollUntilVisible(find.text('Con làm xong rồi ✓'), 150,
        scrollable: find.byType(Scrollable).first);
    await t.tap(find.text('Con làm xong rồi ✓'));
    await t.pump();
    for (final w in t.widgetList<Text>(find.byType(Text))) {
      expect(w.data ?? '', isNot(contains('%')));
    }
  });
}
