/// ⭐⭐ MỘT hành động tiếp theo, chọn theo NHỮNG GÌ PHIÊN ĐO ĐƯỢC.
///
/// Trước đây thẻ kết luôn đưa đúng `NextStep` của kịch bản: một đứa trẻ bỏ dở
/// một câu và một đứa trẻ làm trọn vẹn nhận CÙNG một lời mời. Đó là gợi ý giả,
/// dù chỉ có một cái.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/tutor_script.dart';
import 'package:learning_coach/features/lesson_workspace/tutor_view.dart';

AskStep _ask(String id, {String? block}) => AskStep(
  id: id,
  prompt: 'câu $id',
  promptBlockId: block,
  options: const ['A', 'B'],
  acceptable: const ['^b\$'],
  hints: const ['gợi ý 1'],
  feedbackMatched: 'khớp rồi',
  scaffold: 'sách gọi là B',
  keySource: 'B',
);

TutorScript _script() => TutorScript(
  steps: [
    _ask('q1', block: 'blk-1'),
    _ask('q2', block: 'blk-2'),
    const NextStep(id: 'n', label: 'Đọc lại phần «Em đã học»', target: NextTarget.read),
  ],
);

void main() {
  test('chưa trả lời câu nào ⇒ KHÔNG đổi (dùng NextStep của kịch bản)', () {
    final r = TutorRunner(_script());
    expect(TutorView.nextFromSession(r), isNull);
  });

  test('làm đúng hết ⇒ KHÔNG đổi — mời sang việc tiếp theo như kịch bản', () {
    final r = TutorRunner(_script());
    r.submit('B'); // q1 khớp
    r.submit('B'); // q2 khớp
    expect(TutorView.nextFromSession(r), isNull);
  });

  test('⭐ còn một câu đã thử mà CHƯA khớp ⇒ đưa về ĐÚNG chỗ sách của câu ấy', () {
    final r = TutorRunner(_script());
    r.submit('A'); // q1 sai, chưa khớp
    final n = TutorView.nextFromSession(r);
    expect(n, isNotNull);
    expect(n!.target, NextTarget.read);
    expect(n.anchor, 'blk-1', reason: 'phải trỏ về câu còn dở, không phải câu khác');
    expect(n.label, contains('Xem lại'));
  });

  test('câu dở ở GIỮA phiên vẫn được ưu tiên hơn việc mới', () {
    final r = TutorRunner(_script());
    r.submit('B'); // q1 khớp
    r.submit('A'); // q2 sai
    final n = TutorView.nextFromSession(r);
    expect(n, isNotNull);
    expect(n!.anchor, 'blk-2');
  });

  test('⭐ sai rồi SỬA ĐƯỢC ⇒ không kéo trẻ về nữa', () {
    final r = TutorRunner(_script());
    r.submit('A'); // sai
    r.submit('B'); // tự sửa
    r.submit('B'); // q2 khớp
    expect(TutorView.nextFromSession(r), isNull,
        reason: 'sửa được rồi mà vẫn mời «xem lại» thì phủ nhận nỗ lực của trẻ');
  });

  test('không có neo block ⇒ vẫn về màn Đọc, không rơi vào ngõ cụt', () {
    final r = TutorRunner(TutorScript(steps: [
      _ask('q1'),
      const NextStep(id: 'n', label: 'x', target: NextTarget.read),
    ]));
    r.submit('A');
    final n = TutorView.nextFromSession(r);
    expect(n, isNotNull);
    expect(n!.anchor, isNull);
    expect(n.target, NextTarget.read);
  });
}
