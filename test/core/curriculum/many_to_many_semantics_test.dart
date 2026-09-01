/// ⭐ WAL-54 — chốt SEMANTIC: skillCaseId là TAUGHT-FOR, không phải giới hạn
/// đúng-sai toán học. Kèm phản ví dụ số học chứng minh M:N applicability.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/curriculum/pedagogical_boundary.dart';
import 'package:learning_coach/core/curriculum/problem_applicability.dart';

void main() {
  const mProduct = TeachingMethod(
      id: 'common-denom-by-product', name: 'Lấy tích hai mẫu',
      appliesToConcepts: {'quy-dong'},
      skillCaseId: 'denominator-non-divisible',
      requiresConcepts: {}, requiresTerminology: {});
  const stage = LearningStage(
      grade: 5, bookSeries: 'kntt', lessonId: 'x',
      conceptsIntroduced: {}, methodsIntroduced: {'common-denom-by-product'},
      terminologyIntroduced: {});

  test('⭐ phản ví dụ số học: phương pháp TÍCH đúng cả trên ca CHIA HẾT', () {
    // 1/2 + 1/4 — ca chia hết; quy đồng theo TÍCH (mẫu 8) vẫn cho kết quả đúng.
    final a = analyzeFractionPair(2, 4)!;
    expect(a.skillCase, 'denominator-divisible');
    expect(a.product % a.d1, 0);
    expect(a.product % a.d2, 0,
        reason: 'tích hai mẫu LUÔN là mẫu chung hợp lệ — với mọi cặp, kể cả '
            'chia hết ⇒ Method↔Case là M:N về APPLICABILITY');
    expect(a.productExceedsLcm, isTrue,
        reason: 'tích (8) vượt mẫu chung nhỏ nhất (4) — cùng cấu trúc với '
            'bài học 4,6→24 vs 12: đúng nhưng không gọn');
  });

  test('⭐ semantic hiện hành: TutorScope trả lời "SAM được DẠY gì", KHÔNG phải '
      '"toán học cho phép gì" — và hai câu đó khác nhau', () {
    final e = eligibilityForProblem(
        mProduct, 'quy-dong', 'denominator-divisible', stage);
    expect(e.rejection, MethodRejection.notApplicableToCase,
        reason: 'ĐÚNG cho tutor-selection: sách dạy phương-pháp-tích CHO ca '
            'không-chia-hết, nên SAM không chủ động dạy nó ở ca chia hết. '
            '⚠️ NHƯNG tầng CHẤM BÀI tương lai KHÔNG được tái dùng hàm này để '
            'đánh sai học sinh dùng tích trên ca chia hết — applicability '
            'toán học phải suy từ domain analysis (test trên), không từ '
            'taught-for. Chốt này tồn tại để giữ ranh giới đó thành chữ.');
  });
}
