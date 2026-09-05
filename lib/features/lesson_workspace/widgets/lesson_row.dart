/// TRACK B ROUND 5 — HÀNG BÀI dùng chung cho màn Chương và tab «Bài học» của
/// màn Sách (concept-chuong khung 3 có ĐÚNG hai tab «Chương | Bài học»).
///
/// Tách ra để MỘT vốn từ duy nhất chạy suốt giá sách → sách → chương: cùng
/// «✨ Bài học SAM · 3 cách học · Chưa xem», cùng luật màu (có Bài học SAM =
/// nền nhấn — lỗi vòng 4 D2 đã sửa và không được phép quay lại ở màn thứ hai),
/// cùng «Đã xem (phiên này)» đọc từ trace. Không sao, không %, không «đã học».
library;

import 'package:flutter/material.dart';

import '../../../app/theme/wal_tokens.dart';
import '../../../core/lesson_model/lesson_document.dart';
import '../../../core/lesson_model/next_action.dart' show WorkspaceView;
import '../../subjects/lesson_index.dart';
import '../lesson_workspace_screen.dart';
import '../workspace_trace.dart';

class LessonRow extends StatelessWidget {
  const LessonRow({
    super.key,
    required this.lesson,
    required this.doc,
    required this.trace,
    required this.onOpenLegacy,
    this.learnerId,
  });

  final LessonRef lesson;

  /// `null` ⇒ bài chưa có Lesson Workspace: nói thật, dẫn về đường cũ.
  final LessonDocument? doc;
  final WorkspaceTrace trace;
  final VoidCallback onOpenLegacy;
  final String? learnerId;

  static Key keyFor(int lessonNo) => Key('lesson-row-$lessonNo');

  /// Trạng thái bài bằng lời trẻ, CHỈ từ trace (đã mở cách nào trong phiên).
  static String stateLine(WorkspaceTrace trace, LessonDocument doc) {
    final seen = trace.viewsFor(doc.slotKey);
    final ways = WorkspaceView.values.length;
    if (!trace.opened(doc.slotKey)) {
      return '$ways cách học · ${trace.childLabel(doc.slotKey)}';
    }
    if (seen.isEmpty) return trace.childLabel(doc.slotKey);
    final names = [
      for (final v in WorkspaceView.values)
        if (seen.contains(v)) v.label,
    ];
    return '${trace.childLabel(doc.slotKey)}: ${names.join(' · ')}';
  }

  @override
  Widget build(BuildContext context) {
    final title = lesson.title == null
        ? 'Bài ${lesson.no}'
        : 'Bài ${lesson.no} · ${LessonDocument.titleCase(lesson.title!)}';
    final opened = doc != null && trace.opened(doc!.slotKey);
    return Padding(
      padding: const EdgeInsets.only(bottom: WalSpacing.sm),
      child: Material(
        // ⭐ ROUND 4 (lỗi nhìn thấy trên Nokia): nền tím oải hương là NHẤN
        // MẠNH — Home dùng nó cho thẻ chính. Một vốn từ màu cho cả hành trình
        // ⇒ có Bài học SAM = nền nhấn.
        color: doc != null ? WalColors.surfaceLavender : Colors.white,
        borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
        child: ListTile(
          key: keyFor(lesson.no),
          minVerticalPadding: WalSpacing.sm,
          title: Text(
            title,
            style: const TextStyle(
              fontSize: WalType.body,
              fontWeight: FontWeight.w600,
              color: WalColors.ink,
            ),
          ),
          subtitle: Text(
            doc != null
                ? '✨ Bài học SAM · ${stateLine(trace, doc!)}'
                : 'Chưa có Bài học SAM — mở trong Môn học',
            style: TextStyle(
              fontSize: WalType.secondary,
              color: opened ? WalColors.primaryText : WalColors.inkSoft,
            ),
          ),
          trailing: Icon(
            doc != null ? Icons.chevron_right : Icons.open_in_new,
            color: WalColors.primaryText,
          ),
          onTap: () async {
            final d = doc;
            if (d == null) {
              onOpenLegacy();
              return;
            }
            await Navigator.of(context).push(
              MaterialPageRoute(
                builder: (_) => LessonWorkspaceScreen(
                  doc: d,
                  trace: trace,
                  learnerId: learnerId,
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}
