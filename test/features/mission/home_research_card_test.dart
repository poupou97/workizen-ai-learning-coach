/// LANE C (round 4) — Home: lát cắt NGHIÊN CỨU của lớp khác hiện thành thẻ
/// riêng, ghi rõ «SÁCH LỚP 5», mở bằng cùng callback; không có ⇒ không thẻ;
/// thẻ Bài 17 của đúng lớp không đổi.
library;

import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/lesson_model/workspace_catalog.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/features/mission/mission_center_screen.dart';
import 'package:learning_coach/features/mission/mission_data.dart';

import '../lesson_workspace/support.dart';

const _g6 = LearnerProfile(learnerId: 'l6', displayName: 'Na', grade: 6);

Future<MissionData> _data() => buildMissionFromStore(
  profile: _g6,
  store: JsonlLearnerStore(),
  now: DateTime(2026, 9, 5, 19),
);

LessonDocument _history() {
  final j = jsonDecode(
    File('assets/fixtures/synthetic/lesson-05-sgk-lich-su-va-dia-li-5-b8.synthetic.json').readAsStringSync(),
  ) as Map;
  return LessonDocument.fromJson(j.cast<String, Object?>(), assetBase: FixtureSlot.syntheticDir)!;
}

void main() {
  testWidgets('thẻ Bài 17 (đúng lớp) + thẻ «LÁT CẮT NGHIÊN CỨU · SÁCH LỚP 5» (Bài 8); mở trả đúng tài liệu', (t) async {
    final b17 = loadSyntheticDoc();
    final b8 = _history();
    expect(WorkspaceCatalog.isResearchSlot(b8), isTrue);
    expect(WorkspaceCatalog.isResearchSlot(b17), isFalse);
    LessonDocument? opened;
    await t.pumpWidget(
      fixtureHost(
        MissionCenterScreen(
          data: await _data(),
          onOpenSubjects: () {},
          workspaceLesson: b17,
          researchLessons: [b8],
          onOpenWorkspaceLesson: (d) => opened = d,
        ),
      ),
    );
    await t.pumpAndSettle();
    expect(find.byKey(MissionCenterScreen.workspaceCardKey), findsOneWidget);
    // Home là ListView lười: thẻ thứ hai nằm dưới màn 600 px ⇒ cuộn tới khi thấy
    final card = find.byKey(MissionCenterScreen.researchCardKey(b8.slotKey));
    await t.scrollUntilVisible(card, 120, scrollable: find.byType(Scrollable).first);
    await t.pumpAndSettle();
    expect(card, findsOneWidget);
    expect(find.text('LÁT CẮT NGHIÊN CỨU · SÁCH LỚP 5 · BẢN THỬ NGHIỆM'), findsOneWidget);
    expect(find.textContaining('Bài 8 · Đấu tranh mẫu'), findsOneWidget);
    expect(find.textContaining('trang 36–39'), findsOneWidget);
    final open = find.descendant(of: card, matching: find.text('Mở bài học'));
    await t.ensureVisible(open);
    await t.tap(open);
    expect(opened?.slotKey, b8.slotKey);
  });

  /// ⭐⭐ LANE B (round 4) — MẠCH LẠC với khu «Hôm nay». Thẻ lát cắt là sách
  /// LỚP 5 trên máy của học sinh lớp 6: nó KHÔNG được đứng lẫn trong việc hôm
  /// nay như nội dung bình thường. Chốt: nhãn khu riêng, một dòng lời trẻ nói
  /// thẳng «không phải bài của lớp con», và thẻ nằm DƯỚI thẻ Bài học SAM.
  testWidgets('⭐⭐ lát cắt nghiên cứu có KHU RIÊNG dưới «Hôm nay», nói bằng '
      'lời trẻ rằng đây không phải bài của lớp mình', (t) async {
    final b17 = loadSyntheticDoc();
    final b8 = _history();
    await t.pumpWidget(
      fixtureHost(
        MissionCenterScreen(
          data: await _data(),
          onOpenSubjects: () {},
          workspaceLesson: b17,
          researchLessons: [b8],
          onOpenWorkspaceLesson: (_) {},
        ),
      ),
    );
    await t.pumpAndSettle();
    double y(Finder f) => t.getTopLeft(f).dy;

    // ① Ở đầu màn: nhãn HÔM NAY đứng trên thẻ Bài học SAM, và khu nghiên cứu
    // CHƯA xuất hiện — nó không chen vào việc hôm nay.
    expect(y(find.text('HÔM NAY')),
        lessThan(y(find.byKey(MissionCenterScreen.workspaceCardKey))));
    expect(find.text('SAM ĐANG TẬP ĐỌC SÁCH KHÁC'), findsNothing);

    final card = find.byKey(MissionCenterScreen.researchCardKey(b8.slotKey));
    await t.scrollUntilVisible(card, 120, scrollable: find.byType(Scrollable).first);
    await t.pumpAndSettle();

    // ② Cuộn xuống mới tới khu riêng của lát cắt.
    expect(find.text('SAM ĐANG TẬP ĐỌC SÁCH KHÁC'), findsOneWidget);
    final line = find.byKey(MissionCenterScreen.researchAreaLineKey);
    expect(line, findsOneWidget);
    final lineText = t.widget<Text>(line).data!;
    expect(lineText, contains('không phải bài của lớp con'));
    // Lời trẻ: không mã máy, không %, không hứa hẹn.
    expect(lineText, isNot(contains('%')));
    expect(lineText, isNot(matches(RegExp(r'[a-z]+-[a-z]+-v\d'))));

    // ③ Nhãn khu đứng TRÊN thẻ — trẻ đọc lời cảnh báo trước khi thấy thẻ.
    expect(y(find.text('SAM ĐANG TẬP ĐỌC SÁCH KHÁC')), lessThan(y(card)));
    expect(y(line), lessThan(y(card)));

    // Thẻ nghiên cứu KHÔNG BAO GIỜ mang nhãn bài học của lớp này.
    expect(
        find.descendant(of: card, matching: find.text('BÀI HỌC SAM · BẢN THỬ NGHIỆM')),
        findsNothing);
  });

  testWidgets('không có lát cắt nghiên cứu ⇒ không có thẻ thứ hai', (t) async {
    await t.pumpWidget(
      fixtureHost(
        MissionCenterScreen(
          data: await _data(),
          onOpenSubjects: () {},
          workspaceLesson: loadSyntheticDoc(),
          onOpenWorkspaceLesson: (_) {},
        ),
      ),
    );
    await t.pumpAndSettle();
    expect(find.textContaining('LÁT CẮT NGHIÊN CỨU'), findsNothing);
  });
}
