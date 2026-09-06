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
///   R5 đã MỞ mọi cách học có sẵn             ⇒ Ở LẠI BÀI (round 7: KHÔNG
///      còn bảo trẻ về mục lục — «đã mở» không phải «đã đi qua»)
///
/// Bất biến (giữ bằng test): không bịa phút / phần trăm / mastery; «sang bài
/// tiếp» CHỈ từ [StudentLessonState.hasApprovedValidatedSuccess]; tự báo và
/// dữ liệu cũ không dấu KHÔNG mở khoá bài tiếp; lý do luôn truy được về luật.
library;

import '../context/learning_context.dart';
import '../curriculum/semantic_binding.dart' show LessonRef;
import '../lesson_model/lesson_document.dart';
import '../lesson_model/next_action.dart' show WorkspaceView;
import '../student/learning_map_state.dart' show LearningMapState;
import '../student/student_lesson_state.dart';

export '../student/student_lesson_state.dart' show LessonEvidenceStanding;

enum LessonNextKind {
  read,
  visual,
  tutor,
  nextLesson,
  backToContents,

  /// ⭐ ROUND 7 · WS-R — Ở LẠI BÀI. Trẻ đã MỞ hết những cách học bài này có,
  /// và đó là TẤT CẢ những gì SAM biết. `viewsSeen` là dấu vết «đã mở tab»,
  /// không phải bằng chứng đã học (`OPENED != UNDERSTOOD`), nên nó không đủ
  /// để bảo trẻ rời bài. Xem ghi chú R5 ở dưới.
  keepGoing,
}

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

  /// Những cách học bài NÀY thật sự có, theo thứ tự Founder A8. Dùng chung cho
  /// luật (R5 đếm ở đây) và cho màn hình (hàng «Đã mở» không được liệt kê một
  /// cách học mà bài không có) — MỘT nguồn, nên hai chỗ không thể mâu thuẫn.
  List<WorkspaceView> get availableViews => [
        if (hasReadableBlocks) WorkspaceView.read,
        if (hasSemanticData) WorkspaceView.visual,
        if (hasTutorScript) WorkspaceView.tutor,
      ];

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
    this.standing = LessonEvidenceStanding.none,
    this.evidenceNote,
  });

  final LessonNextKind kind;

  /// ⭐ ROUND 4 — vị thế bằng chứng của bài lúc đề xuất (luật siết).
  final LessonEvidenceStanding standing;

  /// ⭐ ROUND 4 — câu trung thực «đã tham gia nhưng chưa được kiểm» / «ghi
  /// nhận trước hợp đồng mới» để Lane B hiện dưới đề xuất. `null` = không
  /// có gì đáng nói (chưa học; hoặc đã kiểm — R1 tự nói).
  final String? evidenceNote;

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
        LessonNextKind.keepGoing => 'Xem tiếp bài này',
      };
}

/// Luật A8 — thuần, tất định. [viewsSeen] là DẤU VẾT UI (trace) của phiên,
/// không phải bằng chứng; [state] là bằng chứng có lineage.
///
/// ⭐⭐ ROUND 4 (Founder §4): [state] đọc dưới luật SIẾT mặc định. Các kết cục
/// «đã tham gia nhưng chưa được kiểm» được nói ra qua
/// [LessonNextAction.evidenceNote] / [LessonNextAction.standing] (mọi luật)
/// và qua câu R5:
///   - tự báo (participation)              ⇒ «đã tham gia, chưa chấm»;
///   - dữ liệu cũ có chấm-không-dấu         ⇒ «ghi nhận trước hợp đồng mới,
///     chưa kiểm lại nên chưa tính là tự làm được»;
///   - học cùng SAM, chưa lần nào được kiểm ⇒ «chưa có lần tự làm được nào
///     được kiểm».
/// Không kết cục nào mở khoá bài tiếp; không con số nào được bịa.
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

  final standing = state.standing;
  final note = state.evidenceNote;
  final standingBasis = 'standing=${standing.name}'
      '${state.hasHistoricalUnvalidated ? ' historicalUnvalidated=${state.historicalUnvalidatedCount}' : ''}'
      '${state.hasParticipation ? ' participation=${state.participationCount}' : ''}';

  if (state.hasApprovedValidatedSuccess) {
    final next = lesson.nextLesson;
    return LessonNextAction(
      kind: next == null ? LessonNextKind.backToContents : LessonNextKind.nextLesson,
      nextLesson: next,
      rule: 'R1',
      standing: standing,
      reason: next == null
          ? 'Con đã tự làm được bài này (SAM đã chấm) — con về mục lục chọn '
              'bài khác nhé.'
          : 'Con đã tự làm được bài này (SAM đã chấm) — mình sang Bài '
              '${next.lessonNo} nhé.',
      basis: 'state.hasApprovedValidatedSuccess $standingBasis',
    );
  }

  if (!lesson.hasReadableBlocks && !lesson.hasSemanticData && !lesson.hasTutorScript) {
    return LessonNextAction(
      kind: LessonNextKind.backToContents,
      rule: 'R5',
      standing: standing,
      evidenceNote: note,
      reason: 'Bài này SAM chưa đọc được phần nào — con xem trong SGK nhé.',
      basis: 'lesson.empty $standingBasis',
    );
  }

  if (lesson.hasReadableBlocks && !viewsSeen.contains(WorkspaceView.read)) {
    return LessonNextAction(
      kind: LessonNextKind.read,
      view: WorkspaceView.read,
      rule: 'R2',
      standing: standing,
      evidenceNote: note,
      reason: state.hasAnyEvidence
          ? 'Con đọc lại bài trong sách trước nhé — đọc xong SAM sẽ hỏi con.'
          : 'Con đọc bài trong sách trước nhé — chưa có gì ghi lại ở bài này.',
      basis: 'seen.missing:read state=${state.mapState.name} $standingBasis',
    );
  }

  if (lesson.hasSemanticData && !viewsSeen.contains(WorkspaceView.visual)) {
    return LessonNextAction(
      kind: LessonNextKind.visual,
      view: WorkspaceView.visual,
      rule: 'R3',
      standing: standing,
      evidenceNote: note,
      reason: 'Con đã đọc — giờ xem sơ đồ / bảng của bài để thấy từng bước '
          'rõ hơn nhé.',
      basis: 'seen.read && semantic && seen.missing:visual $standingBasis',
    );
  }

  if (lesson.hasTutorScript && !viewsSeen.contains(WorkspaceView.tutor)) {
    final q = lesson.firstAskPrompt;
    return LessonNextAction(
      kind: LessonNextKind.tutor,
      view: WorkspaceView.tutor,
      rule: 'R4',
      standing: standing,
      evidenceNote: note,
      reason: q == null
          ? 'Con đã đọc — giờ học cùng SAM phần này nhé.'
          : 'Con đã đọc — thử trả lời cùng SAM câu hỏi trong sách: «$q»',
      basis: 'seen.read && tutorScript && seen.missing:tutor $standingBasis',
    );
  }

  // R5 — trẻ đã MỞ hết những cách học bài này có.
  //
  // ⭐⭐ ROUND 7 · WS-R — SỬA TIỀN ĐỀ, KHÔNG NỚI CỔNG. Bản vòng 3–6 kết luận
  // «Con đã ĐI QUA các cách học của bài này» rồi bảo trẻ «về mục lục chọn bài
  // khác». Bằng chứng duy nhất sinh ra kết luận ấy là [viewsSeen] — dấu vết
  // UI, được đánh dấu NGAY LÚC MỞ tab (`WorkspaceTrace.markView`). «Đã mở»
  // không phải «đã đi qua», và chính tệp này đã viết ở đầu rằng viewsSeen
  // «không phải bằng chứng». Luật đọc nó như bằng chứng — đó là mâu thuẫn.
  //
  // Hệ quả đo được trên máy thật (LS&ĐL 5 Bài 8, Nokia 6.1): bài không có
  // SemanticData và không có kịch bản, nên `availableViews` chỉ có 📖 Đọc.
  // Trẻ mở bài, chạm Đọc — R3/R4 không bắn — R5 bắn NGAY, và SAM bảo trẻ rời
  // bài mình vừa mở, ngay phía trên hàng «Đã mở: ● Đọc ○ Trực quan ○ Học với
  // SAM» còn nói hai cách kia chưa mở. Hai câu trên một màn, ngược nhau.
  //
  // Sửa: R5 KHÔNG BAO GIỜ ra lệnh rời bài. Nó nói đúng thứ nó biết («đã MỞ»),
  // nói thẳng MỞ chưa phải HIỂU, và đề xuất Ở LẠI. Về mục lục vẫn là quyền
  // của trẻ (nút ← luôn có trên hàng tiêu đề) — nhưng nó là LỰA CHỌN, không
  // phải LỜI KHUYÊN của SAM. Đường DUY NHẤT SAM chủ động mời sang bài khác là
  // R1: `hasApprovedValidatedSuccess`, tức có bằng chứng đã chấm.
  final ways = lesson.availableViews;
  final opened = ways.length == 1
      ? 'Bài này SAM chỉ có một cách học — ${ways.single.label} — và con đã mở rồi.'
      : 'Con đã mở đủ ${ways.length} cách học SAM có cho bài này.';
  final String standingLine;
  if (state.hasHistoricalUnvalidated) {
    standingLine = 'Có lần làm được ghi nhận trước hợp đồng mới, SAM chưa kiểm '
        'lại nên chưa tính là tự làm được.';
  } else if (state.mapState == LearningMapState.participation) {
    standingLine = 'SAM ghi nhận con đã tham gia, chưa chấm phần nào.';
  } else if (state.mapState == LearningMapState.engaged) {
    standingLine = 'Chưa có lần tự làm được nào được kiểm.';
  } else {
    standingLine = 'Mở bài không phải là hiểu bài — SAM chưa chấm phần nào ở đây.';
  }
  return LessonNextAction(
    kind: LessonNextKind.keepGoing,
    rule: 'R5',
    standing: standing,
    evidenceNote: note,
    reason: '$opened $standingLine Con cứ xem tiếp bài này nhé.',
    basis: 'seen.allAvailable=${ways.length} state=${state.mapState.name} '
        '$standingBasis',
  );
}
