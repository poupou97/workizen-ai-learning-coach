/// ⭐⭐ WAL-52 — ranh giới an toàn do TEST giữ: mọi lối ra của màn xác nhận
/// đều đi qua đúng loại CanonicalProblem; unconfirmed không có lối đi tiếp.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/curriculum/canonical_problem.dart';
import 'package:learning_coach/core/perception/perception_provenance.dart';
import 'package:learning_coach/features/camera/confirm_problem_screen.dart';

void main() {
  final t0 = DateTime(2026, 9, 1, 20);
  PerceptionHypothesis hyp([String expr = '3/4 + 2/5']) => PerceptionHypothesis(
      hypothesisId: 'h-ui-1',
      rawImageRef: 'img-sha-1',
      expression: expr,
      pipelineVersion: 'assemble-v1',
      at: t0);

  Future<CanonicalProblem?> pump(WidgetTester t, PerceptionHypothesis? h,
      {VoidCallback? onRetake}) async {
    CanonicalProblem? result;
    await t.pumpWidget(MaterialApp(
      home: ConfirmProblemScreen(
        hypothesis: h,
        now: t0,
        onConfirmed: (p) => result = p,
        onRetake: onRetake ?? () {},
      ),
    ));
    await t.pump();
    return result;
  }

  testWidgets('✓ Đúng rồi → confirmedPerception, exerciseId cp:, giữ nguyên văn',
      (t) async {
    CanonicalProblem? result;
    await t.pumpWidget(MaterialApp(
        home: ConfirmProblemScreen(
            hypothesis: hyp(), now: t0,
            onConfirmed: (p) => result = p, onRetake: () {})));
    await t.tap(find.text('✓ Đúng rồi'));
    await t.pump();
    expect(result!.origin, ProblemOrigin.confirmedPerception);
    expect(result!.exerciseId, startsWith('cp:h-ui-1@'));
    expect(result!.expression, '3/4 + 2/5');
  });

  testWidgets('⭐⭐ Sửa rồi xác nhận → corrected; hypothesis máy KHÔNG bị đụng',
      (t) async {
    final h = hyp('15/1 - 5/7'); // đúng loại biểu thức bịa PHONE-SIM bắt được
    CanonicalProblem? result;
    await t.pumpWidget(MaterialApp(
        home: ConfirmProblemScreen(
            hypothesis: h, now: t0,
            onConfirmed: (p) => result = p, onRetake: () {})));
    await t.tap(find.text('✏️ Sửa'));
    await t.pump();
    await t.enterText(find.byType(TextField), '1/5 - 5/7');
    await t.tap(find.text('✓ Đúng rồi'));
    await t.pump();
    expect(result!.expression, '1/5 - 5/7');
    expect(h.expression, '15/1 - 5/7',
        reason: '⭐⭐ sửa của trẻ là BẢN GHI MỚI — lịch sử máy nguyên vẹn, '
            'Student Correction Rate (#5 WAL-63) đo được từ đây');
    expect(result!.exerciseId, startsWith('cp:'));
  });

  testWidgets('📷 Chụp lại gọi đúng callback, không sinh problem nào', (t) async {
    var retaken = false;
    final result = await pump(t, hyp(), onRetake: () => retaken = true);
    await t.tap(find.text('📷 Chụp lại'));
    await t.pump();
    expect(retaken, isTrue);
    expect(result, isNull);
  });

  testWidgets('⭐ KHÔNG đọc được đề: nói "chưa chắc", KHÔNG có nút Đúng-rồi',
      (t) async {
    await pump(t, null);
    expect(find.textContaining('chưa chắc'), findsOneWidget,
        reason: 'ADMIT_UNCERTAINTY — "chưa chắc" là câu trả lời hợp lệ');
    expect(find.text('✓ Đúng rồi'), findsNothing,
        reason: '⭐ fail closed: không có đường đi tiếp khi máy không đọc được '
            '— chỉ Chụp lại hoặc tự gõ');
    expect(find.text('Chụp lại'), findsOneWidget);
  });

  testWidgets('tự gõ đề → CanonicalProblem man: (nguồn là chính trẻ)', (t) async {
    CanonicalProblem? result;
    await t.pumpWidget(MaterialApp(
        home: ConfirmProblemScreen(
            hypothesis: null, now: t0,
            onConfirmed: (p) => result = p, onRetake: () {})));
    await t.tap(find.text('Gõ đề vào đây ✎'));
    await t.pump();
    await t.enterText(find.byType(TextField), '2/3 + 1/6');
    await t.tap(find.text('✓ Đúng rồi'));
    await t.pump();
    expect(result!.origin, ProblemOrigin.manualInput);
    expect(result!.exerciseId, startsWith('man:'));
    expect(result!.expression, '2/3 + 1/6');
  });

  testWidgets('luật hiển thị: không ký tự % trên màn', (t) async {
    await pump(t, hyp());
    for (final w in t.widgetList<Text>(find.byType(Text))) {
      expect(w.data ?? '', isNot(contains('%')));
    }
  });
}
