/// WAL-98 — Surface READER: bài «Đọc … rồi trả lời» ([ResponseKind.readRespond],
/// 87 bài đọc-trả-lời đo được trong corpus TV5). CÙNG persona SAM, CÙNG luật
/// bằng chứng với Quiz/Select (WAL-97) — surface mới không nhân bản luật dạy.
///
/// Bất biến RIÊNG của Reader (giữ bằng test, không phải lời dặn):
/// - Câu hỏi bị KHOÁ tới khi trẻ tự xác nhận đã đọc đoạn văn — fail-closed:
///   không có «đọc-hiểu» khi chưa đọc. Cùng họ với REVEAL gate của Compose.
/// - «Đọc xong» KHÔNG phải bằng chứng tri thức: nó chỉ MỞ màn trả lời, KHÔNG
///   phát LearningEvent nào (UNOBSERVED không bao giờ thành MASTERED).
/// - Đáp án truy về đoạn văn; bài chưa biết đáp án ⇒ KHÔNG chấm (UNKNOWN ≠ SAI).
/// - WAL-113 B1: câu hỏi MỞ (SGK TV5 KHÔNG in đáp án — corpus thật): trẻ trả
///   lời bằng lời rồi tự xác nhận; Reader ghi ATTEMPT correct=null — không bịa
///   options, không chấm, không biến UNKNOWN thành ĐÚNG.
/// - Không %, không điểm; provenance hiển thị đúng LOẠI hỗ trợ nguồn.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/student/learning_evidence.dart';
import '../../core/student/mastery.dart';
import '../../core/tutor/learning_activity.dart';
import '../../core/tutor/teaching_provenance.dart';
import '../../core/tutor/tutor_feedback.dart';

class ReaderScreen extends StatefulWidget {
  const ReaderScreen({
    super.key,
    required this.activity,
    this.provenance,
    this.onFinished,
    this.now,
  });

  final LearningActivity activity;

  /// Vì sao SAM dạy cách này + nguồn — `null` ⇒ màn KHÔNG nói gì về nguồn.
  final TeachingProvenance? provenance;

  /// Trả về sự kiện đã phát — nơi gọi ghi vào LearnerStore.
  final void Function(List<LearningEvent> events)? onFinished;
  final DateTime Function()? now;

  @override
  State<ReaderScreen> createState() => _ReaderScreenState();
}

class _ReaderScreenState extends State<ReaderScreen> {
  final List<LearningEvent> _events = [];
  bool _read = false; // trẻ đã tự xác nhận đọc xong đoạn văn
  int? _picked;
  bool _hintShown = false;
  bool _done = false;
  bool _wrongOnce = false;
  int _seq = 0;

  LearningActivity get a => widget.activity;
  DateTime _at() => (widget.now ?? DateTime.now)();

  bool get _hasPassage => (a.passage ?? '').trim().isNotEmpty;

  /// Câu hỏi CHỌN (có options) hoặc câu hỏi MỞ (chỉ có prompt — corpus TV5).
  bool get _hasQuestion => a.options.isNotEmpty || a.prompt.trim().isNotEmpty;
  bool get _openQuestion => a.options.isEmpty;

  void _emit(EvidenceKind kind, bool? correct) {
    _events.add(LearningEvent(
      eventId: '${a.activityId}#${_seq++}',
      skillCaseId: a.skillCaseId ?? a.conceptId,
      kind: kind,
      correct: correct,
      exerciseId: a.activityId,
      conceptIds: [a.conceptId],
      at: _at(),
      support: _hintShown ? SupportLevel.hint : SupportLevel.none,
      policyId: 'reader-v1',
      priorEventId: _events.isEmpty ? null : _events.last.eventId,
    ));
  }

  void _markRead() {
    if (_read) return;
    // Đọc-xong CHỈ mở màn trả lời — KHÔNG phát bằng chứng (đọc ≠ mastery).
    setState(() => _read = true);
  }

  /// Câu hỏi MỞ: trẻ trả lời BẰNG LỜI rồi tự xác nhận ⇒ ghi ATTEMPT với
  /// correct=null — UNKNOWN không bao giờ thành ĐÚNG hay SAI (doctrine).
  void _answeredOpen() {
    if (_done) return;
    _emit(EvidenceKind.independentAttempt, null);
    setState(() => _done = true);
    widget.onFinished?.call(_events);
  }

  void _pick(int i) {
    if (_done) return;
    setState(() => _picked = i);
    if (!a.gradable) {
      _emit(EvidenceKind.independentAttempt, null);
      setState(() => _done = true);
      widget.onFinished?.call(_events);
      return;
    }
    final correct = i == a.correctOption;
    _emit(
        _hintShown
            ? (correct
                ? EvidenceKind.postHintSuccess
                : EvidenceKind.guidedAttempt)
            : EvidenceKind.independentAttempt,
        correct);
    if (correct) {
      _emit(EvidenceKind.finalCorrectness, true);
      setState(() => _done = true);
      widget.onFinished?.call(_events);
    } else {
      setState(() => _wrongOnce = true);
    }
  }

  void _askHint() {
    if (_done) return;
    _emit(EvidenceKind.hintRequested, null);
    setState(() => _hintShown = true);
  }

  @override
  Widget build(BuildContext context) {
    final List<Widget> children;
    if (!_hasPassage || !_hasQuestion) {
      children = _unsupportedView();
    } else if (!_read) {
      children = _readingView();
    } else if (_done) {
      children = _resultView();
    } else {
      children = _workingView();
    }
    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(WalSpacing.lg),
          children: children,
        ),
      ),
    );
  }

  // Đoạn văn/câu hỏi thiếu ⇒ nói THẬT, không bịa nội dung đọc.
  List<Widget> _unsupportedView() => [
        Center(
            child: Image.asset('assets/mascot/sam-admit-uncertainty.png',
                width: 96, height: 96)),
        const SizedBox(height: WalSpacing.md),
        _card(const Text(
            'Bài này tớ chưa có đủ đoạn văn hoặc câu hỏi để cùng con đọc. '
            'Mình chọn bài khác nhé.',
            style: TextStyle(
                fontSize: WalType.body, color: WalColors.ink, height: 1.45))),
        const SizedBox(height: WalSpacing.lg),
        _backButton(),
      ];

  List<Widget> _readingView() => [
        Row(children: [
          Image.asset('assets/mascot/sam-listen.png', width: 56, height: 56),
          const SizedBox(width: WalSpacing.md),
          const Expanded(
            child: Text('Con đọc kỹ đoạn văn này trước nhé — đọc xong rồi mình '
                'trả lời câu hỏi.',
                style:
                    TextStyle(fontSize: WalType.body, color: WalColors.ink)),
          ),
        ]),
        const SizedBox(height: WalSpacing.md),
        _card(Text(a.passage!.trim(),
            style: const TextStyle(
                fontSize: WalType.body, color: WalColors.ink, height: 1.6))),
        const SizedBox(height: WalSpacing.lg),
        SizedBox(
          width: double.infinity,
          height: WalSpacing.minTouch + 8,
          child: FilledButton(
            style: FilledButton.styleFrom(
                backgroundColor: WalColors.primary500,
                shape: RoundedRectangleBorder(
                    borderRadius:
                        BorderRadius.circular(WalSpacing.radiusButton))),
            onPressed: _markRead,
            child: const Text('Con đọc xong rồi 📖',
                style: TextStyle(fontSize: WalType.body)),
          ),
        ),
      ];

  List<Widget> _workingView() => [
        Row(children: [
          Image.asset(
              _wrongOnce
                  ? 'assets/mascot/sam-try-again.png'
                  : _hintShown
                      ? 'assets/mascot/sam-hint.png'
                      : 'assets/mascot/sam-your-turn.png',
              width: 56,
              height: 56),
          const SizedBox(width: WalSpacing.md),
          Expanded(
            child: Text(
                _wrongOnce
                    ? 'Chưa đúng — con đọc lại đoạn văn rồi thử lại nhé.'
                    : 'Giờ tới câu hỏi. Câu trả lời nằm ngay trong đoạn con vừa đọc.',
                style: const TextStyle(
                    fontSize: WalType.body, color: WalColors.ink)),
          ),
        ]),
        const SizedBox(height: WalSpacing.md),
        _card(Text(a.passage!.trim(),
            style: const TextStyle(
                fontSize: WalType.secondary,
                color: WalColors.inkSoft,
                height: 1.5))),
        const SizedBox(height: WalSpacing.md),
        _card(Text(a.prompt,
            style: const TextStyle(
                fontSize: WalType.body, color: WalColors.ink, height: 1.5))),
        if (_hintShown) ...[
          const SizedBox(height: WalSpacing.md),
          _card(
              Text(_hintText(),
                  style: const TextStyle(
                      fontSize: WalType.body,
                      color: WalColors.ink,
                      height: 1.45)),
              color: WalColors.surfaceLavender),
        ],
        const SizedBox(height: WalSpacing.md),
        if (_openQuestion) ...[
          _card(const Text(
              'Câu hỏi này con trả lời bằng lời của mình — con nói to câu '
              'trả lời, hoặc kể cho bố mẹ/thầy cô nghe, rồi bấm nút dưới nhé.',
              style: TextStyle(
                  fontSize: WalType.body, color: WalColors.ink, height: 1.45))),
          const SizedBox(height: WalSpacing.md),
          SizedBox(
            width: double.infinity,
            height: WalSpacing.minTouch + 8,
            child: FilledButton(
              style: FilledButton.styleFrom(
                  backgroundColor: WalColors.primary500,
                  shape: RoundedRectangleBorder(
                      borderRadius:
                          BorderRadius.circular(WalSpacing.radiusButton))),
              onPressed: _answeredOpen,
              child: const Text('Con đã trả lời xong 🗣',
                  style: TextStyle(fontSize: WalType.body)),
            ),
          ),
        ] else
          for (var i = 0; i < a.options.length; i++) ...[
          SizedBox(
            width: double.infinity,
            height: WalSpacing.minTouch + 8,
            child: FilledButton(
              style: FilledButton.styleFrom(
                backgroundColor:
                    _picked == i ? WalColors.primary500 : Colors.white,
                foregroundColor: _picked == i ? Colors.white : WalColors.ink,
                alignment: Alignment.centerLeft,
                shape: RoundedRectangleBorder(
                    borderRadius:
                        BorderRadius.circular(WalSpacing.radiusButton)),
              ),
              onPressed: () => _pick(i),
              child: Text(a.options[i],
                  style: const TextStyle(fontSize: WalType.body)),
            ),
          ),
          const SizedBox(height: WalSpacing.sm),
        ],
        SizedBox(
          height: WalSpacing.minTouch,
          child: TextButton(
            onPressed: _hintShown ? null : _askHint,
            child: Text(_hintShown ? 'SAM đã gợi ý rồi' : 'Gợi ý cho tớ ✋',
                style: const TextStyle(
                    fontSize: WalType.body, color: WalColors.primaryText)),
          ),
        ),
      ];

  String _hintText() =>
      'Con đọc lại đoạn văn một lần nữa và tìm câu nói đúng ý câu hỏi — '
      'thường câu trả lời được viết gần như y hệt trong bài.';

  List<Widget> _resultView() {
    if (!a.gradable) {
      return [
        Center(
            child: Image.asset('assets/mascot/sam-admit-uncertainty.png',
                width: 96, height: 96)),
        const SizedBox(height: WalSpacing.md),
        _card(const Text(
            'Tớ chưa có đáp án của bài này nên chưa dám nói đúng hay chưa. '
            'Con hỏi thầy cô giúp tớ nhé — tớ ghi lại là con đã đọc và đã làm rồi.',
            style: TextStyle(
                fontSize: WalType.body, color: WalColors.ink, height: 1.45))),
        const SizedBox(height: WalSpacing.lg),
        _backButton(),
      ];
    }
    final maxSupport = _hintShown ? SupportLevel.hint : SupportLevel.none;
    final f = feedbackFor(
        correct: true, maxSupport: maxSupport, selfCorrected: false);
    return [
      Center(
          child: Image.asset(
              maxSupport == SupportLevel.none
                  ? 'assets/mascot/sam-celebrate-independence.png'
                  : 'assets/mascot/sam-explain.png',
              width: 96,
              height: 96)),
      const SizedBox(height: WalSpacing.md),
      _card(Text(f.praise,
          style: const TextStyle(
              fontSize: WalType.title,
              fontWeight: FontWeight.w700,
              color: WalColors.ink,
              height: 1.35))),
      const SizedBox(height: WalSpacing.md),
      _card(
          Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(f.evidenceLine,
                style: const TextStyle(
                    fontSize: WalType.secondary,
                    color: WalColors.ink,
                    height: 1.4)),
            if (widget.provenance != null) ...[
              const SizedBox(height: WalSpacing.sm),
              const Divider(height: 1),
              const SizedBox(height: WalSpacing.sm),
              Text(widget.provenance!.sourceLineForChild,
                  style: const TextStyle(
                      fontSize: WalType.secondary,
                      color: WalColors.inkSoft,
                      height: 1.4)),
            ],
          ]),
          color: WalColors.surfaceLavender),
      const SizedBox(height: WalSpacing.lg),
      _backButton(),
    ];
  }

  Widget _backButton() => SizedBox(
        height: WalSpacing.minTouch + 8,
        child: FilledButton(
          style: FilledButton.styleFrom(
              backgroundColor: WalColors.primary500,
              shape: RoundedRectangleBorder(
                  borderRadius:
                      BorderRadius.circular(WalSpacing.radiusButton))),
          onPressed: () => Navigator.of(context).maybePop(),
          child: const Text('Về Hôm nay',
              style: TextStyle(fontSize: WalType.body)),
        ),
      );

  Widget _card(Widget child, {Color color = Colors.white}) => Container(
        width: double.infinity,
        padding: const EdgeInsets.all(WalSpacing.lg),
        decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(WalSpacing.radiusCard)),
        child: child,
      );
}
