/// ⭐⭐ WAL-210 round 3 (A-runtime, Founder A8) — NEXT BEST LEARNING ACTION
/// cho MỘT BÀI (PROPOSED): Student Knowledge State + Learning Context + luật
/// sư phạm → một hành động, một lý do ngắn, trung thực.
///
/// Thay thế dần luật prototype của Track B (`nextActionFor` trong
/// `core/lesson_model/next_action.dart` — luật «có sơ đồ ⇒ Trực quan trước»).
/// Thứ tự luật ở đây là thứ tự Founder A8 nêu:
///
///   R0 context chưa giải ra bài / lệch bài  ⇒ về mục lục (fail closed)
///   R1 tự làm được, CÓ DẤU validator        ⇒ bài tiếp (nếu biết) / mục lục
///   R2 chưa Đọc                              ⇒ 📖 Đọc
///   R3 đã Đọc, có SemanticData, chưa Trực quan ⇒ ✨ Trực quan
///   R4 đã Đọc (+Trực quan nếu có), có kịch bản, chưa Học với SAM ⇒ 🦉
///   R5 đã đi qua mọi cách học có sẵn         ⇒ về mục lục (ghi nhận THAM
///      GIA, không nói «đã hiểu»)
///
/// Bất biến (giữ bằng test): không bịa phút / phần trăm / mastery; «sang bài
/// tiếp» CHỈ từ [StudentLessonState.hasApprovedValidatedSuccess]; tự báo và
/// dữ liệu cũ không dấu KHÔNG mở khoá bài tiếp; lý do luôn truy được về luật.
library;

import '../context/learning_context.dart';
import '../curriculum/semantic_binding.dart' show LessonRef;
import '../lesson_model/lesson_document.dart';
import '../lesson_model/next_action.dart' show WorkspaceView;
import '../student/student_lesson_state.dart';

enum LessonNextKind { read, visual, tutor, nextLesson, backToContents }

/// Tóm tắt MÁY ĐỌC ĐƯỢC của tài liệu bài — chỉ những dữ kiện luật cần.
class LessonSummary {
  const LessonSummary({
    required this.lessonRef,
    required this.hasReadableBlocks,
    required this.hasSemanticData,
    required this.hasTutorScript,
    this.firstAskPrompt,
    this.nextLesson,
  });

  final LessonRef lessonRef;
  final bool hasReadableBlocks;
  final bool hasSemanticData;
  final bool hasTutorScript;

  /// Câu hỏi đầu tiên của kịch bản (NGUYÊN VĂN từ kịch bản) — để lý do R4 nêu
  /// đúng câu sách hỏi, không bịa.
  final String? firstAskPrompt;

  /// Bài tiếp theo trong sách nếu tầng trên biết (mục lục); `null` = không
  /// biết ⇒ R1 nói «về mục lục», không đoán số bài.
  final LessonRef? nextLesson;

  static LessonSummary fromDocument(LessonDocument d, {LessonRef? nextLesson}) =>
      LessonSummary(
        lessonRef: LessonRef(d.book, d.lessonNo),
        hasReadableBlocks: d.blocks.any((b) => b is! WithheldBlock),
        hasSemanticData: d.semantic.isNotEmpty,
        hasTutorScript: d.tutorScript != null,
        firstAskPrompt: d.tutorScript?.asks.firstOrNull?.prompt,
        nextLesson: nextLesson,
      );
}

class LessonNextAction {
  const LessonNextAction({
    required this.kind,
    required this.reason,
    required this.rule,
    required this.basis,
    this.view,
    this.nextLesson,
  });

  final LessonNextKind kind;

  /// View tương ứng (Lane B mở tab này); `null` cho bài tiếp / mục lục.
  final WorkspaceView? view;

  /// Câu trẻ đọc được — ngắn, trung thực, không con số bịa.
  final String reason;

  /// `R0`…`R5` — luật đã bắn.
  final String rule;

  /// Dữ kiện máy đọc được sinh ra đề xuất (audit).
  final String basis;
  final LessonRef? nextLesson;

  String get label => switch (kind) {
        LessonNextKind.read => '📖 Đọc',
        LessonNextKind.visual => '✨ Trực quan',
        LessonNextKind.tutor => '🦉 Học với SAM',
        LessonNextKind.nextLesson => 'Sang Bài ${nextLesson?.lessonNo}',
        LessonNextKind.backToContents => 'Về mục lục',
      };
}

/// Luật A8 — thuần, tất định. [viewsSeen] là DẤU VẾT UI (trace) của phiên,
/// không phải bằng chứng; [state] là bằng chứng có lineage.
LessonNextAction nextBestLessonAction({
  required StudentLessonState state,
  required LearningContext context,
  required LessonSummary lesson,
  required Set<WorkspaceView> viewsSeen,
}) {
  final ctxRef = LessonRef.fromContext(context);
  if (ctxRef == null || ctxRef != state.lessonRef || ctxRef != lesson.lessonRef) {
    return LessonNextAction(
      kind: LessonNextKind.backToContents,
      rule: 'R0',
      reason: 'SAM chưa xác định được con đang ở bài nào — con về mục lục '
          'chọn lại bài nhé.',
      basis: 'context=${ctxRef?.key ?? 'null'} state=${state.lessonRef.key} '
          'doc=${lesson.lessonRef.key}',
    );
  }

  if (state.hasApprovedValidatedSuccess) {
    final next = lesson.nextLesson;
    return LessonNextAction(
      kind: next == null ? LessonNextKind.backToContents : LessonNextKind.nextLesson,
      nextLesson: next,
      rule: 'R1',
      reason: next == null
          ? 'Con đã tự làm được bài này (SAM đã chấm) — con về mục lục chọn '
              'bài khác nhé.'
          : 'Con đã tự làm được bài này (SAM đã chấm) — mình sang Bài '
              '${next.lessonNo} nhé.',
      basis: 'state.hasApprovedValidatedSuccess',
    );
  }

  if (!lesson.hasReadableBlocks && !lesson.hasSemanticData && !lesson.hasTutorScript) {
    return const LessonNextAction(
      kind: LessonNextKind.backToContents,
      rule: 'R5',
      reason: 'Bài này SAM chưa đọc được phần nào — con xem trong SGK nhé.',
      basis: 'lesson.empty',
    );
  }

  if (lesson.hasReadableBlocks && !viewsSeen.contains(WorkspaceView.read)) {
    return LessonNextAction(
      kind: LessonNextKind.read,
      view: WorkspaceView.read,
      rule: 'R2',
      reason: state.hasAnyEvidence
          ? 'Con đọc lại bài trong sách trước nhé — đọc xong SAM sẽ hỏi con.'
          : 'Con đọc bài trong sách trước nhé — chưa có gì ghi lại ở bài này.',
      basis: 'seen.missing:read state=${state.mapState.name}',
    );
  }

  if (lesson.hasSemanticData && !viewsSeen.contains(WorkspaceView.visual)) {
    return const LessonNextAction(
      kind: LessonNextKind.visual,
      view: WorkspaceView.visual,
      rule: 'R3',
      reason: 'Con đã đọc — giờ xem sơ đồ / bảng của bài để thấy từng bước '
          'rõ hơn nhé.',
      basis: 'seen.read && semantic && seen.missing:visual',
    );
  }

  if (lesson.hasTutorScript && !viewsSeen.contains(WorkspaceView.tutor)) {
    final q = lesson.firstAskPrompt;
    return LessonNextAction(
      kind: LessonNextKind.tutor,
      view: WorkspaceView.tutor,
      rule: 'R4',
      reason: q == null
          ? 'Con đã đọc — giờ học cùng SAM phần này nhé.'
          : 'Con đã đọc — thử trả lời cùng SAM câu hỏi trong sách: «$q»',
      basis: 'seen.read && tutorScript && seen.missing:tutor',
    );
  }

  return LessonNextAction(
    kind: LessonNextKind.backToContents,
    rule: 'R5',
    reason: state.mapState.name == 'participation'
        ? 'Con đã đi qua các cách học của bài này — SAM ghi nhận con đã tham '
            'gia, chưa chấm phần nào. Con về mục lục chọn bài khác nhé.'
        : 'Con đã đi qua các cách học của bài này. Con có thể xem lại, hoặc '
            'về mục lục chọn bài khác.',
    basis: 'seen.all state=${state.mapState.name}',
  );
}
