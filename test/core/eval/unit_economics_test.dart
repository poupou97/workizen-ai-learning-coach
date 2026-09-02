/// WAL-115 — UNIT ECONOMICS instrumentation trên RUNTIME THẬT của slice.
///
/// MODE A (production hôm nay) phải là $0 LLM COGS **THEO CẤU TRÚC** — không
/// phải lời hứa: test quét import của lib/ và cấm mọi đường ra LLM/network
/// trong engine. Kèm đo ops tất định của MỘT phiên thật (số sự kiện + thời
/// gian CPU) — «deterministic ops/session» là số đo, không phỏng đoán.
library;

import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/adaptive/adaptive_engine.dart';
import 'package:learning_coach/core/curriculum/pedagogical_boundary.dart';
import 'package:learning_coach/core/knowledge/slice_curriculum.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/student/evidence_weighting.dart';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/features/tutor/tutor_session.dart';

void main() {
  test('⭐ MODE A THEO CẤU TRÚC: lib/ không có import LLM/network nào', () {
    final banned = [
      'package:http', 'package:dio', 'HttpClient', 'WebSocket',
      'anthropic', 'openai', 'claude -p', 'googleapis',
    ];
    final hits = <String>[];
    for (final f in Directory('lib')
        .listSync(recursive: true)
        .whereType<File>()
        .where((f) => f.path.endsWith('.dart'))) {
      final src = f.readAsStringSync();
      for (final b in banned) {
        if (src.contains(b)) hits.add('${f.path}: $b');
      }
    }
    expect(hits, isEmpty,
        reason: '⭐ đột biến thêm 1 import http vào engine ⇒ test này đỏ — '
            'Student Free MODE A đứng trên bất biến này');
  });

  test('đo ops tất định của MỘT phiên thật (sai→hint→đúng) — 0 LLM call', () {
    final c = curriculumFor(
        const LearnerProfile(learnerId: 'l', displayName: 'M', grade: 5))!;
    final fp = FractionProblem.parse('3/4 + 2/5')!;
    final ec = fractionCase(fp.b, fp.d)!;
    final sw = Stopwatch()..start();
    final s = TutorSession(
        exerciseId: 'ex-econ',
        skillCaseId: ec,
        problem: fp,
        scope: TutorScope.forProblem(c.conceptId, ec, c.stage, c.catalogue));
    s.submit('1/2');
    s.requestHint();
    s.submit('23/20');
    final m = replayMastery(s.log, BktParams.freeResponse);
    sw.stop();
    expect(m.evidenceCount, greaterThan(0));
    final nEvents = s.log.events.length;
    expect(nEvents, inInclusiveRange(3, 12),
        reason: 'hình phiên thật — neo cho tham số turns/session của model COGS');
    // Toàn phiên + replay chạy TẤT ĐỊNH trong ms-cỡ-đơn-vị trên máy dev —
    // trần rộng chống flake; ý nghĩa: chi phí MODE A là CPU cục bộ, không cloud.
    expect(sw.elapsedMilliseconds, lessThan(1000));
    // ignore: avoid_print
    print('ECON MODE A: events=$nEvents · engine+replay='
        '${sw.elapsedMicroseconds}µs · LLM calls=0 (cấu trúc)');
  });
}
