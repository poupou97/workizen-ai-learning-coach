/// ⭐ SỔ ĐĂNG KÝ BINDING — một mục viết tay, cộng một ĐƯỜNG SUY TỪ NGUỒN.
///
/// Bản gốc (WAL-210 A6) là hằng đóng một mục: thêm binding = thêm một dòng
/// ở đây. Cách ấy KHÔNG scale — 18 bài là 18 tệp Dart viết tay, tức 18 lần
/// một người khẳng định chân lí chương trình.
///
/// Nay có cửa thứ hai: [resolveFromDocument] dựng binding TỪ CHÍNH DỮ LIỆU
/// của bài (`curriculum`, suy từ khối quy tắc in trong sách) rồi giao cho
/// cùng một [resolveBinding]. Không luật tin cậy thứ hai, không runtime thứ
/// hai. Không có ngữ nghĩa in ra ⇒ `null` ⇒ fail closed như trước.
library;

import 'khtn6_bai17.dart';
import 'semantic_binding.dart';
import 'source_grounded_binding.dart';

class SemanticBindingRegistry {
  const SemanticBindingRegistry._();

  static const List<SemanticBinding> bindings = [khtn6Bai17TutorBinding];

  /// Curriculum tối thiểu theo bài — chỉ Bài 17 hôm nay.
  static BindingCurriculum? curriculumFor(LessonRef ref) =>
      ref == khtn6Bai17 ? khtn6Bai17Curriculum : null;

  static List<SemanticBinding> bindingsFor(LessonRef ref) =>
      [for (final b in bindings) if (b.lessonRef == ref) b];

  /// `null` = bài này / hoạt động này chưa có binding ⇒ runtime fail closed.
  static SemanticBinding? forActivity(LessonRef ref, String activityId) {
    for (final b in bindings) {
      if (b.lessonRef == ref && b.activityId == activityId) return b;
    }
    return null;
  }

  /// Giải binding của một hoạt động trong một bài — một cửa cho runtime.
  static ResolvedBinding? resolveFor(LessonRef ref, String activityId) {
    final b = forActivity(ref, activityId);
    if (b == null) return null;
    return resolveBinding(b, curriculumFor(ref));
  }

  /// Cửa thứ hai: ngữ nghĩa nằm TRONG chính tài liệu của bài.
  ///
  /// `curriculumJson` là khối `curriculum` do bộ dựng trích nguyên văn từ
  /// khối quy tắc in. Sai/thiếu một trường bắt buộc ⇒ [SourceCurriculum
  /// .fromJson] trả `null` ⇒ ở đây trả `null`: KHÔNG có đường nào dựng binding
  /// từ ngữ nghĩa chưa chứng minh.
  static ResolvedBinding? resolveFromDocument(
    Object? curriculumJson, {
    required String book,
    required int lessonNo,
    required int grade,
    required String activityId,
    String bookSeries = 'kntt',
  }) {
    final c = SourceCurriculum.fromJson(curriculumJson);
    if (c == null) return null;
    final r = bindingFor(c,
        book: book,
        lessonNo: lessonNo,
        grade: grade,
        bookSeries: bookSeries,
        activityId: activityId);
    return resolveBinding(r.binding, r.curriculum);
  }
}
