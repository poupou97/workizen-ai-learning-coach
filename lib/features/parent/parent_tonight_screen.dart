/// WAL-53 — Parent «Tối nay»: trả lời "tối nay tôi giúp con cái gì?" trong
/// vài giây.
///
/// Luật giữ bằng widget test:
/// - MỌI câu về trạng thái của con đi qua `explainConcept` (claim-gated) —
///   UI không tự suy diễn, không tự khen, không tự chê.
/// - Đúng MỘT khuyến nghị hành động. Không danh sách việc, không dashboard.
/// - KHÔNG mascot ở vùng claim (luật Hub — mascot là bạn của TRẺ, không phải
///   người phát ngôn số liệu với phụ huynh).
/// - Không %, không điểm, không so sánh với "các bạn".
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/adaptive/adaptive_engine.dart';
import '../../core/coach/parent_explanation.dart';
import '../../core/student/concept_summary.dart';
import '../mission/mission_data.dart';

class ParentTonightScreen extends StatelessWidget {
  const ParentTonightScreen({
    super.key,
    required this.childName,
    required this.explanation,
    required this.decision,
    required this.caseDisplayNames,
  });

  final String childName;

  /// Tầng phát ngôn claim-gated (F4/ADR-005) — nguồn DUY NHẤT của mọi câu
  /// nói về trạng thái kiến thức của con.
  final ParentExplanation explanation;

  /// Khuyến nghị của engine — `reason` hiển thị NGUYÊN VĂN.
  final AdaptiveDecision decision;
  final Map<String, String> caseDisplayNames;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(WalSpacing.lg),
          children: [
            Text('Tối nay cùng $childName',
                style: const TextStyle(
                    fontSize: WalType.display,
                    fontWeight: FontWeight.w700,
                    color: WalColors.ink)),
            const SizedBox(height: WalSpacing.lg),

            // ── MỘT khuyến nghị — 10 phút, việc cụ thể ──────────────────
            Container(
              padding: const EdgeInsets.all(WalSpacing.lg),
              decoration: BoxDecoration(
                color: WalColors.primary500,
                borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('VIỆC CHO TỐI NAY · ~10 PHÚT',
                      style: TextStyle(
                          fontSize: WalType.secondary,
                          fontWeight: FontWeight.w700,
                          letterSpacing: 1.1,
                          color: Colors.white70)),
                  const SizedBox(height: WalSpacing.sm),
                  Text(_actionLine(),
                      style: const TextStyle(
                          fontSize: WalType.title,
                          fontWeight: FontWeight.w700,
                          color: Colors.white,
                          height: 1.3)),
                  const SizedBox(height: WalSpacing.sm),
                  // lý do của ENGINE, nguyên văn — cùng câu trẻ thấy ở màn
                  // Hôm nay. Phụ huynh và con nhìn CÙNG một sự thật.
                  Text(decision.reason,
                      style: const TextStyle(
                          fontSize: WalType.secondary,
                          color: Colors.white,
                          height: 1.45)),
                ],
              ),
            ),
            const SizedBox(height: WalSpacing.lg),

            // ── trạng thái 5 giây — claim-gated, KHÔNG mascot ───────────
            Text('SAM ghi nhận được gì',
                style: const TextStyle(
                    fontSize: WalType.body,
                    fontWeight: FontWeight.w700,
                    color: WalColors.ink)),
            const SizedBox(height: WalSpacing.sm),
            Container(
              padding: const EdgeInsets.all(WalSpacing.lg),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(explanation.message,
                      style: const TextStyle(
                          fontSize: WalType.body,
                          color: WalColors.ink,
                          height: 1.5)),
                  if (explanation.citations.isNotEmpty) ...[
                    const SizedBox(height: WalSpacing.md),
                    const Divider(height: 1),
                    const SizedBox(height: WalSpacing.sm),
                    for (final c in explanation.citations)
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 3),
                        child: Text(
                            '• ${caseDisplayNames[c.skillCaseId] ?? c.skillCaseId}'
                            ' — ${c.observation}',
                            style: const TextStyle(
                                fontSize: WalType.secondary,
                                color: WalColors.inkSoft,
                                height: 1.4)),
                      ),
                  ],
                ],
              ),
            ),
            const SizedBox(height: WalSpacing.md),
            const Text(
                'SAM chỉ nói điều có bằng chứng. «Chưa kiểm» nghĩa là chưa '
                'kiểm — không phải con chưa biết.',
                style: TextStyle(
                    fontSize: WalType.secondary,
                    color: WalColors.inkSoft,
                    height: 1.4)),
          ],
        ),
      ),
    );
  }

  /// Tiêu đề hành động: template cố định + tên dạng bài từ ENGINE — không
  /// chứa phán xét nào về trạng thái của con (phần đó là của explainConcept).
  String _actionLine() {
    final target = decision.scope.allowedMethods.isEmpty
        ? null
        : decision.scope.allowedMethods.first.skillCaseId;
    final caseName = target == null ? null : caseDisplayNames[target] ?? target;
    return caseName == null
        ? 'Cùng con mở SAM và làm nhiệm vụ hôm nay.'
        : 'Cùng con làm 1–2 bài dạng «$caseName».';
  }
}

/// Fixture demo — cùng DemoDomain với màn Hôm nay: hai màn nhìn CÙNG dữ liệu.
ParentTonightScreen buildDemoParentTonight({DateTime? now}) {
  final t = now ?? DateTime(2026, 9, 1, 19);
  const names = {
    'denominator-divisible': 'một mẫu số chia hết cho mẫu kia',
    'denominator-non-divisible': 'hai mẫu số không chia hết cho nhau',
    'denominator-equal': 'hai mẫu số bằng nhau',
  };
  final domain = buildDemoDomain(now: t);
  final summary = ConceptSummary.of(domain.mastery,
      knownCaseIds: {for (final c in domain.cases) c.id}, now: t);
  final decision = decide(
    conceptId: 'quy-dong',
    exerciseCase: 'denominator-non-divisible',
    mastery: domain.mastery,
    stage: domain.stage,
    catalogue: domain.catalogue,
    caseCatalogue: domain.cases,
  );
  return ParentTonightScreen(
    childName: 'Minh',
    explanation: explainConcept(summary,
        conceptDisplayName: 'quy đồng mẫu số', caseDisplayNames: names),
    decision: decision,
    caseDisplayNames: names,
  );
}
