/// ⭐⭐ Lệnh 56 §P2 — MỖI THẺ BÀI HỌC PHẢI CÓ HÌNH, và hình ấy phải hợp lệ.
///
/// Founder: «Tôi KHÔNG thấy visual/background của bài học. Phải sửa.» Nhưng
/// §P2.3 đồng thời cấm: «KHÔNG dùng SGK crop bị D4 block làm decorative
/// background.»
///
/// ⭐ Hai câu ấy gặp nhau ở một sự thật đo được: `ContentLicence` hôm nay có
/// ĐÚNG MỘT giá trị — `internalResearchOnly`. Nghĩa là **mọi** bài đều bị D4
/// chặn cho mục đích trang trí, nên tầng hero KHÔNG BAO GIỜ sáng ở bản dựng
/// này. Nó vẫn được viết ra và vẫn đứng đầu chuỗi: ngày một bài có quyền phát
/// hành, thẻ tự nâng cấp mà không phải sửa gì.
///
/// Crop SGK vẫn hiện TRONG bài (màn Đọc) — đó là dùng nguồn để DẠY, khác với
/// mượn nó làm nền cho một thẻ trang trí.
///
/// Chuỗi rơi, đúng thứ tự §P2.3:
///
///   1. hero của chính bài  — chỉ khi licence cho phép trang trí
///   2. BÌA SÁCH của môn    — ảnh đã phát hành cùng app, trẻ nhận ra ngay
///   3. dải màu theo môn    — tất định từ tên môn, không bao giờ trắng trơn
///
/// Không tầng nào bịa ảnh, và không tầng nào mượn ảnh của bài/môn khác.
library;

import '../../core/lesson_model/content_trust.dart';
import '../../core/lesson_model/lesson_document.dart';

/// Nguồn hình của một thẻ bài học.
enum LessonVisualKind {
  /// Hình của chính bài, được phép dùng trang trí.
  hero,

  /// Bìa sách của môn — ảnh đã phát hành cùng app.
  cover,

  /// Không có ảnh nào hợp lệ ⇒ dải màu tất định theo môn.
  gradient,
}

class LessonVisual {
  const LessonVisual({required this.kind, this.asset, required this.seed});

  final LessonVisualKind kind;

  /// Đường dẫn asset — `null` với [LessonVisualKind.gradient].
  final String? asset;

  /// Số tất định suy từ TÊN MÔN — dùng chọn dải màu, và để hai môn khác nhau
  /// không bao giờ ra cùng một màu một cách tình cờ.
  final int seed;
}

/// Có được phép dùng hình của bài làm NỀN TRANG TRÍ không.
///
/// Hôm nay luôn `false` — xem ghi chú đầu tệp. Viết thành hàm riêng để chỗ
/// quyết định nằm ở MỘT nơi, và để test khoá được nó.
bool mayDecorateWithLessonImagery(LessonDocument doc) =>
    doc.licence != ContentLicence.internalResearchOnly;

/// Seed tất định từ tên môn.
int subjectSeed(String subject) {
  var h = 0;
  for (final c in subject.codeUnits) {
    h = (h * 31 + c) & 0x7fffffff;
  }
  return h;
}

/// Hình cho thẻ của [doc]. [coverAsset] là bìa sách của môn (đường dẫn trong
/// `assets/pack/`, ví dụ `covers/06-sgk-khoa-hoc-tu-nhien-6.webp`); `null` khi
/// pack không có bìa cho môn ấy.
LessonVisual lessonVisual(
  LessonDocument doc, {
  String? coverAsset,
  String? heroAsset,
}) {
  final seed = subjectSeed(doc.subject);
  if (heroAsset != null && mayDecorateWithLessonImagery(doc)) {
    return LessonVisual(
      kind: LessonVisualKind.hero,
      asset: heroAsset,
      seed: seed,
    );
  }
  if (coverAsset != null) {
    return LessonVisual(
      kind: LessonVisualKind.cover,
      asset: 'assets/pack/$coverAsset',
      seed: seed,
    );
  }
  return LessonVisual(kind: LessonVisualKind.gradient, seed: seed);
}
