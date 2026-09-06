/// ⭐⭐ ROUND 6 (WS-C) — MỘT SỬA CHỮA ĐÃ KIỂM CHỨNG TỚI ĐƯỢC APP, VÀ KHÔNG TIN ĐƯỢC.
///
/// Vòng 5: không file nào ngoài `tool/corpus/repair/` và `tool/tests/` import gói
/// `repair` — đường sửa chữa đã kiểm chứng mà không nối tới sản phẩm. Các test
/// dưới đây là hợp đồng của dây nối phía app.
///
/// Mỗi test là MỘT CÁNH CỬA mà qua đó một sửa chữa chưa được duyệt có thể trở
/// thành thứ trẻ đọc được. Không cửa nào mở.
library;

import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/content_trust.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/lesson_model/repair_record.dart';

const _book = '05-sgk-lich-su-va-dia-li-5';
const _bid = '$_book:p039:tc2-p1:000';
const _proposed = 'Chiến thắng Bạch Đằng của Ngô Quyền (938)';

Map<String, Object?> repairJson({
  String disposition = 'VALIDATED_REPAIR',
  Map<String, Object?> extra = const {},
}) => {
  'repairId': '$_bid#lanec.tone-corroboration-v1#5c31cd1c',
  'disposition': disposition,
  'failureClass': 'vi_tone_disagreement',
  'method': 'lanec.tone-corroboration-v1',
  'repairVersion': 'repair-v1/lanec.tone-corroboration-v1',
  'validatorId': 'lanec.history-text-validator-v1',
  'validatorVersion': 'v1',
  'verdict': 'validated',
  'supportingLayers': ['E'],
  'changed': false,
  'servable': false,
  'structuredKind': null,
  'caps': <String>[],
  ...extra,
};

Map<String, Object?> sourceRef() => {
  'book': _book,
  'pagePdf': 39,
  'pagePrinted': 37,
  'bbox': [0.07, 0.06, 0.83, 0.08],
  'blockId': _bid,
};

Map<String, Object?> withheldBlockJson({Object? repair}) => {
  'type': 'withheld',
  'id': _bid,
  'sourceRef': sourceRef(),
  'trust': 'withheld',
  'reasons': ['agree_tones'],
  'status': 'WITHHELD',
  'repair': ?repair,
  if (repair != null) 'disposition': 'VALIDATED_REPAIR',
};

Map<String, Object?> docJson(List<Map<String, Object?>> blocks) => {
  'schema': LessonDocument.schemaV1,
  'book': _book,
  'bookTitle': 'Lịch sử và Địa lí 5',
  'subject': 'Lịch sử và Địa lí',
  'grade': 5,
  'lesson': 8,
  'title': 'NƯỚC TA DƯỚI ÁCH ĐÔ HỘ',
  'provenance': {
    'trust': 'trustedStructuredLesson',
    'book': _book,
    'pagePdfStart': 38,
    'pagePdfEnd': 41,
    'generator': 'tool/corpus/tsl_to_lesson_document.py@v1',
    'sourcePipeline': 'tc2-p1',
    'sdmVersion': 'sdm-v3',
    'distribution': 'internal-research-only (Founder D4)',
    'auditStatus': 'notAudited',
    'answerKeysIncluded': false,
  },
  'evidencePolicy': 'none',
  'licence': 'internalResearchOnly',
  'blocks': blocks,
  'semantic': <Object?>[],
  'chapters': <Object?>[],
};

void main() {
  group('ValidatedRepairRef — NỐI ≠ TIN', () {
    test('⭐⭐ đọc được VALIDATED_REPAIR, và KHÔNG bao giờ đọc TRUSTED', () {
      final ok = ValidatedRepairRef.fromJson(repairJson());
      expect(ok, isNotNull);
      expect(ok!.disposition, RepairDisposition.validatedRepair);
      expect(ok.servable, isFalse);
      for (final d in RepairDisposition.values) {
        final parsed = ValidatedRepairRef.fromJson(
          repairJson(disposition: d.wire),
        );
        expect(
          parsed == null,
          d != RepairDisposition.validatedRepair,
          reason: 'đột biến cho ${d.wire} lọt qua ⇒ đỏ',
        );
      }
      // TRUSTED phải bị TỪ CHỐI, không phải bị bỏ qua như chuỗi lạ.
      expect(ValidatedRepairRef.fromJson(repairJson(disposition: 'TRUSTED')), isNull);
      expect(ValidatedRepairRef.fromJson(repairJson(disposition: 'khong-co')), isNull);
    });

    test('⭐⭐ mọi khoá mang GIÁ TRỊ đề xuất đều làm bản ghi bị từ chối', () {
      for (final k in repairForbiddenKeys) {
        expect(
          ValidatedRepairRef.fromJson(repairJson(extra: {k: _proposed})),
          isNull,
          reason: 'khoá $k lọt vào bản ghi ⇒ đỏ',
        );
      }
      expect(
        ValidatedRepairRef.fromJson(repairJson(extra: {'servable': true})),
        isNull,
      );
    });

    test('fail-closed từng nhánh: thiếu dấu vết ⇒ null, không đoán', () {
      for (final k in [
        'repairId',
        'failureClass',
        'method',
        'repairVersion',
        'validatorId',
        'verdict',
      ]) {
        final j = repairJson()..remove(k);
        expect(ValidatedRepairRef.fromJson(j), isNull, reason: 'thiếu $k');
      }
      expect(
        ValidatedRepairRef.fromJson(repairJson(extra: {'verdict': 'insufficient'})),
        isNull,
      );
      expect(ValidatedRepairRef.fromJson('VALIDATED_REPAIR'), isNull);
      expect(ValidatedRepairRef.fromJson(null), isNull);
    });

    test('⭐ vòng lưu–đọc không làm bản ghi mạnh lên (Lane E2, PR #86)', () {
      final before = ValidatedRepairRef.fromJson(repairJson())!.toJson();
      final after = ValidatedRepairRef.fromJson(before)!.toJson();
      expect(after, before);
      expect(ValidatedRepairRef.notStrengthened(before, after), isTrue);
      // ba cách một vòng lưu–đọc có thể nâng bản ghi lên:
      expect(
        ValidatedRepairRef.notStrengthened(before, {
          ...before,
          'disposition': 'TRUSTED',
        }),
        isFalse,
      );
      expect(
        ValidatedRepairRef.notStrengthened(before, {...before, 'servable': true}),
        isFalse,
      );
      final capped = ValidatedRepairRef.fromJson(
        repairJson(extra: {
          'caps': ['trust_gate:founder_decision_absent'],
        }),
      )!;
      expect(capped.cappedByTrustGate, isTrue);
      expect(
        ValidatedRepairRef.notStrengthened(capped.toJson(), before),
        isFalse,
        reason: 'mất một cap là mất lý do bị chặn',
      );
    });

    test('từ vựng disposition GIỐNG HỆT repair/model.py — không vũ trụ thứ tư', () {
      expect(
        RepairDisposition.values.map((d) => d.wire).toSet(),
        {
          'ORIGINAL_OBSERVATION',
          'REPAIRED_CANDIDATE',
          'VALIDATED_REPAIR',
          'TRUSTED',
          'WITHHELD',
          'LEGACY',
          'SUPERSEDED',
          'SUSPECT',
          'HUMAN_VERIFIED',
          'CONFLICT',
        },
      );
      expect(
        RepairDisposition.trusted.strength,
        greaterThan(RepairDisposition.validatedRepair.strength),
      );
    });
  });

  group('LessonBlock / LessonDocument', () {
    test('⭐⭐ vùng bị giữ lại MANG được dấu vết, vẫn KHÔNG CÓ CHỮ', () {
      final d = LessonDocument.fromJson(
        docJson([withheldBlockJson(repair: repairJson())]),
      )!;
      final b = d.blocks.single as WithheldBlock;
      expect(b.trust, ContentTrust.withheld);
      expect(b.hasValidatedRepair, isTrue);
      expect(b.repair!.method, 'lanec.tone-corroboration-v1');
      expect(d.validatedRepairs, hasLength(1));
      expect(d.trustedRepairCount, 0);
      // KHÔNG có đường nào lấy chữ ra: kiểu không có trường chữ.
      expect(jsonEncode(b.toJson()).contains(_proposed), isFalse);
    });

    test('⭐⭐ JSON lén đặt "text" cạnh dấu vết vẫn KHÔNG có chữ', () {
      final j = withheldBlockJson(repair: repairJson());
      j['text'] = _proposed;
      final d = LessonDocument.fromJson(docJson([j]))!;
      expect(jsonEncode(d.toJson()).contains(_proposed), isFalse);
    });

    test('⭐⭐ block PHỤC VỤ mang `repair` ⇒ TỪ CHỐI CẢ TÀI LIỆU', () {
      final served = {
        'type': 'paragraph',
        'id': '$_book:p039:tc2-p1:001',
        'sourceRef': sourceRef(),
        'trust': 'trustedStructuredLesson',
        'text': 'Ngô Quyền đánh tan quân Nam Hán.',
        'repair': repairJson(),
      };
      expect(LessonDocument.fromJson(docJson([served])), isNull);
    });

    test('dấu vết hỏng trên vùng giữ lại ⇒ TỪ CHỐI CẢ TÀI LIỆU, không im lặng bỏ', () {
      for (final bad in [
        repairJson(disposition: 'TRUSTED'),
        repairJson(extra: {'proposedValue': _proposed}),
        repairJson()..remove('validatorId'),
      ]) {
        expect(
          LessonDocument.fromJson(docJson([withheldBlockJson(repair: bad)])),
          isNull,
        );
      }
    });
  });

  group('chế độ hỏng theo từng block — CHỈ cho lệch phiên bản', () {
    Map<String, Object?> unknownKind({String type = 'formula'}) => {
      'type': type,
      'id': '$_book:p039:tc2-p1:007',
      'sourceRef': sourceRef(),
      'trust': 'trustedStructuredLesson',
      'text': _proposed,
      'latex': r'\frac{1}{2}',
    };

    test('⭐ `type` lạ ⇒ vùng giữ lại CÓ LÝ DO và ĐƯỢC ĐẾM, không mất bài học', () {
      final d = LessonDocument.fromJson(
        docJson([withheldBlockJson(), unknownKind()]),
      )!;
      expect(d.blocks, hasLength(2));
      final salvaged = d.blocks.last as WithheldBlock;
      expect(salvaged.reasons, ['unsupported_block_type:formula']);
      expect(salvaged.trust, ContentTrust.withheld); // ÉP, dù pack khai gì
      expect(d.unsupportedBlockTypes, ['formula']);
      expect(d.hasUnsupportedBlocks, isTrue);
      // ⭐ và KHÔNG byte chữ nào của nó đọc được — đây là điều khiến chế độ này
      // không thể thành đường sống cho nội dung xấu.
      expect(jsonEncode(d.toJson()).contains(_proposed), isFalse);
      expect(jsonEncode(d.toJson()).contains(r'\frac'), isFalse);
    });

    test('⭐⭐ VI PHẠM TOÀN VẸN vẫn từ chối CẢ tài liệu — bất biến gốc còn nguyên', () {
      final cases = <Map<String, Object?>>[
        // trust `withheld` trên một block CÓ CHỮ
        {
          'type': 'paragraph',
          'id': 'x',
          'sourceRef': sourceRef(),
          'trust': 'withheld',
          'text': 'a',
        },
        // heading không có chữ
        {
          'type': 'heading',
          'id': 'x',
          'sourceRef': sourceRef(),
          'trust': 'trustedStructuredLesson',
        },
        // withheld không có lý do
        {
          'type': 'withheld',
          'id': 'x',
          'sourceRef': sourceRef(),
          'trust': 'withheld',
          'reasons': <String>[],
        },
        // thiếu nguồn
        {
          'type': 'paragraph',
          'id': 'x',
          'trust': 'trustedStructuredLesson',
          'text': 'a',
        },
        // `type` lạ MÀ mang dấu vết sửa chữa
        {...unknownKind(), 'repair': repairJson()},
      ];
      for (final c in cases) {
        expect(
          LessonDocument.fromJson(docJson([withheldBlockJson(), c])),
          isNull,
          reason: 'vi phạm toàn vẹn ${c['type']} lọt qua ⇒ đỏ',
        );
      }
    });

    test('strictBlockTypes: true khôi phục hành vi tất-cả-hoặc-không', () {
      expect(
        LessonDocument.fromJson(
          docJson([withheldBlockJson(), unknownKind()]),
          strictBlockTypes: true,
        ),
        isNull,
      );
      expect(
        LessonDocument.fromJson(docJson([withheldBlockJson()]),
                strictBlockTypes: true)!
            .unsupportedBlockTypes,
        isEmpty,
      );
    });
  });
}
