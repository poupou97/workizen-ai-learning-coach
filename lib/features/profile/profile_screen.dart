/// WAL-137 #02 — HỒ SƠ NGƯỜI HỌC: xem và sửa ĐÚNG ba thứ profile thật sự giữ.
///
/// Bốn bất biến của Founder Order §1 được màn này giữ NGUYÊN, không nới:
/// 1. **Lớp ≠ trình độ.** Chọn lớp 5 nghĩa là VỊ TRÍ trong chương trình, không
///    phải «đã vững lớp 1-4». Màn này không hiển thị và không sửa mastery.
/// 2. **Đổi lớp KHÔNG đụng bằng chứng.** `withGrade` giữ nguyên learnerId, nên
///    mọi LearningEvidence vẫn thuộc về đúng người. Chuyển lớp, ở lại, học
///    vượt — đều là chuyện bình thường của một đứa trẻ, không phải lý do xoá
///    những gì nó đã làm được.
/// 3. **Năm sinh ≠ lớp.** Năm sinh là TUỲ CHỌN và không hàm nào suy lớp từ nó
///    (hai đứa cùng tuổi có thể khác lớp — đi học sớm, ở lại, học vượt).
/// 4. **Trẻ không cần email/đăng nhập riêng.** Hồ sơ là một mục trong máy của
///    gia đình, không phải một tài khoản.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/store/learner_profile.dart';
import '../../core/store/learner_store.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen(
      {super.key,
      required this.profile,
      required this.store,
      this.onSaved,
      this.otherProfiles = const []});

  final LearnerProfile profile;
  final LearnerStore store;

  /// Gọi sau khi ghi — tầng trên nạp lại hồ sơ để cả app đổi theo.
  final void Function(LearnerProfile saved)? onSaved;

  /// Hồ sơ khác trên CÙNG máy — để nói rõ «đang sửa của ai».
  final List<LearnerProfile> otherProfiles;

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  late final TextEditingController _name =
      TextEditingController(text: widget.profile.displayName);
  late final TextEditingController _birth = TextEditingController(
      text: widget.profile.birthYear?.toString() ?? '');
  late int _grade = widget.profile.grade;
  bool _saved = false;

  @override
  void dispose() {
    _name.dispose();
    _birth.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    final name = _name.text.trim();
    if (name.isEmpty) return;
    // Năm sinh để trống là HỢP LỆ. Nhập bậy (không phải số, ngoài miền) ⇒
    // bỏ qua chứ không đoán hộ.
    final y = int.tryParse(_birth.text.trim());
    final birth = (y != null && y > 1900 && y < 2100) ? y : null;
    final next = LearnerProfile(
      learnerId: widget.profile.learnerId, // ⭐ KHÔNG đổi — bằng chứng bám vào đây
      displayName: name,
      grade: _grade,
      guardianId: widget.profile.guardianId,
      birthYear: birth,
      bookSeries: widget.profile.bookSeries,
    );
    await widget.store.saveProfile(next);
    if (!mounted) return;
    setState(() => _saved = true);
    widget.onSaved?.call(next);
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        backgroundColor: WalColors.surface,
        body: SafeArea(
          child: ListView(
            padding: const EdgeInsets.all(WalSpacing.lg),
            children: [
              const Text('Hồ sơ người học',
                  style: TextStyle(
                      fontSize: WalType.display,
                      fontWeight: FontWeight.w700,
                      color: WalColors.ink)),
              if (widget.otherProfiles.isNotEmpty) ...[
                const SizedBox(height: WalSpacing.sm),
                Text(
                    'Máy này có ${widget.otherProfiles.length + 1} người học. '
                    'Đang sửa hồ sơ của ${widget.profile.displayName}.',
                    style: const TextStyle(
                        fontSize: WalType.secondary,
                        color: WalColors.inkSoft)),
              ],
              const SizedBox(height: WalSpacing.md),
              _card(Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('TÊN GỌI',
                        style: TextStyle(
                            fontSize: WalType.secondary,
                            fontWeight: FontWeight.w700,
                            letterSpacing: 0.6,
                            color: WalColors.inkSoft)),
                    const SizedBox(height: WalSpacing.sm),
                    TextField(
                      controller: _name,
                      decoration: const InputDecoration(
                          border: OutlineInputBorder(),
                          hintText: 'SAM gọi con là gì?'),
                    ),
                  ])),
              const SizedBox(height: WalSpacing.md),
              _card(Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('LỚP ĐANG HỌC Ở TRƯỜNG',
                        style: TextStyle(
                            fontSize: WalType.secondary,
                            fontWeight: FontWeight.w700,
                            letterSpacing: 0.6,
                            color: WalColors.inkSoft)),
                    const SizedBox(height: WalSpacing.sm),
                    Wrap(
                      spacing: WalSpacing.sm,
                      runSpacing: WalSpacing.sm,
                      children: [
                        for (var g = 1; g <= 12; g++)
                          SizedBox(
                            width: 56,
                            height: WalSpacing.minTouch,
                            child: FilledButton(
                              style: FilledButton.styleFrom(
                                  padding: EdgeInsets.zero,
                                  backgroundColor: _grade == g
                                      ? WalColors.primary500
                                      : Colors.white,
                                  foregroundColor: _grade == g
                                      ? Colors.white
                                      : WalColors.ink),
                              onPressed: () => setState(() => _grade = g),
                              child: Text('$g',
                                  style: const TextStyle(
                                      fontSize: WalType.body)),
                            ),
                          ),
                      ],
                    ),
                    const SizedBox(height: WalSpacing.sm),
                    // Nói thẳng điều phụ huynh sợ nhất khi bấm đổi lớp.
                    const Text(
                        'Đổi lớp chỉ đổi VỊ TRÍ trong chương trình. Những gì '
                        'con đã làm được vẫn nằm nguyên trong sổ học — SAM '
                        'không xoá gì cả.',
                        style: TextStyle(
                            fontSize: WalType.secondary,
                            color: WalColors.inkSoft,
                            height: 1.4)),
                  ])),
              const SizedBox(height: WalSpacing.md),
              _card(Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('NĂM SINH (KHÔNG BẮT BUỘC)',
                        style: TextStyle(
                            fontSize: WalType.secondary,
                            fontWeight: FontWeight.w700,
                            letterSpacing: 0.6,
                            color: WalColors.inkSoft)),
                    const SizedBox(height: WalSpacing.sm),
                    TextField(
                      controller: _birth,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(
                          border: OutlineInputBorder(), hintText: 'Ví dụ 2015'),
                    ),
                    const SizedBox(height: WalSpacing.sm),
                    const Text(
                        'Để trống cũng được. SAM KHÔNG đoán lớp từ tuổi — hai '
                        'bạn cùng tuổi vẫn có thể học khác lớp.',
                        style: TextStyle(
                            fontSize: WalType.secondary,
                            color: WalColors.inkSoft,
                            height: 1.4)),
                  ])),
              const SizedBox(height: WalSpacing.lg),
              SizedBox(
                height: WalSpacing.minTouch + 8,
                child: FilledButton(
                  style: FilledButton.styleFrom(
                      backgroundColor: WalColors.primary500),
                  onPressed: _save,
                  child: const Text('Lưu',
                      style: TextStyle(fontSize: WalType.body)),
                ),
              ),
              if (_saved) ...[
                const SizedBox(height: WalSpacing.sm),
                const Text('Đã lưu ✓',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                        fontSize: WalType.body, color: WalColors.ink)),
              ],
            ],
          ),
        ),
      );

  Widget _card(Widget child) => Container(
        width: double.infinity,
        padding: const EdgeInsets.all(WalSpacing.lg),
        decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(WalSpacing.radiusCard)),
        child: child,
      );
}
