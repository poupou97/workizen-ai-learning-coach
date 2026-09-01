/// WAL-65 — gate chất lượng pre-capture trên khung tổng hợp TẤT ĐỊNH.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/perception/precapture_quality.dart';

/// Trang giấy có chữ: nền sáng + vạch "mực" tối đều đặn — nét, đủ sáng.
GrayFrame page({int w = 64, int h = 64, int paper = 200, int ink = 40}) =>
    GrayFrame(width: w, height: h, pixels: [
      for (var y = 0; y < h; y++)
        for (var x = 0; x < w; x++)
          (y % 8 < 2 && x % 3 != 0) ? ink : paper, // dòng chữ mỗi 8px
    ]);

/// Box-blur bán kính 2 — mô phỏng rung tay, tất định.
GrayFrame blur(GrayFrame f) {
  final out = List<int>.filled(f.pixels.length, 0);
  for (var y = 0; y < f.height; y++) {
    for (var x = 0; x < f.width; x++) {
      var s = 0, c = 0;
      for (var dy = -2; dy <= 2; dy++) {
        for (var dx = -2; dx <= 2; dx++) {
          final yy = y + dy, xx = x + dx;
          if (yy < 0 || yy >= f.height || xx < 0 || xx >= f.width) continue;
          s += f.pixels[yy * f.width + xx];
          c++;
        }
      }
      out[y * f.width + x] = s ~/ c;
    }
  }
  return GrayFrame(width: f.width, height: f.height, pixels: out);
}

GrayFrame dim(GrayFrame f, double k) => GrayFrame(
    width: f.width,
    height: f.height,
    pixels: [for (final p in f.pixels) (p * k).round().clamp(0, 255)]);

void main() {
  test('trang chữ nét, đủ sáng ⇒ ok', () {
    final a = assessFrame(page());
    expect(a.verdict, CaptureVerdict.ok,
        reason: 'luma ${a.meanLuma}, nét ${a.sharpness}');
  });

  test('cùng trang ấy box-blur ⇒ tooBlurry — gate phân biệt được nét/mờ', () {
    final sharp = assessFrame(page());
    final blurred = assessFrame(blur(page()));
    expect(blurred.sharpness, lessThan(sharp.sharpness / 3),
        reason: 'blur phải kéo sập phương sai Laplacian');
    expect(blurred.verdict, CaptureVerdict.tooBlurry);
  });

  test('trang tối (đèn yếu) ⇒ tooDark, KHÔNG bị chẩn nhầm thành mờ', () {
    final a = assessFrame(dim(page(), 0.2));
    expect(a.verdict, CaptureVerdict.tooDark,
        reason: 'ảnh tối thì số đo nét vô nghĩa — phải chẩn thiếu sáng trước');
  });

  test('trang cháy sáng ⇒ tooBright', () {
    final a = assessFrame(page(paper: 250, ink: 235));
    expect(a.verdict, CaptureVerdict.tooBright);
  });

  test('lời SAM: mọi verdict có hướng dẫn, không lời nào đổ lỗi cho trẻ', () {
    for (final v in CaptureVerdict.values) {
      final a = CaptureAssessment(verdict: v, meanLuma: 100, sharpness: 100);
      expect(a.guidance, isNotEmpty);
      for (final blame in ['sai', 'kém', 'tệ', 'hỏng', 'lỗi của con']) {
        expect(a.guidance.toLowerCase().contains(blame), isFalse,
            reason: 'đổ lỗi bị cấm: "$blame" trong "${a.guidance}"');
      }
    }
  });
}
