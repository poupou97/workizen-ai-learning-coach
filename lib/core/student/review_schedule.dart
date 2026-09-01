/// ⭐ F5 — Lịch ôn tập: TÁCH KHỎI ước lượng tri thức.
///
/// Founder (2026-09-01): *"Mastery is not permanent... Keep distinction:
/// knowledge estimate vs review scheduling. Do not collapse them prematurely."*
///
/// Điều tra (SM-2 · FSRS · skillcoco · BKT-forget · dkt_forget của EduStudio):
///
/// - Kết quả TÁI LẶP NHẤT của cả nhánh văn liệu spaced-repetition là **hình
///   dạng giãn nở** của khoảng ôn (mỗi lần ôn thành công ⇒ khoảng kế dài ra).
///   SM-2, FSRS, Leitner chỉ khác nhau ở tham số — cùng một hình dạng.
/// - **Hằng số chính xác thì KHÔNG có justification** cho học sinh Việt Nam
///   lớp 5 học phân số: mọi bộ số công bố đều khớp trên dữ liệu flashcard
///   người lớn. ⇒ hình dạng vào kiến trúc, hằng số vào policy có tên, chờ
///   dữ liệu thật.
/// - BKT-forget (thêm P(quên) mỗi bước) ĐỔI pMastery theo thời gian. Chưa
///   dùng: nó sập hai câu hỏi vào một — *"con còn nhớ không?"* (ước lượng)
///   và *"bao giờ nên ôn?"* (lịch). Founder cấm sập sớm. Khi có dữ liệu
///   thật, bật BKT-forget là đổi `EvidenceWeightingPolicy` + replay — log
///   thô đã có timestamp từ F3, không cần migration.
///
/// Phân công hiện tại của ba thứ LIÊN QUAN thời gian — không giẫm nhau:
///
/// | Câu hỏi | Nơi trả lời |
/// |---|---|
/// | Claim với phụ huynh còn được bảo chứng không? | `ConfidenceFactors.recency` (F1) |
/// | pMastery có tự tụt theo thời gian không?      | CHƯA — chờ BKT-forget có dữ liệu |
/// | Bao giờ nên đưa bài ôn?                       | tệp này |
library;

import 'mastery.dart';

/// Mức khẩn của việc ôn MỘT ca.
enum ReviewUrgency {
  /// Chưa có bằng chứng độc lập nào ⇒ không có gì để "ôn" — cần HỌC/ĐO,
  /// không phải review. Gộp hai thứ là gửi bài ôn cho thứ chưa từng học.
  nothingToReview,

  /// Trong khoảng — chưa cần ôn.
  fresh,

  /// Tới hạn ôn.
  reviewDue,

  /// Quá hạn lâu — ưu tiên trước các ca `reviewDue`.
  overdue,
}

/// Tham số lịch ôn — **có tên, có lý do, thay được** (doctrine ADR-004).
class ReviewPolicy {
  const ReviewPolicy({
    this.baseInterval = const Duration(days: 7),
    this.growthFactor = 2.0,
    this.maxGrowthSteps = 4,
    this.overdueGraceFactor = 1.0,
  });

  /// 7 ngày — nhịp tuần học phổ thông: bài tuần này gặp lại đầu tuần sau.
  /// GIẢ THUYẾT chờ dữ liệu, nhưng neo vào một nhịp có thật của trường học.
  final Duration baseInterval;

  /// 2.0 — hình dạng giãn nở (chuẩn của cả họ SM-2/Leitner); 2 là đáy bảo
  /// thủ của dải EF 1.3–2.5 trong SM-2: thà gọi ôn sớm còn hơn để quên.
  final double growthFactor;

  /// Chặn trên 4 bước ⇒ khoảng dài nhất 7×2⁴ = 112 ngày < một học kỳ —
  /// không khoảng ôn nào được vượt qua một kỳ nghỉ hè mà không gặp lại.
  final int maxGrowthSteps;

  /// Quá hạn thêm MỘT khoảng nữa ⇒ `overdue`.
  final double overdueGraceFactor;
}

/// Trạng thái lịch ôn của một ca — SUY RA, không lưu.
class ReviewState {
  const ReviewState({required this.urgency, required this.nextReviewAt});

  final ReviewUrgency urgency;

  /// `null` khi không có gì để ôn.
  final DateTime? nextReviewAt;
}

/// ⭐ Suy trạng thái ôn từ bằng chứng. KHÔNG đụng vào `pMastery` — bất biến
/// tách-hai-câu-hỏi nằm ở chữ ký hàm: nhận `CaseMastery`, trả `ReviewState`,
/// không có đường ghi ngược.
ReviewState reviewStateOf(
  CaseMastery c,
  DateTime now, {
  ReviewPolicy policy = const ReviewPolicy(),
}) {
  final last = c.lastIndependentEvidenceAt;
  if (!c.hasEvidence || last == null) {
    return const ReviewState(
        urgency: ReviewUrgency.nothingToReview, nextReviewAt: null);
  }

  // Khoảng giãn nở theo LƯỢNG bằng chứng độc lập — mỗi bằng chứng thêm là
  // một lần "gặp lại thành công" theo nghĩa spaced-repetition.
  var steps = c.evidenceCount - 1;
  if (steps > policy.maxGrowthSteps) steps = policy.maxGrowthSteps;
  var factor = 1.0;
  for (var i = 0; i < steps; i++) {
    factor *= policy.growthFactor;
  }
  final interval = Duration(
      seconds: (policy.baseInterval.inSeconds * factor).round());
  final due = last.add(interval);
  final overdueAt = due.add(Duration(
      seconds: (interval.inSeconds * policy.overdueGraceFactor).round()));

  final urgency = now.isBefore(due)
      ? ReviewUrgency.fresh
      : now.isBefore(overdueAt)
          ? ReviewUrgency.reviewDue
          : ReviewUrgency.overdue;
  return ReviewState(urgency: urgency, nextReviewAt: due);
}
