/// WAL-95 — Onboarding V1: ĐÚNG HAI câu hỏi.
///
/// Founder Task Order §1 + F13: hỏi ít nhất có thể để bắt đầu học được —
/// tên gọi + lớp. KHÔNG hỏi thời khoá biểu (F13: chưa có bằng chứng nào cho
/// thấy hỏi thêm ở bước này cải thiện UX; friction đo thật ở WAL-49), KHÔNG
/// hỏi năm sinh (tuỳ chọn, thêm sau ở màn hồ sơ nếu cần).
///
/// Luật giữ bằng test:
/// - Chọn lớp KHÔNG sinh bất kỳ bằng chứng nào (grade ≠ mastery).
/// - Không có bước nào hỏi thời khoá biểu.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/store/learner_profile.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key, required this.onDone});

  /// Nhận hồ sơ đã dựng — nơi gọi lo việc lưu (store) và điều hướng.
  final void Function(LearnerProfile) onDone;

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final _name = TextEditingController();
  int? _grade;

  bool get _ready => _name.text.trim().isNotEmpty && _grade != null;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(WalSpacing.lg),
          children: [
            const SizedBox(height: WalSpacing.lg),
            Center(child: Image.asset('assets/mascot/sam-hello.png',
                width: 120, height: 120)),
            const SizedBox(height: WalSpacing.lg),
            const Text('Chào con! Tớ là SAM.',
                textAlign: TextAlign.center,
                style: TextStyle(
                    fontSize: WalType.display,
                    fontWeight: FontWeight.w700,
                    color: WalColors.ink)),
            const SizedBox(height: WalSpacing.sm),
            const Text('Tớ hỏi hai câu thôi rồi mình học nhé.',
                textAlign: TextAlign.center,
                style: TextStyle(
                    fontSize: WalType.body, color: WalColors.inkSoft)),
            const SizedBox(height: WalSpacing.lg),

            // ── câu 1 ──────────────────────────────────────────────────
            const Text('Tớ gọi con là gì?',
                style: TextStyle(
                    fontSize: WalType.title,
                    fontWeight: FontWeight.w700,
                    color: WalColors.ink)),
            const SizedBox(height: WalSpacing.sm),
            TextField(
              controller: _name,
              onChanged: (_) => setState(() {}),
              decoration: InputDecoration(
                hintText: 'Ví dụ: Minh',
                filled: true,
                fillColor: Colors.white,
                border: OutlineInputBorder(
                    borderRadius:
                        BorderRadius.circular(WalSpacing.radiusButton),
                    borderSide: BorderSide.none),
              ),
              style: const TextStyle(
                  fontSize: WalType.title, color: WalColors.ink),
            ),
            const SizedBox(height: WalSpacing.lg),

            // ── câu 2 ──────────────────────────────────────────────────
            const Text('Con đang học lớp mấy?',
                style: TextStyle(
                    fontSize: WalType.title,
                    fontWeight: FontWeight.w700,
                    color: WalColors.ink)),
            const SizedBox(height: WalSpacing.xs),
            // ⭐ Nói thẳng ngay trên màn: chọn lớp là NÓI VỊ TRÍ, không phải
            // nói đã giỏi tới đâu (bất biến grade ≠ mastery, cho người đọc).
            const Text('Chọn lớp con đang học ở trường — SAM sẽ tự tìm hiểu '
                'con đã vững phần nào qua các bài con làm.',
                style: TextStyle(
                    fontSize: WalType.secondary,
                    color: WalColors.inkSoft,
                    height: 1.4)),
            const SizedBox(height: WalSpacing.sm),
            Wrap(
              spacing: WalSpacing.sm,
              runSpacing: WalSpacing.sm,
              children: [
                for (var g = 1; g <= 12; g++)
                  SizedBox(
                    width: 64,
                    height: WalSpacing.minTouch,
                    child: FilledButton(
                      style: FilledButton.styleFrom(
                        backgroundColor: _grade == g
                            ? WalColors.primary500
                            : Colors.white,
                        foregroundColor:
                            _grade == g ? Colors.white : WalColors.ink,
                        padding: EdgeInsets.zero,
                        shape: RoundedRectangleBorder(
                            borderRadius:
                                BorderRadius.circular(WalSpacing.radiusChip)),
                      ),
                      onPressed: () => setState(() => _grade = g),
                      child: Text('$g',
                          style: const TextStyle(fontSize: WalType.body)),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: WalSpacing.lg),
            SizedBox(
              height: WalSpacing.minTouch + 8,
              child: FilledButton(
                style: FilledButton.styleFrom(
                    backgroundColor: WalColors.primary500,
                    disabledBackgroundColor: WalColors.surfaceLavender,
                    shape: RoundedRectangleBorder(
                        borderRadius:
                            BorderRadius.circular(WalSpacing.radiusButton))),
                onPressed: _ready
                    ? () => widget.onDone(LearnerProfile(
                          learnerId:
                              'l-${DateTime.now().millisecondsSinceEpoch}',
                          displayName: _name.text.trim(),
                          grade: _grade!,
                        ))
                    : null,
                child: const Text('Bắt đầu học ▸',
                    style: TextStyle(fontSize: WalType.body)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
