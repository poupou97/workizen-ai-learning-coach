/// TRACK B ROUND 5 — «SƠ ĐỒ QUÁ TRÌNH»: nút + cạnh + dòng chảy.
///
/// Vòng 4 vẽ quy trình bằng MỘT DANH SÁCH ĐÁNH SỐ; Founder §12 gọi đúng tên:
/// đó chưa phải sơ đồ. Vòng 5 dựng lại thành dòng chảy thật — mỗi bước là một
/// NÚT trên một TRỤC liên tục, có mũi tên giữa các nút, có dải tổng quan chạm
/// được ở đầu, và bước bị giữ lại là một nút RỖNG nhìn thấy được chỗ trống.
///
/// Vẫn không có gì được sinh ra: chữ trong nút là `ProcessStep.text` NGUYÊN
/// VĂN, thứ tự là thứ tự sách, màu chỉ để phân biệt bước (không mã hoá nghĩa).
///
/// MỘT thứ mới được thêm và nó vẫn là chữ của sách: nếu lời sách trong bước có
/// «(Hình 17.3)» VÀ tài liệu có đúng một chú thích mang nguyên văn «Hình 17.3»
/// thì nút hiện một chip đưa trẻ tới đúng chỗ đó trong Đọc. Đây là so khớp
/// CHUỖI NGUYÊN VĂN giữa hai block tin được, không phải suy ra ảnh cho bước:
/// KHÔNG hiện ảnh trong nút, vì liên kết ảnh↔chú thích (`captionBlockId`) đang
/// là lỗi đã báo cho Lane A-pipeline (round 4 §5.6) — chỉ ra được lỗi đó là
/// một lời hứa sai với trẻ, còn chỉ chỗ trong sách thì không.
library;

import 'package:flutter/material.dart';

import '../../../app/theme/wal_tokens.dart';
import '../../../core/lesson_model/lesson_document.dart';
import '../../../core/lesson_model/semantic_data.dart';
import 'mindmap_view.dart';

class ProcessFlowView extends StatelessWidget {
  const ProcessFlowView({
    super.key,
    required this.doc,
    required this.semantic,
    required this.onOpenSource,
    required this.onShowInRead,
    required this.pageOf,
    this.onOpenStep,
  });

  final LessonDocument doc;
  final ProcessSemantic semantic;
  final void Function(String blockId) onOpenSource;
  final void Function(String blockId) onShowInRead;

  /// ⭐ ROUND 7 · V1 — chạm một bước ⇒ GIẢI THÍCH bước đó (Founder order 49
  /// §3), không chỉ mở lại lời sách đã nằm trong ô. `null` ⇒ hành vi vòng 5:
  /// chạm mở thẳng sheet nguồn. Renderer vẫn không biết bài nào: nó chỉ trao
  /// lại `ProcessStep` đã có trong dữ liệu có kiểu.
  final void Function(ProcessStep step)? onOpenStep;

  void _tap(ProcessStep step) => onOpenStep == null
      ? onOpenSource(step.sourceBlockId)
      : onOpenStep!(step);

  /// Dòng «SGK … · trang N» của một block — chủ sở hữu là `LessonDocument`.
  final String Function(String blockId) pageOf;

  static const railKey = Key('visual-process-strip');
  static const flowKey = Key('visual-process-flow');
  static Key stepKey(int order) => Key('visual-process-step-$order');
  static Key figureKey(int order) => Key('visual-process-figure-$order');
  static const legendKey = Key('visual-legend');

  /// «Hình 17.3» trong lời sách của bước → block chú thích mang ĐÚNG chuỗi đó.
  /// Không có, hoặc có nhiều hơn một ⇒ không chip (fail closed).
  static ({String label, String blockId})? figureRefIn(
    LessonDocument doc,
    ProcessStep step,
  ) {
    final text = step.text;
    if (text == null) return null;
    final m = RegExp(r'Hình\s+\d+\.\d+').firstMatch(text);
    if (m == null) return null;
    final label = m.group(0)!.replaceAll(RegExp(r'\s+'), ' ');
    final hits = [
      for (final b in doc.blocks)
        if (b is CaptionBlock && b.text.trim() == label) b,
    ];
    return hits.length == 1 ? (label: label, blockId: hits.single.id) : null;
  }

  Color _colorOf(int i, bool withheld) =>
      withheld ? WalColors.inkSoft : MindmapPalette.at(i).line;

  @override
  Widget build(BuildContext context) {
    final steps = semantic.steps;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _rail(steps),
        Padding(
          padding: const EdgeInsets.only(top: WalSpacing.xs),
          child: Text(
            steps.any((s) => s.isWithheld)
                ? 'Mỗi ô là một bước sách viết · ô xám là bước SAM để trống '
                      '(xem trong sách) · chạm một bước để tra cứu lời sách'
                : 'Mỗi ô là một bước sách viết, mũi tên là thứ tự làm · chạm '
                      'một bước để tra cứu lời sách',
            key: legendKey,
            style: const TextStyle(fontSize: 11, color: WalColors.inkSoft),
          ),
        ),
        const SizedBox(height: WalSpacing.md),
        Container(
          key: flowKey,
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
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              for (var i = 0; i < steps.length; i++)
                _node(steps[i], i, i == steps.length - 1),
            ],
          ),
        ),
      ],
    );
  }

  /// Dải tổng quan: nhìn một cái thấy cả dòng chảy; mỗi số chạm được.
  Widget _rail(List<ProcessStep> steps) => Container(
    key: railKey,
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
          for (var i = 0; i < steps.length; i++) ...[
            if (i > 0)
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 3),
                child: Icon(
                  Icons.arrow_forward,
                  size: 18,
                  color: WalColors.primary500.withValues(alpha: 0.7),
                ),
              ),
            InkWell(
              onTap: () => _tap(steps[i]),
              customBorder: const CircleBorder(),
              child: Container(
                width: 34,
                height: 34,
                alignment: Alignment.center,
                decoration: BoxDecoration(
                  color: _colorOf(i, steps[i].isWithheld),
                  shape: BoxShape.circle,
                ),
                child: Text(
                  '${steps[i].order}',
                  style: const TextStyle(
                    fontSize: WalType.secondary,
                    fontWeight: FontWeight.w700,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
          ],
        ],
      ),
    ),
  );

  Widget _node(ProcessStep st, int i, bool last) {
    final color = _colorOf(i, st.isWithheld);
    final fig = figureRefIn(doc, st);
    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SizedBox(
            width: 46,
            child: Stack(
              children: [
                Positioned.fill(
                  child: CustomPaint(
                    painter: _FlowPainter(color: color, last: last),
                  ),
                ),
                Positioned(
                  top: 0,
                  left: 3,
                  child: Container(
                    width: 40,
                    height: 40,
                    alignment: Alignment.center,
                    decoration: BoxDecoration(
                      color: color,
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
                ),
              ],
            ),
          ),
          Expanded(
            child: Padding(
              padding: EdgeInsets.only(bottom: last ? 0 : 18),
              child: Material(
                color: st.isWithheld ? WalColors.surface : Colors.white,
                borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
                child: InkWell(
                  key: stepKey(st.order),
                  borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
                  onTap: () => _tap(st),
                  child: Container(
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(
                        WalSpacing.radiusButton,
                      ),
                      border: Border.all(
                        color: color.withValues(alpha: 0.30),
                        width: 1,
                      ),
                    ),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(
                        WalSpacing.radiusButton - 1,
                      ),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          // vạch màu bên trái = «nút này thuộc bước mấy»
                          Container(width: 4, color: color),
                          Expanded(
                            child: Padding(
                              padding: const EdgeInsets.all(WalSpacing.md - 2),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Row(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Expanded(
                                        child: Text(
                                          st.isWithheld
                                              ? 'Bước này SAM chưa đọc được — '
                                                    'con xem trong sách '
                                                    '(${pageOf(st.sourceBlockId)}).'
                                              : st.text!,
                                          style: TextStyle(
                                            fontSize: WalType.body,
                                            color: st.isWithheld
                                                ? WalColors.inkSoft
                                                : WalColors.ink,
                                            height: 1.45,
                                          ),
                                        ),
                                      ),
                                      const SizedBox(width: WalSpacing.xs),
                                      const Icon(
                                        Icons.menu_book_outlined,
                                        size: 18,
                                        color: WalColors.primaryText,
                                      ),
                                    ],
                                  ),
                                  if (fig != null) ...[
                                    const SizedBox(height: WalSpacing.sm),
                                    _figureChip(fig, st.order),
                                  ],
                                ],
                              ),
                            ),
                          ),
                        ],
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
  }

  /// Chip «sách chỉ tới hình nào» — chạm là nhảy về Đọc đúng chỗ chú thích.
  Widget _figureChip(({String label, String blockId}) fig, int order) => Align(
    alignment: Alignment.centerLeft,
    child: SizedBox(
      height: 36,
      child: TextButton.icon(
        key: figureKey(order),
        style: TextButton.styleFrom(
          padding: const EdgeInsets.symmetric(horizontal: WalSpacing.sm),
          backgroundColor: WalColors.surfaceLavender,
          foregroundColor: WalColors.primaryText,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
          ),
        ),
        onPressed: () => onShowInRead(fig.blockId),
        icon: const Icon(Icons.image_outlined, size: 16),
        label: Text(
          'Sách chỉ tới ${fig.label} — xem trong Đọc',
          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
        ),
      ),
    ),
  );
}

/// Trục dòng chảy: đường dọc liên tục qua cả sơ đồ + mũi tên trước nút sau.
class _FlowPainter extends CustomPainter {
  const _FlowPainter({required this.color, required this.last});
  final Color color;
  final bool last;

  @override
  void paint(Canvas canvas, Size size) {
    final p = Paint()
      ..color = color.withValues(alpha: 0.85)
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;
    const x = 23.0; // tâm huy hiệu số (left 3 + 40/2)
    const top = 42.0;
    if (last) {
      // đuôi ngắn có mũ tròn — kết thúc dòng chảy, không hứa thêm bước
      final end = (top + 10).clamp(top, size.height);
      if (end > top) canvas.drawLine(const Offset(x, top), Offset(x, end), p);
      return;
    }
    final end = size.height - 2;
    if (end <= top) return;
    canvas.drawLine(const Offset(x, top), Offset(x, end), p);
    canvas.drawLine(Offset(x - 6, end - 9), Offset(x, end - 1), p);
    canvas.drawLine(Offset(x + 6, end - 9), Offset(x, end - 1), p);
  }

  @override
  bool shouldRepaint(_FlowPainter old) =>
      old.color != color || old.last != last;
}
