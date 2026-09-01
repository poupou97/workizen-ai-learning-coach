/// ⭐⭐ WAL-51 — Màn "HÔM NAY" (Mission Center): màn hình đầu tiên của
/// «Học cùng SAM», bám wireframe M1 (SLICE-1-WIREFRAMES.md).
///
/// Luật hiển thị (khắc từ doctrine, có widget test giữ):
/// - MỘT hành động kế tiếp, kèm `decision.reason` — lý do trẻ-đọc-được.
/// - CẤM %: không con số nào giả vờ chính xác.
/// - Ôn tới hạn: sắc thái nhẹ, KHÔNG đỏ, không đếm ngược hối thúc.
/// - Thử-thách-phủ: dạng CHƯA THỬ được nói thẳng tên.
/// - Mascot HELLO thu nhỏ — SAM chào rồi lùi lại (STEP_BACK là feature).
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../camera/camera_demo_flow.dart';
import '../parent/parent_tonight_screen.dart';
import 'mission_data.dart';

class MissionCenterScreen extends StatelessWidget {
  const MissionCenterScreen({super.key, required this.data});

  final MissionData data;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(WalSpacing.md),
          children: [
            _greeting(),
            const SizedBox(height: WalSpacing.md),
            _nextActionCard(),
            const SizedBox(height: WalSpacing.lg),
            if (data.reviews.isNotEmpty) ...[
              _sectionLabel('Ôn lại'),
              for (final r in data.reviews) _reviewTile(r),
              const SizedBox(height: WalSpacing.md),
            ],
            if (data.unobservedCaseNames.isNotEmpty) ...[
              _sectionLabel('Thử dạng mới'),
              for (final name in data.unobservedCaseNames) _unseenTile(name),
            ],
            const SizedBox(height: WalSpacing.xl),
            _bottomActions(),
          ],
        ),
      ),
    );
  }

  Widget _greeting() => Row(children: [
        _samChip('assets/mascot/sam-hello.png', size: 44),
        const SizedBox(width: WalSpacing.sm),
        Text('Chào ${data.studentName}!',
            style: const TextStyle(
                fontSize: WalType.title,
                fontWeight: FontWeight.w700,
                color: WalColors.ink)),
      ]);

  Widget _nextActionCard() => Container(
        padding: const EdgeInsets.all(WalSpacing.lg),
        decoration: BoxDecoration(
          color: WalColors.surfaceLavender,
          borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
        ),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(data.nextActionTitle,
              style: const TextStyle(
                  fontSize: WalType.title,
                  fontWeight: FontWeight.w700,
                  color: WalColors.primaryText)),
          const SizedBox(height: WalSpacing.sm),
          // ⭐ reason của engine — hiển thị NGUYÊN VĂN, UI không suy diễn thêm.
          Text(data.decision.reason,
              style: const TextStyle(
                  fontSize: WalType.body, color: WalColors.ink, height: 1.45)),
          const SizedBox(height: WalSpacing.md),
          SizedBox(
            height: WalSpacing.minTouch,
            child: FilledButton(
              style: FilledButton.styleFrom(
                  backgroundColor: WalColors.primary500,
                  shape: RoundedRectangleBorder(
                      borderRadius:
                          BorderRadius.circular(WalSpacing.radiusButton))),
              onPressed: () {}, // nối T1 ở slice camera (WAL-52)
              child: const Text('Bắt đầu',
                  style: TextStyle(
                      fontSize: WalType.body, fontWeight: FontWeight.w700)),
            ),
          ),
        ]),
      );

  Widget _sectionLabel(String t) => Padding(
        padding: const EdgeInsets.only(bottom: WalSpacing.sm),
        child: Text(t,
            style: const TextStyle(
                fontSize: WalType.secondary,
                fontWeight: FontWeight.w700,
                color: WalColors.inkSoft)),
      );

  Widget _reviewTile(ReviewItem r) => _tile(
        chip: _samChip('assets/mascot/sam-review-due.png'),
        title: r.displayName,
        subtitle: 'Tới lúc gặp lại rồi', // KHÔNG đỏ, không hối thúc
        state: LearningStateToken.reviewDue,
      );

  Widget _unseenTile(String name) => _tile(
        chip: _samChip('assets/mascot/sam-probe.png'),
        title: 'Dạng "$name"',
        subtitle: 'Mình chưa thử dạng này', // nói thẳng, không nói mơ hồ
        state: LearningStateToken.insufficientEvidence,
      );

  Widget _tile({
    required Widget chip,
    required String title,
    required String subtitle,
    required LearningStateToken state,
  }) =>
      Container(
        margin: const EdgeInsets.only(bottom: WalSpacing.sm),
        padding: const EdgeInsets.all(WalSpacing.md),
        constraints: const BoxConstraints(minHeight: WalSpacing.minTouch),
        decoration: BoxDecoration(
          color: state.bg,
          borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
        ),
        child: Row(children: [
          chip,
          const SizedBox(width: WalSpacing.md),
          Expanded(
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(title,
                  style: TextStyle(
                      fontSize: WalType.body,
                      fontWeight: FontWeight.w600,
                      color: state.fg)),
              Text(subtitle,
                  style: const TextStyle(
                      fontSize: WalType.secondary, color: WalColors.inkSoft)),
            ]),
          ),
        ]),
      );

  Widget _bottomActions() => Builder(builder: (context) => Row(children: [
        Expanded(
          child: SizedBox(
            height: WalSpacing.minTouch + 8,
            child: FilledButton.icon(
              style: FilledButton.styleFrom(
                  backgroundColor: WalColors.primary500,
                  shape: RoundedRectangleBorder(
                      borderRadius:
                          BorderRadius.circular(WalSpacing.radiusButton))),
              onPressed: () => openCameraDemo(context),
              icon: const Icon(Icons.photo_camera_outlined),
              label: const Text('Chụp bài tập',
                  style: TextStyle(fontSize: WalType.body)),
            ),
          ),
        ),
        const SizedBox(width: WalSpacing.sm),
        SizedBox(
          height: WalSpacing.minTouch + 8,
          child: OutlinedButton(
            style: OutlinedButton.styleFrom(
                foregroundColor: WalColors.primaryText,
                side: const BorderSide(color: WalColors.primary500),
                shape: RoundedRectangleBorder(
                    borderRadius:
                        BorderRadius.circular(WalSpacing.radiusButton))),
            onPressed: () {}, // bản đồ học — sau slice
            child: const Text('Bản đồ ▸',
                style: TextStyle(fontSize: WalType.body)),
          ),
        ),
        const SizedBox(width: WalSpacing.sm),
        SizedBox(
          height: WalSpacing.minTouch,
          child: TextButton(
            // ⚠️ INTENT GATE chưa có — vào thẳng. Gate thật (xác nhận người
            // lớn) đi cùng child-safety architecture; residual ghi ở WAL-53.
            onPressed: () => Navigator.of(context).push(MaterialPageRoute(
                builder: (_) => buildDemoParentTonight())),
            child: const Text('Bố mẹ ▸',
                style: TextStyle(
                    fontSize: WalType.secondary, color: WalColors.inkSoft)),
          ),
        ),
      ]));

  Widget _samChip(String asset, {double size = 36}) => ClipOval(
        child: Image.asset(asset,
            width: size,
            height: size,
            fit: BoxFit.cover,
            errorBuilder: (_, e, s) => Container(
                width: size, height: size, color: WalColors.surfaceLavender)),
      );
}
