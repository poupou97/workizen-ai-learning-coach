/// WAL-52 — nối flow demo: ConfirmProblemScreen → CanonicalProblem →
/// chuỗi DOMAIN THẬT (analyzeFractionPair → decide) → màn kết quả.
///
/// ⚠️ CAPTURE là STUB (hypothesis fixture) — camera thật + pre-capture
/// guidance thuộc WAL-65 + device work (WAL-84). Ranh giới an toàn (màn xác
/// nhận) là deliverable của ticket này và đã THẬT.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/adaptive/adaptive_engine.dart';
import '../../core/curriculum/canonical_problem.dart';
import '../../core/perception/perception_provenance.dart';
import '../../core/curriculum/pedagogical_boundary.dart';
import '../mission/mission_data.dart';
import '../tutor/tutor_screen.dart';
import '../tutor/tutor_session.dart';
import 'confirm_problem_screen.dart';

/// Parse "a/b ± c/d" → cặp mẫu số. Sai dạng ⇒ null (fail closed như mọi nơi).
(int, int)? parseFractionPair(String expr) {
  final m = RegExp(r'^\s*\d{1,3}\s*/\s*(\d{1,3})\s*[+\-−]\s*\d{1,3}\s*/\s*(\d{1,3})\s*$')
      .firstMatch(expr);
  if (m == null) return null;
  return (int.parse(m.group(1)!), int.parse(m.group(2)!));
}

/// Mở flow camera demo từ màn Hôm nay.
void openCameraDemo(BuildContext context) {
  final hypothesis = PerceptionHypothesis(
    hypothesisId: 'demo-h-${DateTime.now().millisecondsSinceEpoch}',
    rawImageRef: 'demo-img',
    expression: '3/4 + 2/5',
    pipelineVersion: 'demo-stub', // capture stub — WAL-65/84
    at: DateTime.now(),
  );
  Navigator.of(context).push(MaterialPageRoute(
    builder: (_) => ConfirmProblemScreen(
      hypothesis: hypothesis,
      onRetake: () => Navigator.of(context).pop(),
      onConfirmed: (problem) {
        Navigator.of(context).pushReplacement(MaterialPageRoute(
            builder: (_) => ProblemResultScreen(problem: problem)));
      },
    ),
  ));
}

/// Màn kết quả tối giản: bài đã xác nhận → ca → quyết định của engine.
class ProblemResultScreen extends StatelessWidget {
  const ProblemResultScreen({super.key, required this.problem});

  final CanonicalProblem problem;

  @override
  Widget build(BuildContext context) {
    final pair = parseFractionPair(problem.expression);
    final exerciseCase =
        pair == null ? null : fractionCase(pair.$1, pair.$2);
    final domain = buildDemoDomain();
    final decision = decide(
      conceptId: 'quy-dong',
      exerciseCase: exerciseCase,
      mastery: domain.mastery,
      stage: domain.stage,
      catalogue: domain.catalogue,
      caseCatalogue: domain.cases,
    );

    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(WalSpacing.lg),
          child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
            Text('Bài của con: ${problem.expression}',
                style: const TextStyle(
                    fontSize: WalType.title,
                    fontWeight: FontWeight.w700,
                    color: WalColors.ink)),
            const SizedBox(height: WalSpacing.md),
            Container(
              padding: const EdgeInsets.all(WalSpacing.lg),
              decoration: BoxDecoration(
                color: WalColors.surfaceLavender,
                borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
              ),
              // reason NGUYÊN VĂN của engine — cùng luật với màn Hôm nay.
              child: Text(decision.reason,
                  style: const TextStyle(
                      fontSize: WalType.body,
                      color: WalColors.ink,
                      height: 1.45)),
            ),
            const Spacer(),
            // Ca xác định được ⇒ vào làm bài (T1). Ca không xác định ⇒ KHÔNG
            // có nút làm bài với tutor — fail closed, chỉ còn đường quay về.
            if (exerciseCase != null && pair != null) ...[
              SizedBox(
                height: WalSpacing.minTouch + 8,
                child: FilledButton(
                  style: FilledButton.styleFrom(
                      backgroundColor: WalColors.primary500,
                      shape: RoundedRectangleBorder(
                          borderRadius:
                              BorderRadius.circular(WalSpacing.radiusButton))),
                  onPressed: () {
                    final fp = FractionProblem.parse(problem.expression)!;
                    final session = TutorSession(
                      exerciseId: problem.exerciseId,
                      skillCaseId: exerciseCase,
                      problem: fp,
                      scope: TutorScope.forProblem('quy-dong', exerciseCase,
                          domain.stage, domain.catalogue),
                    );
                    Navigator.of(context).push(MaterialPageRoute(
                        builder: (_) => TutorScreen(
                            session: session,
                            expression: problem.expression)));
                  },
                  child: const Text('Làm bài này ▸',
                      style: TextStyle(fontSize: WalType.body)),
                ),
              ),
              const SizedBox(height: WalSpacing.sm),
            ],
            SizedBox(
              height: WalSpacing.minTouch,
              child: TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('Về Hôm nay',
                    style: TextStyle(fontSize: WalType.body, color: WalColors.primaryText)),
              ),
            ),
          ]),
        ),
      ),
    );
  }
}
