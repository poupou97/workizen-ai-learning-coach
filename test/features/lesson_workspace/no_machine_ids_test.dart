/// ROUND 4 (Lane B §6.9) — KHÔNG MÃ MÁY TRÊN MÀN TRẺ ĐỌC: quét mọi chữ NHÌN
/// THẤY (Text) trên hành trình Home → Giá sách → Sách → Chương → Workspace
/// (Vào bài học, Đọc, Trực quan ×2, Học với SAM) và các sheet (Nguồn & độ tin,
/// Sách viết cho đoạn / hình / chỗ để trống) với nếp gấp kỹ thuật ĐÓNG; ghim
/// rằng mở nếp gấp mới thấy mã (mã không bị xoá, chỉ đổi chỗ).
///
/// Chạy trên fixture MẪU (CI) và fixture THẬT (máy có `assets/fixtures/real`,
/// nơi id block mang `tc2-p1`, dòng nguồn mang `tc2-p1 / sdm-v2`).
library;

import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/lesson_model/semantic_data.dart';
import 'package:learning_coach/core/lesson_model/next_action.dart';
import 'package:learning_coach/core/lesson_model/workspace_catalog.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/features/lesson_workspace/book_screen.dart';
import 'package:learning_coach/features/lesson_workspace/chapter_screen.dart';
import 'package:learning_coach/features/lesson_workspace/lesson_workspace_screen.dart';
import 'package:learning_coach/features/lesson_workspace/views/timeline_view.dart';
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
        lessonThreads: [HomeLessonThread(doc: d)],
        onOpenWorkspaceLesson: (_, {at}) {},
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
  // ROUND 7 V1: mọi sơ đồ của bài nằm trên CÙNG một màn cuộn — không còn
  // chip hình dạng / chip sơ đồ để bấm qua. Quét thẳng màn, rồi quét cả hai
  // cách nhìn của bảng so sánh, rồi mở nếp gấp «Bảng tóm tắt».
  for (final s in d.semantic) {
    expect(
      find.byKey(VisualView.cardKey(s.id)),
      findsOneWidget,
      reason: '$tag Trực quan thiếu thẻ «${s.title}»',
    );
  }
  for (final v in ['table', 'mindmap']) {
    final btn = find.byKey(VisualView.comparisonViewKey(v));
    if (btn.evaluate().isEmpty) continue;
    await t.ensureVisible(btn);
    await t.tap(btn);
    await t.pumpAndSettle();
    _expectClean(t, '$tag Trực quan bảng so sánh ($v)');
  }
  final fold = find.byKey(const Key('visual-summary-toggle'));
  if (fold.evaluate().isNotEmpty) {
    await t.ensureVisible(fold);
    await t.tap(fold);
    await t.pumpAndSettle();
  }
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

/// Tài liệu lát cắt nghiên cứu: bản THẬT nếu máy có (gitignored), không thì
/// bản MẪU đã commit — luật «không mã máy» phải đúng ở cả hai.
///
/// Trả về CẢ JSON gốc, không chỉ mô hình đã parse: bản ghi sửa (`repair`) là
/// thứ tính chất trung thực treo lên, và nhánh này chưa mang nó vào mô hình
/// app. Thứ phải đúng là **hiện vật đã phát**, nên đọc thẳng hiện vật.
({LessonDocument doc, Map<String, Object?> raw, bool real}) _historyDoc() {
  const real = 'assets/fixtures/real/lesson-05-sgk-lich-su-va-dia-li-5-b8.json';
  const syn =
      'assets/fixtures/synthetic/lesson-05-sgk-lich-su-va-dia-li-5-b8.synthetic.json';
  final useReal = File(real).existsSync();
  final j = (jsonDecode(File(useReal ? real : syn).readAsStringSync()) as Map)
      .cast<String, Object?>();
  return (
    doc: LessonDocument.fromJson(
      j,
      assetBase: useReal ? FixtureSlot.realDir : FixtureSlot.syntheticDir,
    )!,
    raw: j,
    real: useReal,
  );
}

/// Những vùng ĐÃ SỬA, ĐÃ KIỂM mà **vẫn chưa được tin**: `VALIDATED_REPAIR` và
/// `servable != true`. Sự tồn tại của chúng là điều kiện của tính chất trung
/// thực mà test dưới đây canh — không phải «bài này có mốc hay không».
List<Map<String, Object?>> _untrustedRepairs(Map<String, Object?> raw) => [
  for (final b in (raw['blocks']! as List).cast<Map<Object?, Object?>>())
    if (b['repair'] case final Map<Object?, Object?> r)
      if (r['disposition'] == 'VALIDATED_REPAIR' && r['servable'] != true)
        b.cast<String, Object?>(),
];

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
      '(id tc2-p1, dòng nguồn pipeline, mã lý do giữ lại, mã luật)', (t) async {
    final d = loadRealDocOrSkip();
    if (d == null) return;
    await _journey(t, d, 'thật');
  });

  /// ⭐⭐ ROUND 4 (Lane C × Lane B) — LÁT CẮT NGHIÊN CỨU cũng là màn TRẺ đọc.
  /// Nó đi qua cùng luật: thẻ Home, khu riêng, Trực quan → Dòng thời gian,
  /// nguồn kể chuyện, thử xếp thứ tự — không chỗ nào lộ id block / mã pipeline.
  /// Chạy trên fixture THẬT khi máy có, không thì trên fixture MẪU.
  testWidgets('⭐⭐ lát cắt nghiên cứu (LS&ĐL 5): Home + Trực quan → Dòng thời '
      'gian → nguồn không lộ mã máy', (t) async {
    final h = _historyDoc();
    final d = h.doc;
    t.view.physicalSize = const Size(1080, 6000);
    t.view.devicePixelRatio = 2.75;
    addTearDown(t.view.reset);

    // Home: thẻ lát cắt + dòng khu nghiên cứu.
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
          learnerGrade: 6,
          lessonThreads: [
            HomeLessonThread(doc: loadSyntheticDoc()),
            HomeLessonThread(doc: d),
          ],
          onOpenWorkspaceLesson: (_, {at}) {},
        ),
      ),
    );
    await t.pumpAndSettle();
    // ROUND 7 · V2 — bài sách lớp khác nay là MỘT THẺ HỌC BÌNH THƯỜNG trong
    // hàng «HÔM NAY» (order 50 §6), không còn thẻ «lát cắt nghiên cứu» riêng.
    expect(
      find.byKey(MissionCenterScreen.smartCardKey(d.slotKey)),
      findsOneWidget,
    );
    _expectClean(t, 'nghiên cứu Home');

    // Workspace → Trực quan → Dòng thời gian.
    await t.pumpWidget(
      fixtureHost(LessonWorkspaceScreen(doc: d, trace: WorkspaceTrace())),
    );
    await t.pumpAndSettle();
    _expectClean(t, 'nghiên cứu Vào bài học');
    await t.tap(find.byKey(ModePicker.cardKey(WorkspaceView.visual)));
    await t.pumpAndSettle();
    _expectClean(t, 'nghiên cứu Trực quan');

    // ⭐⭐ ROUND 6 — TÍNH CHẤT ĐƯỢC CANH Ở ĐÂY LÀ **TÍNH TRUNG THỰC**, KHÔNG
    // PHẢI «bài này có mốc hay không».
    //
    // Vòng 4 chạy trên fixture MẪU: bảy mốc có năm là đồ dựng sẵn, nên lát cắt
    // mở thẳng vào Dòng thời gian. Golden #1 của vòng 6 chạy trên bản THẬT đã
    // sửa và đã kiểm: block `p039:000` — khối mang CẢ BẢY mốc — vẫn WITHHELD vì
    // `agree_tones`, mang `VALIDATED_REPAIR` với `servable: false`, và KHÔNG
    // mang chữ. Nên bài không còn mốc nào.
    //
    // ⚠ Cái giá của điều đó, nói thẳng: **TRẺ MẤT TRỤC THỜI GIAN.** Đó là giá
    // nhìn thấy được của sự trung thực trong vòng này, không phải một lỗi.
    //
    // Nên luật là: **hễ còn một vùng ĐÃ SỬA mà CHƯA ĐƯỢC TIN, thì tuyệt đối
    // không được có trục thời gian trên màn** — dù dữ liệu có mọc ra
    // `TimelineSemantic` từ đâu. Ghim theo `d.semantic` là chưa đủ: bơm một
    // `TimelineSemantic` vào fixture sẽ khiến app vẽ trục và test vẫn XANH.
    final untrusted = _untrustedRepairs(h.raw);

    if (untrusted.isEmpty) {
      // Fixture MẪU (bản sao sạch / CI): mốc là nội dung của chính nó.
      expect(
        find.byKey(TimelineView.rootKey),
        findsOneWidget,
        reason: 'bản mẫu có mốc dựng sẵn ⇒ lát cắt mở thẳng vào Dòng thời gian',
      );
      _expectClean(t, 'nghiên cứu Dòng thời gian');
      await t.ensureVisible(find.byKey(TimelineView.sourceKey(0)));
      await t.tap(find.byKey(TimelineView.sourceKey(0)));
      await t.pumpAndSettle();
      _expectClean(t, 'nghiên cứu Sách viết (mốc)');
      return;
    }

    // ── Bản THẬT đã sửa ─────────────────────────────────────────────────
    // (a) Ở TẦNG DỮ LIỆU: còn vùng chưa được tin ⇒ không được có mốc nào.
    //     Bắt ở đây, TRƯỚC cây widget, để việc bơm một `TimelineSemantic` vào
    //     hiện vật là ĐỎ ngay — «trục thời gian quay lại mà không có quyết
    //     định tin của Founder» chính là thứ phải đỏ.
    expect(
      h.doc.semantic.whereType<TimelineSemantic>(),
      isEmpty,
      reason:
          '⭐ ${untrusted.length} vùng còn mang VALIDATED_REPAIR chưa được tin, '
          'mà bài lại có TimelineSemantic. RESTORED ≠ TRUSTED: ngưỡng tin sản '
          'xuất là cổng của Founder, không phải của pipeline.',
    );

    // (b) Ở TẦNG MÀN HÌNH: không có trục thời gian.
    expect(
      find.byKey(TimelineView.rootKey),
      findsNothing,
      reason: 'không mốc nào ⇒ tuyệt đối không được vẽ trục thời gian',
    );

    // (c) Khối mang bảy mốc phải có mặt như CHỖ TRỐNG CÓ LÝ DO, bằng lời trẻ
    //     đọc được — không biến mất, không hiện thành chữ hỏng. Chỗ trống sống
    //     ở màn ĐỌC (trang sách), nên sang đó rồi kiểm.
    await t.tap(find.byKey(LessonWorkspaceScreen.tabKey(WorkspaceView.read)));
    await t.pumpAndSettle();
    _expectClean(t, 'nghiên cứu Đọc (bản thật)');
    final events = untrusted.firstWhere(
      (b) => (b['id']! as String).endsWith('p039:tc2-p1:000'),
      orElse: () => throw StateError(
        'không tìm thấy khối p039:000 trong danh sách vùng đã sửa chưa được tin',
      ),
    );
    expect(events['type'], 'withheld');
    expect(
      events.containsKey('text'),
      isFalse,
      reason: 'giá trị đề xuất không được rời khỏi corpus',
    );
    final printed =
        (events['sourceRef']! as Map)['pagePrinted']; // 37 — trang IN
    expect(
      find.textContaining('SAM chưa đọc được'),
      findsWidgets,
      reason: 'chỗ trống phải nói bằng lời trẻ đọc được',
    );
    expect(
      find.textContaining('trang $printed'),
      findsWidgets,
      reason: 'chỗ trống phải chỉ đúng TRANG IN để trẻ mở sách',
    );

    // (d) KHÔNG vùng nào bị giữ lại lặng lẽ trở thành chữ. Đây là phép đếm
    //     CẤU TRÚC, không phải đi tìm một chuỗi.
    //
    //     ⚠ ĐÃ THỬ VÀ BỎ: canh bằng từ khoá («Bạch Đằng», «Ngô Quyền», «938»)
    //     cho ĐỎ GIẢ — chính những chữ ấy nằm trong khối MỤC TIÊU BÀI đã được
    //     phục vụ hợp lệ («ví dụ: 179 TCN, 40, 248, 542, 938,…»). Một canary
    //     bắt cả chữ sách thật thì không canh được gì; tệ hơn, nó dạy người
    //     đọc sau rằng đỏ ở đây là chuyện thường.
    final withheldInArtefact = [
      for (final b in (h.raw['blocks']! as List).cast<Map<Object?, Object?>>())
        if (b['type'] == 'withheld') b,
    ].length;
    expect(
      d.blocks.whereType<WithheldBlock>().length,
      withheldInArtefact,
      reason:
          '⭐ hiện vật khai $withheldInArtefact vùng giữ lại; app dựng ra số '
          'khác ⇒ có vùng đã lặng lẽ thành chữ trên đường nạp',
    );
    for (final w in d.blocks.whereType<WithheldBlock>()) {
      expect(w.reasons, isNotEmpty, reason: 'mỗi chỗ trống phải nêu LÝ DO');
    }
    // Từ vựng của pipeline không phải chữ cho trẻ đọc.
    final onScreen = t
        .widgetList<Text>(find.byType(Text))
        .map((w) => w.data ?? w.textSpan?.toPlainText() ?? '')
        .join('\n');
    for (final jargon in ['VALIDATED_REPAIR', 'agree_tones', 'servable']) {
      expect(onScreen.contains(jargon), isFalse, reason: '«$jargon» trên màn');
    }

    // (e) Và lý do tồn tại của cả tệp này vẫn đúng: không mã máy nào lộ ra.
    await t.tap(find.textContaining('Vì sao SAM để trống?').first);
    await t.pumpAndSettle();
    _expectClean(t, 'nghiên cứu «Vì sao SAM để trống?» (bản thật)');
  });

  test('mã máy vẫn ở nếp gấp: trustTechLines / techLinesFor mang mã', () {
    final d = loadSyntheticDoc();
    expect(trustTechLines(d).any(machineId.hasMatch), isTrue);
    expect(techLinesFor(d, d.blocks.first).any(machineId.hasMatch), isTrue);
  });
}
