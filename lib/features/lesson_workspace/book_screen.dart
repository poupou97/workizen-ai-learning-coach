/// TRACK B — SÁCH: bìa thật + «Mục lục» theo CHƯƠNG (concept-chuong khung 3).
///
/// Chương suy từ MỤC LỤC in của chính cuốn sách (OCR, luật
/// `toc-ocr-chapters-v1` trong fixture) — không từ trí nhớ. Pack lớp 6 không
/// mang chương, nên khi không có fixture nào cho cuốn này thì màn này không
/// được mở (giá sách giữ hành vi cũ) — không có nhóm «bịa».
///
/// ROUND 5 B: khung concept-chuong 3 có ĐÚNG hai tab «Chương | Bài học».
/// Vòng 4 chỉ có danh sách chương, nên muốn tới một bài trẻ phải đoán nó nằm
/// chương nào. Tab «Bài học» liệt kê THẲNG mọi bài của cuốn, theo thứ tự mục
/// lục, dùng chung `LessonRow` với màn Chương ⇒ một vốn từ, một luật màu.
/// Không thêm dữ liệu nào: cùng `lessons` mục lục và cùng `docs`.
///
/// Đường cũ (Book Home + bài đọc / thí nghiệm) vẫn còn, một chạm.
library;

import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart' show SchedulerBinding, SchedulerPhase;

import '../../app/theme/wal_tokens.dart';
import '../../core/lesson_model/lesson_document.dart';
import '../../core/lesson_model/content_trust.dart';
import '../subjects/lesson_index.dart';
import 'chapter_screen.dart';
import 'widgets/fixture_chip.dart';
import 'widgets/lesson_row.dart';
import 'workspace_trace.dart';

class BookScreen extends StatelessWidget {
  const BookScreen({
    super.key,
    required this.book,
    required this.lessons,
    required this.docs,
    required this.trace,
    required this.onOpenLegacy,
    this.learnerId,
  });

  final BookRef book;

  /// Học sinh đang mở — chuyển xuống Workspace cho runtime (round 3).
  final String? learnerId;

  /// Mục lục thật của cuốn (từ pack) — thứ tự mục lục, không sắp lại.
  final List<LessonRef> lessons;
  final List<LessonDocument> docs;
  final WorkspaceTrace trace;

  /// Mở Book Home hiện tại (SubjectHomeScreen) — tầng trên dựng.
  final VoidCallback onOpenLegacy;

  static Key tocModeKey(String mode) => Key('book-toc-$mode');
  static Key lessonFilterKey(String id) => Key('book-lesson-filter-$id');

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
              const SizedBox(height: 2),
              // ROUND 3 B5 (audit O4): tên chương là chữ MỤC LỤC IN đọc máy,
              // giữ nguyên văn (có thể còn lỗi chữ) — nói rõ, không sửa tay.
              if (chapters.any((c) => c.derivation.startsWith('toc-ocr')))
                const Padding(
                  padding: EdgeInsets.only(bottom: WalSpacing.sm),
                  child: Text(
                    'Tên chương lấy từ mục lục in của sách (máy đọc, chưa '
                    'soát) — có thể còn lỗi chữ.',
                    style: TextStyle(fontSize: 12, color: WalColors.inkSoft),
                  ),
                )
              else
                const SizedBox(height: WalSpacing.sm - 2),
              // ROUND 4: hàng chương nghe trace ⇒ «Đã xem (phiên này)» hiện
              // ngay khi quay lại từ Chương/Workspace (dấu vết mở, không
              // phải trạng thái học).
              // ROUND 5: hai tab «Chương | Bài học» (khung concept-chuong 3).
              _TraceRebuilder(
                trace: trace,
                builder: (context) => _TocTabs(
                  chapters: [for (final c in chapters) _chapterRow(context, c)],
                  lessons: [
                    for (final l in lessons)
                      (
                        hasSam: docs.any((d) => d.lessonNo == l.no),
                        row: LessonRow(
                          lesson: l,
                          doc: docs
                              .where((d) => d.lessonNo == l.no)
                              .firstOrNull,
                          trace: trace,
                          onOpenLegacy: onOpenLegacy,
                          learnerId: learnerId,
                        ),
                      ),
                  ],
                ),
              ),
              const SizedBox(height: WalSpacing.md),
              Material(
                color: WalColors.surfaceLavender,
                borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
                child: ListTile(
                  // ROUND 4: không nói «bản hiện tại» với trẻ — chỉ nói có gì.
                  title: const Text(
                    'Các bài khác trong sách',
                    style: TextStyle(
                      fontSize: WalType.body,
                      fontWeight: FontWeight.w600,
                      color: WalColors.ink,
                    ),
                  ),
                  subtitle: const Text(
                    'Danh sách bài + bài đọc / thí nghiệm — như trong Môn học',
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

  static String _range(ChapterRef c) {
    if (c.lessonNos.isEmpty) return '';
    final a = c.lessonNos.first, b = c.lessonNos.last;
    return a == b ? 'Bài $a · ' : 'Bài $a–$b · ';
  }

  Widget _chapterRow(BuildContext context, ChapterRef c) {
    final ls = _lessonsOf(c);
    final withSam = docs.where((d) => c.contains(d.lessonNo)).length;
    final opened = docs.any(
      (d) => c.contains(d.lessonNo) && trace.opened(d.slotKey),
    );
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
            // ROUND 3 B1: dải số bài («Bài 16–17») để trẻ biết chương nằm
            // đâu trong sách — từ mục lục, không suy thêm.
            withSam > 0
                ? '${_range(c)}${ls.length} bài · ✨ $withSam bài học SAM'
                      '${opened ? ' · Đã xem (phiên này)' : ''}'
                : '${_range(c)}${ls.length} bài',
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
                learnerId: learnerId,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/// Dựng lại con khi trace đổi — HOÃN tới sau khung hình khi trace bắn giữa
/// lúc build (Workspace mở trong pha build của route mới; cùng lý do
/// `ChapterScreen._changed`). `ListenableBuilder` gọi setState ngay ⇒ lỗi
/// «markNeedsBuild during build» (bắt được ở boundary_test).
class _TraceRebuilder extends StatefulWidget {
  const _TraceRebuilder({required this.trace, required this.builder});
  final WorkspaceTrace trace;
  final WidgetBuilder builder;

  @override
  State<_TraceRebuilder> createState() => _TraceRebuilderState();
}

class _TraceRebuilderState extends State<_TraceRebuilder> {
  @override
  void initState() {
    super.initState();
    widget.trace.addListener(_changed);
  }

  @override
  void didUpdateWidget(_TraceRebuilder old) {
    super.didUpdateWidget(old);
    if (old.trace != widget.trace) {
      old.trace.removeListener(_changed);
      widget.trace.addListener(_changed);
    }
  }

  @override
  void dispose() {
    widget.trace.removeListener(_changed);
    super.dispose();
  }

  void _changed() {
    if (!mounted) return;
    final phase = SchedulerBinding.instance.schedulerPhase;
    if (phase == SchedulerPhase.idle ||
        phase == SchedulerPhase.postFrameCallbacks) {
      setState(() {});
      return;
    }
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) setState(() {});
    });
  }

  @override
  Widget build(BuildContext context) => widget.builder(context);
}

/// Hai tab «Chương | Bài học» — chỉ đổi CÁCH XẾP cùng một mục lục.
///
/// ROUND 5 D3 (Nokia, lượt 2): KHTN 6 có 55 bài và ĐÚNG MỘT bài có Bài học
/// SAM. Danh sách thẳng thành ra 54 hàng «Chưa có Bài học SAM» che mất hàng
/// duy nhất đáng mở — chính điều màn Sách vừa hứa ở đầu trang («✨ 1 bài học
/// SAM: Bài 17»). Thêm chip lọc CÙNG VỐN TỪ với giá sách. KHÔNG sắp xếp lại
/// mục lục: lọc chỉ ẩn hàng, thứ tự vẫn là thứ tự sách.
class _TocTabs extends StatefulWidget {
  const _TocTabs({required this.chapters, required this.lessons});
  final List<Widget> chapters;
  final List<({bool hasSam, Widget row})> lessons;

  @override
  State<_TocTabs> createState() => _TocTabsState();
}

class _TocTabsState extends State<_TocTabs> {
  bool _byLesson = false;
  bool _samOnly = false;

  @override
  Widget build(BuildContext context) {
    final sam = widget.lessons.where((e) => e.hasSam).length;
    final rows = [
      for (final e in widget.lessons)
        if (!_samOnly || e.hasSam) e.row,
    ];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (widget.lessons.isNotEmpty) ...[
          Row(
            children: [
              _tab('Chương', 'chapters', !_byLesson),
              const SizedBox(width: WalSpacing.sm),
              _tab('Bài học', 'lessons', _byLesson),
            ],
          ),
          const SizedBox(height: WalSpacing.sm),
        ],
        if (_byLesson && sam > 0 && sam < widget.lessons.length) ...[
          SizedBox(
            height: WalSpacing.minTouch,
            child: ListView(
              scrollDirection: Axis.horizontal,
              children: [
                _filter('Tất cả (${widget.lessons.length})', 'all', !_samOnly),
                _filter('✨ Bài học SAM ($sam)', 'sam', _samOnly),
              ],
            ),
          ),
          const SizedBox(height: WalSpacing.sm),
        ],
        ...(_byLesson ? rows : widget.chapters),
      ],
    );
  }

  Widget _filter(String label, String id, bool selected) => Padding(
    padding: const EdgeInsets.only(right: WalSpacing.sm),
    child: ChoiceChip(
      key: BookScreen.lessonFilterKey(id),
      label: Text(
        label,
        style: TextStyle(
          fontSize: WalType.secondary,
          fontWeight: FontWeight.w600,
          color: selected ? Colors.white : WalColors.ink,
        ),
      ),
      selected: selected,
      selectedColor: WalColors.primary500,
      backgroundColor: Colors.white,
      showCheckmark: false,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
      ),
      onSelected: (_) => setState(() => _samOnly = id == 'sam'),
    ),
  );

  Widget _tab(String label, String id, bool selected) => Expanded(
    child: SizedBox(
      height: WalSpacing.minTouch,
      child: Material(
        color: selected ? WalColors.primary500 : Colors.white,
        borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
        child: InkWell(
          key: BookScreen.tocModeKey(id),
          borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
          onTap: () => setState(() => _byLesson = id == 'lessons'),
          child: Center(
            child: Text(
              label,
              style: TextStyle(
                fontSize: WalType.body,
                fontWeight: FontWeight.w700,
                color: selected ? Colors.white : WalColors.ink,
              ),
            ),
          ),
        ),
      ),
    ),
  );
}
