/// WAL-143 — Kiểm tra hiểu bài: cùng engine, khác LUẬT.
///
/// Bốn thứ test này giữ, xếp theo mức khó vi phạm:
/// ① CẤU TRÚC — mã nguồn màn kiểm tra không được có đường nào tới thang hỗ trợ;
/// ② SỰ KIỆN — mọi event phát ra đều support=none, phiên assess SẠCH;
/// ③ QUYỀN KẾT LUẬN — làm đúng hết vẫn KHÔNG được nói «con vững»;
/// ④ KHÔNG ĐIỂM SỐ — màn kết quả không có điểm/%/tỉ số.
library;

import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/assistance_policy.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/core/store/learning_session.dart';
import 'package:learning_coach/core/student/concept_summary.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/features/assessment/assessment_result_screen.dart';
import 'package:learning_coach/features/assessment/assessment_screen.dart';
import 'package:learning_coach/features/learning_session/slice_flow.dart'
    show masteryFromStore;
import 'package:learning_coach/features/shell/session_recorder.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';
import '../../support/curriculum.dart';

const _p = LearnerProfile(learnerId: 'l', displayName: 'Na', grade: 5);

const _items = [
  CorpusExercise(
      expr: '1/2 - 1/5',
      book: '05-sgk-toan-5-tap-mot',
      skillCaseId: 'denominator-non-divisible',
      page: 21),
  CorpusExercise(
      expr: '1/3 + 1/4',
      book: '05-sgk-toan-5-tap-mot',
      skillCaseId: 'denominator-non-divisible',
      page: 21),
];

Future<(List<LearningEvent>, List<AssessmentAnswer>)> _run(
    WidgetTester t, List<String> answers) async {
  List<LearningEvent> ev = const [];
  List<AssessmentAnswer> ans = const [];
  await t.pumpWidget(MaterialApp(
      home: AssessmentScreen(
          items: _items,
          now: () => DateTime(2026, 9, 3, 10),
          onFinished: (e, a) {
            ev = e;
            ans = a;
          })));
  for (final a in answers) {
    await t.enterText(find.byType(TextField), a);
    await t.tap(find.byType(FilledButton));
    await t.pumpAndSettle();
  }
  return (ev, ans);
}

void main() {
  test('⭐① CẤU TRÚC: mã màn kiểm tra KHÔNG có đường nào tới thang hỗ trợ', () {
    final src =
        File('lib/features/assessment/assessment_screen.dart').readAsStringSync();
    // Không dựng TutorSession, không phát hint/lời giải, không nút xin trợ giúp.
    for (final banned in [
      'TutorSession(',
      'EvidenceKind.hintRequested',
      'SupportLevel.hint',
      'SupportLevel.workedStep',
      'SupportLevel.fullSolution',
    ]) {
      expect(src.contains(banned), isFalse,
          reason: '⭐ màn kiểm tra chạm vào «$banned» ⇒ cấm-bằng-nút, không '
              'phải cấm-bằng-cấu-trúc');
    }
    // Trần của policy là none — nếu ai đổi bảng luật, test này phải đỏ.
    expect(rulesFor(AssistancePolicy.assessment).supportCap, SupportLevel.none);
    expect(rulesFor(AssistancePolicy.assessment).revealAllowed, isFalse);
    expect(rulesFor(AssistancePolicy.assessment).mode, SessionMode.assess);
  });

  testWidgets('⭐② mọi sự kiện support=none; phiên assess ghi xong SẠCH',
      (t) async {
    final (ev, ans) = await _run(t, ['3/10', '7/12']);
    expect(ev, hasLength(2));
    expect(ev.every((e) => e.support == SupportLevel.none), isTrue,
        reason: '⭐ đột biến phát hỗ trợ trong bài kiểm tra ⇒ đỏ');
    expect(ev.every((e) => e.kind == EvidenceKind.independentAttempt), isTrue);
    expect(ev.every((e) => e.policyId == 'assessment-v1'), isTrue);
    expect(ev.every((e) => e.knowledgeVersion != null), isTrue);
    expect(ans.map((a) => a.correct), everyElement(isTrue));

    final store = JsonlLearnerStore();
    final rec = await recordSession(
        store: store,
        learnerId: _p.learnerId,
        subjectId: 'toan',
        events: ev,
        trigger: SessionTrigger.assessment,
        mode: SessionMode.assess);
    expect(rec.violations, isEmpty,
        reason: '⭐ phiên thi bị nhiễm dạy học ⇒ kết luận không dùng được');
    expect(rec.session!.mode, SessionMode.assess);
  });

  testWidgets('máy KHÔNG đọc được dạng bài ⇒ không dám chấm (fail closed)',
      (t) async {
    List<LearningEvent> ev = const [];
    await t.pumpWidget(MaterialApp(
        home: AssessmentScreen(
            items: const [
              // Có ca (nên ô đáp án mở) nhưng biểu thức KHÔNG parse được —
              // đường fail-closed của BỘ CHẤM, khác đường ca-không-rõ (WAL-210).
              CorpusExercise(
                  expr: 'vẽ đoạn thẳng AB',
                  book: 'b',
                  skillCaseId: 'denominator-non-divisible'),
            ],
            onFinished: (e, _) => ev = e)));
    await t.enterText(find.byType(TextField), '5');
    await t.tap(find.byType(FilledButton));
    await t.pumpAndSettle();
    expect(ev, isEmpty,
        reason: '⭐ chấm bừa bài không parse được ⇒ bằng chứng giả');
  });

  testWidgets('⭐③④ ĐÚNG HẾT vẫn KHÔNG thành «vững», và không có điểm số',
      (t) async {
    // Phiên thật: 2 câu đúng, ghi kho, đọc lại mastery như app làm.
    final (ev, ans) = await _run(t, ['3/10', '7/12']);
    final store = JsonlLearnerStore();
    final rec = await recordSession(
        store: store,
        learnerId: _p.learnerId,
        subjectId: 'toan',
        events: ev,
        trigger: SessionTrigger.assessment,
        mode: SessionMode.assess);
    final c = toan5Bai6;
    final m = await masteryFromStore(store, _p.learnerId, c);
    final s = ConceptSummary.of(m,
        knownCaseIds: {for (final k in c.cases) k.id},
        now: DateTime(2026, 9, 3, 11));

    expect(s.claim, isNot(ConceptClaim.mastered),
        reason: '⭐ hai câu đúng của MỘT ca KHÔNG được thành «đã vững» — '
            'bài kiểm tra không vượt quyền bằng chứng');

    await t.pumpWidget(MaterialApp(
        home: AssessmentResultScreen(
            answers: ans, summary: s, violations: rec.violations)));
    await t.pumpAndSettle();

    // ④ không điểm số: không «điểm», không «%», không tỉ số tổng kết.
    final texts = t
        .widgetList<Text>(find.byType(Text))
        .map((w) => w.data ?? '')
        .join('\n');
    expect(texts.contains('%'), isFalse);
    expect(texts.toLowerCase().contains('điểm'), isFalse,
        reason: '⭐ «điểm» xuất hiện ⇒ kết quả đã bị điểm-số-hoá');
    expect(RegExp(r'\b\d+\s*/\s*\d+\s*(câu|đúng)').hasMatch(texts), isFalse,
        reason: '⭐ tỉ số tổng kết là một con điểm đội lốt');
    // nhưng PHẢI kể từng câu (sự việc) — đó mới là bằng chứng
    expect(find.textContaining('1/2 - 1/5'), findsOneWidget);
    expect(find.textContaining('đúng'), findsWidgets);
  });

  testWidgets('⭐ có câu SAI ⇒ kết quả NÓI RA câu nào, và chỉ đúng đường có '
      'thật; làm đúng hết thì KHÔNG bịa ra chỗ chưa chắc', (t) async {
    final s = ConceptSummary.of(
        const ConceptMastery(conceptId: 'quy-dong', cases: {}),
        knownCaseIds: const {},
        now: DateTime(2026, 9, 3, 11));
    await t.pumpWidget(MaterialApp(
        home: AssessmentResultScreen(answers: const [
      AssessmentAnswer(expr: '1/2 - 1/5', raw: '3/10', correct: true),
      AssessmentAnswer(expr: '3/11 + 7/12', raw: '10/23', correct: false),
    ], summary: s)));
    await t.pumpAndSettle();
    expect(find.textContaining('CÒN CHƯA CHẮC CHỖ NÀO'), findsOneWidget);
    expect(find.textContaining('3/11 + 7/12'), findsWidgets);
    expect(find.textContaining('Ôn luyện'), findsOneWidget);

    // Đúng hết ⇒ KHÔNG dựng mục «chưa chắc» (không bịa lo lắng).
    await t.pumpWidget(MaterialApp(
        home: AssessmentResultScreen(answers: const [
      AssessmentAnswer(expr: '1/2 - 1/5', raw: '3/10', correct: true),
    ], summary: s)));
    await t.pumpAndSettle();
    expect(find.textContaining('CÒN CHƯA CHẮC CHỖ NÀO'), findsNothing,
        reason: '⭐ đột biến luôn hiện mục chưa-chắc ⇒ đỏ');
  });

  testWidgets('⭐ phiên có hỗ trợ lọt vào ⇒ màn kết quả NÓI RA, không nuốt',
      (t) async {
    final dirty = LearningEvent(
        eventId: 'x#0',
        skillCaseId: 'denominator-non-divisible',
        kind: EvidenceKind.hintRequested,
        correct: null,
        at: DateTime(2026, 9, 3, 10),
        support: SupportLevel.hint,
        conceptIds: const ['quy-dong']);
    await t.pumpWidget(MaterialApp(
        home: AssessmentResultScreen(
            answers: const [
              AssessmentAnswer(expr: '1/2 - 1/5', raw: '3/10', correct: true)
            ],
            summary: ConceptSummary.of(
                const ConceptMastery(conceptId: 'quy-dong', cases: {}),
                knownCaseIds: const {},
                now: DateTime(2026, 9, 3, 11)),
            violations: [dirty])));
    await t.pumpAndSettle();
    expect(find.textContaining('lượt hỗ trợ lọt vào'), findsOneWidget,
        reason: '⭐ nuốt vi phạm ⇒ kết luận rút ra từ phiên bẩn');
  });

  // ⭐⭐ WAL-210 (audit B.6 §3 / hole A): bài KHÔNG quy được về ca ⇒ không
  // chấm, không sinh bằng chứng dưới ca bịa `'unknown-case'`.
  group('WAL-210 — ca KHÔNG XÁC ĐỊNH: fail closed, không xô «unknown-case»', () {
    testWidgets('⭐⭐ câu không có skillCaseId ⇒ nói thật, KHÔNG ô đáp án, '
        'bỏ qua, KHÔNG sự kiện; câu có ca sau đó vẫn chấm bình thường',
        (t) async {
      List<LearningEvent> ev = const [];
      List<AssessmentAnswer> ans = const [];
      await t.pumpWidget(MaterialApp(
          home: AssessmentScreen(
              items: const [
                // parse ĐƯỢC (máy chấm được) nhưng KHÔNG có ca ⇒ vẫn phải từ chối
                CorpusExercise(expr: '1/2 + 1/3', book: '05-sgk-toan-5-tap-mot'),
                CorpusExercise(
                    expr: '1/2 - 1/5',
                    book: '05-sgk-toan-5-tap-mot',
                    skillCaseId: 'denominator-non-divisible',
                    page: 21),
              ],
              now: () => DateTime(2026, 9, 5, 10),
              onFinished: (e, a) {
                ev = e;
                ans = a;
              })));
      expect(find.textContaining('chưa xác định được dạng bài'), findsOneWidget,
          reason: 'trạng thái trung thực, cùng giọng với decide()');
      expect(find.byType(TextField), findsNothing,
          reason: '⭐ đột biến vẫn mở ô đáp án cho ca không rõ ⇒ đỏ');
      await t.tap(find.byType(FilledButton));
      await t.pumpAndSettle();
      // Sang câu có ca: chấm như thường.
      expect(find.byType(TextField), findsOneWidget);
      await t.enterText(find.byType(TextField), '3/10');
      await t.tap(find.byType(FilledButton));
      await t.pumpAndSettle();
      expect(ev, hasLength(1),
          reason: '⭐⭐ đột biến mint sự kiện cho câu không ca ⇒ 2 sự kiện ⇒ đỏ');
      expect(ev.single.skillCaseId, 'denominator-non-divisible');
      expect(ans, hasLength(1));
      expect(ans.single.expr, '1/2 - 1/5');
    });

    testWidgets('mọi câu đều không có ca ⇒ kết thúc với 0 sự kiện, 0 đáp án',
        (t) async {
      List<LearningEvent>? ev;
      await t.pumpWidget(MaterialApp(
          home: AssessmentScreen(
              items: const [
                CorpusExercise(expr: '1/2 + 1/3', book: 'b'),
              ],
              onFinished: (e, _) => ev = e)));
      await t.tap(find.byType(FilledButton));
      await t.pumpAndSettle();
      expect(ev, isEmpty,
          reason: 'không ca thật ⇒ không bằng chứng nào, kể cả participation');
    });

    test('⭐ CẤU TRÚC: chuỗi «unknown-case» không còn ở bất kỳ đâu trong lib/',
        () {
      final hits = Directory('lib')
          .listSync(recursive: true)
          .whereType<File>()
          .where((f) => f.path.endsWith('.dart'))
          .where((f) => f.readAsStringSync().contains("'unknown-case'"))
          .map((f) => f.path)
          .toList();
      expect(hits, isEmpty,
          reason: '⭐ một ca bịa quay lại ⇒ bằng chứng chấm điểm treo dưới ca '
              'không tồn tại (audit B.6 §3)');
    });
  });
}
