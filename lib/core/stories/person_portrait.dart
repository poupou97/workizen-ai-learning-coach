/// ⭐⭐ Lệnh 59 §P2 — CHÂN DUNG NHÂN VẬT LÀ MỘT TÀI SẢN CÓ LAI LỊCH.
///
/// Founder cho phép tìm ảnh trên Internet khi máy không có. Nhưng kèm theo là
/// ba bất biến, và cả ba đều được giữ bằng KIỂU ở đây, không bằng lời dặn:
///
///     FOUND ON INTERNET  !=  FREE TO SHIP
///     SEARCH RESULT      !=  ORIGINAL SOURCE
///     SEARCH RESULT      !=  VERIFIED IDENTITY
///
/// ⭐ VÀ BA SỰ THẬT RIÊNG (§P2.7). Một câu nói đúng KHÔNG chứng minh bức ảnh
/// đúng người; một bức ảnh đúng người KHÔNG chứng minh câu nói có thật. Nên
/// [PersonPortrait] không mang thông tin gì về quote, và quote không tự sinh
/// ra chân dung.
library;

/// Ảnh này là loại gì (§P2.6) — KHÔNG được trình bày minh hoạ như ảnh tư liệu.
enum PortraitType {
  historicalPhoto,
  portraitPhoto,
  portraitPainting,
  illustration,

  /// ⚠ Ảnh do máy sinh. Không bao giờ được để trẻ hiểu đây là ảnh tư liệu.
  aiGeneratedIllustration;

  /// Nhãn trẻ/phụ huynh đọc — nói ĐÚNG loại, không làm sang lên.
  String get label => switch (this) {
    PortraitType.historicalPhoto => 'Ảnh tư liệu',
    PortraitType.portraitPhoto => 'Ảnh chân dung',
    PortraitType.portraitPainting => 'Tranh chân dung',
    PortraitType.illustration => 'Tranh minh hoạ',
    PortraitType.aiGeneratedIllustration => 'Tranh do máy vẽ',
  };
}

/// Quyền dùng (§P2.4). Chỉ MỘT giá trị là tài sản sản phẩm.
enum PortraitUsage {
  approvedForProduct,
  internalOnly,
  unknownRights,
  rejected;

  /// ⭐ Cổng DUY NHẤT quyết định ảnh có được lên sản phẩm hay không.
  bool get isProductionAsset => this == PortraitUsage.approvedForProduct;
}

/// Lai lịch đầy đủ của một bức chân dung.
class PersonPortrait {
  const PersonPortrait({
    required this.personId,
    required this.personName,
    required this.assetPath,
    required this.portraitType,
    required this.usage,
    required this.sourcePageUrl,
    required this.sourceName,
    required this.licence,
    required this.retrievedAt,
    this.imageUrl,
    this.author,
    this.licenceUrl,
    this.identityCheckedAgainst,
  });

  final String personId;
  final String personName;

  /// Đường dẫn asset trong app. Ảnh chưa tải về ⇒ rỗng.
  final String assetPath;

  final PortraitType portraitType;
  final PortraitUsage usage;

  /// ⭐ TRANG NGUỒN GỐC, không phải trang kết quả tìm kiếm (§P2.3).
  final String sourcePageUrl;
  final String sourceName;
  final String licence;
  final String retrievedAt;

  final String? imageUrl;
  final String? author;
  final String? licenceUrl;

  /// Đã đối chiếu danh tính với cái gì (§P2.5). `null` ⇒ CHƯA xác minh, và
  /// khi ấy [eligibleForDisplay] luôn false — thà KHÔNG ẢNH còn hơn SAI NGƯỜI.
  final String? identityCheckedAgainst;

  /// ⭐⭐ Cổng hiển thị: phải vừa được duyệt quyền, vừa xác minh danh tính,
  /// vừa có tệp thật. Thiếu bất kỳ điều nào ⇒ thẻ trích dẫn vẫn chạy, chỉ là
  /// không có ảnh (§P2.7 — không chặn quote vì thiếu ảnh).
  bool get eligibleForDisplay =>
      usage.isProductionAsset &&
      identityCheckedAgainst != null &&
      assetPath.isNotEmpty;
}

/// Kho chân dung đã xác minh, khoá theo `personId`.
///
/// ⭐ RỖNG HÔM NAY, và điều đó được ghi ra chứ không giấu: chưa bức chân dung
/// nào đi trọn quy trình xác minh + quyền dùng. Thẻ trích dẫn vì thế chạy ở
/// nhánh KHÔNG ẢNH — nhánh ấy phải hoạt động tốt, không phải trạng thái lỗi.
///
/// Thêm một người = thêm MỘT dòng ở đây, dùng lại cho MỌI bài có nhân vật ấy
/// (§P2.8) — không tải lại theo từng bài.
class PersonPortraits {
  const PersonPortraits._();

  static const Map<String, PersonPortrait> verified = {};

  /// `null` ⇒ chưa có chân dung đủ điều kiện cho người này.
  static PersonPortrait? forPerson(String? personId) {
    if (personId == null) return null;
    final p = verified[personId];
    return (p != null && p.eligibleForDisplay) ? p : null;
  }
}
