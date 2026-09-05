/// ROUND 4 (Lane B §6.9) — KHÔNG MÃ MÁY TRÊN MÀN TRẺ ĐỌC: quét mọi chữ NHÌN
/// THẤY (Text) trên hành trình Home → Giá sách → Sách → Chương → Workspace
/// (Vào bài học, Đọc, Trực quan ×2, Học với SAM) và các sheet (Nguồn & độ tin,
/// Sách viết cho đoạn / hình / chỗ để trống) với nếp gấp kỹ thuật ĐÓNG; ghim
/// rằng mở nếp gấp mới thấy mã (mã không bị xoá, chỉ đổi chỗ).
///
/// Chạy trên fixture MẪU (CI) và fixture THẬT (máy có `assets/fixtures/real`,
/// nơi id block mang `tc2-p1`, dòng nguồn mang `tc2-p1 / sdm-v2`).
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/lesson_model/next_action.dart';
import 'package:learning_coach/core/lesson_model/workspace_catalog.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/features/lesson_workspace/book_screen.dart';
import 'package:learning_coach/features/lesson_workspace/chapter_screen.dart';
import 'package:learning_coach/features/lesson_workspace/lesson_workspace_screen.dart';
import 'package:learning_coach/features/lesson_workspace/visual_view.dart';
import 'package:learning_coach/features/lesson_workspace/widgets/mode_picker.dart';
import 'package:learning_coach/features/lesson_workspace/widgets/source_sheet.dart';
import 'package:learning_coach/features/lesson_workspace/widgets/tech_details.dart';
import 'package:learning_coach/features/lesson_workspace/widgets/trust_sheet.dart';
import 'package:learning_coach/features/lesson_workspace/workspace_trace.dart';
import 'package:learning_coach/features/mission/mission_center_screen.dart';
import 'package:learning_coach/features/mission/mission_data.dart';
import 'package:learning_coach/features/subjects/book_shelf_screen.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';

import 'support.dart';

/// Dấu hiệu MÃ MÁY — id block/pipeline/luật/mã từ chối/tên file/enum.
final machineId = RegExp(
  r'(tc2-p1|sdm-v2|tsl-[a-z-]+-v\d|toc-ocr|page_feature|math_guard|unknown_role'
  r'|\b0\d-sgk-[a-z0-9-]+|:\d{3}\b|HINT_UNSOURCED|KEY_NOT_VALIDATED|OVER_CAP'
  r'|GUARD:|PLAN:|\.py\b|@v\d|runtimeGuided|prototypeScripted|sourceBlockId'
  r'|synthetic[:-]|make_lesson_fixture|internalResearchOnly|sampledNoGate'
  r'|notAudited|trustedStructuredLesson|fixtureFromTrustedCorpus)',
);

const _p = LearnerProfile(learnerId: 'na', displayName: 'Na', grade: 6);

LessonIndex _idx() => LessonIndex.fromJsonString('''
{"grade":6,"subjects":{"KHTN":[
  {"sourceDocumentId":"06-sgk-khoa-hoc-tu-nhien-6","volume":null,
   "lessons":[{"no":16,"title":"HỖN HỢP CÁC CHẤT","pageStart":56},
              {"no":17,"title":"TÁCH CHẤT KHỎI HỖN HỢP","pageStart":60}]}]},
 "toanExercises":{},
 "books":[
  {"sourceDocumentId":"06-sgk-khoa-hoc-tu-nhien-6","subject":"KHTN","grade":6,
   "title":"KHTN 6","cover":"covers/k.webp","lessonCount":2}]}
''')!;

Iterable<String> _visible(WidgetTester t) => t
    .widgetList<Text>(find.byType(Text))
    .map((w) => w.data ?? w.textSpan?.toPlainText() ?? '');

void _expectClean(WidgetTester t, String where) {
  for (final s in _visible(t)) {
    expect(s, isNot(matches(machineId)), reason: '$where lộ mã máy: «$s»');
  }
}

Future<void> _openAndCheckSheet(
  WidgetTester t,
  LessonDocument d,
  LessonBlock b,
  String where,
) async {
  // Đổi gốc cây trước: cùng kiểu host ⇒ Navigator cũ (và sheet đang mở) bị
  // dùng lại, nút «open» nằm dưới sheet.
  await t.pumpWidget(const SizedBox.shrink());
  await t.pumpWidget(
    fixtureHost(
      Scaffold(
        body: Builder(
          builder: (ctx) => TextButton(
            onPressed: () => showSourceSheet(ctx, doc: d, block: b),
            child: const Text('open'),
          ),
        ),
      ),
    ),
  );
  await t.tap(find.text('open'));
  await t.pumpAndSettle();
  _expectClean(t, where);
  // mở nếp gấp ⇒ mã có mặt (không bị xoá)
  await t.ensureVisible(find.byKey(TechDetails.foldKey));
  await t.tap(find.byKey(TechDetails.foldKey));
  await t.pumpAndSettle();
  expect(
    _visible(t).any((s) => s.startsWith('Mã phần: ')),
    isTrue,
    reason: '$where: nếp gấp phải mang mã phần',
  );
}

Future<void> _journey(WidgetTester t, LessonDocument d, String tag) async {
  // Home (màn cao để ListView dựng hết)
  t.view.physicalSize = const Size(1080, 6000);
  t.view.devicePixelRatio = 2.75;
  addTearDown(t.view.reset);
  final data = await buildMissionFromStore(
    profile: _p,
    store: JsonlLearnerStore(),
    now: DateTime(2026, 9, 5, 19),
    index: _idx(),
  );
  await t.pumpWidget(
    fixtureHost(
      MissionCenterScreen(
        data: data,
        onOpenSubjects: () {},
        workspaceLesson: d,
        onOpenWorkspaceLesson: (_) {},
      ),
    ),
  );
  await t.pumpAndSettle();
  _expectClean(t, '$tag Home');

  // Giá sách → Sách → Chương
  final catalog = WorkspaceCatalog.withDocs([d]);
  final idx = _idx();
  final trace = WorkspaceTrace();
  await t.pumpWidget(
    fixtureHost(
      BookShelfScreen(
        profile: _p,
        index: idx,
        catalog: catalog,
        trace: trace,
        onOpenBook: (_) {},
      ),
    ),
  );
  await t.pumpAndSettle();
  _expectClean(t, '$tag Giá sách');
  final book = idx.bookById('06-sgk-khoa-hoc-tu-nhien-6')!;
  final lessons = idx.subjects['KHTN']!.first.lessons;
  await t.pumpWidget(
    fixtureHost(
      BookScreen(
        book: book,
        lessons: lessons,
        docs: [d],
        trace: trace,
        onOpenLegacy: () {},
      ),
    ),
  );
  await t.pumpAndSettle();
  _expectClean(t, '$tag Sách');
  await t.pumpWidget(
    fixtureHost(
      ChapterScreen(
        book: book,
        chapter: d.chapter!,
        lessons: lessons,
        docs: [d],
        trace: trace,
        onOpenLegacy: () {},
      ),
    ),
  );
  await t.pumpAndSettle();
  _expectClean(t, '$tag Chương');

  // Workspace: Vào bài học → Đọc → Trực quan (mọi hình dạng / sơ đồ) → SAM
  await t.pumpWidget(
    fixtureHost(LessonWorkspaceScreen(doc: d, trace: WorkspaceTrace())),
  );
  await t.pumpAndSettle();
  _expectClean(t, '$tag Vào bài học');
  await t.tap(find.byKey(ModePicker.cardKey(WorkspaceView.read)));
  await t.pumpAndSettle();
  _expectClean(t, '$tag Đọc');
  await t.tap(find.byKey(LessonWorkspaceScreen.tabKey(WorkspaceView.visual)));
  await t.pumpAndSettle();
  _expectClean(t, '$tag Trực quan');
  for (final s in d.semantic) {
    final chip = find.byKey(VisualView.instanceKey(s.id));
    if (chip.evaluate().isNotEmpty) {
      await t.tap(chip);
      await t.pumpAndSettle();
      _expectClean(t, '$tag Trực quan «${s.title}»');
    }
  }
  for (final shape in VisualView.shapesOf(d)) {
    await t.tap(find.byKey(VisualView.shapeKey(shape)));
    await t.pumpAndSettle();
    _expectClean(t, '$tag Trực quan $shape');
  }
  await t.tap(find.byKey(VisualView.shapeKey('summary')));
  await t.pumpAndSettle();
  _expectClean(t, '$tag Bảng tóm tắt');
  await t.tap(find.byKey(LessonWorkspaceScreen.tabKey(WorkspaceView.tutor)));
  await t.pumpAndSettle();
  _expectClean(t, '$tag Học với SAM (giải thích)');
  await t.tap(find.text('Tiếp ▸'));
  await t.pumpAndSettle();
  _expectClean(t, '$tag Học với SAM (hỏi)');
  await t.tap(find.textContaining('Gợi ý cho tớ'));
  await t.pumpAndSettle();
  _expectClean(t, '$tag Học với SAM (gợi ý)');

  // Sheet «Nguồn & độ tin» — gấp: sạch; mở: có mã
  await t.tap(find.byKey(const Key('fixture-chip-tap')));
  await t.pumpAndSettle();
  _expectClean(t, '$tag Nguồn & độ tin');
  await t.ensureVisible(find.byKey(TechDetails.foldKey));
  await t.tap(find.byKey(TechDetails.foldKey));
  await t.pumpAndSettle();
  expect(
    _visible(t).any(machineId.hasMatch),
    isTrue,
    reason: '$tag: nếp gấp «Chi tiết kỹ thuật» phải mang mã',
  );

  // Sheet «Sách viết» cho một đoạn, một hình, một chỗ để trống
  final para = d.blocks.whereType<ParagraphBlock>().first;
  final img = d.blocks.whereType<ImageBlock>().first;
  final wh = d.blocks.whereType<WithheldBlock>().first;
  await _openAndCheckSheet(t, d, para, '$tag Sách viết (đoạn)');
  await _openAndCheckSheet(t, d, img, '$tag Sách viết (hình)');
  await _openAndCheckSheet(t, d, wh, '$tag Sách viết (để trống)');
}

void main() {
  test('regex bắt được mã máy thật, không bắt lời trẻ', () {
    for (final s in [
      '06-sgk-khoa-hoc-tu-nhien-6:p062:tc2-p1:009',
      'SGK KHTN 6 · trang 60–63 · tc2-p1 / sdm-v2',
      'Lý do: page_feature:diagram',
      'luật tsl-enumerated-steps-v1',
      'prototype — suy từ đoạn 06-sgk-khoa-hoc-tu-nhien-6:p063:tc2-p1:005',
      'tool/corpus/tsl_to_lesson_document.py@v1',
    ]) {
      expect(machineId.hasMatch(s), isTrue, reason: s);
    }
    for (final s in [
      'Phần này SAM chưa đọc được — con xem SGK trang 61 nhé.',
      'Bản thử nghiệm · nguồn SGK có cấu trúc, chưa kiểm định (nội bộ)',
      'SGK KHTN 6 · trang 60–63',
      'Máy đã kiểm 5/17 bước là lời lấy đúng trong sách',
      'Hình 17.1',
      '1. Quá trình làm muối từ nước biển sử dụng phương pháp tách chất nào?',
    ]) {
      expect(machineId.hasMatch(s), isFalse, reason: s);
    }
  });

  testWidgets('⭐ fixture MẪU: hành trình + sheet không lộ mã máy', (t) async {
    await _journey(t, loadSyntheticDoc(), 'mẫu');
  });

  testWidgets('⭐⭐ fixture THẬT (nếu có): hành trình + sheet không lộ mã máy '
      '(id tc2-p1, dòng nguồn pipeline, mã lý do giữ lại, mã luật)', (
    t,
  ) async {
    final d = loadRealDocOrSkip();
    if (d == null) return;
    await _journey(t, d, 'thật');
  });

  test('mã máy vẫn ở nếp gấp: trustTechLines / techLinesFor mang mã', () {
    final d = loadSyntheticDoc();
    expect(trustTechLines(d).any(machineId.hasMatch), isTrue);
    expect(
      techLinesFor(d, d.blocks.first).any(machineId.hasMatch),
      isTrue,
    );
  });
}
