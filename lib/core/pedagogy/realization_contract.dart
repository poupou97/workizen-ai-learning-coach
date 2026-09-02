/// WAL-131 §22-23 — LLM REALIZATION CONTRACT: LLM diễn đạt, KHÔNG quyết định.
///
/// Pipeline bắt buộc (mọi lời tới trẻ):
///   RealizationRequest (engine quyết TOÀN BỘ) → buildTutorPrompt (chuồng)
///   → [model — VẪN SHADOW, WAL-30 gate] → validateRealization (guard tất
///   định) → allowed ? text : fallbackRealization (deterministic).
/// LLM không bao giờ là nhánh quyết: act/method/rung/scope đều đến TỪ engine
/// trong request; output vi phạm ⇒ rơi về deterministic — không retry-đến-
/// khi-lọt, không hiển thị «tạm».
library;

import '../curriculum/pedagogical_boundary.dart';
import '../student/mastery.dart';
import '../tutor/output_guard.dart';
import 'pedagogy_model.dart';

/// Loại NỘI DUNG can thiệp (WAL-130 finding #2): «phát lại chậm» ≠ «lộ
/// transcript» dù cùng mức hỗ trợ. Ghi vào interventionId dạng hậu tố
/// `...#<kind>` — evidence cũ (không hậu tố) đọc là [textHint], không đoán.
enum InterventionKind { textHint, replayAudio, slowAudio, transcript, visual }

/// Định danh can thiệp có loại: `policy/method@rung#kind`.
String interventionIdWithKind(
        String policyId, String methodId, SupportLevel level,
        InterventionKind kind) =>
    '$policyId/$methodId@${level.name}#${kind.name}';

/// §23 — cách hiện thực từng act. Ưu tiên deterministic khi đủ tốt
/// (consistency + safety + pedagogy + COGS $0.012/lượt đo được).
enum RealizationPolicy { deterministic, template, retrievalBased, generativeGuarded }

RealizationPolicy realizationPolicyFor(TeachingAct act) => switch (act) {
      // Tính được từ bài ⇒ KHÔNG BAO GIỜ generative (sai một số là sai bài).
      TeachingAct.revealAnswer ||
      TeachingAct.revealStep ||
      TeachingAct.demonstrateStep ||
      TeachingAct.workedExample =>
        RealizationPolicy.deterministic,
      // Câu cấu trúc cố định — template đủ, rẻ, an toàn.
      TeachingAct.observeWait ||
      TeachingAct.stepBack ||
      TeachingAct.askVerification ||
      TeachingAct.reflect =>
        RealizationPolicy.template,
      // Cần nội dung nguồn (so ca, giảng khái niệm) — retrieval trước.
      TeachingAct.contrastCases ||
      TeachingAct.explainConcept =>
        RealizationPolicy.retrievalBased,
      // Wording tự nhiên có giá trị thật — generative NHƯNG qua guard.
      TeachingAct.pumpRecall ||
      TeachingAct.diagnosticProbe ||
      TeachingAct.smallHint ||
      TeachingAct.strategicHint ||
      TeachingAct.askExplanation =>
        RealizationPolicy.generativeGuarded,
    };

/// Engine quyết XONG mới có request — LLM chỉ nhận, không chọn.
class RealizationRequest {
  const RealizationRequest({
    required this.act,
    required this.rung,
    required this.scope,
    required this.methodId,
    required this.grade,
    required this.facts,
    this.kind = InterventionKind.textHint,
    this.examMode = false,
    this.childStatedFacts = const [],
  });

  final TeachingAct act;
  final AssistanceRung rung;
  final TutorScope scope;
  final String methodId;
  final int grade;

  /// Sự thật dẫn xuất của bài — guard dùng chặn rò số/đáp án theo mức.
  final DerivedFacts facts;
  final InterventionKind kind;
  final bool examMode;
  final List<String> childStatedFacts;
}

/// Guard tất định cho MỘT realization. Mức cho phép lấy từ RUNG của request
/// (không tin model tự khai); act và rung phải NHẤT QUÁN — act nặng hơn rung
/// là lỗi engine, fail closed luôn.
GuardVerdict validateRealization(String text, RealizationRequest r) {
  final actLevel = supportLevelOf(r.act);
  final rungLevel = rungToSupport(r.rung);
  if (actLevel.index > rungLevel.index) {
    return GuardVerdict(false,
        ['ACT_OVER_RUNG:${r.act.name}(${actLevel.name})>${r.rung.name}']);
  }
  return validateTutorOutput(
    text: text,
    maxAllowed: rungLevel,
    facts: r.facts,
    examMode: r.examMode,
    childStatedFacts: r.childStatedFacts,
  );
}
