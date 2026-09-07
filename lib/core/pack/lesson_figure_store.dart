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

  /// Nạp pack hình của một lớp: chép asset ra đĩa (sqlite cần đường dẫn tệp)
  /// rồi mở. Lớp chưa dựng pack ⇒ store RỖNG, không phải lỗi.
  ///
  /// Chép lại khi kích thước lệch: bản vá nội dung phải tới được máy ĐÃ CÀI —
  /// «xoá app data để lấy pack mới» không phải cơ chế cập nhật, nó xoá luôn hồ
  /// sơ học của trẻ (cùng bài học với `pack_sync`).
  static Future<LessonFigureStore> loadForGrade(int grade, String dir) async {
    final key = 'assets/pack/figures-g$grade.db';
    final path = '$dir/figures-g$grade.db';
    try {
      final data = await rootBundle.load(key);
      final bytes = data.buffer.asUint8List();
      final f = File(path);
      if (!f.existsSync() || f.lengthSync() != bytes.length) {
        final tmp = File('$path.tmp');
        await tmp.writeAsBytes(bytes, flush: true);
        await tmp.rename(path);
      }
    } catch (_) {
      if (!File(path).existsSync()) return empty();   // lớp này chưa có pack hình
    }
    return open(path);
  }
}
