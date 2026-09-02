/// WAL-149 KS-B — CỔNG TRẠNG THÁI Knowledge Stories (§28 Founder Order #4).
///
/// Bất biến (mutation-guarded):
/// - CHỈ [StoryStatus.verified] được lên production — AUTO_VERIFIED là kết
///   quả máy, chưa qua người chấm, KHÔNG đủ (§28: candidate confidence thấp
///   không tự lên production; PRECISION > RECALL).
/// - Direct-quote render CHỈ khi verified — attribution không chắc thì không
///   bao giờ hiển thị như lời danh nhân (§7; ca Ga-li-lê/«Lê Nguyên Long»).
/// - «Ngày này năm xưa» đòi verified + NGÀY đủ tin cậy — không suy đoán (§14).
library;

enum StoryStatus { candidate, autoVerified, reviewRequired, verified, rejected }

/// Cổng production duy nhất.
bool canShowInProduction(StoryStatus s) => s == StoryStatus.verified;

/// Quote hiển thị NHƯ LỜI NÓI TRỰC TIẾP của danh nhân.
bool canRenderAsDirectQuote(StoryStatus s) => s == StoryStatus.verified;

/// Đủ điều kiện vào pool «Ngày này năm xưa».
bool todayCardEligible({
  required StoryStatus status,
  required bool hasReliableMonthDay,
}) =>
    status == StoryStatus.verified && hasReliableMonthDay;

StoryStatus storyStatusFrom(String raw) => switch (raw) {
      'AUTO_VERIFIED' => StoryStatus.autoVerified,
      'REVIEW_REQUIRED' => StoryStatus.reviewRequired,
      'VERIFIED' => StoryStatus.verified,
      'REJECTED' => StoryStatus.rejected,
      _ => StoryStatus.candidate, // lạ ⇒ mức thấp nhất, không đoán lên
    };
