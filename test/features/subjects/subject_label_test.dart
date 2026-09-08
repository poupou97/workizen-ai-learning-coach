/// ⭐ TÊN MÔN TRẺ ĐỌC ĐƯỢC — chữ tắt của registry lọt thẳng ra màn.
///
/// Máy thật lớp 11: Home ghi «HĐTN-HN», giá sách ghi «GDKT&PL». Tám chữ tắt
/// trong corpus, mỗi chữ được xác minh chéo bằng định danh sách của chính môn
/// ấy (52/52 cuốn xác nhận) — nên dịch là TRA BẢNG, không phải đoán.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/features/subjects/subject_display.dart';

void main() {
  test('⭐ tám chữ tắt có thật trong corpus đều đọc được', () {
    expect(subjectLabel('GDCD'), 'Giáo dục công dân');
    expect(subjectLabel('GDKT&PL'), 'Giáo dục kinh tế và pháp luật');
    expect(subjectLabel('GDTC'), 'Giáo dục thể chất');
    expect(subjectLabel('HĐTN'), 'Hoạt động trải nghiệm');
    expect(subjectLabel('HĐTN-HN'), 'Hoạt động trải nghiệm, hướng nghiệp');
    expect(subjectLabel('KHTN'), 'Khoa học tự nhiên');
    expect(subjectLabel('LS&ĐL'), 'Lịch sử và Địa lí');
    expect(subjectLabel('TN&XH'), 'Tự nhiên và Xã hội');
  });

  test('HĐTN và HĐTN-HN là HAI môn khác nhau, không được gộp', () {
    expect(subjectLabel('HĐTN') == subjectLabel('HĐTN-HN'), isFalse);
  });

  test('tên đã đọc được thì giữ NGUYÊN VĂN', () {
    for (final s in ['Toán', 'Ngữ văn', 'Vật lí', 'Âm nhạc', 'Chuyên đề']) {
      expect(subjectLabel(s), s);
    }
  });

  test('⭐ chữ tắt LẠ ⇒ giữ nguyên, KHÔNG đoán', () {
    // «Thiếu tên» còn sửa được; một cái tên bịa thì trẻ tin nhầm.
    expect(subjectLabel('XYZ&QQ'), 'XYZ&QQ');
  });
}
