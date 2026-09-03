/// WAL-140 — nối gate chất lượng vào khung ngắm: NHẮC, không chặn.
library;

import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/perception/precapture_quality.dart';
import 'package:learning_coach/features/camera/precapture_advisor.dart';

/// Khung YUV giả có STRIDE ĐỆM — đúng như máy thật trả về.
({List<int> plane, int stride}) _yPlane(
    int w, int h, int Function(int x, int y) luma,
    {int pad = 16}) {
  final stride = w + pad;
  final p = List<int>.filled(stride * h, 0);
  for (var y = 0; y < h; y++) {
    for (var x = 0; x < w; x++) {
      p[y * stride + x] = luma(x, y);
      }
    for (var x = w; x < stride; x++) {
      p[y * stride + x] = 255; // rác trong phần đệm — KHÔNG được lọt vào ảnh
    }
  }
  return (plane: p, stride: stride);
}

void main() {
  test('⭐ lấy mẫu TÔN TRỌNG stride — rác trong phần đệm không lọt vào ảnh',
      () {
    // Ảnh đen tuyền, phần đệm trắng. Nếu bỏ qua stride thì ảnh sẽ xiên dần
    // và nhiễm pixel 255 — lỗi trông y như «máy ảnh hỏng».
    final y = _yPlane(64, 48, (_, _) => 0);
    final f = downsampleLuma(
        width: 64, height: 48, yPlane: y.plane, bytesPerRow: y.stride,
        target: 16);
    expect(f.pixels.every((p) => p == 0), isTrue,
        reason: '⭐ đột biến dùng width thay bytesPerRow ⇒ đỏ');
    expect(f.width, lessThanOrEqualTo(16));
    expect(f.height, lessThanOrEqualTo(16));
    expect(f.pixels.length, f.width * f.height);
  });

  test('lấy mẫu giữ được độ sáng trung bình (không bịa dữ liệu)', () {
    final y = _yPlane(80, 60, (_, _) => 120);
    final f = downsampleLuma(
        width: 80, height: 60, yPlane: y.plane, bytesPerRow: y.stride);
    expect(f.pixels.every((p) => p == 120), isTrue);
    expect(assessFrame(f).verdict, isNot(CaptureVerdict.tooDark));
  });

  test('⭐ tiết nhịp: bắn 30 khung/giây nhưng CHỈ chấm theo nhịp', () {
    final a = PrecaptureAdvisor(interval: const Duration(milliseconds: 700));
    final y = _yPlane(40, 30, (_, _) => 10); // tối
    GrayFrame f() => downsampleLuma(
        width: 40, height: 30, yPlane: y.plane, bytesPerRow: y.stride);
    final t0 = DateTime(2026, 9, 3, 15);
    expect(a.offer(f(), t0), isNotNull, reason: 'khung đầu phải được chấm');
    expect(a.offer(f(), t0.add(const Duration(milliseconds: 100))), isNull,
        reason: '⭐ đột biến bỏ tiết nhịp ⇒ chấm mọi khung ⇒ đỏ');
    expect(a.offer(f(), t0.add(const Duration(milliseconds: 800))), isNotNull);
  });

  test('⭐ CHƯA chấm khung nào ⇒ KHÔNG phán xét ảnh chưa nhìn', () {
    final a = PrecaptureAdvisor();
    expect(a.latest, isNull);
    expect(a.needsFixing, isFalse,
        reason: '⭐ chưa nhìn mà đã bảo ảnh xấu ⇒ bịa');
    expect(a.message, contains('Đưa MỘT bài vào khung'));
  });

  test('ảnh tối ⇒ lời nhắc đúng việc cần làm, không đổ lỗi cho trẻ', () {
    final a = PrecaptureAdvisor();
    final y = _yPlane(40, 30, (_, _) => 15);
    a.offer(
        downsampleLuma(
            width: 40, height: 30, yPlane: y.plane, bytesPerRow: y.stride),
        DateTime(2026, 9, 3, 15));
    expect(a.latest!.verdict, CaptureVerdict.tooDark);
    expect(a.needsFixing, isTrue);
    expect(a.message, contains('bật thêm đèn'));
    // Không có chữ nào quy lỗi cho trẻ.
    for (final bad in ['sai', 'kém', 'dở', 'không biết']) {
      expect(a.message.toLowerCase().contains(bad), isFalse);
    }
  });

  test('⭐⭐ CẤU TRÚC: gate chất lượng KHÔNG được khoá nút chụp', () {
    // Ngưỡng WAL-65 còn là giả thuyết V1 (chưa hiệu chỉnh trên khung thật).
    // Khoá nút chụp theo ngưỡng chưa hiệu chỉnh ⇒ có ngày SAM không cho một
    // đứa trẻ chụp bài của chính nó vì đèn nhà nó vàng.
    final src = const String.fromEnvironment('x') +
        _read('lib/features/camera/capture_screen.dart');
    // Nút chụp gọi _shoot qua onTap; onTap KHÔNG được phụ thuộc chất lượng.
    expect(RegExp(r'onTap:\s*(_advisor|.*needsFixing)').hasMatch(src), isFalse,
        reason: '⭐⭐ chất lượng ảnh chặn nút chụp ⇒ đỏ (nhắc, không chặn)');
    expect(src.contains('_shoot'), isTrue);
  });
}

String _read(String p) => File(p).readAsStringSync();
