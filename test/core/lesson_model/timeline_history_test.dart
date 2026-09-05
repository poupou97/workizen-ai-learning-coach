/// LANE C (round 4, Golden Slice #2) — lát cắt Lịch sử LS&ĐL 5 Bài 8:
/// fixture MẪU (commit) đi qua đúng đường của fixture THẬT (gitignore):
/// TimelineSemantic từ `prose-dated-events-v1`, nguồn kể chuyện từ
/// `story-attribution-v1`, TimelineValidator tất định, kịch bản SAM có kiểu
/// (prototype) với mẫu `acceptable` hợp lệ trong RegExp unicode của Dart.
/// Fixture thật chỉ được kiểm khi có file — không xanh giả.
library;

import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/content_trust.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/lesson_model/semantic_data.dart';
import 'package:learning_coach/core/lesson_model/timeline_date.dart';
import 'package:learning_coach/core/lesson_model/timeline_sources.dart';
import 'package:learning_coach/core/lesson_model/timeline_validator.dart';
import 'package:learning_coach/core/lesson_model/tutor_script.dart';
import 'package:learning_coach/core/lesson_model/workspace_catalog.dart';

const historySyntheticPath =
    'assets/fixtures/synthetic/lesson-05-sgk-lich-su-va-dia-li-5-b8.synthetic.json';
const historyRealPath =
    'assets/fixtures/real/lesson-05-sgk-lich-su-va-dia-li-5-b8.json';

LessonDocument _load(String path, String base) {
  final j = jsonDecode(File(path).readAsStringSync()) as Map;
  final d = LessonDocument.fromJson(j.cast<String, Object?>(), assetBase: base);
  if (d == null) throw StateError('$path không parse được');
  return d;
}

/// Mọi `acceptable` phải là RegExp hợp lệ ở chế độ unicode (Dart ném khi
/// gặp `\-` / `\ ` — lỗi mà `re.escape` của Python sinh ra).
void _patternsCompile(TutorScript s) {
  for (final a in s.asks) {
    for (final p in a.acceptable) {
      expect(() => RegExp(p, caseSensitive: false, unicode: true), returnsNormally, reason: p);
    }
    expect(a.hints.length, lessThanOrEqualTo(2));
    expect(a.keySource, isNotEmpty);
    // chống lộ đáp án: không gợi ý nào khớp mẫu đáp án của chính bước đó
    for (final h in a.hints) {
      expect(answerMatches(h, a.acceptable), isFalse, reason: '${a.id}: $h');
    }
  }
}

void main() {
  group('fixture MẪU LS&ĐL 5 Bài 8', () {
    final d = _load(historySyntheticPath, FixtureSlot.syntheticDir);

    test('parse; trust fixtureSynthetic ở mọi block chữ; slot đúng', () {
      expect(d.slotKey, '05-sgk-lich-su-va-dia-li-5#8');
      expect(d.grade, 5);
      expect(d.trust, ContentTrust.fixtureSynthetic);
      for (final b in d.blocks) {
        if (b is! WithheldBlock) expect(b.trust, ContentTrust.fixtureSynthetic);
      }
      expect(WorkspaceCatalog.isResearchSlot(d), isTrue);
      expect(WorkspaceCatalog.defaultSlots.map((s) => s.key), contains(d.slotKey));
    });

    test('prose-dated-events-v1 ⇒ TimelineSemantic 5 mốc, đọc được ngày, theo thứ tự sách', () {
      final tl = d.semantic.whereType<TimelineSemantic>().single;
      expect(tl.derivation, 'prose-dated-events-v1');
      expect(tl.trust, ContentTrust.fixtureSynthetic);
      expect(tl.events.map((e) => e.title), [
        'Ông Mẫu A',
        'Bà Mẫu B',
        'Ông Mẫu C - Bà Mẫu D',
        'Ông Mẫu E',
        'Ông Mẫu G',
      ]);
      expect(tl.events.map((e) => e.when), ['101 - 103', '205', '310 - 320', '398', '450']);
      for (final e in tl.events) {
        expect(TimelineDate.parse(e.when), isNotNull, reason: e.when);
        expect(d.blockById(e.sourceBlockId), isA<ParagraphBlock>());
      }
      // «Năm 101» trong câu chuyện KHÔNG thành mốc (luật không nâng năm kể chuyện)
      expect(tl.events.where((e) => e.text!.startsWith('[MẪU] Thuở xưa')), isEmpty);
    });

    test('story-attribution-v1 ⇒ 1 nguồn: tiêu đề, 2 đoạn, NXB Mẫu 2000, trọn vẹn', () {
      final src = deriveStoryAttributions(d);
      expect(src.length, 1);
      final a = src.single;
      expect(a.form, 'theo');
      expect(a.title, 'CHUYỆN MẪU VỀ ÔNG MẪU A');
      expect(a.storyBlockIds.length, 2);
      expect(a.withheldPartIds, isEmpty);
      expect(a.publisher, 'NXB Mẫu');
      expect(a.year, 2000);
      expect(a.complete, isTrue);
      expect(a.childLine, 'Kể theo: NXB Mẫu, 2000');
      expect(d.blockById(a.attributionBlockId), isA<ParagraphBlock>());
    });

    test('TimelineValidator: cặp tên–năm, thứ tự, trước/sau — tất định, chỉ nói «sách viết»', () {
      final tl = d.semantic.whereType<TimelineSemantic>().single;
      final v = TimelineValidator.forSemantic(tl)!;
      expect(v.bookOrderIsChronological, isTrue);
      expect(v.checkPair('Bà Mẫu B', '205').ok, isTrue);
      expect(v.checkPair('bà mẫu b', '205').ok, isTrue); // hoa/thường
      expect(v.checkPair('Bà Mẫu B', '206').ok, isFalse);
      expect(v.checkPair('Ông Mẫu Z', '205').ok, isFalse);
      expect(v.checkPair('Ông Mẫu A', 'khoảng năm 100').ok, isFalse);
      final ok = v.checkOrder(['Ông Mẫu A', 'Ông Mẫu E', 'Ông Mẫu G']);
      expect(ok.ok, isTrue);
      expect(ok.sourceBlockIds.length, 1);
      final bad = v.checkOrder(['Ông Mẫu E', 'Bà Mẫu B']);
      expect(bad.ok, isFalse);
      expect(bad.firstInversion, (0, 1));
      expect(bad.reason, contains('Bà Mẫu B (205)'));
      expect(bad.reason, isNot(contains('sai')));
      expect(v.checkBefore('Ông Mẫu A', 'Ông Mẫu G').ok, isTrue);
      expect(v.checkBefore('Ông Mẫu G', 'Ông Mẫu A').ok, isFalse);
      expect(v.checkOrder(['Ông Mẫu A']).ok, isFalse);
    });

    test('không mốc / mốc không đọc được ⇒ KHÔNG có validator (nói lí do)', () {
      expect(TimelineValidator.forSemantic(null), isNull);
      final one = TimelineSemantic(
        id: 't', title: 't', trust: ContentTrust.fixtureSynthetic, derivation: 'x',
        events: const [TimelineEvent(when: '205', title: 'B', sourceBlockId: 'b')],
      );
      expect(TimelineValidator.unavailableReason(one), contains('1 mốc'));
      final undated = TimelineSemantic(
        id: 't', title: 't', trust: ContentTrust.fixtureSynthetic, derivation: 'x',
        events: const [
          TimelineEvent(when: 'Bước đầu', title: 'A', sourceBlockId: 'b'),
          TimelineEvent(when: 'Sau đó', title: 'B', sourceBlockId: 'b'),
        ],
      );
      expect(TimelineValidator.forSemantic(undated), isNull);
      expect(TimelineValidator.unavailableReason(undated), contains('Bước đầu'));
    });

    test('kịch bản SAM có kiểu: prototype, 7 bước, mẫu đáp án hợp lệ, không lộ đáp án', () {
      final s = d.tutorScript!;
      expect(s.trust, ContentTrust.prototype);
      expect(s.samMode, SamMode.prototypeScripted);
      expect(s.steps.length, 7);
      expect(s.steps.map((x) => x.id), ['e1', 'q1', 'q2', 'q3', 'e2', 'q4', 'n1']);
      _patternsCompile(s);
      final q1 = s.asks.first;
      expect(q1.isChoice, isTrue);
      expect(answerMatches(q1.options.first, q1.acceptable), isTrue);
      expect(answerMatches('101 – 103', q1.acceptable), isTrue); // trẻ gõ gạch ngang
      expect(answerMatches('205', q1.acceptable), isFalse);
      final q2 = s.asks.elementAt(1);
      expect(answerMatches('Bà Mẫu B', q2.acceptable), isTrue);
      expect(answerMatches('Ông Mẫu C - Bà Mẫu D', q2.acceptable), isFalse);
      final q4 = s.asks.last;
      expect(q4.promptBlockId, isNotNull);
      expect(d.blockById(q4.promptBlockId!), isA<QuestionBlock>());
      expect(answerMatches('Bà Mẫu B (205), Ông Mẫu E (398)', q4.acceptable), isTrue);
      expect(answerMatches('Ông Mẫu Z (999)', q4.acceptable), isFalse);
      // câu hỏi phụ thuộc hình không bao giờ là prompt
      for (final a in s.asks) {
        final b = a.promptBlockId == null ? null : d.blockById(a.promptBlockId!);
        if (b is QuestionBlock) expect(b.text, isNot(contains('quan sát các hình')));
      }
      // mọi bước giải thích trích một block nguồn có thật
      for (final e in s.steps.whereType<ExplainStep>()) {
        expect(d.blockById(e.sourceBlockId!), isNotNull);
      }
    });
  });

  group('fixture THẬT LS&ĐL 5 Bài 8 (chỉ khi máy có)', () {
    final f = File(historyRealPath);
    test('7 mốc từ một block tin được, 3 nguồn (2 trọn vẹn), validator có, kịch bản 7 bước', () {
      if (!f.existsSync()) {
        markTestSkipped('fixture thật chưa sinh trên máy này (poc-out)');
        return;
      }
      final d = _load(historyRealPath, FixtureSlot.realDir);
      expect(d.trust, ContentTrust.trustedStructuredLesson);
      expect(d.title, 'Đấu tranh giành độc lập thời kì Bắc thuộc');
      expect(d.provenance.boundary!.pageStart, 38);
      expect(d.provenance.boundary!.pageEnd, 41);
      final tl = d.semantic.whereType<TimelineSemantic>().single;
      expect(tl.events.length, 7);
      expect(tl.events.map((e) => e.sourceBlockId).toSet().length, 1);
      expect(tl.events.first.title, 'Hai Bà Trưng');
      expect(tl.events.last.when, '938');
      final v = TimelineValidator.forSemantic(tl)!;
      expect(v.bookOrderIsChronological, isTrue);
      expect(v.checkBefore('Bà Triệu', 'Phùng Hưng').ok, isTrue);
      expect(v.checkPair('Khúc Thừa Dụ', '905').ok, isTrue);
      final src = deriveStoryAttributions(d);
      expect(src.length, 3);
      expect(src.where((a) => a.complete).length, 2);
      expect(src.map((a) => a.year), [2017, 2005, 2014]);
      final s = d.tutorScript!;
      expect(s.steps.length, 7);
      _patternsCompile(s);
      expect(answerMatches('40 – 43', s.asks.first.acceptable), isTrue);
      expect(answerMatches('Bà Triệu', s.asks.elementAt(1).acceptable), isTrue);
      // block nguồn của mọi bước tồn tại trong tài liệu
      for (final st in s.steps) {
        final id = switch (st) {
          AskStep(:final promptBlockId) => promptBlockId,
          ExplainStep(:final sourceBlockId) => sourceBlockId,
          NextStep(:final anchorBlockId) => anchorBlockId,
        };
        expect(d.blockById(id!), isNotNull, reason: st.id);
      }
    });
  });
}
