/// WAL-108×110 — Education OCR Adapter: extractor fail-closed + contract.
///
/// Bất biến: adapter chỉ sản xuất HYPOTHESIS; không chắc ⇒ null, không đoán.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/features/camera/education_ocr_adapter.dart';

void main() {
  group('extractFractionExpression — fail closed', () {
    test('một biểu thức giữa nhiễu OCR ⇒ chuẩn hoá đúng', () {
      expect(
        extractFractionExpression(
            ['Bài 3. Tính:', 'a) 3/4 + 2/5 =', 'Trang 22']),
        '3/4 + 2/5',
      );
    });

    test('dấu trừ unicode «−» được chuẩn về «-»', () {
      expect(extractFractionExpression(['1/2 − 1/5']), '1/2 - 1/5');
    });

    test('không có biểu thức ⇒ null (không đoán)', () {
      expect(extractFractionExpression(['Em hãy quan sát hình vẽ']), isNull);
    });

    test('HAI biểu thức khác nhau trong khung ⇒ null — không tự chọn hộ', () {
      expect(
        extractFractionExpression(['a) 3/4 + 2/5', 'b) 1/2 + 1/3']),
        isNull,
      );
    });

    test('cùng một biểu thức lặp lại ⇒ vẫn đọc được', () {
      expect(
        extractFractionExpression(['3/4 + 2/5', '3/4+2/5']),
        '3/4 + 2/5',
      );
    });
  });

  group('FakeEducationOcrAdapter — contract', () {
    test('đọc được ⇒ hypothesis đủ lineage, rawImageRef không lộ đường dẫn',
        () async {
      final a = FakeEducationOcrAdapter(['3/4 + 2/5'],
          now: () => DateTime(2026, 9, 2, 12));
      final h = await a.recognizeExpression('/data/user/0/app/cache/x.jpg');
      expect(h, isNotNull);
      expect(h!.expression, '3/4 + 2/5');
      expect(h.pipelineVersion, a.pipelineVersion);
      expect(h.rawImageRef.contains('/'), isFalse,
          reason: 'ảnh trẻ em: tham chiếu là TÊN, không phải đường dẫn máy');
    });

    test('không đọc được ⇒ null — ADMIT_UNCERTAINTY là câu trả lời hợp lệ',
        () async {
      final a = FakeEducationOcrAdapter(['toàn chữ, không có phân số']);
      expect(await a.recognizeExpression('x.jpg'), isNull);
    });
  });
}
