/// ⭐⭐ CHỐT VÀNG — phương pháp gate theo CA, không chỉ theo lớp.
///
/// Dữ liệu đo từ corpus KNTT:
///   lớp 4 Bài 57 tr.62 — ca "mẫu này CHIA HẾT cho mẫu kia" → lấy mẫu lớn
///   lớp 5 Bài 6  tr.20 — ca "KHÔNG chia hết cho nhau"      → lấy TÍCH hai mẫu
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/curriculum/pedagogical_boundary.dart';
import 'package:learning_coach/core/curriculum/skill_case.dart';

void main() {
  const concept = 'quy-dong';
  const caseDiv = 'denominator-divisible';
  const caseNonDiv = 'denominator-non-divisible';

  const mDivisible = TeachingMethod(
    id: 'common-denom-take-larger',
    name: 'Lấy mẫu số lớn hơn làm mẫu số chung',
    appliesToConcepts: {concept},
    skillCaseId: caseDiv,
    requiresConcepts: {'phan-so', 'chia-het'},
    requiresTerminology: {'mẫu số chung'},
  );
  const mProduct = TeachingMethod(
    id: 'common-denom-by-product',
    name: 'Lấy mẫu số chung là tích hai mẫu số',
    appliesToConcepts: {concept},
    skillCaseId: caseNonDiv,
    requiresConcepts: {'phan-so', 'nhan-so-tu-nhien'},
    requiresTerminology: {'mẫu số chung'},
  );
  const mLcm = TeachingMethod(
    id: 'common-denom-by-lcm',
    name: 'Lấy BCNN làm mẫu số chung',
    appliesToConcepts: {concept},
    skillCaseId: caseNonDiv,
    requiresConcepts: {'phan-so', 'bcnn'},
    requiresTerminology: {'bội chung nhỏ nhất'},
  );
  const catalogue = [mDivisible, mProduct, mLcm];

  const grade4 = LearningStage(
    grade: 4, bookSeries: 'kntt', lessonId: 'toan4-t2-bai57',
    conceptsIntroduced: {'phan-so', 'chia-het'},
    methodsIntroduced: {'common-denom-take-larger'},
    terminologyIntroduced: {'mẫu số chung'},
  );
  const grade5 = LearningStage(
    grade: 5, bookSeries: 'kntt', lessonId: 'toan5-t1-bai6',
    conceptsIntroduced: {'phan-so', 'chia-het', 'nhan-so-tu-nhien'},
    methodsIntroduced: {'common-denom-take-larger', 'common-denom-by-product'},
    terminologyIntroduced: {'mẫu số chung'},
  );

  List<String> ids(TutorScope s) => s.allowedMethods.map((m) => m.id).toList();

  test('A · ca CHIA HẾT + học sinh lớp 4 ⇒ có phương pháp của lớp 4', () {
    expect(ids(TutorScope.forProblem(concept, caseDiv, grade4, catalogue)),
        ['common-denom-take-larger']);
  });

  test('B · ca KHÔNG chia hết + lớp 5 ⇒ phương pháp TÍCH, không phải BCNN', () {
    expect(ids(TutorScope.forProblem(concept, caseNonDiv, grade5, catalogue)),
        ['common-denom-by-product'],
        reason: '⭐ BCNN áp đúng ca này về mặt toán học, nhưng lớp 5 KNTT chưa '
            'dạy — đo được: BCNN xuất hiện 0 lần trong 53 trang');
  });

  test('C · vững ca cũ, gặp ca mới ⇒ KHÔNG phải hỏng cả khái niệm', () {
    // Học sinh có bằng chứng mạnh ở ca chia hết, chưa có ở ca không chia hết.
    const d = DiagnosticOutcome.caseTransitionGap;
    expect(actionFor(d), LearningAction.contrastCases,
        reason: '⭐⭐ Can thiệp đúng là ĐỐI CHIẾU HAI CA, không dạy lại khái niệm. '
            'Bắt một đứa trẻ học lại thứ nó đã vững là cách nhanh nhất làm nó '
            'chán — và chẩn đoán conceptGap sẽ làm đúng như vậy.');
    expect(actionFor(DiagnosticOutcome.conceptGap), LearningAction.teach);
    expect(actionFor(d), isNot(actionFor(DiagnosticOutcome.conceptGap)));
  });

  test('D · CÙNG khái niệm, CA khác ⇒ tập phương pháp KHÁC', () {
    final a = ids(TutorScope.forProblem(concept, caseDiv, grade5, catalogue));
    final b = ids(TutorScope.forProblem(concept, caseNonDiv, grade5, catalogue));
    expect(a, ['common-denom-take-larger']);
    expect(b, ['common-denom-by-product']);
    expect(a, isNot(b),
        reason: '⭐ CÙNG học sinh, CÙNG khái niệm, CÙNG lớp — chỉ khác ĐIỀU KIỆN '
            'của bài. Nếu hai tập bằng nhau thì tầng SkillCase là trang trí.');
  });

  test('E · đúng ca nhưng CHƯA được dạy ⇒ lọc trước khi tới Tutor', () {
    final e = eligibilityForProblem(mLcm, concept, caseNonDiv, grade5);
    expect(e.eligible, isFalse);
    expect(e.rejection, MethodRejection.conceptNotIntroduced);
    expect(e.missing, contains('bcnn'));
  });

  test('⭐ KHÔNG xác định được ca ⇒ FAIL CLOSED, Tutor không nhận gì', () {
    final s = TutorScope.forProblem(concept, null, grade5, catalogue);
    expect(s.allowedMethods, isEmpty,
        reason: '⭐ Thà im còn hơn dạy một phương pháp cho sai loại bài. Ảnh mờ, '
            'chụp thiếu đề, OCR hỏng — đều dẫn tới đây, và đều phải nói "chưa chắc".');
    expect(eligibilityForProblem(mProduct, concept, null, grade5).rejection,
        MethodRejection.caseUnknown);
  });

  test('⭐ phương pháp SAI CA bị loại với lý do riêng, không lẫn với chưa-được-dạy',
      () {
    final e = eligibilityForProblem(mDivisible, concept, caseNonDiv, grade5);
    expect(e.rejection, MethodRejection.notApplicableToCase,
        reason: 'gộp "sai ca" với "chưa học" là mất thông tin chẩn đoán — hai ca '
            'này dẫn tới hai can thiệp khác nhau');
  });
}
