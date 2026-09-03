/// WAL-145 #34 — quyền dữ liệu: lấy ra ĐỦ, xoá THẬT, không đụng con khác.
library;

import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/file_store.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/core/store/learning_session.dart';
import 'package:learning_coach/core/store/timetable.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/features/parent/family_manager_screen.dart';
import 'package:learning_coach/features/parent/parent_area.dart';

const _na = LearnerProfile(learnerId: 'na', displayName: 'Na', grade: 5);
const _bi = LearnerProfile(learnerId: 'bi', displayName: 'Bi', grade: 3);

Future<void> _seed(LearnerStore s) async {
  await s.saveProfile(_na);
  await s.saveProfile(_bi);
  await s.saveParentPin('1234');
  await s.saveActiveLearner('na');
  await s.saveTimetable('na',
      [const TimetableEntry(learnerId: 'na', weekday: 1, period: 1, subjectId: 'Toán')]);
  for (final id in ['na', 'bi']) {
    await s.appendSession(LearningSession(
      sessionId: 's-$id',
      learnerId: id,
      subjectId: 'toan',
      startedAt: DateTime(2026, 9, 3, 10),
      trigger: SessionTrigger.manual,
      events: [
        LearningEvent(
            eventId: '$id#0',
            skillCaseId: 'denominator-non-divisible',
            kind: EvidenceKind.independentAttempt,
            correct: true,
            at: DateTime(2026, 9, 3, 10),
            support: SupportLevel.none,
            conceptIds: const ['quy-dong']),
      ],
    ));
  }
}

void main() {
  test('⭐ XUẤT: đủ dữ liệu của ĐÚNG một con, KHÔNG kèm của anh chị em', () async {
    final s = JsonlLearnerStore();
    await _seed(s);
    final out = await s.exportLearner('na');
    expect(out, contains('"learnerId":"na"'));
    expect(out.contains('"learnerId":"bi"'), isFalse,
        reason: '⭐ xuất kèm dữ liệu con khác ⇒ rò riêng tư');
    // đủ ba loại bản ghi mang learnerId: hồ sơ, phiên học, thời khoá biểu
    expect(out, contains('"type":"profile"'));
    expect(out, contains('"type":"session"'));
    expect(out, contains('"type":"timetable"'));
    // dữ liệu của MÁY (pin bố mẹ) KHÔNG phải của trẻ ⇒ không xuất
    expect(out.contains('1234'), isFalse);
  });

  test('⭐⭐ XOÁ LÀ XOÁ THẬT: bản ghi biến mất, con khác nguyên vẹn', () async {
    final s = JsonlLearnerStore();
    await _seed(s);
    final n = await s.deleteLearner('na');
    expect(n, greaterThan(0));
    expect(await s.exportLearner('na'), isEmpty,
        reason: '⭐⭐ còn sót bản ghi ⇒ «đã xoá» là nói dối');
    expect((await s.profiles()).map((p) => p.learnerId), ['bi']);
    expect(await s.sessions(learnerId: 'na'), isEmpty);
    expect(await s.sessions(learnerId: 'bi'), hasLength(1),
        reason: '⭐⭐ xoá con này làm mất dữ liệu con kia ⇒ đỏ');
    expect(await s.parentPin(), '1234', reason: 'dữ liệu máy không bị đụng');
  });

  test('⭐⭐ XOÁ phải xuống ĐĨA — mở lại không sống lại', () async {
    final dir = await Directory.systemTemp.createTemp('wal145');
    final f = File('${dir.path}/store.jsonl');
    final s1 = await FileLearnerStore.open(f);
    await _seed(s1);
    await s1.deleteLearner('na');
    // Mở LẠI từ đĩa — đây mới là phép thử thật.
    final s2 = await FileLearnerStore.open(f);
    expect(await s2.exportLearner('na'), isEmpty,
        reason: '⭐⭐ chỉ xoá trong bộ nhớ ⇒ mở lại dữ liệu sống lại');
    expect((await s2.profiles()).map((p) => p.learnerId), ['bi']);
    await dir.delete(recursive: true);
  });

  testWidgets('màn hiện quyền, nói rõ dữ liệu không rời máy', (t) async {
    final s = JsonlLearnerStore();
    await _seed(s);
    await t.pumpWidget(MaterialApp(
        home: FamilyManagerScreen(store: s, profiles: const [_na, _bi])));
    await t.pumpAndSettle();
    expect(find.textContaining('không gửi đi đâu cả'), findsOneWidget);
    expect(find.text('Na · Lớp 5'), findsOneWidget);
    expect(find.text('Bi · Lớp 3'), findsOneWidget);
    expect(find.text('Lấy dữ liệu ra'), findsNWidgets(2));
  });

  testWidgets('⭐ xoá phải QUA XÁC NHẬN — bấm nhầm không mất dữ liệu',
      (t) async {
    final s = JsonlLearnerStore();
    await _seed(s);
    await t.pumpWidget(MaterialApp(
        home: FamilyManagerScreen(store: s, profiles: const [_na, _bi])));
    await t.pumpAndSettle();
    await t.tap(find.text('Xoá dữ liệu').first);
    await t.pumpAndSettle();
    expect(find.textContaining('KHÔNG lấy lại được'), findsOneWidget);
    await t.tap(find.text('Thôi'));
    await t.pumpAndSettle();
    expect(await s.sessions(learnerId: 'na'), hasLength(1),
        reason: '⭐ bấm «Thôi» mà vẫn xoá ⇒ đỏ');
  });

  testWidgets('xuất khi máy KHÔNG ghi được tệp ⇒ nói thật, không bịa đường dẫn',
      (t) async {
    final s = JsonlLearnerStore();
    await _seed(s);
    await t.pumpWidget(MaterialApp(
        home: FamilyManagerScreen(store: s, profiles: const [_na])));
    await t.pumpAndSettle();
    await t.tap(find.text('Lấy dữ liệu ra'));
    await t.pumpAndSettle();
    expect(find.textContaining('chưa ghi được ra tệp'), findsOneWidget);
    expect(find.textContaining('dòng dữ liệu của Na'), findsOneWidget);
  });

  testWidgets('⭐ màn PIN KHÔNG tràn khi bàn phím chiếm nửa dưới màn',
      (t) async {
    // Đi máy Nokia lộ ra: bàn phím số đẩy màn tràn 8.8px. Bản debug hiện sọc
    // vàng-đen; bản phát hành thì CẮT mất nút — phụ huynh bấm không được.
    final s = JsonlLearnerStore();
    t.view.physicalSize = const Size(1080, 1920);
    t.view.devicePixelRatio = 2.75;
    t.view.viewInsets = FakeViewPadding(bottom: 900); // bàn phím
    addTearDown(t.view.reset);
    await t.pumpWidget(MaterialApp(
        home: ParentPinScreen(store: s, existingPin: null)));
    await t.pumpAndSettle();
    expect(t.takeException(), isNull,
        reason: '⭐ tràn layout khi có bàn phím ⇒ đỏ');
  });

  test('⭐⭐ KHÔNG so sánh anh chị em ở bất kỳ đâu trong khu bố mẹ', () {
    for (final f in [
      'lib/features/parent/family_manager_screen.dart',
      'lib/features/parent/parent_area.dart',
      'lib/features/parent/parent_tonight_screen.dart',
    ]) {
      // Chỉ quét chữ HIỂN THỊ. Bản đầu quét cả file nên bắt nhầm chính câu
      // chú thích «KHÔNG xếp hạng» — tức là phạt đúng chỗ đang cấm điều đó.
      final src = File(f)
          .readAsLinesSync()
          .where((l) => !l.trimLeft().startsWith('//'))
          .join('\n')
          .toLowerCase();
      for (final banned in [
        'xếp hạng',
        'ranking',
        'giỏi hơn',
        'so với bạn',
        'leaderboard',
        'hơn em',
      ]) {
        expect(src.contains(banned), isFalse,
            reason: '⭐⭐ §15: khu bố mẹ có chữ so sánh «$banned» tại $f');
      }
    }
  });
}
