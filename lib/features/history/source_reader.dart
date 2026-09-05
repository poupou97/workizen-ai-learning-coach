/// WAL-113 B2 — SỬ: SOURCE READER (prototype tối thiểu, dữ liệu THẬT).
///
/// Ba tầng claim — BA KIỂU DỮ LIỆU RIÊNG, ba nhãn UI riêng (bất biến giữ bằng
/// KIỂU + test, không phải lời dặn):
/// - [SourceClaim]       «NGUỒN NÓI GÌ»  — trích NGUYÊN VĂN + attribution in
///   trong SGK (textbookVerbatim). Widget nguồn CHỈ nhận kiểu này.
/// - [SamInterpretation] «SAM DIỄN GIẢI» — diễn giải curated (systemDerived);
///   không bao giờ render dưới nhãn của nguồn.
/// - [StudentConclusion] «EM KẾT LUẬN»   — của học sinh; KHÔNG chấm đúng/sai:
///   evidence phát ra correct=null (UNKNOWN ≠ SAI — kết luận sử không phải
///   một đáp án duy nhất).
/// - Gate: diễn giải + kết luận KHOÁ tới khi trẻ xác nhận ĐÃ ĐỌC NGUỒN (cùng
///   họ READ gate của Reader); «đọc nguồn xong» KHÔNG phát bằng chứng.
/// - Không %, không điểm. Sử KHÔNG bị ép vào Step Solver của Toán.
library;

import 'package:flutter/material.dart';

import '../../app/theme/band_density_scope.dart';
import '../../app/theme/wal_tokens.dart';
import '../../core/context/learning_context.dart';
import '../../core/intent/learning_intent.dart';
import '../../core/knowledge/slice_curriculum.dart' show knowledgeModelVersion;
import '../../core/student/evidence_ids.dart';
import '../../core/student/learning_evidence.dart';
import '../../core/student/mastery.dart';
import '../subjects/lesson_index.dart';

/// Lời của NGUỒN — dữ liệu mined verbatim, có attribution + trang.
class SourceClaim {
  const SourceClaim({required this.text, required this.attribution, this.page});
  final String text;
  final String attribution;
  final int? page;
}

/// Lời của SAM về nguồn — TÁCH KIỂU khỏi lời nguồn.
class SamInterpretation {
  const SamInterpretation(this.text);
  final String text;
}

/// Kết luận CỦA HỌC SINH — tách kiểu khỏi cả hai tầng trên.
class StudentConclusion {
  const StudentConclusion(this.text);
  final String text;
}

/// Ba LẬP TRƯỜNG với nguồn cho trẻ chọn — đây là source evaluation (kỹ năng
/// Sử), không phải câu hỏi có đáp án đúng; vì thế không chấm.
const kConclusionStances = [
  'Nguồn này là bằng chứng cho điều bài học nói',
  'Nguồn này hay nhưng em muốn xem thêm nguồn khác',
  'Em có kết luận khác — em sẽ kể cho thầy cô',
];

class SourceReaderScreen extends StatefulWidget {
  const SourceReaderScreen(
      {super.key,
      required this.source,
      required this.learningContext,
      this.onFinished,
      this.now});

  final SuSource source;

  /// ⭐⭐ WAL-189 — cùng luật WAL-175/178 đã có ở Experiment: `lookup` sinh
  /// TRACE, không sinh EVIDENCE. `_conclude` đọc field này trước khi ghi.
  final LearningContext learningContext;

  /// Trả về sự kiện đã phát — NƠI GỌI ghi kho qua recordSession (một chỗ ghi).
  final void Function(List<LearningEvent> events)? onFinished;
  final DateTime Function()? now;

  @override
  State<SourceReaderScreen> createState() => _SourceReaderScreenState();
}

class _SourceReaderScreenState extends State<SourceReaderScreen> {
  // ⭐ WAL-210 (audit C1): token PHIÊN sinh một lần lúc mở màn — mở lại
  // cùng bài là phiên khác, id khác (đồng hồ máy, không ăn nhịp `now`).
  final String _token = newEvidenceSessionToken(DateTime.now());
  final List<LearningEvent> _events = [];
  bool _readSource = false;
  int? _stance;
  bool _done = false;
  int _seq = 0;

  SuSource get s => widget.source;
  DateTime _at() => (widget.now ?? DateTime.now)();

  bool get _supported =>
      s.excerpt.trim().isNotEmpty && s.attribution.trim().isNotEmpty;

  SourceClaim get _claim =>
      SourceClaim(text: s.excerpt, attribution: s.attribution, page: s.page);
  SamInterpretation? get _gloss =>
      s.samGloss == null ? null : SamInterpretation(s.samGloss!);

  void _markReadSource() {
    if (_readSource) return;
    // Đọc-nguồn-xong CHỈ mở tầng sau — KHÔNG phát bằng chứng (đọc ≠ mastery).
    setState(() => _readSource = true);
  }

  void _conclude(int i) {
    if (_done) return;
    // ⭐⭐ WAL-189 — tra cứu sinh TRACE, không sinh EVIDENCE (WAL-175/178):
    // trẻ vẫn thấy đúng luồng kết luận, chỉ không ghi thành bằng chứng.
    if (widget.learningContext.intent != LearningIntent.lookup) {
      _events.add(LearningEvent(
        eventId: evidenceEventId(
            exerciseId: '${s.book}:p${s.page}',
            sessionToken: _token,
            seq: _seq++),
        skillCaseId: 'su-doc-tu-lieu',
        kind: EvidenceKind.independentAttempt,
        correct: null, // ⭐ UNKNOWN ≠ SAI: kết luận sử không có một đáp án duy nhất
        exerciseId: '${s.book}:p${s.page}',
        conceptIds: const ['su-tu-lieu'],
        at: _at(),
        support: SupportLevel.none,
        policyId: 'source-reader-v1',
        knowledgeVersion: knowledgeModelVersion, // WAL-114
      ));
    }
    setState(() {
      _stance = i;
      _done = true;
    });
    widget.onFinished?.call(_events);
  }

  @override
  Widget build(BuildContext context) {
    final List<Widget> children;
    if (!_supported) {
      children = _unsupportedView();
    } else if (!_readSource) {
      children = _sourceView();
    } else if (_done) {
      children = _doneView();
    } else {
      children = _concludeView();
    }
    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: ListView(
            padding: const EdgeInsets.all(WalSpacing.lg), children: children),
      ),
    );
  }

  // ---- ba widget dán nhãn: mỗi cái CHỈ nhận đúng kiểu tầng của nó ----------

  Widget _sourceCard(SourceClaim c, {bool compact = false}) => _labeled(
        'NGUỒN NÓI GÌ',
        Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(c.text,
              style: TextStyle(
                  fontSize: compact ? WalType.secondary : WalType.body,
                  color: compact ? WalColors.inkSoft : WalColors.ink,
                  height: 1.55,
                  fontStyle: FontStyle.italic)),
          const SizedBox(height: WalSpacing.sm),
          Text('— ${c.attribution}${c.page == null ? '' : ' · tr. ${c.page}'}',
              style: const TextStyle(
                  fontSize: WalType.secondary, color: WalColors.inkSoft)),
        ]),
        color: Colors.white,
      );

  Widget _samCard(SamInterpretation g) => _labeled(
        'SAM DIỄN GIẢI',
        Text(g.text,
            style: const TextStyle(
                fontSize: WalType.body, color: WalColors.ink, height: 1.5)),
        color: WalColors.surfaceLavender,
      );

  Widget _conclusionCard(StudentConclusion c) => _labeled(
        'EM KẾT LUẬN',
        Text(c.text,
            style: const TextStyle(
                fontSize: WalType.body,
                color: WalColors.ink,
                fontWeight: FontWeight.w600,
                height: 1.5)),
        color: Colors.white,
      );

  // ---- views ---------------------------------------------------------------

  List<Widget> _unsupportedView() => [
        Center(
            child: Image.asset('assets/mascot/sam-admit-uncertainty.png',
                width: densityOf(context).mascotHero, height: densityOf(context).mascotHero)),
        const SizedBox(height: WalSpacing.md),
        _card(const Text(
            'Tư liệu này tớ chưa có đủ nguyên văn hoặc nguồn dẫn — tớ không '
            'dám đưa cho con đọc. Mình chọn bài khác nhé.',
            style: TextStyle(
                fontSize: WalType.body, color: WalColors.ink, height: 1.45))),
        const SizedBox(height: WalSpacing.lg),
        _backButton(),
      ];

  List<Widget> _sourceView() => [
        Row(children: [
          Image.asset('assets/mascot/sam-listen.png', width: densityOf(context).mascotChip, height: densityOf(context).mascotChip),
          const SizedBox(width: WalSpacing.md),
          const Expanded(
            child: Text(
                'Đây là TƯ LIỆU GỐC in trong sách. Con đọc kỹ lời của nguồn '
                'trước — rồi mình mới bàn tiếp nhé.',
                style: TextStyle(fontSize: WalType.body, color: WalColors.ink)),
          ),
        ]),
        const SizedBox(height: WalSpacing.md),
        _sourceCard(_claim),
        const SizedBox(height: WalSpacing.lg),
        SizedBox(
          width: double.infinity,
          height: WalSpacing.minTouch + 8,
          child: FilledButton(
            style: _primaryBtn(),
            onPressed: _markReadSource,
            child: const Text('Con đọc nguồn xong 📜',
                style: TextStyle(fontSize: WalType.body)),
          ),
        ),
      ];

  List<Widget> _concludeView() => [
        _sourceCard(_claim, compact: true),
        const SizedBox(height: WalSpacing.md),
        if (_gloss != null) ...[
          _samCard(_gloss!),
          const SizedBox(height: WalSpacing.md),
        ],
        _card(const Text('Đọc nguồn xong, EM kết luận thế nào? Không có đáp án '
            'đúng-sai ở đây — quan trọng là con nghĩ từ nguồn.',
            style: TextStyle(
                fontSize: WalType.body, color: WalColors.ink, height: 1.45))),
        const SizedBox(height: WalSpacing.md),
        for (var i = 0; i < kConclusionStances.length; i++) ...[
          SizedBox(
            width: double.infinity,
            child: FilledButton(
              style: FilledButton.styleFrom(
                backgroundColor: Colors.white,
                foregroundColor: WalColors.ink,
                alignment: Alignment.centerLeft,
                padding: const EdgeInsets.symmetric(
                    horizontal: WalSpacing.lg, vertical: WalSpacing.md),
                shape: RoundedRectangleBorder(
                    borderRadius:
                        BorderRadius.circular(WalSpacing.radiusButton)),
              ),
              onPressed: () => _conclude(i),
              child: Text(kConclusionStances[i],
                  style: const TextStyle(fontSize: WalType.body, height: 1.35)),
            ),
          ),
          const SizedBox(height: WalSpacing.sm),
        ],
      ];

  List<Widget> _doneView() => [
        Center(
            child: Image.asset('assets/mascot/sam-explain.png',
                width: densityOf(context).mascotHero, height: densityOf(context).mascotHero)),
        const SizedBox(height: WalSpacing.md),
        _conclusionCard(StudentConclusion(kConclusionStances[_stance!])),
        const SizedBox(height: WalSpacing.md),
        _card(const Text(
            'Một nguồn chưa chắc đã đủ — sử học cần NHIỀU nguồn để chắc chắn. '
            'Tớ ghi lại là con đã đọc nguồn và TỰ kết luận rồi nhé.',
            style: TextStyle(
                fontSize: WalType.body, color: WalColors.ink, height: 1.45))),
        const SizedBox(height: WalSpacing.lg),
        _backButton(),
      ];

  // ---- chrome --------------------------------------------------------------

  ButtonStyle _primaryBtn() => FilledButton.styleFrom(
      backgroundColor: WalColors.primary500,
      shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(WalSpacing.radiusButton)));

  Widget _backButton() => SizedBox(
        height: WalSpacing.minTouch + 8,
        child: FilledButton(
          style: _primaryBtn(),
          onPressed: () => Navigator.of(context).maybePop(),
          child: const Text('Về danh sách bài',
              style: TextStyle(fontSize: WalType.body)),
        ),
      );

  Widget _labeled(String label, Widget child, {required Color color}) =>
      Container(
        width: double.infinity,
        padding: const EdgeInsets.all(WalSpacing.lg),
        decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(WalSpacing.radiusCard)),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(label,
              style: const TextStyle(
                  fontSize: WalType.secondary,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 0.6,
                  color: WalColors.inkSoft)),
          const SizedBox(height: WalSpacing.sm),
          child,
        ]),
      );

  Widget _card(Widget child) => Container(
        width: double.infinity,
        padding: const EdgeInsets.all(WalSpacing.lg),
        decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(WalSpacing.radiusCard)),
        child: child,
      );
}
