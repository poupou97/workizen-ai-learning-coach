/// ⭐⭐ WAL-210 (audit C1, phần surface) — mở lại CÙNG một hoạt động hai lần
/// với CÙNG đồng hồ tiêm vào ⇒ hai bộ `eventId` KHÔNG giao nhau, và
/// `exerciseId` trên sự kiện vẫn là định danh BÀI (không đổi).
///
/// Bảy điểm phát bằng chứng: Reader (câu mở), Compose (nháp), SourceReader
/// (lập trường), MapReader (chỉ bản đồ), Experiment (quan sát), Assessment
/// (nộp câu), QuizSelect (chọn). Mỗi cái là một phiên riêng — trước WAL-210
/// tất cả đếm `#0` lại từ đầu.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/context/learning_context.dart';
import 'package:learning_coach/core/intent/learning_intent.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/tutor/learning_activity.dart';
import 'package:learning_coach/features/assessment/assessment_screen.dart';
import 'package:learning_coach/features/geography/map_reader_screen.dart';
import 'package:learning_coach/features/history/source_reader.dart';
import 'package:learning_coach/features/science/experiment_screen.dart';
import 'package:learning_coach/features/shell/compose_lite_screen.dart';
import 'package:learning_coach/features/shell/quiz_select_screen.dart';
import 'package:learning_coach/features/shell/reader_screen.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';

import '../support/pack_bundle.dart';

final _clock = DateTime(2026, 9, 5, 10);
const _ctx = LearningContext(
    learnerId: 'na',
    grade: 6,
    subject: 'KHTN',
    sourceDocumentId: '06-sgk-khoa-hoc-tu-nhien-6',
    lessonNo: 17,
    intent: LearningIntent.prepare);

const _reading = LearningActivity(
  activityId: '06-sgk-khoa-hoc-tu-nhien-6:l17:doc-hieu',
  prompt: '2. Tại sao phải mở khoá phễu chiết một cách từ từ?',
  response: ResponseKind.readRespond,
  conceptId: 'khtn-doc-hieu',
  passage: 'Tách dầu ăn khỏi nước. Chuẩn bị: 1 chai nhựa khoảng 500 mL, '
      'dầu ăn, phễu chiết, cốc thuỷ tinh.',
);

const _compose = LearningActivity(
  activityId: '05-sgk-tieng-viet-5-tap-mot:l4:viet',
  prompt: 'Viết đoạn văn tả cơn mưa.',
  response: ResponseKind.compose,
  conceptId: 'tieng-viet-viet',
);

const _quiz = LearningActivity(
  activityId: 'tv5-chon-b1',
  prompt: 'Chọn từ chỉ sự vật.',
  response: ResponseKind.selectIdentify,
  conceptId: 'tu-loai',
  options: ['cái bàn', 'chạy'],
  correctOption: 0,
);

const _source = SuSource(
  book: '05-sgk-lich-su-va-dia-li-5',
  page: 41,
  lesson: 9,
  excerpt: 'Trong Chiếu dời đô có đoạn: "...làm như thế cốt để mưu nghiệp lớn"',
  attribution: '(Theo Đại Việt sử ký toàn thư, Tập I)',
);

const _map = DiaMap(
  subject: 'LS&ĐL',
  book: '05-sgk-lich-su-va-dia-li-5',
  page: 10,
  asset: 'map-ls-dia-5-p012-tu-nhien-vn.png',
  caption: 'Hình 1. Bản đồ tự nhiên Việt Nam',
  pagePdf: 12,
  bboxFrac: [0.075, 0.05, 0.935, 0.905],
  extractionVersion: 'map-crop-v1',
  questions: ['Kể tên và xác định trên bản đồ một số khoáng sản ở nước ta.'],
);

const _experiment = KhoaExperiment(
  book: '06-sgk-khoa-hoc-tu-nhien-6',
  page: 62,
  lesson: 17,
  subject: 'KHTN',
  title: 'Tách dầu ăn khỏi nước',
  chuanBi: '1 chai nhựa khoảng 500 mL, dầu ăn, phễu chiết, cốc thuỷ tinh.',
  tienHanh: ['Rót hỗn hợp dầu ăn và nước vào phễu chiết.'],
  quanSat: 'Quan sát lớp dầu và lớp nước trong phễu.',
);

const _items = [
  CorpusExercise(
      expr: '1/2 - 1/5',
      book: '05-sgk-toan-5-tap-mot',
      skillCaseId: 'denominator-non-divisible',
      page: 21),
];

/// Chạy [run] hai lần trên widget mới toanh, trả về hai bộ id.
Future<(Set<String>, Set<String>, List<LearningEvent>)> _twice(
  WidgetTester t,
  Widget Function(void Function(List<LearningEvent>) sink, int run) build,
  Future<void> Function(WidgetTester t) run,
) async {
  final out = <List<LearningEvent>>[[], []];
  for (var i = 0; i < 2; i++) {
    await t.pumpWidget(build((e) => out[i] = e, i));
    await t.pump();
    await run(t);
    await t.pumpAndSettle();
    expect(out[i], isNotEmpty, reason: 'lần $i phải phát ít nhất một sự kiện');
  }
  return (
    out[0].map((e) => e.eventId).toSet(),
    out[1].map((e) => e.eventId).toSet(),
    out[0],
  );
}

void _expectDistinct(Set<String> a, Set<String> b, List<LearningEvent> first,
    String exerciseId) {
  expect(a.intersection(b), isEmpty,
      reason: '⭐⭐ mở lại cùng bài mà trùng id ⇒ mọi dedupe về sau nuốt lần hai');
  expect(first.every((e) => e.exerciseId == exerciseId), isTrue,
      reason: 'exerciseId vẫn là định danh BÀI, không đổi theo phiên');
  expect(first.every((e) => e.eventId.startsWith('$exerciseId@')), isTrue,
      reason: 'id = bài@phiên#seq — audit đọc được bằng mắt');
}

void main() {
  testWidgets('Reader (câu mở): mở lại ⇒ id khác', (t) async {
    final (a, b, first) = await _twice(
      t,
      (sink, i) => MaterialApp(
          home: ReaderScreen(
              key: ValueKey(i),
              activity: _reading,
              learningContext: _ctx,
              now: () => _clock,
              onFinished: sink)),
      (t) async {
        await t.tap(find.text('Con đọc xong rồi 📖'));
        await t.pumpAndSettle();
        await t.tap(find.text('Con đã trả lời xong 🗣'));
      },
    );
    _expectDistinct(a, b, first, _reading.activityId);
  });

  testWidgets('Compose (nháp): mở lại ⇒ id khác', (t) async {
    final (a, b, first) = await _twice(
      t,
      (sink, i) => MaterialApp(
          home: ComposeLiteScreen(
              key: ValueKey(i),
              activity: _compose,
              learningContext: _ctx,
              now: () => _clock,
              onFinished: sink)),
      (t) async {
        await t.tap(find.text('Xong dàn ý — viết nháp ✍️'));
        await t.pumpAndSettle();
        await t.enterText(find.byType(TextField), 'Trời đổ mưa rào.');
        await t.pumpAndSettle();
        await t.tap(find.text('Nộp nháp'));
        await t.pumpAndSettle();
        await t.tap(find.text('Mình xong rồi'));
      },
    );
    _expectDistinct(a, b, first, _compose.activityId);
  });

  testWidgets('SourceReader (lập trường): mở lại ⇒ id khác', (t) async {
    final (a, b, first) = await _twice(
      t,
      (sink, i) => MaterialApp(
          home: SourceReaderScreen(
              key: ValueKey(i),
              source: _source,
              learningContext: _ctx,
              now: () => _clock,
              onFinished: sink)),
      (t) async {
        await t.tap(find.text('Con đọc nguồn xong 📜'));
        await t.pumpAndSettle();
        await t.scrollUntilVisible(find.text(kConclusionStances[0]), 120,
            scrollable: find.byType(Scrollable).first);
        await t.tap(find.text(kConclusionStances[0]));
      },
    );
    _expectDistinct(a, b, first, '${_source.book}:p${_source.page}');
  });

  testWidgets('MapReader (chỉ bản đồ): mở lại ⇒ id khác', (t) async {
    final (a, b, first) = await _twice(
      t,
      (sink, i) => packHost(MapReaderScreen(
          key: ValueKey(i), map: _map, now: () => _clock, onFinished: sink)),
      (t) async {
        await t.scrollUntilVisible(find.text('Con đã chỉ được trên bản đồ ✅'),
            150,
            scrollable: find.byType(Scrollable).first);
        await t.tap(find.text('Con đã chỉ được trên bản đồ ✅'));
      },
    );
    _expectDistinct(a, b, first, '${_map.book}:p${_map.page}:map');
  });

  testWidgets('Experiment (quan sát): mở lại ⇒ id khác', (t) async {
    final (a, b, first) = await _twice(
      t,
      (sink, i) => MaterialApp(
          home: ExperimentScreen(
              key: ValueKey(i),
              experiment: _experiment,
              learningContext: _ctx,
              now: () => _clock,
              onFinished: sink)),
      (t) async {
        await t.enterText(find.byType(TextField).first, 'Dầu nổi lên trên nước');
        await t.scrollUntilVisible(find.text('Em làm xong thí nghiệm ✅'), 150,
            scrollable: find.byType(Scrollable).first);
        await t.tap(find.text('Em làm xong thí nghiệm ✅'));
      },
    );
    _expectDistinct(
        a, b, first, '${_experiment.book}:p${_experiment.page}');
  });

  testWidgets('Assessment (nộp câu): mở lại ⇒ id khác', (t) async {
    final (a, b, first) = await _twice(
      t,
      (sink, i) => MaterialApp(
          home: AssessmentScreen(
              key: ValueKey(i),
              items: _items,
              now: () => _clock,
              onFinished: (e, _) => sink(e))),
      (t) async {
        await t.enterText(find.byType(TextField), '3/10');
        await t.tap(find.byType(FilledButton));
      },
    );
    _expectDistinct(a, b, first, '${_items.single.book}:${_items.single.expr}');
  });

  testWidgets('QuizSelect (chọn): mở lại ⇒ id khác', (t) async {
    final (a, b, first) = await _twice(
      t,
      (sink, i) => MaterialApp(
          home: QuizSelectScreen(
              key: ValueKey(i),
              activity: _quiz,
              now: () => _clock,
              onFinished: sink)),
      (t) async {
        await t.tap(find.text('cái bàn'));
      },
    );
    _expectDistinct(a, b, first, _quiz.activityId);
  });
}
