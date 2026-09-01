/// WAL-97 — surface Quiz/Select: luật giữ bằng test, trên bài tập THẬT của
/// corpus (TV5-t2 b9 tr.45 «Tìm từ ngữ được lặp lại…» và Toán «Chọn…»).
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/core/tutor/learning_activity.dart';
import 'package:learning_coach/features/shell/quiz_select_screen.dart';

/// Bài THẬT: TV5 tập hai, bài 9, tr.45 (đã trích ở GĐ2 batch ③).
const _tv = LearningActivity(
  activityId: 'tv5-b9-bt3',
  prompt: 'Tìm từ ngữ được lặp lại để liên kết câu trong đoạn văn: '
      '«Một hôm, Thạch Sanh ngồi trong ngục tối. Chàng lấy đàn ra gảy…»',
  response: ResponseKind.selectIdentify,
  conceptId: 'lien-ket-cau',
  skillCaseId: 'lkc-nhan-biet-lap-tu',
  options: ['Thạch Sanh / Chàng', 'ngục tối', 'đàn'],
  correctOption: 0,
  sourceBook: '05-sgk-tieng-viet-5-tap-hai',
  sourcePage: 45,
);

/// Cùng surface, môn KHÁC — bằng chứng bác F1 «mỗi môn cần UI riêng».
const _toan = LearningActivity(
  activityId: 'toan5-chon',
  prompt: 'Chọn phân số bằng 1/2.',
  response: ResponseKind.selectIdentify,
  conceptId: 'phan-so-bang-nhau',
  skillCaseId: 'rut-gon',
  options: ['3/6', '2/5', '4/9'],
  correctOption: 0,
);

/// Bài chưa biết đáp án — UNKNOWN không được thành SAI.
const _unknown = LearningActivity(
  activityId: 'tv5-b11-bt3',
  prompt: 'Tìm các từ ngữ nối thay cho bông hoa để liên kết các câu.',
  response: ResponseKind.selectIdentify,
  conceptId: 'lien-ket-cau',
  options: ['vì vậy', 'tuy nhiên', 'sau đó'],
);

Future<List<LearningEvent>> _run(
    WidgetTester tester, LearningActivity a, int pick) async {
  List<LearningEvent> out = const [];
  await tester.pumpWidget(MaterialApp(
      home: QuizSelectScreen(
    // key theo bài: không có nó, lần pumpWidget thứ hai tái dùng State cũ
    // (cùng type, cùng vị trí) và màn vẫn ở trạng thái đã-xong của bài trước.
    key: ValueKey(a.activityId),
    activity: a,
    now: () => DateTime(2026, 9, 1, 19),
    onFinished: (e) => out = e,
  )));
  await tester.tap(find.text(a.options[pick]));
  await tester.pumpAndSettle();
  return out;
}

void main() {
  test('resolver: SELECT→quiz, NUMERIC→problem, shortText FAIL CLOSED', () {
    expect(resolveSurface(_tv), SurfaceKind.quizSelect);
    expect(resolveSurface(_toan), SurfaceKind.quizSelect);
    expect(
        resolveSurface(const LearningActivity(
            activityId: 'x', prompt: 'Tính 3/4 + 2/5',
            response: ResponseKind.numericStep, conceptId: 'quy-dong')),
        SurfaceKind.problemStep);
    expect(
        resolveSurface(const LearningActivity(
            activityId: 'y', prompt: 'Nêu ví dụ…',
            response: ResponseKind.shortText, conceptId: 'c')),
        SurfaceKind.unsupported,
        reason: 'chưa có surface thì nói KHÔNG HỖ TRỢ, không ép vào quiz');
  });

  testWidgets('⭐ F1 bác: CÙNG surface phục vụ cả Tiếng Việt lẫn Toán',
      (tester) async {
    for (final a in [_tv, _toan]) {
      final events = await _run(tester, a, 0);
      expect(events.first.kind, EvidenceKind.independentAttempt);
      expect(events.first.correct, isTrue);
      expect(events.first.conceptIds, [a.conceptId]);
    }
  });

  testWidgets('chọn đúng ngay ⇒ bằng chứng TỰ LÀM, support none', (tester) async {
    final events = await _run(tester, _tv, 0);
    final attempt = events.first;
    expect(attempt.kind, EvidenceKind.independentAttempt);
    expect(attempt.support, SupportLevel.none);
    expect(attempt.policyId, 'quiz-select-v1');
    expect(find.textContaining('không cần tớ gợi ý'), findsOneWidget);
    expect(find.textContaining('TỰ làm được'), findsOneWidget);
  });

  testWidgets('⭐ chọn đúng SAU gợi ý ⇒ postHintSuccess + support hint, '
      'UI khen nhưng nói thẳng chưa-tính-là-tự-làm', (tester) async {
    List<LearningEvent> out = const [];
    await tester.pumpWidget(MaterialApp(
        home: QuizSelectScreen(
      activity: _tv,
      now: () => DateTime(2026, 9, 1, 19),
      onFinished: (e) => out = e,
    )));
    await tester.tap(find.text('Gợi ý cho tớ ✋'));
    await tester.pumpAndSettle();
    await tester.tap(find.text(_tv.options[0]));
    await tester.pumpAndSettle();

    final post =
        out.firstWhere((e) => e.kind == EvidenceKind.postHintSuccess);
    expect(post.support, SupportLevel.hint);
    expect(out.any((e) => e.kind == EvidenceKind.hintRequested), isTrue);
    expect(out.any((e) =>
        e.kind == EvidenceKind.independentAttempt && e.correct == true),
        isFalse,
        reason: 'khen ≠ ghi công: không có bằng-chứng-tự-làm-đúng nào');
    expect(find.textContaining('chưa tính là con tự làm được'), findsOneWidget);
  });

  testWidgets('chọn sai ⇒ ghi nhận lần thử, KHÔNG kết thúc, không phán xét',
      (tester) async {
    await tester.pumpWidget(MaterialApp(
        home: QuizSelectScreen(
            activity: _tv, now: () => DateTime(2026, 9, 1, 19))));
    await tester.tap(find.text(_tv.options[1]));
    await tester.pumpAndSettle();
    expect(find.textContaining('thử lại nhé'), findsOneWidget);
    expect(find.text('Về Hôm nay'), findsNothing, reason: 'chưa xong');
  });

  testWidgets('⭐ bài CHƯA BIẾT đáp án ⇒ không chấm, không kết luận đúng/sai',
      (tester) async {
    final events = await _run(tester, _unknown, 0);
    expect(events.single.correct, isNull,
        reason: 'UNKNOWN không bao giờ thành SAI (cũng không thành ĐÚNG)');
    expect(events.single.kind, EvidenceKind.independentAttempt);
    expect(find.textContaining('chưa có đáp án'), findsOneWidget);
  });

  testWidgets('không %, không điểm số trên mọi trạng thái màn', (tester) async {
    await tester.pumpWidget(MaterialApp(
        home: QuizSelectScreen(
            activity: _tv, now: () => DateTime(2026, 9, 1, 19))));
    void scan() {
      for (final w in tester.widgetList<Text>(find.byType(Text))) {
        final t = w.data ?? '';
        expect(t.contains('%'), isFalse, reason: 'cấm %: "$t"');
        expect(t.contains('điểm'), isFalse, reason: 'cấm điểm: "$t"');
      }
    }

    scan();
    await tester.tap(find.text('Gợi ý cho tớ ✋'));
    await tester.pumpAndSettle();
    scan();
    await tester.tap(find.text(_tv.options[0]));
    await tester.pumpAndSettle();
    scan();
  });
}
