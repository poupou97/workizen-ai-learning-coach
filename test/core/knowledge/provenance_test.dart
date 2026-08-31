/// ⭐ §6 — suy luận của LLM KHÔNG được đội lốt sự thật trong sách.
///
/// Đây là chốt quan trọng nhất của cả hệ tri thức. Nếu nó hỏng, Parent Coach sẽ
/// nói với phụ huynh "sách viết thế" về một điều sách không hề viết — và phụ
/// huynh tin ta CHÍNH VÌ ta bám sách.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/knowledge/provenance.dart';

void main() {
  Provenance p(KnowledgeOrigin o, {int? page = 11}) => Provenance(
        origin: o,
        sourceId: 'kntt-toan5-t1',
        extractionMethod: 'vision-ocr',
        confidence: 0.9,
        pageStart: page,
      );

  test('⭐ CHỈ tri thức đọc từ nguồn mới được trích dẫn như sách viết', () {
    expect(p(KnowledgeOrigin.sourceDerived).citableAsTextbookFact, isTrue);

    expect(p(KnowledgeOrigin.llmInferred).citableAsTextbookFact, isFalse,
        reason: '⭐ prerequisite do LLM suy ra ("quy đồng cần BCNN") nghe rất '
            'hợp lý và SÁCH CÓ THỂ KHÔNG HỀ NÓI VẬY. Trình bày nó như trích dẫn '
            'là phá chính niềm tin khiến phụ huynh chọn ta.');

    expect(p(KnowledgeOrigin.systemGenerated).citableAsTextbookFact, isFalse);
  });

  test('⭐ không có SỐ TRANG thì không phải trích dẫn được, dù đọc từ nguồn', () {
    expect(p(KnowledgeOrigin.sourceDerived, page: null).citableAsTextbookFact,
        isFalse,
        reason: '"sách có nói" mà không chỉ được trang thì phụ huynh không kiểm '
            'chứng được — đó là khẳng định, không phải trích dẫn');
  });

  test('confidence ngoài [0,1] là lỗi lập trình, phải nổ', () {
    expect(
        () => Provenance(
            origin: KnowledgeOrigin.sourceDerived,
            sourceId: 's',
            extractionMethod: 'm',
            confidence: 1.5),
        throwsA(isA<AssertionError>()));
  });

  test('⭐ ba nguồn gốc là VÉT CẠN — thêm loại mới phải quyết định trích dẫn được không',
      () {
    for (final o in KnowledgeOrigin.values) {
      final citable = switch (o) {
        KnowledgeOrigin.sourceDerived => true,
        KnowledgeOrigin.llmInferred => false,
        KnowledgeOrigin.systemGenerated => false,
      };
      expect(p(o).citableAsTextbookFact, citable);
    }
    expect(KnowledgeOrigin.values, hasLength(3),
        reason: '⭐ thêm một KnowledgeOrigin mà không sửa chốt này ⇒ switch vét '
            'cạn ở trên KHÔNG biên dịch được. Đó là điều mong muốn.');
  });
}
