/// WAL-133 — MỘT chỗ vẽ tài sản hình ảnh, để luật nhãn không thể quên.
///
/// Không có tham số nào tắt được nhãn «Minh hoạ của SAM». Nếu nhãn là một
/// tuỳ chọn thì sớm muộn có màn nào đó tắt nó đi «cho gọn», và ta mất đúng
/// thứ mô hình tài sản sinh ra để bảo vệ.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/assets/learning_asset.dart';

class LearningAssetImage extends StatelessWidget {
  const LearningAssetImage({super.key, required this.asset, this.fit});

  final LearningAsset asset;
  final BoxFit? fit;

  @override
  Widget build(BuildContext context) {
    final label = mandatoryLabelOf(asset);
    final missing = missingNoticeOf(asset);
    final img = Image.asset(
      asset.path,
      fit: fit ?? BoxFit.contain,
      // Thiếu tệp: ảnh nguồn thì NÓI, trang trí thì im (hậu quả khác nhau).
      errorBuilder: (_, _, _) => missing == null
          ? const SizedBox.shrink()
          : Center(
              child: Padding(
                padding: const EdgeInsets.all(WalSpacing.lg),
                child: Text(missing,
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                        fontSize: WalType.secondary,
                        color: WalColors.inkSoft)),
              ),
            ),
    );
    if (label == null) return img;
    return Stack(children: [
      Positioned.fill(child: img),
      Positioned(
        left: 8,
        bottom: 8,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
          decoration: BoxDecoration(
              color: WalColors.surfaceLavender,
              borderRadius: BorderRadius.circular(8)),
          child: Text(label,
              style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                  color: WalColors.ink)),
        ),
      ),
    ]);
  }
}
