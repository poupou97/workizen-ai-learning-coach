/// ⭐ Lệnh 52 §5 — TAB SAM: điểm vào chính của AI Tutor, không phải «Chat».
///
/// Màn này KHÔNG dựng engine hội thoại mới và KHÔNG viết lại Camera Tutor. Nó
/// chỉ gom các đường vào SAM đang nằm rải rác thành MỘT gốc chuẩn (§5).
///
/// ⭐⭐ Lối vào nào CHƯA CÓ THẬT thì nói thẳng là chưa có. Repo này không có
/// package giọng nói nào, và cũng chưa có surface hỏi-tự-do. Làm hai cái nút
/// bấm-không-ra-gì là hứa với trẻ một thứ không tồn tại — cùng họ với luật
/// «không bịa nội dung» mà cả sản phẩm đang giữ. Nút chỉ sáng khi phía sau nó
/// có đường đi thật.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';

class SamHubScreen extends StatelessWidget {
  const SamHubScreen({
    super.key,
    this.learnerName,
    this.onCapture,
    this.onLearnWithSam,
    this.lessonLabel,
  });

  /// Tên trẻ để chào — `null` ⇒ chào chung, không bịa tên.
  final String? learnerName;

  /// 📷 Chụp bài — flow camera THẬT. `null` = máy không có camera/OCR.
  final VoidCallback? onCapture;

  /// 🦉 Học với SAM trên bài đang có workspace. `null` = lớp này chưa có bài.
  final VoidCallback? onLearnWithSam;

  /// Tên bài cho dòng phụ của «Học với SAM» — chỉ hiện khi có bài thật.
  final String? lessonLabel;

  static const captureKey = Key('sam-hub-capture');
  static const learnKey = Key('sam-hub-learn');

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: WalColors.surface,
    body: SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(WalSpacing.lg),
        children: [
          Row(
            children: [
              ClipOval(
                child: Image.asset(
                  'assets/mascot/sam-hello.png',
                  width: 56,
                  height: 56,
                  fit: BoxFit.cover,
                  errorBuilder: (_, _, _) =>
                      const SizedBox(width: 56, height: 56),
                ),
              ),
              const SizedBox(width: WalSpacing.md),
              const Expanded(
                child: Text(
                  'SAM',
                  style: TextStyle(
                    fontSize: WalType.display,
                    fontWeight: FontWeight.w700,
                    color: WalColors.ink,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: WalSpacing.sm),
          Text(
            learnerName == null
                ? 'Con muốn hỏi gì hôm nay?'
                : '$learnerName ơi, con muốn hỏi gì hôm nay?',
            style: const TextStyle(
              fontSize: WalType.body,
              color: WalColors.ink,
              height: 1.45,
            ),
          ),
          const SizedBox(height: WalSpacing.lg),

          if (onLearnWithSam != null)
            _action(
              key: learnKey,
              emoji: '🦉',
              title: 'Học với SAM',
              subtitle: lessonLabel ?? 'Bài SAM đã xếp sẵn từ sách của con',
              onTap: onLearnWithSam,
            ),

          _action(
            key: captureKey,
            emoji: '📷',
            title: 'Chụp bài',
            subtitle: onCapture == null
                // Nói LÝ DO, không chỉ làm mờ nút.
                ? 'Máy này chưa dùng được camera của SAM'
                : 'Chụp bài trong vở để SAM đọc cùng con',
            onTap: onCapture,
          ),

          // ⭐ Hai lối vào CHƯA TỒN TẠI trong repo. Hiện ra vì Founder đã
          // chốt chúng thuộc IA của tab SAM (§5), nhưng nói thật là chưa
          // có — không phải nút chết, không phải lời hứa.
          _action(
            emoji: '⌨️',
            title: 'Nhập câu hỏi',
            subtitle: 'SAM chưa nhận câu hỏi tự do — đang được xây',
            onTap: null,
          ),
          _action(
            emoji: '🎤',
            title: 'Hỏi bằng giọng nói',
            subtitle: 'Chưa có trên máy này — đang được xây',
            onTap: null,
          ),
        ],
      ),
    ),
  );

  Widget _action({
    Key? key,
    required String emoji,
    required String title,
    required String subtitle,
    VoidCallback? onTap,
  }) {
    final on = onTap != null;
    return Padding(
      padding: const EdgeInsets.only(bottom: WalSpacing.sm),
      child: Material(
        color: on ? Colors.white : WalColors.surfaceLavender,
        borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
        child: InkWell(
          key: key,
          borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.all(WalSpacing.lg),
            child: Row(
              children: [
                Text(emoji, style: const TextStyle(fontSize: 28)),
                const SizedBox(width: WalSpacing.md),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: TextStyle(
                          fontSize: WalType.body,
                          fontWeight: FontWeight.w700,
                          color: on ? WalColors.ink : WalColors.inkSoft,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        subtitle,
                        style: const TextStyle(
                          fontSize: WalType.secondary,
                          color: WalColors.inkSoft,
                          height: 1.35,
                        ),
                      ),
                    ],
                  ),
                ),
                if (on)
                  const Icon(Icons.chevron_right, color: WalColors.inkSoft),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
