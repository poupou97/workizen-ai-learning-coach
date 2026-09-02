/// WAL-86 — TutorSession: máy trạng thái RULE-BASED cho một bài tập.
///
/// KHÔNG LLM (WAL-30 vẫn gated). Nội dung gợi ý chỉ được lấy từ
/// `TutorScope.allowedMethods` — ngoài scope thì SAM nhận là chưa chắc,
/// không bịa (fail closed, cùng luật với perception).
///
/// Luật giữ bằng test:
/// - Thang hỗ trợ leo TỪNG NẤC (±1): none → hint → workedStep → fullSolution.
/// - fullSolution CHỈ mở sau khi trẻ đã TỰ THỬ ít nhất một lần (REVEAL gate —
///   Photomath/QANDA cho xem đáp án ngay là phản-mẫu số 1 của pattern library).
/// - Mỗi hành động phát đúng MỘT LearningEvent — không đếm kép:
///   trả lời khi chưa có hỗ trợ → independentAttempt (hoặc selfCorrection nếu
///   tự sửa cái sai của chính mình mà không cần hỗ trợ mới);
///   trả lời khi ĐANG có hỗ trợ → đúng = postHintSuccess, sai = guidedAttempt;
///   xin gợi ý → hintRequested (correct: null — UNKNOWN không thành FAILED);
///   chốt bài → finalCorrectness (kết quả, không phải một lần thử).
/// - UI có thể khen tuỳ ý; MODEL chỉ tin log. Khen ≠ ghi công.
library;

import '../../core/curriculum/pedagogical_boundary.dart';
import '../../core/student/learning_evidence.dart';
import '../../core/student/mastery.dart';

/// Bài phân số "a/b ± c/d" đã bóc số — đầu vào rule-based của slice này.
class FractionProblem {
  const FractionProblem(this.a, this.b, this.op, this.c, this.d);
  final int a, b, c, d;
  final String op; // '+' | '-'

  /// null nếu không phải dạng "a/b ± c/d" — tầng trên phải fail closed.
  static FractionProblem? parse(String expr) {
    final m = RegExp(
            r'^\s*(\d{1,3})\s*/\s*(\d{1,3})\s*([+\-−])\s*(\d{1,3})\s*/\s*(\d{1,3})\s*$')
        .firstMatch(expr);
    if (m == null) return null;
    return FractionProblem(
        int.parse(m.group(1)!),
        int.parse(m.group(2)!),
        m.group(3)! == '−' ? '-' : m.group(3)!,
        int.parse(m.group(4)!),
        int.parse(m.group(5)!));
  }

  int get resultNum => op == '+' ? a * d + c * b : a * d - c * b;
  int get resultDen => b * d;

  /// Đáp án của trẻ dạng "x/y" hoặc số nguyên; chấp nhận phân số CHƯA rút gọn
  /// có cùng giá trị (SGK Toán 5 chấp nhận cả hai dạng ở bước quy đồng).
  bool checkAnswer(String raw) {
    final f = RegExp(r'^\s*(-?\d{1,6})\s*(?:/\s*(\d{1,6})\s*)?$').firstMatch(raw);
    if (f == null) return false;
    final n = int.parse(f.group(1)!);
    final d0 = f.group(2) == null ? 1 : int.parse(f.group(2)!);
    if (d0 == 0) return false;
    return n * resultDen == resultNum * d0;
  }
}

/// Kết quả một lần trẻ bấm "Xong" — UI vẽ theo cái này, không tự suy.
enum SubmitOutcome { independentCorrect, selfCorrected, supportedCorrect, wrong }

/// Bốn chiều của E1 — tách bạch, không gộp thành một lời khen chung.
class TutorOutcome {
  const TutorOutcome({
    required this.correct, // CORRECTNESS — đáp án chốt
    required this.maxSupport, // ASSISTANCE — nấc cao nhất đã dùng
    required this.independent, // EVIDENCE — có được tính là tự làm không
    required this.selfCorrected, // AFFECT — tự sửa đáng khen riêng
  });
  final bool correct;
  final SupportLevel maxSupport;
  final bool independent;
  final bool selfCorrected;
}

class TutorSession {
  TutorSession({
    required this.exerciseId,
    required this.skillCaseId,
    required this.problem,
    required this.scope,
    DateTime Function()? now,
  })  : _now = now ?? DateTime.now,
        log = EvidenceLog.empty(skillCaseId);

  final String exerciseId;
  final String skillCaseId;
  final FractionProblem problem;
  final TutorScope scope;
  final DateTime Function() _now;

  EvidenceLog log;
  SupportLevel support = SupportLevel.none;
  SupportLevel maxSupport = SupportLevel.none;
  bool finished = false;
  bool _lastWasWrong = false;
  bool _supportRaisedSinceWrong = false;
  int _seq = 0;

  bool get hasAttempted => log.events
      .any((e) => e.kind != EvidenceKind.hintRequested && e.correct != null);

  /// REVEAL gate: lời giải trọn vẹn chỉ sau ≥1 lần tự thử.
  bool get revealAllowed => hasAttempted;

  static const policyId = 'tutor-session-v1';
  String? _lastAnswerEventId;

  /// Can thiệp ĐANG treo trên màn hình — mọi câu trả lời khi support > none
  /// mang id này: «đúng sau gợi ý NÀO» nằm trong dữ liệu (§3 Master Order).
  String? _activeInterventionId;

  void _emit(EvidenceKind kind, bool? correct, {String? interventionId}) {
    final id = '$exerciseId#${_seq++}';
    final isAnswer = correct != null;
    log = log.append(LearningEvent(
      eventId: id,
      skillCaseId: skillCaseId,
      kind: kind,
      correct: correct,
      exerciseId: exerciseId,
      at: _now(),
      // LINEAGE (§7): mức hỗ trợ TẠI sự kiện + policy + chuỗi pre/post —
      // «đúng sau hint nhỏ» phải khác «đúng sau xem trọn lời giải» NGAY
      // TRONG DỮ LIỆU, không phải suy đoán từ thứ tự log.
      support: support,
      policyId: policyId,
      priorEventId: isAnswer ? _lastAnswerEventId : null,
      conceptIds: [scope.targetConcept],
      interventionId: interventionId ??
          (isAnswer && support != SupportLevel.none
              ? _activeInterventionId
              : null),
    ));
    if (isAnswer) _lastAnswerEventId = id;
  }

  /// Trẻ bấm "Xong". Một sự kiện, đúng loại, không đếm kép.
  SubmitOutcome submit(String answer) {
    assert(!finished);
    final correct = problem.checkAnswer(answer);
    final SubmitOutcome outcome;
    if (support == SupportLevel.none) {
      if (correct && _lastWasWrong && !_supportRaisedSinceWrong) {
        _emit(EvidenceKind.selfCorrection, true);
        outcome = SubmitOutcome.selfCorrected;
      } else {
        _emit(EvidenceKind.independentAttempt, correct);
        outcome =
            correct ? SubmitOutcome.independentCorrect : SubmitOutcome.wrong;
      }
    } else {
      _emit(correct ? EvidenceKind.postHintSuccess : EvidenceKind.guidedAttempt,
          correct);
      outcome = correct ? SubmitOutcome.supportedCorrect : SubmitOutcome.wrong;
    }
    if (correct) {
      _emit(EvidenceKind.finalCorrectness, true);
      finished = true;
    } else {
      _lastWasWrong = true;
      _supportRaisedSinceWrong = false;
    }
    return outcome;
  }

  /// Trẻ xin gợi ý. Leo đúng MỘT nấc; trả về nội dung để hiển thị,
  /// hoặc null khi không leo được (hết scope, hoặc REVEAL chưa mở).
  ///
  /// `hintRequested` được ghi CẢ khi fail closed — việc trẻ biết mình bí
  /// là bằng chứng siêu nhận thức, độc lập với việc SAM có gì để đưa.
  String? requestHint() {
    assert(!finished);
    if (scope.allowedMethods.isEmpty) {
      // Bí vẫn là bằng chứng siêu nhận thức — ghi CẢ khi fail closed, nhưng
      // KHÔNG có interventionId: không can thiệp nào đã thực sự xảy ra.
      _emit(EvidenceKind.hintRequested, null);
      return null; // fail closed
    }
    final method = scope.allowedMethods.first;
    final next = switch (support) {
      SupportLevel.none => SupportLevel.hint,
      SupportLevel.hint => SupportLevel.workedStep,
      SupportLevel.workedStep =>
        revealAllowed ? SupportLevel.fullSolution : SupportLevel.workedStep,
      SupportLevel.fullSolution => SupportLevel.fullSolution,
    };
    // ⭐ §3 «exact hint identity»: sự kiện xin-gợi-ý mang định danh của ĐÚNG
    // nội dung sẽ hiển thị (kể cả khi đứng yên nhắc lại nấc cũ).
    final delivered =
        (next == support && support != SupportLevel.none) ? support : next;
    _activeInterventionId = interventionIdFor(policyId, method.id, delivered);
    _emit(EvidenceKind.hintRequested, null,
        interventionId: _activeInterventionId);
    if (next == support && support != SupportLevel.none) {
      // đứng yên (REVEAL chưa mở hoặc đã kịch thang) — nhắc lại nấc hiện tại
      return hintTextFor(method, support, problem);
    }
    support = next;
    if (next.index > maxSupport.index) maxSupport = next;
    _supportRaisedSinceWrong = true;
    return hintTextFor(method, support, problem);
  }

  TutorOutcome get outcome => TutorOutcome(
        correct: log.events
            .any((e) => e.kind == EvidenceKind.finalCorrectness && e.correct == true),
        maxSupport: maxSupport,
        independent: maxSupport == SupportLevel.none,
        selfCorrected:
            log.events.any((e) => e.kind == EvidenceKind.selfCorrection),
      );
}

/// Định danh can thiệp — «policy/method@nấc». Đủ để truy về đúng nội dung đã
/// hiển thị: [hintTextFor] là hàm TẤT ĐỊNH của bộ ba này cộng với chính bài.
String interventionIdFor(
        String policyId, String methodId, SupportLevel level) =>
    '$policyId/$methodId@${level.name}';

/// Nội dung gợi ý RULE-BASED — chỉ từ method trong scope, số lấy từ chính bài.
/// Ba nấc tương ứng AutoTutor pump→hint→assertion (prior art WAL-64).
String hintTextFor(TeachingMethod m, SupportLevel level, FractionProblem p) {
  final byProduct = m.id == 'common-denom-by-product';
  switch (level) {
    case SupportLevel.none:
      return '';
    case SupportLevel.hint:
      return byProduct
          ? 'Hai mẫu số ${p.b} và ${p.d} không chia hết cho nhau. '
              'Muốn cộng được thì hai phân số phải cùng mẫu số — '
              'con nghĩ xem mẫu số chung lấy thế nào nhé?'
          : 'Con thử xem mẫu số lớn hơn có chia hết cho mẫu số kia không?';
    case SupportLevel.workedStep:
      return byProduct
          ? 'Bước đầu tiên: lấy mẫu số chung là ${p.b} × ${p.d} = ${p.b * p.d}. '
              'Giờ con quy đồng hai phân số về mẫu ${p.b * p.d} nhé — đến lượt con!'
          : 'Bước đầu tiên: giữ nguyên phân số có mẫu lớn hơn, '
              'quy đồng phân số còn lại. Đến lượt con!';
    case SupportLevel.fullSolution:
      final mc = p.b * p.d;
      return 'Cả bài nhé: mẫu số chung là ${p.b} × ${p.d} = $mc. '
          '${p.a}/${p.b} = ${p.a * p.d}/$mc và ${p.c}/${p.d} = ${p.c * p.b}/$mc. '
          'Vậy ${p.a}/${p.b} ${p.op} ${p.c}/${p.d} = '
          '${p.resultNum}/$mc. '
          'Mai mình làm lại một bài giống thế này không cần SAM nhé!';
  }
}
