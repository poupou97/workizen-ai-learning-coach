/// WAL-138 — Home theo home1: agenda card thật, 5 intent chips, REST không nút.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/core/store/timetable.dart';
import 'package:learning_coach/core/store/learning_session.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/features/mission/mission_center_screen.dart';
import 'package:learning_coach/features/mission/mission_data.dart';

const _p = LearnerProfile(learnerId: 'l-h', displayName: 'Na', grade: 5);

LearningSession _session(String id, DateTime at) => LearningSession(
      sessionId: id,
      learnerId: 'l-h',
      subjectId: 'toan',
      startedAt: at,
      trigger: SessionTrigger.cameraHomework,
      events: [
        LearningEvent(
          eventId: '$id-e',
          skillCaseId: 'denominator-non-divisible',
          kind: EvidenceKind.independentAttempt,
          correct: true,
          at: at,
        ),
      ],
    );

void main() {
  final today = DateTime(2026, 9, 2, 19);

  testWidgets('5 intent chips + ô hỏi SAM trung thực + card VIỆC SAM ĐỀ XUẤT',
      (t) async {
    final store = JsonlLearnerStore();
    final data =
        await buildMissionFromStore(profile: _p, store: store, now: today);
    expect(data.agenda, isNotNull, reason: 'store path phải có agenda');

    await t.pumpWidget(MaterialApp(
        home: MissionCenterScreen(
      data: data,
      onOpenSubjects: () {},
      onReview: () {},
      onStartHomework: () {},
    )));
    for (final chip in [
      '📘 Học trước', '🔁 Ôn luyện', '📷 Làm bài tập',
      '🧭 Học phương pháp', '✅ Kiểm tra hiểu bài',
    ]) {
      expect(find.text(chip), findsOneWidget, reason: chip);
    }
    expect(find.textContaining('SAM đang học cách trò chuyện'), findsOneWidget,
        reason: 'ô hỏi SAM là trạng thái trung thực, không chat giả');
    expect(find.text('VIỆC SAM ĐỀ XUẤT'), findsOneWidget);
    expect(find.text(data.agenda!.reason), findsOneWidget,
        reason: 'reason agenda NGUYÊN VĂN');
  });

  testWidgets('đủ 3 phiên hôm nay ⇒ REST: tiêu đề nghỉ + KHÔNG nút Bắt đầu',
      (t) async {
    final store = JsonlLearnerStore();
    for (var i = 0; i < 3; i++) {
      await store
          .appendSession(_session('s$i', today.subtract(Duration(hours: i + 1))));
    }
    final data =
        await buildMissionFromStore(profile: _p, store: store, now: today);
    await t.pumpWidget(MaterialApp(home: MissionCenterScreen(data: data)));
    expect(find.text('Hôm nay nghỉ ngơi nhé'), findsOneWidget);
    expect(find.textContaining('nghỉ là một phần'), findsOneWidget,
        reason: 'REST reason của resolveAgenda nguyên văn');
    expect(find.text('Bắt đầu'), findsNothing,
        reason: 'REST là nghỉ thật — không có nút gọi vào bàn');
  });

  testWidgets('chip «Học phương pháp» mở sheet trung thực', (t) async {
    final store = JsonlLearnerStore();
    final data =
        await buildMissionFromStore(profile: _p, store: store, now: today);
    await t.pumpWidget(MaterialApp(home: MissionCenterScreen(data: data)));
    await t.tap(find.text('🧭 Học phương pháp'));
    await t.pumpAndSettle();
    expect(find.textContaining('Vì sao cách này?'), findsOneWidget);
  });

  testWidgets('TKB hôm nay ⇒ khu «Sắp tới»; không TKB ⇒ ẩn (F13)', (t) async {
    final store = JsonlLearnerStore();
    await store.saveTimetable('l-h', [
      TimetableEntry(
          learnerId: 'l-h',
          weekday: today.weekday,
          period: 1,
          subjectId: 'Toán'),
    ]);
    final data =
        await buildMissionFromStore(profile: _p, store: store, now: today);
    await t.pumpWidget(MaterialApp(home: MissionCenterScreen(data: data)));
    expect(find.textContaining('Sắp tới ở trường: Toán'), findsOneWidget);

    final empty = await buildMissionFromStore(
        profile: _p, store: JsonlLearnerStore(), now: today);
    await t.pumpWidget(MaterialApp(home: MissionCenterScreen(data: empty)));
    expect(find.textContaining('Sắp tới ở trường'), findsNothing);
  });
}
