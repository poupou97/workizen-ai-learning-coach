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
/// ⭐ MỘT NGƯỜI, không phải hai mươi mốt. `sam-stories.db` có 21 nhân vật;
/// đúng MỘT người đi trọn được chuỗi: nguồn gốc → giấy phép → danh tính →
/// tệp thật. Hai mươi người còn lại KHÔNG có dòng ở đây, nên thẻ trích dẫn của
/// họ chạy nhánh KHÔNG ẢNH — nhánh ấy là trạng thái bình thường, không phải
/// lỗi (§P2.7). Độ phủ chân dung theo dõi ở WAL-226.
///
/// Thêm một người = thêm MỘT dòng ở đây, dùng lại cho MỌI bài có nhân vật ấy
/// (§P2.8) — không tải lại theo từng bài.
class PersonPortraits {
  const PersonPortraits._();

  static const Map<String, PersonPortrait> verified = {
    // ⭐ Thạch Lam (1910–1942), nhà văn Tự Lực văn đoàn.
    //
    // Chuỗi lai lịch, mỗi mắt xích kiểm riêng — lai lịch đầy đủ:
    // docs/content/PERSON-PORTRAIT-PROVENANCE.md
    //
    //   NGUỒN GỐC   Không dừng ở Wikimedia Commons. Commons ghi tệp đến từ
    //               Gallica (Thư viện Quốc gia Pháp), bản số hoá sách «Nhà Văn
    //               Hiện Đại» của Vũ Ngọc Phan. Đã tải trang gốc ở Gallica và
    //               đối chiếu — SEARCH RESULT != ORIGINAL SOURCE (§P2.3).
    //
    //   DANH TÍNH   KHÔNG suy từ tên tệp, cũng không từ chú thích Commons.
    //               Chính bản in mang dòng chữ «Thạch-Lam» ngay dưới bản khắc.
    //               Đó là chú thích của nhà xuất bản, không phải của người
    //               tải ảnh lên — SEARCH RESULT != VERIFIED IDENTITY (§P2.5).
    //
    //   GIẤY PHÉP   PD-Vietnam: tác phẩm nhiếp ảnh công bố lần đầu quá 75 năm
    //               (1942–45 ⇒ 81 năm tính đến 2026). Phạm vi công cộng thì
    //               được phát hành, nên tệp này commit ĐƯỢC — khác hẳn crop
    //               SGK vốn chặn ở D4.
    //
    //   ⚠ ẢNH SHIP KHÔNG PHẢI PIXEL GỐC. Đã cắt lấy phần bản khắc từ ảnh chụp
    //   nguyên trang, lọc median để phá lưới tram của bản in ty-pô 1942, và
    //   giãn tương phản. KHÔNG dựng lại khuôn mặt, KHÔNG upscale bằng máy —
    //   đó sẽ là bịa chi tiết mà bản in không có.
    'p:thạch-lam': PersonPortrait(
      personId: 'p:thạch-lam',
      personName: 'Thạch Lam',
      assetPath: 'assets/people/thach-lam.png',
      // «Ảnh tư liệu», không phải «Ảnh chân dung»: đây là bản in ty-pô 80 năm
      // tuổi của một tấm ảnh, và trẻ nên đọc đúng như thế (§P2.6).
      portraitType: PortraitType.historicalPhoto,
      usage: PortraitUsage.approvedForProduct,
      sourcePageUrl: 'https://gallica.bnf.fr/ark:/12148/bpt6k42462606/f145',
      sourceName: 'Nhà Văn Hiện Đại (1942) · Gallica/BnF',
      licence: 'Phạm vi công cộng (PD-Vietnam)',
      licenceUrl: 'https://commons.wikimedia.org/wiki/Template:PD-Vietnam',
      retrievedAt: '2026-09-07',
      imageUrl:
          'https://upload.wikimedia.org/wikipedia/commons/e/e0/'
          'Portrait_of_writer_Th%E1%BA%A1ch_Lam.jpg',
      // Người chụp KHÔNG rõ. Vũ Ngọc Phan là tác giả SÁCH, không phải người
      // chụp ảnh — Commons ghi ông ở ô «Artist» nhưng ghi rõ «author of the
      // book», nên chép nguyên nghĩa ấy chứ không nâng thành tác giả ảnh.
      author: 'Không rõ người chụp · sách của Vũ Ngọc Phan',
      identityCheckedAgainst:
          'Chú thích in trong chính bản gốc: dòng «Thạch-Lam» đặt ngay dưới '
          'bản khắc, trang f145 bản số hoá Gallica ark:/12148/bpt6k42462606',
    ),
  };

  /// `null` ⇒ chưa có chân dung đủ điều kiện cho người này.
  static PersonPortrait? forPerson(String? personId) {
    if (personId == null) return null;
    final p = verified[personId];
    return (p != null && p.eligibleForDisplay) ? p : null;
  }
}
