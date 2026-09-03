/// Chương trình THẬT của slice, lấy qua ĐÚNG đường công khai mà sản phẩm dùng.
///
/// WAL-170: test không được có cửa sau riêng để lấy chương trình. Đi qua
/// `curriculumForLesson` nghĩa là mỗi test cũng đang ghim ĐỊNH DANH của bài —
/// đổi định danh mà quên đổi bảng đăng ký thì test đỏ, không im lặng trôi.
library;

import 'package:learning_coach/core/knowledge/slice_curriculum.dart';

/// Định danh của Toán 5 tập một · Bài 6 · trang in 20 (corpus:
/// `curriculum-structure.json`, `pageStart: 20`, `titleSource ocr-header:p21`).
const toan5Bai6Key = LessonKey(
  sourceDocumentId: '05-sgk-toan-5-tap-mot',
  number: 6,
  pageStart: 20,
);

/// Chương trình của Toán 5 Bài 6 — ném nếu bảng đăng ký không còn dòng này.
SliceCurriculum get toan5Bai6 {
  final c = curriculumForLesson(toan5Bai6Key);
  if (c == null) {
    throw StateError('Không có chương trình cho $toan5Bai6Key — '
        'bảng đăng ký đổi mà test chưa đổi theo.');
  }
  return c;
}
