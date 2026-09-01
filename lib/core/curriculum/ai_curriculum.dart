/// ADR-008 — AI Curriculum (QĐ 2422/QĐ-BGDĐT 18/8/2026) trong graph hợp nhất.
///
/// Nguồn: khung chính thức 267 YCCĐ với hệ mã TỰ-ĐỊNH-NGHĨA trong văn bản
/// (tr.13-14): `<lớp>.<chủ đề>.<MR?><stt>` — `6.A1.MR1` = lớp 6, chủ đề A1,
/// MỞ RỘNG, số 1. Model này GIỮ NGUYÊN mã chính thức, không đặt tên lại
/// (lệnh Founder: no renaming official terminology).
///
/// Luật giữ bằng test:
/// - Mã là ĐỊNH DANH, không phải thứ tự dạy (chính nguồn nói) — không API nào
///   suy prerequisite/sequence từ mã (F4).
/// - Trần lớp fail-closed: truy vấn ở lớp g không bao giờ trả outcome lớp
///   trên như thể được phép (F8 — cùng luật future-knowledge của WAL-41).
/// - Mã không tồn tại ⇒ null, không đoán.
/// - `status` (SOURCE_EXPLICIT / INFERRED_OCR_CORRECTED) đi theo record —
///   suy diễn không được đội lốt nguyên văn (F6).
///
/// ⚠️ DỮ LIỆU THẬT ở pack (ngoài git — LEGAL INTERPRETATION/REVIEW PENDING,
/// WAL-43); repo chỉ chứa model + test trên fixture tổng hợp.
library;

/// Bốn mạch nội dung ↔ bốn thành phần năng lực (NLa–NLd) — mã CHÍNH THỨC.
enum AiStrand {
  a('A', 'NLa'), // Tư duy lấy con người làm trung tâm
  b('B', 'NLb'), // Đạo đức AI
  c('C', 'NLc'), // Các kĩ thuật và ứng dụng AI
  d('D', 'NLd'); // Thiết kế hệ thống AI

  const AiStrand(this.code, this.competencyCode);
  final String code;
  final String competencyCode;

  static AiStrand? fromCode(String letter) => switch (letter) {
        'A' => AiStrand.a,
        'B' => AiStrand.b,
        'C' => AiStrand.c,
        'D' => AiStrand.d,
        _ => null,
      };
}

/// Nguồn gốc từng record — F6: suy diễn phải mang nhãn.
enum AiOutcomeStatus { sourceExplicit, inferredOcrCorrected }

/// MỘT yêu cầu cần đạt chính thức. Bất biến kiểu: chỉ mint qua [parse] —
/// mã sai định dạng không thể tồn tại trong hệ.
class AiOutcome {
  const AiOutcome._({
    required this.code,
    required this.grade,
    required this.strand,
    required this.topic,
    required this.extended,
    required this.text,
    required this.sourcePage,
    required this.status,
  });

  final String code; // NGUYÊN VĂN mã chính thức, vd '6.A1.MR1'
  final int grade; // 1..12
  final AiStrand strand;
  final String topic; // 'A1'..'D2'
  final bool extended; // MR trong mã = nội dung mở rộng
  final String text;
  final int sourcePage; // trang QĐ 2422 — provenance bắt buộc
  final AiOutcomeStatus status;

  static final _codeRe = RegExp(r'^(\d{1,2})\.([A-D])(\d)\.(MR)?(\d{1,2})$');

  /// Mint duy nhất. Mã lệch định dạng chính thức ⇒ null (fail closed, không
  /// "sửa hộ"); lớp ngoài 1..12 ⇒ null.
  static AiOutcome? parse({
    required String code,
    required String text,
    required int sourcePage,
    AiOutcomeStatus status = AiOutcomeStatus.sourceExplicit,
  }) {
    final m = _codeRe.firstMatch(code);
    if (m == null) return null;
    final grade = int.parse(m.group(1)!);
    if (grade < 1 || grade > 12) return null;
    final strand = AiStrand.fromCode(m.group(2)!);
    if (strand == null) return null;
    return AiOutcome._(
      code: code,
      grade: grade,
      strand: strand,
      topic: '${m.group(2)}${m.group(3)}',
      extended: m.group(4) != null,
      text: text,
      sourcePage: sourcePage,
      status: status,
    );
  }
}

/// Khung AI như MỘT DOMAIN của curriculum graph (ADR-008) — không hạ tầng riêng.
class AiCurriculum {
  AiCurriculum(Iterable<AiOutcome> outcomes)
      : _byCode = {for (final o in outcomes) o.code: o};

  final Map<String, AiOutcome> _byCode;

  /// Tra bằng mã — không có ⇒ null, không đoán.
  AiOutcome? byCode(String code) => _byCode[code];

  /// ⭐ F8: mọi truy vấn theo lớp đi qua TRẦN. [gradeCeiling] là lớp hiện tại
  /// của học sinh — outcome lớp trên KHÔNG BAO GIỜ lọt ra như thể được phép.
  List<AiOutcome> forGrade(int grade, {required int gradeCeiling}) {
    if (grade > gradeCeiling) return const []; // hỏi vượt trần ⇒ rỗng, nói ra
    final out = _byCode.values
        .where((o) => o.grade == grade)
        .toList()
      ..sort((a, b) => a.code.compareTo(b.code)); // tất định để HIỂN THỊ —
    // KHÔNG phải thứ tự dạy (F4): mã chỉ là định danh, nguồn nói vậy.
    return out;
  }

  /// Outcome này có vượt lớp hiện tại của học sinh không? Mã lạ ⇒ null.
  bool? beyondGrade(String code, {required int currentGrade}) {
    final o = _byCode[code];
    if (o == null) return null;
    return o.grade > currentGrade;
  }

  /// Tiến trình một mạch — sắp theo LỚP rồi chủ đề (không theo mã đơn thuần).
  List<AiOutcome> progression(AiStrand strand, {required int gradeCeiling}) =>
      _byCode.values
          .where((o) => o.strand == strand && o.grade <= gradeCeiling)
          .toList()
        ..sort((a, b) {
          if (a.grade != b.grade) return a.grade.compareTo(b.grade);
          if (a.topic != b.topic) return a.topic.compareTo(b.topic);
          if (a.extended != b.extended) return a.extended ? 1 : -1;
          return a.code.compareTo(b.code);
        });
}
