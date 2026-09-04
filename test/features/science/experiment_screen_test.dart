/// WAL-144 #KHTN — ExperimentScreen: PREDICT-gate + nhãn sách/trẻ tách bạch +
/// không chấm. Mỗi bất biến kèm đột biến làm đỏ (reason). Dữ liệu THẬT:
/// «Tách muối ra khỏi dung dịch muối» SGK Khoa học 5 tr.16-17.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/context/learning_context.dart';
import 'package:learning_coach/core/intent/learning_intent.dart';
import 'package:learning_coach/core/pedagogy/pedagogy_model.dart'
    show TeachingAct;
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/features/science/experiment_screen.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';

const _muoi = KhoaExperiment(
  book: '05-sgk-khoa-hoc-5',
  page: 16,
  title: 'Tách muối ra khỏi dung dịch muối',
  chuanBi: 'Muối ăn, 1 bát sứ chịu nhiệt, 1 cốc thuỷ tinh có chứa nước '
      'tinh khiết, 1 thìa, 1 kiềng sắt, 1 lưới tản nhiệt, 1 cốc nến, 1 bật lửa.',
  tienHanh: [
    'Cho 1 thìa muối ăn vào cốc thuỷ tinh chứa 80 ml nước, khuấy đều (hình 5a).',
    'Lấy 5 đến 6 thìa dung dịch muối cho vào bát sứ và đặt bát lên trên kiềng sắt.',
  ],
  duDoan: 'Dự đoán hiện tượng xảy ra với dung dịch muối khi đun.',
  quanSat: 'Sau vài phút, quan sát hiện tượng xảy ra với dung dịch muối.',
);

const _nen = KhoaExperiment(
  book: '05-sgk-khoa-hoc-5',
  page: 19,
  title: 'Thí nghiệm tìm hiểu sự biến đổi trạng thái của nến',
  chuanBi: 'nến vụn, 1 bát sứ chịu nhiệt, 1 đũa thuỷ tinh.',
  tienHanh: ['Cho một ít nến vụn vào bát sứ và đặt bát lên kiềng sắt.'],
  quanSat: 'Quan sát và nhận xét sự biến đổi trạng thái của nến vụn.',
);

const _ctx = LearningContext(
    learnerId: 'na',
    grade: 5,
    subject: 'Khoa học',
    sourceDocumentId: '05-sgk-khoa-hoc-5',
    lessonNo: 3,
    intent: LearningIntent.prepare);

Future<void> _pump(WidgetTester t, KhoaExperiment e,
    {void Function(List<LearningEvent>)? onFinished,
    LearningContext context = _ctx}) async {
  await t.pumpWidget(MaterialApp(
      home: ExperimentScreen(
    key: ValueKey(e.page),
    experiment: e,
    learningContext: context,
    now: () => DateTime(2026, 9, 2, 21),
    onFinished: onFinished,
  )));
}

void main() {
  testWidgets('⭐ PREDICT GATE: sách in «Dự đoán» ⇒ bước Tiến hành KHOÁ '
      'tới khi trẻ ghi dự đoán', (t) async {
    await _pump(t, _muoi);
    expect(find.text('CHUẨN BỊ'), findsOneWidget);
    expect(find.text('DỰ ĐOÁN CỦA EM'), findsOneWidget);
    expect(find.text('TIẾN HÀNH'), findsNothing,
        reason: '⭐ đột biến mở bước trước dự đoán ⇒ test này đỏ — khoa học '
            'bắt đầu bằng giả thuyết, không bằng xem trước kết quả');
    await t.tap(find.text('Chốt dự đoán — xem các bước 🔬'));
    await t.pump();
    expect(find.text('TIẾN HÀNH'), findsNothing,
        reason: 'dự đoán rỗng không phải dự đoán');
    await t.enterText(find.byType(TextField).first, 'Nước cạn, còn lại muối');
    await t.tap(find.text('Chốt dự đoán — xem các bước 🔬'));
    await t.pumpAndSettle();
    expect(find.text('TIẾN HÀNH'), findsOneWidget);
    expect(find.textContaining('khuấy đều'), findsOneWidget,
        reason: 'bước VERBATIM từ sách');
    expect(find.text('Nước cạn, còn lại muối'), findsOneWidget,
        reason: 'dự đoán CỦA EM hiện lại dưới đúng nhãn của em');
  });

  testWidgets('bài KHÔNG in «Dự đoán» (nến) ⇒ vào thẳng bước — không bịa gate',
      (t) async {
    await _pump(t, _nen);
    expect(find.text('TIẾN HÀNH'), findsOneWidget);
    expect(find.text('DỰ ĐOÁN CỦA EM'), findsNothing,
        reason: 'sách không yêu cầu dự đoán thì không bịa yêu cầu');
  });

  testWidgets('⭐ hoàn tất ⇒ MỘT event correct=null (không chấm quan sát), '
      'policy experiment-v1 + knowledgeVersion', (t) async {
    List<LearningEvent> out = const [];
    await _pump(t, _nen, onFinished: (e) => out = e);
    await t.enterText(find.byType(TextField).first, 'Nến chảy ra rồi đông lại');
    await t.scrollUntilVisible(find.text('Em làm xong thí nghiệm ✅'), 150,
        scrollable: find.byType(Scrollable).first);
    await t.tap(find.text('Em làm xong thí nghiệm ✅'));
    await t.pumpAndSettle();
    expect(out.single.kind, EvidenceKind.independentAttempt);
    expect(out.single.correct, isNull,
        reason: '⭐ đột biến chấm quan sát thành đúng/sai ⇒ test đỏ');
    expect(out.single.policyId, 'experiment-v1');
    expect(out.single.knowledgeVersion, isNotNull);
    // ⭐⭐ WAL-178/182 — lineage đến từ LearningContext (không tự bịa trong
    // widget), và act ghi lại đúng nước đi sư phạm đã xảy ra.
    expect(out.single.sourceDocumentId, _ctx.sourceDocumentId);
    expect(out.single.lessonNo, _ctx.lessonNo);
    expect(out.single.act, TeachingAct.askExplanation);
    expect(out.single.learnerText, 'Nến chảy ra rồi đông lại',
        reason: '⭐⭐ đột biến bỏ chữ trẻ viết ⇒ đỏ — trước đây bị vứt khi pop');
    expect(find.text('EM QUAN SÁT ĐƯỢC'), findsOneWidget);
    expect(find.textContaining('không chấm'), findsOneWidget,
        reason: 'nói thật với trẻ về việc không chấm');
    // ⭐⭐ WAL-176 — bài KHÔNG có bước dự đoán (nến) thì câu chốt KHÔNG được
    // nhắc «dự đoán»: trẻ chưa từng được hỏi dự đoán ở bài này.
    expect(find.textContaining('So sánh dự đoán'), findsNothing,
        reason: '⭐⭐ đột biến câu chốt luôn nhắc dự đoán ⇒ đỏ — nói một việc '
            'trẻ chưa từng làm là câu không thật');
  });

  testWidgets('⭐ bài CÓ dự đoán ⇒ câu chốt mời SO SÁNH dự đoán với quan sát',
      (t) async {
    await _pump(t, _muoi);
    await t.enterText(find.byType(TextField).first, 'Nước cạn, còn lại muối');
    await t.tap(find.text('Chốt dự đoán — xem các bước 🔬'));
    await t.pumpAndSettle();
    expect(find.text('TIẾN HÀNH'), findsOneWidget);
    // Ô quan sát nằm dưới cuối ListView — cùng lý do các test khác phải
    // scroll trước khi chạm nút hoàn tất.
    await t.scrollUntilVisible(find.text('EM QUAN SÁT ĐƯỢC'), 150,
        scrollable: find.byType(Scrollable).first);
    await t.enterText(find.byType(TextField), 'Đúng như con đoán');
    await t.scrollUntilVisible(find.text('Em làm xong thí nghiệm ✅'), 150,
        scrollable: find.byType(Scrollable).first);
    await t.tap(find.text('Em làm xong thí nghiệm ✅'));
    await t.pumpAndSettle();
    expect(find.textContaining('So sánh dự đoán'), findsOneWidget,
        reason: 'bài CÓ dự đoán ⇒ câu chốt phải nhắc lại đúng việc trẻ vừa làm');
  });

  testWidgets('không % trên mọi trạng thái', (t) async {
    await _pump(t, _muoi);
    void scan() {
      for (final w in t.widgetList<Text>(find.byType(Text))) {
        expect((w.data ?? '').contains('%'), isFalse,
            reason: 'cấm %: "${w.data}"');
      }
    }

    scan();
    await t.enterText(find.byType(TextField).first, 'muối kết tinh');
    await t.tap(find.text('Chốt dự đoán — xem các bước 🔬'));
    await t.pumpAndSettle();
    scan();
  });

  // ⭐⭐ WAL-178 — Evidence Validator: màn không tự mint evidence nữa, cửa
  // duy nhất là validateCandidateEvidence. Hai luật fail-closed kiểm ở đây.

  testWidgets('⭐⭐ ý định lookup ⇒ Trace, KHÔNG sinh Evidence dù trẻ có viết',
      (t) async {
    List<LearningEvent>? out;
    await _pump(t, _nen,
        context: const LearningContext(
            learnerId: 'na',
            grade: 5,
            subject: 'Khoa học',
            sourceDocumentId: '05-sgk-khoa-hoc-5',
            lessonNo: 3,
            intent: LearningIntent.lookup),
        onFinished: (e) => out = e);
    await t.enterText(
        find.byType(TextField).first, 'Nến chảy ra rồi đông lại');
    await t.scrollUntilVisible(find.text('Em làm xong thí nghiệm ✅'), 150,
        scrollable: find.byType(Scrollable).first);
    await t.tap(find.text('Em làm xong thí nghiệm ✅'));
    await t.pumpAndSettle();
    expect(out, isEmpty,
        reason: '⭐⭐ đột biến sinh evidence từ tra cứu ⇒ đỏ — WAL-175: '
            'lookup sinh Trace, không sinh Evidence, bất kể trẻ viết gì');
  });

  testWidgets('⭐ chữ trẻ viết rỗng ⇒ Trace, không phải "sai"', (t) async {
    List<LearningEvent>? out;
    await _pump(t, _nen, onFinished: (e) => out = e);
    await t.scrollUntilVisible(find.text('Em làm xong thí nghiệm ✅'), 150,
        scrollable: find.byType(Scrollable).first);
    await t.tap(find.text('Em làm xong thí nghiệm ✅'));
    await t.pumpAndSettle();
    expect(out, isEmpty,
        reason: 'im lặng không phải bằng chứng SAI — không có gì để chấm '
            'thì không có gì để ghi, không phải ghi một sự kiện "sai"');
  });
}
