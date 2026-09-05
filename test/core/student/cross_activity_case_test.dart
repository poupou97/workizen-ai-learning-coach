/// FOUNDER DELTA §5 — ca liên-kết-câu (TV5-t2 b9: bài 3 «Tìm từ ngữ được lặp
/// lại» = NHẬN BIẾT; bài 4 «Viết 2-3 câu…liên kết bằng lặp từ» = DÙNG KHI VIẾT).
/// Câu hỏi của lệnh: kiến trúc có nghiền hai demand này thành MỘT mastery không?
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/student/concept_summary.dart';
import 'package:learning_coach/core/student/evidence_validation.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/evidence_weighting.dart';
import 'package:learning_coach/core/student/mastery.dart';

/// ROUND 4 (strict default): sự kiện CÓ CHẤM trong test này mô phỏng đường
/// Deep (TutorSession) — mang dấu `fraction-check-v1` như emitter thật.
const _r4Stamp =
    EvidenceValidation(validatorId: 'fraction-check-v1', validatorVersion: '1');

void main() {
  const p = BktParams.freeResponse;
  final now = DateTime(2026, 9, 1, 20);

  CaseMastery drill(String id, int n) {
    var log = EvidenceLog.empty(id);
    for (var i = 0; i < n; i++) {
      log = log.append(LearningEvent(
          eventId: '$id:$i', skillCaseId: id,
          kind: EvidenceKind.independentAttempt, correct: true,
          validation: _r4Stamp,
          at: now.subtract(Duration(days: 1, minutes: -i))));
    }
    return replayMastery(log, p);
  }

  test('⭐ nhận-biết vững + dùng-khi-viết CHƯA quan sát ⇒ KHÔNG BAO GIỜ '
      '«vững liên kết câu» — không có collapse-gap', () {
    // hai demand = hai SkillCase dưới cùng concept — cơ chế hiện có chứa được
    final m = ConceptMastery(conceptId: 'lien-ket-cau', cases: {
      'lkc-nhan-biet-lap-tu': drill('lkc-nhan-biet-lap-tu', 3),
      // 'lkc-dung-khi-viet' CHƯA có bằng chứng nào
    });
    final s = ConceptSummary.of(m,
        knownCaseIds: {'lkc-nhan-biet-lap-tu', 'lkc-dung-khi-viet'}, now: now);
    expect(s.claim, isNot(ConceptClaim.mastered),
        reason: 'F1/coverage: demand chưa quan sát chặn claim — '
            'recognize KHÔNG nuốt apply');
    expect(s.claim, ConceptClaim.strongOnObserved);
    expect(s.unobservedCases, ['lkc-dung-khi-viet'],
        reason: 'nói được ĐÍCH DANH demand còn thiếu — đúng thứ Parent Coach cần');
  });

  test('cả hai demand có bằng chứng riêng ⇒ claim tách theo từng case, '
      'không một-số-cho-cả-concept', () {
    final m = ConceptMastery(conceptId: 'lien-ket-cau', cases: {
      'lkc-nhan-biet-lap-tu': drill('lkc-nhan-biet-lap-tu', 3),
      'lkc-dung-khi-viet': drill('lkc-dung-khi-viet', 3),
    });
    final s = ConceptSummary.of(m,
        knownCaseIds: {'lkc-nhan-biet-lap-tu', 'lkc-dung-khi-viet'}, now: now);
    expect(s.claim, ConceptClaim.mastered,
        reason: 'đủ coverage cả hai demand mới được nói vững');
  });
}
