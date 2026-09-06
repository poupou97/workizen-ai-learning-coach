/// ROUND 4 (Lane B §6.9 «no machine ids anywhere child-facing») — «Chi tiết
/// kỹ thuật»: mã máy (mã block, luật sinh, mã lý do giữ lại, pipeline, mã từ
/// chối của runtime) nằm SAU một nếp gấp ĐÓNG mặc định. Trẻ đọc màn không gặp
/// mã nào; người lớn/Founder mở nếp gấp thì thấy đủ — không xoá thông tin,
/// chỉ đổi chỗ. Test `no_machine_ids_test` quét mọi chữ NHÌN THẤY (nếp gấp
/// đóng) và ghim rằng mở nếp gấp mới thấy mã.
library;

import 'package:flutter/material.dart';

import '../../../app/theme/wal_tokens.dart';

class TechDetails extends StatelessWidget {
  const TechDetails({
    super.key,
    required this.lines,
    this.title = 'Chi tiết kỹ thuật (dành cho người lớn)',
  });

  static const foldKey = Key('tech-details');

  /// Mỗi dòng một sự thật máy — nguyên trạng, không dịch, không tô đẹp.
  final List<String> lines;
  final String title;

  @override
  Widget build(BuildContext context) {
    if (lines.isEmpty) return const SizedBox.shrink();
    return Theme(
      data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
      child: ExpansionTile(
        key: foldKey,
        tilePadding: EdgeInsets.zero,
        childrenPadding: const EdgeInsets.only(bottom: WalSpacing.sm),
        expandedCrossAxisAlignment: CrossAxisAlignment.start,
        iconColor: WalColors.inkSoft,
        collapsedIconColor: WalColors.inkSoft,
        title: Text(
          '🔧 $title',
          style: const TextStyle(fontSize: 13, color: WalColors.inkSoft),
        ),
        children: [
          for (final l in lines)
            Padding(
              padding: const EdgeInsets.only(bottom: 2),
              child: Text(
                l,
                style: const TextStyle(
                  fontSize: 11,
                  color: WalColors.inkSoft,
                  height: 1.35,
                ),
              ),
            ),
        ],
      ),
    );
  }
}
