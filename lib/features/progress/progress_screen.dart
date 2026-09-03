/// WAL-142 #31 — PROGRESS: chữ claim-gated phủ lên truths — KHÔNG %/điểm/XP/
/// streak (§16). Mọi câu trạng thái đi qua explainConcept (một giọng, một luật).
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/coach/parent_explanation.dart';
import '../../core/knowledge/slice_curriculum.dart';
import '../../core/store/learner_profile.dart';
import '../../core/store/learner_store.dart';
import '../../core/student/concept_summary.dart';
import '../../core/student/learning_evidence.dart';
import '../../core/student/mastery.dart';
import '../../core/student/review_schedule.dart';
import '../learning_session/slice_flow.dart' show masteryFromStore;

class ProgressScreen extends StatefulWidget {
  const ProgressScreen({super.key, required this.profile, required this.store});
  final LearnerProfile profile;
  final LearnerStore store;

  @override
  State<ProgressScreen> createState() => _ProgressScreenState();
}

class _ProgressScreenState extends State<ProgressScreen> {
  ConceptSummary? _summary;
  ConceptMastery? _mastery;
  int _independent = 0, _assisted = 0, _selfCorrections = 0;
  bool _loaded = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    // WAL-170: màn này nói về BẰNG CHỨNG của trẻ (không trưng nguồn của một
    // bài) ⇒ lấy các dòng chương trình đã nạp cho lớp. Nhiều dòng thì chưa có
    // luật gộp claim ⇒ chỉ tổng hợp khi có ĐÚNG một dòng, còn lại nói thật là
    // chưa kể được — không trộn bằng chứng hai khái niệm thành một câu.
    final all = curriculaForLearner(widget.profile);
    final c = all.length == 1 ? all.single : null;
    ConceptMastery? m;
    if (c != null) {
      m = await masteryFromStore(
          widget.store, widget.profile.learnerId, c);
    }
    final sessions =
        await widget.store.sessions(learnerId: widget.profile.learnerId);
    var ind = 0, ast = 0, sc = 0;
    for (final s in sessions) {
      if (maxSupportIn(s) == SupportLevel.none) {
        ind++;
      } else {
        ast++;
      }
      sc += s.events
          .where((e) => e.kind == EvidenceKind.selfCorrection)
          .length;
    }
    if (!mounted) return;
    setState(() {
      _mastery = m;
      // kho TRẮNG (mastery tồn tại nhưng 0 evidence) = chưa có gì để kể.
      final hasEvidence =
          m != null && m.cases.values.any((cm) => cm.hasEvidence);
      _summary = (c != null && m != null && hasEvidence)
          ? ConceptSummary.of(m,
              knownCaseIds: {for (final k in c.cases) k.id},
              now: DateTime.now())
          : null;
      _independent = ind;
      _assisted = ast;
      _selfCorrections = sc;
      _loaded = true;
    });
  }

  @override
  Widget build(BuildContext context) {
    final s = _summary;
    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: !_loaded
            ? const SizedBox.shrink()
            : ListView(
                padding: const EdgeInsets.all(WalSpacing.lg),
                children: [
                  const Text('Tiến bộ của con',
                      style: TextStyle(
                          fontSize: WalType.display,
                          fontWeight: FontWeight.w700,
                          color: WalColors.ink)),
                  const SizedBox(height: WalSpacing.sm),
                  // ĐỘC LẬP vs CÓ HỖ TRỢ — chiều Premium-insight nhưng bản
                  // đếm thô này thuộc BASIC (không paywall learning truth).
                  _card(Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('PHIÊN HỌC',
                            style: TextStyle(
                                fontSize: WalType.secondary,
                                fontWeight: FontWeight.w700,
                                letterSpacing: 0.6,
                                color: WalColors.inkSoft)),
                        const SizedBox(height: WalSpacing.sm),
                        Text(
                            'Con TỰ LÀM trọn vẹn $_independent phiên · có SAM '
                            'giúp $_assisted phiên.',
                            style: const TextStyle(
                                fontSize: WalType.body,
                                color: WalColors.ink,
                                height: 1.5)),
                        if (_selfCorrections > 0)
                          Text(
                              'Con tự phát hiện và sửa $_selfCorrections lần — '
                              'quý hơn làm đúng ngay.',
                              style: const TextStyle(
                                  fontSize: WalType.body,
                                  color: WalColors.mintText,
                                  height: 1.5)),
                      ])),
                  const SizedBox(height: WalSpacing.md),
                  if (s == null)
                    _card(const Text(
                        'Con chưa có bằng chứng học nào trong phạm vi SAM đang '
                        'theo — làm một bài là có ngay dòng đầu tiên ở đây.',
                        style: TextStyle(
                            fontSize: WalType.body,
                            color: WalColors.ink,
                            height: 1.5)))
                  else ...[
                    _conceptCard(s),
                    const SizedBox(height: WalSpacing.md),
                    _reviewCard(),
                  ],
                  const SizedBox(height: WalSpacing.md),
                  _card(const Text(
                      'SAM chỉ kể điều có bằng chứng — không điểm số, không '
                      'xếp hạng. Các môn khác sẽ hiện dần khi con học cùng SAM.',
                      style: TextStyle(
                          fontSize: WalType.secondary,
                          color: WalColors.inkSoft,
                          height: 1.4))),
                ],
              ),
      ),
    );
  }

  Widget _conceptCard(ConceptSummary s) {
    final exp = explainConcept(s,
        conceptDisplayName: 'cộng, trừ phân số khác mẫu số',
        caseDisplayNames: const {
          'denominator-divisible': 'một mẫu số chia hết cho mẫu số còn lại',
          'denominator-non-divisible': 'hai mẫu số không chia hết cho nhau',
        });
    final tok = switch (s.claim) {
      ConceptClaim.mastered => LearningStateToken.mastered,
      ConceptClaim.strongOnObserved => LearningStateToken.strongOnObserved,
      ConceptClaim.developing => LearningStateToken.developing,
      ConceptClaim.needsWork => LearningStateToken.needsWork,
      ConceptClaim.insufficientEvidence =>
        LearningStateToken.insufficientEvidence,
      ConceptClaim.noEvidence => LearningStateToken.noEvidence,
    };
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(WalSpacing.lg),
      decoration: BoxDecoration(
          color: tok.bg,
          borderRadius: BorderRadius.circular(WalSpacing.radiusCard)),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('Toán · Cộng, trừ phân số khác mẫu số',
            style: TextStyle(
                fontSize: WalType.body,
                fontWeight: FontWeight.w700,
                color: tok.fg)),
        const SizedBox(height: WalSpacing.sm),
        Text(exp.message,
            style: const TextStyle(
                fontSize: WalType.body, color: WalColors.ink, height: 1.5)),
      ]),
    );
  }

  Widget _reviewCard() {
    final m = _mastery!;
    final now = DateTime.now();
    final due = <String>[];
    m.cases.forEach((id, cm) {
      final st = reviewStateOf(cm, now);
      if (st.urgency == ReviewUrgency.reviewDue ||
          st.urgency == ReviewUrgency.overdue) {
        due.add(id);
      }
    });
    return _card(Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      const Text('LỊCH GẶP LẠI',
          style: TextStyle(
              fontSize: WalType.secondary,
              fontWeight: FontWeight.w700,
              letterSpacing: 0.6,
              color: WalColors.inkSoft)),
      const SizedBox(height: WalSpacing.sm),
      Text(
          due.isEmpty
              ? 'Chưa có dạng nào tới lúc gặp lại — cứ học tiếp nhé.'
              : 'Tới lúc gặp lại ${due.length} dạng bài — nhẹ nhàng thôi, '
                  'gặp lại là để nhớ lâu.',
          style: const TextStyle(
              fontSize: WalType.body, color: WalColors.ink, height: 1.5)),
    ]));
  }

  Widget _card(Widget child) => Container(
        width: double.infinity,
        padding: const EdgeInsets.all(WalSpacing.lg),
        decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(WalSpacing.radiusCard)),
        child: child,
      );
}
