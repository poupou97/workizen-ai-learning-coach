/// ⭐⭐ WAL-210 round 3 (A-runtime) — Founder A7: PEDAGOGY RUNTIME cho lát cắt
/// vàng. «SAM TUTOR ≠ CHAT. LLM does not decide pedagogy. RETRIEVED ≠
/// PERMITTED. If a real capability is missing, keep the prototype clearly
/// marked rather than fake production capability.»
///
/// Chạy trên fixture MẪU Bài 17 (commit) — cùng kịch bản Track B đã đi trên
/// máy thật; kiểm: chế độ TỪNG BƯỚC đúng; act ngoài phương pháp được phép bị
/// từ chối; lời nói ngoài hợp đồng bị từ chối; không bước nào có validator;
/// không ký hiệu LLM / kho / mạng trong runtime.
library;

import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/context/learning_context.dart';
import 'package:learning_coach/core/curriculum/khtn6_bai17.dart';
import 'package:learning_coach/core/curriculum/pedagogical_boundary.dart';
import 'package:learning_coach/core/curriculum/semantic_binding.dart';
import 'package:learning_coach/core/curriculum/semantic_binding_registry.dart';
import 'package:learning_coach/core/intent/learning_intent.dart';
import 'package:learning_coach/core/knowledge/provenance.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/lesson_model/tutor_script.dart';
import 'package:learning_coach/core/pedagogy/pedagogy_model.dart';
import 'package:learning_coach/core/pedagogy/pedagogy_runtime.dart';
import 'package:learning_coach/core/student/student_lesson_state.dart';

const _fixture =
    'assets/fixtures/synthetic/lesson-06-sgk-khoa-hoc-tu-nhien-6-b17.synthetic.json';

LessonDocument _doc() {
  final j = jsonDecode(File(_fixture).readAsStringSync()) as Map;
  return LessonDocument.fromJson(j.cast<String, Object?>(), assetBase: 'x/')!;
}

const _ctx = LearningContext(
    learnerId: 'na',
    grade: 6,
    subject: 'KHTN',
    sourceDocumentId: '06-sgk-khoa-hoc-tu-nhien-6',
    lessonNo: 17,
    intent: LearningIntent.review);

String? _blockText(LessonDocument d, String id) => switch (d.blockById(id)) {
      ParagraphBlock(:final text) => text,
      QuestionBlock(:final text) => text,
      HeadingBlock(:final text) => text,
      ActivityBlock(:final text) => text,
      CaptionBlock(:final text) => text,
      _ => null,
    };

RuntimePlan _plan(LessonDocument d,
        {ResolvedBinding? binding, bool noBinding = false, LearningContext? ctx}) =>
    PedagogyRuntime.planForScript(
      script: d.tutorScript!,
      binding: noBinding
          ? null
          : binding ??
              SemanticBindingRegistry.resolveFor(
                  khtn6Bai17, SemanticBinding.tutorScriptActivity),
      studentState: StudentLessonState.unseen(khtn6Bai17),
      context: ctx ?? _ctx,
      blockText: (id) => _blockText(d, id),
    );

void main() {
  late LessonDocument doc;
  setUpAll(() => doc = _doc());

  group('Bài 17 (fixture mẫu) — chế độ TỪNG BƯỚC', () {
    test('⭐⭐ kế hoạch ràng buộc được; ask NGUYÊN VĂN câu sách + explain có '
        'block nguồn + next ⇒ runtimeGuided; hint/feedback/scaffold ⇒ prototype',
        () {
      final p = _plan(doc);
      expect(p.isBound, isTrue, reason: p.planRefusals.join(','));
      expect(p.binding!.permitsContent, isTrue,
          reason: 'phương pháp sourceStated («Em đã học», tr. 63) được phép');
      final byPhase = <PlannedStepPhase, List<PlannedStep>>{};
      for (final s in p.steps) {
        byPhase.putIfAbsent(s.phase, () => []).add(s);
      }
      expect(byPhase[PlannedStepPhase.explain]!.single.isRuntimeGuided, isTrue,
          reason: byPhase[PlannedStepPhase.explain]!.single.refusals.join(','));
      for (final a in byPhase[PlannedStepPhase.ask]!) {
        expect(a.isRuntimeGuided, isTrue, reason: '${a.stepId}: ${a.refusals}');
        expect(a.act.act, TeachingAct.diagnosticProbe);
        expect(a.act.methodId, isNull, reason: 'thăm dò không cần phương pháp');
      }
      expect(byPhase[PlannedStepPhase.next]!.single.isRuntimeGuided, isTrue);
      for (final h in byPhase[PlannedStepPhase.hint]!) {
        expect(h.mode, PlannedStepMode.prototypeScripted);
        expect(h.refusals, contains('HINT_UNSOURCED'));
      }
      for (final f in byPhase[PlannedStepPhase.feedbackMatched]!) {
        expect(f.mode, PlannedStepMode.prototypeScripted);
        expect(f.refusals, contains('KEY_NOT_VALIDATED'));
      }
      for (final sc in byPhase[PlannedStepPhase.scaffold]!) {
        expect(sc.mode, PlannedStepMode.prototypeScripted);
        expect(sc.refusals, containsAll(['KEY_NOT_VALIDATED', 'OVER_CAP_WITHOUT_VALIDATOR']));
        expect(sc.act.act, TeachingAct.revealAnswer);
      }
      expect(p.runtimeGuidedCount, 4, reason: 'e1 + q1 + q2 + n1');
      expect(p.prototypeCount, 8, reason: '2×(2 hint + feedback + scaffold)');
    });

    // Lịch sử: guard từng LỘ RA ba chỗ rò đáp án trong gợi ý prototype của
    // fixture mẫu (q1#1 nêu «Cô cạn»; q2#0/#1 nêu «nặng»). Lane B đã viết
    // lại ba gợi ý đó (round 3, tool/fixtures/make_synthetic_fixture.py) —
    // test này nay GHIM rằng không gợi ý nào còn rò; rò trở lại ⇒ đỏ.
    test('⭐ guard: KHÔNG gợi ý prototype nào còn rò đáp án (GUARD:REVEAL)',
        () {
      final p = _plan(doc);
      final leaks = p.steps
          .where((s) => s.phase == PlannedStepPhase.hint)
          .where((s) => s.refusals.any((r) => r.startsWith('GUARD:REVEAL')))
          .map((s) => '${s.stepId}#${s.hintIndex}')
          .toList();
      expect(leaks, isEmpty,
          reason: 'gợi ý phải scaffold mà không nêu dạng đáp án: $leaks');
      // …và vẫn là prototype (HINT_UNSOURCED), không giả năng lực.
      for (final h in p.steps.where((s) => s.phase == PlannedStepPhase.hint)) {
        expect(h.mode, PlannedStepMode.prototypeScripted);
      }
    });

    test('⭐⭐ không bước nào có validator ⇒ participation-only; runtime không '
        'sinh LearningEvent', () {
      final p = _plan(doc);
      expect(p.steps.every((s) => s.validator == null), isTrue);
      expect(p.evidencePolicy, PedagogyRuntime.participationOnly);
    });

    test('mỗi bước có act + rung nhất quán (act không nặng hơn rung) và chữ '
        'lấy NGUYÊN từ kịch bản', () {
      final p = _plan(doc);
      final scriptTexts = <String>{
        for (final s in doc.tutorScript!.steps)
          ...switch (s) {
            ExplainStep(:final text) => [text],
            AskStep(:final prompt, :final hints, :final feedbackMatched, :final scaffold) =>
              [prompt, ...hints, feedbackMatched, scaffold],
            NextStep(:final label) => [label],
          }
      };
      for (final s in p.steps) {
        expect(supportLevelOf(s.act.act).index <= rungToSupport(s.rung).index, isTrue,
            reason: '${s.stepId}/${s.phase.name}');
        expect(scriptTexts, contains(s.text), reason: 'runtime không viết chữ mới');
        expect(s.mode.childLabel, isNotEmpty);
      }
      expect(PlannedStepMode.runtimeGuided.samModeName, 'runtimeGuided');
      expect(PlannedStepMode.prototypeScripted.samModeName, 'prototypeScripted');
    });
  });

  group('FAIL CLOSED', () {
    test('⭐⭐ act ngoài phương pháp được phép bị từ chối: phương pháp KHÔNG '
        'sourceStated ⇒ explain/hint/scaffold prototype, ask vẫn chạy', () {
      final demonstrated = TeachingMethod(
        id: khtn6TachChatMethodId,
        name: khtn6TachChatTheoTinhChat.name,
        appliesToConcepts: khtn6TachChatTheoTinhChat.appliesToConcepts,
        skillCaseId: khtn6TachChatTheoTinhChat.skillCaseId,
        requiresConcepts: khtn6TachChatTheoTinhChat.requiresConcepts,
        requiresTerminology: khtn6TachChatTheoTinhChat.requiresTerminology,
        provenance: const Provenance(
            origin: KnowledgeOrigin.sourceDemonstrated,
            sourceId: '06-sgk-khoa-hoc-tu-nhien-6',
            extractionMethod: 'test',
            confidence: 0.9,
            pageStart: 63),
      );
      final cur = BindingCurriculum(
          conceptId: khtn6TachChatConceptId,
          cases: khtn6Bai17Curriculum.cases,
          stage: khtn6Bai17Stage,
          catalogue: [demonstrated]);
      final rb = resolveBinding(khtn6Bai17TutorBinding, cur);
      expect(rb.hasScope, isTrue);
      expect(rb.permitsContent, isFalse);
      final p = _plan(doc, binding: rb);
      expect(p.isBound, isTrue);
      final explain = p.steps.singleWhere((s) => s.phase == PlannedStepPhase.explain);
      expect(explain.mode, PlannedStepMode.prototypeScripted);
      expect(explain.refusals, contains('NO_ALLOWED_METHOD'));
      expect(explain.act.methodId, isNull);
      expect(p.steps.where((s) => s.phase == PlannedStepPhase.ask).every((s) => s.isRuntimeGuided),
          isTrue,
          reason: 'thăm dò bằng câu sách không cần phương pháp');
    });

    test('⭐⭐ không binding / lệch bài / context chưa giải ⇒ MỌI bước prototype',
        () {
      final none = _plan(doc, noBinding: true);
      expect(none.planRefusals, contains('NO_BINDING'));
      expect(none.steps.every((s) => s.mode == PlannedStepMode.prototypeScripted), isTrue);
      expect(none.steps.every((s) => s.refusals.contains('PLAN:NO_BINDING')), isTrue);

      const otherLesson = LearningContext(
          learnerId: 'na', grade: 6, subject: 'KHTN',
          sourceDocumentId: '06-sgk-khoa-hoc-tu-nhien-6', lessonNo: 16,
          intent: LearningIntent.review);
      final mismatch = _plan(doc, ctx: otherLesson);
      expect(mismatch.planRefusals, containsAll(['BINDING_LESSON_MISMATCH', 'STATE_LESSON_MISMATCH']));
      expect(mismatch.runtimeGuidedCount, 0);

      const unresolved = LearningContext(learnerId: 'na', grade: 6, subject: 'KHTN');
      final u = _plan(doc, ctx: unresolved);
      expect(u.planRefusals, contains('CONTEXT_UNRESOLVED'));
      expect(u.runtimeGuidedCount, 0);
    });

    test('⭐⭐ lời nói ngoài hợp đồng bị từ chối: câu hỏi lộ đáp án ⇒ GUARD:REVEAL; '
        'câu nhắc «trang N» ⇒ GUARD:CITATION_FABRICATION; câu hỏi KHÔNG nguyên '
        'văn sách ⇒ PROMPT_NOT_VERBATIM', () {
      final leakyScript = TutorScript(steps: [
        const ExplainStep(
            id: 'e', text: 'Theo SGK trang 62, cô cạn là làm bay hơi.',
            sourceBlockId: '06-sgk-khoa-hoc-tu-nhien-6:p061:synthetic:006'),
        const AskStep(
            id: 'q',
            prompt: 'Làm muối từ nước biển dùng cách cô cạn hay lọc?',
            promptBlockId: '06-sgk-khoa-hoc-tu-nhien-6:p063:synthetic:020',
            acceptable: ['^cô cạn\$'],
            hints: [],
            feedbackMatched: 'đúng',
            scaffold: 'là cô cạn',
            keySource: 'prototype'),
      ]);
      final p = PedagogyRuntime.planForScript(
        script: leakyScript,
        binding: SemanticBindingRegistry.resolveFor(
            khtn6Bai17, SemanticBinding.tutorScriptActivity),
        studentState: StudentLessonState.unseen(khtn6Bai17),
        context: _ctx,
        blockText: (id) => _blockText(doc, id),
      );
      final e = p.steps.singleWhere((s) => s.phase == PlannedStepPhase.explain);
      expect(e.mode, PlannedStepMode.prototypeScripted);
      expect(e.refusals.any((r) => r.startsWith('GUARD:CITATION_FABRICATION')), isTrue);
      final q = p.steps.singleWhere((s) => s.phase == PlannedStepPhase.ask);
      expect(q.mode, PlannedStepMode.prototypeScripted);
      expect(q.refusals, contains('PROMPT_NOT_VERBATIM'));
      expect(q.refusals.any((r) => r.startsWith('GUARD:REVEAL:côcạn')), isTrue);
    });

    test('literalAnswerForms: bỏ ^\$, hạ chữ, bỏ khoảng trắng; regex phức tạp bị bỏ',
        () {
      expect(PedagogyRuntime.literalAnswerForms(['^cô cạn\$', 'nặng hơn', r'(a|b)+', '']),
          ['côcạn', 'nặnghơn']);
    });
  });

  group('KHÔNG LLM / KHÔNG KHO trong runtime + binding (cấu trúc)', () {
    test('⭐⭐ không import mạng/kho, không ký hiệu LLM, không LearningEvent(', () {
      const files = [
        'lib/core/pedagogy/pedagogy_runtime.dart',
        'lib/core/curriculum/semantic_binding.dart',
        'lib/core/curriculum/semantic_binding_registry.dart',
        'lib/core/curriculum/khtn6_bai17.dart',
        'lib/core/agenda/lesson_next_action.dart',
        'lib/core/student/student_lesson_state.dart',
      ];
      final banned = RegExp(
          r'package:http|dart:io|HttpClient|Socket|openai|anthropic|\bllm\b|\bgpt\b|claude|'
          r'recordSession\(|appendSession\(|LearnerStore|LearningEvent\(|buildTutorPrompt',
          caseSensitive: false);
      for (final f in files) {
        final code = File(f)
            .readAsLinesSync()
            .where((l) => !l.trimLeft().startsWith('//'))
            .join('\n');
        expect(banned.hasMatch(code), isFalse,
            reason: '$f: ${banned.firstMatch(code)?.group(0)}');
      }
    });
  });
}
