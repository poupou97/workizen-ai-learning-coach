/// LANE C (round 5, §11) — CỔNG NGUYÊN VĂN (`verbatim gate`) cho hai luật
/// PROPOSED của Lịch sử.
///
/// Vòng 4 đã BÁC BỎ giả định A26: hai bộ OCR đồng ý (`text_sim` = 100) KHÔNG
/// có nghĩa chữ đúng như bản in — cùng một lỗi dấu có thể xuất hiện ở cả hai.
/// Vì vậy cờ TRUSTED của pipeline không còn đủ để TRÍCH một block cho trẻ đọc:
/// phải có một tín hiệu ĐỘC LẬP với hai bộ ấy. Hôm nay tín hiệu đó là một
/// lượt ĐỌC BẢN IN của người (ledger ở `docs/research/lane-c/data/…`), được
/// `tool/research/lane_c/history_rules.py` ghi vào tài liệu tại
/// `provenance.historyRules.verbatimGate`.
///
/// Tệp này là lớp CHẶN THỨ HAI, phía Dart: dù dữ liệu tới từ đâu, mốc hay
/// nguồn nào không có block đã đối chiếu bản in thì KHÔNG hiển thị.
///
/// Fail-closed có điều kiện, và điều kiện được nói ra:
/// - CÓ chỉ mục và `enabled == true` ⇒ chỉ block `verifiedAgainstPrint` mới
///   dùng được; phần còn lại được ĐẾM và nói rõ.
/// - KHÔNG có (fixture mẫu, tài liệu vòng 4, đường app hôm nay) ⇒ cổng KHÔNG
///   bật; [VerbatimIndex.enabled] là `false` và giao diện phải nói «chưa đối
///   chiếu bản in» thay vì im lặng coi như đã đối chiếu.
///
/// GIỚI HẠN ĐÃ BIẾT (đã báo, chưa tự sửa — CLAUDE.md điều 5): `LessonDocument`
/// hôm nay KHÔNG giữ lại `provenance.historyRules.verbatimGate` của JSON, nên
/// chỉ mục này phải được người nạp fixture truyền vào. Muốn cổng tự bật theo
/// tài liệu thì `lesson_document.dart` (khu A-runtime) phải mang thêm khoá ấy.
library;

enum VerbatimStatus {
  /// Một người đã đọc bản in và xác nhận block đúng từng chữ (dấu câu/kí hiệu
  /// trang trí có thể khác — `verbatim_glyph` cũng vào đây).
  verifiedAgainstPrint,

  /// Bản in khác với chữ pipeline đọc — KHÔNG được trích.
  printDiffers,

  /// Chưa ai đọc bản in cho block này — KHÔNG được trích khi cổng bật.
  unverified,
}

/// Tra cứu trạng thái nguyên văn theo block id, đọc từ chính tài liệu.
class VerbatimIndex {
  const VerbatimIndex._(this._byBlock, this.enabled, this.ledger);

  /// Cổng tắt: không tài liệu nào khai cổng ⇒ không chặn, nhưng cũng KHÔNG
  /// nói dối rằng đã đối chiếu.
  static const VerbatimIndex off = VerbatimIndex._({}, false, null);

  final Map<String, VerbatimStatus> _byBlock;

  /// Tài liệu này có được dựng dưới cổng nguyên văn không.
  final bool enabled;

  /// Tên ledger đã dùng (để giao diện/kiểm thử trích nguồn).
  final String? ledger;

  static const _statuses = <String, VerbatimStatus>{
    'verifiedAgainstPrint': VerbatimStatus.verifiedAgainstPrint,
    'printDiffers': VerbatimStatus.printDiffers,
    'unverified': VerbatimStatus.unverified,
  };

  /// `05-…-5:p039:tc2-p1:000` → `p039:tc2-p1:000` (ledger ghi dạng ngắn).
  static String shortId(String blockId) {
    final parts = blockId.split(':');
    return parts.length >= 4 ? parts.sublist(1).join(':') : blockId;
  }

  /// Đọc `provenance.historyRules.verbatimGate` từ JSON THÔ của tài liệu
  /// (`LessonDocument` chưa giữ khoá này — xem GIỚI HẠN ĐÃ BIẾT ở đầu tệp).
  /// Thiếu khoá, sai kiểu, hay `enabled != true` ⇒ [off].
  static VerbatimIndex fromRawJson(Map<String, Object?>? raw) {
    final prov = raw?['provenance'];
    if (prov is! Map) return off;
    final rules = prov['historyRules'];
    if (rules is! Map) return off;
    final gate = rules['verbatimGate'];
    if (gate is! Map || gate['enabled'] != true) return off;
    final statuses = gate['blockStatus'];
    final map = <String, VerbatimStatus>{};
    if (statuses is Map) {
      for (final e in statuses.entries) {
        final s = _statuses[e.value];
        if (s != null) map[shortId('${e.key}')] = s;
      }
    }
    final led = gate['ledger'];
    return VerbatimIndex._(Map.unmodifiable(map), true, led is String ? led : null);
  }

  VerbatimStatus statusOf(String blockId) =>
      _byBlock[shortId(blockId)] ?? VerbatimStatus.unverified;

  /// Có được trích block này cho trẻ đọc không. Cổng tắt ⇒ `true` (dữ liệu
  /// chưa qua cổng: giao diện nói rõ, không tự ý giấu).
  bool servable(String blockId) =>
      !enabled || statusOf(blockId) == VerbatimStatus.verifiedAgainstPrint;

  /// Câu nói thật cho giao diện khi có phần bị giữ lại — `null` khi không có.
  String? heldBackLine(int n) {
    if (!enabled || n <= 0) return null;
    return 'SAM giữ lại $n phần vì chưa đối chiếu được với bản in.';
  }

  /// Câu nói thật khi tài liệu chưa hề đi qua cổng.
  static const notCheckedLine =
      'Phần này chưa được đối chiếu với bản in — SAM đọc theo máy, dấu thanh có thể lệch.';
}
