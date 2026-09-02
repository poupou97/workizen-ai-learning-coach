/// ⭐⭐ WAL-108 — FIRST VERTICAL SLICE: dây 17 bước của Master Order §3.
///
/// HOME → CAMERA → OCR → CONFIRM → CANONICAL PROBLEM → CURRICULUM CONTEXT →
/// SKILLCASE → TUTORSCOPE → METHOD → DIAGNOSTIC → INDEPENDENT ATTEMPT →
/// SMALL HINT → YOUR TURN → RESPONSE → LEARNING EVIDENCE → KNOWLEDGE STATE →
/// NEXT ACTION.
///
/// Mọi mắt xích đều là object canonical đã có test — file này CHỈ NỐI, không
/// chế luật mới. Bất biến giữ ở đây:
/// - learnerId đi XUYÊN flow (đầu vào bắt buộc, không global);
/// - mastery/diagnostic lấy từ KHO THẬT (replay), không fixture;
/// - curriculum ngoài phạm vi (grade ≠ 5) ⇒ fail closed, KHÔNG dạy sai cấp;
/// - phiên (kể cả BỎ DỞ) ghi MỘT LẦN qua recordSession — không phiên rỗng.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/adaptive/adaptive_engine.dart';
import '../../core/curriculum/canonical_problem.dart';
import '../../core/knowledge/slice_curriculum.dart';
import '../../core/store/learner_profile.dart';
import '../../core/store/learner_store.dart';
import '../../core/store/learning_session.dart';
import '../../core/student/evidence_weighting.dart';
import '../../core/student/mastery.dart';
import '../../core/tutor/teaching_provenance.dart';
import '../camera/capture_screen.dart';
import '../camera/confirm_problem_screen.dart';
import '../camera/education_ocr_adapter.dart';
import '../shell/session_recorder.dart';
import '../tutor/tutor_screen.dart';
import '../tutor/tutor_session.dart';

/// KNOWLEDGE STATE từ KHO: replay bằng chứng thật của TỪNG ca — không cache,
/// không fixture. Đây là hàm mission «Hôm nay» cũng dùng — một luật một chỗ.
Future<ConceptMastery> masteryFromStore(
    LearnerStore store, String learnerId, SliceCurriculum c) async {
  const p = BktParams.freeResponse;
  final cases = <String, CaseMastery>{};
  for (final sc in c.cases) {
    final log =
        await store.evidenceFor(learnerId: learnerId, skillCaseId: sc.id);
    cases[sc.id] = replayMastery(log, p);
  }
  return ConceptMastery(conceptId: c.conceptId, cases: cases);
}

/// HOME → …: mở flow bài-tập-về-nhà cho ĐÚNG learner này.
Future<void> startHomeworkFlow(
  BuildContext context, {
  required LearnerProfile profile,
  required LearnerStore store,
  required EducationOcrAdapter ocr,
}) async {
  final nav = Navigator.of(context);
  while (true) {
    // CAMERA + OCR (adapter — OCR ≠ evidence)
    final outcome = await nav.push<CaptureOutcome>(
        MaterialPageRoute(builder: (_) => CaptureScreen(ocr: ocr)));
    if (outcome == null) return; // trẻ quay lại — huỷ, không ghi gì

    // CONFIRM — ranh giới an toàn WAL-64: nơi DUY NHẤT sinh ConfirmedProblem
    final problem = await nav.push<CanonicalProblem>(MaterialPageRoute(
      builder: (ctx) => ConfirmProblemScreen(
        hypothesis: outcome.hypothesis,
        onConfirmed: (p) => Navigator.of(ctx).pop(p),
        onRetake: () => Navigator.of(ctx).pop(), // null ⇒ vòng lại camera
      ),
    ));
    if (problem == null) continue; // chụp lại

    // CURRICULUM CONTEXT → SKILLCASE → TUTORSCOPE → METHOD → DIAGNOSTIC
    final curriculum = curriculumFor(profile);
    ConceptMastery? mastery;
    if (curriculum != null) {
      mastery = await masteryFromStore(store, profile.learnerId, curriculum);
    }
    await nav.push(MaterialPageRoute(
        builder: (_) => ProblemContextScreen(
              problem: problem,
              profile: profile,
              store: store,
              curriculum: curriculum,
              mastery: mastery,
            )));
    return;
  }
}

/// CURRICULUM CONTEXT + DIAGNOSTIC — «SAM hiểu bài này nằm ở đâu trong
/// chương trình, và vì sao chọn cách này» TRƯỚC khi dạy.
class ProblemContextScreen extends StatelessWidget {
  const ProblemContextScreen({
    super.key,
    required this.problem,
    required this.profile,
    required this.store,
    required this.curriculum,
    required this.mastery,
  });

  final CanonicalProblem problem;
  final LearnerProfile profile;
  final LearnerStore store;

  /// `null` = ngoài phạm vi chương trình đã nạp (grade ≠ 5) — fail closed.
  final SliceCurriculum? curriculum;
  final ConceptMastery? mastery;

  @override
  Widget build(BuildContext context) {
    final c = curriculum;
    if (c == null || mastery == null) return _outOfScope(context);

    final fp = FractionProblem.parse(problem.expression);
    final exerciseCase = fp == null ? null : fractionCase(fp.b, fp.d);
    final decision = decide(
      conceptId: c.conceptId,
      exerciseCase: exerciseCase,
      mastery: mastery!,
      stage: c.stage,
      catalogue: c.catalogue,
      caseCatalogue: c.cases,
    );
    final method = decision.scope.allowedMethods.isEmpty
        ? null
        : decision.scope.allowedMethods.first;
    final provenance = method == null
        ? null
        : explainTeaching(
            scope: decision.scope,
            methodId: method.id,
            exerciseCase: exerciseCase);
    final caseName = {
      for (final sc in c.cases) sc.id: sc.condition
    }[exerciseCase];

    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(WalSpacing.lg),
          child: ListView(children: [
            Text(c.activityLabel,
                style: const TextStyle(
                    fontSize: WalType.secondary,
                    fontWeight: FontWeight.w700,
                    color: WalColors.inkSoft)),
            const SizedBox(height: WalSpacing.sm),
            _card(Text(problem.expression,
                textAlign: TextAlign.center,
                style: const TextStyle(
                    fontSize: WalType.display,
                    fontWeight: FontWeight.w700,
                    color: WalColors.ink))),
            const SizedBox(height: WalSpacing.sm),
            Text(
                caseName != null
                    ? 'Dạng bài: $caseName'
                    : 'Tớ chưa nhận ra dạng bài này.',
                style: const TextStyle(
                    fontSize: WalType.secondary, color: WalColors.inkSoft)),
            const SizedBox(height: WalSpacing.md),
            // DIAGNOSTIC — reason NGUYÊN VĂN của engine, UI không suy diễn.
            _card(
                Text(decision.reason,
                    style: const TextStyle(
                        fontSize: WalType.body,
                        color: WalColors.ink,
                        height: 1.45)),
                color: WalColors.surfaceLavender),
            if (provenance != null) ...[
              const SizedBox(height: WalSpacing.md),
              // WHY THIS METHOD + SOURCE — provenance TRƯỚC khi vào bài (§3).
              _card(Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Cách «${provenance.method.name}»',
                        style: const TextStyle(
                            fontSize: WalType.body,
                            fontWeight: FontWeight.w700,
                            color: WalColors.ink)),
                    const SizedBox(height: WalSpacing.sm),
                    Text(provenance.whyLineForChild,
                        style: const TextStyle(
                            fontSize: WalType.secondary,
                            color: WalColors.ink,
                            height: 1.4)),
                    const SizedBox(height: WalSpacing.sm),
                    Text(provenance.sourceLineForChild,
                        style: const TextStyle(
                            fontSize: WalType.secondary,
                            fontWeight: FontWeight.w600,
                            color: WalColors.primaryText,
                            height: 1.4)),
                    const SizedBox(height: WalSpacing.sm),
                    Text(
                        'Phiên bản: ${TutorSession.policyId} · '
                        '$knowledgeModelVersion',
                        style: const TextStyle(
                            fontSize: WalType.secondary,
                            color: WalColors.inkSoft)),
                  ])),
            ],
            const SizedBox(height: WalSpacing.lg),
            if (fp != null && exerciseCase != null && provenance != null)
              SizedBox(
                height: WalSpacing.minTouch + 8,
                child: FilledButton(
                  style: FilledButton.styleFrom(
                      backgroundColor: WalColors.primary500,
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(
                              WalSpacing.radiusButton))),
                  onPressed: () => _startTutor(context, fp, exerciseCase,
                      decision.scope, provenance, c),
                  child: const Text('Làm bài này ▸',
                      style: TextStyle(fontSize: WalType.body)),
                ),
              )
            else
              // Ca không xác định / không method được phép ⇒ KHÔNG có nút
              // làm bài — SAM nhận «chưa chắc», không dạy bừa (fail closed).
              _card(
                  const Text(
                      'Tớ chưa chắc cách giải bài này nên không dám dạy bừa. '
                      'Con hỏi thầy cô hoặc bố mẹ giúp tớ nhé?',
                      style: TextStyle(
                          fontSize: WalType.body,
                          color: WalColors.ink,
                          height: 1.45)),
                  color: WalColors.surfaceLavender),
            const SizedBox(height: WalSpacing.sm),
            SizedBox(
              height: WalSpacing.minTouch,
              child: TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('Về Hôm nay',
                    style: TextStyle(
                        fontSize: WalType.body,
                        color: WalColors.primaryText)),
              ),
            ),
          ]),
        ),
      ),
    );
  }

  Future<void> _startTutor(
    BuildContext context,
    FractionProblem fp,
    String exerciseCase,
    scope,
    TeachingProvenance provenance,
    SliceCurriculum c,
  ) async {
    final nav = Navigator.of(context);
    final session = TutorSession(
      exerciseId: problem.exerciseId,
      skillCaseId: exerciseCase,
      problem: fp,
      scope: scope,
    );
    await nav.push(MaterialPageRoute(
        builder: (_) => TutorScreen(
            session: session,
            expression: problem.expression,
            provenance: provenance)));
    // LEARNING EVIDENCE — ghi MỘT LẦN, kể cả bài bỏ dở (bằng chứng thật).
    final events = session.log.events;
    if (events.isEmpty) return; // chưa làm gì ⇒ không phiên rỗng
    await recordSession(
      store: store,
      learnerId: profile.learnerId,
      subjectId: c.subjectId,
      events: events,
      trigger: SessionTrigger.cameraHomework,
    );
    if (!nav.mounted) return;
    // KNOWLEDGE STATE + NEXT ACTION — đọc lại TỪ KHO (chứng minh vòng khép kín)
    nav.pushReplacement(MaterialPageRoute(
        builder: (_) => KnowledgeStateScreen(
            profile: profile, store: store, curriculum: c)));
  }

  Widget _outOfScope(BuildContext context) => Scaffold(
        backgroundColor: WalColors.surface,
        body: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(WalSpacing.lg),
            child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(
                    'Tớ chưa học chương trình lớp ${profile.grade} nên chưa '
                    'dám hướng dẫn bài này — dạy sai cấp còn tệ hơn không dạy.',
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                        fontSize: WalType.title,
                        color: WalColors.ink,
                        height: 1.4),
                  ),
                  const SizedBox(height: WalSpacing.xl),
                  SizedBox(
                    height: WalSpacing.minTouch + 8,
                    child: FilledButton(
                      style: FilledButton.styleFrom(
                          backgroundColor: WalColors.primary500),
                      onPressed: () => Navigator.of(context).pop(),
                      child: const Text('Về Hôm nay',
                          style: TextStyle(fontSize: WalType.body)),
                    ),
                  ),
                ]),
          ),
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

/// KNOWLEDGE STATE + NEXT ACTION — đọc lại từ KHO sau khi phiên đã ghi.
/// Không %, không điểm: chữ trung thực theo bằng chứng, và hành động kế
/// tiếp SINH TỪ decide() trên mastery vừa replay — không phải màn tĩnh.
class KnowledgeStateScreen extends StatelessWidget {
  const KnowledgeStateScreen({
    super.key,
    required this.profile,
    required this.store,
    required this.curriculum,
  });

  final LearnerProfile profile;
  final LearnerStore store;
  final SliceCurriculum curriculum;

  Future<(ConceptMastery, AdaptiveDecision)> _load() async {
    final mastery =
        await masteryFromStore(store, profile.learnerId, curriculum);
    final decision = decide(
      conceptId: curriculum.conceptId,
      exerciseCase: 'denominator-non-divisible', // mục tiêu của Bài 6
      mastery: mastery,
      stage: curriculum.stage,
      catalogue: curriculum.catalogue,
      caseCatalogue: curriculum.cases,
    );
    return (mastery, decision);
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        backgroundColor: WalColors.surface,
        body: SafeArea(
          child: FutureBuilder<(ConceptMastery, AdaptiveDecision)>(
            future: _load(),
            builder: (context, snap) {
              final data = snap.data;
              if (data == null) return const SizedBox.shrink();
              final (mastery, decision) = data;
              return Padding(
                padding: const EdgeInsets.all(WalSpacing.lg),
                child: ListView(children: [
                  const Text('Sổ học của con đã ghi thêm ✓',
                      style: TextStyle(
                          fontSize: WalType.title,
                          fontWeight: FontWeight.w700,
                          color: WalColors.ink)),
                  const SizedBox(height: WalSpacing.md),
                  for (final sc in curriculum.cases)
                    _caseTile(sc.condition, mastery.cases[sc.id]),
                  const SizedBox(height: WalSpacing.md),
                  Container(
                    padding: const EdgeInsets.all(WalSpacing.lg),
                    decoration: BoxDecoration(
                      color: WalColors.surfaceLavender,
                      borderRadius:
                          BorderRadius.circular(WalSpacing.radiusCard),
                    ),
                    child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('Bước tiếp theo',
                              style: TextStyle(
                                  fontSize: WalType.secondary,
                                  fontWeight: FontWeight.w700,
                                  color: WalColors.inkSoft)),
                          const SizedBox(height: WalSpacing.sm),
                          Text(decision.reason,
                              style: const TextStyle(
                                  fontSize: WalType.body,
                                  color: WalColors.ink,
                                  height: 1.45)),
                        ]),
                  ),
                  const SizedBox(height: WalSpacing.lg),
                  SizedBox(
                    height: WalSpacing.minTouch + 8,
                    child: FilledButton(
                      style: FilledButton.styleFrom(
                          backgroundColor: WalColors.primary500,
                          shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(
                                  WalSpacing.radiusButton))),
                      onPressed: () =>
                          Navigator.of(context).popUntil((r) => r.isFirst),
                      child: const Text('Về Hôm nay',
                          style: TextStyle(fontSize: WalType.body)),
                    ),
                  ),
                ]),
              );
            },
          ),
        ),
      );

  /// Chữ trạng thái theo BẰNG CHỨNG — không %, UNKNOWN nói thẳng là chưa thử.
  Widget _caseTile(String name, CaseMastery? m) {
    final line = m == null || !m.hasEvidence
        ? 'chưa thử dạng này'
        : m.pMastery >= 0.85
            ? 'con tự làm được rồi'
            : 'đang luyện (${m.evidenceCount} lần có bằng chứng)';
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('· ', style: TextStyle(color: WalColors.inkSoft)),
        Expanded(
          child: Text('Dạng "$name": $line',
              style: const TextStyle(
                  fontSize: WalType.body, color: WalColors.ink, height: 1.4)),
        ),
      ]),
    );
  }
}
