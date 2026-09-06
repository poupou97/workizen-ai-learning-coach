/// ⭐⭐ WAL-183 — KnowledgeStateScreen: icon 🚀/🌱/🎯 gắn ĐÚNG lên tile
/// SkillCase đã có, không màn hình mới, không hệ tính riêng ngoài mastery
/// đã có.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/core/store/learning_session.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/evidence_validation.dart';
import 'package:learning_coach/features/learning_session/slice_flow.dart';

import '../../support/curriculum.dart';

const _p5 = LearnerProfile(learnerId: 'l-5', displayName: 'Minh', grade: 5);

Future<JsonlLearnerStore> _storeWith(List<LearningEvent> events) async {
  final store = JsonlLearnerStore();
  if (events.isNotEmpty) {
    await store.appendSession(LearningSession(
      sessionId: 's1',
      learnerId: _p5.learnerId,
      subjectId: 'toan',
      startedAt: DateTime(2026, 9, 4),
      trigger: SessionTrigger.manual,
      events: events,
    ));
  }
  return store;
}

LearningEvent _correct(String id, DateTime at) => LearningEvent(
    eventId: id,
    skillCaseId: 'denominator-non-divisible',
    kind: EvidenceKind.independentAttempt,
    correct: true,
    validation: _r4Stamp,
    at: at);

/// ROUND 4 (A-runtime, Founder §4 — strict validation default): the graded
/// events this test seeds simulate the Deep path (TutorSession), which has
/// stamped `fraction-check-v1` since round 3; unstamped graded events now read
/// as `historicalUnvalidated` and never as «Tự làm được». Fixture-only change,
/// no assertion changed. — lane A-runtime touched this Lane B test file.
const _r4Stamp =
    EvidenceValidation(validatorId: 'fraction-check-v1', validatorVersion: '1');

void main() {
  testWidgets('⭐ chưa có bằng chứng ⇒ không icon 🌱/🎯/🚀 nào trên tile',
      (t) async {
    final store = await _storeWith(const []);
    await t.pumpWidget(MaterialApp(
        home: KnowledgeStateScreen(
            profile: _p5, store: store, curriculum: toan5Bai6)));
    await t.pumpAndSettle();
    for (final icon in ['🌱', '🎯', '🚀']) {
      expect(find.textContaining(icon), findsNothing,
          reason: 'UNKNOWN không được mặc định bất kỳ tín hiệu nào ($icon)');
    }
  });

  testWidgets(
      '⭐⭐ nhiều lần tự làm đúng liên tiếp ⇒ 🚀 hiện ĐÚNG tile dạng đó, '
      'tái dùng mastery đã có (không hệ tính riêng)', (t) async {
    final at = DateTime(2026, 9, 4);
    final store = await _storeWith([
      for (var i = 0; i < 6; i++) _correct('e$i', at.add(Duration(minutes: i))),
    ]);
    await t.pumpWidget(MaterialApp(
        home: KnowledgeStateScreen(
            profile: _p5, store: store, curriculum: toan5Bai6)));
    await t.pumpAndSettle();
    expect(find.textContaining('🚀'), findsOneWidget,
        reason: '⭐⭐ đột biến bỏ wiring challenge_policy ⇒ đỏ');
    expect(find.textContaining('con tự làm được rồi'), findsOneWidget,
        reason: 'câu chữ mastery cũ vẫn giữ nguyên — chỉ THÊM icon, không '
            'thay luật cũ');
  });
}
