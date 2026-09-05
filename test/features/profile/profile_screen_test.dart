/// WAL-137 #02 — Hồ sơ: bốn bất biến, và chuyển người học KHÔNG nhiễm state.
library;

import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/core/store/learning_session.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/evidence_validation.dart';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/features/learning_session/slice_flow.dart'
    show masteryFromStore;
import 'package:learning_coach/features/profile/profile_screen.dart';
import '../../support/curriculum.dart';

const _na = LearnerProfile(learnerId: 'na', displayName: 'Na', grade: 5);
const _bi = LearnerProfile(learnerId: 'bi', displayName: 'Bi', grade: 3);

LearningEvent _ev(String id, {required bool correct}) => LearningEvent(
      eventId: id,
      skillCaseId: 'denominator-non-divisible',
      kind: EvidenceKind.independentAttempt,
      correct: correct,
      validation: _r4Stamp,
      at: DateTime(2026, 9, 3, 10),
      support: SupportLevel.none,
      conceptIds: const ['quy-dong'],
    );

Future<void> _seed(LearnerStore s, LearnerProfile p, List<LearningEvent> e) =>
    s.appendSession(LearningSession(
      sessionId: 'sess-${p.learnerId}',
      learnerId: p.learnerId,
      subjectId: 'toan',
      startedAt: DateTime(2026, 9, 3, 10),
      trigger: SessionTrigger.manual,
      events: e,
    ));

/// Nút «Lưu» nằm dưới fold trong ListView lười — phải cuộn tới rồi mới bấm
/// được (bài học lặp lại nhiều lần ở repo này).
Future<void> _tapSave(WidgetTester t) async {
  await t.scrollUntilVisible(find.widgetWithText(FilledButton, 'Lưu'), 200,
      scrollable: find.byType(Scrollable).first);
  await t.tap(find.widgetWithText(FilledButton, 'Lưu'));
  await t.pumpAndSettle();
}

/// ROUND 4 (A-runtime, Founder §4 — strict validation default): the graded
/// events this test seeds simulate the Deep path (TutorSession), which has
/// stamped `fraction-check-v1` since round 3; unstamped graded events now read
/// as `historicalUnvalidated` and never as «Tự làm được». Fixture-only change,
/// no assertion changed. — lane A-runtime touched this Lane B test file.
const _r4Stamp =
    EvidenceValidation(validatorId: 'fraction-check-v1', validatorVersion: '1');

void main() {
  testWidgets('⭐ ĐỔI LỚP không đụng bằng chứng (bất biến 2, WAL-95)',
      (t) async {
    final store = JsonlLearnerStore();
    await store.saveProfile(_na);
    await _seed(store, _na, [_ev('e0', correct: true), _ev('e1', correct: true)]);
    final before = await masteryFromStore(store, 'na', toan5Bai6);

    LearnerProfile? saved;
    await t.pumpWidget(MaterialApp(
        home: ProfileScreen(
            profile: _na, store: store, onSaved: (p) => saved = p)));
    await t.pumpAndSettle();
    await t.tap(find.widgetWithText(FilledButton, '4')); // lớp 5 → lớp 4
    await t.pump();
    await _tapSave(t);

    expect(saved!.grade, 4);
    expect(saved!.learnerId, 'na', reason: '⭐ đổi lớp KHÔNG được đổi danh tính');
    final after = await masteryFromStore(store, 'na', toan5Bai6);
    expect(after.cases.length, before.cases.length);
    for (final k in before.cases.keys) {
      expect(after.cases[k]!.independentCorrect,
          before.cases[k]!.independentCorrect,
          reason: '⭐ đổi lớp làm mất bằng chứng ⇒ đỏ');
      expect(after.cases[k]!.hasEvidence, before.cases[k]!.hasEvidence);
    }
  });

  testWidgets('năm sinh TUỲ CHỌN: để trống vẫn lưu được', (t) async {
    final store = JsonlLearnerStore();
    LearnerProfile? saved;
    await t.pumpWidget(MaterialApp(
        home: ProfileScreen(
            profile: _na, store: store, onSaved: (p) => saved = p)));
    await t.pumpAndSettle();
    await _tapSave(t);
    expect(saved, isNotNull);
    expect(saved!.birthYear, isNull);
  });

  testWidgets('năm sinh nhập bậy ⇒ bỏ qua, KHÔNG đoán hộ', (t) async {
    final store = JsonlLearnerStore();
    LearnerProfile? saved;
    await t.pumpWidget(MaterialApp(
        home: ProfileScreen(
            profile: _na, store: store, onSaved: (p) => saved = p)));
    await t.pumpAndSettle();
    await t.enterText(find.byType(TextField).last, 'hai ngàn mười lăm');
    await _tapSave(t);
    expect(saved!.birthYear, isNull);
    expect(saved!.grade, 5, reason: 'không suy lớp từ chỗ khác');
  });

  test('⭐⭐ A → B → A: chuyển người học KHÔNG nhiễm state', () async {
    final store = JsonlLearnerStore();
    await store.saveProfile(_na);
    await store.saveProfile(_bi);
    // Na có 2 lần tự làm ĐÚNG; Bi có 1 lần SAI. Hai sổ học khác hẳn nhau.
    await _seed(store, _na, [_ev('a0', correct: true), _ev('a1', correct: true)]);
    await _seed(store, _bi, [_ev('b0', correct: false)]);

    final c = toan5Bai6;
    Future<ConceptMastery> m(String id) => masteryFromStore(store, id, c);

    final naFirst = await m('na');
    await store.saveActiveLearner('bi');
    final bi = await m('bi');
    await store.saveActiveLearner('na');
    final naAgain = await m('na');

    const k = 'denominator-non-divisible';
    expect(naFirst.cases[k]!.independentCorrect, 2);
    expect(bi.cases[k]!.independentCorrect, 0,
        reason: '⭐⭐ bằng chứng của Na rò sang Bi ⇒ đỏ');
    expect(naAgain.cases[k]!.independentCorrect, 2,
        reason: '⭐⭐ quay lại Na mà số liệu đổi ⇒ state bị nhiễm');
    expect(naAgain.cases[k]!.evidenceCount, naFirst.cases[k]!.evidenceCount);
    expect(naAgain.cases[k]!.pMastery, naFirst.cases[k]!.pMastery);
    expect(await store.activeLearnerId(), 'na');
  });

  testWidgets(
      '⭐⭐ nhập năm sinh HỢP LỆ ⇒ lớp GIỮ NGUYÊN theo lựa chọn, KHÔNG suy từ '
      'tuổi (bất biến 1)', (t) async {
    // Đây là test bắt được đột biến mà bản grep cấu trúc để lọt: mã suy lớp
    // có thể dùng biến tên khác (`birth`), nên phải kiểm HÀNH VI, không kiểm
    // chữ. Bé 2015 mà đang học lớp 3 (đi học muộn/ở lại) — SAM phải nghe theo
    // lựa chọn, không tự tính 2026-2015-6 = 5.
    final store = JsonlLearnerStore();
    LearnerProfile? saved;
    await t.pumpWidget(MaterialApp(
        home: ProfileScreen(
            profile: _na, store: store, onSaved: (p) => saved = p)));
    await t.pumpAndSettle();
    await t.enterText(find.byType(TextField).last, '2015');
    await t.tap(find.widgetWithText(FilledButton, '3'));
    await t.pump();
    await _tapSave(t);
    expect(saved!.birthYear, 2015);
    expect(saved!.grade, 3,
        reason: '⭐⭐ đột biến suy lớp từ năm sinh ⇒ đỏ');
  });

  testWidgets('⭐⭐ cùng năm sinh, khác lớp — hai đứa trẻ có thật', (t) async {
    final store = JsonlLearnerStore();
    final grades = <int>[];
    for (final g in [2, 7]) {
      LearnerProfile? saved;
      await t.pumpWidget(MaterialApp(
          home: ProfileScreen(
              profile: _na, store: store, onSaved: (p) => saved = p)));
      await t.pumpAndSettle();
      await t.enterText(find.byType(TextField).last, '2015');
      await t.tap(find.widgetWithText(FilledButton, '$g'));
      await t.pump();
      await _tapSave(t);
      grades.add(saved!.grade);
    }
    expect(grades, [2, 7],
        reason: '⭐⭐ cùng 2015 mà lớp bị ép về một giá trị ⇒ đang suy từ tuổi');
  });

  test('⭐ CẤU TRÚC: không mã nào suy LỚP từ NĂM SINH', () {
    // Hai đứa cùng tuổi có thể khác lớp (đi học sớm, ở lại, học vượt). Nếu
    // một ngày có ai viết `grade = năm nay - birthYear + …` thì test này đỏ.
    final files = Directory('lib')
        .listSync(recursive: true)
        .whereType<File>()
        .where((f) => f.path.endsWith('.dart'));
    for (final f in files) {
      final src = f.readAsStringSync();
      for (final line in src.split('\n')) {
        if (!line.contains('birthYear')) continue;
        expect(RegExp(r'grade\s*[:=][^;]*birthYear').hasMatch(line), isFalse,
            reason: '⭐ suy lớp từ năm sinh tại ${f.path}: $line');
      }
    }
  });
}
