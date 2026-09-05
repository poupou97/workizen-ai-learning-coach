/// ⭐⭐ WAL-181 — LEARNING MAP STATE: trạng thái NHẸ theo bằng chứng, không
/// phải điểm số (Founder Order 2026-09-04 §8: COVERAGE ≠ MASTERY).
///
/// KHÔNG dùng sao 1-3/%: cả hai đều ngầm hứa một phép đo liên tục mà dữ
/// liệu hôm nay không đủ để tính trung thực — CẤM số giả vờ chính xác đã là
/// doctrine có sẵn (`mission_center_screen.dart`). Đây là các trạng thái tính
/// được NGAY HÔM NAY từ [LearningEvent] lineage (WAL-178/179) cho MỌI bài,
/// không cần chờ có mô hình skillCase cho từng môn (hôm nay: 1/843 bài).
///
/// ⭐ Cố ý CHƯA có "cần ôn lại" — trạng thái đó cần review-schedule cấp
/// skillCase-của-bài mà 842/843 bài không có (degrade gracefully: thiếu dữ
/// liệu thì bớt trạng thái, không suy đoán). Thêm được sau, không phá enum
/// này — mỗi giá trị hiện có vẫn đúng nghĩa khi mở rộng.
///
/// ⭐⭐ WAL-210 — Founder D1 (2026-09-05): «Tự làm được» CHỈ từ bằng chứng tự
/// làm **đã chấm** (`correct == true`). Trước đây hàm này đọc MỌI
/// `independentAttempt` là 🔵 — kể cả cú chạm «Con đã trả lời xong» với
/// `correct: null` (audit C6b) — nên phụ huynh được nói «Con đã tự làm được»
/// từ một nút bấm. Nay tự báo/hoàn thành là trạng thái RIÊNG
/// ([LearningMapState.participation]), và dữ liệu cũ đọc theo cùng luật mà
/// không viết lại log.
library;

import 'learning_evidence.dart';

enum LearningMapState {
  /// ⚪ Không có sự kiện nào khớp lineage của bài này.
  unseen,

  /// 🟣 Trẻ ĐÃ LÀM XONG hoạt động của bài và TỰ BÁO (participation) — không
  /// chấm, không phải bằng chứng năng lực. Chỉ có loại sự kiện này ở bài.
  participation,

  /// 🟢 Có chạm tới bài cùng SAM (có gợi ý / có lần trả lời được chấm…) nhưng
  /// chưa có lần nào trẻ TỰ làm ĐÚNG **được kiểm**. ROUND 4: dữ liệu cũ có
  /// chấm-không-dấu (`historicalUnvalidated`) cũng nằm ở đây.
  engaged,

  /// 🔵 Có ít nhất một bằng chứng TỰ LÀM ĐƯỢC **đã kiểm** (independentAttempt/
  /// selfCorrection với `correct == true` + dấu validator được duyệt).
  independentEvidence,
}

/// Suy trạng thái của MỘT bài từ TOÀN BỘ event của learner (không lọc theo
/// môn trước — lineage tự lọc đúng sách+bài). Hàm THUẦN, không I/O — gọi
/// một lần trên danh sách event đã tải, không phải một lần cho mỗi bài.
///
/// Thứ tự ưu tiên: tự-làm-được-đã-chấm › học cùng SAM › tự báo › chưa học.
///
/// ⭐⭐ ROUND 4 (Founder §4 — STRICT EVIDENCE LÀ MẶC ĐỊNH): [requireValidation]
/// mặc định `true` ⇒ «Tự làm được» CHỈ từ sự kiện mang dấu validator được
/// đăng ký cấp năng lực (`hasApprovedValidation`). Sự kiện có chấm nhưng
/// KHÔNG dấu (dữ liệu trước hợp đồng, emitter chưa đóng dấu) đọc là
/// `historicalUnvalidated` ⇒ rơi xuống 🟢 `engaged` (đã học cùng SAM — chưa
/// có lần tự làm được ĐƯỢC KIỂM). Không viết lại log; không xoá gì.
/// `requireValidation: false` là LUẬT ĐỌC CŨ tường minh (#63) — chỉ để đối
/// chiếu/audit, không dùng cho màn hình trẻ/phụ huynh. Dấu LẠ bị từ chối ở
/// CẢ HAI chế độ.
LearningMapState learningMapStateFor({
  required String sourceDocumentId,
  required int lessonNo,
  required Iterable<LearningEvent> allEvents,
  bool requireValidation = true,
}) {
  final matching = allEvents.where((e) =>
      e.sourceDocumentId == sourceDocumentId && e.lessonNo == lessonNo);
  if (matching.isEmpty) return LearningMapState.unseen;
  if (matching.any((e) =>
      e.isValidatedIndependentSuccess ||
      (!requireValidation && e.isLegacyUnstampedSuccess))) {
    return LearningMapState.independentEvidence;
  }
  // Còn lại: có sự kiện KHÔNG phải tự báo (gợi ý, trả lời có chấm nhưng chưa
  // đúng, trả lời có hỗ trợ…) ⇒ engaged; toàn tự báo ⇒ participation.
  if (matching.any((e) => !e.isParticipation)) return LearningMapState.engaged;
  return LearningMapState.participation;
}

/// Nhãn + màu cho trẻ — chữ/ký hiệu, không phải số. Founder UX Constraint
/// 2026-09-04: badge nhỏ trong danh sách bài ĐÃ CÓ, không phải dashboard mới.
(String, String) childLabelFor(LearningMapState s) => switch (s) {
      LearningMapState.unseen => ('⚪', 'Chưa học'),
      // «Đã học» = đã làm xong hoạt động, tự báo — không nói gì về đúng/sai.
      LearningMapState.participation => ('🟣', 'Đã học'),
      LearningMapState.engaged => ('🟢', 'Đã học cùng SAM'),
      LearningMapState.independentEvidence => ('🔵', 'Tự làm được'),
    };
