/// WAL-142 #19 — LEARNING MAP: cây bài THẬT theo môn (lesson-index) + trạng
/// thái HONEST per-lesson: chỉ bài có evidence mới có badge — không tô màu
/// tiến-độ-ảo cho bài chưa học.
///
/// WAL-142 QA (Nokia n64): bản đầu đổ THẲNG 251 dòng theo thứ tự map JSON ⇒
/// GDTC đứng đầu, bài DUY NHẤT có badge (Toán B6) nằm dưới ~200 dòng — đúng
/// dữ liệu nhưng CHÔN mất điều màn này sinh ra để nói. Sửa: môn CÓ BẰNG CHỨNG
/// lên đầu và mở sẵn; môn khác gập lại kèm số bài (vẫn mở xem được — không
/// giấu dữ liệu, chỉ thôi bắt trẻ cuộn).
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
  final Set<String> _open = {};

  /// Môn đang có bằng chứng thật (slice hiện tại: Toán). `null` = kho trắng.
  String? get _evidenceSubject => _b6Claim == null ? null : 'Toán';

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
    if (mounted) {
      setState(() {
        _loaded = true;
        final s = _evidenceSubject;
        if (s != null) _open.add(s); // môn đang học: mở sẵn
      });
    }
  }

  /// Môn có bằng chứng lên trước; còn lại GIỮ NGUYÊN thứ tự mục lục.
  List<String> _orderedSubjects(LessonIndex idx) {
    final s = _evidenceSubject;
    final keys = idx.subjects.keys.toList();
    if (s == null || !keys.contains(s)) return keys;
    return [s, ...keys.where((k) => k != s)];
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
                    for (final subject in _orderedSubjects(idx))
                      _subjectBlock(idx, subject),
                ],
              ),
      ),
    );
  }

  Widget _subjectBlock(LessonIndex idx, String subject) {
    final books = idx.subjects[subject]!;
    final total = books.fold<int>(0, (n, b) => n + b.lessons.length);
    final open = _open.contains(subject);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        InkWell(
          onTap: () => setState(
              () => open ? _open.remove(subject) : _open.add(subject)),
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: WalSpacing.sm),
            child: Row(children: [
              Expanded(
                child: Text('$subject · $total bài',
                    style: const TextStyle(
                        fontSize: WalType.title,
                        fontWeight: FontWeight.w700,
                        color: WalColors.ink)),
              ),
              Icon(open ? Icons.expand_less : Icons.expand_more,
                  color: WalColors.inkSoft),
            ]),
          ),
        ),
        if (open)
          for (final b in books) ...[
            // Nhiều tập trong một môn ⇒ nói rõ tập nào, không để «Bài 1» lặp
            // hai lần trông như lỗi.
            if (books.length > 1 && b.volume != null)
              Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Text('Tập ${b.volume}',
                    style: const TextStyle(
                        fontSize: WalType.secondary,
                        fontWeight: FontWeight.w700,
                        color: WalColors.inkSoft)),
              ),
            for (final l in b.lessons) _lessonRow(subject, l),
          ],
      ],
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
