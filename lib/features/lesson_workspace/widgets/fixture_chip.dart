/// TRACK B — chip «Bản thử nghiệm»: KHÔNG có nút đóng, KHÔNG có tham số tắt.
///
/// Cùng triết lý `LearningAssetImage` (WAL-133): nếu nhãn là một tuỳ chọn thì
/// sớm muộn có màn tắt nó «cho gọn». Chip chỉ biến mất khi `trust ==
/// trustedCorpus` — tức khi nội dung là sự thật sản phẩm, điều hôm nay chưa
/// có.
library;

import 'package:flutter/material.dart';

import '../../../app/theme/wal_tokens.dart';
import '../../../core/lesson_model/content_trust.dart';

class FixtureChip extends StatelessWidget {
  const FixtureChip({super.key, required this.trust});

  static const chipKey = Key('fixture-chip');

  final ContentTrust trust;

  @override
  Widget build(BuildContext context) {
    final label = fixtureChipLabel(trust);
    if (label == null) return const SizedBox.shrink();
    return Semantics(
      label: 'Bản thử nghiệm',
      child: Container(
        key: chipKey,
        width: double.infinity,
        padding: const EdgeInsets.symmetric(
          horizontal: WalSpacing.md,
          vertical: WalSpacing.sm,
        ),
        decoration: BoxDecoration(
          color: LearningStateToken.needsWork.bg, // ấm, KHÔNG đỏ
          borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
        ),
        child: Row(
          children: [
            const Text('🧪', style: TextStyle(fontSize: 14)),
            const SizedBox(width: WalSpacing.sm),
            Expanded(
              child: Text(
                label,
                style: const TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                  color: WalColors.warnText,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
