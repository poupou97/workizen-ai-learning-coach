/// ⭐⭐ ROUND 4 (A-runtime, Founder §5a) — SOURCE QUOTE INDEX: luật «câu SAM
/// trích có thật trong sách không» là TẤT ĐỊNH, chuẩn hoá tối thiểu, không
/// sửa nguồn, không nới trích-lược, ưu tiên block cùng mục.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/pedagogy/source_quote_index.dart';

const _sec = ['2. Cô cạn'];
const _other = ['I Một số cách tách chất', '1. Lắng, gạn và lọc'];

final _idx = SourceQuoteIndex(const [
  SourceQuoteBlock(
      id: 'b-loc',
      text: '· Lọc (tách chất rắn không tan ra khỏi chất lỏng).',
      headingPath: []),
  SourceQuoteBlock(
      id: 'b-cocan',
      text: 'Phương pháp cô cạn dùng để tách chất tan rắn ra khỏi dung dịch '
          'hoặc huyền phù bằng cách làm cho dung môi bay hơi, thu được chất '
          'rắn còn lại.',
      headingPath: _sec),
  // Cùng một câu xuất hiện ở hai mục — để kiểm ưu tiên cùng mục.
  SourceQuoteBlock(
      id: 'b-dup-other', text: 'Muối ăn không bay hơi.', headingPath: _other),
  SourceQuoteBlock(
      id: 'b-dup-sec', text: 'Muối ăn không bay hơi.', headingPath: _sec),
  // OCR của nguồn có lỗi («khoa» thay vì «khoá») — chỉ mục KHÔNG sửa hộ.
  SourceQuoteBlock(
      id: 'b-ocr',
      text: 'Khi phần dầu ăn chạm vào bề mặt khóa thì vặn khoa lại.',
      headingPath: _other),
  SourceQuoteBlock(id: 'b-empty', text: '   ', headingPath: []),
]);

void main() {
  test('block rỗng bị bỏ; đếm đúng', () {
    expect(_idx.blockCount, 5);
    expect(_idx.headingPathOf('b-cocan'), _sec);
    expect(_idx.headingPathOf('không-có'), isEmpty);
  });

  test('⭐⭐ trích NGUYÊN VĂN (chuẩn hoá hoa/thường, khoảng trắng, dấu câu '
      'đầu-cuối) ⇒ tìm thấy, ghi đúng block', () {
    final v = _idx.verify(
        'Sách viết: lọc «tách chất rắn không tan ra khỏi chất lỏng». Ghép lại xem.');
    expect(v.isSourced, isTrue, reason: v.refusals.join(','));
    expect(v.sourceBlockId, 'b-loc');
    expect(_idx.lookup('  TÁCH chất   rắn không tan ra khỏi chất lỏng. ').blockId,
        'b-loc');
  });

  test('⭐⭐ thiếu một từ so với sách («các») ⇒ QUOTE_NOT_IN_SOURCE — không '
      'paraphrase-check', () {
    final v = _idx.verify('cô cạn «tách chất khó bay hơi ra khỏi chất dễ bay hơi»');
    expect(v.isSourced, isFalse);
    expect(v.refusals,
        ['QUOTE_NOT_IN_SOURCE:tách chất khó bay hơi ra khỏi chất dễ bay hơi']);
    expect(v.sourceBlockId, isNull);
  });

  test('⭐ trích LƯỢC («…» / «...») không phải nguyên văn ⇒ QUOTE_ELIDED', () {
    final v = _idx.verify(
        'mục «tách chất tan rắn ra khỏi dung dịch… bằng cách làm cho dung môi bay hơi»');
    expect(v.refusals.single, startsWith('QUOTE_ELIDED:'));
    expect(_idx.lookup('a ... b').refusal, startsWith('QUOTE_ELIDED:'));
  });

  test('⭐ lỗi OCR của NGUỒN không được sửa hộ: trích «khoá» đúng chính tả '
      'không khớp nguồn viết «khoa» ⇒ không thấy (việc của A-pipeline)', () {
    final v = _idx.verify(
        'Sách dặn: «Khi phần dầu ăn chạm vào bề mặt khoá thì vặn khoá lại»');
    expect(v.isSourced, isFalse);
    expect(v.refusals.single, startsWith('QUOTE_NOT_IN_SOURCE:'));
    // Nguyên văn theo nguồn (kể cả lỗi) thì thấy.
    expect(
        _idx.lookup('Khi phần dầu ăn chạm vào bề mặt khóa thì vặn khoa lại').blockId,
        'b-ocr');
  });

  test('không có «…» nào ⇒ HINT_UNSOURCED (máy không chứng minh được)', () {
    final v = _idx.verify('Con nghĩ xem: muối ăn không bay hơi, còn nước thì bay hơi.');
    expect(v.hasQuotes, isFalse);
    expect(v.isSourced, isFalse);
    expect(v.refusals, ['HINT_UNSOURCED']);
    expect(identical(v, QuoteVerification.noQuotes), isTrue);
  });

  test('hai trích: một thấy, một không ⇒ KHÔNG có nguồn, nhưng block của '
      'đoạn thấy vẫn ghi (UI hiện «Sách viết» cho phần thật)', () {
    final v = _idx.verify(
        'lọc «tách chất rắn không tan ra khỏi chất lỏng», cô cạn «tách chất khó bay hơi ra khỏi chất dễ bay hơi»');
    expect(v.lookups.length, 2);
    expect(v.isSourced, isFalse);
    expect(v.sourceBlockId, 'b-loc');
    expect(v.refusals.length, 1);
  });

  test('⭐ ưu tiên block CÙNG MỤC với câu hỏi; không có mục ⇒ theo thứ tự đọc',
      () {
    expect(_idx.lookup('Muối ăn không bay hơi').blockId, 'b-dup-other',
        reason: 'không ưu tiên ⇒ block đầu tiên theo thứ tự đọc');
    expect(_idx.lookup('Muối ăn không bay hơi', preferHeadingPath: _sec).blockId,
        'b-dup-sec');
    expect(
        _idx
            .lookup('Muối ăn không bay hơi',
                preferHeadingPath: const ['2. Cô cạn', '3. Chiết'])
            .blockId,
        'b-dup-sec',
        reason: 'mục con của «2. Cô cạn» vẫn là cùng mục (tiền tố)');
    expect(
        _idx.lookup('Muối ăn không bay hơi', preferHeadingPath: const ['X']).blockId,
        'b-dup-other',
        reason: 'mục lạ ⇒ rơi về thứ tự đọc, không bịa');
  });

  test('trích rỗng «» hoặc chỉ dấu câu ⇒ không thấy, không nổ', () {
    expect(_idx.lookup(' . ').refusal, startsWith('QUOTE_NOT_IN_SOURCE:'));
    expect(_idx.verify('câu có «» rỗng').hasQuotes, isFalse,
        reason: 'regex «([^«»]+)» không bắt cặp ngoặc rỗng');
  });
}
