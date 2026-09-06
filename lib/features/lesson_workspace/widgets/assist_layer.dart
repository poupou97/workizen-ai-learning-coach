/// ROUND 5 · Lane B — LỚP TRỢ GIÚP NGỮ CẢNH của SAM (thay thẻ đề xuất thường trực).
///
/// PHẢN HỒI FOUNDER trên máy thật: workspace «lặp lại, tốn chiều dọc, quá nhiều
/// hiện diện của cùng ba Learning View, thẻ đề xuất chiếm chỗ thường trực, CTA
/// lặp lại điều hướng đã thấy». Đo được (`workspace_density_test`, khung Nokia
/// 392.7×698.2 dp): chrome ghim 225 dp ở Đọc/Trực quan và **411 dp ở Học với
/// SAM (58.9 % màn)**; ba tên View xuất hiện 6–7 lần trên MỘT màn.
///
/// ⚠ ĐÂY LÀ TRÌNH BÀY, KHÔNG PHẢI ĐỘNG CƠ THỨ HAI. Lớp này nhận MỘT
/// `NextAction` đã dựng sẵn (`Student State + Learning Context + Pedagogy
/// Runtime → Next Action`) và không được phép tự nghĩ ra đề xuất: nó không
/// nhận `LessonDocument`, không nhận trace, không tính gì. Có test cấm.
///
/// ⚠ KHÔNG GIẤU — hé dần. Thông tin chính (bài, View đang mở, nội dung) luôn
/// thấy; ĐỀ XUẤT luôn có mặt ở dạng nhìn thấy được; LÝ DO mở theo yêu cầu.
/// «AI-first» không được biến mất: mọi phương án đều phải trả lời được
/// «ứng dụng biết mình đang ở đâu và đề xuất gì tiếp theo» — nên phương án
/// chỉ-biểu-tượng vẫn mang nhãn trợ năng đầy đủ và một chấm báo khi có đề
/// xuất mới, và ba phương án được đo bằng CÙNG một bộ số.
///
/// ⚠ KỶ LUẬT LINH VẬT: 🦉/chân dung SAM dành cho lúc SAM THỰC SỰ nói (Học với
/// SAM, bong bóng thoại, thẻ kết). Một GỢI Ý dùng 💡. Mục tiêu là SAM có mặt
/// ĐÚNG LÚC hơn, không phải ít hơn.
library;

import 'package:flutter/material.dart';

import '../../../app/theme/wal_tokens.dart';
import '../../../core/lesson_model/next_action.dart';

/// Bốn cách trình bày cùng một `NextAction` — chọn lúc build bằng
/// `--dart-define=WAL_ASSIST=icon|peek|inlineTab` (mặc định `card` = bản vòng
/// 4/5 đang chạy). Sản phẩm KHÔNG có nút đổi: so sánh A/B là việc của người
/// dựng bản, không phải của trẻ.
enum AssistPresentation {
  /// HIỆN TẠI: thẻ mở sẵn, thường trực (chân dung + lý do + CTA + hàng «Đã mở»).
  card,

  /// A — chỉ biểu tượng 💡 ở đầu màn; chạm ⇒ bottom sheet có lý do + một CTA.
  icon,

  /// B — một dòng «💡 SAM gợi ý: Xem Trực quan →»; chạm ⇒ mở tại chỗ.
  peek,

  /// C — 💡 gắn ngay trên TAB đích; chạm huy hiệu ⇒ một dòng «vì sao».
  inlineTab;

  static const _flag = String.fromEnvironment('WAL_ASSIST', defaultValue: '');

  /// CHỈ cho test và cho phép đo A/B trong cùng một lần chạy. Đường sản phẩm
  /// là `--dart-define`; không có UI nào đặt được biến này.
  @visibleForTesting
  static AssistPresentation? debugOverride;

  /// Phương án của bản build này.
  static AssistPresentation get current => debugOverride ?? parse(_flag);

  static AssistPresentation parse(String s) => switch (s.trim()) {
    'icon' => AssistPresentation.icon,
    'peek' => AssistPresentation.peek,
    'inlineTab' || 'inline' => AssistPresentation.inlineTab,
    _ => AssistPresentation.card,
  };

  String get flagName => switch (this) {
    AssistPresentation.card => 'card',
    AssistPresentation.icon => 'icon',
    AssistPresentation.peek => 'peek',
    AssistPresentation.inlineTab => 'inlineTab',
  };
}

/// Ba trạng thái của lớp trợ giúp. Chuyển trạng thái là việc của màn chứa nó.
enum AssistState {
  /// Chỉ dấu hiệu (💡) — vẫn NHÌN THẤY, không phải bị giấu.
  collapsed,

  /// Một dòng nói rõ ĐI ĐÂU: «💡 SAM gợi ý: Xem Trực quan →».
  peek,

  /// Mở đủ: vì sao + một CTA + «Để sau».
  expanded,
}

/// Chữ trẻ đọc — dùng chung cho cả bốn phương án nên không lệch giọng.
abstract final class AssistCopy {
  static const title = 'Gợi ý của SAM';
  static const dismiss = 'Để sau';
  static const why = 'Vì sao?';

  /// «💡 SAM gợi ý: Xem Trực quan» — nêu ĐÍCH ĐẾN, không chỉ nói «có gợi ý».
  static String peekLine(NextAction a) => a.view == null
      ? 'SAM gợi ý: ${a.label}'
      : 'SAM gợi ý: Xem ${a.view!.label}';

  /// Nhãn trợ năng: biểu tượng 💡 một mình KHÔNG đủ cho trình đọc màn hình.
  static String semanticLabel(NextAction a, AssistState s) =>
      '$title: ${a.view == null ? a.label : 'xem ${a.view!.label}'}'
      '${s == AssistState.expanded ? ' — đang mở' : ''}';

  static String semanticHint(AssistState s) => switch (s) {
    AssistState.expanded => 'Chạm để thu gọn gợi ý',
    _ => 'Chạm để xem vì sao SAM gợi ý',
  };
}

/// A — 💡 một mình. Đặt trong hàng đã có (không tốn dòng nào).
class AssistIconButton extends StatelessWidget {
  const AssistIconButton({
    super.key,
    required this.action,
    required this.onOpen,
    this.unseen = true,
  });

  final NextAction action;
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

/// B — dòng hé: «💡 SAM gợi ý: Xem Trực quan →», chạm mở tại chỗ.
/// C dùng lại phần MỞ RỘNG của B, nên hai phương án chỉ khác chỗ đặt dấu hiệu.
class AssistPeek extends StatelessWidget {
  const AssistPeek({
    super.key,
    required this.action,
    required this.state,
    required this.onToggle,
    required this.onGo,
    required this.onDismiss,
  });

  final NextAction action;
  final AssistState state;
  final VoidCallback onToggle;
  final VoidCallback onGo;
  final VoidCallback onDismiss;

  static const peekKey = Key('assist-peek');
  static const expandedKey = Key('assist-expanded');
  static const goKey = Key('assist-go');
  static const dismissKey = Key('assist-dismiss');

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
        const SizedBox(height: WalSpacing.xs),
        Row(
          children: [
            SizedBox(
              height: WalSpacing.minTouch - 8,
              child: FilledButton(
                key: goKey,
                style: FilledButton.styleFrom(
                  backgroundColor: WalColors.primary500,
                  padding: const EdgeInsets.symmetric(
                    horizontal: WalSpacing.md,
                  ),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
                  ),
                ),
                onPressed: onGo,
                child: Text(
                  action.label,
                  style: const TextStyle(
                    fontSize: WalType.secondary,
                    fontWeight: FontWeight.w700,
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

/// A — nội dung của bottom sheet «Gợi ý của SAM».
Future<void> showAssistSheet(
  BuildContext context, {
  required NextAction action,
  required VoidCallback onGo,
}) => showModalBottomSheet<void>(
  context: context,
  backgroundColor: Colors.white,
  shape: const RoundedRectangleBorder(
    borderRadius: BorderRadius.vertical(top: Radius.circular(WalSpacing.lg)),
  ),
  builder: (ctx) => SafeArea(
    child: Padding(
      key: const Key('assist-sheet'),
      padding: const EdgeInsets.all(WalSpacing.lg),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '💡 ${AssistCopy.title}',
            style: TextStyle(
              fontSize: WalType.title,
              fontWeight: FontWeight.w700,
              color: WalColors.ink,
            ),
          ),
          const SizedBox(height: WalSpacing.sm),
          Text(
            action.reason,
            style: const TextStyle(
              fontSize: WalType.body,
              color: WalColors.ink,
              height: 1.4,
            ),
          ),
          const SizedBox(height: WalSpacing.md),
          Row(
            children: [
              Expanded(
                child: SizedBox(
                  height: WalSpacing.minTouch,
                  child: FilledButton(
                    key: AssistPeek.goKey,
                    style: FilledButton.styleFrom(
                      backgroundColor: WalColors.primary500,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(
                          WalSpacing.radiusButton,
                        ),
                      ),
                    ),
                    onPressed: () {
                      Navigator.of(ctx).pop();
                      onGo();
                    },
                    child: Text(
                      action.label,
                      style: const TextStyle(
                        fontSize: WalType.body,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: WalSpacing.sm),
              SizedBox(
                height: WalSpacing.minTouch,
                child: TextButton(
                  key: AssistPeek.dismissKey,
                  onPressed: () => Navigator.of(ctx).pop(),
                  child: const Text(
                    AssistCopy.dismiss,
                    style: TextStyle(
                      fontSize: WalType.body,
                      color: WalColors.primaryText,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    ),
  ),
);
