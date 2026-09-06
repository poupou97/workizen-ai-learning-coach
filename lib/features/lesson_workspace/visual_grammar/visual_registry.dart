/// ⭐ LANE E2 (round 5) — BẢNG ĐĂNG KÝ họ hình của app.
///
/// Thêm một họ hình vào sản phẩm = thêm MỘT mục ở đây. Không sửa lớp kín
/// trong `core/`, không sửa `switch` nào, không đụng vào renderer đang chạy.
/// Đó là toàn bộ khác biệt giữa «một danh sách hình» và «một ngôn ngữ hình».
///
/// §19: `process` và `sequence` DÙNG CHUNG một renderer. Hai họ tồn tại riêng
/// vì chúng nói hai điều khác nhau với trẻ — «làm theo thứ tự này» so với
/// «sách in các phần theo thứ tự này» — chứ KHÔNG phải vì cần hai widget.
library;

import 'renderers/ordered_steps_renderer.dart';
import 'visual_family_renderer.dart';

/// Tên họ hình dùng chung giữa bộ biên dịch và bảng đăng ký.
class VisualGrammarFamily {
  const VisualGrammarFamily._();

  /// Quy trình PHẢI làm theo thứ tự (thí nghiệm, cách làm).
  static const process = 'process';

  /// Chuỗi phần sách IN theo thứ tự (mục 1 → 2 → 3). Yếu hơn `process`:
  /// nói về cách sách trình bày, không nói «phải làm theo thứ tự này».
  static const sequence = 'sequence';
}

const _orderedSteps = OrderedStepsRenderer();

/// Bảng của app. Test dùng bảng RIÊNG để kiểm đường fail-closed.
const defaultVisualRegistry = VisualRendererRegistry([
  VisualFamilyBinding(
    family: VisualGrammarFamily.process,
    childShapeLabel: 'Sơ đồ các bước',
    icon: '🔁',
    renderer: _orderedSteps,
  ),
  VisualFamilyBinding(
    family: VisualGrammarFamily.sequence,
    childShapeLabel: 'Các phần theo thứ tự sách',
    icon: '🔢',
    renderer: _orderedSteps,
  ),
]);
