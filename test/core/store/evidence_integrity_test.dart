/// ⭐⭐ WAL-210 (B-lane) — TÍNH TOÀN VẸN KHO BẰNG CHỨNG: port hai check ĐỎ của
/// audit tiền-tự-trị (`docs/research/pre-autonomy-audit/scripts/
/// runtime_checks.dart`, C1 + C3) thành test thường trực, kèm C2/C8 để khẳng
/// định không có dedupe im lặng nào lọt vào.
///
/// - C1: mở lại CÙNG bài tập ⇒ id sự kiện KHÁC nhau (trước: `…:b6#0` trùng).
/// - C2: `evidenceFor` giữ ĐỦ sự kiện của cả hai phiên — id duy nhất không
///   được trở thành cớ để nuốt lần làm thứ hai.
/// - C3: cùng MỘT phiên ghi hai lần ⇒ kho không nhân đôi (`appendSession`
///   idempotent theo `sessionId`, trả `false` lần hai).
/// - Dữ liệu cũ (id dạng `…#0`, không token) vẫn nạp và vẫn idempotent.
library;

import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/curriculum/pedagogical_boundary.dart';
import 'package:learning_coach/core/knowledge/slice_curriculum.dart';
import 'package:learning_coach/core/store/file_store.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/core/store/learning_session.dart';
import 'package:learning_coach/core/student/evidence_ids.dart';
import 'package:learning_coach/core/student/evidence_weighting.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/features/shell/session_recorder.dart';
import 'package:learning_coach/features/tutor/tutor_session.dart';

const _profile = LearnerProfile(learnerId: 'L1', displayName: 'A', grade: 5);
const _exercise = 'cur:05-sgk-toan-5-tap-mot:p20:b6';
const _case = 'denominator-non-divisible';

TutorSession _open(DateTime at, {String? token}) {
  final c = curriculumForProblem(_profile, '3/4 + 2/5')!;
  return TutorSession(
    exerciseId: _exercise,
    skillCaseId: _case,
    problem: FractionProblem.parse('3/4 + 2/5')!,
    scope: TutorScope.forProblem(
        c.conceptId, c.classifyCase('3/4 + 2/5'), c.stage, c.catalogue),
    now: () => at,
    sessionToken: token,
  );
}

LearningSession _session(String id, List<LearningEvent> events, DateTime at) =>
    LearningSession(
      sessionId: id,
      learnerId: 'L1',
      subjectId: 'toan',
      startedAt: at,
      trigger: SessionTrigger.manual,
      events: events,
    );

void main() {
  group('C1 — id sự kiện duy nhất giữa các lần mở cùng bài', () {
    test('⭐⭐ hai TutorSession trên CÙNG exerciseId, CÙNG đồng hồ ⇒ không id nào trùng',
        () {
      // Đồng hồ tiêm CỐ ĐỊNH và giống hệt nhau — trường hợp khó nhất: nếu
      // token chỉ dựa vào `now` tiêm vào thì hai phiên này sẽ trùng id.
      final t = DateTime(2026, 9, 5, 10);
      final s1 = _open(t)..submit('23/20');
      final s2 = _open(t)..submit('23/20');
      final ids1 = s1.log.events.map((e) => e.eventId).toSet();
      final ids2 = s2.log.events.map((e) => e.eventId).toSet();
      expect(ids1, hasLength(2));
      expect(ids1.intersection(ids2), isEmpty,
          reason: '⭐⭐ audit C1 FAIL cũ: `\$exerciseId#\$seq` đếm lại từ 0 mỗi '
              'phiên ⇒ mở lại là trùng id');
      // exerciseId trên sự kiện KHÔNG đổi — vẫn là định danh BÀI.
      expect(s1.log.events.every((e) => e.exerciseId == _exercise), isTrue);
      expect(s1.log.events.every((e) => e.eventId.startsWith('$_exercise@')),
          isTrue,
          reason: 'id mang bài + phiên, đọc được bằng mắt khi audit');
    });

    test('token tiêm vào ⇒ id TẤT ĐỊNH (replay/test cần), seq vẫn tăng dần', () {
      final s = _open(DateTime(2026, 9, 5), token: 'tok')..submit('23/20');
      expect(s.log.events.map((e) => e.eventId),
          ['$_exercise@tok#0', '$_exercise@tok#1']);
      expect(s.sessionToken, 'tok');
    });

    test('newEvidenceSessionToken: cùng một thời điểm vẫn khác nhau', () {
      final t = DateTime(2026, 9, 5);
      expect(newEvidenceSessionToken(t), isNot(newEvidenceSessionToken(t)));
      expect(
          evidenceEventId(exerciseId: 'x', sessionToken: 'a', seq: 3), 'x@a#3');
    });
  });

  group('C2/C3 — kho không nuốt phiên thật, không nhân đôi phiên lặp', () {
    test('C2: hai phiên khác nhau ⇒ evidenceFor giữ ĐỦ sự kiện, id phân biệt',
        () async {
      final store = JsonlLearnerStore();
      await store.saveProfile(_profile);
      final t1 = DateTime(2026, 9, 5, 10), t2 = DateTime(2026, 9, 5, 11);
      final s1 = _open(t1)..submit('23/20');
      final s2 = _open(t2)..submit('23/20');
      expect(await store.appendSession(_session('s1', s1.log.events, t1)),
          isTrue);
      expect(await store.appendSession(_session('s2', s2.log.events, t2)),
          isTrue);
      final log = await store.evidenceFor(learnerId: 'L1', skillCaseId: _case);
      expect(log.events, hasLength(4));
      expect(log.events.map((e) => e.eventId).toSet(), hasLength(4),
          reason: 'id duy nhất KHÔNG được trở thành cớ để dedupe lần làm thứ hai');
    });

    test('⭐⭐ C3: cùng MỘT phiên ghi hai lần ⇒ lần hai no-op, mastery không đôi',
        () async {
      final store = JsonlLearnerStore();
      final t = DateTime(2026, 9, 5, 10);
      final s = _open(t)..submit('23/20');
      final sess = _session('dup', s.log.events, t);
      expect(await store.appendSession(sess), isTrue);
      expect(await store.appendSession(sess), isFalse,
          reason: '⭐⭐ audit C3 FAIL cũ: onFinished bắn hai lần ⇒ evidenceCount 2 '
              'từ MỘT lần làm thật');
      final log = await store.evidenceFor(learnerId: 'L1', skillCaseId: _case);
      expect(log.events, hasLength(s.log.events.length));
      final m = replayMastery(log, BktParams.freeResponse);
      expect(m.evidenceCount, 1);
      expect((await store.sessions(learnerId: 'L1')), hasLength(1));
    });

    test('recordSession lần hai cùng sự kiện ⇒ appended=false, kho 1 phiên',
        () async {
      final store = JsonlLearnerStore();
      final s = _open(DateTime(2026, 9, 5, 10))..submit('23/20');
      final first = await recordSession(
          store: store,
          learnerId: 'L1',
          subjectId: 'toan',
          events: s.log.events,
          trigger: SessionTrigger.cameraHomework);
      final retry = await recordSession(
          store: store,
          learnerId: 'L1',
          subjectId: 'toan',
          events: s.log.events,
          trigger: SessionTrigger.cameraHomework);
      expect(first.appended, isTrue);
      expect(retry.appended, isFalse);
      expect(retry.session!.sessionId, first.session!.sessionId);
      expect(await store.sessions(learnerId: 'L1'), hasLength(1));
    });

    test('idempotent CẢ với phiên đã nằm trên đĩa (nạp lại rồi ghi lại)',
        () async {
      final store = JsonlLearnerStore();
      final t = DateTime(2026, 9, 5, 10);
      final s = _open(t)..submit('23/20');
      await store.appendSession(_session('on-disk', s.log.events, t));
      final reloaded = JsonlLearnerStore.fromJsonl(store.toJsonl());
      expect(await reloaded.appendSession(_session('on-disk', s.log.events, t)),
          isFalse,
          reason: 'trạng thái idempotent không được chỉ sống trong RAM');
      expect(await reloaded.sessions(learnerId: 'L1'), hasLength(1));
    });

    test('FileLearnerStore: ghi lặp không ghi lại tệp, không nhân đôi', () async {
      final dir = await Directory.systemTemp.createTemp('wal-210-');
      addTearDown(() => dir.delete(recursive: true));
      final file = File('${dir.path}/store.jsonl');
      final store = await FileLearnerStore.open(file);
      final t = DateTime(2026, 9, 5, 10);
      final s = _open(t)..submit('23/20');
      expect(await store.appendSession(_session('f1', s.log.events, t)), isTrue);
      final sizeAfterFirst = await file.length();
      expect(await store.appendSession(_session('f1', s.log.events, t)), isFalse);
      expect(await file.length(), sizeAfterFirst);
      final reopened = await FileLearnerStore.open(file);
      expect(await reopened.sessions(learnerId: 'L1'), hasLength(1));
    });

    test('xoá learner rồi ghi lại cùng sessionId ⇒ được nhận (không có tập id '
        'ma sau khi xoá)', () async {
      final store = JsonlLearnerStore();
      final t = DateTime(2026, 9, 5, 10);
      final s = _open(t)..submit('23/20');
      await store.appendSession(_session('again', s.log.events, t));
      await store.deleteLearner('L1');
      expect(await store.appendSession(_session('again', s.log.events, t)),
          isTrue,
          reason: 'xoá là xoá thật — không được để lại dấu vết chặn ghi');
    });
  });

  group('tương thích dữ liệu cũ', () {
    const oldLine = '{"type":"session","sessionId":"s-L1-1756800000000000",'
        '"learnerId":"L1","subjectId":"toan",'
        '"startedAt":"2026-09-01T19:00:00.000","trigger":"cameraHomework",'
        '"events":[{"eventId":"cur:05-sgk-toan-5-tap-mot:p20:b6#0",'
        '"skillCaseId":"denominator-non-divisible","kind":"independentAttempt",'
        '"at":"2026-09-01T19:00:00.000","correct":true,"support":"none",'
        '"policyId":"tutor-session-v1"},'
        '{"eventId":"cur:05-sgk-toan-5-tap-mot:p20:b6#1",'
        '"skillCaseId":"denominator-non-divisible","kind":"finalCorrectness",'
        '"at":"2026-09-01T19:00:01.000","correct":true}]}';

    test('⭐ phiên cũ (id `…#0`, không token) vẫn nạp và replay đúng', () async {
      final store = JsonlLearnerStore.fromJsonl(oldLine);
      final s = (await store.sessions(learnerId: 'L1')).single;
      expect(s.events.map((e) => e.eventId),
          ['cur:05-sgk-toan-5-tap-mot:p20:b6#0', 'cur:05-sgk-toan-5-tap-mot:p20:b6#1'],
          reason: 'không viết lại id cũ — log là append-only');
      final log = await store.evidenceFor(
          learnerId: 'L1', skillCaseId: 'denominator-non-divisible');
      expect(replayMastery(log, BktParams.freeResponse).independentCorrect, 1);
    });

    test('phiên cũ ghi lại cùng sessionId ⇒ no-op (idempotent theo id phiên, '
        'không theo dạng id sự kiện)', () async {
      final store = JsonlLearnerStore.fromJsonl(oldLine);
      final s = (await store.sessions(learnerId: 'L1')).single;
      expect(await store.appendSession(s), isFalse);
      expect(store.toJsonl().split('\n'), hasLength(1));
    });

    test('phiên MỚI (id có token) và phiên CŨ cùng bài chung sống, không trùng',
        () async {
      final store = JsonlLearnerStore.fromJsonl(oldLine);
      final t = DateTime(2026, 9, 5, 10);
      final s = _open(t)..submit('23/20');
      expect(await store.appendSession(_session('new', s.log.events, t)), isTrue);
      final log = await store.evidenceFor(
          learnerId: 'L1', skillCaseId: 'denominator-non-divisible');
      expect(log.events.map((e) => e.eventId).toSet(), hasLength(4));
    });
  });
}
