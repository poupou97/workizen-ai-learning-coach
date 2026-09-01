/// ⭐ WAL-72 — 5 nguồn bài toán, mỗi nguồn đúng luật provenance của nó.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/curriculum/canonical_problem.dart';
import 'package:learning_coach/core/knowledge/provenance.dart';
import 'package:learning_coach/core/perception/perception_provenance.dart';

void main() {
  final t = DateTime(2026, 9, 1, 10);

  test('curriculum: mint thẳng từ Provenance sách — KHÔNG xác nhận giả', () {
    final p = CanonicalProblem.fromCurriculum(
      exerciseLabel: 'bai6-hd1a',
      expression: '3/5 + 1/2',
      provenance: const Provenance(
          origin: KnowledgeOrigin.sourceStated,
          sourceId: 'toan5-t1-kntt',
          extractionMethod: 'manual',
          confidence: 1.0,
          pageStart: 20),
    );
    expect(p.exerciseId, 'cur:toan5-t1-kntt:p20:bai6-hd1a');
    expect(p.origin, ProblemOrigin.curriculumExercise);
    expect(p.confirmedProblemId, isNull,
        reason: '⭐ falsification §1: bài sách không bị ép qua confirmation — '
            'không overfit camera');
  });

  test('⭐ camera: chữ ký ĐÒI ConfirmedProblem — vá under-enforcement', () {
    final hyp = PerceptionHypothesis(
        hypothesisId: 'h-9', rawImageRef: 'sha-x', expression: '1/2 - 1/5',
        pipelineVersion: 'v1', at: t);
    final confirmed = ConfirmedProblem.confirm(hyp, at: t);
    final p = CanonicalProblem.fromConfirmedPerception(confirmed);
    expect(p.exerciseId, startsWith('cp:h-9@'),
        reason: 'giữ nguyên lineage về hypothesis + ảnh');
    expect(p.confirmedProblemId, confirmed.problemId);
    // Không tồn tại CanonicalProblem.fromPerceptionHypothesis — compiler chặn.
  });

  test('manual / imported / generated: mỗi nguồn một prefix + provenance riêng',
      () {
    final man = CanonicalProblem.fromManualInput(expression: '2/3 + 1/6', at: t);
    final imp = CanonicalProblem.fromImportedWorksheet(
        importRef: 'ws-cothuy-2026w1', exerciseLabel: 'b3', expression: '7/8 - 1/4');
    final gen = CanonicalProblem.fromGeneratedPractice(
        generatorId: 'frac-gen-v1', expression: '5/6 + 1/3', at: t);
    expect(man.exerciseId, startsWith('man:'));
    expect(imp.exerciseId, 'imp:ws-cothuy-2026w1:b3');
    expect(gen.exerciseId, startsWith('gen:frac-gen-v1:'));
    expect(gen.generatorId, 'frac-gen-v1',
        reason: 'audit được AI sinh bài bằng generator nào — cùng doctrine '
            'provenance, áp cho cả bài do hệ tự sinh');
  });

  test('⭐ mọi origin lần ngược được loại nguồn từ CHÍNH exerciseId (§8E)', () {
    for (final (id, prefix) in [
      (CanonicalProblem.fromManualInput(expression: 'x', at: t).exerciseId, 'man:'),
      (CanonicalProblem.fromGeneratedPractice(
              generatorId: 'g', expression: 'x', at: t).exerciseId, 'gen:'),
    ]) {
      expect(id, startsWith(prefix));
    }
  });
}
