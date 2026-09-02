/// WAL-136 (#03/#06) — MÔN HỌC: grid SINH TỪ DATA theo grade của learner.
/// Không %, không hardcode danh sách môn, môn thiếu index nói thật.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/store/learner_profile.dart';
import '../../core/store/learner_store.dart';
import 'lesson_index.dart';
import 'subject_home_screen.dart';

const _subjectEmoji = {
  'Toán': '🔢', 'Tiếng Việt': '📖', 'Tiếng Anh': '🌍', 'Khoa học': '🔬',
  'LS&ĐL': '🗺️', 'Tin học': '💻', 'Đạo đức': '🤝', 'Âm nhạc': '🎵',
  'GDTC': '⚽', 'HĐTN': '🌱', 'Mĩ thuật': '🎨', 'Công nghệ': '🔧',
};

class SubjectsScreen extends StatelessWidget {
  const SubjectsScreen({
    super.key,
    required this.profile,
    required this.store,
    required this.index,
  });

  final LearnerProfile profile;
  final LearnerStore store;

  /// `null` = máy chưa build lesson-index — màn nói thật, không bịa grid.
  final LessonIndex? index;

  @override
  Widget build(BuildContext context) {
    final subjects = index?.subjects.keys.toList() ?? const <String>[];
    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(WalSpacing.lg),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text('Môn học · Lớp ${profile.grade}',
                style: const TextStyle(
                    fontSize: WalType.display,
                    fontWeight: FontWeight.w700,
                    color: WalColors.ink)),
            const SizedBox(height: WalSpacing.md),
            if (subjects.isEmpty)
              const Expanded(
                child: Center(
                  child: Text(
                    'SAM chưa nạp mục lục môn học trên máy này.\n'
                    'Con vẫn chụp bài tập để học được nhé!',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                        fontSize: WalType.body,
                        color: WalColors.inkSoft,
                        height: 1.5),
                  ),
                ),
              )
            else
              Expanded(
                child: GridView.count(
                  crossAxisCount: 2,
                  mainAxisSpacing: WalSpacing.sm,
                  crossAxisSpacing: WalSpacing.sm,
                  childAspectRatio: 1.6,
                  children: [
                    for (final s in subjects)
                      InkWell(
                        borderRadius:
                            BorderRadius.circular(WalSpacing.radiusCard),
                        onTap: () => Navigator.of(context).push(
                            MaterialPageRoute(
                                builder: (_) => SubjectHomeScreen(
                                    profile: profile,
                                    store: store,
                                    index: index!,
                                    subject: s))),
                        child: Container(
                          padding: const EdgeInsets.all(WalSpacing.md),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius:
                                BorderRadius.circular(WalSpacing.radiusCard),
                          ),
                          child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Text(_subjectEmoji[s] ?? '📘',
                                    style: const TextStyle(fontSize: 28)),
                                const SizedBox(height: 6),
                                Text(s,
                                    style: const TextStyle(
                                        fontSize: WalType.body,
                                        fontWeight: FontWeight.w700,
                                        color: WalColors.ink)),
                              ]),
                        ),
                      ),
                  ],
                ),
              ),
            SizedBox(
              height: WalSpacing.minTouch,
              child: TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('Về Hôm nay',
                    style: TextStyle(
                        fontSize: WalType.body, color: WalColors.primaryText)),
              ),
            ),
          ]),
        ),
      ),
    );
  }
}
