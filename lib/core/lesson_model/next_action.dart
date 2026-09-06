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

  /// `null` = không còn View nào **chưa mở**.
  ///
  /// ⭐ ROUND 7 (WS-S, HO-2 từ WS-R): điều đó KHÔNG có nghĩa là bài đã xong, và
  /// từ vòng này nó không còn dẫn tới «về mục lục». `seen` là dấu vết **đã mở
  /// tab**, không phải bằng chứng đã học — `OPENED != UNDERSTOOD`.
  final WorkspaceView? view;

  /// Lý do trẻ đọc được — dựng từ dữ liệu thật của bài, không có con số bịa.
  final String reason;

  /// Dữ kiện máy đọc được đã sinh ra đề xuất (để test + tài liệu trích).
  final String basis;

  /// ⭐⭐ ROUND 7 (WS-S) — HO-2, SỬA Ở NGUỒN.
  ///
  /// Trước vòng này: `view == null ⇒ 'Về mục lục'`. Đó **chính là chuỗi đã bảo
  /// một đứa trẻ rời khỏi bài nó vừa mở** — trên Nokia 6.1, LS&ĐL 5 Bài 8, ngay
  /// phía trên hàng «Đã mở». WS-R đã chữa chỗ GỌI (`founderNextAction` không
  /// còn ép về `NextAction` nữa); đây là chữa **cái nguồn**, để câu ấy không thể
  /// quay lại từ một chỗ gọi khác.
  ///
  /// Vì sao là «Xem tiếp bài này» chứ không phải một câu mới: đó đúng là chữ mà
  /// `LessonNextKind.keepGoing` của WS-R đã dùng. **Hai lớp không được nói hai
  /// kiểu về cùng một tình huống** — mâu thuẫn hai câu trên một màn chính là
  /// khuyết tật gốc.
  ///
  /// SAM không bao giờ đề nghị rời bài từ đường này. Quay lại vẫn là **một
  /// chạm** trên nút ← luôn có ở header — **lựa chọn của trẻ, không phải lời
  /// khuyên của SAM**. Đường duy nhất SAM được đề xuất bài khác vẫn là
  /// `hasApprovedValidatedSuccess` ở `lib/core/agenda/lesson_next_action.dart`.
  String get label =>
      view == null ? 'Xem tiếp bài này' : '${view!.icon} ${view!.label}';
}

/// Luật (theo thứ tự, luật đầu khớp thắng):
/// 1. Bài có sơ đồ quy trình và trẻ chưa xem Trực quan ⇒ Trực quan.
/// 2. Trẻ chưa đọc ⇒ Đọc.
/// 3. Có kịch bản SAM và trẻ chưa học với SAM ⇒ Học với SAM (nêu câu hỏi đầu).
/// 4. Đã MỞ đủ ba ⇒ Ở LẠI BÀI (vòng 7: ghi nhận THAM GIA, không nói «đã hiểu»,
///    và **không bảo trẻ rời bài** — «đã mở» không phải «đã đi qua»).
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
  // ⭐ ROUND 7 (WS-S) — LÝ DO cũng phải đổi, không chỉ nhãn. Câu cũ nói «đã đi
  // qua» (một tuyên bố về việc HỌC, dựng từ dấu vết MỞ TAB) rồi mời trẻ «về mục
  // lục chọn bài khác». Sửa nhãn mà để nguyên lý do thì màn hình vẫn nói đúng
  // câu đã sai — WS-R chữa hàng «Đã mở», đây chữa dòng ngay trên nó.
  return const NextAction(
    view: null,
    reason:
        'Con đã mở đủ ba cách học SAM có cho bài này. Mở không phải là đã '
        'hiểu — con xem lại cách nào con muốn cũng được.',
    basis: 'seen.all',
  );
}
