/// TRACK B — SÁCH: bìa thật + «Mục lục» theo CHƯƠNG (concept-chuong khung 3).
///
/// Chương suy từ MỤC LỤC in của chính cuốn sách (OCR, luật
/// `toc-ocr-chapters-v1` trong fixture) — không từ trí nhớ. Pack lớp 6 không
/// mang chương, nên khi không có fixture nào cho cuốn này thì màn này không
/// được mở (giá sách giữ hành vi cũ) — không có nhóm «bịa».
///
/// Đường cũ (Book Home + bài đọc / thí nghiệm) vẫn còn, một chạm.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/lesson_model/lesson_document.dart';
import '../../core/lesson_model/content_trust.dart';
import '../subjects/lesson_index.dart';
import 'chapter_screen.dart';
import 'widgets/fixture_chip.dart';
import 'workspace_trace.dart';

class BookScreen extends StatelessWidget {
  const BookScreen({
    super.key,
    required this.book,
    required this.lessons,
    required this.docs,
    required this.trace,
    required this.onOpenLegacy,
  });

  final BookRef book;

  /// Mục lục thật của cuốn (từ pack) — thứ tự mục lục, không sắp lại.
  final List<LessonRef> lessons;
  final List<LessonDocument> docs;
  final WorkspaceTrace trace;

  /// Mở Book Home hiện tại (SubjectHomeScreen) — tầng trên dựng.
  final VoidCallback onOpenLegacy;

  /// Chương của cuốn: từ fixture đầu tiên có `chapters`; bài không thuộc
  /// chương nào ⇒ nhóm «Bài khác» (nói thật là mục lục chưa xếp được).
  List<ChapterRef> chaptersFor() {
    final base = docs.where((d) => d.chapters.isNotEmpty).firstOrNull;
    final chapters = [...?base?.chapters];
    final covered = {for (final c in chapters) ...c.lessonNos};
    final rest = [
      for (final l in lessons)
        if (!covered.contains(l.no)) l.no,
    ];
    if (rest.isNotEmpty) {
      chapters.add(
        ChapterRef(
          label: chapters.isEmpty ? 'Mục lục' : 'Bài khác',
          title: chapters.isEmpty
              ? 'Tất cả bài học'
              : 'Chưa xếp được vào chương',
          lessonNos: rest,
          trust: ContentTrust.prototype,
          derivation: 'uncovered-by-toc',
        ),
      );
    }
    return chapters;
  }

  List<LessonRef> _lessonsOf(ChapterRef c) => [
    for (final l in lessons)
      if (c.contains(l.no)) l,
  ];

  @override
  Widget build(BuildContext context) {
    final chapters = chaptersFor();
    final fixture = docs.where((d) => d.isFixture).firstOrNull;
    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(
            WalSpacing.md,
            WalSpacing.xs,
            WalSpacing.md,
            WalSpacing.xl,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                children: [
                  SizedBox(
                    width: WalSpacing.minTouch,
                    height: WalSpacing.minTouch,
                    child: IconButton(
                      tooltip: 'Về giá sách',
                      icon: const Icon(Icons.arrow_back, color: WalColors.ink),
                      onPressed: () => Navigator.of(context).maybePop(),
                    ),
                  ),
                  const Text(
                    'Giá sách',
                    style: TextStyle(
                      fontSize: WalType.secondary,
                      fontWeight: FontWeight.w700,
                      color: WalColors.inkSoft,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: WalSpacing.sm),
              _coverHeader(),
              const SizedBox(height: WalSpacing.md),
              if (fixture != null) FixtureChip(trust: fixture.trust),
              const SizedBox(height: WalSpacing.md),
              const Text(
                'Mục lục',
                style: TextStyle(
                  fontSize: WalType.title,
                  fontWeight: FontWeight.w700,
                  color: WalColors.ink,
                ),
              ),
              const SizedBox(height: WalSpacing.sm),
              for (final c in chapters) _chapterRow(context, c),
              const SizedBox(height: WalSpacing.md),
              Material(
                color: WalColors.surfaceLavender,
                borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
                child: ListTile(
                  title: const Text(
                    'Mục lục & hoạt động (bản hiện tại)',
                    style: TextStyle(
                      fontSize: WalType.body,
                      fontWeight: FontWeight.w600,
                      color: WalColors.ink,
                    ),
                  ),
                  subtitle: const Text(
                    'Danh sách bài + bài đọc / thí nghiệm như trước',
                    style: TextStyle(
                      fontSize: WalType.secondary,
                      color: WalColors.inkSoft,
                    ),
                  ),
                  trailing: const Icon(
                    Icons.open_in_new,
                    color: WalColors.primaryText,
                  ),
                  onTap: onOpenLegacy,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _coverHeader() => Row(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      ClipRRect(
        borderRadius: BorderRadius.circular(8),
        child: SizedBox(
          width: 96,
          height: 128,
          child: Image.asset(
            'assets/pack/${book.cover}',
            fit: BoxFit.cover,
            errorBuilder: (_, _, _) => Container(
              color: WalColors.surfaceLavender,
              alignment: Alignment.center,
              padding: const EdgeInsets.all(WalSpacing.sm),
              child: Text(
                book.title,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: WalType.secondary,
                  fontWeight: FontWeight.w700,
                  color: WalColors.ink,
                ),
              ),
            ),
          ),
        ),
      ),
      const SizedBox(width: WalSpacing.md),
      Expanded(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              book.volumeLabel == null
                  ? book.title
                  : '${book.title} · ${book.volumeLabel}',
              style: const TextStyle(
                fontSize: WalType.display,
                fontWeight: FontWeight.w700,
                color: WalColors.ink,
                height: 1.15,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              '${book.subject} · ${lessons.length} bài',
              style: const TextStyle(
                fontSize: WalType.secondary,
                color: WalColors.inkSoft,
              ),
            ),
            const SizedBox(height: WalSpacing.sm),
            Text(
              docs.isEmpty
                  ? 'Chưa có bài học SAM trong cuốn này.'
                  : '✨ ${docs.length} bài học SAM: '
                        '${docs.map((d) => 'Bài ${d.lessonNo}').join(', ')}',
              style: const TextStyle(
                fontSize: WalType.secondary,
                fontWeight: FontWeight.w600,
                color: WalColors.primaryText,
              ),
            ),
          ],
        ),
      ),
    ],
  );

  Widget _chapterRow(BuildContext context, ChapterRef c) {
    final ls = _lessonsOf(c);
    final withSam = docs.where((d) => c.contains(d.lessonNo)).length;
    return Padding(
      padding: const EdgeInsets.only(bottom: WalSpacing.sm),
      child: Material(
        color: Colors.white,
        borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
        child: ListTile(
          minVerticalPadding: WalSpacing.sm,
          title: Text(
            '${c.label} · ${LessonDocument.titleCase(c.title)}',
            style: const TextStyle(
              fontSize: WalType.body,
              fontWeight: FontWeight.w600,
              color: WalColors.ink,
            ),
          ),
          subtitle: Text(
            withSam > 0
                ? '${ls.length} bài · ✨ $withSam bài học SAM'
                : '${ls.length} bài',
            style: TextStyle(
              fontSize: WalType.secondary,
              color: withSam > 0 ? WalColors.primaryText : WalColors.inkSoft,
            ),
          ),
          trailing: const Icon(
            Icons.chevron_right,
            color: WalColors.primaryText,
          ),
          onTap: () => Navigator.of(context).push(
            MaterialPageRoute(
              builder: (_) => ChapterScreen(
                book: book,
                chapter: c,
                lessons: ls,
                docs: docs,
                trace: trace,
                onOpenLegacy: onOpenLegacy,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
