/// ⭐⭐ TRACK B (WAL-210) — RANH GIỚI MÁY ĐỌC ĐƯỢC của Lesson Workspace.
///
/// Lát cắt dọc «Bookshelf → Book → Chapter → Lesson → Workspace» được phép
/// dùng fixture/kịch bản để NHÌN THẤY sản phẩm, nhưng KHÔNG được phép tạo ra
/// «sự thật học tập» nào. Sáu bất đẳng thức của Founder (2026-09-05) không
/// nằm trong tài liệu để người đọc nhớ — chúng là KIỂU DỮ LIỆU để trình biên
/// dịch và test giữ hộ:
///
/// - `ContentTrust`   : mỗi phần tử nội dung KHAI nó tin được tới đâu.
/// - `EvidencePolicy` : chỉ có MỘT giá trị (`none`) — workspace không có
///   kiểu dữ liệu nào để ghi bằng chứng, nên không thể "quên" mà ghi.
/// - `SamMode`        : chỉ có `prototypeScripted` — UI bắt buộc dán nhãn
///   «SAM (kịch bản thử nghiệm)», không có mode nào để giả làm SAM thật.
/// - `BoundaryClaim`  : sáu bất đẳng thức, hằng công khai để test quét.
library;

/// Nội dung này tin được tới đâu — KHAI ở từng block / sơ đồ / bước kịch bản.
///
/// Chỉ `trustedCorpus` là sự thật sản phẩm. Ba giá trị còn lại đều bắt buộc
/// UI hiện chip «Bản thử nghiệm» không tắt được (xem `fixtureChipLabel`).
enum ContentTrust {
  /// TrustedLearningSource đã qua cổng TC (TC-10/TC-11). **Chưa tồn tại trong
  /// app hôm nay** — giữ giá trị này để mô hình không bị khoá vào fixture.
  trustedCorpus,

  /// Sinh MÁY từ dữ liệu corpus NGOÀI cổng TC — ví dụ tên chương từ MỤC LỤC
  /// OCR thô (`toc-ocr-chapters-v1`), hoặc fixture của bộ sinh cũ
  /// (`make_lesson_fixture.py@v1`). Chữ có thể là nguyên văn SGK qua OCR;
  /// crop trang là NỘI BỘ/NGHIÊN CỨU (Founder D4) — không phân phối.
  /// Vẫn là FIXTURE: chưa qua cổng phát hành cho trẻ.
  fixtureFromTrustedCorpus,

  /// Văn bản GIẢ LẬP, viết lại rõ ràng là mẫu — chỉ để CI/widget test chạy
  /// được ở máy không có corpus. Không câu nào là lời sách.
  fixtureSynthetic,

  /// Người viết tay cho lát cắt này (kịch bản SAM, khoá đáp án tạm, lời gợi
  /// ý). KHÔNG phải Pedagogy Runtime, KHÔNG phải SGV.
  prototype,

  /// ⭐ Round 3 (A1) — block được pipeline TC-v2 (`tc2-p1` / `sdm-v2`) đánh
  /// dấu TRUSTED trong một Trusted Structured Lesson, bắc cầu NGUYÊN VĂN bởi
  /// `tool/corpus/tsl_to_lesson_document.py` (id block, trang, bbox, vai trò,
  /// quan hệ, provenance giữ đủ). **CHƯA phải sự thật sản phẩm**: cổng G1
  /// (kiểm-tin-giả trên mẫu 484 dòng) chưa được Founder chốt, và giấy phép
  /// phân phối (D4) là cổng RIÊNG. UI bắt buộc hiện chip «chưa kiểm định».
  /// Gỡ chip cần HAI quyết định tách biệt: ngưỡng audit + giấy phép.
  trustedStructuredLesson,

  /// ⭐ Round 3 (A1) — vùng pipeline GIỮ LẠI (`WITHHELD` / `CONFLICT`) hoặc
  /// vai trò mô hình tiêu thụ không biết (`unknown_role:*`). CHỈ
  /// `WithheldBlock` được mang giá trị này; block có chữ mà khai `withheld`
  /// ⇒ `fromJson` trả `null` (fail-closed). WITHHELD ≠ TRUSTED — không chữ
  /// nào của nó lọt vào thứ SAM đọc được.
  withheld;

  bool get isProductionTruth => this == trustedCorpus;

  /// Mọi giá trị khác `trustedCorpus` ⇒ chip thử nghiệm bắt buộc.
  bool get requiresFixtureChip => !isProductionTruth;

  /// Giá trị này có được đứng trên một block CÓ CHỮ không. `withheld` thì
  /// không — ràng buộc kiểu, `LessonBlock.fromJson` giữ.
  bool get mayCarryText => this != withheld;

  /// Fail-closed: chuỗi lạ hoặc thiếu ⇒ `null`, KHÔNG mặc định thành tin được.
  static ContentTrust? parse(Object? v) {
    if (v is! String) return null;
    for (final t in values) {
      if (t.name == v) return t;
    }
    return null;
  }
}

/// Chính sách bằng chứng của toàn bộ workspace: **không có**.
///
/// Cố ý là enum MỘT giá trị: không tồn tại `EvidencePolicy.record` để một
/// màn nào đó "bật lên". Muốn ghi bằng chứng thật thì phải đi qua Surface +
/// `recordSession` của đường Deep/Scale — không phải qua đây.
enum EvidencePolicy {
  none;

  static EvidencePolicy? parse(Object? v) => v == 'none' ? none : null;
}

/// Chế độ của SAM trong workspace. Chỉ một giá trị, và giá trị đó BẮT BUỘC
/// hiện thành chữ trên màn: «SAM (kịch bản thử nghiệm)».
enum SamMode {
  prototypeScripted;

  /// Nhãn trẻ nhìn thấy — test quét đúng chuỗi này trên mọi màn Tutor.
  String get childLabel => 'SAM (kịch bản thử nghiệm)';

  static SamMode? parse(Object? v) =>
      v == 'prototypeScripted' ? prototypeScripted : null;
}

/// Sáu bất đẳng thức của Founder — máy đọc được, tài liệu trích từ đây.
enum BoundaryClaim {
  mockIsNotEvidence('MOCK ≠ EVIDENCE'),
  fixtureIsNotTrustedCorpus('FIXTURE ≠ TRUSTED CORPUS'),
  uiCompletionIsNotMastery('UI COMPLETION ≠ MASTERY'),
  tapIsNotCompetence('TAP ≠ COMPETENCE'),
  prototypeSamIsNotProvenPedagogy('PROTOTYPE SAM ≠ PROVEN PEDAGOGY'),
  screenExistsIsNotCapabilityProven('SCREEN EXISTS ≠ CAPABILITY PROVEN');

  const BoundaryClaim(this.statement);
  final String statement;
}

/// Chữ trên chip «Bản thử nghiệm» — theo LOẠI fixture, không chung chung.
/// `null` chỉ khi là sự thật sản phẩm (chip không hiện).
String? fixtureChipLabel(ContentTrust t) => switch (t) {
  ContentTrust.trustedCorpus => null,
  ContentTrust.fixtureFromTrustedCorpus =>
    'Bản thử nghiệm · nội dung nội bộ (từ SGK, chưa phát hành)',
  ContentTrust.fixtureSynthetic => 'Bản thử nghiệm · nội dung mẫu (giả lập)',
  ContentTrust.prototype => 'Bản thử nghiệm · nội dung mẫu / nội bộ',
  // Chữ «chưa kiểm định» là CỐ Ý: nguồn có cấu trúc ≠ đã qua cổng G1/giấy phép.
  ContentTrust.trustedStructuredLesson =>
    'Bản thử nghiệm · nguồn SGK có cấu trúc, chưa kiểm định (nội bộ)',
  ContentTrust.withheld => 'Bản thử nghiệm · phần bị giữ lại (không hiện chữ)',
};

/// ⭐ Round 3 (A1) — GIẤY PHÉP phân phối của một tài liệu, TÁCH khỏi trust.
///
/// Cố ý là enum MỘT giá trị (như `EvidencePolicy`): không tồn tại
/// `distributable` để một fixture nào "bật lên". Founder D4: chữ SGK nguyên
/// văn, trang, crop = NỘI BỘ / NGHIÊN CỨU. Thiếu trường ⇒ giá trị chặt nhất
/// (chính giá trị duy nhất); chuỗi lạ ⇒ `null` ⇒ tài liệu bị từ chối.
enum ContentLicence {
  internalResearchOnly;

  static ContentLicence? parse(Object? v) {
    if (v == null) return internalResearchOnly;
    return v == 'internalResearchOnly' ? internalResearchOnly : null;
  }
}

/// ⭐ Round 3 (A2) — tài liệu này đã đi qua kiểm-tin-giả tới đâu. KHÔNG có
/// giá trị «đạt»: ngưỡng là quyết định của Founder sau khi có số; mô hình chỉ
/// ghi «chưa kiểm» hoặc «đã nằm trong mẫu đo, chưa có cổng». Thiếu ⇒
/// `notAudited` (khẳng định yếu nhất); chuỗi lạ ⇒ `null` ⇒ từ chối.
enum AuditStatus {
  notAudited,
  sampledNoGate;

  static AuditStatus? parse(Object? v) {
    if (v == null) return notAudited;
    for (final s in values) {
      if (s.name == v) return s;
    }
    return null;
  }
}
