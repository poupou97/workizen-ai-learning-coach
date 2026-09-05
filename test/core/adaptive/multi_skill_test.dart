/// ⭐⭐ F6 — Q-matrix: bài `3/4 + 2/5` và các cấu trúc đa kỹ năng khác.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/adaptive/multi_skill_diagnosis.dart';
import 'package:learning_coach/core/student/evidence_validation.dart';
import 'package:learning_coach/core/curriculum/exercise_skill_map.dart';
import 'package:learning_coach/core/curriculum/pedagogical_boundary.dart';
import 'package:learning_coach/core/curriculum/skill_case.dart';
import 'package:learning_coach/core/knowledge/provenance.dart';
import 'package:learning_coach/core/student/evidence_weighting.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/mastery.dart';

/// ROUND 4 (strict default): sự kiện CÓ CHẤM trong test này mô phỏng đường
/// Deep (TutorSession) — mang dấu `fraction-check-v1` như emitter thật.
const _r4Stamp =
    EvidenceValidation(validatorId: 'fraction-check-v1', validatorVersion: '1');

void main() {
  const p = BktParams.freeResponse;
  final at = DateTime(2026, 9, 1, 9);

  const prov = Provenance(
    origin: KnowledgeOrigin.systemDerived,
    sourceId: 'fraction-analyzer',
    extractionMethod: 'deterministic-parse',
    confidence: 1.0,
  );

  // ⭐ 3/4 + 2/5 — ví dụ của Founder: quy đồng (ca không chia hết) VÀ cộng
  // phân số khác mẫu.
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

  group('quy CÔNG khi đúng — conjunctive', () {
    test('⭐ đúng tự làm ⇒ MỖI thành phần một sự kiện chấm được, mang cả nhóm concept',
        () {
      final events = attributeEvidence(
          map: addUnlike, correct: true, independent: true, validation: _r4Stamp, at: at);
      expect(events.length, 2);
      for (final e in events) {
        expect(e.kind, EvidenceKind.independentAttempt);
        expect(e.conceptIds, ['cong-phan-so', 'quy-dong'],
            reason: 'EduStudio cpt_seq: sự kiện mang DANH SÁCH concept — '
                'schema sẵn cho mô hình KT/CD sau này');
      }
      final log = EvidenceLog(
          skillCaseId: 'denominator-non-divisible', events: [events.first]);
      expect(replayMastery(log, p).evidenceCount, 1,
          reason: 'đúng ⇒ mọi thành phần đã chạy ⇒ từng ca được công');
    });

    test('⭐ đúng SAU GỢI Ý ⇒ sự kiện postHintSuccess — F3 áp cả bài đa kỹ năng',
        () {
      final events = attributeEvidence(
          map: addUnlike, correct: true, independent: false, at: at);
      final log = EvidenceLog(
          skillCaseId: 'denominator-non-divisible', events: [events.first]);
      expect(replayMastery(log, p).evidenceCount, 0,
          reason: 'không có cửa sau: đa kỹ năng không miễn trừ luật bằng chứng');
    });

    test('⭐⭐ SAI ⇒ sự kiện ĐƯỢC GHI nhưng KHÔNG thành điểm trừ cho mọi thành phần',
        () {
      final events = attributeEvidence(
          map: addUnlike, correct: false, independent: true, at: at);
      expect(events.length, 2, reason: 'log thô vẫn đủ — F3: preserve raw events');
      for (final e in events) {
        expect(e.kind, EvidenceKind.finalCorrectness);
      }
      final log = EvidenceLog(
          skillCaseId: 'denominator-non-divisible', events: [events.first]);
      final m = replayMastery(log, p);
      expect(m.pMastery, p.prior,
          reason: '⭐⭐ chia lỗi đều khi sai = quy lỗi sai địa chỉ. Belief '
              'đứng yên; việc tìm thành phần hỏng là của attributeFailure.');
      expect(m.evidenceCount, 0);
    });
  });

  group('quy LỖI khi sai — luật loại trừ', () {
    test('① mọi thành phần vững ⇒ lỗi thực thi, không dạy lại gì', () {
      final d = attributeFailure(
        map: addUnlike,
        masteryByConcept: {
          'quy-dong': ConceptMastery(conceptId: 'quy-dong', cases: {
            'denominator-non-divisible':
                drill('denominator-non-divisible', [true, true, true]),
          }),
          'cong-phan-so': ConceptMastery(conceptId: 'cong-phan-so', cases: {
            'khac-mau-so': drill('khac-mau-so', [true, true, true]),
          }),
        },
        stage: stage,
        catalogue: catalogue,
      );
      expect(d.diagnosis, DiagnosticOutcome.executionError);
      expect(d.implicatedCases, isEmpty);
    });

    test('② đúng MỘT thành phần không vững ⇒ nghi phạm duy nhất, chẩn đoán sâu',
        () {
      final d = attributeFailure(
        map: addUnlike,
        masteryByConcept: {
          'quy-dong': ConceptMastery(conceptId: 'quy-dong', cases: {
            // vững ca lớp 4, CHƯA GẶP ca lớp 5 — golden scenario của repo
            'denominator-divisible':
                drill('denominator-divisible', [true, true, true]),
            'denominator-non-divisible':
                CaseMastery.initial('denominator-non-divisible', p),
          }),
          'cong-phan-so': ConceptMastery(conceptId: 'cong-phan-so', cases: {
            'khac-mau-so': drill('khac-mau-so', [true, true, true]),
          }),
        },
        stage: stage,
        catalogue: catalogue,
        caseCatalogue: const [
          SkillCase(id: 'denominator-divisible', conceptId: 'quy-dong',
              condition: 'chia hết', introducedGrade: 4),
          SkillCase(id: 'denominator-non-divisible', conceptId: 'quy-dong',
              condition: 'không chia hết', introducedGrade: 5),
        ],
      );
      expect(d.implicatedCases, ['denominator-non-divisible']);
      expect(d.diagnosis, DiagnosticOutcome.caseTransitionGap,
          reason: '⭐ tái dùng decide: em ấy vững ca lớp 4, bối rối vì luật '
              'đổi — KHÔNG phải hỏng quy đồng, càng không phải hỏng cộng '
              'phân số');
      expect(d.delegated, isNotNull);
      expect(d.reason, contains('1 kỹ năng con đã vững'));
    });

    test('⭐⭐ ③ HAI thành phần không vững ⇒ nói thật: chưa cô lập được', () {
      final d = attributeFailure(
        map: addUnlike,
        masteryByConcept: {
          'quy-dong': ConceptMastery(conceptId: 'quy-dong', cases: {
            'denominator-non-divisible':
                drill('denominator-non-divisible', [false, false]),
          }),
          // cong-phan-so: không có bằng chứng nào
        },
        stage: stage,
        catalogue: catalogue,
      );
      expect(d.diagnosis, DiagnosticOutcome.attributionUnresolved,
          reason: '⭐⭐ đây là biểu diễn ADR-003 §F6 nói là "không có cách '
              'nào" — sai nhưng chưa biết vì thành phần nào');
      expect(d.action, LearningAction.isolateSkills);
      expect(d.implicatedCases, ['denominator-non-divisible', 'khac-mau-so'],
          reason: 'sort tất định — doctrine F4');
      expect(d.delegated, isNull);
    });

    test('hàng Q-matrix rỗng ⇒ fail closed', () {
      final d = attributeFailure(
        map: const ExerciseSkillMap(exerciseId: 'x', requirements: []),
        masteryByConcept: const {},
        stage: stage,
        catalogue: catalogue,
      );
      expect(d.diagnosis, DiagnosticOutcome.insufficientEvidence);
    });

    test('cấu trúc KHÁC phân số: bài toán đố 3 thành phần, 2 chưa vững', () {
      // Founder: "test other structures" — toán đố lớp 5: đọc hiểu đề →
      // phép nhân số thập phân → đổi đơn vị đo.
      const wordProblem = ExerciseSkillMap(
        exerciseId: 'ex-toan-do-dien-tich',
        requirements: [
          SkillRequirement(conceptId: 'doc-hieu-de',
              skillCaseId: 'de-hai-buoc', provenance: prov),
          SkillRequirement(conceptId: 'nhan-thap-phan',
              skillCaseId: 'nhan-hai-chu-so', provenance: prov),
          SkillRequirement(conceptId: 'doi-don-vi',
              skillCaseId: 'm2-sang-ha', provenance: prov),
        ],
      );
      final d = attributeFailure(
        map: wordProblem,
        masteryByConcept: {
          'nhan-thap-phan': ConceptMastery(conceptId: 'nhan-thap-phan', cases: {
            'nhan-hai-chu-so': drill('nhan-hai-chu-so', [true, true, true]),
          }),
        },
        stage: stage,
        catalogue: catalogue,
      );
      expect(d.diagnosis, DiagnosticOutcome.attributionUnresolved);
      expect(d.implicatedCases, ['de-hai-buoc', 'm2-sang-ha']);
      expect(d.reason, contains('3 kỹ năng'));
    });

    test('actionFor vét cạn: outcome mới có can thiệp tương ứng', () {
      expect(actionFor(DiagnosticOutcome.attributionUnresolved),
          LearningAction.isolateSkills);
    });
  });
}
