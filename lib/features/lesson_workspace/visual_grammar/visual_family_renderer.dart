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

class VisualRenderContext {
  const VisualRenderContext({
    required this.section,
    required this.pageLabel,
    required this.onOpenSource,
  });

  final VisualSection section;
  final PageLabelLookup pageLabel;
  final OpenSourceCallback onOpenSource;

  String pageOf(ProvenanceRef ref) => pageLabel(ref.primaryBlockId);
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
