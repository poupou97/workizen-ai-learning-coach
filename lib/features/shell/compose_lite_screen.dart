/// WAL-98 — Surface COMPOSE-LITE: bài «Viết đoạn/bài…» ([ResponseKind.compose],
/// 67 bài viết đo được trong corpus TV5). Quy trình VIẾT-CÓ-QUÁ-TRÌNH:
///
///   prompt → dàn ý (của TRẺ) → nháp (của TRẺ) → SAM góp ý → trẻ sửa
///
/// ⭐ REVEAL GATE — «SAM KHÔNG viết hộ» (cùng họ fail-closed với reveal-lời-giải
/// của Tutor). Giữ bằng CẤU TRÚC + test, không phải lời dặn:
/// - SAM chỉ góp ý SAU khi trẻ đã tự nộp nháp. Trước đó không có nút góp ý,
///   không có checklist, không có bất kỳ nội-dung-mẫu nào. Đột biến mở góp ý
///   trước khi có nháp ⇒ test đỏ.
/// - Không tồn tại trường/dữ liệu nào chứa «bài văn mẫu» ⇒ surface KHÔNG THỂ
///   hiện sản phẩm hoàn chỉnh. Góp ý của SAM là CÂU HỎI tự-soát về QUÁ TRÌNH,
///   không phải câu văn viết thay.
/// - Văn KHÔNG được chấm đúng/sai (UNKNOWN ≠ SAI): mọi sự kiện `correct == null`.
///   Quá trình được ghi lại: nháp = PARTICIPATION (WAL-210 / Founder D1: nộp
///   nháp là tự báo hoàn thành, không phải bằng chứng tự làm); sửa-sau-góp-ý =
///   guidedAttempt (có hỗ trợ, KHÔNG tính tự làm); tự-đọc-lại-rồi-sửa =
///   selfCorrection — hai loại sau vẫn `correct == null` nên KHÔNG là «tự làm
///   được» ở tầng trạng thái; loại của chúng chờ Founder quyết (xem PR).
///   Không %, không điểm, không khen tư chất.
library;

import 'package:flutter/material.dart';

import '../../app/theme/band_density_scope.dart';
import '../../app/theme/wal_tokens.dart';
import '../../core/context/learning_context.dart';
import '../../core/intent/learning_intent.dart';
import '../../core/student/evidence_ids.dart';
import '../../core/student/learning_evidence.dart';
import '../../core/student/mastery.dart';
import '../../core/tutor/learning_activity.dart';
import '../../core/tutor/teaching_provenance.dart';

/// Bộ câu hỏi tự-soát MẶC ĐỊNH khi bài không kèm checklist riêng. Cố ý là CÂU
/// HỎI về quá trình — không câu nào là văn mẫu để chép.
const defaultComposeChecklist = [
  'Câu mở đầu đã nêu được ý chính con muốn viết chưa?',
  'Các câu đã nối với nhau bằng từ ngữ liên kết chưa, hay còn rời rạc?',
  'Con đã đọc to lại một lần để nghe câu có xuôi không?',
];

class ComposeLiteScreen extends StatefulWidget {
  const ComposeLiteScreen({
    super.key,
    required this.activity,
    required this.learningContext,
    this.provenance,
    this.onFinished,
    this.now,
  });

  final LearningActivity activity;

  /// ⭐⭐ WAL-189 — cùng luật WAL-175/178 đã có ở Experiment: `lookup` sinh
  /// TRACE, không sinh EVIDENCE. `_emit` đọc field này trước khi ghi.
  final LearningContext learningContext;
  final TeachingProvenance? provenance;
  final void Function(List<LearningEvent> events)? onFinished;
  final DateTime Function()? now;

  @override
  State<ComposeLiteScreen> createState() => _ComposeLiteScreenState();
}

enum _Stage { outline, draft, afterDraft, revise, done }

class _ComposeLiteScreenState extends State<ComposeLiteScreen> {
  // ⭐ WAL-210 (audit C1): token PHIÊN sinh một lần lúc mở màn — mở lại
  // cùng bài là phiên khác, id khác (đồng hồ máy, không ăn nhịp `now`).
  final String _token = newEvidenceSessionToken(DateTime.now());
  final _outlineCtrl = TextEditingController();
  final _draftCtrl = TextEditingController();
  final List<LearningEvent> _events = [];

  _Stage _stage = _Stage.outline;
  bool _feedbackRequested = false; // trẻ đã nhờ SAM góp ý (⇒ sửa có hỗ trợ)
  int _seq = 0;

  LearningActivity get a => widget.activity;
  DateTime _at() => (widget.now ?? DateTime.now)();

  List<String> get _checklist => a.composeChecklist.isNotEmpty
      ? a.composeChecklist
      : defaultComposeChecklist;

  @override
  void dispose() {
    _outlineCtrl.dispose();
    _draftCtrl.dispose();
    super.dispose();
  }

  void _emit(EvidenceKind kind) {
    // ⭐⭐ WAL-189 — tra cứu sinh TRACE, không sinh EVIDENCE (WAL-175/178).
    // Cửa DUY NHẤT của màn này — mọi chỗ gọi _emit đều qua đây.
    if (widget.learningContext.intent == LearningIntent.lookup) return;
    _events.add(LearningEvent(
      eventId: evidenceEventId(
          exerciseId: a.activityId, sessionToken: _token, seq: _seq++),
      skillCaseId: a.skillCaseId ?? a.conceptId,
      kind: kind,
      // ⭐ Văn KHÔNG chấm đúng/sai: correct luôn null (UNKNOWN ≠ SAI).
      correct: null,
      exerciseId: a.activityId,
      conceptIds: [a.conceptId],
      at: _at(),
      // Sửa sau khi nhờ góp ý ⇒ có hỗ trợ; tự sửa ⇒ không.
      support: _feedbackRequested ? SupportLevel.hint : SupportLevel.none,
      policyId: 'compose-lite-v1',
      priorEventId: _events.isEmpty ? null : _events.last.eventId,
      // WAL-210: version của pack đang mở (Compose chưa từng đóng hằng Toán 5
      // lên văn — không bắt đầu làm thế; chưa biết thì để null).
      knowledgeVersion: widget.learningContext.knowledgeModelVersion,
      // ⭐⭐ WAL-210 (audit C7): lineage sách + bài.
      sourceDocumentId: widget.learningContext.sourceDocumentId,
      lessonNo: widget.learningContext.lessonNo,
    ));
  }

  void _startDraft() => setState(() => _stage = _Stage.draft);

  void _submitDraft() {
    if (_draftCtrl.text.trim().isEmpty) return;
    // Nháp đầu tiên = trẻ TỰ BÁO đã viết xong — participation (D1), không
    // phải bằng chứng tự làm: không ai chấm nháp này.
    _emit(EvidenceKind.participation);
    setState(() => _stage = _Stage.afterDraft);
  }

  void _requestFeedback() {
    // Chỉ vào được từ afterDraft ⇒ luôn đã có nháp. hintRequested = siêu nhận
    // thức (trẻ tự thấy cần góp ý), không đổi belief.
    _emit(EvidenceKind.hintRequested);
    setState(() {
      _feedbackRequested = true;
      _stage = _Stage.revise;
    });
  }

  void _selfRevise() => setState(() => _stage = _Stage.revise);

  void _submitRevision() {
    if (_draftCtrl.text.trim().isEmpty) return;
    // Sau góp ý ⇒ guidedAttempt (có hỗ trợ). Tự đọc lại rồi sửa ⇒ selfCorrection.
    _emit(_feedbackRequested
        ? EvidenceKind.guidedAttempt
        : EvidenceKind.selfCorrection);
    setState(() => _stage = _Stage.done);
    widget.onFinished?.call(_events);
  }

  void _finishWithoutRevision() {
    setState(() => _stage = _Stage.done);
    widget.onFinished?.call(_events);
  }

  @override
  Widget build(BuildContext context) {
    final children = switch (_stage) {
      _Stage.outline => _outlineView(),
      _Stage.draft => _draftView(),
      _Stage.afterDraft => _afterDraftView(),
      _Stage.revise => _reviseView(),
      _Stage.done => _doneView(),
    };
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

  Widget _samRow(String asset, String text) => Row(children: [
        Image.asset('assets/mascot/$asset', width: densityOf(context).mascotChip, height: densityOf(context).mascotChip),
        const SizedBox(width: WalSpacing.md),
        Expanded(
          child: Text(text,
              style:
                  const TextStyle(fontSize: WalType.body, color: WalColors.ink)),
        ),
      ]);

  // BƯỚC 1 — dàn ý của trẻ. Đây là giàn giáo của TRẺ, không chấm, không phát
  // bằng chứng. KHÔNG có nút góp ý ở đây (REVEAL gate).
  List<Widget> _outlineView() => [
        _samRow('sam-think.png',
            'Trước khi viết, con phác vài ý chính nhé — như vẽ khung nhà trước '
            'khi xây. Đây là dàn ý của con, tớ không chấm đâu.'),
        const SizedBox(height: WalSpacing.md),
        _card(Text(a.prompt,
            style: const TextStyle(
                fontSize: WalType.body, color: WalColors.ink, height: 1.5))),
        const SizedBox(height: WalSpacing.md),
        _field(_outlineCtrl, 'Ý 1…\nÝ 2…\nÝ 3…', minLines: 3),
        const SizedBox(height: WalSpacing.md),
        _primary('Xong dàn ý — viết nháp ✍️', _startDraft),
      ];

  // BƯỚC 2 — nháp của trẻ. VẪN chưa có nút góp ý: SAM không được góp ý khi
  // chưa có sản phẩm của trẻ để góp (REVEAL gate).
  List<Widget> _draftView() => [
        _samRow('sam-your-turn.png',
            'Giờ con viết nháp theo dàn ý nhé. Cứ viết theo ý con — sai cũng '
            'không sao, nháp là để sửa mà. Tớ chờ con viết xong.'),
        if (_outlineCtrl.text.trim().isNotEmpty) ...[
          const SizedBox(height: WalSpacing.md),
          _card(
              Text('Dàn ý của con:\n${_outlineCtrl.text.trim()}',
                  style: const TextStyle(
                      fontSize: WalType.secondary,
                      color: WalColors.inkSoft,
                      height: 1.5)),
              color: WalColors.surfaceLavender),
        ],
        const SizedBox(height: WalSpacing.md),
        _field(_draftCtrl, 'Con viết nháp ở đây…', minLines: 5),
        const SizedBox(height: WalSpacing.md),
        _primary(
          'Nộp nháp',
          _draftCtrl.text.trim().isEmpty ? null : _submitDraft,
        ),
      ];

  // BƯỚC 3 — sau nháp: giờ MỚI mở góp ý. Ba lựa chọn của trẻ.
  List<Widget> _afterDraftView() => [
        _samRow('sam-explain.png',
            'Con viết xong nháp rồi — và con đã TỰ viết trước, đó là điều tớ '
            'quý nhất! Giờ con muốn tớ góp ý để sửa, hay tự đọc lại rồi sửa?'),
        const SizedBox(height: WalSpacing.md),
        _card(Text('Nháp của con:\n${_draftCtrl.text.trim()}',
            style: const TextStyle(
                fontSize: WalType.body, color: WalColors.ink, height: 1.5))),
        const SizedBox(height: WalSpacing.lg),
        _primary('Nhờ SAM góp ý ✋', _requestFeedback),
        const SizedBox(height: WalSpacing.sm),
        _secondary('Tự đọc lại rồi sửa', _selfRevise),
        const SizedBox(height: WalSpacing.sm),
        _secondary('Mình xong rồi', _finishWithoutRevision),
      ];

  // BƯỚC 4 — sửa. Nếu đã nhờ góp ý thì hiện checklist CÂU HỎI (không viết thay).
  List<Widget> _reviseView() => [
        _samRow('sam-hint.png',
            _feedbackRequested
                ? 'Tớ không viết hộ đâu — nhưng tớ hỏi con vài câu để con tự '
                    'soát lại nhé. Con sửa thẳng vào nháp bên dưới.'
                : 'Con đọc lại nháp của mình và sửa những chỗ con thấy chưa ưng '
                    'nhé. Tự soát là kỹ năng quý nhất của người viết.'),
        if (_feedbackRequested) ...[
          const SizedBox(height: WalSpacing.md),
          _card(
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  for (final q in _checklist)
                    Padding(
                      padding: const EdgeInsets.only(bottom: WalSpacing.sm),
                      child: Text('• $q',
                          style: const TextStyle(
                              fontSize: WalType.body,
                              color: WalColors.ink,
                              height: 1.45)),
                    ),
                ],
              ),
              color: WalColors.surfaceLavender),
        ],
        const SizedBox(height: WalSpacing.md),
        _field(_draftCtrl, 'Con sửa nháp ở đây…', minLines: 5),
        const SizedBox(height: WalSpacing.md),
        _primary(
          'Nộp bản sửa',
          _draftCtrl.text.trim().isEmpty ? null : _submitRevision,
        ),
      ];

  List<Widget> _doneView() {
    // Khen QUÁ TRÌNH (tự viết + tự sửa), KHÔNG khen tư chất, KHÔNG chấm văn.
    final praise = _feedbackRequested
        ? 'Con đã tự viết nháp rồi sửa lại theo góp ý — đó đúng là cách người '
            'viết thật làm việc. Tớ thích sự kiên trì của con!'
        : 'Con tự viết rồi tự đọc lại để sửa — tự soát bài là điều rất đáng quý!';
    final evidenceLine = _feedbackRequested
        ? 'SAM ghi lại: con TỰ viết nháp, rồi sửa cùng góp ý của tớ (lần này có '
            'hỗ trợ nên tớ chưa tính là con tự làm hết một mình).'
        : 'SAM ghi lại: con TỰ viết nháp và TỰ soát–sửa, không cần tớ góp ý.';
    return [
      Center(
          child: Image.asset('assets/mascot/sam-celebrate-independence.png',
              width: densityOf(context).mascotHero, height: densityOf(context).mascotHero)),
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
            Text(evidenceLine,
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
      const SizedBox(height: WalSpacing.md),
      _card(Text('Bài của con:\n${_draftCtrl.text.trim()}',
          style: const TextStyle(
              fontSize: WalType.body, color: WalColors.ink, height: 1.5))),
      const SizedBox(height: WalSpacing.lg),
      _primary('Về Hôm nay', () => Navigator.of(context).maybePop()),
    ];
  }

  Widget _field(TextEditingController c, String hint, {int minLines = 3}) =>
      TextField(
        controller: c,
        minLines: minLines,
        maxLines: minLines + 6,
        onChanged: (_) => setState(() {}),
        style: const TextStyle(fontSize: WalType.body, color: WalColors.ink),
        decoration: InputDecoration(
          hintText: hint,
          filled: true,
          fillColor: Colors.white,
          contentPadding: const EdgeInsets.all(WalSpacing.md),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
            borderSide: BorderSide.none,
          ),
        ),
      );

  Widget _primary(String label, VoidCallback? onPressed) => SizedBox(
        width: double.infinity,
        height: WalSpacing.minTouch + 8,
        child: FilledButton(
          style: FilledButton.styleFrom(
              backgroundColor: WalColors.primary500,
              disabledBackgroundColor: WalColors.inkSoft,
              shape: RoundedRectangleBorder(
                  borderRadius:
                      BorderRadius.circular(WalSpacing.radiusButton))),
          onPressed: onPressed,
          child: Text(label, style: const TextStyle(fontSize: WalType.body)),
        ),
      );

  Widget _secondary(String label, VoidCallback onPressed) => SizedBox(
        width: double.infinity,
        height: WalSpacing.minTouch,
        child: TextButton(
          onPressed: onPressed,
          child: Text(label,
              style: const TextStyle(
                  fontSize: WalType.body, color: WalColors.primaryText)),
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
