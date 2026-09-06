/// ⭐⭐ Lệnh 51 §1 + §4 — CÁCH LY HỒ SƠ, kiểm ở tầng LƯU TRỮ.
///
/// «Không chấp nhận isolation chỉ ở UI. Phải trace persistence/storage/runtime.»
/// (§1). Nên test này KHÔNG dựng widget nào: nó ghi vào kho như app ghi, ép
/// kho qua một vòng LƯU → ĐỌC LẠI (đúng cái `FileLearnerStore` làm khi khởi
/// động lại), rồi hỏi kho từng câu §1 hỏi.
///
/// Kịch bản §4:
///   Na  — Lớp 6 — học KHTN 6 Bài 17
///   Minh — Lớp 5 — chưa học gì
/// Kỳ vọng: Minh KHÔNG thấy gì của Na; đổi lại Na thì state cũ còn nguyên.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/core/store/learning_session.dart';
import 'package:learning_coach/core/store/timetable.dart';
import 'package:learning_coach/core/store/timetable_generator.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';

const _na = LearnerProfile(learnerId: 'na', displayName: 'Na', grade: 6);
const _minh = LearnerProfile(learnerId: 'minh', displayName: 'Minh', grade: 5);

const _g6 = ['KHTN', 'Ngữ văn', 'Toán', 'Tiếng Anh', 'Tin học'];
const _g5 = ['Khoa học', 'LS&ĐL', 'Tiếng Việt', 'Toán', 'Đạo đức'];

LearningSession _naStudiesB17() => LearningSession(
  sessionId: 'na-b17-1',
  learnerId: 'na',
  subjectId: 'khtn',
  startedAt: DateTime(2026, 9, 6, 19),
  trigger: SessionTrigger.manual,
  conceptIds: const ['tach-chat-khoi-hon-hop'],
  skillCaseIds: const ['chon-cach-tach-theo-tinh-chat'],
  events: [
    LearningEvent(
      eventId: 'na-e1',
      skillCaseId: 'chon-cach-tach-theo-tinh-chat',
      kind: EvidenceKind.independentAttempt,
      at: DateTime(2026, 9, 6, 19, 5),
      policyId: 'tutor-session-v1',
    ),
  ],
);

/// Dựng kho ở trạng thái sau khi Na đã học, Minh thì chưa.
Future<JsonlLearnerStore> _seeded() async {
  final s = JsonlLearnerStore();
  await s.saveProfile(_na);
  await s.saveProfile(_minh);
  await s.saveTimetable(
    'na',
    generateTimetable(
      learnerId: 'na',
      subjects: _g6,
      seed: 12345,
      slotsPerDay: 3,
    ),
  );
  await s.saveTimetable(
    'minh',
    generateTimetable(
      learnerId: 'minh',
      subjects: _g5,
      seed: 777,
      slotsPerDay: 3,
    ),
  );
  await s.appendSession(_naStudiesB17());
  await s.saveActiveLearner('na');
  return s;
}

/// ⭐ Tắt app mở lại: kho đi qua ĐÚNG con đường tuần tự hoá của FileLearnerStore.
JsonlLearnerStore _restart(JsonlLearnerStore s) =>
    JsonlLearnerStore.fromJsonl(s.toJsonl());

void main() {
  group('§1 — hai hồ sơ trên cùng một máy', () {
    test(
      'DEVICE != USER: một máy giữ hai người học, hai lớp khác nhau',
      () async {
        final s = _restart(await _seeded());
        final ps = await s.profiles();
        expect(ps.length, 2);
        expect((await s.profile('na'))!.grade, 6);
        expect((await s.profile('minh'))!.grade, 5);
      },
    );

    test('PHIÊN HỌC không rò: Na có 1 phiên, Minh có 0', () async {
      final s = _restart(await _seeded());
      expect((await s.sessions(learnerId: 'na')).length, 1);
      expect(await s.sessions(learnerId: 'minh'), isEmpty);
    });

    test(
      'BẰNG CHỨNG không rò: ca của Na trống rỗng khi hỏi dưới tên Minh',
      () async {
        final s = _restart(await _seeded());
        const caseId = 'chon-cach-tach-theo-tinh-chat';
        final naLog = await s.evidenceFor(learnerId: 'na', skillCaseId: caseId);
        final minhLog = await s.evidenceFor(
          learnerId: 'minh',
          skillCaseId: caseId,
        );
        expect(naLog.events, isNotEmpty);
        expect(
          minhLog.events,
          isEmpty,
          reason: 'bằng chứng của Na hiện ra dưới hồ sơ Minh',
        );
      },
    );

    test(
      'THỜI KHOÁ BIỂU không rò: hai TKB khác nhau, không cái nào rỗng',
      () async {
        final s = _restart(await _seeded());
        final naT = await s.timetable('na');
        final minhT = await s.timetable('minh');
        expect(naT, isNotEmpty);
        expect(minhT, isNotEmpty);
        expect([
          for (final e in naT) e.subjectId,
        ], isNot(equals([for (final e in minhT) e.subjectId])));
        // Môn lớp 6 không được xuất hiện trong TKB của học sinh lớp 5.
        expect([for (final e in minhT) e.subjectId], isNot(contains('KHTN')));
        expect([
          for (final e in naT) e.subjectId,
        ], isNot(contains('Tiếng Việt')));
        // Mọi tiết mang đúng chủ.
        expect(naT.every((e) => e.learnerId == 'na'), isTrue);
        expect(minhT.every((e) => e.learnerId == 'minh'), isTrue);
      },
    );
  });

  group('§4 — đổi hồ sơ, có khởi động lại ở giữa', () {
    test(
      'Na học → restart → đổi Minh → restart → đổi lại Na: state Na CÒN',
      () async {
        var s = await _seeded();

        s = _restart(s); // tắt mở lần 1
        expect(await s.activeLearnerId(), 'na');

        await s.saveActiveLearner('minh'); // đổi sang Minh
        s = _restart(s); // tắt mở lần 2
        expect(await s.activeLearnerId(), 'minh');
        expect(
          await s.sessions(learnerId: 'minh'),
          isEmpty,
          reason: 'Minh thấy tiến độ của Na sau khi đổi hồ sơ',
        );

        await s.saveActiveLearner('na'); // đổi lại Na
        s = _restart(s); // tắt mở lần 3
        expect(await s.activeLearnerId(), 'na');
        final naAgain = await s.sessions(learnerId: 'na');
        expect(naAgain.length, 1, reason: 'state của Na mất sau khi đi vòng');
        expect(naAgain.single.sessionId, 'na-b17-1');
        expect(await s.timetable('na'), isNotEmpty);
      },
    );

    test('học dưới tên Minh KHÔNG cộng vào Na', () async {
      final s = await _seeded();
      await s.appendSession(
        LearningSession(
          sessionId: 'minh-1',
          learnerId: 'minh',
          subjectId: 'toan',
          startedAt: DateTime(2026, 9, 6, 20),
          trigger: SessionTrigger.manual,
        ),
      );
      final r = _restart(s);
      expect((await r.sessions(learnerId: 'na')).length, 1);
      expect((await r.sessions(learnerId: 'minh')).length, 1);
      expect((await r.sessions(learnerId: 'na')).single.sessionId, 'na-b17-1');
    });
  });

  group('§14 — TKB sinh ra KHÔNG phải là việc học', () {
    test('sinh TKB cho Minh không tạo phiên học nào cho Minh', () async {
      final s = JsonlLearnerStore();
      await s.saveProfile(_minh);
      await s.saveTimetable(
        'minh',
        generateTimetable(
          learnerId: 'minh',
          subjects: _g5,
          seed: 42,
          slotsPerDay: 3,
        ),
      );
      final r = _restart(s);
      expect(await r.timetable('minh'), isNotEmpty);
      expect(
        await r.sessions(learnerId: 'minh'),
        isEmpty,
        reason: 'TIMETABLE ENTRY != LEARNING SESSION',
      );
    });
  });

  group('§1 — xoá/xuất vẫn tôn trọng ranh giới hồ sơ', () {
    test('xoá Na không đụng bản ghi của Minh', () async {
      final s = await _seeded();
      await s.appendSession(
        LearningSession(
          sessionId: 'minh-1',
          learnerId: 'minh',
          subjectId: 'toan',
          startedAt: DateTime(2026, 9, 6, 20),
          trigger: SessionTrigger.manual,
        ),
      );
      final removed = await s.deleteLearner('na');
      expect(removed, greaterThan(0));
      expect(await s.sessions(learnerId: 'na'), isEmpty);
      expect(await s.timetable('na'), isEmpty);
      expect((await s.sessions(learnerId: 'minh')).length, 1);
      expect(await s.timetable('minh'), isNotEmpty);
    });

    test('xuất dữ liệu Na không kèm một dòng nào của Minh', () async {
      final s = await _seeded();
      await s.appendSession(
        LearningSession(
          sessionId: 'minh-1',
          learnerId: 'minh',
          subjectId: 'toan',
          startedAt: DateTime(2026, 9, 6, 20),
          trigger: SessionTrigger.manual,
        ),
      );
      final out = await s.exportLearner('na');
      expect(out, contains('na-b17-1'));
      expect(out, isNot(contains('minh')));
    });
  });
}
