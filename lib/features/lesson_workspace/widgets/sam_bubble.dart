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
    this.label,
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

  /// ROUND 3 (A7.2): nhãn THEO BƯỚC — «SAM (runtime có kiểm)» khi runtime
  /// chứng minh được bước, còn lại «SAM (kịch bản thử nghiệm)». `null` ⇒
  /// nhãn kịch bản (mặc định an toàn). Không có tham số BỎ nhãn.
  final String? label;

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
                  // ROUND 4: nhãn + chú thích («Câu 1/3», «Gợi ý 1/2») co
                  // được ở màn hẹp — không tràn (Nokia 360dp, test 392dp).
                  child: Row(
                    children: [
                      Flexible(
                        child: Text(
                          label ?? SamMode.prototypeScripted.childLabel,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w700,
                            color: label != null &&
                                    label !=
                                        SamMode.prototypeScripted.childLabel
                                ? WalColors.mintText
                                : WalColors.primaryText,
                          ),
                        ),
                      ),
                      if (caption != null) ...[
                        const SizedBox(width: WalSpacing.sm),
                        Text(
                          caption!,
                          maxLines: 1,
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
