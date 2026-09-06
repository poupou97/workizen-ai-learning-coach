/// WAL-137 #04 — THỜI KHOÁ BIỂU: nhập tay, tối giản, và CÓ QUYỀN ĐỂ TRỐNG.
///
/// ⭐⭐ F4 — MÔN TRONG TKB ≠ BÀI HỌC CỤ THỂ. «Thứ Ba tiết 1 = Toán» KHÔNG cho
/// phép suy ra «mai cô dạy Bài 17». Màn này vì thế CỐ Ý không có ô nào để nhập
/// «bài», không hiện dự đoán bài, và không hứa hẹn gì về nội dung buổi học.
/// Việc duy nhất TKB được làm là **xếp lại thứ tự** những gợi ý vốn đã hợp lệ
/// (`prioritiseByTimetable`).
///
/// ⭐ F13 — TKB là TUỲ CHỌN. Bỏ trống là trạng thái hợp lệ, không phải việc
/// còn dở. App chạy y như chưa từng có tính năng này.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/curriculum/subject_id.dart';
import '../../core/store/learner_profile.dart';
import '../../core/store/learner_store.dart';
import '../../core/store/timetable.dart';
import '../../core/store/timetable_generator.dart';

const _weekdayNames = {
  DateTime.monday: 'Thứ Hai',
  DateTime.tuesday: 'Thứ Ba',
  DateTime.wednesday: 'Thứ Tư',
  DateTime.thursday: 'Thứ Năm',
  DateTime.friday: 'Thứ Sáu',
  DateTime.saturday: 'Thứ Bảy',
};

class TimetableScreen extends StatefulWidget {
  const TimetableScreen({
    super.key,
    required this.profile,
    required this.store,
    required this.subjects,
  });

  final LearnerProfile profile;
  final LearnerStore store;

  /// Môn để chọn — lấy từ mục lục THẬT của lớp đó, không phải danh sách bịa.
  final List<String> subjects;

  @override
  State<TimetableScreen> createState() => _TimetableScreenState();
}

class _TimetableScreenState extends State<TimetableScreen> {
  List<TimetableEntry> _entries = const [];
  bool _loaded = false;
  int _day = DateTime.monday;

  /// Đếm số lần bấm «Tạo lại» — vào seed để mỗi lần cho một TKB khác, mà hàm
  /// sinh vẫn là hàm thuần tái lập được (§9).
  int _regenerations = 0;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final e = await widget.store.timetable(widget.profile.learnerId);
    if (!mounted) return;
    setState(() {
      _entries = e;
      _loaded = true;
    });
  }

  Future<void> _persist(List<TimetableEntry> next) async {
    setState(() => _entries = next);
    await widget.store.saveTimetable(widget.profile.learnerId, next);
  }

  List<TimetableEntry> get _today {
    final d = [
      for (final e in _entries)
        if (e.weekday == _day) e,
    ]..sort((a, b) => a.period.compareTo(b.period));
    return d;
  }

  Future<void> _add(String subject) async {
    final periods = _today.map((e) => e.period).toList();
    final next = periods.isEmpty
        ? 1
        : periods.reduce((a, b) => a > b ? a : b) + 1;
    await _persist([
      ..._entries,
      TimetableEntry(
        learnerId: widget.profile.learnerId,
        weekday: _day,
        period: next,
        // ⭐ WAL-176 — ghi MÃ môn (WAL-173 `subjectIdOf`), không phải tên
        // hiển thị: mọi nơi so khớp TKB (`proposeIntent`, gợi ý Home) đọc
        // `subjectId` theo mã. Ghi tên thẳng ⇒ so khớp không bao giờ khớp
        // — bài trước nay chưa lộ ra vì chưa có ai thật sự SO KHỚP nó.
        subjectId: subjectIdOf(subject),
      ),
    ]);
  }

  /// Tên hiển thị từ MÃ đã lưu — tra ngược trong danh sách môn có thật của
  /// máy này. Không thấy môn nào khớp (mục lục đã đổi) ⇒ hiện mã trần, không
  /// bịa tên.
  String _displayName(String subjectId) => widget.subjects.firstWhere(
    (s) => subjectIdOf(s) == subjectId,
    orElse: () => subjectId,
  );

  /// ⭐ Lệnh 51 §8 — «Tạo thời khoá biểu cho con».
  ///
  /// Sinh từ MÔN CÓ THẬT của lớp này (`widget.subjects` lấy từ mục lục pack),
  /// và ghi bằng MÃ môn — không phải tên hiển thị. Ghi tên thẳng thì mọi phép
  /// so khớp TKB im lặng trượt (WAL-176 đã vấp một lần).
  ///
  /// ⭐⭐ Đây là GỢI Ý, không phải chương trình của Bộ GD&ĐT (§10). Màn này nói
  /// ra điều đó ở chỗ trẻ và bố mẹ đọc được, không giấu trong code.
  Future<void> _generate() async {
    if (widget.subjects.isEmpty) return;
    final seed = widget.profile.learnerId.hashCode ^ (_regenerations * 7919);
    final next = generateTimetable(
      learnerId: widget.profile.learnerId,
      subjects: [for (final s in widget.subjects) subjectIdOf(s)],
      seed: seed,
    );
    setState(() => _regenerations++);
    await _persist(next);
  }

  /// §11 — TKB sinh ra KHÔNG phải sự thật bất biến: xoá sạch được.
  Future<void> _clearAll() async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (c) => AlertDialog(
        title: const Text('Xoá hết thời khoá biểu?'),
        content: Text(
          'Sẽ xoá toàn bộ các tiết đã xếp cho '
          '${widget.profile.displayName}. Những gì con đã học KHÔNG bị đụng '
          'tới.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(c).pop(false),
            child: const Text('Thôi'),
          ),
          TextButton(
            onPressed: () => Navigator.of(c).pop(true),
            child: const Text('Xoá hết'),
          ),
        ],
      ),
    );
    if (ok == true) await _persist(const []);
  }

  Future<void> _remove(TimetableEntry e) async => _persist([
    for (final x in _entries)
      if (!(x.weekday == e.weekday &&
          x.period == e.period &&
          x.subjectId == e.subjectId))
        x,
  ]);

  @override
  Widget build(BuildContext context) {
    if (!_loaded) return const Scaffold(body: SizedBox.shrink());
    final today = _today;
    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(WalSpacing.lg),
          children: [
            const Text(
              'Thời khoá biểu',
              style: TextStyle(
                fontSize: WalType.display,
                fontWeight: FontWeight.w700,
                color: WalColors.ink,
              ),
            ),
            const SizedBox(height: WalSpacing.sm),
            // Nói NGAY giới hạn, để không ai kỳ vọng SAM biết bài trên lớp.
            const Text(
              'SAM dùng thời khoá biểu để xếp thứ tự gợi ý — hôm nay có môn '
              'nào thì môn đó lên trước. SAM KHÔNG đoán cô sẽ dạy bài nào.',
              style: TextStyle(
                fontSize: WalType.secondary,
                color: WalColors.inkSoft,
                height: 1.4,
              ),
            ),
            const SizedBox(height: WalSpacing.md),
            // ⭐ §8 + §10 — tạo tự động, kèm nhãn nói rõ nó là GÌ.
            if (widget.subjects.isNotEmpty) _generatorCard(),
            const SizedBox(height: WalSpacing.md),
            Wrap(
              spacing: WalSpacing.sm,
              runSpacing: WalSpacing.sm,
              children: [
                for (final d in _weekdayNames.entries)
                  SizedBox(
                    height: WalSpacing.minTouch,
                    child: FilledButton(
                      style: FilledButton.styleFrom(
                        backgroundColor: _day == d.key
                            ? WalColors.primary500
                            : Colors.white,
                        foregroundColor: _day == d.key
                            ? Colors.white
                            : WalColors.ink,
                      ),
                      onPressed: () => setState(() => _day = d.key),
                      child: Text(
                        d.value,
                        style: const TextStyle(fontSize: WalType.secondary),
                      ),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: WalSpacing.md),
            if (today.isEmpty)
              // Trống là HỢP LỆ — nói cho đúng, đừng làm ra vẻ còn thiếu.
              const Text(
                'Chưa có môn nào cho ngày này — để trống cũng không '
                'sao, con vẫn học bình thường.',
                style: TextStyle(
                  fontSize: WalType.body,
                  color: WalColors.inkSoft,
                  height: 1.45,
                ),
              )
            else
              for (final e in today)
                Padding(
                  padding: const EdgeInsets.only(bottom: WalSpacing.sm),
                  child: Material(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
                    child: ListTile(
                      title: Text(
                        'Tiết ${e.period} · ${_displayName(e.subjectId)}',
                        style: const TextStyle(
                          fontSize: WalType.body,
                          color: WalColors.ink,
                        ),
                      ),
                      trailing: IconButton(
                        icon: const Icon(Icons.close, color: WalColors.inkSoft),
                        onPressed: () => _remove(e),
                      ),
                    ),
                  ),
                ),
            const SizedBox(height: WalSpacing.md),
            const Text(
              'THÊM MÔN VÀO NGÀY NÀY',
              style: TextStyle(
                fontSize: WalType.secondary,
                fontWeight: FontWeight.w700,
                letterSpacing: 0.6,
                color: WalColors.inkSoft,
              ),
            ),
            const SizedBox(height: WalSpacing.sm),
            if (widget.subjects.isEmpty)
              const Text(
                'Máy này chưa nạp mục lục môn học nên chưa thêm được.',
                style: TextStyle(
                  fontSize: WalType.secondary,
                  color: WalColors.inkSoft,
                ),
              )
            else
              Wrap(
                spacing: WalSpacing.sm,
                runSpacing: WalSpacing.sm,
                children: [
                  for (final s in widget.subjects)
                    ActionChip(
                      backgroundColor: Colors.white,
                      label: Text(
                        s,
                        style: const TextStyle(
                          fontSize: WalType.secondary,
                          color: WalColors.ink,
                        ),
                      ),
                      onPressed: () => _add(s),
                    ),
                ],
              ),
          ],
        ),
      ),
    );
  }

  /// Thẻ «tạo tự động». Nhãn `suggestedTimetableLabel` là BẮT BUỘC — lệnh 51
  /// §10 cấm nói đây là chương trình chuẩn khi chưa có nguồn chính thức.
  Widget _generatorCard() => Container(
    width: double.infinity,
    padding: const EdgeInsets.all(WalSpacing.md),
    decoration: BoxDecoration(
      color: WalColors.surfaceLavender,
      borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          suggestedTimetableLabel.toUpperCase(),
          style: const TextStyle(
            fontSize: WalType.secondary,
            fontWeight: FontWeight.w700,
            letterSpacing: 0.6,
            color: WalColors.primaryText,
          ),
        ),
        const SizedBox(height: WalSpacing.xs),
        Text(
          'SAM có thể xếp thử một tuần từ ${widget.subjects.length} môn '
          'trong sách lớp ${widget.profile.grade}. Đây là GỢI Ý để sửa '
          'cho nhanh — không phải thời khoá biểu chuẩn của trường hay '
          'của Bộ GD&ĐT. Xoá và đổi thoải mái.',
          style: const TextStyle(
            fontSize: WalType.secondary,
            color: WalColors.ink,
            height: 1.45,
          ),
        ),
        const SizedBox(height: WalSpacing.sm),
        Row(
          children: [
            SizedBox(
              height: WalSpacing.minTouch,
              child: FilledButton(
                style: FilledButton.styleFrom(
                  backgroundColor: WalColors.primary500,
                ),
                onPressed: _generate,
                child: Text(
                  _entries.isEmpty ? 'Tạo tự động' : 'Tạo lại',
                  style: const TextStyle(fontSize: WalType.secondary),
                ),
              ),
            ),
            if (_entries.isNotEmpty) ...[
              const SizedBox(width: WalSpacing.sm),
              SizedBox(
                height: WalSpacing.minTouch,
                child: TextButton(
                  onPressed: _clearAll,
                  child: const Text(
                    'Xoá hết',
                    style: TextStyle(
                      fontSize: WalType.secondary,
                      color: WalColors.inkSoft,
                    ),
                  ),
                ),
              ),
            ],
          ],
        ),
      ],
    ),
  );
}
