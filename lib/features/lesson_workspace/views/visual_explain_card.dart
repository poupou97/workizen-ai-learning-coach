/// TRACK B ROUND 7 · V1 — trình bày [VisualExplain] trong sheet «Sách viết».
///
/// Vòng 5/6: chạm một ô ⇒ sheet nguồn (nguyên văn + trang + «Xem trong Đọc»).
/// Đúng, nhưng trẻ đọc lại đúng câu vừa thấy trong ô. Vòng 7 chèn phần GIẢI
/// THÍCH lên TRÊN phần nguồn — cùng một sheet, không thêm màn:
///
///   «Lọc»                                     ← tên nút
///   Một trong 4 cách sách nêu ở «…»           ← nút này là gì trong sơ đồ
///   ┌ Dùng để tách ─────────────────────────┐ ← chiều so sánh, chữ SÁCH
///   │ tách chất rắn không tan ra khỏi …     │
///   └───────────────────────────────────────┘
///   BÀI NÀY DÙNG Ở ĐÂU
///   → Lọc nước từ hỗn hợp nước lẫn đất        ← sơ đồ khác CÙNG bài
///   ─────────────────────────────────────────
///   Sách viết  (phần nguồn cũ, không đổi)
///
/// Widget này KHÔNG biết tài liệu bài, KHÔNG biết `LessonDocument`, và không
/// có chữ nào của một bài cụ thể — nó chỉ vẽ mô hình được truyền vào.
library;

import 'package:flutter/material.dart';

import '../../../app/theme/wal_tokens.dart';
import 'visual_explain.dart';

class VisualExplainCard extends StatelessWidget {
  const VisualExplainCard({
    super.key,
    required this.explain,
    this.onOpenLink,
  });

  final VisualExplain explain;

  /// Chạm một liên hệ ⇒ mở sơ đồ đó. `null` ⇒ liên hệ chỉ để đọc.
  final void Function(ExplainLink link)? onOpenLink;

  static const rootKey = Key('visual-explain');
  static const kickerKey = Key('visual-explain-kicker');
  static const linksKey = Key('visual-explain-links');
  static const linksEmptyKey = Key('visual-explain-links-empty');
  static Key factKey(String name) => Key('visual-explain-fact-$name');
  static Key linkKey(String semanticId) =>
      Key('visual-explain-link-$semanticId');

  @override
  Widget build(BuildContext context) => Column(
    key: rootKey,
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text(
        explain.headline,
        style: const TextStyle(
          fontSize: WalType.title,
          fontWeight: FontWeight.w700,
          color: WalColors.ink,
        ),
      ),
      Text(
        explain.kicker,
        key: kickerKey,
        style: const TextStyle(fontSize: 13, color: WalColors.inkSoft),
      ),
      if (explain.withheldNote != null) ...[
        const SizedBox(height: WalSpacing.sm),
        _tile(
          bg: WalColors.surfaceLavender,
          child: Text(
            explain.withheldNote!,
            style: const TextStyle(
              fontSize: WalType.secondary,
              color: WalColors.ink,
              height: 1.45,
            ),
          ),
        ),
      ],
      if (explain.verbatim != null) ...[
        const SizedBox(height: WalSpacing.sm),
        _labelled(
          explainVerbatimLabel,
          Text(
            '«${explain.verbatim}»',
            style: const TextStyle(
              fontSize: WalType.body,
              color: WalColors.ink,
              height: 1.5,
            ),
          ),
        ),
      ],
      for (final f in explain.facts) ...[
        const SizedBox(height: WalSpacing.sm),
        _labelled(
          f.name,
          Text(
            f.value ?? '— sách không nói ở phần này',
            key: factKey(f.name),
            style: TextStyle(
              fontSize: WalType.secondary,
              color: f.value == null ? WalColors.inkSoft : WalColors.ink,
              height: 1.45,
              fontStyle: f.value == null ? FontStyle.italic : FontStyle.normal,
            ),
          ),
        ),
      ],
      if (explain.links.isNotEmpty) ...[
        const SizedBox(height: WalSpacing.md),
        const Text(
          explainLinksLabel,
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w700,
            letterSpacing: .6,
            color: WalColors.primaryText,
          ),
        ),
        const SizedBox(height: 4),
        Column(
          key: linksKey,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            for (final l in explain.links)
              Padding(
                padding: const EdgeInsets.only(bottom: 6),
                child: Material(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
                  child: InkWell(
                    key: linkKey(l.semanticId),
                    borderRadius: BorderRadius.circular(
                      WalSpacing.radiusButton,
                    ),
                    onTap: onOpenLink == null ? null : () => onOpenLink!(l),
                    child: Padding(
                      padding: const EdgeInsets.all(WalSpacing.md),
                      child: Row(
                        children: [
                          Expanded(
                            child: Text(
                              l.title,
                              style: const TextStyle(
                                fontSize: WalType.secondary,
                                fontWeight: FontWeight.w600,
                                color: WalColors.ink,
                                height: 1.35,
                              ),
                            ),
                          ),
                          if (onOpenLink != null)
                            const Padding(
                              padding: EdgeInsets.only(left: WalSpacing.sm),
                              child: Text(
                                '✨ →',
                                style: TextStyle(
                                  fontSize: WalType.secondary,
                                  color: WalColors.primaryText,
                                ),
                              ),
                            ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
          ],
        ),
      ] else if (explain.linksEmptyNote != null) ...[
        const SizedBox(height: WalSpacing.md),
        const Text(
          explainLinksLabel,
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w700,
            letterSpacing: .6,
            color: WalColors.primaryText,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          explain.linksEmptyNote!,
          key: linksEmptyKey,
          style: const TextStyle(
            fontSize: WalType.secondary,
            color: WalColors.inkSoft,
            height: 1.45,
          ),
        ),
      ],
      const SizedBox(height: WalSpacing.md),
      Divider(height: 1, color: WalColors.inkSoft.withValues(alpha: 0.18)),
      const SizedBox(height: WalSpacing.md),
    ],
  );

  Widget _labelled(String label, Widget child) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text(
        label,
        style: const TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w700,
          letterSpacing: .4,
          color: WalColors.inkSoft,
        ),
      ),
      const SizedBox(height: 3),
      _tile(bg: Colors.white, child: child),
    ],
  );

  static Widget _tile({required Color bg, required Widget child}) => Container(
    width: double.infinity,
    padding: const EdgeInsets.all(WalSpacing.md),
    decoration: BoxDecoration(
      color: bg,
      borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
    ),
    child: child,
  );
}
