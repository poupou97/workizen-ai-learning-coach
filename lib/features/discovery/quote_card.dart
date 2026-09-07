/// ⭐⭐ Lệnh 59 §P1 — TRÍCH DẪN PHẢI TRÔNG NHƯ TRÍCH DẪN.
///
/// Trước đó một câu nói của danh nhân render y hệt mọi mẩu khác: tiêu đề +
/// một khối chữ. Founder: «KHÔNG render như body paragraph bình thường.»
///
/// ⭐ BA SỰ THẬT KHÁC NHAU (§P2.7), và thẻ này tôn trọng từng cái một:
///
///   TRÍCH DẪN  — chữ trong ngoặc kép, nguyên văn từ nguồn
///   NGƯỜI NÓI  — chỉ hiện khi nguồn ghi tên; KHÔNG suy ra từ nội dung
///   CHÂN DUNG  — chỉ hiện khi có ảnh đã xác minh danh tính VÀ được duyệt quyền
///
/// Thiếu chân dung KHÔNG chặn thẻ (§P2.7). Thiếu tên người thì thẻ vẫn là một
/// trích dẫn — chỉ là không có dòng «— Tên» (§P1.2).
///
/// ⭐⭐ KHÔNG SỬA CHỮ (§P1.3). Thẻ hiển thị NGUYÊN VĂN chuỗi được truyền vào.
/// Không viết lại, không ghép câu, không dịch, không «làm hay hơn». Dấu ngoặc
/// kép ở đây là lời hứa rằng chữ bên trong truy được về nguồn.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/stories/person_portrait.dart';

class QuoteCard extends StatelessWidget {
  const QuoteCard({
    super.key,
    required this.quoteText,
    required this.sourceLine,
    this.personName,
    this.portrait,
    this.year,
    this.onOpenPerson,
  });

  /// NGUYÊN VĂN. Đã bỏ dấu « » bao ngoài nếu nguồn có, vì thẻ tự vẽ dấu nháy.
  final String quoteText;

  /// «SGK Lịch sử 10 · trang PDF 14» — nguồn đi cùng câu, luôn.
  final String sourceLine;

  /// `null` ⇒ nguồn KHÔNG ghi ai nói. Thẻ khi ấy không bịa ra một cái tên.
  final String? personName;

  /// `null` ⇒ chưa có chân dung đủ điều kiện. Thẻ vẫn chạy.
  final PersonPortrait? portrait;

  final int? year;
  final VoidCallback? onOpenPerson;

  static const cardKey = Key('quote-card');
  static const portraitKey = Key('quote-card-portrait');
  static const attributionKey = Key('quote-card-attribution');

  /// Bỏ dấu bao ngoài của nguồn để thẻ không có hai lớp nháy.
  static String stripOuterQuotes(String s) {
    var t = s.trim();
    const pairs = [('«', '»'), ('"', '"'), ('“', '”')];
    for (final (open, close) in pairs) {
      if (t.length > 1 && t.startsWith(open) && t.endsWith(close)) {
        t = t.substring(open.length, t.length - close.length).trim();
      }
    }
    return t;
  }

  @override
  Widget build(BuildContext context) {
    final text = stripOuterQuotes(quoteText);
    final p = portrait;
    return Container(
      key: cardKey,
      padding: const EdgeInsets.all(WalSpacing.lg),
      decoration: BoxDecoration(
        // Cùng surface/radius với Home, Timetable, Workspace (§P5.2).
        color: WalColors.surfaceLavender,
        borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (p != null) ...[
                _portrait(p),
                const SizedBox(width: WalSpacing.md),
              ],
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      '”',
                      style: TextStyle(
                        fontSize: 40,
                        height: 0.9,
                        fontWeight: FontWeight.w700,
                        color: WalColors.primary500,
                      ),
                    ),
                    Text(
                      text,
                      style: const TextStyle(
                        fontSize: WalType.body + 1,
                        height: 1.5,
                        fontStyle: FontStyle.italic,
                        color: WalColors.ink,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: WalSpacing.md),
          if (personName != null)
            InkWell(
              key: attributionKey,
              onTap: onOpenPerson,
              child: Text(
                year == null ? '— $personName' : '— $personName · $year',
                style: const TextStyle(
                  fontSize: WalType.body,
                  fontWeight: FontWeight.w700,
                  color: WalColors.primaryText,
                ),
              ),
            ),
          const SizedBox(height: WalSpacing.xs),
          Text(
            sourceLine,
            style: const TextStyle(
              fontSize: WalType.secondary,
              color: WalColors.inkSoft,
            ),
          ),
          if (p != null) ...[
            const SizedBox(height: WalSpacing.xs),
            // §P2.6 — nói ĐÚNG loại ảnh và nguồn ảnh. Ảnh là một sự thật
            // RIÊNG, nên nó có dòng lai lịch riêng, không núp sau nguồn câu.
            Text(
              '${p.portraitType.label} · ${p.sourceName} · ${p.licence}',
              style: const TextStyle(fontSize: 12, color: WalColors.inkSoft),
            ),
          ],
        ],
      ),
    );
  }

  Widget _portrait(PersonPortrait p) => ClipRRect(
    borderRadius: BorderRadius.circular(WalSpacing.radiusBookCover),
    child: Image.asset(
      p.assetPath,
      key: portraitKey,
      width: 72,
      height: 88,
      fit: BoxFit.cover,
      // Ảnh hỏng ⇒ thẻ vẫn là một trích dẫn hoàn chỉnh.
      errorBuilder: (_, _, _) => const SizedBox.shrink(),
    ),
  );
}
