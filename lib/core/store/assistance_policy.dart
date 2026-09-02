/// WAL-104 — AssistancePolicy: bài GIAO khác bài TỰ HỌC ở LUẬT HỖ TRỢ,
/// không phải ở một SessionMode mới.
///
/// Falsification (docs/research/SAM-ASSIGNMENT-MODEL-RESEARCH.md): một nửa
/// đã tồn tại (learn/assess + tutoringViolationsInExam). Đây CHỈ là bảng ánh
/// xạ tất định policy → tham số sẵn có — không nhân khái niệm.
library;

import '../student/mastery.dart';
import 'learning_session.dart';

enum AssistancePolicy { practice, homework, mock, assessment }

/// Bộ luật một policy áp lên phiên — toàn tham số ĐÃ TỒN TẠI.
class AssistanceRules {
  const AssistanceRules({
    required this.mode,
    required this.supportCap,
    required this.revealAllowed,
    required this.reviewAfter,
  });

  final SessionMode mode;

  /// Trần SupportLevel surface được phát. Thang ±1 chạy BÊN DƯỚI trần.
  final SupportLevel supportCap;

  /// REVEAL lời giải trọn vẹn. HOMEWORK khoá: sản phẩm nộp phải là CỦA TRẺ
  /// (EEF: giúp-làm-bài-tập không nâng attainment — «làm hộ» là failure
  /// mode có meta-analysis, luật cấu trúc không phải prompt).
  final bool revealAllowed;

  /// Được xem lại + luyện lại sau khi nộp. MOCK ≠ ASSESSMENT chỉ ở đây.
  final bool reviewAfter;
}

AssistanceRules rulesFor(AssistancePolicy p) => switch (p) {
      AssistancePolicy.practice => const AssistanceRules(
          mode: SessionMode.learn,
          supportCap: SupportLevel.fullSolution,
          revealAllowed: true,
          reviewAfter: true,
        ),
      AssistancePolicy.homework => const AssistanceRules(
          mode: SessionMode.learn,
          supportCap: SupportLevel.workedStep,
          revealAllowed: false,
          reviewAfter: true,
        ),
      AssistancePolicy.mock => const AssistanceRules(
          mode: SessionMode.assess,
          supportCap: SupportLevel.none,
          revealAllowed: false,
          reviewAfter: true,
        ),
      AssistancePolicy.assessment => const AssistanceRules(
          mode: SessionMode.assess,
          supportCap: SupportLevel.none,
          revealAllowed: false,
          reviewAfter: false,
        ),
    };

/// Hậu kiểm trần hỗ trợ — cùng họ với eval L1: sự kiện vượt trần của policy.
/// (assess đã có tutoringViolationsInExam; hàm này phủ thêm learn-có-trần.)
List<String> supportCapViolations(LearningSession s, AssistancePolicy p) {
  final cap = rulesFor(p).supportCap;
  return [
    for (final e in s.events)
      if (e.support != null && e.support!.index > cap.index) e.eventId
  ];
}
