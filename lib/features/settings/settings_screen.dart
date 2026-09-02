/// WAL-152 (§17) — SETTINGS tối giản: ENTRY POINT cho Kho khám phá.
/// Concept #38 đầy đủ vẫn ở holder WAL-146 — màn này chỉ mở phần cần thiết,
/// không giả các mục chưa tồn tại.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/stories/stories_store.dart';
import '../discovery/discovery_library_screen.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key, required this.stories});

  final StoriesStore stories;

  @override
  Widget build(BuildContext context) => Scaffold(
        backgroundColor: WalColors.surface,
        body: SafeArea(
          child: ListView(
            padding: const EdgeInsets.all(WalSpacing.lg),
            children: [
              const Text('Thêm',
                  style: TextStyle(
                      fontSize: WalType.display,
                      fontWeight: FontWeight.w700,
                      color: WalColors.ink)),
              const SizedBox(height: WalSpacing.md),
              Material(
                color: Colors.white,
                borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
                child: ListTile(
                  leading: const Text('🧭', style: TextStyle(fontSize: 26)),
                  title: const Text('Kho khám phá của SAM',
                      style: TextStyle(
                          fontSize: WalType.body,
                          fontWeight: FontWeight.w700,
                          color: WalColors.ink)),
                  subtitle: const Text(
                      'Danh nhân, câu nói, sự kiện, phát minh — từ chính SGK',
                      style: TextStyle(
                          fontSize: WalType.secondary,
                          color: WalColors.inkSoft)),
                  trailing: const Icon(Icons.chevron_right,
                      color: WalColors.primaryText),
                  onTap: () => Navigator.of(context).push(MaterialPageRoute(
                      builder: (_) =>
                          DiscoveryLibraryScreen(stories: stories))),
                ),
              ),
              const SizedBox(height: WalSpacing.md),
              const Text(
                'Các mục cài đặt khác (hồ sơ, quyền riêng tư, thông báo…) '
                'đang được SAM xây — sẽ xuất hiện ở đây khi sẵn sàng.',
                style: TextStyle(
                    fontSize: WalType.secondary,
                    color: WalColors.inkSoft,
                    height: 1.4),
              ),
              const SizedBox(height: WalSpacing.md),
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('◂ Về Hôm nay',
                    style: TextStyle(
                        fontSize: WalType.body, color: WalColors.primaryText)),
              ),
            ],
          ),
        ),
      );
}
