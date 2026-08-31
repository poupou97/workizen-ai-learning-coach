/// ⭐⭐ ADR-001 — mastery theo SkillCase làm `caseTransitionGap` SUY RA ĐƯỢC.
///
/// Trước ADR này, `caseTransitionGap` tồn tại như một tên gọi trong enum mà mô hình
/// trạng thái không thể sinh bằng chứng để kết luận. Đây là chốt chứng minh nó đã có
/// thật.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/student/mastery.dart';

void main() {
  const div = 'denominator-divisible';
  const nonDiv = 'denominator-non-divisible';
  const p = BktParams.freeResponse;

  CaseMastery drill(String id, List<bool> answers, [BktParams par = p]) {
    var c = CaseMastery.initial(id, par);
    for (final a in answers) {
      c = c.observe(a, par);
    }
    return c;
  }

  test('BKT: đúng liên tiếp đẩy mastery lên, sai kéo xuống', () {
    final up = drill(div, [true, true, true, true, true]);
    final down = drill(div, [false, false, false]);
    expect(up.pMastery, greaterThan(p.prior));
    expect(down.pMastery, lessThan(p.prior));
    expect(up.pMastery, greaterThan(down.pMastery));
  });

  test('⭐ ca CHƯA GẶP là chưa biết, KHÔNG phải bằng 0', () {
    final fresh = CaseMastery.initial(nonDiv, p);
    expect(fresh.hasEvidence, isFalse);
    final m = ConceptMastery(conceptId: 'quy-dong', cases: {nonDiv: fresh});
    expect(m.derived, isNull,
        reason: '⭐ nếu ca chưa gặp bị tính là 0 thì MỌI học sinh mới đều trông '
            'như đang hỏng mọi thứ — và Parent Coach sẽ báo động ngay ngày đầu');
    expect(m.stateAt(), MasteryState.unknown);
  });

  test('⭐⭐ vững ca A + yếu ca B ⇒ nhìn ra ĐƯỢC, và concept KHÔNG bị coi là thành thạo',
      () {
    final m = ConceptMastery(conceptId: 'quy-dong', cases: {
      div: drill(div, [true, true, true, true, true, true]),
      nonDiv: drill(nonDiv, [false, false]),
    });
    final b = m.caseBreakdown();
    expect(b.strong, contains(div));
    expect(b.weak, contains(nonDiv));
    expect(m.stateAt(), isNot(MasteryState.mastered),
        reason: '⭐ một ca hỏng thì khái niệm chưa thành thạo — dù ca kia rất vững');

    // Đây chính là bằng chứng của caseTransitionGap.
    expect(b.strong.isNotEmpty && (b.weak.isNotEmpty || b.unseen.isNotEmpty), isTrue,
        reason: '⭐⭐ vững ít nhất một ca VÀ yếu/chưa gặp ít nhất một ca — trước '
            'ADR-001 mô hình KHÔNG thể phát biểu điều này, vì chỉ có MỘT con số '
            'mastery cho cả khái niệm');
  });

  test('⭐ min chứ không phải mean — mean GIẤU ca hỏng', () {
    final strong = drill(div, [true, true, true, true, true, true, true]);
    final broken = drill(nonDiv, [false, false, false, false]);
    final m = ConceptMastery(
        conceptId: 'quy-dong', cases: {div: strong, nonDiv: broken});
    final mean = (strong.pMastery + broken.pMastery) / 2;
    expect(m.derived, broken.pMastery);
    expect(m.derived!, lessThan(mean),
        reason: '⭐ mean sẽ để một ca vững kéo ca hỏng lên và che nó đi — đúng thứ '
            'ta đang cố phát hiện. (min là GIẢ THUYẾT của ADR-001, chưa có dữ liệu '
            'thực nghiệm chọn nó.)');
  });

  test('⭐ guess phải theo DẠNG BÀI — trắc nghiệm 4 lựa chọn học chậm hơn', () {
    final free = drill(div, [true, true, true], BktParams.freeResponse);
    final mcq = drill(div, [true, true, true], BktParams.multipleChoice4);
    expect(free.pMastery, greaterThan(mcq.pMastery),
        reason: '⭐ ba câu trắc nghiệm đúng là bằng chứng YẾU HƠN ba câu tự luận '
            'đúng — vì đoán trúng có xác suất 0,25 theo cấu trúc. Dùng chung một '
            'hằng số guess là đọc sai bằng chứng một cách hệ thống (pyBKT: multigs).');
  });

  test('mastery luôn nằm trong [0,1] qua chuỗi dài hỗn hợp', () {
    var c = CaseMastery.initial(div, p);
    for (var i = 0; i < 60; i++) {
      c = c.observe(i % 3 != 0, p);
      expect(c.pMastery, inInclusiveRange(0.0, 1.0));
    }
  });
}
