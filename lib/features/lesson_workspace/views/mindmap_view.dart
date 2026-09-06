/// TRACK B ROUND 5 — «SƠ ĐỒ TƯ DUY»: nút + nhánh, vẽ từ DỮ LIỆU CÓ KIỂU.
///
/// Khung concept 5 (`concept/concept-ai-first/learning-view.png`) vẽ Trực quan
/// là một sơ đồ tư duy: MỘT nút trung tâm, các nút nhánh có màu, mỗi nút một
/// dòng chữ lấy từ sách. Vòng 4 mới chỉ có bảng và danh sách chữ ⇒ Trực quan
/// đứng ở 70–80 %. Vòng 5 đóng đúng khoảng đó — KHÔNG bằng cách sinh hình:
///
/// - Đầu vào là `SemanticData` CÓ KIỂU đã tin được (`ComparisonSemantic`,
///   `ConceptMapSemantic`). Không có đường «bài → LLM → hình».
/// - Mỗi nút mang `sourceBlockId` của chính nó ⇒ chạm là ra lời sách.
/// - MÀU CHỈ ĐỂ PHÂN BIỆT NHÁNH, theo THỨ TỰ nút — không mã hoá nghĩa, không
///   mã hoá điểm số. Màn có một dòng nói đúng điều đó cho trẻ.
/// - KHÔNG emoji theo nghĩa: khung concept có emoji cho từng nhóm chất, nhưng
///   chọn emoji = suy ra nội dung khái niệm, mà nguồn không nói. Fail closed.
///
/// Bố cục (tất định theo số nút):
/// - n ≤ 4 → đúng khung concept: một hàng nút TRÊN, nút trung tâm, một hàng
///   nút DƯỚI; nhánh vẽ bằng `CustomPaint` (thân dọc + thanh ngang + cong góc).
/// - n > 4 → cây: nút trung tâm ở trên, thân dọc bên trái, mỗi nút một nhánh
///   khuỷu — vẫn là nút + cạnh, vẫn đọc được trên màn 360 dp.
library;

import 'package:flutter/material.dart';

import '../../../app/theme/wal_tokens.dart';

/// Một dòng chữ trong nút — NGUYÊN VĂN lời sách, kèm tên chiều nếu có.
class MindmapLine {
  const MindmapLine({required this.value, this.name});

  /// Tên chiều so sánh (vd «Dùng để tách») — `null` ⇒ chỉ có chữ.
  final String? name;

  /// Chữ sách. `null` ⇒ sách không nói ở chiều này (ô để trống, không điền hộ).
  final String? value;
}

/// Một nút nhánh.
class MindmapNode {
  const MindmapNode({
    required this.label,
    required this.sourceBlockId,
    this.edgeLabel,
    this.lines = const [],
  });

  final String label;

  /// Nhãn trên nhánh (quan hệ của sơ đồ khái niệm) — `null` ⇒ nhánh trơn.
  final String? edgeLabel;
  final List<MindmapLine> lines;
  final String sourceBlockId;
}

/// Cặp màu một nhánh. Nền + chữ đã kiểm tương phản ≥ 4.5:1
/// (`mindmap_view_test.dart` §tương phản) — đổi màu mà quên cặp ⇒ test đỏ.
class BranchColor {
  const BranchColor({required this.bg, required this.fg, required this.line});
  final Color bg, fg, line;
}

abstract final class MindmapPalette {
  /// Thứ tự cố định ⇒ cùng dữ liệu luôn ra cùng màu (kiểm lại được).
  static const branches = <BranchColor>[
    BranchColor(
      bg: WalColors.surfaceLavender,
      fg: WalColors.primaryText,
      line: WalColors.primary500,
    ),
    BranchColor(
      bg: Color(0xFFE9FBF5),
      fg: WalColors.mintText,
      line: WalColors.mint500,
    ),
    BranchColor(
      bg: Color(0xFFFFF4E0),
      fg: WalColors.warnText,
      line: WalColors.accent500,
    ),
    BranchColor(
      bg: Color(0xFFFFEFF7),
      fg: WalColors.pinkText,
      line: WalColors.pink500,
    ),
  ];

  static BranchColor at(int i) => branches[i % branches.length];
}

class MindmapView extends StatelessWidget {
  const MindmapView({
    super.key,
    required this.hub,
    required this.nodes,
    required this.onOpenSource,
    this.hubSourceBlockId,
    this.onTapNode,
  });

  /// Nút trung tâm — chữ đã có sẵn trong dữ liệu có kiểu, KHÔNG tự đặt tên.
  final String hub;
  final List<MindmapNode> nodes;
  final void Function(String blockId) onOpenSource;
  final String? hubSourceBlockId;

  /// ⭐ ROUND 7 · V1 — chạm một nút ⇒ GIẢI THÍCH nút đó, không chỉ mở lại lời
  /// sách trong ô. `null` ⇒ hành vi vòng 5 (mở sheet nguồn). Renderer trao
  /// lại chỉ số + chính nút — nó không biết nút ấy thuộc bài nào.
  final void Function(int index, MindmapNode node)? onTapNode;

  void _tap(int i, MindmapNode n) =>
      onTapNode == null ? onOpenSource(n.sourceBlockId) : onTapNode!(i, n);

  static const viewKey = Key('visual-mindmap');
  static Key nodeKey(int i) => Key('visual-mindmap-node-$i');
  static const hubKey = Key('visual-mindmap-hub');

  /// Ngưỡng đổi bố cục — 4 nút là hình khung concept (2 trên, 2 dưới).
  static const gridMax = 4;

  static const _gap = 10.0;
  static const _strip = 30.0;

  @override
  Widget build(BuildContext context) => Container(
    key: viewKey,
    padding: const EdgeInsets.symmetric(
      horizontal: WalSpacing.sm,
      vertical: WalSpacing.md,
    ),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
    ),
    child: LayoutBuilder(
      builder: (ctx, c) {
        final w = c.maxWidth.isFinite ? c.maxWidth : 340.0;
        return nodes.length <= gridMax ? _grid(w) : _tree(w);
      },
    ),
  );

  // ── Bố cục khung concept: hàng trên · nút trung tâm · hàng dưới ──
  Widget _grid(double w) {
    // n ≤ 2 ⇒ trung tâm ở trên, tất cả nhánh xuống dưới (một hàng thoáng hơn
    // hai hàng lẻ trên màn 360 dp).
    final top = nodes.length <= 2 ? 0 : (nodes.length / 2).ceil();
    final above = nodes.take(top).toList();
    final below = nodes.skip(top).toList();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (above.isNotEmpty) ...[
          _row(above, 0, w),
          SizedBox(
            height: _strip,
            child: CustomPaint(
              painter: _BranchPainter(
                centres: _centres(above.length, w),
                hubX: w / 2,
                colors: [for (var i = 0; i < above.length; i++) _c(i).line],
                toHub: true,
              ),
            ),
          ),
        ],
        Center(child: _hubPill()),
        SizedBox(
          height: _strip,
          child: CustomPaint(
            painter: _BranchPainter(
              centres: _centres(below.length, w),
              hubX: w / 2,
              colors: [
                for (var i = 0; i < below.length; i++) _c(above.length + i).line,
              ],
              toHub: false,
            ),
          ),
        ),
        _row(below, above.length, w),
      ],
    );
  }

  /// Tâm cột của một hàng — 1 nút ⇒ giữa, 2 nút ⇒ hai cột đều nhau.
  static List<double> _centres(int n, double w) {
    if (n <= 1) return [w / 2];
    final cw = (w - _gap) / 2;
    return [cw / 2, cw + _gap + cw / 2];
  }

  /// `IntrinsicHeight` ⇒ hai nút cùng hàng CAO BẰNG NHAU (khung concept vẽ
  /// thế); thiếu nó, `stretch` trong cột cuộn dọc là chiều cao vô hạn.
  Widget _row(List<MindmapNode> row, int offset, double w) => IntrinsicHeight(
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        for (var i = 0; i < row.length; i++) ...[
          if (i > 0) const SizedBox(width: _gap),
          Expanded(child: _card(row[i], offset + i)),
        ],
      ],
    ),
  );

  // ── Bố cục cây: thân dọc bên trái, mỗi nút một khuỷu ──
  Widget _tree(double w) => Column(
    crossAxisAlignment: CrossAxisAlignment.stretch,
    children: [
      Center(child: _hubPill()),
      for (var i = 0; i < nodes.length; i++)
        IntrinsicHeight(
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              SizedBox(
                width: 26,
                child: CustomPaint(
                  painter: _TrunkPainter(
                    color: _c(i).line,
                    last: i == nodes.length - 1,
                  ),
                ),
              ),
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.only(bottom: WalSpacing.sm),
                  child: _card(nodes[i], i),
                ),
              ),
            ],
          ),
        ),
    ],
  );

  BranchColor _c(int i) => MindmapPalette.at(i);

  Widget _hubPill() => Material(
    color: WalColors.primary500,
    borderRadius: BorderRadius.circular(999),
    child: InkWell(
      key: hubKey,
      borderRadius: BorderRadius.circular(999),
      onTap: hubSourceBlockId == null
          ? null
          : () => onOpenSource(hubSourceBlockId!),
      child: Container(
        constraints: const BoxConstraints(minHeight: 48),
        padding: const EdgeInsets.symmetric(
          horizontal: WalSpacing.lg,
          vertical: WalSpacing.sm,
        ),
        alignment: Alignment.center,
        child: Text(
          hub,
          textAlign: TextAlign.center,
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
          style: const TextStyle(
            fontSize: WalType.body,
            fontWeight: FontWeight.w700,
            color: Colors.white,
          ),
        ),
      ),
    ),
  );

  Widget _card(MindmapNode n, int i) {
    final c = _c(i);
    return Material(
      color: c.bg,
      borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
      child: InkWell(
        key: nodeKey(i),
        borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
        onTap: () => _tap(i, n),
        child: Container(
          constraints: const BoxConstraints(minHeight: 64),
          padding: const EdgeInsets.all(WalSpacing.sm + 2),
          decoration: BoxDecoration(
            border: Border.all(
              color: c.line.withValues(alpha: 0.45),
              width: 1.5,
            ),
            borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              if (n.edgeLabel != null)
                Padding(
                  padding: const EdgeInsets.only(bottom: 3),
                  child: Text(
                    n.edgeLabel!,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                      color: c.fg,
                    ),
                  ),
                ),
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: Text(
                      n.label,
                      style: TextStyle(
                        fontSize: WalType.secondary + 1,
                        fontWeight: FontWeight.w700,
                        color: c.fg,
                        height: 1.25,
                      ),
                    ),
                  ),
                  Icon(Icons.menu_book_outlined, size: 15, color: c.fg),
                ],
              ),
              for (final l in n.lines) ...[
                const SizedBox(height: 4),
                if (l.name != null)
                  Text(
                    l.name!,
                    style: const TextStyle(
                      fontSize: 11,
                      color: WalColors.inkSoft,
                    ),
                  ),
                Text(
                  l.value ?? '— (sách không nói)',
                  style: TextStyle(
                    fontSize: 13,
                    height: 1.3,
                    color: l.value == null ? WalColors.inkSoft : WalColors.ink,
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

/// Nhánh giữa hàng nút và nút trung tâm: thân dọc + thanh ngang + góc bo.
class _BranchPainter extends CustomPainter {
  const _BranchPainter({
    required this.centres,
    required this.hubX,
    required this.colors,
    required this.toHub,
  });

  final List<double> centres;
  final double hubX;
  final List<Color> colors;

  /// `true` ⇒ nhánh chạy TỪ hàng nút (y=0) XUỐNG nút trung tâm (y=h).
  final bool toHub;

  @override
  void paint(Canvas canvas, Size size) {
    if (centres.isEmpty) return;
    final mid = size.height / 2;
    const r = 8.0;
    for (var i = 0; i < centres.length; i++) {
      final p = Paint()
        ..color = (i < colors.length ? colors[i] : WalColors.primary500)
            .withValues(alpha: 0.75)
        ..strokeWidth = 2.5
        ..style = PaintingStyle.stroke
        ..strokeCap = StrokeCap.round;
      final x = centres[i];
      final path = Path();
      // đoạn dọc phía nút lá
      if (toHub) {
        path.moveTo(x, 0);
        path.lineTo(x, mid - r);
      } else {
        path.moveTo(x, size.height);
        path.lineTo(x, mid + r);
      }
      // góc bo rồi chạy ngang về trục trung tâm
      final dir = hubX >= x ? 1.0 : -1.0;
      if ((hubX - x).abs() > r) {
        path.quadraticBezierTo(x, mid, x + dir * r, mid);
        path.lineTo(hubX - dir * r, mid);
        path.quadraticBezierTo(hubX, mid, hubX, toHub ? mid + r : mid - r);
      } else {
        path.lineTo(x, toHub ? mid + r : mid - r);
      }
      // đoạn dọc phía nút trung tâm
      path.lineTo(hubX, toHub ? size.height : 0);
      canvas.drawPath(path, p);
      _dot(canvas, Offset(x, toHub ? 1 : size.height - 1), p.color);
    }
    _dot(canvas, Offset(hubX, toHub ? size.height - 1 : 1), WalColors.primary500);
  }

  static void _dot(Canvas canvas, Offset o, Color c) => canvas.drawCircle(
    o,
    3,
    Paint()..color = c,
  );

  @override
  bool shouldRepaint(_BranchPainter old) =>
      old.centres.length != centres.length ||
      old.hubX != hubX ||
      old.toHub != toHub;
}

/// Thân dọc + khuỷu của bố cục cây (n > 4).
class _TrunkPainter extends CustomPainter {
  const _TrunkPainter({required this.color, required this.last});
  final Color color;
  final bool last;

  @override
  void paint(Canvas canvas, Size size) {
    final p = Paint()
      ..color = color.withValues(alpha: 0.75)
      ..strokeWidth = 2.5
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;
    const x = 13.0;
    final y = 32.0.clamp(0.0, size.height - 4);
    const r = 8.0;
    final path = Path()
      ..moveTo(x, 0)
      ..lineTo(x, last ? y : size.height);
    canvas.drawPath(path, p);
    canvas.drawPath(
      Path()
        ..moveTo(x, y - r)
        ..quadraticBezierTo(x, y, x + r, y)
        ..lineTo(size.width, y),
      p,
    );
  }

  @override
  bool shouldRepaint(_TrunkPainter old) =>
      old.color != color || old.last != last;
}
