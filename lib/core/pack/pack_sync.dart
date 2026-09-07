/// ⭐⭐ VÒNG ĐỜI PACK — máy ĐÃ CÀI phải nhận được pack mới.
///
/// Điều kiện cũ `if (!f.existsSync())` chép ĐÚNG MỘT LẦN rồi thôi, nên mọi bản
/// vá nội dung về sau bị bỏ qua trong im lặng. «Xoá app data để lấy pack mới»
/// KHÔNG phải cơ chế cập nhật — nó xoá luôn hồ sơ học của trẻ.
///
/// Tách khỏi `main.dart` và tiêm loader để test gọi được KHÔNG cần pack thật:
/// `assets/pack/sam-stories.db` không nằm trong git, nên một test đọc nó sẽ
/// xanh ở máy dev và đỏ trên CI. Một cơ chế cập nhật mà không kiểm được thì
/// chỉ hỏng muộn hơn cơ chế nó thay thế.
library;

import 'dart:io';

import 'package:flutter/services.dart';

const packDbAsset = 'assets/pack/sam-stories.db';
const packIdAsset = 'assets/pack/sam-stories.version';

typedef PackBytesLoader = Future<Uint8List> Function(String key);
typedef PackIdLoader = Future<String> Function(String key);

Future<Uint8List> _defaultBytes(String key) async =>
    (await rootBundle.load(key)).buffer.asUint8List();

Future<String> _defaultId(String key) => rootBundle.loadString(key);

/// Danh tính pack đóng trong APK — `<lược đồ>:<băm nội dung>`.
///
/// Sidecar tí hon do chính bước build pack sinh ra, nên không lệch được với
/// tệp `.db`. Đọc nó rẻ hơn nạp cả 88KB mỗi lần mở app.
Future<String?> bundledPackId({PackIdLoader? loadId}) async {
  try {
    return (await (loadId ?? _defaultId)(packIdAsset)).trim();
  } catch (_) {
    return null; // bản build cũ chưa có sidecar
  }
}

/// Danh tính pack ĐANG nằm trên máy — ghi cạnh tệp sau khi chép xong.
String? installedPackId(String dbPath) {
  final m = File('$dbPath.version');
  if (!m.existsSync()) return null;
  try {
    final s = m.readAsStringSync().trim();
    return s.isEmpty ? null : s;
  } catch (_) {
    return null;
  }
}

/// Đưa pack trên máy về đúng bản đóng trong APK. Trả `true` nếu vừa thay.
///
/// Quy tắc:
///   · so DANH TÍNH, không so byte — rẻ, và nói được «mới hơn» nghĩa là gì
///   · ghi ra `.tmp` rồi RENAME đè. Rename là ĐIỂM CAM KẾT: hỏng nửa chừng thì
///     pack cũ còn nguyên, không bao giờ để lại một tệp cụt cho SQLite mở
///   · marker ghi SAU khi rename xong; marker hỏng chỉ khiến lần mở sau chép
///     lại — vô hại, không mất gì
///   · pack là NỘI DUNG phái sinh từ APK, KHÔNG phải dữ liệu học. Thay nó
///     không đụng tới hồ sơ trẻ, nên không cần và không được xoá app data
///   · thiếu sidecar (bản build cũ) ⇒ chỉ chép khi chưa có tệp; thà giữ pack cũ
///     còn hơn ghi đè mù
Future<bool> syncPack(
  String dbPath, {
  PackBytesLoader? loadBytes,
  PackIdLoader? loadId,
}) async {
  final f = File(dbPath);
  final bundled = await bundledPackId(loadId: loadId);
  final needsCopy =
      !f.existsSync() ||
      (bundled != null && bundled != installedPackId(dbPath));
  if (!needsCopy) return false;

  final bytes = await (loadBytes ?? _defaultBytes)(packDbAsset);
  await f.parent.create(recursive: true);
  final tmp = File('$dbPath.tmp');
  await tmp.writeAsBytes(bytes, flush: true);
  await tmp.rename(dbPath); // ← điểm cam kết

  final marker = File('$dbPath.version');
  if (bundled != null) {
    await marker.writeAsString(bundled, flush: true);
  } else if (marker.existsSync()) {
    // Không có danh tính để ghi ⇒ đừng để marker CŨ nói dối về tệp MỚI.
    await marker.delete();
  }
  return true;
}
