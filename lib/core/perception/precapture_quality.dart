/// WAL-65 — Gate chất lượng TRƯỚC khi chụp: chặn ảnh xấu trước khi nó kịp
/// thành PerceptionHypothesis tồi.
///
/// Vì sao tồn tại: PHONE-SIM đo được ảnh suy giảm vừa phải làm recall
/// 5/5 → 0/5 và Vision BỊA biểu thức với conf≈1.00 — tức là gate SAU chụp
/// (confidence) vô dụng. Chặn phải nằm TRƯỚC: hướng dẫn trẻ chụp lại ngay
/// khi khung hình còn sống, không đợi OCR thất bại rồi mới xin lỗi.
///
/// Thuần Dart trên bytes grayscale — không plugin, không ML. Thiết bị chỉ
/// việc downscale khung preview về grayscale rồi gọi [assessFrame].
/// Ngưỡng là GIẢ THUYẾT V1 (có tên, injectable) — hiệu chỉnh khi có khung
/// hình thật từ thiết bị (residual ghi trong ticket).
library;

/// Một khung preview đã về grayscale 8-bit, row-major.
class GrayFrame {
  const GrayFrame({required this.width, required this.height, required this.pixels})
      : assert(pixels.length == width * height);
  final int width;
  final int height;
  final List<int> pixels; // 0..255
}

enum CaptureVerdict {
  ok,

  /// Thiếu sáng — «Con bật thêm đèn hoặc ra chỗ sáng hơn nhé».
  tooDark,

  /// Cháy sáng/loá — «Ảnh loá quá, con nghiêng vở đi một chút nhé».
  tooBright,

  /// Mờ/rung — «Con giữ máy yên hơn một chút nhé».
  tooBlurry,
}

/// Ngưỡng V1 — GIẢ THUYẾT, injectable, sẽ hiệu chỉnh bằng khung hình thật.
class QualityThresholds {
  const QualityThresholds({
    this.minMeanLuma = 60,
    this.maxMeanLuma = 215,
    this.minSharpness = 1500,
  });

  final double minMeanLuma;
  final double maxMeanLuma;

  /// Phương sai Laplacian tối thiểu — proxy nét/mờ kinh điển, tất định.
  /// 1500 hiệu chỉnh trên trang-chữ TỔNG HỢP: trang nét đo ≈29.000, cùng
  /// trang box-blur r=2 đo ≈430 — ngưỡng nằm giữa với biên rộng hai phía.
  /// ⚠️ Hiệu chỉnh trên khung hình THẬT là residual (thiết bị, WAL-84).
  final double minSharpness;
}

class CaptureAssessment {
  const CaptureAssessment({
    required this.verdict,
    required this.meanLuma,
    required this.sharpness,
  });
  final CaptureVerdict verdict;
  final double meanLuma;
  final double sharpness;

  /// Lời SAM cho từng verdict — cố định, ấm, KHÔNG đổ lỗi cho trẻ.
  String get guidance => switch (verdict) {
        CaptureVerdict.ok => 'Được rồi đó — chụp thôi!',
        CaptureVerdict.tooDark =>
          'Hơi tối — con bật thêm đèn hoặc ra chỗ sáng hơn giúp tớ nhé.',
        CaptureVerdict.tooBright =>
          'Ảnh bị loá — con nghiêng vở đi một chút cho đỡ bóng nhé.',
        CaptureVerdict.tooBlurry =>
          'Hơi nhoè — con giữ máy yên một nhịp rồi mình chụp nhé.',
      };
}

/// Đánh giá MỘT khung. Thứ tự kiểm cố ý: sáng trước, nét sau — ảnh tối thì
/// số đo nét không còn nghĩa (phương sai thấp vì thiếu sáng, không phải vì rung).
CaptureAssessment assessFrame(GrayFrame f,
    {QualityThresholds thresholds = const QualityThresholds()}) {
  var sum = 0;
  for (final p in f.pixels) {
    sum += p;
  }
  final mean = sum / f.pixels.length;

  if (mean < thresholds.minMeanLuma) {
    return CaptureAssessment(
        verdict: CaptureVerdict.tooDark, meanLuma: mean, sharpness: 0);
  }
  if (mean > thresholds.maxMeanLuma) {
    return CaptureAssessment(
        verdict: CaptureVerdict.tooBright, meanLuma: mean, sharpness: 0);
  }

  // Phương sai Laplacian 4-lân-cận — bỏ viền 1px cho gọn và tất định.
  var lapSum = 0.0, lapSqSum = 0.0;
  final n = (f.width - 2) * (f.height - 2);
  for (var y = 1; y < f.height - 1; y++) {
    for (var x = 1; x < f.width - 1; x++) {
      final i = y * f.width + x;
      final lap = 4 * f.pixels[i] -
          f.pixels[i - 1] -
          f.pixels[i + 1] -
          f.pixels[i - f.width] -
          f.pixels[i + f.width];
      lapSum += lap;
      lapSqSum += lap * lap;
    }
  }
  final lapMean = lapSum / n;
  final sharpness = lapSqSum / n - lapMean * lapMean;

  return CaptureAssessment(
    verdict: sharpness < thresholds.minSharpness
        ? CaptureVerdict.tooBlurry
        : CaptureVerdict.ok,
    meanLuma: mean,
    sharpness: sharpness,
  );
}
