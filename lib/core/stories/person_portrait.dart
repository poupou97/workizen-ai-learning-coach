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
/// ⭐ BA NGƯỜI, không phải hai mươi mốt. `sam-stories.db` có 21 nhân vật; ba
/// người đi trọn được chuỗi: nguồn gốc → giấy phép → danh tính → tệp thật →
/// CHỖ DÙNG THẬT. Mười tám người còn lại KHÔNG có dòng ở đây, nên màn chuyện
/// của họ chạy nhánh KHÔNG ẢNH — nhánh ấy là trạng thái bình thường, không
/// phải lỗi (§P2.7).
///
/// ⚠ MỖI NGƯỜI MỘT HỒ SƠ PHÁP LÝ. Ba ảnh này PD vì ba lý do KHÁC NHAU
/// (PD-Vietnam 75 năm · tác giả mất >100 năm · công bố trước 1931). Không
/// được suy từ người này sang người khác. Đã loại đúng theo luật ấy: ảnh
/// Ta-go đẹp nhất là CC BY 4.0 — dùng được nhưng kèm nghĩa vụ ghi công, nên
/// chọn bản PD thay thế. Tô Hoài (mất 2014), Bùi Xuân Phái (1988), Lâm Thị Mỹ
/// Dạ (2023) đều CÒN bản quyền — không lấy.
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

    // ⭐ Han Cri-xti-an An-đéc-xen (1805–1875) — Ngữ văn 6, «Cô bé bán diêm».
    //
    //   NGUỒN GỐC   Ảnh của Thora Hallager (1821–1884) chụp tháng 10/1869,
    //               lưu ở Bảo tàng Odense — chính bảo tàng quê hương An-đéc-xen.
    //   DANH TÍNH   Khác ca Thạch Lam: ảnh này là ảnh CHÍNH của bài An-đéc-xen
    //               trên Wikipedia và được 20 wiki dùng. Có đối chiếu chéo thật,
    //               không phải chỉ một dòng siêu dữ liệu.
    //   GIẤY PHÉP   PD-old-100-expired: tác giả mất 1884, quá 100 năm.
    'p:han-cri-xti-an-an-đéc-xen': PersonPortrait(
      personId: 'p:han-cri-xti-an-an-đéc-xen',
      personName: 'Han Cri-xti-an An-đéc-xen',
      assetPath: 'assets/people/han-cri-xti-an-an-dec-xen.png',
      portraitType: PortraitType.historicalPhoto,
      usage: PortraitUsage.approvedForProduct,
      sourcePageUrl:
          'https://commons.wikimedia.org/wiki/'
          'File:HCA_by_Thora_Hallager_1869_crop.jpg',
      sourceName: 'Thora Hallager, 1869 · Bảo tàng Odense',
      licence: 'Phạm vi công cộng (PD-old-100)',
      licenceUrl:
          'https://commons.wikimedia.org/wiki/Template:PD-old-100-expired',
      retrievedAt: '2026-09-07',
      author: 'Thora Hallager (1821–1884)',
      identityCheckedAgainst:
          'Ảnh chính của bài «Hans Christian Andersen» trên Wikipedia, được 20 '
          'wiki dùng; nguồn ghi Bảo tàng Odense — bảo tàng quê hương ông',
    ),

    // ⭐ Ra-bin-đo-ra-nát Ta-go (1861–1941) — Ngữ văn 6, «Mây và sóng».
    //
    //   NGUỒN GỐC   Công bố 1914 trong «Les Prix Nobel 1913» tr.60 — niên giám
    //               của chính Quỹ Nobel cho người đoạt giải Văn chương 1913.
    //   DANH TÍNH   500 wiki dùng. Đối chiếu chéo mạnh nhất trong ba ảnh.
    //   GIẤY PHÉP   PD-old-100-expired.
    //
    //   ⚠ ĐÃ LOẠI một ứng viên khác: ảnh autochrome 1926 của Georges Chevalier
    //   là **CC BY 4.0**, KHÔNG phải phạm vi công cộng — dùng được nhưng kèm
    //   nghĩa vụ ghi công. Không suy «Thạch Lam PD ⇒ ảnh nào cũng PD»: mỗi ảnh
    //   một hồ sơ. Cũng đã loại một bản PD khác vì tác giả không rõ, nguồn là
    //   một blog và 0 wiki dùng — PD nhưng lai lịch quá mỏng.
    'p:ra-bin-đo-ra-nát-ta-go': PersonPortrait(
      personId: 'p:ra-bin-đo-ra-nát-ta-go',
      personName: 'Ra-bin-đo-ra-nát Ta-go',
      assetPath: 'assets/people/ra-bin-do-ra-nat-ta-go.png',
      portraitType: PortraitType.historicalPhoto,
      usage: PortraitUsage.approvedForProduct,
      sourcePageUrl:
          'https://commons.wikimedia.org/wiki/File:Rabindranath_Tagore_in_1909.jpg',
      sourceName: 'Les Prix Nobel 1913 (xuất bản 1914)',
      licence: 'Phạm vi công cộng (PD-old-100)',
      licenceUrl:
          'https://commons.wikimedia.org/wiki/Template:PD-old-100-expired',
      retrievedAt: '2026-09-07',
      author: 'Generalstabens litografiska anstalt, 1909',
      identityCheckedAgainst:
          'Niên giám Quỹ Nobel «Les Prix Nobel 1913» tr.60 in ảnh này cho người '
          'đoạt giải Văn chương 1913; 500 wiki dùng làm chân dung Ta-go',
    ),
  };

  /// `null` ⇒ chưa có chân dung đủ điều kiện cho người này.
  static PersonPortrait? forPerson(String? personId) {
    if (personId == null) return null;
    final p = verified[personId];
    return (p != null && p.eligibleForDisplay) ? p : null;
  }
}
