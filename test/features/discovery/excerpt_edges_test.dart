/// Mảnh trích chưa trọn câu phải TRÔNG RA chỗ cắt — nhãn phía trên hứa
/// «TRÍCH NGUYÊN VĂN TỪ NGUỒN», nên văn vỡ không được đi qua như văn trọn.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/features/discovery/story_detail_screen.dart';

void main() {
  test('câu trọn vẹn ⇒ KHÔNG thêm gì', () {
    expect(
      markExcerptEdges('Thạch Lam sinh ở Hà Nội.'),
      'Thạch Lam sinh ở Hà Nội.',
    );
  });

  test('mở giữa câu ⇒ dấu … ở đầu', () {
    expect(
      markExcerptEdges('nhà văn của những phận người nhỏ bé.'),
      '… nhà văn của những phận người nhỏ bé.',
    );
  });

  test('đóng giữa câu ⇒ dấu … ở cuối', () {
    expect(
      markExcerptEdges('Ông sinh năm 1910 và bắt đầu viết'),
      'Ông sinh năm 1910 và bắt đầu viết …',
    );
  });

  test('cụt cả hai đầu ⇒ dấu … cả hai phía', () {
    expect(markExcerptEdges('và bắt đầu viết'), '… và bắt đầu viết …');
  });

  test('⭐ KHÔNG sửa chữ — chỉ thêm dấu ở mép', () {
    const body = 'ương pháp nhuộm Gram';
    expect(markExcerptEdges(body), contains(body));
  });

  test('mở bằng ngoặc kép hoặc số vẫn là đầu câu', () {
    expect(
      markExcerptEdges('«Dân ta phải biết sử ta.»'),
      '«Dân ta phải biết sử ta.»',
    );
    expect(markExcerptEdges('1945 là năm bản lề.'), '1945 là năm bản lề.');
  });

  test('rỗng thì không nổ', () => expect(markExcerptEdges('  '), ''));
}
