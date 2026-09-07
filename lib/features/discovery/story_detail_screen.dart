/// WAL-152 (§20) — STORY DETAIL: SOURCE FACT nguyên gốc + trace nguồn.
/// KHÔNG long-article LLM; phần «SAM giải thích» chỉ mở khi có realization
/// gate (WAL-131) — hiện là ghi chú trung thực, không sinh chữ.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import 'quote_card.dart';
import '../../core/stories/person_portrait.dart';
import '../../core/stories/stories_store.dart';
import 'person_detail_screen.dart';
import '../subjects/subject_display.dart';

const storyTypeLabel = {
  'PERSON': 'Danh nhân',
  'QUOTE': 'Câu nói',
  'EVENT': 'Sự kiện',
  'INVENTION_DISCOVERY': 'Phát minh & Khám phá',
  'SOURCE_EXCERPT': 'Trích văn bản',
};

/// ⭐ Mảnh trích chưa trọn câu thì phải TRÔNG RA chỗ cắt.
///
/// Cửa sổ bằng chứng nay đã nới tới ranh giới CÂU khi với tới được (13→5 mở
/// giữa câu, 23→11 đóng giữa câu). Phần còn lại chạm trần độ dài, không nới
/// thêm được — và một mảnh mở giữa câu đọc ra là văn vỡ, trong khi nhãn phía
/// trên hứa «TRÍCH NGUYÊN VĂN TỪ NGUỒN».
///
/// KHÔNG sửa chữ. Chỉ thêm dấu «…» ở mép để chỗ cắt hiện ra đúng như nó là.
String markExcerptEdges(String body) {
  final t = body.trim();
  if (t.isEmpty) return t;
  final startsMidSentence = !RegExp(r'^[«"\(\[]?[A-ZĐÀ-Ỹ0-9]').hasMatch(t);
  final endsMidSentence = !RegExp('[.!?…»"\\)]\$').hasMatch(t);
  return '${startsMidSentence ? '… ' : ''}$t${endsMidSentence ? ' …' : ''}';
}

class StoryDetailScreen extends StatelessWidget {
  const StoryDetailScreen({
    super.key,
    required this.item,
    required this.stories,
  });

  final StoryItem item;
  final StoriesStore stories;

  PersonPortrait? get _portrait => PersonPortraits.forPerson(item.personId);

  static const portraitKey = Key('story-detail-portrait');

  /// Ảnh + dòng lai lịch RIÊNG của ảnh (§P2.6) — dùng cho mọi loại chuyện có
  /// nhân vật, không riêng câu nói.
  Widget _portraitStrip(PersonPortrait p) => Row(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      ClipRRect(
        borderRadius: BorderRadius.circular(WalSpacing.radiusBookCover),
        child: Image.asset(
          p.assetPath,
          key: portraitKey,
          width: 72,
          height: 88,
          fit: BoxFit.cover,
          // Ảnh hỏng ⇒ chuyện vẫn đọc được, không để lỗ đen.
          errorBuilder: (_, _, _) => const SizedBox.shrink(),
        ),
      ),
      const SizedBox(width: WalSpacing.md),
      Expanded(
        child: Text(
          '${p.portraitType.label} · ${p.sourceName} · ${p.licence}',
          style: const TextStyle(fontSize: 12, color: WalColors.inkSoft),
        ),
      ),
    ],
  );

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: WalColors.surface,
    body: SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(WalSpacing.lg),
        children: [
          Text(
            storyTypeLabel[item.type] ?? item.type,
            style: const TextStyle(
              fontSize: WalType.secondary,
              fontWeight: FontWeight.w700,
              letterSpacing: 1.05,
              color: WalColors.inkSoft,
            ),
          ),
          const SizedBox(height: WalSpacing.sm),
          Text(
            item.title,
            style: const TextStyle(
              fontSize: WalType.display,
              fontWeight: FontWeight.w700,
              color: WalColors.ink,
              height: 1.25,
            ),
          ),
          if (item.year != null || item.subject.isNotEmpty) ...[
            const SizedBox(height: WalSpacing.xs),
            Text(
              [
                if (item.year != null) 'Năm ${item.year}',
                '${item.subject} · Lớp ${item.grade}',
              ].join(' · '),
              style: const TextStyle(
                fontSize: WalType.secondary,
                color: WalColors.inkSoft,
              ),
            ),
          ],
          const SizedBox(height: WalSpacing.md),
          // ⭐ Lệnh 59 §P1 — TRÍCH DẪN không render như đoạn văn thường.
          //
          // `title` là câu nói đã được curate (nguyên văn, trong « »);
          // `body` là NGỮ CẢNH quanh nó do OCR cắt ra. Hai thứ khác nhau,
          // nên thẻ lấy `title` làm câu trích và giữ `body` ở khối «trích
          // nguyên văn từ nguồn» phía dưới — không trộn.
          // ⭐⭐ ĐƯỜNG THẬT: NGUỒN → CHUYỆN ĐÃ DUYỆT → NGƯỜI CANONICAL →
          // CHÂN DUNG ĐÃ DUYỆT → MÀN CHUYỆN.
          //
          // Trước đây CHỈ `QuoteCard` tra kho chân dung, mà thẻ ấy chỉ dựng khi
          // `type == 'QUOTE'`. Đo trên kho: 0 chuyện QUOTE nào có personId, nên
          // ảnh đã xác minh không tới được mắt ai. Chuyện PERSON thì CÓ
          // personId và CÓ người thật — ảnh thuộc về đây.
          //
          // ⚠ KHÔNG ép thành «lời danh nhân». Trang nguồn của Thạch Lam là một
          // đoạn TRUYỆN có dẫn nguồn: tác giả VIẾT, nhân vật NÓI. Gắn nhãn
          // «— Thạch Lam» cho lời nhân vật là sai người nói.
          if (_portrait != null) ...[
            _portraitStrip(_portrait!),
            const SizedBox(height: WalSpacing.md),
          ],
          if (item.type == 'QUOTE') ...[
            QuoteCard(
              quoteText: item.title,
              sourceLine: storySourceLine(
                sourceDocumentId: item.sourceDocumentId,
                pagePdf: item.pagePdf,
              ),
              // §P1.2 — CHỈ hiện tên khi NGUỒN ghi tên. Không suy từ nội
              // dung câu, không đoán người nói.
              personName: item.personName,
              year: item.year,
              // §P2.7 — chân dung là sự thật RIÊNG: chỉ hiện khi có ảnh
              // đã xác minh danh tính và được duyệt quyền dùng.
              portrait: PersonPortraits.forPerson(item.personId),
            ),
            const SizedBox(height: WalSpacing.md),
          ],
          Container(
            padding: const EdgeInsets.all(WalSpacing.lg),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ⭐ §21/§39 — SOURCE FACT ≠ SAM EXPLANATION: nhãn rõ.
                const Text(
                  'TRÍCH NGUYÊN VĂN TỪ NGUỒN',
                  style: TextStyle(
                    fontSize: WalType.secondary,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 1.05,
                    color: WalColors.primaryText,
                  ),
                ),
                const SizedBox(height: WalSpacing.sm),
                Text(
                  markExcerptEdges(item.body),
                  style: const TextStyle(
                    fontSize: WalType.body,
                    color: WalColors.ink,
                    height: 1.5,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: WalSpacing.sm),
          Text(
            storySourceLine(
              sourceDocumentId: item.sourceDocumentId,
              pagePdf: item.pagePdf,
            ),
            style: const TextStyle(
              fontSize: WalType.secondary,
              fontWeight: FontWeight.w600,
              color: WalColors.primaryText,
            ),
          ),
          if (item.personId != null) ...[
            const SizedBox(height: WalSpacing.md),
            OutlinedButton(
              onPressed: () => Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (_) => PersonDetailScreen(
                    personId: item.personId!,
                    stories: stories,
                  ),
                ),
              ),
              child: Text(
                'Về ${item.personName ?? "nhân vật"} ▸',
                style: const TextStyle(
                  fontSize: WalType.body,
                  color: WalColors.primaryText,
                ),
              ),
            ),
          ],
          const SizedBox(height: WalSpacing.md),
          const Text(
            'SAM sẽ kể thêm về mục này khi phần trò chuyện được mở — '
            'hiện tại con đang đọc đúng những gì sách viết.',
            style: TextStyle(
              fontSize: WalType.secondary,
              color: WalColors.inkSoft,
              height: 1.4,
            ),
          ),
          const SizedBox(height: WalSpacing.md),
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text(
              '◂ Quay lại',
              style: TextStyle(
                fontSize: WalType.body,
                color: WalColors.primaryText,
              ),
            ),
          ),
        ],
      ),
    ),
  );
}
