/// WAL-50 — BandDensityScope: MỘT chỗ bơm «âm lượng» UI theo band tuổi.
/// Widget đọc qua [densityOf] — thiếu scope ⇒ mặc định tiểu học (an toàn:
/// to/rõ), KHÔNG crash.
library;

import 'package:flutter/widgets.dart';

import 'wal_tokens.dart';

class BandDensityScope extends InheritedWidget {
  const BandDensityScope(
      {super.key, required this.density, required super.child});

  final WalBandDensity density;

  static WalBandDensity of(BuildContext context) =>
      context
          .dependOnInheritedWidgetOfExactType<BandDensityScope>()
          ?.density ??
      WalBandDensity.primary;

  @override
  bool updateShouldNotify(BandDensityScope old) => density != old.density;
}

/// Shorthand cho call-site gọn.
WalBandDensity densityOf(BuildContext context) => BandDensityScope.of(context);
