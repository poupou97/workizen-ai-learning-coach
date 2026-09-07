/// WAL-152 (§19) — PERSON DETAIL: chỉ những gì CÓ TRONG KHO GIÁO DỤC —
/// không Wikipedia clone, không bịa tiểu sử.
///
/// ⭐⭐ Lệnh 59 §P2 — MÀN NÀY MỚI LÀ NƠI TRẺ ĐI TÌM KHUÔN MẶT.
///
/// Máy thật chỉ ra điều mà đọc code không thấy: chân dung đã xác minh nằm
/// trong `PersonPortraits` nhưng KHÔNG hiện ở đâu cả. Người dùng duy nhất của
/// kho ấy là [QuoteCard], mà thẻ ấy chỉ dựng khi `type == 'QUOTE'` — trong khi
/// cả 21 `personId` của kho đều thuộc chuyện `PERSON`, và 2 chuyện `QUOTE` duy
/// nhất lại KHÔNG có `personId`. Giao của hai tập là RỖNG.
///
/// Nên ảnh đúng người, đúng giấy phép, đúng lai lịch vẫn không tới được mắt
/// trẻ — nó chỉ tồn tại trong test. Màn này đóng khoảng trống đó.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/stories/person_portrait.dart';
import '../../core/stories/stories_store.dart';
import '../lesson_workspace/learning_image_viewer.dart';
import 'story_detail_screen.dart';
import '../subjects/subject_display.dart';

class PersonDetailScreen extends StatelessWidget {
  const PersonDetailScreen({
    super.key,
    required this.personId,
    required this.stories,
  });

  final String personId;
  final StoriesStore stories;

  @override
  Widget build(BuildContext context) {
    final p = stories.person(personId);
    final items = stories.byPerson(personId);
    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: p == null
            ? const Center(
                child: Text(
                  'Chưa có thông tin về nhân vật này trong kho.',
                  style: TextStyle(
                    fontSize: WalType.body,
                    color: WalColors.inkSoft,
                  ),
                ),
              )
            : ListView(
                padding: const EdgeInsets.all(WalSpacing.lg),
                children: [
                  _header(context, p.name),
                  const SizedBox(height: WalSpacing.sm),
                  Text(
                    p.name,
                    style: const TextStyle(
                      fontSize: WalType.display,
                      fontWeight: FontWeight.w700,
                      color: WalColors.ink,
                    ),
                  ),
                  Text(
                    [
                      if (p.birthYear != null)
                        '${p.birthYear}–${p.deathYear ?? "?"}',
                      'Xuất hiện trong: ${p.subjects.join(", ")}',
                    ].join(' · '),
                    style: const TextStyle(
                      fontSize: WalType.secondary,
                      color: WalColors.inkSoft,
                    ),
                  ),
                  const SizedBox(height: WalSpacing.md),
                  const Text(
                    'TRONG SÁCH CỦA CON',
                    style: TextStyle(
                      fontSize: WalType.secondary,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 1.05,
                      color: WalColors.inkSoft,
                    ),
                  ),
                  const SizedBox(height: WalSpacing.sm),
                  for (final i in items)
                    Padding(
                      padding: const EdgeInsets.only(bottom: WalSpacing.sm),
                      child: Material(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(
                          WalSpacing.radiusChip,
                        ),
                        child: ListTile(
                          title: Text(
                            i.title,
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(
                              fontSize: WalType.body,
                              fontWeight: FontWeight.w600,
                              color: WalColors.ink,
                            ),
                          ),
                          subtitle: Text(
                            storySourceLine(
                              sourceDocumentId: i.sourceDocumentId,
                              pagePdf: i.pagePdf,
                            ),
                            style: const TextStyle(
                              fontSize: WalType.secondary,
                              color: WalColors.inkSoft,
                            ),
                          ),
                          onTap: () => Navigator.of(context).push(
                            MaterialPageRoute(
                              builder: (_) =>
                                  StoryDetailScreen(item: i, stories: stories),
                            ),
                          ),
                        ),
                      ),
                    ),
                  TextButton(
                    onPressed: () => Navigator.of(context).pop(),
                    child: const Text(
                      '◂ Quay lại',
                      style: TextStyle(
                        fontSize: WalType.body,
                        color: WalColors.primaryText,
                      ),
                    ),
                  ),
                ],
              ),
      ),
    );
  }

  /// Có chân dung đủ điều kiện ⇒ ảnh thật; không có ⇒ chữ cái đầu như cũ.
  ///
  /// Nhánh KHÔNG ẢNH là trạng thái BÌNH THƯỜNG của 20/21 nhân vật, không phải
  /// lỗi — nên nó vẫn phải trông tử tế (§P2.7).
  Widget _header(BuildContext context, String name) {
    final pt = PersonPortraits.forPerson(personId);
    if (pt == null) {
      return CircleAvatar(
        key: initialAvatarKey,
        radius: 36,
        backgroundColor: WalColors.surfaceLavender,
        child: Text(
          name.characters.first,
          style: const TextStyle(
            fontSize: 30,
            fontWeight: FontWeight.w700,
            color: WalColors.primaryText,
          ),
        ),
      );
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Chạm ⇒ xem to, cùng cửa với mọi ảnh khác trong bài (§P0). KHÔNG
        // `bleedScale`: ảnh này đã cắt sạch, không có mép chữ để che.
        InkWell(
          onTap: () => showLearningImage(
            context,
            asset: pt.assetPath,
            aspect: 72 / 88,
            caption: pt.personName,
            sourceLine: '${pt.sourceName} · ${pt.licence}',
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(WalSpacing.radiusBookCover),
            child: Image.asset(
              pt.assetPath,
              key: portraitKey,
              width: 108,
              height: 132,
              fit: BoxFit.cover,
              // Ảnh hỏng ⇒ quay về chữ cái đầu, không để lỗ đen trên màn.
              errorBuilder: (_, _, _) => CircleAvatar(
                key: initialAvatarKey,
                radius: 36,
                backgroundColor: WalColors.surfaceLavender,
                child: Text(
                  name.characters.first,
                  style: const TextStyle(
                    fontSize: 30,
                    fontWeight: FontWeight.w700,
                    color: WalColors.primaryText,
                  ),
                ),
              ),
            ),
          ),
        ),
        const SizedBox(height: WalSpacing.xs),
        // §P2.6 — ảnh là một sự thật RIÊNG nên nó mang lai lịch riêng, không
        // núp sau nguồn của bài. Trẻ đọc được ĐÂY LÀ LOẠI ẢNH GÌ, ở đâu ra.
        Text(
          '${pt.portraitType.label} · ${pt.sourceName} · ${pt.licence}',
          key: provenanceKey,
          style: const TextStyle(fontSize: 12, color: WalColors.inkSoft),
        ),
      ],
    );
  }

  static const portraitKey = Key('person-detail-portrait');
  static const initialAvatarKey = Key('person-detail-initial');
  static const provenanceKey = Key('person-detail-portrait-provenance');
}
