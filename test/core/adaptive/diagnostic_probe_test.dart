/// WAL-70 — vòng khép kín: bất định → probe → trả lời → chẩn đoán tốt hơn
/// → can thiệp. Mỗi test hỏi một câu trả-lời-sai-được.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/adaptive/diagnostic_probe.dart';
import 'package:learning_coach/core/adaptive/multi_skill_diagnosis.dart';
import 'package:learning_coach/core/curriculum/exercise_skill_map.dart';
import 'package:learning_coach/core/curriculum/pedagogical_boundary.dart';
import 'package:learning_coach/core/curriculum/skill_case.dart';
import 'package:learning_coach/core/knowledge/provenance.dart';
import 'package:learning_coach/core/student/mastery.dart';

void main() {
  const p = BktParams.freeResponse;
  final at = DateTime(2026, 9, 1, 9);

  const prov = Provenance(
    origin: KnowledgeOrigin.systemDerived,
    sourceId: 'fraction-analyzer',
    extractionMethod: 'deterministic-parse',
    confidence: 1.0,
  );

  const addUnlike = ExerciseSkillMap(
    exerciseId: 'ex-3/4+2/5',
    requirements: [
      SkillRequirement(
          conceptId: 'quy-dong',
          skillCaseId: 'denominator-non-divisible',
          provenance: prov),
      SkillRequirement(
          conceptId: 'cong-phan-so',
          skillCaseId: 'khac-mau-so',
          provenance: prov),
    ],
  );

  // pool: mỗi nghi phạm có MỘT bài cô lập + một bài đa-kỹ-năng gây nhiễu
  const pool = [
    addUnlike, // đa kỹ năng — không bao giờ được chọn làm probe
    ExerciseSkillMap(exerciseId: 'probe-quy-dong', requirements: [
      SkillRequirement(
          conceptId: 'quy-dong',
          skillCaseId: 'denominator-non-divisible',
          provenance: prov),
    ]),
    ExerciseSkillMap(exerciseId: 'probe-cong', requirements: [
      SkillRequirement(
          conceptId: 'cong-phan-so',
          skillCaseId: 'khac-mau-so',
          provenance: prov),
    ]),
  ];

  const cases = [
    SkillCase(id: 'denominator-non-divisible', conceptId: 'quy-dong',
        condition: 'hai mẫu không chia hết', introducedGrade: 5),
    SkillCase(id: 'khac-mau-so', conceptId: 'cong-phan-so',
        condition: 'cộng khác mẫu', introducedGrade: 4),
  ];

  const stage = LearningStage(
    grade: 5, bookSeries: 'kntt', lessonId: 'toan5-t1-bai6',
    conceptsIntroduced: {'phan-so'},
    methodsIntroduced: {'m-nondiv'},
    terminologyIntroduced: {'mẫu số chung'},
  );
  const catalogue = [
    TeachingMethod(
        id: 'm-nondiv', name: 'tích hai mẫu',
        appliesToConcepts: {'quy-dong'},
        skillCaseId: 'denominator-non-divisible',
        requiresConcepts: {'phan-so'}, requiresTerminology: {'mẫu số chung'}),
  ];

  CaseMastery drill(String id, List<bool> answers) {
    var c = CaseMastery.initial(id, p);
    for (final a in answers) {
      c = c.observeWithSupport(a, p, at: at);
    }
    return c;
  }

  Map<String, ConceptMastery> mastery({
    List<bool> quyDong = const [],
    List<bool> cong = const [],
  }) =>
      {
        'quy-dong': ConceptMastery(conceptId: 'quy-dong', cases: {
          'denominator-non-divisible':
              drill('denominator-non-divisible', quyDong),
        }),
        'cong-phan-so': ConceptMastery(conceptId: 'cong-phan-so', cases: {
          'khac-mau-so': drill('khac-mau-so', cong),
        }),
      };

  MultiSkillDecision diagnose(Map<String, ConceptMastery> m) =>
      attributeFailure(
          map: addUnlike, masteryByConcept: m, stage: stage,
          catalogue: catalogue, caseCatalogue: cases);

  test('⭐ VÒNG KHÉP KÍN: bất định → probe → trả lời → cô lập → can thiệp', () {
    // hai nghi phạm, chưa ca nào có bằng chứng ⇒ chưa cô lập được
    var m = mastery();
    final d0 = diagnose(m);
    expect(d0.diagnosis, DiagnosticOutcome.attributionUnresolved);

    // probe được chọn — bài ĐƠN kỹ năng, có lý do đọc được
    final probe = nextProbe(d0,
        exercisePool: pool, masteryByConcept: m, caseCatalogue: cases);
    expect(probe, isNotNull);
    expect(probe!.exerciseId, startsWith('probe-'));

    // trẻ trả lời probe ĐÚNG 3 lần (ca được probe thành vững)…
    m = probe.skillCaseId == 'khac-mau-so'
        ? mastery(cong: [true, true, true])
        : mastery(quyDong: [true, true, true]);

    // …chẩn đoán lại: còn MỘT nghi phạm ⇒ có quyết định dạy uỷ quyền
    final d1 = diagnose(m);
    expect(d1.diagnosis, isNot(DiagnosticOutcome.attributionUnresolved),
        reason: 'thông tin từ probe phải LÀM TỐT chẩn đoán');
    expect(d1.implicatedCases.length, 1);
    expect(d1.implicatedCases.single, isNot(probe.skillCaseId));
    expect(d1.delegated, isNotNull,
        reason: 'cô lập xong phải dẫn tới CAN THIỆP, không dừng ở chẩn đoán');
  });

  test('thứ tự probe: ít bằng chứng nhất trước; hoà ⇒ lớp dạy sớm hơn trước',
      () {
    // quy-dong có 1 bằng chứng, cong chưa có ⇒ probe cong trước
    var m = mastery(quyDong: [false]);
    var d = diagnose(m);
    var probe = nextProbe(d,
        exercisePool: pool, masteryByConcept: m, caseCatalogue: cases);
    expect(probe!.skillCaseId, 'khac-mau-so');

    // hoà bằng chứng (0–0) ⇒ ca lớp 4 (móng) đi trước ca lớp 5
    m = mastery();
    d = diagnose(m);
    probe = nextProbe(d,
        exercisePool: pool, masteryByConcept: m, caseCatalogue: cases);
    expect(probe!.skillCaseId, 'khac-mau-so',
        reason: 'introducedGrade 4 < 5 — kiểm móng trước (model tracing)');
  });

  test('probe trả lời SAI: nghi phạm xác nhận yếu, vòng vẫn tiến bộ', () {
    // probe cong 2 lần đều sai ⇒ cong yếu rõ; quy-dong vẫn 0 bằng chứng
    final m = mastery(cong: [false, false]);
    final d = diagnose(m);
    // vẫn 2 nghi phạm (cả hai chưa vững) — nhưng probe kế phải nhắm ca CHƯA hỏi
    expect(d.diagnosis, DiagnosticOutcome.attributionUnresolved);
    final probe = nextProbe(d,
        exercisePool: pool, masteryByConcept: m, caseCatalogue: cases);
    expect(probe!.skillCaseId, 'denominator-non-divisible',
        reason: 'ca đã probe có bằng chứng rồi — bất định giờ nằm ở ca kia');
  });

  test('fail closed: không có bài cô lập ⇒ null, KHÔNG đoán ca để dạy', () {
    final m = mastery();
    final d = diagnose(m);
    final probe = nextProbe(d,
        exercisePool: const [addUnlike], // pool chỉ có bài đa kỹ năng
        masteryByConcept: m,
        caseCatalogue: cases);
    expect(probe, isNull);
    expect(d.diagnosis, DiagnosticOutcome.attributionUnresolved,
        reason: 'không probe được thì GIỮ bất định — quy lỗi sai địa chỉ '
            'tệ hơn không quy lỗi');
  });

  test('không phải attributionUnresolved ⇒ không probe (dạy luôn)', () {
    // một nghi phạm duy nhất ⇒ delegated teaching, probe từ chối hoạt động
    final m = mastery(quyDong: [true, true, true]);
    final d = diagnose(m);
    expect(d.implicatedCases.length, 1);
    expect(
        nextProbe(d,
            exercisePool: pool, masteryByConcept: m, caseCatalogue: cases),
        isNull,
        reason: 'đã cô lập được thì DẠY, đừng hỏi thêm — probe chỉ để mua '
            'thông tin còn thiếu');
  });
}
