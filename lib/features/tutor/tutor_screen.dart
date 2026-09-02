/// WAL-86 — T1: màn làm bài với thang gợi ý ±1, và E1: kết quả 4 chiều.
///
/// Luật hiển thị (giữ bằng widget test):
/// - Trẻ THỬ TRƯỚC — không có nút "xem lời giải" khi chưa tự thử lần nào.
/// - Đúng-sau-gợi-ý: UI khen NỖ LỰC, nhưng dòng bằng chứng nói thẳng
///   "lần này có gợi ý nên chưa tính là con tự làm được" — khen ≠ ghi công.
/// - Không %, không điểm số, không đỏ.
library;

import 'package:flutter/material.dart';

import '../../app/theme/band_density_scope.dart';
import '../../app/theme/wal_tokens.dart';
import '../../core/curriculum/pedagogical_boundary.dart';
import '../../core/knowledge/provenance.dart';
import '../../core/knowledge/slice_curriculum.dart';
import '../../core/student/learning_evidence.dart';
import '../../core/student/mastery.dart';
import '../../core/tutor/teaching_provenance.dart';
import '../../core/tutor/tutor_feedback.dart';
import 'tutor_session.dart';

class TutorScreen extends StatefulWidget {
  const TutorScreen({
    super.key,
    required this.session,
    this.catalogue = const [],
    required this.expression,
    this.onFinished,
    this.provenance,
  });

  final TutorSession session;

  /// WAL-141 — catalogue ĐẦY ĐỦ (kể cả method ngoài ca) để drill-down
  /// «trong chương trình còn cách khác» nói thật vì sao SAM không dùng.
  final List<TeachingMethod> catalogue;
  final String expression;

  /// §3/§7 — provenance NHÌN THẤY TỪ TUTOR START: Why This Method + nguồn +
  /// authority + phiên bản. `null` = flow cũ chưa nối (demo) — không bịa.
  final TeachingProvenance? provenance;

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
        Image.asset(_mascot, width: densityOf(context).mascotChip, height: densityOf(context).mascotChip),
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
      const SizedBox(height: WalSpacing.sm),
      _ladder(),
      if (s.log.events.isNotEmpty) ...[
        const SizedBox(height: WalSpacing.sm),
        _stepsPanel(),
      ],
      if (widget.provenance != null)
        Align(
          alignment: Alignment.centerLeft,
          child: TextButton.icon(
            onPressed: () => _showProvenance(context),
            icon: const Icon(Icons.menu_book_outlined,
                size: 18, color: WalColors.primaryText),
            label: const Text('Vì sao cách này? · Nguồn',
                style: TextStyle(
                    fontSize: WalType.secondary,
                    color: WalColors.primaryText)),
          ),
        ),
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
      Center(child: Image.asset(_mascot, width: densityOf(context).mascotHero, height: densityOf(context).mascotHero)),
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

  /// WAL-139 (concept 13 «Mức độ gợi ý» — bản doctrine-safe): thang 4 nấc
  /// HIỂN THỊ mức hỗ trợ HIỆN TẠI do ENGINE quyết (±1) — trẻ thấy mình đang
  /// ở đâu, không chọn được nấc (chọn nấc = xin lời giải không cần thử).
  Widget _ladder() {
    const labels = ['Tự làm', 'Gợi ý', 'Làm mẫu', 'Lời giải'];
    return Row(children: [
      for (var i = 0; i < labels.length; i++) ...[
        if (i > 0)
          const Expanded(
              child: Divider(color: WalColors.surfaceLavender, thickness: 2)),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
          decoration: BoxDecoration(
            color: i == s.support.index
                ? WalColors.primary500
                : WalColors.surfaceLavender,
            borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
          ),
          child: Text(labels[i],
              style: TextStyle(
                  fontSize: WalType.secondary,
                  fontWeight:
                      i == s.support.index ? FontWeight.w700 : FontWeight.w400,
                  color: i == s.support.index
                      ? Colors.white
                      : WalColors.inkSoft)),
        ),
      ],
    ]);
  }

  /// WAL-139 (concept 14 «Các bước bạn đã làm»): dòng thời gian TRUNG THỰC
  /// từ log phiên — đúng loại sự kiện, không cộng dồn thành điểm.
  Widget _stepsPanel() {
    final lines = <String>[];
    for (final e in s.log.events) {
      switch (e.kind) {
        case EvidenceKind.independentAttempt:
          lines.add(e.correct == true
              ? '✓ Con tự làm: đúng!'
              : '· Con thử: chưa đúng — không sao');
        case EvidenceKind.selfCorrection:
          lines.add('★ Con TỰ sửa được — tuyệt nhất đó!');
        case EvidenceKind.hintRequested:
          // hintRequested ghi TRƯỚC khi leo nấc (support = mức cũ) — nội dung
          // ĐÃ ĐƯA nằm trong interventionId («…@nấc», WAL-108 §3).
          final iid = e.interventionId ?? '';
          lines.add(iid.contains('@fullSolution')
              ? '✋ SAM đưa lời giải'
              : iid.contains('@workedStep')
                  ? '✋ SAM làm mẫu một bước'
                  : iid.contains('@hint')
                      ? '✋ SAM gợi ý một chút'
                      : '✋ Con xin gợi ý'); // fail-closed: không có gì để đưa
        case EvidenceKind.guidedAttempt:
          lines.add('· Con thử với gợi ý: chưa đúng');
        case EvidenceKind.postHintSuccess:
          lines.add('✓ Đúng rồi (có gợi ý giúp)');
        case EvidenceKind.hintShown || EvidenceKind.finalCorrectness:
          break; // không thành dòng riêng — tránh đếm kép
      }
    }
    if (lines.isEmpty) return const SizedBox.shrink();
    return _card(
        Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Text('CÁC BƯỚC CON ĐÃ LÀM',
              style: TextStyle(
                  fontSize: WalType.secondary,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 1.05,
                  color: WalColors.inkSoft)),
          const SizedBox(height: 6),
          for (final l in lines)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 2),
              child: Text(l,
                  style: const TextStyle(
                      fontSize: WalType.secondary,
                      color: WalColors.ink,
                      height: 1.35)),
            ),
        ]),
        color: WalColors.surfaceLavender);
  }

  /// §7 — drill-down nguồn: WHAT/WHY/SOURCE/AUTHORITY + phiên bản. Chuỗi
  /// nguồn lấy NGUYÊN VĂN từ core (sourceLineForChild — mutation-guarded):
  /// sourceDemonstrated không bao giờ render thành «sách nói rằng».
  void _showProvenance(BuildContext context) {
    final p = widget.provenance!;
    final authority = switch (p.authority) {
      KnowledgeOrigin.sourceStated => 'Sách nói thẳng quy tắc này.',
      KnowledgeOrigin.sourceDemonstrated =>
        'Sách dạy cách này qua ví dụ (không phát biểu quy tắc).',
      _ => 'Cách của SAM — chưa có chỗ dựa trong sách.',
    };
    showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      backgroundColor: WalColors.surface,
      builder: (_) => Padding(
        padding: const EdgeInsets.fromLTRB(
            WalSpacing.lg, 0, WalSpacing.lg, WalSpacing.xl),
        child: ListView(shrinkWrap: true, children: [
          Text('Cách «${p.method.name}»',
              style: const TextStyle(
                  fontSize: WalType.title,
                  fontWeight: FontWeight.w700,
                  color: WalColors.ink)),
          const SizedBox(height: WalSpacing.sm),
          Text(p.whyLineForChild,
              style: const TextStyle(
                  fontSize: WalType.body, color: WalColors.ink, height: 1.45)),
          const SizedBox(height: WalSpacing.sm),
          Text(p.sourceLineForChild,
              style: const TextStyle(
                  fontSize: WalType.body,
                  fontWeight: FontWeight.w600,
                  color: WalColors.primaryText,
                  height: 1.45)),
          const SizedBox(height: WalSpacing.sm),
          Text(authority,
              style: const TextStyle(
                  fontSize: WalType.secondary, color: WalColors.inkSoft)),
          const SizedBox(height: WalSpacing.md),
          Text(
              'Phiên bản: ${TutorSession.policyId} · $knowledgeModelVersion',
              style: const TextStyle(
                  fontSize: WalType.secondary, color: WalColors.inkSoft)),
          // WAL-141 — CÁCH KHÁC trong chương trình: mỗi cách một nguồn RIÊNG
          // (mint qua explainTeaching — không copy sourceLine của cách chính);
          // cách không áp cho ca ⇒ nói thật LÝ DO, không giấu.
          ...(){
            final others = [
              for (final m in widget.catalogue)
                if (m.id != p.method.id) m
            ];
            if (others.isEmpty) return const <Widget>[];
            return <Widget>[
              const SizedBox(height: WalSpacing.md),
              const Text('Trong chương trình còn cách khác:',
                  style: TextStyle(
                      fontSize: WalType.body,
                      fontWeight: FontWeight.w700,
                      color: WalColors.ink)),
              for (final m in others) ...[
                const SizedBox(height: WalSpacing.sm),
                Builder(builder: (_) {
                  final elig = eligibilityForProblem(
                      m, s.scope.targetConcept, s.skillCaseId, s.scope.stage);
                  final line = elig.eligible
                      ? (explainTeaching(
                                  scope: s.scope,
                                  methodId: m.id,
                                  exerciseCase: s.skillCaseId)
                              ?.sourceLineForChild ??
                          'Đây là cách của SAM — con có thể kiểm lại cùng thầy cô nhé.')
                      : switch (elig.rejection) {
                          MethodRejection.notApplicableToCase =>
                            'Cách này dành cho DẠNG BÀI KHÁC '
                                '(${m.skillCaseId}) — bài này không thuộc dạng '
                                'đó nên SAM không dùng.',
                          _ =>
                            'Cách này chưa nằm trong phạm vi chương trình của bài.',
                        };
                  return Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(WalSpacing.md),
                    decoration: BoxDecoration(
                        color: WalColors.white,
                        borderRadius:
                            BorderRadius.circular(WalSpacing.radiusChip)),
                    child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('«${m.name}»',
                              style: const TextStyle(
                                  fontSize: WalType.body,
                                  fontWeight: FontWeight.w600,
                                  color: WalColors.ink)),
                          const SizedBox(height: 4),
                          Text(line,
                              style: const TextStyle(
                                  fontSize: WalType.secondary,
                                  color: WalColors.inkSoft,
                                  height: 1.4)),
                        ]),
                  );
                }),
              ],
            ];
          }(),
        ]),
      ),
    );
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
