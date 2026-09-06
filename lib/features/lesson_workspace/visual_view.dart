/// TRACK B — MODE 2 «Trực quan»: renderer trên `SemanticData` CÓ KIỂU.
///
/// Không có đường «bài → LLM → hình». Nút/hàng chạm được ⇒ mở đúng block
/// nguồn; «Xem trong Đọc» nhảy về Mode 1 tại block đó.
///
/// ROUND 3 B3 — HỌ RENDERER THEO KIỂU (concept khung 5 «Trực quan hoá»).
/// ROUND 5 B — sơ đồ THẬT thay danh sách chữ:
/// - `ProcessStep[]` → `ProcessFlowView`: nút trên MỘT TRỤC liên tục + mũi
///   tên + dải tổng quan chạm được; bước withheld là nút rỗng chỉ trang.
/// - `ComparisonSemantic` / `ConceptRelation[]` → `MindmapView`.
/// - MÀU CHỈ PHÂN BIỆT NHÁNH/BƯỚC; KHÔNG emoji theo nghĩa.
///
/// ⭐⭐ ROUND 7 · V1 — HAI LỖI TRÌNH BÀY ĐƯỢC ĐO TRÊN MÁY THẬT, ĐÃ SỬA:
///
/// **1. Ba hàng điều hướng cho một màn.** Founder order 48: «Giữ MỘT
/// navigation chính. Không lặp lại navigation bằng nhiều card.» Máy thật
/// (`round5-1-07-visual-mindmap.png`) đếm được BA: tab của workspace, hàng
/// chip HÌNH DẠNG («Sơ đồ quy trình · Bảng so sánh · Bảng tóm tắt» — tự
/// xuống hai dòng trên Nokia), rồi hàng chip CÁCH NHÌN («Sơ đồ tư duy ·
/// Bảng»). Ba hàng ấy đẩy nội dung học đầu tiên xuống **83 % chiều cao màn**:
/// trẻ mở «Trực quan» và thấy… nút bấm.
///
/// Vòng 7 xoá cả hai hàng chip. **Bài có bao nhiêu sơ đồ thì cuộn bấy nhiêu
/// sơ đồ, theo thứ tự tài liệu** — không phải chọn rồi mới thấy. «Cách nhìn»
/// của bảng so sánh (sơ đồ tư duy / bảng) đi vào ĐẦU THẺ của chính nó: nó là
/// một lựa chọn TRONG một sơ đồ, không phải điều hướng của màn. «Bảng tóm
/// tắt» thành nếp gấp cuối màn — nó là bản dự phòng khi không có sơ đồ, nên
/// khi CÓ sơ đồ nó không được đứng ngang hàng.
///
/// **2. «Vì sao SAM chọn sơ đồ này» chiếm một thẻ lavender to.** Nó đúng và
/// phải giữ, nhưng nó là lời giải thích về CÔNG CỤ, không phải nội dung học.
/// Nay là một dòng «ⓘ Vì sao SAM vẽ thế này?» cuối mỗi sơ đồ, mở sheet.
///
/// **3. Chạm một ô thì được GIẢI THÍCH.** Founder order 49 §3: «Chạm "Lọc" →
/// thấy: dùng khi nào · tách cái gì · liên hệ với nội dung bài.» Vòng 5 chạm
/// ra sheet nguồn — đúng câu trẻ vừa đọc trong ô. Vòng 7 chèn `VisualExplain`
/// (hàm THUẦN trên dữ liệu có kiểu, `views/visual_explain.dart`) lên trên
/// phần nguồn của cùng sheet ấy: nút này là gì trong sơ đồ, sách nói gì ở
/// từng chiều, và CHỖ KHÁC TRONG BÀI có nhắc đúng từ này — chạm là nhảy tới
/// sơ đồ đó. Không có sơ đồ nào khác nhắc tới ⇒ nói thẳng ra, không gợi bừa.
///
/// Mã luật sinh (`derivation`) vẫn nằm trong sheet «Nguồn & độ tin».
library;

import 'package:flutter/material.dart';

import '../../app/theme/band_density_scope.dart';
import '../../app/theme/wal_tokens.dart';
import '../../core/display/lesson_title.dart';
import '../../core/lesson_model/lesson_document.dart';
import '../../core/lesson_model/semantic_data.dart';
import 'views/mindmap_view.dart';
import 'views/process_flow_view.dart';
import 'views/timeline_view.dart';
import 'views/visual_explain.dart';
import 'views/visual_explain_card.dart';
import 'widgets/source_sheet.dart';
import 'widgets/trust_sheet.dart';

class VisualView extends StatefulWidget {
  const VisualView({
    super.key,
    required this.doc,
    required this.onShowInRead,
    this.header,
    this.scrollToSemanticId,
  });

  final LessonDocument doc;
  final void Function(String blockId) onShowInRead;

  /// ROUND 7 · V2 — vào Trực quan và DỪNG ĐÚNG ở một sơ đồ. Lời phản hồi của
  /// SAM («bài này dùng cách ấy ở đây») chỉ giữ được lời hứa nếu cú chạm rơi
  /// vào đúng thẻ, không phải vào đầu màn.
  final String? scrollToSemanticId;

  /// ROUND 5 D1 — thẻ «SAM đề xuất» đi vào ĐẦU VÙNG CUỘN thay vì bị ghim trên
  /// đầu màn: lý do dài 6 dòng ghim lại thì che mất nút trung tâm của sơ đồ.
  final Widget? header;

  static const summaryShape = '📋 Bảng tóm tắt';

  /// Nếp gấp «Bảng tóm tắt» cuối màn (ROUND 7 — không còn là một chip
  /// ngang hàng với sơ đồ).
  static const summaryFoldKey = Key('visual-summary-fold');

  /// Thẻ của MỘT sơ đồ trong màn cuộn (ROUND 7 — thay hàng chip hình dạng).
  static Key cardKey(String semanticId) => Key('visual-card-$semanticId');
  static Key whyKey(String semanticId) => Key('visual-why-$semanticId');

  /// ROUND 5 — nút chuyển cách nhìn của bảng so sánh («mindmap» / «table»),
  /// nay nằm TRONG thẻ của chính bảng so sánh đó.
  static Key comparisonViewKey(String v) => Key('visual-comparison-view-$v');
  static const comparisonLegendKey = Key('visual-comparison-legend');

  /// Sơ đồ tư duy chỉ đọc được khi mỗi nút mang tối đa 2 dòng chữ; nhiều
  /// chiều hơn ⇒ CHỈ bảng (fail closed, không nhồi chữ vào nút).
  static bool mindmapFits(ComparisonSemantic s) => s.dimensions.length <= 2;

  /// Mục tiêu + các dòng sau «Em đã học» tới nhãn/tiêu đề kế — NGUYÊN VĂN.
  static List<LessonBlock> summaryBlocks(LessonDocument doc) {
    final out = <LessonBlock>[
      for (final b in doc.blocks)
        if (b is ActivityBlock && b.kind == ActivityKind.objective) b,
    ];
    var inSummary = false;
    for (final b in doc.blocks) {
      if (b is ActivityBlock && b.kind == ActivityKind.stageLabel) {
        inSummary = b.text.trim().toLowerCase().startsWith('em đã học');
        continue;
      }
      if (!inSummary) continue;
      if (b is HeadingBlock || b is SourceRefBlock) break;
      if (LessonDocument.textOf(b) != null) out.add(b);
    }
    return out;
  }

  /// Hình dạng có trong bài, theo thứ tự xuất hiện.
  static List<String> shapesOf(LessonDocument doc) {
    final out = <String>[];
    for (final s in doc.semantic) {
      if (!out.contains(s.shapeLabel)) out.add(s.shapeLabel);
    }
    return out;
  }

  static String icon(SemanticData s) => switch (s) {
    ProcessSemantic() => '🔁',
    ComparisonSemantic() => '⚖️',
    ConceptMapSemantic() => '🕸️',
    TimelineSemantic() => '🕰️',
  };

  /// Nút trung tâm của sơ đồ khái niệm: thực thể xuất hiện nhiều nhất (hoà ⇒
  /// thực thể gặp trước) — tất định, kiểm lại được.
  static String hubOf(ConceptMapSemantic s) {
    final count = <String, int>{};
    final order = <String>[];
    for (final r in s.relations) {
      for (final e in [r.a, r.b]) {
        if (!count.containsKey(e)) order.add(e);
        count[e] = (count[e] ?? 0) + 1;
      }
    }
    var best = order.first;
    for (final e in order) {
      if (count[e]! > count[best]!) best = e;
    }
    return best;
  }

  @override
  State<VisualView> createState() => _VisualViewState();
}

class _VisualViewState extends State<VisualView> {
  /// ROUND 5 — bảng so sánh có HAI cách nhìn: sơ đồ tư duy (mặc định) và
  /// bảng. Cùng một dữ liệu có kiểu, không thêm sự thật nào. Trạng thái theo
  /// TỪNG sơ đồ vì màn nay hiện nhiều sơ đồ một lúc.
  final Set<String> _asTable = {};

  /// Neo cuộn tới một sơ đồ khi trẻ chạm «Bài này dùng ở đâu».
  final Map<String, GlobalKey> _anchors = {};

  bool _summaryOpen = false;

  GlobalKey _anchorFor(String id) => _anchors.putIfAbsent(id, GlobalKey.new);

  @override
  void initState() {
    super.initState();
    _jumpAfterFrame();
  }

  @override
  void didUpdateWidget(VisualView old) {
    super.didUpdateWidget(old);
    if (old.scrollToSemanticId != widget.scrollToSemanticId) _jumpAfterFrame();
  }

  /// Neo chỉ tồn tại sau khi thẻ được dựng ⇒ cuộn ở khung hình sau.
  void _jumpAfterFrame() {
    final id = widget.scrollToSemanticId;
    if (id == null) return;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) _scrollTo(id);
    });
  }

  @override
  Widget build(BuildContext context) {
    final doc = widget.doc;
    final diagrams = doc.semantic;
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(
        WalSpacing.md,
        WalSpacing.sm,
        WalSpacing.md,
        WalSpacing.xl,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (widget.header != null) ...[
            widget.header!,
            const SizedBox(height: WalSpacing.sm),
          ],
          if (diagrams.isEmpty)
            _noDiagrams()
          else
            for (var i = 0; i < diagrams.length; i++) ...[
              if (i > 0) const SizedBox(height: WalSpacing.md),
              _diagramCard(diagrams[i]),
            ],
          const SizedBox(height: WalSpacing.md),
          _summaryFold(doc, forceOpen: diagrams.isEmpty),
        ],
      ),
    );
  }

  // ── Không có sơ đồ ⇒ nói VÌ SAO (fail closed, ROUND 4 §6.5) ──
  Widget _noDiagrams() => Row(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Image.asset(
        'assets/mascot/sam-admit-uncertainty.png',
        width: densityOf(context).mascotChip,
        height: densityOf(context).mascotChip,
        errorBuilder: (_, _, _) => const SizedBox.shrink(),
      ),
      const SizedBox(width: WalSpacing.sm),
      const Expanded(
        child: Text(
          'SAM chưa có sơ đồ cho bài này. SAM chỉ vẽ sơ đồ khi sách '
          'viết rõ từng bước hoặc từng cách; bài này chưa có phần như '
          'vậy nên SAM không tự vẽ — con xem bảng tóm tắt, đọc sách '
          'hoặc học cùng SAM nhé.',
          style: TextStyle(fontSize: WalType.body, color: WalColors.ink),
        ),
      ),
    ],
  );

  // ── MỘT sơ đồ = MỘT thẻ ──────────────────────────────────────────────────

  Widget _diagramCard(SemanticData s) {
    final asTable = _asTable.contains(s.id);
    final comparisonAsMindmap =
        s is ComparisonSemantic && !asTable && VisualView.mindmapFits(s);
    return Container(
      key: _anchorFor(s.id),
      padding: const EdgeInsets.fromLTRB(
        WalSpacing.sm,
        WalSpacing.md,
        WalSpacing.sm,
        WalSpacing.sm,
      ),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
      ),
      child: Column(
        key: VisualView.cardKey(s.id),
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: WalSpacing.sm),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  '${VisualView.icon(s)} ${s.shapeLabel}',
                  style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                    letterSpacing: .6,
                    color: WalColors.inkSoft,
                  ),
                ),
                // Sơ đồ tư duy của bảng so sánh LẤY CHÍNH tiêu đề làm nút
                // trung tâm ⇒ không in lại tiêu đề bên trên.
                if (!comparisonAsMindmap) ...[
                  const SizedBox(height: 2),
                  Text(
                    displayTitle(s.title),
                    style: const TextStyle(
                      fontSize: WalType.body + 2,
                      fontWeight: FontWeight.w700,
                      color: WalColors.ink,
                      height: 1.25,
                    ),
                  ),
                ],
                const SizedBox(height: 2),
                Text(
                  _subtitle(s),
                  style: const TextStyle(
                    fontSize: 13,
                    color: WalColors.inkSoft,
                  ),
                ),
                const SizedBox(height: WalSpacing.sm),
              ],
            ),
          ),
          switch (s) {
            ProcessSemantic() => _process(s),
            ComparisonSemantic() => _comparison(s, asTable: asTable),
            ConceptMapSemantic() => _conceptMap(s),
            // Round 4 (Lane C, Golden Slice #2): renderer Lịch sử.
            TimelineSemantic() => TimelineView(
              doc: widget.doc,
              semantic: s,
              onOpenSource: _openSource,
            ),
          },
          _whyLine(s),
        ],
      ),
    );
  }

  /// Dòng phụ: kích thước + trang nguồn — đếm từ dữ liệu.
  String _subtitle(SemanticData s) {
    final n = switch (s) {
      ProcessSemantic(:final steps) => '${steps.length} bước',
      ComparisonSemantic(:final entities) => '${entities.length} cách',
      ConceptMapSemantic(:final relations) => '${relations.length} quan hệ',
      TimelineSemantic(:final events) => '${events.length} mốc',
    };
    final firstSrc = switch (s) {
      ProcessSemantic(:final steps) => steps.first.sourceBlockId,
      ComparisonSemantic(:final entities) => entities.first.sourceBlockId,
      ConceptMapSemantic(:final relations) => relations.first.sourceBlockId,
      TimelineSemantic(:final events) => events.first.sourceBlockId,
    };
    // Máy thật lượt 2: «3 bước · SGK KHTN 6 · trang 61 · chữ sách…» xuống hai
    // dòng, và «SGK KHTN 6» đã nằm ở hàng tiêu đề ngay trên. Bỏ vế lặp.
    return '$n · ${_pageOnly(firstSrc)} · chữ sách, SAM chỉ xếp lại';
  }

  /// «Vì sao SAM vẽ thế này» — MỘT DÒNG, mở sheet. Vòng 5/6 để nguyên văn
  /// này trong một thẻ lavender to ngay dưới mỗi sơ đồ; đúng nhưng nó là lời
  /// về CÔNG CỤ, không phải nội dung học, nên nó không được ăn chỗ của sơ đồ
  /// tiếp theo.
  Widget _whyLine(SemanticData s) => Align(
    alignment: Alignment.centerLeft,
    child: TextButton(
      key: VisualView.whyKey(s.id),
      style: TextButton.styleFrom(
        minimumSize: const Size(WalSpacing.minTouch, WalSpacing.minTouch),
        padding: const EdgeInsets.symmetric(horizontal: WalSpacing.sm),
      ),
      onPressed: () => _showWhy(s),
      child: const Text(
        'ⓘ Vì sao SAM vẽ thế này?',
        style: TextStyle(fontSize: 13, color: WalColors.primaryText),
      ),
    ),
  );

  /// Lời TẤT ĐỊNH theo luật sinh, không LLM.
  String _whyText(SemanticData s) => switch (s) {
    ProcessSemantic() =>
      'Sách viết hoạt động này thành các bước đánh dấu «·» theo thứ tự — SAM '
          'xếp đúng thứ tự sách, giữ nguyên lời sách, không thêm bước nào. Bước '
          'nào SAM chưa đọc chắc thì để trống và chỉ trang.',
    // ROUND 5 D2 (Nokia, iter 1): lời này phải nói ĐÚNG THỨ TRẺ ĐANG NHÌN —
    // mặc định giờ là sơ đồ tư duy, không phải bảng.
    ComparisonSemantic() when !_asTable.contains(s.id) =>
      'Phần «Em đã học» của sách liệt kê từng cách kèm chú thích trong '
          'ngoặc — SAM đặt tên chung vào giữa và mỗi cách một ô xung quanh, '
          'chữ trong ô vẫn là chữ sách. Màu chỉ để phân biệt các ô.',
    ComparisonSemantic() =>
      'Phần «Em đã học» của sách liệt kê từng cách kèm chú thích trong ngoặc — '
          'SAM xếp thành bảng để con so sánh, chữ vẫn là chữ sách.',
    ConceptMapSemantic() =>
      'Các quan hệ lấy từ dữ liệu có kiểu của bài — SAM đặt khái niệm gặp '
          'nhiều nhất vào giữa và nối các khái niệm sách nói tới, không thêm '
          'quan hệ nào.',
    TimelineSemantic() =>
      'Các mốc lấy từ dữ liệu có kiểu của bài, xếp theo thứ tự sách nêu — '
          'SAM không thêm mốc, không đoán năm.',
  };

  void _showWhy(SemanticData s) => showModalBottomSheet<void>(
    context: context,
    backgroundColor: WalColors.surface,
    showDragHandle: true,
    isScrollControlled: true,
    builder: (sheet) => SafeArea(
      child: SingleChildScrollView(
        key: const Key('visual-why-sheet'),
        child: Padding(
          padding: const EdgeInsets.fromLTRB(
            WalSpacing.lg,
            0,
            WalSpacing.lg,
            WalSpacing.lg,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Image.asset(
                    'assets/mascot/sam-explain.png',
                    width: densityOf(context).mascotChip,
                    height: densityOf(context).mascotChip,
                    errorBuilder: (_, _, _) => const SizedBox.shrink(),
                  ),
                  const SizedBox(width: WalSpacing.sm),
                  const Expanded(
                    child: Text(
                      'Vì sao SAM chọn sơ đồ này',
                      style: TextStyle(
                        fontSize: WalType.title,
                        fontWeight: FontWeight.w700,
                        color: WalColors.ink,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: WalSpacing.sm),
              Text(
                _whyText(s),
                style: const TextStyle(
                  fontSize: WalType.secondary,
                  color: WalColors.ink,
                  height: 1.45,
                ),
              ),
              const SizedBox(height: WalSpacing.sm),
              Align(
                alignment: Alignment.centerLeft,
                child: TextButton(
                  key: const Key('visual-trust-link'),
                  style: TextButton.styleFrom(
                    minimumSize: const Size(WalSpacing.minTouch, 44),
                    padding: EdgeInsets.zero,
                  ),
                  onPressed: () {
                    Navigator.of(sheet).pop();
                    showTrustSheet(context, doc: widget.doc);
                  },
                  child: const Text(
                    'ⓘ Nguồn & độ tin',
                    style: TextStyle(fontSize: 13, color: WalColors.primaryText),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    ),
  );

  // ── Chạm một nút ⇒ giải thích + nguồn (ROUND 7 · V1) ──────────────────────

  void _openSource(String blockId, {Widget? explain}) {
    final b = widget.doc.blockById(blockId);
    if (b == null) return;
    showSourceSheet(
      context,
      doc: widget.doc,
      block: b,
      explain: explain,
      onShowInRead: () => widget.onShowInRead(blockId),
    );
  }

  void _openExplain(VisualExplain e, String blockId) => _openSource(
    blockId,
    explain: VisualExplainCard(
      // Lời sách của nút TRÙNG lời sách của block nguồn ⇒ in một lần thôi.
      explain: _sameAsSource(e.verbatim, blockId) ? e.withoutVerbatim() : e,
      onOpenLink: (l) {
        Navigator.of(context).maybePop();
        _scrollTo(l.semanticId);
      },
    ),
  );

  /// Lời giải thích và block nguồn mang ĐÚNG một câu ⇒ không in hai lần.
  bool _sameAsSource(String? verbatim, String blockId) {
    if (verbatim == null) return false;
    final b = widget.doc.blockById(blockId);
    final text = b == null ? null : LessonDocument.textOf(b);
    return text != null && text.trim() == verbatim.trim();
  }

  /// Nhảy tới sơ đồ khác của CÙNG bài (từ «Bài này dùng ở đâu»).
  void _scrollTo(String semanticId) {
    final ctx = _anchors[semanticId]?.currentContext;
    if (ctx == null) return;
    Scrollable.ensureVisible(
      ctx,
      duration: const Duration(milliseconds: 260),
      alignment: 0.05,
    );
  }

  String _pageOf(String blockId) {
    final b = widget.doc.blockById(blockId);
    return b == null ? 'sách' : widget.doc.sourceLineForBlock(b);
  }

  /// Chỉ vế TRANG của dòng nguồn («SGK KHTN 6 · trang 61» → «trang 61») —
  /// tên sách đã ở hàng tiêu đề của màn, in lại là tốn một dòng đọc.
  String _pageOnly(String blockId) {
    final src = _pageOf(blockId);
    final i = src.indexOf(' · ');
    return i < 0 ? src : src.substring(i + 3);
  }

  // ── Process ──
  Widget _process(ProcessSemantic s) => ProcessFlowView(
    doc: widget.doc,
    semantic: s,
    onOpenSource: _openSource,
    onOpenStep: (step) =>
        _openExplain(explainForStep(s, step), step.sourceBlockId),
    onShowInRead: widget.onShowInRead,
    pageOf: _pageOf,
  );

  // ── Comparison: sơ đồ tư duy (mặc định) hoặc bảng ──

  Widget _comparison(ComparisonSemantic s, {required bool asTable}) {
    final fits = VisualView.mindmapFits(s);
    final table = asTable || !fits;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: WalSpacing.sm),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // «Cách nhìn» là lựa chọn TRONG sơ đồ này, nên nó ở trong thẻ
              // của sơ đồ — không phải một hàng điều hướng thứ ba của màn.
              if (fits) ...[
                // `Wrap`, không `Row`: hai nhãn tiếng Việt + emoji tràn 5 dp
                // trên màn 360 dp (đo bằng test mật độ) — tràn là chữ bị cắt.
                Wrap(
                  spacing: WalSpacing.xs,
                  runSpacing: WalSpacing.xs,
                  children: [
                    _viewChip(
                      key: VisualView.comparisonViewKey('mindmap'),
                      label: '🕸️ Sơ đồ tư duy',
                      selected: !table,
                      onTap: () => setState(() => _asTable.remove(s.id)),
                    ),
                    _viewChip(
                      key: VisualView.comparisonViewKey('table'),
                      label: '⚖️ Bảng',
                      selected: table,
                      onTap: () => setState(() => _asTable.add(s.id)),
                    ),
                  ],
                ),
                const SizedBox(height: WalSpacing.sm),
              ],
              Padding(
                padding: const EdgeInsets.only(bottom: WalSpacing.sm),
                child: Text(
                  table
                      ? 'Mỗi hàng là một cách sách nêu · chạm một hàng để SAM '
                            'giải thích'
                      : 'Mỗi ô là một cách sách nêu · màu chỉ để phân biệt, '
                            'không phải điểm số · chạm một ô để SAM giải thích',
                  key: VisualView.comparisonLegendKey,
                  style: const TextStyle(fontSize: 11, color: WalColors.inkSoft),
                ),
              ),
            ],
          ),
        ),
        if (table) _comparisonTable(s) else _comparisonMindmap(s),
      ],
    );
  }

  /// Thực thể → nút nhánh; mỗi chiều so sánh → một dòng chữ SÁCH trong nút.
  Widget _comparisonMindmap(ComparisonSemantic s) => MindmapView(
    hub: displayTitle(s.title),
    hubSourceBlockId: s.entities.first.sourceBlockId,
    onOpenSource: _openSource,
    onTapNode: (i, _) => _openExplain(
      explainForEntity(s, i, alsoIn: widget.doc.semantic),
      s.entities[i].sourceBlockId,
    ),
    nodes: [
      for (var i = 0; i < s.entities.length; i++)
        MindmapNode(
          label: s.entities[i].name,
          sourceBlockId: s.entities[i].sourceBlockId,
          lines: [
            for (final d in s.dimensions)
              MindmapLine(name: d.name, value: d.values[i]),
          ],
        ),
    ],
  );

  Widget _comparisonTable(ComparisonSemantic s) => Container(
    margin: const EdgeInsets.symmetric(horizontal: WalSpacing.xs),
    decoration: BoxDecoration(
      color: WalColors.surface,
      borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
    ),
    child: Table(
      columnWidths: const {0: IntrinsicColumnWidth()},
      border: TableBorder.symmetric(
        inside: BorderSide(color: WalColors.inkSoft.withValues(alpha: 0.2)),
      ),
      children: [
        TableRow(
          decoration: const BoxDecoration(color: WalColors.surfaceLavender),
          children: [
            _cell('Cách', bold: true),
            for (final d in s.dimensions) _cell(d.name, bold: true),
          ],
        ),
        for (var i = 0; i < s.entities.length; i++)
          TableRow(
            children: [
              InkWell(
                onTap: () => _tapEntity(s, i),
                child: _cell(
                  s.entities[i].name,
                  bold: true,
                  color: WalColors.primaryText,
                ),
              ),
              for (final d in s.dimensions)
                InkWell(
                  onTap: () => _tapEntity(s, i),
                  child: _cell(d.values[i] ?? '— (sách không nói)'),
                ),
            ],
          ),
      ],
    ),
  );

  void _tapEntity(ComparisonSemantic s, int i) => _openExplain(
    explainForEntity(s, i, alsoIn: widget.doc.semantic),
    s.entities[i].sourceBlockId,
  );

  Widget _cell(String t, {bool bold = false, Color color = WalColors.ink}) =>
      Padding(
        padding: const EdgeInsets.all(WalSpacing.md),
        child: Text(
          t,
          style: TextStyle(
            fontSize: WalType.secondary,
            fontWeight: bold ? FontWeight.w700 : FontWeight.w400,
            color: color,
            height: 1.35,
          ),
        ),
      );

  // ── Concept map: cùng sơ đồ tư duy với bảng so sánh (ROUND 5) ──
  Widget _conceptMap(ConceptMapSemantic s) {
    final hub = VisualView.hubOf(s);
    final spokes = <ConceptRelation>[];
    final rest = <ConceptRelation>[];
    for (final r in s.relations) {
      (r.a == hub || r.b == hub ? spokes : rest).add(r);
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Padding(
          padding: EdgeInsets.fromLTRB(
            WalSpacing.sm,
            0,
            WalSpacing.sm,
            WalSpacing.sm,
          ),
          child: Text(
            'Ô giữa là khái niệm sách nói tới nhiều nhất · màu chỉ để phân '
            'biệt nhánh · chạm một ô để SAM giải thích',
            key: Key('visual-concept-legend'),
            style: TextStyle(fontSize: 11, color: WalColors.inkSoft),
          ),
        ),
        MindmapView(
          key: const Key('visual-concept-map'),
          hub: hub,
          hubSourceBlockId: spokes.isNotEmpty
              ? spokes.first.sourceBlockId
              : s.relations.first.sourceBlockId,
          onOpenSource: _openSource,
          onTapNode: (i, _) => _openExplain(
            explainForRelation(s, spokes[i], hub, alsoIn: widget.doc.semantic),
            spokes[i].sourceBlockId,
          ),
          nodes: [
            for (final r in spokes)
              MindmapNode(
                label: r.a == hub ? r.b : r.a,
                edgeLabel: r.relation,
                sourceBlockId: r.sourceBlockId,
              ),
          ],
        ),
        if (rest.isNotEmpty) ...[
          const SizedBox(height: WalSpacing.sm),
          for (final r in rest)
            InkWell(
              onTap: () => _openSource(r.sourceBlockId),
              child: _card(
                Text(
                  '${r.a}  —${r.relation}→  ${r.b}',
                  style: const TextStyle(
                    fontSize: WalType.body,
                    color: WalColors.ink,
                  ),
                ),
              ),
            ),
        ],
      ],
    );
  }

  // ── Bảng tóm tắt: NẾP GẤP cuối màn (fallback) ──
  Widget _summaryFold(LessonDocument doc, {required bool forceOpen}) {
    final blocks = VisualView.summaryBlocks(doc);
    final open = forceOpen || _summaryOpen;
    return Container(
      key: VisualView.summaryFoldKey,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (!forceOpen)
            InkWell(
              key: const Key('visual-summary-toggle'),
              borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
              onTap: () => setState(() => _summaryOpen = !_summaryOpen),
              child: Padding(
                padding: const EdgeInsets.all(WalSpacing.md),
                child: Row(
                  children: [
                    const Expanded(
                      child: Text(
                        '${VisualView.summaryShape} — lời sách',
                        style: TextStyle(
                          fontSize: WalType.secondary,
                          fontWeight: FontWeight.w700,
                          color: WalColors.ink,
                        ),
                      ),
                    ),
                    Icon(
                      open ? Icons.expand_less : Icons.expand_more,
                      color: WalColors.inkSoft,
                    ),
                  ],
                ),
              ),
            )
          else
            const Padding(
              padding: EdgeInsets.fromLTRB(
                WalSpacing.md,
                WalSpacing.md,
                WalSpacing.md,
                0,
              ),
              child: Text(
                'Bảng tóm tắt — lời sách',
                style: TextStyle(
                  fontSize: WalType.title,
                  fontWeight: FontWeight.w700,
                  color: WalColors.ink,
                ),
              ),
            ),
          if (open)
            Padding(
              padding: const EdgeInsets.fromLTRB(
                WalSpacing.md,
                WalSpacing.sm,
                WalSpacing.md,
                WalSpacing.md,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  if (blocks.isEmpty)
                    const Text(
                      'Bài này chưa có phần tóm tắt SAM đọc được.',
                      style: TextStyle(
                        fontSize: WalType.body,
                        color: WalColors.inkSoft,
                      ),
                    )
                  else
                    for (final b in blocks)
                      Padding(
                        padding: const EdgeInsets.only(bottom: WalSpacing.sm),
                        child: SourceCard(
                          doc: doc,
                          block: b,
                          onTap: () => _openSource(b.id),
                        ),
                      ),
                ],
              ),
            ),
        ],
      ),
    );
  }

  Widget _card(Widget child) => Container(
    width: double.infinity,
    margin: const EdgeInsets.only(bottom: WalSpacing.sm),
    padding: const EdgeInsets.all(WalSpacing.md),
    decoration: BoxDecoration(
      color: WalColors.surface,
      borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
    ),
    child: child,
  );

  Widget _viewChip({
    required Key key,
    required String label,
    required bool selected,
    required VoidCallback onTap,
  }) => SizedBox(
    height: WalSpacing.minTouch - 8,
    child: ChoiceChip(
      key: key,
      label: Text(
        label,
        style: TextStyle(
          fontSize: 13,
          fontWeight: FontWeight.w600,
          color: selected ? Colors.white : WalColors.ink,
        ),
      ),
      selected: selected,
      selectedColor: WalColors.primaryText,
      backgroundColor: WalColors.surface,
      showCheckmark: false,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
      ),
      onSelected: (_) => onTap(),
    ),
  );
}
