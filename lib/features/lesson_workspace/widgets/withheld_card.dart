/// TRACK B — vùng BỊ GIỮ LẠI: placeholder thật thà, không bao giờ là chữ.
///
/// «Phần này SAM chưa đọc được — xem SGK trang N». Lý do máy (`math_guard`,
/// `page_feature:diagram`) dịch thành lời trẻ hiểu; ảnh vùng trang (nội bộ)
/// nằm sau một nút bấm — thứ phụ, không phải nội dung.
library;

import 'package:flutter/material.dart';

import '../../../app/theme/wal_tokens.dart';
import '../../../core/lesson_model/lesson_document.dart';

String withheldReasonForChild(String reason) {
  if (reason.contains('math_guard')) return 'đoạn này có số/công thức';
  if (reason.contains('diagram')) return 'đoạn này nằm trong sơ đồ';
  if (reason.contains('table')) return 'đoạn này là bảng';
  if (reason.contains('formula')) return 'đoạn này có công thức';
  return 'SAM chưa chắc đọc đúng';
}

class WithheldCard extends StatefulWidget {
  const WithheldCard({super.key, required this.doc, required this.block});

  static const cardKey = Key('withheld-card');

  final LessonDocument doc;
  final WithheldBlock block;

  @override
  State<WithheldCard> createState() => _WithheldCardState();
}

class _WithheldCardState extends State<WithheldCard> {
  bool _showCrop = false;

  @override
  Widget build(BuildContext context) {
    final b = widget.block;
    final printed =
        b.sourceRef.pagePrinted ??
        widget.doc.printedPageFor(b.sourceRef.pagePdf);
    final page = printed == null
        ? 'trang PDF ${b.sourceRef.pagePdf}'
        : 'trang $printed';
    return Container(
      key: WithheldCard.cardKey,
      width: double.infinity,
      padding: const EdgeInsets.all(WalSpacing.md),
      decoration: BoxDecoration(
        color: WalColors.surface,
        border: Border.all(color: WalColors.inkSoft.withValues(alpha: 0.35)),
        borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Image.asset(
                'assets/mascot/sam-admit-uncertainty@64.png',
                width: 32,
                height: 32,
                errorBuilder: (_, _, _) =>
                    const SizedBox(width: 32, height: 32),
              ),
              const SizedBox(width: WalSpacing.sm),
              Expanded(
                child: Text(
                  'Phần này SAM chưa đọc được — con xem SGK $page nhé.',
                  style: const TextStyle(
                    fontSize: WalType.secondary,
                    fontWeight: FontWeight.w600,
                    color: WalColors.ink,
                    height: 1.4,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            'Lý do: ${withheldReasonForChild(b.reason)} (${b.reason})',
            style: const TextStyle(fontSize: 12, color: WalColors.inkSoft),
          ),
          if (b.crop != null) ...[
            const SizedBox(height: WalSpacing.sm),
            SizedBox(
              height: WalSpacing.minTouch,
              child: TextButton(
                onPressed: () => setState(() => _showCrop = !_showCrop),
                child: Text(
                  _showCrop ? 'Ẩn vùng trang' : 'Xem vùng trang (nội bộ)',
                  style: const TextStyle(
                    fontSize: WalType.secondary,
                    color: WalColors.primaryText,
                  ),
                ),
              ),
            ),
            if (_showCrop)
              ClipRRect(
                borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
                child: Image.asset(
                  '${widget.doc.assetBase}${b.crop}',
                  fit: BoxFit.contain,
                  errorBuilder: (_, _, _) => const Padding(
                    padding: EdgeInsets.all(WalSpacing.sm),
                    child: Text(
                      'Máy này chưa có ảnh vùng trang.',
                      style: TextStyle(fontSize: 13, color: WalColors.inkSoft),
                    ),
                  ),
                ),
              ),
          ],
        ],
      ),
    );
  }
}
