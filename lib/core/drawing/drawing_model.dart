/// WAL-116 — POC OBJECT MODEL cho 2 loại «vẽ» phổ biến nhất đo được từ corpus
/// (GEOMETRY 19-20% · TECHNICAL 28%). ĐÂY LÀ OBJECT MODEL, KHÔNG PHẢI RENDER
/// ENGINE (out-of-scope theo ticket — không build Smart Canvas trước khi
/// classification xong).
///
/// Verdict kiến trúc (từ distribution): SHARED ENGINE + SPECIALIZED MODES —
/// stroke/layer/undo dùng chung; ràng buộc (đo độ dài, snap, dimension) là
/// của TỪNG MODE. Không ONE-SURFACE (GEOMETRY cần chính-xác-hình-học,
/// TECHNICAL cần lớp + kích thước, ARTISTIC tự do — ba hợp đồng khác nhau).
library;

/// Chế độ vẽ — theo taxonomy ĐO ĐƯỢC (không bịa mode chưa có evidence).
enum DrawingMode {
  geometry,
  technical,
  chart,
  graph,
  diagram,
  artistic,
  unsupported, // loại chưa classify được ⇒ nói thật, không ép vào mode gần
}

/// ---- GEOMETRY (Toán: «Vẽ đoạn thẳng AB có độ dài 9 cm») ------------------

class GPoint {
  const GPoint(this.x, this.y, {this.label});
  final double x, y;
  final String? label;
}

/// Nguyên thuỷ hình học CÓ RÀNG BUỘC — độ dài yêu cầu là một phần của ĐỀ,
/// engine kiểm được «vẽ đúng» bằng số (không cần chấm bằng mắt).
class GSegment {
  const GSegment(this.a, this.b, {this.requiredLengthCm});
  final GPoint a, b;
  final double? requiredLengthCm;

  double get lengthCm {
    final dx = a.x - b.x, dy = a.y - b.y;
    // đơn vị model = cm (POC): toạ độ đã ở cm.
    return _sqrt(dx * dx + dy * dy);
  }

  /// `null` khi đề KHÔNG yêu cầu độ dài (UNKNOWN ≠ SAI — không bịa tiêu chí).
  bool? get satisfiesLength => requiredLengthCm == null
      ? null
      : (lengthCm - requiredLengthCm!).abs() <= 0.1; // dung sai 1 mm
}

double _sqrt(double v) {
  // Newton — tránh import dart:math trong POC model thuần.
  if (v <= 0) return 0;
  var x = v;
  for (var i = 0; i < 20; i++) {
    x = (x + v / x) / 2;
  }
  return x;
}

/// ---- TECHNICAL (Công nghệ/Mĩ thuật: «Vẽ phác thảo sản phẩm…») ------------

/// Bản vẽ kĩ thuật = LỚP + chú thích kích thước; tiêu chí là CHECKLIST
/// (đủ hình chiếu/đủ kích thước) — không phải đúng/sai một con số.
class TechLayer {
  const TechLayer({required this.name, this.strokes = 0});
  final String name; // vd 'phác thảo', 'kích thước', 'ghi chú'
  final int strokes; // POC: đếm nét — đủ cho object model
}

class TechnicalSketch {
  const TechnicalSketch(
      {required this.title, required this.layers, this.dimensions = const []});
  final String title;
  final List<TechLayer> layers;
  final List<String> dimensions; // chú thích kích thước («dài 12 cm»…)

  /// Checklist tối thiểu của một bản vẽ kĩ thuật nộp được — POC đo cấu trúc,
  /// KHÔNG chấm thẩm mỹ.
  List<String> get missing => [
        if (layers.every((l) => l.strokes == 0)) 'CHƯA_CÓ_NÉT_VẼ',
        if (dimensions.isEmpty) 'CHƯA_GHI_KÍCH_THƯỚC',
      ];
}
