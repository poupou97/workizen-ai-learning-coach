/// FOUNDER DELTA §10 — các ca fail-closed của pedagogical provenance,
/// trên fixture khớp SỰ THẬT CORPUS đã đo (B57 dạy-qua-ví-dụ, B6-L5 nói thẳng).
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/curriculum/pedagogical_boundary.dart';
import 'package:learning_coach/core/knowledge/provenance.dart';
import 'package:learning_coach/core/tutor/teaching_provenance.dart';

const _stage = LearningStage(
  grade: 5, bookSeries: 'kntt', lessonId: 'toan5-t1-bai6',
  conceptsIntroduced: {'phan-so', 'chia-het', 'nhan-so-tu-nhien'},
  methodsIntroduced: {'common-denom-by-product', 'common-denom-take-larger'},
  terminologyIntroduced: {'mẫu số chung'},
);

// SỰ THẬT CORPUS: B57 Toán 4 tr.62 dạy take-larger THUẦN VÍ DỤ (0 câu «Muốn»)
const _takeLarger = TeachingMethod(
  id: 'common-denom-take-larger',
  name: 'Lấy mẫu số lớn hơn làm mẫu số chung',
  appliesToConcepts: {'quy-dong'},
  skillCaseId: 'denominator-divisible',
  requiresConcepts: {'phan-so', 'chia-het'},
  requiresTerminology: {'mẫu số chung'},
  provenance: Provenance(
    origin: KnowledgeOrigin.sourceDemonstrated,
    sourceId: 'toan4-kntt-t2', extractionMethod: 'deterministic-marker-v1',
    confidence: 1.0, subject: 'Toán', grade: 4, pageStart: 62,
  ),
);

// method CHƯA truy được nguồn — phải fail closed ở tầng phát ngôn
const _noSource = TeachingMethod(
  id: 'common-denom-by-product',
  name: 'Lấy mẫu số chung là tích hai mẫu số',
  appliesToConcepts: {'quy-dong'},
  skillCaseId: 'denominator-non-divisible',
  requiresConcepts: {'phan-so', 'nhan-so-tu-nhien'},
  requiresTerminology: {'mẫu số chung'},
);

void main() {
  test('⭐ F3: DEMONSTRATED không bao giờ thành «Theo SGK» trần (sách-nói)', () {
    final scope = TutorScope.forProblem('quy-dong', 'denominator-divisible',
        _stage, const [_takeLarger, _noSource]);
    final tp = explainTeaching(
        scope: scope,
        methodId: 'common-denom-take-larger',
        exerciseCase: 'denominator-divisible')!;
    expect(tp.authority, KnowledgeOrigin.sourceDemonstrated);
    expect(tp.sourceLineForChild, contains('ví dụ'));
    expect(tp.sourceLineForChild, contains('trang 62'));
    expect(tp.sourceLineForChild, isNot(startsWith('Theo SGK')),
        reason: 'loại hỗ trợ là MỘT PHẦN của tính đúng trích dẫn — '
            'dạy-qua-ví-dụ không được đội lốt sách-nói-thẳng');
  });

  test('F1/F4: method KHÔNG truy được nguồn ⇒ không claim «SGK dạy cách này»',
      () {
    final scope = TutorScope.forProblem('quy-dong', 'denominator-non-divisible',
        _stage, const [_takeLarger, _noSource]);
    final tp = explainTeaching(
        scope: scope,
        methodId: 'common-denom-by-product',
        exerciseCase: 'denominator-non-divisible')!;
    expect(tp.source, isNull);
    expect(tp.authority, isNull);
    expect(tp.sourceLineForChild, contains('cách của SAM'));
    expect(tp.sourceLineForChild.toLowerCase(), isNot(contains('sgk')),
        reason: 'không nguồn ⇒ không mượn thẩm quyền sách');
  });

  test('⭐ F7: method map được ca nhưng KHÔNG có phép sư phạm ⇒ null, không dạy',
      () {
    // stage KHÔNG dạy take-larger (methodsIntroduced thiếu nó)
    const bareStage = LearningStage(
      grade: 5, bookSeries: 'kntt', lessonId: 'toan5-t1-bai6',
      conceptsIntroduced: {'phan-so', 'nhan-so-tu-nhien'},
      methodsIntroduced: {'common-denom-by-product'},
      terminologyIntroduced: {'mẫu số chung'},
    );
    final scope = TutorScope.forProblem('quy-dong', 'denominator-divisible',
        bareStage, const [_takeLarger, _noSource]);
    expect(
        explainTeaching(
            scope: scope,
            methodId: 'common-denom-take-larger',
            exerciseCase: 'denominator-divisible'),
        isNull,
        reason: 'ALLOWED thất bại ⇒ không TeachingAct, không lời giải thích');
  });

  test('F2 (kế thừa TutorScope): caseUnknown ⇒ scope rỗng ⇒ mọi giải thích null',
      () {
    final scope = TutorScope.forProblem(
        'quy-dong', null, _stage, const [_takeLarger, _noSource]);
    expect(
        explainTeaching(
            scope: scope,
            methodId: 'common-denom-take-larger',
            exerciseCase: null),
        isNull);
  });

  test('WHY đọc được: nêu dạng bài + vị trí chương trình, tất định', () {
    final scope = TutorScope.forProblem('quy-dong', 'denominator-divisible',
        _stage, const [_takeLarger]);
    final tp = explainTeaching(
        scope: scope,
        methodId: 'common-denom-take-larger',
        exerciseCase: 'denominator-divisible')!;
    expect(tp.whyLineForChild, contains('dạng'));
    expect(tp.whyLineForChild, contains('lớp 5'));
  });
}
