/// ⭐ WAL-46 — Design tokens «Học cùng SAM». Nguồn: logo.png (palette thật) +
/// DESIGN-SYSTEM-DIRECTION.md. LUẬT CỨNG (bài học Tổng Tài WTM-168, đo được):
/// màu bước -500 là màu NỀN/ICON; CHỮ dùng cặp -700 — và mọi cặp chữ/nền ở
/// đây được KIỂM BẰNG TEST WCAG ≥ 4.5:1 (wal_tokens_contrast_test.dart).
/// Đổi một màu mà quên cặp của nó ⇒ test đỏ, không cần design review bắt.
library;

import 'dart:ui';

abstract final class WalColors {
  // ── Nền ──
  static const surface = Color(0xFFF7F7FC);
  static const surfaceLavender = Color(0xFFF3EEFF);
  static const white = Color(0xFFFFFFFF);

  // ── -500: NỀN/ICON/BIỂU ĐỒ — cấm làm chữ trên nền sáng ──
  static const primary500 = Color(0xFF7C4DFF); // tím SAM
  static const accent500 = Color(0xFFFFB800); // vàng ấm — KHÔNG BAO GIỜ làm chữ
  static const pink500 = Color(0xFFFF7AC8);
  static const mint500 = Color(0xFF4CD4B0);

  // ── -700: CHỮ (mỗi màu -500 có "cặp song sinh đọc được") ──
  static const ink = Color(0xFF2D2D3A); // chữ chính
  static const primaryText = Color(0xFF5B21B6);
  static const pinkText = Color(0xFFBE185D);
  static const mintText = Color(0xFF047857);
  static const warnText = Color(0xFFB45309); // cặp chữ của vàng
  static const inkSoft = Color(0xFF55556A); // chữ phụ
}

/// Trạng thái HỌC → token — điểm khác biệt của WAL: màu mang NGHĨA domain,
/// không trang trí. Ánh xạ đủ ConceptClaim + ReviewUrgency + 2 state hệ thống.
enum LearningStateToken {
  mastered(bg: Color(0xFFE9FBF5), fg: WalColors.mintText), // đầy + ấm
  strongOnObserved(bg: Color(0xFFF3EEFF), fg: WalColors.primaryText), // một phần
  developing(bg: Color(0xFFF7F7FC), fg: WalColors.inkSoft), // đang lớn
  needsWork(bg: Color(0xFFFFF4E0), fg: WalColors.warnText), // ấm, KHÔNG đỏ
  insufficientEvidence(bg: Color(0xFFF7F7FC), fg: WalColors.inkSoft), // dấu hỏi
  noEvidence(bg: Color(0xFFF7F7FC), fg: WalColors.inkSoft),
  reviewDue(bg: Color(0xFFF3EEFF), fg: WalColors.primaryText), // vòng lặp nhẹ
  aiThinking(bg: Color(0xFFF3EEFF), fg: WalColors.primaryText); // SAM THINK

  const LearningStateToken({required this.bg, required this.fg});
  final Color bg;
  final Color fg;
}

abstract final class WalSpacing {
  static const xs = 4.0, sm = 8.0, md = 16.0, lg = 24.0, xl = 32.0;
  static const radiusCard = 20.0, radiusButton = 16.0, radiusChip = 12.0;
  static const minTouch = 48.0; // luật Hub: chạm một tay
}

abstract final class WalType {
  // Tiểu học đọc trước: thân bài ≥16, tối thiểu tuyệt đối 14 (chữ phụ).
  static const display = 28.0, title = 22.0, body = 17.0, secondary = 15.0;
}


/// WAL-50 — DARK PALETTE: cặp chữ/nền tối, CÙNG LUẬT contrast-test ≥4.5:1
/// (không thêm màu nào thiếu cặp). Nền tối ấm — không đen tuyệt đối (OLED
/// smearing + chữ trẻ em cần nền dịu).
abstract final class WalColorsDark {
  static const surface = Color(0xFF17171F);
  static const surfaceCard = Color(0xFF232330);
  static const surfaceLavender = Color(0xFF2A2440);

  static const ink = Color(0xFFECECF4); // chữ chính trên nền tối
  static const inkSoft = Color(0xFFB6B6C8);
  static const primaryText = Color(0xFFC4B5FD); // tím sáng đọc được
  static const mintText = Color(0xFF6EE7C7);
  static const pinkText = Color(0xFFF9A8D4);
  static const warnText = Color(0xFFFBBF24);
}

/// WAL-50 — MOTION TOKENS: duration/curve theo NGHĨA, không theo màn.
/// Spec 12 state: docs/design/MOTION-SPEC-12-STATE.md — mọi state chỉ được
/// dùng token ở đây (đổi nhịp = đổi MỘT chỗ).
abstract final class WalMotion {
  /// phản hồi chạm/chip — nhanh, không phô trương
  static const tap = Duration(milliseconds: 120);

  /// xuất hiện nội dung/hint — đủ thấy, không sốt ruột
  static const gentle = Duration(milliseconds: 240);

  /// chuyển màn/stage
  static const stage = Duration(milliseconds: 320);

  /// CELEBRATE — duy nhất được «rình rang», và chỉ khi claim THẬT
  static const celebrate = Duration(milliseconds: 480);

  /// vòng lặp THINKING (engine đang chẩn đoán)
  static const thinkingLoop = Duration(milliseconds: 1200);
}

/// WAL-50 — CHẾ ĐỘ GỌN THCS (band 6-9): «âm lượng» mascot/hiệu ứng thấp hơn
/// (MASCOT-AUDIT rủi ro #1: lệch tiểu học). Một design system — N policy band.
class WalBandDensity {
  const WalBandDensity._(
      {required this.mascotChip,
      required this.mascotHero,
      required this.celebrateScale,
      required this.showStickers});

  final double mascotChip; // size mascot cạnh lời thoại
  final double mascotHero; // size mascot màn kết quả
  final double celebrateScale; // 1.0 = confetti đầy đủ; 0 = chỉ chữ
  final bool showStickers;

  static const primary = WalBandDensity._(
      mascotChip: 56, mascotHero: 96, celebrateScale: 1.0, showStickers: true);

  /// THCS: mascot nhỏ hơn, celebrate tiết chế, không sticker.
  static const lowerSecondary = WalBandDensity._(
      mascotChip: 40, mascotHero: 64, celebrateScale: 0.5, showStickers: false);

  /// THPT: tối giản — mascot chỉ còn dấu hiệu, không hiệu ứng.
  static const upperSecondary = WalBandDensity._(
      mascotChip: 32, mascotHero: 48, celebrateScale: 0.0, showStickers: false);

  static WalBandDensity forGradeBandLabel(String label) => switch (label) {
        '6-9' => lowerSecondary,
        '10-12' => upperSecondary,
        _ => primary, // '1-2' và '3-5' giữ mặc định tiểu học
      };
}
