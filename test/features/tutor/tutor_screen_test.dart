/// WAL-86 — luật HIỂN THỊ của T1/E1 giữ bằng widget test.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/curriculum/pedagogical_boundary.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/features/tutor/tutor_screen.dart';
import 'package:learning_coach/features/tutor/tutor_session.dart';
import '../../support/curriculum.dart';

const _stage = LearningStage(
  grade: 5,
  bookSeries: 'kntt',
  lessonId: 'toan5-t1-bai6',
  conceptsIntroduced: {'phan-so', 'chia-het', 'nhan-so-tu-nhien'},
  methodsIntroduced: {'common-denom-by-product'},
  terminologyIntroduced: {'mẫu số chung'},
);

/// WAL-168: lấy ĐÚNG method của sản phẩm thay vì chép lại — lời dạy nay là dữ
/// liệu đi cùng method, nên fixture chép tay sẽ kiểm một bản sao không có lời.
final _method = toan5Bai6
    .catalogue
    .firstWhere((m) => m.id == 'common-denom-by-product');

TutorSession _session() {
  var t = DateTime(2026, 9, 1, 19);
  return TutorSession(
    exerciseId: 'cp:test',
    skillCaseId: 'denominator-non-divisible',
    problem: FractionProblem.parse('3/4 + 2/5')!,
    scope: TutorScope.forProblem(
        'quy-dong', 'denominator-non-divisible', _stage, [_method]),
    now: () => t = t.add(const Duration(seconds: 30)),
  );
}

Future<void> _pump(WidgetTester tester, TutorSession s,
    {void Function(TutorOutcome, EvidenceLog)? onFinished}) async {
  await tester.pumpWidget(MaterialApp(
      home: TutorScreen(
          session: s, expression: '3/4 + 2/5', onFinished: onFinished)));
}

Future<void> _answer(WidgetTester tester, String a) async {
  // WAL-139: working list dài hơn (thang + các-bước); ListView build lười —
  // scrollUntilVisible mới TÌM được item chưa build (ensureVisible thì không).
  await tester.scrollUntilVisible(find.byType(TextField), 150,
      scrollable: find.byType(Scrollable).first);
  await tester.enterText(find.byType(TextField), a);
  await tester.scrollUntilVisible(find.text('Con làm xong rồi ✓'), 150,
      scrollable: find.byType(Scrollable).first);
  await tester.tap(find.text('Con làm xong rồi ✓'));
  await tester.pumpAndSettle();
}

Future<void> _tapHint(WidgetTester tester, String label) async {
  await tester.scrollUntilVisible(find.text(label), 150,
      scrollable: find.byType(Scrollable).first);
  await tester.tap(find.text(label));
  await tester.pumpAndSettle();
}

void main() {
  testWidgets('đúng-sau-gợi-ý: UI khen NHƯNG log không ghi công tự làm',
      (tester) async {
    final s = _session();
    EvidenceLog? emitted;
    await _pump(tester, s, onFinished: (_, log) => emitted = log);

    await _answer(tester, '5/9'); // sai
    expect(find.textContaining('thử lại nhé'), findsOneWidget);

    await _tapHint(tester, 'Gợi ý cho tớ ✋');
    expect(find.textContaining('mẫu số chung'), findsWidgets);

    await _answer(tester, '23/20'); // đúng sau gợi ý
    // UI khen nỗ lực…
    expect(find.textContaining('Làm đúng rồi'), findsOneWidget);
    // …nhưng dòng bằng chứng nói thật, và LOG là thứ model tin:
    expect(find.textContaining('chưa tính là con tự làm được'), findsOneWidget);
    expect(emitted, isNotNull);
    expect(emitted!.independentAttempts.where((e) => e.correct == true),
        isEmpty,
        reason: 'khen ≠ ghi công: không có bằng-chứng-tự-làm-đúng nào');
  });

  testWidgets('chưa tự thử thì không có nút Xem lời giải', (tester) async {
    final s = _session();
    await _pump(tester, s);
    expect(find.text('Xem lời giải'), findsNothing);
    // leo hết hai nấc gợi ý vẫn chưa thấy — vì chưa thử lần nào
    await _tapHint(tester, 'Gợi ý cho tớ ✋');
    await _tapHint(tester, 'Gợi ý thêm ✋');
    expect(find.text('Xem lời giải'), findsNothing);
    // thử một lần (sai) → nút mới xuất hiện
    await _answer(tester, '1/2');
    expect(find.text('Xem lời giải'), findsOneWidget);
  });

  testWidgets('tự làm đúng ngay: màn E1 ghi nhận tự làm, mascot độc lập',
      (tester) async {
    final s = _session();
    await _pump(tester, s);
    await _answer(tester, '23/20');
    expect(find.textContaining('không cần tớ gợi ý'), findsOneWidget);
    expect(find.textContaining('TỰ làm được'), findsOneWidget);
    expect(find.text('Không cần gợi ý'), findsOneWidget);
  });

  testWidgets('không phần trăm, không điểm số ở cả T1 lẫn E1', (tester) async {
    final s = _session();
    await _pump(tester, s);
    void scan() {
      for (final w in tester.widgetList<Text>(find.byType(Text))) {
        final t = w.data ?? '';
        expect(t.contains('%'), isFalse, reason: 'cấm %: "$t"');
      }
    }

    scan();
    await tester.tap(find.text('Gợi ý cho tớ ✋'));
    await tester.pumpAndSettle();
    scan();
    await _answer(tester, '23/20');
    scan(); // E1
  });
}
