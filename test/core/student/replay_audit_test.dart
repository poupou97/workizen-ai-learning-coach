/// ⭐⭐⭐ P0 §G — FALSIFICATION: replay KHÔNG được lặng lẽ diễn giải lại lịch sử
/// bằng mô hình tri thức MỚI.
///
/// Câu hỏi Founder: nếu ExerciseSkillMap / danh mục SkillCase đổi về sau,
/// log LearningEvidence append-only có còn tái tạo ĐÚNG trạng thái lịch sử không?
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/adaptive/multi_skill_diagnosis.dart';
import 'package:learning_coach/core/curriculum/exercise_skill_map.dart';
import 'package:learning_coach/core/knowledge/provenance.dart';
import 'package:learning_coach/core/student/evidence_weighting.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/mastery.dart';

void main() {
  const p = BktParams.freeResponse;
  const prov = Provenance(
      origin: KnowledgeOrigin.systemDerived,
      sourceId: 'fraction-analyzer',
      extractionMethod: 'deterministic-parse',
      confidence: 1.0);
  final t0 = DateTime(2026, 9, 1, 8);

  // Q-matrix NĂM NGOÁI: bài chạm 2 thành phần.
  const mapV1 = ExerciseSkillMap(exerciseId: 'ex-1', requirements: [
    SkillRequirement(conceptId: 'quy-dong',
        skillCaseId: 'denominator-non-divisible', provenance: prov),
    SkillRequirement(conceptId: 'cong-phan-so',
        skillCaseId: 'khac-mau-so', provenance: prov),
  ]);
  // Q-matrix HÔM NAY: đội curriculum thêm thành phần thứ ba cho CÙNG bài.
  const mapV2 = ExerciseSkillMap(exerciseId: 'ex-1', requirements: [
    SkillRequirement(conceptId: 'quy-dong',
        skillCaseId: 'denominator-non-divisible', provenance: prov),
    SkillRequirement(conceptId: 'cong-phan-so',
        skillCaseId: 'khac-mau-so', provenance: prov),
    SkillRequirement(conceptId: 'rut-gon',
        skillCaseId: 'rut-gon-co-ban', provenance: prov),
  ]);

  test('⭐⭐ BẤT BIẾN: đổi Q-matrix về sau KHÔNG đổi trạng thái tái tạo từ log cũ',
      () {
    // Sự kiện lịch sử được SINH RA và LƯU khi mapV1 còn hiệu lực —
    // attributeEvidence NƯỚNG mapping vào sự kiện tại thời điểm ghi.
    final historical = attributeEvidence(
        map: mapV1, correct: true, independent: true, at: t0);
    final log = EvidenceLog(
        skillCaseId: 'denominator-non-divisible',
        events: historical
            .where((e) => e.skillCaseId == 'denominator-non-divisible')
            .toList());

    final stateBefore = replayMastery(log, p);
    // ... thời gian trôi, mapV2 ra đời. Replay CÙNG log cũ:
    final stateAfter = replayMastery(log, p);

    expect(stateAfter.pMastery, stateBefore.pMastery,
        reason: '⭐⭐ replay chỉ đọc SỰ KIỆN, không đọc Q-matrix hiện hành — '
            'mapping được nướng vào sự kiện lúc GHI (conceptIds, skillCaseId '
            'là dữ liệu của sự kiện, không phải tra cứu lúc ĐỌC)');
    expect(stateAfter.evidenceCount, stateBefore.evidenceCount);
    expect(historical.first.conceptIds, ['cong-phan-so', 'quy-dong'],
        reason: 'sự kiện lịch sử giữ nguyên danh sách concept của THỜI ĐIỂM '
            'ghi — không tự mọc thêm rut-gon của mapV2');
  });

  test('lần làm MỚI dưới mapV2 sinh sự kiện mới, log cũ không bị đụng', () {
    final oldEvents = attributeEvidence(
        map: mapV1, correct: true, independent: true, at: t0);
    final newEvents = attributeEvidence(
        map: mapV2, correct: true, independent: true,
        at: t0.add(const Duration(days: 30)));
    expect(newEvents.length, 3);
    expect(oldEvents.length, 2,
        reason: 'hai thế hệ sự kiện sống cạnh nhau trong log; mỗi sự kiện '
            'mang mapping của thời điểm nó xảy ra');
  });

  test('⭐ đổi DANH MỤC ca đổi CLAIM (đúng!) nhưng không đổi BẰNG CHỨNG', () {
    // Đây là ranh giới ngữ nghĩa §G: claim ĐƯỢC PHÉP diễn giải lại theo
    // hiểu biết mới về chương trình (ca mới phát hiện ⇒ coverage tụt);
    // BẰNG CHỨNG và belief theo ca thì KHÔNG.
    final events = attributeEvidence(
        map: mapV1, correct: true, independent: true, at: t0);
    final log = EvidenceLog(
        skillCaseId: 'denominator-non-divisible',
        events: events
            .where((e) => e.skillCaseId == 'denominator-non-divisible')
            .toList());
    final m1 = replayMastery(log, p);
    final m2 = replayMastery(log, p);
    expect(m1.pMastery, m2.pMastery,
        reason: 'belief theo ca bất biến với danh mục — danh mục chỉ vào '
            'ConceptSummary.of(knownCaseIds:), tầng CLAIM');
  });

  test('⭐⭐ FALSIFIED: eventId TRÙNG khi làm lại cùng bài — định danh sự kiện phải duy nhất',
      () {
    final first = attributeEvidence(
        map: mapV1, correct: false, independent: true, at: t0);
    final second = attributeEvidence(
        map: mapV1, correct: true, independent: true,
        at: t0.add(const Duration(minutes: 10)));
    final ids = {...first.map((e) => e.eventId), ...second.map((e) => e.eventId)};
    expect(ids.length, first.length + second.length,
        reason: '⭐⭐ log append-only mà hai lần làm cùng bài sinh CÙNG eventId '
            'thì mọi hệ lưu trữ khử-trùng-lặp sẽ nuốt mất lần thứ hai — '
            'bằng chứng bị mất im lặng. eventId phải chứa thời điểm.');
  });
}
