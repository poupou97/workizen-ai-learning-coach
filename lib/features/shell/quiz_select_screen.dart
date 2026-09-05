/// WAL-97 — Surface QUIZ/SELECT: bài «Chọn…»/«Tìm…» (loại lớn nhất corpus,
/// 195 lượt), dùng CHUNG cho Toán và Tiếng Việt — bằng chứng bác F1 («mỗi
/// môn cần UI riêng»).
///
/// Luật giữ bằng test — CÙNG luật với T1, vì SAM là MỘT persona:
/// - Trẻ chọn trước; SAM chỉ gợi ý khi trẻ xin (thang ±1 kế thừa).
/// - Chọn đúng sau gợi ý ⇒ khen nỗ lực NHƯNG nói thẳng «chưa tính là tự làm»
///   (feedbackFor của WAL-69 — widget không tự viết lời khen).
/// - Không %, không điểm số.
/// - Bài chưa biết đáp án (`gradable == false`) ⇒ KHÔNG chấm, KHÔNG sinh bằng
///   chứng — nói thật là SAM chưa có đáp án (UNKNOWN ≠ SAI).
/// - Dòng nguồn hiển thị đúng LOẠI hỗ trợ (sách nói / SAM làm theo ví dụ /
///   cách của SAM) — provenance của Founder Delta, không phải trang trí.
library;

import 'package:flutter/material.dart';

import '../../app/theme/band_density_scope.dart';
import '../../app/theme/wal_tokens.dart';
import '../../core/student/evidence_ids.dart';
import '../../core/student/learning_evidence.dart';
import '../../core/student/mastery.dart';
import '../../core/tutor/learning_activity.dart';
import '../../core/tutor/teaching_provenance.dart';
import '../../core/tutor/tutor_feedback.dart';

class QuizSelectScreen extends StatefulWidget {
  const QuizSelectScreen({
    super.key,
    required this.activity,
    this.provenance,
    this.onFinished,
    this.now,
  });

  final LearningActivity activity;

  /// Vì sao SAM dạy cách này + nguồn — `null` ⇒ màn KHÔNG nói gì về nguồn
  /// (fail closed: không có provenance thì không mượn thẩm quyền sách).
  final TeachingProvenance? provenance;

  /// Trả về sự kiện đã phát — nơi gọi ghi vào LearnerStore.
  final void Function(List<LearningEvent> events)? onFinished;
  final DateTime Function()? now;

  @override
  State<QuizSelectScreen> createState() => _QuizSelectScreenState();
}

class _QuizSelectScreenState extends State<QuizSelectScreen> {
  // ⭐ WAL-210 (audit C1): token PHIÊN sinh một lần lúc mở màn — mở lại
  // cùng bài là phiên khác, id khác (đồng hồ máy, không ăn nhịp `now`).
  final String _token = newEvidenceSessionToken(DateTime.now());
  final List<LearningEvent> _events = [];
  int? _picked;
  bool _hintShown = false;
  bool _done = false;
  bool _wrongOnce = false;
  int _seq = 0;

  LearningActivity get a => widget.activity;
  DateTime _at() => (widget.now ?? DateTime.now)();

  void _emit(EvidenceKind kind, bool? correct) {
    _events.add(LearningEvent(
      eventId: evidenceEventId(
          exerciseId: a.activityId, sessionToken: _token, seq: _seq++),
      skillCaseId: a.skillCaseId ?? a.conceptId,
      kind: kind,
      correct: correct,
      exerciseId: a.activityId,
      conceptIds: [a.conceptId],
      at: _at(),
      support: _hintShown ? SupportLevel.hint : SupportLevel.none,
      policyId: 'quiz-select-v1',
      priorEventId: _events.isEmpty ? null : _events.last.eventId,
    ));
  }

  void _pick(int i) {
    if (_done) return;
    setState(() => _picked = i);
    if (!a.gradable) {
      // Chưa biết đáp án ⇒ ghi nhận đã làm (participation — D1), KHÔNG chấm,
      // KHÔNG kết luận, KHÔNG «tự làm được».
      _emit(EvidenceKind.participation, null);
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
    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(WalSpacing.lg),
          children: _done ? _resultView() : _workingView(),
        ),
      ),
    );
  }

  List<Widget> _workingView() => [
        Row(children: [
          Image.asset(
              _wrongOnce
                  ? 'assets/mascot/sam-try-again.png'
                  : _hintShown
                      ? 'assets/mascot/sam-hint.png'
                      : 'assets/mascot/sam-your-turn.png',
              width: densityOf(context).mascotChip, height: densityOf(context).mascotChip),
          const SizedBox(width: WalSpacing.md),
          Expanded(
            child: Text(
                _wrongOnce
                    ? 'Chưa đúng — con thử lại nhé, sai là một bước của học mà.'
                    : 'Con chọn thử xem nhé!',
                style: const TextStyle(
                    fontSize: WalType.body, color: WalColors.ink)),
          ),
        ]),
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
        for (var i = 0; i < a.options.length; i++) ...[
          SizedBox(
            width: double.infinity,
            height: WalSpacing.minTouch + 8,
            child: FilledButton(
              style: FilledButton.styleFrom(
                backgroundColor:
                    _picked == i ? WalColors.primary500 : Colors.white,
                foregroundColor:
                    _picked == i ? Colors.white : WalColors.ink,
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
      'Con đọc lại câu hỏi và thử loại bớt những đáp án chắc chắn không hợp nhé — '
      'còn lại thường dễ chọn hơn.';

  List<Widget> _resultView() {
    // Bài chưa biết đáp án: nói THẬT, không khen cũng không chê.
    if (!a.gradable) {
      return [
        Center(
            child: Image.asset('assets/mascot/sam-admit-uncertainty.png',
                width: densityOf(context).mascotHero, height: densityOf(context).mascotHero)),
        const SizedBox(height: WalSpacing.md),
        _card(const Text(
            'Tớ chưa có đáp án của bài này nên chưa dám nói đúng hay chưa. '
            'Con hỏi thầy cô giúp tớ nhé — tớ ghi lại là con đã làm rồi.',
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
              width: densityOf(context).mascotHero, height: densityOf(context).mascotHero)),
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
