/// TRACK B — chip «Bản thử nghiệm»: KHÔNG có nút đóng, KHÔNG có tham số tắt.
///
/// Cùng triết lý `LearningAssetImage` (WAL-133): nếu nhãn là một tuỳ chọn thì
/// sớm muộn có màn tắt nó «cho gọn». Chip chỉ biến mất khi `trust ==
/// trustedCorpus` — tức khi nội dung là sự thật sản phẩm, điều hôm nay chưa
/// có.
///
/// ROUND 3 (B1/B5 «source/trust states»): chip GỌN một dòng ở Workspace (khung
/// cố định từng chiếm ~45 % màn Nokia) và CHẠM ĐƯỢC ⇒ mở sheet «nguồn & độ
/// tin» nói đủ: chữ từ đâu, sơ đồ xếp theo luật nào, SAM là kịch bản, không
/// ghi bằng chứng, sáu bất đẳng thức. Gọn không có nghĩa là mờ: chữ vẫn đậm,
/// nền vẫn ấm, và chữ đầy đủ nằm ngay sau một chạm.
library;

import 'package:flutter/material.dart';

import '../../../app/theme/wal_tokens.dart';
import '../../../core/lesson_model/content_trust.dart';

class FixtureChip extends StatelessWidget {
  const FixtureChip({
    super.key,
    required this.trust,
    this.compact = false,
    this.onTap,
  });

  static const chipKey = Key('fixture-chip');

  final ContentTrust trust;

  /// Một dòng (cắt «…»), có dấu ⓘ — dùng ở Workspace, nơi khung cố định phải
  /// nhường chỗ cho thân View. Chữ đầy đủ nằm trong sheet sau [onTap].
  final bool compact;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final label = fixtureChipLabel(trust);
    if (label == null) return const SizedBox.shrink();
    final body = Container(
      key: chipKey,
      width: double.infinity,
      padding: EdgeInsets.symmetric(
        horizontal: compact ? WalSpacing.sm + 4 : WalSpacing.md,
        vertical: compact ? 6 : WalSpacing.sm,
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
              maxLines: compact ? 1 : null,
              overflow: compact ? TextOverflow.ellipsis : null,
              style: const TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w700,
                color: WalColors.warnText,
              ),
            ),
          ),
          if (onTap != null) ...[
            const SizedBox(width: WalSpacing.xs),
            const Icon(
              Icons.info_outline,
              size: 18,
              color: WalColors.warnText,
              semanticLabel: 'Nguồn và độ tin',
            ),
          ],
        ],
      ),
    );
    return Semantics(
      label: 'Bản thử nghiệm',
      button: onTap != null,
      child: onTap == null
          ? body
          : InkWell(
              key: const Key('fixture-chip-tap'),
              onTap: onTap,
              borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
              child: body,
            ),
    );
  }
}
