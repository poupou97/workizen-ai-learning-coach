/// ⭐⭐⭐ THIN SLICE — chứng minh kiến trúc NỐI ĐƯỢC từ đầu tới cuối.
///
///   Bài tập → ca → khái niệm → phương pháp áp dụng được → trạng thái học sinh
///   → phương pháp ĐƯỢC PHÉP → quyết định → TutorScope → bằng chứng học tập
///
/// Dữ liệu **đo từ corpus KNTT thật**:
///   lớp 4 Bài 57 tr.62 — ca "chia hết"      → lấy mẫu lớn
///   lớp 5 Bài 6  tr.20 — ca "không chia hết" → lấy TÍCH hai mẫu
///   BCNN: 0 lần trong 53 trang Toán 5 đã OCR
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/adaptive/adaptive_engine.dart';
import 'package:learning_coach/core/curriculum/concept.dart';
import 'package:learning_coach/core/curriculum/pedagogical_boundary.dart';
import 'package:learning_coach/core/curriculum/skill_case.dart';
import 'package:learning_coach/core/student/mastery.dart';

void main() {
  const concept = 'quy-dong';
  const div = 'denominator-divisible';
  const nonDiv = 'denominator-non-divisible';
  const p = BktParams.freeResponse;

  const mTakeLarger = TeachingMethod(
    id: 'common-denom-take-larger', name: 'Lấy mẫu số lớn hơn',
    appliesToConcepts: {concept}, skillCaseId: div,
    requiresConcepts: {'phan-so', 'chia-het'},
    requiresTerminology: {'mẫu số chung'});
  const mProduct = TeachingMethod(
    id: 'common-denom-by-product', name: 'Lấy tích hai mẫu số',
    appliesToConcepts: {concept}, skillCaseId: nonDiv,
    requiresConcepts: {'phan-so', 'nhan-so-tu-nhien'},
    requiresTerminology: {'mẫu số chung'});
  const mLcm = TeachingMethod(
    id: 'common-denom-by-lcm', name: 'Lấy BCNN',
    appliesToConcepts: {concept}, skillCaseId: nonDiv,
    requiresConcepts: {'phan-so', 'bcnn'},
    requiresTerminology: {'bội chung nhỏ nhất'});
  const catalogue = [mTakeLarger, mProduct, mLcm];

  const grade5 = LearningStage(
    grade: 5, bookSeries: 'kntt', lessonId: 'toan5-t1-bai6',
    conceptsIntroduced: {'phan-so', 'chia-het', 'nhan-so-tu-nhien'},
    methodsIntroduced: {'common-denom-take-larger', 'common-denom-by-product'},
    terminologyIntroduced: {'mẫu số chung'});

  CaseMastery drill(String id, List<bool> a) {
    var c = CaseMastery.initial(id, p);
    for (final x in a) { c = c.observe(x, p); }
    return c;
  }

  test('① phát hiện ca TẤT ĐỊNH từ mẫu số — không cần LLM', () {
    expect(fractionCase(8, 4), div,   reason: '8 chia hết cho 4 → ca lớp 4');
    expect(fractionCase(4, 5), nonDiv, reason: '4 và 5 không chia hết → ca lớp 5');
    expect(fractionCase(4, 0), isNull, reason: 'đầu vào hỏng ⇒ null, không đoán');
  });

  test('⭐⭐⭐ CHUỖI TRỌN VẸN: học sinh vững ca lớp 4, gặp bài 3/4 + 2/5', () {
    // Bằng chứng: 6 lần đúng ở ca chia hết, chưa từng gặp ca không chia hết.
    final mastery = ConceptMastery(conceptId: concept, cases: {
      div: drill(div, [true, true, true, true, true, true]),
      nonDiv: CaseMastery.initial(nonDiv, p),
    });

    final exCase = fractionCase(4, 5);           // ② ca của bài
    expect(exCase, nonDiv);

    final d = decide(                            // ③ quyết định
      conceptId: concept, exerciseCase: exCase,
      mastery: mastery, stage: grade5, catalogue: catalogue,
    );

    // ④ Chẩn đoán ĐÚNG loại — không phải "không hiểu quy đồng"
    expect(d.diagnosis, DiagnosticOutcome.caseTransitionGap,
        reason: '⭐⭐ Em ấy KHÔNG hỏng khái niệm. Em ấy vững dạng đã học và gặp '
            'dạng mới. Chẩn đoán conceptGap ở đây sẽ bắt em học lại thứ đã vững.');
    expect(d.action, LearningAction.contrastCases);

    // ⑤ Phương pháp tới tay Tutor: ĐÚNG ca VÀ đã được dạy
    expect(d.scope.allowedMethods.map((m) => m.id), ['common-denom-by-product'],
        reason: '⭐ mTakeLarger đúng-đã-học nhưng SAI CA; mLcm đúng-ca nhưng CHƯA '
            'HỌC (BCNN: 0 lần trong 53 trang Toán 5). Giao của hai điều kiện chỉ '
            'còn một phương pháp — đúng cái sách đang dạy.');

    // ⑥ Lý do đọc được cho phụ huynh
    expect(d.reason, contains(nonDiv));
    expect(d.reason, isNot(contains('BCNN')));
    expect(d.remediation, RemediationStatus.remediateAvailable);
  });

  test('⭐ CÙNG học sinh, bài ca CHIA HẾT ⇒ chẩn đoán và phương pháp khác hẳn', () {
    final mastery = ConceptMastery(conceptId: concept, cases: {
      div: drill(div, [true, true, true, true, true, true]),
      nonDiv: CaseMastery.initial(nonDiv, p),
    });
    final d = decide(
      conceptId: concept, exerciseCase: fractionCase(8, 4),
      mastery: mastery, stage: grade5, catalogue: catalogue);
    expect(d.diagnosis, DiagnosticOutcome.executionError,
        reason: 'ca này em vững ⇒ sai là nhầm tính, không phải chưa hiểu');
    expect(d.scope.allowedMethods.map((m) => m.id), ['common-denom-take-larger']);
  });

  test('⭐ OCR hỏng, không đọc được mẫu số ⇒ FAIL CLOSED trọn chuỗi', () {
    final d = decide(
      conceptId: concept, exerciseCase: null,
      mastery: ConceptMastery(conceptId: concept, cases: const {}),
      stage: grade5, catalogue: catalogue);
    expect(d.scope.allowedMethods, isEmpty,
        reason: '⭐ Ảnh mờ hay chụp thiếu đề thì Tutor KHÔNG nhận phương pháp nào. '
            'Thà nói "chưa chắc" còn hơn dạy nhầm dạng bài.');
    expect(d.diagnosis, DiagnosticOutcome.insufficientEvidence);
    expect(d.remediation, RemediationStatus.diagnosticConfidenceLow);

    // ⭐ Hai ca "chưa kết luận được" nói với phụ huynh HAI câu khác nhau, và khác
    // biệt đó phải được khoá lại.
    //
    // Phát hiện khi chạy đột biến: gỡ chốt null trong `decide()` mà test vẫn XANH,
    // vì `TutorScope.forProblem` cũng có chốt null riêng và nhánh rơi cuối hàm cho
    // cùng `diagnosis` + `remediation`. Hai lớp chắn độc lập ⇒ gỡ một lớp không lộ.
    // Thứ THỰC SỰ khác là câu nói: "chưa đọc được đề" ≠ "chưa đủ dữ kiện về con".
    expect(d.reason, contains('dạng bài'),
        reason: '⭐ Không đọc được đề là lỗi của ẢNH, không phải của đứa trẻ. Nói '
            '"chưa đủ dữ kiện" ở đây là đổ lỗi nhầm chỗ cho học sinh.');

    final noEvidence = decide(
        conceptId: concept, exerciseCase: nonDiv,
        mastery: ConceptMastery(conceptId: concept, cases: const {}),
        stage: grade5, catalogue: catalogue);
    expect(noEvidence.reason, isNot(contains('dạng bài')));
  });

  test('⭐ học sinh MỚI tinh ⇒ không bị kết luận là hỏng', () {
    final d = decide(
      conceptId: concept, exerciseCase: nonDiv,
      mastery: ConceptMastery(conceptId: concept, cases: {
        div: CaseMastery.initial(div, p),
        nonDiv: CaseMastery.initial(nonDiv, p),
      }),
      stage: grade5, catalogue: catalogue);
    expect(d.diagnosis, DiagnosticOutcome.insufficientEvidence,
        reason: '⭐ Không bằng chứng nào ⇒ không kết luận nào. Ngày đầu dùng app '
            'mà đã bị báo "con hổng kiến thức" là hỏng niềm tin ngay lập tức.');
  });

  test('⑦ vòng lặp khép kín: bằng chứng mới đổi quyết định lần sau', () {
    var m = ConceptMastery(conceptId: concept, cases: {
      div: drill(div, [true, true, true, true, true, true]),
      nonDiv: CaseMastery.initial(nonDiv, p),
    });
    expect(decide(conceptId: concept, exerciseCase: nonDiv, mastery: m,
        stage: grade5, catalogue: catalogue).diagnosis,
        DiagnosticOutcome.caseTransitionGap);

    // Học sinh luyện ca mới và làm đúng nhiều lần.
    m = ConceptMastery(conceptId: concept, cases: {
      ...m.cases,
      nonDiv: drill(nonDiv, [true, true, true, true, true, true, true, true]),
    });
    final after = decide(conceptId: concept, exerciseCase: nonDiv, mastery: m,
        stage: grade5, catalogue: catalogue);
    expect(after.diagnosis, isNot(DiagnosticOutcome.caseTransitionGap),
        reason: '⭐ Bằng chứng mới PHẢI đổi kết luận — §14: mastery updateable và '
            'recoverable. Một mô hình không đổi theo tiến bộ của trẻ là mô hình sai.');
    expect(m.stateAt(), MasteryState.mastered);
  });
}
