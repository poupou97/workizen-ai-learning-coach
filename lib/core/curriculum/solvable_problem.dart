/// WAL-168 — MỘT BÀI đã bóc thành dữ liệu, ở dạng tầng dạy dùng được mà
/// KHÔNG cần biết đó là môn gì.
///
/// Vì sao cần: trước đây `TutorSession.problem` mang kiểu `FractionProblem`,
/// nên chính phiên dạy mang kiểu của một môn. Môn thứ hai không vào nổi runtime
/// dù mọi tầng trên (evidence, mastery, TutorScope, provenance) đều đã trung
/// tính. Đây là một trong ba điểm chặn Architecture Gate đo được ở WAL-168.
///
/// Hợp đồng chỉ có hai việc, và đều là việc của BÀI, không phải của môn:
/// chấm đúng/sai, và cung cấp các giá trị để điền vào lời hướng dẫn.
library;

abstract interface class SolvableProblem {
  /// Trẻ gõ gì thì đúng. Fail closed: không đọc được ⇒ `false`, KHÔNG ném.
  bool checkAnswer(String raw);

  /// Giá trị điền vào mẫu lời dạy của phương pháp — khoá là tên slot.
  ///
  /// ⭐ Đây là chỗ «lời dạy là DỮ LIỆU» gặp «bài là DỮ LIỆU»: phương pháp mang
  /// mẫu câu, bài mang số, không bên nào phải viết Dart cho bên kia.
  Map<String, String> get slots;
}
