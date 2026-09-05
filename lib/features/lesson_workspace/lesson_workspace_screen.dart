/// TRACK B — LESSON WORKSPACE: một bài, ba cách học, một bước tiếp.
///
/// Khung «duy nhất mới» của concept (16-UX-CONCEPT §3): tiêu đề «Bài N ·
/// tên», chip thử nghiệm (bắt buộc khi là fixture), segmented control
/// [📖 Đọc] [✨ Trực quan] [🦉 Học với SAM], thẻ «SAM đề xuất» có lý do tất
/// định, rồi thân View. Nhảy giữa View mang theo block (Đọc → SAM; Trực quan
/// → Đọc) — không hỏi lại gì.
///
/// ROUND 3 (B1 — Founder cầm máy phải thấy ngay 6 điều):
/// 1. Ở ĐÂU: dòng đường dẫn «Giá sách › KHTN 6 › Chương IV» trên tiêu đề.
/// 2. BÀI NÀO: «Bài 17 · Tách chất khỏi hỗn hợp» + «SGK KHTN 6 · trang 60–63».
/// 3. NHỮNG CÁCH NÀO: lần đầu mở ⇒ màn «Vào bài học» ba thẻ (concept khung 3),
///    mỗi thẻ nói bài này có gì theo cách đó; ba tab vẫn luôn ở trên.
/// 4./5. SAM ĐANG LÀM GÌ, VÌ SAO: thẻ được đề xuất mang lý do; sau khi vào
///    View, thẻ «SAM đề xuất» giữ lý do + một nút.
/// 6. LÀM GÌ TIẾP: nút trên thẻ đề xuất / thẻ kết của Tutor.
/// Chip thử nghiệm gọn một dòng, chạm ⇒ sheet «Nguồn & độ tin».
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
import 'widgets/mode_picker.dart';
import 'widgets/trust_sheet.dart';
import 'workspace_trace.dart';

class LessonWorkspaceScreen extends StatefulWidget {
  const LessonWorkspaceScreen({
    super.key,
    required this.doc,
    required this.trace,
    this.initialView,
    this.breadcrumb,
  });

  final LessonDocument doc;
  final WorkspaceTrace trace;

  /// `null` ⇒ lần đầu trong phiên: màn «Vào bài học» (chọn cách học); đã
  /// mở rồi ⇒ vào thẳng View SAM đề xuất (tất định từ dữ liệu bài).
  final WorkspaceView? initialView;

  /// Đường đã đi tới đây («Giá sách › KHTN 6 › Chương IV»). `null` ⇒ dựng từ
  /// chính tài liệu (sách + chương).
  final List<String>? breadcrumb;

  static Key tabKey(WorkspaceView v) => Key('workspace-tab-${v.name}');
  static const nextActionKey = Key('workspace-next-action');
  static const breadcrumbKey = Key('workspace-breadcrumb');

  @override
  State<LessonWorkspaceScreen> createState() => _LessonWorkspaceScreenState();
}

class _LessonWorkspaceScreenState extends State<LessonWorkspaceScreen> {
  /// `null` = đang ở màn «Vào bài học».
  WorkspaceView? _view;
  String? _tutorAnchor;
  String? _readAnchor;
  int _fontStep = 0;

  LessonDocument get doc => widget.doc;
  Set<WorkspaceView> get _seen => widget.trace.viewsFor(doc.slotKey);

  @override
  void initState() {
    super.initState();
    widget.trace.markOpened(doc.slotKey);
    final initial = widget.initialView;
    if (initial != null) {
      _view = initial;
    } else if (_seen.isNotEmpty) {
      _view = nextActionFor(doc: doc, seen: _seen).view ?? WorkspaceView.read;
    } else {
      _view = null; // lần đầu ⇒ chọn cách học
    }
    final v = _view;
    if (v != null) widget.trace.markView(doc.slotKey, v);
  }

  void _switch(WorkspaceView v, {String? tutorAnchor, String? readAnchor}) {
    setState(() {
      _view = v;
      if (v == WorkspaceView.tutor) _tutorAnchor = tutorAnchor;
      if (v == WorkspaceView.read) _readAnchor = readAnchor;
    });
    widget.trace.markView(doc.slotKey, v);
  }

  List<String> get _crumbs =>
      widget.breadcrumb ??
      [
        'Giá sách',
        doc.bookTitle,
        if (doc.chapter != null) doc.chapter!.label,
      ];

  @override
  Widget build(BuildContext context) {
    final next = nextActionFor(doc: doc, seen: _seen);
    // Nokia xoay ngang (n2 D3): khung cố định (tiêu đề + chip + tab + đề
    // xuất) chiếm ~2/3 chiều cao, thân View còn ~225 px. Chế độ GỌN khi màn
    // ngang: tiêu đề 1 dòng, lý do đề xuất 1 dòng, bỏ mascot nhỏ — không bỏ
    // phần tử nào bắt buộc (chip, ba tab, đề xuất vẫn còn).
    final landscape =
        MediaQuery.orientationOf(context) == Orientation.landscape;
    final picking = _view == null;
    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: Column(
          children: [
            _header(context, compact: landscape),
            if (doc.isFixture)
              Padding(
                padding: EdgeInsets.fromLTRB(
                  WalSpacing.md,
                  0,
                  WalSpacing.md,
                  landscape ? WalSpacing.xs : WalSpacing.sm,
                ),
                child: FixtureChip(
                  trust: doc.trust,
                  compact: true,
                  onTap: () => showTrustSheet(context, doc: doc),
                ),
              ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: WalSpacing.md),
              child: _segmented(),
            ),
            // Bàn phím lên (trẻ đang gõ trả lời SAM) ⇒ tạm ẩn thẻ đề xuất để
            // thân View còn chỗ (Nokia n3 D8). Bàn phím xuống ⇒ thẻ trở lại.
            // Ở màn «Vào bài học» lý do nằm trên thẻ được đề xuất ⇒ không lặp.
            if (!picking && MediaQuery.viewInsetsOf(context).bottom == 0)
              Padding(
                padding: const EdgeInsets.fromLTRB(
                  WalSpacing.md,
                  WalSpacing.sm,
                  WalSpacing.md,
                  0,
                ),
                child: _nextActionCard(next, compact: landscape),
              ),
            Expanded(
              child: picking
                  ? ModePicker(doc: doc, proposal: next, onPick: _switch)
                  : _body(_view!),
            ),
          ],
        ),
      ),
    );
  }

  Widget _header(BuildContext context, {bool compact = false}) => Padding(
    padding: const EdgeInsets.fromLTRB(
      WalSpacing.xs,
      WalSpacing.xs,
      WalSpacing.md,
      WalSpacing.xs,
    ),
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.start,
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
              // Một dòng 12sp — đủ rẻ để giữ cả khi màn ngang (câu 1 «ở đâu»).
              Padding(
                padding: EdgeInsets.only(top: compact ? 2 : 6),
                child: Text(
                  _crumbs.join(' › '),
                  key: LessonWorkspaceScreen.breadcrumbKey,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: WalColors.inkSoft,
                  ),
                ),
              ),
              Text(
                doc.lessonLabel,
                maxLines: compact ? 1 : 2,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  fontSize: compact ? WalType.body + 1 : WalType.title,
                  fontWeight: FontWeight.w700,
                  color: WalColors.ink,
                  height: 1.2,
                ),
              ),
              Text(
                doc.pageRangeLine,
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

  Widget _nextActionCard(NextAction next, {bool compact = false}) => Container(
    key: LessonWorkspaceScreen.nextActionKey,
    padding: EdgeInsets.all(compact ? WalSpacing.xs : WalSpacing.sm),
    decoration: BoxDecoration(
      color: WalColors.surfaceLavender,
      borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
    ),
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        if (!compact) ...[
          Image.asset(
            'assets/mascot/sam-probe@64.png',
            width: densityOf(context).mascotChip * 0.7,
            height: densityOf(context).mascotChip * 0.7,
            errorBuilder: (_, _, _) => const SizedBox.shrink(),
          ),
          const SizedBox(width: WalSpacing.sm),
        ],
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
                maxLines: compact ? 1 : 3,
                overflow: TextOverflow.ellipsis,
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

  Widget _body(WorkspaceView view) => switch (view) {
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
