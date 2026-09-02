/// WAL-116 — POC object model: chứa được 2 BÀI THẬT từ corpus.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/drawing/drawing_model.dart';

void main() {
  test('GEOMETRY: «Vẽ đoạn thẳng AB có độ dài 9 cm» (Toán 2 t1 tr.108 — '
      'unit thật) — ràng buộc kiểm được bằng số', () {
    const seg = GSegment(GPoint(0, 0, label: 'A'), GPoint(9, 0, label: 'B'),
        requiredLengthCm: 9);
    expect(seg.lengthCm, closeTo(9, 0.001));
    expect(seg.satisfiesLength, isTrue);
    const sai = GSegment(GPoint(0, 0), GPoint(8.5, 0), requiredLengthCm: 9);
    expect(sai.satisfiesLength, isFalse,
        reason: 'lệch 5mm > dung sai 1mm — engine kiểm được, không cần mắt');
    const tuDo = GSegment(GPoint(0, 0), GPoint(3, 4));
    expect(tuDo.lengthCm, closeTo(5, 0.001));
    expect(tuDo.satisfiesLength, isNull,
        reason: 'đề không yêu cầu độ dài ⇒ KHÔNG bịa tiêu chí (UNKNOWN ≠ SAI)');
  });

  test('TECHNICAL: «Vẽ phác thảo sản phẩm…» (Công nghệ — unit thật) — '
      'checklist cấu trúc, không chấm thẩm mỹ', () {
    const rong = TechnicalSketch(
        title: 'Phác thảo sản phẩm đồ dùng',
        layers: [TechLayer(name: 'phác thảo')]);
    expect(rong.missing, containsAll(['CHƯA_CÓ_NÉT_VẼ', 'CHƯA_GHI_KÍCH_THƯỚC']));
    const du = TechnicalSketch(
        title: 'Phác thảo sản phẩm',
        layers: [TechLayer(name: 'phác thảo', strokes: 12)],
        dimensions: ['dài 12 cm', 'rộng 8 cm']);
    expect(du.missing, isEmpty);
  });

  test('mode vocabulary: có unsupported — loại lạ KHÔNG bị ép vào mode gần', () {
    expect(DrawingMode.values, contains(DrawingMode.unsupported));
    expect(
        DrawingMode.values.map((m) => m.name).any((n) => n.contains('chat')),
        isFalse);
  });
}
