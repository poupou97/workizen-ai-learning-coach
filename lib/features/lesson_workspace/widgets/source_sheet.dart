/// TRACK B — «Sách viết»: sheet nguồn của MỘT block. Nguyên văn + trang in +
/// (nếu có) ảnh vùng trang nội bộ. Withheld ⇒ placeholder thật, không chữ.
///
/// ROUND 4 (§6.3 sheet «tra cứu» cho neo nguồn · §6.10 điều hướng nguồn):
/// - dòng tra cứu «📖 Tra cứu · SGK KHTN 6 · Bài 17 · trang 61» (concept
///   concept-chuong khung 8);
/// - «Trong mục: …» từ đường heading của pipeline (khi có) — trẻ biết đoạn
///   nằm ở mục nào của bài, không phải chỉ trang;
/// - ảnh vùng trang NGUYÊN GỐC (không cắt mép) để đối chiếu với hình đã che
///   mép trong «Đọc» (D-R4 bleed guard);
/// - mã máy (id block, vai trò, pipeline, mã lý do giữ lại) chỉ nằm trong nếp
///   gấp «Chi tiết kỹ thuật» — không có mã nào trên phần trẻ đọc (§6.9).
library;

import 'package:flutter/material.dart';

import '../../../app/theme/wal_tokens.dart';
import '../../../core/lesson_model/lesson_document.dart';
import 'tech_details.dart';
import 'withheld_card.dart';

/// Chữ IN HOA của sách → dạng thường có hoa đầu; chữ thường giữ nguyên.
String _humanCase(String s) =>
    s == s.toUpperCase() ? LessonDocument.titleCase(s) : s;

/// «Trong mục: Nguyên tắc tách chất» — mục CON gần nhất trên đường heading
/// của pipeline, bỏ «Bài N» và tên bài (đã ở tiêu đề). `null` khi không có
/// đường heading (fixture cũ / mẫu) — không bịa mục.
String? sectionLineFor(LessonDocument doc, LessonBlock b) {
  final path = b.relations.headingPath;
  if (path.isEmpty) return null;
  final skip = {
    'bài ${doc.lessonNo}',
    doc.title.trim().toLowerCase(),
  };
  final rest = [
    for (final h in path)
      if (!skip.contains(h.trim().toLowerCase())) h,
  ];
  if (rest.isEmpty) return null;
  final last = rest.last.replaceFirst(RegExp(r'^[·•\-\s]+'), '').trim();
  if (last.isEmpty) return null;
  return 'Trong mục: ${_humanCase(last)}';
}

/// «📖 Tra cứu · SGK KHTN 6 · Bài 17 · trang 61» — từ dòng nguồn của block.
String lookupLineFor(LessonDocument doc, LessonBlock b) {
  final src = doc.sourceLineForBlock(b);
  final i = src.indexOf(' · ');
  final page = i < 0 ? src : src.substring(i + 3);
  return '📖 Tra cứu · SGK ${doc.bookTitle} · Bài ${doc.lessonNo} · $page';
}

/// Sự thật máy của một block — nguyên trạng, cho nếp gấp kỹ thuật.
List<String> techLinesFor(LessonDocument doc, LessonBlock b) {
  final r = b.sourceRef;
  return [
    'Mã phần: ${b.id}',
    'Vai trò máy: ${b.sourceRole ?? '—'}'
        '${b.roleMethod != null ? ' (${b.roleMethod})' : ''}'
        '${b.roleConfidence != null ? ' · tin cậy vai trò ${b.roleConfidence!.toStringAsFixed(2)}' : ''}',
    'Trang PDF ${r.pagePdf}'
        '${r.pagePrinted != null ? ' · trang in ${r.pagePrinted}' : ''}'
        ' · khung ${r.bbox.map((x) => x.toStringAsFixed(3)).join(', ')}',
    if (r.pipeline != null) 'Pipeline: ${r.pipeline}',
    if (r.extraction != null)
      'Trích: ${r.extraction}'
          '${r.ocrConf != null ? ' · OCR ${r.ocrConf!.toStringAsFixed(2)}' : ''}',
    if (r.agreementScore != null)
      'Đồng thuận hai stack: ${r.agreementScore!.toStringAsFixed(2)}',
    'Độ tin: ${b.trust.name}',
    if (b.relations.headingPath.isNotEmpty)
      'Đường mục: ${b.relations.headingPath.join(' › ')}',
    if (b is WithheldBlock)
      'Mã lý do giữ lại: ${b.reasons.join(', ')}'
          '${b.status != null ? ' · trạng thái ${b.status}' : ''}',
    if (b is ImageBlock && b.captionBlockId != null)
      'Chú thích máy gán: ${b.captionBlockId} (UI không dùng — liên kết '
          'pipeline còn sai, O5)',
    if (b is SourceRefBlock) 'Dòng nguồn máy: ${b.text}',
  ];
}

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
              '${doc.sourceLineForBlock(block)}'
              '${onTap != null ? ' · chạm để tra cứu' : ''}',
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
  final section = sectionLineFor(doc, block);
  return showModalBottomSheet<void>(
    context: context,
    backgroundColor: WalColors.surface,
    showDragHandle: true,
    isScrollControlled: true,
    builder: (sheet) => SafeArea(
      child: SingleChildScrollView(
        key: const Key('source-sheet'),
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
              const SizedBox(height: 2),
              Text(
                lookupLineFor(doc, block),
                key: const Key('source-lookup-line'),
                style: const TextStyle(
                  fontSize: WalType.secondary,
                  fontWeight: FontWeight.w600,
                  color: WalColors.primaryText,
                ),
              ),
              if (section != null)
                Text(
                  section,
                  key: const Key('source-section-line'),
                  style: const TextStyle(
                    fontSize: 13,
                    color: WalColors.inkSoft,
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
                  'Ảnh chụp trang sách · nguyên gốc (có thể lẫn chữ cạnh hình) '
                  '· chỉ để đối chiếu, không phát hành',
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
              const SizedBox(height: WalSpacing.sm),
              TechDetails(lines: techLinesFor(doc, block)),
            ],
          ),
        ),
      ),
    ),
  );
}
