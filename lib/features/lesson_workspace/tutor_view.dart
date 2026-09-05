/// TRACK B — MODE 3 «Học với SAM»: SAM Tutor ≠ chat. Vòng lặp có ranh giới
/// chạy trên `TutorScript` bằng `TutorRunner` (tất định, không LLM, không
/// kho). Mọi màn hiện «SAM (kịch bản thử nghiệm)».
///
/// Không có `LearnerStore`, không có `LearningEvent`: view này KHÔNG THỂ ghi
/// bằng chứng — không phải vì nó nhớ không ghi, mà vì nó không có kiểu để ghi.
library;

import 'package:flutter/material.dart';

import '../../app/theme/band_density_scope.dart';
import '../../app/theme/wal_tokens.dart';
import '../../core/lesson_model/content_trust.dart';
import '../../core/lesson_model/lesson_document.dart';
import '../../core/lesson_model/tutor_script.dart';
import 'widgets/sam_bubble.dart';
import 'widgets/source_sheet.dart';

class TutorView extends StatefulWidget {
  const TutorView({
    super.key,
    required this.doc,
    required this.onNext,
    this.anchorBlockId,
    this.onShowInRead,
  });

  final LessonDocument doc;

  /// Từ «Hỏi SAM về đoạn này» — block trẻ đang chạm.
  final String? anchorBlockId;
  final void Function(NextTarget target, String? anchorBlockId) onNext;
  final void Function(String blockId)? onShowInRead;

  static const endCardKey = Key('tutor-end-card');

  @override
  State<TutorView> createState() => _TutorViewState();
}

class _TutorViewState extends State<TutorView> {
  TutorRunner? _runner;
  final _input = TextEditingController();
  final _scroll = ScrollController();

  @override
  void initState() {
    super.initState();
    _start();
  }

  @override
  void didUpdateWidget(TutorView old) {
    super.didUpdateWidget(old);
    if (old.anchorBlockId != widget.anchorBlockId &&
        widget.anchorBlockId != null) {
      _start();
    }
  }

  void _start() {
    final s = widget.doc.tutorScript;
    _runner = s == null
        ? null
        : TutorRunner(s, startAtBlockId: widget.anchorBlockId);
  }

  @override
  void dispose() {
    _input.dispose();
    _scroll.dispose();
    super.dispose();
  }

  /// Lượt SAM mới nhất — cuộn cho nó lên ĐẦU thân màn, không cuộn tới đáy:
  /// ở màn thấp (Nokia xoay ngang, n2 D6) cuộn tới đáy chỉ còn thấy nút
  /// «Gợi ý», câu hỏi và các lựa chọn bị đẩy khuất phía trên.
  final _latestSamKey = GlobalKey();

  void _after(VoidCallback fn) {
    setState(fn);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final ctx = _latestSamKey.currentContext;
      if (ctx == null || !mounted) return;
      Scrollable.ensureVisible(
        ctx,
        alignment: 0.0,
        duration: WalMotion.gentle,
        curve: Curves.easeOut,
      );
    });
  }

  /// Chỉ số lượt SAM (không phải «next») mới nhất trong transcript.
  static int _latestSamIndex(TutorRunner r) {
    for (var i = r.transcript.length - 1; i >= 0; i--) {
      final t = r.transcript[i];
      if (t.isSam && t.kind != TurnKind.next) return i;
    }
    return -1;
  }

  void _submit(String answer) {
    final a = answer.trim();
    if (a.isEmpty) return;
    _input.clear();
    _after(() => _runner!.submit(a));
  }

  @override
  Widget build(BuildContext context) {
    final r = _runner;
    if (r == null) return _noScript();
    final anchor = widget.anchorBlockId == null
        ? null
        : widget.doc.blockById(widget.anchorBlockId!);
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(
            WalSpacing.md,
            WalSpacing.sm,
            WalSpacing.md,
            0,
          ),
          child: Row(
            children: [
              Image.asset(
                'assets/mascot/sam-hello@64.png',
                width: 28,
                height: 28,
                errorBuilder: (_, _, _) =>
                    const SizedBox(width: 28, height: 28),
              ),
              const SizedBox(width: WalSpacing.sm),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      SamMode.prototypeScripted.childLabel,
                      style: const TextStyle(
                        fontSize: WalType.secondary,
                        fontWeight: FontWeight.w700,
                        color: WalColors.ink,
                      ),
                    ),
                    const Text(
                      'SAM đi theo kịch bản viết sẵn — chưa phải SAM thật, không ghi '
                      'bằng chứng học.',
                      style: TextStyle(fontSize: 12, color: WalColors.inkSoft),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        if (anchor != null)
          Padding(
            padding: const EdgeInsets.fromLTRB(
              WalSpacing.md,
              WalSpacing.sm,
              WalSpacing.md,
              0,
            ),
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.all(WalSpacing.sm),
              decoration: BoxDecoration(
                color: WalColors.surfaceLavender,
                borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
              ),
              child: Text(
                r.anchoredToBlock
                    ? 'Con hỏi về đoạn: «${_snippet(anchor)}»'
                    : 'Con hỏi về đoạn: «${_snippet(anchor)}» — SAM chưa có kịch '
                          'bản riêng cho đoạn này, mình bắt đầu từ đầu bài nhé.',
                style: const TextStyle(fontSize: 13, color: WalColors.ink),
              ),
            ),
          ),
        // Ô nhập nằm CUỐI danh sách (như một lượt), không ghim đáy: màn thấp /
        // bàn phím lên vẫn cuộn tới được mọi lựa chọn — không tràn (đo ở test).
        Expanded(
          child: SingleChildScrollView(
            controller: _scroll,
            padding: const EdgeInsets.all(WalSpacing.md),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                for (var i = 0; i < r.transcript.length; i++) ...[
                  KeyedSubtree(
                    key: i == _latestSamIndex(r) ? _latestSamKey : null,
                    child: _turn(r.transcript[i]),
                  ),
                  const SizedBox(height: WalSpacing.sm),
                ],
                if (r.finished || r.current is NextStep) _endCard(r),
                _inputArea(r),
              ],
            ),
          ),
        ),
      ],
    );
  }

  String _snippet(LessonBlock b) {
    final t = LessonDocument.textOf(b) ?? 'hình / vùng trong sách';
    return t.length > 70 ? '${t.substring(0, 70)}…' : t;
  }

  Widget _turn(TutorTurn t) {
    if (!t.isSam) {
      return Align(
        alignment: Alignment.centerRight,
        child: Container(
          constraints: const BoxConstraints(maxWidth: 300),
          padding: const EdgeInsets.all(WalSpacing.md),
          decoration: BoxDecoration(
            color: WalColors.primary500,
            borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
          ),
          child: Text(
            t.text,
            style: const TextStyle(
              fontSize: WalType.body,
              color: Colors.white,
              height: 1.4,
            ),
          ),
        ),
      );
    }
    if (t.kind == TurnKind.next) return const SizedBox.shrink();
    final src = t.sourceBlockId == null
        ? null
        : widget.doc.blockById(t.sourceBlockId!);
    final showSource =
        src != null &&
        (t.kind == TurnKind.explain ||
            t.kind == TurnKind.scaffold ||
            t.kind == TurnKind.matched);
    return SamBubble(
      mascot: t.mascot,
      text: t.text,
      background: switch (t.kind) {
        TurnKind.hint => WalColors.surfaceLavender,
        TurnKind.scaffold => LearningStateToken.needsWork.bg,
        _ => Colors.white,
      },
      child: showSource
          ? SourceCard(
              doc: widget.doc,
              block: src,
              onTap: () => showSourceSheet(
                context,
                doc: widget.doc,
                block: src,
                onShowInRead: widget.onShowInRead == null
                    ? null
                    : () => widget.onShowInRead!(src.id),
              ),
            )
          : null,
    );
  }

  Widget _inputArea(TutorRunner r) {
    final s = r.current;
    final Widget body;
    switch (s) {
      case ExplainStep():
        body = _primary('Tiếp ▸', () => _after(r.advance));
      case AskStep(:final options, :final isChoice):
        body = Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (isChoice)
              for (final o in options) ...[
                SizedBox(
                  height: WalSpacing.minTouch + 4,
                  child: FilledButton(
                    style: FilledButton.styleFrom(
                      backgroundColor: Colors.white,
                      foregroundColor: WalColors.ink,
                      alignment: Alignment.centerLeft,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(
                          WalSpacing.radiusButton,
                        ),
                      ),
                    ),
                    onPressed: () => _submit(o),
                    child: Text(
                      o,
                      style: const TextStyle(fontSize: WalType.body),
                    ),
                  ),
                ),
                const SizedBox(height: WalSpacing.xs),
              ]
            else
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _input,
                      key: const Key('tutor-answer-field'),
                      minLines: 1,
                      maxLines: 3,
                      textInputAction: TextInputAction.send,
                      onSubmitted: _submit,
                      style: const TextStyle(
                        fontSize: WalType.body,
                        color: WalColors.ink,
                      ),
                      decoration: InputDecoration(
                        hintText: 'Con trả lời bằng lời của mình…',
                        filled: true,
                        fillColor: Colors.white,
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(
                            WalSpacing.radiusButton,
                          ),
                          borderSide: BorderSide.none,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: WalSpacing.sm),
                  SizedBox(
                    width: WalSpacing.minTouch + 16,
                    height: WalSpacing.minTouch + 4,
                    child: FilledButton(
                      key: const Key('tutor-send'),
                      style: FilledButton.styleFrom(
                        backgroundColor: WalColors.primary500,
                        padding: EdgeInsets.zero,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(
                            WalSpacing.radiusButton,
                          ),
                        ),
                      ),
                      onPressed: () => _submit(_input.text),
                      child: const Text(
                        'Gửi',
                        style: TextStyle(fontSize: WalType.body),
                      ),
                    ),
                  ),
                ],
              ),
            SizedBox(
              height: WalSpacing.minTouch,
              child: TextButton(
                onPressed: r.canHint ? () => _after(r.requestHint) : null,
                child: Text(
                  r.canHint
                      ? 'Gợi ý cho tớ ✋ (${r.hintLevel + 1}/${s.hints.length})'
                      : 'SAM đã gợi ý hết rồi — con cứ trả lời thử nhé',
                  style: const TextStyle(
                    fontSize: WalType.secondary,
                    color: WalColors.primaryText,
                  ),
                ),
              ),
            ),
          ],
        );
      case NextStep():
      case null:
        body = const SizedBox.shrink();
    }
    return Padding(
      padding: const EdgeInsets.only(top: WalSpacing.xs, bottom: WalSpacing.md),
      child: body,
    );
  }

  Widget _endCard(TutorRunner r) {
    final next = r.current is NextStep
        ? r.current as NextStep
        : r.script.steps.whereType<NextStep>().lastOrNull;
    return Container(
      key: TutorView.endCardKey,
      padding: const EdgeInsets.all(WalSpacing.lg),
      decoration: BoxDecoration(
        color: WalColors.surfaceLavender,
        borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Center(
            child: Image.asset(
              'assets/mascot/sam-hello.png',
              width: densityOf(context).mascotHero,
              height: densityOf(context).mascotHero,
              errorBuilder: (_, _, _) => const SizedBox.shrink(),
            ),
          ),
          const SizedBox(height: WalSpacing.sm),
          const Text(
            'Con đã học cùng SAM phần này',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: WalType.title,
              fontWeight: FontWeight.w700,
              color: WalColors.ink,
            ),
          ),
          const SizedBox(height: 4),
          const Text(
            'Đây là kịch bản thử nghiệm — SAM ghi nhận con đã THAM GIA, chưa '
            'phải bằng chứng con đã hiểu. Thầy cô mới là người xác nhận.',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: WalType.secondary,
              color: WalColors.inkSoft,
              height: 1.4,
            ),
          ),
          const SizedBox(height: WalSpacing.md),
          if (next != null)
            _primary(
              '${_targetIcon(next.target)} ${next.label}',
              () => widget.onNext(next.target, next.anchorBlockId),
            ),
          const SizedBox(height: WalSpacing.xs),
          SizedBox(
            height: WalSpacing.minTouch,
            child: TextButton(
              onPressed: () => widget.onNext(NextTarget.chapter, null),
              child: const Text(
                'Về mục lục',
                style: TextStyle(
                  fontSize: WalType.body,
                  color: WalColors.primaryText,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  String _targetIcon(NextTarget t) => switch (t) {
    NextTarget.read => '📖',
    NextTarget.visual => '✨',
    NextTarget.chapter => '📚',
    NextTarget.done => '✓',
  };

  Widget _primary(String label, VoidCallback onTap) => SizedBox(
    width: double.infinity,
    height: WalSpacing.minTouch + 8,
    child: FilledButton(
      style: FilledButton.styleFrom(
        backgroundColor: WalColors.primary500,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
        ),
      ),
      onPressed: onTap,
      child: Text(label, style: const TextStyle(fontSize: WalType.body)),
    ),
  );

  Widget _noScript() => Padding(
    padding: const EdgeInsets.all(WalSpacing.lg),
    child: SamBubble(
      mascot: 'sam-admit-uncertainty',
      text:
          'SAM chưa có kịch bản cho bài này — con đọc sách hoặc xem '
          'Trực quan nhé.',
    ),
  );
}
