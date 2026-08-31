/// ⭐ §15 — seam cách ly pháp lý.
///
/// Mục tiêu **duy nhất** của tệp này: xoá hoặc thay corpus SGK mà **không phá**
/// Student Knowledge Graph, Tutor Engine, Parent Coach, Curriculum model.
///
/// Trạng thái pháp lý hôm nay là `LEGAL_REVIEW_PENDING`. Nếu Legal Gate ra kết
/// quả xấu, việc phải làm là **đổi một implementation**, không phải viết lại sản
/// phẩm. Mọi truy cập nội dung SGK đi qua đây — không đường nào khác.
library;

import 'provenance.dart';

/// Nội dung này được phép dùng tới đâu. Provider phải **tự khai**, và tầng trên
/// đọc để quyết định có được hiển thị / trích dẫn / xuất bản hay không.
enum ContentLicense {
  /// Chỉ nghiên cứu local/private. **Không** hiển thị nguyên văn cho người dùng
  /// cuối, không xuất bản. Corpus SGK hôm nay ở mức này.
  localResearchOnly,

  /// Đã có giấy phép bằng văn bản từ chủ sở hữu.
  licensed,

  /// Tài nguyên giáo dục mở / văn bản nhà nước (vd. Chương trình GDPT 2018).
  openEducational,

  /// Workizen tự soạn.
  ownContent,
}

class KnowledgeQuery {
  const KnowledgeQuery({
    required this.text,
    this.grade,
    this.subject,
    this.bookSeries,
    this.lessonId,
    this.conceptIds = const [],
    this.limit = 8,
  });

  final String text;

  /// ⭐ §9: lọc ngữ cảnh TRƯỚC rồi mới retrieve. Biết lớp 5 · Toán · KNTT · bài X
  /// thì không có lý do gì quét cả corpus — vừa đắt vừa dễ trả nhầm lớp.
  final int? grade;
  final String? subject;
  final String? bookSeries;
  final String? lessonId;
  final List<String> conceptIds;
  final int limit;
}

class KnowledgeChunk {
  const KnowledgeChunk({
    required this.id,
    required this.text,
    required this.provenance,
    this.contentType,
    this.conceptIds = const [],
    this.methodIds = const [],
  });

  final String id;
  final String text;

  /// **Bắt buộc.** Không có chunk nào tồn tại mà không biết nó ở đâu ra.
  final Provenance provenance;

  /// `explanation` · `example` · `exercise` · `definition` · `summary`
  final String? contentType;
  final List<String> conceptIds;
  final List<String> methodIds;
}

abstract class KnowledgeContentProvider {
  /// Định danh ổn định của nguồn, dùng trong `Provenance.sourceId`.
  String get sourceId;

  /// ⭐ Provider **phải tự khai** giới hạn sử dụng. Không có mặc định "chắc là
  /// dùng được" — nếu quên khai thì không biên dịch được.
  ContentLicense get license;

  Future<List<KnowledgeChunk>> retrieve(KnowledgeQuery query);
}
