/// TRACK B — «SAM đề xuất»: MỘT bước tiếp theo, MỘT lý do, suy TẤT ĐỊNH từ
/// dữ liệu của chính bài (không recommender, không LLM, KHÔNG bịa phút).
///
/// 16-UX-CONCEPT §5: hàng đề xuất chỉ hiện khi có lý do giải thích được;
/// ước lượng thời gian («~5 phút») KHÔNG có trong dữ liệu nào ⇒ không in.
library;

import 'lesson_document.dart';
import 'semantic_data.dart';

enum WorkspaceView {
  read('📖', 'Đọc'),
  visual('✨', 'Trực quan'),
  tutor('🦉', 'Học với SAM');

  const WorkspaceView(this.icon, this.label);
  final String icon;
  final String label;
}

class NextAction {
  const NextAction({
    required this.view,
    required this.reason,
    required this.basis,
  });

  /// `null` = không còn View nào chưa xem — đề xuất «về mục lục».
  final WorkspaceView? view;

  /// Lý do trẻ đọc được — dựng từ dữ liệu thật của bài, không có con số bịa.
  final String reason;

  /// Dữ kiện máy đọc được đã sinh ra đề xuất (để test + tài liệu trích).
  final String basis;

  String get label =>
      view == null ? 'Về mục lục' : '${view!.icon} ${view!.label}';
}

/// Luật (theo thứ tự, luật đầu khớp thắng):
/// 1. Bài có sơ đồ quy trình và trẻ chưa xem Trực quan ⇒ Trực quan.
/// 2. Trẻ chưa đọc ⇒ Đọc.
/// 3. Có kịch bản SAM và trẻ chưa học với SAM ⇒ Học với SAM (nêu câu hỏi đầu).
/// 4. Xem đủ ba ⇒ về mục lục (lời ghi nhận THAM GIA, không nói «đã hiểu»).
NextAction nextActionFor({
  required LessonDocument doc,
  required Set<WorkspaceView> seen,
}) {
  final process = doc.semantic.whereType<ProcessSemantic>().firstOrNull;
  if (process != null && !seen.contains(WorkspaceView.visual)) {
    return NextAction(
      view: WorkspaceView.visual,
      reason:
          'Bài này có sơ đồ quy trình «${process.title}» — con xem '
          'Trực quan trước, rồi đọc kỹ trong sách nhé.',
      basis: 'semantic.process:${process.id}',
    );
  }
  if (!seen.contains(WorkspaceView.read)) {
    final paragraphs = doc.blocks.whereType<ParagraphBlock>().length;
    return NextAction(
      view: WorkspaceView.read,
      reason: seen.contains(WorkspaceView.visual)
          ? 'Con đã xem sơ đồ — giờ đọc bài trong sách để hiểu vì sao '
                'từng bước lại như vậy.'
          : 'Con đọc bài trong sách trước nhé — đọc xong SAM sẽ hỏi con.',
      basis: 'blocks.paragraph=$paragraphs',
    );
  }
  final script = doc.tutorScript;
  final firstAsk = script?.asks.firstOrNull;
  if (script != null && !seen.contains(WorkspaceView.tutor)) {
    return NextAction(
      view: WorkspaceView.tutor,
      reason: firstAsk == null
          ? 'Con đã đọc — giờ học cùng SAM phần này nhé.'
          : 'Con đã đọc — thử trả lời cùng SAM câu hỏi trong sách: '
                '«${firstAsk.prompt}»',
      basis: 'tutorScript.ask:${firstAsk?.id ?? '-'}',
    );
  }
  if (!seen.contains(WorkspaceView.visual)) {
    return const NextAction(
      view: WorkspaceView.visual,
      reason: 'Con còn chưa xem phần Trực quan của bài này.',
      basis: 'seen.missing:visual',
    );
  }
  return const NextAction(
    view: null,
    reason:
        'Con đã đi qua cả ba cách học của bài này. Con có thể xem lại '
        'cách nào con muốn, hoặc về mục lục chọn bài khác.',
    basis: 'seen.all',
  );
}
