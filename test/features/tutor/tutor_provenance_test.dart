/// WAL-108 §3 — «provenance visible từ Tutor Start»: chip nguồn có mặt NGAY
/// khi vào bài (chưa cần xin hint), drill-down đủ WHY/SOURCE/AUTHORITY/VERSION.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/adaptive/adaptive_engine.dart';
import 'package:learning_coach/core/curriculum/pedagogical_boundary.dart';
import 'package:learning_coach/core/knowledge/slice_curriculum.dart';
import 'package:learning_coach/core/tutor/teaching_provenance.dart';
import 'package:learning_coach/features/tutor/tutor_screen.dart';
import 'package:learning_coach/features/tutor/tutor_session.dart';
import '../../support/curriculum.dart';

void main() {
  (TutorSession, TeachingProvenance) build() {
    final c = toan5Bai6;
    final fp = FractionProblem.parse('3/4 + 2/5')!;
    final exerciseCase = fractionCase(fp.b, fp.d)!;
    final scope = TutorScope.forProblem(
        c.conceptId, exerciseCase, c.stage, c.catalogue);
    final session = TutorSession(
        exerciseId: 'ex', skillCaseId: exerciseCase, problem: fp, scope: scope);
    final tp = explainTeaching(
        scope: scope,
        methodId: scope.allowedMethods.first.id,
        exerciseCase: exerciseCase)!;
    return (session, tp);
  }

  testWidgets('chip nguồn hiện TỪ ĐẦU; sheet đủ nguồn + phiên bản',
      (tester) async {
    final (session, tp) = build();
    await tester.pumpWidget(MaterialApp(
        home: TutorScreen(
            session: session,
            expression: '3/4 + 2/5',
            catalogue: toan5Bai6
                .catalogue,
            provenance: tp)));

    // TỪ TUTOR START — chưa bấm gì đã thấy lối vào nguồn.
    expect(find.text('Vì sao cách này? · Nguồn'), findsOneWidget);

    await tester.tap(find.text('Vì sao cách này? · Nguồn'));
    await tester.pumpAndSettle();

    expect(find.text('Cách «Lấy mẫu số chung là tích hai mẫu số»'),
        findsOneWidget);
    expect(find.textContaining('SAM làm theo ví dụ trong SGK Toán 5'),
        findsOneWidget, reason: 'sourceDemonstrated ≠ «sách nói rằng»');
    expect(find.textContaining('trang 21'), findsOneWidget);

    // Dòng phiên bản nằm cuối sheet — ListView build lười: kéo lên đã rồi expect.
    await tester.drag(find.byType(ListView).last, const Offset(0, -250));
    await tester.pumpAndSettle();
    expect(find.textContaining('tutor-session-v1'), findsOneWidget);
    expect(find.textContaining(knowledgeModelVersion), findsOneWidget);

    // WAL-141 — «cách khác» drill-down: take-larger hiện với LÝ DO THẬT
    // (dành cho dạng chia-hết — bài này không thuộc), KHÔNG mượn nguồn
    // của cách chính.
    await tester.drag(find.byType(ListView).last, const Offset(0, -300));
    await tester.pumpAndSettle();
    expect(find.text('Trong chương trình còn cách khác:'), findsOneWidget);
    expect(find.text('«Giữ mẫu số lớn hơn làm mẫu số chung»'), findsOneWidget);
    expect(find.textContaining('DẠNG BÀI KHÁC'), findsOneWidget,
        reason: '⭐ đột biến copy sourceLine cách chính cho cách khác ⇒ đỏ');
    expect(find.textContaining('trang 77'), findsNothing,
        reason: 'cách không áp ⇒ KHÔNG render citation như thể đang dạy nó');
  });

  testWidgets('không truyền provenance ⇒ không có chip (không bịa nguồn)',
      (tester) async {
    final (session, _) = build();
    await tester.pumpWidget(MaterialApp(
        home: TutorScreen(session: session, expression: '3/4 + 2/5')));
    expect(find.text('Vì sao cách này? · Nguồn'), findsNothing);
  });
}
