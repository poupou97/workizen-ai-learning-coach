/// LANE C (round 4, Golden Slice #2) — DÒNG THỜI GIAN cho môn Lịch sử: renderer
/// trên `TimelineSemantic` (chữ sách, SAM chỉ xếp lại) + hai thứ Bài 17 không
/// có: (1) NGUỒN KỂ CHUYỆN — dòng «(Theo …)» của từng câu chuyện, suy bằng
/// `story-attribution-v1` từ các block đã tin; (2) THỬ XẾP THỨ TỰ — trẻ chạm
/// các mốc theo thứ tự mình nghĩ, `TimelineValidator` kiểm TẤT ĐỊNH theo năm
/// sách nêu và nói «sách viết …» (tham gia, không ghi bằng chứng, không khen
/// tư chất).
///
/// Được `VisualView` gọi cho hình dạng «Dòng thời gian» (file này thuộc khu
/// Lane B; Lane C chỉ thêm file này và một dòng gọi — ghi rõ trong PR).
library;

import 'package:flutter/material.dart';

import '../../../app/theme/wal_tokens.dart';
import '../../../core/lesson_model/lesson_document.dart';
import '../../../core/lesson_model/semantic_data.dart';
import '../../../core/lesson_model/timeline_date.dart';
import '../../../core/lesson_model/timeline_sources.dart';
import '../../../core/lesson_model/timeline_validator.dart';
import '../../../core/lesson_model/timeline_verbatim.dart';

class TimelineView extends StatefulWidget {
  const TimelineView({
    super.key,
    required this.doc,
    required this.semantic,
    required this.onOpenSource,
    this.verbatim = VerbatimIndex.off,
  });

  final LessonDocument doc;
  final TimelineSemantic semantic;
  final void Function(String blockId) onOpenSource;

  /// Round 5 — CỔNG NGUYÊN VĂN. Mặc định TẮT vì đường nạp fixture hôm nay chưa
  /// mang trạng thái đối chiếu bản in; khi tắt, thẻ đầu tiên NÓI RÕ là chưa
  /// đối chiếu (không im lặng coi như đã).
  final VerbatimIndex verbatim;

  static const rootKey = Key('visual-timeline');
  static const verbatimNoteKey = Key('timeline-verbatim-note');
  static const orderCheckKey = Key('timeline-order-check');
  static const orderResetKey = Key('timeline-order-reset');
  static Key sourceKey(int i) => Key('timeline-source-$i');
  static Key pickKey(int i) => Key('timeline-pick-$i');

  @override
  State<TimelineView> createState() => _TimelineViewState();
}

class _TimelineViewState extends State<TimelineView> {
  /// Thứ tự trẻ đã chạm (chỉ số mốc trong dữ liệu sách).
  final List<int> _picked = [];
  TimelineCheck? _check;

  TimelineSemantic get s => widget.semantic;
  VerbatimIndex get _v => widget.verbatim;

  /// Mốc còn dùng được sau cổng nguyên văn — mọi chỉ số bên dưới theo danh
  /// sách NÀY, không theo `s.events`, để không bao giờ vẽ một mốc bị giữ lại.
  late final List<TimelineEvent> _events = TimelineValidator.servableEvents(
    s,
    verbatim: _v,
  );
  late final int _eventsHeldBack = s.events.length - _events.length;
  late final List<DatedEvent> _dated = [
    for (final e in _events) DatedEvent(event: e, date: TimelineDate.parse(e.when)),
  ];
  late final TimelineValidator? _validator = TimelineValidator.forSemantic(
    s,
    verbatim: _v,
  );
  late final List<StoryAttribution> _sources = deriveStoryAttributions(
    widget.doc,
    verbatim: _v,
  );
  late final int _sourcesHeldBack = storyAttributionsHeldBack(
    widget.doc,
    verbatim: _v,
  );

  /// Thứ tự chip để trẻ chọn: ĐẢO ngược thứ tự sách (tất định, không ngẫu
  /// nhiên — test lặp lại được; và không phải thứ tự đúng để khỏi «chạm theo
  /// hàng» là xong).
  List<int> get _chipOrder => [for (var i = _events.length - 1; i >= 0; i--) i];

  @override
  Widget build(BuildContext context) => Column(
    key: TimelineView.rootKey,
    crossAxisAlignment: CrossAxisAlignment.stretch,
    children: [
      _verbatimNote(),
      for (var i = 0; i < _events.length; i++) _node(i),
      if (_sources.isNotEmpty) ...[
        const SizedBox(height: WalSpacing.md),
        _label('NGUỒN KỂ CHUYỆN — sách ghi'),
        for (var i = 0; i < _sources.length; i++) _sourceCard(i),
      ],
      const SizedBox(height: WalSpacing.md),
      _label('THỬ XẾP THỨ TỰ — chạm các mốc theo thời gian'),
      _orderExercise(),
    ],
  );

  /// Nói thật về việc đã (hay chưa) đối chiếu với bản in — vòng 4 đã bác bỏ
  /// «hai bộ OCR đồng ý ⇒ đúng nguyên văn», nên im lặng ở đây là nói dối.
  Widget _verbatimNote() {
    final held = _v.heldBackLine(_eventsHeldBack + _sourcesHeldBack);
    final line = !_v.enabled ? VerbatimIndex.notCheckedLine : held;
    if (line == null) return const SizedBox.shrink();
    return Padding(
      key: TimelineView.verbatimNoteKey,
      padding: const EdgeInsets.only(bottom: WalSpacing.sm),
      child: Text(
        line,
        style: const TextStyle(fontSize: 12, color: WalColors.inkSoft, height: 1.35),
      ),
    );
  }

  Widget _label(String t) => Padding(
    padding: const EdgeInsets.only(bottom: WalSpacing.sm),
    child: Text(
      t,
      style: const TextStyle(
        fontSize: 12,
        fontWeight: FontWeight.w700,
        letterSpacing: 1.1,
        color: WalColors.inkSoft,
      ),
    ),
  );

  // ── mốc ──
  Widget _node(int i) {
    final e = _events[i];
    final d = _dated[i].date;
    return InkWell(
      onTap: () => widget.onOpenSource(e.sourceBlockId),
      child: IntrinsicHeight(
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            SizedBox(
              width: 28,
              child: CustomPaint(
                painter: _TimelinePainter(
                  first: i == 0,
                  last: i == _events.length - 1,
                ),
              ),
            ),
            const SizedBox(width: WalSpacing.sm),
            Expanded(
              child: _card(
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      e.when,
                      style: const TextStyle(
                        fontSize: WalType.secondary,
                        fontWeight: FontWeight.w700,
                        color: WalColors.primaryText,
                      ),
                    ),
                    Text(
                      e.title,
                      style: const TextStyle(
                        fontSize: WalType.body,
                        fontWeight: FontWeight.w600,
                        color: WalColors.ink,
                      ),
                    ),
                    // ⭐ ROUND 4 (Lane B, lỗi đọc được trên Nokia): câu trích
                    // của mốc thường CHỈ là «Tên (năm)» — trùng nguyên vẹn
                    // hai dòng ngay trên nó, nên thẻ nói ba lần một điều.
                    // Trùng ⇒ bỏ dòng thứ ba (không sửa dữ liệu, chỉ thôi
                    // lặp lại). Câu dài hơn tên+năm thì vẫn hiện đủ.
                    if (_addsSomething(e))
                      Text(
                        e.text!,
                        style: const TextStyle(
                          fontSize: WalType.secondary,
                          color: WalColors.ink,
                          height: 1.4,
                        ),
                      ),
                    if (d == null)
                      const Text(
                        'SAM chưa đọc được năm của mốc này — con xem trong sách.',
                        style: TextStyle(fontSize: 12, color: WalColors.inkSoft),
                      ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Câu trích của mốc có nói thêm gì ngoài «tên» và «năm» đã hiện không?
  /// So sánh sau khi bỏ dấu câu/khoảng trắng thừa và hạ chữ thường — không
  /// đổi dữ liệu, chỉ quyết định có VẼ dòng đó hay không.
  static String _norm(String v) => v
      .toLowerCase()
      .replaceAll(RegExp(r'[^\p{L}\p{N}]+', unicode: true), ' ')
      .trim();

  static bool _addsSomething(TimelineEvent e) {
    final t = e.text;
    if (t == null || t.trim().isEmpty) return false;
    final body = _norm(t);
    if (body.isEmpty) return false;
    final shown = _norm('${e.title} ${e.when}');
    // «Hai Bà Trưng (40 - 43)» vs tên «Hai Bà Trưng» + năm «40 - 43» ⇒ trùng.
    return body != shown && body != _norm(e.title);
  }

  // ── nguồn kể chuyện ──
  Widget _sourceCard(int i) {
    final a = _sources[i];
    final title = a.title == null
        ? 'Câu chuyện (SAM chưa thấy tiêu đề)'
        : LessonDocument.titleCase(a.title!);
    return InkWell(
      key: TimelineView.sourceKey(i),
      onTap: () => widget.onOpenSource(a.attributionBlockId),
      child: _card(
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '📜 $title',
              style: const TextStyle(
                fontSize: WalType.body,
                fontWeight: FontWeight.w600,
                color: WalColors.ink,
              ),
            ),
            const SizedBox(height: 2),
            Text(
              a.childLine,
              style: const TextStyle(
                fontSize: WalType.secondary,
                color: WalColors.primaryText,
              ),
            ),
            Text(
              a.text,
              style: const TextStyle(
                fontSize: 12,
                fontStyle: FontStyle.italic,
                color: WalColors.inkSoft,
                height: 1.35,
              ),
            ),
            if (!a.complete)
              const Padding(
                padding: EdgeInsets.only(top: 4),
                child: Text(
                  'Câu chuyện này có phần SAM chưa đọc được — con đọc trọn trong sách nhé.',
                  style: TextStyle(fontSize: 12, color: WalColors.inkSoft),
                ),
              ),
          ],
        ),
      ),
    );
  }

  // ── thử xếp thứ tự ──
  Widget _orderExercise() {
    final v = _validator;
    if (v == null) {
      return _card(
        Text(
          TimelineValidator.unavailableReason(s, verbatim: _v) ??
              'Không kiểm được.',
          style: const TextStyle(fontSize: WalType.secondary, color: WalColors.inkSoft),
        ),
      );
    }
    final check = _check;
    return _card(
      Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Wrap(
            spacing: WalSpacing.xs,
            runSpacing: WalSpacing.xs,
            children: [
              for (final i in _chipOrder)
                ChoiceChip(
                  key: TimelineView.pickKey(i),
                  label: Text(
                    _picked.contains(i)
                        ? '${_picked.indexOf(i) + 1} · ${_events[i].title}'
                        : _events[i].title,
                    style: TextStyle(
                      fontSize: 13,
                      color: _picked.contains(i) ? Colors.white : WalColors.ink,
                    ),
                  ),
                  selected: _picked.contains(i),
                  selectedColor: WalColors.primary500,
                  backgroundColor: WalColors.surface,
                  showCheckmark: false,
                  onSelected: check != null
                      ? null
                      : (_) => setState(() {
                          if (!_picked.remove(i)) _picked.add(i);
                        }),
                ),
            ],
          ),
          const SizedBox(height: WalSpacing.sm),
          // ⭐ ROUND 4 (Lane B, lỗi tìm thấy trên fixture THẬT): hai nút này
          // tràn 33 px trên bề ngang Nokia 6.1 khi chữ dài hơn bản MẪU. `Wrap`
          // cho nút thứ hai xuống dòng thay vì bị cắt — mitigation phía hiển
          // thị, không đổi chữ.
          Wrap(
            spacing: WalSpacing.sm,
            runSpacing: WalSpacing.xs,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: [
              SizedBox(
                height: WalSpacing.minTouch,
                child: FilledButton(
                  key: TimelineView.orderCheckKey,
                  style: FilledButton.styleFrom(
                    backgroundColor: WalColors.primary500,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
                    ),
                  ),
                  onPressed: _picked.length < 2 || check != null
                      ? null
                      : () => setState(() {
                          _check = v.checkOrder([
                            for (final i in _picked) _events[i].title,
                          ]);
                        }),
                  child: const Text('Kiểm với sách'),
                ),
              ),
              TextButton(
                key: TimelineView.orderResetKey,
                onPressed: _picked.isEmpty
                    ? null
                    : () => setState(() {
                        _picked.clear();
                        _check = null;
                      }),
                child: const Text('Làm lại'),
              ),
            ],
          ),
          if (check != null) ...[
            const SizedBox(height: WalSpacing.sm),
            Text(
              check.ok ? '✓ ${check.reason}' : '📖 ${check.reason}',
              style: TextStyle(
                fontSize: WalType.secondary,
                color: check.ok ? WalColors.primaryText : WalColors.ink,
                height: 1.4,
              ),
            ),
            const Text(
              'SAM chỉ so với năm sách nêu — đây là phần thử, không phải bài kiểm tra.',
              style: TextStyle(fontSize: 12, color: WalColors.inkSoft),
            ),
          ],
        ],
      ),
    );
  }

  Widget _card(Widget child) => Container(
    width: double.infinity,
    margin: const EdgeInsets.only(bottom: WalSpacing.sm),
    padding: const EdgeInsets.all(WalSpacing.md),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
    ),
    child: child,
  );
}

/// Trục dọc + chấm mốc của dòng thời gian (chuyển từ `visual_view.dart`).
class _TimelinePainter extends CustomPainter {
  const _TimelinePainter({required this.first, required this.last});
  final bool first, last;

  @override
  void paint(Canvas canvas, Size size) {
    final line = Paint()
      ..color = WalColors.primary500.withValues(alpha: 0.5)
      ..strokeWidth = 3
      ..strokeCap = StrokeCap.round;
    const x = 14.0;
    const dotY = 22.0;
    if (!first) canvas.drawLine(const Offset(x, 0), const Offset(x, dotY), line);
    if (!last) {
      canvas.drawLine(const Offset(x, dotY), Offset(x, size.height), line);
    }
    canvas.drawCircle(
      const Offset(x, dotY),
      7,
      Paint()..color = WalColors.primary500,
    );
  }

  @override
  bool shouldRepaint(_TimelinePainter old) =>
      old.first != first || old.last != last;
}
