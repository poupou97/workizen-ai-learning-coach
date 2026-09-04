/// WAL-98 — Surface COMPOSE-LITE: «SAM KHÔNG viết hộ» giữ bằng test, trên bài
/// viết THẬT của corpus (TV5 — viết đoạn có liên kết câu). Falsification: mỗi
/// bất biến của REVEAL gate kèm đột biến làm test đỏ (ghi trong reason).
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/context/learning_context.dart';
import 'package:learning_coach/core/intent/learning_intent.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/core/tutor/learning_activity.dart';
import 'package:learning_coach/core/tutor/tutor_feedback.dart';
import 'package:learning_coach/features/shell/compose_lite_screen.dart';

const _ctx = LearningContext(learnerId: 'na', grade: 5);

/// Bài THẬT: viết đoạn có liên kết câu (case «dùng-khi-viết» của concept #3).
const _compose = LearningActivity(
  activityId: 'tv5-viet-doan-lienket',
  prompt: 'Viết đoạn văn 3–4 câu tả cơn mưa, dùng ít nhất một từ ngữ nối để '
      'liên kết các câu.',
  response: ResponseKind.compose,
  conceptId: 'lien-ket-cau',
  skillCaseId: 'lkc-dung-khi-viet',
  composeChecklist: [
    'Con đã dùng từ ngữ nối (rồi, sau đó, vì thế…) giữa các câu chưa?',
    'Câu mở đầu đã cho biết con tả cơn mưa lúc nào chưa?',
  ],
  sourceBook: '05-sgk-tieng-viet-5-tap-hai',
);

Future<void> _pump(WidgetTester tester,
    {void Function(List<LearningEvent>)? onFinished,
    LearningContext context = _ctx}) async {
  await tester.pumpWidget(MaterialApp(
      home: ComposeLiteScreen(
    activity: _compose,
    learningContext: context,
    now: () => DateTime(2026, 9, 1, 19),
    onFinished: onFinished,
  )));
}

/// Đi từ dàn ý → nộp một nháp không rỗng. Sau bước này màn ở stage afterDraft.
Future<void> _toAfterDraft(WidgetTester tester, String draft) async {
  await tester.tap(find.text('Xong dàn ý — viết nháp ✍️'));
  await tester.pumpAndSettle();
  await tester.enterText(find.byType(TextField), draft);
  await tester.pumpAndSettle();
  await tester.tap(find.text('Nộp nháp'));
  await tester.pumpAndSettle();
}

VoidCallback? _onPressedOf(WidgetTester t, String label) =>
    t.widget<FilledButton>(find.widgetWithText(FilledButton, label)).onPressed;

void main() {
  test('resolver: compose → compose surface', () {
    expect(resolveSurface(_compose), SurfaceKind.compose);
  });

  testWidgets('⭐ REVEAL gate: KHÔNG có góp ý/checklist trước khi trẻ nộp nháp',
      (tester) async {
    await _pump(tester);
    // Stage dàn ý.
    expect(find.text('Nhờ SAM góp ý ✋'), findsNothing,
        reason: 'đột biến mở nút góp ý ở dàn ý ⇒ test đỏ');
    for (final q in _compose.composeChecklist) {
      expect(find.text('• $q'), findsNothing);
    }
    // Sang stage nháp — vẫn CHƯA có góp ý (chưa có sản phẩm để góp).
    await tester.tap(find.text('Xong dàn ý — viết nháp ✍️'));
    await tester.pumpAndSettle();
    expect(find.text('Nhờ SAM góp ý ✋'), findsNothing,
        reason: 'đột biến mở góp ý khi mới có ô nháp trống ⇒ test đỏ');
  });

  testWidgets('nút «Nộp nháp» KHOÁ khi nháp trống, MỞ khi có chữ',
      (tester) async {
    await _pump(tester);
    await tester.tap(find.text('Xong dàn ý — viết nháp ✍️'));
    await tester.pumpAndSettle();
    expect(_onPressedOf(tester, 'Nộp nháp'), isNull,
        reason: 'nháp trống ⇒ không nộp được (không tạo bằng chứng rỗng)');
    await tester.enterText(find.byType(TextField), 'Trời đổ mưa rào.');
    await tester.pumpAndSettle();
    expect(_onPressedOf(tester, 'Nộp nháp'), isNotNull);
  });

  testWidgets('sau nộp nháp ⇒ mở đúng 3 lựa chọn (góp ý / tự sửa / xong)',
      (tester) async {
    await _pump(tester);
    await _toAfterDraft(tester, 'Trời đổ mưa rào. Sau đó, nắng lại lên.');
    expect(find.text('Nhờ SAM góp ý ✋'), findsOneWidget);
    expect(find.text('Tự đọc lại rồi sửa'), findsOneWidget);
    expect(find.text('Mình xong rồi'), findsOneWidget);
    // Nháp của trẻ được hiện lại để soát — nhưng KHÔNG có bài mẫu nào.
    expect(find.textContaining('Nháp của con:'), findsOneWidget);
  });

  testWidgets('⭐ nhờ góp ý → sửa ⇒ guidedAttempt + support hint; checklist là '
      'CÂU HỎI, không viết thay', (tester) async {
    List<LearningEvent> out = const [];
    await _pump(tester, onFinished: (e) => out = e);
    await _toAfterDraft(tester, 'Mưa. Nắng.');
    await tester.tap(find.text('Nhờ SAM góp ý ✋'));
    await tester.pumpAndSettle();
    // Checklist hiện — và là câu hỏi tự soát.
    for (final q in _compose.composeChecklist) {
      expect(find.text('• $q'), findsOneWidget);
    }
    expect(find.textContaining('không viết hộ'), findsOneWidget);
    // Trẻ sửa rồi nộp bản sửa.
    await tester.enterText(
        find.byType(TextField), 'Trời đổ mưa rào. Sau đó, nắng lại lên.');
    await tester.pumpAndSettle();
    await tester.tap(find.text('Nộp bản sửa'));
    await tester.pumpAndSettle();

    final draft =
        out.firstWhere((e) => e.kind == EvidenceKind.independentAttempt);
    final revision =
        out.firstWhere((e) => e.kind == EvidenceKind.guidedAttempt);
    expect(draft.support, SupportLevel.none);
    expect(revision.support, SupportLevel.hint,
        reason: 'sửa SAU góp ý là có hỗ trợ — KHÔNG tính tự làm');
    expect(out.any((e) => e.kind == EvidenceKind.hintRequested), isTrue);
    expect(out.every((e) => e.correct == null), isTrue,
        reason: 'đột biến chấm văn đúng/sai ⇒ test đỏ (UNKNOWN ≠ SAI)');
    expect(out.every((e) => e.policyId == 'compose-lite-v1'), isTrue);
  });

  testWidgets('⭐ tự đọc lại rồi sửa (KHÔNG nhờ góp ý) ⇒ selfCorrection, '
      'support none', (tester) async {
    List<LearningEvent> out = const [];
    await _pump(tester, onFinished: (e) => out = e);
    await _toAfterDraft(tester, 'Mưa rơi.');
    await tester.tap(find.text('Tự đọc lại rồi sửa'));
    await tester.pumpAndSettle();
    // Không nhờ góp ý ⇒ KHÔNG hiện checklist.
    for (final q in _compose.composeChecklist) {
      expect(find.text('• $q'), findsNothing);
    }
    await tester.enterText(
        find.byType(TextField), 'Trời đổ mưa rào rồi tạnh hẳn.');
    await tester.pumpAndSettle();
    await tester.tap(find.text('Nộp bản sửa'));
    await tester.pumpAndSettle();

    final revision =
        out.firstWhere((e) => e.kind == EvidenceKind.selfCorrection);
    expect(revision.support, SupportLevel.none);
    expect(out.any((e) => e.kind == EvidenceKind.hintRequested), isFalse,
        reason: 'không nhờ góp ý ⇒ không có hintRequested');
    expect(out.every((e) => e.correct == null), isTrue);
  });

  // ⭐⭐ WAL-189 — cùng luật WAL-175/178: tra cứu sinh TRACE, không sinh
  // EVIDENCE. Trước WAL-189, Compose không nhận learningContext nên nộp nháp
  // qua ý định "Xem trong sách" vẫn ghi evidence như một lần viết bài thật.
  testWidgets('⭐⭐ ý định lookup ⇒ KHÔNG sinh evidence dù trẻ nộp nháp',
      (tester) async {
    List<LearningEvent>? out;
    await _pump(tester,
        context: const LearningContext(
            learnerId: 'na', grade: 5, intent: LearningIntent.lookup),
        onFinished: (e) => out = e);
    await _toAfterDraft(tester, 'Trời đổ mưa rào.');
    await tester.tap(find.text('Mình xong rồi'));
    await tester.pumpAndSettle();
    expect(out, isEmpty,
        reason: '⭐⭐ đột biến bỏ gate lookup ⇒ đỏ — tra cứu không phải bằng '
            'chứng, dù trẻ có viết gì');
  });

  testWidgets('không %, không điểm, không khen TƯ CHẤT ở mọi trạng thái',
      (tester) async {
    await _pump(tester);
    void scan() {
      for (final w in tester.widgetList<Text>(find.byType(Text))) {
        final t = w.data ?? '';
        expect(t.contains('%'), isFalse, reason: 'cấm %: "$t"');
        expect(t.contains('điểm'), isFalse, reason: 'cấm điểm: "$t"');
        for (final banned in bannedAbilityPraise) {
          expect(t.contains(banned), isFalse, reason: 'cấm khen tư chất: "$t"');
        }
      }
    }

    scan();
    await _toAfterDraft(tester, 'Mưa to. Rồi tạnh.');
    scan();
    await tester.tap(find.text('Nhờ SAM góp ý ✋'));
    await tester.pumpAndSettle();
    scan();
    await tester.enterText(find.byType(TextField), 'Mưa to rồi tạnh dần.');
    await tester.pumpAndSettle();
    await tester.tap(find.text('Nộp bản sửa'));
    await tester.pumpAndSettle();
    scan();
  });
}
