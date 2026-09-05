/// WAL-143 #20 #21 #22 — KIỂM TRA HIỂU BÀI: cùng engine, khác LUẬT.
///
/// `AssistancePolicy.assessment` (WAL-104) đã định nghĩa sẵn luật: mode
/// `assess`, `supportCap = none`, `revealAllowed = false`, `reviewAfter =
/// false`. Màn này CHỈ là mặt tiền của luật đó — không đẻ khái niệm mới.
///
/// ⭐ CẤM GỢI Ý BẰNG CẤU TRÚC: trên màn này KHÔNG TỒN TẠI nút gợi ý, nút xem
/// lời giải, hay đường nào gọi `TutorSession`. Không phải nút xám có tooltip —
/// nút xám vẫn là một nút, và một hôm nào đó ai đó sẽ bật nó lên. Ở đây
/// `SupportLevel` chỉ có một giá trị khả dĩ: `none`.
///
/// KHÔNG ĐIỂM SỐ: kết quả kể từng bài đúng/chưa đúng như BẰNG CHỨNG, và để
/// `ConceptSummary` nói câu kết luận — 3 bài đúng KHÔNG thành «con giỏi rồi».
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/knowledge/slice_curriculum.dart' show knowledgeModelVersion;
import '../../core/store/assistance_policy.dart';
import '../../core/student/evidence_ids.dart';
import '../../core/student/learning_evidence.dart';
import '../../core/student/mastery.dart';
import '../subjects/lesson_index.dart';
// ⭐ CHỈ `show FractionProblem`: màn kiểm tra dùng CÙNG bộ chấm với lúc học
// (không có bộ chấm thứ hai để lệch nhau), nhưng KHÔNG kéo `TutorSession` vào
// tầm với — không có đường nào từ đây gọi được thang hỗ trợ.
import '../tutor/tutor_session.dart' show FractionProblem;

/// Một câu trong bài kiểm tra + câu trả lời của trẻ (nếu đã trả lời).
class AssessmentAnswer {
  const AssessmentAnswer(
      {required this.expr, required this.raw, required this.correct});
  final String expr;
  final String raw;
  final bool correct;
}

class AssessmentScreen extends StatefulWidget {
  const AssessmentScreen({
    super.key,
    required this.items,
    required this.onFinished,
    this.policy = AssistancePolicy.assessment,
    this.now,
  });

  /// Bài THẬT từ corpus (qmap-v1) — không sinh đề.
  final List<CorpusExercise> items;

  /// Trả về sự kiện + câu trả lời để tầng trên ghi kho MỘT LẦN.
  final void Function(List<LearningEvent> events, List<AssessmentAnswer> answers)
      onFinished;
  final AssistancePolicy policy;
  final DateTime Function()? now;

  @override
  State<AssessmentScreen> createState() => _AssessmentScreenState();
}

class _AssessmentScreenState extends State<AssessmentScreen> {
  // ⭐ WAL-210 (audit C1): token PHIÊN sinh một lần lúc mở màn — mở lại
  // cùng bài là phiên khác, id khác (đồng hồ máy, không ăn nhịp `now`).
  final String _token = newEvidenceSessionToken(DateTime.now());
  int _i = 0;
  final _ctrl = TextEditingController();
  final List<LearningEvent> _events = [];
  final List<AssessmentAnswer> _answers = [];

  DateTime _at() => (widget.now ?? DateTime.now)();

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  /// ⭐ WAL-210 (audit B.6 §3, «unknown-case must go»): bài KHÔNG quy
  /// được về ca ⇒ KHÔNG chấm, KHÔNG sinh bằng chứng dưới một ca bịa. Trước
  /// đây `skillCaseId ?? «unknown-case»` biến UNKNOWN thành một cái xô —
  /// bằng chứng có chấm điểm treo dưới một ca không tồn tại. Nay câu đó
  /// được bỏ qua và nói thật; không có sự kiện nào (kể cả participation —
  /// participation cũng cần một ca thật để gắn vào).
  bool get _caseUnknown => widget.items[_i].skillCaseId == null;

  void _skipUnknownCase() {
    setState(() {
      _ctrl.clear();
      _i++;
    });
    if (_i >= widget.items.length) {
      widget.onFinished(List.unmodifiable(_events), List.unmodifiable(_answers));
    }
  }

  void _submit() {
    final e = widget.items[_i];
    if (_caseUnknown) return _skipUnknownCase(); // phòng hờ — UI không mở ô
    final fp = FractionProblem.parse(e.expr);
    final raw = _ctrl.text.trim();
    if (raw.isEmpty) return;
    // fp == null ⇒ máy KHÔNG đọc được dạng bài ⇒ không dám chấm (fail closed).
    final ok = fp?.checkAnswer(raw);
    if (ok == null) return;
    final skillCaseId = e.skillCaseId!; // _caseUnknown đã loại null phía trên
    setState(() {
      _answers.add(AssessmentAnswer(expr: e.expr, raw: raw, correct: ok));
      _events.add(LearningEvent(
        eventId: evidenceEventId(
            exerciseId: '${e.book}:${e.expr}', sessionToken: _token, seq: _i),
        skillCaseId: skillCaseId,
        kind: EvidenceKind.independentAttempt,
        correct: ok,
        exerciseId: '${e.book}:${e.expr}',
        conceptIds: const ['quy-dong'],
        at: _at(),
        // ⭐ Trần của policy assessment là none — và đây là giá trị DUY NHẤT
        // màn này có thể phát. Không nhánh nào tạo được hỗ trợ.
        support: SupportLevel.none,
        policyId: 'assessment-v1',
        knowledgeVersion: knowledgeModelVersion,
      ));
      _ctrl.clear();
      _i++;
    });
    if (_i >= widget.items.length) {
      widget.onFinished(List.unmodifiable(_events), List.unmodifiable(_answers));
    }
  }

  @override
  Widget build(BuildContext context) {
    final rules = rulesFor(widget.policy);
    if (_i >= widget.items.length) return const SizedBox.shrink();
    final e = widget.items[_i];
    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(WalSpacing.lg),
          children: [
            const Text('Kiểm tra hiểu bài',
                style: TextStyle(
                    fontSize: WalType.display,
                    fontWeight: FontWeight.w700,
                    color: WalColors.ink)),
            const SizedBox(height: WalSpacing.sm),
            // Nói TRƯỚC luật chơi — trẻ không bị hụt khi tìm nút gợi ý.
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(WalSpacing.lg),
              decoration: BoxDecoration(
                  color: WalColors.surfaceLavender,
                  borderRadius: BorderRadius.circular(WalSpacing.radiusCard)),
              child: const Text(
                  'Phần này SAM không gợi ý và không chữa bài giữa chừng — '
                  'con làm một mình nhé. Làm xong SAM mới nói con đã chắc '
                  'chỗ nào.',
                  style: TextStyle(
                      fontSize: WalType.body,
                      color: WalColors.ink,
                      height: 1.45)),
            ),
            const SizedBox(height: WalSpacing.md),
            Text('Câu ${_i + 1} trong ${widget.items.length}',
                style: const TextStyle(
                    fontSize: WalType.secondary,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 0.6,
                    color: WalColors.inkSoft)),
            const SizedBox(height: WalSpacing.sm),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(WalSpacing.lg),
              decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(WalSpacing.radiusCard)),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(e.expr,
                    style: const TextStyle(
                        fontSize: WalType.display,
                        fontWeight: FontWeight.w700,
                        color: WalColors.ink)),
                if (e.page != null) ...[
                  const SizedBox(height: WalSpacing.sm),
                  Text('${e.book} · trang ${e.page}',
                      style: const TextStyle(
                          fontSize: WalType.secondary,
                          color: WalColors.inkSoft)),
                ],
                const SizedBox(height: WalSpacing.md),
                if (_caseUnknown)
                  // Cùng giọng với `adaptive_engine.decide` khi không biết ca
                  // («Chưa xác định được dạng bài…») — không đỏ, không chấm.
                  const Text(
                      'Tớ chưa xác định được dạng bài này nên không chấm câu '
                      'này — không tính vào kết quả. Mình sang câu tiếp nhé.',
                      style: TextStyle(
                          fontSize: WalType.body,
                          color: WalColors.ink,
                          height: 1.45))
                else
                  TextField(
                    controller: _ctrl,
                    autofocus: true,
                    decoration: const InputDecoration(
                        hintText: 'Đáp án của con',
                        border: OutlineInputBorder()),
                    onSubmitted: (_) => _submit(),
                  ),
              ]),
            ),
            const SizedBox(height: WalSpacing.md),
            SizedBox(
              height: WalSpacing.minTouch + 8,
              child: FilledButton(
                style: FilledButton.styleFrom(
                    backgroundColor: WalColors.primary500),
                onPressed: _caseUnknown ? _skipUnknownCase : _submit,
                child: Text(
                    _i == widget.items.length - 1 ? 'Nộp bài' : 'Câu tiếp theo',
                    style: const TextStyle(fontSize: WalType.body)),
              ),
            ),
            const SizedBox(height: WalSpacing.md),
            // Không có nút gợi ý — và nói thẳng vì sao, thay vì để trẻ tìm.
            Text(
                rules.revealAllowed
                    ? ''
                    : 'Không có nút gợi ý ở phần kiểm tra — để điều SAM ghi '
                        'lại đúng là sức của con.',
                style: const TextStyle(
                    fontSize: WalType.secondary, color: WalColors.inkSoft)),
          ],
        ),
      ),
    );
  }
}
