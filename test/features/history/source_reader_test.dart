/// WAL-113 B2 — SourceReader: NGUỒN NÓI ≠ SAM DIỄN GIẢI ≠ EM KẾT LUẬN.
/// Ba tầng ba KIỂU + ba nhãn — mỗi bất biến kèm đột biến làm test đỏ (reason).
/// Dữ liệu THẬT: khối TƯ LIỆU Chiếu dời đô, SGK Sử-Địa 5 tr. 41 (bài 9).
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/context/learning_context.dart';
import 'package:learning_coach/core/intent/learning_intent.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/features/history/source_reader.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';

const _ctx = LearningContext(learnerId: 'na', grade: 5);

const _gloss = 'Nguồn này cho thấy vua Lý Thái Tổ chọn thành Đại La vì thế '
    'đất rộng, cao, ở giữa bốn phương — việc dời đô có tính toán.';

const _src = SuSource(
  book: '05-sgk-lich-su-va-dia-li-5',
  page: 41,
  lesson: 9,
  lessonTitle: 'TRIỀU LÝ VÀ VIỆC ĐỊNH ĐÔ Ở THĂNG LONG',
  excerpt: 'Trong Chiếu dời đô có đoạn: "...làm như thế cốt để mưu nghiệp '
      'lớn, chọn ở chỗ giữa, làm kế cho con cháu muôn vạn đời..."',
  attribution:
      '(Theo Ngô Sỹ Liên và các sử thần Triều Hậu Lê, Đại Việt sử ký toàn thư, Tập I)',
  samGloss: _gloss,
);

Future<void> _pump(WidgetTester t, SuSource s,
    {void Function(List<LearningEvent>)? onFinished,
    LearningContext context = _ctx}) async {
  await t.pumpWidget(MaterialApp(
      home: SourceReaderScreen(
    key: ValueKey('${s.book}:${s.page}'),
    source: s,
    learningContext: context,
    now: () => DateTime(2026, 9, 2, 19),
    onFinished: onFinished,
  )));
}

void main() {
  testWidgets('⭐ SOURCE gate: diễn giải + kết luận KHOÁ tới khi đọc nguồn xong',
      (t) async {
    await _pump(t, _src);
    expect(find.text('NGUỒN NÓI GÌ'), findsOneWidget);
    expect(find.textContaining('Chiếu dời đô'), findsWidgets);
    expect(find.textContaining('Đại Việt sử ký toàn thư'), findsOneWidget,
        reason: 'attribution của SGK hiện NGAY cạnh lời nguồn');
    expect(find.text('SAM DIỄN GIẢI'), findsNothing,
        reason: '⭐ đột biến mở diễn giải trước khi trẻ đọc nguồn ⇒ đỏ');
    expect(find.textContaining('tính toán'), findsNothing,
        reason: 'gloss không được rò rỉ trước gate');
    expect(find.textContaining('bằng chứng cho điều bài học nói'), findsNothing);
  });

  testWidgets('⭐ sau khi đọc: BA NHÃN TÁCH BẠCH — gloss chỉ dưới nhãn SAM, '
      'nguồn vẫn dưới nhãn NGUỒN', (t) async {
    await _pump(t, _src);
    await t.tap(find.text('Con đọc nguồn xong 📜'));
    await t.pumpAndSettle();
    expect(find.text('NGUỒN NÓI GÌ'), findsOneWidget);
    expect(find.text('SAM DIỄN GIẢI'), findsOneWidget);
    expect(find.text('EM KẾT LUẬN'), findsNothing,
        reason: 'chưa kết luận thì chưa có tầng của em');
    expect(find.text(_gloss), findsOneWidget);
    expect(find.textContaining('không có đáp án đúng-sai',
        findRichText: true), findsNothing); // câu copy chính xác kiểm dưới
    expect(find.textContaining('Không có đáp án'), findsOneWidget,
        reason: 'nói thật: source evaluation không chấm');
    // ListView build lười — nút lập trường dưới fold: cuộn tới rồi mới assert.
    for (final st in kConclusionStances) {
      await t.scrollUntilVisible(find.text(st), 120,
          scrollable: find.byType(Scrollable).first);
      expect(find.text(st), findsOneWidget);
    }
  });

  testWidgets('⭐ kết luận ⇒ MỘT attempt correct=null (UNKNOWN ≠ SAI), '
      'policy source-reader-v1; «đọc nguồn xong» KHÔNG phát bằng chứng',
      (t) async {
    List<LearningEvent> out = const [];
    await _pump(t, _src, onFinished: (e) => out = e);
    await t.tap(find.text('Con đọc nguồn xong 📜'));
    await t.pumpAndSettle();
    expect(out, isEmpty, reason: 'đọc ≠ mastery — không event khi mới đọc');
    await t.scrollUntilVisible(find.text(kConclusionStances[1]), 120,
        scrollable: find.byType(Scrollable).first);
    await t.tap(find.text(kConclusionStances[1]));
    await t.pumpAndSettle();
    expect(out.single.kind, EvidenceKind.independentAttempt);
    expect(out.single.correct, isNull,
        reason: '⭐ đột biến chấm kết luận sử thành đúng/sai ⇒ test đỏ');
    expect(out.single.policyId, 'source-reader-v1');
    expect(out.single.skillCaseId, 'su-doc-tu-lieu');
    expect(find.text('EM KẾT LUẬN'), findsOneWidget);
    expect(find.text(kConclusionStances[1]), findsOneWidget,
        reason: 'kết luận CỦA EM hiện lại dưới đúng nhãn của em');
    expect(find.textContaining('NHIỀU nguồn'), findsOneWidget,
        reason: 'dạy đúng phương pháp sử: một nguồn chưa đủ');
  });

  // ⭐⭐ WAL-189 — cùng luật WAL-175/178: tra cứu sinh TRACE, không sinh
  // EVIDENCE. Trước WAL-189, SourceReader không nhận learningContext nên kết
  // luận qua ý định "Xem trong sách" vẫn ghi evidence như một lần học thật.
  testWidgets('⭐⭐ ý định lookup ⇒ KHÔNG sinh evidence dù trẻ kết luận',
      (t) async {
    List<LearningEvent>? out;
    await _pump(t, _src,
        context: const LearningContext(
            learnerId: 'na', grade: 5, intent: LearningIntent.lookup),
        onFinished: (e) => out = e);
    await t.tap(find.text('Con đọc nguồn xong 📜'));
    await t.pumpAndSettle();
    await t.scrollUntilVisible(find.text(kConclusionStances[1]), 120,
        scrollable: find.byType(Scrollable).first);
    await t.tap(find.text(kConclusionStances[1]));
    await t.pumpAndSettle();
    expect(out, isEmpty,
        reason: '⭐⭐ đột biến bỏ gate lookup ⇒ đỏ — tra cứu không phải bằng '
            'chứng, dù trẻ có kết luận gì');
  });

  testWidgets('⭐ fail-closed: thiếu attribution ⇒ KHÔNG render như nguồn',
      (t) async {
    const bad = SuSource(
        book: '05-sgk-lich-su-va-dia-li-5',
        excerpt: 'một đoạn không rõ nguồn',
        attribution: '');
    await _pump(t, bad);
    expect(find.text('NGUỒN NÓI GÌ'), findsNothing,
        reason: '⭐ đột biến render nguồn không dẫn được ⇒ đỏ');
    expect(find.textContaining('chưa có đủ nguyên văn hoặc nguồn dẫn'),
        findsOneWidget);
  });

  testWidgets('gloss null ⇒ KHÔNG có nhãn SAM DIỄN GIẢI (không bịa diễn giải)',
      (t) async {
    const noGloss = SuSource(
        book: '05-sgk-lich-su-va-dia-li-5',
        page: 18,
        excerpt: 'Năm 1836, vua Minh Mạng cử Phạm Hữu Nhật chỉ huy đội binh '
            'thuyền ra quần đảo Hoàng Sa, mang theo 10 cái bài gỗ (cột mốc).',
        attribution: '(Theo Quốc sử quán Triều Nguyễn, Đại Nam thực lục, Tập bốn)');
    await _pump(t, noGloss);
    await t.tap(find.text('Con đọc nguồn xong 📜'));
    await t.pumpAndSettle();
    expect(find.text('SAM DIỄN GIẢI'), findsNothing);
    for (final st in kConclusionStances) {
      await t.scrollUntilVisible(find.text(st), 120,
          scrollable: find.byType(Scrollable).first);
      expect(find.text(st), findsOneWidget,
          reason: 'không có diễn giải vẫn kết luận được — nguồn là đủ');
    }
  });

  testWidgets('không %, không điểm trên mọi trạng thái', (t) async {
    await _pump(t, _src);
    void scan() {
      for (final w in t.widgetList<Text>(find.byType(Text))) {
        final txt = w.data ?? '';
        expect(txt.contains('%'), isFalse, reason: 'cấm %: "$txt"');
        expect(txt.contains('điểm'), isFalse, reason: 'cấm điểm: "$txt"');
      }
    }

    scan();
    await t.tap(find.text('Con đọc nguồn xong 📜'));
    await t.pumpAndSettle();
    scan();
    await t.scrollUntilVisible(find.text(kConclusionStances.first), 120,
        scrollable: find.byType(Scrollable).first);
    await t.tap(find.text(kConclusionStances.first));
    await t.pumpAndSettle();
    scan();
  });
}
