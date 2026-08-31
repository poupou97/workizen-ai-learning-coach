import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/curriculum/curriculum_edge.dart';
import 'package:learning_coach/core/knowledge/provenance.dart';

void main() {
  // Đo được từ mục lục Toán 5 KNTT (PDF tr.5): Bài 5 tr.16, Bài 6 tr.20.
  final order = CurriculumEdge(
    from: 'toan5-bai5', to: 'toan5-bai6', kind: EdgeKind.sourceOrder,
    evidence: 'Mục lục: Bài 5 tr.16 · Bài 6 tr.20',
    provenance: const Provenance(
      origin: KnowledgeOrigin.sourceDerived, sourceId: 'kntt-toan5-t1',
      extractionMethod: 'toc-parse', confidence: 0.99, pageStart: 4),
  );

  final prereq = CurriculumEdge(
    from: 'quy-dong', to: 'add-unlike-fractions', kind: EdgeKind.prerequisite,
    evidence: 'suy từ việc Bài 6 dùng quy đồng ở bước đầu',
    provenance: const Provenance(
      origin: KnowledgeOrigin.llmInferred, sourceId: 'kntt-toan5-t1',
      extractionMethod: 'llm', confidence: 0.85),
  );

  test('⭐ THỨ TỰ trong mục lục trích dẫn được — sách tự xếp', () {
    expect(order.citable, isTrue);
  });

  test('⭐⭐ TIÊN QUYẾT do suy luận KHÔNG trích dẫn được, dù confidence cao', () {
    expect(prereq.provenance.confidence, greaterThan(0.8));
    expect(prereq.citable, isFalse,
        reason: '⭐ 0.85 là khá chắc, và vẫn KHÔNG được nói "sách nói thế". Độ '
            'đúng và quyền trích dẫn là hai câu hỏi khác nhau — trộn chúng là '
            'lúc Parent Coach bắt đầu bịa nguồn.');
  });

  test('⭐ hai cạnh khác LOẠI giữa cùng cặp nút là hợp lệ và cần thiết', () {
    expect(order.kind, isNot(prereq.kind));
    expect({order.kind, prereq.kind},
        containsAll([EdgeKind.sourceOrder, EdgeKind.prerequisite]),
        reason: 'sách xếp A trước B (fact) và ta cho rằng A cần cho B (suy luận) '
            'là HAI khẳng định — graph phải chứa được cả hai mà không nhập nhằng');
  });
}
