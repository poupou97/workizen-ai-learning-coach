import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/curriculum/curriculum_edge.dart';
import 'package:learning_coach/core/curriculum/prerequisite_edges.dart';
import 'package:learning_coach/core/knowledge/provenance.dart';

void main() {
  test('cạnh sourceStated đầu tiên: citable AS DEPENDENCY — sách nói thẳng',
      () {
    final e = prerequisiteEdges.single;
    expect(e.kind, EdgeKind.prerequisite);
    expect(e.provenance.origin, KnowledgeOrigin.sourceStated);
    expect(e.citable, true); // được nói «sách nói con cần HHCN trước»
    expect(e.evidence, isNotEmpty); // cạnh nào cũng có trích dẫn chống lưng
    expect(e.provenance.pageStart, 54); // lần ngược được trang gốc
  });

  test('CÙNG cạnh đó nếu chỉ suy từ thứ tự (sourceSequence) → KHÔNG citable',
      () {
    final e = prerequisiteEdges.single;
    final downgraded = CurriculumEdge(
      from: e.from,
      to: e.to,
      kind: EdgeKind.prerequisite,
      provenance: const Provenance(
        origin: KnowledgeOrigin.sourceSequence,
        sourceId: '05-sgk-toan-5-tap-hai',
        extractionMethod: 'toc-parse',
        confidence: 0.9,
      ),
    );
    expect(downgraded.citable, false,
        reason: 'độ đúng và quyền trích dẫn là hai câu hỏi khác nhau');
  });
}
