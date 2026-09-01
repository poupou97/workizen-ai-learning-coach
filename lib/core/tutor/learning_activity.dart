/// WAL-97 — NGỮ NGHĨA HOẠT ĐỘNG học tập (Task Order §17, Delta §4).
///
/// Tầng giữa của chuỗi bắt buộc:
///   Truth (nguồn/chương trình) → **Activity semantics (ở đây)** →
///   Resolver → Interaction Surface → UI
///
/// ⭐ F8: KHÔNG có quyết định UI nào trong tầng chương trình/nội dung. Ở đây
/// cũng KHÔNG có tên widget — chỉ nói bài tập ĐÒI HỎI kiểu trả lời gì; ánh xạ
/// sang màn hình là việc của resolver, thay được mà không đụng tri thức.
///
/// Taxonomy V1 — **đo từ corpus thật**, không chép danh sách:
/// động từ mở đầu 1.706 bài tập (Toán 4-5 + TV5): Tìm 119 · Đọc 87 · Chọn 76 ·
/// Viết 67 · Tính 44 · Nêu 37 · Đặt 34. MCQ-4 / MAP / ORAL: **0 xuất hiện** ⇒
/// KHÔNG tạo loại cho chúng (Delta §4: falsify và tối giản taxonomy).
library;

enum ResponseKind {
  /// «Chọn…», «Tìm…» — chỉ ra thứ có sẵn trong đề. Lớn nhất corpus (195 lượt).
  selectIdentify,

  /// «Tính…», «Đặt tính rồi tính…» — ra một giá trị/các bước.
  numericStep,

  /// «Nêu…», «Trả lời…» — câu trả lời ngắn bằng lời.
  shortText,

  /// «Viết đoạn/bài…» — tạo văn bản dài, có quy trình nháp-sửa.
  compose,

  /// «Đọc … rồi thực hiện yêu cầu» — đọc hiểu rồi trả lời.
  readRespond,
}

/// Một bài tập đã mang ngữ nghĩa — cầu nối giữa ContentUnit (nguồn) và surface.
class LearningActivity {
  const LearningActivity({
    required this.activityId,
    required this.prompt,
    required this.response,
    required this.conceptId,
    this.skillCaseId,
    this.options = const [],
    this.correctOption,
    this.sourcePage,
    this.sourceBook,
  });

  final String activityId;
  final String prompt;
  final ResponseKind response;
  final String conceptId;

  /// `null` = chưa quy được về ca ⇒ tầng trên phải fail closed, không đoán.
  final String? skillCaseId;

  /// Lựa chọn cho [ResponseKind.selectIdentify]. Rỗng với loại khác.
  final List<String> options;

  /// Chỉ số đáp án đúng. `null` = chưa biết đáp án ⇒ KHÔNG được chấm
  /// (UNKNOWN không bao giờ thành SAI — doctrine).
  final int? correctOption;

  final int? sourcePage;
  final String? sourceBook;

  bool get gradable => correctOption != null &&
      correctOption! >= 0 &&
      correctOption! < options.length;
}

/// ⭐ RESOLVER: hoạt động → surface. Đây là NƠI DUY NHẤT ánh xạ này tồn tại
/// (F8) — đổi giao diện chỉ sửa ở đây, tri thức không đổi một dòng.
enum SurfaceKind { quizSelect, problemStep, reader, compose, unsupported }

SurfaceKind resolveSurface(LearningActivity a) => switch (a.response) {
      ResponseKind.selectIdentify => SurfaceKind.quizSelect,
      ResponseKind.numericStep => SurfaceKind.problemStep,
      ResponseKind.readRespond => SurfaceKind.reader,
      ResponseKind.compose => SurfaceKind.compose,
      // shortText chưa có surface riêng — fail closed, KHÔNG ép vào quiz
      ResponseKind.shortText => SurfaceKind.unsupported,
    };
