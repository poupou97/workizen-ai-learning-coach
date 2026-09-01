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
    expect(p(KnowledgeOrigin.sourceStated).citableAsTextbookFact, isTrue);

    expect(p(KnowledgeOrigin.llmInferred).citableAsTextbookFact, isFalse,
        reason: '⭐ prerequisite do LLM suy ra ("quy đồng cần BCNN") nghe rất '
            'hợp lý và SÁCH CÓ THỂ KHÔNG HỀ NÓI VẬY. Trình bày nó như trích dẫn '
            'là phá chính niềm tin khiến phụ huynh chọn ta.');

    expect(p(KnowledgeOrigin.systemDerived).citableAsTextbookFact, isFalse);
  });

  test('⭐ không có SỐ TRANG thì không phải trích dẫn được, dù đọc từ nguồn', () {
    expect(p(KnowledgeOrigin.sourceStated, page: null).citableAsTextbookFact,
        isFalse,
        reason: '"sách có nói" mà không chỉ được trang thì phụ huynh không kiểm '
            'chứng được — đó là khẳng định, không phải trích dẫn');
  });

  test('confidence ngoài [0,1] là lỗi lập trình, phải nổ', () {
    expect(
        () => Provenance(
            origin: KnowledgeOrigin.sourceStated,
            sourceId: 's',
            extractionMethod: 'm',
            confidence: 1.5),
        throwsA(isA<AssertionError>()));
  });

  test('⭐ ba nguồn gốc là VÉT CẠN — thêm loại mới phải quyết định trích dẫn được không',
      () {
    for (final o in KnowledgeOrigin.values) {
      final citable = switch (o) {
        KnowledgeOrigin.sourceStated => true,
        // ⭐ DẠY-QUA-VÍ-DỤ (B57): trang/ví dụ CÓ THẬT ⇒ trích được sự tồn tại
        // («SGK có ví dụ ở tr.62»), nhưng tầng phát ngôn phải render là
        // MINH HOẠ — không bao giờ thành «sách nói rằng» (Delta §2: loại hỗ
        // trợ là một phần của tính đúng trích dẫn).
        KnowledgeOrigin.sourceDemonstrated => true,
        // ⭐ Thứ tự trong mục lục LÀ sự thật trong sách — trích dẫn được như
        // thứ tự. Nó chỉ không được dùng để phát biểu PHỤ THUỘC.
        KnowledgeOrigin.sourceSequence => true,
        KnowledgeOrigin.systemDerived => false,
        KnowledgeOrigin.llmInferred => false,
      };
      expect(p(o).citableAsTextbookFact, citable);

      // Chỉ sách NÓI THẲNG mới được phát biểu quan hệ phụ thuộc.
      expect(p(o).citableAsDependency, o == KnowledgeOrigin.sourceStated);
    }
    expect(KnowledgeOrigin.values, hasLength(5),
        reason: '⭐ thêm một KnowledgeOrigin mà không sửa chốt này ⇒ switch vét '
            'cạn ở trên KHÔNG biên dịch được. Đó là điều mong muốn.');
  });
}
