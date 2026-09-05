/// TRACK B — KỊCH BẢN SAM (Mode 3 «Học với SAM») + máy trạng thái chạy nó.
///
/// ⭐ UX PROTOTYPE ≠ PROVEN PEDAGOGY RUNTIME. Vòng lặp ở đây — SAM giải thích
/// → hỏi → trẻ trả lời → gợi ý (2 bậc) → kiểm → phản hồi → bước tiếp — là
/// KỊCH BẢN VIẾT TAY chạy tất định (không LLM, không BKT, không
/// `PlannedAct`). Nó cho Founder NHÌN THẤY hình dạng trải nghiệm; nó không
/// chứng minh SAM dạy được.
///
/// Bất biến giữ bằng test:
/// - Khớp đáp án chỉ bằng mẫu `acceptable` của kịch bản (regex tất định);
///   không khớp ⇒ gợi ý, hết gợi ý ⇒ scaffold rồi ĐI TIẾP — không bao giờ
///   kẹt, không bao giờ chê.
/// - Lời khen chỉ xuất hiện khi khớp mẫu; không có lời khen tư chất
///   (`bannedAbilityPraise` của tutor_feedback).
/// - Runner không nhận `LearnerStore`, không phát `LearningEvent` — không có
///   kiểu dữ liệu nào để làm việc đó.
library;

import 'content_trust.dart';

sealed class TutorStep {
  const TutorStep({required this.id});
  final String id;

  Map<String, Object?> toJson();

  static TutorStep? fromJson(Map<String, Object?> j) {
    final id = j['id'];
    if (id is! String) return null;
    switch (j['type']) {
      case 'explain':
        final text = j['text'];
        if (text is! String || text.trim().isEmpty) return null;
        return ExplainStep(
          id: id,
          text: text,
          sourceBlockId: j['sourceBlockId'] as String?,
          mascot: (j['mascot'] as String?) ?? 'sam-explain',
        );
      case 'ask':
        final prompt = j['prompt'];
        if (prompt is! String || prompt.trim().isEmpty) return null;
        final acceptable = [
          for (final a in (j['acceptable'] as List? ?? const []))
            if (a is String && a.isNotEmpty) a,
        ];
        final hints = [
          for (final h in (j['hints'] as List? ?? const []))
            if (h is String && h.isNotEmpty) h,
        ];
        final matched = j['feedbackMatched'], scaffold = j['scaffold'];
        final keySource = j['keySource'];
        if (matched is! String || scaffold is! String) return null;
        if (keySource is! String || keySource.trim().isEmpty) return null;
        if (acceptable.isEmpty || hints.length > 2) return null;
        return AskStep(
          id: id,
          prompt: prompt,
          promptBlockId: j['promptBlockId'] as String?,
          options: [
            for (final o in (j['options'] as List? ?? const []))
              if (o is String) o,
          ],
          acceptable: acceptable,
          hints: hints,
          feedbackMatched: matched,
          scaffold: scaffold,
          keySource: keySource,
        );
      case 'next':
        final label = j['label'];
        final target = NextTarget.parse(j['target']);
        if (label is! String || target == null) return null;
        return NextStep(
          id: id,
          label: label,
          target: target,
          anchorBlockId: j['anchorBlockId'] as String?,
        );
      default:
        return null;
    }
  }
}

/// SAM nói — có thể trích một block nguồn (hiện thành thẻ «Sách viết»).
final class ExplainStep extends TutorStep {
  const ExplainStep({
    required super.id,
    required this.text,
    this.sourceBlockId,
    this.mascot = 'sam-explain',
  });
  final String text;
  final String? sourceBlockId;
  final String mascot;

  @override
  Map<String, Object?> toJson() => {
    'type': 'explain',
    'id': id,
    'text': text,
    if (sourceBlockId != null) 'sourceBlockId': sourceBlockId,
    'mascot': mascot,
  };
}

/// SAM hỏi. `prompt` nên là NGUYÊN VĂN một câu hỏi trong sách
/// (`promptBlockId`); `acceptable`/`hints`/`scaffold`/`keySource` là
/// PROTOTYPE — `keySource` bắt buộc nói khoá đáp án từ đâu ra (không phải SGV).
final class AskStep extends TutorStep {
  const AskStep({
    required super.id,
    required this.prompt,
    required this.acceptable,
    required this.hints,
    required this.feedbackMatched,
    required this.scaffold,
    required this.keySource,
    this.promptBlockId,
    this.options = const [],
  }); // thang gợi ý ≤ 2 bậc: kiểm ở `fromJson` (const ctor không đếm được)

  final String prompt;
  final String? promptBlockId;

  /// Rỗng ⇒ trẻ gõ chữ; có ⇒ trẻ chạm chọn (chuỗi option được đem đi khớp).
  final List<String> options;

  /// Regex (không phân biệt hoa/thường) trên câu trả lời đã chuẩn hoá.
  final List<String> acceptable;
  final List<String> hints;
  final String feedbackMatched;

  /// Khi hết gợi ý mà chưa khớp: SAM chỉ ra chỗ trong sách rồi đi tiếp.
  final String scaffold;
  final String keySource;

  bool get isChoice => options.isNotEmpty;

  @override
  Map<String, Object?> toJson() => {
    'type': 'ask',
    'id': id,
    'prompt': prompt,
    if (promptBlockId != null) 'promptBlockId': promptBlockId,
    'options': options,
    'acceptable': acceptable,
    'hints': hints,
    'feedbackMatched': feedbackMatched,
    'scaffold': scaffold,
    'keySource': keySource,
  };
}

enum NextTarget {
  read,
  visual,
  chapter,
  done;

  static NextTarget? parse(Object? v) {
    for (final t in values) {
      if (t.name == v) return t;
    }
    return null;
  }
}

/// Bước tiếp — một hành động, một lý do; không có «tiếp theo» mơ hồ.
final class NextStep extends TutorStep {
  const NextStep({
    required super.id,
    required this.label,
    required this.target,
    this.anchorBlockId,
  });
  final String label;
  final NextTarget target;
  final String? anchorBlockId;

  @override
  Map<String, Object?> toJson() => {
    'type': 'next',
    'id': id,
    'label': label,
    'target': target.name,
    if (anchorBlockId != null) 'anchorBlockId': anchorBlockId,
  };
}

class TutorScript {
  const TutorScript({
    required this.steps,
    this.samMode = SamMode.prototypeScripted,
    this.trust = ContentTrust.prototype,
    this.evidencePolicy = EvidencePolicy.none,
  });

  final SamMode samMode;
  final ContentTrust trust;
  final EvidencePolicy evidencePolicy;
  final List<TutorStep> steps;

  Iterable<AskStep> get asks => steps.whereType<AskStep>();

  static TutorScript? fromJson(Map<String, Object?> j) {
    final mode = SamMode.parse(j['samMode']);
    final trust = ContentTrust.parse(j['trust']);
    final policy = EvidencePolicy.parse(j['evidencePolicy']);
    if (mode == null || trust == null || policy == null) return null;
    final steps = <TutorStep>[];
    for (final s in (j['steps'] as List? ?? const []).whereType<Map>()) {
      final st = TutorStep.fromJson(s.cast<String, Object?>());
      if (st == null) return null; // một bước hỏng ⇒ không có kịch bản
      steps.add(st);
    }
    if (steps.isEmpty) return null;
    return TutorScript(
      steps: steps,
      samMode: mode,
      trust: trust,
      evidencePolicy: policy,
    );
  }

  Map<String, Object?> toJson() => {
    'samMode': samMode.name,
    'trust': trust.name,
    'evidencePolicy': evidencePolicy.name,
    'steps': [for (final s in steps) s.toJson()],
  };
}

/// Ai nói, nói gì, thuộc loại gì — để UI vẽ và test quét.
enum TurnKind { explain, ask, learner, hint, matched, scaffold, next }

class TutorTurn {
  const TutorTurn({
    required this.kind,
    required this.text,
    this.stepId,
    this.sourceBlockId,
  });
  final TurnKind kind;
  final String text;
  final String? stepId;
  final String? sourceBlockId;

  bool get isSam => kind != TurnKind.learner;

  String get mascot => switch (kind) {
    TurnKind.explain => 'sam-explain',
    TurnKind.ask => 'sam-probe',
    TurnKind.learner => '',
    TurnKind.hint => 'sam-hint',
    TurnKind.matched => 'sam-celebrate-independence',
    TurnKind.scaffold => 'sam-step-back',
    TurnKind.next => 'sam-your-turn',
  };
}

/// Chuẩn hoá câu trả lời trước khi khớp: thường hoá, gộp khoảng trắng, bỏ
/// dấu câu đầu/cuối. KHÔNG bỏ dấu tiếng Việt (mẫu viết có dấu).
String normalizeAnswer(String s) => s
    .toLowerCase()
    .replaceAll(RegExp(r'\s+'), ' ')
    .replaceAll(RegExp(r'^[\s.,;:!?"«»]+|[\s.,;:!?"«»]+$'), '')
    .trim();

bool answerMatches(String answer, List<String> acceptable) {
  final a = normalizeAnswer(answer);
  if (a.isEmpty) return false;
  for (final p in acceptable) {
    if (RegExp(p, caseSensitive: false, unicode: true).hasMatch(a)) return true;
  }
  return false;
}

/// Máy trạng thái TẤT ĐỊNH chạy [TutorScript]. Không có tham số ngẫu nhiên,
/// không có kho, không có mạng.
class TutorRunner {
  TutorRunner(this.script, {String? startAtBlockId}) {
    if (startAtBlockId != null) {
      final i = script.steps.indexWhere(
        (s) => switch (s) {
          AskStep(:final promptBlockId) => promptBlockId == startAtBlockId,
          ExplainStep(:final sourceBlockId) => sourceBlockId == startAtBlockId,
          NextStep() => false,
        },
      );
      if (i >= 0) {
        _index = i;
        anchoredToBlock = true;
      }
    }
    _enter();
  }

  final TutorScript script;
  final List<TutorTurn> transcript = [];

  /// Vào từ «Hỏi SAM về đoạn này» và kịch bản CÓ bước cho đoạn đó.
  bool anchoredToBlock = false;

  int _index = 0;
  int _hintLevel = 0;

  TutorStep? get current =>
      _index < script.steps.length ? script.steps[_index] : null;
  bool get finished => current == null;
  int get hintLevel => _hintLevel;

  /// Còn gợi ý để xin không (UI ẩn nút khi hết).
  bool get canHint => switch (current) {
    AskStep(:final hints) => _hintLevel < hints.length,
    _ => false,
  };

  void _enter() {
    _hintLevel = 0;
    final s = current;
    switch (s) {
      case ExplainStep(:final text, :final sourceBlockId, :final id):
        transcript.add(
          TutorTurn(
            kind: TurnKind.explain,
            text: text,
            stepId: id,
            sourceBlockId: sourceBlockId,
          ),
        );
      case AskStep(:final prompt, :final promptBlockId, :final id):
        transcript.add(
          TutorTurn(
            kind: TurnKind.ask,
            text: prompt,
            stepId: id,
            sourceBlockId: promptBlockId,
          ),
        );
      case NextStep(:final label, :final id, :final anchorBlockId):
        transcript.add(
          TutorTurn(
            kind: TurnKind.next,
            text: label,
            stepId: id,
            sourceBlockId: anchorBlockId,
          ),
        );
      case null:
        break;
    }
  }

  /// Bước giải thích / bước tiếp: trẻ bấm «Tiếp» ⇒ sang bước sau.
  void advance() {
    if (finished) return;
    _index++;
    _enter();
  }

  /// Trẻ xin gợi ý (không cần trả lời sai trước — Founder: scaffold, không
  /// phạt). Trả về `null` khi hết bậc.
  String? requestHint() {
    final s = current;
    if (s is! AskStep || _hintLevel >= s.hints.length) return null;
    final h = s.hints[_hintLevel++];
    transcript.add(TutorTurn(kind: TurnKind.hint, text: h, stepId: s.id));
    return h;
  }

  /// Trẻ trả lời. Khớp ⇒ phản hồi khớp + sang bước sau. Không khớp ⇒ còn gợi
  /// ý thì gợi ý; hết gợi ý thì scaffold + sang bước sau (KHÔNG kẹt, KHÔNG
  /// chê).
  TurnKind submit(String answer) {
    final s = current;
    if (s is! AskStep) return TurnKind.learner;
    transcript.add(
      TutorTurn(kind: TurnKind.learner, text: answer, stepId: s.id),
    );
    if (answerMatches(answer, s.acceptable)) {
      transcript.add(
        TutorTurn(
          kind: TurnKind.matched,
          text: s.feedbackMatched,
          stepId: s.id,
          sourceBlockId: s.promptBlockId,
        ),
      );
      advance();
      return TurnKind.matched;
    }
    if (_hintLevel < s.hints.length) {
      requestHint();
      return TurnKind.hint;
    }
    transcript.add(
      TutorTurn(
        kind: TurnKind.scaffold,
        text: s.scaffold,
        stepId: s.id,
        sourceBlockId: s.promptBlockId,
      ),
    );
    advance();
    return TurnKind.scaffold;
  }
}
