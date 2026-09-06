/// LANE C (round 5, §11) — CỔNG NGUYÊN VĂN phía Dart.
///
/// Vòng 4 bác bỏ A26 («hai bộ OCR đồng ý ⇒ đúng nguyên văn»), nên lớp chặn
/// thứ hai này phải: (1) không trích mốc/nguồn nào chưa đối chiếu bản in khi
/// cổng bật; (2) không im lặng khi cổng TẮT — giao diện phải nói ra; (3) không
/// bao giờ đọc tiêu đề câu chuyện sai dấu cho trẻ nghe.
library;

import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/lesson_model/semantic_data.dart';
import 'package:learning_coach/core/lesson_model/timeline_sources.dart';
import 'package:learning_coach/core/lesson_model/timeline_validator.dart';
import 'package:learning_coach/core/lesson_model/timeline_verbatim.dart';

const _syntheticPath =
    'assets/fixtures/synthetic/lesson-05-sgk-lich-su-va-dia-li-5-b8.synthetic.json';

LessonDocument _doc() {
  final j = jsonDecode(File(_syntheticPath).readAsStringSync()) as Map;
  final d = LessonDocument.fromJson(j.cast<String, Object?>(), assetBase: 'x');
  if (d == null) throw StateError('fixture MẪU không parse được');
  return d;
}

TimelineSemantic _timeline(LessonDocument d) =>
    d.semantic.whereType<TimelineSemantic>().first;

VerbatimIndex _index(Map<String, String> statuses, {bool enabled = true}) =>
    VerbatimIndex.fromRawJson({
      'provenance': {
        'historyRules': {
          'verbatimGate': {
            'enabled': enabled,
            'ledger': 'test-ledger.json',
            'blockStatus': statuses,
          },
        },
      },
    });

void main() {
  test('id ngắn: ledger ghi «p039:tc2-p1:000», block mang tên sách ở đầu', () {
    expect(
      VerbatimIndex.shortId('05-sgk-lich-su-va-dia-li-5:p039:tc2-p1:000'),
      'p039:tc2-p1:000',
    );
    expect(VerbatimIndex.shortId('p039:tc2-p1:000'), 'p039:tc2-p1:000');
    expect(VerbatimIndex.shortId('mau-1'), 'mau-1');
  });

  test('thiếu khoá / sai kiểu / enabled != true ⇒ cổng TẮT, không chặn gì', () {
    for (final raw in <Map<String, Object?>?>[
      null,
      <String, Object?>{},
      {'provenance': 'không phải map'},
      {
        'provenance': {'historyRules': 42},
      },
      {
        'provenance': {
          'historyRules': {
            'verbatimGate': {'enabled': false},
          },
        },
      },
    ]) {
      final v = VerbatimIndex.fromRawJson(raw);
      expect(v.enabled, isFalse);
      expect(v.servable('bất kì'), isTrue, reason: 'cổng tắt thì không tự ý giấu');
      expect(v.heldBackLine(3), isNull);
      expect(v.statusOf('bất kì'), VerbatimStatus.unverified);
    }
  });

  test('cổng bật: chỉ block đã đối chiếu bản in mới trích được', () {
    final v = _index({
      'a': 'verifiedAgainstPrint',
      'b': 'printDiffers',
      'c': 'unverified',
    });
    expect(v.enabled, isTrue);
    expect(v.ledger, 'test-ledger.json');
    expect(v.servable('a'), isTrue);
    expect(v.servable('b'), isFalse);
    expect(v.servable('c'), isFalse);
    expect(v.servable('không có trong ledger'), isFalse, reason: 'fail closed');
    expect(v.heldBackLine(2), contains('giữ lại 2 phần'));
    expect(v.heldBackLine(0), isNull);
  });

  test('mốc chưa đối chiếu bị loại khỏi validator, và lí do nói ra số mốc', () {
    final d = _doc();
    final tl = _timeline(d);
    expect(tl.events.length, greaterThanOrEqualTo(3));
    // cổng tắt ⇒ như vòng 4
    expect(TimelineValidator.forSemantic(tl), isNotNull);
    expect(TimelineValidator.servableEvents(tl).length, tl.events.length);

    final all = {
      for (final e in tl.events)
        VerbatimIndex.shortId(e.sourceBlockId): 'verifiedAgainstPrint',
    };
    final vOk = _index(all);
    expect(TimelineValidator.servableEvents(tl, verbatim: vOk).length, tl.events.length);
    expect(TimelineValidator.forSemantic(tl, verbatim: vOk), isNotNull);

    final vNone = _index({'không liên quan': 'verifiedAgainstPrint'});
    expect(TimelineValidator.servableEvents(tl, verbatim: vNone), isEmpty);
    expect(TimelineValidator.forSemantic(tl, verbatim: vNone), isNull);
    expect(
      TimelineValidator.unavailableReason(tl, verbatim: vNone),
      contains('chưa đối chiếu được với bản in'),
    );
  });

  test('nguồn kể chuyện: block dòng nguồn chưa đối chiếu ⇒ không có thẻ nào', () {
    final d = _doc();
    final base = deriveStoryAttributions(d);
    expect(base, isNotEmpty);
    final vNone = _index({'không liên quan': 'verifiedAgainstPrint'});
    expect(deriveStoryAttributions(d, verbatim: vNone), isEmpty);
    expect(storyAttributionsHeldBack(d, verbatim: vNone), base.length);
    expect(storyAttributionsHeldBack(d), 0, reason: 'cổng tắt ⇒ không giữ lại gì');
  });

  test('tiêu đề câu chuyện chưa đối chiếu: KHÔNG trích, câu chuyện không trọn vẹn', () {
    final d = _doc();
    final base = deriveStoryAttributions(d).first;
    expect(base.titleBlockId, isNotNull);
    expect(base.title, isNotNull);

    final v = _index({
      VerbatimIndex.shortId(base.attributionBlockId): 'verifiedAgainstPrint',
      for (final id in base.storyBlockIds)
        VerbatimIndex.shortId(id): 'verifiedAgainstPrint',
      VerbatimIndex.shortId(base.titleBlockId!): 'printDiffers',
    });
    final gated = deriveStoryAttributions(d, verbatim: v).single;
    expect(gated.title, isNull, reason: 'không đọc chữ sai dấu cho trẻ nghe');
    expect(gated.titleBlockId, base.titleBlockId, reason: 'vẫn truy được về sách');
    expect(gated.titleVerbatimWithheld, isTrue);
    expect(gated.complete, isFalse);
    expect(gated.publisher, base.publisher, reason: 'NXB/năm nằm trong dòng nguồn đã đối chiếu');
  });
}
