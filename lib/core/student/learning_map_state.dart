/// ⭐⭐ WAL-181 — LEARNING MAP STATE: trạng thái NHẸ theo bằng chứng, không
/// phải điểm số (Founder Order 2026-09-04 §8: COVERAGE ≠ MASTERY).
///
/// KHÔNG dùng sao 1-3/%: cả hai đều ngầm hứa một phép đo liên tục mà dữ
/// liệu hôm nay không đủ để tính trung thực — CẤM số giả vờ chính xác đã là
/// doctrine có sẵn (`mission_center_screen.dart`). Đây là 3 trạng thái tính
/// được NGAY HÔM NAY từ [LearningEvent] lineage (WAL-178/179) cho MỌI bài,
/// không cần chờ có mô hình skillCase cho từng môn (hôm nay: 1/843 bài).
///
/// ⭐ Cố ý CHƯA có "cần ôn lại" — trạng thái đó cần review-schedule cấp
/// skillCase-của-bài mà 842/843 bài không có (degrade gracefully: thiếu dữ
/// liệu thì bớt trạng thái, không suy đoán). Thêm được sau, không phá enum
/// này — mỗi giá trị hiện có vẫn đúng nghĩa khi mở rộng.
library;

import 'learning_evidence.dart';

enum LearningMapState {
  /// ⚪ Không có sự kiện nào khớp lineage của bài này.
  unseen,

  /// 🟢 Có chạm tới bài (session/evidence tồn tại) nhưng chưa có lần nào
  /// trẻ TỰ làm không cần hỗ trợ.
  engaged,

  /// 🔵 Có ít nhất một bằng chứng TỰ LÀM (independentAttempt/selfCorrection).
  independentEvidence,
}

/// Suy trạng thái của MỘT bài từ TOÀN BỘ event của learner (không lọc theo
/// môn trước — lineage tự lọc đúng sách+bài). Hàm THUẦN, không I/O — gọi
/// một lần trên danh sách event đã tải, không phải một lần cho mỗi bài.
LearningMapState learningMapStateFor({
  required String sourceDocumentId,
  required int lessonNo,
  required Iterable<LearningEvent> allEvents,
}) {
  final matching = allEvents.where((e) =>
      e.sourceDocumentId == sourceDocumentId && e.lessonNo == lessonNo);
  if (matching.isEmpty) return LearningMapState.unseen;
  final hasIndependent = matching.any((e) =>
      e.kind == EvidenceKind.independentAttempt ||
      e.kind == EvidenceKind.selfCorrection);
  return hasIndependent
      ? LearningMapState.independentEvidence
      : LearningMapState.engaged;
}

/// Nhãn + màu cho trẻ — chữ/ký hiệu, không phải số. Founder UX Constraint
/// 2026-09-04: badge nhỏ trong danh sách bài ĐÃ CÓ, không phải dashboard mới.
(String, String) childLabelFor(LearningMapState s) => switch (s) {
      LearningMapState.unseen => ('⚪', 'Chưa học'),
      LearningMapState.engaged => ('🟢', 'Đã học cùng SAM'),
      LearningMapState.independentEvidence => ('🔵', 'Tự làm được'),
    };
