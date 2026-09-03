/// WAL-140 — nối `assessFrame` (WAL-65) vào KHUNG NGẮM SỐNG.
///
/// Phần thuần Dart tách hẳn khỏi plugin camera để test được mà không cần
/// thiết bị: đổi khung preview thành [GrayFrame] + luật tiết nhịp. Màn hình
/// chỉ còn việc bơm khung vào và vẽ lời nhắc.
///
/// ⭐ NHẮC, KHÔNG CHẶN. Ngưỡng chất lượng hiện là GIẢ THUYẾT V1 (WAL-65 nói
/// rõ: hiệu chỉnh trên khung hình thật là residual). Khoá nút chụp theo một
/// ngưỡng chưa hiệu chỉnh thì có ngày SAM không cho một đứa trẻ chụp bài của
/// chính nó vì đèn nhà nó vàng. Nhắc trước, còn quyền bấm vẫn của trẻ.
library;

import '../../core/perception/precapture_quality.dart';

/// Lấy mẫu kênh Y (độ sáng) của khung YUV420 về một [GrayFrame] nhỏ.
///
/// Kênh Y CHÍNH LÀ ảnh xám — không cần đổi màu, chỉ cần lấy mẫu thưa. Làm
/// vậy vừa rẻ (chạy được trên Nokia 2018) vừa không bịa thêm dữ liệu.
///
/// [bytesPerRow] thường LỚN HƠN [width] (stride có đệm) — bỏ qua chuyện này
/// là ảnh xiên dần theo từng dòng, một lỗi trông như «máy ảnh hỏng».
GrayFrame downsampleLuma({
  required int width,
  required int height,
  required List<int> yPlane,
  required int bytesPerRow,
  int target = 96,
}) {
  assert(width > 0 && height > 0 && target > 1);
  final step = (width > height ? width : height) / target;
  final w = (width / step).floor().clamp(2, target);
  final h = (height / step).floor().clamp(2, target);
  final out = List<int>.filled(w * h, 0);
  for (var y = 0; y < h; y++) {
    final sy = (y * step).floor().clamp(0, height - 1);
    for (var x = 0; x < w; x++) {
      final sx = (x * step).floor().clamp(0, width - 1);
      final i = sy * bytesPerRow + sx;
      out[y * w + x] = i < yPlane.length ? yPlane[i] : 0;
    }
  }
  return GrayFrame(width: w, height: h, pixels: out);
}

/// Tiết nhịp + giữ kết quả mới nhất.
///
/// Preview bắn ~30 khung/giây; chấm hết là máy nóng và chữ nhảy loạn trước
/// mắt trẻ. Mỗi [interval] chấm một khung là đủ để lời nhắc theo kịp tay.
class PrecaptureAdvisor {
  PrecaptureAdvisor({this.interval = const Duration(milliseconds: 700)});

  final Duration interval;
  DateTime? _lastAt;
  CaptureAssessment? _latest;

  CaptureAssessment? get latest => _latest;

  /// Đã tới lúc chấm khung tiếp theo chưa.
  bool shouldAssess(DateTime now) =>
      _lastAt == null || now.difference(_lastAt!) >= interval;

  /// Chấm một khung và ghi lại. Trả `null` nếu chưa tới nhịp (bỏ khung).
  CaptureAssessment? offer(GrayFrame f, DateTime now,
      {QualityThresholds thresholds = const QualityThresholds()}) {
    if (!shouldAssess(now)) return null;
    _lastAt = now;
    return _latest = assessFrame(f, thresholds: thresholds);
  }

  /// Lời nhắc đang hiển thị. Chưa chấm được khung nào ⇒ câu hướng dẫn chung,
  /// KHÔNG phải một phán xét về ảnh mà máy chưa hề nhìn.
  String get message =>
      _latest?.guidance ?? 'Đưa MỘT bài vào khung — chữ rõ, đủ sáng nhé';

  /// Có đang nhắc sửa gì không (dùng để đổi màu viền khung ngắm).
  bool get needsFixing =>
      _latest != null && _latest!.verdict != CaptureVerdict.ok;
}
