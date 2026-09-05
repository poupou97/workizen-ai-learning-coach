/// ROUND 3 B1 — «VÀO BÀI HỌC»: chọn cách học (concept learning-view khung 3).
///
/// Lần ĐẦU mở một bài trong phiên, thay vì rơi thẳng vào một View, trẻ thấy
/// ba tấm thẻ [1 Đọc như sách] [2 Trực quan hoá] [3 Học cùng SAM] — mỗi thẻ
/// nói bài này CÓ GÌ theo cách đó (đếm từ dữ liệu bài, không bịa), và thẻ SAM
/// đề xuất mang lý do. Đây là chỗ Founder cầm máy thấy ngay câu 3 («học được
/// bằng những cách nào») và câu 5 («vì sao SAM đề xuất cách đó»).
///
/// Không có trạng thái, không ghi gì: chạm thẻ ⇒ [onPick] — tầng trên đổi View.
library;

import 'package:flutter/material.dart';

import '../../../app/theme/band_density_scope.dart';
import '../../../app/theme/wal_tokens.dart';
import '../../../core/lesson_model/lesson_document.dart';
import '../../../core/lesson_model/next_action.dart';

class ModePicker extends StatelessWidget {
  const ModePicker({
    super.key,
    required this.doc,
    required this.proposal,
    required this.onPick,
  });

  final LessonDocument doc;
  final NextAction proposal;
  final void Function(WorkspaceView view) onPick;

  static Key cardKey(WorkspaceView v) => Key('workspace-pick-${v.name}');

  /// Dòng «bài này có gì theo cách này» — ĐẾM từ dữ liệu, không hứa.
  static String describe(LessonDocument doc, WorkspaceView v) {
    switch (v) {
      case WorkspaceView.read:
        final p = doc.blocks.whereType<ParagraphBlock>().length;
        final i = doc.blocks.whereType<ImageBlock>().length;
        final q = doc.blocks.whereType<QuestionBlock>().length;
        final w = doc.blocks.whereType<WithheldBlock>().length;
        final parts = [
          if (p > 0) '$p đoạn',
          if (i > 0) '$i hình',
          if (q > 0) '$q câu hỏi trong sách',
        ];
        final base = parts.isEmpty
            ? 'Đọc như trong sách'
            : 'Như trong sách · ${parts.join(' · ')}';
        return w > 0 ? '$base · $w chỗ SAM để trống' : base;
      case WorkspaceView.visual:
        if (doc.semantic.isEmpty) {
          return 'Chưa có sơ đồ cho bài này — chỉ có bảng tóm tắt lời sách';
        }
        final counts = <String, int>{};
        for (final s in doc.semantic) {
          counts[s.shapeLabel] = (counts[s.shapeLabel] ?? 0) + 1;
        }
        return [
          for (final e in counts.entries)
            e.value > 1 ? '${e.key} ×${e.value}' : e.key,
          'Bảng tóm tắt',
        ].join(' · ');
      case WorkspaceView.tutor:
        final s = doc.tutorScript;
        if (s == null) return 'Chưa có kịch bản cho bài này';
        final n = s.asks.length;
        return 'SAM giải thích, hỏi $n câu trong sách, gợi ý khi con cần '
            '(kịch bản thử nghiệm)';
    }
  }

  static String _tagline(WorkspaceView v) => switch (v) {
    WorkspaceView.read => 'Đọc như sách',
    WorkspaceView.visual => 'Trực quan hoá',
    WorkspaceView.tutor => 'Học cùng SAM',
  };

  @override
  Widget build(BuildContext context) {
    final size = densityOf(context).mascotChip;
    return SingleChildScrollView(
      key: const Key('mode-picker'),
      padding: const EdgeInsets.fromLTRB(
        WalSpacing.md,
        WalSpacing.sm,
        WalSpacing.md,
        WalSpacing.xl,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Image.asset(
                'assets/mascot/sam-probe.png',
                width: size,
                height: size,
                errorBuilder: (_, _, _) => SizedBox(width: size, height: size),
              ),
              const SizedBox(width: WalSpacing.sm),
              Expanded(
                child: Container(
                  padding: const EdgeInsets.all(WalSpacing.md),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
                  ),
                  child: const Text(
                    'Con muốn học bài này theo cách nào? Mỗi cách giúp con '
                    'hiểu bài theo một góc nhìn khác nhau nhé.',
                    style: TextStyle(
                      fontSize: WalType.body,
                      color: WalColors.ink,
                      height: 1.45,
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: WalSpacing.md),
          for (var i = 0; i < WorkspaceView.values.length; i++) ...[
            _card(WorkspaceView.values[i], i + 1),
            const SizedBox(height: WalSpacing.sm),
          ],
        ],
      ),
    );
  }

  Widget _card(WorkspaceView v, int n) {
    final proposed = proposal.view == v;
    return Material(
      color: proposed ? WalColors.surfaceLavender : Colors.white,
      borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
      child: InkWell(
        key: ModePicker.cardKey(v),
        onTap: () => onPick(v),
        borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
        child: Container(
          padding: const EdgeInsets.all(WalSpacing.md),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
            border: proposed
                ? Border.all(color: WalColors.primary500, width: 2)
                : null,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    width: 40,
                    height: 40,
                    alignment: Alignment.center,
                    decoration: BoxDecoration(
                      color: proposed
                          ? WalColors.primary500
                          : WalColors.surfaceLavender,
                      shape: BoxShape.circle,
                    ),
                    child: Text(
                      '$n',
                      style: TextStyle(
                        fontSize: WalType.body,
                        fontWeight: FontWeight.w700,
                        color: proposed ? Colors.white : WalColors.primaryText,
                      ),
                    ),
                  ),
                  const SizedBox(width: WalSpacing.sm),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '${v.icon} ${_tagline(v)}',
                          style: const TextStyle(
                            fontSize: WalType.title - 2,
                            fontWeight: FontWeight.w700,
                            color: WalColors.ink,
                          ),
                        ),
                        Text(
                          describe(doc, v),
                          style: const TextStyle(
                            fontSize: WalType.secondary,
                            color: WalColors.inkSoft,
                            height: 1.35,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const Icon(
                    Icons.chevron_right,
                    color: WalColors.primaryText,
                  ),
                ],
              ),
              if (proposed) ...[
                const SizedBox(height: WalSpacing.sm),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(WalSpacing.sm),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        '🦉 SAM đề xuất cách này — vì sao?',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w700,
                          color: WalColors.primaryText,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        proposal.reason,
                        style: const TextStyle(
                          fontSize: 13,
                          color: WalColors.ink,
                          height: 1.35,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
