/// ⭐ Cạnh trong Curriculum Graph — **thứ tự sách KHÔNG phải quan hệ tiên quyết**.
///
/// Phân biệt này nhỏ về chữ và lớn về hậu quả. Mục lục Toán 5 KNTT xếp
/// `Bài 3 → Bài 5 → Bài 6`: đó là **sự thật trong sách**, NXB tự đặt, trích dẫn
/// được tới số trang. Nhưng *"Bài 6 CẦN Bài 5 làm tiên quyết"* là **diễn giải
/// của ta** — sách không hề nói vậy.
///
/// Nếu trộn hai thứ, Parent Coach sẽ nói *"sách nói con cần học lại Bài 5"* về
/// một điều sách không viết. Và phụ huynh tin ta **chính vì** ta bám sách.
library;

import 'package:learning_coach/core/knowledge/provenance.dart';

enum EdgeKind {
  /// Sách xếp A trước B. SOURCE FACT — đọc được từ mục lục.
  sourceOrder,

  /// A là tiên quyết của B. Chỉ là SOURCE FACT khi sách **nói thẳng**
  /// ("cần biết…", "đã học ở bài…"); còn lại là suy luận.
  prerequisite,

  /// A dẫn tới B trong lộ trình học.
  precedes,

  /// Method áp dụng cho concept.
  methodAppliesTo,
}

class CurriculumEdge {
  const CurriculumEdge({
    required this.from,
    required this.to,
    required this.kind,
    required this.provenance,
    this.evidence,
  });

  final String from;
  final String to;
  final EdgeKind kind;

  /// **Bắt buộc.** Không cạnh nào tồn tại mà không biết nó ở đâu ra.
  final Provenance provenance;

  /// Trích dẫn/quan sát chống lưng cho cạnh này.
  final String? evidence;

  /// ⭐ Được phép nói với phụ huynh "sách nói thế" về cạnh này không.
  ///
  /// Một cạnh `prerequisite` do LLM suy ra **không bao giờ** được — kể cả khi nó
  /// gần như chắc chắn đúng. Độ đúng và quyền trích dẫn là hai câu hỏi khác nhau.
  bool get citable =>
      provenance.origin == KnowledgeOrigin.sourceDerived &&
      provenance.pageStart != null;
}
