/// WAL-133 — «Hình trong sách»: hình SGK đã crop, mỗi hình đi kèm ĐÚNG những
/// gì chứng minh được về nó.
///
/// Ba lớp chữ, KHÔNG BAO GIỜ trộn:
/// 1. caption IN trong sách — nguyên văn, không có thì để trống, không bịa;
/// 2. lời của SAM — luôn có nhãn «SAM nói thêm», để trẻ biết ai đang nói;
/// 3. dòng nguồn — sách nào, trang in nào.
///
/// Cùng luật với SourceReader (WAL-113): trẻ phải luôn phân biệt được đâu là
/// sách nói, đâu là SAM nói.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../shell/learning_asset_image.dart';
import 'lesson_index.dart';
import 'subject_display.dart';

class SourceGalleryScreen extends StatelessWidget {
  const SourceGalleryScreen({
    super.key,
    required this.subject,
    required this.assets,
    this.bookTitles = const {},
  });

  final String subject;
  final List<IndexedSourceAsset> assets;

  /// ROUND 3 B5: mã sách → tên sách trong mục lục pack, để dòng nguồn đọc là
  /// «SGK Toán 6 · trang 22» thay vì «06-sgk-toan-6-tap-mot · trang 22».
  /// Không có tên ⇒ giữ mã (thật, không bịa).
  final Map<String, String> bookTitles;

  @override
  Widget build(BuildContext context) => Scaffold(
        backgroundColor: WalColors.surface,
        body: SafeArea(
          child: ListView(
            padding: const EdgeInsets.all(WalSpacing.lg),
            children: [
              Text('Hình trong sách · $subject',
                  style: const TextStyle(
                      fontSize: WalType.display,
                      fontWeight: FontWeight.w700,
                      color: WalColors.ink)),
              const SizedBox(height: WalSpacing.sm),
              const Text(
                  'Đây là hình chụp lại từ sách giáo khoa của con — không phải '
                  'hình SAM vẽ.',
                  style: TextStyle(
                      fontSize: WalType.secondary, color: WalColors.inkSoft)),
              const SizedBox(height: WalSpacing.md),
              for (final a in assets) ...[
                _card(a),
                const SizedBox(height: WalSpacing.md),
              ],
            ],
          ),
        ),
      );

  Widget _card(IndexedSourceAsset a) {
    final asset = a.toAsset();
    final printed = a.printedCaption;
    final gloss = a.samGloss;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(WalSpacing.lg),
      decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(WalSpacing.radiusCard)),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        SizedBox(
          height: 260,
          width: double.infinity,
          child: InteractiveViewer(
              maxScale: 6,
              child: LearningAssetImage(asset: asset, fit: BoxFit.contain)),
        ),
        // Caption của SÁCH — chỉ hiện khi sách THẬT SỰ in một caption.
        if (printed != null) ...[
          const SizedBox(height: WalSpacing.sm),
          Text(printed,
              style: const TextStyle(
                  fontSize: WalType.body,
                  fontWeight: FontWeight.w700,
                  color: WalColors.ink)),
        ],
        // Lời SAM — LUÔN có nhãn, không bao giờ đứng lẫn với lời sách.
        if (gloss != null) ...[
          const SizedBox(height: WalSpacing.sm),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(WalSpacing.sm),
            decoration: BoxDecoration(
                color: WalColors.surfaceLavender,
                borderRadius: BorderRadius.circular(8)),
            child:
                Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              const Text('SAM NÓI THÊM',
                  style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 0.6,
                      color: WalColors.inkSoft)),
              const SizedBox(height: 4),
              Text(gloss,
                  style: const TextStyle(
                      fontSize: WalType.secondary,
                      color: WalColors.ink,
                      height: 1.4)),
            ]),
          ),
        ],
        const SizedBox(height: WalSpacing.sm),
        Text(
            childSourceLine(
                sourceDocumentId: a.sourceDocumentId,
                pagePrinted: a.pagePrinted,
                bookTitles: bookTitles),
            style: const TextStyle(
                fontSize: WalType.secondary, color: WalColors.inkSoft)),
      ]),
    );
  }
}
