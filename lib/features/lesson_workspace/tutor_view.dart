/// TRACK B — MODE 3 «Học với SAM»: SAM Tutor ≠ chat. Vòng lặp có ranh giới
/// chạy trên `TutorScript` bằng `TutorRunner` (tất định, không LLM, không
/// kho). Mọi màn hiện «SAM (kịch bản thử nghiệm)».
///
/// Không có `LearnerStore`, không có `LearningEvent`: view này KHÔNG THỂ ghi
/// bằng chứng — không phải vì nó nhớ không ghi, mà vì nó không có kiểu để ghi.
///
/// ROUND 3 B4 (concept khung 6 «Học cùng SAM»): vòng lặp NHÌN THẤY ĐƯỢC —
/// dải pha «Giải thích › Hỏi › Con trả lời › Gợi ý › Phản hồi › Tiếp» sáng ở
/// pha hiện tại (suy tất định từ trạng thái runner); mỗi câu hỏi mang «Câu
/// n/N»; lựa chọn có chữ cái A/B/C/D; thẻ kết đếm số câu con ĐÃ ĐI QUA (tham
/// gia, không chấm). Không có bước nào là runtime sư phạm: PEDAGOGY REALITY
/// của view này = 0 bước runtimeGuided / N bước prototypeScripted.
library;

import 'package:flutter/material.dart';

import '../../app/theme/band_density_scope.dart';
import '../../app/theme/wal_tokens.dart';
import '../../core/lesson_model/content_trust.dart';
import '../../core/lesson_model/lesson_document.dart';
import '../../core/lesson_model/tutor_script.dart';
import 'widgets/sam_bubble.dart';
import 'widgets/source_sheet.dart';
import '../../core/pedagogy/pedagogy_runtime.dart';
import 'widgets/runtime_plan.dart';

class TutorView extends StatefulWidget {
  const TutorView({
    super.key,
    required this.doc,
    required this.onNext,
    this.anchorBlockId,
    this.onShowInRead,
    this.learnerId,
  });

  final LessonDocument doc;

  /// Học sinh đang mở (cho `LearningContext` của runtime). `null` ⇒ hằng
  /// [noLearnerId]; không có sự kiện nào được phát dù giá trị là gì.
  final String? learnerId;

  /// Từ «Hỏi SAM về đoạn này» — block trẻ đang chạm.
  final String? anchorBlockId;
  final void Function(NextTarget target, String? anchorBlockId) onNext;
  final void Function(String blockId)? onShowInRead;

  static const endCardKey = Key('tutor-end-card');
  static const phaseStripKey = Key('tutor-phase-strip');

  /// Sáu pha của vòng lặp — thứ tự cố định, chữ trẻ đọc.
  static const phases = [
    'Giải thích',
    'Hỏi',
    'Con trả lời',
    'Gợi ý',
    'Phản hồi',
    'Tiếp',
  ];

  /// Pha hiện tại, TẤT ĐỊNH từ runner: bước hiện tại + lượt cuối transcript.
  static int phaseOf(TutorRunner r) {
    if (r.finished || r.current is NextStep) return 5;
    if (r.current is ExplainStep) return 0;
    final last = r.transcript.isEmpty ? null : r.transcript.last;
    return switch (last?.kind) {
      null || TurnKind.explain => 1,
      TurnKind.ask => _hasFeedbackBefore(r) ? 4 : 2,
      TurnKind.hint => 3,
      TurnKind.matched || TurnKind.scaffold => 4,
      TurnKind.learner || TurnKind.next => 2,
    };
  }

  /// Lượt ngay trước câu hỏi hiện tại là phản hồi (khớp/scaffold) ⇒ trẻ đang
  /// đọc phản hồi + câu mới: pha «Phản hồi».
  static bool _hasFeedbackBefore(TutorRunner r) {
    final n = r.transcript.length;
    if (n < 2) return false;
    final k = r.transcript[n - 2].kind;
    return k == TurnKind.matched || k == TurnKind.scaffold;
  }

  /// «Câu n/N» của một bước hỏi; không phải bước hỏi ⇒ `null`.
  static String? askCaption(TutorScript script, String? stepId) {
    if (stepId == null) return null;
    final asks = script.asks.toList();
    final i = asks.indexWhere((a) => a.id == stepId);
    return i < 0 ? null : 'Câu ${i + 1}/${asks.length}';
  }

  /// Số câu hỏi con ĐÃ ĐI QUA (có lượt trả lời) — đếm THAM GIA, không chấm.
  static int askedCount(TutorRunner r) => {
    for (final t in r.transcript)
      if (t.kind == TurnKind.learner && t.stepId != null) t.stepId!,
  }.length;

  /// ROUND 3 (A7.2) — bước runtime ứng với lượt thứ [i] của transcript:
  /// cùng `stepId`, cùng pha; gợi ý thứ k của một bước ⇒ `hintIndex == k`.
  /// Không tìm thấy ⇒ `null` ⇒ nhãn kịch bản (an toàn).
  static PlannedStep? stepForTurn(
    RuntimePlan? plan,
    List<TutorTurn> ts,
    int i,
  ) {
    if (plan == null) return null;
    final t = ts[i];
    final phase = switch (t.kind) {
      TurnKind.explain => PlannedStepPhase.explain,
      TurnKind.ask => PlannedStepPhase.ask,
      TurnKind.hint => PlannedStepPhase.hint,
      TurnKind.matched => PlannedStepPhase.feedbackMatched,
      TurnKind.scaffold => PlannedStepPhase.scaffold,
      TurnKind.next => PlannedStepPhase.next,
      TurnKind.learner => null,
    };
    if (phase == null) return null;
    var hintIndex = 0;
    if (t.kind == TurnKind.hint) {
      for (var k = 0; k < i; k++) {
        if (ts[k].kind == TurnKind.hint && ts[k].stepId == t.stepId) {
          hintIndex++;
        }
      }
    }
    for (final s in plan.steps) {
      if (s.stepId != t.stepId || s.phase != phase) continue;
      if (phase == PlannedStepPhase.hint && s.hintIndex != hintIndex) continue;
      return s;
    }
    return null;
  }

  /// Tên LOẠI BƯỚC bằng lời trẻ — dùng để liệt kê đúng những loại thật sự
  /// nằm ở mỗi bên của dòng runtime.
  static const _phaseWord = {
    PlannedStepPhase.explain: 'giải thích',
    PlannedStepPhase.ask: 'câu hỏi',
    PlannedStepPhase.hint: 'gợi ý',
    PlannedStepPhase.feedbackMatched: 'phản hồi',
    PlannedStepPhase.scaffold: 'chỉ từng bước',
    PlannedStepPhase.next: 'bước tiếp',
  };

  /// Liệt kê loại bước theo thứ tự enum, không lặp — `null` khi rỗng.
  static String? _phaseList(RuntimePlan plan, {required bool guided}) {
    final out = <String>[];
    for (final e in _phaseWord.entries) {
      final any = plan.steps.any(
        (s) =>
            s.phase == e.key &&
            (s.mode == PlannedStepMode.runtimeGuided) == guided,
      );
      if (any) out.add(e.value);
    }
    return out.isEmpty ? null : out.join(', ');
  }

  /// Dòng runtime cho phần đầu Tutor và sheet «Nguồn & độ tin» — LỜI TRẺ
  /// (round 4 §6.6), con số giữ nguyên: PEDAGOGY REALITY đọc được trên máy.
  /// Mã máy nằm ở [runtimeLineTechnical].
  ///
  /// ⭐ ROUND 4 (lỗi thấy trên Nokia): danh sách loại bước trong ngoặc trước
  /// đây là chữ CỨNG «(giải thích, câu hỏi, bước tiếp)». Khi hai gợi ý của
  /// Bài 17 qua được luật trích dẫn (5/17 → 7/17), câu vẫn nói như cũ ⇒ dòng
  /// tự mâu thuẫn với chính con số của nó. Nay liệt kê ĐO TỪ kế hoạch.
  static String runtimeLine(RuntimePlan? plan) {
    if (plan == null) return 'Bài này không có kịch bản.';
    if (!plan.isBound) {
      return 'Máy chưa ràng buộc được bài này với sách — mọi bước là lời '
          'viết sẵn để thử.';
    }
    final guided = _phaseList(plan, guided: true);
    final proto = _phaseList(plan, guided: false);
    return 'Máy đã kiểm ${plan.runtimeGuidedCount}/${plan.steps.length} bước '
        'là lời lấy đúng trong sách${guided == null ? '' : ' ($guided)'} · '
        '${plan.prototypeCount} bước còn lại là lời viết sẵn để thử'
        '${proto == null ? '' : ' ($proto)'}.';
  }

  /// Dòng runtime KỸ THUẬT (mã từ chối) — chỉ trong nếp gấp «Chi tiết kỹ
  /// thuật» của sheet «Nguồn & độ tin».
  static String runtimeLineTechnical(RuntimePlan? plan) {
    if (plan == null) return 'no tutor script';
    if (!plan.isBound) {
      return 'unbound (${plan.planRefusals.join(', ')}) — all steps '
          'prototypeScripted';
    }
    final codes = {
      for (final s in plan.steps)
        for (final r in s.refusals) r.split(':').first,
    }.toList()..sort();
    return '${plan.runtimeGuidedCount}/${plan.steps.length} runtimeGuided · '
        '${plan.prototypeCount} prototypeScripted · refusals '
        '${codes.isEmpty ? '—' : codes.join(', ')} · validator null on every '
        'step · ${plan.evidencePolicy}';
  }

  /// Chú giải nhãn theo bước — lời trẻ cho hai chuỗi nhãn của runtime.
  static const labelLegend =
      'Nhãn xanh «runtime có kiểm» = lời lấy đúng trong sách, máy đã kiểm · '
      'nhãn tím «kịch bản thử nghiệm» = lời viết sẵn để thử.';

  /// Số thứ tự gợi ý (1-based) của lượt gợi ý thứ [i] trong transcript.
  static int hintNumber(List<TutorTurn> ts, int i) {
    var n = 0;
    for (var k = 0; k <= i; k++) {
      if (ts[k].kind == TurnKind.hint && ts[k].stepId == ts[i].stepId) n++;
    }
    return n;
  }

  @override
  State<TutorView> createState() => _TutorViewState();
}

class _TutorViewState extends State<TutorView> {
  TutorRunner? _runner;
  RuntimePlan? _plan;
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
    // A7: kế hoạch runtime — nhãn theo bước; không phát sự kiện nào.
    _plan = planForDoc(widget.doc, learnerId: widget.learnerId);
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
    // Toàn bộ thân (nhãn, neo, transcript, ô nhập) là MỘT vùng cuộn: bàn phím
    // lên thì không có phần cố định nào để tràn (Nokia n3 D8: tràn 60 px, ô
    // nhập bị bàn phím che).
    return SingleChildScrollView(
      controller: _scroll,
      padding: const EdgeInsets.only(bottom: WalSpacing.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
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
                        style: TextStyle(
                          fontSize: 12,
                          color: WalColors.inkSoft,
                        ),
                      ),
                      // A7.2 — PEDAGOGY REALITY nhìn thấy được: bao nhiêu
                      // bước runtime kiểm được, bao nhiêu bước còn là kịch bản.
                      Text(
                        TutorView.runtimeLine(_plan),
                        key: const Key('tutor-runtime-line'),
                        style: const TextStyle(
                          fontSize: 12,
                          color: WalColors.mintText,
                        ),
                      ),
                      // ROUND 4 §6.6 — chú giải nhãn theo bước bằng lời trẻ.
                      const Text(
                        TutorView.labelLegend,
                        key: Key('tutor-label-legend'),
                        style: TextStyle(fontSize: 11, color: WalColors.inkSoft),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(
              WalSpacing.md,
              WalSpacing.sm,
              WalSpacing.md,
              0,
            ),
            child: _phaseStrip(TutorView.phaseOf(r)),
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
          Padding(
            padding: const EdgeInsets.all(WalSpacing.md),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                for (var i = 0; i < r.transcript.length; i++) ...[
                  KeyedSubtree(
                    key: i == _latestSamIndex(r) ? _latestSamKey : null,
                    child: _turn(
                      r.transcript[i],
                      TutorView.stepForTurn(_plan, r.transcript, i),
                      hintCaption: r.transcript[i].kind == TurnKind.hint
                          ? 'Gợi ý ${TutorView.hintNumber(r.transcript, i)}/'
                                '${_hintsOf(r.transcript[i].stepId)}'
                          : null,
                    ),
                  ),
                  const SizedBox(height: WalSpacing.sm),
                ],
                if (r.finished || r.current is NextStep) _endCard(r),
                _inputArea(r),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Dải pha: chip nhỏ, pha hiện tại tô đậm — trẻ và Founder thấy SAM đang ở
  /// đâu trong vòng lặp. Không có pha nào là «chấm điểm».
  Widget _phaseStrip(int current) => SizedBox(
    key: TutorView.phaseStripKey,
    height: 28,
    child: ListView.separated(
      scrollDirection: Axis.horizontal,
      itemCount: TutorView.phases.length,
      // Nokia 360dp (round 3 n1 D-R3-08): sáu pha phải vừa một hàng — đệm
      // hẹp, mũi tên nhỏ; vẫn cuộn ngang được nếu chữ to hơn.
      separatorBuilder: (_, _) => const Icon(
        Icons.chevron_right,
        size: 12,
        color: WalColors.inkSoft,
      ),
      itemBuilder: (_, i) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 6),
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: i == current ? WalColors.primary500 : Colors.white,
          borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
        ),
        child: Text(
          TutorView.phases[i],
          style: TextStyle(
            fontSize: 12,
            fontWeight: i == current ? FontWeight.w700 : FontWeight.w500,
            color: i == current ? Colors.white : WalColors.inkSoft,
          ),
        ),
      ),
    ),
  );

  String _snippet(LessonBlock b) {
    final t = LessonDocument.textOf(b) ?? 'hình / vùng trong sách';
    return t.length > 70 ? '${t.substring(0, 70)}…' : t;
  }

  /// Số bậc gợi ý của một bước hỏi (thang ≤ 2 bậc theo kịch bản).
  int _hintsOf(String? stepId) {
    for (final s in widget.doc.tutorScript?.asks ?? const <AskStep>[]) {
      if (s.id == stepId) return s.hints.length;
    }
    return 0;
  }

  Widget _turn(TutorTurn t, PlannedStep? step, {String? hintCaption}) {
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
      // Nhãn THEO BƯỚC (A7.2): runtime chứng minh được ⇒ «runtime có kiểm».
      label: step?.mode.childLabel,
      caption: t.kind == TurnKind.ask
          ? TutorView.askCaption(widget.doc.tutorScript!, t.stepId)
          : hintCaption,
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
              for (var i = 0; i < options.length; i++) ...[
                SizedBox(
                  height: WalSpacing.minTouch + 4,
                  child: FilledButton(
                    style: FilledButton.styleFrom(
                      backgroundColor: Colors.white,
                      foregroundColor: WalColors.ink,
                      alignment: Alignment.centerLeft,
                      padding: const EdgeInsets.symmetric(
                        horizontal: WalSpacing.sm,
                      ),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(
                          WalSpacing.radiusButton,
                        ),
                      ),
                    ),
                    onPressed: () => _submit(options[i]),
                    child: Row(
                      children: [
                        // Chữ cái A/B/C/D (concept khung 6) — chỉ là nhãn,
                        // chuỗi đem đi khớp vẫn là lời lựa chọn.
                        Container(
                          width: 28,
                          height: 28,
                          alignment: Alignment.center,
                          decoration: const BoxDecoration(
                            color: WalColors.surfaceLavender,
                            shape: BoxShape.circle,
                          ),
                          child: Text(
                            String.fromCharCode(65 + i),
                            style: const TextStyle(
                              fontSize: WalType.secondary,
                              fontWeight: FontWeight.w700,
                              color: WalColors.primaryText,
                            ),
                          ),
                        ),
                        const SizedBox(width: WalSpacing.sm),
                        Expanded(
                          child: Text(
                            options[i],
                            style: const TextStyle(fontSize: WalType.body),
                          ),
                        ),
                      ],
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
            // ROUND 4 §6.6 — THANG gợi ý nhìn thấy: bậc đã dùng tô đậm; hết
            // thang thì nói thật SAM sẽ chỉ chỗ trong sách (không chê, không
            // kẹt). Không có bậc nào là «lộ đáp án» — thang ≤ 2 bậc theo kịch bản.
            Padding(
              padding: const EdgeInsets.only(top: WalSpacing.xs),
              child: Row(
                key: const Key('tutor-hint-ladder'),
                children: [
                  const Text(
                    'Bậc gợi ý',
                    style: TextStyle(fontSize: 12, color: WalColors.inkSoft),
                  ),
                  const SizedBox(width: WalSpacing.xs),
                  for (var k = 0; k < s.hints.length; k++)
                    Container(
                      margin: const EdgeInsets.only(right: 4),
                      width: 22,
                      height: 22,
                      alignment: Alignment.center,
                      decoration: BoxDecoration(
                        color: k < r.hintLevel
                            ? WalColors.primary500
                            : Colors.white,
                        shape: BoxShape.circle,
                        border: Border.all(
                          color: WalColors.primary500,
                          width: 1.5,
                        ),
                      ),
                      child: Text(
                        '${k + 1}',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w700,
                          color: k < r.hintLevel
                              ? Colors.white
                              : WalColors.primaryText,
                        ),
                      ),
                    ),
                  Expanded(
                    child: SizedBox(
                      height: WalSpacing.minTouch,
                      child: TextButton(
                        onPressed: r.canHint
                            ? () => _after(r.requestHint)
                            : null,
                        style: TextButton.styleFrom(
                          alignment: Alignment.centerLeft,
                          padding: const EdgeInsets.symmetric(
                            horizontal: WalSpacing.sm,
                          ),
                        ),
                        child: Text(
                          r.canHint
                              ? 'Gợi ý cho tớ ✋'
                              : 'SAM đã gợi ý hết rồi — con cứ trả lời thử, '
                                    'SAM sẽ chỉ chỗ trong sách',
                          style: const TextStyle(
                            fontSize: WalType.secondary,
                            color: WalColors.primaryText,
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
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
          if (TutorView.askedCount(r) > 0)
            Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: Text(
                'Con đã đi qua ${TutorView.askedCount(r)}/'
                '${r.script.asks.length} câu hỏi của sách cùng SAM.',
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: WalType.secondary,
                  fontWeight: FontWeight.w600,
                  color: WalColors.primaryText,
                ),
              ),
            ),
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
