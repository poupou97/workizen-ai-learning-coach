/// WAL-95 — kho dữ liệu học sinh: bất biến của Founder Task Order §1/§5/§6/§7/§12
/// phải sống qua LƯU → ĐỌC LẠI, không chỉ trong RAM.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/pedagogy/pedagogy_model.dart'
    show TeachingAct;
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/core/store/learning_session.dart';
import 'package:learning_coach/core/store/timetable.dart';
import 'package:learning_coach/core/student/evidence_weighting.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/mastery.dart';

LearningEvent _ev(String id, EvidenceKind k,
        {bool? correct, SupportLevel? support, String? prior, DateTime? at}) =>
    LearningEvent(
      eventId: id,
      skillCaseId: 'denominator-non-divisible',
      kind: k,
      correct: correct,
      at: at ?? DateTime(2026, 9, 1, 19),
      support: support,
      policyId: 'tutor-session-v1',
      priorEventId: prior,
    );

void main() {
  group('§1 profile — ba bất biến', () {
    test('birthYear KHÔNG suy ra grade; hai trẻ cùng tuổi khác lớp cùng tồn tại',
        () async {
      final store = JsonlLearnerStore();
      await store.saveProfile(const LearnerProfile(
          learnerId: 'l1', displayName: 'Minh', grade: 5,
          birthYear: 2015, guardianId: 'g1'));
      await store.saveProfile(const LearnerProfile(
          learnerId: 'l2', displayName: 'An', grade: 4,
          birthYear: 2015, guardianId: 'g1'));
      final ps = await store.profiles(guardianId: 'g1');
      expect(ps.map((p) => p.grade), [5, 4]);
      expect(ps.every((p) => p.birthYear == 2015), isTrue);
    });

    test('grade đổi được, và đổi lớp KHÔNG đụng bằng chứng', () async {
      final store = JsonlLearnerStore();
      const p = LearnerProfile(learnerId: 'l1', displayName: 'Minh', grade: 4);
      await store.saveProfile(p);
      await store.appendSession(LearningSession(
        sessionId: 's1', learnerId: 'l1', subjectId: 'toan',
        startedAt: DateTime(2026, 9, 1, 19),
        trigger: SessionTrigger.manual,
        skillCaseIds: const ['denominator-non-divisible'],
        events: [_ev('e1', EvidenceKind.independentAttempt, correct: true)],
      ));
      await store.saveProfile(p.withGrade(5)); // lên lớp
      expect((await store.profile('l1'))!.grade, 5);
      final log = await store.evidenceFor(
          learnerId: 'l1', skillCaseId: 'denominator-non-divisible');
      expect(log.events, hasLength(1),
          reason: 'đổi vị trí chương trình không xoá/không thêm bằng chứng');
    });

    test('⭐ grade ≠ mastery: chọn lớp 5 KHÔNG sinh bằng chứng lớp 1-4 nào',
        () async {
      final store = JsonlLearnerStore();
      await store.saveProfile(
          const LearnerProfile(learnerId: 'l1', displayName: 'Minh', grade: 5));
      for (final c in ['quy-dong', 'cong-phan-so', 'nhan-phan-so']) {
        final log = await store.evidenceFor(learnerId: 'l1', skillCaseId: c);
        expect(log.events, isEmpty);
      }
    });

    test('lớp ngoài 1..12 bị TỪ CHỐI khi đọc lại, không kẹp về biên', () {
      expect(
          LearnerProfile.fromJson(
              {'learnerId': 'x', 'displayName': 'y', 'grade': 13}),
          isNull);
      expect(
          LearnerProfile.fromJson(
              {'learnerId': 'x', 'displayName': 'y', 'grade': 0}),
          isNull);
    });
  });

  group('§5-6 session — lưu MỘT lần, ba view là phép chiếu', () {
    Future<JsonlLearnerStore> seeded() async {
      final s = JsonlLearnerStore();
      await s.saveProfile(
          const LearnerProfile(learnerId: 'l1', displayName: 'Minh', grade: 5));
      await s.appendSession(LearningSession(
        sessionId: 's-toan', learnerId: 'l1', subjectId: 'toan',
        startedAt: DateTime(2026, 9, 1, 19),
        trigger: SessionTrigger.cameraHomework,
        conceptIds: const ['quy-dong'],
        skillCaseIds: const ['denominator-non-divisible'],
        events: [_ev('e1', EvidenceKind.independentAttempt, correct: true)],
      ));
      await s.appendSession(LearningSession(
        sessionId: 's-tv', learnerId: 'l1', subjectId: 'tieng-viet',
        startedAt: DateTime(2026, 9, 2, 20),
        trigger: SessionTrigger.reviewDue,
      ));
      return s;
    }

    test('⭐ MỘT bản ghi phục vụ cả ba view (ngày / môn / tri thức)', () async {
      final s = await seeded();
      final byDay = await s.sessions(
          learnerId: 'l1', onDay: DateTime(2026, 9, 1));
      final bySubject = await s.sessions(learnerId: 'l1', subjectId: 'toan');
      final byKnowledge = await s.sessions(
          learnerId: 'l1', skillCaseId: 'denominator-non-divisible');
      expect(byDay.single.sessionId, 's-toan');
      expect(bySubject.single.sessionId, 's-toan');
      expect(byKnowledge.single.sessionId, 's-toan');
      // và kho chỉ chứa ĐÚNG 2 bản ghi phiên — không nhân bản cho từng view
      expect((await s.sessions(learnerId: 'l1')), hasLength(2));
    });

    test('học sinh khác không thấy dữ liệu của nhau (multi-child cô lập)',
        () async {
      final s = await seeded();
      expect(await s.sessions(learnerId: 'l2'), isEmpty);
      expect(
          (await s.evidenceFor(
                  learnerId: 'l2', skillCaseId: 'denominator-non-divisible'))
              .events,
          isEmpty);
    });
  });

  group('§7 lineage sống qua lưu-đọc', () {
    test('⭐ round-trip JSONL giữ support/policyId/priorEventId và REPLAY khớp',
        () async {
      final store = JsonlLearnerStore();
      await store.appendSession(LearningSession(
        sessionId: 's1', learnerId: 'l1', subjectId: 'toan',
        startedAt: DateTime(2026, 9, 1, 19),
        trigger: SessionTrigger.manual,
        events: [
          _ev('e1', EvidenceKind.independentAttempt,
              correct: false, support: SupportLevel.none,
              at: DateTime(2026, 9, 1, 19)),
          _ev('e2', EvidenceKind.hintRequested,
              at: DateTime(2026, 9, 1, 19, 1)),
          _ev('e3', EvidenceKind.postHintSuccess,
              correct: true, support: SupportLevel.hint, prior: 'e1',
              at: DateTime(2026, 9, 1, 19, 2)),
        ],
      ));
      // lưu ra chuỗi rồi NẠP LẠI như khởi động app
      final reloaded = JsonlLearnerStore.fromJsonl(store.toJsonl());
      final s = (await reloaded.sessions(learnerId: 'l1')).single;
      final post = s.events.firstWhere(
          (e) => e.kind == EvidenceKind.postHintSuccess);
      expect(post.support, SupportLevel.hint,
          reason: 'không có trường này thì «đúng sau hint nhỏ» lẫn với '
              '«đúng sau xem trọn lời giải» ngay khi mở lại app');
      expect(post.priorEventId, 'e1');
      expect(post.policyId, 'tutor-session-v1');
      expect(maxSupportIn(s), SupportLevel.hint);

      // REPLAY sau khi nạp lại phải cho ĐÚNG kết luận: chưa có bằng chứng tự làm
      final log = await reloaded.evidenceFor(
          learnerId: 'l1', skillCaseId: 'denominator-non-divisible');
      final m = replayMastery(log, BktParams.freeResponse);
      expect(m.independentCorrect, 0,
          reason: 'đúng-sau-gợi-ý không bao giờ thành bằng chứng tự làm');
      expect(m.supportedCount, greaterThan(0));
    });

    test('⭐⭐ WAL-178/182 — sourceDocumentId/lessonNo/act/learnerText sống '
        'qua JSONL round-trip (không phải chỉ đúng trong RAM)', () async {
      final store = JsonlLearnerStore();
      await store.appendSession(LearningSession(
        sessionId: 's1', learnerId: 'l1', subjectId: 'khoa-hoc',
        startedAt: DateTime(2026, 9, 4, 10),
        trigger: SessionTrigger.manual,
        events: [
          LearningEvent(
            eventId: 'e1',
            skillCaseId: 'khtn-thi-nghiem',
            kind: EvidenceKind.independentAttempt,
            at: DateTime(2026, 9, 4, 10),
            sourceDocumentId: '05-sgk-khoa-hoc-5',
            lessonNo: 1,
            act: TeachingAct.askExplanation,
            learnerText: 'Đất tan ra trong nước, có bọt khí',
          ),
        ],
      ));
      final reloaded = JsonlLearnerStore.fromJsonl(store.toJsonl());
      final e = (await reloaded.sessions(learnerId: 'l1')).single.events.single;
      expect(e.sourceDocumentId, '05-sgk-khoa-hoc-5',
          reason: '⭐⭐ đột biến bỏ lineage khi lưu ⇒ đỏ — Learning Map/Parent '
              'View/Citation đọc field này SAU KHI app khởi động lại, không '
              'chỉ trong phiên đang chạy');
      expect(e.lessonNo, 1);
      expect(e.act, TeachingAct.askExplanation);
      expect(e.learnerText, 'Đất tan ra trong nước, có bọt khí',
          reason: 'chữ trẻ viết phải sống qua lưu-đọc, không chỉ callback');
    });

    test('lineage khuyết trong dữ liệu cũ ⇒ null, KHÔNG suy đoán', () async {
      final store = JsonlLearnerStore.fromJsonl(
          '{"type":"session","sessionId":"old","learnerId":"l1",'
          '"subjectId":"toan","startedAt":"2026-01-01T08:00:00.000",'
          '"trigger":"manual","events":[{"eventId":"e1",'
          '"skillCaseId":"c","kind":"independentAttempt",'
          '"at":"2026-01-01T08:00:00.000","correct":true}]}');
      final e = (await store.sessions(learnerId: 'l1')).single.events.single;
      expect(e.sourceDocumentId, isNull);
      expect(e.lessonNo, isNull);
      expect(e.act, isNull);
      expect(e.learnerText, isNull);
    });

    test('support khuyết trong dữ liệu cũ ⇒ null, KHÔNG mặc định none', () async {
      final store = JsonlLearnerStore.fromJsonl(
          '{"type":"session","sessionId":"old","learnerId":"l1",'
          '"subjectId":"toan","startedAt":"2026-01-01T08:00:00.000",'
          '"trigger":"manual","events":[{"eventId":"e1",'
          '"skillCaseId":"c","kind":"independentAttempt",'
          '"at":"2026-01-01T08:00:00.000","correct":true}]}');
      final s = (await store.sessions(learnerId: 'l1')).single;
      expect(s.events.single.support, isNull);
    });

    test('dòng hỏng không làm sập kho (append-only bền)', () async {
      final store = JsonlLearnerStore.fromJsonl(
          'không-phải-json\n'
          '{"type":"profile","learnerId":"l1","displayName":"Minh","grade":5}');
      expect((await store.profiles()), hasLength(1));
    });
  });

  group('§12/F7 exam ≠ learn', () {
    test('⭐ phiên ASSESS có sự kiện mang hỗ trợ ⇒ VI PHẠM phát hiện được', () {
      final dirty = LearningSession(
        sessionId: 'x', learnerId: 'l1', subjectId: 'toan',
        startedAt: DateTime(2026, 9, 1), trigger: SessionTrigger.assessment,
        mode: SessionMode.assess,
        events: [
          _ev('e1', EvidenceKind.independentAttempt,
              correct: true, support: SupportLevel.none),
          _ev('e2', EvidenceKind.postHintSuccess,
              correct: true, support: SupportLevel.hint),
        ],
      );
      final v = tutoringViolationsInExam(dirty);
      expect(v.map((e) => e.eventId), ['e2']);
    });

    test('phiên assess sạch ⇒ không vi phạm; phiên learn không bị soi luật thi',
        () {
      final clean = LearningSession(
        sessionId: 'x', learnerId: 'l1', subjectId: 'toan',
        startedAt: DateTime(2026, 9, 1), trigger: SessionTrigger.assessment,
        mode: SessionMode.assess,
        events: [
          _ev('e1', EvidenceKind.independentAttempt,
              correct: true, support: SupportLevel.none)
        ],
      );
      expect(tutoringViolationsInExam(clean), isEmpty);
      final learn = LearningSession(
        sessionId: 'y', learnerId: 'l1', subjectId: 'toan',
        startedAt: DateTime(2026, 9, 1), trigger: SessionTrigger.manual,
        events: [
          _ev('e1', EvidenceKind.postHintSuccess,
              correct: true, support: SupportLevel.hint)
        ],
      );
      expect(tutoringViolationsInExam(learn), isEmpty,
          reason: 'dạy học có hỗ trợ là BÌNH THƯỜNG — chỉ thi mới cấm');
    });
  });

  group('WAL-96 thời khoá biểu trong kho', () {
    test('lưu → đọc lại giữ nguyên; TKB là TUỲ CHỌN nên rỗng là hợp lệ',
        () async {
      final store = JsonlLearnerStore();
      expect(await store.timetable('l1'), isEmpty,
          reason: 'chưa nhập TKB ⇒ rỗng, không lỗi (F13)');
      await store.saveTimetable('l1', const [
        TimetableEntry(
            learnerId: 'l1', weekday: 2, period: 1, subjectId: 'toan'),
        TimetableEntry(
            learnerId: 'l1', weekday: 2, period: 2, subjectId: 'tieng-viet'),
      ]);
      final reloaded = JsonlLearnerStore.fromJsonl(store.toJsonl());
      final tt = await reloaded.timetable('l1');
      expect(tt.map((e) => e.subjectId), ['toan', 'tieng-viet']);
      expect(await reloaded.timetable('l2'), isEmpty,
          reason: 'TKB cũng cô lập theo learnerId');
    });

    test('đổi TKB giữa kỳ: bản mới thắng, lịch sử vẫn còn trong log', () async {
      final store = JsonlLearnerStore();
      await store.saveTimetable('l1', const [
        TimetableEntry(
            learnerId: 'l1', weekday: 2, period: 1, subjectId: 'toan')
      ]);
      await store.saveTimetable('l1', const [
        TimetableEntry(
            learnerId: 'l1', weekday: 2, period: 1, subjectId: 'khoa-hoc')
      ]);
      expect((await store.timetable('l1')).single.subjectId, 'khoa-hoc');
      expect(store.toJsonl().split('\n').where((l) => l.contains('timetable')),
          hasLength(2), reason: 'append-only: lịch sử đổi lịch không mất');
    });
  });
}
