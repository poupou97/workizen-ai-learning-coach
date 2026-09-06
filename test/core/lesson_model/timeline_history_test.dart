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
import 'package:learning_coach/core/lesson_model/repair_record.dart';
import 'package:learning_coach/core/lesson_model/semantic_data.dart';
import 'package:learning_coach/core/lesson_model/timeline_date.dart';
import 'package:learning_coach/core/lesson_model/timeline_sources.dart';
import 'package:learning_coach/core/lesson_model/timeline_validator.dart';
import 'package:learning_coach/core/lesson_model/tutor_script.dart';
import 'package:learning_coach/core/lesson_model/workspace_catalog.dart';

import '../../support/golden_chain_ledger.dart';

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

  // ⭐⭐ ROUND 6 (WS-C) — TIỀN ĐỀ CŨ ĐÃ SAI, VÀ NÓ PHẢI SAI.
  //
  // Test này từng khẳng định «7 mốc từ một block tin được». Nó viết ra kì vọng
  // của vòng 4/5, khi các mốc đến từ một fixture MẪU. Trên fixture THẬT hôm nay
  // con số là **0 mốc**, và đó là hệ thống chạy ĐÚNG:
  //
  //   `p039:000` — block mang cả bảy mốc — bị giữ lại vì `agree_tones` («Bạch
  //   Đằng» của stack chính vs «Bạch Đăng» của stack kiểm). Vòng 6 SỬA được nó:
  //   một `ValidatedRepair` tất định, validator độc lập xác nhận. Nhưng NỐI ≠
  //   TIN — một sửa chữa đã kiểm chứng KHÔNG tự động thành tin được, nên block
  //   vẫn bị giữ lại, vẫn không có chữ, và **không dòng thời gian nào dựng được
  //   từ nó**.
  //
  // Tiền lệ (Lane D, vòng 5): một test khẳng định «B6 có bài tập thật» đang GHIM
  // KHUYẾT TẬT; tiền đề được sửa, cổng KHÔNG được nới. Ở đây cũng vậy — và test
  // mới đáng giá hơn test cũ, vì nó không khẳng định «0 mốc» mà khẳng định **VÌ
  // SAO**: block có mặt, bị giữ lại, mang sửa chữa đã kiểm chứng, và dòng thời
  // gian không dựng được CHỪNG NÀO nó chưa được tin. Ai đó làm dòng thời gian
  // hiện lại mà KHÔNG có quyết định tin của Founder ⇒ ĐỎ. Ai đó lặng lẽ phục vụ
  // block ⇒ ĐỎ.
  group('fixture THẬT LS&ĐL 5 Bài 8 (chỉ khi máy có)', () {
    final f = File(historyRealPath);

    test('⭐⭐ block bảy mốc: CÓ MẶT, BỊ GIỮ LẠI, mang VALIDATED_REPAIR — và '
        'không dòng thời gian nào dựng được khi nó chưa được tin', () {
      if (!goldenChainGate('GC-07')) return;
      final d = _load(historyRealPath, FixtureSlot.realDir);
      // danh tính bài học không đổi — đây vẫn là Golden #1
      expect(d.trust, ContentTrust.trustedStructuredLesson);
      expect(d.title, 'Đấu tranh giành độc lập thời kì Bắc thuộc');
      expect(d.provenance.boundary!.pageStart, 38);
      expect(d.provenance.boundary!.pageEnd, 41);

      // 1. block mang bảy mốc CÓ MẶT — không biến mất (bài học R13: giữ lại là
      //    một quyết định kiểm được; biến mất thì không).
      final ev = d.blockById('05-sgk-lich-su-va-dia-li-5:p039:tc2-p1:000');
      expect(ev, isNotNull, reason: 'block bảy mốc không được rơi khỏi tài liệu');
      expect(ev, isA<WithheldBlock>(),
          reason: 'phục vụ block này cần quyết định tin của Founder');
      final w = ev! as WithheldBlock;
      expect(w.trust, ContentTrust.withheld);
      expect(w.reasons, contains('agree_tones'));

      // 2. nó MANG một sửa chữa đã được kiểm chứng — nhìn thấy được, đếm được.
      expect(w.hasValidatedRepair, isTrue);
      final r = w.repair!;
      expect(r.disposition, RepairDisposition.validatedRepair);
      expect(r.verdict, 'validated');
      expect(r.method, 'lanec.tone-corroboration-v1');
      expect(r.validatorId, 'lanec.history-text-validator-v1');
      expect(r.changed, isFalse, reason: 'sửa DISPOSITION, không viết lại chữ');
      // 3. …và KHÔNG tin được, KHÔNG phục vụ được.
      expect(r.servable, isFalse);
      expect(d.trustedRepairCount, 0);

      // 4. KHÔNG chữ nào của nó đọc được — `WithheldBlock` không có trường chữ.
      expect(
        jsonEncode(w.toJson()).contains('Bạch Đằng'),
        isFalse,
        reason: 'giá trị đề xuất ở lại corpus, không bao giờ tới app',
      );

      // 5. ⭐ HỆ QUẢ, và đây là điều test này bảo vệ: không dòng thời gian nào.
      //    Nếu mốc quay lại mà block vẫn chưa được tin ⇒ ai đó đã dựng dữ liệu
      //    học từ một thứ chưa ai duyệt.
      expect(
        d.semantic.whereType<TimelineSemantic>(),
        isEmpty,
        reason: 'dòng thời gian chỉ được quay lại CÙNG một quyết định tin của '
            'Founder cho block nguồn — xem PR #90, NỐI ≠ TIN',
      );

      // 6. và không block PHỤC VỤ nào mang dấu vết sửa chữa (bất biến của cầu).
      for (final b in d.blocks) {
        if (b is WithheldBlock) continue;
        expect(
          (b.toJson()).containsKey('repair'),
          isFalse,
          reason: '${b.id} được phục vụ mà mang sửa chữa ⇒ phục hồi chưa qua cổng',
        );
      }
      recordGoldenChain('GC-07', exercised: true);
    });

    test('kế toán sửa chữa của tài liệu nói thật: 6 vùng mang sửa chữa, 0 tin được', () {
      if (!goldenChainGate('GC-08')) return;
      final d = _load(historyRealPath, FixtureSlot.realDir);
      final withRepair = d.validatedRepairs;
      expect(withRepair, hasLength(6));
      for (final b in withRepair) {
        expect(b.trust, ContentTrust.withheld);
        expect(b.repair!.servable, isFalse);
      }
      // `provenance.repair` là kế toán ở mức tài liệu; mô hình chưa phân tích nó,
      // nên đọc thẳng JSON — con số phải khớp với thứ mô hình đếm được.
      final raw = jsonDecode(f.readAsStringSync()) as Map;
      final prov =
          (raw['provenance'] as Map)['repair'] as Map<String, dynamic>;
      expect(prov['trusted'], 0, reason: 'bất biến, không phải phép đo');
      expect(prov['onBlocks'], withRepair.length);
      expect(prov['productionTrustThreshold'], isNull);
      // an toàn phiên bản fixture: bản ghi phải tự nói nó thuộc thế hệ nào
      for (final k in [
        'sourceTslSha256',
        'projectedTslSha256',
        'hashMethod',
        'generator',
        'generation',
      ]) {
        expect(prov[k], isNotNull, reason: 'thiếu $k ⇒ không chứng minh được lai lịch');
      }
      recordGoldenChain('GC-08', exercised: true);
    });

    test('nguồn kể chuyện vẫn dựng được từ những block CÒN được phục vụ', () {
      if (!goldenChainGate('GC-09')) return;
      final d = _load(historyRealPath, FixtureSlot.realDir);
      final src = deriveStoryAttributions(d);
      // Không ghim một con số của vòng 4: khẳng định TÍNH CHẤT — mọi nguồn dựng
      // được đều trỏ tới một block CÓ THẬT và CÒN được phục vụ trong tài liệu.
      for (final a in src) {
        final b = d.blockById(a.attributionBlockId);
        expect(b, isNotNull, reason: a.attributionBlockId);
        expect(
          b,
          isNot(isA<WithheldBlock>()),
          reason: '${a.attributionBlockId}: không dựng nguồn từ vùng bị giữ lại',
        );
      }
      recordGoldenChain('GC-09', exercised: true);
    });
  });
}
