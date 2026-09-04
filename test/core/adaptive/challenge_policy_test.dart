/// ⭐⭐ WAL-183 — Adaptive Challenge Policy: tín hiệu 🌱/🎯/🚀 từ Learner
/// Capability đã có, chống dao động khi vững-rồi-sai-lại.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/adaptive/challenge_policy.dart';
import 'package:learning_coach/core/student/evidence_weighting.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/mastery.dart';

const _p = BktParams.freeResponse;
const _case = 'denominator-non-divisible';

LearningEvent _attempt(
  String id,
  bool correct,
  DateTime at, {
  EvidenceKind kind = EvidenceKind.independentAttempt,
}) =>
    LearningEvent(
        eventId: id, skillCaseId: _case, kind: kind, correct: correct, at: at);

CaseMastery _replay(List<LearningEvent> events) =>
    replayMastery(EvidenceLog(skillCaseId: _case, events: events), _p);

void main() {
  group('challengeSignalFor — ngưỡng cơ bản', () {
    test('⭐ chưa có bằng chứng ⇒ null, KHÔNG mặc định 🎯', () {
      final m = CaseMastery.initial(_case, _p);
      expect(challengeSignalFor(m), isNull,
          reason: 'UNKNOWN LÀ TRẠNG THÁI THẬT — không suy đoán khi chưa có gì');
    });

    test('pMastery cao, chưa có tín hiệu trước ⇒ stretch', () {
      final m = CaseMastery(
          skillCaseId: _case, pMastery: 0.9, evidenceCount: 4);
      expect(challengeSignalFor(m), ChallengeSignal.stretch);
    });

    test('pMastery giữa, chưa có tín hiệu trước ⇒ fit', () {
      final m = CaseMastery(
          skillCaseId: _case, pMastery: 0.72, evidenceCount: 3);
      expect(challengeSignalFor(m), ChallengeSignal.fit);
    });

    test('pMastery thấp, chưa có tín hiệu trước ⇒ consolidate', () {
      final m = CaseMastery(
          skillCaseId: _case, pMastery: 0.4, evidenceCount: 2);
      expect(challengeSignalFor(m), ChallengeSignal.consolidate);
    });
  });

  group('⭐⭐ chống dao động — một câu trả lời lệch nhẹ KHÔNG lật tín hiệu', () {
    test('đang stretch, pMastery dịu nhẹ (vẫn ≥ ngưỡng ra) ⇒ VẪN stretch', () {
      final m = CaseMastery(
          skillCaseId: _case, pMastery: 0.8, evidenceCount: 6);
      expect(
          challengeSignalFor(m, previous: ChallengeSignal.stretch),
          ChallengeSignal.stretch,
          reason: '0.8 dưới ngưỡng vào (0.85) nhưng trên ngưỡng ra (0.75) — '
              'một câu sai lẻ không được kéo tín hiệu xuống ngay');
    });

    test('đang stretch, pMastery rơi qua hẳn ngưỡng ra ⇒ rời stretch', () {
      final m = CaseMastery(
          skillCaseId: _case, pMastery: 0.7, evidenceCount: 6);
      expect(challengeSignalFor(m, previous: ChallengeSignal.stretch),
          ChallengeSignal.fit,
          reason: 'rơi thật (dưới 0.75) mới rời — không rơi thẳng xuống '
              'consolidate vì 0.7 chưa dưới 0.6');
    });

    test('đang consolidate, pMastery nhích nhẹ ⇒ VẪN consolidate', () {
      final m = CaseMastery(
          skillCaseId: _case, pMastery: 0.65, evidenceCount: 3);
      expect(
          challengeSignalFor(m, previous: ChallengeSignal.consolidate),
          ChallengeSignal.consolidate,
          reason: 'một câu đúng lẻ không được đẩy ngay lên fit');
    });

    test('đang consolidate, pMastery vượt hẳn ngưỡng ra ⇒ rời consolidate', () {
      final m = CaseMastery(
          skillCaseId: _case, pMastery: 0.75, evidenceCount: 3);
      expect(challengeSignalFor(m, previous: ChallengeSignal.consolidate),
          ChallengeSignal.fit);
    });
  });

  group('⭐⭐ BOUNDED FIRST POC — 6 trạng thái bằng chứng tổng hợp (Toán, '
      'denominator SkillCase, replay THẬT qua replayMastery)', () {
    test('① chưa thử dạng này ⇒ null', () {
      expect(challengeSignalFor(_replay(const [])), isNull);
    });

    test('② đang luyện, còn yếu (sai liên tiếp) ⇒ consolidate', () {
      final at = DateTime(2026, 9, 4);
      final m = _replay([
        _attempt('e1', false, at),
        _attempt('e2', false, at.add(const Duration(minutes: 1))),
      ]);
      expect(challengeSignalFor(m), ChallengeSignal.consolidate);
    });

    test('③ đang luyện, mạnh dần (sai rồi vừa đúng lại) ⇒ fit — chưa đủ để '
        'gọi là vững, không còn ở mức yếu', () {
      final at = DateTime(2026, 9, 4);
      final m = _replay([
        _attempt('e1', false, at),
        _attempt('e2', true, at.add(const Duration(minutes: 1))),
      ]);
      expect(challengeSignalFor(m), ChallengeSignal.fit);
    });

    test('④ vững liên tục (nhiều lần đúng tự làm) ⇒ stretch', () {
      final at = DateTime(2026, 9, 4);
      final m = _replay([
        for (var i = 0; i < 6; i++)
          _attempt('e$i', true, at.add(Duration(minutes: i))),
      ]);
      expect(challengeSignalFor(m), ChallengeSignal.stretch);
    });

    test(
        '⭐⭐ ⑤ vững rồi MỘT LẦN sai lại — có previous=stretch ⇒ VẪN stretch '
        '(đột biến bỏ hysteresis ⇒ đỏ)', () {
      final at = DateTime(2026, 9, 4);
      final m = _replay([
        for (var i = 0; i < 6; i++)
          _attempt('e$i', true, at.add(Duration(minutes: i))),
        _attempt('e6', false, at.add(const Duration(minutes: 6))),
      ]);
      expect(challengeSignalFor(m, previous: ChallengeSignal.stretch),
          ChallengeSignal.stretch,
          reason: 'đây CHÍNH LÀ ca "vững rồi sai lại" Founder order nêu — '
              'một câu sai giữa chuỗi vững không được lật ngay về thấp hơn');
      // Không truyền previous (vd. lần đầu app hiện tín hiệu, chưa theo dõi
      // lịch sử) ⇒ dùng ngưỡng vào thẳng, có thể khác — đó là lựa chọn của
      // NGƯỜI GỌI (có/không theo dõi previous), không phải lỗi hàm.
    });

    test('⑥ hỗ trợ nhiều (guided/hint, ít tự làm) ⇒ chưa đủ bằng chứng độc '
        'lập để lên tín hiệu cao', () {
      final at = DateTime(2026, 9, 4);
      final m = _replay([
        _attempt('e1', true, at, kind: EvidenceKind.hintShown),
        _attempt('e2', true, at.add(const Duration(minutes: 1)),
            kind: EvidenceKind.guidedAttempt),
        _attempt('e3', true, at.add(const Duration(minutes: 2)),
            kind: EvidenceKind.guidedAttempt),
        _attempt('e4', false, at.add(const Duration(minutes: 3))),
      ]);
      expect(challengeSignalFor(m), ChallengeSignal.consolidate,
          reason: 'guided/hint không được tính là bằng chứng độc lập — chỉ '
              'một lần tự làm (và sai) thật sự đếm');
    });
  });

  group('challengeLabelFor', () {
    test('⭐ không chữ số, không %, đúng nguyên tắc gamification nhẹ', () {
      for (final s in ChallengeSignal.values) {
        final (icon, label) = challengeLabelFor(s);
        expect(icon, isNotEmpty);
        expect(RegExp(r'[0-9%]').hasMatch(label), isFalse, reason: label);
      }
    });
  });
}
