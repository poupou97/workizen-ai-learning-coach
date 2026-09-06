/// ⭐ LANE E2 (round 5) — HỢP ĐỒNG RENDERER: một renderer chỉ nhận
/// `VisualSection`, không nhận bài.
///
/// Vì sao hợp đồng phải hẹp đến thế: hôm nay `visual_view.dart` chọn hình
/// bằng `switch` VÉT CẠN trên `sealed class SemanticData`. Thêm một họ hình
/// = sửa lớp kín trong `core/` + bốn `switch` ở ba file. Đó không phải một
/// ngôn ngữ, đó là một danh sách đóng. Ở đây họ hình là CHUỖI và renderer
/// ĐĂNG KÝ vào một registry — thêm họ = thêm một dòng đăng ký.
///
/// Ba điều renderer KHÔNG được phép làm, và không thể làm vì kiểu:
/// 1. **Biết mình đang vẽ bài nào.** `VisualRenderContext` không có `book`,
///    `lessonNo`, `LessonDocument` — nên `if (lessonId == …)` không viết ra
///    được. Test `no_lesson_branching_test.dart` quét cả thư mục.
/// 2. **Suy ra tri thức.** Không có chỗ nào nhận chữ tự do; mọi nhãn đã nằm
///    sẵn trong spec cùng nguồn của nó.
/// 3. **Vẽ đại khi không hiểu.** Họ hình chưa có renderer, hoặc dữ liệu sai
///    hình dạng ⇒ `unsupportedReason` trả lý do và host nói thật bằng lời trẻ.
library;

import 'package:flutter/widgets.dart';

import '../../../core/visual_spec/visual_spec.dart';

/// Mở «Sách viết gì ở đây» cho một phần tử — host cài, renderer chỉ gọi.
typedef OpenSourceCallback = void Function(ProvenanceRef ref);

/// Đổi id block (MÃ MÁY) thành dòng trang trẻ đọc («SGK KHTN 6 · trang 62»).
/// Renderer KHÔNG BAO GIỜ hiện id; nó chỉ có hàm này.
typedef PageLabelLookup = String Function(String blockId);

/// ⭐⭐ RÀO CHẮN DANH TÍNH — thứ mà một test theo TÊN TRƯỜNG không bắt được.
///
/// `VisualSpec` không có trường `book` / `lessonNo` / `slotKey`, và test đã
/// khoá điều đó. Nhưng danh tính vẫn đi lọt qua GIÁ TRỊ: `blockIds` mang
/// `06-sgk-khoa-hoc-tu-nhien-6:p062:…`. Một renderer chỉ cần
/// `id.startsWith('06-sgk-khoa-hoc-tu-nhien-6')` là rẽ nhánh theo bài được,
/// trong khi mọi rào theo tên trường vẫn xanh. Bảo đảm khi ấy chỉ là DANH
/// NGHĨA — nó mạnh đúng bằng cái kênh hẹp nhất còn hở.
///
/// Nên tại RANH GIỚI VẼ, mọi `blockIds` bị thay bằng thẻ vô nghĩa (`h0`,
/// `h1`…). Renderer cầm thẻ; chỉ `VisualRenderContext` giữ bảng thẻ → nguồn
/// thật và mới đổi ngược được. Không phải renderer *không nên* đọc danh tính
/// — nó KHÔNG CÒN GÌ ĐỂ ĐỌC.
///
/// Artefact trên đĩa vẫn giữ id block THẬT: chuỗi nguồn phải kiểm lại được.
/// Chỉ bản mà renderer nhìn thấy mới bị che.
VisualSection redactIdentityForRender(
  VisualSection section,
  Map<String, ProvenanceRef> handleToRef,
) {
  ProvenanceRef hide(ProvenanceRef ref) {
    final handle = 'h${handleToRef.length}';
    handleToRef[handle] = ref;
    return ProvenanceRef(
      blockIds: [handle],
      // Tên luật, độ tin, khoảng ký tự: đã kiểm — KHÔNG mang danh tính bài.
      derivationRule: ref.derivationRule,
      trust: ref.trust,
      claimId: ref.claimId,
      charSpan: ref.charSpan,
    );
  }

  return VisualSection(
    id: section.id,
    family: section.family,
    title: section.title,
    titleProvenance: hide(section.titleProvenance),
    nodes: [
      for (final n in section.nodes)
        VisualNode(
          id: n.id,
          label: n.label,
          detail: n.detail,
          badge: n.badge,
          status: n.status,
          provenance: hide(n.provenance),
          confidence: n.confidence,
        ),
    ],
    edges: [
      for (final e in section.edges)
        VisualEdge(
          fromId: e.fromId,
          toId: e.toId,
          label: e.label,
          kind: e.kind,
          status: e.status,
          provenance: hide(e.provenance),
        ),
    ],
    groups: [
      for (final g in section.groups)
        VisualGroup(
          id: g.id,
          label: g.label,
          nodeIds: g.nodeIds,
          axis: g.axis,
          provenance: g.provenance == null ? null : hide(g.provenance!),
        ),
    ],
    ordering: section.ordering,
    emphasis: section.emphasis,
    trust: section.trust,
    childSummary: section.childSummary,
  );
}

class VisualRenderContext {
  factory VisualRenderContext({
    required VisualSection section,
    required PageLabelLookup pageLabel,
    required OpenSourceCallback onOpenSource,
  }) {
    final handles = <String, ProvenanceRef>{};
    return VisualRenderContext._(
      section: redactIdentityForRender(section, handles),
      pageLabel: pageLabel,
      onOpenSource: onOpenSource,
      handleToRef: handles,
    );
  }

  const VisualRenderContext._({
    required this.section,
    required this.pageLabel,
    required this._onOpenSource,
    required this._handleToRef,
  });


  /// Bản ĐÃ CHE — mọi `blockIds` là thẻ vô nghĩa.
  final VisualSection section;
  final PageLabelLookup pageLabel;
  final OpenSourceCallback _onOpenSource;
  final Map<String, ProvenanceRef> _handleToRef;

  ProvenanceRef _real(ProvenanceRef redacted) =>
      _handleToRef[redacted.primaryBlockId] ?? redacted;

  /// «SGK KHTN 6 · trang 62» — host đổi thẻ thành lời trẻ.
  String pageOf(ProvenanceRef ref) => pageLabel(_real(ref).primaryBlockId);

  /// Mở «Sách viết gì ở đây». Renderer đưa thẻ; context đưa nguồn thật.
  void openSource(ProvenanceRef ref) => _onOpenSource(_real(ref));
}

abstract class VisualFamilyRenderer {
  const VisualFamilyRenderer();

  /// `null` ⇒ dựng được. Chuỗi ⇒ MÃ lý do (máy đọc, để đếm), host dịch sang
  /// lời trẻ. Kiểm HÌNH DẠNG DỮ LIỆU, không kiểm danh tính bài.
  String? unsupportedReason(VisualSection section);

  Widget build(BuildContext context, VisualRenderContext ctx);
}

/// Một họ hình gắn với renderer + chữ trẻ đọc cho họ ấy.
class VisualFamilyBinding {
  const VisualFamilyBinding({
    required this.family,
    required this.childShapeLabel,
    required this.icon,
    required this.renderer,
  });

  final String family;

  /// Tên hình trẻ đọc trên tab — KHÔNG phải tên họ máy.
  final String childShapeLabel;
  final String icon;
  final VisualFamilyRenderer renderer;
}

/// Bảng đăng ký MỞ. `defaults` là bảng của app; test dựng bảng riêng để kiểm
/// đường fail-closed mà không phải sửa app.
class VisualRendererRegistry {
  const VisualRendererRegistry(this.bindings);

  final List<VisualFamilyBinding> bindings;

  VisualFamilyBinding? bindingFor(String family) {
    for (final b in bindings) {
      if (b.family == family) return b;
    }
    return null;
  }

  bool supports(String family) => bindingFor(family) != null;

  Set<String> get families => {for (final b in bindings) b.family};
}
