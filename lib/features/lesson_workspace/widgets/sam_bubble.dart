/// TRACK B — lời của SAM trong workspace: mascot chip + bong bóng + NHÃN.
///
/// Nhãn mặc định «SAM (kịch bản thử nghiệm)» là bắt buộc theo `SamMode`;
/// widget không có tham số bỏ nhãn — chỉ đổi được sang nhãn ngắn ở chỗ chật.
library;

import 'package:flutter/material.dart';

import '../../../app/theme/band_density_scope.dart';
import '../../../app/theme/wal_tokens.dart';
import '../../../core/lesson_model/content_trust.dart';

class SamBubble extends StatelessWidget {
  const SamBubble({
    super.key,
    required this.mascot,
    required this.text,
    this.showLabel = true,
    this.child,
    this.background = Colors.white,
    this.caption,
  });

  /// Tên state mascot (`sam-explain`…), không có đuôi.
  final String mascot;
  final String text;
  final bool showLabel;

  /// Thẻ phụ dưới lời (vd «Sách viết…»).
  final Widget? child;
  final Color background;

  /// ROUND 3 B4: chữ nhỏ cạnh nhãn («Câu 1/3») — vị trí trong vòng lặp.
  final String? caption;

  @override
  Widget build(BuildContext context) {
    final size = densityOf(context).mascotChip;
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Image.asset(
          'assets/mascot/$mascot.png',
          width: size,
          height: size,
          errorBuilder: (_, _, _) => SizedBox(width: size, height: size),
        ),
        const SizedBox(width: WalSpacing.sm),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (showLabel)
                Padding(
                  padding: const EdgeInsets.only(bottom: 2),
                  child: Row(
                    children: [
                      Text(
                        SamMode.prototypeScripted.childLabel,
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w700,
                          color: WalColors.primaryText,
                        ),
                      ),
                      if (caption != null) ...[
                        const SizedBox(width: WalSpacing.sm),
                        Text(
                          caption!,
                          style: const TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w700,
                            color: WalColors.inkSoft,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(WalSpacing.md),
                decoration: BoxDecoration(
                  color: background,
                  borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
                ),
                child: Text(
                  text,
                  style: const TextStyle(
                    fontSize: WalType.body,
                    color: WalColors.ink,
                    height: 1.45,
                  ),
                ),
              ),
              if (child != null) ...[
                const SizedBox(height: WalSpacing.sm),
                child!,
              ],
            ],
          ),
        ),
      ],
    );
  }
}
