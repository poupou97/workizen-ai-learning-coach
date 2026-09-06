/// ⭐⭐ ROUND 6 (workstream C) — MỘT SỬA CHỮA ĐÃ ĐƯỢC KIỂM CHỨNG, đi tới được app.
///
/// Vòng 5 kết thúc bằng một sự thật đã kiểm bằng cấu trúc, không phải bằng báo
/// cáo: **không file nào ngoài `tool/corpus/repair/` và `tool/tests/` import gói
/// `repair`**. Đường sửa chữa đã được kiểm chứng, và KHÔNG nối tới sản phẩm. Nên
/// «không dòng chữ phục vụ nào thay đổi» là điều chắc chắn của dây nối, không
/// phải kết quả đo. File này là đầu app của dây nối đó.
///
/// **NỐI ≠ TIN.** Nối đường sửa chữa KHÔNG cần đặt ngưỡng tin sản phẩm — đó là
/// cổng của Founder. Một vùng được sửa **vẫn bị giữ lại**, vẫn KHÔNG CÓ CHỮ, chỉ
/// khác một điều: nó **nhìn thấy được và đếm được**. Đó là toàn bộ mục đích.
///
/// Bốn ràng buộc là KIỂU DỮ LIỆU, không phải lời hứa:
/// 1. `ValidatedRepairRef` chỉ tồn tại với `disposition = VALIDATED_REPAIR`.
///    `fromJson` trả `null` cho mọi giá trị khác — kể cả `TRUSTED`. Không có
///    trường, cờ hay hàm nào trong file này biến nó thành tin được.
/// 2. Bản ghi KHÔNG mang giá trị đề xuất. Không `text`, không `proposedValue`,
///    không `latex`. Có một trong số đó ⇒ `null` ⇒ TÀI LIỆU BỊ TỪ CHỐI: một pack
///    cố lén giá trị qua đây là một pack không được đọc.
/// 3. Chỉ `WithheldBlock` được mang bản ghi (`LessonBlock.fromJson` giữ).
/// 4. `servable` luôn `false` — là getter, không phải trường, nên JSON không đặt
///    được. Cùng luật với `MathExpression.servable` bên Python.
///
/// Từ vựng `disposition` LẤY NGUYÊN của `tool/corpus/repair/model.py` —
/// KHÔNG dựng vũ trụ provenance thứ tư. `ContentTrust` vẫn là thứ nói block này
/// có được hiện chữ không; `RepairDisposition` nói giai đoạn sửa chữa của nó.
library;

/// Bảy + ba trạng thái của lệnh phiên bản-dữ liệu (Founder §14), NGUYÊN VĂN
/// chuỗi dây (`repair.model.Disposition`). Có mặt đủ để **nhận ra rồi từ chối**
/// một giá trị mạnh hơn, chứ không phải để dùng.
enum RepairDisposition {
  originalObservation('ORIGINAL_OBSERVATION', 2),
  repairedCandidate('REPAIRED_CANDIDATE', 3),
  validatedRepair('VALIDATED_REPAIR', 4),
  trusted('TRUSTED', 6),
  withheld('WITHHELD', 0),
  legacy('LEGACY', 1),
  superseded('SUPERSEDED', 1),
  suspect('SUSPECT', 1),
  humanVerified('HUMAN_VERIFIED', 5),
  conflict('CONFLICT', 0);

  const RepairDisposition(this.wire, this.strength);

  /// Chuỗi trên dây — giống hệt Python, để một dòng ledger đọc được ở cả hai bên.
  final String wire;

  /// Thứ tự MẠNH YẾU, chỉ dùng để chứng minh một vòng lưu–đọc không làm nó
  /// mạnh lên (Lane E2: một round trip từng NÂNG grounding mà không ai báo).
  final int strength;

  /// Fail-closed: chuỗi lạ hoặc thiếu ⇒ `null`, KHÔNG mặc định thành gì cả.
  static RepairDisposition? parse(Object? v) {
    if (v is! String) return null;
    for (final d in values) {
      if (d.wire == v) return d;
    }
    return null;
  }
}

/// Những khoá KHÔNG BAO GIỜ được có trên một bản ghi sửa chữa: đó là các cửa
/// mà giá trị đề xuất có thể đi qua để tới màn hình của trẻ. Bản sao của
/// `REPAIR_FORBIDDEN_KEYS` trong `tool/corpus/tsl_to_lesson_document.py` — hai
/// đầu cùng kiểm, vì đầu nào cũng có thể là đầu bị bỏ quên.
const repairForbiddenKeys = <String>{
  'proposedValue',
  'text',
  'value',
  'latex',
  'textProjection',
  'candidate',
  'originalObservations',
  'structuredValue',
};

/// DẤU VẾT của một sửa chữa đã được một validator TẤT ĐỊNH xác nhận — và chưa
/// ai quyết định cho phục vụ.
///
/// Giữ đủ để đọc lại quyết định: hỏng ở lớp nào (`failureClass`), sửa bằng luật
/// nào (`method`), phiên bản sửa (`repairVersion`), ai kiểm và phiên bản nào
/// (`validatorId` / `validatorVersion`), kết quả (`verdict`), những lớp tín hiệu
/// độc lập đã ủng hộ (`supportingLayers`), giá trị có đổi không (`changed`), và
/// vì sao nó bị chặn lại (`caps`). Giá trị thì KHÔNG — giá trị ở lại corpus.
class ValidatedRepairRef {
  const ValidatedRepairRef({
    required this.repairId,
    required this.failureClass,
    required this.method,
    required this.repairVersion,
    required this.validatorId,
    required this.validatorVersion,
    required this.verdict,
    this.supportingLayers = const [],
    this.changed = false,
    this.structuredKind,
    this.caps = const [],
  });

  /// Định danh bản ghi trong `repairs[]` của TSL (nội bộ/nghiên cứu).
  final String repairId;

  /// Lớp hỏng (`text_agreement_segmentation`, `vi_text_diacritic`,
  /// `formula_flattened`…) — nguyên trạng, không dịch, không gộp.
  final String failureClass;

  /// Luật sửa (`column-linearisation-v1`, `vi.diacritic-agreed-error-v1`…).
  final String method;

  /// `repair-v1/<luật>` — phiên bản để phát lại được.
  final String repairVersion;
  final String validatorId;
  final String validatorVersion;

  /// `validated` — kiểu này không tồn tại với giá trị khác.
  final String verdict;

  /// Các lớp tín hiệu ĐỘC LẬP (`A`..`F`) đã ủng hộ. Luật của Founder «một sửa
  /// chữa đáng tin phải được một tín hiệu hoặc nguồn độc lập xác nhận» là một
  /// phát biểu về tập này.
  final List<String> supportingLayers;

  /// Giá trị đề xuất có KHÁC quan sát gốc không. `false` ⇒ luật không viết lại
  /// chữ nào, nó chỉ nói rằng cái CỔNG đã sai.
  final bool changed;

  /// Loại cấu trúc kèm theo (`mathExpression`…) nếu có — CHỈ tên loại, không
  /// bao giờ là bản dựng hình của nó.
  final String? structuredKind;

  /// Vì sao bản ghi này bị chặn lại (`trust_gate:founder_decision_absent`).
  /// Mất một cap qua vòng lưu–đọc là làm mất lý do — test bắt.
  final List<String> caps;

  /// LUÔN `false`. Là getter chứ không phải trường: JSON không đặt được.
  bool get servable => false;

  RepairDisposition get disposition => RepairDisposition.validatedRepair;

  /// Bị chặn vì ngưỡng tin sản phẩm chưa có (cổng Founder).
  bool get cappedByTrustGate =>
      caps.any((c) => c.startsWith('trust_gate:'));

  /// Fail-closed ở mọi nhánh. `null` ⇒ `LessonBlock.fromJson` trả `null` ⇒ tài
  /// liệu bị từ chối: một bản ghi sửa chữa hỏng KHÔNG được im lặng biến mất.
  static ValidatedRepairRef? fromJson(Object? v) {
    if (v is! Map) return null;
    // ⭐ Giá trị đề xuất không bao giờ được đi cùng bản ghi.
    for (final k in repairForbiddenKeys) {
      if (v.containsKey(k)) return null;
    }
    // ⭐ Chỉ VALIDATED_REPAIR. `TRUSTED` bị từ chối như mọi chuỗi lạ khác.
    if (RepairDisposition.parse(v['disposition']) !=
        RepairDisposition.validatedRepair) {
      return null;
    }
    if (v['servable'] == true) return null;
    final id = v['repairId'],
        fc = v['failureClass'],
        m = v['method'],
        rv = v['repairVersion'],
        vid = v['validatorId'],
        verdict = v['verdict'];
    if (id is! String || id.isEmpty) return null;
    if (fc is! String || fc.isEmpty) return null;
    if (m is! String || m.isEmpty) return null;
    if (rv is! String || rv.isEmpty) return null;
    if (vid is! String || vid.isEmpty) return null;
    if (verdict != 'validated') return null;
    return ValidatedRepairRef(
      repairId: id,
      failureClass: fc,
      method: m,
      repairVersion: rv,
      validatorId: vid,
      validatorVersion: v['validatorVersion'] is String
          ? v['validatorVersion'] as String
          : 'unversioned',
      verdict: verdict as String,
      supportingLayers: [
        for (final l in (v['supportingLayers'] as List? ?? const []))
          if (l is String && l.isNotEmpty) l,
      ],
      changed: v['changed'] == true,
      structuredKind: v['structuredKind'] is String
          ? v['structuredKind'] as String
          : null,
      caps: [
        for (final c in (v['caps'] as List? ?? const []))
          if (c is String && c.isNotEmpty) c,
      ],
    );
  }

  Map<String, Object?> toJson() => {
    'repairId': repairId,
    'disposition': disposition.wire,
    'failureClass': failureClass,
    'method': method,
    'repairVersion': repairVersion,
    'validatorId': validatorId,
    'validatorVersion': validatorVersion,
    'verdict': verdict,
    'supportingLayers': supportingLayers,
    'changed': changed,
    'servable': servable,
    'structuredKind': structuredKind,
    'caps': caps,
  };

  /// Một vòng lưu–đọc KHÔNG được làm bản ghi mạnh lên (Lane E2, PR #86).
  ///
  /// Cùng họ với luật «không có constructor từ dạng trình bày»: cả hai đều là
  /// cửa để một khẳng định yếu trở thành mạnh mà không có bằng chứng mới. Trả
  /// `false` (chứ không ném) để test đọc được cả hai chiều.
  static bool notStrengthened(
    Map<String, Object?> before,
    Map<String, Object?> after,
  ) {
    final b = RepairDisposition.parse(before['disposition'])?.strength ?? -1;
    final a = RepairDisposition.parse(after['disposition'])?.strength ?? -1;
    if (a > b) return false;
    if (after['servable'] == true && before['servable'] != true) return false;
    final bc = (before['caps'] as List? ?? const []).length;
    final ac = (after['caps'] as List? ?? const []).length;
    if (ac < bc) return false; // mất một cap là mất lý do bị chặn
    return true;
  }
}
