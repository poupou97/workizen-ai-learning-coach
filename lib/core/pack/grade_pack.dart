/// CÀI PACK HÌNH THEO LỚP — tầng nhỏ nhất, không đóng cứng nhà cung cấp nào.
///
/// App hỗ trợ lớp 1–12 nhưng một đứa trẻ chỉ dùng MỘT lớp. Gói cả 12 pack hình
/// (332 MB) vào APK là bắt mọi máy mang 11 lớp không ai mở. Ở đây pack được cài
/// lúc chạy, từng lớp một.
///
/// ⭐ [PackSource] là chỗ DUY NHẤT biết pack đến từ đâu. Domain không biết —
/// nên đổi từ thư mục trên máy sang một endpoint thật sau này là thay một lớp
/// cài, không phải sửa logic bài học. Chưa chọn nhà cung cấp nào.
///
/// ⭐ NGUYÊN TỬ. Ghi vào `.part`, kiểm băm, RỒI mới `rename` vào chỗ thật.
/// `rename` trong cùng thư mục là nguyên tử ở mọi hệ tệp app dùng, nên không có
/// khoảnh khắc nào một nửa pack nằm ở đường dẫn mà `LessonFigureStore` sẽ mở.
/// Nửa pack mà vẫn nạp thì trẻ mở bài ra thấy ảnh vỡ và không ai biết vì sao.
///
/// ⭐ FAIL CLOSED. Băm sai / tải hỏng / chưa có pack ⇒ KHÔNG kích hoạt, giữ
/// nguyên bản đang dùng, và bài vẫn đọc được phần chữ. Read-only là trạng thái
/// sản phẩm hợp lệ; một pack hỏng không được phép làm hỏng cả bài đọc.
///
/// ⭐ KHÔNG ĐỘNG VÀO DỮ LIỆU HỌC. Chỉ ghi/xoá trong thư mục pack của chính nó.
library;

import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:crypto/crypto.dart';

/// Manifest do bước dựng pack sinh ra — máy cài kiểm được TRƯỚC khi kích hoạt.
class GradePackManifest {
  const GradePackManifest(
      {required this.grade,
      required this.file,
      required this.version,
      required this.size,
      required this.sha256});

  final int grade;
  final String file;

  /// `g6-90d3de03b0a4` — đổi khi nội dung đổi, để sau này biết có bản mới.
  final String version;
  final int size;
  final String sha256;

  static GradePackManifest? parse(String raw) {
    final Object? j;
    try {
      j = jsonDecode(raw);
    } catch (_) {
      return null;
    }
    if (j is! Map) return null;
    final g = j['grade'], f = j['file'], v = j['version'];
    final s = j['size'], h = j['sha256'];
    if (g is! int || f is! String || v is! String || s is! int || h is! String) {
      return null;
    }
    if (g < 1 || g > 12 || s <= 0 || h.length != 64) return null;
    // Tên tệp phải là TÊN, không phải đường dẫn: một manifest nói `../../x` sẽ
    // ghi ra ngoài thư mục pack.
    if (f.contains('/') || f.contains('\\') || f == '.' || f == '..') return null;
    return GradePackManifest(
        grade: g, file: f, version: v, size: s, sha256: h.toLowerCase());
  }

  Map<String, Object?> toJson() => {
        'grade': grade, 'file': file, 'version': version,
        'size': size, 'sha256': sha256,
      };
}

/// Nơi pack đến từ. Cài từ thư mục trên máy hôm nay; một endpoint thật sau này
/// chỉ là một lớp khác ở đây.
abstract class PackSource {
  Future<GradePackManifest?> manifest(int grade);
  Future<Uint8List?> bytes(GradePackManifest m);
}

/// Nguồn là một THƯ MỤC trên máy (adb push, thẻ nhớ, thư mục tải về).
/// Không mạng, không nhà cung cấp, không chi phí — đủ để chứng minh đường cài.
class DirectoryPackSource implements PackSource {
  const DirectoryPackSource(this.dir);
  final String dir;

  @override
  Future<GradePackManifest?> manifest(int grade) async {
    final f = File('$dir/figures-g$grade.manifest.json');
    if (!f.existsSync()) return null;
    try {
      return GradePackManifest.parse(await f.readAsString());
    } catch (_) {
      return null;
    }
  }

  @override
  Future<Uint8List?> bytes(GradePackManifest m) async {
    final f = File('$dir/${m.file}');
    if (!f.existsSync()) return null;
    try {
      return await f.readAsBytes();
    } catch (_) {
      return null;
    }
  }
}

enum InstallResult {
  /// Đã có sẵn đúng phiên bản ấy — không tải lại.
  alreadyInstalled,
  installed,

  /// Nguồn không có pack cho lớp này. Không phải lỗi: bài vẫn đọc được chữ.
  notAvailable,

  /// Tải/đọc hỏng — giữ nguyên bản đang dùng.
  fetchFailed,

  /// Băm hoặc kích thước không khớp manifest ⇒ KHÔNG kích hoạt.
  verifyFailed,
  writeFailed,
}

class GradePackInstaller {
  const GradePackInstaller({required this.source, required this.dir});

  final PackSource source;

  /// Thư mục pack của app. Chỉ đọc/ghi ở đây — dữ liệu học nằm chỗ khác.
  final String dir;

  String packPath(int grade) => '$dir/figures-g$grade.db';
  String _statePath(int grade) => '$dir/figures-g$grade.installed.json';

  /// Phiên bản pack ĐANG nằm trên máy, `null` nếu chưa có.
  Future<String?> installedVersion(int grade) async {
    final f = File(_statePath(grade));
    if (!f.existsSync() || !File(packPath(grade)).existsSync()) return null;
    try {
      final j = jsonDecode(await f.readAsString());
      return j is Map && j['version'] is String ? j['version'] as String : null;
    } catch (_) {
      return null;
    }
  }

  Future<InstallResult> install(int grade) async {
    final m = await source.manifest(grade);
    if (m == null || m.grade != grade) return InstallResult.notAvailable;
    if (await installedVersion(grade) == m.version) {
      return InstallResult.alreadyInstalled;
    }
    final data = await source.bytes(m);
    if (data == null) return InstallResult.fetchFailed;

    // KIỂM TRƯỚC KHI GHI VÀO CHỖ THẬT. Kích thước rẻ, băm chắc — làm cả hai:
    // một tệp cụt vẫn có thể trùng vài byte đầu, và một tệp đúng độ dài vẫn có
    // thể hỏng ruột.
    if (data.length != m.size) return InstallResult.verifyFailed;
    if (sha256.convert(data).toString() != m.sha256) {
      return InstallResult.verifyFailed;
    }

    try {
      Directory(dir).createSync(recursive: true);
      final part = File('${packPath(grade)}.part');
      await part.writeAsBytes(data, flush: true);
      await part.rename(packPath(grade));   // nguyên tử: không có nửa pack
      await File(_statePath(grade))
          .writeAsString(jsonEncode(m.toJson()), flush: true);
      return InstallResult.installed;
    } catch (_) {
      try {
        final part = File('${packPath(grade)}.part');
        if (part.existsSync()) part.deleteSync();
      } catch (_) {}
      return InstallResult.writeFailed;
    }
  }
}

/// Nơi pack được ĐẶT VÀO máy trước khi cài — hôm nay là một thư mục, vì Founder
/// chọn chứng minh đường cài trước khi chọn nhà cung cấp nào.
///
/// `adb push figures-g6.db figures-g6.manifest.json <đường dẫn này>/`
///
/// Không dùng thư mục dữ liệu học: cài pack không được đụng tới hồ sơ của trẻ.
String gradePackStagingDir(String documentsPath) =>
    '$documentsPath/hoc-cung-sam/incoming';
