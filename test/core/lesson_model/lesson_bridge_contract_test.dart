/// Round 3 · A1 — HỢP ĐỒNG cầu TSL → LessonDocument, phía TIÊU THỤ (Dart):
/// các trường mới parse được, fail-closed khi thiếu/lạ, WITHHELD không chữ,
/// giấy phép tách khỏi trust, và fixture THẬT (nếu máy có) đếm được theo trust.
///
/// Tài liệu mẫu ở đây là GIẢ LẬP (mọi chữ mang «[MẪU]») — không câu nào là
/// lời sách.
library;

import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/content_trust.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';

import '../../features/lesson_workspace/support.dart';

const _book = '06-sgk-mau-6';

Map<String, Object?> _ref(int page, int printed, String id) => {
  'book': _book,
  'pagePdf': page,
  'pagePrinted': printed,
  'bbox': [0.1, 0.2, 0.7, 0.03],
  'blockId': id,
  'extraction': 'docling-x+ocrmac',
  'ocrConf': 0.98,
  'pipeline': 'tc2-p1',
  'agreementScore': 1.0,
};

/// Một tài liệu đúng hình dạng cầu sinh ra (rút gọn, giả lập).
Map<String, Object?> bridgeDoc() => {
  'schema': 'wal-lesson-fixture-v1',
  'book': _book,
  'bookTitle': 'KHTN 6',
  'subject': 'KHTN',
  'grade': 6,
  'lesson': 9,
  'title': '[MẪU] BÀI MẪU',
  'chapter': null,
  'chapters': <Object?>[],
  'provenance': {
    'trust': 'trustedStructuredLesson',
    'book': _book,
    'pagePdfStart': 11,
    'pagePdfEnd': 12,
    'pagePrintedStart': 10,
    'pagePrintedEnd': 11,
    'generator': 'tool/corpus/tsl_to_lesson_document.py@v1',
    'sourcePipeline': 'tc2-p1',
    'sdmVersion': 'sdm-v2',
    'pipelineVersion': 'tc2-p1/sdm-v2',
    'boundaryConfidence': 0.95,
    'boundary': {
      'pageStart': 11,
      'pageEnd': 12,
      'confidence': 0.95,
      'headerFound': true,
      'source': 'both',
      'attachMethods': {'header': 1, 'continuation': 1},
    },
    'tslPath': 'x/bai-9.tsl.json',
    'sourceHash': 'ab' * 32,
    'docType': 'SGK',
    'sourceability': 'PARTIAL',
    'answerKeysIncluded': false,
    'auditStatus': 'sampledNoGate',
    'auditRef': 'docs/research/FALSE-TRUST-AUDIT-RESULT-2026-09-05.md',
    'distribution': 'internal-research-only (Founder D4)',
  },
  'evidencePolicy': 'none',
  'licence': 'internalResearchOnly',
  'blocks': [
    {
      'id': '$_book:p011:tc2-p1:001',
      'type': 'heading',
      'sourceRef': _ref(11, 10, '$_book:p011:tc2-p1:001'),
      'trust': 'trustedStructuredLesson',
      'roleConfidence': 0.97,
      'sourceRole': 'heading',
      'roleMethod': 'lexicon',
      'relations': {'headingPath': ['Bài 9'], 'order': 1},
      'text': '[MẪU] BÀI MẪU',
      'level': 1,
    },
    {
      'id': '$_book:p011:tc2-p1:002',
      'type': 'caption',
      'sourceRef': _ref(11, 10, '$_book:p011:tc2-p1:002'),
      'trust': 'trustedStructuredLesson',
      'roleConfidence': 0.8,
      'sourceRole': 'caption',
      'roleMethod': 'native',
      'relations': {
        'headingPath': ['Bài 9', '[MẪU] BÀI MẪU'],
        'refersFigure': true,
        'captionOf': '$_book:p011:fig00',
        'order': 2,
        'enumeratorRestored': true,
      },
      'text': '[MẪU] Chú thích hình mẫu',
      'refersFigure': true,
    },
    {
      'id': '$_book:p011:tc2-p1:020',
      'type': 'withheld',
      'sourceRef': _ref(11, 10, '$_book:p011:tc2-p1:020'),
      'trust': 'withheld',
      'sourceRole': 'body',
      'relations': {'order': 3},
      'reason': 'math_guard,agree_text',
      'reasons': ['math_guard', 'agree_text'],
      'status': 'CONFLICT',
      'textLen': 16,
    },
    {
      'id': '$_book:b9:sourceRef',
      'type': 'sourceRef',
      'sourceRef': {
        'book': _book,
        'pagePdf': 11,
        'pagePrinted': 10,
        'bbox': [0, 0, 1, 1],
        'blockId': null,
        'pipeline': 'tc2-p1',
      },
      'trust': 'trustedStructuredLesson',
      'sourceRole': 'provenance_line',
      'text': 'SGK KHTN 6 · trang 10–11 · tc2-p1 / sdm-v2',
    },
  ],
  'semantic': <Object?>[],
};

Map<String, Object?> _copy(Map<String, Object?> j) =>
    (jsonDecode(jsonEncode(j)) as Map).cast<String, Object?>();

void main() {
  test('tài liệu cầu parse được: trust mới, licence, quan hệ, boundary', () {
    final d = LessonDocument.fromJson(bridgeDoc())!;
    expect(d.trust, ContentTrust.trustedStructuredLesson);
    expect(d.trust.requiresFixtureChip, isTrue, reason: 'chưa qua G1/giấy phép');
    expect(d.trust.isProductionTruth, isFalse);
    expect(fixtureChipLabel(d.trust), contains('chưa kiểm định'));
    expect(d.licence, ContentLicence.internalResearchOnly);
    expect(d.provenance.pipelineVersion, 'tc2-p1/sdm-v2');
    expect(d.provenance.auditStatus, AuditStatus.sampledNoGate);
    expect(d.provenance.auditRef, contains('FALSE-TRUST-AUDIT-RESULT'));
    expect(d.provenance.sourceHash, 'ab' * 32);
    expect(d.provenance.answerKeysIncluded, isFalse);
    final b = d.provenance.boundary!;
    expect((b.pageStart, b.pageEnd, b.confidence, b.headerFound, b.source), (
      11,
      12,
      0.95,
      true,
      'both',
    ));
    expect(b.attachMethods, {'header': 1, 'continuation': 1});

    final h = d.blocks.first as HeadingBlock;
    expect(h.sourceRole, 'heading');
    expect(h.roleMethod, 'lexicon');
    expect(h.relations.headingPath, ['Bài 9']);
    expect(h.relations.order, 1);
    expect(h.sourceRef.pipeline, 'tc2-p1');
    expect(h.sourceRef.agreementScore, 1.0);

    final c = d.blocks[1] as CaptionBlock;
    expect(c.relations.captionOf, '$_book:p011:fig00');
    expect(c.relations.refersFigure, isTrue);
    expect(c.relations.enumeratorRestored, isTrue);

    final w = d.blocks[2] as WithheldBlock;
    expect(w.trust, ContentTrust.withheld);
    expect(w.reasons, ['math_guard', 'agree_text']);
    expect(w.reason, 'math_guard,agree_text', reason: 'UI cũ đọc chuỗi');
    expect(w.status, 'CONFLICT');
    expect(LessonDocument.textOf(w), isNull);
    expect(d.blockCountByTrust, {
      ContentTrust.trustedStructuredLesson: 3,
      ContentTrust.withheld: 1,
    });
  });

  test('⭐⭐ WITHHELD ≠ TRUSTED: block có chữ mà khai withheld ⇒ tài liệu null', () {
    final j = bridgeDoc();
    ((j['blocks'] as List).first as Map)['trust'] = 'withheld';
    expect(LessonDocument.fromJson(j), isNull);
    expect(ContentTrust.withheld.mayCarryText, isFalse);
    for (final t in ContentTrust.values) {
      expect(t.mayCarryText, t != ContentTrust.withheld);
    }
  });

  test('⭐⭐ withheld: JSON lén đặt "text" ⇒ không đọc, không ghi lại', () {
    final j = bridgeDoc();
    ((j['blocks'] as List)[2] as Map)['text'] = '[MẪU] CHỮ LẬU';
    final d = LessonDocument.fromJson(j)!;
    final w = d.blocks.whereType<WithheldBlock>().single;
    expect(LessonDocument.textOf(w), isNull);
    expect(jsonEncode(w.toJson()), isNot(contains('CHỮ LẬU')));
    expect(jsonEncode(d.toJson()), isNot(contains('CHỮ LẬU')));
  });

  test('fail-closed: licence lạ / auditStatus lạ / khoá đáp án / boundary hỏng', () {
    var j = bridgeDoc();
    j['licence'] = 'distributable';
    expect(LessonDocument.fromJson(j), isNull, reason: 'không có giấy phép phát hành');

    j = bridgeDoc();
    (j['provenance'] as Map)['auditStatus'] = 'passed';
    expect(LessonDocument.fromJson(j), isNull, reason: 'không có giá trị «đạt»');

    j = bridgeDoc();
    (j['provenance'] as Map)['answerKeysIncluded'] = true;
    expect(LessonDocument.fromJson(j), isNull, reason: 'đáp án SGV không tới trẻ');

    j = bridgeDoc();
    (j['provenance'] as Map)['answerKeysIncluded'] = 'no';
    expect(LessonDocument.fromJson(j), isNull);

    j = bridgeDoc();
    ((j['provenance'] as Map)['boundary'] as Map).remove('pageEnd');
    expect(LessonDocument.fromJson(j), isNull, reason: 'boundary có mà hỏng');

    j = bridgeDoc();
    (j['provenance'] as Map)['trust'] = 'withheld';
    expect(LessonDocument.fromJson(j), isNull);

    j = bridgeDoc();
    final w = (j['blocks'] as List)[2] as Map;
    w['reasons'] = <Object?>[];
    w['reason'] = '';
    expect(LessonDocument.fromJson(j), isNull, reason: 'withheld không lý do');

    j = bridgeDoc();
    ((j['blocks'] as List)[2] as Map)['reasons'] = ['', '  '];
    ((j['blocks'] as List)[2] as Map)['reason'] = ' , ';
    expect(LessonDocument.fromJson(j), isNull);
  });

  test('thiếu trường mới ⇒ giá trị chặt nhất / yếu nhất, tài liệu vẫn parse', () {
    final j = bridgeDoc();
    j.remove('licence');
    final p = j['provenance'] as Map;
    p.remove('auditStatus');
    p.remove('boundary');
    p.remove('pipelineVersion');
    for (final b in (j['blocks'] as List).cast<Map>()) {
      b.remove('relations');
      b.remove('sourceRole');
      b.remove('roleMethod');
      (b['sourceRef'] as Map).remove('pipeline');
    }
    final d = LessonDocument.fromJson(j)!;
    expect(d.licence, ContentLicence.internalResearchOnly);
    expect(d.provenance.auditStatus, AuditStatus.notAudited);
    expect(d.provenance.boundary, isNull);
    expect(d.blocks.first.relations.isEmpty, isTrue);
    expect(d.blocks.first.sourceRole, isNull);
    expect(d.blocks.first.sourceRef.pipeline, isNull);
    // withheld cũ chỉ có `reason` «a,b»
    final w = d.blocks.whereType<WithheldBlock>().single;
    expect(w.reasons, ['math_guard', 'agree_text']);
  });

  test('fixture MẪU cũ (không licence, không quan hệ) vẫn parse — không gãy Lane B', () {
    final d = loadSyntheticDoc();
    expect(d.licence, ContentLicence.internalResearchOnly);
    expect(d.provenance.auditStatus, AuditStatus.notAudited);
    expect(d.trust, ContentTrust.fixtureSynthetic);
  });

  test('roundtrip toJson → fromJson giữ trường mới', () {
    final d = LessonDocument.fromJson(bridgeDoc())!;
    final d2 = LessonDocument.fromJson(_copy(d.toJson()))!;
    expect(d2.licence, d.licence);
    expect(d2.provenance.boundary!.attachMethods, {'header': 1, 'continuation': 1});
    expect(d2.provenance.auditStatus, AuditStatus.sampledNoGate);
    final c = d2.blocks[1] as CaptionBlock;
    expect(c.relations.captionOf, '$_book:p011:fig00');
    expect(c.roleMethod, 'native');
    final w = d2.blocks[2] as WithheldBlock;
    expect(w.reasons, ['math_guard', 'agree_text']);
    expect(w.status, 'CONFLICT');
    expect(w.toJson().containsKey('text'), isFalse);
  });

  test('parse enum: ContentLicence / AuditStatus fail-closed', () {
    expect(ContentLicence.parse(null), ContentLicence.internalResearchOnly);
    expect(ContentLicence.parse('internalResearchOnly'), ContentLicence.internalResearchOnly);
    expect(ContentLicence.parse('public'), isNull);
    expect(ContentLicence.values, [ContentLicence.internalResearchOnly]);
    expect(AuditStatus.parse(null), AuditStatus.notAudited);
    expect(AuditStatus.parse('sampledNoGate'), AuditStatus.sampledNoGate);
    expect(AuditStatus.parse('gatePassed'), isNull);
    expect(ContentTrust.parse('trustedStructuredLesson'), ContentTrust.trustedStructuredLesson);
    expect(ContentTrust.parse('withheld'), ContentTrust.withheld);
  });

  test('⭐ fixture THẬT từ cầu (nếu máy có): đếm theo trust, không chữ ở withheld', () {
    final d = loadRealDocOrSkip();
    if (d == null) return;
    expect(d.trust, ContentTrust.trustedStructuredLesson);
    expect(d.licence, ContentLicence.internalResearchOnly);
    expect(d.provenance.generator, contains('tsl_to_lesson_document.py'));
    expect(d.provenance.pipelineVersion, 'tc2-p1/sdm-v2');
    expect(d.provenance.boundary, isNotNull);
    expect(d.provenance.sourceHash, hasLength(64));
    final counts = d.blockCountByTrust;
    expect(counts[ContentTrust.withheld], 4, reason: 'TSL Bài 17 giữ lại 4 vùng');
    expect(counts.containsKey(ContentTrust.trustedCorpus), isFalse);
    expect(counts.containsKey(ContentTrust.fixtureSynthetic), isFalse);
    for (final b in d.blocks) {
      expect(b.sourceRef.book, d.book);
      if (b is WithheldBlock) {
        expect(b.trust, ContentTrust.withheld);
        expect(b.reasons, isNotEmpty);
        expect(b.status, isNotNull);
        expect(LessonDocument.textOf(b), isNull);
      } else {
        expect(b.trust, ContentTrust.trustedStructuredLesson);
        if (b is! SourceRefBlock && b is! ImageBlock) {
          expect(b.sourceRef.blockId, isNotNull);
          expect(b.sourceRef.pipeline, 'tc2-p1');
          expect(b.sourceRole, isNotNull);
          expect(b.relations.order, isNotNull);
        }
      }
    }
    // in số liệu cho báo cáo — không assert số ngoài 4 withheld
    for (final e in counts.entries) {
      // ignore: avoid_print
      print('BRIDGE-COUNT ${e.key.name} ${e.value}');
    }
  });
}
