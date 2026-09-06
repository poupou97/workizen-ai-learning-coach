/// ROUND 7 · V2 — VÒNG LẶP DẠY TRÊN MÀN (Founder order 49 §2).
///
/// `answer_diagnosis_test.dart` chứng minh LỜI đúng. Tệp này chứng minh trẻ
/// THẤY nó, và thấy đúng thứ tự: GIẢI THÍCH → HỎI → TRẺ TRẢ LỜI → PHẢN HỒI
/// THEO CÂU TRẢ LỜI → GIẢI THÍCH KHÁC → THỬ LẠI.
///
/// Ba điều dễ hỏng nhất, mỗi điều một test:
/// 1. Hai đáp án sai KHÁC NHAU trên MÀN, không chỉ trong mô hình.
/// 2. Sau phản hồi, vòng lặp CHƯA đóng — câu hỏi vẫn còn, có lời mời thử lại.
/// 3. Trả lời khớp KHÔNG được đọc thành «đã thạo»: màn nói mấy lần thử,
///    mấy gợi ý, và trẻ đã MỞ cách học nào.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/lesson_model/next_action.dart';
import 'package:learning_coach/core/lesson_model/tutor_script.dart';
import 'package:learning_coach/features/lesson_workspace/teaching/answer_diagnosis.dart';
import 'package:learning_coach/features/lesson_workspace/teaching/diagnosis_card.dart';
import 'package:learning_coach/features/lesson_workspace/tutor_view.dart';

import 'support.dart';

/// Nokia 6.1 ở 360 dp: mọi phép đo dưới đây phải đúng ở KHỔ MÁY THẬT, không
/// phải ở khổ mặc định 800×600 của test.
const _nokia = Size(360, 640);

Future<void> _openTutor(
  WidgetTester t, {
  LessonDocument? doc,
  Set<WorkspaceView> seen = const {},
  void Function(String semanticId)? onOpenVisual,
}) async {
  await t.binding.setSurfaceSize(_nokia);
  addTearDown(() => t.binding.setSurfaceSize(null));
  await t.pumpWidget(
    fixtureHost(
      Scaffold(
        body: TutorView(
          doc: doc ?? loadSyntheticDoc(),
          viewsSeen: seen,
          onOpenVisual: onOpenVisual,
          onNext: (_, _) {},
        ),
      ),
    ),
  );
  await t.pumpAndSettle();
  await tapScrolled(t, find.text('Tiếp ▸'));
}

/// Ở khổ Nokia (640 dp) phần lớn nút nằm dưới nếp gấp — cuộn tới rồi mới
/// chạm, đúng như trẻ phải làm trên máy.
Future<void> tapScrolled(WidgetTester t, Finder f) async {
  await t.ensureVisible(f.first);
  await t.pumpAndSettle();
  await t.tap(f.first);
  await t.pumpAndSettle();
}

/// Toàn bộ chữ đang hiện trên màn.
List<String> _screenText(WidgetTester t) => t
    .widgetList<Text>(find.byType(Text))
    .map((w) => w.data ?? '')
    .where((s) => s.isNotEmpty)
    .toList();

void main() {
  testWidgets('⭐⭐ HAI ĐÁP ÁN SAI ⇒ HAI LỜI KHÁC NHAU trên chính màn hình', (
    t,
  ) async {
    // Bài mẫu có «Lọc» (bảng nêu) và «Chiết» (bảng KHÔNG nêu) ⇒ hai nhánh
    // khác nhau, hai lời khác nhau. Đây đúng là điều Founder bảo phải nhìn
    // thấy trên máy: nếu hai phương án nhiễu ra cùng một câu thì hỏng.
    await _openTutor(t);
    await tapScrolled(t, find.widgetWithText(FilledButton, 'Lọc'));
    final afterLoc = _screenText(t).join('\n');
    expect(find.byKey(DiagnosisCard.rootKey), findsOneWidget);
    expect(afterLoc, contains('Con chọn «Lọc (mẫu)»'));

    await tapScrolled(t, find.widgetWithText(FilledButton, 'Chiết'));
    final afterChiet = _screenText(t).join('\n');
    expect(afterChiet, contains('«Chiết»'));

    // Lời cho «Chiết» KHÔNG phải lời cho «Lọc».
    expect(
      afterChiet.contains('Con chọn «Chiết». Sách viết'),
      isFalse,
      reason: 'bảng mẫu không nêu «Chiết» ⇒ không được bịa dòng sách cho nó',
    );
    expect(find.byKey(DiagnosisCard.kindKey(DiagnosisKind.misconception)),
        findsOneWidget);
    expect(find.byKey(DiagnosisCard.kindKey(DiagnosisKind.insufficient)),
        findsOneWidget);

    // …và KHÔNG có câu mặc định nào dùng cho cả hai.
    for (final banned in ['gần rồi', 'Chưa đúng —', 'kém', 'giỏi']) {
      expect(afterChiet, isNot(contains(banned)));
    }
  });

  testWidgets('⭐ sau phản hồi, vòng lặp CHƯA đóng: câu hỏi còn đó, có lời mời '
      'thử lại, đáp án đã thử được đánh dấu', (t) async {
    await _openTutor(t);
    expect(find.byKey(const Key('tutor-retry-banner')), findsNothing);
    await tapScrolled(t, find.widgetWithText(FilledButton, 'Lọc'));

    // 1) câu hỏi vẫn còn — cùng bộ lựa chọn, vẫn bấm được
    expect(find.widgetWithText(FilledButton, 'Cô cạn'), findsOneWidget);
    expect(find.widgetWithText(FilledButton, 'Lọc'), findsOneWidget);

    // 2) lời mời thử lại nhìn thấy được (nếu không, trẻ tưởng câu đã đóng)
    expect(find.byKey(const Key('tutor-retry-banner')), findsOneWidget);
    expect(find.byKey(DiagnosisCard.retryKey), findsWidgets);

    // 3) đáp án ĐÃ THỬ có dấu — không khoá, chỉ đánh dấu
    expect(find.byKey(const Key('tutor-option-tried-0')), findsOneWidget);
    expect(find.byKey(const Key('tutor-option-tried-1')), findsNothing);

    // 4) dải pha vẫn còn (vòng lặp chưa đóng) và pha cuối là THỬ LẠI
    expect(find.byKey(TutorView.phaseStripKey), findsOneWidget);
    expect(TutorView.phases.last, 'Thử lại');
  });

  test('⭐ THỨ TỰ của order 49 §2: phản hồi theo lỗi đứng TRƯỚC cách giải '
      'thích khác, và bước hỏi KHÔNG bị đóng', () {
    final d = loadSyntheticDoc();
    final r = TutorRunner(
      d.tutorScript!,
      diagnose: (step, answer, earlier) => diagnoseAnswer(
        step: step,
        answer: answer,
        semantic: d.semantic,
        earlierAnswers: earlier,
      )?.headline,
    )..advance();
    final q = r.current as AskStep;
    expect(r.submit('Lọc'), TurnKind.hint);
    expect(
      r.transcript.map((t) => t.kind).toList().sublist(
        r.transcript.length - 3,
      ),
      [TurnKind.learner, TurnKind.diagnose, TurnKind.hint],
      reason: 'PHẢN HỒI trước, GIẢI THÍCH KHÁC sau — không phải ngược lại',
    );
    expect(r.current, same(q), reason: 'chưa đóng câu: trẻ còn được thử lại');
    expect(TutorView.phaseOf(r), 5, reason: 'dải pha sáng «Thử lại»');

    // Không có hook ⇒ hành vi trước vòng 7 V2 giữ nguyên (không lượt thừa).
    final plain = TutorRunner(d.tutorScript!)..advance();
    plain.submit('Lọc');
    expect(
      plain.transcript.any((t) => t.kind == TurnKind.diagnose),
      isFalse,
    );
  });

  testWidgets('⭐⭐ CORRECT ANSWER != MASTERY — khớp sau hai lần thử và một gợi '
      'ý thì màn NÓI ĐÚNG THẾ, không phong trạng thái', (t) async {
    await _openTutor(t, seen: {WorkspaceView.visual});
    await tapScrolled(t, find.widgetWithText(FilledButton, 'Lọc'));
    await tapScrolled(t, find.widgetWithText(FilledButton, 'Cô cạn'));

    final story = t.widget<Text>(
      find.byKey(const Key('tutor-attempt-story')),
    );
    expect(story.data, contains('lần thử thứ 2'));
    expect(story.data, contains('sau 1 gợi ý'));
    // TRACE != EVIDENCE: «đã MỞ», không bao giờ «đã hiểu».
    expect(story.data, contains('đã mở Trực quan'));

    final screen = _screenText(t).join('\n').toLowerCase();
    for (final banned in [
      'đã thạo',
      'thành thạo',
      'con hiểu rồi',
      'hoàn thành bài',
      'điểm',
      '%',
      '⭐',
    ]) {
      expect(screen, isNot(contains(banned)), reason: '«$banned» trên màn');
    }
  });

  testWidgets('⭐ câu tự viết không đối chiếu được ⇒ SAM nói ĐÚNG GIỚI HẠN của '
      'mình, không suy diễn hiểu hay chưa', (t) async {
    await _openTutor(t);
    await tapScrolled(t, find.widgetWithText(FilledButton, 'Cô cạn'));
    await t.ensureVisible(find.byKey(const Key('tutor-answer-field')));
    await t.pumpAndSettle();
    await t.enterText(find.byKey(const Key('tutor-answer-field')), 'zzz qqq');
    await tapScrolled(t, find.byKey(const Key('tutor-send')));

    expect(find.byKey(DiagnosisCard.limitKey), findsOneWidget);
    expect(
      find.byKey(DiagnosisCard.kindKey(DiagnosisKind.insufficient)),
      findsOneWidget,
    );
    expect(find.textContaining('SAM CHỈ BIẾT CHỪNG NÀY'), findsOneWidget);
    final screen = _screenText(t).join('\n');
    expect(screen, contains('KHÔNG BIẾT'));
    expect(screen, isNot(contains('con chưa hiểu')));
  });

  test('⭐⭐ LỖI MÁY THẬT (lượt 1): neo cuộn phải rơi vào lượt PHẢN HỒI, không '
      'phải lượt gợi ý — nếu không, vòng lặp bị đảo ngay trên màn', () {
    final d = loadSyntheticDoc();
    final r = TutorRunner(
      d.tutorScript!,
      diagnose: (step, answer, earlier) => diagnoseAnswer(
        step: step,
        answer: answer,
        semantic: d.semantic,
        earlierAnswers: earlier,
      )?.headline,
    )..advance();
    r.submit('Lọc');
    // ba lượt cuối: con trả lời · phản hồi · gợi ý
    final i = TutorView.debugAnchorIndex(r);
    expect(
      r.transcript[i].kind,
      TurnKind.diagnose,
      reason: 'màn phải mở ra ở câu SAM nói về ĐÁP ÁN CỦA TRẺ',
    );
    expect(i, lessThan(r.transcript.length - 1), reason: 'gợi ý nằm SAU nó');

    // Không có phản hồi (không hook) ⇒ giữ hành vi cũ: lượt SAM cuối.
    final plain = TutorRunner(d.tutorScript!)..advance();
    plain.submit('Lọc');
    expect(
      plain.transcript[TutorView.debugAnchorIndex(plain)].kind,
      TurnKind.hint,
    );
  });

  testWidgets('⭐ bài mẫu KHÔNG có sơ đồ mang đúng tên ấy ⇒ SAM nói thẳng, '
      'không gợi bừa một liên hệ', (t) async {
    // Bảng mẫu đặt tên thực thể là «Lọc (mẫu)» còn quy trình tên «Lọc nước
    // đục (thí nghiệm mẫu)» — KHÔNG khớp nguyên từ. Đúng ra phải nói không
    // có, chứ không phải nới phép khớp cho ra một liên hệ.
    await _openTutor(t);
    await tapScrolled(t, find.widgetWithText(FilledButton, 'Lọc'));
    expect(find.byKey(DiagnosisCard.linksEmptyKey), findsOneWidget);
    expect(
      find.textContaining('không dựng thêm sơ đồ'),
      findsOneWidget,
    );
  });

  testWidgets('FIXTURE THẬT — liên hệ trong lời phản hồi mở ĐÚNG sơ đồ ấy ở '
      'Trực quan', (t) async {
    final doc = loadRealDocOrSkip();
    if (doc == null) return;
    String? opened;
    await _openTutor(t, doc: doc, onOpenVisual: (id) => opened = id);
    await tapScrolled(t, find.widgetWithText(FilledButton, 'Lọc'));
    final link = find.byKey(DiagnosisCard.linkKey('process-1'));
    expect(link, findsOneWidget, reason: 'bài thật nhắc «Lọc» ở quy trình 1');
    await tapScrolled(t, link);
    expect(opened, 'process-1');
  });

  testWidgets('không tràn ở khổ Nokia sau khi thêm lời phản hồi', (t) async {
    await _openTutor(t);
    await tapScrolled(t, find.widgetWithText(FilledButton, 'Lọc'));
    expect(t.takeException(), isNull);
    await tapScrolled(t, find.widgetWithText(FilledButton, 'Chiết'));
    expect(t.takeException(), isNull);
  });

  group('FIXTURE THẬT — Bài 17 trên khổ máy thật', () {
    testWidgets('⭐⭐ ba phương án nhiễu của câu 1 ⇒ ba màn khác nhau', (
      t,
    ) async {
      final doc = loadRealDocOrSkip();
      if (doc == null) return;
      await _openTutor(t, doc: doc);
      final q1 = doc.tutorScript!.asks.first;
      final wrong = [
        for (final o in q1.options)
          if (!answerMatches(o, q1.acceptable)) o,
      ];
      final seen = <String>{};
      for (final w in wrong) {
        await tapScrolled(t, find.widgetWithText(FilledButton, w));
        final card = t
            .widgetList<Text>(
              find.descendant(
                of: find.byKey(DiagnosisCard.rootKey).last,
                matching: find.byType(Text),
              ),
            )
            .map((x) => x.data ?? '')
            .join(' ');
        expect(t.takeException(), isNull, reason: 'không tràn ở 360 dp');
        seen.add(card);
      }
      expect(
        seen.length,
        wrong.length,
        reason: 'ba phương án nhiễu ⇒ ba thẻ phản hồi khác nhau TRÊN MÀN',
      );
    });
  });
}
