/// WAL-173 — mã môn suy từ TÊN, không tra bảng cứng theo tên môn.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/curriculum/subject_id.dart';

void main() {
  test('⭐ bỏ dấu đúng, đ→d, nối bằng gạch', () {
    expect(subjectIdOf('Vật lí'), 'vat-li');
    expect(subjectIdOf('Hoá học'), 'hoa-hoc');
    expect(subjectIdOf('Khoa học'), 'khoa-hoc');
    expect(subjectIdOf('Toán'), 'toan');
    expect(subjectIdOf('Tiếng Việt'), 'tieng-viet');
    expect(subjectIdOf('Đạo đức'), 'dao-duc',
        reason: '⭐ đ KHÔNG phải d có dấu — bỏ dấu kiểu nào cũng không ra d');
    expect(subjectIdOf('Lịch sử và Địa lí'), 'lich-su-va-dia-li');
  });

  test('⭐⭐ môn CHƯA TỪNG BIẾT vẫn ra mã riêng, không dồn về khoa-hoc', () {
    expect(subjectIdOf('Sinh học'), 'sinh-hoc',
        reason: '⭐⭐ đột biến quay lại switch theo tên ⇒ rơi về khoa-hoc ⇒ '
            'bằng chứng của trẻ bị ghi SAI MÔN');
    expect(subjectIdOf('Địa lí'), 'dia-li');
    expect(subjectIdOf('Giáo dục thể chất'), 'giao-duc-the-chat');
  });

  test('không sinh gạch thừa ở hai đầu hay giữa', () {
    expect(subjectIdOf('  Âm  nhạc  '), 'am-nhac');
    expect(subjectIdOf('GDKT&PL'), 'gdkt-pl');
  });
}
