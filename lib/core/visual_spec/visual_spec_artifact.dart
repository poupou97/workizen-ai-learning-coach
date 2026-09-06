/// ⭐ LANE E2 (round 5) — ARTEFACT: các `VisualSpec` được DỰNG SẴN NGOÀI GIỜ
/// CHẠY, đóng gói một tệp có phiên bản; lúc chạy app chỉ ĐỌC và VẼ.
///
/// §13 «precompute, don't call a model at runtime»: đường duy nhất để một
/// spec vào app là tệp này. Không có API nào ở đây nhận `String prompt`, và
/// `lib/core/visual_spec/**` không import gì ngoài `lesson_model` — muốn gọi
/// mô hình lúc chạy thì phải thêm import mới, việc mà test chặn.
///
/// `lessonKey` (`book#lessonNo`) sống Ở ĐÂY chứ không nằm trong `VisualSpec`:
/// tra cứu là việc của tầng nạp, rẽ nhánh theo bài là việc KHÔNG AI được làm.
library;

import 'dart:convert';

import 'visual_spec.dart';

class VisualSpecArtifact {
  const VisualSpecArtifact({
    required this.artifactVersion,
    required this.builtAt,
    required this.builder,
    required this.specs,
  });

  static const currentVersion = 'visual-spec-artifact-v1';

  final String artifactVersion;

  /// Ngày dựng (ISO-8601) — cho replay và cho «artefact này cũ hơn pack».
  final String builtAt;

  /// Ai dựng (`semantic-to-spec-v1`) — mã máy, để dựng lại y hệt.
  final String builder;

  /// `book#lessonNo` → spec. Một bài một spec (một hình chính + hình phụ).
  final Map<String, VisualSpec> specs;

  VisualSpec? forLesson(String lessonKey) => specs[lessonKey];

  int get lessonCount => specs.length;

  int get sectionCount {
    var n = 0;
    for (final s in specs.values) {
      n += s.sections.length;
    }
    return n;
  }

  /// Đếm theo HỌ hình — số liệu cho báo cáo, máy đếm không ước.
  Map<String, int> get sectionsByFamily {
    final m = <String, int>{};
    for (final s in specs.values) {
      for (final sec in s.sections) {
        m.update(sec.family, (n) => n + 1, ifAbsent: () => 1);
      }
    }
    return m;
  }

  /// Fail-closed: một spec hỏng ⇒ CẢ artefact bị từ chối. Nửa artefact là
  /// thứ nguy hiểm nhất — app sẽ im lặng thiếu hình mà không ai biết.
  static VisualSpecArtifact? fromJson(Object? v) {
    if (v is! Map) return null;
    final ver = v['artifactVersion'];
    final builtAt = v['builtAt'];
    final builder = v['builder'];
    if (ver != currentVersion || builtAt is! String || builder is! String) {
      return null;
    }
    final raw = v['specs'];
    if (raw is! Map) return null;
    final specs = <String, VisualSpec>{};
    for (final e in raw.entries) {
      final key = e.key;
      if (key is! String || key.isEmpty) return null;
      final spec = VisualSpec.fromJson(e.value);
      if (spec == null) return null;
      specs[key] = spec;
    }
    return VisualSpecArtifact(
      artifactVersion: ver as String,
      builtAt: builtAt,
      builder: builder,
      specs: specs,
    );
  }

  static VisualSpecArtifact? parse(String source) {
    try {
      return fromJson(jsonDecode(source));
    } on FormatException {
      return null;
    }
  }

  Map<String, Object?> toJson() => {
    'artifactVersion': artifactVersion,
    'builtAt': builtAt,
    'builder': builder,
    'specs': {for (final e in specs.entries) e.key: e.value.toJson()},
  };

  String encode() => const JsonEncoder.withIndent('  ').convert(toJson());
}
