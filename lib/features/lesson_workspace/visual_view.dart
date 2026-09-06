/// TRACK B — MODE 2 «Trực quan»: renderer trên `SemanticData` CÓ KIỂU.
///
/// Không có đường «bài → LLM → hình». Tab con chỉ hiện cho hình dạng bài này
/// CÓ (16-UX-CONCEPT §1 hàng 5); luôn có «Bảng tóm tắt» làm fallback (chữ
/// nguyên văn phần MỤC TIÊU / Em đã học). Nút/hàng chạm được ⇒ mở đúng block
/// nguồn; «Xem trong Đọc» nhảy về Mode 1 tại block đó.
///
/// ROUND 3 B3 — HỌ RENDERER THEO KIỂU (concept khung 5 «Trực quan hoá»):
/// - Tab theo HÌNH DẠNG (🔁 Sơ đồ quy trình · ⚖️ Bảng so sánh · 🕸️ Sơ đồ
///   khái niệm · 🕰️ Dòng thời gian · 📋 Bảng tóm tắt); hình dạng có nhiều sơ đồ
///   ⇒ hàng chọn thứ hai «1 · tên» «2 · tên» (Nokia n1 D2: hai tab y hệt).
/// - `TimelineEvent[]` → dòng thời gian: trục dọc + mốc (Lane C sở hữu).
///
/// ROUND 5 B — TRỰC QUAN THÀNH SƠ ĐỒ THẬT (Founder §12: «Trực quan vẫn chưa
/// tới khung concept»). Không đổi nguồn sự thật, chỉ đổi CÁCH VẼ dữ liệu có
/// kiểu; vẫn không có đường «bài → LLM → hình»:
/// - `ProcessStep[]` → `ProcessFlowView`: nút trên MỘT TRỤC liên tục + mũi
///   tên + dải tổng quan chạm được; bước withheld là nút rỗng chỉ trang
///   (trước: danh sách đánh số).
/// - `ComparisonSemantic` → `MindmapView`: nút trung tâm là tiêu đề dữ liệu,
///   mỗi thực thể một nút nhánh có màu mang chữ sách — đúng hình khung concept
///   khung 5. Bảng vẫn còn, sau nút chuyển «Sơ đồ tư duy / Bảng».
/// - `ConceptRelation[]` → cùng `MindmapView` (nút trung tâm tất định =
///   thực thể gặp nhiều nhất); quan hệ không chạm trung tâm ⇒ thẻ bên dưới.
/// - MÀU CHỈ PHÂN BIỆT NHÁNH/BƯỚC, có một dòng nói đúng thế cho trẻ; KHÔNG
///   emoji theo nghĩa (chọn emoji = suy ra nội dung nguồn không nói).
/// Bài 17 chỉ có Process + Comparison ⇒ hai tab kia KHÔNG hiện (fail closed);
/// hai renderer còn lại được kiểm bằng dữ liệu có kiểu dựng trong test.
/// Mã luật sinh (`derivation`) rời màn trẻ đọc ⇒ nằm trong sheet «Nguồn & độ tin».
library;

import 'package:flutter/material.dart';

import '../../app/theme/band_density_scope.dart';
import '../../app/theme/wal_tokens.dart';
import '../../core/lesson_model/lesson_document.dart';
import '../../core/lesson_model/semantic_data.dart';
import 'views/mindmap_view.dart';
import 'views/process_flow_view.dart';
import 'views/timeline_view.dart';
import 'widgets/source_sheet.dart';
import 'widgets/trust_sheet.dart';

class VisualView extends StatefulWidget {
  const VisualView({
    super.key,
    required this.doc,
    required this.onShowInRead,
    this.header,
  });

  final LessonDocument doc;
  final void Function(String blockId) onShowInRead;

  /// ROUND 5 D1 — thẻ «SAM đề xuất» đi vào ĐẦU VÙNG CUỘN thay vì bị ghim trên
  /// đầu màn (như màn Đọc từ vòng 4): lý do dài 6 dòng ghim lại thì che mất
  /// nút trung tâm của sơ đồ.
  final Widget? header;

  static const summaryShape = '📋 Bảng tóm tắt';

  static Key shapeKey(String shapeLabel) => Key('visual-shape-$shapeLabel');
  static Key instanceKey(String id) => Key('visual-instance-$id');

  /// Sơ đồ tư duy chỉ đọc được khi mỗi nút mang tối đa 2 dòng chữ; nhiều
  /// chiều hơn ⇒ CHỈ bảng (fail closed, không nhồi chữ vào nút).
  static bool mindmapFits(ComparisonSemantic s) => s.dimensions.length <= 2;

  /// ROUND 5 — nút chuyển cách nhìn của bảng so sánh («mindmap» / «table»).
  static Key comparisonViewKey(String v) => Key('visual-comparison-view-$v');
  static const comparisonLegendKey = Key('visual-comparison-legend');

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

  /// Hình dạng có trong bài, theo thứ tự xuất hiện — tab chỉ cho thứ CÓ.
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
  /// Hình dạng đang xem; `VisualView.summaryShape` = Bảng tóm tắt.
  late String _shape;

  /// Sơ đồ đang xem trong hình dạng đó (khi có nhiều).
  int _instance = 0;

  /// ROUND 5 — bảng so sánh có HAI cách nhìn: sơ đồ tư duy (khung concept,
  /// mặc định) và bảng. Cùng một dữ liệu có kiểu, không thêm sự thật nào.
  bool _comparisonAsTable = false;

  @override
  void initState() {
    super.initState();
    final shapes = VisualView.shapesOf(widget.doc);
    _shape = shapes.isEmpty ? VisualView.summaryShape : shapes.first;
  }

  List<SemanticData> get _ofShape => [
    for (final s in widget.doc.semantic)
      if (s.shapeLabel == _shape) s,
  ];

  @override
  Widget build(BuildContext context) {
    final doc = widget.doc;
    final shapes = VisualView.shapesOf(doc);
    final summary = _shape == VisualView.summaryShape;
    final inShape = summary ? const <SemanticData>[] : _ofShape;
    final current = inShape.isEmpty
        ? null
        : inShape[_instance.clamp(0, inShape.length - 1)];
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
          Wrap(
            spacing: WalSpacing.sm,
            runSpacing: WalSpacing.sm,
            children: [
              for (final sh in shapes)
                _chip(
                  key: VisualView.shapeKey(sh),
                  label:
                      '${VisualView.icon(doc.semantic.firstWhere((s) => s.shapeLabel == sh))} $sh',
                  selected: _shape == sh,
                  onTap: () => setState(() {
                    _shape = sh;
                    _instance = 0;
                  }),
                ),
              _chip(
                key: VisualView.shapeKey('summary'),
                label: VisualView.summaryShape,
                selected: summary,
                onTap: () => setState(() => _shape = VisualView.summaryShape),
              ),
            ],
          ),
          if (inShape.length > 1) ...[
            const SizedBox(height: WalSpacing.sm),
            Wrap(
              spacing: WalSpacing.xs,
              runSpacing: WalSpacing.xs,
              children: [
                for (var i = 0; i < inShape.length; i++)
                  _chip(
                    key: VisualView.instanceKey(inShape[i].id),
                    label: '${i + 1} · ${_short(inShape[i].title)}',
                    selected: _instance == i,
                    small: true,
                    onTap: () => setState(() => _instance = i),
                  ),
              ],
            ),
          ],
          const SizedBox(height: WalSpacing.md),
          if (shapes.isEmpty)
            Row(
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
                    // ROUND 4 §6.5 — fail closed nói VÌ SAO bằng lời trẻ.
                    'SAM chưa có sơ đồ cho bài này. SAM chỉ vẽ sơ đồ khi sách '
                    'viết rõ từng bước hoặc từng cách; bài này chưa có phần như '
                    'vậy nên SAM không tự vẽ — con xem bảng tóm tắt, đọc sách '
                    'hoặc học cùng SAM nhé.',
                    style: TextStyle(
                      fontSize: WalType.body,
                      color: WalColors.ink,
                    ),
                  ),
                ),
              ],
            ),
          if (current != null) _renderer(current) else _summary(doc),
        ],
      ),
    );
  }

  static String _short(String t) =>
      t.length > 30 ? '${t.substring(0, 30)}…' : t;

  Widget _chip({
    required Key key,
    required String label,
    required bool selected,
    required VoidCallback onTap,
    bool small = false,
  }) => SizedBox(
    height: WalSpacing.minTouch,
    child: ChoiceChip(
      key: key,
      label: Text(
        label,
        style: TextStyle(
          fontSize: small ? 13 : WalType.secondary,
          fontWeight: FontWeight.w600,
          color: selected ? Colors.white : WalColors.ink,
        ),
      ),
      selected: selected,
      selectedColor: small ? WalColors.primaryText : WalColors.primary500,
      backgroundColor: Colors.white,
      showCheckmark: false,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
      ),
      onSelected: (_) => onTap(),
    ),
  );

  Widget _renderer(SemanticData s) {
    // Sơ đồ tư duy của bảng so sánh LẤY CHÍNH tiêu đề làm nút trung tâm ⇒
    // không in lại tiêu đề bên trên (Nokia: một dòng thừa là một dòng đọc mất).
    final titleIsHub =
        s is ComparisonSemantic &&
        !_comparisonAsTable &&
        VisualView.mindmapFits(s);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (!titleIsHub) ...[
          Text(
            s.title,
            style: const TextStyle(
              fontSize: WalType.title,
              fontWeight: FontWeight.w700,
              color: WalColors.ink,
            ),
          ),
          const SizedBox(height: 2),
        ],
        Text(
          _subtitle(s),
          style: const TextStyle(fontSize: 13, color: WalColors.inkSoft),
        ),
        const SizedBox(height: WalSpacing.sm),
        switch (s) {
          ProcessSemantic() => _process(s),
          ComparisonSemantic() => _comparison(s),
          ConceptMapSemantic() => _conceptMap(s),
          // Round 4 (Lane C, Golden Slice #2): renderer Lịch sử — mốc + nguồn kể
          // chuyện + thử xếp thứ tự (TimelineValidator), views/timeline_view.dart.
          TimelineSemantic() => TimelineView(
            doc: widget.doc,
            semantic: s,
            onOpenSource: _openSource,
          ),
        },
        const SizedBox(height: WalSpacing.md),
        _why(s),
      ],
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
    return '$n · ${_pageOf(firstSrc)} · chữ sách, SAM chỉ xếp lại';
  }

  /// «Vì sao SAM chọn sơ đồ này» — lời TẤT ĐỊNH theo luật sinh, không LLM.
  Widget _why(SemanticData s) {
    final text = switch (s) {
      ProcessSemantic() =>
        'Sách viết hoạt động này thành các bước đánh dấu «·» theo thứ tự — SAM '
            'xếp đúng thứ tự sách, giữ nguyên lời sách, không thêm bước nào. Bước '
            'nào SAM chưa đọc chắc thì để trống và chỉ trang.',
      // ROUND 5 D2 (Nokia, iter 1): lời này phải nói ĐÚNG THỨ TRẺ ĐANG NHÌN —
      // mặc định giờ là sơ đồ tư duy, không phải bảng.
      ComparisonSemantic() when !_comparisonAsTable =>
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
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Image.asset(
          'assets/mascot/sam-explain.png',
          width: densityOf(context).mascotChip,
          height: densityOf(context).mascotChip,
          errorBuilder: (_, _, _) => const SizedBox.shrink(),
        ),
        const SizedBox(width: WalSpacing.sm),
        Expanded(
          child: Container(
            padding: const EdgeInsets.all(WalSpacing.md),
            decoration: BoxDecoration(
              color: WalColors.surfaceLavender,
              borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Vì sao SAM chọn sơ đồ này',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                    color: WalColors.primaryText,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  text,
                  style: const TextStyle(
                    fontSize: WalType.secondary,
                    color: WalColors.ink,
                    height: 1.4,
                  ),
                ),
                SizedBox(
                  height: WalSpacing.minTouch - 8,
                  child: Align(
                    alignment: Alignment.centerLeft,
                    child: TextButton(
                      key: const Key('visual-trust-link'),
                      style: TextButton.styleFrom(
                        padding: EdgeInsets.zero,
                        minimumSize: const Size(WalSpacing.minTouch, 36),
                      ),
                      onPressed: () => showTrustSheet(context, doc: widget.doc),
                      child: const Text(
                        'ⓘ Nguồn & độ tin',
                        style: TextStyle(
                          fontSize: 13,
                          color: WalColors.primaryText,
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  void _openSource(String blockId) {
    final b = widget.doc.blockById(blockId);
    if (b == null) return;
    showSourceSheet(
      context,
      doc: widget.doc,
      block: b,
      onShowInRead: () => widget.onShowInRead(blockId),
    );
  }

  String _pageOf(String blockId) {
    final b = widget.doc.blockById(blockId);
    return b == null ? 'sách' : widget.doc.sourceLineForBlock(b);
  }

  // ── Process: dòng chảy nút + cạnh (ROUND 5, views/process_flow_view.dart) ──
  Widget _process(ProcessSemantic s) => ProcessFlowView(
    doc: widget.doc,
    semantic: s,
    onOpenSource: _openSource,
    onShowInRead: widget.onShowInRead,
    pageOf: _pageOf,
  );

  // ── Comparison: sơ đồ tư duy (mặc định) hoặc bảng ──

  Widget _comparison(ComparisonSemantic s) {
    final fits = VisualView.mindmapFits(s);
    final asTable = _comparisonAsTable || !fits;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (fits) ...[
          Row(
            children: [
              _chip(
                key: VisualView.comparisonViewKey('mindmap'),
                label: '🕸️ Sơ đồ tư duy',
                selected: !asTable,
                small: true,
                onTap: () => setState(() => _comparisonAsTable = false),
              ),
              const SizedBox(width: WalSpacing.xs),
              _chip(
                key: VisualView.comparisonViewKey('table'),
                label: '⚖️ Bảng',
                selected: asTable,
                small: true,
                onTap: () => setState(() => _comparisonAsTable = true),
              ),
            ],
          ),
          const SizedBox(height: WalSpacing.sm),
        ],
        Padding(
          padding: const EdgeInsets.only(bottom: WalSpacing.sm),
          child: Text(
            asTable
                ? 'Mỗi hàng là một cách sách nêu · chạm một hàng để tra cứu '
                      'lời sách'
                : 'Mỗi ô là một cách sách nêu · màu chỉ để phân biệt, không '
                      'phải điểm số · chạm một ô để tra cứu lời sách',
            key: VisualView.comparisonLegendKey,
            style: const TextStyle(fontSize: 11, color: WalColors.inkSoft),
          ),
        ),
        if (asTable) _comparisonTable(s) else _comparisonMindmap(s),
      ],
    );
  }

  /// Thực thể → nút nhánh; mỗi chiều so sánh → một dòng chữ SÁCH trong nút.
  Widget _comparisonMindmap(ComparisonSemantic s) => MindmapView(
    hub: s.title,
    hubSourceBlockId: s.entities.first.sourceBlockId,
    onOpenSource: _openSource,
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
    decoration: BoxDecoration(
      color: Colors.white,
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
                onTap: () => _openSource(s.entities[i].sourceBlockId),
                child: _cell(
                  s.entities[i].name,
                  bold: true,
                  color: WalColors.primaryText,
                ),
              ),
              for (final d in s.dimensions)
                InkWell(
                  onTap: () => _openSource(s.entities[i].sourceBlockId),
                  child: _cell(d.values[i] ?? '— (sách không nói)'),
                ),
            ],
          ),
      ],
    ),
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
          padding: EdgeInsets.only(bottom: WalSpacing.sm),
          child: Text(
            'Ô giữa là khái niệm sách nói tới nhiều nhất · màu chỉ để phân '
            'biệt nhánh · chạm một ô để tra cứu lời sách',
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

  // ── Bảng tóm tắt (fallback) ──
  Widget _summary(LessonDocument doc) {
    final blocks = VisualView.summaryBlocks(doc);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text(
          'Bảng tóm tắt — lời sách',
          style: TextStyle(
            fontSize: WalType.title,
            fontWeight: FontWeight.w700,
            color: WalColors.ink,
          ),
        ),
        const SizedBox(height: WalSpacing.sm),
        if (blocks.isEmpty)
          const Text(
            'Bài này chưa có phần tóm tắt SAM đọc được.',
            style: TextStyle(fontSize: WalType.body, color: WalColors.inkSoft),
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
    );
  }

  Widget _card(Widget child) => Container(
    width: double.infinity,
    margin: const EdgeInsets.only(bottom: WalSpacing.sm),
    padding: const EdgeInsets.all(WalSpacing.md),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
    ),
    child: child,
  );
}
