/// ⭐⭐ F2 — biên/tương đương của APPLICABLE_TO_PROBLEM (Founder Decision 3).
///
/// Danh sách ca biên là CỦA FOUNDER, không phải của agent: cùng mẫu · chia hết
/// · coprime · non-coprime non-divisible · unknown/malformed. Unknown fail closed.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/adaptive/adaptive_engine.dart';
import 'package:learning_coach/core/curriculum/pedagogical_boundary.dart';
import 'package:learning_coach/core/curriculum/problem_applicability.dart';

void main() {
  group('bốn ca biên — vét cạn và loại trừ nhau', () {
    test('cùng mẫu số: 3/5 + 1/5 KHÔNG có bước quy đồng nào', () {
      final a = analyzeFractionPair(5, 5)!;
      expect(a.equal, isTrue);
      expect(a.oneDividesOther, isFalse,
          reason: '⭐⭐ `5 % 5 == 0` là đúng số học và SAI toán học về ca — '
              'đây chính là lỗi gốc F2. Chia hết đòi hai mẫu KHÁC nhau.');
      expect(a.skillCase, 'denominator-equal');
    });

    test('một mẫu chia hết cho mẫu kia', () {
      for (final (d1, d2) in [(2, 4), (4, 2), (3, 9), (12, 4)]) {
        final a = analyzeFractionPair(d1, d2)!;
        expect(a.oneDividesOther, isTrue, reason: '$d1,$d2');
        expect(a.skillCase, 'denominator-divisible');
      }
    });

    test('coprime: tích hai mẫu CHÍNH LÀ mẫu chung nhỏ nhất', () {
      final a = analyzeFractionPair(4, 5)!;
      expect(a.coprime, isTrue);
      expect(a.skillCase, 'denominator-non-divisible');
      expect(a.lcm, a.product);
      expect(a.productExceedsLcm, isFalse);
    });

    test('⭐ non-coprime non-divisible: tích VƯỢT mẫu chung nhỏ nhất', () {
      final a = analyzeFractionPair(4, 6)!;
      expect(a.nonCoprimeNonDivisible, isTrue);
      expect(a.skillCase, 'denominator-non-divisible',
          reason: 'sách lớp 5 dạy chung một phương pháp — gộp ở tầng '
              'SkillCase là sự thật SƯ PHẠM');
      expect(a.lcm, 12);
      expect(a.product, 24);
      expect(a.productExceedsLcm, isTrue,
          reason: '⭐ một đứa trẻ quy đồng 4,6 ra 12 là ĐÚNG — trình chấm nào '
              'chỉ chấp nhận 24 sẽ đánh sai em ấy. Cờ này tồn tại để điều đó '
              'không xảy ra.');
    });

    test('⭐ vét cạn: mọi cặp hợp lệ rơi vào ĐÚNG MỘT trong bốn ca', () {
      for (var d1 = 1; d1 <= 12; d1++) {
        for (var d2 = 1; d2 <= 12; d2++) {
          final a = analyzeFractionPair(d1, d2)!;
          final flags = [
            a.equal,
            a.oneDividesOther,
            a.coprime,
            a.nonCoprimeNonDivisible
          ].where((f) => f).length;
          expect(flags, 1,
              reason: '$d1,$d2 phải thuộc đúng một ca — chồng ca hoặc rơi '
                  'ra ngoài đều là lỗ để một phương pháp sai lọt vào');
        }
      }
    });
  });

  group('unknown/malformed — fail closed, không đoán', () {
    test('mẫu số 0, âm, hoặc thiếu ⇒ null', () {
      expect(analyzeFractionPair(0, 5), isNull);
      expect(analyzeFractionPair(5, 0), isNull);
      expect(analyzeFractionPair(-3, 4), isNull);
      expect(analyzeFractionPair(null, 5), isNull);
      expect(analyzeFractionPair(5, null), isNull);
      expect(fractionCase(0, 5), isNull);
    });

    test('null chảy xuống TutorScope thành tập RỖNG', () {
      const stage = LearningStage(
        grade: 5, bookSeries: 'kntt', lessonId: 'x',
        conceptsIntroduced: {'phan-so'},
        methodsIntroduced: {'m1'},
        terminologyIntroduced: {'mẫu số chung'},
      );
      const m = TeachingMethod(
          id: 'm1', name: 'x', appliesToConcepts: {'quy-dong'},
          skillCaseId: 'denominator-divisible',
          requiresConcepts: {}, requiresTerminology: {});
      final s = TutorScope.forProblem(
          'quy-dong', fractionCase(0, 5), stage, const [m]);
      expect(s.allowedMethods, isEmpty);
    });
  });

  group('⭐⭐ siết wildcard — phương pháp KHÔNG KHAI ca không vào phạm vi bài', () {
    const stage = LearningStage(
      grade: 5, bookSeries: 'kntt', lessonId: 'x',
      conceptsIntroduced: {'phan-so'},
      methodsIntroduced: {'m-wild', 'm-div'},
      terminologyIntroduced: {'mẫu số chung'},
    );
    const wildcard = TeachingMethod(
        id: 'm-wild', name: 'không khai ca',
        appliesToConcepts: {'quy-dong'},
        requiresConcepts: {}, requiresTerminology: {});
    const mDiv = TeachingMethod(
        id: 'm-div', name: 'lấy mẫu lớn',
        appliesToConcepts: {'quy-dong'}, skillCaseId: 'denominator-divisible',
        requiresConcepts: {}, requiresTerminology: {});

    test('trong phạm vi MỘT BÀI: caseNotDeclared, fail closed', () {
      final e = eligibilityForProblem(
          wildcard, 'quy-dong', 'denominator-equal', stage);
      expect(e.eligible, isFalse);
      expect(e.rejection, MethodRejection.caseNotDeclared,
          reason: '⭐⭐ wildcard là cửa sau đưa phương pháp quy đồng tới bài '
              'cùng-mẫu-số — đúng lỗi F2 qua đường khác. Không khai = unknown, '
              'unknown fail closed.');
    });

    test('duyệt mức KHÁI NIỆM (forConcept) vẫn dùng được', () {
      final s = TutorScope.forConcept('quy-dong', stage, const [wildcard]);
      expect(s.allowedMethods.map((m) => m.id), contains('m-wild'),
          reason: 'siết áp cho phạm-vi-bài, không cấm duyệt tài nguyên '
              'của khái niệm');
    });

    test('⭐ 3/5 + 1/5 KHÔNG bao giờ nhận phương pháp quy đồng', () {
      final kase = fractionCase(5, 5);
      expect(kase, 'denominator-equal');
      final e = eligibilityForProblem(mDiv, 'quy-dong', kase, stage);
      expect(e.rejection, MethodRejection.notApplicableToCase);
      final s = TutorScope.forProblem('quy-dong', kase, stage, const [mDiv, wildcard]);
      expect(s.allowedMethods, isEmpty,
          reason: '⭐ chưa có method nào đăng ký cho ca cùng-mẫu ⇒ tập rỗng '
              'là hành vi ĐÚNG: thà im còn hơn dạy quy đồng cho bài không '
              'cần quy đồng');
    });
  });
}
