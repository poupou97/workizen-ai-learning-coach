/// Mẩu trích trọn nghĩa — «một nửa câu về lịch sử là một câu SAI về lịch sử».
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/stories/snippet_integrity.dart';

void main() {
  _fieldMismatchTests();
  group('cụt ĐUÔI', () {
    test('ca thật trên máy: dừng giữa một cái tên', () {
      // «Cô-lôm-bô tìm ra châu Mỹ (1492 - 1502), cuộc thám hiểm của Ph.»
      // Dấu chấm ấy là chấm VIẾT TẮT, không phải chấm hết câu.
      expect(isCompleteSnippet(
          'Cô-lôm-bô tìm ra châu Mỹ (1492 - 1502), cuộc thám hiểm của Ph.'),
          isFalse);
    });

    test('dừng giữa câu, không có dấu kết', () {
      expect(isCompleteSnippet(
          'Chương VI: Lắc-ki thực sự may mắn bắt đầu kể về hành trình Gióc-ba thực hi'),
          isFalse);
    });

    test('dừng giữa một chữ', () {
      expect(isCompleteSnippet('Ông là phi công và từng tham gia chiến đ'), isFalse);
    });
  });

  group('cụt ĐẦU', () {
    test('bắt đầu bằng chữ thường', () {
      expect(isCompleteSnippet(
          'năm 1088, Trường Đại học Bô-lô-na là trường đại học lâu đời nhất.'),
          isFalse);
    });

    test('bắt đầu bằng dấu câu', () {
      expect(isCompleteSnippet('- Thường thức âm nhạc: nêu được đôi nét.'), isFalse);
      expect(isCompleteSnippet(') Giai đoạn mở rộng hoạt động.'), isFalse);
    });
  });

  group('trọn nghĩa', () {
    test('một câu đầy đủ được nhận', () {
      expect(isCompleteSnippet(
          'Năm 1941, Tô Hoài xuất bản truyện Con Dế Mèn; sau đó tác giả viết '
          'thêm Dế Mèn phiêu lưu kí.'),
          isTrue);
    });

    test('kết bằng dấu hỏi / chấm than / ngoặc kép cũng là kết', () {
      for (final t in ['Vì sao nước biển mặn?', 'Thật kì diệu!',
                       'Ông nói: "Tôi sẽ trở lại."']) {
        expect(isCompleteSnippet(t), isTrue, reason: t);
      }
    });

    test('tên viết tắt GIỮA câu không bị nhầm là cụt', () {
      // Chỉ chữ viết tắt Ở CUỐI mới là dấu hiệu cắt dở.
      expect(isCompleteSnippet(
          'Ph. Ma-gien-lăng là người đầu tiên đi vòng quanh thế giới.'),
          isTrue);
    });

    test('rỗng / null ⇒ không trọn', () {
      expect(isCompleteSnippet(null), isFalse);
      expect(isCompleteSnippet('   '), isFalse);
    });
  });
}

/// ⭐ THẺ PHẢI LỌC ĐÚNG TRƯỜNG NÓ HIỂN THỊ.
///
/// Bản sửa đầu lọc `body` trong khi thẻ hiện `title` — nên máy thật VẪN ra một
/// mẩu cụt. Đo trên kho: chỉ 4/38 `title` trọn nghĩa, so với 17/38 `body`.
void _fieldMismatchTests() {
  test('title là chỗ hay cụt nhất — không được lọc nhầm trường', () {
    // Chính hai ca thật lấy từ kho.
    const titleCut = 'châu Mỹ (1492 - 1502), cuộc thám hiểm của Ph.';
    const bodyWhole = 'Năm 1941, Tô Hoài xuất bản truyện Con Dế Mèn; sau đó '
        'tác giả viết thêm Dế Mèn phiêu lưu kí.';
    expect(isCompleteSnippet(titleCut), isFalse);
    expect(isCompleteSnippet(bodyWhole), isTrue);
  });

  test('«Năm 1941» — một nhãn, không phải một sự thật', () {
    expect(isCompleteSnippet('Năm 1941'), isFalse);
  });
}
