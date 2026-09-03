/// ⭐⭐ WAL-46 — WCAG contrast là UNIT TEST, không phải checklist design.
/// Bài học Tổng Tài (WTM-168): màu -500 làm chữ = 2.31:1 lọt review bằng mắt;
/// từ nay compiler + test giữ, không phải mắt người.
library;

import 'dart:math' as math;

import 'dart:ui';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/app/theme/wal_tokens.dart';

/// WCAG 2.x relative luminance + contrast ratio — công thức chuẩn, không xấp xỉ.
double _lin(double c) =>
    c <= 0.04045 ? c / 12.92 : _pow((c + 0.055) / 1.055, 2.4);
double _pow(double x, double e) {
  // pow cho double dương — tránh import dart:math trong file test nhỏ? Không —
  // dùng chuẩn:
  return x <= 0 ? 0 : _exp(e * _ln(x));
}
double _exp(double x) {
  var s = 1.0, t = 1.0;
  for (var i = 1; i < 30; i++) {
    t *= x / i;
    s += t;
  }
  return s;
}
double _ln(double x) {
  var y = (x - 1) / (x + 1), y2 = y * y, s = 0.0, t = y;
  for (var i = 1; i < 60; i += 2) {
    s += t / i;
    t *= y2;
  }
  return 2 * s;
}

double luminance(Color c) =>
    0.2126 * _lin(c.r) + 0.7152 * _lin(c.g) + 0.0722 * _lin(c.b);

double contrast(Color a, Color b) {
  final la = luminance(a), lb = luminance(b);
  final hi = la > lb ? la : lb, lo = la > lb ? lb : la;
  return (hi + 0.05) / (lo + 0.05);
}

void main() {
  test('⭐ WAL-140: chữ nhắc trên nền ĐEN của màn chụp đạt WCAG AA', () {
    // Màn chụp có nền đen tuyệt đối (camera preview). Vàng của bảng SÁNG đặt
    // lên đó là chữ tối trên nền tối — nên màn ấy phải dùng cặp của bảng TỐI.
    double lum(Color c) {
      double ch(double v) =>
          v <= 0.03928 ? v / 12.92 : math.pow((v + 0.055) / 1.055, 2.4) as double;
      return 0.2126 * ch(c.r) + 0.7152 * ch(c.g) + 0.0722 * ch(c.b);
    }

    double ratio(Color a, Color b) {
      final l1 = lum(a), l2 = lum(b);
      final hi = l1 > l2 ? l1 : l2, lo = l1 > l2 ? l2 : l1;
      return (hi + 0.05) / (lo + 0.05);
    }

    expect(ratio(WalColorsDark.warnText, const Color(0xFF000000)),
        greaterThanOrEqualTo(4.5),
        reason: 'lời nhắc chụp phải đọc được trên nền đen');
    expect(ratio(WalColors.warnText, const Color(0xFF000000)), lessThan(4.5),
        reason: 'ghi lại VÌ SAO không được dùng vàng bảng sáng ở đó');
  });

  test('⭐⭐ MỌI cặp chữ/nền khai báo đạt WCAG AA ≥ 4.5:1 — ĐO, không tin mắt', () {
    final pairs = <String, (Color fg, Color bg)>{
      'ink/surface': (WalColors.ink, WalColors.surface),
      'ink/white': (WalColors.ink, WalColors.white),
      'inkSoft/surface': (WalColors.inkSoft, WalColors.surface),
      'primaryText/white': (WalColors.primaryText, WalColors.white),
      'primaryText/surfaceLavender': (WalColors.primaryText, WalColors.surfaceLavender),
      'pinkText/white': (WalColors.pinkText, WalColors.white),
      'mintText/white': (WalColors.mintText, WalColors.white),
      'warnText/white': (WalColors.warnText, WalColors.white),
      for (final s in LearningStateToken.values) 'state:${s.name}': (s.fg, s.bg),
      // WAL-50 — dark palette CÙNG LUẬT, không ngoại lệ:
      'dark:ink/surface': (WalColorsDark.ink, WalColorsDark.surface),
      'dark:ink/card': (WalColorsDark.ink, WalColorsDark.surfaceCard),
      'dark:inkSoft/surface': (WalColorsDark.inkSoft, WalColorsDark.surface),
      'dark:primaryText/surface': (WalColorsDark.primaryText, WalColorsDark.surface),
      'dark:primaryText/lavender': (WalColorsDark.primaryText, WalColorsDark.surfaceLavender),
      'dark:mintText/surface': (WalColorsDark.mintText, WalColorsDark.surface),
      'dark:pinkText/surface': (WalColorsDark.pinkText, WalColorsDark.surface),
      'dark:warnText/surface': (WalColorsDark.warnText, WalColorsDark.surface),
    };
    final failures = <String>[];
    pairs.forEach((name, p) {
      final r = contrast(p.$1, p.$2);
      if (r < 4.5) failures.add('$name = ${r.toStringAsFixed(2)}:1');
    });
    expect(failures, isEmpty,
        reason: '⭐⭐ cặp dưới 4.5:1 (bài học 2.31:1 của Tổng Tài không được '
            'tái diễn): $failures');
  });

  test('⭐ vàng FFB800 không bao giờ là chữ — đo để chứng minh vì sao cấm', () {
    expect(contrast(WalColors.accent500, WalColors.white), lessThan(4.5),
        reason: 'chính vì nó KHÔNG đạt trên nền sáng nên luật cấm tồn tại — '
            'con số làm luật, không phải khẩu vị');
  });

  test('⭐ WAL-50: THCS/THPT «âm lượng» THẤP HƠN tiểu học — đo bằng số', () {
    final p = WalBandDensity.primary;
    final lo = WalBandDensity.lowerSecondary;
    final up = WalBandDensity.upperSecondary;
    expect(lo.mascotChip, lessThan(p.mascotChip),
        reason: '⭐ đột biến cho THCS to bằng tiểu học ⇒ đỏ (MASCOT-AUDIT #1)');
    expect(lo.celebrateScale, lessThan(p.celebrateScale));
    expect(lo.showStickers, isFalse);
    expect(up.celebrateScale, 0.0, reason: 'THPT: không confetti');
    expect(WalBandDensity.forGradeBandLabel('6-9'), same(lo));
    expect(WalBandDensity.forGradeBandLabel('3-5'), same(p));
  });

  test('motion: CELEBRATE là duration dài nhất (một chỗ được rình rang), '
      'tap ngắn nhất', () {
    expect(WalMotion.celebrate, greaterThan(WalMotion.stage));
    expect(WalMotion.tap, lessThan(WalMotion.gentle));
    expect(WalMotion.thinkingLoop, greaterThan(WalMotion.celebrate),
        reason: 'loop chờ ≠ hiệu ứng — chậm và đều');
  });

  test('mọi LearningStateToken có bg ≠ fg và đủ 8 trạng thái thiết kế', () {
    expect(LearningStateToken.values.length, 8);
    for (final s in LearningStateToken.values) {
      expect(s.bg, isNot(s.fg));
    }
  });
}
