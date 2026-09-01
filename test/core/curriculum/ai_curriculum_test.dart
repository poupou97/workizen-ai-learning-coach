/// ADR-008 — luật của AiCurriculum giữ bằng test trên FIXTURE TỔNG HỢP
/// (text thật của QĐ 2422 ở pack ngoài git — legal REVIEW PENDING).
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/curriculum/ai_curriculum.dart';

AiOutcome _o(String code, {int page = 1, AiOutcomeStatus? status}) =>
    AiOutcome.parse(
        code: code,
        text: 'fixture cho $code',
        sourcePage: page,
        status: status ?? AiOutcomeStatus.sourceExplicit)!;

void main() {
  final cur = AiCurriculum([
    _o('3.A1.1'), _o('3.A1.2'), _o('3.C5.1'),
    _o('3.A1.MR1'),
    _o('5.B2.1'),
    _o('9.C4.MR2', status: AiOutcomeStatus.inferredOcrCorrected),
    _o('12.D2.MR3'),
  ]);

  test('parse: mã đúng định dạng chính thức mới được mint', () {
    expect(AiOutcome.parse(code: '6.A1.MR1', text: 't', sourcePage: 1),
        isNotNull);
    // mã hỏng — mọi biến thể đều bị từ chối, không "sửa hộ"
    for (final bad in ['6.E1.1', '13.A1.1', '0.A1.1', 'A1.1', '6.A1.XR1',
        '6.A.1', '6.A1.MR']) {
      expect(AiOutcome.parse(code: bad, text: 't', sourcePage: 1), isNull,
          reason: 'mã "$bad" phải bị từ chối');
    }
    final mr = AiOutcome.parse(code: '6.A1.MR1', text: 't', sourcePage: 9)!;
    expect(mr.extended, isTrue, reason: 'MR trong mã = mở rộng (F3 tại nguồn)');
    expect(mr.grade, 6);
    expect(mr.topic, 'A1');
    expect(mr.strand, AiStrand.a);
    expect(mr.sourcePage, 9, reason: 'provenance trang bắt buộc');
  });

  test('⭐ F8: trần lớp fail-closed — hỏi vượt trần trả RỖNG, không lộ', () {
    expect(cur.forGrade(3, gradeCeiling: 3), hasLength(4));
    expect(cur.forGrade(5, gradeCeiling: 3), isEmpty,
        reason: 'học sinh lớp 3 hỏi nội dung lớp 5 ⇒ rỗng');
    expect(cur.forGrade(12, gradeCeiling: 3), isEmpty);
    // progression cũng chịu trần
    final p = cur.progression(AiStrand.c, gradeCeiling: 3);
    expect(p.map((o) => o.code), ['3.C5.1'],
        reason: '9.C4.MR2 lớp 9 không được lọt qua trần lớp 3');
  });

  test('mã lạ ⇒ null, không đoán (fail closed)', () {
    expect(cur.byCode('7.A1.1'), isNull);
    expect(cur.beyondGrade('7.A1.1', currentGrade: 5), isNull,
        reason: 'không biết ⇒ null — UNKNOWN không thành một câu trả lời');
    expect(cur.beyondGrade('9.C4.MR2', currentGrade: 5), isTrue);
    expect(cur.beyondGrade('3.A1.1', currentGrade: 5), isFalse);
  });

  test('F6: status suy-diễn đi theo record, không đội lốt nguyên văn', () {
    expect(cur.byCode('9.C4.MR2')!.status,
        AiOutcomeStatus.inferredOcrCorrected);
    expect(cur.byCode('3.A1.1')!.status, AiOutcomeStatus.sourceExplicit);
  });

  test('F4: không API nào suy prerequisite từ mã — progression sắp theo LỚP',
      () {
    final p = cur.progression(AiStrand.a, gradeCeiling: 12);
    expect(p.map((o) => o.grade).toList(), [3, 3, 3],
        reason: 'chỉ có dữ liệu lớp 3 cho mạch A trong fixture');
    // cốt lõi đứng trước mở rộng trong cùng lớp/chủ đề — thứ tự HIỂN THỊ
    expect(p.map((o) => o.code).toList(), ['3.A1.1', '3.A1.2', '3.A1.MR1']);
  });
}
