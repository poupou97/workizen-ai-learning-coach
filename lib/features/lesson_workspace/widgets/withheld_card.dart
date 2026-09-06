/// TRACK B — vùng BỊ GIỮ LẠI: placeholder thật thà, không bao giờ là chữ.
///
/// «Phần này SAM chưa đọc được — xem SGK trang N». Lý do máy (`math_guard`,
/// `page_feature:diagram`) dịch thành lời trẻ hiểu; ảnh vùng trang (nội bộ)
/// nằm sau một nút bấm — thứ phụ, không phải nội dung.
///
/// ROUND 4 (§6.3 «withheld cards in child language with a «vì sao»»): thẻ có
/// nút «Vì sao SAM để trống?» mở một đoạn giải thích bằng lời trẻ 11 tuổi
/// (sơ đồ / số & công thức / bảng / chưa rõ loại); KHÔNG có mã máy trên thẻ —
/// mã nằm trong nếp gấp kỹ thuật của sheet «Sách viết».
library;

import 'package:flutter/material.dart';

import '../../../app/theme/wal_tokens.dart';
import '../../../core/lesson_model/lesson_document.dart';

/// Lý do ngắn (một cụm) — theo mã máy, KHÔNG in mã.
String withheldReasonForChild(String reason) {
  if (reason.contains('math_guard')) return 'đoạn này có số/công thức';
  if (reason.contains('diagram')) return 'đoạn này nằm trong sơ đồ';
  if (reason.contains('table')) return 'đoạn này là bảng';
  if (reason.contains('formula')) return 'đoạn này có công thức';
  if (reason.contains('unknown_role')) return 'máy chưa rõ đoạn này là gì';
  return 'SAM chưa chắc đọc đúng';
}

/// «Vì sao SAM để trống?» — đoạn giải thích cho trẻ 11 tuổi: chuyện gì ở chỗ
/// đó trong sách, vì sao máy dễ đọc sai, và SAM làm gì (chỉ trang, không đoán).
String withheldWhyForChild(String reason) {
  if (reason.contains('math_guard') || reason.contains('formula')) {
    return 'Chỗ này trong sách có số hoặc công thức. Máy đọc số dễ sai một '
        'chữ số là sai cả ý, nên SAM không chép lại mà chỉ trang để con xem '
        'tận mắt trong sách.';
  }
  if (reason.contains('diagram')) {
    return 'Chỗ này trong sách là một sơ đồ — chữ nằm xen trong hình. Máy đọc '
        'chữ trong sơ đồ hay bị nhầm, mà SAM chỉ chép lại khi chắc là đúng, nên '
        'SAM để trống và chỉ trang cho con.';
  }
  if (reason.contains('table')) {
    return 'Chỗ này là một bảng. Máy hay đọc lẫn ô này sang ô kia, nên SAM để '
        'trống và chỉ trang — con xem bảng trong sách nhé.';
  }
  if (reason.contains('unknown_role')) {
    return 'Máy chưa hiểu chỗ này là loại gì (câu hỏi, chú thích hay ghi '
        'chú), nên SAM không đoán mà chỉ trang cho con.';
  }
  return 'Máy chưa chắc đọc đúng chỗ này, nên SAM không đoán — con mở sách ra '
      'xem nhé, số trang ghi ngay trên thẻ.';
}

class WithheldCard extends StatefulWidget {
  const WithheldCard({super.key, required this.doc, required this.block});

  static const cardKey = Key('withheld-card');
  static const whyKey = Key('withheld-why');

  final LessonDocument doc;
  final WithheldBlock block;

  @override
  State<WithheldCard> createState() => _WithheldCardState();
}

class _WithheldCardState extends State<WithheldCard> {
  bool _showCrop = false;
  bool _showWhy = false;

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
          // ROUND 3 B5 (n1 D-R3-07): mã lý do máy («page_feature:diagram»)
          // rời dòng trẻ đọc — round 4: mã chỉ còn trong nếp gấp kỹ thuật
          // của sheet «Sách viết».
          Text(
            'Lý do: ${withheldReasonForChild(b.reason)}',
            style: const TextStyle(fontSize: 12, color: WalColors.inkSoft),
          ),
          Wrap(
            crossAxisAlignment: WrapCrossAlignment.center,
            children: [
              SizedBox(
                height: WalSpacing.minTouch,
                child: TextButton(
                  key: WithheldCard.whyKey,
                  style: TextButton.styleFrom(
                    padding: const EdgeInsets.symmetric(
                      horizontal: WalSpacing.xs,
                    ),
                  ),
                  onPressed: () => setState(() => _showWhy = !_showWhy),
                  child: Text(
                    _showWhy ? 'Ẩn giải thích' : 'Vì sao SAM để trống?',
                    style: const TextStyle(
                      fontSize: WalType.secondary,
                      color: WalColors.primaryText,
                    ),
                  ),
                ),
              ),
              if (b.crop != null)
                SizedBox(
                  height: WalSpacing.minTouch,
                  child: TextButton(
                    style: TextButton.styleFrom(
                      padding: const EdgeInsets.symmetric(
                        horizontal: WalSpacing.xs,
                      ),
                    ),
                    onPressed: () => setState(() => _showCrop = !_showCrop),
                    child: Text(
                      _showCrop ? 'Ẩn ảnh trang' : 'Xem ảnh chụp trang sách',
                      style: const TextStyle(
                        fontSize: WalType.secondary,
                        color: WalColors.primaryText,
                      ),
                    ),
                  ),
                ),
            ],
          ),
          if (_showWhy)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(WalSpacing.sm),
              decoration: BoxDecoration(
                color: WalColors.surfaceLavender,
                borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
              ),
              child: Text(
                withheldWhyForChild(b.reason),
                style: const TextStyle(
                  fontSize: WalType.secondary,
                  color: WalColors.ink,
                  height: 1.4,
                ),
              ),
            ),
          if (_showCrop && b.crop != null) ...[
            const SizedBox(height: WalSpacing.xs),
            ClipRRect(
              borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
              child: Image.asset(
                '${widget.doc.assetBase}${b.crop}',
                fit: BoxFit.contain,
                errorBuilder: (_, _, _) => const Padding(
                  padding: EdgeInsets.all(WalSpacing.sm),
                  child: Text(
                    'Máy này chưa có ảnh chụp trang.',
                    style: TextStyle(fontSize: 13, color: WalColors.inkSoft),
                  ),
                ),
              ),
            ),
            const Text(
              'Ảnh chụp trang sách — chỉ để con đối chiếu, không phát hành.',
              style: TextStyle(fontSize: 11, color: WalColors.inkSoft),
            ),
          ],
        ],
      ),
    );
  }
}
