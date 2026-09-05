/// TRACK B — LESSON WORKSPACE: một bài, ba cách học, một bước tiếp.
///
/// Khung «duy nhất mới» của concept (16-UX-CONCEPT §3): tiêu đề «Bài N ·
/// tên», chip thử nghiệm (bắt buộc khi là fixture), segmented control
/// [📖 Đọc] [✨ Trực quan] [🦉 Học với SAM], thẻ «SAM đề xuất» có lý do tất
/// định, rồi thân View. Nhảy giữa View mang theo block (Đọc → SAM; Trực quan
/// → Đọc) — không hỏi lại gì.
///
/// Màn này KHÔNG nhận `LearnerStore` — theo cấu trúc, không ghi được gì.
library;

import 'package:flutter/material.dart';

import '../../app/theme/band_density_scope.dart';
import '../../app/theme/wal_tokens.dart';
import '../../core/lesson_model/lesson_document.dart';
import '../../core/lesson_model/next_action.dart';
import '../../core/lesson_model/tutor_script.dart';
import 'smart_book_view.dart';
import 'tutor_view.dart';
import 'visual_view.dart';
import 'widgets/fixture_chip.dart';
import 'workspace_trace.dart';

class LessonWorkspaceScreen extends StatefulWidget {
  const LessonWorkspaceScreen({
    super.key,
    required this.doc,
    required this.trace,
    this.initialView,
  });

  final LessonDocument doc;
  final WorkspaceTrace trace;

  /// `null` ⇒ mở ở View SAM đề xuất (tất định từ dữ liệu bài).
  final WorkspaceView? initialView;

  static Key tabKey(WorkspaceView v) => Key('workspace-tab-${v.name}');
  static const nextActionKey = Key('workspace-next-action');

  @override
  State<LessonWorkspaceScreen> createState() => _LessonWorkspaceScreenState();
}

class _LessonWorkspaceScreenState extends State<LessonWorkspaceScreen> {
  late WorkspaceView _view;
  String? _tutorAnchor;
  String? _readAnchor;
  int _fontStep = 0;

  LessonDocument get doc => widget.doc;
  Set<WorkspaceView> get _seen => widget.trace.viewsFor(doc.slotKey);

  @override
  void initState() {
    super.initState();
    widget.trace.markOpened(doc.slotKey);
    _view =
        widget.initialView ??
        nextActionFor(doc: doc, seen: _seen).view ??
        WorkspaceView.read;
    widget.trace.markView(doc.slotKey, _view);
  }

  void _switch(WorkspaceView v, {String? tutorAnchor, String? readAnchor}) {
    setState(() {
      _view = v;
      if (v == WorkspaceView.tutor) _tutorAnchor = tutorAnchor;
      if (v == WorkspaceView.read) _readAnchor = readAnchor;
    });
    widget.trace.markView(doc.slotKey, v);
  }

  @override
  Widget build(BuildContext context) {
    final next = nextActionFor(doc: doc, seen: _seen);
    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: Column(
          children: [
            _header(context),
            if (doc.isFixture)
              Padding(
                padding: const EdgeInsets.fromLTRB(
                  WalSpacing.md,
                  0,
                  WalSpacing.md,
                  WalSpacing.sm,
                ),
                child: FixtureChip(trust: doc.trust),
              ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: WalSpacing.md),
              child: _segmented(),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(
                WalSpacing.md,
                WalSpacing.sm,
                WalSpacing.md,
                0,
              ),
              child: _nextActionCard(next),
            ),
            Expanded(child: _body()),
          ],
        ),
      ),
    );
  }

  Widget _header(BuildContext context) => Padding(
    padding: const EdgeInsets.fromLTRB(
      WalSpacing.xs,
      WalSpacing.xs,
      WalSpacing.md,
      WalSpacing.xs,
    ),
    child: Row(
      children: [
        SizedBox(
          width: WalSpacing.minTouch,
          height: WalSpacing.minTouch,
          child: IconButton(
            tooltip: 'Về mục lục',
            icon: const Icon(Icons.arrow_back, color: WalColors.ink),
            onPressed: () => Navigator.of(context).maybePop(),
          ),
        ),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                doc.lessonLabel,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  fontSize: WalType.title,
                  fontWeight: FontWeight.w700,
                  color: WalColors.ink,
                  height: 1.2,
                ),
              ),
              Text(
                doc.chapter == null
                    ? doc.pageRangeLine
                    : '${doc.chapter!.label} · ${doc.pageRangeLine}',
                style: const TextStyle(
                  fontSize: WalType.secondary,
                  color: WalColors.inkSoft,
                ),
              ),
            ],
          ),
        ),
      ],
    ),
  );

  Widget _segmented() => Container(
    padding: const EdgeInsets.all(4),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
    ),
    child: Row(
      children: [
        for (final v in WorkspaceView.values)
          Expanded(
            child: Semantics(
              button: true,
              selected: _view == v,
              label: v.label,
              child: SizedBox(
                height: WalSpacing.minTouch + 4,
                child: TextButton(
                  key: LessonWorkspaceScreen.tabKey(v),
                  onPressed: () => _switch(v),
                  style: TextButton.styleFrom(
                    backgroundColor: _view == v
                        ? WalColors.primary500
                        : Colors.transparent,
                    foregroundColor: _view == v ? Colors.white : WalColors.ink,
                    padding: const EdgeInsets.symmetric(horizontal: 4),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(
                        WalSpacing.radiusChip,
                      ),
                    ),
                  ),
                  child: FittedBox(
                    fit: BoxFit.scaleDown,
                    child: Text(
                      '${v.icon} ${v.label}',
                      style: const TextStyle(
                        fontSize: WalType.secondary,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
      ],
    ),
  );

  Widget _nextActionCard(NextAction next) => Container(
    key: LessonWorkspaceScreen.nextActionKey,
    padding: const EdgeInsets.all(WalSpacing.sm),
    decoration: BoxDecoration(
      color: WalColors.surfaceLavender,
      borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
    ),
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Image.asset(
          'assets/mascot/sam-probe@64.png',
          width: densityOf(context).mascotChip * 0.7,
          height: densityOf(context).mascotChip * 0.7,
          errorBuilder: (_, _, _) => const SizedBox.shrink(),
        ),
        const SizedBox(width: WalSpacing.sm),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'SAM đề xuất',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                  color: WalColors.primaryText,
                ),
              ),
              Text(
                next.reason,
                style: const TextStyle(
                  fontSize: 13,
                  color: WalColors.ink,
                  height: 1.35,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(width: WalSpacing.xs),
        SizedBox(
          height: WalSpacing.minTouch,
          child: FilledButton(
            style: FilledButton.styleFrom(
              backgroundColor: WalColors.primary500,
              padding: const EdgeInsets.symmetric(horizontal: WalSpacing.sm),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
              ),
            ),
            onPressed: () {
              final v = next.view;
              if (v == null) {
                Navigator.of(context).maybePop();
              } else {
                _switch(v);
              }
            },
            child: Text(
              next.label,
              style: const TextStyle(
                fontSize: WalType.secondary,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ),
      ],
    ),
  );

  Widget _body() => switch (_view) {
    WorkspaceView.read => SmartBookView(
      doc: doc,
      fontStep: _fontStep,
      onFontStep: (s) => setState(() => _fontStep = s),
      onAskSam: (b) => _switch(WorkspaceView.tutor, tutorAnchor: b.id),
      scrollToBlockId: _readAnchor,
    ),
    WorkspaceView.visual => VisualView(
      doc: doc,
      onShowInRead: (id) => _switch(WorkspaceView.read, readAnchor: id),
    ),
    WorkspaceView.tutor => TutorView(
      doc: doc,
      anchorBlockId: _tutorAnchor,
      onShowInRead: (id) => _switch(WorkspaceView.read, readAnchor: id),
      onNext: (target, anchor) => switch (target) {
        NextTarget.read => _switch(WorkspaceView.read, readAnchor: anchor),
        NextTarget.visual => _switch(WorkspaceView.visual),
        NextTarget.chapter ||
        NextTarget.done => Navigator.of(context).maybePop(),
      },
    ),
  };
}
