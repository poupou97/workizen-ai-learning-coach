/// ⭐⭐ F6 — Q-matrix: một bài tập chạm NHIỀU thành phần tri thức.
///
/// Founder (2026-09-01): *"Do not assume one exercise = one Concept."*
/// `3/4 + 2/5` cần `quy-dong` (ca không chia hết) VÀ `cong-phan-so` (khác mẫu)
/// và có thể `rut-gon`. EduStudio xác nhận đây là giả định nền của cả họ mô
/// hình KT/CD: trường `cpt_seq` — một bài ánh xạ một DANH SÁCH concept.
///
/// Cố ý TỐI THIỂU (Founder: *"Do not adopt a full cognitive-diagnosis model
/// merely because Q-matrix exists"*): đây là Q-matrix NHỊ PHÂN có xuất xứ,
/// không phải DINA/NCDM. Những gì mô hình đầy đủ cần thêm (tham số
/// slip/guess theo bài, ước lượng đồng thời...) đều đòi dữ liệu học sinh
/// thật mà ta chưa có. Biểu diễn này tiến hoá được: thêm trọng số/tham số
/// là thêm trường, không phải đổi schema.
library;

import '../knowledge/provenance.dart';

/// Một thành phần tri thức mà bài tập đòi hỏi — một ô "1" trong hàng Q-matrix.
class SkillRequirement {
  const SkillRequirement({
    required this.conceptId,
    required this.skillCaseId,
    required this.provenance,
  });

  final String conceptId;

  /// **Bắt buộc khai** — cùng doctrine với F2: một requirement không rõ ca
  /// là một requirement không kiểm chứng được, và unknown fail closed.
  final String skillCaseId;

  /// Ánh xạ bài→kỹ năng này Ở ĐÂU RA. Một hàng Q-matrix do LLM đoán không
  /// bao giờ được trình bày như sự thật của sách — đúng luật Provenance
  /// hiện hành, không thêm luật mới.
  final Provenance provenance;
}

/// Hàng Q-matrix của MỘT bài tập.
///
/// Mô hình kết hợp là **CONJUNCTIVE (AND)** — làm đúng đòi hỏi MỌI thành
/// phần cùng hoạt động (giả định DINA-gate, chuẩn trong văn liệu CD cho
/// toán nhiều bước). Hệ quả bất đối xứng và CỐ Ý:
///
///   - ĐÚNG  ⇒ bằng chứng cho TỪNG thành phần (tất cả đã chạy);
///   - SAI   ⇒ KHÔNG chia lỗi đều — chỉ biết ÍT NHẤT MỘT thành phần hỏng,
///             và việc tìm ra thành phần nào là bài toán CHẨN ĐOÁN
///             (`attributeFailure`), không phải phép chia đều điểm trừ.
///
/// Chia lỗi đều khi sai chính là "quy lỗi sai địa chỉ" mà ADR-003 §F6 cảnh
/// báo là tệ hơn không quy lỗi.
class ExerciseSkillMap {
  const ExerciseSkillMap({required this.exerciseId, required this.requirements});

  final String exerciseId;
  final List<SkillRequirement> requirements;

  bool get isEmpty => requirements.isEmpty;

  /// Các concept bài này chạm — dùng cho `LearningEvent.conceptIds`.
  List<String> get conceptIds =>
      requirements.map((r) => r.conceptId).toSet().toList()..sort();
}
