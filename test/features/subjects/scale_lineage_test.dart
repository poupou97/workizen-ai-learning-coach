/// ⭐⭐ WAL-210 (audit C7 + B.6 §2/§4) — LINEAGE + VERSION trên mọi surface
/// của đường Scale, đo trên bài mẫu chung của các track:
/// **KHTN 6 · Bài 17 «Tách chất khỏi hỗn hợp»** (`06-sgk-khoa-hoc-tu-nhien-6`).
///
/// Trước WAL-210 chỉ Experiment mang `sourceDocumentId/lessonNo`; Reader/
/// Compose/Source/Map/Tutor/Assessment không — Learning Map nói «Chưa học»
/// với bài trẻ vừa học xong, Parent không kể. Và hằng `slice-toan5-b6-v1+
/// qmap-v1` (Toán 5) bị đóng lên evidence của mọi môn.
///
/// Hai lớp: (a) fixture TRONG BỘ NHỚ (CI luôn chạy) mô phỏng pack lớp 6 đã
/// dựng lại theo hợp đồng `buildProvenance`; (b) FILE THẬT — skip khi máy
/// chưa có pack, hoặc khi Bài 17 chưa có hoạt động (pack hôm nay chỉ có một
/// bài đọc từ pattern router; sau PR-C nó bị guard chặn tới khi pack khai
/// `experimental`).
library;

import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/context/learning_context.dart';
import 'package:learning_coach/core/curriculum/pedagogical_boundary.dart';
import 'package:learning_coach/core/intent/learning_intent.dart';
import 'package:learning_coach/core/knowledge/slice_curriculum.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/learning_map_state.dart';
import 'package:learning_coach/core/tutor/learning_activity.dart';
import 'package:learning_coach/features/assessment/assessment_screen.dart';
import 'package:learning_coach/features/geography/map_reader_screen.dart';
import 'package:learning_coach/features/history/source_reader.dart';
import 'package:learning_coach/features/shell/compose_lite_screen.dart';
import 'package:learning_coach/features/shell/reader_screen.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';
import 'package:learning_coach/features/subjects/subject_home_screen.dart';
import 'package:learning_coach/features/tutor/tutor_session.dart';

import '../../support/curriculum.dart';
import '../../support/pack_bundle.dart';

const _book = '06-sgk-khoa-hoc-tu-nhien-6';
const _lesson = 17;
const _packVersion = 'g6-20260905T1200-abcdef12';
const _p6 = LearnerProfile(learnerId: 'l6', displayName: 'Na', grade: 6);

/// Pack lớp 6 «đã dựng lại»: provenance đầy đủ, Bài 17 có MỘT bài đọc mined
/// (không `source` router) — cùng đoạn «Tách dầu ăn khỏi nước» tr. 62.
LessonIndex _g6() => LessonIndex.fromJsonString('''
{"grade":6,"version":"lesson-index-v2",
 "buildProvenance":{"schema":1,"builderVersion":"build_lesson_index.py@2",
   "gitSha":"abcdef1234567890","builtAt":"2026-09-05T12:00:00Z","grade":6,
   "flags":{"PATTERN_ROUTER":"0","UNITS_SOURCE":"units-v3","ROUTE_EXPLAIN":"0"},
   "experimental":false,"attachmentRule":"capped-toc-v1","contentHash":"0",
   "packVersion":"$_packVersion"},
 "subjects":{"KHTN":[{"sourceDocumentId":"$_book","volume":null,
   "lessons":[{"no":16,"title":"Hỗn hợp các chất","pageStart":56},
              {"no":17,"title":"Tách chất khỏi hỗn hợp","pageStart":60}]}]},
 "tvReadings":[{"book":"$_book","lesson":17,"page":62,"subject":"KHTN",
   "passage":"Tách dầu ăn khỏi nước. Chuẩn bị: 1 chai nhựa khoảng 500 mL, dầu ăn, phễu chiết, cốc thuỷ tinh.",
   "questions":[{"prompt":"2. Tại sao phải mở khoá phễu chiết một cách từ từ?","page":62}]}]}
''')!;

LearningContext _ctx({LearningIntent? intent = LearningIntent.prepare,
        String? version = _packVersion}) =>
    LearningContext(
        learnerId: _p6.learnerId,
        grade: 6,
        subject: 'KHTN',
        sourceDocumentId: _book,
        lessonNo: _lesson,
        intent: intent,
        knowledgeModelVersion: version);

void _expectLineage(LearningEvent e, {String? version = _packVersion}) {
  expect(e.sourceDocumentId, _book,
      reason: '⭐⭐ audit C7: thiếu sách ⇒ Learning Map mù');
  expect(e.lessonNo, _lesson, reason: '⭐⭐ audit C7: thiếu bài ⇒ Learning Map mù');
  expect(e.knowledgeVersion, version,
      reason: 'version của ĐÚNG pack, không phải hằng Toán 5');
  expect(
      learningMapStateFor(
          sourceDocumentId: _book, lessonNo: _lesson, allEvents: [e]),
      isNot(LearningMapState.unseen),
      reason: '⭐⭐ bài vừa học xong không được là «Chưa học»');
}

void main() {
  group('(a) từng surface — fixture trong bộ nhớ', () {
    testWidgets('Reader: câu mở ⇒ participation mang sách + bài + packVersion',
        (t) async {
      List<LearningEvent> out = const [];
      final r = _g6().readingsForTv(_book, _lesson).single;
      await t.pumpWidget(MaterialApp(
          home: ReaderScreen(
              activity: LearningActivity(
                  activityId: '$_book:l$_lesson:doc-hieu',
                  prompt: r.questions.single.prompt,
                  response: ResponseKind.readRespond,
                  conceptId: 'khtn-doc-hieu',
                  passage: r.passage),
              learningContext: _ctx(),
              now: () => DateTime(2026, 9, 5, 10),
              onFinished: (e) => out = e)));
      await t.tap(find.text('Con đọc xong rồi 📖'));
      await t.pumpAndSettle();
      await t.tap(find.text('Con đã trả lời xong 🗣'));
      await t.pumpAndSettle();
      expect(out.single.kind, EvidenceKind.participation);
      _expectLineage(out.single);
    });

    testWidgets('Reader: pack CHƯA khai provenance ⇒ rơi về hằng cũ, không null',
        (t) async {
      List<LearningEvent> out = const [];
      await t.pumpWidget(MaterialApp(
          home: ReaderScreen(
              activity: const LearningActivity(
                  activityId: 'x',
                  prompt: 'Tại sao?',
                  response: ResponseKind.readRespond,
                  conceptId: 'c',
                  passage: 'Đoạn văn.'),
              learningContext: _ctx(version: null),
              onFinished: (e) => out = e)));
      await t.tap(find.text('Con đọc xong rồi 📖'));
      await t.pumpAndSettle();
      await t.tap(find.text('Con đã trả lời xong 🗣'));
      await t.pumpAndSettle();
      _expectLineage(out.single, version: knowledgeModelVersion);
    });

    testWidgets('Compose: nháp ⇒ participation mang sách + bài + packVersion',
        (t) async {
      List<LearningEvent> out = const [];
      await t.pumpWidget(MaterialApp(
          home: ComposeLiteScreen(
              activity: const LearningActivity(
                  activityId: '$_book:l$_lesson:viet',
                  prompt: 'Viết cách tách dầu ăn khỏi nước.',
                  response: ResponseKind.compose,
                  conceptId: 'khtn-viet'),
              learningContext: _ctx(),
              onFinished: (e) => out = e)));
      await t.tap(find.text('Xong dàn ý — viết nháp ✍️'));
      await t.pumpAndSettle();
      await t.enterText(find.byType(TextField), 'Dùng phễu chiết.');
      await t.pumpAndSettle();
      await t.tap(find.text('Nộp nháp'));
      await t.pumpAndSettle();
      await t.tap(find.text('Mình xong rồi'));
      await t.pumpAndSettle();
      expect(out.single.kind, EvidenceKind.participation);
      _expectLineage(out.single);
    });

    testWidgets('SourceReader: lập trường ⇒ participation mang lineage + version',
        (t) async {
      List<LearningEvent> out = const [];
      await t.pumpWidget(MaterialApp(
          home: SourceReaderScreen(
              source: const SuSource(
                  book: _book,
                  page: 61,
                  lesson: _lesson,
                  excerpt: 'Người ta dùng phương pháp lọc để tách chất rắn…',
                  attribution: '(SGK KHTN 6, tr. 61)'),
              learningContext: _ctx(),
              onFinished: (e) => out = e)));
      await t.tap(find.text('Con đọc nguồn xong 📜'));
      await t.pumpAndSettle();
      await t.scrollUntilVisible(find.text(kConclusionStances[0]), 120,
          scrollable: find.byType(Scrollable).first);
      await t.tap(find.text(kConclusionStances[0]));
      await t.pumpAndSettle();
      expect(out.single.kind, EvidenceKind.participation);
      _expectLineage(out.single);
    });

    testWidgets('MapReader: nhận context ⇒ lineage (bài từ DiaMap.lesson) + '
        'version; lookup ⇒ không sự kiện', (t) async {
      const map = DiaMap(
          subject: 'KHTN',
          book: _book,
          page: 60,
          lesson: _lesson,
          asset: 'map-khtn-6-p060.png',
          caption: 'Hình 17.1',
          pagePdf: 62,
          bboxFrac: [0, 0, 1, 1],
          extractionVersion: 'map-crop-v1',
          questions: ['Chỉ ra bộ phận lọc.']);
      List<LearningEvent> out = const [];
      await t.pumpWidget(packHost(MapReaderScreen(
          map: map,
          // context KHÔNG biết bài — DiaMap.lesson mới là nguồn số bài.
          learningContext: LearningContext(
              learnerId: 'l6',
              grade: 6,
              subject: 'KHTN',
              sourceDocumentId: _book,
              knowledgeModelVersion: _packVersion),
          onFinished: (e) => out = e)));
      await t.pump();
      await t.scrollUntilVisible(find.text('Con đã chỉ được trên bản đồ ✅'), 150,
          scrollable: find.byType(Scrollable).first);
      await t.tap(find.text('Con đã chỉ được trên bản đồ ✅'));
      await t.pumpAndSettle();
      expect(out.single.kind, EvidenceKind.participation);
      _expectLineage(out.single);

      List<LearningEvent>? lookup;
      await t.pumpWidget(packHost(MapReaderScreen(
          key: const ValueKey('lookup'),
          map: map,
          learningContext: _ctx(intent: LearningIntent.lookup),
          onFinished: (e) => lookup = e)));
      await t.pump();
      await t.scrollUntilVisible(find.text('Con đã chỉ được trên bản đồ ✅'), 150,
          scrollable: find.byType(Scrollable).first);
      await t.tap(find.text('Con đã chỉ được trên bản đồ ✅'));
      await t.pumpAndSettle();
      expect(lookup, isEmpty,
          reason: 'WAL-189 giờ áp cả Map — tra cứu không sinh evidence');
    });

    testWidgets('MapReader KHÔNG context, DiaMap không lesson (pack hôm nay) ⇒ '
        'sách có, bài null, KHÔNG hiện trên Learning Map — không đoán', (t) async {
      const map = DiaMap(
          subject: 'LS&ĐL',
          book: '05-sgk-lich-su-va-dia-li-5',
          page: 10,
          asset: 'map-ls-dia-5-p012-tu-nhien-vn.png',
          caption: 'Hình 1',
          pagePdf: 12,
          bboxFrac: [0, 0, 1, 1],
          extractionVersion: 'map-crop-v1',
          questions: ['Kể tên.']);
      List<LearningEvent> out = const [];
      await t.pumpWidget(packHost(MapReaderScreen(map: map, onFinished: (e) => out = e)));
      await t.pump();
      await t.scrollUntilVisible(find.text('Con đã chỉ được trên bản đồ ✅'), 150,
          scrollable: find.byType(Scrollable).first);
      await t.tap(find.text('Con đã chỉ được trên bản đồ ✅'));
      await t.pumpAndSettle();
      expect(out.single.sourceDocumentId, map.book);
      expect(out.single.lessonNo, isNull);
      expect(out.single.knowledgeVersion, knowledgeModelVersion);
    });

    test('Tutor: bài mở TỪ pack ⇒ sự kiện mang sách + bài; bài CHỤP ⇒ null',
        () {
      final c = toan5Bai6;
      final fp = FractionProblem.parse('3/4 + 2/5')!;
      final scope = TutorScope.forProblem(c.conceptId,
          c.classifyCase('3/4 + 2/5'), c.stage, c.catalogue);
      final fromPack = TutorSession(
          exerciseId: 'cur:05-sgk-toan-5-tap-mot:p20:b6',
          skillCaseId: 'denominator-non-divisible',
          problem: fp,
          scope: scope,
          sourceDocumentId: '05-sgk-toan-5-tap-mot',
          lessonNo: 6)
        ..submit('23/20');
      for (final e in fromPack.log.events) {
        expect(e.sourceDocumentId, '05-sgk-toan-5-tap-mot');
        expect(e.lessonNo, 6);
        expect(e.knowledgeVersion, knowledgeModelVersion,
            reason: 'đường Deep giữ hằng của nó');
      }
      final fromCamera = TutorSession(
          exerciseId: 'cp:abc',
          skillCaseId: 'denominator-non-divisible',
          problem: fp,
          scope: scope)
        ..submit('23/20');
      for (final e in fromCamera.log.events) {
        expect(e.sourceDocumentId, isNull,
            reason: 'bài chụp: không biết bài nào — Founder quyết stamp gì');
        expect(e.lessonNo, isNull);
      }
    });

    testWidgets('Assessment: context về ĐÚNG cuốn ⇒ lineage; cuốn khác ⇒ bài null',
        (t) async {
      const items = [
        CorpusExercise(
            expr: '1/2 - 1/5',
            book: '05-sgk-toan-5-tap-mot',
            skillCaseId: 'denominator-non-divisible',
            page: 21),
      ];
      Future<LearningEvent> run(LearningContext? ctx, Key key) async {
        List<LearningEvent> ev = const [];
        await t.pumpWidget(MaterialApp(
            home: AssessmentScreen(
                key: key,
                items: items,
                learningContext: ctx,
                onFinished: (e, _) => ev = e)));
        await t.enterText(find.byType(TextField), '3/10');
        await t.tap(find.byType(FilledButton));
        await t.pumpAndSettle();
        return ev.single;
      }

      final same = await run(
          const LearningContext(
              learnerId: 'l',
              grade: 5,
              sourceDocumentId: '05-sgk-toan-5-tap-mot',
              lessonNo: 6),
          const ValueKey(1));
      expect(same.sourceDocumentId, '05-sgk-toan-5-tap-mot');
      expect(same.lessonNo, 6);
      final other = await run(
          const LearningContext(
              learnerId: 'l', grade: 5, sourceDocumentId: _book, lessonNo: 17),
          const ValueKey(2));
      expect(other.sourceDocumentId, '05-sgk-toan-5-tap-mot',
          reason: 'sách là sự thật của chính bài tập');
      expect(other.lessonNo, isNull, reason: 'không ghép bài của sách khác');
      final none = await run(null, const ValueKey(3));
      expect(none.lessonNo, isNull);
    });
  });

  group('(b) Book Home → Reader → kho → Learning Map (fixture KHTN 6 Bài 17)', () {
    testWidgets('⭐⭐ học xong Bài 17 ⇒ sự kiện trong kho mang lineage + packVersion; '
        'mở lại Book Home ⇒ badge «Đã học», không còn «Chưa học»', (t) async {
      final store = JsonlLearnerStore();
      final idx = _g6();
      final book = BookRef(
          sourceDocumentId: _book,
          subject: 'KHTN',
          title: 'KHTN 6',
          cover: 'covers/x.webp',
          lessonCount: 55);
      // Key theo lượt: lượt hai phải là CÂY MỚI (lượt một còn route Reader
      // nằm trên Navigator ⇒ Book Home cũ offstage, finder không thấy).
      Widget home(int run) => MaterialApp(
          key: ValueKey('run-$run'),
          home: SubjectHomeScreen(
              profile: _p6,
              store: store,
              index: idx,
              subject: 'KHTN',
              book: book));

      await t.pumpWidget(home(1));
      await t.pumpAndSettle();
      final tile = find.widgetWithText(ListTile, 'Bài 17 · Tách chất khỏi hỗn hợp');
      expect(tile, findsOneWidget);
      expect(
          find.descendant(of: tile, matching: find.textContaining('Đã học')),
          findsNothing,
          reason: 'chưa học ⇒ chưa có badge');

      // Một hoạt động, một ý định khả dĩ ⇒ vào thẳng Reader (không sheet).
      await t.tap(tile);
      await t.pumpAndSettle();
      await t.tap(find.text('Con đọc xong rồi 📖'));
      await t.pumpAndSettle();
      await t.tap(find.text('Con đã trả lời xong 🗣'));
      await t.pumpAndSettle();

      final sessions = await store.sessions(learnerId: _p6.learnerId);
      expect(sessions, hasLength(1));
      final e = sessions.single.events.single;
      expect(e.kind, EvidenceKind.participation);
      _expectLineage(e);
      expect(sessions.single.subjectId, 'khtn');

      // Mở lại Book Home: badge phải đổi — đây là chính lỗi C7 của audit.
      await t.pumpWidget(home(2));
      await t.pumpAndSettle();
      final again = find.widgetWithText(ListTile, 'Bài 17 · Tách chất khỏi hỗn hợp');
      expect(again, findsOneWidget);
      expect(find.descendant(of: again, matching: find.textContaining('Đã học ·')),
          findsOneWidget,
          reason: '⭐⭐ audit C7: trước WAL-210 chỗ này là «Chưa học»');
      expect(find.descendant(of: again, matching: find.textContaining('Tự làm được')),
          findsNothing,
          reason: '⭐⭐ Founder D1: một nút bấm không thành «Tự làm được»');
      // Bài 16 không lây.
      final other = find.widgetWithText(ListTile, 'Bài 16 · Hỗn hợp các chất');
      expect(find.descendant(of: other, matching: find.textContaining('Đã học')),
          findsNothing);
    });
  });

  group('(c) FILE THẬT — pack lớp 6 trên máy', () {
    test('Bài 17 «Tách chất khỏi hỗn hợp» có trong mục lục KHTN 6', () {
      final f = File('assets/pack/lesson-index-g6.json');
      if (!f.existsSync()) {
        markTestSkipped('pack lớp 6 chưa dựng trên máy này');
        return;
      }
      final idx = LessonIndex.fromJsonString(f.readAsStringSync())!;
      final khtn = (idx.subjects['KHTN'] ?? const <BookLessons>[])
          .where((b) => b.sourceDocumentId == _book)
          .expand((b) => b.lessons)
          .where((l) => l.no == _lesson)
          .toList();
      expect(khtn, isNotEmpty, reason: 'bài mẫu chung của các track phải có');
      expect(khtn.first.title, 'Tách chất khỏi hỗn hợp');
      final acts = idx.activitiesFor(book: _book, lessonNo: _lesson);
      if (acts.isEmpty) {
        markTestSkipped('Bài 17 chưa có hoạt động trên pack này (chờ lane Python '
            'dựng lại pack với buildProvenance — pack hôm nay chỉ có bài đọc '
            'pattern-router)');
        return;
      }
      if (idx.packVersion == null) {
        markTestSkipped('pack chưa khai buildProvenance — chưa có packVersion để '
            'kiểm (chờ lane Python)');
        return;
      }
      expect(idx.packVersion, isNotEmpty);
    });
  });
}
