/// ⭐⭐ WAL-210 round 3 (A-runtime) — Founder A4 EVIDENCE INTEGRITY, trên nền
/// #60 (id duy nhất + `appendSession` idempotent):
///
/// - Dòng cuối VỠ (torn write) không làm mất các phiên đã ghi TRƯỚC — kể cả
///   sau khi kho ghi lại cả tệp (whole-file rewrite của `FileLearnerStore`).
/// - MỞ LẠI app + THỬ LẠI ghi cùng phiên ⇒ không đếm kép (mastery, số phiên,
///   số sự kiện) — qua đĩa, không chỉ trong RAM.
/// - MỞ LẠI cùng bài ⇒ phiên MỚI được ĐẾM (không có dedupe im lặng nào nuốt
///   lần làm thứ hai).
/// - Dấu validator (A3) sống qua đĩa.
///
/// Đây là test HỒI QUY cho hành vi hôm nay (ghi lại cả tệp, không hash) —
/// KHÔNG đổi cách lưu; các phương án bền hơn nằm ở
/// docs/architecture/EVIDENCE-DURABILITY-AND-INTEGRITY-OPTIONS.md (research).
library;

import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/curriculum/pedagogical_boundary.dart';
import 'package:learning_coach/core/knowledge/slice_curriculum.dart';
import 'package:learning_coach/core/store/file_store.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learning_session.dart';
import 'package:learning_coach/core/student/evidence_weighting.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/features/tutor/tutor_session.dart';

const _profile = LearnerProfile(learnerId: 'L1', displayName: 'A', grade: 5);
const _exercise = 'cur:05-sgk-toan-5-tap-mot:p20:b6';
const _case = 'denominator-non-divisible';

TutorSession _open(DateTime at) {
  final c = curriculumForProblem(_profile, '3/4 + 2/5')!;
  return TutorSession(
    exerciseId: _exercise,
    skillCaseId: _case,
    problem: FractionProblem.parse('3/4 + 2/5')!,
    scope: TutorScope.forProblem(
        c.conceptId, c.classifyCase('3/4 + 2/5'), c.stage, c.catalogue),
    now: () => at,
  );
}

LearningSession _session(String id, List<LearningEvent> events, DateTime at) =>
    LearningSession(
      sessionId: id,
      learnerId: 'L1',
      subjectId: 'toan',
      startedAt: at,
      trigger: SessionTrigger.cameraHomework,
      events: events,
    );

void main() {
  late Directory dir;
  File f() => File('${dir.path}/store.jsonl');

  setUp(() async {
    dir = await Directory.systemTemp.createTemp('wal-210-a4-');
  });
  tearDown(() => dir.delete(recursive: true));

  test('⭐⭐ torn last line: hai phiên đã ghi trước còn nguyên; ghi tiếp được; '
      'sau rewrite cả tệp vẫn còn đủ', () async {
    final s1 = await FileLearnerStore.open(f());
    await s1.saveProfile(_profile);
    final t1 = DateTime(2026, 9, 5, 10), t2 = DateTime(2026, 9, 5, 11);
    await s1.appendSession(_session('a', (_open(t1)..submit('23/20')).log.events, t1));
    await s1.appendSession(_session('b', (_open(t2)..submit('23/20')).log.events, t2));
    // Ghi hỏng giữa chừng: dòng thứ ba chỉ có nửa JSON.
    await f().writeAsString('\n{"type":"session","sessionId":"c","learnerId":"L1"',
        mode: FileMode.append);

    final s2 = await FileLearnerStore.open(f());
    expect((await s2.sessions(learnerId: 'L1')).map((s) => s.sessionId), ['a', 'b'],
        reason: 'dòng vỡ không được kéo theo dòng lành');
    // Ghi tiếp ⇒ cả tệp được ghi lại; hai phiên cũ vẫn phải còn.
    final t3 = DateTime(2026, 9, 5, 12);
    expect(await s2.appendSession(_session('d', (_open(t3)..submit('23/20')).log.events, t3)),
        isTrue);
    final s3 = await FileLearnerStore.open(f());
    expect((await s3.sessions(learnerId: 'L1')).map((s) => s.sessionId), ['a', 'b', 'd']);
    final log = await s3.evidenceFor(learnerId: 'L1', skillCaseId: _case);
    expect(log.events, hasLength(6));
    expect(replayMastery(log, BktParams.freeResponse).evidenceCount, 3);
  });

  test('⭐⭐ mở lại + thử lại cùng phiên ⇒ không đếm kép qua đĩa (mastery, '
      'số phiên, số sự kiện)', () async {
    final t = DateTime(2026, 9, 5, 10);
    final sess = _session('retry', (_open(t)..submit('23/20')).log.events, t);
    final s1 = await FileLearnerStore.open(f());
    expect(await s1.appendSession(sess), isTrue);
    // «Khởi động lại» rồi callback bắn lại cùng phiên.
    final s2 = await FileLearnerStore.open(f());
    expect(await s2.appendSession(sess), isFalse);
    // Lần nữa, sau khi mở lại lần nữa.
    final s3 = await FileLearnerStore.open(f());
    expect(await s3.appendSession(sess), isFalse);
    expect(await s3.sessions(learnerId: 'L1'), hasLength(1));
    final log = await s3.evidenceFor(learnerId: 'L1', skillCaseId: _case);
    expect(log.events, hasLength(2));
    expect(replayMastery(log, BktParams.freeResponse).evidenceCount, 1);
    expect(f().readAsLinesSync().where((l) => l.contains('"retry"')), hasLength(1),
        reason: 'đúng MỘT dòng cho phiên này trên đĩa');
  });

  test('⭐ mở lại CÙNG BÀI (phiên mới, token mới) ⇒ phiên thứ hai ĐƯỢC ĐẾM',
      () async {
    final t = DateTime(2026, 9, 5, 10);
    final s1 = await FileLearnerStore.open(f());
    await s1.appendSession(_session('first', (_open(t)..submit('23/20')).log.events, t));
    final s2 = await FileLearnerStore.open(f());
    await s2.appendSession(_session('second', (_open(t)..submit('23/20')).log.events, t));
    final s3 = await FileLearnerStore.open(f());
    final log = await s3.evidenceFor(learnerId: 'L1', skillCaseId: _case);
    expect(log.events.map((e) => e.eventId).toSet(), hasLength(4),
        reason: 'id duy nhất KHÔNG được trở thành cớ dedupe lần làm thứ hai');
    expect(replayMastery(log, BktParams.freeResponse).evidenceCount, 2);
  });

  test('⭐ A3: dấu validator sống qua đĩa', () async {
    final t = DateTime(2026, 9, 5, 10);
    final s1 = await FileLearnerStore.open(f());
    await s1.appendSession(_session('v', (_open(t)..submit('23/20')).log.events, t));
    final s2 = await FileLearnerStore.open(f());
    final log = await s2.evidenceFor(learnerId: 'L1', skillCaseId: _case);
    for (final e in log.events) {
      expect(e.validation?.validatorId, 'fraction-check-v1', reason: e.eventId);
    }
  });
}
