/// TRACK B — Học với SAM: vòng lặp nhìn thấy, nhãn kịch bản, không chê,
/// thẻ kết chỉ ghi nhận THAM GIA.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/tutor_script.dart';
import 'package:learning_coach/core/pedagogy/pedagogy_runtime.dart';
import 'package:learning_coach/features/lesson_workspace/widgets/runtime_plan.dart';
import 'package:learning_coach/features/lesson_workspace/tutor_view.dart';

import 'support.dart';

void main() {
  testWidgets('⭐ nhãn «SAM (kịch bản thử nghiệm)» + giải thích → Tiếp → hỏi', (
    t,
  ) async {
    await t.pumpWidget(
      fixtureHost(
        Scaffold(
          body: TutorView(doc: loadSyntheticDoc(), onNext: (_, _) {}),
        ),
      ),
    );
    await t.pumpAndSettle();
    expect(find.text('SAM (kịch bản thử nghiệm)'), findsWidgets);
    expect(find.textContaining('không ghi bằng chứng học'), findsOneWidget);
    expect(find.textContaining('[MẪU] Bài này nói về'), findsOneWidget);
    // A7.2 — nhãn THEO BƯỚC: bước giải thích có block nguồn ⇒ runtime kiểm.
    expect(find.text('SAM (runtime có kiểm)'), findsOneWidget);
    expect(
      find.textContaining('Runtime kiểm được 4/12 bước'),
      findsOneWidget,
      reason: 'PEDAGOGY REALITY nhìn thấy: 4 runtimeGuided / 8 prototype',
    );
    expect(find.text('SÁCH VIẾT'), findsOneWidget, reason: 'trích block nguồn');
    await t.tap(find.text('Tiếp ▸'));
    await t.pumpAndSettle();
    expect(find.textContaining('Làm muối từ nước biển'), findsOneWidget);
    expect(find.text('Cô cạn'), findsOneWidget);
  });

  testWidgets('⭐⭐ chọn sai ⇒ gợi ý (không chê); sai tiếp ⇒ gợi ý 2; sai nữa ⇒ '
      'scaffold và đi tiếp — không «Chính xác», không kẹt', (t) async {
    await t.pumpWidget(
      fixtureHost(
        Scaffold(
          body: TutorView(doc: loadSyntheticDoc(), onNext: (_, _) {}),
        ),
      ),
    );
    await t.pumpAndSettle();
    await t.tap(find.text('Tiếp ▸'));
    await t.pumpAndSettle();
    final loc = find.widgetWithText(FilledButton, 'Lọc');
    await t.tap(loc);
    await t.pumpAndSettle();
    expect(find.textContaining('Gợi ý 1'), findsOneWidget);
    // gợi ý vẫn là kịch bản (HINT_UNSOURCED) ⇒ nhãn kịch bản, không giả
    expect(find.text('SAM (kịch bản thử nghiệm)'), findsWidgets);
    await t.tap(loc);
    await t.pumpAndSettle();
    expect(find.textContaining('Gợi ý 2'), findsOneWidget);
    await t.tap(loc);
    await t.pumpAndSettle();
    expect(find.textContaining('Chưa khớp, không sao'), findsOneWidget);
    expect(find.textContaining('Khớp với bảng mẫu'), findsNothing);
    expect(find.textContaining('Chính xác'), findsNothing);
    // đã sang câu hỏi mở tiếp theo
    expect(find.byKey(const Key('tutor-answer-field')), findsOneWidget);
    for (final s in ['sai', 'kém', 'tệ']) {
      expect(find.textContaining(s), findsNothing, reason: 'không chê');
    }
  });

  testWidgets('chọn đúng ⇒ phản hồi khớp; gõ trả lời khớp mẫu ⇒ thẻ kết THAM '
      'GIA + bước tiếp', (t) async {
    NextTarget? target;
    await t.pumpWidget(
      fixtureHost(
        Scaffold(
          body: TutorView(
            doc: loadSyntheticDoc(),
            onNext: (tg, _) => target = tg,
          ),
        ),
      ),
    );
    await t.pumpAndSettle();
    await t.tap(find.text('Tiếp ▸'));
    await t.pumpAndSettle();
    await t.tap(find.text('Cô cạn'));
    await t.pumpAndSettle();
    expect(find.textContaining('Khớp với bảng mẫu'), findsOneWidget);
    await t.enterText(
      find.byKey(const Key('tutor-answer-field')),
      'vì cát nặng hơn nước',
    );
    await t.tap(find.byKey(const Key('tutor-send')));
    await t.pumpAndSettle();
    expect(find.textContaining('nặng hơn» — khớp ý mẫu'), findsOneWidget);
    expect(find.byKey(TutorView.endCardKey), findsOneWidget);
    expect(find.text('Con đã học cùng SAM phần này'), findsOneWidget);
    expect(find.textContaining('chưa phải bằng chứng'), findsOneWidget);
    await t.tap(find.textContaining('Đọc lại phần'));
    expect(target, NextTarget.read);
  });

  testWidgets('nút gợi ý dùng được trước khi trả lời, ẩn khi hết', (t) async {
    await t.pumpWidget(
      fixtureHost(
        Scaffold(
          body: TutorView(doc: loadSyntheticDoc(), onNext: (_, _) {}),
        ),
      ),
    );
    await t.pumpAndSettle();
    await t.tap(find.text('Tiếp ▸'));
    await t.pumpAndSettle();
    await t.tap(find.textContaining('Gợi ý cho tớ'));
    await t.pumpAndSettle();
    await t.tap(find.textContaining('Gợi ý cho tớ'));
    await t.pumpAndSettle();
    expect(find.textContaining('SAM đã gợi ý hết rồi'), findsOneWidget);
  });

  testWidgets('neo vào đoạn có bước ⇒ bắt đầu ở câu hỏi của đoạn đó', (
    t,
  ) async {
    final d = loadSyntheticDoc();
    final q = d.tutorScript!.asks.first.promptBlockId!;
    await t.pumpWidget(
      fixtureHost(
        Scaffold(
          body: TutorView(doc: d, anchorBlockId: q, onNext: (_, _) {}),
        ),
      ),
    );
    await t.pumpAndSettle();
    expect(find.textContaining('Con hỏi về đoạn:'), findsOneWidget);
    expect(find.text('Cô cạn'), findsOneWidget, reason: 'vào thẳng câu hỏi');
  });

  testWidgets('ROUND 3 B4: dải pha sáng đúng pha — giải thích → hỏi/con trả '
      'lời → gợi ý → phản hồi → tiếp; «Câu n/N»; chữ cái A/B/C/D', (t) async {
    final d = loadSyntheticDoc();
    await t.pumpWidget(
      fixtureHost(Scaffold(body: TutorView(doc: d, onNext: (_, _) {}))),
    );
    await t.pumpAndSettle();
    expect(find.byKey(TutorView.phaseStripKey), findsOneWidget);
    Text chip(String label) => t.widget<Text>(find.text(label));
    expect(chip('Giải thích').style?.fontWeight, FontWeight.w700);
    await t.tap(find.text('Tiếp ▸'));
    await t.pumpAndSettle();
    expect(chip('Con trả lời').style?.fontWeight, FontWeight.w700);
    expect(chip('Giải thích').style?.fontWeight, FontWeight.w500);
    expect(find.text('Câu 1/${d.tutorScript!.asks.length}'), findsOneWidget);
    // chữ cái lựa chọn — nhãn, không đổi chuỗi khớp
    expect(find.text('A'), findsOneWidget);
    expect(find.text('B'), findsOneWidget);
    expect(find.widgetWithText(FilledButton, 'Cô cạn'), findsOneWidget);
    await t.tap(find.textContaining('Gợi ý cho tớ'));
    await t.pumpAndSettle();
    expect(chip('Gợi ý').style?.fontWeight, FontWeight.w700);
    await t.tap(find.widgetWithText(FilledButton, 'Cô cạn'));
    await t.pumpAndSettle();
    expect(chip('Phản hồi').style?.fontWeight, FontWeight.w700);
    expect(find.text('Câu 2/${d.tutorScript!.asks.length}'), findsOneWidget);
  });

  test('ROUND 3 B4: phaseOf / askedCount tất định từ runner', () {
    final d = loadSyntheticDoc();
    final r = TutorRunner(d.tutorScript!);
    expect(TutorView.phaseOf(r), 0);
    r.advance();
    expect(TutorView.phaseOf(r), 2, reason: 'SAM vừa hỏi ⇒ lượt con');
    expect(TutorView.askedCount(r), 0);
    r.requestHint();
    expect(TutorView.phaseOf(r), 3);
    r.submit('Cô cạn');
    expect(TutorView.phaseOf(r), 4, reason: 'phản hồi khớp + câu mới');
    expect(TutorView.askedCount(r), 1);
    expect(TutorView.askCaption(d.tutorScript!, d.tutorScript!.asks.first.id),
        'Câu 1/${d.tutorScript!.asks.length}');
    expect(TutorView.askCaption(d.tutorScript!, 'e1'), isNull);
  });

  testWidgets('ROUND 3 B4: thẻ kết đếm câu đã ĐI QUA (tham gia), không điểm', (
    t,
  ) async {
    await t.pumpWidget(
      fixtureHost(
        Scaffold(body: TutorView(doc: loadSyntheticDoc(), onNext: (_, _) {})),
      ),
    );
    await t.pumpAndSettle();
    await t.tap(find.text('Tiếp ▸'));
    await t.pumpAndSettle();
    await t.tap(find.widgetWithText(FilledButton, 'Cô cạn'));
    await t.pumpAndSettle();
    await t.enterText(
      find.byKey(const Key('tutor-answer-field')),
      'vì cát nặng hơn nước',
    );
    await t.tap(find.byKey(const Key('tutor-send')));
    await t.pumpAndSettle();
    expect(find.byKey(TutorView.endCardKey), findsOneWidget);
    expect(find.textContaining('Con đã đi qua 2/2 câu hỏi'), findsOneWidget);
    for (final w in t.widgetList<Text>(find.byType(Text))) {
      final s = (w.data ?? '').toLowerCase();
      expect(s, isNot(contains('điểm')));
      expect(s, isNot(contains('%')));
      expect(s, isNot(contains('chính xác')));
    }
  });

  test('ROUND 3 A7 — PEDAGOGY REALITY của bài mẫu: 4 runtimeGuided / 8 '
      'prototypeScripted; không bước nào có validator; nhãn theo bước', () {
    final d = loadSyntheticDoc();
    final plan = planForDoc(d, learnerId: 'na')!;
    expect(plan.isBound, isTrue);
    expect(plan.runtimeGuidedCount, 4);
    expect(plan.prototypeCount, 8);
    expect(plan.steps.every((s) => s.validator == null), isTrue);
    final r = TutorRunner(d.tutorScript!);
    final explain = TutorView.stepForTurn(plan, r.transcript, 0)!;
    expect(explain.mode.childLabel, 'SAM (runtime có kiểm)');
    r.advance();
    r.requestHint();
    r.requestHint();
    final n = r.transcript.length;
    final h1 = TutorView.stepForTurn(plan, r.transcript, n - 2)!;
    final h2 = TutorView.stepForTurn(plan, r.transcript, n - 1)!;
    expect([h1.hintIndex, h2.hintIndex], [0, 1]);
    expect(h1.mode.childLabel, 'SAM (kịch bản thử nghiệm)');
    // không có learner ⇒ context vẫn giải ra bài ⇒ vẫn ràng buộc được
    expect(planForDoc(d)!.isBound, isTrue);
  });

  test('ROUND 3 — gợi ý prototype KHÔNG nêu dạng đáp án (guard REVEAL)', () {
    final d = loadSyntheticDoc();
    final plan = planForDoc(d, learnerId: 'na')!;
    final leaks = [
      for (final s in plan.steps)
        if (s.phase == PlannedStepPhase.hint &&
            s.refusals.any((x) => x.startsWith('GUARD:REVEAL')))
          '${s.stepId}#${s.hintIndex}',
    ];
    expect(leaks, isEmpty, reason: leaks.join(','));
    for (final a in d.tutorScript!.asks) {
      final forms = PedagogyRuntime.literalAnswerForms(a.acceptable);
      for (final h in a.hints) {
        final squashed = h.toLowerCase().replaceAll(' ', '');
        for (final f in forms) {
          expect(squashed, isNot(contains(f)), reason: '${a.id}: «$h» nêu «$f»');
        }
      }
    }
  });
}
