/// TRACK B — MODE 2 «Trực quan»: renderer trên `SemanticData` CÓ KIỂU.
///
/// Không có đường «bài → LLM → hình». Tab con chỉ hiện cho hình dạng bài này
/// CÓ (16-UX-CONCEPT §1 hàng 5); luôn có «Bảng tóm tắt» làm fallback (chữ
/// nguyên văn phần MỤC TIÊU / Em đã học). Nút/hàng chạm được ⇒ mở đúng block
/// nguồn; «Xem trong Đọc» nhảy về Mode 1 tại block đó.
library;

import 'package:flutter/material.dart';

import '../../app/theme/band_density_scope.dart';
import '../../app/theme/wal_tokens.dart';
import '../../core/lesson_model/lesson_document.dart';
import '../../core/lesson_model/semantic_data.dart';
import 'widgets/source_sheet.dart';

class VisualView extends StatefulWidget {
  const VisualView({super.key, required this.doc, required this.onShowInRead});

  final LessonDocument doc;
  final void Function(String blockId) onShowInRead;

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

  @override
  State<VisualView> createState() => _VisualViewState();
}

class _VisualViewState extends State<VisualView> {
  int _tab = 0; // index vào doc.semantic; == semantic.length ⇒ Bảng tóm tắt

  @override
  Widget build(BuildContext context) {
    final doc = widget.doc;
    final n = doc.semantic.length;
    final summary = _tab >= n;
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
              for (var i = 0; i < n; i++)
                _tabChip(i, _tabLabel(doc, doc.semantic[i])),
              _tabChip(n, '📋 Bảng tóm tắt'),
            ],
          ),
          const SizedBox(height: WalSpacing.md),
          if (n == 0)
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
                    'SAM chưa có sơ đồ cho bài này — con xem bảng tóm tắt, đọc '
                    'sách hoặc học cùng SAM nhé.',
                    style: TextStyle(
                      fontSize: WalType.body,
                      color: WalColors.ink,
                    ),
                  ),
                ),
              ],
            ),
          if (summary) _summary(doc) else _renderer(doc.semantic[_tab]),
        ],
      ),
    );
  }

  /// Nhãn tab: hai sơ đồ CÙNG hình dạng thì thêm tên (Nokia n1 D2: hai tab
  /// «Sơ đồ quy trình» y hệt nhau, trẻ không biết tab nào là gì).
  static String _tabLabel(LessonDocument doc, SemanticData s) {
    final dup = doc.semantic.where((x) => x.shapeLabel == s.shapeLabel).length;
    final base = '${_icon(s)} ${s.shapeLabel}';
    if (dup <= 1) return base;
    final t = s.title.length > 26 ? '${s.title.substring(0, 26)}…' : s.title;
    return '$base: $t';
  }

  static String _icon(SemanticData s) => switch (s) {
    ProcessSemantic() => '🔁',
    ComparisonSemantic() => '⚖️',
    ConceptMapSemantic() => '🕸️',
    TimelineSemantic() => '🕰️',
  };

  Widget _tabChip(int i, String label) => SizedBox(
    height: WalSpacing.minTouch,
    child: ChoiceChip(
      label: Text(
        label,
        style: TextStyle(
          fontSize: WalType.secondary,
          fontWeight: FontWeight.w600,
          color: _tab == i ? Colors.white : WalColors.ink,
        ),
      ),
      selected: _tab == i,
      selectedColor: WalColors.primary500,
      backgroundColor: Colors.white,
      showCheckmark: false,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
      ),
      onSelected: (_) => setState(() => _tab = i),
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
      ConceptMapSemantic() => 'Các quan hệ lấy từ dữ liệu có kiểu của bài.',
      TimelineSemantic() => 'Các mốc lấy từ dữ liệu có kiểu của bài.',
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
                const SizedBox(height: 4),
                Text(
                  'luật: ${s.derivation} · ${s.trust.name}',
                  style: const TextStyle(
                    fontSize: 11,
                    color: WalColors.inkSoft,
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

  // ── Process ──
  Widget _process(ProcessSemantic s) => Column(
    children: [
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
        ),
      ],
    ),
  );

  String _pageOf(String blockId) {
    final b = widget.doc.blockById(blockId);
    return b == null ? 'sách' : widget.doc.sourceLineForBlock(b);
  }

  // ── Comparison ──
  Widget _comparison(ComparisonSemantic s) => Container(
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

  // ── Concept map / Timeline (kiểu có, dữ liệu Bài 17 không có) ──
  Widget _conceptMap(ConceptMapSemantic s) => Column(
    children: [
      for (final r in s.relations)
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
  );

  Widget _timeline(TimelineSemantic s) => Column(
    children: [
      for (final e in s.events)
        InkWell(
          onTap: () => _openSource(e.sourceBlockId),
          child: _card(
            Text(
              '${e.when} · ${e.title}',
              style: const TextStyle(
                fontSize: WalType.body,
                color: WalColors.ink,
              ),
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
