/// ⭐⭐ WAL-72 — CanonicalProblem: định danh bài toán NGUỒN-BẤT-KHẢ-TRI.
///
/// Kết quả falsification §1 (review Founder 2026-09-01):
/// - KHÔNG overfit: bài không-camera chưa từng bị ép qua xác nhận giả
///   (`exerciseId` là String tự do — curriculum test vẫn dùng 'ex-…' thẳng).
/// - NHƯNG under-enforcement: chính vì String tự do, không gì CẤM mã camera
///   mint id thô bỏ qua ConfirmedProblem — bảo đảm §11 yếu hơn quảng cáo.
///
/// Sửa: MỌI nguồn bài toán mint định danh qua đây, mỗi nguồn một factory với
/// provenance ĐÚNG CỦA NGUỒN ĐÓ:
/// - camera        → factory BẮT BUỘC cầm [ConfirmedProblem] (compile-level;
///                   PerceptionHypothesis không có đường vào)
/// - curriculum    → mint thẳng từ Provenance sách — KHÔNG xác nhận giả
/// - manual        → trẻ tự gõ — chính trẻ là nguồn, không cần confirm
/// - imported      → phiếu bài tập nhập vào — mang ref nguồn nhập
/// - generated     → hệ sinh bài luyện — mang generatorId (audit được ai sinh)
library;

import '../knowledge/provenance.dart';
import '../perception/perception_provenance.dart';

enum ProblemOrigin {
  curriculumExercise,
  confirmedPerception,
  manualInput,
  importedWorksheet,
  generatedPractice,
}

class CanonicalProblem {
  const CanonicalProblem._({
    required this.exerciseId,
    required this.origin,
    required this.expression,
    this.curriculumProvenance,
    this.confirmedProblemId,
    this.generatorId,
    this.importRef,
    this.at,
  });

  /// Bài trong SÁCH — provenance là Provenance chuẩn của corpus (trang IN,
  /// nguồn, citable…). Không đi qua bất kỳ "xác nhận" nào — sách là nguồn tin.
  factory CanonicalProblem.fromCurriculum({
    required String exerciseLabel,
    required String expression,
    required Provenance provenance,
  }) =>
      CanonicalProblem._(
        exerciseId: 'cur:${provenance.sourceId}'
            ':p${provenance.pageStart ?? 0}:$exerciseLabel',
        origin: ProblemOrigin.curriculumExercise,
        expression: expression,
        curriculumProvenance: provenance,
      );

  /// ⭐ Bài từ CAMERA — chữ ký ĐÒI [ConfirmedProblem]: perception chưa xác
  /// nhận không có kiểu nào lọt vào đây. Đây là chỗ under-enforcement được vá.
  factory CanonicalProblem.fromConfirmedPerception(ConfirmedProblem p) =>
      CanonicalProblem._(
        exerciseId: p.exerciseId, // 'cp:…' — giữ nguyên lineage hypothesis
        origin: ProblemOrigin.confirmedPerception,
        expression: p.expression,
        confirmedProblemId: p.problemId,
      );

  /// Trẻ tự gõ đề. Nguồn là chính trẻ — không cần confirm, nhưng ghi thời điểm.
  factory CanonicalProblem.fromManualInput({
    required String expression,
    required DateTime at,
  }) =>
      CanonicalProblem._(
        exerciseId: 'man:${at.microsecondsSinceEpoch}',
        origin: ProblemOrigin.manualInput,
        expression: expression,
        at: at,
      );

  /// Phiếu bài tập nhập (file/scan phiếu của giáo viên…).
  factory CanonicalProblem.fromImportedWorksheet({
    required String importRef,
    required String exerciseLabel,
    required String expression,
  }) =>
      CanonicalProblem._(
        exerciseId: 'imp:$importRef:$exerciseLabel',
        origin: ProblemOrigin.importedWorksheet,
        expression: expression,
        importRef: importRef,
      );

  /// Bài LUYỆN do hệ sinh — generatorId để audit "ai sinh bài này bằng luật gì".
  factory CanonicalProblem.fromGeneratedPractice({
    required String generatorId,
    required String expression,
    required DateTime at,
  }) =>
      CanonicalProblem._(
        exerciseId: 'gen:$generatorId:${at.microsecondsSinceEpoch}',
        origin: ProblemOrigin.generatedPractice,
        expression: expression,
        generatorId: generatorId,
        at: at,
      );

  /// Định danh dùng cho `ExerciseSkillMap.exerciseId` — prefix mã hoá origin
  /// nên mọi LearningEvent lần ngược được về ĐÚNG loại nguồn (§8E).
  final String exerciseId;
  final ProblemOrigin origin;
  final String expression;

  final Provenance? curriculumProvenance;
  final String? confirmedProblemId;
  final String? generatorId;
  final String? importRef;
  final DateTime? at;
}
