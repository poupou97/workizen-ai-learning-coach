/// WAL-152 (§17) — SETTINGS tối giản: ENTRY POINT cho Kho khám phá.
/// Concept #38 đầy đủ vẫn ở holder WAL-146 — màn này chỉ mở phần cần thiết,
/// không giả các mục chưa tồn tại.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/stories/stories_store.dart';
import '../../core/store/learner_profile.dart';
import '../../core/store/learner_store.dart';
import '../discovery/discovery_library_screen.dart';
import '../learning_map/learning_map_screen.dart';
import '../progress/progress_screen.dart';
import '../student/sessions_screen.dart';
import '../profile/profile_screen.dart';
import '../subjects/lesson_index.dart';
import '../timetable/timetable_screen.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen(
      {super.key,
      required this.stories,
      this.profile,
      this.store,
      this.index,
      this.profiles = const [],
      this.onProfileChanged});

  final StoriesStore stories;
  final LearnerProfile? profile;
  final LearnerStore? store;
  final LessonIndex? index;

  /// WAL-137: hồ sơ khác trên cùng máy — màn Hồ sơ nói rõ «đang sửa của ai».
  final List<LearnerProfile> profiles;

  /// Gọi sau khi sửa hồ sơ để cả app nạp lại đúng người.
  final void Function(LearnerProfile saved)? onProfileChanged;

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
              // WAL-142 — ba lối vào truths (chỉ khi có hồ sơ thật).
              if (profile != null && store != null) ...[
                const SizedBox(height: WalSpacing.sm),
                _entry(context, '🌱', 'Tiến bộ của con',
                    'Điều SAM biết chắc — có bằng chứng, không điểm số',
                    (c) => ProgressScreen(profile: profile!, store: store!)),
                const SizedBox(height: WalSpacing.sm),
                _entry(context, '🗺️', 'Bản đồ học tập',
                    'Cây bài theo môn — bài nào đang học cùng SAM',
                    (c) => LearningMapScreen(
                        profile: profile!, store: store!, index: index)),
                const SizedBox(height: WalSpacing.sm),
                _entry(context, '🕰️', 'Các phiên học',
                    'Lịch sử phiên — tự làm hay có SAM giúp',
                    (c) => SessionsScreen(profile: profile!, store: store!)),
                const SizedBox(height: WalSpacing.sm),
                // WAL-137 — hồ sơ + thời khoá biểu.
                _entry(
                    context,
                    '👤',
                    'Hồ sơ của ${profile!.displayName}',
                    'Tên, lớp đang học, năm sinh (không bắt buộc)',
                    (c) => ProfileScreen(
                        profile: profile!,
                        store: store!,
                        onSaved: onProfileChanged,
                        otherProfiles: [
                          for (final p in profiles)
                            if (p.learnerId != profile!.learnerId) p
                        ])),
                const SizedBox(height: WalSpacing.sm),
                _entry(
                    context,
                    '🗓️',
                    'Thời khoá biểu',
                    'Không bắt buộc — chỉ giúp SAM xếp thứ tự gợi ý',
                    (c) => TimetableScreen(
                        profile: profile!,
                        store: store!,
                        subjects: index?.subjects.keys.toList() ?? const [])),
              ],
              const SizedBox(height: WalSpacing.md),
              const Text(
                // WAL-137: hồ sơ ĐÃ có ở trên — bỏ khỏi danh sách «đang xây»,
                // vì một câu hứa thừa cũng là một câu không đúng.
                'Các mục cài đặt khác (quyền riêng tư, thông báo…) đang được '
                'SAM xây — sẽ xuất hiện ở đây khi sẵn sàng.',
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

  Widget _entry(BuildContext context, String emoji, String title,
          String subtitle, Widget Function(BuildContext) builder) =>
      Material(
        color: Colors.white,
        borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
        child: ListTile(
          leading: Text(emoji, style: const TextStyle(fontSize: 26)),
          title: Text(title,
              style: const TextStyle(
                  fontSize: WalType.body,
                  fontWeight: FontWeight.w700,
                  color: WalColors.ink)),
          subtitle: Text(subtitle,
              style: const TextStyle(
                  fontSize: WalType.secondary, color: WalColors.inkSoft)),
          trailing:
              const Icon(Icons.chevron_right, color: WalColors.primaryText),
          onTap: () => Navigator.of(context)
              .push(MaterialPageRoute(builder: builder)),
        ),
      );
}
