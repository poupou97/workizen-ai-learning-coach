/// WAL-145 #34 — QUẢN LÝ GIA ĐÌNH: quyền dữ liệu, không phải bảng theo dõi.
///
/// Ba luật màn này giữ:
/// 1. **KHÔNG so sánh anh chị em.** Mỗi con một thẻ riêng, không xếp hạng,
///    không «bạn nào giỏi hơn» (§15). Con số duy nhất hiện ra là SỐ BẢN GHI —
///    một sự việc về dữ liệu, không phải một lời phán về đứa trẻ.
/// 2. **Xoá là xoá thật.** Không cờ, không tombstone; và màn báo lại SỐ bản
///    ghi đã gỡ, để phụ huynh có con số thật thay vì câu «đã xoá xong».
/// 3. **Không xem lén.** Màn này không hiện nội dung trẻ đã làm — chỉ đưa
///    quyền: lấy dữ liệu ra, hoặc xoá đi.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/store/learner_profile.dart';
import '../../core/store/learner_store.dart';

class FamilyManagerScreen extends StatefulWidget {
  const FamilyManagerScreen({
    super.key,
    required this.store,
    required this.profiles,
    this.saveExport,
    this.onChanged,
  });

  final LearnerStore store;
  final List<LearnerProfile> profiles;

  /// Ghi bản xuất ra tệp, trả về đường dẫn. `null` = máy này không ghi được
  /// (test/desktop) ⇒ màn nói số dòng thay vì bịa một đường dẫn.
  final Future<String?> Function(String learnerId, String jsonl)? saveExport;

  /// Gọi sau khi xoá — tầng trên nạp lại danh sách hồ sơ.
  final VoidCallback? onChanged;

  @override
  State<FamilyManagerScreen> createState() => _FamilyManagerScreenState();
}

class _FamilyManagerScreenState extends State<FamilyManagerScreen> {
  final Map<String, String> _notice = {};
  late List<LearnerProfile> _profiles = widget.profiles;

  Future<void> _export(LearnerProfile p) async {
    final jsonl = await widget.store.exportLearner(p.learnerId);
    final lines = jsonl.trim().isEmpty ? 0 : jsonl.trim().split('\n').length;
    final path = await widget.saveExport?.call(p.learnerId, jsonl);
    if (!mounted) return;
    setState(() => _notice[p.learnerId] = path == null
        ? 'Đã lấy ra $lines dòng dữ liệu của ${p.displayName}. '
            'Máy này chưa ghi được ra tệp.'
        : 'Đã lưu $lines dòng vào: $path');
  }

  Future<void> _confirmDelete(LearnerProfile p) async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (c) => AlertDialog(
        title: Text('Xoá toàn bộ dữ liệu của ${p.displayName}?'),
        content: const Text(
            'Mọi bài đã làm và mọi bằng chứng học tập sẽ bị xoá khỏi máy này '
            'và KHÔNG lấy lại được. Hồ sơ của những bạn khác không bị đụng tới.'),
        actions: [
          TextButton(
              onPressed: () => Navigator.of(c).pop(false),
              child: const Text('Thôi')),
          TextButton(
              onPressed: () => Navigator.of(c).pop(true),
              child: const Text('Xoá')),
        ],
      ),
    );
    if (ok != true) return;
    final n = await widget.store.deleteLearner(p.learnerId);
    final left = await widget.store.profiles();
    if (!mounted) return;
    setState(() {
      _profiles = left;
      _notice.remove(p.learnerId);
    });
    widget.onChanged?.call();
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text('Đã xoá $n bản ghi của ${p.displayName}.')));
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        backgroundColor: WalColors.surface,
        body: SafeArea(
          child: ListView(
            padding: const EdgeInsets.all(WalSpacing.lg),
            children: [
              const Text('Quản lý gia đình',
                  style: TextStyle(
                      fontSize: WalType.display,
                      fontWeight: FontWeight.w700,
                      color: WalColors.ink)),
              const SizedBox(height: WalSpacing.sm),
              const Text(
                  'Dữ liệu học của các con nằm TRÊN MÁY NÀY và không gửi đi '
                  'đâu cả. Bố mẹ có quyền lấy ra hoặc xoá đi bất cứ lúc nào.',
                  style: TextStyle(
                      fontSize: WalType.secondary,
                      color: WalColors.inkSoft,
                      height: 1.4)),
              const SizedBox(height: WalSpacing.md),
              for (final p in _profiles) _card(p),
              if (_profiles.isEmpty)
                const Text('Chưa có hồ sơ nào trên máy này.',
                    style: TextStyle(
                        fontSize: WalType.body, color: WalColors.inkSoft)),
            ],
          ),
        ),
      );

  Widget _card(LearnerProfile p) => Container(
        margin: const EdgeInsets.only(bottom: WalSpacing.md),
        padding: const EdgeInsets.all(WalSpacing.lg),
        decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(WalSpacing.radiusCard)),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('${p.displayName} · Lớp ${p.grade}',
              style: const TextStyle(
                  fontSize: WalType.title,
                  fontWeight: FontWeight.w700,
                  color: WalColors.ink)),
          const SizedBox(height: WalSpacing.sm),
          Row(children: [
            TextButton(
              onPressed: () => _export(p),
              child: const Text('Lấy dữ liệu ra',
                  style: TextStyle(
                      fontSize: WalType.body, color: WalColors.primaryText)),
            ),
            const SizedBox(width: WalSpacing.sm),
            TextButton(
              onPressed: () => _confirmDelete(p),
              child: const Text('Xoá dữ liệu',
                  style: TextStyle(
                      fontSize: WalType.body, color: WalColors.warnText)),
            ),
          ]),
          if (_notice[p.learnerId] != null)
            Text(_notice[p.learnerId]!,
                style: const TextStyle(
                    fontSize: WalType.secondary,
                    color: WalColors.inkSoft,
                    height: 1.4)),
        ]),
      );
}
