/// TRACK B — LessonDocument: (de)serialise fail-closed; withheld không chữ;
/// mọi block có nguồn; bảng điều tra năng lực máy đếm.
library;

import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/content_trust.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/lesson_model/semantic_data.dart';

import '../../features/lesson_workspace/support.dart';

void main() {
  test(
    'fixture MẪU parse được, đủ 9 loại block, không block nào thiếu nguồn',
    () {
      final d = loadSyntheticDoc();
      expect(d.trust, ContentTrust.fixtureSynthetic);
      expect(d.isFixture, isTrue);
      expect(d.evidencePolicy, EvidencePolicy.none);
      final kinds = d.blocks.map((b) => b.runtimeType).toSet();
      expect(
        kinds,
        containsAll([
          HeadingBlock,
          ParagraphBlock,
          ImageBlock,
          CaptionBlock,
          TableBlock,
          QuestionBlock,
          ActivityBlock,
          WithheldBlock,
          SourceRefBlock,
        ]),
      );
      for (final b in d.blocks) {
        expect(b.sourceRef.book, d.book);
        expect(b.trust, ContentTrust.fixtureSynthetic);
      }
      // vòng 7: nguyên văn nguồn, không còn hạ chữ (quyết định của Founder)
      expect(d.lessonLabel, 'Bài 17 · ${d.title}');
      expect(d.pageRangeLine, 'SGK KHTN 6 · trang 60–63');
    },
  );

  test('⭐⭐ WITHHELD không có chữ — kể cả khi JSON lén đặt "text"', () {
    final j = jsonDecode(File(syntheticPath).readAsStringSync()) as Map;
    final blocks = (j['blocks'] as List).cast<Map>();
    final w = blocks.firstWhere((b) => b['type'] == 'withheld');
    w['text'] = 'CHỮ LẬU';
    final d = LessonDocument.fromJson(j.cast<String, Object?>())!;
    final wb = d.blocks.whereType<WithheldBlock>().first;
    expect(
      LessonDocument.textOf(wb),
      isNull,
      reason: 'đột biến đọc "text" ở withheld ⇒ đỏ',
    );
    expect(jsonEncode(wb.toJson()), isNot(contains('CHỮ LẬU')));
  });

  test('roundtrip toJson → fromJson giữ số block, semantic, kịch bản', () {
    final d = loadSyntheticDoc();
    final d2 = LessonDocument.fromJson(
      jsonDecode(jsonEncode(d.toJson())) as Map<String, Object?>,
    )!;
    expect(d2.blocks.length, d.blocks.length);
    expect(d2.semantic.length, d.semantic.length);
    expect(d2.tutorScript!.steps.length, d.tutorScript!.steps.length);
    expect(d2.chapters.length, d.chapters.length);
  });

  test(
    'fail-closed: sai schema / thiếu trust / policy lạ / block hỏng ⇒ null',
    () {
      final base = jsonDecode(File(syntheticPath).readAsStringSync()) as Map;
      Map<String, Object?> copy() =>
          (jsonDecode(jsonEncode(base)) as Map).cast<String, Object?>();

      var j = copy();
      j['schema'] = 'v0';
      expect(LessonDocument.fromJson(j), isNull);

      j = copy();
      j['evidencePolicy'] = 'record';
      expect(
        LessonDocument.fromJson(j),
        isNull,
        reason: '⭐⭐ không có chính sách ghi bằng chứng nào được parse',
      );

      j = copy();
      (j['provenance'] as Map)['trust'] = 'trusted';
      expect(LessonDocument.fromJson(j), isNull);

      j = copy();
      ((j['blocks'] as List).first as Map).remove('sourceRef');
      expect(
        LessonDocument.fromJson(j),
        isNull,
        reason: 'block không nguồn ⇒ cả tài liệu không dùng được',
      );

      j = copy();
      j['blocks'] = [];
      expect(LessonDocument.fromJson(j), isNull);
    },
  );

  // ⭐ ROUND 7 · WS-S (HO-1) — `LessonDocument.titleCase` ĐÃ BỊ XOÁ.
  //
  // Test cũ ở đây là ví dụ giáo khoa của lỗi chọn quần thể: cả BA đầu vào đều
  // IN HOA, tức chỉ nạp đúng tiền đề mà phép biến đổi giả định, nên nó không
  // thể đỏ dù hàm phá mọi danh từ riêng trong một chuỗi đã có chữ thường —
  // đúng cái đã xảy ra với «thời kì Bắc thuộc» trên máy thật. Thay bằng bất
  // biến của quyết định Founder: nhãn bài mang NGUYÊN VĂN tiêu đề. Quần thể
  // thật (2 382 tiêu đề) ở `test/core/display/title_fidelity_test.dart`.
  test('nhãn bài học mang NGUYÊN VĂN tiêu đề nguồn', () {
    final d = loadSyntheticDoc();
    expect(d.lessonLabel, 'Bài ${d.lessonNo} · ${d.title}');
  });

  test('bảng điều tra năng lực (census) đếm theo trust từng phần tử', () {
    final d = loadSyntheticDoc();
    final rows = d.capabilityCensus();
    expect(rows.every((r) => r.count > 0), isTrue);
    expect(rows.map((r) => r.element), contains('block.withheld'));
    expect(
      rows.where((r) => r.element == 'tutor.steps').single.trust,
      ContentTrust.prototype,
    );
    expect(
      rows.any((r) => r.trust == ContentTrust.trustedCorpus),
      isFalse,
      reason: 'hôm nay không phần tử nào là sự thật sản phẩm',
    );
  });

  test('⭐ fixture THẬT (nếu máy có): 4 withheld, không chữ, trust nội bộ', () {
    final d = loadRealDocOrSkip();
    if (d == null) return;
    // Round 3 (A1): fixture thật nay do CẦU sinh — trust là
    // `trustedStructuredLesson` (chưa kiểm định), vẫn bắt buộc chip.
    expect(d.trust, ContentTrust.trustedStructuredLesson);
    expect(d.trust.requiresFixtureChip, isTrue);
    expect(d.provenance.distribution, contains('D4'));
    expect(d.blocks.whereType<WithheldBlock>().length, 4);
    for (final w in d.blocks.whereType<WithheldBlock>()) {
      expect(LessonDocument.textOf(w), isNull);
      expect(w.trust, ContentTrust.withheld);
    }
    expect(d.blocks.whereType<ImageBlock>().length, 8);
    expect(d.blocks.whereType<QuestionBlock>().length, 11);
    expect(d.semantic.whereType<ProcessSemantic>().length, 2);
    expect(
      d.semantic.whereType<ComparisonSemantic>().single.entities.length,
      4,
    );
    expect(d.chapter?.label, 'Chương IV');
    expect(d.tutorScript, isNotNull);
    // in bảng điều tra để tài liệu trích — không assert số cụ thể ngoài trên
    for (final r in d.capabilityCensus()) {
      // ignore: avoid_print
      print('CENSUS ${r.toString()}');
    }
  });
}
