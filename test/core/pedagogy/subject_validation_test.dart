/// WAL-130 — 5-SUBJECT PEDAGOGY VALIDATION (mức blueprint × log).
///
/// Learner ở đây là MÔ PHỎNG CÓ DÁN NHÃN (policyId 'scenario-sim-v1') —
/// WAL-49: simulation được FALSIFY, không được claim validated-on-real-learners.
/// Kết quả «v0 CHƯA bắt được X» là finding chủ đích — characterization test,
/// đổi hành vi phải đổi test một cách CÓ Ý THỨC.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/curriculum/pedagogical_boundary.dart';
import 'package:learning_coach/core/pedagogy/blueprint_catalogue_v0.dart';
import 'package:learning_coach/core/pedagogy/learning_blueprint.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/mastery.dart';
import '../../support/curriculum.dart';

const _sim = 'scenario-sim-v1';
var _seq = 0;
LearningEvent ev(String caseId, EvidenceKind kind,
        {bool? correct, SupportLevel support = SupportLevel.none}) =>
    LearningEvent(
      eventId: 'sim#${_seq++}',
      skillCaseId: caseId,
      kind: kind,
      correct: correct,
      at: DateTime(2026, 9, 2, 20, 0, _seq),
      support: support,
      policyId: _sim,
    );
EvidenceLog log(String caseId, List<LearningEvent> events) =>
    events.fold(EvidenceLog.empty(caseId), (l, e) => l.append(e));

void main() {
  group('TOÁN — case KHÁC grade/bài (chống overfit B6)', () {
    test('toan6 b15: đúng độc lập tuân thủ; đúng-sau-demonstration hợp lệ '
        'trong cap nhưng KHÔNG có independentAttempt ⇒ EVIDENCE_MISSING', () {
      const c = 'bo-ngoac-dau-tru';
      expect(
          blueprintViolations(blueprintSoNguyenB15,
              log(c, [ev(c, EvidenceKind.independentAttempt, correct: true)])),
          isEmpty);
      final v = blueprintViolations(
          blueprintSoNguyenB15,
          log(c, [
            ev(c, EvidenceKind.hintRequested, support: SupportLevel.none),
            ev(c, EvidenceKind.postHintSuccess,
                correct: true, support: SupportLevel.workedStep),
          ]));
      expect(v.join(), contains('EVIDENCE_MISSING'));
    });

    test('FUTURE-KNOWLEDGE LEAKAGE: học sinh lớp 4 chưa có thuật ngữ «mẫu số '
        'chung» ⇒ TutorScope RỖNG với method lớp 5 — kernel thật chặn', () {
      final c5 = toan5Bai6;
      const stage4 = LearningStage(
        grade: 4,
        bookSeries: 'kntt',
        lessonId: 'toan4-truoc-b57',
        conceptsIntroduced: {'phan-so'}, // CHƯA có nhân-số-tự-nhiên đầy đủ
        methodsIntroduced: {}, // chưa dạy method quy đồng nào
        terminologyIntroduced: {}, // chưa có «mẫu số chung»
      );
      final scope = TutorScope.forProblem(
          'quy-dong', 'denominator-non-divisible', stage4, c5.catalogue);
      expect(scope.allowedMethods, isEmpty,
          reason: 'method lớp 5 không được rò xuống learner lớp 4');
    });
  });

  group('TIẾNG VIỆT — đọc-hiểu (recognize ≠ explain, SAM không đọc hộ)', () {
    const c = 'doc-hieu-tra-loi';
    test('nhận-diện đúng độc lập rồi giải-thích với scaffold ≤ cap: 0 vi phạm',
        () {
      final v = blueprintViolations(
          blueprintTv3DocHieu,
          log(c, [
            ev(c, EvidenceKind.independentAttempt, correct: true),
            ev(c, EvidenceKind.hintRequested, support: SupportLevel.none),
            ev(c, EvidenceKind.guidedAttempt,
                correct: true, support: SupportLevel.workedStep),
          ]));
      expect(v, isEmpty, reason: 'partialScaffold cap = workedStep evidence');
    });

    test('SAM đọc hộ trọn đáp án (fullSolution) ⇒ ASSISTANCE_OVER_CAP', () {
      final v = blueprintViolations(
          blueprintTv3DocHieu,
          log(c, [
            ev(c, EvidenceKind.independentAttempt, correct: false),
            ev(c, EvidenceKind.postHintSuccess,
                correct: true, support: SupportLevel.fullSolution),
          ]));
      expect(v.any((x) => x.startsWith('ASSISTANCE_OVER_CAP')), isTrue);
    });
  });

  group('LỊCH SỬ — sử liệu: trần thấp nhất, không kết luận hộ', () {
    const c = 'doc-su-lieu-ket-luan';
    test('HS lập luận độc lập + một strategic hint: 0 vi phạm', () {
      final v = blueprintViolations(
          blueprintSu10SuLieu,
          log(c, [
            ev(c, EvidenceKind.independentAttempt, correct: false),
            ev(c, EvidenceKind.hintRequested, support: SupportLevel.none),
            ev(c, EvidenceKind.guidedAttempt,
                correct: true, support: SupportLevel.hint),
          ]));
      expect(v, isEmpty);
    });

    test('một bước «làm mẫu kết luận» (workedStep) ⇒ vượt trần Sử ngay', () {
      final v = blueprintViolations(
          blueprintSu10SuLieu,
          log(c, [
            ev(c, EvidenceKind.independentAttempt, correct: false),
            ev(c, EvidenceKind.postHintSuccess,
                correct: true, support: SupportLevel.workedStep),
          ]));
      expect(v.any((x) => x.startsWith('ASSISTANCE_OVER_CAP')), isTrue,
          reason: 'demonstration/workedExample bị blueprint Sử cấm');
    });
  });

  group('KHOA HỌC — quan sát trước; LIMITATION v0 phát hiện chủ đích', () {
    const c = 'quan-sat-ghi-nhan';
    test('✅ v0.1 (WAL-131 trả nợ finding #1): demo TRƯỚC khi trẻ quan sát '
        '⇒ LEARNER_FIRST_VIOLATED', () {
      final v = blueprintViolations(
          blueprintKhoa4QuanSat,
          log(c, [
            // sai thứ tự sư phạm: làm mẫu NGAY từ đầu, quan sát sau
            ev(c, EvidenceKind.postHintSuccess,
                correct: true, support: SupportLevel.workedStep),
            ev(c, EvidenceKind.independentAttempt, correct: true),
          ]));
      expect(v.any((x) => x.startsWith('LEARNER_FIRST_VIOLATED')), isTrue);
    });

    test('trẻ quan sát trước rồi mới được scaffold: 0 vi phạm learnerFirst',
        () {
      final v = blueprintViolations(
          blueprintKhoa4QuanSat,
          log(c, [
            ev(c, EvidenceKind.independentAttempt, correct: false),
            ev(c, EvidenceKind.postHintSuccess,
                correct: true, support: SupportLevel.workedStep),
          ]));
      expect(v.where((x) => x.startsWith('LEARNER_FIRST')), isEmpty);
    });
  });

  group('NGOẠI NGỮ — listening: cap replay; gap loại-can-thiệp', () {
    const c = 'listen-and-tick';
    test('nghe 2 lần (hint=replay) rồi đúng độc lập lần 3: 0 vi phạm', () {
      final v = blueprintViolations(
          blueprintNn3Listening,
          log(c, [
            ev(c, EvidenceKind.independentAttempt, correct: false),
            ev(c, EvidenceKind.hintRequested, support: SupportLevel.none),
            ev(c, EvidenceKind.guidedAttempt,
                correct: false, support: SupportLevel.hint),
            ev(c, EvidenceKind.independentAttempt, correct: true),
          ]));
      expect(v, isEmpty);
    });

    test('⚠️ CHARACTERIZATION: lộ transcript (về evidence = workedStep) '
        'KHÔNG phân biệt được với phát-lại-chậm — gap loại-can-thiệp '
        '(interventionId có id nhưng evidence không có CONTENT TYPE)', () {
      final v = blueprintViolations(
          blueprintNn3Listening,
          log(c, [
            ev(c, EvidenceKind.independentAttempt, correct: false),
            ev(c, EvidenceKind.postHintSuccess,
                correct: true, support: SupportLevel.workedStep),
          ]));
      // demonstration cap cho phép workedStep ⇒ v0 chấp nhận CẢ HAI:
      // phát-lại-chậm (đúng pedagogy) và lộ-transcript (sai pedagogy).
      expect(v, isEmpty,
          reason: 'GHI NHẬN gap cho WAL-123/131: cần interventionKind '
              'trong contract trước khi voice/listening lên production');
    });
  });
}
