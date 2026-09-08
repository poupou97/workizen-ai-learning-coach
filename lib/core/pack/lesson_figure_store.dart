/// HÌNH CỦA BÀI — đọc từ pack theo LỚP.
///
/// Vì sao SQLite chứ không phải hàng nghìn tệp asset: đo được ~4,4 hình/bài trên
/// 2.589 bài ⇒ ~11.400 tệp. Flutter khai báo asset theo THƯ MỤC và không đệ quy,
/// nên từng ấy tệp vừa làm chậm build vừa dễ rơi mất im lặng (WAL-167 n89).
///
/// Vì sao TÁCH THEO LỚP: ~31 MB một lớp nhưng ~367 MB cả 12 lớp. App chỉ dùng
/// lớp của trẻ, nên tách theo lớp là đúng hình dạng bài toán chứ không phải mẹo
/// tiết kiệm — mở đúng một tệp, không gánh 11 lớp còn lại.
///
/// Không có pack của lớp ⇒ store RỖNG và bài vẫn đọc được phần chữ. Đọc là
/// trạng thái sản phẩm hợp lệ; thiếu hình không được làm hỏng cả bài.
library;

import 'dart:io';

import 'package:flutter/services.dart';
import 'package:sqlite3/sqlite3.dart';

class LessonFigureStore {
  LessonFigureStore._(this._db);

  final Database? _db;

  static LessonFigureStore empty() => LessonFigureStore._(null);

  /// Mở từ FILE đã nằm trên đĩa (caller lo chép asset ra). Lỗi ⇒ store rỗng.
  static LessonFigureStore open(String path) {
    try {
      final db = sqlite3.open(path, mode: OpenMode.readOnly);
      db.select('SELECT 1 FROM fig LIMIT 1');
      return LessonFigureStore._(db);
    } catch (_) {
      return LessonFigureStore._(null);
    }
  }

  bool get isEmpty => _db == null;

  /// Ảnh JPEG của một hình, `null` khi pack này không có nó.
  Uint8List? jpeg(String id) {
    final db = _db;
    if (db == null) return null;
    try {
      final rows = db.select('SELECT jpeg FROM fig WHERE id = ?', [id]);
      if (rows.isEmpty) return null;
      final v = rows.first['jpeg'];
      return v is Uint8List ? v : null;
    } catch (_) {
      return null;
    }
  }

  int get count {
    final db = _db;
    if (db == null) return 0;
    try {
      return db.select('SELECT COUNT(*) c FROM fig').first['c'] as int;
    } catch (_) {
      return 0;
    }
  }

  void close() => _db?.dispose();

  /// Nạp pack hình của một lớp — ƯU TIÊN PACK ĐÃ CÀI trên máy.
  ///
  /// App hỗ trợ lớp 1–12 nhưng trẻ chỉ dùng một lớp; gói cả 12 pack (332 MB)
  /// vào APK là bắt mọi máy mang 11 lớp không ai mở. Pack được cài lúc chạy
  /// (`GradePackInstaller`), nên đường đọc ở đây là:
  ///
  ///   pack ĐÃ CÀI  →  asset gói kèm (nếu bản build còn mang, giai đoạn chuyển
  ///                   tiếp)  →  RỖNG
  ///
  /// Rỗng KHÔNG phải lỗi: bài vẫn đọc được phần chữ. Read-only là trạng thái
  /// sản phẩm hợp lệ, và một lớp chưa tải pack không được làm hỏng bài đọc.
  static Future<LessonFigureStore> loadForGrade(int grade, String dir) async {
    final installed = File('$dir/figures-g$grade.db');
    if (installed.existsSync()) return open(installed.path);

    // Bản build còn gói sẵn pack ⇒ chép ra đĩa rồi mở (tương thích ngược).
    // Chép lại khi kích thước lệch: bản vá nội dung phải tới được máy ĐÃ CÀI —
    // «xoá app data để lấy pack mới» không phải cơ chế cập nhật, nó xoá luôn hồ
    // sơ học của trẻ (cùng bài học với `pack_sync`).
    final key = 'assets/pack/figures-g$grade.db';
    try {
      final data = await rootBundle.load(key);
      final bytes = data.buffer.asUint8List();
      final f = File('$dir/bundled-figures-g$grade.db');
      if (!f.existsSync() || f.lengthSync() != bytes.length) {
        final tmp = File('${f.path}.tmp');
        await tmp.writeAsBytes(bytes, flush: true);
        await tmp.rename(f.path);
      }
      return open(f.path);
    } catch (_) {
      return empty();          // lớp này chưa có pack — hợp lệ, không phải lỗi
    }
  }
}
