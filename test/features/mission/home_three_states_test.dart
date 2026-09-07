/// ⭐⭐ LỆNH 55 — HOME PHẢI TỬ TẾ Ở CẢ BA TRẠNG THÁI.
///
///   A. nhiều mạch học   B. ít mạch học   C. CHƯA có bài nào SAM xếp sẵn
///
/// Trạng thái C là PRODUCT GAP thật (lớp 7 chưa có bài), không phải lý do nới
/// bộ lọc lớp. Nên bài kiểm này giữ hai điều cùng lúc: Home **hữu ích** ở C,
/// **và** vẫn fail-closed — không bài lớp khác nào lẻn vào để lấp chỗ trống.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/features/mission/home_cards.dart';
import 'package:learning_coach/features/mission/mission_center_screen.dart';
import 'package:learning_coach/features/mission/mission_data.dart';

import '../lesson_workspace/support.dart';

LessonDocument _atGrade(LessonDocument d, int grade, String book) =>
    LessonDocument(
      schema: d.schema,
      book: book,
      bookTitle: '$book-title',
      subject: d.subject,
      grade: grade,
      lessonNo: d.lessonNo,
      title: d.title,
      provenance: d.provenance,
      blocks: d.blocks,
      semantic: d.semantic,
      tutorScript: d.tutorScript,
    );

const _shelf7 = [
  HomeShelfSubject(subject: 'Toán', listedLessons: 40, openableLessons: 0),
  HomeShelfSubject(subject: 'KHTN', listedLessons: 50, openableLessons: 1),
  HomeShelfSubject(subject: 'Ngữ văn', listedLessons: 20, openableLessons: 0),
];

Future<void> _pump(
  WidgetTester t, {
  required List<HomeLessonThread> threads,
  required int grade,
}) async {
  t.view.physicalSize = const Size(720, 6000);
  t.view.devicePixelRatio = 2.0;
  addTearDown(t.view.resetPhysicalSize);
  addTearDown(t.view.resetDevicePixelRatio);
  await t.pumpWidget(
    MaterialApp(
      home: MissionCenterScreen(
        data: buildDemoMission(now: DateTime(2026, 9, 7, 19)),
        learnerName: 'Bi',
        learnerGrade: grade,
        lessonThreads: threads,
        shelfSubjects: _shelf7,
        subjectChips: const [
          HomeSubjectChip(subject: 'Toán', hasSamLesson: false),
          HomeSubjectChip(subject: 'KHTN', hasSamLesson: false),
          HomeSubjectChip(subject: 'Ngữ văn', hasSamLesson: false),
        ],
        onOpenSubjects: () {},
      ),
    ),
  );
  await t.pump();
}

void main() {
  final base = loadSyntheticDoc();

  testWidgets('C — chưa có bài SAM: nói THẲNG, có việc làm được, có lớp', (
    t,
  ) async {
    await _pump(t, threads: const [], grade: 7);

    expect(find.byKey(MissionCenterScreen.noSamLessonKey), findsOneWidget);
    expect(
      find.textContaining('Chưa có bài học SAM chuẩn bị sẵn cho lớp 7'),
      findsOneWidget,
    );
    // Việc thật duy nhất làm được lúc này.
    expect(find.widgetWithText(FilledButton, 'Mở giá sách'), findsOneWidget);
    // Lớp hiện ngay dưới tên — máy của chung.
    // «Lớp 7» còn xuất hiện dưới mỗi bìa sách, nên khoá theo KEY của dòng
    // lời chào chứ không theo chuỗi.
    final gradeLine = find.byKey(MissionCenterScreen.gradeLineKey);
    expect(gradeLine, findsOneWidget);
    expect(t.widget<Text>(gradeLine).data, 'Lớp 7');
  });

  testWidgets('⛔ C — KHÔNG được nói «không có gì để học»', (t) async {
    await _pump(t, threads: const [], grade: 7);
    for (final banned in [
      'Không có gì để học',
      'không có gì để học',
      'Trống',
    ]) {
      expect(find.textContaining(banned), findsNothing, reason: banned);
    }
  });

  testWidgets('⛔⭐ C — KHÔNG lấy bài lớp khác lấp chỗ trống', (t) async {
    // Có bài lớp 6 trong catalog, học sinh lớp 7 ⇒ vẫn là trạng thái C.
    await _pump(
      t,
      threads: [
        HomeLessonThread(doc: _atGrade(base, 6, '06-sgk-khoa-hoc-tu-nhien-6')),
      ],
      grade: 7,
    );
    expect(
      find.byKey(MissionCenterScreen.noSamLessonKey),
      findsOneWidget,
      reason: 'bài lớp 6 được dùng để thoát trạng thái C',
    );
    expect(find.byKey(MissionCenterScreen.todayRowKey), findsNothing);
  });

  testWidgets(
    'B — có MỘT mạch học: hàng thẻ hiện, không còn khối trạng thái C',
    (t) async {
      await _pump(
        t,
        threads: [
          HomeLessonThread(
            doc: _atGrade(base, 7, '07-sgk-khoa-hoc-tu-nhien-7'),
          ),
        ],
        grade: 7,
      );
      expect(find.byKey(MissionCenterScreen.noSamLessonKey), findsNothing);
      expect(find.byKey(MissionCenterScreen.todayRowKey), findsOneWidget);
    },
  );

  testWidgets('A — nhiều mạch học: vẫn là hàng thẻ, không khối trạng thái C', (
    t,
  ) async {
    await _pump(
      t,
      threads: [
        HomeLessonThread(doc: _atGrade(base, 7, '07-sgk-khoa-hoc-tu-nhien-7')),
        HomeLessonThread(doc: _atGrade(base, 7, '07-sgk-toan-7')),
      ],
      grade: 7,
    );
    expect(find.byKey(MissionCenterScreen.noSamLessonKey), findsNothing);
    expect(find.byKey(MissionCenterScreen.todayRowKey), findsOneWidget);
  });
}
