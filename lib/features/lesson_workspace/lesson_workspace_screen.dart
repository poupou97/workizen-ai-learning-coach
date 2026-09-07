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
///    View, một dòng «💡 SAM gợi ý: …» giữ ĐÍCH ĐẾN, chạm ⇒ lý do tại chỗ.
/// 6. LÀM GÌ TIẾP: nút trong gợi ý đã mở / thẻ kết của Tutor.
/// Chip thử nghiệm gọn một dòng, chạm ⇒ sheet «Nguồn & độ tin».
///
/// ROUND 6 · WS-D — **PHƯƠNG ÁN B ĐÃ ĐƯỢC FOUNDER CHỌN, ĐÃ THI HÀNH.**
/// Vòng 5 dựng bốn cách trình bày cùng một `NextAction` từ một commit và đo
/// trên Nokia 6.1: nội dung bài đầu tiên ở «Học với SAM» 820 px (card) →
/// 712 px (B đang hé) → 634 px (B đã thu gọn); nhãn View 7 → 4. Vòng 6 gỡ cờ
/// `--dart-define=WAL_ASSIST`, xoá ba phương án còn lại, và xoá luôn ba thứ
/// bản đồ trùng lặp gọi tên: **CTA đổi View trên thẻ đề xuất** (lặp đúng cái
/// tab ngay phía trên), **chân dung SAM ở chỗ SAM không nói**, và **hàng
/// «Đã mở ● ○ ○» thường trực** (nay nằm trong trạng thái EXPANDED).
///
/// ⚠ Gợi ý vẫn là TRÌNH BÀY của Next Action — không có động cơ đề xuất thứ
/// hai. `_proposal()` là nguồn duy nhất; `assist_layer` không đọc bài,
/// không đọc trace (có test soi mã).
///
/// Màn này KHÔNG nhận `LearnerStore` — theo cấu trúc, không ghi được gì.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/agenda/lesson_next_action.dart';
import '../../core/display/lesson_title.dart';
import '../../core/lesson_model/lesson_document.dart';
import '../../core/lesson_model/next_action.dart';
import '../../core/lesson_model/tutor_script.dart';
import 'smart_book_view.dart';
import 'tutor_view.dart';
import 'visual_view.dart';
import 'widgets/assist_layer.dart';
import 'widgets/fixture_chip.dart';
import 'widgets/mode_picker.dart';
import 'widgets/trust_sheet.dart';
import 'workspace_trace.dart';
import 'widgets/runtime_plan.dart';

class LessonWorkspaceScreen extends StatefulWidget {
  const LessonWorkspaceScreen({
    super.key,
    required this.doc,
    required this.trace,
    this.initialView,
    this.breadcrumb,
    this.learnerId,
  });

  final LessonDocument doc;
  final WorkspaceTrace trace;

  /// `null` ⇒ lần đầu trong phiên: màn «Vào bài học» (chọn cách học); đã
  /// mở rồi ⇒ vào thẳng View SAM đề xuất (tất định từ dữ liệu bài).
  final WorkspaceView? initialView;

  /// Đường đã đi tới đây («Giá sách › KHTN 6 › Chương IV»). `null` ⇒ dựng từ
  /// chính tài liệu (sách + chương).
  final List<String>? breadcrumb;

  /// Học sinh đang mở — chỉ để runtime giải `LearningContext`; workspace vẫn
  /// không có kho, không phát sự kiện. `null` ⇒ hằng `noLearnerId`.
  final String? learnerId;

  static Key tabKey(WorkspaceView v) => Key('workspace-tab-${v.name}');
  static const breadcrumbKey = Key('workspace-breadcrumb');

  @override
  State<LessonWorkspaceScreen> createState() => _LessonWorkspaceScreenState();
}

class _LessonWorkspaceScreenState extends State<LessonWorkspaceScreen> {
  /// `null` = đang ở màn «Vào bài học».
  WorkspaceView? _view;
  String? _tutorAnchor;
  String? _readAnchor;

  /// ROUND 7 · V2 — sơ đồ mà Trực quan phải dừng đúng ở đó, khi trẻ chạm một
  /// liên hệ trong lời phản hồi của SAM.
  String? _visualAnchor;
  int _fontStep = 0;

  /// PHƯƠNG ÁN B — trạng thái của lớp trợ giúp. Ở ĐÂY, không ở widget con, vì
  /// «đề xuất mới» là việc của màn: khi View được đề xuất ĐỔI, gợi ý hé lại
  /// một lần. Mặc định PEEK: trẻ biết ĐÍCH ĐẾN mà không phải chạm gì.
  AssistState _assist = AssistState.peek;
  WorkspaceView? _assistFor;

  /// Đề xuất đổi sang View KHÁC ⇒ hé lại (không nhắc lại cùng một điều).
  void _syncAssist(LessonNextAction next) {
    if (_assistFor == next.view) return;
    _assistFor = next.view;
    _assist = AssistState.peek;
  }

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
      _view = _proposal().view ?? WorkspaceView.read;
    } else {
      _view = null; // lần đầu ⇒ chọn cách học
    }
    final v = _view;
    if (v != null) widget.trace.markView(doc.slotKey, v);
  }

  void _switch(
    WorkspaceView v, {
    String? tutorAnchor,
    String? readAnchor,
    String? visualAnchor,
  }) {
    setState(() {
      _view = v;
      if (v == WorkspaceView.tutor) _tutorAnchor = tutorAnchor;
      if (v == WorkspaceView.read) _readAnchor = readAnchor;
      if (v == WorkspaceView.visual) _visualAnchor = visualAnchor;
    });
    widget.trace.markView(doc.slotKey, v);
  }

  /// «SAM đề xuất» theo thứ tự Founder A8 (Đọc → Trực quan → Học với SAM),
  /// từ `NextBestLearningAction` (Lane A-runtime, PR #69) — luật prototype
  /// «có sơ đồ ⇒ Trực quan trước» của `nextActionFor` không còn dùng ở UI.
  /// Xung đột thứ tự này được TRẢ VỀ Founder trong PR, không tự quyết ở đây.
  LessonNextAction _proposal() =>
      founderNextAction(doc, seen: _seen, learnerId: widget.learnerId);

  List<String> get _crumbs =>
      widget.breadcrumb ??
      ['Giá sách', doc.bookTitle, if (doc.chapter != null) doc.chapter!.label];

  @override
  Widget build(BuildContext context) {
    final next = _proposal();
    // Nokia xoay ngang (n2 D3): khung cố định (tiêu đề + chip + tab + đề
    // xuất) chiếm ~2/3 chiều cao, thân View còn ~225 px. Chế độ GỌN khi màn
    // ngang: tiêu đề 1 dòng, lý do đề xuất 1 dòng, bỏ mascot nhỏ — không bỏ
    // phần tử nào bắt buộc (chip, ba tab, đề xuất vẫn còn).
    final landscape =
        MediaQuery.orientationOf(context) == Orientation.landscape;
    final picking = _view == null;
    // ROUND 6: MỘT cách trình bày duy nhất (phương án B, Founder chọn). Không
    // có động cơ đề xuất thứ hai: `next` vẫn là `_proposal()` duy nhất.
    _syncAssist(next);
    final keyboardUp = MediaQuery.viewInsetsOf(context).bottom != 0;
    final showAssist = !picking && !keyboardUp;
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
            // PHƯƠNG ÁN B — một dòng hé dưới tab, mở TẠI CHỖ khi trẻ chạm.
            // Trạng thái COLLAPSED không vẽ dòng này: dấu hiệu 💡 chuyển lên
            // hàng tiêu đề (`_headerAssist`) — thấy được, không tốn dòng nào.
            if (showAssist && _assist != AssistState.collapsed)
              Padding(
                padding: const EdgeInsets.fromLTRB(
                  WalSpacing.md,
                  WalSpacing.sm,
                  WalSpacing.md,
                  0,
                ),
                child: AssistPeek(
                  action: next,
                  state: _assist,
                  onToggle: () => setState(
                    () => _assist = _assist == AssistState.expanded
                        ? AssistState.peek
                        : AssistState.expanded,
                  ),
                  onGo: () {
                    final v = next.view;
                    if (v == null) {
                      Navigator.of(context).maybePop();
                    } else {
                      _switch(v);
                    }
                  },
                  onDismiss: () =>
                      setState(() => _assist = AssistState.collapsed),
                  // Dấu vết phiên, đã dựng thành CHUỖI ở đây — lớp trợ giúp
                  // không được tự hỏi trace (có test soi mã). Chỉ hiện khi
                  // trẻ đã chủ động mở «vì sao»: vòng 4/5 ghim nó thường
                  // trực và bản đồ trùng lặp §2 mục 11 xếp nó vào nhóm «gộp
                  // được vào lớp trợ giúp».
                  seenLine: _assist == AssistState.expanded ? _seenLine : null,
                ),
              ),
            // Bàn phím lên (trẻ đang gõ trả lời SAM) ⇒ tạm ẩn gợi ý để thân
            // View còn chỗ (Nokia n3 D8). Bàn phím xuống ⇒ gợi ý trở lại.
            // Ở màn «Vào bài học» lý do nằm trên thẻ được đề xuất ⇒ không lặp.
            //
            // ROUND 6: thẻ «SAM đề xuất» thường trực ĐÃ BỊ XOÁ ở cả ba View —
            // đó chính là quyết định B. Vòng 4 §6.3 và vòng 5 D1 đã phải đẩy
            // nó vào vùng cuộn của Đọc rồi Trực quan để trang sách và nút
            // trung tâm của sơ đồ không bị che; B bỏ hẳn nhu cầu ấy.
            Expanded(
              // ⭐ MÉP TRÊN CỦA VÙNG CUỘN LÀ MỘT NHÁT CẮT CỨNG.
              //
              // Thấy trên Nokia khi cuộn giữa bài: dòng chữ ở mép bị xén NGANG
              // THÂN CHỮ, sát ngay khối gợi ý, không có ranh giới nào. Trẻ đọc
              // ra như chữ bị lỗi chứ không phải chữ đang trượt lên.
              //
              // Dải mờ ngắn cho chữ CHÌM xuống dưới phần tiêu đề. Dùng lớp phủ
              // gradient thay vì ShaderMask: máy cũ không phải hợp thành lại
              // cả vùng cuộn mỗi khung hình.
              child: Stack(
                children: [
                  Positioned.fill(
                    child: picking
                        ? ModePicker(doc: doc, proposal: next, onPick: _switch)
                        : _body(_view!),
                  ),
                  Positioned(
                    top: 0,
                    left: 0,
                    right: 0,
                    height: WalSpacing.md,
                    child: IgnorePointer(
                      child: DecoratedBox(
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            begin: Alignment.topCenter,
                            end: Alignment.bottomCenter,
                            colors: [
                              WalColors.surface,
                              WalColors.surface.withValues(alpha: 0),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// COLLAPSED — 💡 trong hàng tiêu đề: không tốn dòng nào, nhưng phải mang
  /// nhãn trợ năng đầy đủ (biểu tượng một mình không đủ cho trình đọc màn
  /// hình).
  ///
  /// ROUND 5 D5 (lỗi máy thật tìm ra): sau «Để sau» gợi ý KHÔNG được biến mất
  /// — «hé dần, không phải giấu đi». Đây là chỗ nó đi về. Chạm ⇒ mở thẳng
  /// EXPANDED tại chỗ (trẻ chạm 💡 là đang hỏi «vì sao»), không mở sheet:
  /// bottom sheet là phương án A và A đã bị loại.
  Widget? _headerAssist() {
    if (_assist != AssistState.collapsed) return null;
    if (_view == null) return null;
    if (MediaQuery.viewInsetsOf(context).bottom != 0) return null;
    return AssistIconButton(
      action: _proposal(),
      // Thu gọn rồi thì không còn «chưa xem» — chấm báo tắt cho đến khi đề
      // xuất trỏ sang View khác (`_syncAssist` đưa về PEEK).
      unseen: false,
      onOpen: () => setState(() => _assist = AssistState.expanded),
    );
  }

  /// «Đã mở: ● Đọc ○ Trực quan ○ Học với SAM» — dấu vết PHIÊN, không phải
  /// bằng chứng học. MỞ ≠ HIỂU. Dựng ở đây vì lớp trợ giúp không được đọc
  /// trace.
  ///
  /// ⭐ ROUND 7 · WS-R — hàng này từng duyệt `WorkspaceView.values` VÔ ĐIỀU
  /// KIỆN, nên nó vẽ «○ Trực quan ○ Học với SAM» cho cả bài KHÔNG CÓ hai thứ
  /// đó. Trên LS&ĐL 5 Bài 8 (Nokia 6.1) nó nằm ngay dưới câu SAM nói trẻ đã
  /// đi qua mọi cách học của bài — hai câu ngược nhau trên một màn, và «○»
  /// mời trẻ đi tìm thứ không tồn tại. Màn «Vào bài học» đã nói thật từ vòng
  /// 3 («Chưa có sơ đồ cho bài này»); hàng này thì chưa. Nay nó chỉ chấm
  /// ●/○ cho những cách học bài NÀY có, và NÊU TÊN những cách không có.
  String get _seenLine {
    final have = availableViewsOf(doc);
    final missing = [
      for (final v in WorkspaceView.values)
        if (!have.contains(v)) v.label,
    ];
    final marks = [
      'Đã mở:',
      for (final v in have) '${_seen.contains(v) ? '●' : '○'} ${v.label}',
    ].join(' ');
    if (missing.isEmpty) return marks;
    return '$marks · Bài này chưa có ${missing.join(', ')}';
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
                displayLessonLabel(doc.lessonNo, doc.title),
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
        ?_headerAssist(),
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
                    // MỘT BỘ CHỮ DUY NHẤT cho ba View: nhãn tab và nhãn thẻ ở
                    // màn «Vào bài học» đều lấy từ `WorkspaceView.label`.
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
      scrollToSemanticId: _visualAnchor,
    ),
    WorkspaceView.tutor => TutorView(
      doc: doc,
      learnerId: widget.learnerId,
      anchorBlockId: _tutorAnchor,
      // TRACE != EVIDENCE: SAM chi duoc noi «con da MO», khong bao gio «con da hieu».
      viewsSeen: _seen,
      onShowInRead: (id) => _switch(WorkspaceView.read, readAnchor: id),
      onOpenVisual: (semanticId) =>
          _switch(WorkspaceView.visual, visualAnchor: semanticId),
      onNext: (target, anchor) => switch (target) {
        NextTarget.read => _switch(WorkspaceView.read, readAnchor: anchor),
        NextTarget.visual => _switch(WorkspaceView.visual),
        NextTarget.chapter ||
        NextTarget.done => Navigator.of(context).maybePop(),
      },
    ),
  };
}
