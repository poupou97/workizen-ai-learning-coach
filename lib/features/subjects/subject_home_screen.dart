/// WAL-136 (#07) — SUBJECT HOME: danh sách bài THẬT (tên mined từ SGK).
/// Bài Toán có bài tập corpus ⇒ vào học thẳng (CanonicalProblem.fromCurriculum
/// — sách là nguồn, không xác nhận giả). Bài chưa nối engine ⇒ nói thật.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/curriculum/canonical_problem.dart';
import '../../core/knowledge/provenance.dart';
import '../../core/store/learner_profile.dart';
import '../../core/store/learner_store.dart';
import '../learning_session/slice_flow.dart';
import 'lesson_index.dart';

class SubjectHomeScreen extends StatelessWidget {
  const SubjectHomeScreen({
    super.key,
    required this.profile,
    required this.store,
    required this.index,
    required this.subject,
  });

  final LearnerProfile profile;
  final LearnerStore store;
  final LessonIndex index;
  final String subject;

  bool get _isToan => subject == 'Toán';

  @override
  Widget build(BuildContext context) {
    final books = index.subjects[subject] ?? const <BookLessons>[];
    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(WalSpacing.lg),
          children: [
            Text('$subject · Lớp ${profile.grade}',
                style: const TextStyle(
                    fontSize: WalType.display,
                    fontWeight: FontWeight.w700,
                    color: WalColors.ink)),
            const SizedBox(height: WalSpacing.sm),
            for (final b in books) ...[
              if (b.volume != null || books.length > 1)
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: WalSpacing.sm),
                  child: Text(
                      b.volume == null ? 'Sách' : 'Tập ${b.volume}',
                      style: const TextStyle(
                          fontSize: WalType.secondary,
                          fontWeight: FontWeight.w700,
                          color: WalColors.inkSoft)),
                ),
              for (final l in b.lessons) _lessonTile(context, b, l),
            ],
            if (books.isEmpty)
              const Padding(
                padding: EdgeInsets.only(top: WalSpacing.xl),
                child: Text(
                  'SAM chưa có mục lục môn này trên máy.',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                      fontSize: WalType.body, color: WalColors.inkSoft),
                ),
              ),
            const SizedBox(height: WalSpacing.md),
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('◂ Môn học',
                  style: TextStyle(
                      fontSize: WalType.body, color: WalColors.primaryText)),
            ),
          ],
        ),
      ),
    );
  }

  Widget _lessonTile(BuildContext context, BookLessons b, LessonRef l) {
    final exercises = _isToan ? index.exercisesForToan(l.no) : const <CorpusExercise>[];
    final openable = exercises.isNotEmpty;
    return Padding(
      padding: const EdgeInsets.only(bottom: WalSpacing.sm),
      // Material bọc ListTile — nền + ink vẽ đúng chỗ (assertion framework).
      child: Material(
        color: openable ? Colors.white : WalColors.surfaceLavender,
        borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
        child: ListTile(
        title: Text(
          l.title == null ? 'Bài ${l.no}' : 'Bài ${l.no} · ${_titleCase(l.title!)}',
          style: const TextStyle(
              fontSize: WalType.body,
              fontWeight: FontWeight.w600,
              color: WalColors.ink),
        ),
        subtitle: Text(
          openable
              ? '${exercises.length} bài tập từ SGK — vào học ngay'
              : 'SAM đang học bài này — con chụp bài tập để học cùng nhé',
          style:
              const TextStyle(fontSize: WalType.secondary, color: WalColors.inkSoft),
        ),
        trailing: openable
            ? const Icon(Icons.chevron_right, color: WalColors.primaryText)
            : null,
          onTap:
              openable ? () => _openExercise(context, l, exercises.first) : null,
        ),
      ),
    );
  }

  /// «CỘNG, TRỪ HAI PHÂN SỐ…» → «Cộng, trừ hai phân số…» — tiêu đề mined in hoa.
  static String _titleCase(String upper) {
    final low = upper.toLowerCase();
    return low.isEmpty ? low : low[0].toUpperCase() + low.substring(1);
  }

  void _openExercise(BuildContext context, LessonRef l, CorpusExercise e) {
    // Sách là NGUỒN TIN: bài tập in trong SGK ⇒ sourceStated, có trang.
    final problem = CanonicalProblem.fromCurriculum(
      exerciseLabel: 'b${l.no}',
      expression: e.expr,
      provenance: Provenance(
        origin: KnowledgeOrigin.sourceStated,
        sourceId: e.book,
        extractionMethod: 'qmap-v1',
        confidence: 0.9,
        grade: index.grade,
        subject: subject,
        pageStart: e.page,
      ),
    );
    openCanonicalProblem(context,
        problem: problem, profile: profile, store: store);
  }
}
