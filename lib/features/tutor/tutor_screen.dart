/// WAL-86 — T1: màn làm bài với thang gợi ý ±1, và E1: kết quả 4 chiều.
///
/// Luật hiển thị (giữ bằng widget test):
/// - Trẻ THỬ TRƯỚC — không có nút "xem lời giải" khi chưa tự thử lần nào.
/// - Đúng-sau-gợi-ý: UI khen NỖ LỰC, nhưng dòng bằng chứng nói thẳng
///   "lần này có gợi ý nên chưa tính là con tự làm được" — khen ≠ ghi công.
/// - Không %, không điểm số, không đỏ.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/student/learning_evidence.dart';
import '../../core/student/mastery.dart';
import '../../core/tutor/tutor_feedback.dart';
import 'tutor_session.dart';

class TutorScreen extends StatefulWidget {
  const TutorScreen({
    super.key,
    required this.session,
    required this.expression,
    this.onFinished,
  });

  final TutorSession session;
  final String expression;

  /// Log đầy đủ của phiên — nơi duy nhất model được phép "biết" chuyện gì
  /// đã xảy ra. Test đọc cái này để chứng minh UI khen mà model không ghi công.
  final void Function(TutorOutcome, EvidenceLog)? onFinished;

  @override
  State<TutorScreen> createState() => _TutorScreenState();
}

class _TutorScreenState extends State<TutorScreen> {
  final _answer = TextEditingController();
  String? _hintText;
  bool _hintUnavailable = false;
  SubmitOutcome? _lastOutcome;
  bool _done = false;

  TutorSession get s => widget.session;

  void _submit() {
    if (_answer.text.trim().isEmpty) return;
    final out = s.submit(_answer.text);
    setState(() {
      _lastOutcome = out;
      if (out != SubmitOutcome.wrong) _done = true;
    });
    if (s.finished) widget.onFinished?.call(s.outcome, s.log);
  }

  void _hint() {
    final text = s.requestHint();
    setState(() {
      _hintText = text;
      _hintUnavailable = text == null;
    });
  }

  String get _mascot {
    if (_done) {
      return s.outcome.independent || s.outcome.selfCorrected
          ? 'assets/mascot/sam-celebrate-independence.png'
          : 'assets/mascot/sam-explain.png';
    }
    if (_hintUnavailable) return 'assets/mascot/sam-admit-uncertainty.png';
    if (_lastOutcome == SubmitOutcome.wrong) {
      return 'assets/mascot/sam-try-again.png';
    }
    if (_hintText != null) return 'assets/mascot/sam-hint.png';
    return 'assets/mascot/sam-your-turn.png';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(WalSpacing.lg),
          child: _done ? _evidencePanel() : _working(),
        ),
      ),
    );
  }

  Widget _card(Widget child, {Color color = Colors.white}) => Container(
        width: double.infinity,
        padding: const EdgeInsets.all(WalSpacing.lg),
        decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(WalSpacing.radiusCard)),
        child: child,
      );

  Widget _working() {
    final hintLabelNext = switch (s.support) {
      SupportLevel.none => 'Gợi ý cho tớ ✋',
      SupportLevel.hint => 'Gợi ý thêm ✋',
      SupportLevel.workedStep =>
        s.revealAllowed ? 'Xem lời giải' : 'Gợi ý thêm ✋',
      SupportLevel.fullSolution => 'Đọc lại lời giải',
    };
    // REVEAL gate ở tầng UI: chưa tự thử ⇒ nút thang dừng ở workedStep là hết
    // (logic thật nằm trong session; UI chỉ không hứa thứ session sẽ từ chối).
    return ListView(children: [
      Row(children: [
        Image.asset(_mascot, width: 56, height: 56),
        const SizedBox(width: WalSpacing.md),
        Expanded(
          child: Text(
            _done
                ? ''
                : _lastOutcome == SubmitOutcome.wrong
                    ? 'Chưa đúng — không sao, thử lại nhé! Sai là một bước của học mà.'
                    : 'Đến lượt con! Con thử làm trước nhé.',
            style: const TextStyle(fontSize: WalType.body, color: WalColors.ink),
          ),
        ),
      ]),
      const SizedBox(height: WalSpacing.md),
      _card(Text(widget.expression,
          textAlign: TextAlign.center,
          style: const TextStyle(
              fontSize: WalType.display,
              fontWeight: FontWeight.w700,
              color: WalColors.ink))),
      if (_hintText != null && _hintText!.isNotEmpty) ...[
        const SizedBox(height: WalSpacing.md),
        _card(
            Text(_hintText!,
                style: const TextStyle(
                    fontSize: WalType.body, color: WalColors.ink, height: 1.45)),
            color: WalColors.surfaceLavender),
      ],
      if (_hintUnavailable) ...[
        const SizedBox(height: WalSpacing.md),
        _card(
            const Text(
                'Tớ chưa chắc cách giải bài này nên không dám gợi ý bừa. '
                'Con hỏi thầy cô hoặc bố mẹ giúp tớ nhé?',
                style: TextStyle(
                    fontSize: WalType.body, color: WalColors.ink, height: 1.45)),
            color: WalColors.surfaceLavender),
      ],
      const SizedBox(height: WalSpacing.md),
      TextField(
        controller: _answer,
        decoration: InputDecoration(
          hintText: 'Đáp án của con, ví dụ 7/10',
          filled: true,
          fillColor: Colors.white,
          border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
              borderSide: BorderSide.none),
        ),
        style: const TextStyle(fontSize: WalType.title, color: WalColors.ink),
      ),
      const SizedBox(height: WalSpacing.md),
      SizedBox(
        height: WalSpacing.minTouch + 8,
        child: FilledButton(
          style: FilledButton.styleFrom(
              backgroundColor: WalColors.primary500,
              shape: RoundedRectangleBorder(
                  borderRadius:
                      BorderRadius.circular(WalSpacing.radiusButton))),
          onPressed: _submit,
          child: const Text('Con làm xong rồi ✓',
              style: TextStyle(fontSize: WalType.body)),
        ),
      ),
      const SizedBox(height: WalSpacing.sm),
      SizedBox(
        height: WalSpacing.minTouch,
        child: TextButton(
          onPressed: _hint,
          child: Text(hintLabelNext,
              style: const TextStyle(
                  fontSize: WalType.body, color: WalColors.primaryText)),
        ),
      ),
    ]);
  }

  /// E1 — bốn chiều tách bạch. Không cộng dồn thành một "điểm".
  /// Chuỗi lấy từ CORE `feedbackFor` — luật khen là TESTABLE RULE ở đó,
  /// widget không tự viết lời khen (WAL-69).
  Widget _evidencePanel() {
    final o = s.outcome;
    final f = feedbackFor(
        correct: o.correct,
        maxSupport: o.maxSupport,
        selfCorrected: o.selfCorrected);
    final praise = f.praise;
    final evidenceLine = f.evidenceLine;
    return ListView(children: [
      Center(child: Image.asset(_mascot, width: 96, height: 96)),
      const SizedBox(height: WalSpacing.md),
      _card(Text(praise,
          style: const TextStyle(
              fontSize: WalType.title,
              fontWeight: FontWeight.w700,
              color: WalColors.ink,
              height: 1.35))),
      const SizedBox(height: WalSpacing.md),
      _card(
          Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            _dim('Đáp án', o.correct ? 'Đúng' : 'Chưa đúng'),
            _dim(
                'Trợ giúp',
                switch (o.maxSupport) {
                  SupportLevel.none => 'Không cần gợi ý',
                  SupportLevel.hint => 'Một gợi ý nhỏ',
                  SupportLevel.workedStep => 'Được làm mẫu một bước',
                  SupportLevel.fullSolution => 'Đã xem lời giải',
                }),
            _dim('Tớ ghi nhớ', evidenceLine),
          ]),
          color: WalColors.surfaceLavender),
      const SizedBox(height: WalSpacing.lg),
      SizedBox(
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
      ),
    ]);
  }

  Widget _dim(String label, String value) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 6),
        child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
          SizedBox(
              width: 92,
              child: Text(label,
                  style: const TextStyle(
                      fontSize: WalType.secondary,
                      fontWeight: FontWeight.w700,
                      color: WalColors.primaryText))),
          Expanded(
              child: Text(value,
                  style: const TextStyle(
                      fontSize: WalType.secondary,
                      color: WalColors.ink,
                      height: 1.4))),
        ]),
      );
}
