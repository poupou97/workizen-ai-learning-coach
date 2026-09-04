/// WAL-144 #KHTN — SURFACE THÍ NGHIỆM (bounded, dữ liệu THẬT Khoa học 5).
///
/// Flow đúng File 04: Hiện tượng → DỰ ĐOÁN (của TRẺ) → Tiến hành (VERBATIM
/// từ sách) → EM QUAN SÁT ĐƯỢC (của trẻ) → so sánh — không chấm.
///
/// Bất biến (giữ bằng test + đột biến):
/// - ⭐ PREDICT GATE: sách in «Dự đoán…» ⇒ các bước Tiến hành KHOÁ tới khi
///   trẻ ghi dự đoán CỦA MÌNH (cùng họ READ/SOURCE gate — khoa học bắt đầu
///   bằng giả thuyết, không bằng xem đáp án).
/// - Lời sách VERBATIM dưới nhãn riêng (CHUẨN BỊ / TIẾN HÀNH); lời của trẻ
///   dưới nhãn «DỰ ĐOÁN CỦA EM» / «EM QUAN SÁT ĐƯỢC» — không lẫn.
/// - Không chấm đúng/sai quan sát (correct=null — UNKNOWN ≠ SAI); không %,
///   không điểm. Một sự kiện khi hoàn tất, policy experiment-v1.
library;

import 'package:flutter/material.dart';

import '../../app/theme/band_density_scope.dart';
import '../../app/theme/wal_tokens.dart';
import '../../core/knowledge/slice_curriculum.dart' show knowledgeModelVersion;
import '../../core/student/learning_evidence.dart';
import '../../core/student/mastery.dart';
import '../subjects/lesson_index.dart';

class ExperimentScreen extends StatefulWidget {
  const ExperimentScreen(
      {super.key, required this.experiment, this.onFinished, this.now});

  final KhoaExperiment experiment;
  final void Function(List<LearningEvent> events)? onFinished;
  final DateTime Function()? now;

  @override
  State<ExperimentScreen> createState() => _ExperimentScreenState();
}

class _ExperimentScreenState extends State<ExperimentScreen> {
  final _predictCtrl = TextEditingController();
  final _observeCtrl = TextEditingController();
  bool _predicted = false;
  bool _done = false;

  KhoaExperiment get e => widget.experiment;
  DateTime _at() => (widget.now ?? DateTime.now)();

  bool get _needsPrediction => (e.duDoan ?? '').trim().isNotEmpty;

  @override
  void dispose() {
    _predictCtrl.dispose();
    _observeCtrl.dispose();
    super.dispose();
  }

  void _submitPrediction() {
    if (_predictCtrl.text.trim().isEmpty) return;
    // Dự đoán CHỈ mở gate — chưa phải bằng chứng (giả thuyết ≠ mastery).
    setState(() => _predicted = true);
  }

  void _finish() {
    if (_done) return;
    setState(() => _done = true);
    widget.onFinished?.call([
      LearningEvent(
        eventId: '${e.book}:p${e.page}#0',
        skillCaseId: 'khtn-thi-nghiem',
        kind: EvidenceKind.independentAttempt,
        correct: null, // ⭐ quan sát không bị máy chấm — UNKNOWN ≠ SAI
        exerciseId: '${e.book}:p${e.page}',
        conceptIds: const ['khtn-quan-sat'],
        at: _at(),
        support: SupportLevel.none,
        policyId: 'experiment-v1',
        knowledgeVersion: knowledgeModelVersion,
      )
    ]);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(WalSpacing.lg),
          children: _done
              ? _doneView()
              : [
                  _samRow(
                      'sam-think.png',
                      'Thí nghiệm trong SGK: «${e.title}». '
                      '${_needsPrediction ? 'Con DỰ ĐOÁN trước rồi mới làm nhé — nhà khoa học là vậy đó.' : 'Con đọc kỹ các bước rồi làm cùng người lớn nhé.'}'),
                  const SizedBox(height: WalSpacing.md),
                  _labeled(
                      'CHUẨN BỊ',
                      Text(e.chuanBi,
                          style: const TextStyle(
                              fontSize: WalType.body,
                              color: WalColors.ink,
                              height: 1.5))),
                  const SizedBox(height: WalSpacing.md),
                  if (_needsPrediction && !_predicted) ...[
                    _labeled(
                        'DỰ ĐOÁN CỦA EM',
                        Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(e.duDoan!,
                                  style: const TextStyle(
                                      fontSize: WalType.body,
                                      color: WalColors.ink,
                                      height: 1.5)),
                              const SizedBox(height: WalSpacing.sm),
                              TextField(
                                controller: _predictCtrl,
                                minLines: 2,
                                maxLines: 4,
                                decoration: const InputDecoration(
                                    hintText: 'Em nghĩ điều gì sẽ xảy ra…'),
                              ),
                            ])),
                    const SizedBox(height: WalSpacing.md),
                    _primary('Chốt dự đoán — xem các bước 🔬',
                        _submitPrediction),
                  ] else ...[
                    if (_needsPrediction)
                      _labeled(
                          'DỰ ĐOÁN CỦA EM',
                          Text(_predictCtrl.text.trim(),
                              style: const TextStyle(
                                  fontSize: WalType.body,
                                  color: WalColors.ink,
                                  height: 1.5))),
                    if (_needsPrediction)
                      const SizedBox(height: WalSpacing.md),
                    _labeled(
                        'TIẾN HÀNH',
                        Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              for (final s in e.tienHanh)
                                Padding(
                                  padding: const EdgeInsets.only(
                                      bottom: WalSpacing.sm),
                                  child: Text('• $s',
                                      style: const TextStyle(
                                          fontSize: WalType.body,
                                          color: WalColors.ink,
                                          height: 1.5)),
                                ),
                              if (e.quanSat != null)
                                Text(e.quanSat!,
                                    style: const TextStyle(
                                        fontSize: WalType.body,
                                        fontStyle: FontStyle.italic,
                                        color: WalColors.inkSoft,
                                        height: 1.5)),
                            ])),
                    const SizedBox(height: WalSpacing.md),
                    _labeled(
                        'EM QUAN SÁT ĐƯỢC',
                        TextField(
                          controller: _observeCtrl,
                          minLines: 2,
                          maxLines: 5,
                          decoration: const InputDecoration(
                              hintText:
                                  'Làm xong, em ghi lại điều em thấy…'),
                        )),
                    const SizedBox(height: WalSpacing.md),
                    _primary('Em làm xong thí nghiệm ✅', _finish),
                  ],
                  const SizedBox(height: WalSpacing.md),
                  Text('Nguồn: SGK ${e.subject} · tr. ${e.page}',
                      style: const TextStyle(
                          fontSize: WalType.secondary,
                          color: WalColors.inkSoft)),
                ],
        ),
      ),
    );
  }

  List<Widget> _doneView() => [
        Center(
            child: Image.asset('assets/mascot/sam-celebrate-independence.png',
                width: densityOf(context).mascotHero, height: densityOf(context).mascotHero)),
        const SizedBox(height: WalSpacing.md),
        if (_needsPrediction)
          _labeled(
              'DỰ ĐOÁN CỦA EM',
              Text(_predictCtrl.text.trim(),
                  style: const TextStyle(
                      fontSize: WalType.body, color: WalColors.ink))),
        if (_needsPrediction) const SizedBox(height: WalSpacing.sm),
        _labeled(
            'EM QUAN SÁT ĐƯỢC',
            Text(_observeCtrl.text.trim().isEmpty
                    ? '(em chưa ghi)'
                    : _observeCtrl.text.trim(),
                style: const TextStyle(
                    fontSize: WalType.body, color: WalColors.ink))),
        const SizedBox(height: WalSpacing.md),
        // ⭐⭐ WAL-176 — câu chốt PHẢI khớp việc trẻ vừa thật sự làm: bài
        // không có bước dự đoán (SGK không in) thì không được nhắc «dự đoán»
        // — nhắc một việc trẻ chưa từng làm là câu nói không thật, dù nghe
        // hợp lý ở bài khác.
        _card(Text(
            _needsPrediction
                ? 'So sánh dự đoán với điều em thấy — giống hay khác đều quý: '
                    'nhà khoa học học từ chính chỗ khác nhau đó. Tớ không chấm '
                    'đúng/sai; con kể cho thầy cô nghe kết quả nhé.'
                : 'Điều em quan sát được rất đáng quý. Tớ không chấm đúng/sai; '
                    'con kể cho thầy cô nghe kết quả nhé.',
            style: const TextStyle(
                fontSize: WalType.body, color: WalColors.ink, height: 1.45))),
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
            child: const Text('Về danh sách bài',
                style: TextStyle(fontSize: WalType.body)),
          ),
        ),
      ];

  Widget _samRow(String asset, String text) => Row(children: [
        Image.asset('assets/mascot/$asset', width: densityOf(context).mascotChip, height: densityOf(context).mascotChip),
        const SizedBox(width: WalSpacing.md),
        Expanded(
            child: Text(text,
                style: const TextStyle(
                    fontSize: WalType.body, color: WalColors.ink))),
      ]);

  Widget _primary(String label, VoidCallback onPressed) => SizedBox(
        width: double.infinity,
        height: WalSpacing.minTouch + 8,
        child: FilledButton(
          style: FilledButton.styleFrom(
              backgroundColor: WalColors.primary500,
              shape: RoundedRectangleBorder(
                  borderRadius:
                      BorderRadius.circular(WalSpacing.radiusButton))),
          onPressed: onPressed,
          child: Text(label, style: const TextStyle(fontSize: WalType.body)),
        ),
      );

  Widget _labeled(String label, Widget child) => Container(
        width: double.infinity,
        padding: const EdgeInsets.all(WalSpacing.lg),
        decoration: BoxDecoration(
            color: Colors.white,
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
