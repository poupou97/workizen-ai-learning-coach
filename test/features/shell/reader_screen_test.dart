/// WAL-98 — Surface READER: luật giữ bằng test, trên bài đọc-hiểu THẬT của
/// corpus (TV5 tập hai, chuỗi liên-kết-câu). Falsification: mỗi bất biến kèm một
/// đột biến làm test đỏ (ghi trong reason).
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/context/learning_context.dart';
import 'package:learning_coach/core/intent/learning_intent.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/core/tutor/learning_activity.dart';
import 'package:learning_coach/features/shell/reader_screen.dart';

const _ctx = LearningContext(learnerId: 'na', grade: 5);

/// Bài THẬT: đọc đoạn về Thạch Sanh rồi tìm từ chỉ nhân vật ở câu sau
/// (liên-kết-câu bằng đại từ — chuỗi b9→b13 GĐ2 batch ③).
const _reading = LearningActivity(
  activityId: 'tv5-doc-b9',
  prompt: 'Từ ngữ nào ở câu thứ hai được dùng để chỉ Thạch Sanh?',
  response: ResponseKind.readRespond,
  conceptId: 'lien-ket-cau',
  skillCaseId: 'lkc-nhan-biet-thay-the',
  passage: 'Một hôm, Thạch Sanh ngồi trong ngục tối. Chàng lấy cây đàn vua ban '
      'ra gảy. Tiếng đàn vẳng đến hoàng cung.',
  options: ['Chàng', 'ngục tối', 'cây đàn'],
  correctOption: 0,
  sourceBook: '05-sgk-tieng-viet-5-tap-hai',
  sourcePage: 45,
);

/// Bài đọc-hiểu chưa có đáp án — UNKNOWN không được thành SAI.
const _readingUnknown = LearningActivity(
  activityId: 'tv5-doc-unknown',
  prompt: 'Theo em, chi tiết nào trong đoạn là hay nhất?',
  response: ResponseKind.readRespond,
  conceptId: 'doc-hieu',
  passage: 'Mùa thu, lá vàng rơi đầy sân trường. Gió heo may se lạnh.',
  options: ['câu 1', 'câu 2'],
);

/// readRespond nhưng THIẾU đoạn văn ⇒ Reader phải nói KHÔNG HỖ TRỢ, không bịa.
const _noPassage = LearningActivity(
  activityId: 'tv5-doc-nopassage',
  prompt: 'Đọc rồi trả lời.',
  response: ResponseKind.readRespond,
  conceptId: 'doc-hieu',
  options: ['a', 'b'],
);

Future<void> _pump(WidgetTester tester, LearningActivity a,
    {void Function(List<LearningEvent>)? onFinished,
    LearningContext context = _ctx}) async {
  await tester.pumpWidget(MaterialApp(
      home: ReaderScreen(
    key: ValueKey(a.activityId),
    activity: a,
    learningContext: context,
    now: () => DateTime(2026, 9, 1, 19),
    onFinished: onFinished,
  )));
}

void main() {
  test('resolver: readRespond → reader (không ép sang quiz)', () {
    expect(resolveSurface(_reading), SurfaceKind.reader);
  });

  testWidgets('⭐ REVEAL/READ gate: câu hỏi KHOÁ tới khi trẻ xác nhận đọc xong',
      (tester) async {
    await _pump(tester, _reading);
    // Trước khi đọc xong: thấy đoạn văn + nút đọc-xong, KHÔNG thấy đáp án.
    expect(find.textContaining('Thạch Sanh'), findsWidgets);
    expect(find.text('Con đọc xong rồi 📖'), findsOneWidget);
    for (final opt in _reading.options) {
      expect(find.text(opt), findsNothing,
          reason: 'đột biến mở đáp án trước khi đọc ⇒ test này đỏ');
    }
    // Sau khi xác nhận đọc: câu hỏi + đáp án mới hiện.
    await tester.tap(find.text('Con đọc xong rồi 📖'));
    await tester.pumpAndSettle();
    expect(find.text(_reading.prompt), findsOneWidget);
    expect(find.text('Chàng'), findsOneWidget);
  });

  testWidgets('«đọc xong» KHÔNG phát bằng chứng tri thức (đọc ≠ mastery)',
      (tester) async {
    List<LearningEvent> out = const [];
    await _pump(tester, _reading, onFinished: (e) => out = e);
    await tester.tap(find.text('Con đọc xong rồi 📖'));
    await tester.pumpAndSettle();
    // Chưa trả lời ⇒ chưa có onFinished, và không nên có event nào tích luỹ.
    expect(out, isEmpty);
    // Trả lời đúng ⇒ event ĐẦU TIÊN là attempt, không phải một «read» event.
    await tester.tap(find.text('Chàng'));
    await tester.pumpAndSettle();
    expect(out.first.kind, EvidenceKind.independentAttempt,
        reason: 'đột biến phát event lúc đọc-xong ⇒ event đầu không còn là attempt');
    expect(out.every((e) => e.exerciseId == _reading.activityId), isTrue);
  });

  testWidgets('đọc xong → chọn đúng ⇒ TỰ LÀM (support none), policy reader-v1',
      (tester) async {
    List<LearningEvent> out = const [];
    await _pump(tester, _reading, onFinished: (e) => out = e);
    await tester.tap(find.text('Con đọc xong rồi 📖'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Chàng'));
    await tester.pumpAndSettle();
    final attempt = out.first;
    expect(attempt.kind, EvidenceKind.independentAttempt);
    expect(attempt.correct, isTrue);
    expect(attempt.support, SupportLevel.none);
    expect(attempt.policyId, 'reader-v1');
    expect(out.any((e) => e.kind == EvidenceKind.finalCorrectness), isTrue);
    expect(find.textContaining('TỰ làm được'), findsOneWidget);
  });

  testWidgets('đọc xong → chọn đúng SAU gợi ý ⇒ postHintSuccess + support hint',
      (tester) async {
    List<LearningEvent> out = const [];
    await _pump(tester, _reading, onFinished: (e) => out = e);
    await tester.tap(find.text('Con đọc xong rồi 📖'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Gợi ý cho tớ ✋'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Chàng'));
    await tester.pumpAndSettle();
    final post = out.firstWhere((e) => e.kind == EvidenceKind.postHintSuccess);
    expect(post.support, SupportLevel.hint);
    expect(
        out.any((e) =>
            e.kind == EvidenceKind.independentAttempt && e.correct == true),
        isFalse,
        reason: 'có gợi ý ⇒ KHÔNG có bằng-chứng-tự-làm-đúng');
  });

  testWidgets('⭐ bài đọc-hiểu CHƯA BIẾT đáp án ⇒ không chấm đúng/sai',
      (tester) async {
    List<LearningEvent> out = const [];
    await _pump(tester, _readingUnknown, onFinished: (e) => out = e);
    await tester.tap(find.text('Con đọc xong rồi 📖'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('câu 1'));
    await tester.pumpAndSettle();
    expect(out.single.correct, isNull,
        reason: 'UNKNOWN không bao giờ thành SAI (cũng không thành ĐÚNG)');
    expect(find.textContaining('chưa có đáp án'), findsOneWidget);
  });

  testWidgets('readRespond THIẾU đoạn văn ⇒ nói KHÔNG HỖ TRỢ, không bịa đoạn',
      (tester) async {
    await _pump(tester, _noPassage);
    expect(find.text('Con đọc xong rồi 📖'), findsNothing);
    expect(find.textContaining('chưa có đủ đoạn văn'), findsOneWidget);
  });

  // ---- WAL-113 B1: câu hỏi MỞ từ corpus THẬT (SGK không in đáp án) --------
  const openReading = LearningActivity(
    activityId: '05-sgk-tieng-viet-5-tap-hai:l26:doc-hieu',
    prompt:
        '2. Chuyện gì đã xảy ra với cô bé Xa-đa-cô khi Hi-rô-si-ma bị ném bom?',
    response: ResponseKind.readRespond,
    conceptId: 'tv-doc-hieu',
    passage: 'Ngày 16 tháng 7 năm 1945, nước Mỹ chế tạo được bom nguyên tử. '
        'Hơn nửa tháng sau, chính phủ Mỹ quyết định ném cả hai quả bom mới '
        'chế tạo xuống Nhật Bản.',
    sourceBook: '05-sgk-tieng-viet-5-tap-hai',
    sourcePage: 127,
  );

  testWidgets('⭐ WAL-113: câu hỏi MỞ — READ gate vẫn khoá, không bịa options',
      (tester) async {
    await _pump(tester, openReading);
    expect(find.text('Con đọc xong rồi 📖'), findsOneWidget,
        reason: 'không có options KHÔNG có nghĩa là unsupported — corpus thật');
    expect(find.text('Con đã trả lời xong 🗣'), findsNothing,
        reason: 'đột biến mở nút trả-lời trước khi đọc ⇒ đỏ');
    await tester.tap(find.text('Con đọc xong rồi 📖'));
    await tester.pumpAndSettle();
    expect(find.text(openReading.prompt), findsOneWidget);
    expect(find.text('Con đã trả lời xong 🗣'), findsOneWidget);
  });

  testWidgets('⭐ WAL-113: trả lời MỞ ⇒ MỘT attempt correct=null — UNKNOWN '
      'không thành ĐÚNG hay SAI', (tester) async {
    List<LearningEvent> out = const [];
    await _pump(tester, openReading, onFinished: (e) => out = e);
    await tester.tap(find.text('Con đọc xong rồi 📖'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Con đã trả lời xong 🗣'));
    await tester.pumpAndSettle();
    expect(out.single.kind, EvidenceKind.independentAttempt);
    expect(out.single.correct, isNull,
        reason: '⭐ đột biến ghi correct=true cho câu mở ⇒ test này đỏ');
    expect(out.single.support, SupportLevel.none);
    expect(out.single.knowledgeVersion, isNotNull,
        reason: 'WAL-114: mọi evidence mang knowledge model version');
    expect(out.any((e) => e.kind == EvidenceKind.finalCorrectness), isFalse,
        reason: 'không chấm ⇒ không có finalCorrectness');
    expect(find.textContaining('chưa có đáp án'), findsOneWidget,
        reason: 'nói thật với trẻ: SAM không biết đúng/sai');
  });

  // ⭐⭐ WAL-189 — cùng luật WAL-175/178 đã kiểm ở Experiment: tra cứu sinh
  // TRACE, không sinh EVIDENCE, dù trẻ có trả lời gì. Trước WAL-189, Reader
  // không nhận learningContext nên KHÔNG THỂ áp luật này — bài đọc mở qua ý
  // định "Xem trong sách" vẫn ghi evidence đầy đủ như một lần làm bài thật.

  testWidgets('⭐⭐ ý định lookup ⇒ KHÔNG sinh evidence dù trẻ trả lời',
      (tester) async {
    List<LearningEvent>? out;
    await _pump(tester, _reading,
        context: const LearningContext(
            learnerId: 'na', grade: 5, intent: LearningIntent.lookup),
        onFinished: (e) => out = e);
    await tester.tap(find.text('Con đọc xong rồi 📖'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Chàng'));
    await tester.pumpAndSettle();
    expect(out, isEmpty,
        reason: '⭐⭐ đột biến bỏ gate lookup ⇒ đỏ — WAL-175: tra cứu sinh '
            'Trace, không sinh Evidence, bất kể trẻ chọn gì');
  });

  testWidgets('không %, không điểm trên mọi trạng thái Reader', (tester) async {
    await _pump(tester, _reading);
    void scan() {
      for (final w in tester.widgetList<Text>(find.byType(Text))) {
        final t = w.data ?? '';
        expect(t.contains('%'), isFalse, reason: 'cấm %: "$t"');
        expect(t.contains('điểm'), isFalse, reason: 'cấm điểm: "$t"');
      }
    }

    scan();
    await tester.tap(find.text('Con đọc xong rồi 📖'));
    await tester.pumpAndSettle();
    scan();
    await tester.tap(find.text('Chàng'));
    await tester.pumpAndSettle();
    scan();
  });
}
