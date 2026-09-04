/// ⭐⭐ WAL-183 — Adaptive Challenge Policy: tín hiệu độ khó tiếp theo
/// (🌱 Củng cố / 🎯 Vừa sức / 🚀 Thử thách) suy TRỰC TIẾP từ Learner
/// Capability đã có (`mastery.dart`) — không hệ tính riêng, không LLM.
///
/// CHỐNG DAO ĐỘNG: một câu trả lời đơn lẻ không được lật tín hiệu ĐÃ ỔN ĐỊNH.
/// Dùng hysteresis — ngưỡng VÀO một mức khó hơn ngưỡng RA khỏi mức đó — cùng
/// tinh thần với streak/threshold đã có tiền lệ ở `error_hypothesis.dart`.
library;

import '../student/mastery.dart';

/// KHÔNG phải nhãn trên hồ sơ trẻ — gắn theo MỘT SkillCase đang mở, tại một
/// thời điểm. Trẻ có thể "Thử thách" ở dạng này và "Củng cố" ở dạng khác
/// cùng lúc; không có "trẻ giỏi/kém" toàn cục nào được suy ra từ đây.
enum ChallengeSignal {
  /// 🌱 Còn yếu ở dạng này — củng cố lại, không đẩy khó hơn.
  consolidate,

  /// 🎯 Đang trong vùng luyện tập vừa sức.
  fit,

  /// 🚀 Đã vững — sẵn sàng thử thách hơn.
  stretch,
}

/// Hàm THUẦN. [previous] = tín hiệu đang hiển thị cho ca này (nếu có) —
/// truyền vào để chống dao động; bỏ trống (lần đầu hoặc không theo dõi) thì
/// dùng thẳng ngưỡng vào.
///
/// Trả `null` khi [case_] chưa có bằng chứng — UNKNOWN LÀ TRẠNG THÁI THẬT,
/// không mặc định 🎯.
ChallengeSignal? challengeSignalFor(
  CaseMastery case_, {
  ChallengeSignal? previous,
  double stretchEnter = 0.85,
  double stretchExit = 0.75,
  double consolidateEnter = 0.6,
  double consolidateExit = 0.7,
}) {
  assert(stretchExit <= stretchEnter,
      'ngưỡng RA khỏi stretch phải ≤ ngưỡng VÀO — nếu không hysteresis vô nghĩa');
  assert(consolidateExit >= consolidateEnter,
      'ngưỡng RA khỏi consolidate phải ≥ ngưỡng VÀO — nếu không hysteresis vô nghĩa');

  if (!case_.hasEvidence) return null;
  final p = case_.pMastery;

  // Đã ở một cực thì phải lùi qua ngưỡng RA (xa hơn ngưỡng VÀO) mới đổi —
  // một câu trả lời lệch nhẹ quanh biên không lật tín hiệu đã ổn định.
  if (previous == ChallengeSignal.stretch && p >= stretchExit) {
    return ChallengeSignal.stretch;
  }
  if (previous == ChallengeSignal.consolidate && p < consolidateExit) {
    return ChallengeSignal.consolidate;
  }

  if (p >= stretchEnter) return ChallengeSignal.stretch;
  if (p < consolidateEnter) return ChallengeSignal.consolidate;
  return ChallengeSignal.fit;
}

/// Icon+nhãn ngắn cho tín hiệu — CẤM %, CẤM số, đúng nguyên tắc gamification
/// nhẹ (Founder Order 2026-09-04): trình bày tiến bộ, không đo lường giả vờ
/// chính xác.
(String icon, String label) challengeLabelFor(ChallengeSignal s) => switch (s) {
      ChallengeSignal.consolidate => ('🌱', 'Củng cố'),
      ChallengeSignal.fit => ('🎯', 'Vừa sức'),
      ChallengeSignal.stretch => ('🚀', 'Thử thách'),
    };
