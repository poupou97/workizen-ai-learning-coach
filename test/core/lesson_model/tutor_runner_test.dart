/// TRACK B — TutorRunner: vòng lặp có ranh giới, tất định, không kẹt,
/// không chê, không khen khi chưa khớp, không khen tư chất.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/content_trust.dart';
import 'package:learning_coach/core/lesson_model/tutor_script.dart';
import 'package:learning_coach/core/tutor/tutor_feedback.dart'
    show bannedAbilityPraise;

import '../../features/lesson_workspace/support.dart';

TutorScript _script() => TutorScript(
  steps: const [
    ExplainStep(id: 'e', text: 'Giải thích.', sourceBlockId: 'b1'),
    AskStep(
      id: 'q',
      prompt: 'Hỏi?',
      promptBlockId: 'b2',
      options: ['Cô cạn', 'Lọc'],
      acceptable: [r'^cô cạn$'],
      hints: ['gợi ý 1', 'gợi ý 2'],
      feedbackMatched: 'Khớp với sách.',
      scaffold: 'Chưa khớp — sách nói cô cạn. Đi tiếp nhé.',
      keySource: 'prototype',
    ),
    NextStep(id: 'n', label: 'Đọc lại', target: NextTarget.read),
  ],
);

void main() {
  test('kịch bản bắt đầu bằng lời giải thích; Tiếp ⇒ câu hỏi', () {
    final r = TutorRunner(_script());
    expect(r.transcript.single.kind, TurnKind.explain);
    r.advance();
    expect(r.current, isA<AskStep>());
    expect(r.transcript.last.kind, TurnKind.ask);
  });

  test('⭐ khớp mẫu ⇒ phản hồi khớp rồi sang bước tiếp', () {
    final r = TutorRunner(_script())..advance();
    expect(r.submit('  CÔ CẠN. '), TurnKind.matched);
    expect(
      r.transcript.map((t) => t.kind),
      containsAllInOrder([TurnKind.learner, TurnKind.matched, TurnKind.next]),
    );
    expect(r.current, isA<NextStep>());
  });

  test(
    '⭐⭐ không khớp ⇒ gợi ý 1 → gợi ý 2 → scaffold rồi ĐI TIẾP, không kẹt',
    () {
      final r = TutorRunner(_script())..advance();
      expect(r.submit('Lọc'), TurnKind.hint);
      expect(r.hintLevel, 1);
      expect(r.submit('Lọc'), TurnKind.hint);
      expect(r.hintLevel, 2);
      expect(r.canHint, isFalse);
      expect(r.submit('Lọc'), TurnKind.scaffold);
      expect(r.current, isA<NextStep>(), reason: 'sai 3 lần vẫn đi tiếp');
      final kinds = r.transcript.map((t) => t.kind).toList();
      expect(
        kinds.where((k) => k == TurnKind.matched),
        isEmpty,
        reason: '⭐⭐ không khớp thì KHÔNG có lời khen',
      );
      expect(kinds, contains(TurnKind.scaffold));
    },
  );

  test('xin gợi ý trước khi trả lời được phép (scaffold, không phạt)', () {
    final r = TutorRunner(_script())..advance();
    expect(r.requestHint(), 'gợi ý 1');
    expect(r.requestHint(), 'gợi ý 2');
    expect(r.requestHint(), isNull);
  });

  test('câu trả lời rỗng không khớp gì', () {
    expect(answerMatches('   ', [r'.*']), isFalse);
    expect(answerMatches('cô cạn', [r'^cô cạn$']), isTrue);
  });

  test('neo vào block: có bước cho block ⇒ bắt đầu ở đó; không ⇒ từ đầu', () {
    final r1 = TutorRunner(_script(), startAtBlockId: 'b2');
    expect(r1.anchoredToBlock, isTrue);
    expect(r1.current, isA<AskStep>());
    final r2 = TutorRunner(_script(), startAtBlockId: 'zzz');
    expect(r2.anchoredToBlock, isFalse);
    expect(r2.current, isA<ExplainStep>());
  });

  test(
    'parse: thang gợi ý > 2 bậc, thiếu keySource, thiếu acceptable ⇒ null',
    () {
      final ok = _script().toJson();
      expect(TutorScript.fromJson(ok), isNotNull);
      final ask = (ok['steps'] as List)[1] as Map<String, Object?>;
      ask['hints'] = ['a', 'b', 'c'];
      expect(TutorScript.fromJson(ok), isNull);
      ask['hints'] = ['a'];
      ask['keySource'] = '';
      expect(TutorScript.fromJson(ok), isNull);
      ask['keySource'] = 'prototype';
      ask['acceptable'] = [];
      expect(TutorScript.fromJson(ok), isNull);
      (ok['steps'] as List)[1] = ask..['acceptable'] = ['x'];
      ok['evidencePolicy'] = 'record';
      expect(
        TutorScript.fromJson(ok),
        isNull,
        reason: '⭐⭐ kịch bản mang chính sách ghi bằng chứng ⇒ không parse',
      );
    },
  );

  test('⭐ kịch bản fixture (mẫu + thật nếu có): không khen tư chất, không '
      '«Chính xác! 🎉», mọi AskStep khai keySource không phải SGV', () {
    final scripts = [loadSyntheticDoc().tutorScript!];
    final real = loadRealDocOrSkip();
    if (real != null) scripts.add(real.tutorScript!);
    for (final s in scripts) {
      expect(s.samMode, SamMode.prototypeScripted);
      expect(s.trust, ContentTrust.prototype);
      expect(s.evidencePolicy, EvidencePolicy.none);
      for (final st in s.steps) {
        final texts = switch (st) {
          ExplainStep(:final text) => [text],
          AskStep(:final hints, :final feedbackMatched, :final scaffold) => [
            ...hints,
            feedbackMatched,
            scaffold,
          ],
          NextStep(:final label) => [label],
        };
        for (final t in texts) {
          final low = t.toLowerCase();
          for (final banned in bannedAbilityPraise) {
            expect(
              low,
              isNot(contains(banned)),
              reason: 'khen tư chất «$banned» trong «$t»',
            );
          }
          expect(t, isNot(contains('Chính xác!')));
          expect(t, isNot(contains('🎉')));
        }
        if (st is AskStep) {
          expect(st.keySource.toLowerCase(), contains('không phải sgv'));
          expect(st.hints.length, lessThanOrEqualTo(2));
        }
      }
    }
  });
}
