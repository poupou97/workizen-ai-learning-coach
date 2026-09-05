/// WAL-136 — Subjects/SubjectHome: grid từ data, bài mở được vs nói thật.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/core/store/learning_session.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/evidence_validation.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';
import 'package:learning_coach/features/subjects/subject_home_screen.dart';
import 'package:learning_coach/features/subjects/subjects_screen.dart';

const _p = LearnerProfile(learnerId: 'l', displayName: 'M', grade: 5);

LessonIndex idx() => LessonIndex.fromJsonString('''
{"grade":5,"subjects":{
  "Toán":[{"sourceDocumentId":"05-sgk-toan-5-tap-mot","volume":"1",
    "lessons":[{"no":6,"title":"CỘNG, TRỪ HAI PHÂN SỐ KHÁC MẪU SỐ","pageStart":20},
               {"no":9,"title":"THỂ TÍCH","pageStart":40}]}],
  "Khoa học":[{"sourceDocumentId":"05-sgk-khoa-hoc-5","volume":null,
    "lessons":[{"no":1,"title":"ĐẤT VÀ NƯỚC","pageStart":6}]}]},
 "toanExercises":{"6":[{"expr":"1/2 - 1/5","page":21,"book":"05-sgk-toan-5-tap-mot"}]}}
''')!;

/// ROUND 4 (A-runtime, Founder §4 — strict validation default): the graded
/// events this test seeds simulate the Deep path (TutorSession), which has
/// stamped `fraction-check-v1` since round 3; unstamped graded events now read
/// as `historicalUnvalidated` and never as «Tự làm được». Fixture-only change,
/// no assertion changed. — lane A-runtime touched this Lane B test file.
const _r4Stamp =
    EvidenceValidation(validatorId: 'fraction-check-v1', validatorVersion: '1');

void main() {
  testWidgets('grid môn sinh từ data; thiếu index ⇒ nói thật', (t) async {
    await t.pumpWidget(MaterialApp(
        home: SubjectsScreen(
            profile: _p, store: JsonlLearnerStore(), index: idx())));
    expect(find.text('Môn học · Lớp 5'), findsOneWidget);
    expect(find.text('Toán'), findsOneWidget);
    expect(find.text('Khoa học'), findsOneWidget);

    await t.pumpWidget(MaterialApp(
        home: SubjectsScreen(
            profile: _p, store: JsonlLearnerStore(), index: null)));
    expect(find.textContaining('chưa nạp mục lục'), findsOneWidget);
  });

  testWidgets('Subject Home: tên bài THẬT; bài có bài tập mở được, bài chưa '
      'nối engine nói thật (không dead-end)', (t) async {
    await t.pumpWidget(MaterialApp(
        home: SubjectHomeScreen(
            profile: _p,
            store: JsonlLearnerStore(),
            index: idx(),
            subject: 'Toán')));
    expect(find.textContaining('Cộng, trừ hai phân số khác mẫu số'),
        findsOneWidget, reason: 'title mined thật, đổi về câu thường');
    expect(find.textContaining('1 bài tập từ SGK'), findsOneWidget);
    expect(find.textContaining('SAM đang học bài này'), findsOneWidget,
        reason: 'bài 9 chưa có exercises — nói thật');

    // ⭐ WAL-175 — bấm bài ra bộ chọn Ý ĐỊNH, không phải danh sách việc.
    await t.tap(find.textContaining('Cộng, trừ hai phân số'));
    await t.pumpAndSettle();
    expect(find.text('Con muốn bắt đầu thế nào?'), findsOneWidget,
        reason: 'không có thời khoá biểu, không có bằng chứng ⇒ SAM HỎI, '
            'không bịa lý do');
    expect(find.text('Con có bài tập'), findsOneWidget);
    expect(find.text('Xem trong sách'), findsOneWidget);

    // «Xem trong sách» dẫn tới NGUỒN, và nguồn phải đúng luật
    // (demonstrated ≠ «sách nói rằng»).
    await t.tap(find.text('Xem trong sách'));
    await t.pumpAndSettle();
    expect(find.textContaining('làm theo ví dụ trong SGK Toán 5, trang 21'),
        findsOneWidget);
    expect(find.textContaining('làm theo ví dụ trong SGK Toán 4, trang 77'),
        findsOneWidget, reason: 'take-larger cũng demonstrated — cùng luật');
    expect(find.textContaining('sách nói'), findsNothing);
    await t.tapAt(const Offset(400, 50)); // đóng sheet
    await t.pumpAndSettle();
    await t.tap(find.textContaining('Cộng, trừ hai phân số'));
    await t.pumpAndSettle();
    await t.tap(find.text('Con có bài tập'));
    await t.pumpAndSettle();
    expect(find.text('1/2 - 1/5'), findsOneWidget,
        reason: 'bài THẬT từ SGK (cur: origin), không placeholder');
    expect(find.textContaining('SAM làm theo ví dụ trong SGK Toán 5'),
        findsOneWidget, reason: 'provenance hiện TRƯỚC khi học');
  });

  // ⭐⭐ WAL-181 — badge Learning Map trong ĐÚNG tile đã có (không dashboard
  // riêng, đúng Founder UX Constraint 2026-09-04).
  group('Learning Map badge', () {
    testWidgets('⭐ chưa có event nào khớp lineage ⇒ không hiện badge nào',
        (t) async {
      await t.pumpWidget(MaterialApp(
          home: SubjectHomeScreen(
              profile: _p,
              store: JsonlLearnerStore(),
              index: idx(),
              subject: 'Toán')));
      await t.pumpAndSettle();
      expect(find.textContaining('Tự làm được'), findsNothing);
      expect(find.textContaining('Đã học cùng SAM'), findsNothing);
    });

    testWidgets(
        '⭐⭐ có independentAttempt khớp đúng bài ⇒ badge "Tự làm được" hiện '
        'ĐÚNG tile, không lan sang bài khác', (t) async {
      final store = JsonlLearnerStore();
      await store.appendSession(LearningSession(
        sessionId: 's1',
        learnerId: 'l',
        subjectId: 'toan',
        startedAt: DateTime(2026, 9, 4),
        trigger: SessionTrigger.manual,
        events: [
          LearningEvent(
            eventId: 'e1',
            skillCaseId: 'denominator-non-divisible',
            kind: EvidenceKind.independentAttempt,
            // WAL-210 D1: «Tự làm được» chỉ từ tự làm ĐÃ CHẤM đúng.
            // ROUND 4: … và ĐÃ KIỂM (dấu validator được duyệt).
            correct: true,
            validation: _r4Stamp,
            at: DateTime(2026, 9, 4),
            sourceDocumentId: '05-sgk-toan-5-tap-mot',
            lessonNo: 6,
          ),
        ],
      ));
      await t.pumpWidget(MaterialApp(
          home: SubjectHomeScreen(
              profile: _p, store: store, index: idx(), subject: 'Toán')));
      await t.pumpAndSettle();
      expect(find.textContaining('Tự làm được'), findsOneWidget,
          reason: '⭐⭐ đột biến không đọc lineage thật ⇒ đỏ');
      // Bài 9 (Thể tích) không có event nào khớp — không được lây badge.
      expect(
          find.descendant(
              of: find.widgetWithText(ListTile, 'Bài 9 · Thể tích'),
              matching: find.textContaining('Tự làm được')),
          findsNothing,
          reason: 'badge không được lan sang bài chưa có bằng chứng');
    });
  });
}
