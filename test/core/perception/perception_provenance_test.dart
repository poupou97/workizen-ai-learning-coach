/// ⭐⭐ WAL-64 — bất biến: perception chưa xác nhận KHÔNG vào evidence;
/// sửa của người KHÔNG ghi đè lịch sử máy.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/curriculum/exercise_skill_map.dart';
import 'package:learning_coach/core/knowledge/provenance.dart';
import 'package:learning_coach/core/perception/perception_provenance.dart';

void main() {
  final t = DateTime(2026, 9, 1, 9);
  final hyp = PerceptionHypothesis(
    hypothesisId: 'h-001',
    rawImageRef: 'img-sha256-abc',
    expression: '15/1 - 5/7', // đúng loại biểu thức bịa mà PHONE-SIM bắt được
    pipelineVersion: 'assemble-v1+consensus-3of6',
    at: t,
    consensusVotes: 3,
    viewCount: 6,
  );

  test('⭐⭐ sửa của trẻ tạo BẢN GHI MỚI — hypothesis máy còn nguyên vẹn', () {
    final confirmed = ConfirmedProblem.confirm(hyp,
        correctedExpression: '1/5 - 5/7', at: t.add(const Duration(seconds: 30)));
    expect(hyp.expression, '15/1 - 5/7',
        reason: '⭐⭐ không bao giờ ghi đè lịch sử máy bằng sửa của người — '
            'mất nó là mất luôn Student Correction Rate (#5) và mất khả năng '
            'audit pipeline nào đã bịa gì');
    expect(confirmed.expression, '1/5 - 5/7');
    expect(confirmed.kind, ConfirmationKind.corrected);
    expect(confirmed.hypothesisId, hyp.hypothesisId,
        reason: 'lineage: problem → hypothesis → ảnh gốc');
  });

  test('xác nhận nguyên văn ⇒ confirmedAsIs, biểu thức giữ nguyên', () {
    final c = ConfirmedProblem.confirm(hyp, at: t);
    expect(c.kind, ConfirmationKind.confirmedAsIs);
    expect(c.expression, hyp.expression);
  });

  test('⭐ exerciseId cho Q-matrix CHỈ tồn tại sau xác nhận — cổng nằm ở kiểu', () {
    final confirmed = ConfirmedProblem.confirm(hyp,
        correctedExpression: '1/5 - 5/7', at: t);
    final map = ExerciseSkillMap(
      exerciseId: confirmed.exerciseId,
      requirements: const [
        SkillRequirement(
            conceptId: 'quy-dong',
            skillCaseId: 'denominator-non-divisible',
            provenance: Provenance(
                origin: KnowledgeOrigin.systemDerived,
                sourceId: 'fraction-analyzer',
                extractionMethod: 'deterministic-parse',
                confidence: 1.0)),
      ],
    );
    expect(map.exerciseId, startsWith('cp:h-001@'),
        reason: '⭐ mọi evidence gốc-camera lần ngược được về ConfirmedProblem '
            '(và từ đó về hypothesis + ảnh). PerceptionHypothesis KHÔNG có '
            'exerciseId — compiler chặn đường tắt, không phải code review.');
  });

  test('hai lần xác nhận cùng hypothesis ⇒ hai problemId khác nhau', () {
    final a = ConfirmedProblem.confirm(hyp, at: t);
    final b = ConfirmedProblem.confirm(hyp, at: t.add(const Duration(minutes: 1)));
    expect(a.problemId, isNot(b.problemId),
        reason: 'cùng bài chụp lại/xác nhận lại là sự kiện mới — bài học '
            'eventId của replay audit §G áp luôn ở đây');
  });
}
