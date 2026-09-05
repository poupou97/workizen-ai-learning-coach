/// ⭐⭐ WAL-210 round 3 (A-runtime) — Founder A6 SEMANTIC BINDING (bounded to
/// Bài 17): binding giải được cho Bài 17; rỗng cho mọi bài khác; không
/// phương pháp nào được phép mà không có nguồn NÓI THẲNG (RETRIEVED ≠
/// PERMITTED áp cho binding). Sổ đăng ký đúng MỘT mục — không K-12.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/context/learning_context.dart';
import 'package:learning_coach/core/curriculum/khtn6_bai17.dart';
import 'package:learning_coach/core/curriculum/pedagogical_boundary.dart';
import 'package:learning_coach/core/curriculum/semantic_binding.dart';
import 'package:learning_coach/core/curriculum/semantic_binding_registry.dart';
import 'package:learning_coach/core/knowledge/provenance.dart';
import 'package:learning_coach/core/knowledge/slice_curriculum.dart';
import 'package:learning_coach/core/store/learner_profile.dart';

TeachingMethod _method({Provenance? provenance, String? skillCaseId}) =>
    TeachingMethod(
      id: khtn6TachChatMethodId,
      name: 'x',
      appliesToConcepts: {khtn6TachChatConceptId},
      skillCaseId: skillCaseId ?? khtn6ChonCachTachCaseId,
      requiresConcepts: const {},
      requiresTerminology: const {},
      provenance: provenance,
    );

BindingCurriculum _cur(TeachingMethod m) => BindingCurriculum(
    conceptId: khtn6TachChatConceptId,
    cases: khtn6Bai17Curriculum.cases,
    stage: khtn6Bai17Stage,
    catalogue: [m]);

void main() {
  group('sổ đăng ký — đúng MỘT binding, PROPOSED', () {
    test('⭐ chỉ Bài 17; status PROPOSED; activity = kịch bản Học với SAM', () {
      expect(SemanticBindingRegistry.bindings, hasLength(1));
      final b = SemanticBindingRegistry.bindings.single;
      expect(b.lessonRef, khtn6Bai17);
      expect(b.status, 'PROPOSED');
      expect(b.activityId, SemanticBinding.tutorScriptActivity);
      expect(b.bindingSource, BindingSource.curated);
      expect(b.provenance.basis, contains('tc2-p1'));
    });

    test('⭐⭐ giải được cho Bài 17: scope + đúng MỘT phương pháp sourceStated',
        () {
      final r = SemanticBindingRegistry.resolveFor(
          khtn6Bai17, SemanticBinding.tutorScriptActivity)!;
      expect(r.hasScope, isTrue);
      expect(r.scope!.targetConcept, khtn6TachChatConceptId);
      expect(r.allowedMethods.map((m) => m.id), [khtn6TachChatMethodId]);
      expect(r.allowedMethods.single.provenance!.origin, KnowledgeOrigin.sourceStated);
      expect(r.allowedMethods.single.provenance!.pageStart, 63);
      expect(r.allowedMethods.single.provenance!.citableAsTextbookFact, isTrue);
      expect(r.refusals, isEmpty);
      expect(r.allowedMethods.single.hints, isNull,
          reason: 'không có SGV/khoá đáp án ⇒ không bịa lời dạy');
    });

    test('⭐⭐ bài khác / sách khác / hoạt động khác ⇒ rỗng, không mượn', () {
      const b16 = LessonRef('06-sgk-khoa-hoc-tu-nhien-6', 16);
      const toan5 = LessonRef('05-sgk-toan-5-tap-mot', 6);
      expect(SemanticBindingRegistry.bindingsFor(b16), isEmpty);
      expect(SemanticBindingRegistry.bindingsFor(toan5), isEmpty);
      expect(SemanticBindingRegistry.resolveFor(b16, SemanticBinding.tutorScriptActivity), isNull);
      expect(SemanticBindingRegistry.resolveFor(khtn6Bai17, 'visual:process-1'), isNull);
      expect(SemanticBindingRegistry.curriculumFor(b16), isNull);
    });

    test('⭐ curriculum tối thiểu Bài 17 KHÔNG lọt vào đường chụp bài (Toán 5)',
        () {
      const p6 = LearnerProfile(learnerId: 'x', displayName: 'x', grade: 6);
      expect(curriculaForLearner(p6), isEmpty,
          reason: 'BindingCurriculum không đăng ký vào _curriculumByLesson');
      expect(curriculumForProblem(p6, 'Làm muối từ nước biển'), isNull);
    });
  });

  group('RETRIEVED ≠ PERMITTED — không phương pháp nào không có nguồn nói thẳng',
      () {
    test('⭐⭐ provenance sourceDemonstrated ⇒ loại (METHOD_NOT_SOURCE_STATED); '
        'scope vẫn có (act không cần phương pháp vẫn chạy)', () {
      final r = resolveBinding(
          khtn6Bai17TutorBinding,
          _cur(_method(
              provenance: const Provenance(
                  origin: KnowledgeOrigin.sourceDemonstrated,
                  sourceId: 's',
                  extractionMethod: 't',
                  confidence: 0.9,
                  pageStart: 63))));
      expect(r.hasScope, isTrue);
      expect(r.allowedMethods, isEmpty);
      expect(r.refusals, contains('METHOD_NOT_SOURCE_STATED:$khtn6TachChatMethodId'));
      expect(r.permitsContent, isFalse);
    });

    test('⭐⭐ không provenance ⇒ loại; sourceStated nhưng KHÔNG có trang ⇒ loại',
        () {
      expect(
          resolveBinding(khtn6Bai17TutorBinding, _cur(_method())).refusals,
          contains('METHOD_NOT_SOURCE_STATED:$khtn6TachChatMethodId'));
      final noPage = resolveBinding(
          khtn6Bai17TutorBinding,
          _cur(_method(
              provenance: const Provenance(
                  origin: KnowledgeOrigin.sourceStated,
                  sourceId: 's',
                  extractionMethod: 't',
                  confidence: 0.9))));
      expect(noPage.allowedMethods, isEmpty);
      expect(noPage.refusals, contains('METHOD_NOT_SOURCE_STATED:$khtn6TachChatMethodId'));
    });

    test('⭐ phương pháp KHÔNG khai trong binding ⇒ loại dù scope cho phép', () {
      const undeclared = SemanticBinding(
          activityId: SemanticBinding.tutorScriptActivity,
          lessonRef: khtn6Bai17,
          conceptId: khtn6TachChatConceptId,
          skillCaseId: khtn6ChonCachTachCaseId,
          methodIds: [],
          bindingSource: BindingSource.curated,
          confidence: 0.5,
          provenance: BindingProvenance(curatedBy: 't', basis: 't'));
      final r = resolveBinding(undeclared, khtn6Bai17Curriculum);
      expect(r.allowedMethods, isEmpty);
      expect(r.refusals, contains('METHOD_NOT_DECLARED_IN_BINDING:$khtn6TachChatMethodId'));
    });

    test('⭐ phương pháp khai ca KHÁC ⇒ ngoài scope (F2 gating giữ nguyên)', () {
      final r = resolveBinding(
          khtn6Bai17TutorBinding,
          _cur(_method(
              skillCaseId: 'ca-khac',
              provenance: khtn6TachChatTheoTinhChat.provenance)));
      expect(r.allowedMethods, isEmpty);
      expect(r.refusals, contains('METHOD_NOT_IN_SCOPE:$khtn6TachChatMethodId'));
    });

    test('⭐ không curriculum / lệch khái niệm / không ca ⇒ fail closed có lý do',
        () {
      expect(resolveBinding(khtn6Bai17TutorBinding, null).refusals, ['NO_CURRICULUM']);
      expect(resolveBinding(khtn6Bai17TutorBinding, null).hasScope, isFalse);
      const noConcept = SemanticBinding(
          activityId: 'a',
          lessonRef: khtn6Bai17,
          methodIds: [],
          bindingSource: BindingSource.fixture,
          confidence: 0.1,
          provenance: BindingProvenance(curatedBy: 't', basis: 't'));
      expect(resolveBinding(noConcept, khtn6Bai17Curriculum).refusals, ['NO_CONCEPT']);
      const noCase = SemanticBinding(
          activityId: 'a',
          lessonRef: khtn6Bai17,
          conceptId: khtn6TachChatConceptId,
          methodIds: [khtn6TachChatMethodId],
          bindingSource: BindingSource.fixture,
          confidence: 0.1,
          provenance: BindingProvenance(curatedBy: 't', basis: 't'));
      final r = resolveBinding(noCase, khtn6Bai17Curriculum);
      expect(r.refusals, contains('NO_SKILL_CASE'));
      expect(r.allowedMethods, isEmpty, reason: 'ca null ⇒ TutorScope rỗng');
    });
  });

  test('LessonRef.fromContext: chỉ khi context đã giải ra bài (A5 cùng luật)', () {
    expect(LessonRef.fromContext(null), isNull);
    expect(LessonRef.fromContext(const LearningContext(learnerId: 'l', grade: 6)), isNull);
    expect(
        LessonRef.fromContext(const LearningContext(
            learnerId: 'l', grade: 6, sourceDocumentId: '06-sgk-khoa-hoc-tu-nhien-6')),
        isNull);
    expect(
        LessonRef.fromContext(const LearningContext(
            learnerId: 'l',
            grade: 6,
            sourceDocumentId: '06-sgk-khoa-hoc-tu-nhien-6',
            lessonNo: 17)),
        khtn6Bai17);
  });
}
