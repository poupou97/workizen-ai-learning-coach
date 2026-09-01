/// ⭐ Xuất xứ tri thức — **bắt buộc khai, không có mặc định**.
///
/// Work order §6: *"Prerequisite do LLM suy luận KHÔNG được giả thành textbook
/// fact."* Đó không phải lời nhắc để review — nó phải là thứ **trình biên dịch
/// giữ hộ**, vì đây là chỗ sai âm thầm và không ai phát hiện ra cho tới khi một
/// đứa trẻ được dạy sai và ta nói với phụ huynh rằng "sách viết thế".
///
/// Bài học mang từ Workizen Hub: mọi quyền/nguồn gốc được *phát sẵn theo mặc
/// định* đều bị vòng qua sớm hay muộn. Ở Hub đó là `FlowTrigger` có mặc định
/// `user()` ⇒ một đường vào OS quên khai là mặc nhiên được tiêu tiền. Ở đây, một
/// concept quên khai xuất xứ sẽ mặc nhiên trông như sự thật trong sách.
library;

/// Tri thức này ở đâu ra.
enum KnowledgeOrigin {
  /// ⭐ Sách **nói thẳng**. "Muốn cộng hai phân số khác mẫu số, ta quy đồng…"
  /// Trích dẫn được nguyên văn, kèm trang.
  sourceStated,

  /// ⭐ Sách **DẠY QUA VÍ DỤ/HOẠT ĐỘNG** mà không phát biểu quy tắc.
  /// Ca kiểm chuẩn: B57 Toán 4 — quy đồng dạy thuần bằng ví dụ mẫu, KHÔNG có
  /// câu «Muốn quy đồng…» nào (đo trên corpus, WAL-74). Trích dẫn ĐƯỢC
  /// (trang có thật) nhưng KHÔNG BAO GIỜ được render thành «sách nói rằng…» —
  /// loại hỗ trợ là một phần của tính đúng trích dẫn (Founder Delta §2).
  sourceDemonstrated,

  /// Sách chỉ **xếp thứ tự**. Mục lục đặt Bài 5 trước Bài 6 — đó là sự thật,
  /// nhưng sách KHÔNG nói "Bài 6 cần Bài 5".
  ///
  /// Tách khỏi [sourceStated] vì đây là chỗ dễ trượt nhất: thứ tự trông y hệt
  /// quan hệ nhân quả, và một lần gộp là Parent Coach bắt đầu nói "sách bảo con
  /// cần học lại Bài 5" về điều sách không viết.
  sourceSequence,

  /// Hệ thống suy ra bằng luật tất định từ dữ liệu nguồn (khoảng trang, offset).
  systemDerived,

  /// **LLM suy luận.** Hợp lý, thường đúng, và sách có thể không hề nói vậy.
  llmInferred,
}

/// Nguồn gốc của một mẩu tri thức. **Mọi trường quan trọng đều `required`.**
class Provenance {
  const Provenance({
    required this.origin,
    required this.sourceId,
    required this.extractionMethod,
    required this.confidence,
    this.bookSeries,
    this.grade,
    this.subject,
    this.pageStart,
    this.pageEnd,
    this.sourceHash,
  }) : assert(confidence >= 0 && confidence <= 1);

  final KnowledgeOrigin origin;

  /// Định danh nguồn — KHÔNG phải đường dẫn tệp. Đường dẫn rò rỉ bố cục ổ đĩa
  /// của người dùng vào dữ liệu, và đổi máy là hỏng.
  final String sourceId;

  /// `vision-ocr`, `toc-parse`, `glossary-parse`, `llm-gpt-x`, `manual`…
  final String extractionMethod;

  final double confidence;
  final String? bookSeries;
  final int? grade;
  final String? subject;

  /// ⚠️ Số trang **IN TRÊN SÁCH**, không phải số trang PDF. Toán 5 tập một có
  /// PDF = trang in + 1. Nhầm hệ quy chiếu là trích dẫn sai trang cho học sinh.
  final int? pageStart;
  final int? pageEnd;

  final String? sourceHash;

  /// ⭐ Được phép nói với người dùng "sách viết thế" hay không.
  ///
  /// Chỉ `sourceDerived` mới được. Đây là câu hỏi mà Parent Coach phải trả lời
  /// đúng: phụ huynh tin ta vì ta bám sách, nên một suy luận trình bày như trích
  /// dẫn là phá vỡ chính niềm tin đó.
  bool get citableAsTextbookFact =>
      (origin == KnowledgeOrigin.sourceStated ||
          origin == KnowledgeOrigin.sourceDemonstrated ||
          origin == KnowledgeOrigin.sourceSequence) &&
      pageStart != null;

  /// ⭐ Được phép phát biểu một quan hệ PHỤ THUỘC ("A cần B") như lời của sách.
  ///
  /// Chỉ [sourceStated]. Thứ tự trong mục lục **không** là phụ thuộc — dù bằng
  /// chứng có mạnh đến đâu. Đo được: Toán 5 Bài 6 mở đầu bằng "không chia hết
  /// cho nhau", tham chiếu rõ ca của lớp 4 — bằng chứng rất mạnh, và vẫn KHÔNG
  /// phải câu "cần học Bài 57 trước".
  bool get citableAsDependency =>
      origin == KnowledgeOrigin.sourceStated && pageStart != null;
}
