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
/// - `ProcessStep[]` → quy trình: dải tổng quan 1→2→3 + từng bước; bước
///   withheld là chỗ trống chỉ trang.
/// - `ConceptRelation[]` → sơ đồ khái niệm: nút TRUNG TÂM (thực thể xuất hiện
///   nhiều nhất, tất định) + nan hoa có nhãn quan hệ, vẽ bằng CustomPaint;
///   quan hệ không chạm nút trung tâm ⇒ thẻ «a —quan hệ→ b» bên dưới.
/// - `TimelineEvent[]` → dòng thời gian: trục dọc + mốc.
/// Bài 17 chỉ có Process + Comparison ⇒ hai tab kia KHÔNG hiện (fail closed);
/// hai renderer còn lại được kiểm bằng dữ liệu có kiểu dựng trong test.
/// Mã luật sinh (`derivation`) rời màn trẻ đọc ⇒ nằm trong sheet «Nguồn & độ tin».
library;

import 'package:flutter/material.dart';

import '../../app/theme/band_density_scope.dart';
import '../../app/theme/wal_tokens.dart';
import '../../core/lesson_model/lesson_document.dart';
import '../../core/lesson_model/semantic_data.dart';
import 'widgets/source_sheet.dart';
import 'widgets/trust_sheet.dart';

class VisualView extends StatefulWidget {
  const VisualView({super.key, required this.doc, required this.onShowInRead});

  final LessonDocument doc;
  final void Function(String blockId) onShowInRead;

  static const summaryShape = '📋 Bảng tóm tắt';

  static Key shapeKey(String shapeLabel) => Key('visual-shape-$shapeLabel');
  static Key instanceKey(String id) => Key('visual-instance-$id');

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

  static String _short(String t) => t.length > 30 ? '${t.substring(0, 30)}…' : t;

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

  Widget _renderer(SemanticData s) => Column(
    crossAxisAlignment: CrossAxisAlignment.stretch,
    children: [
      Text(
        s.title,
        style: const TextStyle(
          fontSize: WalType.title,
          fontWeight: FontWeight.w700,
          color: WalColors.ink,
        ),
      ),
      const SizedBox(height: 2),
      Text(
        _subtitle(s),
        style: const TextStyle(fontSize: 13, color: WalColors.inkSoft),
      ),
      const SizedBox(height: WalSpacing.sm),
      switch (s) {
        ProcessSemantic() => _process(s),
        ComparisonSemantic() => _comparison(s),
        ConceptMapSemantic() => _conceptMap(s),
        TimelineSemantic() => _timeline(s),
      },
      const SizedBox(height: WalSpacing.md),
      _why(s),
    ],
  );

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
                      onPressed: () =>
                          showTrustSheet(context, doc: widget.doc),
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

  // ── Process ──
  Widget _process(ProcessSemantic s) => Column(
    children: [
      _processStrip(s),
      // ROUND 4 §6.5 — chú giải + cách dùng, lời trẻ.
      Padding(
        padding: const EdgeInsets.only(top: WalSpacing.xs),
        child: Text(
          s.steps.any((st) => st.isWithheld)
              ? 'Số tím = bước sách viết · số xám = bước SAM để trống (xem '
                    'trong sách) · chạm một bước để tra cứu lời sách'
              : 'Mỗi số là một bước sách viết · chạm một bước để tra cứu '
                    'lời sách',
          key: const Key('visual-legend'),
          style: const TextStyle(fontSize: 11, color: WalColors.inkSoft),
        ),
      ),
      const SizedBox(height: WalSpacing.md),
      for (var i = 0; i < s.steps.length; i++) ...[
        _processNode(s.steps[i]),
        if (i < s.steps.length - 1)
          const SizedBox(
            height: 28,
            child: CustomPaint(painter: _ArrowPainter()),
          ),
      ],
    ],
  );

  /// Dải tổng quan ①→②→③: nhìn một cái thấy cả quy trình, rồi đọc từng bước.
  Widget _processStrip(ProcessSemantic s) => Container(
    key: const Key('visual-process-strip'),
    padding: const EdgeInsets.symmetric(
      horizontal: WalSpacing.sm,
      vertical: WalSpacing.sm,
    ),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
    ),
    child: SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: [
          for (var i = 0; i < s.steps.length; i++) ...[
            if (i > 0)
              const Padding(
                padding: EdgeInsets.symmetric(horizontal: 2),
                child: Icon(
                  Icons.arrow_forward,
                  size: 18,
                  color: WalColors.primary500,
                ),
              ),
            Container(
              width: 32,
              height: 32,
              alignment: Alignment.center,
              decoration: BoxDecoration(
                color: s.steps[i].isWithheld
                    ? WalColors.inkSoft
                    : WalColors.primary500,
                shape: BoxShape.circle,
              ),
              child: Text(
                '${s.steps[i].order}',
                style: const TextStyle(
                  fontSize: WalType.secondary,
                  fontWeight: FontWeight.w700,
                  color: Colors.white,
                ),
              ),
            ),
          ],
        ],
      ),
    ),
  );

  Widget _processNode(ProcessStep st) => InkWell(
    onTap: () => _openSource(st.sourceBlockId),
    borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 40,
          height: 40,
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: st.isWithheld ? WalColors.inkSoft : WalColors.primary500,
            shape: BoxShape.circle,
          ),
          child: Text(
            '${st.order}',
            style: const TextStyle(
              fontSize: WalType.body,
              fontWeight: FontWeight.w700,
              color: Colors.white,
            ),
          ),
        ),
        const SizedBox(width: WalSpacing.sm),
        Expanded(
          child: Container(
            padding: const EdgeInsets.all(WalSpacing.md),
            decoration: BoxDecoration(
              color: st.isWithheld ? WalColors.surface : Colors.white,
              border: st.isWithheld
                  ? Border.all(color: WalColors.inkSoft.withValues(alpha: 0.35))
                  : null,
              borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Text(
                    st.isWithheld
                        ? 'Bước này SAM chưa đọc được — con xem trong sách '
                              '(${_pageOf(st.sourceBlockId)}).'
                        : st.text!,
                    style: TextStyle(
                      fontSize: WalType.body,
                      color: st.isWithheld ? WalColors.inkSoft : WalColors.ink,
                      height: 1.45,
                    ),
                  ),
                ),
                const SizedBox(width: WalSpacing.xs),
                // dấu «chạm để tra cứu» — không phải nội dung
                const Icon(
                  Icons.menu_book_outlined,
                  size: 18,
                  color: WalColors.primaryText,
                ),
              ],
            ),
          ),
        ),
      ],
    ),
  );

  // ── Comparison ──
  Widget _comparison(ComparisonSemantic s) => Column(
    crossAxisAlignment: CrossAxisAlignment.stretch,
    children: [
      const Padding(
        padding: EdgeInsets.only(bottom: WalSpacing.xs),
        child: Text(
          'Mỗi hàng là một cách sách nêu · chạm một hàng để tra cứu lời sách',
          style: TextStyle(fontSize: 11, color: WalColors.inkSoft),
        ),
      ),
      _comparisonTable(s),
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

  // ── Concept map: nút trung tâm + nan hoa có nhãn ──
  Widget _conceptMap(ConceptMapSemantic s) {
    final hub = VisualView.hubOf(s);
    final spokes = <ConceptRelation>[];
    final rest = <ConceptRelation>[];
    for (final r in s.relations) {
      (r.a == hub || r.b == hub ? spokes : rest).add(r);
    }
    return Column(
      children: [
        Container(
          key: const Key('visual-concept-map'),
          padding: const EdgeInsets.all(WalSpacing.sm),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
          ),
          child: LayoutBuilder(
            builder: (ctx, c) {
              final w = c.maxWidth.isFinite ? c.maxWidth : 360.0;
              // Mỗi nan hoa một hàng cao 72; nút trung tâm ở cột trái.
              final h = (spokes.length * 72.0).clamp(96.0, 720.0);
              return SizedBox(
                width: w,
                height: h,
                child: Stack(
                  children: [
                    Positioned.fill(
                      child: CustomPaint(
                        painter: _SpokePainter(
                          count: spokes.length,
                          hubX: w * 0.22,
                          leafX: w * 0.62,
                        ),
                      ),
                    ),
                    Positioned(
                      left: 0,
                      top: h / 2 - 28,
                      width: w * 0.44,
                      child: Center(
                        child: _node(
                          hub,
                          hub: true,
                          onTap: () => _openSource(spokes.isNotEmpty
                              ? spokes.first.sourceBlockId
                              : s.relations.first.sourceBlockId),
                        ),
                      ),
                    ),
                    for (var i = 0; i < spokes.length; i++) ...[
                      Positioned(
                        left: w * 0.62,
                        top: (i + 0.5) * (h / spokes.length) - 22,
                        width: w * 0.38,
                        child: _node(
                          spokes[i].a == hub ? spokes[i].b : spokes[i].a,
                          onTap: () => _openSource(spokes[i].sourceBlockId),
                        ),
                      ),
                      Positioned(
                        left: w * 0.36,
                        top: (i + 0.5) * (h / spokes.length) - 32,
                        width: w * 0.26,
                        child: Text(
                          spokes[i].relation,
                          textAlign: TextAlign.center,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w600,
                            color: WalColors.primaryText,
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
              );
            },
          ),
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

  Widget _node(String label, {bool hub = false, VoidCallback? onTap}) =>
      Material(
        color: hub ? WalColors.primary500 : WalColors.surfaceLavender,
        borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
          child: Container(
            constraints: const BoxConstraints(minHeight: 44),
            padding: const EdgeInsets.symmetric(
              horizontal: WalSpacing.sm,
              vertical: 6,
            ),
            alignment: Alignment.center,
            child: Text(
              label,
              textAlign: TextAlign.center,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                fontSize: hub ? WalType.body : WalType.secondary,
                fontWeight: FontWeight.w700,
                color: hub ? Colors.white : WalColors.primaryText,
              ),
            ),
          ),
        ),
      );

  // ── Timeline: trục dọc + mốc ──
  Widget _timeline(TimelineSemantic s) => Column(
    key: const Key('visual-timeline'),
    children: [
      for (var i = 0; i < s.events.length; i++)
        InkWell(
          onTap: () => _openSource(s.events[i].sourceBlockId),
          child: IntrinsicHeight(
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                SizedBox(
                  width: 28,
                  child: CustomPaint(
                    painter: _TimelinePainter(
                      first: i == 0,
                      last: i == s.events.length - 1,
                    ),
                  ),
                ),
                const SizedBox(width: WalSpacing.sm),
                Expanded(
                  child: _card(
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          s.events[i].when,
                          style: const TextStyle(
                            fontSize: WalType.secondary,
                            fontWeight: FontWeight.w700,
                            color: WalColors.primaryText,
                          ),
                        ),
                        Text(
                          s.events[i].title,
                          style: const TextStyle(
                            fontSize: WalType.body,
                            fontWeight: FontWeight.w600,
                            color: WalColors.ink,
                          ),
                        ),
                        if (s.events[i].text != null)
                          Text(
                            s.events[i].text!,
                            style: const TextStyle(
                              fontSize: WalType.secondary,
                              color: WalColors.ink,
                              height: 1.4,
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
    ],
  );

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

/// Mũi tên nối hai bước — vẽ tay, không gói ngoài.
class _ArrowPainter extends CustomPainter {
  const _ArrowPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final p = Paint()
      ..color = WalColors.primary500
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;
    const x = 20.0; // tâm vòng tròn số (width 40)
    canvas.drawLine(Offset(x, 2), Offset(x, size.height - 8), p);
    canvas.drawLine(
      Offset(x - 6, size.height - 14),
      Offset(x, size.height - 6),
      p,
    );
    canvas.drawLine(
      Offset(x + 6, size.height - 14),
      Offset(x, size.height - 6),
      p,
    );
  }

  @override
  bool shouldRepaint(_ArrowPainter old) => false;
}

/// Nan hoa từ nút trung tâm tới từng nút lá của sơ đồ khái niệm.
class _SpokePainter extends CustomPainter {
  const _SpokePainter({
    required this.count,
    required this.hubX,
    required this.leafX,
  });
  final int count;
  final double hubX, leafX;

  @override
  void paint(Canvas canvas, Size size) {
    if (count == 0) return;
    final p = Paint()
      ..color = WalColors.primary500.withValues(alpha: 0.6)
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;
    final hub = Offset(hubX, size.height / 2);
    for (var i = 0; i < count; i++) {
      final y = (i + 0.5) * (size.height / count);
      canvas.drawLine(hub, Offset(leafX, y), p);
    }
  }

  @override
  bool shouldRepaint(_SpokePainter old) =>
      old.count != count || old.hubX != hubX || old.leafX != leafX;
}

/// Trục dọc + chấm mốc của dòng thời gian.
class _TimelinePainter extends CustomPainter {
  const _TimelinePainter({required this.first, required this.last});
  final bool first, last;

  @override
  void paint(Canvas canvas, Size size) {
    final line = Paint()
      ..color = WalColors.primary500.withValues(alpha: 0.5)
      ..strokeWidth = 3
      ..strokeCap = StrokeCap.round;
    const x = 14.0;
    const dotY = 22.0;
    if (!first) canvas.drawLine(const Offset(x, 0), const Offset(x, dotY), line);
    if (!last) {
      canvas.drawLine(const Offset(x, dotY), Offset(x, size.height), line);
    }
    canvas.drawCircle(
      const Offset(x, dotY),
      7,
      Paint()..color = WalColors.primary500,
    );
  }

  @override
  bool shouldRepaint(_TimelinePainter old) =>
      old.first != first || old.last != last;
}
