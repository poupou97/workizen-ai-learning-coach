/// ⭐⭐ WAL-210 round 3 (A-runtime, Founder A3) — VALIDATED EVIDENCE CONTRACT.
///
/// «SELF REPORT ≠ COMPETENCE.» Chuỗi bắt buộc để một hành động của trẻ trở
/// thành bằng chứng NĂNG LỰC:
///
///   LearnerAction → EvidenceValidator (đã đăng ký, tất định)
///     → ValidatedEvidence (mang validatorId + validatorVersion)
///     → LearningEvent.validation → Student Knowledge State
///
/// Ba bất biến giữ bằng kiểu + test:
/// - [ValidatedEvidence] có constructor RIÊNG TƯ của thư viện này: chỉ một
///   [DeterministicValidator] (lớp cơ sở ở đây) mới mint được. Không có
///   đường nào từ UI, từ kịch bản, từ LLM tới một `ValidatedEvidence`.
/// - [EvidenceValidation] là DẤU trên sự kiện. Dấu chỉ có giá trị năng lực
///   khi `validatorId` nằm trong [approvedEvidenceValidators] VÀ mục đó khai
///   `grantsCompetence`. Dấu lạ ⇒ FAIL CLOSED (đọc như chưa kiểm chứng, không
///   đẩy mastery, không «Tự làm được»).
/// - Surface Scale (Reader/Quiz chọn đáp án theo khoá pack, tự báo…) KHÔNG
///   có validator ở đây — không bịa validator cho chúng (Founder A3).
///
/// Trạng thái: PROPOSED (D2). Sự kiện CŨ trên đĩa không có dấu — luật đọc
/// dữ liệu cũ nằm ở `LearningEvent.hasApprovedValidation` / policy BKT; xem
/// docs/architecture/ROUND3-RUNTIME-CONTRACTS.md §A3.
library;

import '../curriculum/fraction_problem.dart';
import '../curriculum/solvable_problem.dart';

/// Dấu kiểm chứng trên MỘT sự kiện: ai chấm, phiên bản nào.
class EvidenceValidation {
  const EvidenceValidation({
    required this.validatorId,
    required this.validatorVersion,
  });

  /// Định danh validator, vd `fraction-check-v1`. Ổn định — nằm trên đĩa.
  final String validatorId;

  /// Phiên bản CÀI ĐẶT của validator (đổi khi luật chấm đổi mà id giữ).
  final String validatorVersion;

  /// Có nằm trong sổ đăng ký và được phép tạo bằng chứng năng lực không.
  /// `false` cho mọi id lạ — fail closed.
  bool get grantsCompetence =>
      approvedEvidenceValidators[validatorId]?.grantsCompetence ?? false;

  /// Có trong sổ đăng ký (kể cả validator chỉ cấp participation).
  bool get isRegistered => approvedEvidenceValidators.containsKey(validatorId);

  Map<String, Object?> toJson() => {
        'validatorId': validatorId,
        'validatorVersion': validatorVersion,
      };

  /// Fail closed: thiếu/lệch kiểu ⇒ `null` (đọc như chưa kiểm chứng).
  static EvidenceValidation? fromJson(Object? v) {
    if (v is! Map) return null;
    final id = v['validatorId'], ver = v['validatorVersion'];
    if (id is! String || ver is! String || id.isEmpty || ver.isEmpty) {
      return null;
    }
    return EvidenceValidation(validatorId: id, validatorVersion: ver);
  }

  @override
  bool operator ==(Object other) =>
      other is EvidenceValidation &&
      other.validatorId == validatorId &&
      other.validatorVersion == validatorVersion;

  @override
  int get hashCode => Object.hash(validatorId, validatorVersion);

  @override
  String toString() => '$validatorId@$validatorVersion';
}

/// Một mục trong sổ đăng ký validator.
class ValidatorRegistration {
  const ValidatorRegistration({
    required this.validatorId,
    required this.description,
    required this.grantsCompetence,
    required this.deterministic,
  });

  final String validatorId;
  final String description;

  /// `true` ⇒ sự kiện `correct == true` mang dấu này được phép đẩy mastery /
  /// thành «Tự làm được». `false` ⇒ chỉ ghi nhận THAM GIA.
  final bool grantsCompetence;

  /// Mọi validator được đăng ký hôm nay đều tất định. Trường này tồn tại để
  /// một validator không-tất-định (LLM-judge…) KHÔNG THỂ được đăng ký mà
  /// không khai — và test chặn `deterministic == false`.
  final bool deterministic;
}

/// ⭐ SỔ ĐĂNG KÝ — danh sách đóng. Thêm validator = thêm một dòng ở đây + một
/// lớp con [DeterministicValidator] + test. Không có đường đăng ký lúc chạy.
const Map<String, ValidatorRegistration> approvedEvidenceValidators = {
  // Đường Deep (Toán 5 slice): chấm `a/b ± c/d` bằng số học phân số —
  // `FractionProblem.checkAnswer`. Tất định, kiểm được, có test golden.
  'fraction-check-v1': ValidatorRegistration(
    validatorId: 'fraction-check-v1',
    description:
        'Chấm đáp án phân số a/b ± c/d bằng số học (FractionProblem.checkAnswer)',
    grantsCompetence: true,
    deterministic: true,
  ),
  // Cửa `validateCandidateEvidence` (Thí nghiệm / quan sát tự do): chỉ
  // kiểm «có chất liệu + không phải tra cứu» — cấp PARTICIPATION, không
  // bao giờ cấp năng lực (Founder D1, #63).
  'candidate-gate-v1': ValidatorRegistration(
    validatorId: 'candidate-gate-v1',
    description: 'Cổng claim tự do → participation (không chấm đúng/sai)',
    grantsCompetence: false,
    deterministic: true,
  ),
};

/// ⭐ Kết quả chấm ĐÃ KIỂM CHỨNG — chỉ [DeterministicValidator] mint được.
final class ValidatedEvidence {
  const ValidatedEvidence._({required this.correct, required this.validation});

  final bool correct;
  final EvidenceValidation validation;
}

/// Lớp cơ sở của mọi validator được đăng ký. `base` ⇒ lớp con phải nằm
/// trong cây kế thừa này; [grade] là đường DUY NHẤT tới `ValidatedEvidence._`.
abstract base class DeterministicValidator {
  const DeterministicValidator();

  String get validatorId;
  String get validatorVersion;

  EvidenceValidation get validation => EvidenceValidation(
      validatorId: validatorId, validatorVersion: validatorVersion);

  /// Luật chấm thuần — lớp con cài. Fail closed: không đọc được ⇒ `false`.
  bool check(String rawAnswer);

  /// Chấm và đóng dấu. Validator CHƯA đăng ký thì không mint được gì —
  /// trả `null` chứ không đóng dấu giả (fail closed).
  ValidatedEvidence? grade(String rawAnswer) {
    if (!validation.isRegistered) return null;
    return ValidatedEvidence._(correct: check(rawAnswer), validation: validation);
  }
}

/// `fraction-check-v1` — bọc [FractionProblem.checkAnswer].
final class FractionCheckValidator extends DeterministicValidator {
  const FractionCheckValidator(this.problem);
  final FractionProblem problem;

  @override
  String get validatorId => 'fraction-check-v1';

  @override
  String get validatorVersion => '1';

  @override
  bool check(String rawAnswer) => problem.checkAnswer(rawAnswer);
}

/// Validator ĐÃ ĐĂNG KÝ cho một bài. `null` = loại bài chưa có validator ⇒
/// tầng dạy không được chấm thành bằng chứng năng lực (fail closed).
DeterministicValidator? approvedValidatorFor(SolvableProblem problem) =>
    switch (problem) {
      FractionProblem() => FractionCheckValidator(problem),
      _ => null,
    };
