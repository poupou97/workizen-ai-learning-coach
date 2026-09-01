/// ⭐⭐⭐ F1 — CHỐT VÀNG ConceptSummary (Founder Decisions 1 & 2, 2026-09-01).
///
/// Mười kịch bản dưới đây là DANH SÁCH CỦA FOUNDER, không phải của agent.
/// Bất biến trung tâm:  MASTERY ước lượng cao ≠ COVERAGE đủ ≠ CONFIDENCE cao.
/// Và: nếu bằng chứng không đỡ nổi chữ "mastered" thì KHÔNG nói "mastered".
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/student/concept_summary.dart';
import 'package:learning_coach/core/student/evidence_weighting.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/mastery.dart';

void main() {
  const p = BktParams.freeResponse;
  const concept = 'quy-dong';
  const eq = 'denominator-equal';
  const div = 'denominator-divisible';
  const nonDiv = 'denominator-non-divisible';
  final now = DateTime(2026, 9, 1, 20);

  var seq = 0;
  CaseMastery drill(
    String id, {
    required List<bool> answers,
    Duration age = const Duration(days: 1),
    List<EvidenceKind>? kinds,
  }) {
    var log = EvidenceLog.empty(id);
    for (var i = 0; i < answers.length; i++) {
      final kind = kinds?[i] ?? EvidenceKind.independentAttempt;
      if (kind == EvidenceKind.postHintSuccess) {
        log = log.append(LearningEvent(
            eventId: 'h${seq++}', skillCaseId: id,
            kind: EvidenceKind.hintShown, at: now.subtract(age)));
      }
      log = log.append(LearningEvent(
        eventId: 'e${seq++}',
        skillCaseId: id,
        kind: kind,
        correct: answers[i],
        at: now.subtract(age).add(Duration(minutes: i)),
      ));
    }
    return replayMastery(log, p);
  }

  ConceptSummary sum(Map<String, CaseMastery> cases, Set<String> known) =>
      ConceptSummary.of(ConceptMastery(conceptId: concept, cases: cases),
          knownCaseIds: known, now: now);

  group('mười kịch bản Founder', () {
    test('① hai ca mạnh + một ca CHƯA QUAN SÁT ⇒ KHÔNG BAO GIỜ mastered', () {
      final s = sum({
        div: drill(div, answers: [true, true, true]),
        nonDiv: drill(nonDiv, answers: [true, true, true]),
      }, {div, nonDiv, eq});
      expect(s.claim, ConceptClaim.strongOnObserved,
          reason: '⭐⭐ BẤT BIẾN Decision 1: ca đã quan sát mạnh đến đâu cũng '
              'không kéo được ca CHƯA quan sát thành "đã vững"');
      expect(s.claim, isNot(ConceptClaim.mastered));
      expect(s.unobservedCases, [eq],
          reason: 'ca chưa hỏi phải được NÓI RA, không giấu');
      expect(s.coverage.isComplete, isFalse);
      expect(s.confidence, greaterThanOrEqualTo(0.6),
          reason: '⭐ confidence CAO là đúng — bằng chứng đã có rất tốt. '
              'Chặn nằm ở COVERAGE. Hai trục không được trộn.');
    });

    test('② mọi ca đã quan sát và đều mạnh ⇒ mastered', () {
      final s = sum({
        div: drill(div, answers: [true, true, true]),
        nonDiv: drill(nonDiv, answers: [true, true, true]),
        eq: drill(eq, answers: [true, true]),
      }, {div, nonDiv, eq});
      expect(s.claim, ConceptClaim.mastered);
      expect(s.coverage.isComplete, isTrue);
      expect(s.unobservedCases, isEmpty);
    });

    test('③ một ca quan sát thấy YẾU ⇒ needsWork, nêu đúng ca', () {
      final s = sum({
        div: drill(div, answers: [true, true, true]),
        nonDiv: drill(nonDiv, answers: [false, false, false]),
      }, {div, nonDiv});
      expect(s.claim, ConceptClaim.needsWork);
      expect(s.weakestObservedCases, [nonDiv]);
    });

    test('④ bằng chứng TỰ MÂU THUẪN ⇒ không kết luận theo hướng nào', () {
      final s = sum({
        div: drill(div, answers: [true, false, true, false, true, false]),
      }, {div});
      expect(s.confidenceFactors.consistency, 0,
          reason: 'đúng/sai chia đôi hoàn hảo — thước đo mâu thuẫn không '
              'hằng số: |đúng − sai| / tổng');
      expect(s.claim, ConceptClaim.insufficientEvidence,
          reason: '⭐ kể cả báo động "needsWork" trên bằng chứng mâu thuẫn '
              'cũng là công bố vượt bằng chứng — chỉ theo hướng ngược lại');
    });

    test('⑤ bằng chứng CŨ ⇒ confidence sập dù mastery ước lượng còn cao', () {
      final s = sum({
        div: drill(div, answers: [true, true, true],
            age: const Duration(days: 200)),
      }, {div});
      expect(s.estimatedMastery, greaterThan(0.85),
          reason: 'ước lượng KHÔNG bị đụng — recency là trục confidence, '
              'không phải mô hình quên (F5 xử riêng, Founder tách hai thứ)');
      expect(s.confidenceFactors.recency, 0);
      expect(s.claim, ConceptClaim.insufficientEvidence,
          reason: '⭐ "con vững quy đồng" dựa trên bằng chứng 7 tháng trước '
              'là một câu nói không còn được bảo chứng');
    });

    test('⑥ bằng chứng THƯA (một lần mỗi ca) ⇒ chưa được claim vững', () {
      final s = sum({
        div: drill(div, answers: [true]),
        nonDiv: drill(nonDiv, answers: [true]),
      }, {div, nonDiv});
      expect(s.confidenceFactors.volume, 0.5,
          reason: 'chuẩn ≥2 suy từ chính mô hình: BKT khai slip > 0, tức MỘT '
              'lần đúng có thể là may — claim phải sống sót một lần trượt '
              'được mô hình thừa nhận');
      expect(s.claim, ConceptClaim.insufficientEvidence);
    });

    test('⑦ CHỈ toàn post-hint success ⇒ ca vẫn là CHƯA QUAN SÁT', () {
      final s = sum({
        div: drill(div,
            answers: [true, true, true, true],
            kinds: List.filled(4, EvidenceKind.postHintSuccess)),
      }, {div});
      expect(s.estimatedMastery, isNull,
          reason: '⭐⭐ F3 chặn F1 qua cửa sau: can thiệp đủ nhiều không được '
              'làm coverage tự "đầy"');
      expect(s.evidenceCount, 0);
      expect(s.supportedPracticeCount, 4,
          reason: 'nhưng KHÔNG vứt công luyện — Coach phải nói được "con '
              'đang luyện với gợi ý, chưa có bằng chứng tự làm"');
      expect(s.claim, ConceptClaim.insufficientEvidence);
      expect(s.unobservedCases, [div]);
    });

    test('⑧ tự làm đúng TRƯỚC khi có gợi ý ⇒ được tính trọn vẹn', () {
      final s = sum({
        div: drill(div, answers: [true, true, true]),
      }, {div});
      expect(s.claim, ConceptClaim.mastered);
      expect(s.evidenceCount, 3);
    });

    test('⑨ khái niệm chỉ có MỘT ca đã biết ⇒ coverage trọn với một ca', () {
      final s = sum({
        div: drill(div, answers: [true, true, true]),
      }, {div});
      expect(s.coverage.isComplete, isTrue);
      expect(s.coverage.knownCaseCount, 1);
      expect(s.claim, ConceptClaim.mastered,
          reason: 'claim "vững" ở đây nghĩa là vững TRONG PHẠM VI chương '
              'trình đã biết — danh mục ca chính là giới hạn của câu nói');
    });

    test('⑩ PHÁT HIỆN CA MỚI sau khi từng "mastered" ⇒ claim tự hạ', () {
      final cases = {
        div: drill(div, answers: [true, true, true]),
        nonDiv: drill(nonDiv, answers: [true, true, true]),
      };
      final before = sum(cases, {div, nonDiv});
      expect(before.claim, ConceptClaim.mastered);

      // Corpus khám phá ra ca thứ ba (vd đọc thêm SGV) — chỉ danh mục đổi.
      final after = sum(cases, {div, nonDiv, eq});
      expect(after.claim, ConceptClaim.strongOnObserved,
          reason: '⭐⭐ không có trạng thái "mastered" nào được LƯU để mà quên '
              'hạ — summary suy ra mỗi lần từ bằng chứng + danh mục hiện '
              'hành, nên tri thức mới về chương trình tự động hạ claim');
      expect(after.unobservedCases, [eq]);
    });
  });

  group('ADR-007 — pha loãng claim theo hỗ trợ (từ số đo WAL-87)', () {
    // ĐỐI CHỨNG: cùng 3 đúng độc lập/ca, KHÔNG hỗ trợ ⇒ mastered như cũ.
    // Chứng minh cú lật ở test dưới đến từ MỘT biến duy nhất: supportedCount.
    test('stream thuần độc lập: hành vi KHÔNG đổi (mastered)', () {
      final s = sum({
        div: drill(div, answers: [true, true, true]),
        nonDiv: drill(nonDiv, answers: [true, true, true]),
      }, {
        div, nonDiv
      });
      expect(s.claim, ConceptClaim.mastered);
    });

    test('stream nặng hỗ trợ: 3 độc lập + 16 có-hỗ-trợ ⇒ KHÔNG được claim vững',
        () {
      final heavy = drill(nonDiv,
          answers: [
            for (var i = 0; i < 16; i++) true, // 16 lần đúng-sau-gợi-ý
            true, true, true, // 3 lần độc lập
          ],
          kinds: [
            for (var i = 0; i < 16; i++) EvidenceKind.postHintSuccess,
            EvidenceKind.independentAttempt,
            EvidenceKind.independentAttempt,
            EvidenceKind.independentAttempt,
          ]);
      // cần = 2 + 16 ~/ 4 = 6 bằng chứng độc lập; mới có 3 ⇒ volume 0.5 < 0.6
      expect(heavy.supportedCount, 16);
      expect(heavy.evidenceCount, 3);
      final s = sum({
        div: drill(div, answers: [true, true, true]),
        nonDiv: heavy,
      }, {
        div, nonDiv
      });
      expect(s.claim, isNot(ConceptClaim.mastered),
          reason: 'mẫu độc lập thưa đang cõng cả kết luận — WAL-87 đo được '
              'FALSE TRUSTED 7–13%% ở đúng cấu hình stream này');
      expect(s.claim, ConceptClaim.insufficientEvidence,
          reason: 'không đủ tin thì không kết luận theo HƯỚNG nào');
    });

    test('đủ bù: 6 độc lập + 16 hỗ trợ ⇒ lại được claim', () {
      final earned = drill(nonDiv,
          answers: [for (var i = 0; i < 22; i++) true],
          kinds: [
            for (var i = 0; i < 16; i++) EvidenceKind.postHintSuccess,
            for (var i = 0; i < 6; i++) EvidenceKind.independentAttempt,
          ]);
      expect(earned.evidenceCount, 6);
      final s = sum({
        div: drill(div, answers: [true, true, true]),
        nonDiv: earned,
      }, {
        div, nonDiv
      });
      expect(s.claim, ConceptClaim.mastered,
          reason: 'dilution là RÀO CÓ THỂ VƯỢT bằng bằng chứng thật, '
              'không phải án chung thân cho trẻ cần nhiều gợi ý');
    });
  });

  group('bất biến ba trục', () {
    test('⭐⭐ MASTERY cao ≠ COVERAGE đủ ≠ CONFIDENCE cao — ba trục ĐỘC LẬP', () {
      // Cùng mastery ước lượng cao, ba tình huống khác nhau ở trục khác:
      final coverageGap = sum({
        div: drill(div, answers: [true, true, true]),
      }, {div, nonDiv});
      final staleGap = sum({
        div: drill(div, answers: [true, true, true],
            age: const Duration(days: 200)),
        nonDiv: drill(nonDiv, answers: [true, true, true],
            age: const Duration(days: 200)),
      }, {div, nonDiv});
      final complete = sum({
        div: drill(div, answers: [true, true, true]),
        nonDiv: drill(nonDiv, answers: [true, true, true]),
      }, {div, nonDiv});

      for (final s in [coverageGap, staleGap, complete]) {
        expect(s.estimatedMastery, greaterThan(0.85),
            reason: 'cả ba cùng mastery ước lượng cao');
      }
      expect(coverageGap.claim, ConceptClaim.strongOnObserved);
      expect(staleGap.claim, ConceptClaim.insufficientEvidence);
      expect(complete.claim, ConceptClaim.mastered);
      expect(coverageGap.confidence, greaterThanOrEqualTo(0.6),
          reason: 'thiếu coverage KHÔNG làm giảm confidence — hai trục khác nhau');
      expect(staleGap.coverage.isComplete, isTrue,
          reason: 'đủ coverage KHÔNG cứu được bằng chứng cũ — hai trục khác nhau');
    });

    test('chưa có sự kiện nào ⇒ noEvidence, mastery = null, KHÔNG PHẢI 0', () {
      final s = sum({}, {div, nonDiv});
      expect(s.claim, ConceptClaim.noEvidence);
      expect(s.estimatedMastery, isNull);
      expect(s.unobservedCases, [div, nonDiv]);
    });

    test('⭐ ca yếu nhất KHÔNG phân giải được ⇒ nêu cả nhóm, sort tất định', () {
      // Hai ca cùng hồ sơ bằng chứng ⇒ cùng pMastery ⇒ trong epsilon.
      final s = sum({
        nonDiv: drill(nonDiv, answers: [false, false]),
        div: drill(div, answers: [false, false]),
      }, {div, nonDiv});
      expect(s.weakestObservedCases, [div, nonDiv],
          reason: '⭐ Decision 5: bằng chứng không chọn được MỘT ca thì nói '
              'cả nhóm — không bịa một thứ tự từ thứ tự chèn Map');
    });

    test('thứ tự chèn Map KHÔNG đổi bất kỳ trường nào của summary', () {
      Map<String, CaseMastery> build(List<String> order) => {
            for (final id in order)
              id: drill(id, answers: id == nonDiv ? [false, false] : [true, true]),
          };
      final a = sum(build([div, nonDiv, eq]), {div, nonDiv, eq});
      final b = sum(build([eq, nonDiv, div]), {div, nonDiv, eq});
      expect(a.claim, b.claim);
      expect(a.weakestObservedCases, b.weakestObservedCases);
      expect(a.unobservedCases, b.unobservedCases);
      expect(a.estimatedMastery, b.estimatedMastery);
    });
  });
}
