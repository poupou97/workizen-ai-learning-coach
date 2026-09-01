/// ⭐⭐⭐ WAL-64 — Perception Provenance: bất biến §11/§12 do KIỂU giữ hộ.
///
///   UNCONFIRMED MACHINE PERCEPTION MUST NOT ENTER LEARNING EVIDENCE.
///
/// Bằng chứng ép ra bất biến này (PHONE-SIM + WAL-62): chuỗi perception có
/// thể lắp ráp biểu thức BỊA với conf cao trên ảnh xấu; conf của OCR vô dụng
/// làm cổng; đồng thuận đa view chỉ là tiền-lọc. ⇒ Ranh giới tin cậy duy
/// nhất là XÁC NHẬN CỦA HỌC SINH, và ranh giới đó phải nằm trong hệ kiểu —
/// không nằm trong kỷ luật của người gọi.
///
/// Ba mảnh, ba vai:
/// - [PerceptionHypothesis] — máy ĐOÁN gì. Bất biến, KHÔNG BAO GIỜ bị sửa.
/// - [ConfirmedProblem]     — trẻ XÁC NHẬN gì. Bản ghi MỚI trỏ về hypothesis;
///   sửa của người không ghi đè lịch sử máy (cùng doctrine append-only F3).
/// - Đường vào evidence: mã sinh LearningEvent từ camera phải đi qua
///   `ConfirmedProblem.exerciseId` — không có constructor nào nhận thẳng
///   hypothesis.
///
/// Những gì CỐ Ý không thêm (đối chiếu danh sách §12, chỉ giữ cái bất biến
/// đòi — replay audit §G đã chứng minh mapping nướng-lúc-ghi lo phần version):
/// knowledge-model version, TutorScope version, mapping version — KHÔNG cần
/// trên bản ghi perception; chúng đã bất biến hoá qua denormalization của
/// LearningEvent (xem replay_audit_test).
library;

/// Giả thuyết của MÁY về bài toán trong ảnh. **Bất biến.**
class PerceptionHypothesis {
  const PerceptionHypothesis({
    required this.hypothesisId,
    required this.rawImageRef,
    required this.expression,
    required this.pipelineVersion,
    required this.at,
    this.consensusVotes,
    this.viewCount,
  });

  final String hypothesisId;

  /// Tham chiếu ảnh gốc (id/hash — KHÔNG phải đường dẫn tuyệt đối; ảnh trẻ
  /// em là dữ liệu nhạy cảm, chính sách lưu/xoá thuộc WAL-44).
  final String rawImageRef;

  /// Biểu thức máy đọc được, đúng nguyên văn pipeline phát ra.
  final String expression;

  /// Pipeline nào sinh ra — để đối chiếu benchmark WAL-63 theo phiên bản.
  final String pipelineVersion;

  final DateTime at;

  /// Số phiếu đồng thuận multi-view (WAL-62) — tiền-lọc, KHÔNG phải cổng.
  final int? consensusVotes;
  final int? viewCount;
}

/// Trẻ đã xác nhận/sửa như thế nào.
enum ConfirmationKind { confirmedAsIs, corrected, retaken }

/// ⭐⭐ Bài toán ĐÃ ĐƯỢC TRẺ XÁC NHẬN — thứ DUY NHẤT được phép chảy tiếp vào
/// ExerciseSkillMap → LearningEvidence.
///
/// Là bản ghi MỚI trỏ về hypothesis; hypothesis gốc còn nguyên vẹn vĩnh viễn
/// (đo được Student Correction Rate #5 của WAL-63 chính từ cặp bản ghi này).
class ConfirmedProblem {
  ConfirmedProblem._({
    required this.problemId,
    required this.hypothesisId,
    required this.expression,
    required this.kind,
    required this.confirmedAt,
  });

  /// Cổng DUY NHẤT: phải cầm một [PerceptionHypothesis] thật mới tạo được.
  /// [correctedExpression] `null` = trẻ xác nhận nguyên văn.
  factory ConfirmedProblem.confirm(
    PerceptionHypothesis h, {
    String? correctedExpression,
    required DateTime at,
  }) {
    final corrected =
        correctedExpression != null && correctedExpression != h.expression;
    return ConfirmedProblem._(
      problemId: 'cp:${h.hypothesisId}@${at.microsecondsSinceEpoch}',
      hypothesisId: h.hypothesisId,
      expression: corrected ? correctedExpression : h.expression,
      kind: corrected
          ? ConfirmationKind.corrected
          : ConfirmationKind.confirmedAsIs,
      confirmedAt: at,
    );
  }

  final String problemId;

  /// Lineage về giả thuyết máy — mọi mastery-changing event lần ngược được
  /// tới đúng biểu diễn bài toán mà trẻ đã xác nhận, và từ đó tới ảnh gốc.
  final String hypothesisId;

  final String expression;
  final ConfirmationKind kind;
  final DateTime confirmedAt;

  /// ⭐ ID để làm `ExerciseSkillMap.exerciseId` cho bài gốc-camera. Đây là
  /// mắt xích kiểu: đường sinh evidence từ camera nhận ConfirmedProblem,
  /// không nhận PerceptionHypothesis — unconfirmed không có exerciseId.
  String get exerciseId => problemId;
}
