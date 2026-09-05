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

import '../../core/context/learning_context.dart';
import '../../core/curriculum/pedagogical_boundary.dart';
import '../../core/curriculum/solvable_problem.dart';
import '../../core/student/evidence_ids.dart';
import '../../core/student/evidence_validation.dart';
import '../../core/student/learning_evidence.dart';
import '../../core/knowledge/slice_curriculum.dart' show knowledgeModelVersion;
import '../../core/student/mastery.dart';

// WAL-168: `FractionProblem` đã chuyển xuống `core/curriculum` (tri thức miền,
// không phải UI). Vẫn xuất lại ở đây để mọi chỗ import cũ không phải đổi.
export '../../core/curriculum/fraction_problem.dart' show FractionProblem;

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
    String? sessionToken,
    this.sourceDocumentId,
    this.lessonNo,
    DeterministicValidator? validator,
  })  : _now = now ?? DateTime.now,
        // ⭐⭐ Round 3 (Founder A3): phiên dạy CHỈ chấm qua validator ĐÃ ĐĂNG
        // KÝ. Loại bài chưa có validator ⇒ không mở phiên chấm — fail closed
        // ngay tại biên engine, không có nhánh «tạm chấm».
        validator = validator ??
            approvedValidatorFor(problem) ??
            (throw ArgumentError(
                'TutorSession: loại bài ${problem.runtimeType} chưa có '
                'EvidenceValidator đăng ký — không được chấm (A3)')),
        log = EvidenceLog.empty(skillCaseId) {
    // A3: validator TIÊM VÀO cũng phải nằm trong sổ đăng ký — không có đường
    // «validator riêng» đi vòng qua registry (RETRIEVED ≠ PERMITTED).
    if (!this.validator.validation.isRegistered) {
      throw ArgumentError('TutorSession: validator '
          '${this.validator.validation} không có trong sổ đăng ký (A3)');
    }
    // ⭐ WAL-210 (audit C1): token sinh MỘT LẦN lúc mở phiên — mở lại cùng
    // bài là phiên khác, id khác. Lấy từ ĐỒNG HỒ MÁY, không từ `now` tiêm
    // vào: token chỉ cần DUY NHẤT, còn `now` là để test giữ tất định dấu
    // thời gian sự kiện — không được "ăn" mất một nhịp của nó. Tiêm
    // `sessionToken` khi cần id tất định.
    this.sessionToken = sessionToken ?? newEvidenceSessionToken(DateTime.now());
  }

  /// ⭐⭐ Round 3 (Founder A5) — LINEAGE CHỈ TỪ CONTEXT ĐÃ GIẢI. Bài mở từ
  /// pack đi qua đây với `learningContext` có `hasLesson`; bài CHỤP (camera)
  /// không có context bài ⇒ `sourceDocumentId == null && lessonNo == null`.
  /// Không có đường «ảnh chụp → AI đoán bài → stamp».
  TutorSession.inContext({
    required String exerciseId,
    required String skillCaseId,
    required SolvableProblem problem,
    required TutorScope scope,
    required LearningContext? learningContext,
    DateTime Function()? now,
    String? sessionToken,
    DeterministicValidator? validator,
  }) : this(
          exerciseId: exerciseId,
          skillCaseId: skillCaseId,
          problem: problem,
          scope: scope,
          now: now,
          sessionToken: sessionToken,
          validator: validator,
          sourceDocumentId: lineageFromContext(learningContext).$1,
          lessonNo: lineageFromContext(learningContext).$2,
        );

  /// A5 — luật stamp: CHỈ khi context đã giải ra ĐỦ (sách + số bài). Context
  /// tầng Global/Subject/Book (thiếu bài) ⇒ `(null, null)`, không stamp nửa
  /// vời một cuốn sách không có bài.
  static (String?, int?) lineageFromContext(LearningContext? c) =>
      (c != null && c.hasLesson) ? (c.sourceDocumentId, c.lessonNo) : (null, null);

  final String exerciseId;
  final String skillCaseId;

  /// Validator ĐÃ ĐĂNG KÝ đang chấm phiên này — dấu của nó nằm trên mọi sự
  /// kiện có `correct` (A3).
  final DeterministicValidator validator;

  /// Định danh PHIÊN — phần làm cho `eventId` duy nhất giữa các lần mở.
  late final String sessionToken;

  /// ⭐ WAL-210 (audit C7) — LINEAGE sách + bài của bài tập đang dạy, khi
  /// bài mở TỪ một bài trong pack. Bài CHỤP (camera) không biết bài nào ⇒
  /// `null` — Founder quyết có/không suy ra từ chương trình (chưa quyết).
  final String? sourceDocumentId;
  final int? lessonNo;

  /// ⭐ WAL-168: phiên dạy KHÔNG mang kiểu của một môn. Trước đây trường này
  /// là `FractionProblem`, nên môn thứ hai không vào nổi runtime.
  final SolvableProblem problem;
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
    final id = evidenceEventId(
        exerciseId: exerciseId, sessionToken: sessionToken, seq: _seq++);
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
      // WAL-114: mọi evidence mang CẢ HAI version — tutor policy + knowledge.
      knowledgeVersion: knowledgeModelVersion,
      // ⭐⭐ WAL-210 lineage (null khi bài không đến từ một bài trong pack).
      sourceDocumentId: sourceDocumentId,
      lessonNo: lessonNo,
      // ⭐⭐ Round 3 (A3): sự kiện CÓ CHẤM mang dấu của validator đã chấm;
      // sự kiện không chấm (xin gợi ý) không mang dấu nào.
      validation: isAnswer ? validator.validation : null,
    ));
    if (isAnswer) _lastAnswerEventId = id;
  }

  /// Trẻ bấm "Xong". Một sự kiện, đúng loại, không đếm kép.
  SubmitOutcome submit(String answer) {
    assert(!finished);
    // ⭐⭐ A3: chấm QUA validator đã đăng ký — `ValidatedEvidence` là thứ duy
    // nhất được phép quyết `correct`. `grade` chỉ trả null khi validator
    // không nằm trong sổ — constructor đã chặn, nên nhánh dưới là chốt
    // fail-closed dự phòng: KHÔNG phát sự kiện trả lời nào (không có bằng
    // chứng giả), UI chỉ thấy «chưa đúng».
    final graded = validator.grade(answer);
    if (graded == null) return SubmitOutcome.wrong;
    final correct = graded.correct;
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

/// Nội dung gợi ý RULE-BASED — mẫu câu lấy từ CHÍNH PHƯƠNG PHÁP, số lấy từ
/// chính bài. Ba nấc tương ứng AutoTutor pump→hint→assertion (prior art WAL-64).
///
/// ⭐ WAL-168: hàm này KHÔNG còn biết phương pháp nào là phương pháp nào, và
/// không còn biết bài là phân số hay không. Thêm một phương pháp = thêm
/// [MethodHints] vào dòng dữ liệu của nó — không sửa hàm này.
///
/// Phương pháp chưa có mẫu câu ⇒ chuỗi rỗng: SAM im lặng chứ không bịa lời dạy.
String hintTextFor(TeachingMethod m, SupportLevel level, SolvableProblem p) {
  final h = m.hints;
  if (h == null || level == SupportLevel.none) return '';
  final template = switch (level) {
    SupportLevel.none => '',
    SupportLevel.hint => h.hint,
    SupportLevel.workedStep => h.workedStep,
    SupportLevel.fullSolution => h.fullSolution,
  };
  return h.fill(template, p.slots);
}
