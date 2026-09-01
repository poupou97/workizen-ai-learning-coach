/// ⭐⭐⭐ PHASE 16 — CỐ Ý PHÁ KIẾN TRÚC.
///
/// Kiến trúc sống sót qua phép thử đáng giá hơn kiến trúc tích thêm tính năng.
/// Mỗi test dưới đây được viết để **thất bại** trên mã hiện tại. Nếu nó xanh
/// ngay lần đầu thì hoặc lỗ hổng không có thật, hoặc có lớp chắn thứ hai chưa
/// biết — phải phân biệt trước khi kết luận (§4.5).
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/adaptive/adaptive_engine.dart';
import 'package:learning_coach/core/curriculum/pedagogical_boundary.dart';
import 'package:learning_coach/core/curriculum/skill_case.dart';
import 'package:learning_coach/core/student/mastery.dart';

void main() {
  const concept = 'quy-dong';
  const div = 'denominator-divisible';
  const nonDiv = 'denominator-non-divisible';
  const p = BktParams.freeResponse;

  CaseMastery drill(String id, int n, {bool correct = true}) {
    var c = CaseMastery.initial(id, p);
    for (var i = 0; i < n; i++) {
      c = c.observe(correct, p);
    }
    return c;
  }

  group('F1 · mastery công bố VƯỢT bằng chứng', () {
    test('⭐⭐ KHÔNG được báo "mastered" khi còn ca CHƯA TỪNG GẶP', () {
      // Ba ca. Học sinh luyện kỹ hai ca, ca thứ ba chưa gặp lần nào.
      final m = ConceptMastery(conceptId: concept, cases: {
        div: drill(div, 10),
        nonDiv: drill(nonDiv, 10),
        'denominator-equal': CaseMastery.initial('denominator-equal', p),
      });

      expect(m.stateAt(), isNot(MasteryState.mastered),
          reason: '⭐⭐ `min` được chọn với lý do "mean giấu một ca hỏng sau một '
              'ca vững". Nhưng `min` chỉ chạy trên các ca CÓ bằng chứng — nó '
              'giấu trọn ca CHƯA GẶP. Nói với phụ huynh "con đã nắm vững quy '
              'đồng" trong khi một phần ba khái niệm chưa từng được hỏi là công '
              'bố vượt bằng chứng. Đúng thứ ADR-001 nói đang cố tránh.');
    });

    test('có ca chưa gặp ⇒ phải phân biệt được với "đã phủ hết ca"', () {
      final covered = ConceptMastery(conceptId: concept, cases: {
        div: drill(div, 10),
        nonDiv: drill(nonDiv, 10),
      });
      final partial = ConceptMastery(conceptId: concept, cases: {
        div: drill(div, 10),
        nonDiv: drill(nonDiv, 10),
        'denominator-equal': CaseMastery.initial('denominator-equal', p),
      });
      expect(covered.stateAt(), isNot(partial.stateAt()),
          reason: '⭐ Hai tình huống khác nhau về chất — "đã kiểm hết ca" và '
              '"còn ca chưa hỏi" — mà cho cùng một kết luận thì kết luận đó '
              'không mang thông tin.');
    });
  });

  group('F2 · phương pháp SAI VỀ TOÁN HỌC vẫn tới tay Tutor', () {
    test('⭐⭐ cùng mẫu số KHÔNG phải ca "chia hết" — nó không cần quy đồng', () {
      expect(fractionCase(5, 5), isNot(div),
          reason: '⭐⭐ `5 % 5 == 0` nên hàm xếp `3/5 + 1/5` vào ca "chia hết", '
              'rồi Tutor nhận phương pháp "lấy mẫu số lớn hơn". Nhưng bài này '
              'KHÔNG CÓ bước quy đồng nào cả — hai mẫu đã bằng nhau. Đây đúng '
              'ca PHASE 16 gọi tên: pedagogically available nhưng mathematically '
              'inapplicable. Bất biến P0 nói phải chặn, mà nó lọt.');
    });

    test('⭐ ca cùng mẫu số phải nhận diện được, không im lặng gộp', () {
      expect(fractionCase(5, 5), 'denominator-equal',
          reason: 'Sách dạy cộng cùng mẫu số TRƯỚC khi dạy quy đồng. Đó là một '
              'ca riêng có thật trong chương trình, không phải biến thể của ca '
              'chia hết.');
    });
  });

  group('F3 · gợi ý của Tutor làm nhiễu chính bằng chứng', () {
    test('⭐⭐ đúng SAU KHI được gợi ý không được tính như đúng tự làm', () {
      final unaided = drill(div, 4);
      var afterHints = CaseMastery.initial(div, p);
      for (var i = 0; i < 4; i++) {
        afterHints = afterHints
            .observeWithSupport(true, p, support: SupportLevel.fullSolution);
      }
      expect(afterHints.pMastery, lessThan(unaided.pMastery),
          reason: '⭐⭐ Vòng lặp tự xác nhận: Tutor gợi ý → trẻ làm đúng → '
              'mastery tăng → engine kết luận trẻ đã vững → thôi gợi ý. Bằng '
              'chứng do chính can thiệp sinh ra bị tính như bằng chứng độc lập.');
    });

    test('⭐ được đọc luôn lời giải thì KHÔNG phải bằng chứng về mastery', () {
      final c = CaseMastery.initial(div, p)
          .observeWithSupport(true, p, support: SupportLevel.fullSolution);
      expect(c.pMastery, lessThanOrEqualTo(p.prior),
          reason: 'Chép lại lời giải vừa đọc không chứng minh điều gì về việc '
              'trẻ tự làm được.');
      expect(c.hasEvidence, isFalse,
          reason: '⭐ Lần làm có hỗ trợ KHÔNG được vào evidenceCount — nếu vào, '
              'nó nhuộm luôn `derived` và `caseBreakdown`.');
      expect(c.supportedCount, 1,
          reason: 'Vẫn phải đếm được là trẻ đã luyện, chỉ là đếm riêng.');
    });

    test('⭐ gợi ý nhẹ: cho công LỌC HỌC được, không cho công TRẢ LỜI ĐÚNG', () {
      final hinted = CaseMastery.initial(div, p)
          .observeWithSupport(true, p, support: SupportLevel.hint);
      final unaided = CaseMastery.initial(div, p).observe(true, p);
      expect(hinted.pMastery, greaterThan(p.prior),
          reason: 'Có dạy thì có khả năng đã học được — số hạng `learn` vẫn áp.');
      expect(hinted.pMastery, lessThan(unaided.pMastery),
          reason: '⭐ nhưng phải THẤP HƠN tự làm đúng, nếu không thì gợi ý vẫn '
              'là con đường tắt để thổi mastery lên.');
    });
  });


  group('F4 · lý do hiển thị cho phụ huynh chọn ca TÙY TIỆN', () {
    const stage = LearningStage(
      grade: 5, bookSeries: 'kntt', lessonId: 'toan5-t1-bai6',
      conceptsIntroduced: {'phan-so'},
      methodsIntroduced: {'m-nondiv'},
      terminologyIntroduced: {'mẫu số chung'});
    const catalogue = [
      TeachingMethod(
          id: 'm-nondiv', name: 'tích hai mẫu',
          appliesToConcepts: {concept}, skillCaseId: nonDiv,
          requiresConcepts: {'phan-so'}, requiresTerminology: {'mẫu số chung'})
    ];
    // Ca có thật, kèm lớp được dạy — đo từ corpus KNTT.
    const cases = [
      SkillCase(id: 'denominator-equal', conceptId: concept,
          condition: 'hai mẫu số bằng nhau', introducedGrade: 4),
      SkillCase(id: div, conceptId: concept,
          condition: 'một mẫu chia hết cho mẫu kia', introducedGrade: 4),
      SkillCase(id: nonDiv, conceptId: concept,
          condition: 'hai mẫu không chia hết cho nhau', introducedGrade: 5),
    ];

    test('⭐ nêu ca được dạy GẦN NHẤT TRƯỚC ca đang vướng, không phải ca đầu map', () {
      final m = ConceptMastery(conceptId: concept, cases: {
        'ca-khong-lien-quan': drill('ca-khong-lien-quan', 10),
        div: drill(div, 10),
        nonDiv: CaseMastery.initial(nonDiv, p),
      });
      final d = decide(
          conceptId: concept, exerciseCase: nonDiv, mastery: m, stage: stage,
          catalogue: catalogue, caseCatalogue: cases);
      expect(d.diagnosis, DiagnosticOutcome.caseTransitionGap);
      expect(d.reason, contains(div),
          reason: '⭐ Ca lớp 4 "chia hết" mới là ca mà luật ĐỔI so với nó. '
              '"ca-khong-lien-quan" không có trong catalogue nên không được nêu.');
      expect(d.reason, isNot(contains('ca-khong-lien-quan')));
    });

    test('⭐⭐ THỨ TỰ CHÈN MAP không được đổi câu nói với phụ huynh', () {
      ConceptMastery build(List<String> order) => ConceptMastery(
          conceptId: concept,
          cases: {
            for (final id in order)
              id: id == nonDiv
                  ? CaseMastery.initial(nonDiv, p)
                  : drill(id, 10),
          });
      String reasonFor(List<String> order) => decide(
          conceptId: concept, exerciseCase: nonDiv, mastery: build(order),
          stage: stage, catalogue: catalogue).reason;

      // KHÔNG truyền caseCatalogue ⇒ ép chạy nhánh dự phòng.
      expect(reasonFor(['zzz-ca-khac', div, nonDiv]),
             reasonFor([div, 'zzz-ca-khac', nonDiv]),
          reason: '⭐⭐ Đây là chốt bắt đúng lỗi gốc: cùng bằng chứng, khác thứ '
              'tự chèn, phải cho CÙNG một câu. Nhánh dự phòng xếp theo số bằng '
              'chứng rồi theo id — tất định, không theo thứ tự Map.');
    });
  });
}
