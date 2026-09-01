/// ⭐ SkillCase — tầng trung gian giữa Khái niệm và Phương pháp.
///
/// Vì sao cần: đo từ corpus KNTT, khái niệm `quy-dong` có **hai ca**, dạy ở
/// **hai lớp**, bằng **hai phương pháp**:
///
/// | Ca | Điều kiện | Phương pháp | Dạy ở |
/// |---|---|---|---|
/// | chia hết | mẫu này chia hết cho mẫu kia | lấy mẫu lớn, giữ nguyên một phân số | lớp 4, tr.62 |
/// | không chia hết | không chia hết cho nhau | lấy **tích** hai mẫu | lớp 5, tr.20 |
///
/// ⇒ Học sinh có thể **nắm một phần** một khái niệm. Sai bài lớp 5 KHÔNG suy ra
/// "không hiểu quy đồng" — có thể em ấy vững ca lớp 4 và bối rối vì **luật đổi**.
/// Đó là ca chẩn đoán riêng, và can thiệp khác hẳn: **đối chiếu hai ca**, không
/// dạy lại từ đầu.
library;

class SkillCase {
  const SkillCase({
    required this.id,
    required this.conceptId,
    required this.condition,
    required this.introducedGrade,
  });

  final String id;
  final String conceptId;

  /// Điều kiện **theo lời sách**, không phải theo cách ta diễn đạt lại.
  /// Lớp 5 tr.20: *"Hai mẫu số 5 và 2 không chia hết cho nhau."*
  final String condition;

  /// `null` = corpus chưa có bài dạy ca này.
  final int? introducedGrade;
}

/// Chẩn đoán — **bảy khả năng, không phải hai**.
///
/// Gộp tất cả vào "sai/đúng" là mất chính thông tin quyết định can thiệp.
enum DiagnosticOutcome {
  conceptGap,
  prerequisiteGap,
  methodGap,

  /// ⭐ Vững ca cũ, chưa vững ca mới. Ca này chỉ nhìn ra khi mô hình có
  /// SkillCase — nếu không, nó bị chẩn đoán nhầm thành `conceptGap` và đứa trẻ
  /// phải học lại thứ nó đã biết.
  caseTransitionGap,

  /// Biết phương pháp, sai số học.
  executionError,
  carelessError,

  /// Chưa đủ bằng chứng. **Là câu trả lời hợp lệ**, không phải thất bại.
  insufficientEvidence,

  /// ⭐ F6 — bài ĐA KỸ NĂNG sai, và ≥2 thành phần chưa vững: biết là hỏng,
  /// CHƯA biết hỏng ở thành phần nào. Trước khi có giá trị này, engine buộc
  /// phải quy lỗi cho một concept — quy lỗi sai địa chỉ tệ hơn không quy lỗi
  /// (ADR-003 §F6).
  attributionUnresolved,
}

/// Can thiệp tương ứng. Ánh xạ vét cạn — thêm một chẩn đoán mà quên quyết định
/// can thiệp thì không biên dịch được.
enum LearningAction {
  teach,
  practice,
  review,
  diagnosePrerequisite,
  remediate,

  /// ⭐ Đối chiếu hai ca — can thiệp cho `caseTransitionGap`.
  /// *"Con đã biết làm khi một mẫu số chia hết cho mẫu kia. Bài này khác:
  /// hai mẫu không chia hết cho nhau. Mình thử so hai trường hợp nhé."*
  contrastCases,

  /// ⭐ F6 — cô lập kỹ năng: ra vài bài NGẮN, mỗi bài chạm đúng MỘT thành
  /// phần, để tìm thành phần hỏng thay vì đoán. Chính là "chẩn đoán theo
  /// prerequisite graph" của tài liệu nghiên cứu: log₂(k) câu thay vì dạy
  /// lại cả k thành phần.
  isolateSkills,

  challenge,
  advance,
  revisit,
  rest,
}

LearningAction actionFor(DiagnosticOutcome d) => switch (d) {
      DiagnosticOutcome.conceptGap => LearningAction.teach,
      DiagnosticOutcome.prerequisiteGap => LearningAction.diagnosePrerequisite,
      DiagnosticOutcome.methodGap => LearningAction.teach,
      DiagnosticOutcome.caseTransitionGap => LearningAction.contrastCases,
      DiagnosticOutcome.executionError => LearningAction.practice,
      DiagnosticOutcome.carelessError => LearningAction.practice,
      DiagnosticOutcome.insufficientEvidence => LearningAction.diagnosePrerequisite,
      DiagnosticOutcome.attributionUnresolved => LearningAction.isolateSkills,
    };
