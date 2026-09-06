/// ROUND 6 · WS-D — LỚP TRỢ GIÚP NGỮ CẢNH của SAM: **PHƯƠNG ÁN B ĐÃ CHỌN**.
///
/// Vòng 5 dựng BỐN cách trình bày cùng một `NextAction` từ MỘT commit
/// (`--dart-define=WAL_ASSIST=card|icon|peek|inlineTab`) và đo cả bốn trên
/// Nokia 6.1 thật. **Founder chọn B.** Vòng 6 thi hành quyết định đó: bản
/// dựng chỉ còn MỘT cách trình bày, cờ build đã gỡ, ba phương án kia đã xoá.
/// Số đo lịch sử của A/B/C nằm ở `docs/design/TRACK-B-ROUND5-WORKSPACE-
/// DUPLICATION.md` §5 và tái dựng được ở nhánh vòng 5 (`lane-b/round5-
/// experience`, PR #87) — KHÔNG tái dựng được ở nhánh này, và đó là chủ ý.
///
/// B = MỘT dòng gọn mặc định + hai trạng thái nữa:
///
///   COLLAPSED  💡 trong hàng tiêu đề (0 dòng)          ← sau «Để sau»
///   PEEK       «💡 SAM gợi ý: Xem Đọc →» (1 dòng)      ← MẶC ĐỊNH
///   EXPANDED   vì sao + CTA + «Để sau» + «Đã mở …»     ← trẻ chạm mới mở
///
/// Đề xuất chuyển sang View KHÁC ⇒ hé lại một lần (việc của màn chứa, không
/// phải của widget này).
///
/// ⚠ ĐÂY LÀ TRÌNH BÀY, KHÔNG PHẢI ĐỘNG CƠ THỨ HAI. Lớp này nhận MỘT
/// `NextAction` đã dựng sẵn (`Student State + Learning Context + Pedagogy
/// Runtime → Next Action`) và không được phép tự nghĩ ra đề xuất: nó không
/// nhận tài liệu bài, không nhận trace, không tính gì. Có test soi mã cấm.
/// Dòng «Đã mở …» cũng đi vào đây dưới dạng MỘT CHUỖI đã dựng sẵn — lớp này
/// không được tự hỏi trace xem trẻ đã mở gì.
///
/// ⚠ KHÔNG GIẤU — hé dần. Thông tin chính (bài, View đang mở, nội dung) luôn
/// thấy; ĐỀ XUẤT luôn có mặt ở dạng nhìn thấy được **ở cả ba View**; LÝ DO mở
/// theo yêu cầu. Trạng thái thu gọn vẫn còn 💡 (lỗi D5 đo trên máy vòng 5:
/// «Để sau» từng làm SAM biến mất hoàn toàn).
///
/// ⚠ KỶ LUẬT LINH VẬT: 🦉/chân dung SAM dành cho lúc SAM THỰC SỰ nói (Học với
/// SAM, bong bóng thoại, thẻ kết). Một GỢI Ý dùng 💡.
library;

import 'package:flutter/material.dart';

import '../../../app/theme/wal_tokens.dart';
import '../../../core/agenda/lesson_next_action.dart';

/// Ba trạng thái của lớp trợ giúp. Chuyển trạng thái là việc của màn chứa nó.
enum AssistState {
  /// Chỉ dấu hiệu (💡) — vẫn NHÌN THẤY, không phải bị giấu.
  collapsed,

  /// Một dòng nói rõ ĐI ĐÂU: «💡 SAM gợi ý: Xem Trực quan →». MẶC ĐỊNH.
  peek,

  /// Mở đủ: vì sao + một CTA + «Để sau» + dòng «Đã mở».
  expanded,
}

/// Chữ trẻ đọc — một giọng duy nhất cho cả ba trạng thái.
abstract final class AssistCopy {
  static const title = 'Gợi ý của SAM';
  static const dismiss = 'Để sau';
  static const why = 'Vì sao?';

  /// «💡 SAM gợi ý: Xem Trực quan» — nêu ĐÍCH ĐẾN, không chỉ nói «có gợi ý».
  static String peekLine(LessonNextAction a) => a.view == null
      ? 'SAM gợi ý: ${a.label}'
      : 'SAM gợi ý: Xem ${a.view!.label}';

  /// Nhãn trợ năng: biểu tượng 💡 một mình KHÔNG đủ cho trình đọc màn hình.
  static String semanticLabel(LessonNextAction a, AssistState s) =>
      '$title: ${a.view == null ? a.label : 'xem ${a.view!.label}'}'
      '${s == AssistState.expanded ? ' — đang mở' : ''}';

  static String semanticHint(AssistState s) => switch (s) {
    AssistState.expanded => 'Chạm để thu gọn gợi ý',
    _ => 'Chạm để xem vì sao SAM gợi ý',
  };
}

/// COLLAPSED — 💡 một mình, đặt trong hàng tiêu đề đã có (không tốn dòng nào).
class AssistIconButton extends StatelessWidget {
  const AssistIconButton({
    super.key,
    required this.action,
    required this.onOpen,
    this.unseen = true,
  });

  final LessonNextAction action;
  final VoidCallback onOpen;

  /// Chấm báo «có gợi ý con chưa xem» — để 💡 không thành đồ trang trí chết.
  final bool unseen;

  static const buttonKey = Key('assist-icon');

  @override
  Widget build(BuildContext context) => Semantics(
    button: true,
    label: AssistCopy.semanticLabel(action, AssistState.collapsed),
    hint: AssistCopy.semanticHint(AssistState.collapsed),
    child: SizedBox(
      width: WalSpacing.minTouch,
      height: WalSpacing.minTouch,
      child: IconButton(
        key: buttonKey,
        tooltip: AssistCopy.title,
        onPressed: onOpen,
        icon: Stack(
          clipBehavior: Clip.none,
          children: [
            const Text('💡', style: TextStyle(fontSize: 22)),
            if (unseen)
              Positioned(
                right: -2,
                top: -1,
                child: Container(
                  width: 9,
                  height: 9,
                  decoration: const BoxDecoration(
                    color: WalColors.primary500,
                    shape: BoxShape.circle,
                  ),
                ),
              ),
          ],
        ),
      ),
    ),
  );
}

/// PEEK + EXPANDED — «💡 SAM gợi ý: Xem Trực quan →», chạm mở TẠI CHỖ.
class AssistPeek extends StatelessWidget {
  const AssistPeek({
    super.key,
    required this.action,
    required this.state,
    required this.onToggle,
    required this.onGo,
    required this.onDismiss,
    this.seenLine,
  });

  final LessonNextAction action;
  final AssistState state;
  final VoidCallback onToggle;
  final VoidCallback onGo;
  final VoidCallback onDismiss;

  /// «Đã mở: ● Đọc ○ Trực quan ○ Học với SAM» — CHUỖI đã dựng sẵn bởi màn
  /// chứa. Vòng 5 xếp dòng này vào nhóm «gộp được vào lớp trợ giúp» (bản đồ
  /// trùng lặp §2 mục 11): nó là DẤU VẾT PHIÊN, không phải bằng chứng học,
  /// nên chỉ hiện khi trẻ đã chủ động hỏi «vì sao».
  /// `null` ⇒ không có gì để nói.
  final String? seenLine;

  static const peekKey = Key('assist-peek');
  static const expandedKey = Key('assist-expanded');
  static const goKey = Key('assist-go');
  static const dismissKey = Key('assist-dismiss');
  static const seenKey = Key('assist-seen-row');

  @override
  Widget build(BuildContext context) =>
      state == AssistState.expanded ? _expanded(context) : _peek(context);

  Widget _peek(BuildContext context) => Semantics(
    button: true,
    label: AssistCopy.semanticLabel(action, AssistState.peek),
    hint: AssistCopy.semanticHint(AssistState.peek),
    child: Material(
      color: WalColors.surfaceLavender,
      borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
      child: InkWell(
        key: peekKey,
        borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
        onTap: onToggle,
        child: Container(
          constraints: const BoxConstraints(minHeight: WalSpacing.minTouch),
          padding: const EdgeInsets.symmetric(horizontal: WalSpacing.sm),
          child: Row(
            children: [
              const Text('💡', style: TextStyle(fontSize: 16)),
              const SizedBox(width: 6),
              Expanded(
                child: Text(
                  AssistCopy.peekLine(action),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    fontSize: WalType.secondary,
                    fontWeight: FontWeight.w600,
                    color: WalColors.primaryText,
                  ),
                ),
              ),
              const Icon(
                Icons.expand_more,
                size: 20,
                color: WalColors.primaryText,
              ),
            ],
          ),
        ),
      ),
    ),
  );

  Widget _expanded(BuildContext context) => Container(
    key: expandedKey,
    padding: const EdgeInsets.all(WalSpacing.sm),
    decoration: BoxDecoration(
      color: WalColors.surfaceLavender,
      borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        Semantics(
          button: true,
          label: AssistCopy.semanticLabel(action, AssistState.expanded),
          hint: AssistCopy.semanticHint(AssistState.expanded),
          child: InkWell(
            onTap: onToggle,
            child: Row(
              children: [
                const Text('💡', style: TextStyle(fontSize: 16)),
                const SizedBox(width: 6),
                const Expanded(
                  child: Text(
                    AssistCopy.title,
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                      color: WalColors.primaryText,
                    ),
                  ),
                ),
                const Icon(
                  Icons.expand_less,
                  size: 20,
                  color: WalColors.primaryText,
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 2),
        Text(
          action.reason,
          style: const TextStyle(
            fontSize: 13,
            color: WalColors.ink,
            height: 1.35,
          ),
        ),
        if (seenLine != null)
          Padding(
            padding: const EdgeInsets.only(top: 4),
            child: Text(
              seenLine!,
              key: seenKey,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(fontSize: 11, color: WalColors.inkSoft),
            ),
          ),
        const SizedBox(height: WalSpacing.xs),
        Row(
          children: [
            // ROUND 6 (lỗi test bắt được, chưa từng lộ ở vòng 5): nhãn CTA
            // dài nhất — «🦉 Học với SAM» — làm hàng nút TRÀN 2.2 px ở khung
            // Nokia. Vòng 5 chỉ mở EXPANDED khi đích là «✨ Trực quan» nên
            // không chạm phải. `Flexible` + cắt một dòng: vùng chạm vẫn 40 dp
            // cao, cả hàng vẫn vừa mọi bề ngang.
            Flexible(
              child: SizedBox(
                height: WalSpacing.minTouch - 8,
                child: FilledButton(
                  key: goKey,
                  style: FilledButton.styleFrom(
                    backgroundColor: WalColors.primary500,
                    padding: const EdgeInsets.symmetric(
                      horizontal: WalSpacing.md,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(
                        WalSpacing.radiusChip,
                      ),
                    ),
                  ),
                  onPressed: onGo,
                  child: Text(
                    action.label,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontSize: WalType.secondary,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ),
            ),
            const SizedBox(width: WalSpacing.xs),
            SizedBox(
              height: WalSpacing.minTouch - 8,
              child: TextButton(
                key: dismissKey,
                onPressed: onDismiss,
                child: const Text(
                  AssistCopy.dismiss,
                  style: TextStyle(
                    fontSize: WalType.secondary,
                    color: WalColors.primaryText,
                  ),
                ),
              ),
            ),
          ],
        ),
      ],
    ),
  );
}
