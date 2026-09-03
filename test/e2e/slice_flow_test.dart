/// ⭐⭐ WAL-108 — e2e KERNEL của First Vertical Slice (không widget):
/// curriculum guard → scope → tutor session → recordSession → kho →
/// mission «Hôm nay» đổi theo bằng chứng. Đúng vòng 17 bước, phần domain.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/adaptive/adaptive_engine.dart';
import 'package:learning_coach/core/curriculum/pedagogical_boundary.dart';
import 'package:learning_coach/core/knowledge/provenance.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/core/store/learning_session.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/core/tutor/teaching_provenance.dart';
import 'package:learning_coach/features/learning_session/slice_flow.dart';
import 'package:learning_coach/features/mission/mission_data.dart';
import 'package:learning_coach/features/shell/session_recorder.dart';
import 'package:learning_coach/features/tutor/tutor_session.dart';
import 'package:learning_coach/core/knowledge/slice_curriculum.dart';
import '../support/curriculum.dart';

const _p5 = LearnerProfile(learnerId: 'l-5', displayName: 'Minh', grade: 5);

void main() {
  group('CURRICULUM CONTEXT — fail closed theo ĐỊNH DANH BÀI', () {
    // WAL-170: trước đây fail-closed đo bằng LỚP («grade != 5 ⇒ null»), nghĩa
    // là mọi bài của trẻ lớp 5 đều nhận chương trình + provenance của Toán 5
    // Bài 6. Nay tra khớp ĐÚNG BÀI; lớp chỉ còn là bộ lọc của màn tình-hình-học.
    test('⭐⭐ bài KHÁC trong cùng cuốn KHÔNG mượn được chương trình Bài 6', () {
      expect(curriculumForLesson(toan5Bai6Key), isNotNull);
      for (final other in [
        const LessonKey(
            sourceDocumentId: '05-sgk-toan-5-tap-mot', number: 7, pageStart: 23),
        const LessonKey(
            sourceDocumentId: '05-sgk-khoa-hoc-5', number: 1, pageStart: 64),
        // đúng số bài, đúng sách, SAI trang in ⇒ vẫn là bài khác
        const LessonKey(
            sourceDocumentId: '05-sgk-toan-5-tap-mot', number: 6, pageStart: 99),
        // thiếu trang in ⇒ không đủ định danh ⇒ không khớp
        const LessonKey(sourceDocumentId: '05-sgk-toan-5-tap-mot', number: 6),
      ]) {
        expect(curriculumForLesson(other), isNull,
            reason: '⭐⭐ đột biến tra theo lớp/số bài ⇒ $other mượn được '
                'provenance trang 21 SGK Toán ⇒ đỏ');
      }
    });

    test('⭐ lớp khác ⇒ không có dòng chương trình nào', () {
      for (final g in [1, 2, 3, 4, 6, 9, 12]) {
        expect(
            curriculaForLearner(
                LearnerProfile(learnerId: 'x', displayName: 'X', grade: g)),
            isEmpty,
            reason: 'grade $g phải fail closed');
      }
      expect(curriculaForLearner(_p5), hasLength(1));
    });

    test('⭐ bài CHỤP ĐƯỢC: không dòng nào nhận ra đề ⇒ null, không mượn bừa',
        () {
      expect(curriculumForProblem(_p5, '1/2 + 1/3'), isNotNull);
      expect(curriculumForProblem(_p5, 'Quan sát cây đậu sau ba ngày'), isNull,
          reason: '⭐ đột biến trả dòng đầu tiên của lớp ⇒ đỏ');
    });

    test('provenance method từ corpus: sourceDemonstrated ⇒ «làm theo ví dụ», '
        'KHÔNG «sách nói rằng»', () {
      final c = toan5Bai6;
      final scope = TutorScope.forProblem(c.conceptId,
          'denominator-non-divisible', c.stage, c.catalogue);
      final tp = explainTeaching(
          scope: scope,
          methodId: 'common-denom-by-product',
          exerciseCase: 'denominator-non-divisible')!;
      expect(tp.authority, KnowledgeOrigin.sourceDemonstrated);
      expect(tp.sourceLineForChild, contains('làm theo ví dụ'));
      expect(tp.sourceLineForChild, contains('trang 21'));
      expect(tp.sourceLineForChild.contains('sách nói'), isFalse);
    });
  });

  group('§3 — BCNN không thể xuất hiện ở Math5 B6', () {
    test('mọi nấc hint của mọi method trong catalogue: không BCNN/bội chung',
        () {
      final c = toan5Bai6;
      final fp = FractionProblem.parse('3/4 + 2/5')!;
      for (final m in c.catalogue) {
        for (final level in SupportLevel.values) {
          final text = hintTextFor(m, level, fp).toLowerCase();
          expect(text.contains('bcnn'), isFalse,
              reason: '${m.id}@${level.name}');
          expect(text.contains('bội chung'), isFalse,
              reason: '${m.id}@${level.name}');
        }
      }
    });

    test('BCNN cũng không có mặt trong catalogue để mà lọt', () {
      final c = toan5Bai6;
      expect(
          c.catalogue.any((m) =>
              m.id.toLowerCase().contains('bcnn') ||
              m.name.toLowerCase().contains('bội chung')),
          isFalse);
    });
  });

  group('lineage — «exact hint identity» xuyên phiên (§3/§7)', () {
    TutorSession newSession() {
      final c = toan5Bai6;
      final fp = FractionProblem.parse('3/4 + 2/5')!;
      final exerciseCase = fractionCase(fp.b, fp.d)!;
      return TutorSession(
        exerciseId: 'ex-1',
        skillCaseId: exerciseCase,
        problem: fp,
        scope: TutorScope.forProblem(
            c.conceptId, exerciseCase, c.stage, c.catalogue),
      );
    }

    test('sai → hint → đúng: hintRequested VÀ postHintSuccess cùng mang '
        'đúng interventionId; independent = false', () {
      final s = newSession();
      expect(s.submit('1/2'), SubmitOutcome.wrong); // INDEPENDENT ATTEMPT
      s.requestHint(); // SMALL HINT
      expect(s.submit('23/20'), SubmitOutcome.supportedCorrect); // RESPONSE

      const wantId = 'tutor-session-v1/common-denom-by-product@hint';
      final hint = s.log.events
          .singleWhere((e) => e.kind == EvidenceKind.hintRequested);
      final success = s.log.events
          .singleWhere((e) => e.kind == EvidenceKind.postHintSuccess);
      expect(hint.interventionId, wantId);
      expect(success.interventionId, wantId,
          reason: '«đúng sau gợi ý NÀO» phải nằm trong dữ liệu');
      expect(s.outcome.independent, isFalse,
          reason: 'correct-after-hint = assisted (§3)');
      expect(s.outcome.correct, isTrue);

      // Sự kiện độc lập KHÔNG mang interventionId — không bôi lineage bừa.
      final indep = s.log.events
          .singleWhere((e) => e.kind == EvidenceKind.independentAttempt);
      expect(indep.interventionId, isNull);
      // conceptIds gắn từ scope — Q-matrix-ready.
      expect(indep.conceptIds, ['quy-dong']);
    });

    test('tự làm đúng ngay: independent = true, không lineage can thiệp', () {
      final s = newSession();
      expect(s.submit('23/20'), SubmitOutcome.independentCorrect);
      expect(s.outcome.independent, isTrue);
      expect(s.log.events.every((e) => e.interventionId == null), isTrue);
    });
  });

  group('vòng khép kín: tutor → recordSession → kho → «Hôm nay» đổi', () {
    test('trước: chưa thử dạng mới; sau 1 phiên tự-làm-đúng: hết «chưa thử», '
        'evidence đúng learner', () async {
      final store = JsonlLearnerStore();
      final t0 = DateTime(2026, 9, 2, 19);

      final before = await buildMissionFromStore(
          profile: _p5, store: store, now: t0);
      expect(before.unobservedCaseNames,
          contains('hai mẫu số không chia hết cho nhau'));

      // Phiên: trẻ tự làm đúng (INDEPENDENT ATTEMPT → LEARNING EVIDENCE).
      final c = toan5Bai6;
      final fp = FractionProblem.parse('3/4 + 2/5')!;
      final exerciseCase = fractionCase(fp.b, fp.d)!;
      final s = TutorSession(
        exerciseId: 'ex-1',
        skillCaseId: exerciseCase,
        problem: fp,
        scope: TutorScope.forProblem(
            c.conceptId, exerciseCase, c.stage, c.catalogue),
        now: () => t0,
      );
      s.submit('23/20');
      final rec = await recordSession(
        store: store,
        learnerId: _p5.learnerId,
        subjectId: c.subjectId,
        events: s.log.events,
        trigger: SessionTrigger.cameraHomework,
      );
      expect(rec.session, isNotNull);
      expect(rec.session!.learnerId, 'l-5', reason: 'đúng learnerId (§3)');
      expect(rec.session!.subjectId, 'toan');
      expect(rec.violations, isEmpty);

      // KNOWLEDGE STATE từ kho — không cache.
      final mastery =
          await masteryFromStore(store, _p5.learnerId, c);
      expect(mastery.cases[exerciseCase]!.hasEvidence, isTrue);

      // NEXT ACTION đổi theo bằng chứng.
      final after = await buildMissionFromStore(
          profile: _p5, store: store, now: t0.add(const Duration(minutes: 5)));
      expect(after.unobservedCaseNames,
          isNot(contains('hai mẫu số không chia hết cho nhau')));

      // Learner khác: KHÔNG thấy gì (NO CROSS-LEARNER CONTAMINATION).
      final other = await store.evidenceFor(
          learnerId: 'l-khac', skillCaseId: exerciseCase);
      expect(other.events, isEmpty);
    });

    test('phiên rỗng ⇒ không ghi (không rác lịch sử)', () async {
      final store = JsonlLearnerStore();
      final rec = await recordSession(
        store: store,
        learnerId: 'l-5',
        subjectId: 'toan',
        events: const [],
        trigger: SessionTrigger.cameraHomework,
      );
      expect(rec.session, isNull);
      expect(
          await store.sessions(learnerId: 'l-5'), isEmpty);
    });
  });

  group('grade ngoài slice — mission nói thật', () {
    test('grade 3: không mượn nội dung lớp 5, không review/unobserved bịa',
        () async {
      final store = JsonlLearnerStore();
      final m = await buildMissionFromStore(
          profile: const LearnerProfile(
              learnerId: 'l-3', displayName: 'Na', grade: 3),
          store: store);
      expect(m.nextActionTitle, contains('lớp 3'));
      expect(m.reviews, isEmpty);
      expect(m.unobservedCaseNames, isEmpty);
    });
  });
}
