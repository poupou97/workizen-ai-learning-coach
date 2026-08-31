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
  /// Đọc được **trực tiếp** từ nguồn: OCR một trang, mục trong bảng thuật ngữ,
  /// dòng trong mục lục. Trích dẫn được tới trang.
  sourceDerived,

  /// **LLM suy luận.** Ví dụ: "quy đồng mẫu số cần BCNN" — hợp lý, thường đúng,
  /// và **sách có thể không hề nói vậy**. Không bao giờ được trình bày cho phụ
  /// huynh/học sinh như điều sách viết.
  llmInferred,

  /// Hệ thống tự sinh: id, chỉ mục, thống kê. Không phải khẳng định tri thức.
  systemGenerated,
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
      origin == KnowledgeOrigin.sourceDerived && pageStart != null;
}
