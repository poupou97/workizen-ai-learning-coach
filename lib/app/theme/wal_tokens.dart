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
