/// ⭐ LANE E2 (round 5) §19 — RENDERER DÙNG LẠI ĐƯỢC cho MỌI chuỗi có thứ tự.
///
/// MỘT renderer này phục vụ hai họ hình và nhiều môn:
///
/// | họ        | môn đã chứng minh                | luật sinh                        |
/// |-----------|----------------------------------|----------------------------------|
/// | `process` | KHTN 6 — quy trình tách chất     | `tsl-enumerated-steps-v1`        |
/// | `sequence`| Vật lí 10 — các bước thí nghiệm  | `numbered-section-sequence-v1`   |
/// | `sequence`| Ngữ văn 9 — các bước nói và nghe | `numbered-section-sequence-v1`   |
///
/// Không có dòng nào trong file này biết môn nào, bài nào, sách nào. Nó nhận
/// `VisualSection` — nút có thứ tự + cạnh — và vẽ. Đổi môn KHÔNG đổi mã.
///
/// CỐ Ý CHƯA TRAU CHUỐT (chỉ thị Founder): việc phải chứng minh trước là
/// **dùng lại ngữ nghĩa + có nguồn**, không phải hình đẹp. Không hoạt ảnh,
/// không bố cục thông minh; mỗi bước một hàng, mũi tên là một nét.
library;

import 'package:flutter/material.dart';

import '../../../../app/theme/wal_tokens.dart';
import '../../../../core/visual_spec/visual_spec.dart';
import '../visual_family_renderer.dart';

class OrderedStepsRenderer extends VisualFamilyRenderer {
  const OrderedStepsRenderer();

  static const rootKey = Key('visual-grammar-ordered-steps');
  static Key stepKey(String nodeId) => Key('ordered-step-$nodeId');
  static Key inferredNoteKey(String nodeId) => Key('ordered-inferred-$nodeId');

  /// Cạnh mà renderer này hiểu. Cạnh khác kiểu ⇒ TỪ CHỐI, không vẽ bừa.
  static const _kinds = {EdgeKind.sequence, EdgeKind.precedes};

  @override
  String? unsupportedReason(VisualSection section) {
    if (section.nodes.length < 2) return 'need_two_nodes';
    for (final e in section.edges) {
      if (!_kinds.contains(e.kind)) return 'edge_kind:${e.kind.name}';
    }
    // Chuỗi phải nói được thứ tự: hoặc có `ordering`, hoặc có cạnh nối.
    if (section.ordering.isEmpty && section.edges.isEmpty) {
      return 'no_order_evidence';
    }
    return null;
  }

  @override
  Widget build(BuildContext context, VisualRenderContext ctx) {
    final nodes = ctx.section.orderedNodes;
    return Column(
      key: rootKey,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        for (var i = 0; i < nodes.length; i++) ...[
          _step(ctx, nodes[i], i + 1),
          if (i < nodes.length - 1) _connector(ctx.section, nodes[i].id),
        ],
      ],
    );
  }

  /// Mũi tên giữa hai bước. Cạnh SUY DIỄN ⇒ nét đứt + nói ra bằng lời trẻ.
  Widget _connector(VisualSection section, String fromId) {
    final edge = section.edgesFrom(fromId).firstOrNull;
    final inferred = edge?.isInferred ?? false;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          const SizedBox(width: 18),
          Icon(
            inferred ? Icons.more_vert : Icons.arrow_downward,
            size: 18,
            color: inferred ? WalColors.inkSoft : WalColors.primary500,
          ),
          if (edge?.label != null) ...[
            const SizedBox(width: WalSpacing.xs),
            Expanded(
              child: Text(
                edge!.label!,
                style: const TextStyle(fontSize: 12, color: WalColors.inkSoft),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _step(VisualRenderContext ctx, VisualNode n, int position) {
    // Số hiển thị: nhãn nhỏ của SÁCH nếu có, không thì vị trí SAM xếp.
    final badge = n.badge ?? '$position';
    final page = ctx.pageOf(n.provenance);
    return InkWell(
      key: stepKey(n.id),
      onTap: () => ctx.openSource(n.provenance),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 4),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 36,
              height: 36,
              alignment: Alignment.center,
              decoration: BoxDecoration(
                color: n.isWithheld ? WalColors.inkSoft : WalColors.primary500,
                shape: BoxShape.circle,
              ),
              child: Text(
                badge,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  fontSize: 13,
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
                  color: n.isWithheld ? WalColors.surface : Colors.white,
                  borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      // Chỗ trống THẬT: không có chữ thì nói không có chữ và
                      // chỉ trang, không tóm tắt hộ, không đoán.
                      n.isWithheld
                          ? 'Chỗ này SAM chưa đọc được — con xem trong sách '
                                '($page).'
                          : n.label!,
                      style: TextStyle(
                        fontSize: WalType.body,
                        height: 1.4,
                        color: n.isWithheld
                            ? WalColors.inkSoft
                            : WalColors.ink,
                      ),
                    ),
                    if (n.detail != null)
                      Padding(
                        padding: const EdgeInsets.only(top: 4),
                        child: Text(
                          n.detail!,
                          style: const TextStyle(
                            fontSize: WalType.secondary,
                            color: WalColors.ink,
                            height: 1.35,
                          ),
                        ),
                      ),
                    // ⭐ Trạng thái suy luận nói THẲNG cho trẻ: nhãn không
                    // phải chữ sách thì trẻ phải biết trước khi tin.
                    if (n.status == InferenceStatus.inferred)
                      Padding(
                        key: inferredNoteKey(n.id),
                        padding: const EdgeInsets.only(top: 4),
                        child: Text(
                          InferenceStatus.inferred.childNote!,
                          style: const TextStyle(
                            fontSize: 12,
                            color: WalColors.inkSoft,
                          ),
                        ),
                      ),
                    Padding(
                      padding: const EdgeInsets.only(top: 4),
                      child: Text(
                        page,
                        style: const TextStyle(
                          fontSize: 12,
                          color: WalColors.primaryText,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
