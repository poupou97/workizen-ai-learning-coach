/// WAL-142 #19 — LEARNING MAP: cây bài THẬT theo môn (lesson-index) + trạng
/// thái HONEST per-lesson: chỉ bài có evidence mới có badge — không tô màu
/// tiến-độ-ảo cho bài chưa học.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/knowledge/slice_curriculum.dart';
import '../../core/store/learner_profile.dart';
import '../../core/store/learner_store.dart';
import '../../core/student/concept_summary.dart';
import '../learning_session/slice_flow.dart' show masteryFromStore;
import '../subjects/lesson_index.dart';

class LearningMapScreen extends StatefulWidget {
  const LearningMapScreen(
      {super.key,
      required this.profile,
      required this.store,
      required this.index});
  final LearnerProfile profile;
  final LearnerStore store;
  final LessonIndex? index;

  @override
  State<LearningMapScreen> createState() => _LearningMapScreenState();
}

class _LearningMapScreenState extends State<LearningMapScreen> {
  ConceptClaim? _b6Claim; // slice: chỉ Toán B6 có mastery thật hôm nay
  bool _loaded = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final c = curriculumFor(widget.profile);
    if (c != null) {
      final m = await masteryFromStore(
          widget.store, widget.profile.learnerId, c);
      final hasEvidence =
          m.cases.values.any((cm) => cm.hasEvidence);
      if (hasEvidence) {
        _b6Claim = ConceptSummary.of(m,
                knownCaseIds: {for (final k in c.cases) k.id},
                now: DateTime.now())
            .claim;
      }
    }
    if (mounted) setState(() => _loaded = true);
  }

  @override
  Widget build(BuildContext context) {
    final idx = widget.index;
    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: !_loaded
            ? const SizedBox.shrink()
            : ListView(
                padding: const EdgeInsets.all(WalSpacing.lg),
                children: [
                  const Text('Bản đồ học tập',
                      style: TextStyle(
                          fontSize: WalType.display,
                          fontWeight: FontWeight.w700,
                          color: WalColors.ink)),
                  const SizedBox(height: WalSpacing.sm),
                  if (idx == null)
                    const Text('SAM chưa nạp mục lục trên máy này.',
                        style: TextStyle(
                            fontSize: WalType.body, color: WalColors.inkSoft))
                  else
                    for (final subject in idx.subjects.keys) ...[
                      Padding(
                        padding:
                            const EdgeInsets.symmetric(vertical: WalSpacing.sm),
                        child: Text(subject,
                            style: const TextStyle(
                                fontSize: WalType.title,
                                fontWeight: FontWeight.w700,
                                color: WalColors.ink)),
                      ),
                      for (final b in idx.subjects[subject]!)
                        for (final l in b.lessons) _lessonRow(subject, l),
                    ],
                ],
              ),
      ),
    );
  }

  Widget _lessonRow(String subject, LessonRef l) {
    // Badge CHỈ khi có bằng chứng thật (slice: Toán B6).
    final isB6 = subject == 'Toán' && l.no == 6;
    final claim = isB6 ? _b6Claim : null;
    final badge = switch (claim) {
      null => null,
      ConceptClaim.mastered => LearningStateToken.mastered,
      ConceptClaim.strongOnObserved => LearningStateToken.strongOnObserved,
      _ => LearningStateToken.developing,
    };
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(children: [
        Expanded(
          child: Text('Bài ${l.no}${l.title == null ? '' : ' · ${l.title}'}',
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                  fontSize: WalType.secondary, color: WalColors.ink)),
        ),
        if (badge != null)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
            decoration: BoxDecoration(
                color: badge.bg, borderRadius: BorderRadius.circular(8)),
            child: Text('đang học cùng SAM',
                style: TextStyle(fontSize: 12, color: badge.fg)),
          ),
      ]),
    );
  }
}
