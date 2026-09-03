/// WAL-143 × WAL-109 — XÁC NHẬN ĐÚNG NGƯỜI trước khi ghi bằng chứng thi.
///
/// DEVICE ≠ USER: một máy giữ nhiều hồ sơ. Bài kiểm tra sinh ra bằng chứng
/// ĐỘC LẬP — thứ nặng ký nhất trong kho, thứ `ConceptSummary` dựa vào để nói
/// «con vững». Ghi nhầm người còn tệ hơn không ghi: nó bẩn hồ sơ của cả hai
/// đứa, và không có cách nào biết mà gỡ ra sau.
///
/// Một hồ sơ ⇒ KHÔNG hỏi (ma sát vô nghĩa cũng là lỗi thiết kế).
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/store/learner_profile.dart';

Future<LearnerProfile?> confirmLearner(
  BuildContext context, {
  required List<LearnerProfile> profiles,
  required LearnerProfile active,
}) async {
  if (profiles.length <= 1) return active;
  return showModalBottomSheet<LearnerProfile>(
    context: context,
    showDragHandle: true,
    builder: (ctx) => SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(
            WalSpacing.lg, 0, WalSpacing.lg, WalSpacing.xl),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text('Ai đang làm bài kiểm tra?',
                style: TextStyle(
                    fontSize: WalType.title,
                    fontWeight: FontWeight.w700,
                    color: WalColors.ink)),
            const SizedBox(height: WalSpacing.sm),
            const Text(
                'SAM ghi kết quả vào sổ học của đúng người — nên hỏi cho chắc.',
                style: TextStyle(
                    fontSize: WalType.secondary, color: WalColors.inkSoft)),
            const SizedBox(height: WalSpacing.md),
            for (final p in profiles)
              Padding(
                padding: const EdgeInsets.only(bottom: WalSpacing.sm),
                child: SizedBox(
                  height: WalSpacing.minTouch + 8,
                  child: FilledButton(
                    style: FilledButton.styleFrom(
                        backgroundColor: p.learnerId == active.learnerId
                            ? WalColors.primary500
                            : Colors.white,
                        foregroundColor: p.learnerId == active.learnerId
                            ? Colors.white
                            : WalColors.ink),
                    onPressed: () => Navigator.of(ctx).pop(p),
                    child: Text(p.displayName,
                        style: const TextStyle(fontSize: WalType.body)),
                  ),
                ),
              ),
          ],
        ),
      ),
    ),
  );
}
