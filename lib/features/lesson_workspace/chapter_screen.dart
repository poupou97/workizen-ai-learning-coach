/// TRACK B — CHƯƠNG: các bài trong một chương + trạng thái ĐÃ MỞ (trace).
///
/// «Đã xem (phiên này)» là dấu vết mở màn, KHÔNG phải trạng thái học (không
/// sao, không %, không «đã học»). Bài chưa có workspace ⇒ nói thật và dẫn về
/// mục lục hiện tại (đường cũ vẫn mở được bài đọc / thí nghiệm).
library;

import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart' show SchedulerBinding, SchedulerPhase;

import '../../app/theme/wal_tokens.dart';
import '../../core/lesson_model/lesson_document.dart';
import '../subjects/lesson_index.dart';
import 'lesson_workspace_screen.dart';
import 'widgets/fixture_chip.dart';
import 'workspace_trace.dart';

class ChapterScreen extends StatefulWidget {
  const ChapterScreen({
    super.key,
    required this.book,
    required this.chapter,
    required this.lessons,
    required this.docs,
    required this.trace,
    required this.onOpenLegacy,
  });

  final BookRef book;
  final ChapterRef chapter;

  /// Bài của chương này (đã lọc theo `chapter.lessonNos`), thứ tự mục lục.
  final List<LessonRef> lessons;
  final List<LessonDocument> docs;
  final WorkspaceTrace trace;
  final VoidCallback onOpenLegacy;

  @override
  State<ChapterScreen> createState() => _ChapterScreenState();
}

class _ChapterScreenState extends State<ChapterScreen> {
  @override
  void initState() {
    super.initState();
    widget.trace.addListener(_changed);
  }

  @override
  void dispose() {
    widget.trace.removeListener(_changed);
    super.dispose();
  }

  /// Trace đổi khi màn Workspace mở (trong pha build của route mới) ⇒ hoãn
  /// tới sau khung hình, không setState giữa lúc build (lỗi bắt được ở test).
  void _changed() {
    if (!mounted) return;
    if (SchedulerBinding.instance.schedulerPhase == SchedulerPhase.idle ||
        SchedulerBinding.instance.schedulerPhase ==
            SchedulerPhase.postFrameCallbacks) {
      setState(() {});
      return;
    }
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) setState(() {});
    });
  }

  LessonDocument? _docFor(int no) =>
      widget.docs.where((d) => d.lessonNo == no).firstOrNull;

  @override
  Widget build(BuildContext context) {
    final fixture = widget.docs.where((d) => d.isFixture).firstOrNull;
    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(
            WalSpacing.md,
            WalSpacing.xs,
            WalSpacing.md,
            WalSpacing.xl,
          ),
          children: [
            Row(
              children: [
                SizedBox(
                  width: WalSpacing.minTouch,
                  height: WalSpacing.minTouch,
                  child: IconButton(
                    tooltip: 'Về sách',
                    icon: const Icon(Icons.arrow_back, color: WalColors.ink),
                    onPressed: () => Navigator.of(context).maybePop(),
                  ),
                ),
                Expanded(
                  child: Text(
                    widget.book.title,
                    style: const TextStyle(
                      fontSize: WalType.secondary,
                      fontWeight: FontWeight.w700,
                      color: WalColors.inkSoft,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: WalSpacing.xs),
            Text(
              widget.chapter.label,
              style: const TextStyle(
                fontSize: WalType.secondary,
                fontWeight: FontWeight.w700,
                color: WalColors.primaryText,
              ),
            ),
            Text(
              LessonDocument.titleCase(widget.chapter.title),
              style: const TextStyle(
                fontSize: WalType.display,
                fontWeight: FontWeight.w700,
                color: WalColors.ink,
                height: 1.2,
              ),
            ),
            const SizedBox(height: WalSpacing.sm),
            if (fixture != null) FixtureChip(trust: fixture.trust),
            const SizedBox(height: WalSpacing.md),
            for (final l in widget.lessons) _row(context, l),
            if (widget.lessons.isEmpty)
              const Text(
                'Chương này chưa có bài nào trong mục lục trên máy.',
                style: TextStyle(
                  fontSize: WalType.body,
                  color: WalColors.inkSoft,
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _row(BuildContext context, LessonRef l) {
    final doc = _docFor(l.no);
    final title = l.title == null
        ? 'Bài ${l.no}'
        : 'Bài ${l.no} · ${LessonDocument.titleCase(l.title!)}';
    final opened = doc != null && widget.trace.opened(doc.slotKey);
    return Padding(
      padding: const EdgeInsets.only(bottom: WalSpacing.sm),
      child: Material(
        color: doc != null ? Colors.white : WalColors.surfaceLavender,
        borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
        child: ListTile(
          minVerticalPadding: WalSpacing.sm,
          title: Text(
            title,
            style: const TextStyle(
              fontSize: WalType.body,
              fontWeight: FontWeight.w600,
              color: WalColors.ink,
            ),
          ),
          subtitle: Text(
            doc != null
                ? '✨ Bài học SAM · Đọc · Trực quan · Học với SAM · '
                      '${widget.trace.childLabel(doc.slotKey)}'
                : 'Chưa có Bài học SAM — mở mục lục hiện tại',
            style: TextStyle(
              fontSize: WalType.secondary,
              color: opened ? WalColors.primaryText : WalColors.inkSoft,
            ),
          ),
          trailing: Icon(
            doc != null ? Icons.chevron_right : Icons.open_in_new,
            color: WalColors.primaryText,
          ),
          onTap: () async {
            if (doc == null) {
              widget.onOpenLegacy();
              return;
            }
            await Navigator.of(context).push(
              MaterialPageRoute(
                builder: (_) =>
                    LessonWorkspaceScreen(doc: doc, trace: widget.trace),
              ),
            );
          },
        ),
      ),
    );
  }
}
