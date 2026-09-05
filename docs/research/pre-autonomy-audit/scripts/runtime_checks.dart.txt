// Pre-autonomy audit (Layer C) — small read-only runtime checks against the
// real domain code. Run from repo root: `dart run poc-out/audit/pre-autonomy/scripts/runtime_checks.dart`
// Nothing is written; no app code is modified.
import 'package:learning_coach/core/context/learning_context.dart';
import 'package:learning_coach/core/curriculum/fraction_problem.dart';
import 'package:learning_coach/core/intent/learning_intent.dart';
import 'package:learning_coach/core/knowledge/slice_curriculum.dart';
import 'package:learning_coach/core/pedagogy/pedagogy_model.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/core/store/learning_session.dart';
import 'package:learning_coach/core/student/evidence_validator.dart';
import 'package:learning_coach/core/student/evidence_weighting.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/learning_map_state.dart';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/core/tutor/learning_activity.dart';
import 'package:learning_coach/core/tutor/teaching_provenance.dart';
import 'package:learning_coach/core/tutor/tutor_prompt.dart';
import 'package:learning_coach/core/curriculum/pedagogical_boundary.dart';
import 'package:learning_coach/features/tutor/tutor_session.dart';

void check(String name, bool ok, String detail) {
  print('${ok ? "PASS" : "FAIL"}  $name — $detail');
}

Future<void> main() async {
  final profile = const LearnerProfile(learnerId: 'L1', displayName: 'A', grade: 5);
  final c = curriculumForProblem(profile, '3/4 + 2/5')!;
  final fp = FractionProblem.parse('3/4 + 2/5')!;
  final scope = TutorScope.forProblem(
      c.conceptId, c.classifyCase('3/4 + 2/5'), c.stage, c.catalogue);

  // C1. eventId uniqueness across two TutorSessions on the SAME exercise id
  //     (re-opening the same textbook exercise = same CanonicalProblem.exerciseId).
  final s1 = TutorSession(exerciseId: 'cur:05-sgk-toan-5-tap-mot:p20:b6', skillCaseId: 'denominator-non-divisible', problem: fp, scope: scope, now: () => DateTime(2026, 9, 5, 10));
  s1.submit('23/20');
  final s2 = TutorSession(exerciseId: 'cur:05-sgk-toan-5-tap-mot:p20:b6', skillCaseId: 'denominator-non-divisible', problem: fp, scope: scope, now: () => DateTime(2026, 9, 5, 11));
  s2.submit('23/20');
  final ids1 = s1.log.events.map((e) => e.eventId).toSet();
  final ids2 = s2.log.events.map((e) => e.eventId).toSet();
  check('C1 TutorSession eventId unique across re-open of same exercise',
      ids1.intersection(ids2).isEmpty,
      'session1=$ids1 session2=$ids2 overlap=${ids1.intersection(ids2)}');

  // C2. Store: does evidenceFor() dedupe by eventId?  (both sessions appended)
  final store = JsonlLearnerStore();
  await store.saveProfile(profile);
  await store.appendSession(LearningSession(sessionId: 's1', learnerId: 'L1', subjectId: 'toan', startedAt: DateTime(2026, 9, 5, 10), trigger: SessionTrigger.manual, events: s1.log.events));
  await store.appendSession(LearningSession(sessionId: 's2', learnerId: 'L1', subjectId: 'toan', startedAt: DateTime(2026, 9, 5, 11), trigger: SessionTrigger.manual, events: s2.log.events));
  final log = await store.evidenceFor(learnerId: 'L1', skillCaseId: 'denominator-non-divisible');
  check('C2 evidenceFor keeps BOTH sessions\' events (no silent dedupe)',
      log.events.length == s1.log.events.length + s2.log.events.length,
      'events replayed=${log.events.length} (expected ${s1.log.events.length + s2.log.events.length}); distinct eventIds=${log.events.map((e) => e.eventId).toSet().length}');

  // C3. Same session appended TWICE (e.g. onFinished fired twice / re-open) → double counting?
  final store2 = JsonlLearnerStore();
  final sess = LearningSession(sessionId: 'dup', learnerId: 'L1', subjectId: 'toan', startedAt: DateTime(2026, 9, 5, 10), trigger: SessionTrigger.manual, events: s1.log.events);
  await store2.appendSession(sess);
  await store2.appendSession(sess);
  final log2 = await store2.evidenceFor(learnerId: 'L1', skillCaseId: 'denominator-non-divisible');
  final m2 = replayMastery(log2, BktParams.freeResponse);
  check('C3 identical session appended twice is NOT double-counted',
      log2.events.length == s1.log.events.length,
      'replayed=${log2.events.length} vs single=${s1.log.events.length}; evidenceCount after replay=${m2.evidenceCount}');

  // C4. Ungraded activity: gradable=false when correctOption null / out of range.
  const a1 = LearningActivity(activityId: 'x', prompt: 'p', response: ResponseKind.selectIdentify, conceptId: 'c', options: ['a', 'b']);
  const a2 = LearningActivity(activityId: 'x', prompt: 'p', response: ResponseKind.selectIdentify, conceptId: 'c', options: ['a', 'b'], correctOption: 5);
  check('C4 gradable=false when correctOption null', !a1.gradable, 'a1.gradable=${a1.gradable}');
  check('C4b gradable=false when correctOption out of range', !a2.gradable, 'a2.gradable=${a2.gradable}');
  check('C4c shortText resolves to unsupported (fail closed)', resolveSurface(const LearningActivity(activityId: 'y', prompt: 'p', response: ResponseKind.shortText, conceptId: 'c')) == SurfaceKind.unsupported, '');

  // C5. Unknown case / unknown method → empty scope / null prompt / null provenance.
  final emptyScope = TutorScope.forProblem('quy-dong', null, c.stage, c.catalogue);
  check('C5 unknown case ⇒ allowedMethods empty', emptyScope.allowedMethods.isEmpty, 'n=${emptyScope.allowedMethods.length}');
  final tp = explainTeaching(scope: scope, methodId: 'bcnn-common-denominator', exerciseCase: 'denominator-non-divisible');
  check('C5b unknown/unpermitted methodId ⇒ explainTeaching null', tp == null, 'tp=$tp');
  final prompt = buildTutorPrompt(TutorPromptRequest(scope: scope, methodId: 'bcnn-common-denominator', exerciseCase: 'denominator-non-divisible', problemText: '3/4 + 2/5', grade: 5));
  check('C5c unpermitted method ⇒ buildTutorPrompt null', prompt == null, '');
  final hintOut = TutorSession(exerciseId: 'e', skillCaseId: 'denominator-equal', problem: FractionProblem.parse('3/5 + 1/5')!, scope: TutorScope.forProblem('quy-dong', 'denominator-equal', c.stage, c.catalogue)).requestHint();
  check('C5d hint on case with no permitted method ⇒ null (fail closed)', hintOut == null, 'hint=$hintOut');

  // C6. validateCandidateEvidence: kind is ALWAYS independentAttempt, even when support>none.
  final ctx = const LearningContext(learnerId: 'L1', grade: 5, subject: 'Khoa học', sourceDocumentId: '05-sgk-khoa-hoc-5', lessonNo: 3, intent: LearningIntent.review);
  final ev = validateCandidateEvidence(
      const CandidateEvidence(skillCaseId: 'khtn-thi-nghiem', learnerText: 'nước sôi', policyId: 'experiment-v1', support: SupportLevel.workedStep, act: TeachingAct.demonstrateStep),
      context: ctx, eventId: 'e#0', at: DateTime(2026, 9, 5));
  check('C6 validator with support=workedStep still mints kind=independentAttempt (latent mislabel)',
      ev?.kind == EvidenceKind.independentAttempt, 'kind=${ev?.kind} support=${ev?.support} correct=${ev?.correct}');
  final mapState = learningMapStateFor(sourceDocumentId: '05-sgk-khoa-hoc-5', lessonNo: 3, allEvents: [ev!]);
  check('C6b such an event shows as 🔵 "Tự làm được" on the Learning Map badge', mapState == LearningMapState.independentEvidence, 'state=$mapState');
  final lookupEv = validateCandidateEvidence(const CandidateEvidence(skillCaseId: 'k', learnerText: 'x', policyId: 'p'), context: const LearningContext(learnerId: 'L1', grade: 5, intent: LearningIntent.lookup), eventId: 'e', at: DateTime(2026));
  check('C6c lookup intent ⇒ no evidence', lookupEv == null, '');

  // C7. Reader-style event (no sourceDocumentId/lessonNo) is invisible to the Learning Map badge.
  final readerEv = LearningEvent(eventId: 'r#0', skillCaseId: 'tieng-viet-doc-hieu', kind: EvidenceKind.independentAttempt, correct: null, at: DateTime(2026, 9, 5), support: SupportLevel.none, policyId: 'reader-v1');
  check('C7 Reader/Compose/Source/Tutor events carry NO lineage ⇒ Learning Map badge stays unseen',
      learningMapStateFor(sourceDocumentId: '05-sgk-tieng-viet-5-tap-mot', lessonNo: 2, allEvents: [readerEv]) == LearningMapState.unseen, 'state=${learningMapStateFor(sourceDocumentId: '05-sgk-tieng-viet-5-tap-mot', lessonNo: 2, allEvents: [readerEv])}');

  // C8. Store scoping: evidence keyed by learnerId, not device.
  final other = await store.evidenceFor(learnerId: 'L2', skillCaseId: 'denominator-non-divisible');
  check('C8 evidence keyed by learnerId (L2 sees nothing of L1)', other.events.isEmpty, 'L2 events=${other.events.length}');

  // C9. Tamper: JSONL line edited by hand is accepted silently (no hash / signature).
  final jsonl = store.toJsonl().replaceAll('"correct":true', '"correct":false');
  final tampered = JsonlLearnerStore.fromJsonl(jsonl);
  final tlog = await tampered.evidenceFor(learnerId: 'L1', skillCaseId: 'denominator-non-divisible');
  check('C9 hand-edited JSONL (correct true→false) is replayed without detection',
      tlog.events.where((e) => e.correct == false).isNotEmpty, 'wrong-count after tamper=${tlog.events.where((e) => e.correct == false).length}');

  // C10. Deep path registrations
  print('INFO  SliceCurriculum registrations for grade 5 = ${curriculaForLearner(profile).length}; grade 6 = ${curriculaForLearner(profile.withGrade(6)).length}');
}
