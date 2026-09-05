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

  /// Sinh MÁY từ một Trusted Structured Lesson thật (`tc2-p1`, `sdm-v2`) bởi
  /// `tool/fixtures/make_lesson_fixture.py`. Chữ là nguyên văn SGK qua OCR +
  /// gate; crop trang là NỘI BỘ/NGHIÊN CỨU (Founder D4) — không phân phối.
  /// Vẫn là FIXTURE: chưa qua cổng phát hành cho trẻ.
  fixtureFromTrustedCorpus,

  /// Văn bản GIẢ LẬP, viết lại rõ ràng là mẫu — chỉ để CI/widget test chạy
  /// được ở máy không có corpus. Không câu nào là lời sách.
  fixtureSynthetic,

  /// Người viết tay cho lát cắt này (kịch bản SAM, khoá đáp án tạm, lời gợi
  /// ý). KHÔNG phải Pedagogy Runtime, KHÔNG phải SGV.
  prototype;

  bool get isProductionTruth => this == trustedCorpus;

  /// Mọi giá trị khác `trustedCorpus` ⇒ chip thử nghiệm bắt buộc.
  bool get requiresFixtureChip => !isProductionTruth;

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
};
