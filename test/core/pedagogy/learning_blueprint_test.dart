/// WAL-129 — blueprint là HỢP ĐỒNG KIỂM ĐƯỢC: drive phiên thật + bắt vi phạm.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/adaptive/adaptive_engine.dart';
import 'package:learning_coach/core/curriculum/pedagogical_boundary.dart';
import 'package:learning_coach/core/pedagogy/blueprint_catalogue_v0.dart';
import 'package:learning_coach/core/pedagogy/learning_blueprint.dart';
import 'package:learning_coach/core/pedagogy/pedagogy_model.dart';
import 'package:learning_coach/core/pedagogy/source_misconception.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/features/tutor/tutor_session.dart';
import '../../support/curriculum.dart';

void main() {
  group('catalogue v0 — 8 blueprint, 5 family, nguồn đầy đủ', () {
    test('đủ 5 subject family và mọi blueprint có (doc, trang)', () {
      expect(blueprintCatalogueV0, hasLength(8));
      final fams = blueprintCatalogueV0.map((b) => b.subject).toSet();
      expect(
          fams,
          containsAll(
              ['Toán', 'Tiếng Việt', 'Lịch sử', 'Khoa học', 'Tiếng Anh']));
      for (final b in blueprintCatalogueV0) {
        expect(b.source.sourceDocumentId, isNotNull, reason: b.blueprintId);
        expect(b.source.page, isNotNull, reason: b.blueprintId);
        expect(b.sequence, isNotEmpty, reason: b.blueprintId);
        expect(b.evidenceRequired, contains(EvidenceKind.independentAttempt),
            reason: '${b.blueprintId}: phiên đạt phải có lần TỰ LÀM');
      }
    });

    test('KHÔNG một sequence chung (F2/F3): ≥4 chuỗi intent khác nhau', () {
      final seqs = blueprintCatalogueV0
          .map((b) => b.sequence.map((s) => s.intent.name).join('→'))
          .toSet();
      expect(seqs.length, greaterThanOrEqualTo(4),
          reason: 'các blueprint không được rập một khuôn');
    });

    test('misconceptionIds trỏ vào seed có thật — không mồ côi', () {
      final known = sourceMisconceptionSeedV0.map((m) => m.id).toSet();
      for (final b in blueprintCatalogueV0) {
        for (final id in b.misconceptionIds) {
          expect(known, contains(id), reason: b.blueprintId);
        }
      }
    });

    test('Sử: không có act reveal nào — SAM không kết luận hộ từ sử liệu', () {
      for (final s in blueprintSu10SuLieu.sequence) {
        expect(s.allowedActs, isNot(contains(TeachingAct.revealAnswer)));
        expect(s.allowedActs, isNot(contains(TeachingAct.workedExample)));
      }
      expect(rungToSupport(blueprintSu10SuLieu.assistanceCap).index,
          lessThan(SupportLevel.workedStep.index));
    });
  });

  group('⭐ blueprint DRIVE phiên TutorSession THẬT (Toán 5 B6)', () {
    TutorSession run() {
      final c = toan5Bai6;
      final fp = FractionProblem.parse('3/4 + 2/5')!;
      final ec = fractionCase(fp.b, fp.d)!;
      return TutorSession(
          exerciseId: 'ex',
          skillCaseId: ec,
          problem: fp,
          scope:
              TutorScope.forProblem(c.conceptId, ec, c.stage, c.catalogue));
    }

    test('phiên sai→hint→đúng TUÂN THỦ blueprint (0 vi phạm)', () {
      final s = run();
      s.submit('1/2');
      s.requestHint();
      s.submit('23/20');
      expect(blueprintViolations(blueprintQuyDongB6, s.log), isEmpty);
    });

    test('phiên chỉ-xem-không-tự-làm ⇒ EVIDENCE_MISSING independentAttempt',
        () {
      final s = run();
      s.requestHint(); // xin hint ngay, chưa từng tự thử
      s.submit('23/20'); // đúng sau hint — KHÔNG có independentAttempt
      final v = blueprintViolations(blueprintQuyDongB6, s.log);
      expect(v.join(), contains('EVIDENCE_MISSING: independentAttempt'));
    });

    test('blueprint trần thấp (Sử) bắt được phiên vượt trần hỗ trợ', () {
      // Phiên Toán leo tới fullSolution — đối chiếu blueprint Sử (cap
      // strategicHint→hint) phải nổ ASSISTANCE_OVER_CAP.
      final s = run();
      s.submit('1/2'); // thử (mở REVEAL gate)
      s.requestHint(); // hint
      s.requestHint(); // workedStep
      s.requestHint(); // fullSolution
      final v = blueprintViolations(
          // đổi case-list để không nổ CASE_OUT trước — cô lập đúng luật cap
          LearningExperienceBlueprint(
            blueprintId: 'bp:test:cap',
            subject: 'Lịch sử',
            grade: 10,
            lessonId: 'x',
            conceptIds: const [],
            skillCaseIds: const ['denominator-non-divisible'],
            methodIds: const [],
            sequence: blueprintSu10SuLieu.sequence,
            assistanceCap: blueprintSu10SuLieu.assistanceCap,
            evidenceRequired: const [EvidenceKind.independentAttempt],
            source: blueprintSu10SuLieu.source,
          ),
          s.log);
      expect(v.any((x) => x.startsWith('ASSISTANCE_OVER_CAP')), isTrue);
    });

    test('phiên bỏ dở TRƯỚC khi trả lời: không bị đòi evidence (chưa vi phạm)',
        () {
      final s = run();
      s.requestHint(); // chỉ xin hint rồi thoát
      expect(
          blueprintViolations(blueprintQuyDongB6, s.log)
              .where((v) => v.startsWith('EVIDENCE_MISSING')),
          isEmpty);
    });

    test('case ngoài blueprint bị bắt — không dạy chéo hợp đồng', () {
      final s = run();
      s.submit('23/20');
      final v = blueprintViolations(blueprintTv1AmVan, s.log);
      expect(v.any((x) => x.startsWith('CASE_OUT_OF_BLUEPRINT')), isTrue);
    });
  });
}
