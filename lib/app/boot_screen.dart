/// ROUND 3 B5 — màn KHỞI ĐỘNG: thay khung TRẮNG lúc app chưa nạp xong hồ sơ /
/// mission (audit 05 §4 «cold start blank», Track B O1).
///
/// Nguyên nhân có biên: `main.dart` dựng `Scaffold(body: SizedBox.shrink())`
/// trong hai khoảng chờ (profiles + mission). Màn này chỉ là NHÃN HIỆU + một
/// dòng nói thật «đang mở» — không tiến trình %, không spinner vô hồn (DESIGN
/// §3), không quyết định gì. Thiếu asset mascot ⇒ vẫn có chữ.
library;

import 'package:flutter/material.dart';

import 'theme/wal_tokens.dart';

class BootScreen extends StatelessWidget {
  const BootScreen({super.key, this.note = 'Đang mở…'});

  static const key_ = Key('boot-screen');

  /// Dòng phụ — nói việc đang chờ, không hứa hẹn.
  final String note;

  @override
  Widget build(BuildContext context) => Scaffold(
    key: key_,
    backgroundColor: WalColors.surface,
    body: SafeArea(
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Image.asset(
              'assets/mascot/sam-hello.png',
              width: 96,
              height: 96,
              errorBuilder: (_, _, _) => const SizedBox(width: 96, height: 96),
            ),
            const SizedBox(height: WalSpacing.md),
            const Text(
              'Học cùng SAM',
              style: TextStyle(
                fontSize: WalType.display,
                fontWeight: FontWeight.w700,
                color: WalColors.ink,
              ),
            ),
            const SizedBox(height: WalSpacing.xs),
            Text(
              note,
              style: const TextStyle(
                fontSize: WalType.secondary,
                color: WalColors.inkSoft,
              ),
            ),
          ],
        ),
      ),
    ),
  );
}
