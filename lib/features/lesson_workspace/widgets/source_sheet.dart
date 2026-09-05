/// TRACK B — «Sách viết»: sheet nguồn của MỘT block. Nguyên văn + trang in +
/// (nếu có) ảnh vùng trang nội bộ. Withheld ⇒ placeholder thật, không chữ.
library;

import 'package:flutter/material.dart';

import '../../../app/theme/wal_tokens.dart';
import '../../../core/lesson_model/lesson_document.dart';
import 'withheld_card.dart';

/// Thẻ nguồn gọn (dùng trong Tutor / Visual): «Sách viết: … · SGK trang N».
class SourceCard extends StatelessWidget {
  const SourceCard({
    super.key,
    required this.doc,
    required this.block,
    this.onTap,
  });

  final LessonDocument doc;
  final LessonBlock block;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final text = LessonDocument.textOf(block);
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(WalSpacing.md),
        decoration: BoxDecoration(
          color: WalColors.surfaceLavender,
          borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'SÁCH VIẾT',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w700,
                color: WalColors.primaryText,
              ),
            ),
            const SizedBox(height: 4),
            if (text != null)
              Text(
                '«$text»',
                style: const TextStyle(
                  fontSize: WalType.secondary,
                  color: WalColors.ink,
                  height: 1.4,
                ),
              )
            else
              Text(
                block is WithheldBlock
                    ? 'Phần này SAM chưa đọc được — con xem trong sách nhé.'
                    : 'Hình trong sách.',
                style: const TextStyle(
                  fontSize: WalType.secondary,
                  color: WalColors.inkSoft,
                ),
              ),
            const SizedBox(height: 4),
            Text(
              doc.sourceLineForBlock(block),
              style: const TextStyle(fontSize: 13, color: WalColors.inkSoft),
            ),
          ],
        ),
      ),
    );
  }
}

Future<void> showSourceSheet(
  BuildContext context, {
  required LessonDocument doc,
  required LessonBlock block,
  VoidCallback? onShowInRead,
}) {
  final text = LessonDocument.textOf(block);
  final crop = switch (block) {
    ImageBlock(:final crop) => crop,
    WithheldBlock(:final crop) => crop,
    _ => null,
  };
  return showModalBottomSheet<void>(
    context: context,
    backgroundColor: WalColors.surface,
    showDragHandle: true,
    isScrollControlled: true,
    builder: (sheet) => SafeArea(
      child: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(
            WalSpacing.lg,
            0,
            WalSpacing.lg,
            WalSpacing.lg,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Sách viết',
                style: TextStyle(
                  fontSize: WalType.title,
                  fontWeight: FontWeight.w700,
                  color: WalColors.ink,
                ),
              ),
              const SizedBox(height: WalSpacing.sm),
              if (block is WithheldBlock)
                WithheldCard(doc: doc, block: block)
              else if (text != null)
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(WalSpacing.md),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(
                      WalSpacing.radiusButton,
                    ),
                  ),
                  child: Text(
                    text,
                    style: const TextStyle(
                      fontSize: WalType.body,
                      color: WalColors.ink,
                      height: 1.5,
                    ),
                  ),
                ),
              if (crop != null && block is! WithheldBlock) ...[
                const SizedBox(height: WalSpacing.sm),
                ClipRRect(
                  borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
                  child: Image.asset(
                    '${doc.assetBase}$crop',
                    fit: BoxFit.contain,
                    errorBuilder: (_, _, _) => const SizedBox.shrink(),
                  ),
                ),
                const Text(
                  'Ảnh vùng trang · nội bộ, không phát hành',
                  style: TextStyle(fontSize: 12, color: WalColors.inkSoft),
                ),
              ],
              const SizedBox(height: WalSpacing.sm),
              Text(
                doc.sourceLineForBlock(block),
                style: const TextStyle(
                  fontSize: WalType.secondary,
                  color: WalColors.inkSoft,
                ),
              ),
              if (onShowInRead != null) ...[
                const SizedBox(height: WalSpacing.md),
                SizedBox(
                  width: double.infinity,
                  height: WalSpacing.minTouch + 4,
                  child: FilledButton(
                    style: FilledButton.styleFrom(
                      backgroundColor: WalColors.primary500,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(
                          WalSpacing.radiusButton,
                        ),
                      ),
                    ),
                    onPressed: () {
                      Navigator.of(sheet).pop();
                      onShowInRead();
                    },
                    child: const Text(
                      '📖 Xem trong Đọc',
                      style: TextStyle(fontSize: WalType.body),
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    ),
  );
}
