/// WAL-114 — LINEAGE end-to-end: từ 1 LearningEvent về ĐÚNG TRANG SÁCH,
/// và 5 điều kiện fail-closed — mỗi bất biến một đột biến làm đỏ (reason).
library;

import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/curriculum/pedagogical_boundary.dart';
import 'package:learning_coach/core/knowledge/lineage.dart';
import 'package:learning_coach/core/knowledge/provenance.dart';
import 'package:learning_coach/core/knowledge/slice_curriculum.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learning_session.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/mastery.dart';

void main() {
  final c = curriculumFor(
      const LearnerProfile(learnerId: 'l', displayName: 'M', grade: 5))!;
  final scope = TutorScope.forProblem(
      'quy-dong', 'denominator-non-divisible', c.stage, c.catalogue);

  LearningEvent ev(String? iid, {String caseId = 'denominator-non-divisible'}) =>
      LearningEvent(
        eventId: 'e1',
        skillCaseId: caseId,
        kind: EvidenceKind.postHintSuccess,
        correct: true,
        at: DateTime(2026, 9, 2, 20),
        support: SupportLevel.hint,
        policyId: 'tutor-session-v1',
        interventionId: iid,
        knowledgeVersion: knowledgeModelVersion,
      );

  test('⭐ HAPPY PATH: 1 evidence → đúng trang SGK nguồn + đủ 7 chiều', () {
    final r = lineageFor(
        e: ev('tutor-session-v1/common-denom-by-product@hint'),
        catalogue: c.catalogue,
        scope: scope);
    expect(r.proven, isTrue, reason: 'lineage phải chứng minh được');
    final t = r.trace!;
    final j = t.toJson();
    // SOURCE: đúng sách + đúng TRANG IN (đột biến đổi pageStart/pdf ⇒ đỏ)
    final src = j['source'] as Map;
    expect(src['sourceDocumentId'], '05-sgk-toan-5-tap-mot');
    expect(src['pagePrinted'], 21,
        reason: '⚠️ trang IN trên sách — nhầm hệ quy chiếu là trích sai trang');
    // AUTHORITY: dạy-qua-ví-dụ ⇒ DEMONSTRATED, KHÔNG được thăng lên EXPLICIT
    expect(t.authority, TeachingAuthority.sourceDemonstrated,
        reason: '⭐ đột biến authorityFor demonstrated→explicit ⇒ test đỏ');
    expect((j['sourceLineForChild'] as String).contains('làm theo ví dụ'),
        isTrue, reason: 'render đúng LOẠI hỗ trợ nguồn (ca B57)');
    expect((j['sourceLineForChild'] as String).contains('sách nói'), isFalse);
    // PERMISSION + VERSIONS
    expect((j['permission'] as Map)['supportLevel'], 'hint');
    final v = j['versions'] as Map;
    expect(v['tutorPolicy'], 'tutor-session-v1');
    expect(v['knowledgeModel'], knowledgeModelVersion,
        reason: 'cả HAI version phải trong trace (§acceptance)');
    // In trace end-to-end làm EVIDENCE (đọc được trong test output)
    // ignore: avoid_print
    print('LINEAGE TRACE:\n${const JsonEncoder.withIndent('  ').convert(j)}');
  });

  test('fail-closed 0: sự kiện không can thiệp ⇒ noTeachingIntervention', () {
    final r = lineageFor(e: ev(null), catalogue: c.catalogue, scope: scope);
    expect(r.violation, LineageViolation.noTeachingIntervention);
  });

  test('⭐ fail-closed 1 (provenance mismatch): method không tồn tại', () {
    final r = lineageFor(
        e: ev('tutor-session-v1/bcnn-magic@hint'),
        catalogue: c.catalogue,
        scope: scope);
    expect(r.violation, LineageViolation.methodUnknown,
        reason: 'dữ liệu trỏ method ma ⇒ KHÔNG kể chuyện nguồn');
  });

  test('⭐ fail-closed 2: method ngoài APPLICABLE∩ALLOWED ⇒ methodNotAllowed',
      () {
    // scope của ca CHIA-HẾT — by-product (ca không-chia-hết) không được phép.
    final scopeDiv = TutorScope.forProblem(
        'quy-dong', 'denominator-divisible', c.stage, c.catalogue);
    final r = lineageFor(
        e: ev('tutor-session-v1/common-denom-by-product@hint',
            caseId: 'denominator-divisible'),
        catalogue: c.catalogue,
        scope: scopeDiv);
    expect(r.violation, LineageViolation.methodNotAllowed);
  });

  test('⭐ fail-closed 3: method KHÔNG khai nguồn ⇒ missingSource', () {
    const noSrc = TeachingMethod(
      id: 'm-tay-khong',
      name: 'Cách không nguồn',
      appliesToConcepts: {'quy-dong'},
      skillCaseId: 'denominator-non-divisible',
      requiresConcepts: {},
      requiresTerminology: {},
    );
    final r = lineageFor(
        e: ev('tutor-session-v1/m-tay-khong@hint'),
        catalogue: [...c.catalogue, noSrc],
        scope: scope);
    expect(r.violation, LineageViolation.missingSource,
        reason: 'không nguồn thì không có gì để trích — im, không bịa');
  });

  test('⭐ fail-closed 4: nguồn lớp 6 trong stage lớp 5 ⇒ futureKnowledge', () {
    const g6 = TeachingMethod(
      id: 'm-bcnn-g6',
      name: 'BCNN (lớp 6)',
      appliesToConcepts: {'quy-dong'},
      skillCaseId: 'denominator-non-divisible',
      requiresConcepts: {},
      requiresTerminology: {},
      provenance: Provenance(
        origin: KnowledgeOrigin.sourceStated,
        sourceId: '06-sgk-toan-6-tap-mot',
        extractionMethod: 'rule-method-v1',
        confidence: 0.9,
        grade: 6,
        pageStart: 30,
      ),
    );
    final r = lineageFor(
        e: ev('tutor-session-v1/m-bcnn-g6@hint'),
        catalogue: [...c.catalogue, g6],
        scope: scope);
    expect(r.violation, LineageViolation.futureKnowledge,
        reason: '«BCNN không thể xuất hiện ở Math5 B6» — cả lúc TRUY VẤN');
  });

  test('⭐ fail-closed 5: scope hỏng trỏ method sai concept ⇒ curriculumConflict',
      () {
    const alien = TeachingMethod(
      id: 'm-doc-hieu',
      name: 'Phương pháp môn khác',
      appliesToConcepts: {'doc-hieu'},
      skillCaseId: 'denominator-non-divisible',
      requiresConcepts: {},
      requiresTerminology: {},
      provenance: Provenance(
        origin: KnowledgeOrigin.sourceStated,
        sourceId: '05-sgk-tieng-viet-5-tap-mot',
        extractionMethod: 'rule-method-v1',
        confidence: 0.9,
        grade: 5,
        pageStart: 10,
      ),
    );
    // mô phỏng scope LƯU bị hỏng (bypass builder) — lineage phải tự bắt.
    final broken = TutorScope(
      targetConcept: 'quy-dong',
      allowedMethods: const [alien],
      allowedTerminology: const {},
      prerequisiteScope: const {},
      stage: c.stage,
    );
    final r = lineageFor(
        e: ev('tutor-session-v1/m-doc-hieu@hint'),
        catalogue: const [alien],
        scope: broken);
    expect(r.violation, LineageViolation.curriculumConflict);
  });

  test('authority mapping: sequence/system/llm/null ⇒ SAM_INFERRED (không thăng quyền)',
      () {
    expect(authorityFor(KnowledgeOrigin.sourceStated),
        TeachingAuthority.sourceExplicit);
    expect(authorityFor(KnowledgeOrigin.sourceDemonstrated),
        TeachingAuthority.sourceDemonstrated);
    for (final o in [
      KnowledgeOrigin.sourceSequence,
      KnowledgeOrigin.systemDerived,
      KnowledgeOrigin.llmInferred,
      null,
    ]) {
      expect(authorityFor(o), TeachingAuthority.samInferred,
          reason: 'mục lục/suy luận KHÔNG phải lời sách — $o');
    }
  });

  test('⭐ knowledgeVersion sống qua LƯU-ĐỌC (JSONL round-trip)', () {
    final s = LearningSession(
      sessionId: 's1',
      learnerId: 'l',
      subjectId: 'toan',
      startedAt: DateTime(2026, 9, 2, 20),
      trigger: SessionTrigger.manual,
      events: [ev('tutor-session-v1/common-denom-by-product@hint')],
    );
    final back = LearningSession.fromJson(
        jsonDecode(jsonEncode(s.toJson())) as Map<String, Object?>)!;
    expect(back.events.single.knowledgeVersion, knowledgeModelVersion,
        reason: 'đột biến bỏ serialize knowledgeVersion ⇒ test đỏ');
    expect(back.events.single.policyId, 'tutor-session-v1');
  });
}
