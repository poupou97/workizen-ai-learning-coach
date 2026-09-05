/// ⭐⭐ WAL-210 round 3 (A-runtime) — Founder A7: PEDAGOGY RUNTIME cho lát cắt
/// vàng. «SAM TUTOR ≠ CHAT. LLM does not decide pedagogy. RETRIEVED ≠
/// PERMITTED. If a real capability is missing, keep the prototype clearly
/// marked rather than fake production capability.»
///
/// Chạy trên fixture MẪU Bài 17 (commit) — cùng kịch bản Track B đã đi trên
/// máy thật; kiểm: chế độ TỪNG BƯỚC đúng; act ngoài phương pháp được phép bị
/// từ chối; lời nói ngoài hợp đồng bị từ chối; không bước nào có validator;
/// không ký hiệu LLM / kho / mạng trong runtime.
///
/// ⭐⭐ ROUND 4 (Founder §5): năng lực MỚI duy nhất là kiểm trích dẫn «…»
/// (`SourceQuoteIndex`). Nhóm «fixture THẬT» ĐO số bước đổi nhãn trên Bài 17
/// thật (bỏ qua ở máy không có fixture) và GHIM từng mã lý do — con số
/// Pedagogy Reality trong báo cáo được trích từ đây, không đặt tay.
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
        {ResolvedBinding? binding,
        bool noBinding = false,
        LearningContext? ctx,
        bool withQuoteIndex = true,
        TutorScript? script}) =>
    PedagogyRuntime.planForScript(
      script: script ?? d.tutorScript!,
      binding: noBinding
          ? null
          : binding ??
              SemanticBindingRegistry.resolveFor(
                  khtn6Bai17, SemanticBinding.tutorScriptActivity),
      studentState: StudentLessonState.unseen(khtn6Bai17),
      context: ctx ?? _ctx,
      blockText: (id) => _blockText(d, id),
      quoteIndex: withQuoteIndex ? SourceQuoteIndex.fromLessonDocument(d) : null,
    );

const _realFixture = 'assets/fixtures/real/lesson-06-sgk-khoa-hoc-tu-nhien-6-b17.json';

LessonDocument? _realDocOrSkip() {
  final f = File(_realFixture);
  if (!f.existsSync()) {
    markTestSkipped('fixture thật chưa có trên máy này (gitignored)');
    return null;
  }
  final j = jsonDecode(f.readAsStringSync()) as Map;
  return LessonDocument.fromJson(j.cast<String, Object?>(), assetBase: 'x/')!;
}

String _key(PlannedStep s) =>
    '${s.stepId}/${s.phase.name}${s.hintIndex == null ? '' : '#${s.hintIndex}'}';

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
      // ROUND 4: có chỉ mục trích dẫn hay không, fixture mẫu vẫn 4/12 — gợi
      // ý mẫu không trích «…» nào ⇒ HINT_UNSOURCED; không đổi nhãn.
      expect(_plan(doc, withQuoteIndex: false).runtimeGuidedCount, 4);
      expect(PlannedStepMode.runtimeGuided.samMode.name, 'runtimeGuided');
      expect(PlannedStepMode.prototypeScripted.samMode.name, 'prototypeScripted');
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

  group('ROUND 4 §5(a) — trích dẫn «…» nguyên văn: NĂNG LỰC THẬT, không hard-code', () {
    /// Kịch bản đối chứng DƯƠNG: gợi ý trích NGUYÊN VĂN một block của fixture
    /// mẫu (không lộ đáp án) ⇒ đổi nhãn runtimeGuided. Chứng minh luật áp cho
    /// MỌI bước theo dữ liệu, không theo id bước.
    test('⭐⭐ gợi ý trích nguyên văn block (không rò đáp án) ⇒ runtimeGuided, '
        'ghi đúng sourceBlockId; gợi ý không trích ⇒ HINT_UNSOURCED', () {
      const q = AskStep(
          id: 'qx',
          prompt: '[MẪU] Làm muối từ nước biển dùng cách tách chất nào?',
          promptBlockId: '06-sgk-khoa-hoc-tu-nhien-6:p063:synthetic:020',
          acceptable: ['^cô cạn\$'],
          hints: [
            'Sách viết: «Các chất trong một hỗn hợp có tính chất khác nhau» — '
                'muối và nước khác nhau ở chỗ nào?',
            'Con nghĩ xem muối có bay hơi không.',
          ],
          feedbackMatched: 'ok',
          scaffold: 'x',
          keySource: 'prototype');
      final p = _plan(doc, script: const TutorScript(steps: [q]));
      final hints = p.steps.where((s) => s.phase == PlannedStepPhase.hint).toList();
      expect(hints[0].isRuntimeGuided, isTrue, reason: hints[0].refusals.join(','));
      expect(hints[0].sourceBlockId, '06-sgk-khoa-hoc-tu-nhien-6:p061:synthetic:006');
      expect(hints[0].quotes!.isSourced, isTrue);
      expect(hints[0].act.methodId, khtn6TachChatMethodId,
          reason: 'gợi ý vẫn cần phương pháp được phép');
      expect(hints[1].isRuntimeGuided, isFalse);
      expect(hints[1].refusals, ['HINT_UNSOURCED']);
      // Không có chỉ mục ⇒ không chứng minh được ⇒ prototype (fail closed).
      final noIdx = _plan(doc, script: const TutorScript(steps: [q]), withQuoteIndex: false);
      expect(noIdx.steps.where((s) => s.phase == PlannedStepPhase.hint).every((s) => !s.isRuntimeGuided),
          isTrue);
    });

    test('⭐⭐ trích nguyên văn nhưng RÒ ĐÁP ÁN ⇒ vẫn prototype (GUARD:REVEAL); '
        'trích không có trong bài ⇒ QUOTE_NOT_IN_SOURCE; trích lược ⇒ QUOTE_ELIDED',
        () {
      const q = AskStep(
          id: 'qy',
          prompt: '[MẪU] Làm muối từ nước biển dùng cách tách chất nào?',
          promptBlockId: '06-sgk-khoa-hoc-tu-nhien-6:p063:synthetic:020',
          acceptable: ['^cô cạn\$'],
          hints: [
            // nguyên văn block :023 nhưng chứa «Cô cạn» = đáp án
            'Sách viết: «Cô cạn (tách chất rắn đã tan bằng cách làm bay hơi chất lỏng)».',
            'Sách viết: «muối tan trong nước còn cát thì không».',
          ],
          feedbackMatched: 'ok',
          scaffold: 'x',
          keySource: 'prototype');
      final p = _plan(doc, script: const TutorScript(steps: [q]));
      final hints = p.steps.where((s) => s.phase == PlannedStepPhase.hint).toList();
      expect(hints[0].quotes!.isSourced, isTrue, reason: 'trích có thật…');
      expect(hints[0].isRuntimeGuided, isFalse, reason: '…nhưng guard chặn rò');
      expect(hints[0].refusals.any((r) => r.startsWith('GUARD:REVEAL:côcạn')), isTrue);
      expect(hints[1].refusals.single, startsWith('QUOTE_NOT_IN_SOURCE:'));
      const z = AskStep(
          id: 'qz',
          prompt: 'p',
          acceptable: [r'(x|y)+'], // regex phức ⇒ không có dạng đáp án để chặn
          hints: ['«Các chất trong một hỗn hợp… để tách chúng ra»'],
          feedbackMatched: 'ok',
          scaffold: 'x',
          keySource: 'prototype');
      final pz = _plan(doc, script: const TutorScript(steps: [z]));
      expect(pz.steps.firstWhere((s) => s.phase == PlannedStepPhase.hint).refusals.single,
          startsWith('QUOTE_ELIDED:'));
    });

    test('phản hồi «khớp» và scaffold vẫn prototype dù trích đúng — khoá đáp án '
        'không có validator (A3); block trích vẫn ghi để UI hiện «Sách viết»', () {
      const q = AskStep(
          id: 'qf',
          prompt: '[MẪU] 1. Vì sao hạt cát lắng xuống đáy cốc?',
          promptBlockId: '06-sgk-khoa-hoc-tu-nhien-6:p061:synthetic:008',
          acceptable: ['nặng'],
          hints: [],
          feedbackMatched: 'Khớp với «Nước đục để yên thì hạt nặng lắng xuống».',
          scaffold: 'Sách: «Nước đục để yên thì hạt nặng lắng xuống». Đi tiếp nhé.',
          keySource: 'prototype');
      final p = _plan(doc, script: const TutorScript(steps: [q]));
      final fb = p.steps.singleWhere((s) => s.phase == PlannedStepPhase.feedbackMatched);
      final sc = p.steps.singleWhere((s) => s.phase == PlannedStepPhase.scaffold);
      for (final s in [fb, sc]) {
        expect(s.isRuntimeGuided, isFalse);
        expect(s.refusals, contains('KEY_NOT_VALIDATED'));
        expect(s.sourceBlockId, '06-sgk-khoa-hoc-tu-nhien-6:p061:synthetic:007');
        expect(s.validator, isNull);
      }
      expect(sc.refusals, contains('OVER_CAP_WITHOUT_VALIDATOR'));
    });
  });

  group('ROUND 4 — fixture THẬT Bài 17 (bỏ qua nếu thiếu): ĐO, không đặt tay', () {
    /// ⭐ ROUND 4 · Lane B đã SỬA kịch bản (không sửa luật): q1#1 bỏ trích dẫn
    /// «trang 62» tự chế và trích liền một mạch; q3#1 trả lại hai chữ «các»
    /// đúng như sách. Hai gợi ý đó nay QUA được luật ⇒ 5 → 7 / 17. Con số này
    /// là ĐO SAU KHI SỬA NGUỒN CHỮ, không phải nới luật: q2#1 vẫn trượt vì
    /// lỗi OCR nằm trong nguồn (A-pipeline), ba gợi ý #0 vẫn không trích gì.
    test('⭐⭐ 17 bước: 5 runtimeGuided KHÔNG kiểm trích dẫn → 7 khi kiểm; '
        'từng mã lý do nói đúng chỗ hỏng còn lại của kịch bản/nguồn', () {
      final d = _realDocOrSkip();
      if (d == null) return;
      final before = _plan(d, withQuoteIndex: false);
      final after = _plan(d);
      expect(before.steps.length, 17);
      expect(before.runtimeGuidedCount, 5, reason: 'e1 + q1 + q2 + q3 + n1');
      expect(after.runtimeGuidedCount, 7,
          reason: '⭐ + q1/hint#1 + q3/hint#1 sau khi kịch bản trích ĐÚNG NGUYÊN '
              'VĂN sách — con số phải ĐO, không đặt tay');
      expect(after.runtimeGuidedIn(PlannedStepPhase.hint), 2);
      expect(after.runtimeGuidedIn(PlannedStepPhase.ask), 3);
      expect(after.runtimeGuidedIn(PlannedStepPhase.explain), 1);
      expect(after.runtimeGuidedIn(PlannedStepPhase.next), 1);
      expect(after.steps.every((s) => s.validator == null), isTrue,
          reason: 'không validator mới — Evidence Reality Bài 17 = 0, trung thực');

      final by = {for (final s in after.steps) _key(s): s};
      // q1#1 (ĐÃ SỬA): trích liền một mạch từ block «Phương pháp cô cạn dùng
      // để …», KHÔNG còn «…» và KHÔNG còn số trang tự chế ⇒ hết lý do từ chối.
      expect(by['q1/hint#1']!.refusals, isEmpty);
      expect(by['q1/hint#1']!.mode, PlannedStepMode.runtimeGuided);
      expect(by['q1/hint#1']!.sourceBlockId,
          '06-sgk-khoa-hoc-tu-nhien-6:p063:tc2-p1:005');
      // q2#1: kịch bản trích «khoá» đúng chính tả, nguồn OCR đọc «khóa … khoa»
      // ⇒ không nguyên văn — lỗi FIDELITY của nguồn (A-pipeline), runtime không sửa hộ.
      expect(by['q2/hint#1']!.refusals.single, startsWith('QUOTE_NOT_IN_SOURCE:Khi phần dầu ăn'));
      // q3#1 (ĐÃ SỬA): cả hai trích đều nguyên văn (Lọc 4:004, Cô cạn 4:006).
      expect(by['q3/hint#1']!.refusals, isEmpty);
      expect(by['q3/hint#1']!.mode, PlannedStepMode.runtimeGuided);
      expect(by['q3/hint#1']!.sourceBlockId, '06-sgk-khoa-hoc-tu-nhien-6:p064:tc2-p1:004');
      // ba gợi ý còn lại không trích gì.
      for (final k in ['q1/hint#0', 'q2/hint#0', 'q3/hint#0']) {
        expect(by[k]!.refusals, ['HINT_UNSOURCED'], reason: k);
      }
      // scaffold q1/q3 trích đúng («cô cạn» = tiêu đề mục; «Em đã học») nhưng
      // vẫn prototype: lộ đáp án từ khoá prototype, quá trần không validator.
      expect(by['q1/scaffold']!.sourceBlockId, '06-sgk-khoa-hoc-tu-nhien-6:p063:tc2-p1:002');
      expect(by['q3/scaffold']!.sourceBlockId, '06-sgk-khoa-hoc-tu-nhien-6:p064:tc2-p1:002');
      for (final k in ['q1/scaffold', 'q2/scaffold', 'q3/scaffold']) {
        expect(by[k]!.refusals, containsAll(['KEY_NOT_VALIDATED', 'OVER_CAP_WITHOUT_VALIDATOR']));
      }
      // ignore: avoid_print
      print('ROUND4-PEDAGOGY real Bài 17: before=${before.runtimeGuidedCount}/'
          '${before.steps.length} after=${after.runtimeGuidedCount}/${after.steps.length}; '
          '${[for (final s in after.steps) '${_key(s)}=${s.mode.samModeName}${s.refusals.isEmpty ? '' : s.refusals}'].join(' | ')}');
    });
  });

  group('KHÔNG LLM / KHÔNG KHO trong runtime + binding (cấu trúc)', () {
    test('⭐⭐ không import mạng/kho, không ký hiệu LLM, không LearningEvent(', () {
      const files = [
        'lib/core/pedagogy/pedagogy_runtime.dart',
        'lib/core/pedagogy/source_quote_index.dart',
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
