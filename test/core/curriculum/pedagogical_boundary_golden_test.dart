/// ⭐⭐ CHỐT VÀNG — cùng một bài toán, khác learning state ⇒ khác phương pháp dạy.
///
/// Dữ liệu trong tệp này **đo từ corpus thật**, không bịa:
/// Toán 5 KNTT tập một, Bài 6 (trang in 20) dạy nguyên văn *"Hai mẫu số 5 và 2
/// không chia hết cho nhau. Lấy mẫu số chung là TÍCH của hai mẫu số (5 × 2 = 10)."*
/// Quét 53 trang OCR: `BCNN` · `bội chung` · `ƯCLN` xuất hiện **0 lần**.
///
/// Đây là chốt bảo vệ điều dễ hỏng nhất của sản phẩm: một câu trả lời **đúng về
/// toán học** nhưng **sai về sư phạm** thì không có test thông thường nào bắt
/// được — nó đúng.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/curriculum/pedagogical_boundary.dart';

void main() {
  const addUnlike = 'add-unlike-fractions';

  // ── Danh mục method: hai cách quy đồng, đều ĐÚNG về toán học ───────────────
  const productMethod = TeachingMethod(
    id: 'common-denom-by-product',
    name: 'Lấy mẫu số chung là tích hai mẫu số',
    appliesToConcepts: {addUnlike},
    requiresConcepts: {'quy-dong', 'nhan-so-tu-nhien'},
    requiresTerminology: {'mẫu số chung'},
  );
  const lcmMethod = TeachingMethod(
    id: 'common-denom-by-lcm',
    name: 'Lấy mẫu số chung là BCNN',
    appliesToConcepts: {addUnlike},
    requiresConcepts: {'quy-dong', 'bcnn'},
    requiresTerminology: {'bội chung nhỏ nhất'},
  );
  const catalogue = [productMethod, lcmMethod];

  // ── Trạng thái A: học sinh lớp 5 KNTT, đang ở Bài 6 ───────────────────────
  const grade5AtLesson6 = LearningStage(
    grade: 5,
    bookSeries: 'kntt',
    lessonId: 'toan5-t1-bai6',
    conceptsIntroduced: {'phan-so', 'rut-gon', 'quy-dong', 'nhan-so-tu-nhien'},
    methodsIntroduced: {'common-denom-by-product'},
    terminologyIntroduced: {'mẫu số chung', 'rút gọn', 'phân số tối giản'},
  );

  // ── Trạng thái B: cùng học sinh, sau khi ĐÃ học BCNN ──────────────────────
  const laterStageWithLcm = LearningStage(
    grade: 6,
    bookSeries: 'kntt',
    lessonId: 'toan6-bcnn-sau',
    conceptsIntroduced: {
      'phan-so', 'rut-gon', 'quy-dong', 'nhan-so-tu-nhien', 'bcnn'
    },
    methodsIntroduced: {'common-denom-by-product', 'common-denom-by-lcm'},
    terminologyIntroduced: {
      'mẫu số chung', 'rút gọn', 'phân số tối giản', 'bội chung nhỏ nhất'
    },
  );

  test('⭐⭐ lớp 5 Bài 6: CHỈ method của sách được phép — BCNN bị chặn', () {
    final scope = TutorScope.forConcept(addUnlike, grade5AtLesson6, catalogue);

    expect(scope.allowedMethods.map((m) => m.id), ['common-denom-by-product'],
        reason: '⭐ Sách dạy lấy TÍCH hai mẫu số (Toán 5 KNTT tr.20). BCNN đúng '
            'về toán học nhưng học sinh CHƯA HỌC — dùng nó là dạy ngoài chương '
            'trình, và Parent Coach sẽ bảo phụ huynh hỏi con về một khái niệm '
            'con chưa từng gặp.');

    final why = eligibilityOf(lcmMethod, addUnlike, grade5AtLesson6);
    expect(why.eligible, isFalse);
    expect(why.rejection, MethodRejection.conceptNotIntroduced);
    expect(why.missing, contains('bcnn'),
        reason: 'phải nói RÕ thiếu gì — Parent Coach cần giải thích được');
  });

  test('⭐⭐ CÙNG bài toán, learning state MUỘN HƠN ⇒ BCNN được phép', () {
    final scope = TutorScope.forConcept(addUnlike, laterStageWithLcm, catalogue);
    expect(scope.allowedMethods.map((m) => m.id),
        containsAll(['common-denom-by-product', 'common-denom-by-lcm']),
        reason: '⭐ Đây là nửa còn lại của bất biến: ranh giới sư phạm KHÔNG '
            'phải cấm vĩnh viễn một phương pháp. Nó mở ra khi học sinh đã học. '
            'Một chốt chỉ chặn mà không bao giờ mở là chốt sai.');
  });

  test('⭐ CÙNG bài toán + CÙNG concept, hai state cho hai tập method KHÁC nhau',
      () {
    final a = TutorScope.forConcept(addUnlike, grade5AtLesson6, catalogue);
    final b = TutorScope.forConcept(addUnlike, laterStageWithLcm, catalogue);
    expect(a.allowedMethods.length, isNot(b.allowedMethods.length),
        reason: '⭐⭐ Đây LÀ phát biểu của Founder: SAME MATHEMATICAL PROBLEM + '
            'DIFFERENT LEARNING STATE = POSSIBLY DIFFERENT TUTORING METHOD. '
            'Nếu hai tập bằng nhau thì learning state không ảnh hưởng gì và cả '
            'kiến trúc này là trang trí.');
  });

  test('⭐ từ vựng cũng bị chặn, không chỉ khái niệm', () {
    const sameConceptsNoTerm = LearningStage(
      grade: 5, bookSeries: 'kntt', lessonId: 'x',
      conceptsIntroduced: {'quy-dong', 'bcnn', 'nhan-so-tu-nhien'},
      methodsIntroduced: {'common-denom-by-lcm'},
      terminologyIntroduced: {'mẫu số chung'}, // thiếu "bội chung nhỏ nhất"
    );
    final e = eligibilityOf(lcmMethod, addUnlike, sameConceptsNoTerm);
    expect(e.rejection, MethodRejection.terminologyNotIntroduced,
        reason: 'biết khái niệm mà chưa gặp TỪ gọi tên nó thì lời giải thích vẫn '
            'là tiếng lạ — đo được: Toán 5 KNTT không dùng cụm "phân số bằng nhau"');
  });

  test('method không áp dụng cho concept thì bị loại vì lý do KHÁC', () {
    final e = eligibilityOf(productMethod, 'khai-niem-khac', grade5AtLesson6);
    expect(e.rejection, MethodRejection.notApplicable,
        reason: 'gộp mọi lý do từ chối vào một là mất thông tin chẩn đoán');
  });
}
