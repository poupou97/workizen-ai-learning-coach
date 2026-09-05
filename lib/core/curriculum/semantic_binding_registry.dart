/// ⭐ WAL-210 round 3 (A6) — SỔ ĐĂNG KÝ BINDING: hằng đóng, một mục.
///
/// Thêm binding = thêm một dòng ở đây + một mục curriculum tối thiểu + test
/// «giải được» cho đúng bài đó. Không quét, không sinh tự động, không LLM.
library;

import 'khtn6_bai17.dart';
import 'semantic_binding.dart';

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
}
