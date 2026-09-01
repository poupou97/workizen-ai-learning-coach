/// ⭐⭐ CHỐT VÀNG — khái niệm #2: `so-sanh-so-thap-phan` (WAL-36).
///
/// Dữ liệu ĐO TỪ CORPUS: Toán 5 KNTT Bài 11 tr.38–39 (quy tắc ba ca, ví dụ
/// gắn nhãn ca) + tr.40 (luật số-0 tận cùng — mục SAU). Đây là lần thứ hai
/// SkillCase được kiểm trên một khái niệm thật — abstraction giữ nguyên schema.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/curriculum/decimal_comparison_case.dart';
import 'package:learning_coach/core/student/concept_summary.dart';
import 'package:learning_coach/core/student/mastery.dart';

void main() {
  group('bốn ca — theo LỜI SÁCH, không theo cách ta diễn đạt lại', () {
    test('① phần nguyên khác nhau — ví dụ tr.38: "3,5 > 2,75 (phần nguyên có 3 > 2)"',
        () {
      expect(analyzeDecimalComparison('3,5', '2,75')!.skillCase,
          'integer-part-differs');
      // Bài tập 1a tr.39
      expect(analyzeDecimalComparison('37,29', '36,92')!.skillCase,
          'integer-part-differs',
          reason: '⭐ 37,29 vs 36,92: MỌI chữ số thập phân của số bé đều lớn '
              'hơn — đứa trẻ so nhầm tầng sẽ trả lời ngược. Sách xếp bài này '
              'ở ca ①: chỉ phần nguyên quyết định.');
    });

    test('② phần nguyên bằng — ví dụ tr.38: "2,75 > 2,29 (hàng phần mười có 7 > 2)"',
        () {
      expect(analyzeDecimalComparison('2,75', '2,29')!.skillCase,
          'fraction-digit-differs');
      // Bài tập 1b tr.39 — khác ở hàng phần trăm
      expect(analyzeDecimalComparison('135,74', '135,75')!.skillCase,
          'fraction-digit-differs');
    });

    test('③ bằng nhau hoàn toàn — bài tập 1c tr.39: 89,215 và 89,215', () {
      expect(analyzeDecimalComparison('89,215', '89,215')!.skillCase,
          'all-parts-equal');
    });

    test('⭐⭐ ④ KHÁC ĐỘ DÀI — cần luật số-0 tận cùng dạy ở MỤC SAU (tr.40)', () {
      final a = analyzeDecimalComparison('76,3', '76,30')!;
      expect(a.skillCase, 'unequal-decimal-length',
          reason: '⭐⭐ 76,3 = 76,30 về GIÁ TRỊ, nhưng để NHÌN RA điều đó '
              'đứa trẻ cần luật "viết thêm/bỏ chữ số 0" — dạy TÁCH RIÊNG sau '
              'quy tắc ba ca. Vững ①②③ chưa suy ra được vững ④. Chuẩn hoá '
              'trước khi phân ca là XOÁ MẤT đúng ca này.');
      // Bài tr.40: 8,6100 = 8,6? — đuôi khác cả khi không toàn số 0
      expect(analyzeDecimalComparison('8,61', '8,6100')!.skillCase,
          'unequal-decimal-length');
    });

    test('⭐ vét cạn: mọi cặp trong sweep rơi vào ĐÚNG MỘT ca', () {
      const samples = ['3,5', '2,75', '2,29', '37,29', '36,92', '135,74',
        '89,215', '76,3', '76,30', '0,7', '0,70', '38', '8,6100'];
      for (final x in samples) {
        for (final y in samples) {
          final a = analyzeDecimalComparison(x, y)!;
          final n = [
            a.integerPartDiffers,
            a.fractionDigitDiffers,
            a.unequalDecimalLength,
            a.allPartsEqual
          ].where((f) => f).length;
          expect(n, 1, reason: '$x vs $y');
        }
      }
    });
  });

  group('malformed — fail closed (doctrine F2 áp nguyên)', () {
    test('rỗng, hai dấu phẩy, ký tự lạ, dấu chấm Anh-Mỹ, phẩy cụt ⇒ null', () {
      for (final bad in ['', '3,5,2', 'abc', '3.5', '5,']) {
        expect(analyzeDecimalComparison(bad, '2,5'), isNull, reason: '"$bad"');
        expect(analyzeDecimalComparison('2,5', bad), isNull);
      }
    });
  });

  group('⭐⭐ bất biến F1 TỔNG QUÁT HOÁ sang khái niệm #2', () {
    test('vững ①② nhưng ca ④ CHƯA quan sát ⇒ không bao giờ "mastered"', () {
      const p = BktParams.freeResponse;
      CaseMastery drill(String id, int n) {
        var c = CaseMastery.initial(id, p);
        for (var i = 0; i < n; i++) {
          c = c.observeWithSupport(true, p, at: DateTime(2026, 9, 1));
        }
        return c;
      }

      final summary = ConceptSummary.of(
        ConceptMastery(conceptId: 'so-sanh-so-thap-phan', cases: {
          'integer-part-differs': drill('integer-part-differs', 3),
          'fraction-digit-differs': drill('fraction-digit-differs', 3),
        }),
        knownCaseIds: {
          'integer-part-differs',
          'fraction-digit-differs',
          'unequal-decimal-length',
          'all-parts-equal',
        },
        now: DateTime(2026, 9, 1, 12),
      );
      expect(summary.claim, ConceptClaim.strongOnObserved,
          reason: '⭐⭐ cùng một chốt F1, khái niệm KHÁC, không sửa một dòng '
              'schema nào — đây chính là điều WAL-36 cần chứng minh: '
              'abstraction SkillCase + ConceptSummary tái dùng nguyên vẹn');
      expect(summary.unobservedCases,
          ['all-parts-equal', 'unequal-decimal-length']);
    });
  });
}
