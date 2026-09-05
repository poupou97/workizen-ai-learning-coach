/// ⭐⭐ WAL-210 round 3 (A-runtime, Founder A7) — PEDAGOGY RUNTIME cho lát cắt
/// vàng (PROPOSED, bounded): biến kịch bản Track B (`TutorScript`) thành
/// `PlannedAct` QUA các mảnh runtime ĐÃ CÓ — không runtime thứ ba, không LLM.
///
///   Trusted Source (block của TSL/fixture) + LearningContext (bài đã giải)
///   + Student State (StudentLessonState) + Allowed Methods (SemanticBinding
///   → TutorScope, RETRIEVED ≠ PERMITTED) + LearningActivity (TutorScript)
///     → PedagogyRuntime.planForScript → hành vi ĐƯỢC PHÉP của SAM
///
/// Mỗi bước kịch bản thành một [PlannedStep] mang act + rung + chế độ:
/// - [PlannedStepMode.runtimeGuided]  — runtime CHỨNG MINH được bước này hợp
///   lệ: có scope, act không cần phương pháp hoặc có phương pháp được phép,
///   chữ truy được về block nguồn, và lời nói qua `validateRealization`.
/// - [PlannedStepMode.prototypeScripted] — KHÔNG chứng minh được ⇒ giữ
///   nguyên nhãn «kịch bản thử nghiệm», kèm MÃ LÝ DO. Không giả năng lực.
///
/// Điều runtime này KHÔNG làm (giữ bằng test): không quyết định nội dung mới
/// (chỉ dùng chữ CÓ SẴN trong kịch bản/nguồn), không phát `LearningEvent`
/// (không có validator đăng ký cho câu trả lời tự do ⇒ participation-only
/// như Track B hôm nay), không import kho/mạng/LLM. SAM TUTOR ≠ CHAT.
///
/// ⭐⭐ ROUND 4 (Founder §5 — «real capability, not hard-coding»): thêm ĐÚNG MỘT
/// năng lực tất định — [SourceQuoteIndex]: mọi đoạn «…» trong gợi ý / phản
/// hồi / scaffold phải là NGUYÊN VĂN một block chữ của bài. Gợi ý có nguồn
/// (mọi trích dẫn đều tìm thấy, guard sạch, có phương pháp) mới rời nhãn
/// prototype. Phản hồi «khớp» và scaffold lộ đáp án vẫn phụ thuộc KHOÁ
/// prototype ⇒ vẫn prototype (không có validator cho khoá — A3). Kết quả đo
/// trên fixture thật Bài 17 nằm trong `pedagogy_runtime_test` (nhóm «fixture
/// THẬT»): năng lực có thật; số bước đổi nhãn là số ĐO ĐƯỢC, không đặt tay.
library;

import '../context/learning_context.dart';
import '../curriculum/semantic_binding.dart';
import '../lesson_model/content_trust.dart' show SamMode;
import '../lesson_model/tutor_script.dart';
import '../student/evidence_validation.dart';
import '../student/student_lesson_state.dart';
import '../tutor/output_guard.dart';
import 'pedagogy_model.dart';
import 'realization_contract.dart';
import 'source_quote_index.dart';

export 'source_quote_index.dart';

const String pedagogyRuntimeVersion = 'pedagogy-runtime-v1';

/// Chế độ TỪNG BƯỚC — UI bắt buộc hiện nhãn theo bước, không theo kịch bản.
/// Tên trùng với `SamMode` của Track B để Lane A-data thêm
/// `SamMode.runtimeGuided` mà không đổi chuỗi (`samModeName`).
enum PlannedStepMode {
  runtimeGuided('runtimeGuided', 'SAM (runtime có kiểm)'),
  prototypeScripted('prototypeScripted', 'SAM (kịch bản thử nghiệm)');

  const PlannedStepMode(this.samModeName, this.childLabel);
  final String samModeName;
  final String childLabel;

  /// ⭐ ROUND 4 §5(d): cùng một enum với Lane B (`SamMode` nay có
  /// `runtimeGuided`) — nhãn theo TỪNG BƯỚC vẫn bắt buộc hiện.
  SamMode get samMode => this == runtimeGuided
      ? SamMode.runtimeGuided
      : SamMode.prototypeScripted;
}

enum PlannedStepPhase { explain, ask, hint, feedbackMatched, scaffold, next }

class PlannedStep {
  const PlannedStep({
    required this.stepId,
    required this.phase,
    required this.act,
    required this.rung,
    required this.text,
    required this.mode,
    required this.refusals,
    this.sourceBlockId,
    this.hintIndex,
    this.guard,
    this.validator,
    this.quotes,
  });

  /// id bước trong kịch bản (`e1`, `q1`…); một bước `ask` sinh nhiều
  /// PlannedStep (ask / hint / feedback / scaffold) cùng `stepId`.
  final String stepId;
  final PlannedStepPhase phase;
  final PlannedAct act;
  final AssistanceRung rung;

  /// Chữ TẤT ĐỊNH lấy từ kịch bản — runtime không viết thêm một từ.
  final String text;
  final String? sourceBlockId;
  final int? hintIndex;
  final PlannedStepMode mode;

  /// Mã lý do cố định (test đọc): `PLAN:<mã>`, `NO_ALLOWED_METHOD`,
  /// `NO_SOURCE_BLOCK`, `SOURCE_BLOCK_UNRESOLVED`, `NO_PROMPT_BLOCK`,
  /// `PROMPT_NOT_VERBATIM`, `HINT_UNSOURCED`, `QUOTE_ELIDED:<đoạn>`,
  /// `QUOTE_NOT_IN_SOURCE:<đoạn>`, `KEY_NOT_VALIDATED`,
  /// `OVER_CAP_WITHOUT_VALIDATOR`, `GUARD:<lý do guard>`.
  final List<String> refusals;
  final GuardVerdict? guard;

  /// ⭐ ROUND 4: kết quả kiểm trích dẫn «…» của bước (gợi ý / phản hồi /
  /// scaffold); `null` = bước không qua kiểm trích dẫn (explain/ask/next)
  /// hoặc không có [SourceQuoteIndex].
  final QuoteVerification? quotes;

  /// Validator ĐÃ ĐĂNG KÝ chấm câu trả lời của bước này. `null` = không có ⇒
  /// bước không được tạo bằng chứng năng lực (participation-only). Hôm nay
  /// LUÔN `null` cho Bài 17 (câu trả lời tự do / khoá prototype).
  final EvidenceValidation? validator;

  bool get isRuntimeGuided => mode == PlannedStepMode.runtimeGuided;
}

class RuntimePlan {
  const RuntimePlan({
    required this.steps,
    required this.lessonRef,
    required this.activityId,
    required this.binding,
    required this.studentState,
    required this.planRefusals,
    required this.evidencePolicy,
  });

  final List<PlannedStep> steps;
  final LessonRef? lessonRef;
  final String activityId;
  final ResolvedBinding? binding;
  final StudentLessonState studentState;

  /// Lý do cấp KẾ HOẠCH (context/binding) — khi có, MỌI bước là prototype.
  final List<String> planRefusals;

  /// Chính sách bằng chứng của kế hoạch — chuỗi cố định, test đọc.
  final String evidencePolicy;

  bool get isBound => planRefusals.isEmpty;
  int get runtimeGuidedCount => steps.where((s) => s.isRuntimeGuided).length;
  int get prototypeCount => steps.length - runtimeGuidedCount;

  /// Số bước runtime-guided theo pha — để báo cáo «năng lực nào làm bước
  /// nào thành thật» không gộp.
  int runtimeGuidedIn(PlannedStepPhase phase) =>
      steps.where((s) => s.phase == phase && s.isRuntimeGuided).length;
}

class PedagogyRuntime {
  const PedagogyRuntime._();

  static const participationOnly =
      'participation-only: không có validator đăng ký cho câu trả lời của '
      'kịch bản (A3) — runtime không phát LearningEvent';

  /// Trần hỗ trợ cho các bước PHỤ THUỘC KHOÁ ĐÁP ÁN (gợi ý / phản hồi /
  /// scaffold) khi KHÔNG có validator cho khoá: SAM được gợi ý, không được
  /// PHÁN đúng/sai hay LỘ đáp án từ một khoá prototype. Bước giải thích neo
  /// vào block nguồn không phụ thuộc khoá ⇒ không chịu trần này (vẫn chịu
  /// phương pháp + guard).
  static const capWithoutValidator = AssistanceRung.strategicHint;

  /// [blockText] tra chữ NGUYÊN VĂN của một block nguồn theo id (Lane B đưa
  /// `doc.blockById(id)?.text`); `null` = không tra được ⇒ bước không truy
  /// được về nguồn.
  ///
  /// ⭐ ROUND 4: [quoteIndex] = mọi block chữ của bài
  /// (`SourceQuoteIndex.fromLessonDocument(doc)`); thiếu ⇒ gợi ý / phản hồi
  /// / scaffold không kiểm được trích dẫn ⇒ giữ nguyên nhãn prototype.
  static RuntimePlan planForScript({
    required TutorScript script,
    required ResolvedBinding? binding,
    required StudentLessonState studentState,
    required LearningContext context,
    String? Function(String blockId)? blockText,
    SourceQuoteIndex? quoteIndex,
  }) {
    final ctxRef = LessonRef.fromContext(context);
    final planRefusals = <String>[];
    if (ctxRef == null) planRefusals.add('CONTEXT_UNRESOLVED');
    if (binding == null) {
      planRefusals.add('NO_BINDING');
    } else {
      if (ctxRef != null && binding.binding.lessonRef != ctxRef) {
        planRefusals.add('BINDING_LESSON_MISMATCH');
      }
      if (!binding.hasScope) {
        planRefusals.addAll(['NO_SCOPE', ...binding.refusals]);
      }
    }
    if (ctxRef != null && studentState.lessonRef != ctxRef) {
      planRefusals.add('STATE_LESSON_MISMATCH');
    }

    final steps = <PlannedStep>[];
    final methodId = (binding?.allowedMethods.isNotEmpty ?? false)
        ? binding!.allowedMethods.first.id
        : null;

    PlannedStep plan({
      required String stepId,
      required PlannedStepPhase phase,
      required TeachingAct act,
      required AssistanceRung rung,
      required String text,
      required bool needsMethod,
      required List<String> answerForms,
      bool keyDependent = false,
      List<String> childStated = const [],
      String? sourceBlockId,
      int? hintIndex,
      List<String> stepRefusals = const [],
      QuoteVerification? quotes,
    }) {
      final refusals = <String>[
        for (final r in planRefusals) 'PLAN:$r',
        ...stepRefusals,
      ];
      if (needsMethod && methodId == null) refusals.add('NO_ALLOWED_METHOD');
      if (keyDependent && rung.index > capWithoutValidator.index) {
        refusals.add('OVER_CAP_WITHOUT_VALIDATOR');
      }
      GuardVerdict? verdict;
      final scope = binding?.scope;
      if (scope != null) {
        final req = RealizationRequest(
          act: act,
          rung: rung,
          scope: scope,
          methodId: methodId ?? '',
          grade: context.grade,
          facts: DerivedFacts.textOnly(answerForms: answerForms),
          childStatedFacts: childStated,
        );
        verdict = validateRealization(text.toLowerCase(), req);
        if (!verdict.allowed) {
          refusals.addAll(verdict.blockedReasons.map((r) => 'GUARD:$r'));
        }
      }
      return PlannedStep(
        stepId: stepId,
        phase: phase,
        act: PlannedAct(act, methodId: needsMethod ? methodId : null),
        rung: rung,
        text: text,
        sourceBlockId: sourceBlockId,
        hintIndex: hintIndex,
        mode: refusals.isEmpty
            ? PlannedStepMode.runtimeGuided
            : PlannedStepMode.prototypeScripted,
        refusals: refusals,
        guard: verdict,
        validator: null, // A3: không có validator đăng ký cho bước nào
        quotes: quotes,
      );
    }

    for (final s in script.steps) {
      switch (s) {
        case ExplainStep(:final id, :final text, :final sourceBlockId):
          final r = <String>[];
          if (sourceBlockId == null) {
            r.add('NO_SOURCE_BLOCK');
          } else if (blockText?.call(sourceBlockId) == null) {
            r.add('SOURCE_BLOCK_UNRESOLVED');
          }
          steps.add(plan(
            stepId: id,
            phase: PlannedStepPhase.explain,
            act: TeachingAct.explainConcept,
            rung: AssistanceRung.demonstration,
            text: text,
            needsMethod: true,
            answerForms: const [],
            sourceBlockId: sourceBlockId,
            stepRefusals: r,
          ));

        case AskStep(
            :final id,
            :final prompt,
            :final promptBlockId,
            :final acceptable,
            :final hints,
            :final feedbackMatched,
            :final scaffold,
          ):
          final answers = literalAnswerForms(acceptable);
          // ASK — thăm dò, không cần phương pháp; câu hỏi phải NGUYÊN VĂN
          // một block nguồn (câu sách hỏi), không phải câu SAM tự đặt.
          final askRefusals = <String>[];
          final blockPrompt =
              promptBlockId == null ? null : blockText?.call(promptBlockId);
          if (promptBlockId == null) {
            askRefusals.add('NO_PROMPT_BLOCK');
          } else if (blockPrompt == null ||
              normalizeAnswer(blockPrompt) != normalizeAnswer(prompt)) {
            askRefusals.add('PROMPT_NOT_VERBATIM');
          }
          steps.add(plan(
            stepId: id,
            phase: PlannedStepPhase.ask,
            act: TeachingAct.diagnosticProbe,
            rung: AssistanceRung.independent,
            text: prompt,
            needsMethod: false,
            answerForms: answers,
            sourceBlockId: promptBlockId,
            stepRefusals: askRefusals,
          ));
          // ⭐ ROUND 4 §5(a): ưu tiên block CÙNG MỤC với câu hỏi.
          final section = promptBlockId == null
              ? const <String>[]
              : (quoteIndex?.headingPathOf(promptBlockId) ?? const []);
          QuoteVerification? check(String text) =>
              quoteIndex?.verify(text, preferHeadingPath: section);

          // HINT — mang nội dung ⇒ cần phương pháp; chữ gợi ý phải TRÍCH
          // NGUYÊN VĂN một block của bài («…» tìm thấy) mới có nguồn; không
          // trích / trích không thấy / trích lược ⇒ prototype, có mã lý do.
          // Guard vẫn chạy để lộ rò đáp án cho Founder thấy.
          for (var i = 0; i < hints.length && i < 2; i++) {
            final v = check(hints[i]) ?? QuoteVerification.noQuotes;
            steps.add(plan(
              stepId: id,
              phase: PlannedStepPhase.hint,
              act: i == 0 ? TeachingAct.smallHint : TeachingAct.strategicHint,
              rung: i == 0
                  ? AssistanceRung.smallHint
                  : AssistanceRung.strategicHint,
              text: hints[i],
              needsMethod: true,
              answerForms: answers,
              keyDependent: true,
              hintIndex: i,
              sourceBlockId: v.sourceBlockId,
              stepRefusals: v.refusals,
              quotes: v,
            ));
          }
          // FEEDBACK khi khớp — PHÁN «đúng» theo khoá prototype ⇒ không có
          // validator ⇒ prototype. Trẻ đã nêu đáp án ⇒ guard không phạt oan.
          // Trích dẫn (nếu có) vẫn được kiểm và ghi block nguồn.
          final fb = check(feedbackMatched);
          steps.add(plan(
            stepId: id,
            phase: PlannedStepPhase.feedbackMatched,
            act: TeachingAct.reflect,
            rung: AssistanceRung.independent,
            text: feedbackMatched,
            needsMethod: false,
            answerForms: answers,
            keyDependent: true,
            childStated: answers,
            sourceBlockId: fb?.sourceBlockId,
            stepRefusals: [
              'KEY_NOT_VALIDATED',
              if (fb != null && fb.hasQuotes) ...fb.refusals,
            ],
            quotes: fb,
          ));
          // SCAFFOLD — bottom-out lộ đáp án từ khoá prototype: quá trần.
          final sc = check(scaffold);
          steps.add(plan(
            stepId: id,
            phase: PlannedStepPhase.scaffold,
            act: TeachingAct.revealAnswer,
            rung: AssistanceRung.workedSolution,
            text: scaffold,
            needsMethod: true,
            answerForms: answers,
            keyDependent: true,
            sourceBlockId: sc?.sourceBlockId,
            stepRefusals: [
              'KEY_NOT_VALIDATED',
              if (sc != null && sc.hasQuotes) ...sc.refusals,
            ],
            quotes: sc,
          ));

        case NextStep(:final id, :final label, :final anchorBlockId):
          steps.add(plan(
            stepId: id,
            phase: PlannedStepPhase.next,
            act: TeachingAct.stepBack,
            rung: AssistanceRung.independent,
            text: label,
            needsMethod: false,
            answerForms: const [],
            sourceBlockId: anchorBlockId,
          ));
      }
    }

    return RuntimePlan(
      steps: steps,
      lessonRef: ctxRef,
      activityId: SemanticBinding.tutorScriptActivity,
      binding: binding,
      studentState: studentState,
      planRefusals: planRefusals,
      evidencePolicy: participationOnly,
    );
  }

  /// Dạng đáp án LITERAL từ các mẫu `acceptable` (regex) của kịch bản — chỉ
  /// những mẫu KHÔNG có siêu ký tự (ngoài `^`/`$`) mới thành dạng chặn rò;
  /// mẫu phức tạp bị bỏ qua (không đoán). Trả về dạng đã hạ chữ + bỏ khoảng
  /// trắng, đúng cách `validateTutorOutput` so khớp (`squashed`).
  static List<String> literalAnswerForms(List<String> acceptable) {
    final out = <String>[];
    for (final p in acceptable) {
      var s = p;
      if (s.startsWith('^')) s = s.substring(1);
      if (s.endsWith(r'$')) s = s.substring(0, s.length - 1);
      if (RegExp(r'[\\\[\]().|*+?{}]').hasMatch(s)) continue;
      final form = s.toLowerCase().replaceAll(' ', '');
      if (form.isNotEmpty) out.add(form);
    }
    return out;
  }
}
